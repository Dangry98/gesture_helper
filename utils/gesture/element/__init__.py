from __future__ import annotations

from functools import cache

import bpy
from bpy.props import CollectionProperty, BoolProperty

from .prop import ElementProperty, ElementAddProperty
from ... import icon_two
from ...public import (
    PublicOnlyOneSelectedPropertyGroup,
    PublicUniqueNamePropertyGroup,
    PublicOperator,
    get_pref, PublicSortAndRemovePropertyGroup, PublicProperty
)


class ElementCURE:
    class ElementPoll(PublicProperty, PublicOperator):

        @classmethod
        def poll(cls, context):
            return cls._pref().active_element is not None

    class ADD(PublicOperator, ElementProperty, ElementAddProperty, PublicProperty):
        bl_idname = 'gesture.element_add'
        bl_label = '添加手势项'

        @property
        def collection(self):
            r = self.relationship
            ae = self.active_element
            if r == 'SAME' and ae:
                pe = ae.parent_element
                # 如果没有同级则快进到根
                if pe:
                    return pe.element
            elif r == 'CHILD' and ae:
                return ae.element
            # if r == 'ROOT':
            return self.active_gesture.element

        def execute(self, context):
            print('add element', self.relationship, self.active_element, self.active_gesture)
            add = self.collection.add()
            print('add')
            add.element_type = self.element_type
            add.selected_type = self.selected_type
            self.gesture_cache_clear()
            self.element_cache_clear()
            print('clear')
            add.name = 'Element'
            print('finished')
            return {"FINISHED"}

    class REMOVE(ElementPoll):
        bl_idname = 'gesture.element_remove'
        bl_label = '删除手势项'

        def execute(self, context):
            self.pref.active_element.remove()
            self.element_cache_clear()
            return {"FINISHED"}

    class MOVE(ElementPoll):  # TODO MOVE COPY
        bl_idname = 'gesture.element_move'
        bl_label = '移动手势项'

        def execute(self, context):
            return {"FINISHED"}

    class SORT(ElementPoll):
        bl_idname = 'gesture.element_sort'
        bl_label = '排序手势项'

        is_next: BoolProperty()

        def execute(self, _):
            self.active_element.sort(self.is_next)
            self.element_cache_clear()
            return {"FINISHED"}


@cache
def get_childes(item: Element):
    childes = item.element.values()
    if len(childes):
        for child in childes:
            childes.extend(get_childes(child))
    childes.append(item)
    return childes


@cache
def get_parent_gesture(element: 'Element') -> 'Gesture':
    try:
        pref = get_pref()
        for g in pref.gesture:
            if element in g.element_iteration:
                return g
    except IndexError:
        ...


@cache
def get_parent_element(element: 'Element') -> 'Element':
    for e in element.parent_gesture.element_iteration:
        if element in e.element.values():
            return e


@cache
def get_element_index(element: 'Element') -> int:
    try:
        return element.collection.values().index(element)
    except ValueError:
        ...


class ElementProperty(ElementCURE,
                      PublicUniqueNamePropertyGroup,
                      PublicSortAndRemovePropertyGroup,
                      PublicOnlyOneSelectedPropertyGroup):
    enabled: BoolProperty(name='启用', default=True)

    element: CollectionProperty(type=Element)

    def _get_index(self) -> int:
        return get_element_index(self)

    def _set_index(self, value):
        if self.is_root:
            self.parent_gesture['index_element'] = self.index
        else:
            self.parent_element['index_element'] = self.index

    index = property(
        fget=_get_index,
        fset=_set_index,
        doc='通过当前项的index,来设置索引的index值,以及移动项')

    @property
    def parent_element(self) -> 'Element':
        return get_parent_element(self)

    @property
    def parent_gesture(self) -> 'Gesture':
        return get_parent_gesture(self)

    @property
    def collection_iteration(self) -> list:
        items = []
        for e in self.parent_gesture.element:
            items.extend(get_childes(e))
        return items

    @property
    def collection(self):
        pe = self.parent_element
        if pe:
            return pe.element
        else:
            return self.parent_gesture.element

    @property
    def element_iteration(self) -> [Element]:
        return get_childes(self)

    @property
    def selected_iteration(self) -> [Element]:
        return self.parent_gesture.element_iteration

    @property
    def names_iteration(self):
        return self.element_iteration

    @property
    def is_root(self):
        return self in self.parent_gesture.element.values()

    def selected_update(self, context):
        """
        在选择其它子项的时候自动将活动索引切换
        @rtype: object
        """
        for (index, element) in enumerate(self.parent_gesture.element):
            if self in element.collection_iteration:
                self.parent_gesture['index_element'] = self.index

    def remove_before(self):
        col = self.collection
        gl = len(col)
        if gl > 1:
            if self.is_last:
                self.index = 0
                col[self.index - 1]['selected'] = True
            else:
                col[self.index + 1]['selected'] = True


# TODO 子元素的删除需要单独处理,是子级的子级,不能直接拿到
class Element(ElementProperty):
    def draw_ui(self, layout: 'bpy.types.UILayout') -> None:
        layout.prop(self, 'enabled', text='', emboss=False)
        layout.prop(self,
                    'selected',
                    text='',
                    icon=icon_two(self.selected, 'RESTRICT_SELECT'),
                    emboss=False
                    )
        layout.prop(self, 'name')
        self.draw_child_element(layout)

    def draw_child_element(self, layout):
        for element in self.element:
            box = layout.box()
            element.draw_ui(box)

    def draw_ui_property(self, layout: 'bpy.types.UILayout') -> None:
        layout.prop(self, 'name')

        self.draw_debug(layout)

    def draw_debug(self, layout):
        layout.label(text=str(self))
        layout.label(text=str(self.index))
        layout.label(text=str(self.parent_gesture))
        layout.label(text=str(self.parent_element))
        layout.label(text=str(self.collection_iteration))

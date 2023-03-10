from functools import cache, wraps

import bpy
from bpy.props import EnumProperty, StringProperty, BoolProperty, FloatProperty, IntProperty
from bpy.types import PropertyGroup

from ..log import log
from ..property import ui_emboss_enum, ui_alignment, ui_direction, CUSTOM_UI_TYPE_ITEMS, UI_ELEMENT_TYPE_ENUM_ITEMS, \
    UI_ELEMENT_SELECT_STRUCTURE_TYPE, SELECT_STRUCTURE, CTEXT_ENUM_ITEMS
from ..utils import PublicClass, PublicName, PublicMove


def have_update(func):
    @wraps(func)
    def up(*args, **kwargs):
        self = args[0]
        a = None
        if self.is_update:  # 如果之前是可更新的才存后面解开
            a = True
            self.is_update = False
        ret = func(*args, **kwargs)
        if a:
            self.is_update = True
        log.debug(f'have_update {func}')
        self.update()
        return ret

    return up


class UiElement(PropertyGroup,
                PublicName,
                PublicClass,
                PublicMove
                ):
    default_float = {'min': 0,
                     'soft_max': 20,
                     'soft_min': 0.15,
                     }
    activate_init: BoolProperty()
    active: BoolProperty()
    scale_x: FloatProperty(**default_float)
    scale_y: FloatProperty(**default_float)
    ui_units_x: FloatProperty(**default_float)
    ui_units_y: FloatProperty(**default_float)
    active_default: BoolProperty()

    alert: BoolProperty()
    use_property_decorate: BoolProperty()
    use_property_split: BoolProperty(name='使用属性拆分')

    emboss_enum: EnumProperty(name='emboss enum',
                              description='有两个emboss 这个用于UILayout的输入枚举项',
                              **ui_emboss_enum,
                              default='NORMAL')
    enabled: BoolProperty(name='启用')

    alignment: EnumProperty('对齐模式', **ui_alignment)
    direction: EnumProperty(name='方向', **ui_direction)

    # UILayout property

    def _update_text(self, context):
        self._by_text_set_name()

    text: StringProperty(name='文字', default='text', update=_update_text)

    # enum
    ctext: EnumProperty(items=CTEXT_ENUM_ITEMS, name='翻译类型')
    text_ctxt: EnumProperty(items=CTEXT_ENUM_ITEMS, name='翻译类型')
    heading_ctxt: EnumProperty(items=CTEXT_ENUM_ITEMS, name='翻译类型')

    # int
    columns: IntProperty()

    row_major: IntProperty()

    toggle: IntProperty(name='切换',
                        max=1, min=-1, default=1)

    # float

    factor: FloatProperty(name='系数',
                          min=0.01,
                          max=100,
                          soft_max=0.8,
                          soft_min=0.1,
                          step=0.01,
                          default=0.5)

    # bool
    def _update_heading(self, context):
        """更新标题文字
        并自动更新元素名称

        Args:
            context (_type_): _description_
        """

        self._by_heading_set_name()

    align: BoolProperty(name='对齐')
    heading: StringProperty(name='标题', update=_update_heading)
    translate: BoolProperty(name='翻译文字')
    invert_checkbox: BoolProperty(name='反转复选框')
    emboss: BoolProperty(name='浮雕')

    expand: BoolProperty(name='扩展')

    slider: BoolProperty()

    depress: BoolProperty()

    even_columns: BoolProperty()
    even_rows: BoolProperty()


class ElementProperty(UiElement):
    @property
    def _items(self):
        return self.ui_element_items[self._parent_element_key]


class RelationProperty(ElementProperty):
    """
    只通过父级来获取关系子级更新在父级设置时自动更新一次
    """

    @property
    def collection(self):
        return self.parent_element.ui_items_collection_group

    @have_update
    def check_parent_element(self):
        """找父级元素,如果没有的话
        更新一下所有的ui元素"""
        key = self._parent_element_key
        if key not in self:
            log.debug('check_parent_element \temm')
            for i in self.element_items:  # 元素项
                el_n = i['name']
                for j in i.ui_items_collection_group.values():  # ui项
                    j[key] = el_n

    # @staticmethod
    @cache
    def _parent_element(self):
        key = self._parent_element_key
        if key not in self or self[key] not in self.element_items:
            self.check_parent_element()
            self.clear_element_cache()
        return self.element_items[self[key]]

    @property
    def parent_element(self):  # 反回父级元素,如果没有直接报错
        return self._parent_element()

    @staticmethod
    @cache
    def _get_children(self):  # 迭代子级ui
        key = self._child_ui_key
        ret = []
        if key not in self:
            return ret
        for i in self.child:
            ret.append(i)
            ret.extend(i.child)
        return ret
        # return [(i, *i.child[:]) for i in self.child_ui]

    @staticmethod
    @cache
    def _get_child(self):  # 子级ui
        key = self._child_ui_key
        return list(ui for ui in self.collection if key in self and ui.name in self[key])

    @staticmethod
    @cache
    def _get_parent(self):
        _key = self._parent_ui_key
        if _key in self:
            key = self[_key]
            col = self.collection
            if key not in col:
                log.error(f'{self} hava parent key but not in list find {key}')
                return
            return col[key]

    @have_update
    def _set_parent(self, parent: 'UiCollectionGroupElement'):
        name = getattr(parent, 'name', None)
        key = self._parent_ui_key

        if self == parent:
            log.info(f'{self.name} set parent error parent is self')
        elif parent and name in self.collection:
            self[key] = name
            log.info(f'{self} set parent {name}')
        else:
            if key in self:
                del self[key]
                log.debug(f'{self} del parent {name}\n{parent}')
            else:
                log.debug(f'not define parent {self}')

    @have_update
    def _del_parent(self):
        log.debug(f'del_parent {self}')
        parent_key = self._parent_ui_key

        for c in self.child:
            c.parent = self.parent

        if parent_key in self:  # 将数据从self删除
            del self[parent_key]

    child = property(_get_child)  # 交由更新方法托管
    parent = property(_get_parent, _set_parent, _del_parent)
    children = property(_get_children)

    @property
    def level(self) -> int:
        return self['level']

    @classmethod
    def clear_element_cache(cls):
        cls._get_parent.cache_clear()
        cls._get_child.cache_clear()
        cls._get_children.cache_clear()
        cls._parent_element.cache_clear()

    def update(self):
        if self.is_update:  # 锁避免重复调用
            self.clear_element_cache()
            self.update_relation()
            log.debug(f'update {self}\n')

    def update_level(self):
        def set_level(item, level):
            item['level'] = level + 1
            for j in item.child:
                set_level(j, item.level)

        for r in self.parent_element[self._children_ui_element_not_parent_key]:
            i = self.collection[r]
            set_level(i, 0)

    def update_child(self):
        ck = self._child_ui_key
        not_parent = []

        for el in self.collection:
            parent = el.parent
            if parent:
                if ck not in parent or type(parent[ck]) != list:
                    parent[ck] = [el.name, ]
                else:
                    parent[ck] += [el.name, ]

            else:
                not_parent.append(el)

        self.parent_element[self._children_ui_element_not_parent_key] = [i.name for i in not_parent]

    def update_relation(self):
        """更新级数和父级子级
        -添加时
        删除时
        移动时
        改名时
        copy
        """
        self.update_child()
        self.update_level()

    @have_update
    def change_name(self, old_name, new_name):
        log.debug(f'change_name {new_name}\n{self.child}')
        pk = self._parent_ui_key
        ck = self._child_ui_key
        for i in self.child:
            i[pk] = new_name
            log.debug(f'\t {i}\t{i[pk]}')
        if self.parent:
            cl = list(self.parent[ck])
            for index, j in enumerate(cl):
                if j == old_name:
                    cl[index] = new_name
                break
            self.parent[ck] = cl


class CRUD(RelationProperty):

    def remove(self, remove_child=False):

        def up_child(it):
            for j in it.child:
                j.parent = it.parent

        if remove_child:
            for i in self.child:
                i.remove(remove_child)
        up_child(self)
        log.debug(f'remove {self.name}  re_child = {remove_child}')
        self.parent_element.ui_items_collection_group.remove(self._index)
        self.clear_element_cache()

    @have_update
    def move(self, is_next=True):
        parent = self.parent_element
        col = parent.ui_items_collection_group

        self.move_collection_element(col,
                                     parent,
                                     is_next=is_next)
        self.check_parent_element()

    @have_update
    def copy(self, copy_child=False, parent: 'UiCollectionGroupElement' = None):
        new = self.parent_element.ui_items_collection_group.add()
        key = self._parent_ui_key

        def co(f, t):
            for i in list(f.keys()):  # 复制所有属性过去

                if i in ('name',
                         *self._not_copy_list,
                         ):  # 不设置子级和
                    continue
                elif i == key and parent:
                    t[i] = parent.name
                else:
                    t[i] = f[i]

        new.set_name(self.name)
        co(self, new)
        if copy_child:
            for c in self.child:
                c.copy(copy_child, new)
        log.debug(f'copy {self.name} to {new.name}')

    @have_update
    def move_to(self, to):
        self.parent = to


class UiCollectionGroupElement(CRUD):  # ui项
    ui_element_type: EnumProperty(items=UI_ELEMENT_TYPE_ENUM_ITEMS + UI_ELEMENT_SELECT_STRUCTURE_TYPE, )

    # def __str__(self):
    #     return self.__class__.__name__ + self['name']

    @property
    def is_select_structure(self):
        return self.ui_element_type.lower() in SELECT_STRUCTURE

    @property
    def _items(self):
        self.check_parent_element()
        key = self[self._parent_element_key]
        return self.element_items[key].ui_items_collection_group

    @property
    def _index(self):
        return self.parent_element.ui_items_collection_group.values().index(self)

    def register_key(self):
        ...

    def unregister_key(self):
        ...


class_tuple = (
    UiElement,

    UiCollectionGroupElement,
)

register_class, unregister_class = bpy.utils.register_classes_factory(class_tuple)


def register():
    register_class()


def unregister():
    unregister_class()

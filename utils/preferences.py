import bpy.utils
from bpy.props import CollectionProperty, IntProperty, BoolProperty, PointerProperty, FloatProperty
from bpy.types import AddonPreferences, PropertyGroup

from . import gesture
from .gesture.element.element_property import ElementAddProperty
from .public import ADDON_NAME, get_pref, PublicProperty

AddElementProperty = type('Add Element Property', (ElementAddProperty, PropertyGroup), {})


class DrawProperty(PropertyGroup):
    element_split_factor: FloatProperty(name='拆分系数', default=0.09, max=0.95, min=0.01)
    element_show_enabled_button: BoolProperty(name='显示 启用/禁用 按钮', default=False)
    element_debug_mode: BoolProperty(name='Debug模式', default=False)
    element_show_left_side: BoolProperty(name='显示在左侧', default=False)


class ElementDraw:
    @staticmethod
    def draw_property(layout: 'bpy.types.UILayout') -> None:
        pref = get_pref()
        act = pref.active_element
        prop = pref.draw_property
        if act:
            if not prop.element_show_left_side:
                act.draw_item_property(layout)
            if prop.element_debug_mode:
                act.draw_debug(layout)
        else:
            layout.label(text='请 选择或添加 一个手势元素')

    @staticmethod
    def draw_element_cure(layout: 'bpy.types.UILayout', cls) -> None:
        column = layout.column(align=True)
        column.operator(
            cls.REMOVE.bl_idname,
            icon='REMOVE',
            text=''
        )

    @staticmethod
    def draw_element_add_property(layout: 'bpy.types.UILayout') -> None:
        from .enum import ENUM_ELEMENT_TYPE, ENUM_SELECTED_TYPE
        from .gesture.element import ElementCURE

        pref = get_pref()
        add = pref.add_element_property

        relationship = add.relationship
        add_child = add.is_have_add_child

        split = layout.split(factor=.4)

        row = split.row(align=True)
        row.label(text='添加元素关系')
        row.prop(add, 'relationship', expand=True)

        sub_row = split.row(align=True)
        sub_row.enabled = add_child

        if add_child:
            element_row = sub_row.row(align=True)
            element_row.separator()
            element_row.label(text='添加项:')
            for i, n, d in ENUM_ELEMENT_TYPE:
                if i != 'SELECTED_STRUCTURE':
                    ops = element_row.operator(ElementCURE.ADD.bl_idname, text=n)
                    ops.element_type = i
                    ops.relationship = relationship
            element_row.separator()
            for i, n, d in ENUM_SELECTED_TYPE:
                ops = element_row.operator(ElementCURE.ADD.bl_idname, text=n)
                ops.element_type = 'SELECTED_STRUCTURE'
                ops.selected_type = i
                ops.relationship = relationship
        else:
            sub_row.row(align=True).label(text="无法为 '操作符' 添加子级")


class GestureDraw:

    @staticmethod
    def draw_gesture_cure(layout: 'bpy.types.UILayout') -> None:
        from .gesture import gesture_cure
        GestureDraw.public_cure(layout, gesture_cure.GestureCURE)

    @staticmethod
    def draw_gesture_key(layout) -> None:
        pref = get_pref()
        active = pref.active_gesture
        if active:
            column = layout.column()
            column.active = active.is_enable
            active.draw_key(column)
        else:
            layout.label(text='Not Select Gesture')

    @staticmethod
    def draw_gesture(layout: bpy.types.UILayout) -> None:
        from ..ui.ui_list import GestureUIList
        pref = get_pref()
        row = layout.row(align=True)
        GestureDraw.draw_gesture_cure(row)
        column = row.column(align=True)
        column.template_list(
            GestureUIList.bl_idname,
            GestureUIList.bl_idname,
            pref,
            'gesture',
            pref,
            'index_gesture',
        )
        GestureDraw.draw_gesture_key(column)

    @staticmethod
    def draw_element(layout: bpy.types.UILayout) -> None:
        from ..ui.ui_list import ElementUIList
        pref = get_pref()
        active_gesture = pref.active_gesture
        if active_gesture:
            column = layout.column()

            ElementDraw.draw_element_add_property(column)
            row = column.row(align=True)

            sub_column = row.column()
            sub_column.template_list(
                ElementUIList.bl_idname,
                ElementUIList.bl_idname,
                active_gesture,
                'element',
                active_gesture,
                'index_element',
            )
            ElementDraw.draw_property(sub_column)

            GestureDraw.draw_element_cure(row)
        else:
            layout.label(text='请添加或选择一个手势')

    @staticmethod
    def draw_element_cure(layout: bpy.types.UILayout) -> None:
        from .gesture import ElementCURE
        GestureDraw.public_cure(layout, ElementCURE)

    @staticmethod
    def public_cure(layout, cls) -> None:
        is_element = cls.__name__ == 'ElementCURE'
        pref = get_pref()
        draw_property = pref.draw_property

        column = layout.column(align=True)
        if is_element:
            ElementDraw.draw_element_cure(column, cls)
            column.separator()
        else:
            column.operator(
                cls.ADD.bl_idname,
                icon='ADD',
                text=''
            )
            column.operator(
                cls.REMOVE.bl_idname,
                icon='REMOVE',
                text=''
            )

        column.separator()

        column.operator(
            cls.SORT.bl_idname,
            icon='SORT_DESC',
            text=''
        ).is_next = False
        if is_element:
            column.operator(
                cls.MOVE.bl_idname,
                icon='CANCEL' if pref.is_move_element else 'GRIP',  # TODO if is move
                text=''
            )
        column.operator(
            cls.SORT.bl_idname,
            icon='SORT_ASC',
            text=''
        ).is_next = True

        if is_element:
            column.separator()
            icon = 'ALIGN_LEFT' if draw_property.element_show_left_side else 'ALIGN_RIGHT'
            column.prop(draw_property, 'element_show_left_side', icon=icon, text='', emboss=False)


class BlenderPreferencesDraw(GestureDraw):

    # 绘制右边层
    def right_layout(self: bpy.types.Panel, context: bpy.context):
        pref = get_pref()
        draw_property = pref.draw_property
        act = pref.active_element

        layout = self.layout
        layout.label(text='right_layout')

        column = layout.column()
        column.prop(pref, 'enabled')
        split = column.split()

        if draw_property.element_show_left_side:  # 绘制属性在左侧
            box = split.box()
            if act:
                act.draw_item_property(box)
            else:
                box.label(text='请 选择或添加 一个手势元素')
        else:
            GestureDraw.draw_gesture(split)
        GestureDraw.draw_element(split)

    def left_layout(self: bpy.types.Panel, context: bpy.context):
        layout = self.layout
        layout.label(text='left_layout')

    def bottom_layout(self: bpy.types.Panel, context: bpy.context):
        layout = self.layout
        layout.label(text='bottom_layout')
        BlenderPreferencesDraw.exit(layout)

    def left_bottom_layout(self: bpy.types.Panel, context: bpy.context):
        layout = self.layout
        layout.label(text='left_bottom_layout')
        BlenderPreferencesDraw.exit(layout)

    @staticmethod
    def exit(layout: 'bpy.types.UILayout') -> 'bpy.types.UILayout.operator':
        """退出按钮"""
        from ..ops.switch_ui import SwitchGestureWindow
        layout.alert = True
        return layout.operator(SwitchGestureWindow.bl_idname,
                               text='退出',
                               icon='PANEL_CLOSE'
                               )


class GesturePreferences(PublicProperty,
                         AddonPreferences,
                         BlenderPreferencesDraw):
    bl_idname = ADDON_NAME

    # 项配置
    gesture: CollectionProperty(type=gesture.Gesture)
    index_gesture: IntProperty(name='手势索引')
    is_preview: BoolProperty(name='是在预览模式')  # TODO

    add_element_property: PointerProperty(type=AddElementProperty)
    draw_property: PointerProperty(type=DrawProperty)

    enabled: BoolProperty(
        name='启用手势',
        description="""启用禁用整个系统,主要是keymap""",
        default=True, update=lambda self, context: gesture.GestureKeymap.key_restart())

    is_move_element: BoolProperty(
        default=False,
        description="""TODO 移动元素 整个元素需要只有移动操作符可用"""  # TODO
    )

    def draw(self, context):
        from ..ops.switch_ui import SwitchGestureWindow

        layout = self.layout
        layout.operator(SwitchGestureWindow.bl_idname)
        self.right_layout(layout)


classes_list = (
    DrawProperty,
    AddElementProperty,
    GesturePreferences,
)

register_classes, unregister_classes = bpy.utils.register_classes_factory(classes_list)


def register():
    gesture.register()
    register_classes()


def unregister():
    unregister_classes()
    gesture.unregister()

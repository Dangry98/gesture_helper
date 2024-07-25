import bpy
from mathutils import Vector

from ..lib.bpu import BpuLayout
from ..utils.public import PublicOperator, PublicProperty


def __draw__(bpu, event):
    # column = bpu.column()
    column = bpu
    column.label(event.type)
    a = column.operator("mesh.primitive_plane_add", text="Emm 添加")
    a.size = 10

    menu = column.menu("text")
    menu.active = True
    menu.label("fsef开发了可发二十艾萨克发生")
    menu.operator("mesh.primitive_plane_add", "aaaaa爱上发涩发a")
    menu.label("fsef1")
    menu.label("fsef2")
    menu.operator("mesh.primitive_plane_add", "fasefase某某地某某地")

    for i in range(4):
        column.label(f"text {i} sdjrogijsodirgiosjdrg")
    column.separator()

    ops = column.operator("mesh.primitive_plane_add")
    ops.size = 100

    m = menu.menu("sub", "test_id")
    m.active = True
    m.label("sub menu 1")
    m.label("sub menu 2")
    m.label("sub menu A")
    ops = m.operator("mesh.primitive_plane_add", "AAAAA")
    ops = m.operator("mesh.primitive_plane_add", "AAseA")
    ops = m.operator("mesh.primitive_plane_add", "AAAefaefA")

    column.label(event.value)


class GestureQuickAddKeymap:
    """注册快捷键"""
    kc = bpy.context.window_manager.keyconfigs.addon  # 获取按键配置addon的
    km = kc.keymaps.new(name='Window', space_type='EMPTY', region_type='WINDOW')
    kmi = None

    @classmethod
    def register(cls):
        cls.kmi = cls.km.keymap_items.new(GestureQuickAdd.bl_idname, 'ACCENT_GRAVE', 'PRESS',
                                          ctrl=True, alt=True, shift=True)

    @classmethod
    def unregister(cls):
        cls.km.keymap_items.remove(cls.kmi)


class GestureQuickAdd(PublicOperator, PublicProperty):
    bl_idname = "gesture.quick_add"
    bl_label = "Quick Add"
    is_in_quick_add = False  # 是在添加模式

    def __init__(self):
        super().__init__()
        self.mouse_position = None
        self.__difference_mouse__ = None
        self.gesture_bpu = BpuLayout()
        self.gesture_bpu.font_size = 20

        self.start_mouse_position = None
        self.offset_position = Vector((0, 0))

    @classmethod
    def poll(cls, context):
        return not cls.is_in_quick_add

    @property
    def is_exit(self):
        return self.is_right_mouse

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
        self.start_mouse_position = Vector((event.mouse_x, event.mouse_y))
        self.offset_position = self.start_mouse_position
        self.init_invoke(event)

        wm = context.window_manager
        wm.modal_handler_add(self)
        GestureQuickAdd.is_in_quick_add = True

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        self.mouse_position = Vector((event.mouse_x, event.mouse_y))
        # print(event.type, event.value, "\tprev", event.type_prev, event.value_prev)
        self.init_module(event)
        if self.draw_gesture_gpu(event):
            return {'RUNNING_MODAL'}
        e = self.modal_event(event)
        if e:
            return e
        return {'PASS_THROUGH'}

    def draw_gesture_gpu(self, event):
        try:
            self.gesture_bpu.register_draw()
            with self.gesture_bpu as bpu:
                bpu.offset_position = self.offset_position - Vector((600, 0))
                bpu.mouse_position = self.mouse_position
                # __draw__(bpu, event)
                for g in self.pref.gesture.values()[::-1]:
                    o = bpu.operator("wm.context_set_int", g.name, active=g.is_active)
                    o.data_path = "window_manager.gesture_index"
                    o.value = g.index
                bpu.separator()
                bpu.label("选择手势")

                if bpu.check_event(event):
                    return True
        except Exception as e:
            self.gesture_bpu.unregister_draw()
            print(e.args)

    def modal_event(self, event):
        space = (event.type == "SPACE" and not event.alt and not event.ctrl and not event.shift)
        mv = (event.type == "MOUSEMOVE" and event.type_prev == "SPACE")
        if space or mv:
            if event.value == "PRESS":
                self.__difference_mouse__ = self.start_mouse_position - self.mouse_position
            elif event.value == "RELEASE":
                self.__difference_mouse__ = None
            elif self.__difference_mouse__:
                nd = self.start_mouse_position - self.mouse_position
                d = self.__difference_mouse__ - nd
                self.offset_position = self.mouse_position - d
            return {'PASS_THROUGH', 'RUNNING_MODAL'}

        if self.is_exit:
            self.gesture_bpu.unregister_draw()
            GestureQuickAdd.is_in_quick_add = False
            return {'FINISHED'}

from math import pi

import bpy
from bpy.props import StringProperty
from mathutils import Vector

from ..utils.public import PublicClass
from ..utils.public.public_gpu import PublicGpu
from ..utils.public.public_operator import PublicOperator


class OpsProp(PublicOperator,
              ):
    system: StringProperty()
    gesture_points = []
    gesture_items = []
    active_gesture = None

    @property
    def current_system(self):
        return self.pref.systems.get(self.system)

    @property
    def system_type(self):
        return self.current_system.system_type

    @property
    def is_exit(self):
        return self.event.value == 'RELEASE'

    @property
    def active_point(self):
        return self.gesture_points[-1]

    @property
    def gesture_direction(self, split=22.5) -> int:
        def gesture_index(ang: float) -> int:
            an = abs(ang)
            if split < an < (split + 45):
                return 5 if ang < 0 else 7
            elif (90 - split) < an < (90 + split):
                return 4 if ang < 0 else 3
            elif (90 + split) < an < (90 + split + 45):
                return 6 if ang < 0 else 8

        vector = self.mouse_co - self.active_point
        if vector == Vector((0, 0)):
            return -1  # 没有任何朝向
        angle = (180 * vector.angle_signed(Vector((-1, 0)))) / pi

        max_split = 180 - split

        if -split < angle < split:
            return 1
        elif (max_split < angle) | (angle < -max_split):
            return 2
        else:
            return gesture_index(angle)

    @property
    def gesture_distance(self):
        """获取手势相对活动点的移动距离"""
        return (self.mouse_co - self.active_point).magnitude

    @property
    def beyond_distance(self):
        return 100

    def _beyond_distance(self, distance):
        return self.gesture_distance > (distance + distance * 0.3)

    @property
    def gesture_about_beyond_distance(self):
        return self._beyond_distance(self.beyond_distance - 20)

    @property
    def gesture_beyond_distance(self) -> bool:
        return self._beyond_distance(self.beyond_distance)

    @property
    def gesture_point_item(self):
        """获取手势指向项

        Returns:
            UIElementItem: _description_
        """
        act = self.active_gestures_item
        dire = self.gestures_direction
        items = self.item.__get_gestures_direction_items__(act)

        if not dire:
            return

        switch_dire = {3: 4, 4: 3}
        dire = switch_dire[dire] if dire in switch_dire else dire

        index = dire - 1  # ERROR上下颠倒
        return items[index] if dire else None

    @property
    def is_beyond_distance_event(self) -> bool:
        """获取 手势超出距离 并且朝向的项是有效的布尔值

        Returns:
            _type_: _description_
        """
        return self.gesture_beyond_distance and self.gesture_point_item


class GestureDraw(OpsProp,
                  PublicGpu):
    data = {}
    _handler_draw_gesture = []

    def register_draw_gesture(self):
        GestureDraw._handler_draw_gesture.append(
            bpy.types.SpaceView3D.draw_handler_add(
                self.draw_gesture_system, (),
                'WINDOW', 'POST_PIXEL'))

    @staticmethod
    def unregister_draw_gesture():
        while len(GestureDraw._handler_draw_gesture):
            bpy.types.SpaceView3D.draw_handler_remove(GestureDraw._handler_draw_gesture.pop(), 'WINDOW')

    def draw_gesture_system(self):
        self.draw_gesture_points()
        self.draw_gesture_line()
        self.draw_gesture_items()
        self.draw_test()

    def draw_gesture_line(self):
        self.draw_2d_line(self.gesture_points + [self.mouse_co, ], (1.0, 0.5, 0.5, 1), 3.4)

    def draw_gesture_points(self):
        self.draw_2d_points(self.gesture_points)

    def draw_gesture_items(self):
        for i in range(8):
            TempDrawGesture().draw_gesture(self, i + 1, False)

    def draw_test(self):
        import gpu
        from gpu_extras.batch import batch_for_shader
        vertices = (
            (100, 100), (300, 100),
            (100, 200), (300, 200))

        indices = (
            (0, 1, 2), (2, 1, 3))

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

        shader.uniform_float("color", (0, 0.5, 0.5, 1.0))
        batch.draw(shader)

        # for item in self.wait_draw_gesture_items:
        #     item.draw_gesturre()

        import blf
        import bpy

        font_info = {
            "font_id": 0,
            "handler": None,
        }

        import os
        # Create a new font object, use external ttf file.
        font_path = bpy.path.abspath('//Zeyada.ttf')
        # Store the font indice - to use later.
        if os.path.exists(font_path):
            font_info["font_id"] = blf.load(font_path)
        else:
            # Default font.
            font_info["font_id"] = 0

        # set the font drawing routine to run every frame
        # def draw_callback_px(self, context):
        #     """Draw on the viewports"""
        #     # BLF drawing routine
        font_id = font_info["font_id"]
        blf.position(font_id, 2, 80, 0)
        blf.size(font_id, 50)
        blf.draw(font_id, str(self.gesture_direction))
        blf.position(font_id, 200, 800, 0)
        # blf.draw(font_id, str([i.name for i in self.wait_draw_gesture_items]))
        blf.draw(font_id, str(self.test))
        blf.position(font_id, 200, 500, 0)
        blf.draw(font_id,
                 str([
                     self.gesture_about_beyond_distance,
                     self.gesture_beyond_distance,
                     int(self.gesture_distance),
                 ]))


class GestureOps(GestureDraw):
    test = []

    def clear_gesture_data(self):
        self.gesture_points.clear()

    def update_data(self, context, event):
        GestureDraw.data['ops'] = self
        GestureDraw.data['event'] = event
        GestureDraw.data['context'] = context
        self.test = event.mouse_x, event.mouse_y

    def invoke_gesture(self, context, event):
        self.update_data(context, event)
        self.gesture_points.append(self.start_mouse_co)

        context.window_manager.modal_handler_add(self)
        self.register_draw_gesture()
        return {'RUNNING_MODAL'}

    def modal_gesture(self, context, event):
        self.update_data(context, event)
        if self.is_exit:
            self.exit()
            return {'FINISHED'}
        elif self.gesture_beyond_distance:
            self.gesture_points.append(self.mouse_co)
        self.tag_redraw(context)
        return {'RUNNING_MODAL'}

    def exit_gesture(self):
        self.unregister_draw_gesture()
        self.clear_gesture_data()


class TempDrawGesture(PublicClass, PublicGpu):
    direction: int
    width = 50
    height = 20
    direction_angle_maps = {
        1: 4,
        2: 0,
        3: -2,
        4: 2,
        5: 3,
        6: 1,
        7: -3,
        8: -1,

    }

    @property
    def start_point(self):
        w, h = self.width, self.height
        c_w = w / 2
        c_h = h / 2
        direction_map = {
            1: (-w, -c_h),
            2: (0, -c_h),
            3: (-c_w, -h),
            4: (-c_w, 0),
            5: (-w, 0),
            6: (0, 0),
            7: (-w, -h),
            8: (0, -h),
        }
        return self.point + Vector(direction_map[self.direction])

    def draw_gesture(self, ops, direction, is_about_beyond: bool):
        a = self.direction_angle_maps[direction]
        point = self.calculate_point_on_circle(ops.active_point, ops.beyond_distance, a * 45)
        self.direction = direction
        self.point = point
        self.draw_2d_points([point, ])
        self.draw_background()
        self.draw_text()

    def draw_background(self):
        x, y = self.start_point
        self.draw_2d_rectangle(x, y, x + self.width, y + self.height)

    def draw_text(self):
        x, y = self.start_point
        self.draw_2d_text(str(self.direction), self.height, x, y)


class SystemOps(GestureOps,
                ):
    bl_idname = PublicOperator.ops_id_name('gesture_ops')
    bl_label = 'Gesture Ui Operator'

    def invoke(self, context, event):
        self.init_invoke(context, event)
        self.tag_redraw(context)
        if not self.current_system:
            self.report({'WARNING': f'Not Find System {self.system}'})
        else:
            return getattr(self, f'invoke_{self.system_type.lower()}')(context, event)

    def modal(self, context, event):
        self.init_modal(context, event)
        return getattr(self, f'modal_{self.system_type.lower()}')(context, event)

    def exit(self):
        getattr(self, f'exit_{self.system_type.lower()}')()
        self.tag_redraw(bpy.context)


classes_tuple = (
    SystemOps,
)

register_class, unregister_class = bpy.utils.register_classes_factory(classes_tuple)


def register():
    register_class()


def unregister():
    unregister_class()
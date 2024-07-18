import blf
from mathutils import Vector

from .bpu_property import BpuProperty
from .bpu_type import Quadrant


class BpuMeasure(BpuProperty):
    # text  不含边距
    __width__ = -1
    __height__ = -1

    # layout  不含边距
    __height_list__ = []
    __width_list__ = []

    __is_measurements_completed__ = False  # 是已完成测量

    def __init__(self):
        super().__init__()
        self.__is_measurements_completed__ = False
        self.__height_list__ = []
        self.__width_list__ = []

    @property
    def __max_width__(self) -> int:
        if self.__width_list__:
            return max(self.__width_list__)
        return -1

    @property
    def __max_height__(self) -> int:
        if self.__height_list__:
            return max(self.__height_list__)
        return -1


    def __measure__(self, parent=None) -> None:
        """测量数据"""
        if self.__is_measurements_completed__:
            # 测量过,跳过
            return

        self.__height_list__ = []
        self.__width_list__ = []

        if self.type.is_draw_text:
            blf.size(self.font_id, self.font_size)
            (self.__width__, self.__height__) = blf.dimensions(self.font_id, self.text)
        elif self.type.is_draw_child:
            for child in self.__draw_children__:
                child.__measure__(self)
                self.__width_list__.append(child.draw_width)
                self.__height_list__.append(child.draw_height)

            self.__width__ = sum(self.__width_list__)
            self.__height__ = sum(self.__height_list__)
        self.__is_measurements_completed__ = True

    @property
    def draw_height(self) -> int:
        """绘制高度
        只有在绘制layout的时侯才需要此属性"""
        self.__measure__()

        margin = self.__margin__
        if self.type.is_horizontal_layout:
            return self.__max_height__ + margin * 2
        elif self.type.is_vertical_layout:
            return self.__height__ + margin * 2

        # 文字
        return self.__height__ + margin * 2

    @property
    def draw_width(self) -> int:
        """绘制宽度
        只有在绘制layout的时侯才需要此属性"""
        self.__measure__()

        margin = self.__margin__

        if self.type.is_horizontal_layout:
            return self.__width__ + margin * 2
        elif self.type.is_vertical_layout:
            return self.__max_width__ + margin * 2

        # 文字
        return self.__width__ + margin * 2

    @property
    def draw_size(self):
        return self.draw_width, self.draw_height

    def child_offset(self, parent: 'BpuMeasure', index: int = 0) -> Vector:
        """
        子级偏移量
        :param index:
        :param parent:
        :return:
        """
        if parent.type.is_parent:
            return Vector([0, 0])
        elif parent.type.is_horizontal_layout:
            return Vector((self.draw_width, 0))
        elif parent.type.is_vertical_layout:
            return Vector((0, self.draw_height))
        else:
            return Vector(self.draw_size)

    def parent_offset(self, parent: 'BpuMeasure' = None) -> Vector:
        margin = self.__margin__
        if self.type.is_parent:
            return Vector([0, 0])
        else:
            return Vector([margin, margin])
        # elif parent and parent.type.is_parent:
        # return Vector([parent.__margin__, parent.__margin__])
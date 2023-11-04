# 每一项手势的快捷键
# 不需要去记录每一个快捷键的位置
# 只需要记录快捷键用到的数据和空间
# 每次开启插件的时候从数据里面当场新建一些快捷键并填入缓存数据
# 使用临时快捷键来修改每一个快捷键的位置
import traceback

import bpy
from bpy.types import KeyMapItem, PropertyGroup
from idprop.types import IDPropertyGroup

from .. import PropertyGetUtils
from ..key import get_temp_kmi, get_temp_keymap, add_addon_kmi
from ..public import PublicProperty
from ...ops import key


def draw_kmi(layout: bpy.types.UILayout, kmi: 'bpy', key_maps):
    map_type = kmi.map_type

    col = layout.column()

    if kmi.show_expanded:
        col = col.column(align=True)
        box = col.box()
    else:
        box = col.column()

    split = box.split()

    # header bar
    row = split.row(align=True)
    row.prop(kmi, "show_expanded", text="", emboss=False)
    # row.prop(kmi, "active", text="", emboss=False)
    row.operator(key.OperatorSetKeyMaps.bl_idname)

    row = split.row()
    row.prop(kmi, "map_type", text="")
    if map_type == 'KEYBOARD':
        row.prop(kmi, "type", text="", full_event=True)
    elif map_type == 'MOUSE':
        row.prop(kmi, "type", text="", full_event=True)
    elif map_type == 'NDOF':
        row.prop(kmi, "type", text="", full_event=True)
    elif map_type == 'TWEAK':
        sub_row = row.row()
        sub_row.prop(kmi, "type", text="")
        sub_row.prop(kmi, "value", text="")
    elif map_type == 'TIMER':
        row.prop(kmi, "type", text="")
    else:
        row.label()

    row.operator("preferences.keyitem_restore", text="", icon='BACK').item_id = kmi.id
    # Expanded, additional event settings
    if kmi.show_expanded:
        box = col.box()
        if map_type not in {'TEXTINPUT', 'TIMER'}:
            sub = box.column()
            sub_row = sub.row(align=True)

            if map_type == 'KEYBOARD':
                sub_row.prop(kmi, "type", text="", event=True)
                sub_row.prop(kmi, "value", text="")
                sub_row_repeat = sub_row.row(align=True)
                sub_row_repeat.active = kmi.value in {'ANY', 'PRESS'}
                sub_row_repeat.prop(kmi, "repeat", text="Repeat")
            elif map_type in {'MOUSE', 'NDOF'}:
                sub_row.prop(kmi, "type", text="")
                sub_row.prop(kmi, "value", text="")

            if map_type in {'KEYBOARD', 'MOUSE'} and kmi.value == 'CLICK_DRAG':
                sub_row = sub.row()
                sub_row.prop(kmi, "direction")

            sub_row = sub.row()
            sub_row.scale_x = 0.75
            sub_row.prop(kmi, "any", toggle=True)
            # Use `*_ui` properties as integers aren't practical.
            sub_row.prop(kmi, "shift_ui", toggle=True)
            sub_row.prop(kmi, "ctrl_ui", toggle=True)
            sub_row.prop(kmi, "alt_ui", toggle=True)
            sub_row.prop(kmi, "oskey_ui", text="Cmd", toggle=True)

            sub_row.prop(kmi, "key_modifier", text="", event=True)

        col = box.column(align=True)
        for k in key_maps:
            col.label(text=k)


class TempKey(PropertyGroup, PublicProperty):

    @property
    def temp_kmi_data(self):
        return dict(
            PropertyGetUtils.props_data(
                self.temp_kmi,
                exclude=(
                    'name', 'id', 'show_expanded', 'properties', 'idname', 'map_type', 'active', 'propvalue',
                    'shift_ui', 'ctrl_ui', 'alt_ui', 'oskey_ui'
                )
            )
        )

    @property
    def temp_kmi(self) -> 'KeyMapItem':
        return get_temp_kmi(key.OperatorTempModifierKey.bl_idname, {'gesture': self.name})


class UpdateKey(TempKey):

    def _set_key(self, value):
        self['key'] = value
        self.update_key()

    def _get_key(self):
        default = {'type': 'NONE', 'value': 'PRESS'}
        if 'key' in self and dict(self['key']):
            default.update(
                {k: dict(value) if type(value) == IDPropertyGroup else value
                 for (k, value) in
                 dict(self['key']).items()}
            )
        return default

    def _get_keymap(self):
        return self['keymap'] if 'keymap' in self else ['Window', ]

    def _set_keymap(self, value):
        self['keymap'] = value
        self.update_key()

    key = property(fget=_get_key, fset=_set_key, doc='用来存快捷键的键位数据')
    keymaps = property(fget=_get_keymap, fset=_set_keymap, doc='用来存快捷键可用的区域')

    @property
    def add_kmi_data(self):
        from ...ops import gesture
        return {'idname': gesture.GestureOperator.bl_idname, **self.temp_kmi_data}

    def from_temp_key_update_data(self):
        data = self.temp_kmi_data
        if self.key != data:
            self.key = data


class GestureKey(UpdateKey):
    __key_data__ = {}  # {self:(keymap:kmi)}

    def draw_key(self, layout):
        layout.context_pointer_set('keymap', get_temp_keymap())

        layout.operator(key.OperatorSetKeyMaps.bl_idname)
        layout.operator(key.OperatorTempModifierKey.bl_idname)

        draw_kmi(layout, self.temp_kmi, self.keymaps)
        layout.label(text=str(self.key))
        layout.label(text=str(self.keymaps))
        layout.label(text=str(self.temp_kmi.id))
        layout.label(text=str(self.temp_kmi))
        layout.label(text=str(self.temp_kmi_data))
        # TODO 在keymap被改时更新
        # TODO 在key被改时更新
        self.from_temp_key_update_data()

    def load_key(self):
        if not self.enable:
            return

        if self in GestureKey.__key_data__:  # 还没注销
            self.unload_key()

        data = GestureKey.__key_data__[self] = []
        for keymap in self.keymaps:
            data.append(add_addon_kmi(keymap, self.add_kmi_data, {'gesture': self.name}))

        print('load_key', self.name)
        print(self.key)
        print(self.keymaps)
        print(self.temp_kmi)
        print(self.temp_kmi_data)
        print(GestureKey.__key_data__)
        print()

    def unload_key(self):
        if self in GestureKey.__key_data__:  # 如果被禁用了会出现没有快捷键的情况
            for keymap, kmi in GestureKey.__key_data__[self]:
                keymap.keymap_items.remove(kmi)
            GestureKey.__key_data__.pop(self)

    def update_key(self):
        caller_name = traceback.extract_stack()[-2][2]
        print("update_key 被 {} 调用".format(caller_name), self)
        self.unload_key()
        self.load_key()

    @classmethod
    def start_load_key(cls):
        for g in cls._pref().gesture:
            g.load_key()

    @classmethod
    def stop_unload_key(cls):
        for g in cls._pref().gesture:
            g.unload_key()

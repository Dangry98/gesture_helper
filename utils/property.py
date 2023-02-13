from .utils import from_bl_rna_get_bl_property_data

rna_data = from_bl_rna_get_bl_property_data

# misc get property

icon_enum = rna_data(EnumPropertyItem, 'icon')
icon_enum['items'] = [icon[:3] + icon[:1] + icon[-1:]
                      for icon in icon_enum['items'][1:]]

ui_events_keymaps = i18n_contexts.ui_events_keymaps

# ui get  property
ui_emboss_enum = rna_data(UILayout, 'emboss')
ui_alignment = rna_data(UILayout, 'alignment')
ui_direction = rna_data(UILayout, 'direction')
ui_operator_context = rna_data(
    UILayout, 'operator_context', )

# pie property  # 饼菜单所需属性
pie_property_items = ['pie_animation_timeout',
                      'pie_tap_timeout',
                      'pie_initial_timeout',
                      'pie_menu_radius',
                      'pie_menu_threshold',
                      'pie_menu_confirm',
                      ]
pie_animation_timeout = rna_data(
    PreferencesView, 'pie_animation_timeout', fill_copy=True)
pie_tap_timeout = rna_data(
    PreferencesView, 'pie_tap_timeout', fill_copy=True)
pie_initial_timeout = rna_data(
    PreferencesView, 'pie_initial_timeout', fill_copy=True)
pie_menu_radius = rna_data(
    PreferencesView, 'pie_menu_radius', fill_copy=True)
pie_menu_threshold = rna_data(
    PreferencesView, 'pie_menu_threshold', fill_copy=True)
pie_menu_confirm = rna_data(
    PreferencesView, 'pie_menu_confirm', fill_copy=True)
# custom element property   default
pie_animation_timeout['default'] = 6
pie_tap_timeout['default'] = 20
pie_initial_timeout['default'] = 0
pie_menu_radius['default'] = 100
pie_menu_threshold['default'] = 20
pie_menu_confirm['default'] = 60
pie_animation_timeout['min'] = pie_tap_timeout['min'] = pie_initial_timeout[
    'min'] = pie_menu_radius['min'] = pie_menu_threshold['min'] = pie_menu_confirm['min'] = -1
pie_animation_timeout['soft_min'] = pie_tap_timeout['soft_min'] = pie_initial_timeout[
    'soft_min'] = pie_menu_radius['soft_min'] = pie_menu_threshold['soft_min'] = pie_menu_confirm['soft_min'] = 0

# kmi get property
kmi_type = rna_data(
    KeyMapItem, 'type', msgctxt=ui_events_keymaps)
kmi_value = rna_data(KeyMapItem, 'value')
kmi_map_type = rna_data(KeyMapItem, 'map_type')
kmi_key_modifier = rna_data(KeyMapItem, 'key_modifier')
kmi_value_enum = KeyMapItem.bl_rna.properties['type'].enum_items
kmi_map_type['items'].remove(('TIMER', 'Timer', '', 'NONE', 4))
kmi_map_type['items'].remove(('TEXTINPUT', 'Text Input', '', 'NONE', 3))
# kmi_value['items'].append(('DOUBLE_KEY',      '双键', '', 'NONE', -114))  TODO ERROR 和手势系统有冲突
# kmi_value['items'].append(('LONG_PRESS',      '长按', '', 'NONE', -514))
kmi_type_classify = {'TEXTINPUT': ('TEXTINPUT',),
                     'TIMER': ('TIMER', 'TIMER0', 'TIMER1', 'TIMER2',
                               'TIMER_JOBS', 'TIMER_AUTOSAVE', 'TIMER_REPORT', 'TIMERREGION'),
                     'MOUSE': ('LEFTMOUSE', 'MIDDLEMOUSE', 'RIGHTMOUSE', 'BUTTON4MOUSE', 'BUTTON5MOUSE', 'BUTTON6MOUSE',
                               'BUTTON7MOUSE', 'PEN', 'ERASER', 'MOUSEMOVE',
                               'TRACKPADPAN', 'TRACKPADZOOM', 'MOUSEROTATE', 'MOUSESMARTZOOM', 'WHEELUPMOUSE',
                               'WHEELDOWNMOUSE', 'WHEELINMOUSE', 'WHEELOUTMOUSE'),
                     'NDOF': (
                         'NDOF_MOTION', 'NDOF_BUTTON_MENU', 'NDOF_BUTTON_FIT', 'NDOF_BUTTON_TOP', 'NDOF_BUTTON_BOTTOM',
                         'NDOF_BUTTON_LEFT', 'NDOF_BUTTON_RIGHT', 'NDOF_BUTTON_FRONT', 'NDOF_BUTTON_BACK',
                         'NDOF_BUTTON_ISO1', 'NDOF_BUTTON_ISO2', 'NDOF_BUTTON_ROLL_CW', 'NDOF_BUTTON_ROLL_CCW',
                         'NDOF_BUTTON_SPIN_CW', 'NDOF_BUTTON_SPIN_CCW', 'NDOF_BUTTON_TILT_CW', 'NDOF_BUTTON_TILT_CCW',
                         'NDOF_BUTTON_ROTATE', 'NDOF_BUTTON_PANZOOM', 'NDOF_BUTTON_DOMINANT', 'NDOF_BUTTON_PLUS',
                         'NDOF_BUTTON_MINUS', 'NDOF_BUTTON_1', 'NDOF_BUTTON_2', 'NDOF_BUTTON_3', 'NDOF_BUTTON_4',
                         'NDOF_BUTTON_5', 'NDOF_BUTTON_6', 'NDOF_BUTTON_7', 'NDOF_BUTTON_8', 'NDOF_BUTTON_9',
                         'NDOF_BUTTON_10', 'NDOF_BUTTON_A', 'NDOF_BUTTON_B', 'NDOF_BUTTON_C'),

                     'KEYBOARD': (
                         'NONE', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
                         'R',
                         'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                         'ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE',
                         'LEFT_CTRL', 'LEFT_ALT', 'LEFT_SHIFT', 'RIGHT_ALT', 'RIGHT_CTRL', 'RIGHT_SHIFT', 'OSKEY',
                         'APP', 'GRLESS', 'ESC', 'TAB', 'RET', 'SPACE', 'LINE_FEED', 'BACK_SPACE', 'DEL', 'SEMI_COLON',
                         'PERIOD', 'COMMA', 'QUOTE', 'ACCENT_GRAVE', 'MINUS', 'PLUS', 'SLASH', 'BACK_SLASH', 'EQUAL',
                         'LEFT_BRACKET', 'RIGHT_BRACKET', 'LEFT_ARROW', 'DOWN_ARROW', 'RIGHT_ARROW', 'UP_ARROW',
                         'NUMPAD_2', 'NUMPAD_4', 'NUMPAD_6', 'NUMPAD_8', 'NUMPAD_1', 'NUMPAD_3', 'NUMPAD_5', 'NUMPAD_7',
                         'NUMPAD_9',
                         'NUMPAD_PERIOD', 'NUMPAD_SLASH', 'NUMPAD_ASTERIX', 'NUMPAD_0', 'NUMPAD_MINUS', 'NUMPAD_ENTER',
                         'NUMPAD_PLUS',
                         'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15',
                         'F16', 'F17', 'F18', 'F19', 'F20', 'F21', 'F22', 'F23', 'F24',
                         'PAUSE', 'INSERT', 'HOME', 'PAGE_UP', 'PAGE_DOWN', 'END', 'MEDIA_PLAY', 'MEDIA_STOP',
                         'MEDIA_FIRST', 'MEDIA_LAST',)
                     # 'INBETWEEN_MOUSEMOVE''WINDOW_DEACTIVATE', 'ACTIONZONE_AREA', 'ACTIONZONE_REGION', 'ACTIONZONE_FULLSCREEN', 'XR_ACTION'
                     }

# kmi property 存放默认添加的数据
DEFAULT_KEYMAPS = {'3D View', 'Window'}  # 默认添加keymaps

TIME_DEFAULT = {'max': 2000, 'min': -1, 'default': 300}
SKIP_DEFAULT = {'options': {'HIDDEN', 'SKIP_SAVE', }}
# ui items property
CUSTOM_UI_TYPE_ITEMS = (('panel', 'Panel', '绘制面板可在窗口工具栏或是侧边栏显示'),
                        ('menu', 'Menu', '菜单,指定快捷键设置弹出菜单'),
                        ('menu_pie', 'Pie Panel',
                         '饼菜单,指定快捷键设置弹出饼菜单,也可设置为手势系统,通过手势来'),
                        # ('layout',      'Layout',       ''), TODO
                        )

UI_LAYOUT_INCOMING_ITEMS = {  # uilayout 需传入参数
    'box': [],
    'menu_pie': [],  # 用column的数据
    'separator_spacer': [],

    'separator': ['factor'],

    'row': ['heading',
            'align',
            # 'heading_ctxt',# TODO ctxt
            'translate',
            ],
    'prop': ['text',
             'property',
             # 'data', #自动获取
             #  'icon',
             #  'icon_only',
             #  'text_ctxt',
             'expand',
             'translate',
             'slider',
             #  'event',
             #  'full_event',
             'emboss',
             'index',
             'icon_value',
             'invert_checkbox',
             'toggle',
             ],
    'split': ['factor',
              'align',
              ],
    'label': ['text',
              #   'text_ctxt',
              'translate',
              'icon',
              # 'icon_value',
              ],

    'menu': ['menu',
             'text',
             'translate',
             #  'text_ctxt',
             'icon',
             #  'icon_value',
             ],
    'menu_contents': ['menu'],

    'column': ['heading',
               'align',
               #    'heading_ctxt',
               'translate',
               ],
    'operator': ['operator',
                 'text',
                 #  'text_ctxt',
                 'translate',
                 'icon',
                 'emboss',
                 'depress',
                 #  'icon_value',
                 ],
    'uilayout': ['activate_init',
                 'active',
                 'scale_x',
                 'scale_y',
                 'ui_units_x',
                 'ui_units_y',
                 'active_default',
                 'alert',
                 'use_property_decorate',
                 'use_property_split',
                 'emboss_enum',
                 'enabled',
                 'alignment',
                 #  'direction', only read
                 #  'operator_context', operator
                 ],

    # 选择结构
    'if': ['poll_string'],
    'elif': ['poll_string'],
    'else': ['poll_string'],
}

UI_ELEMENT_TYPE_ENUM_ITEMS = [  # ui layout类型
    # ('separator_spacer',   'Separator Spacer', ''), TODO 用作Separator的附加属性
    ('label', 'Label', '',),
    ('separator', 'Separator', '',),
    ('', 'General', '',),

    ('row', 'Row', '',),
    ('box', 'Box', '',),
    ('split', 'Split', '',),
    ('column', 'Column', '',),
    ('menu_pie', 'Menu Pie', '',),
    ('', 'Layout', '',),

    ('menu', 'Menu', '',),
    ('prop', 'Prop', '',),
    ('operator', 'Operator', '',),
    ('', 'other', '',),
    # operator_menu_hold
    # operator_enum
    # operator_menu_enum
    # template_operator_search
    # popup_menu_pie TODO
    # ('',            'popup_menu', ''), TODO
]

SELECT_STRUCTURE = ('if', 'elif', 'else',)
UI_ELEMENT_SELECT_STRUCTURE_TYPE = [(i, i, '')  # 选择结构
                                    for i in SELECT_STRUCTURE
                                    ]

ALLOW_CHILD_TYPE = (  # 允许有子级的项
    'if', 'elif', 'else',  # 选择枚举
    'box', 'row', 'split', 'column', 'menu_pie')

CANNOT_ACT_AS_CHILD = (  # 无法作为子级 除选择结构外
    'menu_pie',
)

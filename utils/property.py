exclude_items = {'rna_type', 'bl_idname', 'srna'}  # 排除项

_base_data = {'name': 'name',
              'description': 'description',
              'options': 'options',
              'override': 'override',
              #   'tags': 'tags', ERROR
              }
_generic_data = {**_base_data,
                 'default': 'default',
                 'subtype': 'subtype',
                 }

_math_property = {**_generic_data,
                  'hard_min': 'min',  # change
                  'hard_max': 'max',  # change
                  'soft_min': 'soft_min',
                  'soft_max': 'soft_max',
                  'step': 'step',
                  }

_float_property = {**_math_property,
                   'precision': 'precision',
                   'unit': 'unit',
                   }

property_data = {  # 属性参数
    'EnumProperty': {'items': 'items',
                     **_generic_data},

    'StringProperty': {**_generic_data},

    'PointerProperty': {'type': 'type',
                        **_base_data},
    'CollectionProperty': {'type': 'type',
                           **_base_data},

    'BoolProperty': {**_generic_data},
    'BoolVectorProperty': {'size': 'size',
                           **_generic_data},

    'FloatProperty': _float_property,
    'FloatVectorProperty': {'size': 'size',
                            **_float_property},

    'IntProperty': _math_property,
    'IntVectorProperty': {'size': 'size', **_math_property},
}


def from_bl_rna_get_bl_property_data(parent_prop: object, property_name: str, msgctxt=None, fill_copy=False) -> dict:
    bl_rna = getattr(parent_prop, 'bl_rna', None)
    if not bl_rna:
        print(Exception(f'{parent_prop} no bl_rna'))
        return dict()

    ret_data = {}
    pro = bl_rna.properties[property_name]
    typ = pro.type
    property_fill_name = type(pro.type_recast()).__name__

    def get_t(text, msg):
        import bpy
        return bpy.app.translations.pgettext_iface(
            text, msgctxt=msg)

    if fill_copy:
        # 获取输入属性的所有参数
        for i in property_data[property_fill_name]:
            prop = getattr(pro, i, None)
            if prop is not None:
                index = property_data[property_fill_name][i]
                ret_data[index] = prop

    if typ == 'ENUM':
        ret_data['items'] = [(i.identifier,
                              get_t(i.name, msgctxt) if msgctxt else i.name,
                              i.description,
                              i.icon,
                              i.value)
                             for i in pro.enum_items]
    return ret_data


get_rna_data = from_bl_rna_get_bl_property_data
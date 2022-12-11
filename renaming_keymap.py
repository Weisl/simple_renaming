import bpy
import rna_keymap_ui

# kmi_name, kmi_value, km_name, space_type, region_type
# eventType, eventValue, ctrl, shift, alt
keymaps_items_dict = {"Renaming Popup": ['wm.call_panel', 'VIEW3D_PT_tools_renaming_panel', '3D View Generic', 'VIEW_3D', 'WINDOW',
                                         'F2', 'PRESS', True, False, False
                                         ],

                      "Suffix/Prefix Popup": ['wm.call_panel', 'VIEW3D_PT_tools_type_suffix', '3D View Generic', 'VIEW_3D', 'WINDOW',
                                              'F2', 'PRESS', True, True, False
                                              ],

                      "Renaming Popup Outliner": ['wm.call_panel', 'VIEW3D_PT_tools_renaming_panel',
                                                  'Outliner', 'OUTLINER', 'WINDOW',
                                                  'F2', 'PRESS', True, False, False
                                                  ]
                      }


# -----------------------------------------------------------------------------
#    Keymap
# -----------------------------------------------------------------------------
addon_keymaps = []


def draw_keymap_items(wm, layout):
    kc = wm.keyconfigs.user

    for name, items in keymaps_items_dict.items():
        kmi_name, kmi_value, km_name = items[:3]
        split = layout.split()
        col = split.column()
        col.label(text=name)
        km = kc.keymaps[km_name]
        get_hotkey_entry_item(kc, km, kmi_name, kmi_value, col)


def get_hotkey_entry_item(kc, km, kmi_name, kmi_value, col):

    # for menus and pie_menu
    if kmi_value:
        for km_item in km.keymap_items:
            if km_item.idname == kmi_name and km_item.properties.name == kmi_value:
                col.context_pointer_set('keymap', km)
                rna_keymap_ui.draw_kmi([], kc, km, km_item, col, 0)
                return

        col.label(text="No hotkey entry found for {}".format(kmi_value))
        col.operator(RENAMING_OT_add_hotkey_renaming.bl_idname, icon='ADD')

    # for operators
    else:
        if km.keymap_items.get(kmi_name):
            col.context_pointer_set('keymap', km)
            rna_keymap_ui.draw_kmi(
                [], kc, km, km.keymap_items[kmi_name], col, 0)
        else:
            col.label(text="No hotkey entry found for {}".format(kmi_name))
            col.operator(RENAMING_OT_add_hotkey_renaming.bl_idname, icon='ADD')


def remove_hotkey():
    ''' clears addon keymap hotkeys stored in addon_keymaps '''

    # only works for menues and pie menus
    for km, kmi in addon_keymaps:
        if hasattr(kmi.properties, 'name'):
            if kmi.properties.name in ['VIEW3D_PT_tools_renaming_panel', 'VIEW3D_PT_tools_type_suffix', 'VIEW3D_PT_tools_renaming_panel']:
                km.keymap_items.remove(kmi)

    addon_keymaps.clear()


def add_hotkey(context=None):
    '''Add default hotkey konfiguration'''
    if not context:
        context = bpy.context

    kc = context.window_manager.keyconfigs.addon

    if not kc:
        return

    for items in keymaps_items_dict.values():
        kmi_name, kmi_value, km_name, space_type, region_type = items[:5]
        eventType, eventValue, ctrl, shift, alt = items[5:]
        km = kc.keymaps.new(name=km_name, space_type=space_type,
                            region_type=region_type)

        kmi = km.keymap_items.new(kmi_name, eventType,
                                  eventValue, ctrl=ctrl, shift=shift,
                                  alt=alt

                                  )
        if kmi_value:
            kmi.properties.name = kmi_value

        kmi.active = True

    addon_keymaps.append((km, kmi))


class RENAMING_OT_add_hotkey_renaming(bpy.types.Operator):
    ''' Add hotkey entry '''
    bl_idname = "renaming.add_hotkey"
    bl_label = "Addon Preferences Example"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        add_hotkey(context)

        self.report({'INFO'},
                    "Hotkey added in User Preferences -> Input -> Screen -> Screen (Global)")

        return {'FINISHED'}


classes = (
    RENAMING_OT_add_hotkey_renaming,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    add_hotkey()


def unregister():
    remove_hotkey()

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

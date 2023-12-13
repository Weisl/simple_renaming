import bpy

keymaps_items_dict = {
    "Renaming Popup": ['wm.call_panel', 'VIEW3D_PT_tools_renaming_panel', '3D View Generic', 'VIEW_3D', 'WINDOW',
                       'F2', 'PRESS', True, False, True
                       ],

    "Suffix/Prefix Popup": ['wm.call_panel', 'VIEW3D_PT_tools_type_suffix', '3D View Generic', 'VIEW_3D', 'WINDOW',
                            'F2', 'PRESS', True, True, False
                            ],

    "Renaming Popup Outliner": ['wm.call_panel', 'VIEW3D_PT_tools_renaming_panel',
                                'Outliner', 'OUTLINER', 'WINDOW',
                                'F2', 'PRESS', True, False, False
                                ]
    }


def add_keymap():
    km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name="Window")
    prefs = bpy.context.preferences.addons[__package__.split('.')[0]].preferences


    kmi = km.keymap_items.new(idname='wm.call_panel', type=prefs.renaming_panel_type, value='PRESS',
                              ctrl=prefs.renaming_panel_ctrl, shift=prefs.renaming_panel_shift,
                              alt=prefs.renaming_panel_alt)
    add_key_to_keymap('VIEW3D_PT_tools_renaming_panel', kmi, km, active=prefs.renaming_panel_active)

    kmi = km.keymap_items.new(idname='wm.call_panel', type=prefs.renaming_suf_pre_type, value='PRESS',
                              ctrl=prefs.renaming_suf_pre_ctrl, shift=prefs.renaming_suf_pre_shift,
                              alt=prefs.renaming_suf_pre_alt)
    add_key_to_keymap('VIEW3D_PT_tools_type_suffix', kmi, km, active=prefs.renaming_suf_pre_active)


def add_key_to_keymap(idname, kmi, km, active=True):
    ''' Add ta key to the appropriate keymap '''
    kmi.properties.name = idname
    kmi.active = active
    # keys.append((km, kmi))


def remove_key(context, idname, properties_name):
    '''Removes addon hotkeys from the keymap'''
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps['Window']

    for kmi in km.keymap_items:
        if kmi.idname == idname and kmi.properties.name == properties_name:
            km.keymap_items.remove(kmi)


def remove_keymap():
    '''Removes keys from the keymap. Currently this is only called when unregistering the addon. '''
    # only works for menues and pie menus
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps['Window']

    for kmi in km.keymap_items:
        if hasattr(kmi.properties, 'name') and kmi.properties.name in ['COLLISION_MT_pie_menu',
                                                                       'VIEW3D_PT_collision_visibility_panel',
                                                                       'VIEW3D_PT_collision_material_panel']:
            km.keymap_items.remove(kmi)


class REMOVE_OT_hotkey(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "collision.remove_hotkey"
    bl_label = "Remove hotkey"
    bl_description = "Remove hotkey"
    bl_options = {'REGISTER', 'INTERNAL'}

    idname: bpy.props.StringProperty()
    properties_name: bpy.props.StringProperty()
    property_prefix: bpy.props.StringProperty()

    def execute(self, context):
        remove_key(context, self.idname, self.properties_name)

        prefs = context.preferences.addons[__package__.split('.')[0]].preferences
        setattr(prefs, f'{self.property_prefix}_type', "NONE")
        setattr(prefs, f'{self.property_prefix}_ctrl', False)
        setattr(prefs, f'{self.property_prefix}_shift', False)
        setattr(prefs, f'{self.property_prefix}_alt', False)

        return {'FINISHED'}


class RENAMING_OT_add_hotkey_renaming(bpy.types.Operator):
    ''' Add hotkey entry '''
    bl_idname = "utilities.add_hotkey"
    bl_label = "Addon Preferences Example"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        add_hotkey(context)
        return {'FINISHED'}

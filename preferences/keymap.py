import bpy

# keys = []


def add_keymap():
    km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name="Window")
    prefs = bpy.context.preferences.addons[__package__.split('.')[
        0]].preferences

    # type, ctrl, shift, alt parameters are stored and retrived from the preferences.
    kmi = km.keymap_items.new(idname='wm.call_menu_pie', type=prefs.collision_pie_type, value='PRESS',
                              ctrl=prefs.collision_pie_ctrl, shift=prefs.collision_pie_shift, alt=prefs.collision_pie_alt)

    # The active parameter is part of the keymap and not keymapitem.
    add_key_to_keymap("COLLISION_MT_pie_menu", kmi, km, active=prefs.collision_pie_active)
    kmi = km.keymap_items.new(idname='wm.call_panel', type=prefs.collision_visibility_type, value='PRESS',
                              ctrl=prefs.collision_visibility_ctrl, shift=prefs.collision_visibility_shift, alt=prefs.collision_visibility_alt)
    add_key_to_keymap('VIEW3D_PT_collision_visibility_panel', kmi, km, active=prefs.collision_visibility_active)
    kmi = km.keymap_items.new(idname='wm.call_panel', type=prefs.collision_material_type, value='PRESS',
                              ctrl=prefs.collision_material_ctrl, shift=prefs.collision_material_shift, alt=prefs.collision_material_alt)
    add_key_to_keymap('VIEW3D_PT_collision_material_panel', kmi, km, active=prefs.collision_material_active)


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
        if hasattr(kmi.properties, 'name') and kmi.properties.name in ['COLLISION_MT_pie_menu', 'VIEW3D_PT_collision_visibility_panel', 'VIEW3D_PT_collision_material_panel']:
            km.keymap_items.remove(kmi)


def remove_key(context, idname, properties_name):
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps["Window"]

    for kmi in km.keymap_items:
        if kmi.idname == idname and kmi.properties.name == properties_name:
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

        prefs = context.preferences.addons[__package__.split('.')[
            0]].preferences
        setattr(prefs,f'{self.property_prefix}_type',"NONE")
        setattr(prefs,f'{self.property_prefix}_ctrl',False)
        setattr(prefs,f'{self.property_prefix}_shift',False)
        setattr(prefs,f'{self.property_prefix}_alt',False)

        return {'FINISHED'}

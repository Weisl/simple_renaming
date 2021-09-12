import bpy

addon_keymaps = []


def remove_hotkey():
    ''' clears addon keymap hotkeys stored in addon_keymaps '''
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    km = kc.keymaps.new(name="3D View Generic", space_type='VIEW_3D', region_type='WINDOW')

    for km, kmi in addon_keymaps:
        if hasattr(kmi.properties, 'name'):
            if kmi.properties.name in ['VIEW3D_PT_tools_renaming_panel', 'VIEW3D_PT_tools_type_suffix']:
                km.keymap_items.remove(kmi)

    addon_keymaps.clear()


def add_hotkey():
    '''
    Adds default hotkey konfiguration
    '''
    prefs = bpy.context.preferences.addons[__package__].preferences

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    # if not kc:
    #     return

    km = kc.keymaps.new(name="3D View Generic", space_type='VIEW_3D', region_type='WINDOW')
    kmi = km.keymap_items.new(idname='wm.call_panel', type='F2', value='PRESS', ctrl=True)
    kmi.properties.name = 'VIEW3D_PT_tools_renaming_panel'
    kmi.active = True

    km = kc.keymaps.new(name="3D View Generic", space_type='VIEW_3D', region_type='WINDOW')
    kmi = km.keymap_items.new(idname='wm.call_panel', type='F2', value='PRESS', ctrl=True, shift=True)
    kmi.properties.name = 'VIEW3D_PT_tools_type_suffix'
    kmi.active = True

    addon_keymaps.append((km, kmi))


def get_hotkey_entry_item(km, kmi_name, kmi_value):
    '''
    returns hotkey of specific type, with specific properties.name (keymap is not a dict, so referencing by keys is not enough
    if there are multiple hotkeys!)
    '''
    for i, km_item in enumerate(km.keymap_items):
        if km.keymap_items.keys()[i] == kmi_name:
            if km.keymap_items[i].properties.name == kmi_value:
                return km_item
    return None


class RENAMING_OT_add_hotkey_renaming(bpy.types.Operator):
    ''' Add hotkey entry '''
    bl_idname = "renaming.add_hotkey"
    bl_label = "Addon Preferences Example"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        add_hotkey()
        self.report({'INFO'}, "Hotkey added in User Preferences -> Input -> Screen -> Screen (Global)")
        return {'FINISHED'}


classes = (
    RENAMING_OT_add_hotkey_renaming,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

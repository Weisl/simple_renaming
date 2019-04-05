import bpy
import rna_keymap_ui

addon_keymaps = []

# addon Preferences
class VIEW3D_OT_renaming_preferences(bpy.types.AddonPreferences):
    """Contains the blender addon preferences"""
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__  ### __package__ works on multifile and __name__ not

    renaming_category: bpy.props.StringProperty(
        name="Category",
        description="Defines in which category of the tools panel the simple renaimg panel is listed",
        default='Misc',
        # update = update_panel_position,
    )

    renamingPanel_showPopup: bpy.props.BoolProperty(
       name="Show Popup",
       description="Enable or Disable Popup",
       default=True,
    )

    def draw(self, context):
        layout = self.layout
        wm = bpy.context.window_manager

        row = layout.row()
        row.prop(self,"renaming_category", expand = True)
        row = layout.row()
        row.prop(self,"renamingPanel_showPopup")

        ####### custom keymap preferences ###########
        box = layout.box()
        split = box.split()
        col = split.column()
        col.label(text = 'Setup Hotkeys')
        col.separator()

        kc = wm.keyconfigs.user
        km = kc.keymaps['Renaming Panel']
        kmi = get_hotkey_entry_item(km, 'wm.call_panel', 'VIEW3D_PT_tools_renaming_panel')
        if kmi:
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label("No hotkey entry found")
            col.operator(TEMPLATE_OT_add_hotkey.bl_idname, text = "Add hotkey entry", icon = 'ZOOMIN')

def get_addon_preferences():
    ''' quick wrapper for referencing addon preferences '''
    addon_preferences = bpy.context.preferences.addons[__package__].preferences
    return addon_preferences

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


def add_hotkey():
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    wm = bpy.context.window_manager

    #active_keyconfig = wm.keyconfigs.active
    addon_keyconfig = wm.keyconfigs.user

    kc = addon_keyconfig
    if not kc:
        return

    km = kc.keymaps.new(name="Renaming Panel", space_type='EMPTY', region_type='WINDOW')
    kmi = km.keymap_items.new(idname='wm.call_panel', type='F2', value='PRESS', ctrl = True)
    kmi.properties.name = 'VIEW3D_PT_tools_renaming_panel'
    # kmi = km.keymap_items.new(idname='wm.call_panel', type='F2', value='PRESS', ctrl = True)
    # kmi.properties.name = 'VIEW3D_PT_tools_type_suffix'
    kmi.active = True

    addon_keymaps.append((km, kmi))

class TEMPLATE_OT_add_hotkey(bpy.types.Operator):
    ''' Add hotkey entry '''
    bl_idname = "template.add_hotkey"
    bl_label = "Addon Preferences Example"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        add_hotkey()
        self.report({'INFO'}, "Hotkey added in User Preferences -> Input -> Screen -> Screen (Global)")
        return {'FINISHED'}

def remove_hotkey():
    ''' clears all addon level keymap hotkeys stored in addon_keymaps '''
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user
    km = kc.keymaps['Renaming Panel']

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        wm.keyconfigs.user.keymaps.remove(km)
    addon_keymaps.clear()




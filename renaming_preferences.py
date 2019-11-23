import bpy
import rna_keymap_ui

from bpy.props import (
    BoolProperty,
    IntProperty,
    EnumProperty,
    StringProperty,
    FloatVectorProperty,
    PointerProperty,
    CollectionProperty,
)

addon_keymaps = []

class RENAMING_OT_add_hotkey_renaming(bpy.types.Operator):
    ''' Add hotkey entry '''
    bl_idname = "renaming.add_hotkey"
    bl_label = "Addon Preferences Example"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        add_hotkey()
        self.report({'INFO'}, "Hotkey added in User Preferences -> Input -> Screen -> Screen (Global)")
        return {'FINISHED'}


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
    kmi = km.keymap_items.new(idname='wm.call_panel', type='F2', value='PRESS', ctrl = True)
    kmi.properties.name = 'VIEW3D_PT_tools_renaming_panel'
    kmi.active = True

    km = kc.keymaps.new(name="3D View Generic", space_type='VIEW_3D', region_type='WINDOW')
    kmi = km.keymap_items.new(idname='wm.call_panel', type='F2', value='PRESS', ctrl = True, shift = True)
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

# addon Preferences
class VIEW3D_OT_renaming_preferences(bpy.types.AddonPreferences):
    """Contains the blender addon preferences"""
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__  ### __package__ works on multifile and __name__ not

    prefs_tabs : EnumProperty               (items=(('ui', "UI", "UI"),('keymaps', "Keymaps", "Keymaps")),default='ui')
    renaming_category: StringProperty       (name="Category",description="Defines in which category of the tools panel the simple renaimg panel is listed",default='Misc') # update = update_panel_position,
    renaming_separator: StringProperty      (
        name="Separator",
        description="Defines the separator between different operations",
        default='_',
    )

    renamingPanel_advancedMode : bpy.props.BoolProperty(
       name="Advanced (Experimental)",
       description="Enable or Disable Advanced Mode",
       default=True,
    )

    renamingPanel_showPopup: bpy.props.BoolProperty(
       name="Show Popup",
       description="Enable or Disable Popup",
       default=True,
    )

    renaming_stringHigh: StringProperty(
        name="High",
        description="Defines in which category of the tools panel the simple renaimg panel is listed",
        default="high",
        # update = update_panel_position,
    )
    renaming_stringLow: StringProperty(
        name="Low",
        description="Defines in which category of the tools panel the simple renaimg panel is listed",
        default='low',
        # update = update_panel_position,
    )
    renaming_stringCage: StringProperty(
        name="Cage",
        description="Defines in which category of the tools panel the simple renaimg panel is listed",
        default='cage',
        # update = update_panel_position,
    )
    renaming_user1: StringProperty(
        name="User 1",
        description="Defines in which category of the tools panel the simple renaimg panel is listed",
        default='',
        # update = update_panel_position,
    )
    renaming_user2: StringProperty(
        name="User 2",
        description="Defines in which category of the tools panel the simple renaimg panel is listed",
        default='',
        # update = update_panel_position,
    )
    renaming_user3: StringProperty(
        name="User 3",
        description="Defines in which category of the tools panel the simple renaimg panel is listed",
        default='',
        # update = update_panel_position,
    )


    def draw(self, context):
        '''
        simple preference UI to define custom inputs and user preferences
        '''
        layout = self.layout
        wm = bpy.context.window_manager

        row= layout.row(align=True)
        row.prop(self, "prefs_tabs", expand=True)

        if self.prefs_tabs == 'ui':

            row = layout.row()
            row.prop(self,"renaming_category", expand = True)
            row = layout.row()
            row.prop(self,"renamingPanel_showPopup")
            row = layout.row()
            row.prop(self,"renamingPanel_advancedMode")
            row = layout.row()
            row.prop(self, "renaming_separator")
            row = layout.row()
            row.prop(self,"renaming_stringLow")
            row = layout.row()
            row.prop(self,"renaming_stringHigh")
            row = layout.row()
            row.prop(self,"renaming_stringCage")
            row = layout.row()
            row.prop(self,"renaming_user1")
            row = layout.row()
            row.prop(self,"renaming_user2")
            row = layout.row()
            row.prop(self,"renaming_user3")


        if self.prefs_tabs == 'keymaps':
            box = layout.box()
            split = box.split()
            col = split.column()

            wm = bpy.context.window_manager
            kc = wm.keyconfigs.addon
            km = kc.keymaps['3D View Generic']

            kmis = []
            kmis.append(get_hotkey_entry_item(km, 'wm.call_panel', 'VIEW3D_PT_tools_renaming_panel'))
            kmis.append(get_hotkey_entry_item(km, 'wm.call_panel', 'VIEW3D_PT_tools_type_suffix'))
            for kmi in kmis:
                if kmi:
                    col.context_pointer_set("keymap", km)
                    rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
                else:
                    col.label(text="No hotkey entry found")
                    col.operator(RENAMING_OT_add_hotkey_renaming.bl_idname, text = "Add hotkey entry", icon = 'ADD')


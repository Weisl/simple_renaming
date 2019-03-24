import bpy

from bpy.props import (
    BoolProperty,
    StringProperty,
)

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



    renaming_stringHigh: bpy.props.StringProperty(
        name="High-Poly",
        description="String used for high poly meshes",
        default='high',
        # update = update_panel_position,
    )
    renaming_stringLow: bpy.props.StringProperty(
        name="Low-Poly",
        description="String used for high poly meshes",
        default='low',
        # update = update_panel_position,
    )
    renaming_stringCage: bpy.props.StringProperty(
        name="Cage",
        description="String used for high poly meshes",
        default='cage',
        # update = update_panel_position,
    )
    renaming_user1: bpy.props.StringProperty(
        name="User1",
        description="Custom String",
        default='',
        # update = update_panel_position,
    )
    renaming_user2: bpy.props.StringProperty(
        name="User2",
        description="Custom String",
        default='',
        # update = update_panel_position,
    )
    renaming_user3: bpy.props.StringProperty(
        name="User3",
        description="Custom String",
        default='',
        # update = update_panel_position,
    )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self,"renaming_category", expand = True)
        row = layout.row()
        row.prop(self,"renamingPanel_showPopup")
        row = layout.row()

        row.prop(self,"renaming_stringHigh")
        row = layout.row()
        row.prop(self,"renaming_stringLow")
        row = layout.row()
        row.prop(self,"renaming_stringCage")
        row = layout.row()
        row.prop(self,"renaming_user1")
        row = layout.row()
        row.prop(self,"renaming_user2")
        row = layout.row()
        row.prop(self,"renaming_user3")




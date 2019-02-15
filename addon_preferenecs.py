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

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self,"renaming_category", expand = True)
        row = layout.row()
        row.prop(self,"renamingPanel_showPopup")



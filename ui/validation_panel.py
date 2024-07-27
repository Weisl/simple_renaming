import bpy
from .. import __package__ as base_package
from .renaming_panels import get_addon_name

# addon Panel
class VIEW3D_PT_validation(bpy.types.Panel):
    """Creates a renaming Panel"""
    bl_label = "Name Validation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Validation"

    def draw_header(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP').url = "https://weisl.github.io/renaming/"
        addon_name = get_addon_name()

        op = row.operator("preferences.rename_addon_search", text="", icon='PREFERENCES')
        op.addon_name = addon_name
        op.prefs_tabs = 'VALIDATE'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        prefs = context.preferences.addons[base_package].preferences
        regex = prefs.regex_Mesh

        row = layout.row()
        row.label(text=prefs.regex_Mesh)
        row = layout.row()
        row.operator("renaming.validate")
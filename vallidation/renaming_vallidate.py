import re

import bpy

from .. import __package__ as base_package
from ..operators.renaming_utilities import getRenamingList, callInfoPopup
from ..ui.renaming_panels import get_addon_name


class VIEW3D_OT_Validate(bpy.types.Operator):
    bl_idname = "renaming.validate"
    bl_label = "Validate Names"
    bl_description = "replaces parts in the object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene
        prefs = context.preferences.addons[f'{base_package}'].preferences
        regex = prefs.regex_Mesh

        renaming_list, switch_edit_mode, err_msg = getRenamingList(context)

        if len(renaming_list) > 0:
            for entity in renaming_list:
                if entity != None:
                    if regex != '':
                        match = bool(re.compile(regex).match(entity.name))

                        if match:
                            wm.renaming_info_messages.addMessage("Valid", entity.name)
                        else:
                            wm.renaming_info_messages.addMessage("Not", entity.name)

        callInfoPopup(context)
        return {'FINISHED'}


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
        row.operator("renaming.vallidate")

import re

import bpy

from ..operators.renaming_utilities import getRenamingList, callInfoPopup
from ..ui.renaming_panels import get_addon_name

class VIEW3D_OT_Validate(bpy.types.Operator):
    bl_idname = "renaming.vallidate"
    bl_label = "Vallidate Names"
    bl_description = "replaces parts in the object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene
        package = __package__.split('.')[0]
        prefs = context.preferences.addons[f'{package}'].preferences
        regex = prefs.regex_Mesh

        renamingList = []
        renamingList, switchEditMode, errMsg = getRenamingList(context)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity != None:
                    if regex != '':
                        match = bool(re.compile(regex).match(entity.name))

                        if match:
                            wm.renaming_info_messages.addMessage("Vallid", entity.name)
                        else:
                            wm.renaming_info_messages.addMessage("Not", entity.name)

        callInfoPopup(context)
        return {'FINISHED'}


# addon Panel
class VIEW3D_PT_vallidation(bpy.types.Panel):
    """Creates a renaming Panel"""
    bl_label = "Name Vallidation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Vallidation"

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

        prefs = context.preferences.addons[__package__.split('.')[0]].preferences
        regex = prefs.regex_Mesh

        row = layout.row()
        row.label(text=prefs.regex_Mesh)
        row = layout.row()
        row.operator("renaming.vallidate")



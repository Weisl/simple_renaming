import re

import bpy

from .renaming_utilities import getRenamingList, callInfoPopup


class VIEW3D_OT_Validate(bpy.types.Operator):
    bl_idname = "renaming.vallidate"
    bl_label = "Vallidate Names"
    bl_description = "replaces parts in the object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene

        prefs = context.preferences.addons[__package__].preferences
        regex = prefs.regex_Mesh

        renamingList = []
        renamingList, switchEditMode, errMsg = getRenamingList(self, context)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    if regex is not '':
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
    bl_label = "Rename"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Vallidation"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        prefs = context.preferences.addons[__package__].preferences
        regex = prefs.regex_Mesh

        row = layout.row()
        row.label(text=prefs.regex_Mesh)
        row = layout.row()
        row.operator("renaming.vallidate")

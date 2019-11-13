import bpy, re
from .renaming_utilities import getRenamingList,callPopup

class VIEW3D_OT_Vallidate(bpy.types.Operator):
    bl_idname = "renaming.vallidate"
    bl_label = "Vallidate Names"
    bl_description = "replaces parts in the object names"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        wm = context.scene

        prefs = bpy.context.preferences.addons[__package__].preferences
        regex = prefs.meshRegex
        compiledRegex = re.compile(regex)

        renamingList = []
        renamingList = getRenamingList(self, context)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    if regex is not '':
                        match = bool(compiledRegex.match(entity.name))
                        if match:
                            wm.renaming_messages.addMessage("Vallid", entity.name)
                        else:
                            wm.renaming_messages.addMessage("Not", entity.name)

        callPopup(context)
        return {'FINISHED'}


# addon Panel
class VIEW3D_PT_vallidation(bpy.types.Panel):
    """Creates a renaming Panel"""
    bl_label = "Vallidation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Simple Renaming Panel"

    def draw(self, context):

        layout = self.layout
        scene = context.scene

        prefs = bpy.context.preferences.addons[__package__].preferences
        regex = prefs.meshRegex

        row = layout.row()
        row.label(text = prefs.meshRegex)
        row = layout.row()
        row.operator("renaming.vallidate")

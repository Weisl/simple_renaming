import bpy, re
from .renaming_utilities import getRenamingList, callInfoPopup

class VIEW3D_OT_Vallidate(bpy.types.Operator):
    bl_idname = "renaming.vallidate"
    bl_label = "Vallidate Names"
    bl_description = "replaces parts in the object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene

        prefs = bpy.context.preferences.addons[__package__].preferences
        regex = prefs.regex_Mesh
        compiledRegex = re.compile(regex)

        renamingList = []
        renamingList = getRenamingList(self, context)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    if regex is not '':
                        match = bool(compiledRegex.match(entity.name))

                    # if wm.naming_vallidate is not '':
                    #     pattern = re.compile(re.escape(wm.naming_vallidate))
                    #     match = re.match(pattern, entity.name)

                        if match:
                            wm.renaming_messages.addMessage("Vallid", entity.name)
                        else:
                            wm.renaming_messages.addMessage("Not", entity.name)

        callInfoPopup(context)
        return {'FINISHED'}


# addon Panel
class VIEW3D_PT_vallidation(bpy.types.Panel):
    """Creates a renaming Panel"""
    bl_label = "Vallidation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Vallidation"

    def draw(self, context):

        layout = self.layout
        scene = context.scene

        prefs = bpy.context.preferences.addons[__package__].preferences
        regex = prefs.regex_Mesh

        row = layout.row()
        row.label(text = prefs.regex_Mesh)
        row = layout.row()
        row.operator("renaming.vallidate")

import bpy
from ..operators.renaming_utilities import getRenamingList, callRenamingPopup, callErrorPopup
from .renaming_operators import switchToEditMode


class VIEW3D_OT_use_objectname_for_data(bpy.types.Operator):
    bl_idname = "renaming.dataname_from_obj"
    bl_label = "Data Name from Object"
    bl_description = "Renames the object data according to the object name and adds the in the data textfield specified suffix."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene
        suffix_data = wm.renaming_sufpre_data_02

        msg = wm.renaming_messages  # variable to save messages
        errMsg = wm.renaming_error_messages

        renamingList, switchEditMode, errMsg = getRenamingList(context)

        if errMsg != None:
            errorMsg = wm.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        # TODO: Clean up. Should use getRenamingList instead of iterating through all objects by itself.

        if wm.renaming_only_selection == True:
            for obj in context.selected_objects:

                objName = obj.name + suffix_data
                # if suffix_data != '':
                if hasattr(obj, 'data') and obj.data != None:
                    oldName = obj.data.name
                    newName = objName
                    obj.data.name = newName
                    msg.addMessage(oldName, obj.data.name)
        else:
            for obj in bpy.data.objects:
                objName = obj.name + suffix_data
                # if suffix_data != '':
                # if (obj.type == 'CURVE' or obj.type == 'LATTICE' or obj.type == 'MESH' or obj.type == 'META' or obj.type == 'SURFACE'):
                if hasattr(obj, 'data') and obj.data != None:
                    oldName = obj.data.name
                    newName = objName
                    obj.data.name = newName
                    msg.addMessage(oldName, obj.data.name)

        callRenamingPopup(context)
        if switchEditMode:
            switchToEditMode(context)

        return {'FINISHED'}


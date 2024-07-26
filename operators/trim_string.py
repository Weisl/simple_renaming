import bpy

from .renaming_operators import switchToEditMode
from ..operators.renaming_utilities import getRenamingList, trimString, callRenamingPopup, callErrorPopup


class VIEW3D_OT_trim_string(bpy.types.Operator):
    bl_idname = "renaming.cut_string"
    bl_label = "Trim End of String"
    bl_description = "Deletes the in the trim size specified amount of characters at the end of object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene
        renamingList, switchEditMode, errMsg = getRenamingList(context)

        if errMsg is not None:
            errorMsg = wm.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        msg = wm.renaming_messages

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    oldName = entity.name
                    newName = trimString(entity.name, wm.renaming_cut_size)
                    entity.name = newName
                    msg.addMessage(oldName, entity.name)

        callRenamingPopup(context)

        if switchEditMode:
            switchToEditMode(context)

        return {'FINISHED'}

import bpy
from ..operators.renaming_utilities import getRenamingList, callRenamingPopup, callErrorPopup
from ..variable_replacer.variable_replacer import VariableReplacer
from .renaming_operators import switchToEditMode
class VIEW3D_OT_add_suffix(bpy.types.Operator):
    bl_idname = "renaming.add_suffix"
    bl_label = "Add suffix"
    bl_description = "Adds a suffix to object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        wm = context.scene

        renamingList = []
        renamingList, switchEditMode, errMsg = getRenamingList(context)

        if errMsg != None:
            errorMsg = wm.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        msg = wm.renaming_messages

        VariableReplacer.reset()
        if len(renamingList) > 0:
            for entity in renamingList:
                if entity != None:
                    suffix = VariableReplacer.replaceInputString(context, wm.renaming_suffix, entity)
                    if entity.name.endswith(suffix) != True:
                        oldName = entity.name
                        newName = entity.name + suffix
                        entity.name = newName
                        msg.addMessage(oldName, entity.name)
        else:
            msg.addMessage(None, None, "Insert Valide String")
        if switchEditMode:
            switchToEditMode(context)
        callRenamingPopup(context)
        return {'FINISHED'}

class VIEW3D_OT_add_prefix(bpy.types.Operator):
    bl_idname = "renaming.add_prefix"
    bl_label = "Add Prefix"
    bl_description = "Adds a prefix to object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene

        msg = wm.renaming_messages
        errMsg = wm.renaming_error_messages

        renamingList = []
        renamingList, switchEditMode, errMsg = getRenamingList(context)

        if errMsg != None:
            errorMsg = wm.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        VariableReplacer.reset()

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity != None:
                    pre = VariableReplacer.replaceInputString(context, wm.renaming_prefix, entity)
                    if entity.name.startswith(pre) != True:
                        oldName = entity.name
                        newName = pre + entity.name
                        entity.name = newName
                        msg.addMessage(oldName, entity.name)

        callRenamingPopup(context)
        if switchEditMode:
            switchToEditMode(context)

        return {'FINISHED'}
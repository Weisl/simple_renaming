import bpy

from .renaming_operators import switchToEditMode
from ..operators.renaming_utilities import getRenamingList, callRenamingPopup, callErrorPopup
from ..variable_replacer.variable_replacer import VariableReplacer


class VIEW3D_OT_add_suffix(bpy.types.Operator):
    bl_idname = "renaming.add_suffix"
    bl_label = "Add suffix"
    bl_description = "Adds a suffix to object names"
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

        VariableReplacer.reset()
        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    suffix = VariableReplacer.replaceInputString(context, wm.renaming_suffix, entity)
                    if not entity.name.endswith(suffix):
                        oldName = entity.name
                        newName = entity.name + suffix
                        entity.name = newName
                        msg.addMessage(oldName, entity.name)
        else:
            msg.addMessage(None, None, "Insert Valid String")
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

        renamingList, switchEditMode, errMsg = getRenamingList(context)

        if errMsg is not None:
            errorMsg = wm.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        VariableReplacer.reset()

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    pre = VariableReplacer.replaceInputString(context, wm.renaming_prefix, entity)
                    if not entity.name.startswith(pre):
                        oldName = entity.name
                        newName = pre + entity.name
                        entity.name = newName
                        msg.addMessage(oldName, entity.name)

        callRenamingPopup(context)
        if switchEditMode:
            switchToEditMode(context)

        return {'FINISHED'}

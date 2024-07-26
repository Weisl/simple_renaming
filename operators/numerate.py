import bpy

from .renaming_operators import switchToEditMode
from .. import __package__ as base_package
from ..operators.renaming_utilities import getRenamingList, callRenamingPopup, callErrorPopup


class VIEW3D_OT_renaming_numerate(bpy.types.Operator):
    bl_idname = "renaming.numerate"
    bl_label = "Numerate"
    bl_description = "adds a growing number to the object names with the amount of digits specified in Number Length"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = context.preferences.addons[base_package].preferences
        separator = prefs.renaming_separator

        wm = context.scene

        startNum = prefs.numerate_start_number

        step = prefs.numerate_step
        digits = prefs.numerate_digits

        msg = wm.renaming_messages

        renamingList = []
        renamingList, switchEditMode, errMsg = getRenamingList(context)

        if errMsg is not None:
            errorMsg = wm.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        if len(renamingList) > 0:
            i = 0
            for entity in renamingList:
                if entity is not None:
                    oldName = entity.name
                    newName = entity.name + separator + (
                        '{num:{fill}{width}}'.format(num=(i * step) + startNum, fill='0', width=digits))
                    entity.name = newName
                    msg.addMessage(oldName, entity.name)
                    i = i + 1

        callRenamingPopup(context)
        if switchEditMode:
            switchToEditMode(context)
        return {'FINISHED'}

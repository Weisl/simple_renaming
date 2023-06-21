import re
import bpy

from ..operators.renaming_utilities import getRenamingList, callRenamingPopup, callErrorPopup
from ..variable_replacer.variable_replacer import VariableReplacer

from .renaming_operators import switchToEditMode

class VIEW3D_OT_search_and_replace(bpy.types.Operator):
    bl_idname = "renaming.search_replace"
    bl_label = "Search and Replace"
    bl_description = "replaces parts in the object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene

        # get list of objects to be renamed
        renamingList, switchEditMode, errMsg = getRenamingList(context)

        if errMsg != None:
            errorMsg = wm.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        searchName = wm.renaming_search
        replaceName = wm.renaming_replace

        msg = wm.renaming_messages  # variable to save messages
        errMsg = wm.renaming_error_messages

        VariableReplacer.reset()

        if len(renamingList) > 0:
            for entity in renamingList:  # iterate over all objects that are to be renamed
                if entity != None:
                    if searchName != '':
                        oldName = entity.name
                        searchReplaced = VariableReplacer.replaceInputString(context, wm.renaming_search, entity)
                        replaceReplaced = VariableReplacer.replaceInputString(context, wm.renaming_replace, entity)
                        if wm.renaming_useRegex == False:
                            if wm.renaming_matchcase:
                                newName = str(entity.name).replace(searchReplaced, replaceReplaced)
                                entity.name = newName
                                msg.addMessage(oldName, entity.name)
                            else:
                                replaceSearch = re.compile(re.escape(searchReplaced), re.IGNORECASE)
                                newName = replaceSearch.sub(replaceReplaced, entity.name)
                                entity.name = newName
                                msg.addMessage(oldName, entity.name)
                        else:  # Use regex
                            # pattern = re.compile(re.escape(searchName))
                            newName = re.sub(searchReplaced, replaceReplaced, str(entity.name))
                            entity.name = newName
                            msg.addMessage(oldName, entity.name)

        callRenamingPopup(context)
        if switchEditMode:
            switchToEditMode(context)
        return {'FINISHED'}


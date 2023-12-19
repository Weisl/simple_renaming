import re
import bpy

from .renaming_operators import switchToEditMode

from ..operators.renaming_utilities import getRenamingList, callErrorPopup
from ..variable_replacer.variable_replacer import VariableReplacer

class VIEW3D_OT_naming(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        VariableReplacer.reset()
        return


class VIEW3D_OT_search_and_select(VIEW3D_OT_naming):
    bl_idname = "renaming.search_select"
    bl_label = "Search and Select"
    bl_description = "Select Object By Name"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return super().invoke(context, event)

    def execute(self, context):
        super().execute(context)
        wm = context.scene

        # get list of objects to be selected
        selectionList = []

        renamingList, switchEditMode, errMsg = getRenamingList(context)

        if errMsg != None:
            errorMsg = wm.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        searchName = wm.renaming_search
        msg = wm.renaming_messages  # variable to save messages

        if len(renamingList) > 0:
            for entity in renamingList:  # iterate over all objects that are to be renamed
                if entity != None and searchName != '':
                    entityName = entity.name
                    searchReplaced = VariableReplacer.replaceInputString(context, searchName, entity)

                    if wm.renaming_matchcase == True:
                        if entityName.find(searchReplaced) >= 0:
                            selectionList.append(entity)
                            msg.addMessage("selected", entityName)
                    else:
                        if re.search(searchReplaced, entityName, re.IGNORECASE):
                            selectionList.append(entity)

        if str(wm.renaming_object_types) == 'OBJECT':
            # set to object mode
            if bpy.context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

            bpy.ops.object.select_all(action='DESELECT')

            for obj in selectionList:
                obj.select_set(True)

        elif str(wm.renaming_object_types) == 'BONE':
            # print("SELECTION LIST: " + str(selectionList))
            if bpy.context.mode == 'POSE':
                bpy.ops.pose.select_all(action='DESELECT')
                for bone in selectionList:
                    bone.select = True

            elif bpy.context.mode == 'EDIT_ARMATURE':
                bpy.ops.armature.select_all(action='DESELECT')
                for bone in selectionList:
                    # print("EDIT Bone: " + str(bone))
                    bone.select = True
                    bone.select_head = True
                    bone.select_tail = True

        # callRenamingPopup(context)
        if switchEditMode:
            switchToEditMode(context)
        return {'FINISHED'}
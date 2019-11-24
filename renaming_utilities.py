import bpy
from abc import ABCMeta, abstractmethod
from bpy.types import PoseBone

def trimString(string, size):
    list1 = string
    list2 = list1[:-size]
    return ''.join(list2)

def getRenamingList(self, context, overrideSelection = False):
    wm = context.scene
    renamingList = []
    switchEditMode = False

    onlySelection = wm.renaming_only_selection
    if overrideSelection == True:
        onlySelection = False

    if wm.renaming_object_types == 'OBJECT':
        if onlySelection == True:
            for obj in bpy.context.selected_objects:
                if obj.type in wm.renaming_object_types_specified:
                    renamingList.append(obj)
        else:
            for obj in bpy.data.objects:
                if obj.type in wm.renaming_object_types_specified:
                    renamingList.append(obj)

    elif wm.renaming_object_types == 'DATA':
        if onlySelection == True:
            for obj in bpy.context.selected_objects:
                if obj.data not in renamingList:
                    renamingList.append(obj.data)
        else:
            for obj in bpy.data.objects:
                if obj.data not in renamingList:
                    renamingList.append(obj.data)

    elif wm.renaming_object_types == 'MATERIAL':
        if onlySelection == True:
            for obj in bpy.context.selected_objects:
                for mat in obj.material_slots:
                    if mat is not None and mat.name != '':
                        renamingList.append(bpy.data.materials[mat.name])
        else:
            renamingList = list(bpy.data.materials)

    elif wm.renaming_object_types == 'IMAGE':
        renamingList = list(bpy.data.images)

    elif wm.renaming_object_types == 'BONE':
        if onlySelection == True:
            modeOld = bpy.context.mode
            selectedBones = []
            if modeOld == 'POSE':
                selectedBones = bpy.context.selected_pose_bones.copy()
            else:
                selectedBones = bpy.context.selected_bones.copy()
                switchEditMode = True

            bpy.ops.object.mode_set(mode='POSE')
            for selected_bone in selectedBones:
                name = selected_bone.name
                for arm in bpy.data.armatures:

                    for bone in arm.bones:
                        if name == bone.name:
                            newBone = PoseBone(arm.bones[name])
                            renamingList.append(newBone)

        else:
            for arm in bpy.data.armatures:
                for bone in arm.bones:
                    # print(bone)
                    renamingList.append(bone)

    elif wm.renaming_object_types == 'COLLECTION':
        renamingList = list(bpy.data.collections)

    elif wm.renaming_object_types == 'SHAPEKEYS':
        for key_grp in bpy.data.shape_keys:
            for key in key_grp.key_blocks:
                renamingList.append(key)

    # elif wm.renaming_object_types == 'VERTEXGROUP':
    #     if onlySelection == True:
    #         for obj in bpy.context.selected_objects:
    #             for vtx in obj.vertex_groups:
    #                 if vtx is not None and vtx.name != '':
    #                     renamingList.append(obj.vertex_groups[vtx.name])
    #     else:
    #         for obj in bpy.data.objects:
    #             for vtx in obj.vertex_groups:
    #                 if vtx is not None and vtx.name != '':
    #                     renamingList.append(obj.vertex_groups[vtx.name])

    elif wm.renaming_object_types == 'ACTIONS':
        renamingList = list(bpy.data.actions)

    #renamingList.sort(key=lambda x: x.name, reverse=False)
    return renamingList, switchEditMode

def callRenamingPopup(context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    if addon_prefs.renamingPanel_showPopup == True:
        bpy.ops.wm.call_panel(name="renaming.popup")
    return

def callInfoPopup(context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    bpy.ops.wm.call_panel(name="renamingValidation.popup")
    return


windowVariables = []


class MESSAGE():
    message = []

    @classmethod
    def addMessage(cls):
        return

    @classmethod
    def getMessages(cls):
        return cls.message

    @classmethod
    def printAll(cls):
        print("Print All " + str(list(cls.message)))
        return

    @classmethod
    def clear(cls):
        cls.message = []

    @classmethod
    def draw(cls, context):
        return

class INFO_MESSAGES(MESSAGE):

    @classmethod
    def addMessage(cls, assetName, message='', obType=False, obIcon=False):
        dict = {'assetName': assetName, 'message': message, 'obType': obType, 'obIcon': obIcon}
        cls.message.append(dict)
        return

    def draw(cls,context, layout):
        box = layout.box()
        wm = context.scene
        print("Draw")
        if len(cls.message) <= 0:
            box.label(text="No Objects Validated", icon="INFO")
        else:
            i = 0
            for msg in cls.message:
                if msg is not None:
                    if (msg['message'] is not None):

                            row = box.row(align=True)
                            row.alignment = 'EXPAND'

                            if msg['obType'] is not False and msg['obIcon'] is not False:
                                row.label(text=str(msg['obType']), icon=msg['obIcon'])
                                # row.label(text = str(msg['obType']), icon = 'INFO')
                            else:
                                row.label(text=str(wm.renaming_object_types))

                            row.label(text=str(msg['assetName']), icon='FILE_TICK')
                            row.label(text=str(msg['oldName']))

                            i += 1


class RENAMING_MESSAGES(MESSAGE):
    message = []

    @classmethod
    def addMessage(cls, oldName, newName = None, obType=False, obIcon=False, warning=False):
        dict = {'oldName': oldName, 'newName': newName, 'obType': obType, 'obIcon': obIcon, 'warning': warning}
        cls.message.append(dict)
        return

    def draw(cls, context, layout):
        box = layout.box()
        wm = context.scene

        if len(wm.renaming_messages.message) <= 0:
            box.label(text="No Objects Renamed", icon="INFO")
        else:
            i = 0
            for msg in wm.renaming_messages.message:
                if msg is not None:
                    if msg['warning'] == False:
                        if (msg['newName'] is not None and msg['oldName'] is not None) and msg['oldName'] != msg[
                            'newName']:

                            if i == 0:
                                row = box.row(align=True)
                                row.alignment = 'EXPAND'
                                row.label(text="OBJECT TYPE")
                                row.label(text="NEW NAME")
                                row.label(text="OLD NAME")
                                row.separator()

                            row = box.row(align=True)
                            row.alignment = 'EXPAND'

                            if msg['obType'] is not False and msg['obIcon'] is not False:
                                row.label(text=str(msg['obType']), icon=msg['obIcon'])
                                # row.label(text = str(msg['obType']), icon = 'INFO')
                            else:
                                row.label(text=str(wm.renaming_object_types))

                            row.label(text=str(msg['newName']), icon='FILE_TICK')
                            row.label(text=str(msg['oldName']))

                            i += 1

                    else: #if msg['warning'] == True
                        if msg['newName'] is not None and msg['oldName'] is not None:
                            box.label(text="Warning", icon="ERROR")
                            box.label(text="       " + "Name: " + str(msg['oldName']))
                            box.label(text="       " + msg['warning'])
                        else:
                            box.label(text="Warning", icon="ERROR")
                            box.label(text="       " + msg['warning'])
            if i == 0:
                box.label(text="No Objects Renamed", icon="INFO")
            return



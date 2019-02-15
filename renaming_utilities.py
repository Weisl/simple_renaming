import bpy
def trimString(string, size):
    list1 = string
    list2 = list1[:-size]
    return ''.join(list2)

def getRenamingList(self, context):
    wm = context.scene
    renamingList = []

    if wm.renaming_object_types == 'OBJECT':
        if wm.renaming_only_selection == True:
            for obj in bpy.context.selected_objects:
                if obj.type in wm.renaming_object_types_specified:
                    renamingList.append(obj)
        else:
            for obj in bpy.data.objects:
                if obj.type in wm.renaming_object_types_specified:
                    renamingList.append(obj)

    elif wm.renaming_object_types == 'DATA':
        if wm.renaming_only_selection == True:
            for obj in bpy.context.selected_objects:
                if obj.data not in renamingList:
                    renamingList.append(obj.data)
        else:
            for obj in bpy.data.objects:
                if obj.data not in renamingList:
                    renamingList.append(obj.data)

    elif wm.renaming_object_types == 'MATERIAL':
        if wm.renaming_only_selection == True:
            for obj in bpy.context.selected_objects:
                for mat in obj.material_slots:
                    if mat is not None and mat.name != '':
                        renamingList.append(bpy.data.materials[mat.name])
        else:
            renamingList = list(bpy.data.materials)

    elif wm.renaming_object_types == 'IMAGE':
        renamingList = list(bpy.data.images)

    elif wm.renaming_object_types == 'BONE':
        if wm.renaming_only_selection == True:
            mode = bpy.context.mode
            bpy.ops.object.mode_set(mode='POSE')
            for pose_bone in bpy.context.selected_pose_bones:
                print(pose_bone)
                renamingList.append(pose_bone)
            bpy.ops.object.mode_set(mode='OBJECT')
        else:
            for arm in bpy.data.armatures:
                for bone in arm.bones:
                    print(bone)
                    renamingList.append(bone)

    elif wm.renaming_object_types == 'COLLECTION':
        renamingList = list(bpy.data.collections)

    elif wm.renaming_object_types == 'SHAPEKEYS':
        for key_grp in bpy.data.shape_keys:
            for key in key_grp.key_blocks:
                renamingList.append(key)

    elif wm.renaming_object_types == 'VERTEXGROUP':
        if wm.renaming_only_selection == True:
            for obj in bpy.context.selected_objects:
                for vtx in obj.vertex_groups:
                    if vtx is not None and vtx.name != '':
                        renamingList.append(obj.vertex_groups[vtx.name])
        else:
            for obj in bpy.data.objects:
                for vtx in obj.vertex_groups:
                    if vtx is not None and vtx.name != '':
                        renamingList.append(obj.vertex_groups[vtx.name])

    #renamingList.sort(key=lambda x: x.name, reverse=False)
    return renamingList

def callPopup(context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    if addon_prefs.renamingPanel_showPopup == True:
        bpy.ops.renaming.popup('INVOKE_DEFAULT')

    return

windowVariables = []

class RENAMING_MESSAGES():
    message = []

    @classmethod
    def addMessage(cls, oldName, newName, obType=False, obIcon=False, warning=False):
        dict = {'oldName': oldName, 'newName': newName, 'obType': obType, 'obIcon': obIcon, 'warning': warning}
        cls.message.append(dict)
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



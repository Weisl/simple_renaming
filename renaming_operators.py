import bpy, re
from .renaming_utilities import getRenamingList,trimString,callPopup
import time
#############################################
############ OPERATORS ########################
#############################################

def getfileName(context):
    scn = context.scene

    if bpy.data.is_saved:
        filename = bpy.path.display_name(bpy.context.blend_data.filepath)
    else:
        filename = "UNSAVED"
        #scn.renaming_messages.addMessage(oldName, entity.name)
        #TODO: Error message! is unsaved
    return filename

def getDateName(context):
    #Todo: Specify Date Layout in preferences
    #TODO: Fix Timezone
    t = time.localtime()
    t = time.mktime(t)
    return time.strftime("%d%b%Y", time.gmtime(t))

def getTimeName(context):
    #TODO: Specify Time Layout in preferences
    t = time.localtime()
    t = time.mktime(t)
    return time.strftime("%H:%M", time.gmtime(t))

def getActive(context):
    #TODO: Error Case
    return context.object.name

def getType(context):
    #TODO: Error Case
    #TODO: Per Object
    return str(context.object.type)

def getParent(context):
    #TODO: Error Case
    return context.object.parent.name


class VariableReplacer():
    addon_prefs = None

    @classmethod
    def replaceInputString(cls, context,inputTest):
        cls.addon_prefs = bpy.context.preferences.addons[__package__].preferences

        inputTest = re.sub(r'@f', getfileName(context), inputTest)
        inputTest = re.sub(r'@o', 'OBJECT', inputTest)
        inputTest = re.sub(r'@h', cls.getPrefString('high'), inputTest)
        inputTest = re.sub(r'@l', cls.getPrefString('low'), inputTest)
        inputTest = re.sub(r'@c', cls.getPrefString('cage'), inputTest)
        inputTest = re.sub(r'@u1', cls.getPrefString('user1'), inputTest)
        inputTest = re.sub(r'@u2', cls.getPrefString('user2'), inputTest)
        inputTest = re.sub(r'@u3', cls.getPrefString('user3'), inputTest)
        inputTest = re.sub(r'@d', getDateName(context), inputTest)
        inputTest = re.sub(r'@a', getActive(context), inputTest)
        inputTest = re.sub(r'@t', getTimeName(context), inputTest)
        inputTest = re.sub(r'@y', getType(context), inputTest)
        #inputTest = re.sub(r'@p', getParent(context), inputTest)
        inputTest = re.sub(r'@r', 'RESOLUTION', inputTest)
        inputTest = re.sub(r'@i', 'FILETYPE', inputTest)
        return inputTest

    @classmethod
    def high(cls):
        return cls.addon_prefs.renaming_stringHigh

    @classmethod
    def low(cls):
        return cls.addon_prefs.renaming_stringLow

    @classmethod
    def cage(cls):
        return cls.addon_prefs.renaming_stringCage

    @classmethod
    def user1(cls):
        return cls.addon_prefs.renaming_user1

    @classmethod
    def user2(cls):
        return cls.addon_prefs.renaming_user2

    @classmethod
    def user3(cls):
        return cls.addon_prefs.renaming_user3

    @classmethod
    def getPrefString(cls, suffixString):
        method = getattr(cls, suffixString, lambda: "Undefined variable")
        return method()



class VIEW3D_OT_search_and_replace(bpy.types.Operator):
    bl_idname = "renaming.search_replace"
    bl_label = "Search and Replace"
    bl_description = "replaces parts in the object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene

        renamingList = []
        renamingList = getRenamingList(self, context)

        searchName = VariableReplacer.replaceInputString(context, wm.renaming_search)
        replaceName = VariableReplacer.replaceInputString(context, wm.renaming_replace)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    if searchName is not '':
                        oldName = entity.name
                        if wm.renaming_useRegex == False:
                            if wm.renaming_matchcase:
                                newName = str(entity.name).replace(searchName, replaceName)
                                entity.name = newName
                                wm.renaming_messages.addMessage(oldName, entity.name)
                            else:
                                replaceSearch = re.compile(re.escape(searchName), re.IGNORECASE)
                                newName = replaceSearch.sub(replaceName, entity.name)
                                entity.name = newName
                                wm.renaming_messages.addMessage(oldName, entity.name)
                        else: # Use regex
                            #pattern = re.compile(re.escape(searchName))
                            newName = re.sub(searchName, replaceName, str(entity.name))
                            entity.name = newName
                            wm.renaming_messages.addMessage(oldName, entity.name)

        callPopup(context)
        return {'FINISHED'}

class VIEW3D_OT_replace_name(bpy.types.Operator):
    bl_idname = "renaming.name_replace"
    bl_label = "Replace Names"
    bl_description = "replaces the names of the objects"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        wm = context.scene
        addon_prefs = bpy.context.preferences.addons[__package__].preferences
        seperator = addon_prefs.renamingPanel_defaultseperator

        replaceName = VariableReplacer.replaceInputString(context,wm.renaming_newName)

        renamingList = getRenamingList(self, context)

        shapeKeyNamesList = []
        if wm.renaming_object_types == 'SHAPEKEYS':
            for key_grp in bpy.data.shape_keys:
                for key in key_grp.key_blocks:
                    shapeKeyNamesList.append(key.name)
            # for key in bpy.data.shape_keys[0].key_blocks:
            #     shapeKeyNamesList.append(key.name)

        print ("shape key list " + str(shapeKeyNamesList))

        if len(str(replaceName)) > 0:
            digits = 3
            if len(renamingList) > 0:


                for entity in renamingList:


                    if entity is not None:
                        i = 1
                        if wm.renaming_object_types == 'COLLECTION' or wm.renaming_object_types == 'IMAGE':
                            i = 0

                        oldName = entity.name
                        newName = ""

                        dataList = []
                        boneList = []

                        if wm.renaming_object_types == 'BONE':
                            for arm in bpy.data.armatures:
                                for bone in arm.bones:
                                    boneList.append(bone.name)

                        if wm.renaming_object_types == 'DATA':
                            for obj in bpy.data.objects:
                                if obj.data is not None:
                                    dataList.append(obj.data.name)

                        while True:
                            newName = replaceName + seperator + ('{num:{fill}{width}}'.format(num=i, fill='0', width=digits))

                            if wm.renaming_object_types == 'OBJECT':
                                if newName in bpy.data.objects and newName != entity.name:
                                    i = i + 1
                                else:
                                    break
                            elif wm.renaming_object_types == 'MATERIAL':
                                if newName in bpy.data.materials and newName != entity.name:
                                    i = i + 1
                                else:
                                    break

                            elif wm.renaming_object_types == 'IMAGE':
                                if newName in bpy.data.images and newName != entity.name:
                                    i = i + 1
                                else:
                                    break
                            elif wm.renaming_object_types == 'DATA':
                                if newName in dataList and newName != entity.name:
                                    i = i + 1
                                else:
                                    break
                            elif wm.renaming_object_types == 'BONE':
                                if newName in boneList and newName != entity.name:
                                    i = i + 1
                                else:
                                    break
                            elif wm.renaming_object_types == 'COLLECTION':
                                if newName in bpy.data.collections and newName != entity.name:
                                    i = i + 1
                                else:
                                    break

                            elif wm.renaming_object_types == 'ACTIONS':
                                if newName in bpy.data.actions and newName != entity.name:
                                    i = i + 1
                                else:
                                    break

                            elif wm.renaming_object_types == 'SHAPEKEYS':
                                print (str(i) + "  " + str(shapeKeyNamesList))
                                if newName in shapeKeyNamesList:
                                    print('1')
                                    shapeKeyNamesList.append(newName)
                                    i = i + 1
                                else:
                                    shapeKeyNamesList.append(newName)
                                    break
                            else:
                                break

                        newName = replaceName + seperator + ('{num:{fill}{width}}'.format(num=i, fill='0', width=digits))
                        entity.name = newName
                        wm.renaming_messages.addMessage(oldName, entity.name)
                        i = i + 1

        else:  # len(str(replaceName)) <= 0
            wm.renaming_messages.addMessage(None, None, "Insert a valid string to replace names")

        i = 0
        callPopup(context)
        return {'FINISHED'}



class VIEW3D_OT_trim_string(bpy.types.Operator):
    bl_idname = "renaming.cut_string"
    bl_label = "Trim End of String"
    bl_description = "Deletes the in the trim size specified amount of characters at the end of object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene
        renamingList = []
        renamingList = getRenamingList(self, context)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    oldName = entity.name
                    newName = trimString(entity.name, wm.renaming_cut_size)
                    entity.name = newName
                    wm.renaming_messages.addMessage(oldName, entity.name)

        callPopup(context)
        return {'FINISHED'}

class VIEW3D_OT_add_suffix(bpy.types.Operator):
    bl_idname = "renaming.add_suffix"
    bl_label = "Add suffix"
    bl_description = "Adds a suffix to object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        wm = context.scene

        suffix = VariableReplacer.replaceInputString(context, wm.renaming_suffix)

        renamingList = []
        renamingList = getRenamingList(self, context)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    if entity.name.endswith(suffix) is not True:
                        oldName = entity.name
                        newName = entity.name + suffix
                        entity.name = newName
                        wm.renaming_messages.addMessage(oldName, entity.name)
        else:
            wm.renaming_messages.addMessage(None, None, "Insert Valide String")

        callPopup(context)
        return {'FINISHED'}

class VIEW3D_OT_add_prefix(bpy.types.Operator):
    bl_idname = "renaming.add_prefix"
    bl_label = "Add Prefix"
    bl_description = "Adds a prefix to object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene
        pre = VariableReplacer.replaceInputString(context, wm.renaming_prefix)

        renamingList = []
        renamingList = getRenamingList(self, context)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    if entity.name.startswith(pre) is not True:
                        oldName = entity.name
                        newName = pre + entity.name
                        entity.name = newName
                        wm.renaming_messages.addMessage(oldName, entity.name)

        callPopup(context)
        return {'FINISHED'}

class VIEW3D_OT_renaming_numerate(bpy.types.Operator):
    bl_idname = "renaming.numerate"
    bl_label = "Numerate"
    bl_description = "adds a growing number to the object names with the amount of digits specified in Number Lenght"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene
        i = 1

        step = wm.renaming_base_numerate
        digits = wm.renaming_digits_numerate

        renamingList = []
        renamingList = getRenamingList(self, context)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    oldName = entity.name
                    newName = entity.name + '_' + ('{num:{fill}{width}}'.format(num=i * step, fill='0', width=digits))
                    entity.name = newName
                    wm.renaming_messages.addMessage(oldName, entity.name)
                    i = i + 1

        callPopup(context)
        return {'FINISHED'}

class VIEW3D_OT_use_objectname_for_data(bpy.types.Operator):
    bl_idname = "renaming.dataname_from_obj"
    bl_label = "Data Name from Object"
    bl_description = "Renames the object data according to the object name and adds the in the data textfield specified suffix."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene
        suffix_data = wm.renaming_sufpre_data_02

        if wm.renaming_only_selection == True:
            for obj in bpy.context.selected_objects:

                objName = obj.name + suffix_data
                #if suffix_data is not '':
                if  hasattr(obj, 'data') and obj.data is not None:
                    oldName = obj.data.name
                    newName = objName
                    obj.data.name = newName
                    wm.renaming_messages.addMessage(oldName, obj.data.name)
        else:
            for obj in bpy.data.objects:
                objName = obj.name + suffix_data
                #if suffix_data is not '':
                #if (obj.type == 'CURVE' or obj.type == 'LATTICE' or obj.type == 'MESH' or obj.type == 'META' or obj.type == 'SURFACE'):
                if hasattr(obj, 'data') and obj.data is not None:
                    oldName = obj.data.name
                    newName = objName
                    obj.data.name = newName
                    wm.renaming_messages.addMessage(oldName, obj.data.name)

        callPopup(context)
        return {'FINISHED'}








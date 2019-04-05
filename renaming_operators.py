import bpy, re
from .renaming_utilities import getRenamingList,trimString,callPopup
import time
#############################################
############ OPERATORS ########################
#############################################

class VariableReplacer():
    addon_prefs = None
    entity = None

    @classmethod
    def replaceInputString(cls,context,inputText,entity):
        print ("Replacer inputText: " + inputText)
        print ("Replacer Entity1: " + entity.name)
        cls.addon_prefs = bpy.context.preferences.addons[__package__].preferences
        inputText = re.sub(r'@f', cls.getfileName(context), inputText)      # file name
        ##### System ################
        inputText = re.sub(r'@d', cls.getDateName(context), inputText)      # date
        inputText = re.sub(r'@t', cls.getTimeName(context), inputText)      # time
        ##### UserStrings ################
        inputText = re.sub(r'@h', cls.gethigh(), inputText)     # high
        inputText = re.sub(r'@l', cls.getlow(), inputText)      # low
        inputText = re.sub(r'@c', cls.getcage(), inputText)     # cage
        inputText = re.sub(r'@u1', cls.getuser1(), inputText)
        inputText = re.sub(r'@u2', cls.getuser2(), inputText)
        inputText = re.sub(r'@u3', cls.getuser3(), inputText)
        ##### GetScene ################
        inputText = re.sub(r'@a', cls.getActive(context), inputText)        # active object
        ##### Objects #################
        print ("Replacer Entity2: " + cls.getObject(context, entity))
        print ("Replacer Entity3: " + inputText)
        inputText = re.sub(r'@o', cls.getObject(context, entity), inputText) # object
        print ("Replacer Entity4: " + inputText)
        inputText = re.sub(r'@y', cls.getType(context, entity), inputText)   # type
        inputText = re.sub(r'@p', cls.getParent(context, entity), inputText) # parent
        ###### IMAGES ###########
        inputText = re.sub(r'@r', 'RESOLUTION', inputText)
        inputText = re.sub(r'@i', 'FILETYPE', inputText)
        print ("Replacer Entity5: " + inputText)
        return inputText

    @classmethod
    def gethigh(cls):
        return cls.addon_prefs.renaming_stringHigh

    @classmethod
    def getlow(cls):
        return cls.addon_prefs.renaming_stringLow

    @classmethod
    def getcage(cls):
        return cls.addon_prefs.renaming_stringCage

    @classmethod
    def getuser1(cls):
        return cls.addon_prefs.renaming_user1

    @classmethod
    def getuser2(cls):
        return cls.addon_prefs.renaming_user2

    @classmethod
    def getuser3(cls):
        return cls.addon_prefs.renaming_user3

    @classmethod
    def getPrefString(cls, suffixString):
        method = getattr(cls, suffixString, lambda: "Undefined variable")
        return method()

    @classmethod
    def getfileName(cls,context):
        scn = context.scene

        if bpy.data.is_saved:
            filename = bpy.path.display_name(bpy.context.blend_data.filepath)
        else:
            filename = "UNSAVED"
            #scn.renaming_messages.addMessage(oldName, entity.name)
            #TODO: Error message! is unsaved
        return filename

    @classmethod
    def getDateName(cls,context):
        #Todo: Specify Date Layout in preferences
        #TODO: Fix Timezone
        t = time.localtime()
        t = time.mktime(t)
        return time.strftime("%d%b%Y", time.gmtime(t))

    @classmethod
    def getTimeName(cls,context):
        #TODO: Specify Time Layout in preferences
        t = time.localtime()
        t = time.mktime(t)
        return time.strftime("%H:%M", time.gmtime(t))

    @classmethod
    def getActive(cls,context):
        return context.object.name

    ################## OBJECTS ####################################
    @classmethod
    def getObject(cls,context, entity):
        objName = entity.name
        print ("getObject Entity: " + objName)
        return objName


    @classmethod
    def getType(cls,context, entity):
        #TODO: Error Case
        #TODO: Per Object
        return str(entity.type)

    @classmethod
    def getParent(cls,context, entity):
        #TODO: Error Case
        if entity.parent is not None:
            return str(entity.parent.name)
        else:
            return ""
        #return "Parent"

class VIEW3D_OT_search_and_replace(bpy.types.Operator):
    bl_idname = "renaming.search_replace"
    bl_label = "Search and Replace"
    bl_description = "replaces parts in the object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene

        renamingList = []
        renamingList = getRenamingList(self, context)

        searchName = wm.renaming_search
        replaceName = wm.renaming_replace

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    if searchName is not '':
                        oldName = entity.name
                        if wm.renaming_useRegex == False:

                            searchReplaced = VariableReplacer.replaceInputString(context, wm.renaming_search, entity)
                            replaceReplaced = VariableReplacer.replaceInputString(context, wm.renaming_replace, entity)


                            if wm.renaming_matchcase:
                                newName = str(entity.name).replace(searchReplaced, replaceReplaced)
                                entity.name = newName
                                wm.renaming_messages.addMessage(oldName, entity.name)
                            else:
                                replaceSearch = re.compile(re.escape(searchReplaced), re.IGNORECASE)
                                newName = replaceSearch.sub(replaceReplaced, entity.name)
                                entity.name = newName
                                wm.renaming_messages.addMessage(oldName, entity.name)
                        else: # Use regex
                            #pattern = re.compile(re.escape(searchName))
                            newName = re.sub(searchReplaced, replaceReplaced, str(entity.name))
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

        replaceName = wm.renaming_newName

        renamingList = getRenamingList(self, context)

        digits = len(wm.renaming_numerate)
        shapeKeyNamesList = []
        if wm.renaming_object_types == 'SHAPEKEYS':
            for key_grp in bpy.data.shape_keys:
                for key in key_grp.key_blocks:
                    shapeKeyNamesList.append(key.name)
            # for key in bpy.data.shape_keys[0].key_blocks:
            #     shapeKeyNamesList.append(key.name)

        if len(str(replaceName)) > 0:
            if len(renamingList) > 0:
                for entity in renamingList:
                    if entity is not None:
                        replaceName = VariableReplacer.replaceInputString(context, wm.renaming_newName, entity)
                        print ("Entity: " + entity.name + "         " + "replaced: " + replaceName)

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



        renamingList = []
        renamingList = getRenamingList(self, context)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    suffix = VariableReplacer.replaceInputString(context, wm.renaming_suffix, entity)
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

        renamingList = []
        renamingList = getRenamingList(self, context)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    pre = VariableReplacer.replaceInputString(context, wm.renaming_prefix, entity)
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








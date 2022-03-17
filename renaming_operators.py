import random
import re
import string
import time

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    IntProperty,
)

from .renaming_utilities import getRenamingList, trimString, callRenamingPopup, callErrorPopup


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def switchToEditMode(context):
    bpy.ops.object.mode_set(mode='EDIT')


def numerate_object_name(context, name, typelist, active_entity_name, return_type_list = False):

    wm = context.scene
    digits = len(wm.renaming_numerate)

    prefs = context.preferences.addons[__package__].preferences
    separator = prefs.renaming_separator
    startNum = prefs.numerate_start_number
    step = prefs.numerate_step

    i = startNum

    newName = name + separator + (
        '{num:{fill}{width}}'.format(num=(i * step), fill='0', width=digits))

    while newName in typelist and newName != active_entity_name:
        newName = name + separator + (
            '{num:{fill}{width}}'.format(num=(i * step) + startNum, fill='0', width=digits))
        i += 1

    if return_type_list: # Manually add new name to custom generated list like all bones and all shape keys
        typelist.append(newName)
        return newName, typelist

    return newName

def getAllBones(mode):
    '''Get list of all bones depending of Edit or Pose Mode'''

    boneList = []

    for arm in bpy.data.armatures:
        if mode == 'POSE':
            for bone in arm.bones:
                boneList.append(bone.name)
        else:  # mode == 'EDIT':
            for bone in arm.edit_bones:
                boneList.append(bone.name)

    return boneList

def getAllShapeKeys():
    '''get list of all shape keys'''
    shapeKeyNamesList = []

    for key_grp in bpy.data.shape_keys:
        for key in key_grp.key_blocks:
            shapeKeyNamesList.append(key.name)

    return shapeKeyNamesList

def getAllDataNames():
    dataList = []

    for obj in bpy.data.objects:
        if obj.data is not None:
            dataList.append(obj.data.name)

    return dataList

class VariableReplacer():
    addon_prefs = None
    entity = None
    number = 1
    digits = 3
    step = 1
    startnumber = 0

    @classmethod
    def reset(cls):
        prefs = bpy.context.preferences.addons[__package__].preferences
        startNum = prefs.numerate_start_number
        numerate_step = prefs.numerate_step
        numerate_digits = prefs.numerate_digits

        # print("reset = " + str(startNum))
        cls.step = numerate_step
        cls.digits = numerate_digits
        cls.startNum = startNum
        cls.number = 0

    @classmethod
    def replaceInputString(cls, context, inputText, entity):
        wm = context.scene
        cls.addon_prefs = context.preferences.addons[__package__].preferences

        ##### System and Global Values ################
        inputText = re.sub(r'@f', cls.getfileName(context), inputText)  # file name
        inputText = re.sub(r'@d', cls.getDateName(context), inputText)  # date
        inputText = re.sub(r'@i', cls.getTimeName(context), inputText)  # time
        inputText = re.sub(r'@r', cls.getRandomString(context), inputText)

        ##### UserStrings ################
        inputText = re.sub(r'@h', cls.gethigh(), inputText)  # high
        inputText = re.sub(r'@l', cls.getlow(), inputText)  # low
        inputText = re.sub(r'@b', cls.getcage(), inputText)  # cage
        inputText = re.sub(r'@u1', cls.getuser1(), inputText)
        inputText = re.sub(r'@u2', cls.getuser2(), inputText)
        inputText = re.sub(r'@u3', cls.getuser3(), inputText)

        ##### GetScene ################
        inputText = re.sub(r'@a', cls.getActive(context), inputText)  # active object
        inputText = re.sub(r'@n', cls.getNumber(context), inputText)

        if wm.renaming_object_types == 'OBJECT':
            ##### Objects #################
            inputText = re.sub(r'@o', cls.getObject(context, entity), inputText)  # object
            inputText = re.sub(r'@t', cls.getType(context, entity), inputText)  # type
            inputText = re.sub(r'@p', cls.getParent(context, entity), inputText)  # parent
            inputText = re.sub(r'@c', cls.getCollection(context, entity), inputText)  # collection

        ###### IMAGES ###########
        if wm.renaming_object_types == 'IMAGE':
            inputText = re.sub(r'@r', 'RESOLUTION', inputText)
            inputText = re.sub(r'@i', 'FILETYPE', inputText)

        return inputText

    @classmethod
    def gethigh(cls):
        return cls.addon_prefs.renaming_stringHigh

    # @classmethod
    def getRandomString(cls):
        return randomString(6)

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
    def getNumber(cls, context):
        wm = context.scene
        # digits = len(wm.renaming_numerate)
        newNr = cls.number
        step = cls.step
        startNum = cls.startNum
        nr = str('{num:{fill}{width}}'.format(num=(newNr * step) + startNum, fill='0', width=cls.digits))
        cls.number = newNr + 1
        return nr

    @classmethod
    def getfileName(cls, context):
        scn = context.scene

        if bpy.data.is_saved:
            filename = bpy.path.display_name(context.blend_data.filepath)
        else:
            filename = "UNSAVED"
            # scn.renaming_messages.addMessage(oldName, entity.name)
            # TODO: Error message! is unsaved
        return filename

    @classmethod
    def getDateName(cls, context):
        # Todo: Specify Date Layout in preferences
        # TODO: Fix Timezone
        t = time.localtime()
        t = time.mktime(t)
        return time.strftime("%d%b%Y", time.gmtime(t))

    @classmethod
    def getTimeName(cls, context):
        # TODO: Specify Time Layout in preferences
        t = time.localtime()
        t = time.mktime(t)
        return time.strftime("%H:%M", time.gmtime(t))

    @classmethod
    def getActive(cls, context):
        if context.object is None:
            return ""
        else:
            return context.object.name

    ################## OBJECTS ####################################
    @classmethod
    def getObject(cls, context, entity):
        objName = entity.name
        return objName

    @classmethod
    def getType(cls, context, entity):
        # TODO: Error Case
        # TODO: Per Object
        return str(entity.type)

    @classmethod
    def getParent(cls, context, entity):
        # TODO: Error Case
        if entity.parent is not None:
            return str(entity.parent.name)
        else:
            return entity.name
        # return "Parent"

    @classmethod
    def getCollection(cls, context, entity):
        # prefs = context.preferences.addons[__package__].preferences
        # separator = prefs.renaming_separator

        collectionNames = ""
        for collection in bpy.data.collections:
            collection_objects = collection.objects
            if entity.name in collection.objects and entity in collection_objects[:]:
                collectionNames += collection.name

        return collectionNames

# TODO Parent class that contains common functionality like setting up variables, getRenamingList and Error Handling

class VIEW3D_OT_search_and_select(bpy.types.Operator):
    bl_idname = "renaming.search_select"
    bl_label = "Search and Select"
    bl_description = "Select Object By Name"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene

        # get list of objects to be selected
        selectionList = []

        # renamingList, switchEditMode = getRenamingList(self, context, overrideSelection = True)
        renamingList, switchEditMode, errMsg = getRenamingList(self, context)

        if errMsg is not None:
            errorMsg = wm.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        searchName = wm.renaming_search
        msg = wm.renaming_messages  # variable to save messages

        VariableReplacer.reset()

        if len(renamingList) > 0:
            for entity in renamingList:  # iterate over all objects that are to be renamed
                if entity is not None and searchName is not '':
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


class VIEW3D_OT_search_and_replace(bpy.types.Operator):
    bl_idname = "renaming.search_replace"
    bl_label = "Search and Replace"
    bl_description = "replaces parts in the object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene

        # get list of objects to be renamed
        renamingList = []
        renamingList, switchEditMode, errMsg = getRenamingList(self, context)

        if errMsg is not None:
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
                if entity is not None:
                    if searchName is not '':
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


class VIEW3D_OT_replace_name(bpy.types.Operator):
    bl_idname = "renaming.name_replace"
    bl_label = "Replace Names"
    bl_description = "replaces the names of the objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        wm = context.scene

        replaceName = wm.renaming_newName
        renamingList, switchEditMode, errMsg = getRenamingList(self, context)

        if errMsg is not None:
            errorMsg = wm.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        modeOld = context.mode

        # settings for numerating the new name

        prefs = context.preferences.addons[__package__].preferences
        separator = prefs.renaming_separator
        startNum = prefs.numerate_start_number
        step = prefs.numerate_step

        msg = wm.renaming_messages

        # get list of all objects of certain type
        if wm.renaming_object_types == 'SHAPEKEYS':
            shapeKeyNamesList = getAllShapeKeys()

        if wm.renaming_object_types == 'BONE':
            boneList = getAllBones(modeOld)

        if wm.renaming_object_types == 'DATA':
            dataList = getAllDataNames()


        VariableReplacer.reset()

        if len(str(replaceName)) > 0: # New name is not empty
            if len(renamingList) > 0: # List of objects to rename is not empty
                for entity in renamingList:
                    if entity is not None:

                        replaceName = VariableReplacer.replaceInputString(context, wm.renaming_newName, entity)

                        i = 0

                        oldName = entity.name
                        newName = replaceName

                        dataList = []
                        
                        if wm.renaming_usenumerate == False:
                            entity.name = replaceName
                            msg.addMessage(oldName, entity.name)

                        else: # if wm.renaming_usenumerate == True

                            if wm.renaming_object_types == 'OBJECT':
                                new_name = numerate_object_name(context, replaceName, bpy.data.objects, entity.name)

                            elif wm.renaming_object_types == 'MATERIAL':
                                new_name = numerate_object_name(context, replaceName, bpy.data.materials, entity.name)

                            elif wm.renaming_object_types == 'IMAGE':
                                new_name = numerate_object_name(context, replaceName, bpy.data.images, entity.name)

                            elif wm.renaming_object_types == 'DATA':
                                new_name, dataList = numerate_object_name(context, replaceName, dataList, entity.name, return_type_list = True)

                            elif wm.renaming_object_types == 'BONE':
                                new_name, boneList = numerate_object_name(context, replaceName, boneList, entity.name, return_type_list = True)

                            elif wm.renaming_object_types == 'COLLECTION':
                                new_name = numerate_object_name(context, replaceName, bpy.data.collections, entity.name)

                            elif wm.renaming_object_types == 'ACTIONS':
                                new_name = numerate_object_name(context, replaceName, bpy.data.actions, entity.name)

                            elif wm.renaming_object_types == 'SHAPEKEYS':
                                new_name, shapeKeyNamesList = numerate_object_name(context, replaceName, shapeKeyNamesList, entity.name, return_type_list = True)

                            entity.name = new_name
                            msg.addMessage(oldName, entity.name)

        else:  # len(str(replaceName)) <= 0
            msg.addMessage(None, None, "Insert a valid string to replace names")



        callRenamingPopup(context)
        if switchEditMode:
            switchToEditMode(context)
        return {'FINISHED'}


class VIEW3D_OT_trim_string(bpy.types.Operator):
    bl_idname = "renaming.cut_string"
    bl_label = "Trim End of String"
    bl_description = "Deletes the in the trim size specified amount of characters at the end of object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene
        renamingList = []
        renamingList, switchEditMode, errMsg = getRenamingList(self, context)

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


class VIEW3D_OT_add_suffix(bpy.types.Operator):
    bl_idname = "renaming.add_suffix"
    bl_label = "Add suffix"
    bl_description = "Adds a suffix to object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        wm = context.scene

        renamingList = []
        renamingList, switchEditMode, errMsg = getRenamingList(self, context)

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
                    if entity.name.endswith(suffix) is not True:
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
        renamingList, switchEditMode, errMsg = getRenamingList(self, context)

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
                    if entity.name.startswith(pre) is not True:
                        oldName = entity.name
                        newName = pre + entity.name
                        entity.name = newName
                        msg.addMessage(oldName, entity.name)

        callRenamingPopup(context)
        if switchEditMode:
            switchToEditMode(context)

        return {'FINISHED'}


class VIEW3D_OT_renaming_numerate(bpy.types.Operator):
    bl_idname = "renaming.numerate"
    bl_label = "Numerate"
    bl_description = "adds a growing number to the object names with the amount of digits specified in Number Lenght"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        separator = prefs.renaming_separator

        wm = context.scene

        startNum = prefs.numerate_start_number

        step = prefs.numerate_step
        digits = prefs.numerate_digits

        msg = wm.renaming_messages
        errMsg = wm.renaming_error_messages

        renamingList = []
        renamingList, switchEditMode, errMsg = getRenamingList(self, context)

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


class VIEW3D_OT_use_objectname_for_data(bpy.types.Operator):
    bl_idname = "renaming.dataname_from_obj"
    bl_label = "Data Name from Object"
    bl_description = "Renames the object data according to the object name and adds the in the data textfield specified suffix."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene
        suffix_data = wm.renaming_sufpre_data_02

        msg = wm.renaming_messages  # variable to save messages
        errMsg = wm.renaming_error_messages

        renamingList, switchEditMode, errMsg = getRenamingList(self, context)

        if errMsg is not None:
            errorMsg = wm.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        # TODO: Clean up. Should use getRenamingList instead of iterating through all objects by itself.

        if wm.renaming_only_selection == True:
            for obj in context.selected_objects:

                objName = obj.name + suffix_data
                # if suffix_data is not '':
                if hasattr(obj, 'data') and obj.data is not None:
                    oldName = obj.data.name
                    newName = objName
                    obj.data.name = newName
                    msg.addMessage(oldName, obj.data.name)
        else:
            for obj in bpy.data.objects:
                objName = obj.name + suffix_data
                # if suffix_data is not '':
                # if (obj.type == 'CURVE' or obj.type == 'LATTICE' or obj.type == 'MESH' or obj.type == 'META' or obj.type == 'SURFACE'):
                if hasattr(obj, 'data') and obj.data is not None:
                    oldName = obj.data.name
                    newName = objName
                    obj.data.name = newName
                    msg.addMessage(oldName, obj.data.name)

        callRenamingPopup(context)
        if switchEditMode:
            switchToEditMode(context)

        return {'FINISHED'}


enumObjectTypes = [('EMPTY', "", "Rename empty objects", 'OUTLINER_OB_EMPTY', 1),
                   ('MESH', "", "Rename mesh objects", 'OUTLINER_OB_MESH', 2),
                   ('CAMERA', "", "Rename Camera objects", 'OUTLINER_OB_CAMERA', 4),
                   ('LIGHT', "", "Rename light objects", 'OUTLINER_OB_LIGHT', 8),
                   ('ARMATURE', "", "Rename armature objects", 'OUTLINER_OB_ARMATURE', 16),
                   ('LATTICE', "", "Rename lattice objects", 'OUTLINER_OB_LATTICE', 32),
                   ('CURVE', "", "Rename curve objects", 'OUTLINER_OB_CURVE', 64),
                   ('SURFACE', "", "Rename surface objects", 'OUTLINER_OB_SURFACE', 128),
                   ('FONT', "", "Rename font objects", 'OUTLINER_OB_FONT', 256),
                   ('GPENCIL', "", "Rename greace pencil objects", 'OUTLINER_OB_GREASEPENCIL', 512),
                   ('META', "", "Rename metaball objects", 'OUTLINER_OB_META', 1024),
                   ('SPEAKER', "", "Rename empty speakers", 'OUTLINER_OB_SPEAKER', 2048),
                   ('LIGHT_PROBE', "", "Rename mesh lightpropes", 'OUTLINER_OB_LIGHTPROBE', 4096),
                   ('VOLUME', "", "Rename mesh volumes", 'OUTLINER_OB_VOLUME', 8192)
                   ]

enumObjectTypesAdd = [('SPEAKER', "", "Rename empty speakers", 'OUTLINER_OB_SPEAKER', 1),
                      ('LIGHT_PROBE', "", "Rename mesh lightpropes", 'OUTLINER_OB_LIGHTPROBE', 2)]



prefixSuffixItems = [('PRE', "Prefix", "prefix"),
                     ('SUF', "Suffix", "suffix")
                     ]

renamingEntitiesItems = [('OBJECT', "Object", "Scene Objects"),
                         # ('ADDOBJECTS', "Objects (additional)","Scene Objects"),
                         ('MATERIAL', "Material", "Materials"),
                         ('IMAGE', "Image Textures", "Image Textures"),
                         ('DATA', "Data", "Object Data"),
                         ('BONE', "Bone", "Bones"),
                         ('COLLECTION', "Collection", "Rename collections"),
                         ('ACTIONS', "Actions", "Rename Actions"),
                         ('SHAPEKEYS', "Shape Keys", "Rename shape keys")
                         # ('VERTEXGROUPS',"Vertex Groups", "Rename vertex groups")
                         # ('UVMaps')
                         # ('FACEMAPS')
                         # ('PARTICLESYSTEM')
                         ]

classes = (
    VIEW3D_OT_search_and_select,
    VIEW3D_OT_search_and_replace,
    VIEW3D_OT_replace_name,
    VIEW3D_OT_trim_string,
    VIEW3D_OT_add_suffix,
    VIEW3D_OT_add_prefix,
    VIEW3D_OT_renaming_numerate,
    VIEW3D_OT_use_objectname_for_data,
)


def register():
    IDStore = bpy.types.Scene

    IDStore.renaming_sufpre_type = EnumProperty(
        name="Suffix or Prefix by Type",
        items=prefixSuffixItems,
        description="Add Prefix or Suffix to type",
        default='SUF'
    )

    IDStore.renaming_object_types = EnumProperty(
        name="Renaming Objects",
        items=renamingEntitiesItems,
        description="Which kind of object to rename",
    )

    IDStore.renaming_object_types_specified = EnumProperty(name="Object Types",
                                                           items=enumObjectTypes,
                                                           description="Which kind of object to rename",
                                                           options={'ENUM_FLAG'},
                                                           default={'CURVE', 'LATTICE', 'SURFACE','MESH',
                                                                    'ARMATURE', 'LIGHT', 'CAMERA', 'EMPTY', 'GPENCIL',
                                                                    'FONT', 'SPEAKER', 'LIGHT_PROBE', 'VOLUME'}
                                                           )

    IDStore.renaming_newName = StringProperty(name="New Name", default='')
    IDStore.renaming_search = StringProperty(name='Search', default='')
    IDStore.renaming_replace = StringProperty(name='Replace', default='')
    IDStore.renaming_suffix = StringProperty(name="Suffix", default='')
    IDStore.renaming_prefix = StringProperty(name="Prefix", default='')
    IDStore.renaming_numerate = StringProperty(name="Numerate", default='###')

    IDStore.renaming_only_selection = BoolProperty(name="Selected Objects", description="Rename Selected Objects",
                                                   default=True)
    IDStore.renamingPanel_advancedMode = BoolProperty(name="Advanced Renaming",
                                                      description="Enable additional feautres for renaming",
                                                      default=False)
    IDStore.renaming_matchcase = BoolProperty(name="Match Case", description="", default=True)
    IDStore.renaming_useRegex = BoolProperty(name="Use Regex", description="", default=False)
    IDStore.renaming_usenumerate = BoolProperty(name="Numerate",
                                                description="Enable and Disable the numeration of objects. This can be especially useful in combination with the custom numberation variable @n",
                                                default=True,
                                                )
    IDStore.renaming_base_numerate = IntProperty(name="Step Size", default=1)
    IDStore.renaming_start_number = IntProperty(name="Step Size", default=1)
    IDStore.renaming_digits_numerate = IntProperty(name="Number Length", default=3)
    IDStore.renaming_cut_size = IntProperty(name="Trim Size", default=3)

    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    IDStore = bpy.types.Scene
    del IDStore.renaming_search
    del IDStore.renaming_newName
    del IDStore.renaming_object_types
    del IDStore.renaming_sufpre_type
    del IDStore.renaming_replace
    del IDStore.renaming_suffix
    del IDStore.renaming_prefix
    del IDStore.renaming_only_selection
    del IDStore.renaming_base_numerate
    del IDStore.renaming_digits_numerate
    del IDStore.renaming_cut_size

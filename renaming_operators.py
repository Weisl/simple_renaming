import re

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    IntProperty,
)

from .renaming_utilities import getRenamingList, trimString, callRenamingPopup, callErrorPopup
from .variable_replacer import VariableReplacer


def switchToEditMode(context):
    '''Switch to Edit Mode'''
    bpy.ops.object.mode_set(mode='EDIT')


def numerate_entity_name(context, basename, typelist, active_entity_name, return_type_list=False):
    '''Numerate entities and make sure they have a unique number'''
    wm = context.scene
    digits = len(wm.renaming_numerate)

    # Preferences
    prefs = context.preferences.addons[__package__].preferences
    separator = prefs.renaming_separator
    startNum = prefs.numerate_start_number
    step = prefs.numerate_step

    i = startNum

    newName = basename + separator + (
        '{num:{fill}{width}}'.format(num=(i * step), fill='0', width=digits))

    while newName in typelist and newName != active_entity_name:
        newName = basename + separator + (
            '{num:{fill}{width}}'.format(num=(i * step) + startNum, fill='0', width=digits))
        i += 1

    if return_type_list:  # Manually add new name to custom generated list like all bones and all shape keys
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


def getAllVertexGroups():
    '''get list of all vertex groups'''
    vtrxGrpNamesList = []

    for obj in bpy.data.objects:
        for vrtGrp in obj.vertex_groups:
            vtrxGrpNamesList.append(vrtGrp.name)

    return vtrxGrpNamesList


def getAllParticleNames():
    '''get list of all particle systems'''
    particlesNamesList = []

    for obj in bpy.data.objects:
        for particle_system in obj.particle_systems:
            particlesNamesList.append(particle_system.name)
    return particlesNamesList


def getAllUvMaps():
    uvNamesList = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        for uv in obj.data.uv_layers:
            uvNamesList.append(uv)
    return uvNamesList


def getAllFacemaps():
    facemapNamesList = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        for face_map in obj.face_maps:
            facemapNamesList.append(face_map)
    return facemapNamesList


def getAllColorAttributes():
    colorAttributesList = []

    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        for color_attribute in obj.data.color_attributes:
            colorAttributesList.append(color_attribute)

    return colorAttributesList


def getAllAttributes():
    attributesList = []

    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        for color_attribute in obj.data.color_attributes:
            attributesList.append(color_attribute)

    return attributesList


def getAllDataNames():
    '''get list of all data'''
    dataList = []

    for obj in bpy.data.objects:
        if obj.data != None:
            dataList.append(obj.data.name)

    return dataList


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

        # renamingList, switchEditMode = getRenamingList(context, overrideSelection = True)
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


class VIEW3D_OT_replace_name(bpy.types.Operator):
    bl_idname = "renaming.name_replace"
    bl_label = "Replace Names"
    bl_description = "replaces the names of the objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene

        replaceName = scene.renaming_newName
        renamingList, switchEditMode, errMsg = getRenamingList(context)

        if errMsg != None:
            errorMsg = scene.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        modeOld = context.mode

        # settings for numerating the new name
        prefs = context.preferences.addons[__package__].preferences
        separator = prefs.renaming_separator
        startNum = prefs.numerate_start_number
        step = prefs.numerate_step

        msg = scene.renaming_messages

        if context.scene.renaming_object_types == 'VERTEXGROUPS':
            vertexGroupNameList = getAllVertexGroups()
        if scene.renaming_object_types == 'PARTICLES':
            particleList = getAllParticleNames()
        if context.scene.renaming_object_types == 'FACEMAPS':
            facemapsList = getAllFacemaps()
        if context.scene.renaming_object_types == 'UVMAPS':
            uvmapsList = getAllUvMaps()
        if context.scene.renaming_object_types == 'COLORATTRIBUTES':
            colorAttributeList = getAllColorAttributes()
        if context.scene.renaming_object_types == 'ATTRIBUTES':
            attributeList = getAllAttributes()
        if scene.renaming_object_types == 'SHAPEKEYS':
            shapeKeyNamesList = getAllShapeKeys()
        if scene.renaming_object_types == 'BONE':
            boneList = getAllBones(modeOld)
        if scene.renaming_object_types == 'DATA':
            dataList = getAllDataNames()

        VariableReplacer.reset()

        if len(str(replaceName)) > 0:  # New name != empty
            if len(renamingList) > 0:  # List of objects to rename != empty
                for entity in renamingList:
                    if entity != None:

                        replaceName = VariableReplacer.replaceInputString(context, scene.renaming_newName, entity)

                        i = 0

                        oldName = entity.name
                        newName = replaceName

                        dataList = []

                        if scene.renaming_usenumerate == False:
                            entity.name = replaceName
                            msg.addMessage(oldName, entity.name)

                        else:  # if scene.renaming_usenumerate == True

                            if scene.renaming_object_types == 'OBJECT':
                                new_name = numerate_entity_name(context, replaceName, bpy.data.objects, entity.name)

                            elif scene.renaming_object_types == 'MATERIAL':
                                new_name = numerate_entity_name(context, replaceName, bpy.data.materials, entity.name)

                            elif scene.renaming_object_types == 'IMAGE':
                                new_name = numerate_entity_name(context, replaceName, bpy.data.images, entity.name)

                            elif scene.renaming_object_types == 'DATA':
                                new_name, dataList = numerate_entity_name(context, replaceName, dataList, entity.name,
                                                                          return_type_list=True)

                            elif scene.renaming_object_types == 'BONE':
                                new_name, boneList = numerate_entity_name(context, replaceName, boneList, entity.name,
                                                                          return_type_list=True)

                            elif scene.renaming_object_types == 'COLLECTION':
                                new_name = numerate_entity_name(context, replaceName, bpy.data.collections, entity.name)

                            elif scene.renaming_object_types == 'ACTIONS':
                                new_name = numerate_entity_name(context, replaceName, bpy.data.actions, entity.name)

                            elif scene.renaming_object_types == 'SHAPEKEYS':
                                new_name, shapeKeyNamesList = numerate_entity_name(context, replaceName,
                                                                                   shapeKeyNamesList, entity.name,
                                                                                   return_type_list=True)
                            elif context.scene.renaming_object_types == 'VERTEXGROUPS':
                                new_name, vertexGroupNameList = numerate_entity_name(context, replaceName,
                                                                                     vertexGroupNameList, entity.name,
                                                                                     return_type_list=True)

                            elif context.scene.renaming_object_types == 'PARTICLES':
                                new_name, particleList = numerate_entity_name(context, replaceName,
                                                                                     particleList, entity.name,
                                                                                     return_type_list=True)

                            elif context.scene.renaming_object_types == 'FACEMAPS':
                                new_name, facemapsList = numerate_entity_name(context, replaceName,
                                                                              facemapsList, entity.name,
                                                                              return_type_list=True)

                            elif context.scene.renaming_object_types == 'UVMAPS':
                                new_name, uvmapsList = numerate_entity_name(context, replaceName,
                                                                            uvmapsList, entity.name,
                                                                            return_type_list=True)

                            elif context.scene.renaming_object_types == 'ATTRIBUTES':
                                new_name, attributeList = numerate_entity_name(context, replaceName,
                                                                               attributeList, entity.name,
                                                                               return_type_list=True)
                            elif context.scene.renaming_object_types == 'COLORATTRIBUTES':
                                new_name, colorAttributeList = numerate_entity_name(context, replaceName,
                                                                                    colorAttributeList, entity.name,
                                                                                    return_type_list=True)
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
        renamingList, switchEditMode, errMsg = getRenamingList(context)

        if errMsg != None:
            errorMsg = wm.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        msg = wm.renaming_messages

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity != None:
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
        renamingList, switchEditMode, errMsg = getRenamingList(context)

        if errMsg != None:
            errorMsg = wm.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        if len(renamingList) > 0:
            i = 0
            for entity in renamingList:
                if entity != None:
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

        renamingList, switchEditMode, errMsg = getRenamingList(context)

        if errMsg != None:
            errorMsg = wm.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        # TODO: Clean up. Should use getRenamingList instead of iterating through all objects by itself.

        if wm.renaming_only_selection == True:
            for obj in context.selected_objects:

                objName = obj.name + suffix_data
                # if suffix_data != '':
                if hasattr(obj, 'data') and obj.data != None:
                    oldName = obj.data.name
                    newName = objName
                    obj.data.name = newName
                    msg.addMessage(oldName, obj.data.name)
        else:
            for obj in bpy.data.objects:
                objName = obj.name + suffix_data
                # if suffix_data != '':
                # if (obj.type == 'CURVE' or obj.type == 'LATTICE' or obj.type == 'MESH' or obj.type == 'META' or obj.type == 'SURFACE'):
                if hasattr(obj, 'data') and obj.data != None:
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
                         ('DATA', "Data", "Object Data"),
                         ('MATERIAL', "Material", "Materials"),
                         ('BONE', "Bone", "Bones"),
                         ('IMAGE', "Image Textures", "Image Textures"),
                         ('COLLECTION', "Collection", "Rename collections"),
                         ('ACTIONS', "Actions", "Rename Actions"),
                         ('SHAPEKEYS', "Shape Keys", "Rename shape keys"),
                         ('VERTEXGROUPS', "Vertex Groups", "Rename vertex groups"),
                         ('PARTICLES', "Particles", "Rename particle systems"),
                         ('UVMAPS', "UV Maps", "Rename vertex groups"),
                         ('FACEMAPS', "Facemaps", "Rename vertex groups"),
                         ('COLORATTRIBUTES', "Color Attributes", "Rename color attributes"),
                         ('ATTRIBUTES', "Attributes", "Rename attributes"),
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

    IDStore.renaming_sufpre_type = EnumProperty(name="Suffix or Prefix by Type",
                                                items=prefixSuffixItems,
                                                description="Add Prefix or Suffix to type",
                                                default='SUF'
                                                )

    IDStore.renaming_object_types = EnumProperty(name="Renaming Objects",
                                                 items=renamingEntitiesItems,
                                                 description="Which kind of object to rename",
                                                 )

    IDStore.renaming_object_types_specified = EnumProperty(name="Object Types",
                                                           items=enumObjectTypes,
                                                           description="Which kind of object to rename",
                                                           options={'ENUM_FLAG'},
                                                           default={'CURVE', 'LATTICE', 'SURFACE', 'MESH',
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

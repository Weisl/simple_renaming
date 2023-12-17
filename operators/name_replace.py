import bpy
from ..operators.renaming_utilities import getRenamingList, callRenamingPopup, callErrorPopup
from ..variable_replacer.variable_replacer import VariableReplacer

from .renaming_operators import switchToEditMode, numerate_entity_name
from .renaming_operators import getAllVertexGroups, getAllAttributes, getAllBones, getAllModifiers, getAllUvMaps, getAllColorAttributes, getAllParticleNames, getAllParticleSettingsNames, getAllDataNames, getAllShapeKeys
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
        prefs = context.preferences.addons[__package__.split('.')[0]].preferences
        separator = prefs.renaming_separator
        startNum = prefs.numerate_start_number
        step = prefs.numerate_step

        msg = scene.renaming_messages

        if context.scene.renaming_object_types == 'VERTEXGROUPS':
            vertexGroupNameList = getAllVertexGroups()
        if scene.renaming_object_types == 'PARTICLESYSTEM':
            particleList = getAllParticleNames()
        if scene.renaming_object_types == 'PARTICLESETTINGS':
            particleSettingsList = getAllParticleSettingsNames()
        if context.scene.renaming_object_types == 'UVMAPS':
            uvmapsList = getAllUvMaps()
        if context.scene.renaming_object_types == 'COLORATTRIBUTES':
            colorAttributeList = getAllColorAttributes()
        if context.scene.renaming_object_types == 'ATTRIBUTES':
            attributeList = getAllAttributes()
        if scene.renaming_object_types == 'SHAPEKEYS':
            shapeKeyNamesList = getAllShapeKeys()
        if scene.renaming_object_types == 'MODIFIERS':
            modifierNamesList = getAllModifiers()

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
                            elif scene.renaming_object_types == 'MODIFIERS':
                                new_name, modifierNamesList = numerate_entity_name(context, replaceName,
                                                                                   modifierNamesList, entity.name,
                                                                                   return_type_list=True)
                            elif context.scene.renaming_object_types == 'VERTEXGROUPS':
                                new_name, vertexGroupNameList = numerate_entity_name(context, replaceName,
                                                                                     vertexGroupNameList, entity.name,
                                                                                     return_type_list=True)

                            elif context.scene.renaming_object_types == 'PARTICLESYSTEM':
                                new_name, particleList = numerate_entity_name(context, replaceName,
                                                                              particleList, entity.name,
                                                                              return_type_list=True)

                            elif context.scene.renaming_object_types == 'PARTICLESETTINGS':
                                new_name, particleSettingsList = numerate_entity_name(context, replaceName,
                                                                              particleSettingsList, entity.name,
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

                            try:
                                entity.name = new_name
                                msg.addMessage(oldName, entity.name)
                            except AttributeError:
                                print("Attribute {} is read only".format(new_name))


        else:  # len(str(replaceName)) <= 0
            msg.addMessage(None, None, "Insert a valid string to replace names")

        callRenamingPopup(context)
        if switchEditMode:
            switchToEditMode(context)
        return {'FINISHED'}
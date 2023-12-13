import bpy
from ..variable_replacer.variable_replacer import VariableReplacer


def switchToEditMode(context):
    '''Switch to Edit Mode'''
    bpy.ops.object.mode_set(mode='EDIT')


def numerate_entity_name(context, basename, typelist, active_entity_name, return_type_list=False):
    '''Numerate entities and make sure they have a unique number'''
    wm = context.scene
    digits = len(wm.renaming_numerate)

    # Preferences
    prefs = context.preferences.addons[__package__.split('.')[0]].preferences
    separator = prefs.renaming_separator
    startNum = prefs.numerate_start_number
    step = prefs.numerate_step


    i = 0
    newName = basename + separator + (
        '{num:{fill}{width}}'.format(num=(i * step) + startNum, fill='0', width=digits))

    i = 1
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


def getAllModifiers():
    '''get list of all modifiers'''
    modifierList = []

    for obj in bpy.data.objects:
        for mod in obj.modifiers:
            modifierList.append(mod.name)

    return modifierList


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

def getAllParticleSettingsNames():
    '''get list of all particle settings'''
    particlesNamesList = []
    for par in bpy.data.particles:
        particlesNamesList.append(par.name)
        
    return particlesNamesList

def getAllUvMaps():
    uvNamesList = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        for uv in obj.data.uv_layers:
            uvNamesList.append(uv)
    return uvNamesList


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










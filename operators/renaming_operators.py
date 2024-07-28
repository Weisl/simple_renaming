import bpy

from .. import __package__ as base_package


def switch_to_edit_mode(context):
    """Switch to Edit Mode"""
    bpy.ops.object.mode_set(mode='EDIT')


def numerate_entity_name(context, basename, type_list, active_entity_name, return_type_list=False):
    """Numerate entities and make sure they have a unique number"""
    wm = context.scene
    digits = len(wm.renaming_numerate)

    # Preferences
    prefs = context.preferences.addons[base_package].preferences
    separator = prefs.renaming_separator
    start_number = prefs.numerate_start_number
    step = prefs.numerate_step

    i = 0
    new_name = basename + separator + (
        '{num:{fill}{width}}'.format(num=(i * step) + start_number, fill='0', width=digits))

    i = 1
    while new_name in type_list and new_name != active_entity_name:
        new_name = basename + separator + (
            '{num:{fill}{width}}'.format(num=(i * step) + start_number, fill='0', width=digits))
        i += 1

    if return_type_list:  # Manually add new name to custom generated list like all bones and all shape keys
        type_list.append(new_name)
        return new_name, type_list

    return new_name


def getAllBones(mode):
    """Get list of all bones depending on Edit or Pose Mode"""
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
    """get list of all modifiers"""
    modifierList = []

    for obj in bpy.data.objects:
        for mod in obj.modifiers:
            modifierList.append(mod.name)

    return modifierList


def getAllShapeKeys():
    """get list of all shape keys"""
    shapeKeyNamesList = []

    for key_grp in bpy.data.shape_keys:
        for key in key_grp.key_blocks:
            shapeKeyNamesList.append(key.name)

    return shapeKeyNamesList


def getAllVertexGroups():
    """get list of all vertex groups"""
    vrtx_grp_names_list = []

    for obj in bpy.data.objects:
        for vrtGrp in obj.vertex_groups:
            vrtx_grp_names_list.append(vrtGrp.name)

    return vrtx_grp_names_list


def getAllParticleNames():
    """get list of all particle systems"""
    particlesNamesList = []

    for obj in bpy.data.objects:
        for particle_system in obj.particle_systems:
            particlesNamesList.append(particle_system.name)
    return particlesNamesList


def getAllParticleSettingsNames():
    """get list of all particle settings"""
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
    """get list of all data"""
    dataList = []

    for obj in bpy.data.objects:
        if obj.data is not None:
            dataList.append(obj.data.name)

    return dataList

import bpy

from .numbering import format_number
from .. import __package__ as base_package


def switch_to_edit_mode(context):
    """Switch to Edit Mode"""
    bpy.ops.object.mode_set(mode='EDIT')


def numerate_entity_name(context, basename, type_list, active_entity_name, return_type_list=False):
    """Numerate entities and make sure they have a unique number"""
    wm = context.scene
    digits = wm.renaming_numerate

    # Preferences
    prefs = context.preferences.addons[base_package].preferences
    separator = prefs.renaming_separator
    start_number = prefs.numerate_start_number
    step = prefs.numerate_step
    use_letters = prefs.numerate_use_letters
    letters_upper = prefs.numerate_letters_upper

    i = 0
    new_name = basename + separator + format_number(
        (i * step) + start_number, digits, use_letters, letters_upper)

    i = 1
    while new_name in type_list and new_name != active_entity_name:
        new_name = basename + separator + format_number(
            (i * step) + start_number, digits, use_letters, letters_upper)
        i += 1

    if return_type_list:  # Manually add new name to custom generated set like all bones and all shape keys
        type_list.add(new_name)
        return new_name, type_list

    return new_name


def getAllBones(mode):
    """Get list of all bone names depending on Edit or Pose Mode"""
    if mode == 'POSE':
        return [bone.name for arm in bpy.data.armatures for bone in arm.bones]
    else:  # mode == 'EDIT'
        return [bone.name for arm in bpy.data.armatures for bone in arm.edit_bones]


def getAllModifiers():
    """get list of all modifier names"""
    return [mod.name for obj in bpy.data.objects for mod in obj.modifiers]


def getAllShapeKeys():
    """get list of all shape key names"""
    return [key.name for key_grp in bpy.data.shape_keys for key in key_grp.key_blocks]


def getAllVertexGroups():
    """get list of all vertex group names"""
    return [vg.name for obj in bpy.data.objects for vg in obj.vertex_groups]


def getAllParticleNames():
    """get list of all particle system names"""
    return [ps.name for obj in bpy.data.objects for ps in obj.particle_systems]


def getAllParticleSettingsNames():
    """get list of all particle settings names"""
    return [par.name for par in bpy.data.particles]


def getAllUvMaps():
    """get list of all UV map names"""
    return [uv.name for obj in bpy.data.objects if obj.type == 'MESH'
            for uv in obj.data.uv_layers]


def getAllColorAttributes():
    """get list of all color attribute names"""
    return [ca.name for obj in bpy.data.objects if obj.type == 'MESH'
            for ca in obj.data.color_attributes]


def getAllAttributes():
    """get list of all attribute names"""
    return [attr.name for obj in bpy.data.objects if obj.type == 'MESH'
            for attr in obj.data.attributes]


def getAllDataNames():
    """get list of all data names"""
    return [obj.data.name for obj in bpy.data.objects if obj.data is not None]

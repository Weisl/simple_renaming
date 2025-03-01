import bpy
from bpy.types import PoseBone, EditBone

from .. import __package__ as base_package


def trim_string(string, size):
    return string[size[0]:max(0, len(string)-size[1])]


def get_renaming_list(context):
    scene = context.scene

    renaming_list = []
    switch_edit_mode = False

    selection_only = scene.renaming_only_selection

    obj_list = context.selected_objects.copy() if selection_only is True else list(bpy.data.objects).copy()

    if scene.renaming_sorting:
        if scene.renaming_object_types == 'BONE':
            sort_enum = scene.renaming_sort_bone_enum
        else:
            sort_enum = scene.renaming_sort_enum

        if sort_enum == 'SELECTION':
            obj_list = get_ordered_selection_objects()
        elif sort_enum == 'X':
            obj_list = get_sorted_objects_x(obj_list)
        elif sort_enum == 'Y':
            obj_list = get_sorted_objects_y(obj_list)
        else:  # scene.renaming_sort_enum == 'Z':
            obj_list = get_sorted_objects_z(obj_list)

        if scene.renaming_sort_reverse:
            obj_list.reverse()

    if scene.renaming_object_types == 'OBJECT':
        for obj in obj_list:
            if obj in obj_list and obj.type in scene.renaming_object_types_specified:
                renaming_list.append(obj)

    elif scene.renaming_object_types == 'DATA':
        for obj in obj_list:
            if obj.data not in renaming_list:
                renaming_list.append(obj.data)

    elif scene.renaming_object_types == 'MATERIAL':
        if selection_only:
            for obj in context.selected_objects:
                for mat in obj.material_slots:
                    if mat is not None and mat.name != '':
                        renaming_list.append(bpy.data.materials[mat.name])
        else:
            renaming_list = list(bpy.data.materials)

    elif scene.renaming_object_types == 'IMAGE':
        renaming_list = list(bpy.data.images)

    elif scene.renaming_object_types == 'BONE':
        old_mode = context.mode

        if selection_only:

            selection_and_active = context.selected_objects.copy()
            if context.object not in selection_and_active:
                selection_and_active.append(context.object)

            if old_mode == 'OBJECT':
                error_msg = "Renaming only selected Bones is only supported for EDIT and POSE mode by now."
                return None, None, error_msg

            elif old_mode == 'POSE':
                selected_bones = context.selected_pose_bones.copy()

            else:  # if old_mode == 'EDIT_ARMATURE'
                selected_bones = context.selected_editable_bones.copy()
                switch_edit_mode = True

            armatures = []
            for obj in selection_and_active:
                if obj.type == 'ARMATURE':
                    armatures.append(obj.data)

            for selected_bone in selected_bones:
                for arm in armatures:
                    if old_mode == 'POSE':
                        name = selected_bone.name
                        for bone in arm.bones:
                            if name == bone.name:
                                new_bone = PoseBone(arm.bones[name])
                                renaming_list.append(new_bone)
                    else:  # old_mode == 'EDIT_ARMATURE':
                        for bone in arm.edit_bones:
                            if selected_bone == bone:
                                new_bone = EditBone(selected_bone)
                                renaming_list.append(new_bone)

        else:  # if selection_only == False
            for arm in bpy.data.armatures:
                if old_mode == 'EDIT_ARMATURE':
                    for bone in arm.edit_bones:
                        new_bone = EditBone(bone)
                        renaming_list.append(new_bone)
                else:  # old_mode == 'POSE' or old_mode == 'OBJECT'
                    for bone in arm.bones:
                        new_bone = PoseBone(bone)
                        renaming_list.append(new_bone)

    elif scene.renaming_object_types == 'COLLECTION':
        if bpy.context.space_data.type == 'OUTLINER' and selection_only is True:
            selected_collections = [c for c in context.selected_ids if c.bl_rna.identifier == "Collection"]
            for col in selected_collections:
                renaming_list.append(col)
        else:
            renaming_list = list(bpy.data.collections)

    elif scene.renaming_object_types == 'SHAPEKEYS':
        if selection_only:
            for obj in context.selected_objects:
                for shape in obj.data.shape_keys.key_blocks:
                    renaming_list.append(shape)
        else:  # selection_only == False:
            for key_grp in bpy.data.shape_keys:
                for key in key_grp.key_blocks:
                    renaming_list.append(key)

    elif scene.renaming_object_types == 'MODIFIERS':
        if selection_only:
            for obj in context.selected_objects:
                for mod in obj.modifiers:
                    renaming_list.append(mod)
        else:  # selection_only == False:
            for obj in bpy.data.objects:
                for mod in obj.modifiers:
                    renaming_list.append(mod)

    elif context.scene.renaming_object_types == 'VERTEXGROUPS':
        if selection_only:
            for obj in context.selected_objects:
                for vtx in obj.vertex_groups:
                    renaming_list.append(vtx)
        else:
            for obj in bpy.data.objects:
                for vtx in obj.vertex_groups:
                    renaming_list.append(vtx)

    elif context.scene.renaming_object_types == 'PARTICLESYSTEM':
        if selection_only:
            for obj in context.selected_objects:
                for particles in obj.particle_systems:
                    renaming_list.append(particles)
        else:
            for obj in bpy.data.objects:
                for particles in obj.particle_systems:
                    renaming_list.append(particles)

    elif context.scene.renaming_object_types == 'PARTICLESETTINGS':
        for particles in bpy.data.particles:
            renaming_list.append(particles)

    elif context.scene.renaming_object_types == 'UVMAPS':

        for obj in obj_list:
            if obj.type != 'MESH':
                continue
            for uv in obj.data.uv_layers:
                renaming_list.append(uv)

    elif context.scene.renaming_object_types == 'COLORATTRIBUTES':

        for obj in obj_list:
            if obj.type != 'MESH':
                continue
            for color_attribute in obj.data.color_attributes:
                renaming_list.append(color_attribute)

    elif context.scene.renaming_object_types == 'ATTRIBUTES':

        for obj in obj_list:
            if obj.type != 'MESH':
                continue
            for attribute in obj.data.attributes:
                renaming_list.append(attribute)

    elif scene.renaming_object_types == 'ACTIONS':
        if selection_only:
            obj_list = context.selected_objects.copy()
            for obj in obj_list:
                ad = obj.animation_data
                if ad:
                    if ad.action:
                        renaming_list.append(obj.animation_data.action)
                        for t in ad.nla_tracks:
                            for s in t.strips:
                                renaming_list.append(s.action)

        else:
            renaming_list = list(bpy.data.actions)

    # renaming_list.sort(key=lambda x: x.name, reverse=False)
    return renaming_list, switch_edit_mode, None


def call_renaming_popup(context):
    prefs = context.preferences.addons[base_package].preferences

    if prefs.renamingPanel_showPopup:
        bpy.ops.wm.call_panel(name="POPUP_PT_popup")
    return


def call_info_popup(context):
    bpy.ops.wm.call_panel(name="POPUP_PT_info")
    return


def call_error_popup(context):
    bpy.ops.wm.call_panel(name="POPUP_PT_error")
    return


# Function to get the global X location of an object
def get_global_x(obj):
    return obj.matrix_world.to_translation().x


# Function to get the global X location of an object
def get_global_y(obj):
    return obj.matrix_world.to_translation().y


def get_global_z(obj):
    return obj.matrix_world.to_translation().z


def get_ordered_selection_objects():
    tagged_objects = []
    for o in bpy.data.objects:
        order_index = o.get("selection_order", -1)
        if order_index >= 0:
            tagged_objects.append((order_index, o))
    tagged_objects = sorted(tagged_objects, key=lambda item: item[0])
    return [o for i, o in tagged_objects]


def get_sorted_objects_x(objects):
    # Sort objects by their global X location
    sorted_objects = sorted(objects, key=get_global_x)
    return sorted_objects


def get_sorted_objects_y(objects):
    # Sort objects by their global X location
    sorted_objects = sorted(objects, key=get_global_y)
    return sorted_objects


def get_sorted_objects_z(objects):
    # Sort objects by their global X location
    sorted_objects = sorted(objects, key=get_global_z)
    return sorted_objects


def clear_order_flag(obj):
    try:
        del obj["selection_order"]
    except KeyError:
        pass


def update_selection_order():
    if not bpy.context.selected_objects:
        for o in bpy.data.objects:
            clear_order_flag(o)
        return
    selection_order = get_ordered_selection_objects()
    idx = 0
    for o in selection_order:
        if not o.select_get():
            selection_order.remove(o)
            clear_order_flag(o)
        else:
            o["selection_order"] = idx

            # Hackish way to prevent unwanted keyframing of custom property. 
            # Setting custom properties non-animatable is not possible yet, see:
            # https://projects.blender.org/blender/blender/issues/113506
            if o.animation_data and o.animation_data.action:
                fcurves = o.animation_data.action.fcurves
                for fcurve in fcurves:
                    if fcurve.data_path == '["selection_order"]':
                        fcurves.remove(fcurve)

            idx += 1
    for o in bpy.context.selected_objects:
        if o not in selection_order:
            o["selection_order"] = len(selection_order)
            selection_order.append(o)

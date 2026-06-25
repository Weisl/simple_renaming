import time

import bpy
from bpy.types import PoseBone, EditBone

from .. import __package__ as base_package


def log_timing(context, label, t_start, entity_count):
    """Print elapsed time to the console when debug_timing is enabled."""
    prefs = context.preferences.addons[base_package].preferences
    if not prefs.debug_timing:
        return
    elapsed_ms = (time.perf_counter() - t_start) * 1000
    print(f"[RENAMING] {label}: {elapsed_ms:.1f} ms  ({entity_count} entities, "
          f"{elapsed_ms / entity_count:.3f} ms/entity)" if entity_count else
          f"[RENAMING] {label}: {elapsed_ms:.1f} ms")


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

        if sort_enum == 'X':
            obj_list = get_sorted_objects_x(obj_list)
        elif sort_enum == 'Y':
            obj_list = get_sorted_objects_y(obj_list)
        else:  # scene.renaming_sort_enum == 'Z':
            obj_list = get_sorted_objects_z(obj_list)

        if scene.renaming_sort_reverse:
            obj_list.reverse()

    if scene.renaming_object_types == 'OBJECT':
        for obj in obj_list:
            if obj.type in scene.renaming_object_types_specified:
                renaming_list.append(obj)

    elif scene.renaming_object_types == 'DATA':
        seen_data = set()
        for obj in obj_list:
            if obj.data is not None and id(obj.data) not in seen_data:
                seen_data.add(id(obj.data))
                renaming_list.append(obj.data)

    elif scene.renaming_object_types == 'MATERIAL':
        if selection_only:
            for obj in context.selected_objects:
                for mat in obj.material_slots:
                    if mat.material is not None:
                        renaming_list.append(mat.material)
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
        if bpy.context.space_data and bpy.context.space_data.type == 'OUTLINER' and selection_only is True:
            selected_collections = [c for c in context.selected_ids if c.bl_rna.identifier == "Collection"]
            for col in selected_collections:
                renaming_list.append(col)
        else:
            renaming_list = list(bpy.data.collections)

    elif scene.renaming_object_types == 'SHAPEKEYS':
        filter_index = scene.renaming_filter_by_index
        idx = scene.renaming_index_target
        if selection_only:
            for obj in context.selected_objects:
                if obj.data and obj.data.shape_keys:
                    items = list(obj.data.shape_keys.key_blocks)
                    if filter_index:
                        if idx < len(items):
                            renaming_list.append(items[idx])
                    else:
                        renaming_list.extend(items)
        else:  # selection_only == False:
            for key_grp in bpy.data.shape_keys:
                items = list(key_grp.key_blocks)
                if filter_index:
                    if idx < len(items):
                        renaming_list.append(items[idx])
                else:
                    renaming_list.extend(items)

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
        filter_index = scene.renaming_filter_by_index
        idx = scene.renaming_index_target
        obj_iter = context.selected_objects if selection_only else bpy.data.objects
        for obj in obj_iter:
            items = list(obj.vertex_groups)
            if filter_index:
                if idx < len(items):
                    renaming_list.append(items[idx])
            else:
                renaming_list.extend(items)

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

        filter_index = scene.renaming_filter_by_index
        active_only = scene.renaming_active_only
        idx = scene.renaming_index_target
        for obj in obj_list:
            if obj.type != 'MESH':
                continue
            if filter_index:
                items = list(obj.data.uv_layers)
                if idx < len(items):
                    item = items[idx]
                    if not active_only or obj.data.uv_layers.active == item:
                        renaming_list.append(item)
            elif active_only:
                active = obj.data.uv_layers.active
                if active is not None:
                    renaming_list.append(active)
            else:
                for uv in obj.data.uv_layers:
                    renaming_list.append(uv)

    elif context.scene.renaming_object_types == 'COLORATTRIBUTES':

        filter_index = scene.renaming_filter_by_index
        active_only = scene.renaming_active_only
        idx = scene.renaming_index_target
        for obj in obj_list:
            if obj.type != 'MESH':
                continue
            if filter_index:
                items = list(obj.data.color_attributes)
                if idx < len(items):
                    item = items[idx]
                    if not active_only or obj.data.color_attributes.active_color == item:
                        renaming_list.append(item)
            elif active_only:
                active = obj.data.color_attributes.active_color
                if active is not None:
                    renaming_list.append(active)
            else:
                for color_attribute in obj.data.color_attributes:
                    renaming_list.append(color_attribute)

    elif context.scene.renaming_object_types == 'ATTRIBUTES':

        filter_index = scene.renaming_filter_by_index
        idx = scene.renaming_index_target
        for obj in obj_list:
            if obj.type != 'MESH':
                continue
            items = list(obj.data.attributes)
            if filter_index:
                if idx < len(items):
                    renaming_list.append(items[idx])
            else:
                renaming_list.extend(items)

    elif scene.renaming_object_types == 'NODE_GROUPS':
        renaming_list = list(bpy.data.node_groups)

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


def rename_data_if_enabled(scene, entity):
    if scene.renaming_also_rename_data and \
            scene.renaming_object_types in ('OBJECT', 'ADDOBJECTS'):
        if hasattr(entity, 'data') and entity.data is not None:
            entity.data.name = entity.name


def update_bone_drivers(old_name, new_name):
    """Update all driver paths that reference a renamed bone."""
    if old_name == new_name:
        return

    # Blender may use either double or single quotes in data_path strings.
    old_tokens = (f'pose.bones["{old_name}"]', f"pose.bones['{old_name}']")
    new_token = f'pose.bones["{new_name}"]'

    for datablock in list(bpy.data.objects) + list(bpy.data.scenes):
        anim_data = getattr(datablock, 'animation_data', None)
        if anim_data is None:
            continue
        for fcurve in anim_data.drivers:
            # Location 1: FCurve data_path
            for old_token in old_tokens:
                if old_token in fcurve.data_path:
                    fcurve.data_path = fcurve.data_path.replace(old_token, new_token)

            driver = fcurve.driver
            if driver is None:
                continue
            for var in driver.variables:
                for target in var.targets:
                    # Location 2: bone_target field
                    if target.bone_target == old_name:
                        target.bone_target = new_name
                    # Location 3: data_path inside variable target
                    for old_token in old_tokens:
                        if old_token in target.data_path:
                            target.data_path = target.data_path.replace(old_token, new_token)



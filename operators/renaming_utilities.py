import re
import time

import bpy

from .. import __package__ as base_package

SELECTION_ORDER_KEY = "selection_order"


def count_selection_order_tags(context):
    if context.scene.renaming_object_types == 'BONE':
        return sum(1 for arm in bpy.data.armatures for bone in arm.bones if SELECTION_ORDER_KEY in bone)
    return sum(1 for o in bpy.data.objects if SELECTION_ORDER_KEY in o)


def _selection_order_key(tag):
    """Sort key putting tagged items first (in click order), untagged items
    last (in their existing relative order, since sorted() is stable)."""
    return (0, tag) if tag is not None else (1, 0)


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


def get_geometry_nodes_input(mod, identifier):
    """Value of a Geometry Nodes modifier input. Blender 5.3 exposes inputs as
    ``mod.properties.inputs.<identifier>.value``; older versions store them
    as ID properties on the modifier."""
    props = getattr(mod, "properties", None)
    if props is not None:
        return getattr(getattr(props.inputs, identifier, None), "value", None)
    return mod.get(identifier)


class _ImageCollector:
    """Gathers images in first-seen order without duplicates."""

    def __init__(self, include_node_groups):
        self.include_node_groups = include_node_groups
        self.images = []
        self._seen = set()
        self._visited_trees = set()

    def add(self, image):
        if isinstance(image, bpy.types.Image) and image.as_pointer() not in self._seen:
            self._seen.add(image.as_pointer())
            self.images.append(image)

    def add_node_tree(self, node_tree):
        """Images referenced by the nodes of ``node_tree``: image properties
        (Image Texture, Environment Texture, Image input nodes, ...) and Image
        socket values (e.g. Geometry Nodes Image Texture). Nested node groups
        are walked only when ``include_node_groups`` is set."""
        if node_tree is None or node_tree.as_pointer() in self._visited_trees:
            return
        self._visited_trees.add(node_tree.as_pointer())
        for node in node_tree.nodes:
            self.add(getattr(node, "image", None))
            for socket in node.inputs:
                if socket.type == 'IMAGE':
                    self.add(getattr(socket, "default_value", None))
            if self.include_node_groups and node.type == 'GROUP':
                self.add_node_tree(node.node_tree)

    def add_material(self, mat):
        if mat is None:
            return
        self.add_node_tree(mat.node_tree)
        gp_style = getattr(mat, "grease_pencil", None)
        if gp_style is not None:
            self.add(getattr(gp_style, "fill_image", None))
            self.add(getattr(gp_style, "stroke_image", None))

    def add_modifier(self, mod):
        # Displace, Warp, Wave, Vertex Weight ... modifiers use an image texture.
        texture = getattr(mod, "texture", None)
        if texture is not None and texture.type == 'IMAGE':
            self.add(texture.image)
        if mod.type == 'NODES' and mod.node_group is not None:
            # Images assigned to the modifier's Image inputs.
            for item in mod.node_group.interface.items_tree:
                if (item.item_type == 'SOCKET' and item.in_out == 'INPUT'
                        and item.socket_type == 'NodeSocketImage'):
                    self.add(get_geometry_nodes_input(mod, item.identifier))
            # The modifier's own tree is its top level, like a material's tree.
            self.add_node_tree(mod.node_group)

    def add_object(self, obj):
        if obj.type == 'EMPTY':
            self.add(obj.data)
        elif obj.type == 'CAMERA':
            for background in obj.data.background_images:
                self.add(background.image)
        for slot in obj.material_slots:
            self.add_material(slot.material)
        for mod in obj.modifiers:
            self.add_modifier(mod)


def get_images_of_objects(objects, include_node_groups=True):
    """Images used by ``objects``: textures in their materials and modifiers
    (optionally including nested node groups), the image of image empties and
    camera background images. Returned in object order without duplicates."""
    collector = _ImageCollector(include_node_groups)
    for obj in objects:
        collector.add_object(obj)
    return collector.images


def get_renaming_list(context):
    scene = context.scene

    renaming_list = []
    switch_edit_mode = False

    selection_only = scene.renaming_only_selection

    obj_list = context.selected_objects.copy() if selection_only is True else list(bpy.data.objects).copy()

    # Bones are sorted in the BONE branch below, after the bone list is built.
    if scene.renaming_sorting and scene.renaming_object_types != 'BONE':
        sort_enum = scene.renaming_sort_enum

        if sort_enum == 'SELECTION':
            obj_list = sorted(obj_list, key=lambda o: _selection_order_key(o.get(SELECTION_ORDER_KEY)))
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
            effective_type = 'GPENCIL' if obj.type == 'GREASEPENCIL' else obj.type
            if effective_type in scene.renaming_object_types_specified:
                renaming_list.append(obj)

    elif scene.renaming_object_types == 'DATA':
        seen_data = set()
        for obj in obj_list:
            if obj.data is not None and id(obj.data) not in seen_data:
                seen_data.add(id(obj.data))
                renaming_list.append(obj.data)

    elif scene.renaming_object_types == 'MATERIAL':
        if selection_only:
            for obj in obj_list:
                for mat in obj.material_slots:
                    if mat.material is not None:
                        renaming_list.append(mat.material)
        else:
            renaming_list = list(bpy.data.materials)

    elif scene.renaming_object_types == 'IMAGE':
        if selection_only:
            renaming_list = get_images_of_objects(obj_list, scene.renaming_images_include_node_groups)
        else:
            renaming_list = list(bpy.data.images)

    elif scene.renaming_object_types == 'BONE':
        old_mode = context.mode
        bone_order_keys = []
        # Armature -> owning Object, needed to reach the real PoseBone in POSE
        # mode and to sort bones in world space (a single Armature datablock
        # can be used by several objects).
        armature_owners = {obj.data: obj for obj in bpy.data.objects if obj.type == 'ARMATURE'}

        def _bone_order_value(arm, name):
            bone = arm.bones.get(name)
            return bone.get(SELECTION_ORDER_KEY) if bone else None

        if selection_only:

            if old_mode == 'OBJECT':
                error_msg = "Renaming only selected Bones is only supported for EDIT and POSE mode by now."
                return None, None, error_msg

            elif old_mode == 'POSE':
                # context.selected_pose_bones already gives real, correctly-owned
                # PoseBone entries — no need to re-find them by name (which used to
                # wrap a plain Bone as a "PoseBone", a type it never actually was).
                for selected_bone in context.selected_pose_bones.copy():
                    renaming_list.append(selected_bone)
                    bone_order_keys.append(selected_bone.bone.get(SELECTION_ORDER_KEY))

            else:  # if old_mode == 'EDIT_ARMATURE'
                switch_edit_mode = True
                for selected_bone in context.selected_editable_bones.copy():
                    renaming_list.append(selected_bone)
                    bone_order_keys.append(_bone_order_value(selected_bone.id_data, selected_bone.name))

        else:  # if selection_only == False
            for arm in bpy.data.armatures:
                if old_mode == 'EDIT_ARMATURE':
                    for bone in arm.edit_bones:
                        renaming_list.append(bone)
                        bone_order_keys.append(_bone_order_value(arm, bone.name))
                elif old_mode == 'POSE':
                    owner_obj = armature_owners.get(arm)
                    if owner_obj is None:
                        continue
                    for bone in arm.bones:
                        renaming_list.append(owner_obj.pose.bones[bone.name])
                        bone_order_keys.append(_bone_order_value(arm, bone.name))
                else:  # old_mode == 'OBJECT'
                    for bone in arm.bones:
                        renaming_list.append(bone)
                        bone_order_keys.append(_bone_order_value(arm, bone.name))

        if scene.renaming_sorting:
            sort_enum = scene.renaming_sort_bone_enum
            if sort_enum == 'SELECTION':
                sort_keys = [_selection_order_key(tag) for tag in bone_order_keys]
            else:
                axis = 'XYZ'.index(sort_enum)
                sort_keys = [_bone_world_head(bone, armature_owners)[axis] for bone in renaming_list]
            # Stable sort on the key only, so ties keep their existing order.
            renaming_list = [b for _, b in sorted(zip(sort_keys, renaming_list), key=lambda pair: pair[0])]
            if scene.renaming_sort_reverse:
                renaming_list.reverse()

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
            for obj in obj_list:
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
        for obj in obj_list:
            for mod in obj.modifiers:
                renaming_list.append(mod)

    elif context.scene.renaming_object_types == 'VERTEXGROUPS':
        filter_index = scene.renaming_filter_by_index
        idx = scene.renaming_index_target
        for obj in obj_list:
            items = list(obj.vertex_groups)
            if filter_index:
                if idx < len(items):
                    renaming_list.append(items[idx])
            else:
                renaming_list.extend(items)

    elif context.scene.renaming_object_types == 'PARTICLESYSTEM':
        for obj in obj_list:
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


def _bone_world_head(bone, armature_owners):
    """World-space head of a Bone, EditBone or PoseBone. Bone and EditBone
    belong to the Armature datablock, so the owning object comes from
    ``armature_owners``; without an owner the armature-space head is used."""
    if isinstance(bone, bpy.types.PoseBone):
        return bone.id_data.matrix_world @ bone.head
    head = bone.head if isinstance(bone, bpy.types.EditBone) else bone.head_local
    owner = armature_owners.get(bone.id_data)
    return owner.matrix_world @ head if owner is not None else head


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


_AUTO_SUFFIX_RE = re.compile(r'\.\d{3,}$')


def _detect_name_conflict(intended, actual):
    """Return a short warning reason if Blender's auto-uniquify changed the
    name the caller asked for, else False. The caller (the popup) already
    shows the intended vs. actual name side by side, so this only needs to
    say why, not repeat either name. Strips any pre-existing numeric tail
    from both sides before comparing, so an intended name that already ends
    in e.g. '.005' (numerate/rename-by-index) is still recognized correctly
    when Blender bumps it to '.006' instead of leaving it untouched."""
    if intended == actual:
        return False
    if _AUTO_SUFFIX_RE.sub('', intended) == _AUTO_SUFFIX_RE.sub('', actual):
        return "name already in use"
    return "could not apply name exactly"


def apply_rename(scene, entity, new_name, msg, old_name=None, obType=False, obIcon=False):
    """Assign entity.name, detect any Blender-side conflict, and log a message.
    Returns (actual_name, warning_or_None, is_protected).

    If Blender can't give the entity exactly the requested name, the rename
    is reverted rather than kept under whatever fallback name Blender's
    auto-uniquify picked — accepting that fallback is how a batch full of
    conflicts turns into a confusing cascade (Foo.002 silently becoming
    Foo.001, etc., see issue #233). A conflicting entity is left untouched
    and reported as skipped instead.

    is_protected distinguishes a rename that Blender refused outright (the ID
    is linked from an external library, or it's a built-in/intrinsic item
    Blender hard-protects from renaming — e.g. mesh attributes like
    "position"; nothing changed) from a plain name conflict (the rename is
    attempted, found to collide, and reverted) — different failure modes
    callers should track/report separately.

    old_name overrides what gets reported/used for driver fixups — needed by
    name_replace's enumerate path, which parks entities under a temporary
    placeholder name before calling this, so entity.name at call time is
    that placeholder, not the real original name.
    """
    reported_old_name = old_name if old_name is not None else entity.name
    try:
        entity.name = new_name
    except AttributeError:
        warning = "name is protected, could not rename"
        msg.add_message(reported_old_name, reported_old_name, obType, obIcon, warning=warning)
        return reported_old_name, warning, True

    warning = _detect_name_conflict(new_name, entity.name)
    if warning:
        if entity.name != reported_old_name:
            try:
                entity.name = reported_old_name
            except AttributeError:
                pass
        msg.add_message(reported_old_name, reported_old_name, obType, obIcon, warning=warning)
        return reported_old_name, warning, False

    rename_data_if_enabled(scene, entity)
    if isinstance(entity, (bpy.types.Bone, bpy.types.EditBone, bpy.types.PoseBone)):
        update_bone_drivers(reported_old_name, entity.name)

    msg.add_message(reported_old_name, entity.name, obType, obIcon, warning=False)
    return entity.name, False, False


def report_rename_warnings(op, conflict_count, protected_count=0):
    """Surface a status-bar/Info-log warning so conflicts are visible even
    when the popup preference (renamingPanel_showPopup) is off."""
    parts = []
    if conflict_count:
        noun = "item" if conflict_count == 1 else "items"
        parts.append(f"{conflict_count} {noun} skipped due to a naming conflict")
    if protected_count:
        noun = "item" if protected_count == 1 else "items"
        parts.append(f"{protected_count} protected {noun} could not be renamed")
    if parts:
        op.report({'WARNING'}, "; ".join(parts) + ". See the Rename Info popup for details.")


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



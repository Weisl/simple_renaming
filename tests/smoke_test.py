"""
Smoke tests for simple_renaming performance optimisations.

Run headlessly:
    /path/to/blender --background --python tests/smoke_test.py

The script discovers the already-loaded addon, builds a small scene for each
test, exercises every changed code path, and exits with code 0 (pass) or 1
(fail).

Note: bpy.ops.wm.read_homefile() crashes Blender 5.x in background mode, so
each test cleans up after itself instead of resetting the scene.
"""

import sys
import os
from importlib import import_module

import bpy
import addon_utils

# ---------------------------------------------------------------------------
# Addon discovery and loading.
#
# Two scenarios:
#   A) Normal startup: the extension is already registered as
#      bl_ext.<repo>.simple_renaming — just find it.
#   B) --factory-startup: no user extensions loaded — add the source tree to
#      sys.path and enable it as a legacy addon named 'simple_renaming'.
# ---------------------------------------------------------------------------

# tests/ -> simple_renaming/ -> extensions/  (the dir that *contains* the package)
_ADDON_SOURCE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _find_addon_id():
    for key in bpy.context.preferences.addons.keys():
        if key == "simple_renaming" or key.endswith(".simple_renaming"):
            return key
    return None


def _load_addon():
    """Load the addon from source when it is not already registered."""
    if _ADDON_SOURCE not in sys.path:
        sys.path.insert(0, _ADDON_SOURCE)
    addon_utils.enable("simple_renaming", default_set=True)
    return _find_addon_id()


ADDON_ID = _find_addon_id() or _load_addon()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

failures = []


def check(condition, label):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}")
        failures.append(label)


def scene_prop(name, value):
    setattr(bpy.context.scene, name, value)


def purge_objects(names):
    for name in list(names):
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)


def purge_all_with_prefix(prefix):
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefix):
            bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        if mesh.name.startswith(prefix):
            bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        if mat.name.startswith(prefix):
            bpy.data.materials.remove(mat)
    for col in list(bpy.data.collections):
        if col.name.startswith(prefix):
            bpy.data.collections.remove(col)
    for arm in list(bpy.data.armatures):
        if arm.name.startswith(prefix):
            bpy.data.armatures.remove(arm)
    for hc in list(bpy.data.hair_curves):
        if hc.name.startswith(prefix):
            bpy.data.hair_curves.remove(hc)


def add_mesh_object(name, collection=None):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if collection is not None:
        collection.objects.link(obj)
    return obj


def _numbering_module():
    return import_module(f"{ADDON_ID}.operators.numbering")


def reset_scene_props():
    scene_prop("renaming_only_selection", False)
    scene_prop("renaming_use_enumerate", False)
    scene_prop("renaming_new_name", "")
    scene_prop("renaming_search", "")
    scene_prop("renaming_replace", "")


# ---------------------------------------------------------------------------
# Test 1 – getCollection cache (@c variable)
# ---------------------------------------------------------------------------

def test_get_collection():
    print("\n[Test 1] getCollection cache (@c variable)")
    PREFIX = "T1_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    col = bpy.data.collections.new(f"{PREFIX}Assets")
    bpy.context.scene.collection.children.link(col)
    objs = [add_mesh_object(f"{PREFIX}Obj{i}", collection=col) for i in range(3)]
    bpy.context.view_layer.objects.active = objs[0]

    scene_prop("renaming_object_types", "OBJECT")
    scene_prop("renaming_new_name", "@c_item")
    bpy.ops.renaming.name_replace()

    result = any(o.name == f"{PREFIX}Assets_item" for o in bpy.data.objects)
    check(result, "Objects renamed using @c (collection name)")

    purge_all_with_prefix(PREFIX)
    purge_all_with_prefix(f"{PREFIX}Assets")  # collection-named objects


# ---------------------------------------------------------------------------
# Test 2 – getOwnerObjectName cache for materials (@o variable)
# ---------------------------------------------------------------------------

def test_get_owner_object_name_material():
    print("\n[Test 2] getOwnerObjectName cache – material @o variable")
    PREFIX = "T2_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    obj = add_mesh_object(f"{PREFIX}Holder")
    mat = bpy.data.materials.new(f"{PREFIX}OldMat")
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj

    scene_prop("renaming_object_types", "MATERIAL")
    scene_prop("renaming_new_name", "@o_mat")
    bpy.ops.renaming.name_replace()

    check(bpy.data.materials.get(f"{PREFIX}Holder_mat") is not None,
          "Material renamed using @o (owner object name)")

    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 3 – getOwnerObjectName cache for shape keys (@o variable)
# ---------------------------------------------------------------------------

def test_get_owner_object_name_shapekey():
    print("\n[Test 3] getOwnerObjectName cache – shape key @o variable")
    PREFIX = "T3_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    mesh = bpy.data.meshes.new(f"{PREFIX}SKMesh")
    obj = bpy.data.objects.new(f"{PREFIX}SKHolder", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.shape_key_add(name="Basis")
    obj.shape_key_add(name="Key1")
    bpy.context.view_layer.objects.active = obj

    scene_prop("renaming_object_types", "SHAPEKEYS")
    scene_prop("renaming_new_name", "@o_shape")
    bpy.ops.renaming.name_replace()

    # Both shape keys resolve @o to the same owner-object name, so they're
    # guaranteed to collide with each other — only the first one processed
    # can claim it; apply_rename now reverts (skips) the second instead of
    # auto-suffixing it. Just confirm @o resolved correctly at all.
    keys = [k.name for k in obj.data.shape_keys.key_blocks]
    check(f"{PREFIX}SKHolder_shape" in keys,
          f"Shape key renamed using @o (owner object name) — got {keys}")

    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 4 – numerate_entity_name set uniqueness (bones)
# ---------------------------------------------------------------------------

def test_numerate_bones_unique():
    print("\n[Test 4] numerate_entity_name set uniqueness – bones")
    PREFIX = "T4_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    arm_data = bpy.data.armatures.new(f"{PREFIX}Arm")
    arm_obj = bpy.data.objects.new(f"{PREFIX}Arm", arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    for i in range(5):
        b = arm_data.edit_bones.new(f"{PREFIX}Bone{i}")
        b.head = (0, i * 0.1, 0)
        b.tail = (0, i * 0.1, 0.1)
    bpy.ops.object.mode_set(mode='OBJECT')

    scene_prop("renaming_object_types", "BONE")
    scene_prop("renaming_new_name", "bone")
    scene_prop("renaming_use_enumerate", True)
    bpy.ops.renaming.name_replace()

    names = [b.name for b in arm_data.bones]
    check(len(names) == len(set(names)),
          f"All bone names unique after numerate — got {names}")

    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 5 – getAllAttributes fix (was iterating color_attributes by mistake)
# ---------------------------------------------------------------------------

def test_get_all_attributes():
    print("\n[Test 5] getAllAttributes returns attribute names, not color_attribute names")
    PREFIX = "T5_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    mesh = bpy.data.meshes.new(f"{PREFIX}AttrMesh")
    obj = bpy.data.objects.new(f"{PREFIX}AttrObj", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    # Add a writable custom attribute (built-ins like 'position' are read-only).
    mesh.attributes.new(name=f"{PREFIX}my_float", type='FLOAT', domain='POINT')

    scene_prop("renaming_object_types", "ATTRIBUTES")
    scene_prop("renaming_new_name", "renamed_attr")
    bpy.ops.renaming.name_replace()

    attr_names = [a.name for a in mesh.attributes]
    # The custom attribute should be renamed; built-in read-only ones are skipped.
    check(any("renamed_attr" in n for n in attr_names),
          f"Custom attribute renamed correctly — got {attr_names}")

    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 6 – search & replace, case-insensitive, static pattern path
# ---------------------------------------------------------------------------

def test_search_replace_static_pattern():
    print("\n[Test 6] search_replace static pattern (no @ variables)")
    PREFIX = "T6_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    # Distinct numeric suffixes keep the 3 results from colliding with each
    # other post-replace — a genuine collision would now get reverted
    # (skipped) instead of auto-suffixed, which isn't what this test targets.
    for name in [f"{PREFIX}Cube_Low_1", f"{PREFIX}cube_low_2", f"{PREFIX}CUBE_LOW_3"]:
        add_mesh_object(name)

    scene_prop("renaming_object_types", "OBJECT")
    scene_prop("renaming_search", "cube_low")
    scene_prop("renaming_replace", "Base")
    scene_prop("renaming_matchcase", False)
    scene_prop("renaming_useRegex", False)
    bpy.ops.renaming.search_replace()

    renamed = [o.name for o in bpy.data.objects
               if o.name.startswith(PREFIX) and "Base" in o.name]
    check(len(renamed) == 3,
          f"Case-insensitive replace hit all 3 variants — got {renamed}")

    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 7 – update_bone_drivers: driver paths updated after bone rename
# ---------------------------------------------------------------------------

def test_bone_rename_updates_drivers():
    print("\n[Test 7] update_bone_drivers – FCurve data_path and bone_target updated")
    PREFIX = "T7_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    # Create armature with one bone.
    arm_data = bpy.data.armatures.new(f"{PREFIX}Arm")
    arm_obj = bpy.data.objects.new(f"{PREFIX}Arm", arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    b = arm_data.edit_bones.new(f"{PREFIX}OldBone")
    b.head = (0, 0, 0)
    b.tail = (0, 0, 0.1)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add a driver FCurve on the armature object that drives X location,
    # using the bone name in data_path and bone_target.
    fcurve = arm_obj.driver_add('location', 0)
    fcurve.data_path = f'pose.bones["{PREFIX}OldBone"].location[0]'
    drv = fcurve.driver
    drv.type = 'AVERAGE'
    var = drv.variables.new()
    var.type = 'TRANSFORMS'
    target = var.targets[0]
    target.id = arm_obj
    target.bone_target = f"{PREFIX}OldBone"

    # Rename the bone via the extension.
    scene_prop("renaming_object_types", "BONE")
    scene_prop("renaming_new_name", f"{PREFIX}NewBone")
    scene_prop("renaming_use_enumerate", False)
    bpy.ops.renaming.name_replace()

    # Find the driver FCurve (data_path may have changed).
    updated_fcurve = None
    if arm_obj.animation_data:
        for fc in arm_obj.animation_data.drivers:
            if f"{PREFIX}NewBone" in fc.data_path:
                updated_fcurve = fc
                break

    check(updated_fcurve is not None,
          f"FCurve data_path updated to contain '{PREFIX}NewBone'")

    if updated_fcurve is not None:
        bt = updated_fcurve.driver.variables[0].targets[0].bone_target
        check(bt == f"{PREFIX}NewBone",
              f"bone_target updated to '{PREFIX}NewBone' — got '{bt}'")
        check(f"{PREFIX}OldBone" not in updated_fcurve.data_path,
              "Old bone name no longer present in data_path")

    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 8 – CURVES object type enabled by default and renamed in OBJECT mode
# ---------------------------------------------------------------------------

def test_curves_object_type():
    print("\n[Test 8] CURVES object type – enabled by default and renamed")
    PREFIX = "T8_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    curves_data = bpy.data.hair_curves.new(f"{PREFIX}CurvesData")
    obj = bpy.data.objects.new(f"{PREFIX}Curves", curves_data)
    bpy.context.scene.collection.objects.link(obj)
    for other in bpy.context.selected_objects:
        other.select_set(False)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    check(obj.type == 'CURVES', f"Test object has type CURVES — got '{obj.type}'")

    scene = bpy.context.scene
    check('CURVES' in scene.renaming_object_types_specified,
          "CURVES is enabled by default in renaming_object_types_specified")

    scene_prop("renaming_object_types", "OBJECT")
    scene_prop("renaming_only_selection", True)
    scene_prop("renaming_new_name", f"{PREFIX}Renamed")
    bpy.ops.renaming.name_replace()

    check(obj.name == f"{PREFIX}Renamed",
          f"Curves object renamed via OBJECT mode — got '{obj.name}'")

    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 9 – SELECTION sort mode numbers objects in tagged click order
# ---------------------------------------------------------------------------

def test_selection_order_sort():
    print("\n[Test 9] SELECTION sort mode – tagged objects get the first numbers "
          "in click order, untagged ones are still renamed (not dropped) after them")
    PREFIX = "T9_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    # Restrict to MESH so a --factory-startup scene's default Camera/Light (also
    # enabled by default) don't get swept into the untagged-but-in-scope group below.
    default_types_specified = set(bpy.context.scene.renaming_object_types_specified)
    scene_prop("renaming_object_types_specified", {'MESH'})
    # The default startup scene's own "Cube" (also MESH) would otherwise be an
    # extra untagged-but-in-scope object, making the exact numbering below
    # nondeterministic — clear it out so only this test's 4 objects are in play.
    for obj in list(bpy.data.objects):
        if obj.type == 'MESH' and not obj.name.startswith(PREFIX):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Obj0..Obj2 are "clicked" (tagged) in reverse order, simulating what
    # VIEW3D_OT_select_in_renaming_order would tag via raycasting. Obj3 is
    # deliberately left untagged — it must still be renamed, not dropped, just
    # sorted after the deliberately-ordered ones.
    objs = [add_mesh_object(f"{PREFIX}Obj{i}") for i in range(4)]
    for obj in objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]

    untagged = objs[3]
    click_order = list(reversed(objs[:3]))  # Obj2, Obj1, Obj0
    for idx, obj in enumerate(click_order):
        obj["selection_order"] = idx

    scene_prop("renaming_object_types", "OBJECT")
    scene_prop("renaming_sorting", True)
    scene_prop("renaming_sort_enum", "SELECTION")
    scene_prop("renaming_use_enumerate", True)
    scene_prop("renaming_new_name", f"{PREFIX}Sorted")
    bpy.ops.renaming.name_replace()

    check(click_order[0].name.endswith("001") and
          click_order[1].name.endswith("002") and
          click_order[2].name.endswith("003"),
          "Tagged objects numbered first, in click order — got "
          f"{[o.name for o in click_order]}")
    check(untagged.name.endswith("004"),
          f"Untagged object still renamed, sorted after tagged ones — got '{untagged.name}'")

    for obj in objs:
        if "selection_order" in obj:
            del obj["selection_order"]

    scene_prop("renaming_sorting", False)
    scene_prop("renaming_sort_enum", "X")
    scene_prop("renaming_use_enumerate", False)
    scene_prop("renaming_object_types_specified", default_types_specified)
    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 10 – SELECTION sort mode numbers bones in tagged click order
# ---------------------------------------------------------------------------

def test_selection_order_sort_bones():
    print("\n[Test 10] SELECTION sort mode – numbers bones in tagged (clicked) order")
    PREFIX = "T10_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    arm_data = bpy.data.armatures.new(f"{PREFIX}Arm")
    arm_obj = bpy.data.objects.new(f"{PREFIX}Arm", arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    bone_names = []
    for i in range(3):
        b = arm_data.edit_bones.new(f"{PREFIX}Bone{i}")
        b.head = (0, i * 0.1, 0)
        b.tail = (0, i * 0.1, 0.1)
        bone_names.append(b.name)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Created as Bone0, Bone1, Bone2 (in that order) but "clicked" (tagged) in reverse,
    # simulating what VIEW3D_OT_select_in_renaming_order would tag on the persistent
    # Bone data-block (armature.bones), same as it would from Edit or Pose mode.
    click_order_names = list(reversed(bone_names))  # Bone2, Bone1, Bone0
    for idx, name in enumerate(click_order_names):
        arm_data.bones[name]["selection_order"] = idx
    click_order_bones = [arm_data.bones[name] for name in click_order_names]

    scene_prop("renaming_object_types", "BONE")
    scene_prop("renaming_sorting", True)
    scene_prop("renaming_sort_bone_enum", "SELECTION")
    scene_prop("renaming_only_selection", False)
    scene_prop("renaming_use_enumerate", True)
    scene_prop("renaming_new_name", f"{PREFIX}Sorted")
    bpy.ops.renaming.name_replace()

    check(click_order_bones[0].name.endswith("001") and
          click_order_bones[1].name.endswith("002") and
          click_order_bones[2].name.endswith("003"),
          "Bones numbered in tagged click order (first click = 001), not creation "
          f"order — got {[b.name for b in click_order_bones]}")

    scene_prop("renaming_sorting", False)
    scene_prop("renaming_sort_bone_enum", "X")
    scene_prop("renaming_use_enumerate", False)
    scene_prop("renaming_only_selection", False)
    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 11 – SELECTION sort mode still respects "Only Selected"
# ---------------------------------------------------------------------------

def test_selection_order_respects_only_selected():
    print("\n[Test 11] SELECTION sort mode still respects \"Only Selected\"")
    PREFIX = "T11_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    objs = [add_mesh_object(f"{PREFIX}Obj{i}") for i in range(4)]
    # Tag all 4 (as if picked in an earlier session) but only keep 3 selected
    # now — the tagged-but-unselected one must be left alone.
    click_order = [objs[3], objs[1], objs[0], objs[2]]
    for idx, obj in enumerate(click_order):
        obj["selection_order"] = idx

    excluded = objs[2]
    for obj in objs:
        obj.select_set(obj is not excluded)
    bpy.context.view_layer.objects.active = objs[0]

    scene_prop("renaming_object_types", "OBJECT")
    scene_prop("renaming_only_selection", True)
    scene_prop("renaming_sorting", True)
    scene_prop("renaming_sort_enum", "SELECTION")
    scene_prop("renaming_use_enumerate", True)
    scene_prop("renaming_new_name", f"{PREFIX}Sorted")
    bpy.ops.renaming.name_replace()

    expected_order = [o for o in click_order if o is not excluded]  # objs[3], objs[1], objs[0]
    check(excluded.name == f"{PREFIX}Obj2",
          f"Tagged-but-unselected object left untouched — got '{excluded.name}'")
    check(expected_order[0].name.endswith("001") and
          expected_order[1].name.endswith("002") and
          expected_order[2].name.endswith("003"),
          "Only the selected+tagged objects renamed, in click order — got "
          f"{[o.name for o in expected_order]}")

    for obj in objs:
        if "selection_order" in obj:
            del obj["selection_order"]
    scene_prop("renaming_only_selection", False)
    scene_prop("renaming_sorting", False)
    scene_prop("renaming_sort_enum", "X")
    scene_prop("renaming_use_enumerate", False)
    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 12 – MATERIAL renaming follows object click order under Selection sort
# ---------------------------------------------------------------------------

def test_material_follows_object_selection_order():
    print("\n[Test 12] MATERIAL renaming follows object click order under Selection sort")
    PREFIX = "T12_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    obj0 = add_mesh_object(f"{PREFIX}Obj0")
    mat0 = bpy.data.materials.new(f"{PREFIX}Mat0")
    obj0.data.materials.append(mat0)

    obj1 = add_mesh_object(f"{PREFIX}Obj1")
    mat1 = bpy.data.materials.new(f"{PREFIX}Mat1")
    obj1.data.materials.append(mat1)

    # Click order: Obj1 first, then Obj0 — reverse of creation order.
    obj1["selection_order"] = 0
    obj0["selection_order"] = 1
    obj0.select_set(True)
    obj1.select_set(True)
    bpy.context.view_layer.objects.active = obj0

    scene_prop("renaming_object_types", "MATERIAL")
    scene_prop("renaming_only_selection", True)
    scene_prop("renaming_sorting", True)
    scene_prop("renaming_sort_enum", "SELECTION")
    scene_prop("renaming_use_enumerate", True)
    scene_prop("renaming_new_name", f"{PREFIX}Mat")
    bpy.ops.renaming.name_replace()

    check(mat1.name.endswith("001") and mat0.name.endswith("002"),
          f"Materials renamed in object click order (Obj1's material first) — got "
          f"mat1={mat1.name}, mat0={mat0.name}")

    for obj in (obj0, obj1):
        if "selection_order" in obj:
            del obj["selection_order"]
    scene_prop("renaming_only_selection", False)
    scene_prop("renaming_sorting", False)
    scene_prop("renaming_sort_enum", "X")
    scene_prop("renaming_use_enumerate", False)
    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 13 – name_replace logs a warning when a target name collides in-batch
# ---------------------------------------------------------------------------

def test_name_replace_conflict_warning():
    print("\n[Test 13] name_replace skips (reverts) the second object on an in-batch name collision")
    PREFIX = "T13_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()
    bpy.context.scene.renaming_messages.clear()

    obj_a = add_mesh_object(f"{PREFIX}A")
    obj_b = add_mesh_object(f"{PREFIX}B")
    orig_a, orig_b = obj_a.name, obj_b.name
    obj_a.select_set(True)
    obj_b.select_set(True)
    bpy.context.view_layer.objects.active = obj_a

    scene_prop("renaming_object_types", "OBJECT")
    scene_prop("renaming_only_selection", True)
    scene_prop("renaming_new_name", f"{PREFIX}Same")
    bpy.ops.renaming.name_replace()

    target = f"{PREFIX}Same"
    claimed = [o for o in (obj_a, obj_b) if o.name == target]
    skipped = [o for o in (obj_a, obj_b) if o.name != target]
    check(len(claimed) == 1,
          f"Exactly one object claimed the target name — got {[obj_a.name, obj_b.name]}")
    check(len(skipped) == 1 and skipped[0].name in (orig_a, orig_b),
          f"The colliding object was left at its original name instead of auto-suffixed — got {[obj_a.name, obj_b.name]}")

    warnings = [m for m in bpy.context.scene.renaming_messages.message if m.get('warning')]
    check(len(warnings) == 1,
          f"Exactly one conflict warning logged for the collision — got {len(warnings)}")

    scene_prop("renaming_only_selection", False)
    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 14 – trim_string warns even when the colliding result looks unchanged
# (the exact "no objects renamed" confusion from GitHub issue #233)
# ---------------------------------------------------------------------------

def test_trim_conflict_no_visible_change_still_warns():
    print("\n[Test 14] trim_string warns even when the colliding target name looks unchanged")
    PREFIX = "T14_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()
    bpy.context.scene.renaming_messages.clear()

    obj_a = add_mesh_object(f"{PREFIX}Chest")
    obj_b = add_mesh_object(f"{PREFIX}Chest.001")

    obj_a.select_set(False)
    obj_b.select_set(True)
    bpy.context.view_layer.objects.active = obj_b

    scene_prop("renaming_object_types", "OBJECT")
    scene_prop("renaming_only_selection", True)
    scene_prop("renaming_trim_indices", (0, 4))  # strip the trailing ".001"
    bpy.ops.renaming.trim_string()

    check(obj_b.name == f"{PREFIX}Chest.001",
          f"Colliding trim silently reverted to the original name — got {obj_b.name}")

    warnings = [m for m in bpy.context.scene.renaming_messages.message if m.get('warning')]
    check(len(warnings) == 1,
          f"Conflict warning logged even though the name looked unchanged — got {len(warnings)}")

    scene_prop("renaming_only_selection", False)
    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 15 – shared numbering module: format_number / int_to_letters / letters_to_int
# ---------------------------------------------------------------------------

def test_numbering_module_roundtrip():
    print("\n[Test 15] numbering module – format_number / int_to_letters / letters_to_int")
    numbering = _numbering_module()

    check(numbering.format_number(5, 3, use_letters=False) == "005",
          "format_number digits mode zero-pads correctly")
    check(numbering.int_to_letters(1) == "A" and numbering.int_to_letters(26) == "Z"
          and numbering.int_to_letters(27) == "AA",
          "int_to_letters produces spreadsheet-style base-26 letters (1->A, 26->Z, 27->AA)")
    check(numbering.format_number(1, 3, use_letters=True, letters_upper=False) == "a",
          "format_number letters mode respects letters_upper=False")

    roundtrip_ok = all(
        numbering.letters_to_int(numbering.int_to_letters(n)) == n
        for n in range(1, 100)
    )
    check(roundtrip_ok, "int_to_letters/letters_to_int roundtrip holds for n in 1..99")


# ---------------------------------------------------------------------------
# Test 16 – number_transform.py output unchanged after delegating to numbering.py
# ---------------------------------------------------------------------------

def test_number_transform_regression():
    print("\n[Test 16] number_transform – pad_number/number_to_letters/letters_to_number unchanged")
    nt = import_module(f"{ADDON_ID}.operators.number_transform")

    check(nt.pad_number("Cube9", 3) == "Cube009", "pad_number pads to width")
    check(nt.pad_number("Cube009", 0) == "Cube9", "pad_number width=0 strips leading zeros")
    check(nt.number_to_letters("Cube27", upper=True, separator="_") == "Cube_AA",
          "number_to_letters converts the digit run to base-26 letters, inserting a separator")
    check(nt.number_to_letters("CubeOnly", upper=False, separator="_") == "CubeOnly",
          "number_to_letters leaves the name unchanged when there is no digit run")
    check(nt.letters_to_number("Cube_AA", 3) == "Cube_027",
          "letters_to_number reverses number_to_letters")
    check(nt.letters_to_number("12345", 3) == "12345",
          "letters_to_number leaves the name unchanged when there is no letter run")


# ---------------------------------------------------------------------------
# Test 17 – renaming.numerate operator: explicit digits vs letters kwargs
# ---------------------------------------------------------------------------

def test_numerate_operator_digits_vs_letters():
    print("\n[Test 17] renaming.numerate – explicit operator kwargs override prefs (digits vs letters)")
    PREFIX = "T17_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    objs = [add_mesh_object(f"{PREFIX}Obj{i}") for i in range(3)]
    for obj in objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]

    scene_prop("renaming_object_types", "OBJECT")
    scene_prop("renaming_only_selection", True)
    bpy.ops.renaming.numerate(start_number=1, step=1, digits=3, use_letters=False)

    suffixes = sorted(o.name[-3:] for o in objs)
    check(suffixes == ["001", "002", "003"],
          f"Digits mode via explicit operator kwargs — got {[o.name for o in objs]}")

    purge_all_with_prefix(PREFIX)
    objs = [add_mesh_object(f"{PREFIX}Obj{i}") for i in range(3)]
    for obj in objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]

    bpy.ops.renaming.numerate(start_number=1, step=1, digits=3, use_letters=True, letters_upper=True)
    letters_got = sorted(o.name[-1] for o in objs)
    check(letters_got == ["A", "B", "C"],
          f"Letters mode via explicit operator kwargs — got {[o.name for o in objs]}")

    scene_prop("renaming_only_selection", False)
    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 18 – renaming.numerate per-owner counter reset still works in letters mode
# ---------------------------------------------------------------------------

def test_numerate_operator_per_object_type_reset_letters():
    print("\n[Test 18] renaming.numerate – per-owner counter resets in letters mode (shape keys)")
    PREFIX = "T18_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    owners = []
    for i in range(2):
        mesh = bpy.data.meshes.new(f"{PREFIX}SKMesh{i}")
        obj = bpy.data.objects.new(f"{PREFIX}SKHolder{i}", mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.shape_key_add(name="Basis")
        obj.shape_key_add(name="Key1")
        obj.shape_key_add(name="Key2")
        obj.select_set(True)
        owners.append(obj)
    bpy.context.view_layer.objects.active = owners[0]

    scene_prop("renaming_object_types", "SHAPEKEYS")
    scene_prop("renaming_only_selection", True)
    bpy.ops.renaming.numerate(start_number=1, step=1, digits=3, use_letters=True, letters_upper=True)

    for obj in owners:
        names = [k.name for k in obj.data.shape_keys.key_blocks]
        check(any(n.endswith("_A") for n in names),
              f"Counter restarts at 'A' for owner '{obj.name}' — got {names}")

    scene_prop("renaming_only_selection", False)
    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 19 – numerate_entity_name collision-avoidance unaffected by letters mode
# ---------------------------------------------------------------------------

def test_name_replace_letters_mode_collision_avoidance():
    print("\n[Test 19] name_replace + Numerate checkbox – collision avoidance still works in letters mode")
    PREFIX = "T19_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    existing = add_mesh_object(f"{PREFIX}bone_A")
    new_obj = add_mesh_object(f"{PREFIX}Fresh")
    existing.select_set(False)
    new_obj.select_set(True)
    bpy.context.view_layer.objects.active = new_obj

    addon_prefs = bpy.context.preferences.addons[ADDON_ID].preferences
    prev_use_letters = addon_prefs.numerate_use_letters
    addon_prefs.numerate_use_letters = True
    try:
        scene_prop("renaming_object_types", "OBJECT")
        scene_prop("renaming_only_selection", True)
        scene_prop("renaming_new_name", f"{PREFIX}bone")
        scene_prop("renaming_numerate", 1)
        scene_prop("renaming_use_enumerate", True)
        bpy.ops.renaming.name_replace()
    finally:
        addon_prefs.numerate_use_letters = prev_use_letters

    check(new_obj.name == f"{PREFIX}bone_B",
          f"Collision-avoidance search skipped the pre-existing '_A' name in letters mode — got '{new_obj.name}'")

    scene_prop("renaming_only_selection", False)
    scene_prop("renaming_use_enumerate", False)
    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Test 20 – @n variable respects the shared numerate_use_letters preference
# ---------------------------------------------------------------------------

def test_variable_replacer_letters_mode():
    print("\n[Test 20] @n variable respects numerate_use_letters and produces sequential letters")
    PREFIX = "T20_"
    purge_all_with_prefix(PREFIX)
    reset_scene_props()

    objs = [add_mesh_object(f"{PREFIX}Obj{i}") for i in range(3)]
    for obj in objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]

    addon_prefs = bpy.context.preferences.addons[ADDON_ID].preferences
    prev_use_letters = addon_prefs.numerate_use_letters
    prev_start = addon_prefs.numerate_start_number
    addon_prefs.numerate_use_letters = True
    addon_prefs.numerate_start_number = 1
    try:
        scene_prop("renaming_object_types", "OBJECT")
        scene_prop("renaming_only_selection", True)
        scene_prop("renaming_new_name", f"{PREFIX}obj_@n")
        bpy.ops.renaming.name_replace()
    finally:
        addon_prefs.numerate_use_letters = prev_use_letters
        addon_prefs.numerate_start_number = prev_start

    letters_got = sorted(o.name[-1] for o in objs)
    check(letters_got == ["A", "B", "C"],
          f"@n produced sequential letters across the renaming list — got {[o.name for o in objs]}")

    scene_prop("renaming_only_selection", False)
    purge_all_with_prefix(PREFIX)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if ADDON_ID is None:
        print("ERROR: simple_renaming addon not found.")
        print("       Loaded addons:", list(bpy.context.preferences.addons.keys()))
        sys.exit(1)

    print(f"Found addon as: '{ADDON_ID}'")
    # bpy.ops.wm.call_panel crashes in background mode — disable the popup.
    bpy.context.preferences.addons[ADDON_ID].preferences.renamingPanel_showPopup = False

    test_get_collection()
    test_get_owner_object_name_material()
    test_get_owner_object_name_shapekey()
    test_numerate_bones_unique()
    test_get_all_attributes()
    test_search_replace_static_pattern()
    test_bone_rename_updates_drivers()
    test_curves_object_type()
    test_selection_order_sort()
    test_selection_order_sort_bones()
    test_selection_order_respects_only_selected()
    test_material_follows_object_selection_order()
    test_name_replace_conflict_warning()
    test_trim_conflict_no_visible_change_still_warns()
    test_numbering_module_roundtrip()
    test_number_transform_regression()
    test_numerate_operator_digits_vs_letters()
    test_numerate_operator_per_object_type_reset_letters()
    test_name_replace_letters_mode_collision_avoidance()
    test_variable_replacer_letters_mode()

    print(f"\n{'='*50}")
    if failures:
        print(f"FAILED ({len(failures)} failures):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print(f"All 20 tests passed.")
        sys.exit(0)

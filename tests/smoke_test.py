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

    keys = [k.name for k in obj.data.shape_keys.key_blocks]
    check(all(k.startswith(f"{PREFIX}SKHolder_shape") for k in keys),
          f"Shape keys renamed using @o — got {keys}")

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

    for name in [f"{PREFIX}Cube_Low", f"{PREFIX}cube_low", f"{PREFIX}CUBE_LOW"]:
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

    print(f"\n{'='*50}")
    if failures:
        print(f"FAILED ({len(failures)} failures):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print(f"All 8 tests passed.")
        sys.exit(0)

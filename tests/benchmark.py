"""
Performance benchmark for simple_renaming operators.

Run headlessly:
    /path/to/blender --background --factory-startup --python tests/benchmark.py

Prints a timing table for each operator at three scene sizes (small / medium /
large).  Run on two branches and diff the output to compare before vs after.

Example output:
    Operator          |  100 ents |  500 ents | 1000 ents
    ------------------|-----------|-----------|----------
    name_replace      |   3.2 ms  |  14.7 ms  |  29.1 ms
    search_replace    |   2.8 ms  |  12.3 ms  |  24.6 ms
    ...
"""

import sys
import os
import time

import bpy
import addon_utils

# ---------------------------------------------------------------------------
# Addon loading (same logic as smoke_test.py)
# ---------------------------------------------------------------------------

_ADDON_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _find_addon_id():
    for key in bpy.context.preferences.addons.keys():
        if key == "simple_renaming" or key.endswith(".simple_renaming"):
            return key
    return None


def _load_addon():
    if _ADDON_PARENT not in sys.path:
        sys.path.insert(0, _ADDON_PARENT)
    addon_utils.enable("simple_renaming", default_set=True)
    return _find_addon_id()


ADDON_ID = _find_addon_id() or _load_addon()

if ADDON_ID is None:
    print("ERROR: simple_renaming not found.")
    sys.exit(1)

# Redirect Blender's stdout noise during benchmarking so timing rows print cleanly.
import io
_devnull = open(os.devnull, 'w')


prefs = bpy.context.preferences.addons[ADDON_ID].preferences
prefs.renamingPanel_showPopup = False   # prevent crash in background mode
prefs.debug_timing = False              # we handle timing here, not the operators


# ---------------------------------------------------------------------------
# Scene helpers
# ---------------------------------------------------------------------------

def purge_prefix(prefix):
    for ob in list(bpy.data.objects):
        if ob.name.startswith(prefix):
            bpy.data.objects.remove(ob, do_unlink=True)
    for me in list(bpy.data.meshes):
        if me.name.startswith(prefix):
            bpy.data.meshes.remove(me)
    for ma in list(bpy.data.materials):
        if ma.name.startswith(prefix):
            bpy.data.materials.remove(ma)
    for col in list(bpy.data.collections):
        if col.name.startswith(prefix):
            bpy.data.collections.remove(col)


def build_object_scene(n, prefix="BM_"):
    """Create n mesh objects spread across n//10 collections."""
    purge_prefix(prefix)
    collections = []
    for i in range(max(1, n // 10)):
        col = bpy.data.collections.new(f"{prefix}Col{i:03d}")
        bpy.context.scene.collection.children.link(col)
        collections.append(col)

    for i in range(n):
        mesh = bpy.data.meshes.new(f"{prefix}Mesh{i:04d}")
        obj = bpy.data.objects.new(f"{prefix}Obj{i:04d}", mesh)
        bpy.context.scene.collection.objects.link(obj)
        collections[i % len(collections)].objects.link(obj)
        mat = bpy.data.materials.new(f"{prefix}Mat{i:04d}")
        mesh.materials.append(mat)

    bpy.context.view_layer.objects.active = bpy.data.objects[f"{prefix}Obj0000"]
    return n


def set_scene_props(**kwargs):
    for k, v in kwargs.items():
        setattr(bpy.context.scene, k, v)


# ---------------------------------------------------------------------------
# Timing helper
# ---------------------------------------------------------------------------

def run_timed(fn):
    # Suppress Blender's mid-line status messages so rows print cleanly.
    old_stdout = sys.stdout
    sys.stdout = _devnull
    t0 = time.perf_counter()
    fn()
    ms = (time.perf_counter() - t0) * 1000
    sys.stdout = old_stdout
    return ms


# ---------------------------------------------------------------------------
# Individual benchmarks — each returns elapsed ms for a given entity count
# ---------------------------------------------------------------------------

def bench_name_replace(n):
    build_object_scene(n)
    set_scene_props(
        renaming_object_types='OBJECT',
        renaming_new_name="renamed",
        renaming_only_selection=False,
        renaming_use_enumerate=False,
    )
    ms = run_timed(bpy.ops.renaming.name_replace)
    purge_prefix("BM_")
    purge_prefix("renamed")
    return ms


def bench_name_replace_collection_var(n):
    """Tests getCollection cache via @c variable."""
    build_object_scene(n)
    set_scene_props(
        renaming_object_types='OBJECT',
        renaming_new_name="@c_item",
        renaming_only_selection=False,
        renaming_use_enumerate=False,
    )
    ms = run_timed(bpy.ops.renaming.name_replace)
    purge_prefix("BM_")
    for ob in list(bpy.data.objects):
        if "_item" in ob.name:
            bpy.data.objects.remove(ob, do_unlink=True)
    return ms


def bench_material_rename_owner_var(n):
    """Tests getOwnerObjectName cache via @o variable on materials."""
    build_object_scene(n)
    set_scene_props(
        renaming_object_types='MATERIAL',
        renaming_new_name="@o_mat",
        renaming_only_selection=False,
        renaming_use_enumerate=False,
    )
    ms = run_timed(bpy.ops.renaming.name_replace)
    purge_prefix("BM_")
    return ms


def bench_search_replace(n):
    build_object_scene(n)
    set_scene_props(
        renaming_object_types='OBJECT',
        renaming_search="BM_Obj",
        renaming_replace="Renamed",
        renaming_only_selection=False,
        renaming_matchcase=True,
        renaming_useRegex=False,
    )
    ms = run_timed(bpy.ops.renaming.search_replace)
    purge_prefix("BM_")
    purge_prefix("Renamed")
    return ms


def bench_add_suffix(n):
    build_object_scene(n)
    set_scene_props(
        renaming_object_types='OBJECT',
        renaming_suffix="_low",
        renaming_only_selection=False,
    )
    ms = run_timed(bpy.ops.renaming.add_suffix)
    purge_prefix("BM_")
    return ms


def bench_numerate(n):
    build_object_scene(n)
    set_scene_props(
        renaming_object_types='OBJECT',
        renaming_only_selection=False,
    )
    ms = run_timed(bpy.ops.renaming.numerate)
    purge_prefix("BM_")
    purge_prefix("BM_Obj")
    return ms


# ---------------------------------------------------------------------------
# Real-scene benchmark — runs when a .blend file was loaded before the script
# ---------------------------------------------------------------------------

def print_scene_stats():
    obj_count = len(bpy.data.objects)
    mesh_count = sum(1 for o in bpy.data.objects if o.type == 'MESH')
    mat_count = len(bpy.data.materials)
    col_count = len(bpy.data.collections)
    bone_count = sum(len(arm.bones) for arm in bpy.data.armatures)
    print(f"  Objects : {obj_count}  (meshes: {mesh_count})")
    print(f"  Materials: {mat_count}")
    print(f"  Collections: {col_count}")
    print(f"  Bones: {bone_count}")


def bench_real_op(label, setup_props, op, restore_fn=None):
    """Time a single operator on the currently loaded scene."""
    set_scene_props(renaming_only_selection=False, renaming_use_enumerate=False)
    set_scene_props(**setup_props)
    ms = run_timed(op)
    if restore_fn:
        restore_fn()
    return label, ms, len(bpy.data.objects)


def run_real_scene_benchmarks():
    filepath = bpy.data.filepath
    print(f"\n{'='*56}")
    print(f"Real-scene benchmark: {os.path.basename(filepath)}")
    print(f"{'='*56}")
    print_scene_stats()

    # Snapshot original names so we can restore after each op
    def snapshot():
        return {o.name: o for o in bpy.data.objects}

    def restore(snap):
        for orig_name, obj in snap.items():
            try:
                obj.name = orig_name
            except Exception:
                pass

    results = []

    # 1. name_replace plain
    snap = snapshot()
    n = len(bpy.data.objects)
    set_scene_props(renaming_object_types='OBJECT', renaming_new_name="bench_obj",
                    renaming_only_selection=False, renaming_use_enumerate=False)
    ms = run_timed(bpy.ops.renaming.name_replace)
    restore(snap)
    results.append(("name_replace (plain)", ms, n))

    # 2. name_replace with @c variable (exercises getCollection cache)
    snap = snapshot()
    set_scene_props(renaming_object_types='OBJECT', renaming_new_name="@c_bench",
                    renaming_only_selection=False, renaming_use_enumerate=False)
    ms = run_timed(bpy.ops.renaming.name_replace)
    restore(snap)
    results.append(("name_replace (@c var)", ms, n))

    # 3. material rename with @o variable (exercises getOwnerObjectName cache)
    mat_snap = {m.name: m for m in bpy.data.materials}
    n_mats = len(bpy.data.materials)
    set_scene_props(renaming_object_types='MATERIAL', renaming_new_name="@o_mat",
                    renaming_only_selection=False, renaming_use_enumerate=False)
    ms = run_timed(bpy.ops.renaming.name_replace)
    for orig_name, mat in mat_snap.items():
        try:
            mat.name = orig_name
        except Exception:
            pass
    results.append(("material rename (@o var)", ms, n_mats))

    # 4. search_replace (case-insensitive, no variables — static pattern path)
    snap = snapshot()
    n = len(bpy.data.objects)
    set_scene_props(renaming_object_types='OBJECT', renaming_search=".",
                    renaming_replace="_", renaming_only_selection=False,
                    renaming_matchcase=False, renaming_useRegex=False)
    ms = run_timed(bpy.ops.renaming.search_replace)
    restore(snap)
    results.append(("search_replace", ms, n))

    # 5. add_suffix
    snap = snapshot()
    set_scene_props(renaming_object_types='OBJECT', renaming_suffix="_bk",
                    renaming_only_selection=False)
    ms = run_timed(bpy.ops.renaming.add_suffix)
    restore(snap)
    results.append(("add_suffix", ms, n))

    # 6. numerate
    snap = snapshot()
    set_scene_props(renaming_object_types='OBJECT', renaming_only_selection=False)
    ms = run_timed(bpy.ops.renaming.numerate)
    restore(snap)
    results.append(("numerate", ms, n))

    COL2 = 26
    print(f"\n{'Operator':<{COL2}} | {'Time':>8} | {'ms/entity':>10} | {'Entities':>8}")
    print("-" * (COL2 + 36))
    for label, ms, count in results:
        per = ms / count if count else 0
        print(f"{label:<{COL2}} | {ms:>6.1f} ms | {per:>8.3f} ms | {count:>8}")
    print()


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

SIZES = [100, 500, 1000]

BENCHMARKS = [
    ("name_replace (plain)",     bench_name_replace),
    ("name_replace (@c var)",    bench_name_replace_collection_var),
    ("material rename (@o var)", bench_material_rename_owner_var),
    ("search_replace",           bench_search_replace),
    ("add_suffix",               bench_add_suffix),
    ("numerate",                 bench_numerate),
]

COL = 22
NUM_COL = 11


def fmt(ms):
    return f"{ms:6.1f} ms".center(NUM_COL)


if __name__ == "__main__":
    # ── Real-scene benchmark first — before warmup destroys scene objects ───
    if bpy.data.is_saved:
        run_real_scene_benchmarks()

    # Warmup: trigger any first-use Blender messages before the synthetic
    # table starts.
    bench_name_replace(10)

    # ── Synthetic scene benchmarks ──────────────────────────────────────────
    print(f"\n{'Operator':<{COL}}", end="")
    for n in SIZES:
        print(f"| {f'{n} ents':^{NUM_COL-1}}", end="")
    print()
    print("-" * (COL + len(SIZES) * (NUM_COL + 1)))

    for label, fn in BENCHMARKS:
        print(f"{label:<{COL}}", end="", flush=True)
        for n in SIZES:
            ms = fn(n)
            print(f"|{fmt(ms)}", end="", flush=True)
        print()

    print()

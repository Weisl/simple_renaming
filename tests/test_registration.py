"""
Registration / preference lifecycle tests for simple_renaming.

Run headlessly:
    /path/to/blender --background --factory-startup --python tests/test_registration.py

Covers the panel-related preference callbacks and disabling/re-enabling the
addon while the Prefix/Suffix panel is hidden. Kept separate from
test_smoke.py because it disables and re-enables the addon.
"""

import os
import sys

import addon_utils
import bpy

# tests/ -> simple_renaming/ -> extensions/  (the dir that *contains* the package)
_ADDON_SOURCE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _find_addon_id():
    for key in bpy.context.preferences.addons.keys():
        if key == "simple_renaming" or key.endswith(".simple_renaming"):
            return key
    return None


def _load_addon():
    if _ADDON_SOURCE not in sys.path:
        sys.path.insert(0, _ADDON_SOURCE)
    addon_utils.enable("simple_renaming", default_set=True)
    return _find_addon_id()


ADDON_ID = _find_addon_id() or _load_addon()

failures = []


def check(condition, label):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}")
        failures.append(label)


def prefs():
    return bpy.context.preferences.addons[ADDON_ID].preferences


def panels():
    mod = sys.modules[f"{ADDON_ID}.ui.renaming_panels"]
    return mod.VIEW3D_PT_tools_renaming_panel, mod.VIEW3D_PT_tools_type_suffix


def test_suffix_panel_toggle_is_idempotent():
    print("\n[Test 1] Prefix/Suffix panel toggle can be set to the same value twice")
    _, suffix = panels()
    try:
        prefs().renaming_show_suffix_prefix_panel = True
        prefs().renaming_show_suffix_prefix_panel = True
        check(suffix.is_registered, "Panel registered after showing it twice")
        prefs().renaming_show_suffix_prefix_panel = False
        prefs().renaming_show_suffix_prefix_panel = False
        check(not suffix.is_registered, "Panel unregistered after hiding it twice")
    except Exception as e:
        check(False, f"Toggling raised {type(e).__name__}: {e}")
    finally:
        prefs().renaming_show_suffix_prefix_panel = True


def test_category_change_keeps_hidden_panel_hidden():
    print("\n[Test 2] Changing the sidebar category doesn't re-show a hidden panel")
    main, suffix = panels()
    old_category = prefs().renaming_category
    try:
        prefs().renaming_show_suffix_prefix_panel = False
        prefs().renaming_category = "RegTestTab"
        check(main.is_registered and main.bl_category == "RegTestTab",
              f"Main panel moved to new tab — got '{main.bl_category}'")
        check(not suffix.is_registered, "Hidden Prefix/Suffix panel stays hidden")
        prefs().renaming_show_suffix_prefix_panel = True
        check(suffix.is_registered and suffix.bl_category == "RegTestTab",
              f"Re-shown Prefix/Suffix panel uses the new tab — got '{suffix.bl_category}'")
    finally:
        prefs().renaming_show_suffix_prefix_panel = True
        prefs().renaming_category = old_category


def test_disable_enable_with_hidden_panel():
    print("\n[Test 3] Disable and re-enable the addon while the Prefix/Suffix panel is hidden")
    prefs().renaming_show_suffix_prefix_panel = False
    module_name = ADDON_ID
    # addon_utils' default error handler only prints; re-raise so a failing
    # register/unregister actually fails the test.
    try:
        addon_utils.disable(module_name, default_set=False, handle_error=_raise)
        check(True, "Addon disabled without errors")
    except Exception as e:
        check(False, f"Disabling raised {type(e).__name__}: {e}")
        return

    try:
        addon_utils.enable(module_name, default_set=False, handle_error=_raise)
        check(module_name in bpy.context.preferences.addons, "Addon re-enabled without errors")
    except Exception as e:
        check(False, f"Re-enabling raised {type(e).__name__}: {e}")
        return

    main, suffix = panels()
    check(main.is_registered, "Main panel registered after re-enable")
    check(not suffix.is_registered, "Stored 'hide Prefix/Suffix panel' preference applied on enable")
    prefs().renaming_show_suffix_prefix_panel = True
    check(suffix.is_registered, "Prefix/Suffix panel can be shown again after re-enable")


def _raise(ex):
    raise ex


if __name__ == "__main__":
    if ADDON_ID is None:
        print("ERROR: simple_renaming addon not found.")
        sys.exit(1)
    print(f"Found addon as: '{ADDON_ID}'")

    test_suffix_panel_toggle_is_idempotent()
    test_category_change_keeps_hidden_panel_hidden()
    test_disable_enable_with_hidden_panel()

    print(f"\n{'=' * 50}")
    if failures:
        print(f"FAILED ({len(failures)} failures):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("All registration tests passed.")
    sys.exit(0)

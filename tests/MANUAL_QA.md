# Manual QA — Simple Renaming v2.1.11

Run this before tagging the release. Tick each box, and note the Blender
version next to any failure.

**Blender versions:** run every section on **4.2** (the minimum version) and **5.3** (the latest).
Run section 2 on **5.2** as well: Geometry Nodes modifier inputs are read one
way on 5.3 and another way on 5.2 and older (`get_geometry_nodes_input`).

**Clean profile:** start each run with
`tools/test_blender.sh --blender <path> --build --reset`, so your own add-ons
and keymaps don't affect the results.

---

## 1. Pre-flight

- [ ] `python tests/run_tests.py --blender <path>` passes on 4.2 and 5.3 ("All 21 tests passed.").
- [ ] CI `tests.yml` is green for the whole matrix (4.2 – 5.3).
- [ ] `blender --command extension validate .` reports no errors.
- [ ] The add-on enables with no errors in the console or the Info editor.
- [ ] Disable, then re-enable the add-on: no errors, and the Rename tab reappears in the N-panel.

## 2. New: Image Textures "Only Of Selected Objects" ([#259](https://github.com/Weisl/simple_renaming/issues/259))

Open `tests/manual_test_images.blend`. Its built-in `README_issue_259` text
lists which image belongs to which object. Open the N-panel, Rename tab, then set
**Target = Image Textures**, **Search = `IMG_`**, **Replace = `DONE_`**. Check the
results in Outliner > Blender File > Images, then press Ctrl+Z after each case.

### UI

- [ ] With Target = Image Textures, the panel shows **Only Of Selected Objects** and **Include Node Groups**.
- [ ] **Include Node Groups** is greyed out when Only Of Selected Objects is OFF.
- [ ] Neither option is shown for targets other than Image Textures (Include Node Groups) or targets outside the "of selected" list (Only Of Selected Objects), e.g. Collections or Node Groups.
- [ ] No Sorting section is shown for Image Textures (same as before).
- [ ] Open the Renaming Popup with its hotkey: both options are drawn there too, with no "Layout panels can not be used in this context" error.
- [ ] Hover tooltips read correctly for both options.

### Core cases (from the README in the .blend file)

- [ ] **Only Selected ON, Node Groups ON:** all 8 `SEL_*` images are renamed (Material, Material_InGroup, Displace, GN_Input, GN_Node, GN_InGroup, Empty, Camera). `IMG_Unselected` and `IMG_Unused` are unchanged.
- [ ] **Only Selected ON, Node Groups OFF:** same as above, except `IMG_Material_InGroup` and `IMG_GN_InGroup` are unchanged.
- [ ] **Only Selected OFF:** all 10 images are renamed, including `IMG_Unused` and the image of the unselected object.
- [ ] **Nothing selected, Only Selected ON:** nothing is renamed, with no error or traceback (check what message appears, if any).
- [ ] **Only `UNSEL_Cube` selected:** only `IMG_Unselected` is renamed.

### Every operator respects the filter

With Only Selected ON and Node Groups ON, each of these should change only the 8 `SEL_*` images:

- [ ] Search & Replace
- [ ] New Name / Rename (enumerate OFF): one image keeps the name, the rest get `.001`, `.002`…, and a collision warning is shown
- [ ] New Name / Rename (enumerate ON): numbered without collisions
- [ ] Add Prefix / Add Suffix
- [ ] Numerate
- [ ] Trim (start/end)
- [ ] Case transform (upper/lower/title…)
- [ ] Number transform
- [ ] Search & Select: no error with the Image target (it should not change the object selection)
- [ ] Ctrl+Z after each operator restores all image names in a single step

### Edge cases

- [ ] **Image shared by two selected objects.** Shift+D `SEL_Material` (the duplicate keeps the same material), select both, then Add Prefix `X_`. `IMG_Material` becomes `X_IMG_Material` once, not `X_X_IMG_Material`.
- [ ] **Same node group used twice.** Add a second group node using `MAT_Selected_NodeGroup` to `MAT_Selected`, then Add Prefix. The group's image gets the prefix once.
- [ ] **Edit Mode.** Tab into Edit Mode on `SEL_Material` and run Search & Replace. Its images are renamed, and you stay in Edit Mode.
- [ ] **World environment texture.** Add an Environment Texture to the World. With Only Selected ON, that image is **not** renamed (the World isn't an object, so this is expected). With Only Selected OFF, it is renamed.
- [ ] **Empty material slot or modifier without a texture.** Add an empty material slot and a Displace modifier with no texture to `SEL_Modifiers`. No errors.
- [ ] **Grease Pencil (optional).** A GP object whose material uses a fill/stroke image: that image is renamed when the object is selected.
- [ ] **Linked/library image (optional).** Images that can't be renamed show the usual warning, not a traceback.

### Behaviour change: check this on purpose

`Only Of Selected Objects` defaults to **ON**, and its value is shared with Materials, Data, etc.
Before this release, the Image target always renamed **all** images.

- [ ] Open a file saved with v2.1.10 (Target = Image Textures, no objects selected) and run Search & Replace. Result: nothing is renamed until Only Selected is turned OFF. Decide whether this is acceptable or should be mentioned in the changelog or release notes.
- [ ] Turning Only Selected OFF for Images also turns it OFF for Materials, and the reverse (the same property is shared). Confirm this is acceptable.

## 3. Regression: v2.1.10 fixes

- [ ] The Renaming Popup hotkey opens and draws Numerate Settings as a box, with no layout-panel error.
- [ ] Hide the Prefix/Suffix by Type panel in Preferences, then change the sidebar tab category. The panel stays hidden.
- [ ] With that panel hidden, disable the add-on, then enable it again. No error, and the add-on registers fully.
- [ ] The "hide Prefix/Suffix by Type panel" preference is applied right after Blender restarts.

## 4. Regression: other targets

- [ ] Run all the tests in the `ReadMe - Test Instructions` text in `tests/manual_test_scene.blend` (naming conflict warnings, #233).
- [ ] **Materials, Only Of Selected Objects ON:** only the materials of selected objects are renamed (unchanged by this release).
- [ ] **Objects:** Numerate with selection-order sorting still works.
- [ ] **Bones:** rename in Pose Mode and in Edit Mode.
- [ ] **Prefix/Suffix by Type panel:** add a type prefix to a mixed selection (mesh, camera, light, empty).
- [ ] **Variable replacer:** `@n`, `@f`, `@d` and `@i` still expand in New Name.

## 5. Packaging & release

- [ ] `version` in `blender_manifest.toml` is bumped to `2.1.11` (it is still `2.1.10`).
- [ ] The `CHANGELOG.md` heading for v2.1.11 has a release date and no longer says "Unreleased". Also update the "`master` is currently in sync with…" line.
- [ ] The built zip is named `simple_renaming_panel_2.1.11.zip`.
- [ ] The zip contains no `tests/`, `tools/`, `.github/`, `CHANGELOG.md` or `__pycache__/`.
- [ ] Install the built zip through Preferences > Get Extensions > Install from Disk on 4.2 and on 5.3. It enables cleanly.
- [ ] The release notes on the documentation site include the #259 entry.
- [ ] Merge `develop` into `master` and tag `v2.1.11`.

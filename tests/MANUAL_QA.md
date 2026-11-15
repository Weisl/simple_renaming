# Manual QA — Simple Renaming v2.1.10

Run this before tagging the release. Tick each box, and note the Blender
version next to any failure.

**Blender versions:** run every section on **5.3** (the latest). Blender 4.2
(the minimum version) is covered by the automated tests in CI only; no manual pass.
Run section 2 on **5.2** as well: Geometry Nodes modifier inputs are read one
way on 5.3 and another way on 5.2 and older (`get_geometry_nodes_input`).

**Clean profile:** start each run with
`tools/test_blender.sh --blender <path> --build --reset`, so your own add-ons
and keymaps don't affect the results.

---

## 1. Pre-flight

- [x] `python tests/run_tests.py --blender <path>` passes on 4.5, 5.0, 5.1, 5.2 and 5.3 ("All 23 tests passed.").
- [ ] CI `tests.yml` is green for the whole matrix (4.2 – 5.3).
- [x] `blender --factory-startup --command extension validate .` reports no errors.
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

Decided: consistency within the add-on matters more than matching v2.1.9, so both
points below are intended. The change is listed under "Changes" in the changelog
and release notes.

- [ ] Open a file saved with v2.1.9 (Target = Image Textures, no objects selected) and run Search & Replace. Result: nothing is renamed until Only Selected is turned OFF.
- [ ] Turning Only Selected OFF for Images also turns it OFF for Materials, and the reverse (the same property is shared).

## 3. Fixes: Search and Select regex ([#257](https://github.com/Weisl/simple_renaming/issues/257)) and bone sorting ([#258](https://github.com/Weisl/simple_renaming/issues/258))

### Search and Select (Target = Objects)

Add three objects named `a.b`, `axb` and `Cube`.

- [ ] **Use Regex ON**, Search = `a.b`: selects `a.b` and `axb`. Same result with Match Case ON (it is greyed out).
- [ ] **Use Regex OFF**, Search = `a.b`: selects only `a.b` (the `.` is literal), with Match Case ON and OFF.
- [ ] **Use Regex OFF**, Search = `cube`: selects `Cube` with Match Case OFF, nothing with Match Case ON.
- [ ] **Use Regex OFF**, Search = `(`: no "Invalid regular expression" error.
- [ ] **Use Regex ON**, Search = `(`: shows the "Invalid regular expression" error, no traceback.
- [ ] Search and Select on Bones (Pose and Edit Mode) still selects the matching bones.

### Bone sorting

Make an armature with 3–4 bones spread along X, created out of X order. Turn on **Sort Target Objects** and **Numerate**.

- [ ] **X Axis**, Edit Mode, New Name `Bone`: bones are numbered from −X to +X.
- [ ] Same in **Pose Mode** and in **Object Mode** (Only Selected OFF).
- [ ] **Reverse Sorting Order** flips the numbering for X, Y, Z and Selection.
- [ ] **Y Axis** and **Z Axis** sort along their axes.
- [ ] Rotate the armature object 180° around Z: the X order flips (sorting uses world space).
- [ ] **Only Selected ON** with a subset of bones selected: only those are renamed, in axis order.
- [ ] **Selection** sort with "Select in Renaming Order" still numbers bones in click order.

## 4. Fixes: renaming popup and panel preferences ([#260](https://github.com/Weisl/simple_renaming/issues/260), [#261](https://github.com/Weisl/simple_renaming/issues/261))

- [ ] The Renaming Popup hotkey opens and draws Numerate Settings as a box, with no layout-panel error.
- [ ] Hide the Prefix/Suffix by Type panel in Preferences, then change the sidebar tab category. The panel stays hidden.
- [ ] With that panel hidden, disable the add-on, then enable it again. No error, and the add-on registers fully.
- [ ] The "hide Prefix/Suffix by Type panel" preference is applied right after Blender restarts.

## 5. Regression: other targets

- [ ] Run all the tests in the `ReadMe - Test Instructions` text in `tests/manual_test_scene.blend` (naming conflict warnings, #233).
- [ ] **Materials, Only Of Selected Objects ON:** only the materials of selected objects are renamed (unchanged by this release).
- [ ] **Objects:** Numerate with selection-order sorting still works.
- [ ] **Bones:** rename in Pose Mode and in Edit Mode.
- [ ] **Prefix/Suffix by Type panel:** add a type prefix to a mixed selection (mesh, camera, light, empty).
- [ ] **Variable replacer:** `@n`, `@f`, `@d` and `@i` still expand in New Name.

## 6. Packaging & release

- [x] `version` in `blender_manifest.toml` is `2.1.10`.
- [x] The `CHANGELOG.md` heading for v2.1.10 has a release date and no longer says "Unreleased". Also update the "`master` is currently in sync with…" line.
- [ ] The built zip is named `simple_renaming_panel_2.1.10.zip`.
- [x] The zip contains no `tests/`, `tools/`, `.github/`, `CHANGELOG.md` or `__pycache__/`.
- [ ] Install the built zip through Preferences > Get Extensions > Install from Disk on 5.3. It enables cleanly.
- [ ] The release notes on the documentation site include the v2.1.10 entries (#257–#263).
- [ ] Merge `develop` into `master` and tag `v2.1.10`.

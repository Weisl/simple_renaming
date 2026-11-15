# Changelog

All notable changes to Simple Renaming are documented here. Dates are set
when a version is actually tagged/released.

Each version below mirrors the structure used on the
[documentation site's release notes page](https://weisl.github.io/simple_renaming/renaming_release_notes/):
a short summary of the release, followed by "Features", "Fixes", and similar
lists whose entries link back to their GitHub issue. New releases are added
as a new section above the previous one — existing entries are never
overwritten, so this file (like the docs page) accumulates the full release
history over time.

`master` is currently in sync with the latest release, v2.1.10 — add the next
`## Simple Renaming vX.Y.Z (Unreleased)` section here as new work lands.

## Simple Renaming v2.1.11 (Unreleased)

### Features

- Image Textures renaming now has an "Only Of Selected Objects" option. It limits renaming to images used by the selected objects: images in their materials and modifiers (Displace and other texture modifiers, Geometry Nodes inputs and nodes), images shown by image empties, and camera background images. An "Include Node Groups" toggle sets whether images inside nested node groups are renamed too. ([#259](https://github.com/Weisl/simple_renaming/issues/259))

## Simple Renaming v2.1.10 (2026-11-12)

Compatibility update for Blender 5.2 and 5.3, plus fixes to the renaming popup and panel preferences.

### Fixes

- The "Renaming Popup" hotkey no longer fails to draw with "Layout panels can not be used in this context"; the Numerate Settings section is shown as a box inside the popup. ([#260](https://github.com/Weisl/simple_renaming/issues/260))
- Changing the sidebar tab category no longer brings back a hidden Prefix/Suffix by Type panel. ([#261](https://github.com/Weisl/simple_renaming/issues/261))
- Disabling the add-on while the Prefix/Suffix by Type panel is hidden no longer raises an error and leaves the add-on half-registered. ([#261](https://github.com/Weisl/simple_renaming/issues/261))
- The "hide Prefix/Suffix by Type panel" preference is now applied when the add-on loads. ([#261](https://github.com/Weisl/simple_renaming/issues/261))

### Maintenance

- Tested against Blender 5.2 and 5.3; both added to the CI test matrix. ([#262](https://github.com/Weisl/simple_renaming/issues/262))
- The extension package no longer includes development files (tests, tools, CI config, changelog). ([#263](https://github.com/Weisl/simple_renaming/issues/263))
- Release zips are now named `simple_renaming_panel_<version>.zip`. ([#263](https://github.com/Weisl/simple_renaming/issues/263))

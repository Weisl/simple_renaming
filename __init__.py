'''
Copyright (C) 2017 Matthias Patscheider
patscheider.matthias@gmail.com

Created by Matthias Patscheider

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Simple Renaming Panel",
    "description": "This Addon offers the basic functionality of renaming a set of objects",
    "author": "Matthias Patscheider",
    "version": (1, 3, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tools ",
    "warning": "",
    "wiki_url": "https://github.com/Weisl/simple_renaming_panel",
    "tracker_url": "https://github.com/Weisl/simple_renaming_panel/issues",
    "support": "COMMUNITY",
    "category": "Scene"
}

# TODO: Create Properties group for add suffix prefix type
# TODO: add List Of Textures
# TODO: Wait for asset manager and otherwise import Auto updater again
# TODO: Alt+N for quick rename
# TODO: Blendshapes
# DONE: The first one is to keep the mode (edit, pose, etc) after renaming, because if you are switching in objet mode an pose mode all the time, the workflow become a bit slow, especialy in rigging process. I think if yo make a variable before with the process with the mode avaible, you can mantain the mode after renaming... but you know more than me XD
# DONE: Regex
# DONE: add Preferences
# DONE: add Actions
# DONE: Split to multifile
# DONE: And the second one is have the posibiliti to turn off the popup message after renaming, they are a bit annoying when you have to renamin diferent selections.


# support reloading sub-modules
if "bpy" in locals():
    import importlib
    importlib.reload(addon_preferenecs)
    importlib.reload(renaming_operators)
    importlib.reload(renaming_popup)
    importlib.reload(renaming_utilities)
    importlib.reload(renaming_panels)
    importlib.reload(renaming_sufPre_operators)
else:
    from . import addon_preferenecs
    from . import renaming_operators
    from . import renaming_popup
    from . import renaming_utilities
    from . import renaming_panels
    from . import renaming_sufPre_operators

import bpy

from bpy.props import (
    BoolProperty,
    IntProperty,
    EnumProperty,
    StringProperty,
    FloatVectorProperty,
    PointerProperty,
    CollectionProperty,
)
from .renaming_utilities import RENAMING_MESSAGES



classes = (
    addon_preferenecs.TEMPLATE_OT_add_hotkey,
    addon_preferenecs.VIEW3D_OT_renaming_preferences,
    renaming_panels.VIEW3D_PT_tools_renaming_panel,
    renaming_panels.VIEW3D_PT_tools_type_suffix,
    renaming_popup.VIEW3D_OT_renaming_popup,
    renaming_operators.VIEW3D_OT_add_suffix,
    renaming_operators.VIEW3D_OT_add_prefix,
    renaming_operators.VIEW3D_OT_search_and_replace,
    renaming_operators.VIEW3D_OT_renaming_numerate,
    renaming_operators.VIEW3D_OT_trim_string,
    renaming_operators.VIEW3D_OT_use_objectname_for_data,
    renaming_operators.VIEW3D_OT_replace_name,
    renaming_sufPre_operators.VIEW3D_OT_add_type_suf_pre,
)

def menu_add_suffix(self, context):
    self.layout.operator(VIEW3D_OT_add_suffix.bl_idname)  # or YourClass.bl_idname


enumObjectTypes = [('EMPTY', "", "Rename empty objects", 'OUTLINER_OB_EMPTY', 1),
                   ('MESH', "", "Rename mesh objects", 'OUTLINER_OB_MESH', 2),
                   ('CAMERA', "", "Rename Camera objects", 'OUTLINER_OB_CAMERA', 4),
                   ('LIGHT', "", "Rename light objects", 'OUTLINER_OB_LIGHT', 8),
                   ('ARMATURE', "", "Rename armature objects", 'OUTLINER_OB_ARMATURE', 16),
                   ('LATTICE', "", "Rename lattice objects", 'OUTLINER_OB_LATTICE', 32),
                   ('CURVE', "", "Rename curve objects", 'OUTLINER_OB_CURVE', 64),
                   ('SURFACE', "", "Rename surface objects", 'OUTLINER_OB_SURFACE', 128),
                   ('TEXT', "", "Rename text objects", 'OUTLINER_OB_FONT', 256),
                   ('GPENCIL', "", "Rename greace pencil objects", 'OUTLINER_OB_GREASEPENCIL', 512),
                   ('METABALL', "", "Rename metaball objects", 'OUTLINER_OB_META', 1024),
                   ('SPEAKER', "", "Rename empty speakers", 'OUTLINER_OB_SPEAKER', 2048),
                   ('LIGHT_PROBE', "", "Rename mesh lightpropes", 'OUTLINER_OB_LIGHTPROBE', 4096)
                   ]

enumObjectTypesAdd = [('SPEAKER', "", "Rename empty speakers", 'OUTLINER_OB_SPEAKER', 1),
                   ('LIGHT_PROBE', "", "Rename mesh lightpropes", 'OUTLINER_OB_LIGHTPROBE', 2)]

enumObjectTypesExt = [('EMPTY', "", "Rename empty objects", 'OUTLINER_OB_EMPTY', 1),
                      ('MESH', "", "Rename mesh objects", 'OUTLINER_OB_MESH', 2),
                      ('CAMERA', "", "Rename Camera objects", 'OUTLINER_OB_CAMERA', 4),
                      ('LIGHT', "", "Rename light objects", 'OUTLINER_OB_LIGHT', 8),
                      ('ARMATURE', "", "Rename armature objects", 'OUTLINER_OB_ARMATURE', 16),
                      ('LATTICE', "", "Rename lattice objects", 'OUTLINER_OB_LATTICE', 32),
                      ('CURVE', "", "Rename curve objects", 'OUTLINER_OB_CURVE', 64),
                      ('SURFACE', "", "Rename surface objects", 'OUTLINER_OB_SURFACE', 128),
                      ('TEXT', "", "Rename text objects", 'OUTLINER_OB_FONT', 256),
                      ('GPENCIL', "", "Rename greace pencil objects", 'OUTLINER_OB_GREASEPENCIL', 512),
                      ('METABALL', "", "Rename metaball objects", 'OUTLINER_OB_META', 2048),
                      ('COLLECTION', "", "Rename collections", 'GROUP', 4096),
                      ('BONE', "", "", 'BONE_DATA', 8192), ]

def register():
    # bpy.types.INFO_MT_mesh_add.append(menu_add_suffix)
    # IDStore = bpy.types.
    IDStore = bpy.types.Scene
    IDStore.renaming_sufpre_type = EnumProperty(
        name="Suffix or Prefix by Type",
        items=(('PRE', "Prefix", "prefix"),
               ('SUF', "Suffix", "suffix"),),
        description="Add Prefix or Suffix to type",
        default = 'SUF'
    )

    IDStore.renaming_object_types = EnumProperty(
        name="Renaming Objects",
        items=(('OBJECT', "Object", "Scene Objects"),
               #('ADDOBJECTS', "Objects (additional)","Scene Objects"),
               ('MATERIAL', "Material", "Materials"),
               ('IMAGE', "Image Textures", "Image Textures"),
               ('DATA', "Data", "Object Data"),
               ('BONE', "Bone", "Bones"),
               ('COLLECTION', "Collection", "Rename collections"),
               ('ACTIONS', "Actions", "Rename Actions"),
               ('SHAPEKEYS',"Shape Keys", "Rename shape keys")
               #('VERTEXGROUPS',"Vertex Groups", "Rename vertex groups")
               # ('UVMaps')
               # ('FACEMAPS')
               # ('PARTICLESYSTEM')
               ),
        description="Which kind of object to rename",
    )

    # IDStore.renaming_object_types_specified = EnumProperty(name="Object Types",items=enumObjectTypes,description="Which kind of object to export",options={'ENUM_FLAG'}, default= {'CURVE','LATTICE','SURFACE','METABALL','MESH','ARMATURE','LIGHT','CAMERA','EMPTY'})
    IDStore.renaming_object_types_specified = EnumProperty(name="Object Types",
                                                           items=enumObjectTypes,
                                                           description="Which kind of object to rename",
                                                           options={'ENUM_FLAG'},
                                                           default={'CURVE', 'LATTICE', 'SURFACE', 'METABALL', 'MESH',
                                                                    'ARMATURE', 'LIGHT', 'CAMERA', 'EMPTY', 'GPENCIL',
                                                                    'TEXT', 'SPEAKER', 'LIGHT_PROBE'}
                                                           )

    # IDStore.renaming_object_addtypes_specified = EnumProperty(name="Additional Object Types",
    #                                                        items=enumObjectTypesAdd,
    #                                                        description="Which kind of object to rename",
    #                                                        options={'ENUM_FLAG'},
    #                                                        default={'SPEAKER', 'LIGHT_PROBE'}
    #                                                        )


    IDStore.renaming_newName = StringProperty(name="New Name", default='')
    IDStore.renaming_search = StringProperty(name='Search', default='')
    IDStore.renaming_replace = StringProperty(name='Replace', default='')
    IDStore.renaming_suffix = StringProperty(name="Suffix", default='')
    IDStore.renaming_prefix = StringProperty(name="Prefix", default='')
    IDStore.renaming_only_selection = BoolProperty(
        name="Selected Objects",
        description="Rename Selected Objects",
        default=True,
    )

    IDStore.renaming_matchcase = BoolProperty(
        name="Match Case",
        description="",
        default=True,
    )
    IDStore.renaming_useRegex = BoolProperty(
        name="Use Regex",
        description="",
        default=False,
    )

    IDStore.renaming_base_numerate = IntProperty(name="Step Size", default=1)
    IDStore.renaming_digits_numerate = IntProperty(name="Number Length", default=3)
    IDStore.renaming_cut_size = IntProperty(name="Trim Size", default=3)
    IDStore.renaming_messages = RENAMING_MESSAGES()

    ############## Type Suffix Prefix ########################################
    IDStore.type_pre_sub_only_selection = BoolProperty(
        name="Selected Objects",
        description="Rename Selected Objects",
        default=True,
    )

    IDStore.renaming_sufpre_types_specified = EnumProperty(name="Object Types",
                                                           items=enumObjectTypesExt,
                                                           description="Which kind of object to rename",
                                                           options={'ENUM_FLAG'},
                                                           default={'CURVE', 'LATTICE', 'SURFACE', 'METABALL', 'MESH',
                                                                    'ARMATURE', 'LIGHT', 'CAMERA', 'EMPTY', 'GPENCIL',
                                                                    'TEXT', 'BONE', 'COLLECTION'}
                                                           )

    IDStore.renaming_sufpre_material = StringProperty(name='Material', default='')
    IDStore.renaming_sufpre_geometry = StringProperty(name='Geometry', default='')
    IDStore.renaming_sufpre_empty = StringProperty(name="Empty", default='')
    IDStore.renaming_sufpre_group = StringProperty(name="Group", default='')
    IDStore.renaming_sufpre_curve = StringProperty(name="Curve", default='')
    IDStore.renaming_sufpre_armature = StringProperty(name="Armature", default='')
    IDStore.renaming_sufpre_lattice = StringProperty(name="Lattice", default='')
    IDStore.renaming_sufpre_data = StringProperty(name="Data", default='')
    IDStore.renaming_sufpre_data_02 = StringProperty(name="Data = Objectname + ", default='')
    IDStore.renaming_sufpre_surfaces = StringProperty(name="Surfaces", default='')
    IDStore.renaming_sufpre_cameras = StringProperty(name="Cameras", default='')
    IDStore.renaming_sufpre_lights = StringProperty(name="Lights", default='')
    IDStore.renaming_sufpre_collection = StringProperty(name="Collections", default='')
    IDStore.renaming_sufpre_text = StringProperty(name="Text", default='')
    IDStore.renaming_sufpre_gpencil = StringProperty(name="Grease Pencil", default='')
    IDStore.renaming_sufpre_metaball = StringProperty(name="Metaballs", default='')
    IDStore.renaming_sufpre_bone = StringProperty(name="Bones", default='')
    IDStore.renaming_sufpre_speakers = StringProperty(name="Speakers", default='')
    IDStore.renaming_sufpre_lightprops = StringProperty(name="LightProps", default='')

    from .addon_preferenecs import add_hotkey
    add_hotkey()

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():

    IDStore = bpy.types.Scene
    del IDStore.renaming_search
    del IDStore.renaming_newName
    del IDStore.renaming_object_types
    del IDStore.renaming_sufpre_type
    del IDStore.renaming_replace
    del IDStore.renaming_suffix
    del IDStore.renaming_prefix
    del IDStore.renaming_only_selection
    del IDStore.renaming_base_numerate
    del IDStore.renaming_digits_numerate
    del IDStore.renaming_cut_size
    del IDStore.renaming_sufpre_material
    del IDStore.renaming_sufpre_geometry
    del IDStore.renaming_sufpre_empty
    del IDStore.renaming_sufpre_group
    del IDStore.renaming_sufpre_curve
    del IDStore.renaming_sufpre_armature
    del IDStore.renaming_sufpre_lattice
    del IDStore.renaming_sufpre_data
    del IDStore.renaming_sufpre_data_02

    del IDStore.renaming_sufpre_lights
    del IDStore.renaming_sufpre_cameras
    del IDStore.renaming_sufpre_surfaces
    del IDStore.renaming_sufpre_bone
    del IDStore.renaming_sufpre_collection
    del IDStore.renaming_object_types_specified
    del IDStore.renaming_sufpre_speakers
    del IDStore.renaming_sufpre_lightprops

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    from .addon_preferenecs import remove_hotkey
    remove_hotkey()


if __name__ == "__main__":
    register()

# import bpy
# filename = "G:/GitHub/mp_simple_renaming_panel/simple_renaming_panel.py"
# exec(compile(open(filename).read(), filename, 'exec'))

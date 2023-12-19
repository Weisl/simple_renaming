import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    IntProperty,
)

from bpy.app.handlers import persistent

from . import add_pre_suffix
from . import name_from_data
from . import name_replace
from . import numerate
from . import search_replace
from . import search_select
from . import trim_string
from .renaming_utilities import update_selection_order

enumObjectTypes = [('EMPTY', "", "Rename empty objects", 'OUTLINER_OB_EMPTY', 1),
                   ('MESH', "", "Rename mesh objects", 'OUTLINER_OB_MESH', 2),
                   ('CAMERA', "", "Rename Camera objects", 'OUTLINER_OB_CAMERA', 4),
                   ('LIGHT', "", "Rename light objects", 'OUTLINER_OB_LIGHT', 8),
                   ('ARMATURE', "", "Rename armature objects", 'OUTLINER_OB_ARMATURE', 16),
                   ('LATTICE', "", "Rename lattice objects", 'OUTLINER_OB_LATTICE', 32),
                   ('CURVE', "", "Rename curve objects", 'OUTLINER_OB_CURVE', 64),
                   ('SURFACE', "", "Rename surface objects", 'OUTLINER_OB_SURFACE', 128),
                   ('FONT', "", "Rename font objects", 'OUTLINER_OB_FONT', 256),
                   ('GPENCIL', "", "Rename greace pencil objects", 'OUTLINER_OB_GREASEPENCIL', 512),
                   ('META', "", "Rename metaball objects", 'OUTLINER_OB_META', 1024),
                   ('SPEAKER', "", "Rename empty speakers", 'OUTLINER_OB_SPEAKER', 2048),
                   ('LIGHT_PROBE', "", "Rename mesh lightpropes", 'OUTLINER_OB_LIGHTPROBE', 4096),
                   ('VOLUME', "", "Rename mesh volumes", 'OUTLINER_OB_VOLUME', 8192)]

enumObjectTypesAdd = [('SPEAKER', "", "Rename empty speakers", 'OUTLINER_OB_SPEAKER', 1),
                      ('LIGHT_PROBE', "", "Rename mesh lightpropes", 'OUTLINER_OB_LIGHTPROBE', 2)]

prefixSuffixItems = [('PRE', "Prefix", "prefix"),
                     ('SUF', "Suffix", "suffix")
                     ]

renamingEntitiesItems = [('OBJECT', "Object", "Scene Objects"),
                         ('MATERIAL', "Material", "Materials"),
                         ('COLLECTION', "Collection", "Rename collections"),
                         None,
                         ('DATA', "Data", "Object Data"),
                         None,
                         ('BONE', "Bone", "Bones"),
                         ('IMAGE', "Image Textures", "Image Textures"),
                         None,
                         ('MODIFIERS', "Modifiers", "Rename Modifiers"),
                         ('SHAPEKEYS', "Shape Keys", "Rename shape keys"),
                         None,
                         ('ATTRIBUTES', "Attributes", "Rename attributes"),
                         ('COLORATTRIBUTES', "Color Attributes", "Rename color attributes"),
                         ('UVMAPS', "UV Maps", "Rename vertex groups"),
                         ('VERTEXGROUPS', "Vertex Groups", "Rename vertex groups"),
                         None,
                         ('ACTIONS', "Actions", "Rename Actions"),
                         None,
                         ('PARTICLESYSTEM', "Particle Systems", "Rename particle systems"),
                         ('PARTICLESETTINGS', "Particle Settings", "Rename particle settings"),
                         ]

classes = (
    search_select.VIEW3D_OT_search_and_select,
    search_replace.VIEW3D_OT_search_and_replace,
    name_replace.VIEW3D_OT_replace_name,
    trim_string.VIEW3D_OT_trim_string,
    add_pre_suffix.VIEW3D_OT_add_suffix,
    add_pre_suffix.VIEW3D_OT_add_prefix,
    numerate.VIEW3D_OT_renaming_numerate,
    name_from_data.VIEW3D_OT_use_objectname_for_data,
)

enum_sort_items = [('X', "X Axis", "Sort the object based on the X axis."),
                   ('Y', "Y Axis", "Sort the object based on the Y axis."),
                   ('Z', "Z Axis", "Sort the object based on the Z axis."),
                   ('SELECTION', "Selection", "Sort the objects based on the selection order"), ]


# persistent is needed for handler to work in addons https://docs.blender.org/api/current/bpy.app.handlers.html
@persistent
def PostChange(scene):
    if bpy.context.mode != "OBJECT":
        return

    # The any() function returns True if any element of an iterable is True. If not, it returns False.
    is_selection_update = any(
        not u.is_updated_geometry
        and not u.is_updated_transform
        and not u.is_updated_shading
        for u in bpy.context.view_layer.depsgraph.updates
    )
    if is_selection_update:
        update_selection_order()


def register():
    IDStore = bpy.types.Scene

    IDStore.renaming_sufpre_type = EnumProperty(name="Suffix or Prefix by Type",
                                                items=prefixSuffixItems,
                                                description="Add Prefix or Suffix to type",
                                                default='SUF'
                                                )

    IDStore.renaming_object_types = EnumProperty(name="Renaming Objects",
                                                 items=renamingEntitiesItems,
                                                 description="Which kind of object to rename",
                                                 )

    IDStore.renaming_object_types_specified = EnumProperty(name="Object Types",
                                                           items=enumObjectTypes,
                                                           description="Which kind of object to rename",
                                                           options={'ENUM_FLAG'},
                                                           default={'CURVE', 'LATTICE', 'SURFACE', 'MESH',
                                                                    'ARMATURE', 'LIGHT', 'CAMERA', 'EMPTY', 'GPENCIL',
                                                                    'FONT', 'SPEAKER', 'LIGHT_PROBE', 'VOLUME'}
                                                           )

    IDStore.renaming_sort_enum = EnumProperty(
        name="Sort by",
        description="Sort Objects based on following attribute",
        items=enum_sort_items,
        default='X',  # Set a default value
    )

    IDStore.renaming_newName = StringProperty(name="New Name", default='')
    IDStore.renaming_search = StringProperty(name='Search', default='')
    IDStore.renaming_replace = StringProperty(name='Replace', default='')
    IDStore.renaming_suffix = StringProperty(name="Suffix", default='')
    IDStore.renaming_prefix = StringProperty(name="Prefix", default='')
    IDStore.renaming_numerate = StringProperty(name="Numerate", default='###')

    IDStore.renaming_sorting = bpy.props.BoolProperty(
        name="Sort Target Objects",
        description="Sort the entries for renaming",
        default=False,
    )

    IDStore.renaming_only_selection = BoolProperty(name="Selected Objects", description="Rename Selected Objects",
                                                   default=True)

    IDStore.renaming_matchcase = BoolProperty(name="Match Case", description="", default=True)
    IDStore.renaming_useRegex = BoolProperty(name="Use Regex", description="", default=False)
    IDStore.renaming_usenumerate = BoolProperty(name="Numerate",
                                                description="Enable and Disable the numeration of objects. This can be especially useful in combination with the custom numberation variable @n",
                                                default=True,
                                                )
    IDStore.renaming_base_numerate = IntProperty(name="Step Size", default=1)
    IDStore.renaming_start_number = IntProperty(name="Step Size", default=1)
    IDStore.renaming_digits_numerate = IntProperty(name="Number Length", default=3)
    IDStore.renaming_cut_size = IntProperty(name="Trim Size", default=3)

    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.app.handlers.depsgraph_update_post.append(PostChange)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

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

    bpy.app.handlers.depsgraph_update_post.remove(PostChange)

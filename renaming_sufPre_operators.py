import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
)

from .renaming_utilities import callRenamingPopup
from .renaming_proFeatures import tChange

class VIEW3D_OT_add_type_suf_pre(bpy.types.Operator):
    """Add Type Suffix"""
    bl_idname = "renaming.add_sufpre_by_type"
    bl_label = "Add Type Suffix or Prefix"
    bl_description = "Adds the above defined Suffixes or Prefixes to all objects in your scene"
    bl_options = {'REGISTER', 'UNDO'}

    option: StringProperty()

    def getSelectionAll(self):

        context = self.context
        useSelection = context.scene.type_pre_sub_only_selection

        if useSelection:
            return context.selected_objects.copy()
        else:
            return bpy.data.objects

    def renameSufPre(self, objList, preSuf='', objectType='', icon=''):
        context = self.context
        wm = context.scene

        switchSufPre = wm.renaming_sufpre_type  # either use pre of suffix

        if preSuf is not '':
            for ent in objList:
                if hasattr(ent, 'name'):
                    oldName = ent.name
                    nameIsNew = True

                    if switchSufPre == 'SUF':
                        if ent.name.endswith(preSuf) == False:
                            newName = self.sufpreAdd(context, ent, preSuf)
                        else:
                            nameIsNew = False
                    else:
                        if ent.name.startswith(preSuf) == False:
                            newName = self.sufpreAdd(context, ent, preSuf)
                        else:
                            nameIsNew = False

                    if nameIsNew == True:
                        ent.name = newName
                        wm.renaming_messages.addMessage(oldName, ent.name, objectType, icon)
                else:
                    # wm.renaming_messages.addMessage(oldName, ent.name, objectType, 'OUTLINER_OB_EMPTY')
                    pass

    def empty(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'EMPTY':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_empty, objectType='EMPTY', icon='OUTLINER_OB_EMPTY')
        return

    def mesh(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'MESH':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_geometry, objectType='MESH', icon='OUTLINER_OB_MESH')
        return

    def material(self):
        context = self.context
        wm = context.scene
        objList = []

        if wm.type_pre_sub_only_selection:
            for obj in context.selected_objects:
                for mat in obj.material_slots:
                    if mat is not None and mat.name != '':
                        objList.append(bpy.data.materials[mat.name])
        else:
            objList = list(bpy.data.materials)

        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_material, objectType='MATERIAL', icon='MATERIAL')
        return

    def speakers(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'SPEAKER':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_speakers, objectType='SPEAKER', icon='OUTLINER_OB_SPEAKER')
        return

    def lightprops(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'LIGHT_PROBE':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_lightprops, objectType='LIGHT_PROBE',
                          icon='OUTLINER_OB_LIGHTPROBE')
        return

    def data(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            objList.append(obj.data)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_data, objectType='DATA', icon='FILE_BLANK')
        return

    def camera(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'CAMERA':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_cameras, objectType='CAMERA', icon='OUTLINER_OB_CAMERA')
        return

    def light(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'LIGHT':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_lights, objectType='LIGHT', icon='LIGHT')
        return

    def armature(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'ARMATURE':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_armature, objectType='ARMATURE',
                          icon='OUTLINER_OB_ARMATURE')
        return

    def lattice(self):

        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'LATTICE':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_lattice, objectType='LATTICE', icon='OUTLINER_OB_LATTICE')
        return

    def curve(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'CURVE':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_curve, objectType='CURVE', icon='OUTLINER_OB_CURVE')
        return

    def surface(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'SURFACE':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_surfaces, objectType='SURFACE', icon='OUTLINER_OB_SURFACE')
        return

    def text(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'FONT':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_text, objectType='FONT', icon='OUTLINER_OB_FONT')
        return

    def gpencil(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'GPENCIL':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_gpencil, objectType='GPENCIL',
                          icon='OUTLINER_OB_GREASEPENCIL')
        return

    def metaball(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'META':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_metaball, objectType='META', icon='OUTLINER_OB_META')
        return

    def collection(self):
        context = self.context
        wm = context.scene
        objList = []

        for col in bpy.data.collections:
            objList.append(col)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_collection, objectType='COLLECTION', icon='GROUP')
        return

    def bone(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'ARMATURE':
                for bone in obj.data.bones:
                    objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_bone, objectType='BONE', icon='BONE_DATA')
        return

    def all(self):
        self.empty()
        self.mesh()
        self.camera()
        self.light()
        self.armature()
        self.lattice()
        self.curve()
        self.surface()
        self.text()
        self.gpencil()
        self.metaball()
        self.collection()
        self.bone()
        self.material()
        self.data()

    def errorMsg(self):
        pass

    def switch_type(self, argument):
        context = self.context
        selection = context.selected_objects
        all = bpy.data.objects

        switcher = {
            1: 'empty',
            2: 'mesh',
            3: 'camera',
            4: 'light',
            5: 'armature',
            6: 'lattice',
            7: 'curve',
            8: 'surface',
            9: 'text',
            10: 'gpencil',
            11: 'metaball',
            12: 'collection',
            13: 'bone',
            14: 'material',
            15: 'data',
            16: 'all',
            # 17: 'actions',
        }

        method = getattr(self, argument, lambda: "Invalid month")
        return method()

    def main(self, context, objectList, isSuffix, stringExtension):
        pass

    def execute(self, context):
        self.context = context

        wm = context.scene
        self.switch_type(self.option)

        callRenamingPopup(context)
        return {'FINISHED'}

    def sufpreAdd(self, context, obj, sufpreName):
        wm = context.scene

        nName = obj.name
        if wm.renaming_sufpre_type == 'SUF':
            nName = nName + sufpreName
        else:
            nName = sufpreName + nName

        if nName not in bpy.data.objects:
            obj.name = nName
            return nName
        else:
            i = 1
            while (nName in bpy.data.objects):
                if wm.renaming_sufpre_type == 'SUF':
                    nName = obj.name + "_" + str(i) + sufpreName
                else:
                    nName = sufpreName + obj.name + "_" + str(i)
                i = i + 1

        obj.name = nName
        return nName


classes = (
    VIEW3D_OT_add_type_suf_pre,
)

enumPresetItems = [('FILE', "File", "", '', 1),
                   ('OBJECT', "Object", "", '', 2),
                   ('HIGH', "High", "", '', 4),
                   ('LOW', "Low", "", '', 8),
                   ('CAGE', "Cage", "", '', 16),
                   ('DATE', "Date", "", '', 32),
                   ('TIME', "Time", "", '', 128),
                   ('TYPE', "Type", "", '', 1024),
                   ('PARENT', "Parent", "", '', 2048),
                   ('ACTIVE', "Active", "", '', 4096),
                   ('USER1', "User1", "", '', 8192),
                   ('USER2', "User2", "", '', 256),
                   ('USER3', "User3", "", '', 512),
                   ('NUMBER', "Number", "", '', 1024),
                   ]

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
    IDStore = bpy.types.Scene

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

    IDStore.renaming_inputContext = StringProperty(name="LightProps", default='')

    # Pro Features
    IDStore.renaming_presetNaming = EnumProperty(name="Object Types",
                                                 items=enumPresetItems,
                                                 description="Which kind of object to rename",
                                                 update=tChange
                                                 )

    IDStore.renaming_presetNaming1 = EnumProperty(name="Object Types",
                                                  items=enumPresetItems,
                                                  description="Which kind of object to rename",
                                                  update=tChange
                                                  )

    IDStore.renaming_presetNaming2 = EnumProperty(name="Object Types",
                                                  items=enumPresetItems,
                                                  description="Which kind of object to rename",
                                                  update=tChange
                                                  )

    IDStore.renaming_presetNaming3 = EnumProperty(name="Object Types",
                                                  items=enumPresetItems,
                                                  description="Which kind of object to rename",
                                                  update=tChange
                                                  )

    IDStore.renaming_presetNaming4 = EnumProperty(name="Object Types",
                                                  items=enumPresetItems,
                                                  description="Which kind of object to rename",
                                                  update=tChange
                                                  )

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    IDStore = bpy.types.Scene

    del IDStore.renaming_sufpre_material
    del IDStore.renaming_sufpre_geometry
    del IDStore.renaming_sufpre_empty
    del IDStore.renaming_sufpre_group
    del IDStore.renaming_sufpre_curve
    del IDStore.renaming_sufpre_armature
    del IDStore.renaming_sufpre_lattice
    del IDStore.renaming_sufpre_data
    del IDStore.renaming_sufpre_data_02
    del IDStore.renaming_start_number

    del IDStore.renaming_sufpre_lights
    del IDStore.renaming_sufpre_cameras
    del IDStore.renaming_sufpre_surfaces
    del IDStore.renaming_sufpre_bone
    del IDStore.renaming_sufpre_collection
    del IDStore.renaming_object_types_specified
    del IDStore.renaming_sufpre_speakers
    del IDStore.renaming_sufpre_lightprops
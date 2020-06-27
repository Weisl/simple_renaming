import bpy
from bpy.props import (
    StringProperty,
)

from .renaming_utilities import callRenamingPopup


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

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
    "version": (1, 2, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tools ",
    "warning": "",
    "wiki_url": "https://github.com/Weisl/simple_renaming_panel",
    "tracker_url": "https://github.com/Weisl/simple_renaming_panel/issues",
    "support": "COMMUNITY",
    "category": "Scene"
    }

### Simple renaming panel
#DONE: Only affect certain mesh type Lights/Empties ....
#DONE: Implement Text Type
#DONE: Implement Greace pencilA

#### type suffix/prefix
#DONE: Popup on Type suffix/prefix
#DONE: influence selection only
#DONE: Only affect certain mesh type Lights/Empties ....
#TODO: Replace enum with buttons


import bpy
import re

from bpy.types import AddonPreferences
from bpy.props import (
    BoolProperty,
    IntProperty,
    EnumProperty,
    StringProperty,
    FloatVectorProperty,
    PointerProperty,
    CollectionProperty,
)


#######################################
######### RENAMING  ###################
#######################################



def trimString(string, size):
    list1 = string
    list2 = list1[:-size]
    return ''.join(list2)

def getRenamingList(self, context):
    wm = context.scene
    renamingList = []

    if wm.renaming_object_types == 'OBJECT':
        if wm.renaming_only_selection == True:
            for obj in bpy.context.selected_objects:
                if obj.type in wm.renaming_object_types_specified:
                    renamingList.append(obj)
        else:
            for obj in bpy.data.objects:
                if obj.type in wm.renaming_object_types_specified:
                    renamingList.append(obj)

    elif wm.renaming_object_types == 'DATA':
        if wm.renaming_only_selection == True:
            for obj in bpy.context.selected_objects:
                if obj.data not in renamingList:
                    renamingList.append(obj.data)
        else:
            for obj in bpy.data.objects:
                if obj.data not in renamingList:
                    renamingList.append(obj.data)

    elif wm.renaming_object_types == 'MATERIAL':
        if wm.renaming_only_selection == True:
            for obj in bpy.context.selected_objects:
                for mat in obj.material_slots:
                    if mat is not None and mat.name != '':
                        renamingList.append(bpy.data.materials[mat.name])
        else:
            renamingList = list(bpy.data.materials)

    elif wm.renaming_object_types == 'IMAGE':
        renamingList = list(bpy.data.images)

    elif wm.renaming_object_types == 'BONE':
        for arm in bpy.data.armatures:
            for bone in arm.bones:
                renamingList.append(bone)

    elif wm.renaming_object_types == 'COLLECTION':
        renamingList = list(bpy.data.collections)
    return renamingList

windowVariables = []


class RENAMING_MESSAGES():
    message = []

    @classmethod
    def addMessage(cls, oldName, newName,obType = False, obIcon = False, warning = False):
        dict = {'oldName' : oldName, 'newName' : newName , 'obType': obType, 'obIcon' : obIcon, 'warning' : warning}
        cls.message.append(dict)
        return

    @classmethod
    def getMessages(cls):
        return cls.message

    @classmethod
    def printAll(cls):
        print("Print All " + str(list(cls.message)))
        return

    @classmethod
    def clear(cls):
        cls.message = []

#addon Panel
class VIEW3D_PT_tools_renaming_panel(bpy.types.Panel):
    """Creates a renaming Panel"""
    bl_label = "Simple Renaming Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):


        layout = self.layout
        scene = context.scene

        layout.prop(scene, "renaming_object_types", expand = True)
        if str(scene.renaming_object_types) == 'OBJECT':
            layout.prop(scene, "renaming_object_types_specified", expand=True)

        layout.use_property_split = True  # Activate single-column layout


        if str(scene.renaming_object_types) == 'MATERIAL' or str(scene.renaming_object_types) == 'DATA':
            layout.prop(scene, "renaming_only_selection", text="Only Of Selected Objects")
        elif str(scene.renaming_object_types) == 'OBJECT':
            layout.prop(scene, "renaming_only_selection", text="Only Selected")

        layout.separator()

        layout.prop(scene,"renaming_newName")
        layout.operator("renaming.name_replace")
        layout.prop(scene, "renaming_search")
        layout.prop(scene, "renaming_replace")
        layout.prop(scene, "renaming_matchcase")
        layout.operator("renaming.search_replace")

        layout.prop(scene, "renaming_prefix")
        layout.operator("renaming.add_prefix")

        layout.prop(scene, "renaming_suffix")
        layout.operator("renaming.add_suffix")

        layout.prop(scene,"renaming_digits_numerate")
        layout.operator("renaming.numerate")
        layout.prop(scene, "renaming_cut_size")
        layout.operator("renaming.cut_string")

        if str(scene.renaming_object_types) == 'DATA':
            layout.prop(scene, "renaming_sufpre_data_02")
            layout.operator("renaming.dataname_from_obj")


# addon Panel
class VIEW3D_PT_tools_type_suffix(bpy.types.Panel):
    """Creates a renaming Panel"""
    bl_label = "Prefix/Suffix by Type"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "VIEW3D_PT_tools_renaming_panel"

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        layout.prop(scene, "type_pre_sub_only_selection", text="Only Selected")
        layout.prop(scene, "renaming_sufpre_type", expand=True)
        layout.prop(scene, "renaming_sufpre_types_specified")
        layout.use_property_split = True  # Activate single-column layout


        if scene.renaming_sufpre_type == "PRE":
            layout.label(text = "Add Type Prefix")
        else:
            layout.label(text = "Add Type Suffix")






        row = layout.row()
        row.prop(scene, "renaming_sufpre_geometry")
        row = layout.row()
        row.prop(scene, "renaming_sufpre_material")
        row = layout.row()
        row.prop(scene, "renaming_sufpre_empty")
        row = layout.row()
        row.prop(scene, "renaming_sufpre_curve")
        row = layout.row()
        row.prop(scene, "renaming_sufpre_armature")
        row = layout.row()
        row.prop(scene, "renaming_sufpre_lattice")
        row = layout.row()
        row.prop(scene, "renaming_sufpre_data")
        
        row = layout.row()
        row.prop(scene, "renaming_sufpre_surfaces")
        row = layout.row()
        row.prop(scene, "renaming_sufpre_cameras")
        row = layout.row()
        row.prop(scene, "renaming_sufpre_lights")
        row = layout.row()
        row.prop(scene, "renaming_sufpre_collection")
        row = layout.row()
        row.operator("renaming.add_sufpre_by_type")




class VIEW3D_OT_renaming_popup(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "renaming.popup"
    bl_label = "Renaming Panel"

    message: bpy.props.StringProperty(
        name = "message",
        description = "message",
        default = ''
    )

    def execute(self, context):
        #self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 800)

    def draw(self, context):
        wm = bpy.context.scene
        layout = self.layout
        box = layout.box()

        if len(wm.renaming_messages.message) <= 0:
            box.label(text = "No Objects Renamed", icon = "INFO")
        else:
            i = 0
            for msg in wm.renaming_messages.message:
                if msg is not None:
                    if msg['warning'] == False:
                        if (msg['newName'] is not None and msg['oldName'] is not None) and msg['oldName'] != msg['newName']:

                            if i == 0:
                                row = box.row(align=True)
                                row.alignment = 'EXPAND'
                                row.label(text = "OBJECT TYPE")
                                row.label(text = "NEW NAME")
                                row.label(text = "OLD NAME")
                                row.separator()

                            row = box.row(align=True)
                            row.alignment = 'EXPAND'

                            if msg['obType'] is not False and msg['obIcon'] is not False:
                                row.label(text = str(msg['obType']), icon = msg['obIcon'])
                                #row.label(text = str(msg['obType']), icon = 'INFO')
                            else:
                                row.label(text = str(wm.renaming_object_types))

                            row.label(text = str(msg['newName']), icon = 'FILE_TICK')
                            row.label(text = str(msg['oldName']))

                            i += 1
                            print ("i = " + str(i))

                    else:
                        if msg['newName'] is not None and msg['oldName'] is not None:
                            box.label(text = "Warning", icon = "ERROR")
                            box.label(text = "       " + "Name: " + str(msg['oldName']))
                            box.label(text = "       " + msg['warning'])
                        else:
                            box.label(text = "Warning", icon = "ERROR")
                            box.label(text = "       " + msg['warning'])
            if i == 0:
                print("Entered")
                box.label(text = "No Objects Renamed", icon="INFO")
        wm.renaming_messages.clear()


    # def execute(self, context):
    #     self.report({'INFO'}, self.message)
    #     print(self.message)
    #     return {'FINISHED'}

        #scene = context.scene
        #return {'FINISHED'}

# Operators

class VIEW3D_OT_add_type_suf_pre(bpy.types.Operator):
    """Add Type Suffix"""
    bl_idname="renaming.add_sufpre_by_type"
    bl_label="Add Type Suffix or Prefix"
    bl_description= "Adds the above defined Suffixes or Prefixes to all objects in your scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        wm = context.scene

        geo_sufpre = wm.renaming_sufpre_geometry
        mat_suffix = wm.renaming_sufpre_material
        empt_sufpre = wm.renaming_sufpre_empty
        lattice_suffix = wm.renaming_sufpre_lattice
        curve_suffix = wm.renaming_sufpre_curve
        armature_suffix = wm.renaming_sufpre_armature
        data_suffix = wm.renaming_sufpre_data
        surfaces_sufpre = wm.renaming_sufpre_surfaces
        light_sufpre = wm.renaming_sufpre_lights
        bone_sufpre = wm.renaming_sufpre_bones
        camera_sufpre = wm.renaming_sufpre_cameras
        collection_sufpre = wm.renaming_sufpre_collection

        typePreSufList = []

        if wm.type_pre_sub_only_selection == True:
            typePreSufList = bpy.context.selected_objects.copy()
        else:
            typePreSufList = bpy.data.objects

        if collection_sufpre is not '':
            for col in bpy.data.collections:
                oldName = col.name
                nameIsNew = True
                if wm.renaming_sufpre_type == 'SUF':
                    if col.name.endswith(collection_sufpre) == False:
                        newName = self.sufpreAdd(context, col, collection_sufpre)
                    else:
                        nameIsNew = False
                else:
                    if col.name.startswith(collection_sufpre) == False:
                        newName = self.sufpreAdd(context, col, collection_sufpre)
                    else:
                        nameIsNew = False
                if nameIsNew == True:
                    col.name = newName
                    wm.renaming_messages.addMessage(oldName, col.name, 'COLLECTION', 'GROUP')

        if camera_sufpre is not '' or light_sufpre is not '' or surfaces_sufpre is not '' or geo_sufpre is not '' or empt_sufpre is not '' or lattice_suffix is not '' or data_suffix is not '':
            for obj in typePreSufList:
                if light_sufpre is not '':
                    if obj.type == 'LIGHT':
                        oldName = obj.name
                        nameIsNew = True
                        if wm.renaming_sufpre_type == 'SUF':
                            if obj.name.endswith(light_sufpre) == False:
                                newName = self.sufpreAdd(context, obj, light_sufpre)
                            else:
                                nameIsNew = False
                        else:
                            if obj.name.startswith(light_sufpre) == False:
                                newName = self.sufpreAdd(context, obj, light_sufpre)
                            else:
                                nameIsNew = False
                        if nameIsNew == True:
                            obj.name = newName
                            wm.renaming_messages.addMessage(oldName, obj.name, 'LIGHT', 'LIGHT')

                if surfaces_sufpre is not '':
                    if obj.type == 'SURFACE':
                        oldName = obj.name
                        nameIsNew = True
                        if wm.renaming_sufpre_type == 'SUF':
                            if obj.name.endswith(surfaces_sufpre) == False:
                                newName = self.sufpreAdd(context, obj, surfaces_sufpre)
                            else:
                                nameIsNew = False
                        else:
                            if obj.name.startswith(surfaces_sufpre) == False:
                                newName = self.sufpreAdd(context, obj, surfaces_sufpre)
                            else:
                                nameIsNew = False
                        if nameIsNew == True:
                            obj.name = newName
                            wm.renaming_messages.addMessage(oldName, obj.name, 'SURFACE', 'OUTLINER_OB_SURFACE')


                if camera_sufpre is not '':
                    if obj.type == 'CAMERA':
                        oldName = obj.name
                        nameIsNew = True
                        if wm.renaming_sufpre_type == 'SUF':
                            if obj.name.endswith(camera_sufpre) == False:
                                newName = self.sufpreAdd(context,obj, camera_sufpre)
                            else:
                                nameIsNew = False
                        else:
                            if obj.name.startswith(camera_sufpre) == False:
                                newName = self.sufpreAdd(context,obj, camera_sufpre)
                            else:
                                nameIsNew = False
                        if nameIsNew == True:
                            obj.name = newName
                            wm.renaming_messages.addMessage(oldName, obj.name,'CAMERA' ,'OUTLINER_OB_CAMERA')


                if geo_sufpre is not '':
                    if obj.type == 'MESH':
                        oldName = obj.name
                        nameIsNew = True
                        if wm.renaming_sufpre_type == 'SUF':
                            if obj.name.endswith(geo_sufpre) == False:
                                newName = self.sufpreAdd(context,obj, geo_sufpre)
                            else:
                                nameIsNew = False
                        else:
                            if obj.name.startswith(geo_sufpre) == False:
                                newName = self.sufpreAdd(context,obj, geo_sufpre)
                            else:
                                nameIsNew = False
                        if nameIsNew == True:
                            obj.name = newName
                            wm.renaming_messages.addMessage(oldName, obj.name,'MESH' ,'OUTLINER_OB_MESH')

                if empt_sufpre is not '':
                    if obj.type == 'EMPTY':
                        oldName = obj.name
                        nameIsNew = True
                        if wm.renaming_sufpre_type == 'SUF':
                            if obj.name.endswith(empt_sufpre) == False:
                                newName = self.sufpreAdd(context,obj, empt_sufpre)
                            else:
                                nameIsNew = False
                        else:
                            if obj.name.startswith(empt_sufpre) == False:
                                newName = self.sufpreAdd(context, obj, empt_sufpre)
                            else:
                                nameIsNew = False
                        if nameIsNew == True:
                            obj.name = newName
                            wm.renaming_messages.addMessage(oldName , obj.name, 'EMPTY', 'OUTLINER_OB_EMPTY')

                if lattice_suffix is not '':
                    if obj.type == 'LATTICE' and obj.name.endswith(lattice_suffix) == False:
                        oldName = obj.name
                        nameIsNew = True
                        if wm.renaming_sufpre_type == 'SUF':
                            if obj.name.endswith(lattice_suffix) == False:
                                newName = self.sufpreAdd(context,obj,  lattice_suffix)
                            else:
                                nameIsNew = False
                        else:
                            if obj.name.startswith(lattice_suffix) == False:
                                newName = self.sufpreAdd(context, obj, lattice_suffix)
                            else:
                                nameIsNew = False

                        if nameIsNew == True:
                            obj.name = newName
                            wm.renaming_messages.addMessage(oldName, obj.name, 'LATTICE' ,'OUTLINER_OB_LATTICE' )

                if curve_suffix is not '':
                    if obj.type == 'CURVE' and obj.name.endswith(curve_suffix) == False:
                        oldName = obj.name
                        nameIsNew = True
                        if wm.renaming_sufpre_type == 'SUF':
                            if obj.name.endswith(curve_suffix) == False:
                                newName = self.sufpreAdd(context,obj,  curve_suffix)
                            else:
                                nameIsNew = False
                        else:
                            if obj.name.startswith(curve_suffix) == False:
                                newName = self.sufpreAdd(context, obj, curve_suffix)
                            else:
                                nameIsNew = False
                        if nameIsNew == True:
                            obj.name = newName
                            wm.renaming_messages.addMessage(oldName, obj.name, 'CURVE', 'OUTLINER_OB_CURVE')

                if data_suffix is not '':
                    if (obj.type == 'CURVE' or obj.type == 'LATTICE' or obj.type == 'MESH' or obj.type == 'META' or obj.type == 'SURFACE') and obj.data.name.endswith(data_suffix) == False:
                        oldName = obj.name
                        nameIsNew = True
                        if wm.renaming_sufpre_type == 'SUF':
                            if obj.data.name.endswith(data_suffix) == False:
                                newName = self.suffixDataAdd(context, obj, data_suffix)
                            else:
                                nameIsNew = False
                        else:
                            if obj.data.name.startswith(data_suffix) == False:
                                newName = self.suffixDataAdd(context,obj, data_suffix)
                            else:
                                nameIsNew = False

                        if nameIsNew == True:
                            obj.data.name = newName
                            wm.renaming_messages.addMessage(oldName, obj.data.name,'DATA' ,'FILE_BLANK')
        bpy.ops.renaming.popup('INVOKE_DEFAULT')

        if mat_suffix is not '':
            for mat in bpy.data.materials:
                oldName = mat.name
                nameIsNew = True
                if wm.renaming_sufpre_type == 'SUF':
                    if mat.name.endswith(mat_suffix) == False:
                        newName = self.sufpreMatAdd(context, mat, mat_suffix)
                    else:
                        nameIsNew = False
                else:
                    if mat.name.startswith(mat_suffix) == False:
                        newName = self.sufpreMatAdd(context, mat, mat_suffix)
                    else:
                        nameIsNew = False

                if nameIsNew == True:
                    mat.name = newName
                    wm.renaming_messages.addMessage(oldName, mat.name, 'MATERIAL', 'MATERIAL')

        # if group_suffix != '':
        #     for group in bpy.data.groups:
        #         nameIsNew = True
        #         oldName = group.name
        #         if scene.renaming_sufpre_type == 'SUF':
        #             if group.name.endswith(group_suffix) == False:
        #                 newName =self.suffixGrpAdd(context,group, group_suffix)
        #             else:
        #                 nameIsNew = False
        #         else:
        #             if group.name.startswith(group_suffix) == False:
        #                 newName = self.suffixGrpAdd(context, group, group_suffix)
        #             else:
        #                 nameIsNew = False
        #         if nameIsNew == True:
        #             group.name = newName
        #             scene.renaming_messages.addMessage(oldName, group.name, 'GROUP', 'OUTLINER_OB_GROUP_INSTANCE')

        if armature_suffix is not '' or bone_sufpre is not '':
            for armature in bpy.data.armatures:
                if armature_suffix is not '':
                    nameIsNew = True
                    oldName = armature.name
                    if wm.renaming_sufpre_type == 'SUF':
                        if armature.name.endswith(armature_suffix) == False:
                            newName = self.suffixArmAdd(context,armature, armature_suffix)
                        else:
                            nameIsNew = False
                    else:
                        if armature.name.startswith(armature_suffix) == False:
                            newName = self.suffixArmAdd(context, armature, armature_suffix)
                        else:
                            nameIsNew = False
                    if nameIsNew == True:
                        armature.name = newName
                        wm.renaming_messages.addMessage(oldName, armature.name, 'ARMATURE', 'OUTLINER_OB_ARMATURE')
                if bone_sufpre is not '':
                    for bone in armature.bones:
                        nameIsNew = True
                        oldName = bone.name
                        if wm.renaming_sufpre_type == 'SUF':
                            if bone.name.endswith(bone_sufpre) == False:
                                newName = self.suffixArmAdd(context, bone, bone_sufpre)
                            else:
                                nameIsNew = False
                        else:
                            if bone.name.startswith(bone_sufpre) == False:
                                newName = self.suffixArmAdd(context, bone, bone_sufpre)
                            else:
                                nameIsNew = False
                        if nameIsNew == True:
                            bone.name = newName
                            wm.addMessage(oldName, bone.name, 'BONE', 'BONE_DATA')

        # bpy.ops.renaming.popup('INVOKE_DEFAULT')

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
            while(nName in bpy.data.objects):
                if wm.renaming_sufpre_type == 'SUF':
                    nName = obj.name + "_" + str(i) + sufpreName
                else:
                    nName = sufpreName + obj.name + "_" + str(i)
                i = i + 1

        obj.name = nName
        return nName

    def suffixDataAdd(self, context, obj, sufpreName):
        wm = context.scene

        nName = obj.data.name
        if wm.renaming_sufpre_type == 'SUF':
            nName = nName + sufpreName
        else:
            nName = sufpreName + nName

        if nName not in bpy.data.meshes and nName not in bpy.data.lattices and nName not in bpy.data.curves and nName not in bpy.data.METABALL:
            obj.data.name = nName
            return nName
        else:
            i = 1
            while( nName in bpy.data.meshes or nName  in bpy.data.lattices or nName  in bpy.data.curves or nName  in bpy.data.METABALL):
                nName = obj.data.name + "_" + str(i)
                i = i + 1
            return nName

    def sufpreMatAdd(self,context, mat, sufpreName):
        wm = context.scene
        nName = mat.name
        if wm.renaming_sufpre_type == 'SUF':
            nName = nName + sufpreName
        else:
            nName = sufpreName + nName

        if nName not in bpy.data.materials:
            mat.name = nName
            return nName
        else:
            i = 1
            while( nName in bpy.data.materials):
                nName = mat.name + "_" + str(i)
                i = i + 1
            return nName

    # def suffixGrpAdd(self, context, grp, sufpreName):
    #     scene = context.scene
    #
    #     nName = grp.name
    #     if scene.renaming_sufpre_type == 'SUF':
    #         nName = nName + sufpreName
    #     else:
    #         nName = sufpreName + nName
    #
    #     if nName not in bpy.data.groups:
    #         grp.name = nName
    #         return nName
    #     else:
    #         i = 1
    #         while( nName in bpy.data.groups):
    #             nName = grp.name + "_" + str(i)
    #             i = i + 1
    #         return nName

    def suffixArmAdd(self, context, arm, sufpreName):
        wm = context.scene

        nName = arm.name
        if wm.renaming_sufpre_type == 'SUF':
            nName = nName + sufpreName
        else:
            nName = sufpreName + nName

        if nName not in bpy.data.armatures:
            arm.name = nName
            return nName
        else:
            i = 1
            while( nName in bpy.data.armatures):
                nName = arm.name + "_" + str(i)
                i = i + 1
            return nName

class VIEW3D_OT_search_and_replace(bpy.types.Operator):
    bl_idname="renaming.search_replace"
    bl_label="Search and Replace"
    bl_description = "replaces parts in the object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        wm = context.scene

        renamingList = []
        renamingList = getRenamingList(self, context)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    if wm.renaming_search is not '':
                        if wm.renaming_matchcase:
                            oldName = entity.name
                            newName = str(entity.name).replace(wm.renaming_search, wm.renaming_replace)
                            entity.name = newName
                            wm.renaming_messages.addMessage(oldName, entity.name)
                        else:
                            oldName = entity.name
                            replaceSearch = re.compile(re.escape(wm.renaming_search), re.IGNORECASE)
                            newName = replaceSearch.sub(wm.renaming_replace, entity.name)
                            entity.name = newName
                            wm.renaming_messages.addMessage(oldName, entity.name)

        bpy.ops.renaming.popup('INVOKE_DEFAULT')
        return{'FINISHED'}

class VIEW3D_OT_replace_name(bpy.types.Operator):
    bl_idname="renaming.name_replace"
    bl_label="Replace Names"
    bl_description = "replaces the names of the objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        wm = context.scene
        replaceName = wm.renaming_newName
        renamingList = getRenamingList(self, context)

        if len(str(replaceName)) > 0:
            digits = 3
            if len(renamingList) > 0:
                for entity in renamingList:
                    if entity is not None:
                        i = 1
                        if wm.renaming_object_types == 'GROUP' or wm.renaming_object_types == 'IMAGE':
                            i = 0
                        oldName = entity.name
                        newName = ""

                        dataList = []
                        boneList = []

                        if wm.renaming_object_types == 'BONE':
                            for arm in bpy.data.armatures:
                                for bone in arm.bones:
                                    boneList.append(bone.name)

                        if wm.renaming_object_types == 'DATA':
                            for obj in bpy.data.objects:
                                if obj.data is not None:
                                    dataList.append(obj.data.name)

                        while True:
                            print ("Entered While " + str(i) )
                            newName = replaceName + '_' + ('{num:{fill}{width}}'.format(num=i, fill='0', width=digits))

                            if wm.renaming_object_types == 'OBJECT':
                                if newName in bpy.data.objects and newName != entity.name:
                                    i = i + 1
                                else:
                                    break
                            elif wm.renaming_object_types == 'MATERIAL':
                                if newName in bpy.data.materials and newName != entity.name:
                                    i = i + 1
                                else:
                                    break
                            # elif scene.renaming_object_types == 'GROUP':
                            #     if newName in bpy.data.groups and newName != entity.name:
                            #         i = i + 1
                            #     else:
                            #         break
                            elif wm.renaming_object_types == 'IMAGE':
                                if newName in bpy.data.images and newName != entity.name:
                                    i = i + 1
                                else:
                                    break
                            elif wm.renaming_object_types == 'DATA':
                                if newName in dataList and newName != entity.name:
                                    i = i + 1
                                else:
                                    break
                            elif wm.renaming_object_types == 'BONE':
                                if newName in boneList and newName != entity.name:
                                    i = i + 1
                                else:
                                    break


                        newName = replaceName + '_' + ('{num:{fill}{width}}'.format(num=i, fill='0', width= digits))
                        entity.name = newName
                        wm.renaming_messages.addMessage(oldName, entity.name)
                        i = i + 1

        else: #len(str(replaceName)) <= 0
            wm.renaming_messages.addMessage(None, None, "Insert a valid string to replace names")


        i = 0
        bpy.ops.renaming.popup('INVOKE_DEFAULT')
        return {'FINISHED'}

class VIEW3D_OT_trim_string(bpy.types.Operator):
    bl_idname="renaming.cut_string"
    bl_label="Trim End of String"
    bl_description = "Deletes the in the trim size specified amount of characters at the end of object names"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self,context):
        wm = context.scene
        renamingList = []
        renamingList = getRenamingList(self, context)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    oldName = entity.name
                    newName = trimString(entity.name, wm.renaming_cut_size)
                    entity.name = newName
                    wm.renaming_messages.addMessage(oldName, entity.name)

        bpy.ops.renaming.popup('INVOKE_DEFAULT')
        return{'FINISHED'}

class VIEW3D_OT_add_suffix(bpy.types.Operator):
    bl_idname="renaming.add_suffix"
    bl_label="Add suffix"
    bl_description = "Adds a suffix to object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):

        wm = context.scene
        suffix = wm.renaming_suffix

        renamingList = []
        renamingList = getRenamingList(self, context)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    if entity.name.endswith(suffix) is not True:
                        oldName = entity.name
                        newName = entity.name + suffix
                        entity.name = newName
                        wm.renaming_messages.addMessage(oldName, entity.name)
        else:
            wm.renaming_messages.addMessage(None, None, "Insert Valide String")

        bpy.ops.renaming.popup('INVOKE_DEFAULT')
        return{'FINISHED'}

class VIEW3D_OT_add_prefix(bpy.types.Operator):
    bl_idname="renaming.add_prefix"
    bl_label="Add Prefix"
    bl_description = "Adds a prefix to object names"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self,context):
        wm = context.scene
        pre = wm.renaming_prefix

        renamingList = []
        renamingList = getRenamingList(self, context)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    if entity.name.startswith(pre) is not True:
                        oldName = entity.name
                        newName = pre + entity.name
                        entity.name = newName
                        wm.renaming_messages.addMessage(oldName, entity.name)

        bpy.ops.renaming.popup('INVOKE_DEFAULT')
        return{'FINISHED'}

class VIEW3D_OT_renaming_numerate(bpy.types.Operator):
    bl_idname="renaming.numerate"
    bl_label="Numerate"
    bl_description = "adds a growing number to the object names with the amount of digits specified in Number Lenght"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self,context):
        wm = context.scene
        i = 1
        step = wm.renaming_base_numerate
        digits = wm.renaming_digits_numerate

        renamingList = []
        renamingList = getRenamingList(self, context)

        if len(renamingList) > 0:
            for entity in renamingList:
                if entity is not None:
                    oldName = entity.name
                    newName = entity.name + '_' + ('{num:{fill}{width}}'.format(num=i * step, fill='0', width= digits))
                    entity.name = newName
                    wm.renaming_messages.addMessage(oldName, entity.name)
                    i = i + 1

        bpy.ops.renaming.popup('INVOKE_DEFAULT')
        return{'FINISHED'}

class VIEW3D_OT_use_objectname_for_data(bpy.types.Operator):
    bl_idname = "renaming.dataname_from_obj"
    bl_label = "Data Name from Object"
    bl_description = "Renames the object data according to the object name and adds the in the data textfield specified suffix."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene
        suffix_data = wm.renaming_sufpre_data_02

        if wm.renaming_only_selection == True:
            for obj in bpy.context.selected_objects:

                objName = obj.name + suffix_data
                if suffix_data is not '':
                    if (obj.type == 'CURVE' or obj.type == 'LATTICE' or obj.type == 'MESH' or obj.type == 'META' or obj.type == 'SURFACE'):
                        oldName = obj.data.name
                        newName = objName
                        obj.data.name = newName
                        wm.renaming_messages.addMessage(oldName, obj.data.name)
        else:
            for obj in bpy.data.objects:
                objName = obj.name + suffix_data
                if suffix_data is not '':
                    if (obj.type == 'CURVE' or obj.type == 'LATTICE' or obj.type == 'MESH' or obj.type == 'META' or obj.type == 'SURFACE'):
                        oldName = obj.data.name
                        newName = objName
                        obj.data.name = newName
                        wm.renaming_messages.addMessage(oldName, obj.data.name)

        bpy.ops.renaming.popup('INVOKE_DEFAULT')
        return {'FINISHED'}

#addon Preferences
class VIEW3D_OT_renaming_preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    renaming_category = bpy.props.StringProperty (
        name = "Category",
        description = "Defines in which category of the tools panel the simple renaimg panel is listed",
        default = 'Misc',
        #update = update_panel_position,
    )

    # addon updater preferences from `__init__`, be sure to copy all of them
    #auto_check_update = bpy.props.BoolProperty(
    #    name="Auto-check for Update",
    #    description="If enabled, auto-check for updates using an interval",
    #    default=False,
    #)
    #updater_intrval_months = bpy.props.IntProperty(
    #    name='Months',
    #    description="Number of months between checking for updates",
    #    default=0,
    #    min=0
    #)
    #updater_intrval_days = bpy.props.IntProperty(
    #    name='Days',
    #    description="Number of days between checking for updates",
    #    default=7,
    #    min=0,
    #)
    #updater_intrval_hours = bpy.props.IntProperty(
    #    name='Hours',
    #    description="Number of hours between checking for updates",
    #    default=0,
    #    min=0,
    #    max=23
    #)
    #updater_intrval_minutes = bpy.props.IntProperty(
    #    name='Minutes',
    #    description="Number of minutes between checking for updates",
    #    default=0,
    #    min=0,
    #    max=59
    #)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "renaming_category")

        # updater draw function
        #addon_updater_ops.update_settings_ui(self,context)

classes = (
    VIEW3D_PT_tools_renaming_panel,
    VIEW3D_OT_renaming_popup,
    VIEW3D_OT_add_suffix,
    VIEW3D_OT_add_prefix,
    VIEW3D_OT_search_and_replace,
    VIEW3D_OT_renaming_numerate,
    VIEW3D_OT_add_type_suf_pre,
    VIEW3D_OT_trim_string,
    VIEW3D_OT_use_objectname_for_data,
    VIEW3D_OT_replace_name,
    VIEW3D_PT_tools_type_suffix,
    #VIEW3D_OT_renaming_preferences,
    )


def menu_add_suffix(self, context):
    self.layout.operator(VIEW3D_OT_add_suffix.bl_idname)                # or YourClass.bl_idname

enumObjectTypes = [('EMPTY', "", "Rename empty objects",'OUTLINER_OB_EMPTY',  1),
                   ('MESH', "", "Rename mesh objects",'OUTLINER_OB_MESH', 2 ),
                   ('CAMERA', "", "Rename Camera objects",'OUTLINER_OB_CAMERA', 4),
                   ('LIGHT', "", "Rename light objects",'OUTLINER_OB_LIGHT', 8),
                   ('ARMATURE', "", "Rename armature objects",'OUTLINER_OB_ARMATURE', 16),
                   ('LATTICE', "", "Rename lattice objects",'OUTLINER_OB_LATTICE', 32),
                   ('CURVE', "", "Rename curve objects",'OUTLINER_OB_CURVE', 64),
                   ('SURFACE', "", "Rename surface objects",'OUTLINER_OB_SURFACE', 128),
                   ('TEXT', "", "Rename text objects", 'OUTLINER_OB_FONT', 256),
                   ('GPENCIL', "", "Rename greace pencil objects", 'OUTLINER_OB_GREASEPENCIL', 512),
                   ('METABALL', "", "Rename metaball objects",'OUTLINER_OB_META', 1024)]

enumObjectTypesExt = [('EMPTY', "", "Rename empty objects",'OUTLINER_OB_EMPTY',  1),
                   ('MESH', "", "Rename mesh objects",'OUTLINER_OB_MESH', 2 ),
                   ('CAMERA', "", "Rename Camera objects",'OUTLINER_OB_CAMERA', 4),
                   ('LIGHT', "", "Rename light objects",'OUTLINER_OB_LIGHT', 8),
                   ('ARMATURE', "", "Rename armature objects",'OUTLINER_OB_ARMATURE', 16),
                   ('LATTICE', "", "Rename lattice objects",'OUTLINER_OB_LATTICE', 32),
                   ('CURVE', "", "Rename curve objects",'OUTLINER_OB_CURVE', 64),
                   ('SURFACE', "", "Rename surface objects",'OUTLINER_OB_SURFACE', 128),
                   ('TEXT', "", "Rename text objects", 'OUTLINER_OB_FONT', 256),
                   ('GPENCIL', "", "Rename greace pencil objects", 'OUTLINER_OB_GREASEPENCIL', 512),
                   ('METABALL', "", "Rename metaball objects",'OUTLINER_OB_META', 2048),
                   ('COLLECTION', "", "Rename collections",'GROUP', 4096),
                   ('BONE',"", "", 'BONE_DATA', 8192),]

def register():
    #bpy.types.INFO_MT_mesh_add.append(menu_add_suffix)
    # IDStore = bpy.types.
    IDStore = bpy.types.Scene
    IDStore.renaming_sufpre_type = EnumProperty(
            name="Suffix or Prefix by Type",
            items=(('PRE', "Prefix", "prefix"),
                   ('SUF', "Suffix", "suffix"),),
            description="Add Prefix or Suffix to type",
            )


    IDStore.renaming_object_types = EnumProperty(
             name="Renaming Objects",
             items=(('OBJECT', "Object", "Scene Objects"),
                    ('MATERIAL', "Material", "Materials"),
                    ('IMAGE', "Image Textures", "Image Textures"),
                    ('DATA', "Data", "Object Data"),
                    ('BONE', "Bone", "Bones")),
             description="Which kind of object to rename",
             )

    #IDStore.renaming_object_types_specified = EnumProperty(name="Object Types",items=enumObjectTypes,description="Which kind of object to export",options={'ENUM_FLAG'}, default= {'CURVE','LATTICE','SURFACE','METABALL','MESH','ARMATURE','LIGHT','CAMERA','EMPTY'})
    IDStore.renaming_object_types_specified = EnumProperty(name="Object Types",
                                                           items=enumObjectTypes,
                                                           description="Which kind of object to rename",
                                                           options={'ENUM_FLAG'},
                                                           default= {'CURVE','LATTICE','SURFACE','METABALL','MESH','ARMATURE','LIGHT','CAMERA','EMPTY', 'GPENCIL', 'TEXT'}
                                                           )

    IDStore.renaming_newName = StringProperty(name="New Name", default = '')
    IDStore.renaming_search = StringProperty(name='Search', default = '')
    IDStore.renaming_replace = StringProperty(name='Replace', default = '')
    IDStore.renaming_suffix = StringProperty(name="Suffix", default = '')
    IDStore.renaming_prefix = StringProperty(name="Prefix", default = '')
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
    IDStore.renaming_base_numerate = IntProperty(name="Step Size", default = 1)
    IDStore.renaming_digits_numerate = IntProperty(name="Number Length", default = 3)
    IDStore.renaming_cut_size = IntProperty(name="Trim Size", default = 3)
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
                                                           default = {'CURVE', 'LATTICE', 'SURFACE', 'METABALL', 'MESH', 'ARMATURE', 'LIGHT', 'CAMERA', 'EMPTY', 'GPENCIL','TEXT', 'BONE','COLLECTION'}
                                                           )

    IDStore.renaming_sufpre_material = StringProperty(name='Material', default = '')
    IDStore.renaming_sufpre_geometry = StringProperty(name='Geometry', default = '')
    IDStore.renaming_sufpre_empty = StringProperty(name="Empty", default = '')
    IDStore.renaming_sufpre_group = StringProperty(name="Group", default = '')
    IDStore.renaming_sufpre_curve = StringProperty(name="Curve", default = '')
    IDStore.renaming_sufpre_armature = StringProperty(name="Armature", default = '')
    IDStore.renaming_sufpre_lattice = StringProperty(name="Lattice", default = '')
    IDStore.renaming_sufpre_data = StringProperty(name="Data", default = '')
    IDStore.renaming_sufpre_data_02 = StringProperty(name="Data = Objectname + ", default = '')
    IDStore.renaming_sufpre_surfaces = StringProperty(name="Surfaces", default = '')
    IDStore.renaming_sufpre_cameras = StringProperty(name="Cameras", default = '')
    IDStore.renaming_sufpre_lights = StringProperty(name="Lights", default = '')
    IDStore.renaming_sufpre_bones = StringProperty(name="Bones", default = '')
    IDStore.renaming_sufpre_collection = StringProperty(name="Collections", default = '')

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    #IDStore = bpy.types.Scene
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
    del IDStore.renaming_sufpre_bones
    del IDStore.renaming_sufpre_collection
    del IDStore.renaming_object_types_specified

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

#register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()

#import bpy
#filename = "G:\GitHub\mp_simple_renaming_panel\simple_renaming_panel.py"
#exec(compile(open(filename).read(), filename, 'exec'))
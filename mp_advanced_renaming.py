bl_info = {
    "name": "MP Advanced Renaming",
    "description": "This Addon offers advanced functionalities to rename a set of objects",
    "author": "Matthias Patscheider",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "View3D > Tools > Misc",
    "warning": "Beta", # used for warning icon and text in addons panel
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
                "Scripts/My_Script",
    "tracker_url": "http://developer.blender.org/maniphest/task/create/?project=3&type=Bug",
    "support": "COMMUNITY",
    "category": "Scene"
    }

import os
from os.path import *

import bpy
from bpy.types import WindowManager
from bpy.types import Scene

from bpy.props import (
    StringProperty,
    EnumProperty,
    BoolProperty,
    FloatProperty,
    IntProperty
    )
    
#######################################
######### RENAMING 
#######################################
         
class RenamingPanel(bpy.types.Panel):
    """Creates a renaming Panel"""
    bl_label = "Advanced Renaming Panel"
    #bl_idname = "RENAMING_panel"
    #bl_space_type = 'PROPERTIES'
    #bl_region_type = 'WINDOW'
    #bl_context = "scene"
    #bl_label = 'Custom Panel'
    bl_space_type = 'VIEW_3D'  # Choosing Viewport
    bl_region_type = 'TOOLS' # Choosing tools panel in viewport
    
    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene

        #row = layout.row()
        #row.prop(wm, "renaming_newName") 
        
        #row = layout.row()
        #row.label("Multi Selection is possible")
        #row = layout.row()
        #row.prop(wm, "renaming_object_types") 
        
        row = layout.row()
        row.prop(wm, "rename_only_selection")
        row = layout.row()
        row.label("Search and Replace")
        row = layout.row()
        row.prop(wm, "renaming_search")
        row.prop(wm, "renaming_replace")
        row = layout.row()
        row.operator("renaming.search_replace")
        row = layout.row()
        row.prop(wm, "renaming_prefix") 
        row = layout.row()
        row.operator("renaming.add_prefix")
        row = layout.row()        
        row.prop(wm, "renaming_suffix")
        row = layout.row()
        row.operator("renaming.add_suffix")
        
        
        row = layout.row()
        row.prop(wm,"renaming_base_numerate")        
        row = layout.row()
        row.prop(wm,"renaming_digits_numerate")
        row = layout.row()
        row.operator("renaming.numerate")
        

        ###### TODO: rename data ########
        ###### TODO: rename Mat #######
        
        row = layout.row()
        row.prop(wm, "renaming_cut_size")
        row = layout.row()
        row.operator("renaming.cut_string")
        
        row = layout.row()
        row.prop(wm, "renaming_suffix_data_02")
        row = layout.row()
        row.operator("renaming.dataname_from_obj")
        



class SuffixPanel(bpy.types.Panel):
    """Creates a renaming Panel"""
    bl_label = "Suffix Panel"
    #bl_idname = "SUFFIX_panel"
    #bl_space_type = 'PROPERTIES'
    #bl_region_type = 'WINDOW'
    #bl_context = "scene"        
    #bl_label = 'Custom Panel'
    bl_space_type = 'VIEW_3D'  # Choosing Viewport
    bl_region_type = 'TOOLS' # Choosing tools panel in viewport
    
    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        scene = context.scene
        # Check for string length
        
        box = layout.box()
        row = box.row()
        row.label("add suffix by type")
        row = box.row()
        row.prop(wm, "renaming_suffix_geometry")
        row = box.row()
        row.prop(wm, "renaming_suffix_material")
        row = box.row()
        row.prop(wm, "renaming_suffix_empty")
        row = box.row()
        row.prop(wm, "renaming_suffix_curve")
        row = box.row()
        row.prop(wm, "renaming_suffix_armature")
        row = box.row()
        row.prop(wm, "renaming_suffix_group")
        row = box.row()
        row.prop(wm, "renaming_suffix_lattice")
        row = box.row()
        row.prop(wm, "renaming_suffix_data")
        
        row = box.row()
        row.operator("renaming.add_suffix_by_type")
    
class UseObjectnameForData(bpy.types.Operator):        
    bl_idname="renaming.dataname_from_obj"
    bl_label="Data Suffix"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}   

    def execute(self,context):
        wm = context.window_manager   
        suffix_data = wm.renaming_suffix_data_02
        for obj in bpy.data.objects:
            if suffix_data is not '':
                if (obj.type == 'CURVE' or obj.type == 'LATTICE' or obj.type == 'MESH') and obj.name.endswith(suffix_data) == False:
                    obj.data.name = obj.name + suffix_data
        return {'FINISHED'}
    
class AddTypeSuffix(bpy.types.Operator):
    bl_idname="renaming.add_suffix_by_type"
    bl_label="Add type specific suffix"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    def execute(self,context):
        wm = context.window_manager
        
        geo_suffix = wm.renaming_suffix_geometry
        mat_suffix = wm.renaming_suffix_material
        empt_suffix = wm.renaming_suffix_empty  
        lattice_suffix = wm.renaming_suffix_lattice
        curve_suffix = wm.renaming_suffix_curve
        group_suffix = wm.renaming_suffix_group
        armature_suffix = wm.renaming_suffix_armature
        data_suffix = wm.renaming_suffix_data
        
        
        if geo_suffix is not '' or empt_suffix is not '' or LATTICE or suffix_data is not '':
            for obj in bpy.data.objects:
                if geo_suffix is not '': 
                    if obj.type == 'MESH' and obj.name.endswith(geo_suffix) == False:
                        obj.name = obj.name + geo_suffix
                            
                if empt_suffix is not '': 
                    if obj.type == 'EMPTY' and obj.name.endswith(empt_suffix) == False:
                        obj.name = obj.name + empt_suffix                        
        
                if lattice_suffix is not '':
                    if obj.type == 'LATTICE' and obj.name.endswith(lattice_suffix) == False:
                        obj.name = obj.name + lattice_suffix    
                if curve_suffix is not '': 
                    if obj.type == 'CURVE' and obj.name.endswith(curve_suffix) == False:
                        obj.name = obj.name + curve_suffix
                
                if suffix_data is not '':
                    if (obj.type == 'CURVE' or obj.type == 'LATTICE' or obj.type == 'MESH') and obj.name.endswith(data_suffix) == False:
                        obj.data.name = obj.name + data_suffix
                        
                        
        if mat_suffix is not '': 
            for mat in bpy.data.materials:
                if mat.name.endswith(mat_suffix) == False:
                    mat.name = mat.name + mat_suffix
        
        

                    
        if group_suffix is not '':
            for group in bpy.data.groups:
                if group.name.endswith(group_suffix) == False:
                    group.name = group.name + group_suffix
                    
        if armature_suffix is not '':
            for armature in bpy.data.armatures:
                if armature.name.endswith(armature_suffix) == False:
                    armature.name = armature.name + armature_suffix
                    
        

        return {'FINISHED'}
           
       
class SearchAndReplace(bpy.types.Operator):
    bl_idname="renaming.search_replace"
    bl_label="Search and Replace"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    type = StringProperty()
    
    def execute(self,context):
        wm = context.window_manager
        if wm.rename_only_selection == True: 
            for obj in context.selected_objects:
                obj.name = str(obj.name).replace(wm.renaming_search, wm.renaming_replace)
                obj.data.name = str(obj.name) + "_data"
        else: 
            for obj in bpy.data.objects:
                obj.name= str(obj.name).replace(wm.renaming_search, wm.renaming_replace)
                obj.data.name = str(obj.name) + "_data"
        return{'FINISHED'}      

def trimString(string, size):      
    list1 = string
    list2 = list1[:-size]
    return ''.join(list2)
    
class TrimString(bpy.types.Operator):
    bl_idname="renaming.cut_string"
    bl_label="Trim the end of the string"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    def execute(self,context):
        wm = context.window_manager
        if wm.rename_only_selection == True: 
            for obj in context.selected_objects:
                obj.name = trimString(obj.name, wm.renaming_cut_size)
        else: 
            for obj in bpy.data.objects:
                obj.name = trimString(obj.name, wm.renaming_cut_size)
        
        
        return{'FINISHED'}             

class Addsuffix(bpy.types.Operator):
    bl_idname="renaming.add_suffix"
    bl_label="Add suffix"  
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}    

    def execute(self,context):
        
        wm = context.window_manager
        suffix = wm.renaming_suffix
        print("suffix" + suffix)
        if wm.rename_only_selection == True: 
            for obj in context.selected_objects: 
                obj.name = obj.name + suffix
        
        else: 
            for obj in bpy.data.objects:  
                obj.name = obj.name + suffix          
        
        return{'FINISHED'}  

        
        
    
class AddPrefix(bpy.types.Operator):
    bl_idname="renaming.add_prefix"
    bl_label="Add Prefix"    
    bl_options = {'REGISTER', 'UNDO'}
    

    def execute(self,context):
        wm = context.window_manager
        pre = wm.renaming_prefix
        
        if wm.rename_only_selection == True: 
            for obj in context.selected_objects: 
                obj.name = pre + obj.name
        else: 
        ## TODO: ERROR! 
            for obj in bpy.data.objects:  
                filename = pre + obj.name
                obj.name = filename
                
        return{'FINISHED'}  
 
class RenamingNumerate(bpy.types.Operator):
    bl_idname="renaming.numerate"
    bl_label="Numerate"    
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL' }
    
    

    def execute(self,context):
        wm = context.window_manager
        i = 1
        step = wm.renaming_base_numerate
        digits = wm.renaming_digits_numerate
        
        
        if wm.rename_only_selection == True: 
            for obj in context.selected_objects: 
                obj.name = obj.name + '_' + ('{num:{fill}{width}}'.format(num=i * step, fill='0', width= digits))
                i = i + 1 
        else: 
            for obj in bpy.data.objects:  
                obj.name = obj.name + '_' + ('{num:{fill}{width}}'.format(num=i * step, fill='0', width= digits))
                i = i + 1         
        
        return{'FINISHED'}  
  
windowVariables = []
  
def register():

    ############################
    ######REnaming
    ############################
    WindowManager.renaming_object_types = EnumProperty(
            name="Renaming Objects",
            options={'ENUM_FLAG'},
            items=(('OBJECT', "Object", ""),
                   ('MESH', "Mesh", ""),
                   ('MATERIAL', "Material", ""),
                   ('DATA', "Data", "")),
            description="Which kind of object to rename",
            default={'OBJECT'},
            )
    windowVariables
    
    WindowManager.renaming_search = StringProperty(name='Search', default = '')
    WindowManager.renaming_replace = StringProperty(name='Replace', default = '')
    WindowManager.renaming_suffix = StringProperty(name="suffix", default = '')
    WindowManager.renaming_prefix = StringProperty(name="Prefix", default = '') 
    WindowManager.rename_only_selection = BoolProperty(
            name="Only Selected Objects",
            description="Rename only selected objects",
            default=True,
            )          
    WindowManager.renaming_base_numerate = IntProperty(name="Step Size", default = 1)    
    WindowManager.renaming_digits_numerate = IntProperty(name="Length", default = 3)     
    WindowManager.renaming_cut_size = IntProperty(name="Letters to trim", default = 3)         
    
    WindowManager.renaming_suffix_material = StringProperty(name='material', default = '')
    WindowManager.renaming_suffix_geometry = StringProperty(name='geometry', default = '')
    WindowManager.renaming_suffix_empty = StringProperty(name="empty", default = '')
    WindowManager.renaming_suffix_group = StringProperty(name="group", default = '')  
    WindowManager.renaming_suffix_curve = StringProperty(name="curve", default = '') 
    WindowManager.renaming_suffix_armature = StringProperty(name="armature", default = '')     
    WindowManager.renaming_suffix_lattice = StringProperty(name="lattice", default = '')     
    WindowManager.renaming_suffix_data = StringProperty(name="data", default = '')     

    WindowManager.renaming_suffix_data_02 = StringProperty(name="data", default = '')  
    
    bpy.utils.register_class(RenamingPanel)    
    bpy.utils.register_class(Addsuffix)
    bpy.utils.register_class(AddPrefix)
    bpy.utils.register_class(SearchAndReplace)    
    bpy.utils.register_class(RenamingNumerate)    
    bpy.utils.register_class(AddTypeSuffix)
    bpy.utils.register_class(TrimString)
    bpy.utils.register_class(UseObjectnameForData)
    bpy.utils.register_class(SuffixPanel)

 


    

def unregister():

    del WindowManager.renaming_search
    del WindowManager.renaming_object_types
    del WindowManager.renaming_replace 
    del WindowManager.renaming_suffix
    del WindowManager.renaming_prefix
    del WindowManager.rename_only_selection
    del WindowManager.renaming_base_numerate  
    del WindowManager.renaming_digits_numerate   
    del WindowManager.renaming_cut_size       
    
    del WindowManager.renaming_suffix_material 
    del WindowManager.renaming_suffix_geometry
    del WindowManager.renaming_suffix_empty 
    del WindowManager.renaming_suffix_group  
    del WindowManager.renaming_suffix_curve 
    del WindowManager.renaming_suffix_armature    
    del WindowManager.renaming_suffix_lattice    
    del WindowManager.renaming_suffix_data      
    
    del WindowManager.renaming_suffix_data_02  
    
    bpy.utils.unregister_class(RenamingPanel)
    bpy.utils.unregister_class(AddTypeSuffix)
    bpy.utils.unregister_class(Addsuffix)
    bpy.utils.unregister_class(AddPrefix)
    bpy.utils.unregister_class(SearchAndReplace)    
    bpy.utils.unregister_class(RenamingNumerate)
    bpy.utils.unregister_class(TrimString)
    bpy.utils.unregister_class(UseObjectnameForData)
    bpy.utils.unregister_class(SuffixPanel)



if __name__ == "__main__":
    register()

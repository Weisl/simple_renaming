# This sample script demonstrates a dynamic EnumProperty with custom icons.
# The EnumProperty is populated dynamically with thumbnails of the contents of
# a chosen directory in 'enum_previews_from_directory_items'.
# Then, the same enum is displayed with different interfaces. Note that the
# generated icon previews do not have Blender IDs, which means that they can
# not be used with UILayout templates that require IDs,
# such as template_list and template_ID_preview.
#
# Other use cases:
# - make a fixed list of enum_items instead of calculating them in a function
# - generate isolated thumbnails to use as custom icons in buttons
#   and menu items
#
# For custom icons, see the template "ui_previews_custom_icon.py".
#
# For distributable scripts, it is recommended to place the icons inside the
# script directory and access it relative to the py script file for portability:
#
#    os.path.join(os.path.dirname(__file__), "images")


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
    bl_label = "Renaming panel"
    bl_idname = "RENAMING_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    
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
        row.label("add suffix by type")
        row = layout.row()
        row.prop(wm, "renaming_suffix_geometry")
        row = layout.row()
        row.prop(wm, "renaming_suffix_material")
        row = layout.row()
        row.prop(wm, "renaming_suffix_empty")
        row = layout.row()
        row.prop(wm, "renaming_suffix_curve")
        row = layout.row()
        row.prop(wm, "renaming_suffix_armature")
        row = layout.row()
        row.prop(wm, "renaming_suffix_group")
        
        row.operator("renaming.add_suffix_by_type")
        
        # Check for string length
        
class AddTypeSuffix(bpy.types.Operator):
    bl_idname="renaming.add_suffix_by_type"
    bl_label="Add type specific suffix"
    
    
    def execute(self,context):
        wm = context.window_manager
        
        geo_suffix = wm.renaming_suffix_geometry
        
        if geo_suffix is not '': 
            for obj in bpy.data.objects:
                if obj.type == 'MESH' and obj.name.endswith(geo_suffix) == False:
                        obj.name = obj.name + geo_suffix
        
        mat_suffix = wm.renaming_suffix_material         
        
        if mat_suffix is not '': 
            for mat in bpy.data.materials:
                if mat.name.endswith(mat_suffix) == False:
                    mat.name = mat.name + mat_suffix
        
        empt_suffix = wm.renaming_suffix_empty
        
        if empt_suffix is not '': 
            for empt in bpy.data.objects:
                if empt.type == 'EMPTY' and empt.name.endswith(empt_suffix) == False:
                        empt.name = empt.name + empt_suffix
        #if wm.renaming_suffix_empty is not '': 
        #if wm.renaming_suffix_curve is not '': 
        #if wm.renaming_suffix_armature is not '': 
        #if wm.renaming_suffix_group is not '': 
        return {'FINISHED'}
       
class SearchAndReplace(bpy.types.Operator):
    bl_idname="renaming.search_replace"
    bl_label="Search and Replace"
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
        

class Addsuffix(bpy.types.Operator):
    bl_idname="renaming.add_suffix"
    bl_label="Add suffix"        

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
    
    

    def execute(self,context):
        wm = context.window_manager
        i = 1
        step = wm.renaming_base_numerate
        digits = wm.renaming_digits_numerate
        
        
        if wm.rename_only_selection == True: 
            for obj in context.selected_objects: 
                obj.name = obj.name + ('{num:{fill}{width}}'.format(num=i * step, fill='0', width= digits))
                i = i + 1 
        else: 
            for obj in bpy.data.objects:  
                obj.name = obj.name + ('{num:{fill}{width}}'.format(num=i * step, fill='0', width= digits))
                i = i + 1         
        
        return{'FINISHED'}  


            
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
            

    WindowManager.renaming_suffix_material = StringProperty(name='material', default = '')
    WindowManager.renaming_suffix_geometry = StringProperty(name='geometry', default = '')
    WindowManager.renaming_suffix_empty = StringProperty(name="empty", default = '')
    WindowManager.renaming_suffix_group = StringProperty(name="group", default = '')  
    WindowManager.renaming_suffix_curve = StringProperty(name="curve", default = '') 
    WindowManager.renaming_suffix_armature = StringProperty(name="armature", default = '')     
 
           


    bpy.utils.register_class(RenamingPanel)    
    bpy.utils.register_class(Addsuffix)
    bpy.utils.register_class(AddPrefix)
    bpy.utils.register_class(SearchAndReplace)    
    bpy.utils.register_class(RenamingNumerate)    
    bpy.utils.register_class(AddTypeSuffix)

 


    

def unregister():

    bpy.utils.unregister_class(RenamingPanel)
    bpy.utils.unregister_class(AddTypeSuffix)
    bpy.utils.unregister_class(Addsuffix)
    bpy.utils.unregister_class(AddPrefix)
    bpy.utils.unregister_class(SearchAndReplace)    
    bpy.utils.unregister_class(RenamingNumerate)



if __name__ == "__main__":
    register()

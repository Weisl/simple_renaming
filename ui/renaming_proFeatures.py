import bpy
from bpy.props import StringProperty


class RENAMING_MT_variableMenu(bpy.types.Menu):
    bl_label = "Renaming Variables"
    bl_idname = "MENU_MT_renaming_variables"

    def draw(self, context):
        layout = self.layout

        wm = bpy.context.scene

        layout.operator("object.renaming_multivariables", text="RANDOM").naming_preset = "RANDOM"
        layout.operator("object.renaming_multivariables", text="NUMBER").naming_preset = "NUMBER"
        layout.separator()
        layout.operator("object.renaming_multivariables", text="LOW").naming_preset = "LOW"
        layout.operator("object.renaming_multivariables", text="HIGH").naming_preset = "HIGH"
        layout.operator("object.renaming_multivariables", text="CAGE").naming_preset = "CAGE"
        layout.separator()
        layout.operator("object.renaming_multivariables", text='FILE').naming_preset = 'FILE'
        layout.operator("object.renaming_multivariables", text="TIME").naming_preset = "TIME"
        layout.operator("object.renaming_multivariables", text="DATE").naming_preset = "DATE"
        layout.separator()
        layout.operator("object.renaming_multivariables", text="USER1").naming_preset = "USER1"
        layout.operator("object.renaming_multivariables", text="USER2").naming_preset = "USER2"
        layout.operator("object.renaming_multivariables", text="USER3").naming_preset = "USER3"

        if wm.renaming_object_types == 'OBJECT':
            layout.separator()
            layout.operator("object.renaming_multivariables", text="PARENT").naming_preset = "PARENT"
            layout.operator("object.renaming_multivariables", text="DATA").naming_preset = "DATA"
            layout.operator("object.renaming_multivariables", text="ACTIVE").naming_preset = "ACTIVE"
            layout.operator("object.renaming_multivariables", text='FILE').naming_preset = 'OBJECT'
            layout.operator("object.renaming_multivariables", text="TYPE").naming_preset = "TYPE"
            layout.operator("object.renaming_multivariables", text="COLLECTION").naming_preset = "COLLECTION"


class VIEW3D_OT_inputVariables(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.renaming_multivariables"
    bl_label = "Simple Object Operator"

    naming_preset: StringProperty()

    def execute(self, context):
        # wm = context.scene
        # replaceName = VariableReplacer.replaceInputString(context, wm.renaming_newName)

        # The print function works fine
        naming_preset = self.naming_preset
        # print (self.naming_preset)
        name_var = ""

        # print('T changed to ', naming_preset)
        if naming_preset == 'FILE':
            name_var = "@f"
        if naming_preset == 'OBJECT':
            name_var = "@o"
        if naming_preset == "HIGH":
            name_var = "@h"
        if naming_preset == "LOW":
            name_var = "@l"
        if naming_preset == "CAGE":
            name_var = "@b"
        if naming_preset == "DATE":
            name_var = "@d"
        if naming_preset == "ACTIVE":
            name_var = "@a"
        if naming_preset == "USER1":
            name_var = "@u1"
        if naming_preset == "USER2":
            name_var = "@u2"
        if naming_preset == "USER3":
            name_var = "@u3"
        if naming_preset == "TIME":
            name_var = "@i"
        if naming_preset == "TYPE":
            name_var = "@t"
        if naming_preset == "PARENT":
            name_var = "@p"
        if naming_preset == "DATA":
            name_var = "@m"
        if naming_preset == "NUMBER":
            name_var = "@n"
        if naming_preset == "RANDOM":
            name_var = "@r"
        if naming_preset == "COLLECTION":
            name_var = "@c"

        scn = context.scene
        if scn.renaming_inputContext == 'newName':
            context.scene.renaming_newName += str(name_var)
        if scn.renaming_inputContext == 'prefix':
            context.scene.renaming_prefix += str(name_var)
        if scn.renaming_inputContext == 'suffix':
            context.scene.renaming_suffix += str(name_var)
        if scn.renaming_inputContext == 'search':
            context.scene.renaming_search += str(name_var)
        if scn.renaming_inputContext == 'replace':
            context.scene.renaming_replace += str(name_var)

        return {'FINISHED'}

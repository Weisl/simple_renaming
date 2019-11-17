import bpy
from .renaming_utilities import getRenamingList,trimString

class VIEW3D_PT_renaming_popup(bpy.types.Panel):
    """Tooltip"""
    bl_idname = "renaming.popup"
    bl_label = "Renaming Info"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Rename"
    bl_ui_units_x = 30
    bl_options = {'DEFAULT_CLOSED'}

    message: bpy.props.StringProperty(
        name="message",
        description="message",
        default=''
    )

    def draw(self, context):
        wm = bpy.context.scene
        layout = self.layout
        box = layout.box()

        if len(wm.renaming_messages.message) <= 0:
            box.label(text="No Objects Renamed", icon="INFO")
        else:
            i = 0
            for msg in wm.renaming_messages.message:
                if msg is not None:
                    if msg['warning'] == False:
                        if (msg['newName'] is not None and msg['oldName'] is not None) and msg['oldName'] != msg[
                            'newName']:

                            if i == 0:
                                row = box.row(align=True)
                                row.alignment = 'EXPAND'
                                row.label(text="OBJECT TYPE")
                                row.label(text="NEW NAME")
                                row.label(text="OLD NAME")
                                row.separator()

                            row = box.row(align=True)
                            row.alignment = 'EXPAND'

                            if msg['obType'] is not False and msg['obIcon'] is not False:
                                row.label(text=str(msg['obType']), icon=msg['obIcon'])
                                # row.label(text = str(msg['obType']), icon = 'INFO')
                            else:
                                row.label(text=str(wm.renaming_object_types))

                            row.label(text=str(msg['newName']), icon='FILE_TICK')
                            row.label(text=str(msg['oldName']))

                            i += 1

                    else: #if msg['warning'] == True
                        if msg['newName'] is not None and msg['oldName'] is not None:
                            box.label(text="Warning", icon="ERROR")
                            box.label(text="       " + "Name: " + str(msg['oldName']))
                            box.label(text="       " + msg['warning'])
                        else:
                            box.label(text="Warning", icon="ERROR")
                            box.label(text="       " + msg['warning'])
            if i == 0:
                box.label(text="No Objects Renamed", icon="INFO")
        wm.renaming_messages.clear()


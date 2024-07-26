import bpy


class VIEW3D_PT_error_popup(bpy.types.Panel):
    """Tooltip"""
    bl_idname = "POPUP_PT_error"
    bl_label = "Renaming Info"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_ui_units_x = 30

    def draw(self, context):

        layout = self.layout
        box = layout.box()
        wm = context.scene

        messages = wm.renaming_error_messages

        if len(messages.message) <= 0:
            box.label(text="Unknown Error", icon="INFO")
        else:
            for msg in messages.message:
                if msg is not None:
                    row = box.row(align=False)
                    # row.alignment = 'EXPAND'

                    if msg['isError']:
                        row.label(text=str('Error'), icon='ERROR')
                        row = box.row(align=False)
                        row.label(text=str(msg['message']), icon='ERROR')
                    else:
                        row.label(text=str('Warning'), icon='ERROR')
                        row = box.row(align=False)
                        row.label(text=str(msg['message']), icon='CANCEL')

        messages.clear()
        return


class VIEW3D_PT_info_popup(bpy.types.Panel):
    """Tooltip"""
    bl_idname = "POPUP_PT_info"
    bl_label = "Renaming Info"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_ui_units_x = 30

    def draw(self, context):

        layout = self.layout

        box = layout.box()
        wm = context.scene
        infos = wm.renaming_info_messages

        if len(infos.message) <= 0:
            box.label(text="No Objects Validated", icon="INFO")
        else:
            i = 0
            for msg in infos.message:
                if msg is not None:
                    if (msg['message'] is not None):

                        row = box.row(align=True)
                        row.alignment = 'EXPAND'

                        if msg['obType'] is not False and msg['obIcon'] is not False:
                            row.label(text=str(msg['obType']), icon=msg['obIcon'])
                            # row.label(text = str(msg['obType']), icon = 'INFO')
                        else:
                            row.label(text=str(wm.renaming_object_types))

                        row.label(text=str(msg['assetName']), icon='FILE_TICK')
                        row.label(text=str(msg['oldName']))

                        i += 1

        infos.clear()


class VIEW3D_PT_renaming_popup(bpy.types.Panel):
    """Tooltip"""
    bl_idname = "POPUP_PT_popup"
    bl_label = "Renaming Info"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_ui_units_x = 30

    def draw(self, context):
        wm = context.scene

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

                    else:  # if msg['warning'] == True
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

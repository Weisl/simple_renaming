import time

import bpy

from .renaming_operators import getAllModifiers, \
    getAllParticleNames, getAllParticleSettingsNames, getAllDataNames
from .renaming_operators import switch_to_edit_mode, numerate_entity_name
from ..operators.renaming_utilities import get_renaming_list, call_renaming_popup, call_error_popup, apply_rename, report_rename_warnings, log_timing
from ..variable_replacer.variable_replacer import VariableReplacer


class VIEW3D_OT_replace_name(bpy.types.Operator):
    bl_idname = "renaming.name_replace"
    bl_label = "Replace Names"
    bl_description = "replaces the names of the objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        scene = context.scene

        replaceName = scene.renaming_new_name
        renaming_list, switch_edit_mode, errMsg = get_renaming_list(context)

        if errMsg is not None:
            error_msg = scene.renaming_error_messages
            error_msg.add_message(errMsg)
            call_error_popup(context)
            return {'CANCELLED'}

        old_mode = context.mode
        t_start = time.perf_counter()

        # settings for numerating the new name
        msg = scene.renaming_messages
        conflicts = 0
        protected = 0

        per_object_types = {'SHAPEKEYS', 'VERTEXGROUPS', 'UVMAPS', 'COLORATTRIBUTES', 'ATTRIBUTES', 'BONE'}
        per_obj_owner_items = {
            'SHAPEKEYS': lambda o: o.key_blocks,
            'VERTEXGROUPS': lambda o: o.vertex_groups,
            'UVMAPS': lambda o: o.uv_layers,
            'COLORATTRIBUTES': lambda o: o.color_attributes,
            'ATTRIBUTES': lambda o: o.attributes,
            # EditBone.id_data and plain Bone.id_data are both the Armature
            # (edit_bones / bones directly); PoseBone.id_data is the owning
            # Object instead, so its bones live one level down at o.data.bones.
            'BONE': lambda o: (o.edit_bones if old_mode == 'EDIT_ARMATURE'
                               else (o.data.bones if o.bl_rna.identifier == 'Object' else o.bones)),
        }

        particleSettingsList = set()
        particleList = set()
        dataList = set()
        modifierNamesList = set()

        if scene.renaming_object_types == 'PARTICLESYSTEM':
            particleList = set(getAllParticleNames())
        if scene.renaming_object_types == 'PARTICLESETTINGS':
            particleSettingsList = set(getAllParticleSettingsNames())
        if scene.renaming_object_types == 'MODIFIERS':
            modifierNamesList = set(getAllModifiers())
        if scene.renaming_object_types == 'DATA':
            dataList = set(getAllDataNames())

        current_owner = None
        per_obj_name_list = set()

        # OBJECT is the one type whose variables (@o, and the no-parent/
        # no-data fallbacks of @p/@m) read the entity's own *current* name
        # directly, so its replacement string must be computed from the real
        # name before that name gets parked under a placeholder below.
        precomputed_replace_names = {}
        if scene.renaming_use_enumerate and scene.renaming_object_types == 'OBJECT':
            VariableReplacer.reset()
            VariableReplacer.prepare(context)
            for entity in renaming_list:
                if entity is not None:
                    precomputed_replace_names[id(entity)] = VariableReplacer.replaceInputString(
                        context, scene.renaming_new_name, entity)

        # Entities about to be renamed shouldn't block each other (or
        # themselves) just because their old name still matches the target
        # naming pattern — e.g. reordering a subset of an already-numbered
        # "spine_001..006" chain back onto base name "spine" would otherwise
        # collide with (or snap back to) names that are about to be vacated
        # by this very rename. Park them under unique placeholder names
        # first so collision-avoidance only ever sees names belonging to
        # entities that are NOT part of this rename. This applies to every
        # type, not just per-object sub-items — plain OBJECT/MATERIAL/...
        # renumbering is just as prone to an entity "snapping back" to its
        # own old slot the moment the target order doesn't match the order
        # its old numeric suffixes were assigned in.
        real_old_names = {}
        if scene.renaming_use_enumerate:
            for idx, e in enumerate(renaming_list):
                if e is not None:
                    real_old_names[id(e)] = e.name
                    try:
                        e.name = f"__renaming_tmp_{idx}__"
                    except AttributeError:
                        pass  # read-only (e.g. library-linked) — leave it under its real name

        if not precomputed_replace_names:
            VariableReplacer.reset()
            VariableReplacer.prepare(context)

        if len(str(replaceName)) > 0:  # New name != empty
            if len(renaming_list) > 0:  # List of objects to rename != empty
                for entity in renaming_list:
                    if entity is not None:

                        if scene.renaming_object_types in per_object_types:
                            owner = entity.id_data
                            if owner != current_owner:
                                current_owner = owner
                                VariableReplacer.reset()
                                per_obj_name_list = {item.name for item in per_obj_owner_items[scene.renaming_object_types](owner)}

                        if id(entity) in precomputed_replace_names:
                            replaceName = precomputed_replace_names[id(entity)]
                        else:
                            replaceName = VariableReplacer.replaceInputString(context, scene.renaming_new_name, entity)

                        oldName = real_old_names.get(id(entity))
                        new_name = ''

                        if not scene.renaming_use_enumerate:
                            _, warning, is_protected = apply_rename(scene, entity, replaceName, msg, old_name=oldName)
                            if is_protected:
                                protected += 1
                            elif warning:
                                conflicts += 1

                        else:  # if scene.renaming_use_enumerate == True

                            if scene.renaming_object_types == 'OBJECT':
                                new_name = numerate_entity_name(context, replaceName, bpy.data.objects, entity.name)

                            elif scene.renaming_object_types == 'MATERIAL':
                                new_name = numerate_entity_name(context, replaceName, bpy.data.materials, entity.name)

                            elif scene.renaming_object_types == 'IMAGE':
                                new_name = numerate_entity_name(context, replaceName, bpy.data.images, entity.name)

                            elif scene.renaming_object_types == 'DATA':
                                new_name, dataList = numerate_entity_name(context, replaceName, dataList, entity.name,
                                                                          return_type_list=True)

                            elif scene.renaming_object_types == 'COLLECTION':
                                new_name = numerate_entity_name(context, replaceName, bpy.data.collections, entity.name)

                            elif scene.renaming_object_types == 'ACTIONS':
                                new_name = numerate_entity_name(context, replaceName, bpy.data.actions, entity.name)

                            elif scene.renaming_object_types == 'NODE_GROUPS':
                                new_name = numerate_entity_name(context, replaceName, bpy.data.node_groups, entity.name)

                            elif scene.renaming_object_types in per_object_types:
                                new_name, per_obj_name_list = numerate_entity_name(context, replaceName,
                                                                                   per_obj_name_list, entity.name,
                                                                                   return_type_list=True)

                            elif scene.renaming_object_types == 'MODIFIERS':
                                new_name, modifierNamesList = numerate_entity_name(context, replaceName,
                                                                                   modifierNamesList, entity.name,
                                                                                   return_type_list=True)

                            elif scene.renaming_object_types == 'PARTICLESYSTEM':
                                new_name, particleList = numerate_entity_name(context, replaceName,
                                                                              particleList, entity.name,
                                                                              return_type_list=True)

                            elif scene.renaming_object_types == 'PARTICLESETTINGS':
                                new_name, particleSettingsList = numerate_entity_name(context, replaceName,
                                                                                      particleSettingsList, entity.name,
                                                                                      return_type_list=True)

                            _, warning, is_protected = apply_rename(scene, entity, new_name, msg, old_name=oldName)
                            if is_protected:
                                protected += 1
                            elif warning:
                                conflicts += 1


        else:  # len(str(replaceName)) <= 0
            msg.add_message(None, None, warning="Insert a valid string to replace names")

        log_timing(context, "name_replace", t_start, len(renaming_list))
        report_rename_warnings(self, conflicts, protected)
        call_renaming_popup(context)
        if switch_edit_mode:
            switch_to_edit_mode(context)
        return {'FINISHED'}

bl_info = {
    "name": "Auto Bone Aligner",
    "author": "AI Assistant",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > N-Panel > Game Export",
    "description": "Bake mesh relative offset to a specific bone for UE/Unity direct attachment.",
    "category": "Object",
}

import bpy


# -------------------------------------------------------------------
# Scene properties (persistent UI state)
# -------------------------------------------------------------------
class AlignerSceneProperties(bpy.types.PropertyGroup):
    target_mesh: bpy.props.PointerProperty(
        name="Target Mesh",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'MESH',
        description="The mesh object whose transform will be baked",
    )
    target_armature: bpy.props.PointerProperty(
        name="Target Armature",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE',
        description="The armature containing the target bone",
    )
    target_bone: bpy.props.StringProperty(
        name="Target Bone",
        description="Bone to calculate the relative offset against",
    )


# -------------------------------------------------------------------
# Core operator
# -------------------------------------------------------------------
class ALIGNER_OT_bake_offset(bpy.types.Operator):
    bl_idname = "aligner.bake_offset"
    bl_label = "Bake Offset to Origin"
    bl_description = (
        "Calculate the mesh's local-space offset relative to the chosen bone "
        "and bake it as the mesh's new default transform"
    )
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        props = scene.aligner_props
        return props.target_mesh is not None and props.target_armature is not None

    def execute(self, context):
        scene = context.scene
        props = scene.aligner_props

        mesh_obj = props.target_mesh
        armature_obj = props.target_armature
        bone_name = props.target_bone

        # --- Validation --------------------------------------------------
        if mesh_obj is None:
            self.report({'ERROR'}, "Target Mesh is not set.")
            return {'CANCELLED'}
        if armature_obj is None:
            self.report({'ERROR'}, "Target Armature is not set.")
            return {'CANCELLED'}
        if mesh_obj.type != 'MESH':
            self.report({'ERROR'}, "Target Mesh must be a MESH object.")
            return {'CANCELLED'}
        if armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Target Armature must be an ARMATURE object.")
            return {'CANCELLED'}
        if not bone_name:
            self.report({'ERROR'}, "No bone selected.")
            return {'CANCELLED'}
        pose_bone = armature_obj.pose.bones.get(bone_name)
        if pose_bone is None:
            self.report({'ERROR'}, f"Bone '{bone_name}' not found in armature '{armature_obj.name}'.")
            return {'CANCELLED'}

        # --- Ensure OBJECT mode ------------------------------------------
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # --- Core matrix math --------------------------------------------
        bone_world = armature_obj.matrix_world @ pose_bone.matrix

        # Step 1-4: Move mesh origin to the bone's world-space position
        # Use 3D cursor as a pivot — vertices stay in place, only the
        # object-level origin shifts.
        saved_cursor = bpy.context.scene.cursor.location.copy()
        bpy.context.scene.cursor.location = bone_world.translation
        bpy.context.view_layer.objects.active = mesh_obj
        mesh_obj.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.scene.cursor.location = saved_cursor

        # Step 5-6: Calculate relative offset (origin is now at the bone)
        mesh_world = mesh_obj.matrix_world.copy()
        relative_matrix = bone_world.inverted() @ mesh_world

        # Step 7-8: Apply the relative offset and freeze transforms
        mesh_obj.matrix_world = relative_matrix
        bpy.ops.object.transform_apply(
            location=True,
            rotation=True,
            scale=True,
        )

        # Step 9: Restore the top-most parent scale (UE import compensation)
        top_parent = armature_obj
        while top_parent.parent:
            top_parent = top_parent.parent
        top_scale = top_parent.matrix_world.to_scale()
        mesh_obj.scale = top_scale

        self.report({'INFO'}, f"Offset baked successfully. Mesh origin reset.")
        return {'FINISHED'}


# -------------------------------------------------------------------
# UI Panel
# -------------------------------------------------------------------
class ALIGNER_PT_bone_aligner(bpy.types.Panel):
    bl_idname = "ALIGNER_PT_bone_aligner"
    bl_label = "Bone Aligner"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Game Export"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.aligner_props

        # Setup section
        layout.label(text="Setup", icon='SETTINGS')
        layout.prop(props, "target_mesh")
        layout.prop(props, "target_armature")

        # Bone picker (prop_search)
        if props.target_armature:
            layout.prop_search(
                props,
                "target_bone",
                props.target_armature.data,
                "bones",
                text="Bone",
            )
        else:
            layout.prop(props, "target_bone", text="Bone")

        # Action button
        layout.separator()
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator(
            "aligner.bake_offset",
            text="Bake Offset to Origin",
            icon='FILE_TICK',
        )

        # Hint
        layout.separator()
        layout.label(
            text="Note: Mesh will jump to origin after baking.",
            icon='INFO',
        )


# -------------------------------------------------------------------
# Registration
# -------------------------------------------------------------------
classes = (
    AlignerSceneProperties,
    ALIGNER_OT_bake_offset,
    ALIGNER_PT_bone_aligner,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.aligner_props = bpy.props.PointerProperty(
        type=AlignerSceneProperties
    )


def unregister():
    del bpy.types.Scene.aligner_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)



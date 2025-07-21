
import bpy

class MIKTOS_PT_main_panel(bpy.types.Panel):
    bl_label = "Miktos AI"
    bl_idname = "MIKTOS_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Miktos"

    def draw(self, context):
        layout = self.layout
        
        # Connection status
        layout.label(text="AI Bridge Connection:")
        layout.operator("miktos.connect_bridge")
        
        # Texture generation
        layout.separator()
        layout.label(text="Texture Generation:")
        layout.prop(context.scene, "miktos_prompt")
        layout.operator("miktos.generate_texture")

def register():
    bpy.utils.register_class(MIKTOS_PT_main_panel)
    bpy.types.Scene.miktos_prompt = bpy.props.StringProperty(
        name="Prompt",
        description="AI texture generation prompt",
        default="brick wall texture"
    )

def unregister():
    bpy.utils.unregister_class(MIKTOS_PT_main_panel)
    del bpy.types.Scene.miktos_prompt

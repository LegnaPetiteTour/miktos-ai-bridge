
import bpy
import requests
import json

class MIKTOS_OT_connect_bridge(bpy.types.Operator):
    bl_idname = "miktos.connect_bridge"
    bl_label = "Connect to AI Bridge"
    bl_description = "Connect to Miktos AI Bridge"

    def execute(self, context):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                self.report({'INFO'}, "Connected to AI Bridge")
            else:
                self.report({'ERROR'}, "AI Bridge not responding")
        except Exception as e:
            self.report({'ERROR'}, f"Connection failed: {str(e)}")
        
        return {'FINISHED'}

class MIKTOS_OT_generate_texture(bpy.types.Operator):
    bl_idname = "miktos.generate_texture"
    bl_label = "Generate Texture"
    bl_description = "Generate AI texture for selected object"

    def execute(self, context):
        prompt = context.scene.miktos_prompt
        
        if not prompt:
            self.report({'ERROR'}, "Please enter a prompt")
            return {'CANCELLED'}
        
        try:
            # Send texture generation request
            data = {
                "command": "generate_texture",
                "parameters": {
                    "prompt": prompt,
                    "size": [1024, 1024],
                    "maps": ["diffuse"]
                }
            }
            
            response = requests.post(
                "http://localhost:8000/api/v1/execute-command",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.report({'INFO'}, "Texture generation started")
                else:
                    self.report({'ERROR'}, f"Generation failed: {result.get('message')}")
            else:
                self.report({'ERROR'}, "AI Bridge request failed")
                
        except Exception as e:
            self.report({'ERROR'}, f"Request failed: {str(e)}")
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MIKTOS_OT_connect_bridge)
    bpy.utils.register_class(MIKTOS_OT_generate_texture)

def unregister():
    bpy.utils.unregister_class(MIKTOS_OT_connect_bridge)
    bpy.utils.unregister_class(MIKTOS_OT_generate_texture)


import bpy
import bmesh
import json
import asyncio
import websockets
from websockets.server import serve
import threading

class MiktosBridge:
    def __init__(self):
        self.server = None
        self.port = 9999
        
    async def handle_command(self, websocket, path):
        """Handle incoming commands from Miktos AI Bridge"""
        async for message in websocket:
            try:
                command = json.loads(message)
                response = await self.process_command(command)
                await websocket.send(json.dumps(response))
            except Exception as e:
                error_response = {
                    "status": "error",
                    "error": str(e)
                }
                await websocket.send(json.dumps(error_response))
    
    async def process_command(self, command):
        """Process commands from AI Bridge"""
        cmd_type = command.get("command")
        data = command.get("data", {})
        
        if cmd_type == "ping":
            return {"status": "success", "message": "pong"}
        
        elif cmd_type == "get_scene_info":
            return self.get_scene_info()
        
        elif cmd_type == "apply_texture":
            return self.apply_texture(data)
        
        elif cmd_type == "create_primitive":
            return self.create_primitive(data)
        
        else:
            return {"status": "error", "error": f"Unknown command: {cmd_type}"}
    
    def get_scene_info(self):
        """Get current scene information"""
        scene = bpy.context.scene
        objects = [obj.name for obj in scene.objects]
        
        return {
            "status": "success",
            "data": {
                "scene_name": scene.name,
                "objects": objects,
                "frame_current": scene.frame_current,
                "frame_start": scene.frame_start,
                "frame_end": scene.frame_end
            }
        }
    
    def apply_texture(self, data):
        """Apply texture to object"""
        try:
            object_name = data.get("object_name")
            texture_path = data.get("texture_path")
            
            # Get object
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"status": "error", "error": f"Object {object_name} not found"}
            
            # Create material
            material = bpy.data.materials.new(name=f"{object_name}_material")
            material.use_nodes = True
            
            # Clear default nodes
            material.node_tree.nodes.clear()
            
            # Add shader nodes
            bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
            output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
            tex_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')
            
            # Load texture
            tex_node.image = bpy.data.images.load(texture_path)
            
            # Link nodes
            material.node_tree.links.new(tex_node.outputs[0], bsdf.inputs[0])
            material.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
            
            # Assign material to object
            if obj.data.materials:
                obj.data.materials[0] = material
            else:
                obj.data.materials.append(material)
            
            return {"status": "success", "message": f"Texture applied to {object_name}"}
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def start_server(self):
        """Start WebSocket server"""
        async def run_server():
            self.server = await serve(self.handle_command, "localhost", self.port)
            await self.server.wait_closed()
        
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(run_server())
        
        thread = threading.Thread(target=run_in_thread)
        thread.daemon = True
        thread.start()

# Initialize bridge when addon loads
if __name__ == "__main__":
    bridge = MiktosBridge()
    bridge.start_server()
    print("Miktos Bridge addon loaded and server started on port 9999")

"""
Blender Connector

This module provides integration with Blender via its Python API and addon system.
Supports real-time communication for texture application, scene manipulation,
and workflow automation.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import socket
import websockets
from websockets.server import serve
import subprocess
import time

from .base import BaseConnector, ConnectorStatus
from ..core.config import settings

logger = logging.getLogger(__name__)


class BlenderConnector(BaseConnector):
    """Connector for Blender integration via WebSocket communication"""
    
    def __init__(self, port: int = 9999):
        super().__init__("Blender")
        self.port = port
        self.websocket = None
        self.server = None
        self.blender_process = None
        self.addon_installed = False
        
        # Communication settings
        self.connection_timeout = 30
        self.command_timeout = 10
        
    async def connect(self, **kwargs) -> bool:
        """Establish connection to Blender"""
        try:
            self.status = ConnectorStatus.CONNECTING
            logger.info(f"Connecting to Blender on port {self.port}...")
            
            # Check if Blender is already running with our addon
            if not await self._check_blender_connection():
                # Try to start Blender with our addon
                if not await self._start_blender_with_addon():
                    self.set_error("Failed to start Blender with Miktos addon")
                    return False
            
            # Wait for WebSocket connection
            if await self._wait_for_connection():
                self.status = ConnectorStatus.CONNECTED
                logger.info("Successfully connected to Blender")
                return True
            else:
                self.set_error("Connection timeout - Blender not responding")
                return False
                
        except Exception as e:
            self.set_error(f"Connection failed: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Blender"""
        try:
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
            
            if self.server:
                self.server.close()
                await self.server.wait_closed()
                self.server = None
            
            self.status = ConnectorStatus.DISCONNECTED
            logger.info("Disconnected from Blender")
            return True
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """Check if connection is active"""
        if self.status != ConnectorStatus.CONNECTED or not self.websocket:
            return False
        
        try:
            # Send ping to check connection
            response = await self._send_command({
                "command": "ping",
                "data": {}
            })
            return response.get("status") == "success"
        except:
            self.status = ConnectorStatus.DISCONNECTED
            return False
    
    async def get_scene_info(self) -> Dict[str, Any]:
        """Get current scene information from Blender"""
        try:
            response = await self._send_command({
                "command": "get_scene_info",
                "data": {}
            })
            
            if response.get("status") == "success":
                return response.get("data", {})
            else:
                raise Exception(f"Failed to get scene info: {response.get('error')}")
                
        except Exception as e:
            logger.error(f"Error getting scene info: {e}")
            return {}
    
    async def apply_texture(self, object_name: str, texture_path: str, **kwargs) -> bool:
        """Apply texture to specified object in Blender"""
        try:
            command_data = {
                "command": "apply_texture",
                "data": {
                    "object_name": object_name,
                    "texture_path": str(texture_path),
                    "material_name": kwargs.get("material_name", f"{object_name}_material"),
                    "texture_type": kwargs.get("texture_type", "diffuse"),
                    "uv_unwrap": kwargs.get("uv_unwrap", True)
                }
            }
            
            response = await self._send_command(command_data)
            
            if response.get("status") == "success":
                logger.info(f"Successfully applied texture to {object_name}")
                return True
            else:
                logger.error(f"Failed to apply texture: {response.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying texture: {e}")
            return False
    
    async def execute_script(self, script: str) -> Dict[str, Any]:
        """Execute Python script in Blender"""
        try:
            response = await self._send_command({
                "command": "execute_script",
                "data": {
                    "script": script
                }
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error executing script: {e}")
            return {"status": "error", "error": str(e)}
    
    async def create_primitive(self, primitive_type: str, location: List[float] = [0, 0, 0], **kwargs) -> bool:
        """Create a primitive object in Blender"""
        try:
            response = await self._send_command({
                "command": "create_primitive",
                "data": {
                    "type": primitive_type,
                    "location": location,
                    "rotation": kwargs.get("rotation", [0, 0, 0]),
                    "scale": kwargs.get("scale", [1, 1, 1]),
                    "name": kwargs.get("name")
                }
            })
            
            return response.get("status") == "success"
            
        except Exception as e:
            logger.error(f"Error creating primitive: {e}")
            return False
    
    async def get_selected_objects(self) -> List[str]:
        """Get list of currently selected objects"""
        try:
            response = await self._send_command({
                "command": "get_selected_objects",
                "data": {}
            })
            
            if response.get("status") == "success":
                return response.get("data", {}).get("objects", [])
            return []
            
        except Exception as e:
            logger.error(f"Error getting selected objects: {e}")
            return []
    
    # Private methods
    async def _check_blender_connection(self) -> bool:
        """Check if Blender is running and accessible"""
        try:
            # Try to connect to existing WebSocket
            uri = f"ws://localhost:{self.port}"
            websocket = await websockets.connect(uri, timeout=2)
            await websocket.close()
            return True
        except:
            return False
    
    async def _start_blender_with_addon(self) -> bool:
        """Start Blender with Miktos addon"""
        try:
            # Path to our Blender addon
            addon_path = Path(__file__).parent.parent.parent / "blender_addon"
            
            if not addon_path.exists():
                logger.error("Blender addon not found - creating basic addon")
                await self._create_basic_addon(addon_path)
            
            # Start Blender with addon
            blender_cmd = [
                settings.blender_path,
                "--background",
                "--python", str(addon_path / "miktos_bridge.py")
            ]
            
            logger.info(f"Starting Blender with Miktos addon: {settings.blender_path}")
            self.blender_process = subprocess.Popen(
                blender_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give Blender time to start
            await asyncio.sleep(5)
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Blender: {e}")
            return False
    
    async def _wait_for_connection(self) -> bool:
        """Wait for Blender to establish WebSocket connection"""
        start_time = time.time()
        
        while time.time() - start_time < self.connection_timeout:
            try:
                if await self._check_blender_connection():
                    # Establish persistent connection
                    uri = f"ws://localhost:{self.port}"
                    self.websocket = await websockets.connect(uri)
                    return True
            except:
                pass
            
            await asyncio.sleep(1)
        
        return False
    
    async def _send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Send command to Blender via WebSocket"""
        if not self.websocket:
            raise Exception("No WebSocket connection to Blender")
        
        try:
            # Send command
            await self.websocket.send(json.dumps(command))
            
            # Wait for response
            response_data = await asyncio.wait_for(
                self.websocket.recv(),
                timeout=self.command_timeout
            )
            
            return json.loads(response_data)
            
        except asyncio.TimeoutError:
            raise Exception("Command timeout - Blender not responding")
        except Exception as e:
            raise Exception(f"Communication error: {str(e)}")
    
    async def _create_basic_addon(self, addon_path: Path):
        """Create basic Blender addon for Miktos integration"""
        addon_path.mkdir(parents=True, exist_ok=True)
        
        # Create basic addon file
        addon_content = '''
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
'''
        
        addon_file = addon_path / "miktos_bridge.py"
        with open(addon_file, 'w') as f:
            f.write(addon_content)
        
        logger.info(f"Created basic Blender addon at {addon_file}")


# Additional utility functions
async def get_blender_installation_path():
    """Detect Blender installation path"""
    import shutil
    
    # Common Blender executable names
    blender_names = ["blender", "blender.exe", "Blender"]
    
    for name in blender_names:
        path = shutil.which(name)
        if path:
            return path
    
    # Check common installation directories
    import platform
    system = platform.system()
    
    if system == "Darwin":  # macOS
        common_paths = [
            "/Applications/Blender.app/Contents/MacOS/Blender",
            "/Applications/Blender.app/Contents/MacOS/blender"
        ]
    elif system == "Windows":
        common_paths = [
            "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
            "C:\\Program Files (x86)\\Blender Foundation\\Blender\\blender.exe"
        ]
    else:  # Linux
        common_paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/opt/blender/blender"
        ]
    
    for path in common_paths:
        if Path(path).exists():
            return path
    
    return None

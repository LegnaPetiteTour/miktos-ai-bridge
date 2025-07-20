#!/usr/bin/env python3
"""
Miktos Platform - Development Setup Script

This script helps set up the complete development environment for Miktos,
including all dependencies, configurations, and initial setup.
"""

import subprocess
import sys
import os
import json
import shutil
from pathlib import Path
import platform
import urllib.request


class MiktosSetup:
    """Miktos Platform development setup"""
    
    def __init__(self):
        self.system = platform.system()
        self.project_root = Path(__file__).parent
        self.setup_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log setup messages"""
        log_entry = f"[{level}] {message}"
        self.setup_log.append(log_entry)
        print(log_entry)
    
    def run_command(self, command: str, cwd: Path = None) -> bool:
        """Run shell command and return success status"""
        try:
            cwd = cwd or self.project_root
            self.log(f"Running: {command}")
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log(f"✅ Command successful")
                return True
            else:
                self.log(f"❌ Command failed: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Command error: {str(e)}", "ERROR")
            return False
    
    def check_python_version(self) -> bool:
        """Check Python version compatibility"""
        self.log("Checking Python version...")
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 11:
            self.log(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
            return True
        else:
            self.log(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible. Need Python 3.11+", "ERROR")
            return False
    
    def setup_virtual_environment(self) -> bool:
        """Set up Python virtual environment"""
        self.log("Setting up virtual environment...")
        
        venv_path = self.project_root / "venv"
        
        if venv_path.exists():
            self.log("Virtual environment already exists")
            return True
        
        # Create virtual environment
        if self.run_command(f"python -m venv {venv_path}"):
            self.log("✅ Virtual environment created")
            return True
        else:
            self.log("❌ Failed to create virtual environment", "ERROR")
            return False
    
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        self.log("Installing Python dependencies...")
        
        # Determine pip command based on OS
        venv_path = self.project_root / "venv"
        if self.system == "Windows":
            pip_cmd = str(venv_path / "Scripts" / "pip")
        else:
            pip_cmd = str(venv_path / "bin" / "pip")
        
        # Install requirements
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            if self.run_command(f"{pip_cmd} install -r {requirements_file}"):
                self.log("✅ Python dependencies installed")
                return True
            else:
                self.log("❌ Failed to install Python dependencies", "ERROR")
                return False
        else:
            self.log("❌ requirements.txt not found", "ERROR")
            return False
    
    def setup_environment_file(self) -> bool:
        """Set up environment configuration file"""
        self.log("Setting up environment configuration...")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if env_file.exists():
            self.log("Environment file already exists")
            return True
        
        # Create .env from example or default
        env_content = """# Miktos AI Bridge Configuration

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=info

# ComfyUI Configuration
COMFYUI_HOST=localhost
COMFYUI_PORT=8188
COMFYUI_URL=http://localhost:8188
COMFYUI_MODELS_PATH=./models
COMFYUI_OUTPUT_PATH=./output

# Database
DATABASE_URL=sqlite:///./miktos.db

# Redis (for Celery)
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs (optional)
HUGGINGFACE_API_KEY=your-hf-key-here
OPENAI_API_KEY=your-openai-key-here

# Blender Integration
BLENDER_PATH=blender
BLENDER_ADDON_PORT=9999

# Output Directories
OUTPUT_DIR=./output
TEXTURE_OUTPUT_DIR=./output/textures
MODEL_OUTPUT_DIR=./output/models
"""
        
        try:
            with open(env_file, 'w') as f:
                f.write(env_content)
            self.log("✅ Environment file created")
            return True
        except Exception as e:
            self.log(f"❌ Failed to create environment file: {str(e)}", "ERROR")
            return False
    
    def create_directories(self) -> bool:
        """Create necessary directories"""
        self.log("Creating project directories...")
        
        directories = [
            "output",
            "output/textures",
            "output/models", 
            "output/workflows",
            "models",
            "logs",
            "temp",
            "blender_addon"
        ]
        
        try:
            for dir_name in directories:
                dir_path = self.project_root / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
                self.log(f"Created directory: {dir_name}")
            
            self.log("✅ All directories created")
            return True
        except Exception as e:
            self.log(f"❌ Failed to create directories: {str(e)}", "ERROR")
            return False
    
    def check_external_dependencies(self) -> dict:
        """Check for external dependencies"""
        self.log("Checking external dependencies...")
        
        dependencies = {
            "node": {"command": "node --version", "required": False},
            "npm": {"command": "npm --version", "required": False},
            "blender": {"command": "blender --version", "required": False},
            "redis-server": {"command": "redis-server --version", "required": False},
            "git": {"command": "git --version", "required": True}
        }
        
        results = {}
        
        for dep, info in dependencies.items():
            try:
                result = subprocess.run(
                    info["command"],
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    results[dep] = {"available": True, "version": version}
                    self.log(f"✅ {dep}: {version}")
                else:
                    results[dep] = {"available": False, "version": None}
                    level = "ERROR" if info["required"] else "WARN"
                    self.log(f"❌ {dep}: Not available", level)
            
            except Exception as e:
                results[dep] = {"available": False, "version": None, "error": str(e)}
                level = "ERROR" if info["required"] else "WARN"
                self.log(f"❌ {dep}: Error checking - {str(e)}", level)
        
        return results
    
    def setup_blender_addon(self) -> bool:
        """Set up basic Blender addon"""
        self.log("Setting up Blender addon...")
        
        addon_dir = self.project_root / "blender_addon"
        addon_file = addon_dir / "__init__.py"
        
        if addon_file.exists():
            self.log("Blender addon already exists")
            return True
        
        # Create basic addon structure
        addon_init_content = '''
bl_info = {
    "name": "Miktos Bridge",
    "author": "Miktos Universe", 
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Miktos",
    "description": "Bridge between Blender and Miktos AI Platform",
    "category": "3D View",
}

import bpy
from . import miktos_panel
from . import miktos_operators

def register():
    miktos_panel.register()
    miktos_operators.register()

def unregister():
    miktos_panel.unregister()
    miktos_operators.unregister()

if __name__ == "__main__":
    register()
'''
        
        try:
            with open(addon_file, 'w') as f:
                f.write(addon_init_content)
            
            # Create additional addon files
            self._create_addon_files(addon_dir)
            
            self.log("✅ Blender addon structure created")
            return True
        except Exception as e:
            self.log(f"❌ Failed to create Blender addon: {str(e)}", "ERROR")
            return False
    
    def _create_addon_files(self, addon_dir: Path):
        """Create additional Blender addon files"""
        
        # Panel file
        panel_content = '''
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
'''
        
        operators_content = '''
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
'''
        
        # Write files
        with open(addon_dir / "miktos_panel.py", 'w') as f:
            f.write(panel_content)
        
        with open(addon_dir / "miktos_operators.py", 'w') as f:
            f.write(operators_content)
    
    def run_integration_test(self) -> bool:
        """Run integration test"""
        self.log("Running integration test...")
        
        test_script = self.project_root / "integration_test.py"
        if test_script.exists():
            if self.run_command(f"python {test_script}"):
                self.log("✅ Integration test completed")
                return True
            else:
                self.log("❌ Integration test failed", "ERROR")
                return False
        else:
            self.log("❌ Integration test script not found", "ERROR")
            return False
    
    def generate_setup_report(self, dependency_results: dict):
        """Generate setup completion report"""
        print("\n" + "=" * 60)
        print("🎉 MIKTOS DEVELOPMENT SETUP COMPLETE!")
        print("=" * 60)
        
        print("\n📋 Setup Summary:")
        print("✅ Python environment configured")
        print("✅ Dependencies installed")
        print("✅ Environment file created")
        print("✅ Project directories created")
        print("✅ Blender addon structure created")
        
        print("\n🔧 External Dependencies:")
        for dep, info in dependency_results.items():
            status = "✅" if info["available"] else "❌"
            version = info.get("version", "Not available")
            print(f"  {status} {dep}: {version}")
        
        print("\n🚀 Next Steps:")
        print("1. Activate virtual environment:")
        if self.system == "Windows":
            print("   .\\venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        
        print("2. Start AI Bridge:")
        print("   python main.py")
        
        print("3. Open desktop app:")
        print("   cd ../miktos-desktop")
        print("   npm run tauri dev")
        
        if not dependency_results.get("blender", {}).get("available"):
            print("\n💡 Optional: Install Blender for 3D integration")
            print("   Download from: https://www.blender.org/download/")
        
        if not dependency_results.get("redis-server", {}).get("available"):
            print("\n💡 Optional: Install Redis for background tasks")
            if self.system == "Darwin":
                print("   brew install redis")
            elif self.system == "Linux":
                print("   sudo apt-get install redis-server")
            else:
                print("   Download from: https://redis.io/download")
        
        print("\n📚 Documentation:")
        print("   • Architecture: docs/ARCHITECTURE.md")
        print("   • Getting Started: docs/GETTING_STARTED.md")
        print("   • Contributing: CONTRIBUTING.md")
        
        print("\n🧪 Testing:")
        print("   python integration_test.py")
        
        print("\n" + "=" * 60)
    
    def run_setup(self):
        """Run complete setup process"""
        print("🚀 Miktos Platform - Development Setup")
        print("=" * 40)
        
        # Check Python version
        if not self.check_python_version():
            print("❌ Setup failed: Incompatible Python version")
            return False
        
        # Setup steps
        steps = [
            ("Virtual Environment", self.setup_virtual_environment),
            ("Python Dependencies", self.install_python_dependencies),
            ("Environment Configuration", self.setup_environment_file),
            ("Project Directories", self.create_directories),
            ("Blender Addon", self.setup_blender_addon),
        ]
        
        for step_name, step_func in steps:
            self.log(f"\n📦 {step_name}")
            if not step_func():
                print(f"❌ Setup failed at: {step_name}")
                return False
        
        # Check external dependencies
        dependency_results = self.check_external_dependencies()
        
        # Generate report
        self.generate_setup_report(dependency_results)
        
        return True


def main():
    """Main setup execution"""
    setup = MiktosSetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎉 Setup completed successfully!")
        return 0
    else:
        print("\n❌ Setup failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Test script for standalone ComfyUI mode
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.config import settings
from src.comfyui.standalone_executor import StandaloneComfyUIExecutor
from src.comfyui.workflow_manager import WorkflowManager, WorkflowType

async def test_standalone_mode():
    """Test the standalone ComfyUI implementation"""
    print("🧪 Testing Standalone ComfyUI Mode")
    print("=" * 50)
    
    # Test configuration
    print(f"✅ Standalone mode enabled: {settings.comfyui_standalone_mode}")
    
    # Test standalone executor
    executor = StandaloneComfyUIExecutor()
    
    # Test connection
    connected = await executor.check_connection()
    print(f"✅ Connection test: {'PASS' if connected else 'FAIL'}")
    
    # Test queue status
    queue = await executor.get_queue_status()
    print(f"✅ Queue status: {queue}")
    
    # Test available models
    models = await executor.get_available_models()
    print(f"✅ Available models: {models}")
    
    # Test workflow manager
    workflow_manager = WorkflowManager()
    templates = workflow_manager.list_workflows()
    print(f"✅ Available workflows: {len(templates)}")
    
    for template in templates:
        print(f"   - {template.name} ({template.type.value})")
    
    # Test workflow execution
    print("\n🚀 Testing Workflow Execution")
    print("-" * 30)
    
    if templates:
        template = templates[0]  # Use first available template
        print(f"Testing workflow: {template.name}")
        
        # Create test parameters
        test_params = {
            "prompt": "A beautiful medieval texture for 3D modeling",
            "negative_prompt": "blurry, low quality",
            "steps": 20,
            "cfg": 7.0,
            "width": 512,
            "height": 512
        }
        
        try:
            result = await executor.execute_simple_generation(**test_params)
            print(f"✅ Workflow execution: {'PASS' if result else 'FAIL'}")
            if result:
                print(f"   Result: {result}")
        except Exception as e:
            print(f"❌ Workflow execution failed: {e}")
    
    print("\n🎉 Standalone mode test completed!")
    return True

if __name__ == "__main__":
    asyncio.run(test_standalone_mode())

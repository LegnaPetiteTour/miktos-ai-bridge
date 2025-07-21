#!/usr/bin/env python3
"""
Validation script to test our standalone ComfyUI implementation
"""
import sys
import os
import asyncio

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_standalone_mode():
    """Test the standalone ComfyUI implementation"""
    print("🔍 Testing Miktos AI Bridge Standalone Mode...")
    
    try:
        # Test configuration import
        print("1. Testing configuration...")
        from src.core.config import settings
        print(f"   ✅ Config loaded - Standalone mode: {settings.comfyui_standalone_mode}")
        
        # Test standalone executor import
        print("2. Testing standalone executor...")
        from src.comfyui.standalone_executor import StandaloneComfyUIExecutor
        print("   ✅ StandaloneComfyUIExecutor imported successfully")
        
        # Test executor initialization
        print("3. Testing executor initialization...")
        executor = StandaloneComfyUIExecutor()
        print("   ✅ Executor initialized successfully")
        
        # Test workflow manager
        print("4. Testing workflow manager...")
        from src.comfyui.workflow_manager import WorkflowManager
        workflow_manager = WorkflowManager()
        workflows = workflow_manager.list_workflows()
        print(f"   ✅ Workflow manager loaded {len(workflows)} workflows")
        
        for workflow in workflows:
            print(f"     - {workflow.name}: {workflow.description}")
        
        # Test simple workflow execution
        print("5. Testing workflow execution...")
        result = await executor.execute_simple_generation(
            prompt="test texture",
            negative_prompt="low quality",
            steps=20,
            cfg=7.0,
            width=512,
            height=512
        )
        print(f"   ✅ Workflow execution completed: {result['status']}")
        
        print("\n🎉 All tests passed! Standalone mode is working correctly.")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_standalone_mode())
    sys.exit(0 if result else 1)

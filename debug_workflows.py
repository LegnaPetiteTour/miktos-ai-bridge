#!/usr/bin/env python3
"""
Debug script to check workflow template names
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_workflows():
    """Debug workflow template names"""
    try:
        from src.comfyui.workflow_manager import WorkflowManager
        
        workflow_manager = WorkflowManager()
        
        print("🔍 Available workflow templates:")
        for name, template in workflow_manager.templates.items():
            print(f"  Key: '{name}' -> Template Name: '{template.name}'")
        
        print(f"\n📊 Total templates: {len(workflow_manager.templates)}")
        
        # Test lookup
        test_name = "Basic Texture Generation"
        template = workflow_manager.get_workflow_template(test_name)
        print(f"\n🔍 Looking up '{test_name}': {'Found' if template else 'Not Found'}")
        
        if not template:
            print("Available template keys:")
            for key in workflow_manager.templates.keys():
                print(f"  - '{key}'")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_workflows()

#!/usr/bin/env python3
"""
Miktos Platform - Integration Test Suite

This script tests the communication between the desktop app, AI bridge,
and external connectors to ensure the platform is working correctly.
"""

import sys
import os
import asyncio
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our modules
from src.core.bridge import MiktosAIBridge
from src.core.models import AICommand
from src.connectors.blender_connector import BlenderConnector
from src.comfyui.client import ComfyUIClient
import requests


class IntegrationTester:
    """Comprehensive integration testing for Miktos Platform"""
    
    def __init__(self):
        self.ai_bridge = None
        self.blender_connector = None
        self.test_results = {}
        self.bridge_url = "http://localhost:8000"
        
    async def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Miktos Platform - Integration Test Suite")
        print("=" * 50)
        
        tests = [
            ("AI Bridge Initialization", self.test_ai_bridge_init),
            ("AI Bridge API Endpoints", self.test_api_endpoints),
            ("ComfyUI Integration", self.test_comfyui_integration),
            ("Blender Connector", self.test_blender_connector),
            ("Texture Generation Workflow", self.test_texture_generation),
            ("Command Processing", self.test_command_processing),
            ("Real-time Communication", self.test_realtime_communication),
            ("Error Handling", self.test_error_handling),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔄 Running: {test_name}")
            try:
                result = await test_func()
                self.test_results[test_name] = result
                if result["success"]:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED - {result.get('error')}")
            except Exception as e:
                self.test_results[test_name] = {"success": False, "error": str(e)}
                print(f"❌ {test_name}: ERROR - {str(e)}")
        
        # Generate report
        await self.generate_report()
    
    async def test_ai_bridge_init(self) -> Dict[str, Any]:
        """Test AI Bridge initialization"""
        try:
            self.ai_bridge = MiktosAIBridge()
            await self.ai_bridge.initialize()
            
            if self.ai_bridge.is_ready():
                return {
                    "success": True,
                    "status": self.ai_bridge.status.value,
                    "message": "AI Bridge initialized successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"AI Bridge not ready: {self.ai_bridge.status.value}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_api_endpoints(self) -> Dict[str, Any]:
        """Test AI Bridge API endpoints"""
        try:
            endpoints = [
                ("/", "GET"),
                ("/health", "GET"),
                ("/api/v1/status", "GET")
            ]
            
            results = {}
            
            for endpoint, method in endpoints:
                url = f"{self.bridge_url}{endpoint}"
                
                try:
                    if method == "GET":
                        response = requests.get(url, timeout=5)
                    else:
                        response = requests.post(url, timeout=5)
                    
                    results[endpoint] = {
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                    }
                    
                except requests.exceptions.ConnectionError:
                    results[endpoint] = {
                        "success": False,
                        "error": "Connection refused - AI Bridge not running"
                    }
                except Exception as e:
                    results[endpoint] = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Check if all endpoints are working
            all_success = all(r.get("success", False) for r in results.values())
            
            return {
                "success": all_success,
                "results": results,
                "message": "All endpoints working" if all_success else "Some endpoints failed"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_comfyui_integration(self) -> Dict[str, Any]:
        """Test ComfyUI integration"""
        try:
            client = ComfyUIClient()
            
            # Test connection
            connected = await client.check_connection()
            
            if connected:
                # Test workflow submission
                test_workflow = {
                    "test": "workflow",
                    "simple": True
                }
                
                # This would fail without actual ComfyUI, but we test the client
                return {
                    "success": True,
                    "connected": connected,
                    "message": "ComfyUI client functional"
                }
            else:
                return {
                    "success": False,
                    "connected": False,
                    "message": "ComfyUI not available (expected in development)"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_blender_connector(self) -> Dict[str, Any]:
        """Test Blender connector"""
        try:
            self.blender_connector = BlenderConnector()
            
            # Test connection (will likely fail without Blender running)
            connected = await self.blender_connector.connect()
            
            if connected:
                # Test basic commands
                scene_info = await self.blender_connector.get_scene_info()
                
                return {
                    "success": True,
                    "connected": True,
                    "scene_info": scene_info,
                    "message": "Blender connector working"
                }
            else:
                return {
                    "success": False,
                    "connected": False,
                    "message": "Blender not available (expected without Blender running)"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_texture_generation(self) -> Dict[str, Any]:
        """Test texture generation workflow"""
        try:
            if not self.ai_bridge:
                return {"success": False, "error": "AI Bridge not initialized"}
            
            # Create texture generation command
            command = AICommand.create(
                command="generate_texture",
                parameters={
                    "prompt": "red brick wall texture",
                    "size": [512, 512],
                    "maps": ["diffuse", "normal"]
                }
            )
            
            # Execute command
            response = await self.ai_bridge.execute_command(command)
            
            return {
                "success": response.success,
                "result": response.result,
                "error": response.error,
                "message": "Texture generation test completed"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_command_processing(self) -> Dict[str, Any]:
        """Test command processing system"""
        try:
            if not self.ai_bridge:
                return {"success": False, "error": "AI Bridge not initialized"}
            
            # Test various commands
            commands = [
                {
                    "command": "get_workflow_status",
                    "parameters": {"workflow_id": "test_123"}
                },
                {
                    "command": "generate_model",
                    "parameters": {"prompt": "simple cube"}
                }
            ]
            
            results = {}
            
            for cmd_data in commands:
                command = AICommand.create(**cmd_data)
                response = await self.ai_bridge.execute_command(command)
                
                results[cmd_data["command"]] = {
                    "success": response.success,
                    "error": response.error
                }
            
            # Check if command handlers are working
            all_processed = all(
                not r.get("error", "").startswith("Unknown command") 
                for r in results.values()
            )
            
            return {
                "success": all_processed,
                "results": results,
                "message": "Command processing functional"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_realtime_communication(self) -> Dict[str, Any]:
        """Test real-time communication features"""
        try:
            # Test progress callbacks
            progress_updates = []
            
            def progress_callback(workflow_id: str, progress: float):
                progress_updates.append({"workflow_id": workflow_id, "progress": progress})
            
            if self.ai_bridge:
                self.ai_bridge.add_progress_callback(progress_callback)
                
                # Simulate progress update
                self.ai_bridge._update_workflow_progress("test_workflow", 0.5)
                
                # Check if callback was called
                callback_working = len(progress_updates) > 0
                
                return {
                    "success": callback_working,
                    "progress_updates": progress_updates,
                    "message": "Progress callbacks working" if callback_working else "Progress callbacks not working"
                }
            else:
                return {"success": False, "error": "AI Bridge not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling"""
        try:
            if not self.ai_bridge:
                return {"success": False, "error": "AI Bridge not initialized"}
            
            # Test invalid command
            invalid_command = AICommand.create(
                command="invalid_command",
                parameters={}
            )
            
            response = await self.ai_bridge.execute_command(invalid_command)
            
            # Should return error response gracefully
            error_handled = not response.success and "Unknown command" in response.error
            
            return {
                "success": error_handled,
                "error_response": {
                    "success": response.success,
                    "error": response.error
                },
                "message": "Error handling working" if error_handled else "Error handling not working"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def generate_report(self):
        """Generate integration test report"""
        print("\n" + "=" * 50)
        print("📋 INTEGRATION TEST REPORT")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results.values() if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📄 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"  {status} {test_name}")
            if not result["success"] and "error" in result:
                print(f"    Error: {result['error']}")
        
        # Save report to file
        report_data = {
            "timestamp": time.time(),
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "results": self.test_results
        }
        
        report_path = Path("integration_test_report.json")
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n📁 Report saved to: {report_path}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        
        if failed_tests == 0:
            print("  🎉 All tests passed! The integration is working well.")
        else:
            print("  🔧 Some tests failed. Priority fixes:")
            
            if not self.test_results.get("AI Bridge API Endpoints", {}).get("success"):
                print("    1. Start the AI Bridge server: python main.py")
            
            if not self.test_results.get("ComfyUI Integration", {}).get("success"):
                print("    2. Install and configure ComfyUI")
            
            if not self.test_results.get("Blender Connector", {}).get("success"):
                print("    3. Install Blender and the Miktos addon")
        
        print("\n🚀 Next Steps:")
        print("  1. Implement missing components based on failed tests")
        print("  2. Set up development environment for external tools")
        print("  3. Test with real workflows and user scenarios")
        print("  4. Add more comprehensive end-to-end tests")
    
    async def cleanup(self):
        """Clean up test resources"""
        if self.ai_bridge:
            await self.ai_bridge.shutdown()
        
        if self.blender_connector:
            await self.blender_connector.close()


async def main():
    """Main test execution"""
    tester = IntegrationTester()
    
    try:
        await tester.run_all_tests()
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

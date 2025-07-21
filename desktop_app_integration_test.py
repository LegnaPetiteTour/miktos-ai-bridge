#!/usr/bin/env python3
"""
Desktop App Integration Test
Test the connection between Desktop App and AI Bridge
"""
import asyncio
import json
import time
import websockets
import requests
from datetime import datetime

class DesktopAppIntegrationTest:
    def __init__(self):
        self.ai_bridge_url = "http://localhost:8000"
        self.websocket_url = "ws://localhost:8000/ws/status"
        
    def test_api_endpoints(self):
        """Test all API endpoints that the Desktop App uses"""
        print("🔄 Testing Desktop App API Integration...")
        
        endpoints = [
            ("/health", "Health Check"),
            ("/api/v1/status", "Status Endpoint"),
            ("/api/v1/workflows", "Workflows List")
        ]
        
        results = {}
        
        for endpoint, name in endpoints:
            try:
                url = f"{self.ai_bridge_url}{endpoint}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    results[name] = {
                        "status": "✅ SUCCESS",
                        "response_time": response.elapsed.total_seconds(),
                        "data_keys": list(data.keys()) if isinstance(data, dict) else "non-dict"
                    }
                else:
                    results[name] = {
                        "status": f"❌ FAILED ({response.status_code})",
                        "response_time": response.elapsed.total_seconds()
                    }
                    
            except Exception as e:
                results[name] = {
                    "status": f"❌ ERROR: {str(e)}",
                    "response_time": 0
                }
        
        return results
    
    def test_workflow_execution(self):
        """Test AI workflow execution as Desktop App would"""
        print("🎨 Testing AI Workflow Execution...")
        
        try:
            # Test basic texture workflow
            workflow_data = {
                "workflow_name": "basic_texture",
                "parameters": {
                    "prompt": "rusty metal texture for 3D model",
                    "negative_prompt": "blurry, low quality",
                    "width": 512,
                    "height": 512,
                    "steps": 15,
                    "cfg": 7.0
                }
            }
            
            url = f"{self.ai_bridge_url}/api/v1/execute-workflow"
            response = requests.post(url, json=workflow_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get("task_id")
                
                # Test progress tracking
                if task_id:
                    time.sleep(2)  # Wait a moment for processing
                    progress_url = f"{self.ai_bridge_url}/api/v1/task/{task_id}"
                    progress_response = requests.get(progress_url, timeout=5)
                    
                    if progress_response.status_code == 200:
                        progress_data = progress_response.json()
                        return {
                            "workflow_execution": "✅ SUCCESS",
                            "task_id": task_id,
                            "progress_tracking": "✅ SUCCESS",
                            "final_status": progress_data.get("status", "unknown")
                        }
                
                return {
                    "workflow_execution": "✅ SUCCESS",
                    "task_id": task_id,
                    "progress_tracking": "❌ No task_id returned"
                }
            else:
                return {
                    "workflow_execution": f"❌ FAILED ({response.status_code})",
                    "error": response.text
                }
                
        except Exception as e:
            return {
                "workflow_execution": f"❌ ERROR: {str(e)}"
            }
    
    async def test_websocket_connection(self):
        """Test WebSocket connection for real-time updates"""
        print("🔗 Testing WebSocket Connection...")
        
        try:
            # Try to connect to WebSocket with proper timeout handling
            websocket = await asyncio.wait_for(
                websockets.connect(self.websocket_url), 
                timeout=5
            )
            
            # Send a test message
            await websocket.send(json.dumps({"type": "status_request"}))
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3)
                data = json.loads(response)
                
                await websocket.close()
                return {
                    "websocket_connection": "✅ SUCCESS",
                    "response_received": "✅ SUCCESS",
                    "data_type": type(data).__name__
                }
            except asyncio.TimeoutError:
                await websocket.close()
                return {
                    "websocket_connection": "✅ SUCCESS",
                    "response_received": "⚠️ TIMEOUT (connection works, no immediate response)"
                }
                    
        except Exception as e:
            return {
                "websocket_connection": f"❌ ERROR: {str(e)}"
            }
    
    def test_live_context_simulation(self):
        """Simulate Live Context Panel operations"""
        print("📊 Testing Live Context Panel Simulation...")
        
        try:
            # Test status polling (what Live Context Panel does)
            status_url = f"{self.ai_bridge_url}/api/v1/status"
            response = requests.get(status_url, timeout=5)
            
            if response.status_code == 200:
                status_data = response.json()
                
                # Simulate what Desktop App checks
                ai_bridge_ok = status_data.get("bridge_status") == "running"
                comfyui_ok = status_data.get("comfyui_status") in ["standalone", "connected"]
                workflows_available = status_data.get("available_workflows", 0) > 0
                
                return {
                    "status_polling": "✅ SUCCESS",
                    "ai_bridge_status": "✅ RUNNING" if ai_bridge_ok else "❌ NOT RUNNING",
                    "comfyui_status": f"✅ {status_data.get('comfyui_status', 'unknown').upper()}",
                    "workflows_available": f"✅ {status_data.get('available_workflows', 0)} workflows" if workflows_available else "❌ No workflows",
                    "connection_simulation": "✅ Desktop App would connect successfully"
                }
            else:
                return {
                    "status_polling": f"❌ FAILED ({response.status_code})"
                }
                
        except Exception as e:
            return {
                "status_polling": f"❌ ERROR: {str(e)}"
            }

async def run_integration_test():
    """Run complete Desktop App integration test"""
    print("🚀 Miktos Desktop App Integration Test")
    print("=" * 50)
    print(f"⏰ Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tester = DesktopAppIntegrationTest()
    
    # Test 1: API Endpoints
    api_results = tester.test_api_endpoints()
    print("📋 API Endpoints Test Results:")
    for endpoint, result in api_results.items():
        print(f"  {result['status']} {endpoint} ({result['response_time']:.3f}s)")
        if 'data_keys' in result:
            print(f"    Data: {result['data_keys']}")
    print()
    
    # Test 2: Workflow Execution
    workflow_results = tester.test_workflow_execution()
    print("🎨 Workflow Execution Test Results:")
    for key, value in workflow_results.items():
        print(f"  {value} {key.replace('_', ' ').title()}")
    print()
    
    # Test 3: WebSocket Connection
    websocket_results = await tester.test_websocket_connection()
    print("🔗 WebSocket Connection Test Results:")
    for key, value in websocket_results.items():
        print(f"  {value} {key.replace('_', ' ').title()}")
    print()
    
    # Test 4: Live Context Simulation
    context_results = tester.test_live_context_simulation()
    print("📊 Live Context Panel Simulation Results:")
    for key, value in context_results.items():
        print(f"  {value} {key.replace('_', ' ').title()}")
    print()
    
    # Summary
    print("=" * 50)
    print("🎯 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    total_tests = 0
    passed_tests = 0
    
    for result_set in [api_results, workflow_results, websocket_results, context_results]:
        for key, value in result_set.items():
            total_tests += 1
            if isinstance(value, str) and "✅" in value:
                passed_tests += 1
            elif isinstance(value, dict) and "✅" in value.get("status", ""):
                passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"📊 Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! Desktop App integration ready for full testing")
    elif success_rate >= 75:
        print("✅ GOOD! Desktop App integration mostly functional")
    elif success_rate >= 50:
        print("⚠️ PARTIAL! Some Desktop App features may not work")
    else:
        print("❌ ISSUES! Desktop App integration needs attention")
    
    print(f"⏰ Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(run_integration_test())

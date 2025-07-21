#!/usr/bin/env python3
"""
Desktop App Connection Test
Simulate Desktop App connecting to AI Bridge for end-to-end testing
"""
import asyncio
import websockets
import requests
import json
import time
from datetime import datetime

class DesktopAppSimulator:
    def __init__(self):
        self.ai_bridge_url = "http://localhost:8000"
        self.websocket_url = "ws://localhost:8000/ws/status"
        
    async def simulate_desktop_app_workflow(self):
        """Simulate complete Desktop App workflow"""
        print("🖥️ DESKTOP APP SIMULATION - END-TO-END TEST")
        print("=" * 55)
        print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        # Step 1: Initial connection check (what Desktop App does on startup)
        print("1️⃣ INITIAL CONNECTION CHECK")
        try:
            response = requests.get(f"{self.ai_bridge_url}/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ AI Bridge connection successful")
                health_data = response.json()
                print(f"   📊 Service: {health_data.get('service', 'unknown')}")
                print(f"   🔗 ComfyUI: {'✅ Connected' if health_data.get('comfyui_connected') else '❌ Disconnected'}")
            else:
                print(f"   ❌ Connection failed: {response.status_code}")
                return
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
            return
        print()
        
        # Step 2: Get system status (Live Context Panel simulation)
        print("2️⃣ SYSTEM STATUS CHECK (Live Context Panel)")
        try:
            response = requests.get(f"{self.ai_bridge_url}/api/v1/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                print(f"   🔧 Bridge Status: {status.get('bridge_status', 'unknown').upper()}")
                print(f"   🎨 ComfyUI Mode: {status.get('comfyui_mode', 'unknown').upper()}")
                print(f"   📊 Available Workflows: {status.get('available_workflows', 0)}")
                print(f"   🔄 Active Tasks: {status.get('active_tasks', 0)}")
                print("   ✅ Status check successful")
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Status error: {e}")
        print()
        
        # Step 3: List available workflows (Workflow Canvas simulation)
        print("3️⃣ WORKFLOW DISCOVERY (Workflow Canvas)")
        try:
            response = requests.get(f"{self.ai_bridge_url}/api/v1/workflows", timeout=5)
            if response.status_code == 200:
                workflows = response.json().get("workflows", [])
                print(f"   📋 Found {len(workflows)} workflows:")
                for i, workflow in enumerate(workflows, 1):
                    print(f"      {i}. {workflow.get('name', 'Unknown')}")
                    print(f"         📝 {workflow.get('description', 'No description')}")
                print("   ✅ Workflow discovery successful")
            else:
                print(f"   ❌ Workflow discovery failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Workflow error: {e}")
        print()
        
        # Step 4: Execute a workflow (AI Command Bar simulation)
        print("4️⃣ WORKFLOW EXECUTION (AI Command Bar)")
        try:
            workflow_data = {
                "workflow_name": "basic_texture",
                "parameters": {
                    "prompt": "rusty metal texture for spaceship hull",
                    "negative_prompt": "blurry, low quality, distorted",
                    "width": 512,
                    "height": 512,
                    "steps": 15,
                    "cfg": 7.0,
                    "seed": 42
                }
            }
            
            print("   🎨 Executing: Basic Texture Generation")
            print(f"   📝 Prompt: {workflow_data['parameters']['prompt']}")
            
            response = requests.post(
                f"{self.ai_bridge_url}/api/v1/execute-workflow",
                json=workflow_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get("task_id")
                print(f"   ✅ Workflow started - Task ID: {task_id}")
                
                # Monitor progress
                await self.monitor_task_progress(task_id)
                
            else:
                print(f"   ❌ Workflow execution failed: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Execution error: {e}")
        print()
        
        # Step 5: WebSocket real-time monitoring (Live Context Panel)
        print("5️⃣ REAL-TIME MONITORING (WebSocket)")
        await self.test_websocket_monitoring()
        
        print("🎉 DESKTOP APP SIMULATION COMPLETE")
        print("=" * 55)
    
    async def monitor_task_progress(self, task_id):
        """Monitor task progress like Desktop App would"""
        print("   🔄 Monitoring task progress...")
        
        for i in range(6):  # Check 6 times over 5 seconds
            try:
                response = requests.get(f"{self.ai_bridge_url}/api/v1/task/{task_id}", timeout=5)
                if response.status_code == 200:
                    task_data = response.json()
                    status = task_data.get("status", "unknown")
                    progress = task_data.get("progress", 0.0)
                    
                    print(f"      📊 Progress: {progress:.1f}% - Status: {status}")
                    
                    if status in ["completed", "error"]:
                        if status == "completed":
                            print("   ✅ Task completed successfully!")
                            output_path = task_data.get("output_path", "No output path")
                            print(f"   💾 Output: {output_path}")
                        else:
                            print("   ❌ Task failed!")
                        break
                else:
                    print(f"      ❌ Progress check failed: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Progress error: {e}")
            
            if i < 5:  # Don't sleep after the last iteration
                await asyncio.sleep(1)
    
    async def test_websocket_monitoring(self):
        """Test WebSocket connection like Live Context Panel would"""
        try:
            print("   🔗 Connecting to WebSocket...")
            websocket = await asyncio.wait_for(
                websockets.connect(self.websocket_url),
                timeout=5
            )
            
            print("   ✅ WebSocket connected")
            
            # Listen for a few status updates
            for i in range(3):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=3)
                    data = json.loads(message)
                    timestamp = datetime.fromtimestamp(data.get("timestamp", 0)).strftime('%H:%M:%S')
                    print(f"   📊 [{timestamp}] Status update received - {data.get('active_tasks', 0)} active tasks")
                except asyncio.TimeoutError:
                    print("   ⏱️ No immediate status update (normal)")
                    break
            
            await websocket.close()
            print("   ✅ WebSocket test completed")
            
        except Exception as e:
            print(f"   ❌ WebSocket error: {e}")

async def main():
    simulator = DesktopAppSimulator()
    await simulator.simulate_desktop_app_workflow()

if __name__ == "__main__":
    asyncio.run(main())

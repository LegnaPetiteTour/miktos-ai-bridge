#!/usr/bin/env python3
"""
Miktos AI Bridge - Main Entry Point
Phase 2: ComfyUI Integration
"""
import sys
import os
import asyncio
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Now import our modules
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import time

# Import our ComfyUI integration
from src.comfyui.client import ComfyUIClient
from src.comfyui.workflow_manager import WorkflowManager, WorkflowType
from src.comfyui.standalone_executor import StandaloneComfyUIExecutor
from src.core.config import settings

# App configuration
app = FastAPI(
    title="Miktos AI Bridge",
    description="AI Bridge for Miktos Platform - ComfyUI Integration & 3D Software Connectivity",
    version="0.2.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ComfyUI client and workflow manager
if getattr(settings, 'comfyui_standalone_mode', False):
    logger.info("🎨 Using standalone ComfyUI executor (development mode)")
    comfyui_client = StandaloneComfyUIExecutor(output_dir=settings.output_dir)
else:
    logger.info("🔌 Using external ComfyUI server")
    comfyui_client = ComfyUIClient()
workflow_manager = WorkflowManager()

# Global state for tracking active generations
active_generations: Dict[str, Dict[str, Any]] = {}

# Request/Response models
class CommandRequest(BaseModel):
    command: str
    parameters: Optional[Dict[str, Any]] = None

class TextureGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = ""
    width: Optional[int] = 1024
    height: Optional[int] = 1024
    steps: Optional[int] = 20
    cfg: Optional[float] = 7.0
    workflow_template: Optional[str] = "basic_texture"

class WorkflowExecutionRequest(BaseModel):
    workflow_name: str
    parameters: Dict[str, Any]

class CommandResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Miktos AI Bridge is running!", "version": "0.2.0", "comfyui_integration": "active"}

@app.get("/health")
async def health_check():
    comfyui_connected = await comfyui_client.check_connection()
    return {
        "status": "healthy", 
        "service": "miktos-ai-bridge",
        "comfyui_connected": comfyui_connected,
        "available_workflows": len(workflow_manager.templates)
    }

# Enhanced execute command endpoint with AI integration
@app.post("/api/v1/execute-command", response_model=CommandResponse)
async def execute_command(request: CommandRequest, background_tasks: BackgroundTasks):
    """Execute a natural language command with AI processing"""
    try:
        command = request.command.lower().strip()
        parameters = request.parameters or {}
        
        # Simple command parsing - this will be enhanced with LLM later
        if any(keyword in command for keyword in ["texture", "material", "surface"]):
            # Texture generation command
            prompt = request.command
            task_id = f"texture_{asyncio.get_event_loop().time()}"
            
            # Start background texture generation
            background_tasks.add_task(
                generate_texture_background,
                task_id,
                prompt,
                parameters
            )
            
            return CommandResponse(
                success=True,
                message=f"Texture generation started: {prompt}",
                data={"command_type": "texture_generation", "prompt": prompt},
                task_id=task_id
            )
        
        elif any(keyword in command for keyword in ["generate", "create", "make"]):
            # General generation command
            return CommandResponse(
                success=True,
                message=f"AI generation request processed: {request.command}",
                data={"command": request.command, "parameters": parameters}
            )
        
        else:
            # Default response for unrecognized commands
            return CommandResponse(
                success=True,
                message=f"Command received and queued: {request.command}",
                data={"command": request.command, "parameters": parameters}
            )
            
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced texture generation endpoint
@app.post("/api/v1/generate-texture", response_model=CommandResponse)
async def generate_texture(request: TextureGenerationRequest, background_tasks: BackgroundTasks):
    """Generate a texture using ComfyUI"""
    try:
        # Check ComfyUI connection
        if not await comfyui_client.check_connection():
            return CommandResponse(
                success=False,
                message="ComfyUI is not available. Please ensure ComfyUI is running.",
                data={"error": "comfyui_not_available"}
            )
        
        task_id = f"texture_{asyncio.get_event_loop().time()}"
        
        # Start background generation
        background_tasks.add_task(
            generate_texture_with_comfyui,
            task_id,
            request.dict()
        )
        
        return CommandResponse(
            success=True,
            message=f"Texture generation started: {request.prompt}",
            data={
                "prompt": request.prompt,
                "workflow": request.workflow_template,
                "estimated_time": "30-60 seconds"
            },
            task_id=task_id
        )
        
    except Exception as e:
        logger.error(f"Error starting texture generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# New workflow execution endpoint
@app.post("/api/v1/execute-workflow", response_model=CommandResponse)
async def execute_workflow(request: WorkflowExecutionRequest, background_tasks: BackgroundTasks):
    """Execute a specific AI workflow"""
    try:
        workflow_template = workflow_manager.get_workflow_template(request.workflow_name)
        if not workflow_template:
            raise HTTPException(
                status_code=404, 
                detail=f"Workflow '{request.workflow_name}' not found"
            )
        
        # Prepare workflow with parameters
        workflow = workflow_manager.prepare_workflow(request.workflow_name, request.parameters)
        if not workflow:
            raise HTTPException(
                status_code=400,
                detail="Failed to prepare workflow with given parameters"
            )
        
        task_id = f"workflow_{asyncio.get_event_loop().time()}"
        
        # Start background execution
        background_tasks.add_task(
            execute_workflow_background,
            task_id,
            workflow,
            workflow_template.name
        )
        
        return CommandResponse(
            success=True,
            message=f"Workflow '{workflow_template.name}' started",
            data={
                "workflow_name": workflow_template.name,
                "workflow_type": workflow_template.type.value,
                "parameters": request.parameters
            },
            task_id=task_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get task progress endpoint
@app.get("/api/v1/task/{task_id}")
async def get_task_progress(task_id: str):
    """Get progress of a background task"""
    if task_id not in active_generations:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return active_generations[task_id]

# List available workflows
@app.get("/api/v1/workflows")
async def list_workflows(workflow_type: Optional[str] = None):
    """List available AI workflows"""
    try:
        if workflow_type:
            workflows = workflow_manager.list_workflows(WorkflowType(workflow_type))
        else:
            workflows = workflow_manager.list_workflows()
        
        return {
            "workflows": [
                {
                    "name": template.name,
                    "type": template.type.value,
                    "description": template.description,
                    "parameters": template.parameters,
                    "required_models": template.required_models
                }
                for template in workflows
            ]
        }
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced status endpoint
@app.get("/api/v1/status")
async def get_status():
    """Get the current status of the AI Bridge"""
    try:
        if settings.comfyui_standalone_mode:
            # Standalone mode - always report as connected
            return {
                "bridge_status": "running",
                "comfyui_status": "standalone",
                "comfyui_mode": "standalone",
                "comfyui_queue": {"pending": 0, "running": 0},
                "available_models": ["standalone_model_v1"],
                "total_models": 1,
                "active_tasks": len(active_generations),
                "available_workflows": len(workflow_manager.templates)
            }
        else:
            # External ComfyUI mode
            comfyui_connected = await comfyui_client.check_connection()
            queue_status = await comfyui_client.get_queue_status() if comfyui_connected else {}
            available_models = await comfyui_client.get_available_models() if comfyui_connected else []
            
            return {
                "bridge_status": "running",
                "comfyui_status": "connected" if comfyui_connected else "disconnected",
                "comfyui_mode": "external",
                "comfyui_queue": queue_status,
                "available_models": available_models[:10],  # Limit for response size
                "total_models": len(available_models),
                "active_tasks": len(active_generations),
                "available_workflows": len(workflow_manager.templates)
            }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {
            "bridge_status": "running",
            "comfyui_status": "error",
            "comfyui_mode": "standalone" if settings.comfyui_standalone_mode else "external",
            "error": str(e),
            "active_tasks": len(active_generations),
            "available_workflows": len(workflow_manager.templates)
        }

# Background task functions
async def generate_texture_background(task_id: str, prompt: str, parameters: Dict[str, Any]):
    """Background task for texture generation"""
    active_generations[task_id] = {
        "status": "started",
        "progress": 0.0,
        "message": "Initializing texture generation..."
    }
    
    try:
        # Simple texture generation using basic workflow
        result = await comfyui_client.execute_simple_generation(
            prompt=prompt,
            negative_prompt=parameters.get("negative_prompt", ""),
            steps=parameters.get("steps", 20),
            cfg=parameters.get("cfg", 7.0),
            width=parameters.get("width", 1024),
            height=parameters.get("height", 1024)
        )
        
        if result and result["status"] == "completed":
            active_generations[task_id] = {
                "status": "completed",
                "progress": 1.0,
                "message": "Texture generation completed successfully",
                "result": result
            }
        else:
            active_generations[task_id] = {
                "status": "error",
                "progress": 0.0,
                "message": f"Generation failed: {result.get('error', 'Unknown error') if result else 'No result'}"
            }
    
    except Exception as e:
        logger.error(f"Background texture generation error: {e}")
        active_generations[task_id] = {
            "status": "error",
            "progress": 0.0,
            "message": f"Generation error: {str(e)}"
        }

async def generate_texture_with_comfyui(task_id: str, request_data: Dict[str, Any]):
    """Background task for ComfyUI texture generation"""
    active_generations[task_id] = {
        "status": "preparing",
        "progress": 0.1,
        "message": "Preparing workflow..."
    }
    
    try:
        # Prepare workflow
        workflow = workflow_manager.prepare_workflow(
            request_data["workflow_template"],
            request_data
        )
        
        if not workflow:
            raise Exception("Failed to prepare workflow")
        
        active_generations[task_id]["progress"] = 0.2
        active_generations[task_id]["message"] = "Submitting to ComfyUI..."
        
        # Execute workflow
        result = await comfyui_client.submit_workflow(workflow)
        
        if result:
            active_generations[task_id] = {
                "status": "completed",
                "progress": 1.0,
                "message": "Texture generation completed",
                "result": {"prompt_id": result}
            }
        else:
            raise Exception("Failed to submit workflow to ComfyUI")
    
    except Exception as e:
        logger.error(f"ComfyUI texture generation error: {e}")
        active_generations[task_id] = {
            "status": "error",
            "progress": 0.0,
            "message": f"Error: {str(e)}"
        }

async def execute_workflow_background(task_id: str, workflow: Dict[str, Any], workflow_name: str):
    """Background task for workflow execution"""
    active_generations[task_id] = {
        "status": "executing",
        "progress": 0.1,
        "message": f"Executing workflow: {workflow_name}"
    }
    
    try:
        prompt_id = await comfyui_client.submit_workflow(workflow)
        
        if prompt_id:
            active_generations[task_id] = {
                "status": "completed",
                "progress": 1.0,
                "message": f"Workflow '{workflow_name}' completed successfully",
                "result": {"prompt_id": prompt_id}
            }
        else:
            raise Exception("Failed to execute workflow")
    
    except Exception as e:
        logger.error(f"Workflow execution error: {e}")
        active_generations[task_id] = {
            "status": "error",
            "progress": 0.0,
            "message": f"Workflow error: {str(e)}"
        }

# WebSocket endpoint for real-time status updates
@app.websocket("/ws/status")
async def websocket_status_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time status updates"""
    await websocket.accept()
    logger.info("WebSocket client connected for status updates")
    
    try:
        while True:
            # Send status update every 2 seconds
            current_mode = "standalone" if settings.comfyui_standalone_mode else "external"
            status_data = {
                "timestamp": time.time(),
                "bridge_status": "running",
                "comfyui_status": current_mode,
                "comfyui_mode": current_mode,
                "active_tasks": len(active_generations),
                "available_workflows": len(workflow_manager.get_available_templates()),
                "task_updates": []
            }
            
            # Add task updates
            for task_id, task_info in active_generations.items():
                status_data["task_updates"].append({
                    "task_id": task_id,
                    "status": task_info.get("status", "unknown"),
                    "progress": task_info.get("progress", 0.0),
                    "message": task_info.get("message", "")
                })
            
            await websocket.send_text(json.dumps(status_data))
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

@app.websocket("/ws/tasks/{task_id}")
async def websocket_task_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for specific task updates"""
    await websocket.accept()
    logger.info(f"WebSocket client connected for task {task_id}")
    
    try:
        while True:
            if task_id in active_generations:
                task_info = active_generations[task_id]
                await websocket.send_text(json.dumps({
                    "task_id": task_id,
                    "status": task_info.get("status", "unknown"),
                    "progress": task_info.get("progress", 0.0),
                    "message": task_info.get("message", ""),
                    "timestamp": time.time()
                }))
                
                # Close connection if task is completed or failed
                if task_info.get("status") in ["completed", "error"]:
                    break
                    
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from task {task_id}")
    except Exception as e:
        logger.error(f"WebSocket task error: {e}")

@app.websocket("/ws/blender")
async def blender_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint specifically for Blender addon communication"""
    await websocket.accept()
    logger.info("Blender addon connected via WebSocket")
    
    try:
        while True:
            # Send Blender-specific status updates
            status_data = {
                "timestamp": time.time(),
                "bridge_status": "running",
                "blender_connected": True,
                "active_generations": len(active_generations),
                "available_workflows": len(workflow_manager.list_workflows()),
                "addon_version": "1.0.0",
                "task_updates": []
            }
            
            # Add task updates with Blender-specific information
            for task_id, task_info in active_generations.items():
                status_data["task_updates"].append({
                    "task_id": task_id,
                    "status": task_info.get("status", "unknown"),
                    "progress": task_info.get("progress", 0.0),
                    "message": task_info.get("message", ""),
                    "workflow_type": task_info.get("workflow_type", "unknown"),
                    "blender_ready": task_info.get("status") == "completed"
                })
            
            await websocket.send_text(json.dumps(status_data))
            await asyncio.sleep(1)  # Faster updates for Blender
            
    except WebSocketDisconnect:
        logger.info("Blender addon disconnected")
    except Exception as e:
        logger.error(f"Blender WebSocket error: {e}")

@app.post("/api/v1/blender/generate-material")
async def generate_blender_material(
    material_request: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """
    Generate AI material optimized for Blender workflow
    """
    try:
        # Extract Blender-specific parameters
        workflow_name = material_request.get("workflow_type", "basic_texture")
        parameters = material_request.get("parameters", {})
        blender_info = material_request.get("blender_info", {})
        
        # Add Blender-specific optimization
        if "blender_version" in blender_info:
            parameters["blender_optimized"] = True
            parameters["render_engine"] = blender_info.get("render_engine", "cycles")
        
        # Generate task ID
        task_id = f"blender_{int(time.time() * 1000)}"
        
        # Initialize task tracking
        active_generations[task_id] = {
            "status": "starting",
            "progress": 0.0,
            "message": "Preparing Blender-optimized material generation...",
            "workflow_type": workflow_name,
            "blender_info": blender_info,
            "start_time": time.time()
        }
        
        # Start background generation
        background_tasks.add_task(
            execute_blender_workflow,
            task_id,
            workflow_name, 
            parameters
        )
        
        return {
            "success": True,
            "message": f"Blender material generation started",
            "task_id": task_id,
            "workflow_type": workflow_name,
            "estimated_time": "15-30 seconds",
            "blender_optimized": True
        }
        
    except Exception as e:
        logger.error(f"Blender material generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start material generation: {str(e)}")

async def execute_blender_workflow(task_id: str, workflow_name: str, parameters: Dict[str, Any]):
    """Execute workflow optimized for Blender integration"""
    try:
        logger.info(f"Starting Blender-optimized workflow: {workflow_name} (Task: {task_id})")
        
        # Update status
        active_generations[task_id] = {
            "status": "executing",
            "progress": 10.0,
            "message": "Generating Blender-compatible textures...",
            "workflow_type": workflow_name
        }
        
        # Get workflow template and validate parameters
        template = workflow_manager.get_workflow_template(workflow_name)
        if not template:
            raise Exception(f"Workflow '{workflow_name}' not found")
        
        # Validate and get parameters
        validated_params = workflow_manager._validate_and_fill_parameters(template, parameters)
        if not validated_params:
            raise Exception("Parameter validation failed")
        
        # Prepare the workflow with validated parameters
        prepared_workflow = workflow_manager.prepare_workflow(workflow_name, validated_params)
        
        # Add Blender-specific enhancements
        if validated_params.get("blender_optimized"):
            validated_params["output_format"] = "png"  # Blender-friendly format
            validated_params["color_space"] = "sRGB"   # Proper color space
            validated_params["bit_depth"] = 8          # Standard bit depth
        
        # Progress update
        active_generations[task_id]["progress"] = 50.0
        active_generations[task_id]["message"] = "Processing AI generation..."
        
        # Execute workflow (using standalone executor)
        if settings.comfyui_standalone_mode:
            prompt_id = await comfyui_client.submit_workflow(prepared_workflow)
            
            if prompt_id:
                # For standalone mode, create a mock result
                result = {
                    "status": "completed",
                    "prompt_id": prompt_id,
                    "outputs": [f"mock_texture_{prompt_id[:8]}.png"]
                }
                
                # Progress update
                active_generations[task_id]["progress"] = 90.0
                active_generations[task_id]["message"] = "Preparing Blender materials..."
                
                # Create Blender-specific result
                blender_result = {
                    "texture_files": result.get("outputs", []),
                    "material_info": {
                        "type": "principled_bsdf",
                        "base_color": result.get("outputs", [None])[0] if result.get("outputs") else None,
                        "workflow_type": workflow_name,
                        "parameters_used": validated_params
                    },
                    "blender_compatible": True
                }
                
                # Mark as completed
                active_generations[task_id] = {
                    "status": "completed",
                    "progress": 100.0,
                    "message": "Material ready for Blender application!",
                    "workflow_type": workflow_name,
                    "result": blender_result,
                    "output_path": result.get("outputs", ["No output path"])[0]
                }
                
                logger.info(f"Blender workflow completed: {task_id}")
            else:
                raise Exception("Workflow execution failed")
        else:
            # External ComfyUI would go here
            raise Exception("External ComfyUI not configured for Blender workflow")
    
    except Exception as e:
        logger.error(f"Blender workflow execution error: {e}")
        active_generations[task_id] = {
            "status": "error",
            "progress": 0.0,
            "message": f"Blender workflow error: {str(e)}"
        }

if __name__ == "__main__":
    print("🚀 Starting Miktos AI Bridge...")
    print("===============================")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("Press Ctrl+C to stop the server")
    print("")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
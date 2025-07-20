"""
Miktos AI Bridge - Core Bridge Implementation

This module contains the main AI bridge class that orchestrates
ComfyUI integration, model management, and workflow execution.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import json
import uuid
from dataclasses import dataclass, asdict
from enum import Enum

from .config import settings
from .models import WorkflowStatus, AICommand, AIResponse, GenerationRequest
from ..comfyui.client import ComfyUIClient
from ..comfyui.workflow_manager import WorkflowManager
from ..workflows.texture_generator import TextureGenerator
from ..connectors.blender_connector import BlenderConnector

logger = logging.getLogger(__name__)

class BridgeStatus(Enum):
    """Bridge status enumeration"""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    SHUTDOWN = "shutdown"

@dataclass
class WorkflowExecution:
    """Workflow execution tracking"""
    id: str
    name: str
    status: WorkflowStatus
    progress: float
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class MiktosAIBridge:
    """
    Main AI Bridge class that orchestrates all AI operations
    """
    
    def __init__(self):
        self.status = BridgeStatus.INITIALIZING
        self.comfyui_client: Optional[ComfyUIClient] = None
        self.workflow_manager: Optional[WorkflowManager] = None
        self.texture_generator: Optional[TextureGenerator] = None
        self.blender_connector: Optional[BlenderConnector] = None
        
        # Execution tracking
        self.active_workflows: Dict[str, WorkflowExecution] = {}
        self.command_handlers: Dict[str, Callable] = {}
        
        # Callbacks
        self.progress_callbacks: List[Callable] = []
        
        logger.info("MiktosAIBridge initialized")
    
    async def initialize(self):
        """Initialize the AI bridge and all components"""
        try:
            logger.info("Initializing AI Bridge components...")
            
            # Initialize ComfyUI client
            self.comfyui_client = ComfyUIClient(
                server_address=f"{settings.comfyui_host}:{settings.comfyui_port}",
                timeout=settings.comfyui_timeout
            )
            
            # Initialize workflow manager
            self.workflow_manager = WorkflowManager(self.comfyui_client)
            
            # Initialize texture generator
            self.texture_generator = TextureGenerator(
                self.comfyui_client,
                self.workflow_manager
            )
            
            # Initialize Blender connector
            self.blender_connector = BlenderConnector()
            
            # Register command handlers
            self._register_command_handlers()
            
            # Test ComfyUI connection
            await self._test_comfyui_connection()
            
            self.status = BridgeStatus.READY
            logger.info("AI Bridge initialization complete")
            
        except Exception as e:
            self.status = BridgeStatus.ERROR
            logger.error(f"Failed to initialize AI Bridge: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the AI bridge"""
        logger.info("Shutting down AI Bridge...")
        self.status = BridgeStatus.SHUTDOWN
        
        # Cancel active workflows
        for workflow_id in list(self.active_workflows.keys()):
            await self.cancel_workflow(workflow_id)
        
        # Close connections
        if self.comfyui_client:
            await self.comfyui_client.close()
        
        if self.blender_connector:
            await self.blender_connector.close()
        
        logger.info("AI Bridge shutdown complete")
    
    def _register_command_handlers(self):
        """Register command handlers"""
        self.command_handlers = {
            "generate_texture": self._handle_generate_texture,
            "generate_model": self._handle_generate_model,
            "apply_style": self._handle_apply_style,
            "execute_workflow": self._handle_execute_workflow,
            "get_workflow_status": self._handle_get_workflow_status,
            "cancel_workflow": self._handle_cancel_workflow,
        }
    
    async def _test_comfyui_connection(self):
        """Test ComfyUI connection"""
        if not self.comfyui_client:
            raise Exception("ComfyUI client not initialized")
        
        try:
            await self.comfyui_client.connect()
            logger.info("ComfyUI connection test successful")
        except Exception as e:
            logger.error(f"ComfyUI connection test failed: {e}")
            raise
    
    async def execute_command(self, command: AICommand) -> AIResponse:
        """Execute an AI command"""
        if self.status != BridgeStatus.READY:
            return AIResponse(
                id=command.id,
                success=False,
                error=f"Bridge not ready (status: {self.status.value})"
            )
        
        handler = self.command_handlers.get(command.command)
        if not handler:
            return AIResponse(
                id=command.id,
                success=False,
                error=f"Unknown command: {command.command}"
            )
        
        try:
            self.status = BridgeStatus.BUSY
            result = await handler(command)
            self.status = BridgeStatus.READY
            
            return AIResponse(
                id=command.id,
                success=True,
                result=result
            )
            
        except Exception as e:
            self.status = BridgeStatus.READY
            logger.error(f"Command execution failed: {e}")
            return AIResponse(
                id=command.id,
                success=False,
                error=str(e)
            )
    
    async def _handle_generate_texture(self, command: AICommand) -> Dict[str, Any]:
        """Handle texture generation command"""
        if not self.texture_generator:
            raise Exception("Texture generator not initialized")
        
        prompt = command.parameters.get("prompt", "")
        size = command.parameters.get("size", [512, 512])
        maps = command.parameters.get("maps", ["diffuse", "normal", "roughness"])
        
        logger.info(f"Generating texture: {prompt}")
        
        # Create workflow execution
        execution = WorkflowExecution(
            id=str(uuid.uuid4()),
            name=f"Texture: {prompt[:50]}",
            status=WorkflowStatus.RUNNING,
            progress=0.0,
            start_time=datetime.now()
        )
        
        self.active_workflows[execution.id] = execution
        
        try:
            # Generate texture
            result = await self.texture_generator.generate_texture(
                prompt=prompt,
                size=size,
                maps=maps,
                progress_callback=lambda p: self._update_workflow_progress(execution.id, p)
            )
            
            # Update execution
            execution.status = WorkflowStatus.COMPLETED
            execution.progress = 1.0
            execution.end_time = datetime.now()
            execution.result = result
            
            return {
                "workflow_id": execution.id,
                "result": result
            }
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            raise
    
    async def _handle_generate_model(self, command: AICommand) -> Dict[str, Any]:
        """Handle 3D model generation command"""
        # TODO: Implement 3D model generation
        return {"message": "3D model generation not yet implemented"}
    
    async def _handle_apply_style(self, command: AICommand) -> Dict[str, Any]:
        """Handle style application command"""
        # TODO: Implement style application
        return {"message": "Style application not yet implemented"}
    
    async def _handle_execute_workflow(self, command: AICommand) -> Dict[str, Any]:
        """Handle workflow execution command"""
        if not self.workflow_manager:
            raise Exception("Workflow manager not initialized")
        
        workflow_data = command.parameters.get("workflow")
        if not workflow_data:
            raise Exception("No workflow data provided")
        
        # Execute workflow
        result = await self.workflow_manager.execute_workflow(workflow_data)
        
        return {"result": result}
    
    async def _handle_get_workflow_status(self, command: AICommand) -> Dict[str, Any]:
        """Handle workflow status request"""
        workflow_id = command.parameters.get("workflow_id")
        if not workflow_id:
            raise Exception("No workflow ID provided")
        
        execution = self.active_workflows.get(workflow_id)
        if not execution:
            raise Exception(f"Workflow {workflow_id} not found")
        
        return asdict(execution)
    
    async def _handle_cancel_workflow(self, command: AICommand) -> Dict[str, Any]:
        """Handle workflow cancellation"""
        workflow_id = command.parameters.get("workflow_id")
        if not workflow_id:
            raise Exception("No workflow ID provided")
        
        await self.cancel_workflow(workflow_id)
        
        return {"message": f"Workflow {workflow_id} cancelled"}
    
    async def cancel_workflow(self, workflow_id: str):
        """Cancel a workflow execution"""
        execution = self.active_workflows.get(workflow_id)
        if execution and execution.status == WorkflowStatus.RUNNING:
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = datetime.now()
            
            # TODO: Cancel actual ComfyUI execution
            logger.info(f"Workflow {workflow_id} cancelled")
    
    def _update_workflow_progress(self, workflow_id: str, progress: float):
        """Update workflow progress"""
        execution = self.active_workflows.get(workflow_id)
        if execution:
            execution.progress = progress
            
            # Notify progress callbacks
            for callback in self.progress_callbacks:
                try:
                    callback(workflow_id, progress)
                except Exception as e:
                    logger.error(f"Progress callback error: {e}")
    
    def add_progress_callback(self, callback: Callable):
        """Add a progress callback"""
        self.progress_callbacks.append(callback)
    
    def remove_progress_callback(self, callback: Callable):
        """Remove a progress callback"""
        if callback in self.progress_callbacks:
            self.progress_callbacks.remove(callback)
    
    # Status methods
    def is_ready(self) -> bool:
        """Check if bridge is ready"""
        return self.status == BridgeStatus.READY
    
    def is_comfyui_connected(self) -> bool:
        """Check ComfyUI connection status"""
        return self.comfyui_client and self.comfyui_client.is_connected()
    
    def get_loaded_models_count(self) -> int:
        """Get number of loaded models"""
        # TODO: Implement model counting
        return 0
    
    def get_active_workflows_count(self) -> int:
        """Get number of active workflows"""
        return len([w for w in self.active_workflows.values() 
                   if w.status == WorkflowStatus.RUNNING])
    
    def get_workflow_history(self) -> List[Dict[str, Any]]:
        """Get workflow execution history"""
        return [asdict(w) for w in self.active_workflows.values()]
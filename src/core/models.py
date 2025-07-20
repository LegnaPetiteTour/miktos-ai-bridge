"""
Miktos AI Bridge - Core Models

This module defines the core data models and schemas used throughout
the AI Bridge for type safety and validation.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CommandType(Enum):
    """Available command types"""
    GENERATE_TEXTURE = "generate_texture"
    GENERATE_MODEL = "generate_model"
    APPLY_STYLE = "apply_style"
    EXECUTE_WORKFLOW = "execute_workflow"
    GET_WORKFLOW_STATUS = "get_workflow_status"
    CANCEL_WORKFLOW = "cancel_workflow"
    GET_SCENE_INFO = "get_scene_info"
    APPLY_TEXTURE = "apply_texture"


@dataclass
class AICommand:
    """AI command data model"""
    id: str
    command: str
    parameters: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None
    
    @classmethod
    def create(cls, command: str, parameters: Dict[str, Any], user_id: Optional[str] = None):
        """Create a new AI command"""
        return cls(
            id=str(uuid.uuid4()),
            command=command,
            parameters=parameters,
            timestamp=datetime.now(),
            user_id=user_id
        )


@dataclass
class AIResponse:
    """AI command response data model"""
    id: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None
    execution_time: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class GenerationRequest:
    """Base generation request model"""
    prompt: str
    negative_prompt: str = ""
    width: int = 1024
    height: int = 1024
    steps: int = 20
    cfg: float = 7.0
    seed: Optional[int] = None
    model_name: str = "stable-diffusion-xl"


@dataclass
class TextureGenerationRequest(GenerationRequest):
    """Texture generation specific request"""
    maps: List[str] = None
    material_name: Optional[str] = None
    uv_unwrap: bool = True
    
    def __post_init__(self):
        if self.maps is None:
            self.maps = ["diffuse", "normal", "roughness"]


@dataclass
class WorkflowExecution:
    """Workflow execution tracking model"""
    id: str
    name: str
    status: WorkflowStatus
    progress: float
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    workflow_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class SceneInfo:
    """3D scene information model"""
    scene_name: str
    objects: List[str]
    selected_objects: List[str]
    frame_current: int
    frame_start: int
    frame_end: int
    render_engine: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TextureInfo:
    """Texture information model"""
    id: str
    name: str
    file_path: str
    size: List[int]
    format: str
    map_type: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MaterialInfo:
    """Material information model"""
    id: str
    name: str
    textures: Dict[str, TextureInfo]
    shader_type: str
    properties: Dict[str, Any]
    created_at: datetime


@dataclass
class ConnectorStatus:
    """External connector status model"""
    name: str
    connected: bool
    status: str
    last_ping: Optional[datetime] = None
    capabilities: List[str] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


@dataclass
class SystemStatus:
    """System status model"""
    bridge_status: str
    comfyui_connected: bool
    active_workflows: int
    available_models: int
    connectors: List[ConnectorStatus]
    uptime: float
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None


class Priority(Enum):
    """Task priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Task:
    """Background task model"""
    id: str
    name: str
    status: str
    priority: Priority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Utility functions
def create_success_response(command_id: str, result: Dict[str, Any]) -> AIResponse:
    """Create a successful AI response"""
    return AIResponse(
        id=command_id,
        success=True,
        result=result
    )


def create_error_response(command_id: str, error: str) -> AIResponse:
    """Create an error AI response"""
    return AIResponse(
        id=command_id,
        success=False,
        error=error
    )


def serialize_datetime(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

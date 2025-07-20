"""
Base Connector Interface

This module defines the base interface that all external software connectors
must implement for consistent integration with the Miktos AI Bridge.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class ConnectorStatus(Enum):
    """Connector status enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class BaseConnector(ABC):
    """Base connector interface for external software integration"""
    
    def __init__(self, name: str):
        self.name = name
        self.status = ConnectorStatus.DISCONNECTED
        self.last_error: Optional[str] = None
        self.connection_params: Dict[str, Any] = {}
        
    @abstractmethod
    async def connect(self, **kwargs) -> bool:
        """Establish connection to external software"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from external software"""
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if connection is active"""
        pass
    
    @abstractmethod
    async def get_scene_info(self) -> Dict[str, Any]:
        """Get current scene information"""
        pass
    
    @abstractmethod
    async def apply_texture(self, object_name: str, texture_path: str, **kwargs) -> bool:
        """Apply texture to specified object"""
        pass
    
    @abstractmethod
    async def execute_script(self, script: str) -> Dict[str, Any]:
        """Execute script in external software"""
        pass
    
    # Common utility methods
    def get_status(self) -> Dict[str, Any]:
        """Get connector status"""
        return {
            "name": self.name,
            "status": self.status.value,
            "connected": self.status == ConnectorStatus.CONNECTED,
            "last_error": self.last_error
        }
    
    def set_error(self, error_message: str):
        """Set error status"""
        self.status = ConnectorStatus.ERROR
        self.last_error = error_message
        logger.error(f"{self.name} connector error: {error_message}")
    
    async def close(self):
        """Cleanup and close connector"""
        if self.status == ConnectorStatus.CONNECTED:
            await self.disconnect()

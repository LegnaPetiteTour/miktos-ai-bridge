"""
Configuration management for Miktos AI Bridge
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Server settings
    host: str = "localhost"
    port: int = 8000
    debug: bool = True
    
    # AI Model settings
    model_cache_dir: str = "models"
    device: str = "cpu"  # Will auto-detect GPU if available
    
    # ComfyUI settings
    comfyui_host: str = "localhost"
    comfyui_port: int = 8188
    comfyui_timeout: int = 300
    
    # API settings
    api_version: str = "v1"
    cors_origins: list = ["*"]
    
    # Logging settings
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Development settings
    auto_reload: bool = True
    
    class Config:
        env_file = ".env"
        env_prefix = "MIKTOS_"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings
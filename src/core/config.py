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
    comfyui_url: str = "http://localhost:8188"
    comfyui_models_path: str = "./models"
    comfyui_output_path: str = "./output"
    comfyui_timeout: int = 300
    comfyui_standalone_mode: bool = True  # Run without external ComfyUI server
    
    # Database settings
    database_url: str = "sqlite:///./miktos.db"
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    
    # Security settings
    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # External API settings
    huggingface_api_key: str = "your-hf-key-here"
    openai_api_key: str = "your-openai-key-here"
    
    # Blender settings
    blender_path: str = "/Applications/Blender.app/Contents/MacOS/Blender"
    blender_addon_port: int = 9999
    
    # Output directories
    output_dir: str = "./output"
    texture_output_dir: str = "./output/textures"
    model_output_dir: str = "./output/models"
    
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
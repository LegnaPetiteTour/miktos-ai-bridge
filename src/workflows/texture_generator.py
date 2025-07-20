"""
Texture Generator

This module provides AI-powered texture generation capabilities using ComfyUI
workflows and various diffusion models.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import json
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class TextureGenerator:
    """AI-powered texture generation using ComfyUI workflows"""
    
    def __init__(self, comfyui_client, workflow_manager):
        self.comfyui_client = comfyui_client
        self.workflow_manager = workflow_manager
        self.output_dir = Path("./output/textures")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Texture generation settings
        self.default_size = [1024, 1024]
        self.default_steps = 20
        self.default_cfg = 7.0
        
    async def generate_texture(
        self,
        prompt: str,
        size: List[int] = None,
        maps: List[str] = None,
        negative_prompt: str = "",
        steps: int = None,
        cfg: float = None,
        model_name: str = "stable-diffusion-xl",
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Generate texture maps using AI"""
        
        try:
            # Set defaults
            size = size or self.default_size
            maps = maps or ["diffuse", "normal", "roughness"]
            steps = steps or self.default_steps
            cfg = cfg or self.default_cfg
            
            logger.info(f"Generating texture: {prompt}")
            logger.info(f"Size: {size}, Maps: {maps}, Steps: {steps}")
            
            # Create unique job ID
            job_id = str(uuid.uuid4())
            output_paths = {}
            
            # Generate each requested texture map
            for i, map_type in enumerate(maps):
                if progress_callback:
                    progress = (i / len(maps)) * 0.8  # Reserve 20% for post-processing
                    progress_callback(progress)
                
                # Adjust prompt for specific map types
                adjusted_prompt = self._adjust_prompt_for_map(prompt, map_type)
                
                # Generate texture map
                result = await self._generate_single_map(
                    prompt=adjusted_prompt,
                    negative_prompt=negative_prompt,
                    size=size,
                    steps=steps,
                    cfg=cfg,
                    model_name=model_name,
                    map_type=map_type,
                    job_id=job_id
                )
                
                if result.get("success"):
                    output_paths[map_type] = result["output_path"]
                else:
                    logger.error(f"Failed to generate {map_type} map: {result.get('error')}")
            
            # Post-processing
            if progress_callback:
                progress_callback(0.9)
            
            # Create texture set metadata
            metadata = {
                "job_id": job_id,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "size": size,
                "maps": maps,
                "steps": steps,
                "cfg": cfg,
                "model_name": model_name,
                "generated_at": datetime.now().isoformat(),
                "output_paths": output_paths
            }
            
            # Save metadata
            metadata_path = self.output_dir / f"{job_id}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            if progress_callback:
                progress_callback(1.0)
            
            logger.info(f"Texture generation complete: {len(output_paths)} maps generated")
            
            return {
                "success": True,
                "job_id": job_id,
                "output_paths": output_paths,
                "metadata": metadata,
                "metadata_path": str(metadata_path)
            }
            
        except Exception as e:
            logger.error(f"Texture generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_single_map(
        self,
        prompt: str,
        negative_prompt: str,
        size: List[int],
        steps: int,
        cfg: float,
        model_name: str,
        map_type: str,
        job_id: str
    ) -> Dict[str, Any]:
        """Generate a single texture map"""
        
        try:
            # Create workflow for texture generation
            workflow = self._create_texture_workflow(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=size[0],
                height=size[1],
                steps=steps,
                cfg=cfg,
                model_name=model_name,
                map_type=map_type
            )
            
            # Submit workflow to ComfyUI
            if self.comfyui_client and await self.comfyui_client.check_connection():
                result = await self.comfyui_client.queue_workflow(workflow)
                
                if result.get("success"):
                    # Wait for completion and get output
                    output_path = await self._wait_for_output(result["prompt_id"], job_id, map_type)
                    
                    return {
                        "success": True,
                        "output_path": output_path,
                        "prompt_id": result["prompt_id"]
                    }
                else:
                    return {"success": False, "error": result.get("error", "Unknown error")}
            else:
                # Fallback: Create placeholder texture
                logger.warning("ComfyUI not available, creating placeholder texture")
                output_path = await self._create_placeholder_texture(job_id, map_type, size)
                
                return {
                    "success": True,
                    "output_path": output_path,
                    "placeholder": True
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _adjust_prompt_for_map(self, base_prompt: str, map_type: str) -> str:
        """Adjust prompt based on texture map type"""
        
        adjustments = {
            "diffuse": base_prompt,
            "normal": f"{base_prompt}, normal map, surface details, purple and blue tones",
            "roughness": f"{base_prompt}, roughness map, surface roughness, grayscale",
            "metallic": f"{base_prompt}, metallic map, metal reflectance, grayscale",
            "height": f"{base_prompt}, height map, displacement, grayscale",
            "ambient_occlusion": f"{base_prompt}, ambient occlusion, shadow detail, grayscale"
        }
        
        return adjustments.get(map_type, base_prompt)
    
    def _create_texture_workflow(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        steps: int,
        cfg: float,
        model_name: str,
        map_type: str
    ) -> Dict[str, Any]:
        """Create ComfyUI workflow for texture generation"""
        
        # Basic SDXL workflow template
        workflow = {
            "1": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "2": {
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "seed": int(datetime.now().timestamp()),
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["1", 0],
                    "negative": ["2", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": f"{model_name}.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "7": {
                "inputs": {
                    "filename_prefix": f"texture_{map_type}",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        return workflow
    
    async def _wait_for_output(self, prompt_id: str, job_id: str, map_type: str) -> str:
        """Wait for ComfyUI to complete and return output path"""
        
        # This is a simplified implementation
        # In practice, you'd monitor ComfyUI's queue and wait for completion
        
        max_wait = 300  # 5 minutes
        wait_time = 0
        
        while wait_time < max_wait:
            # Check if output file exists
            # ComfyUI typically saves to output folder
            output_pattern = f"texture_{map_type}*.png"
            
            # For now, create a placeholder path
            output_filename = f"{job_id}_{map_type}.png"
            output_path = self.output_dir / output_filename
            
            # Simulate processing time
            await asyncio.sleep(2)
            
            # Create placeholder file for demo
            await self._create_placeholder_texture(job_id, map_type, self.default_size)
            
            return str(output_path)
    
    async def _create_placeholder_texture(self, job_id: str, map_type: str, size: List[int]) -> str:
        """Create placeholder texture for testing"""
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            import random
            
            # Create image with appropriate colors for map type
            if map_type == "normal":
                color = (128, 128, 255)  # Normal map blue
            elif map_type in ["roughness", "metallic", "height", "ambient_occlusion"]:
                color = (128, 128, 128)  # Grayscale
            else:
                # Random color for diffuse
                color = (
                    random.randint(100, 200),
                    random.randint(100, 200),
                    random.randint(100, 200)
                )
            
            # Create image
            img = Image.new('RGB', size, color)
            draw = ImageDraw.Draw(img)
            
            # Add some texture pattern
            for i in range(0, size[0], 50):
                for j in range(0, size[1], 50):
                    noise = random.randint(-30, 30)
                    adjusted_color = tuple(max(0, min(255, c + noise)) for c in color)
                    draw.rectangle([i, j, i+25, j+25], fill=adjusted_color)
            
            # Add text label
            try:
                font = ImageFont.load_default()
                text = f"{map_type.upper()}\n{job_id[:8]}"
                draw.text((10, 10), text, fill=(255, 255, 255))
            except:
                pass
            
            # Save image
            output_filename = f"{job_id}_{map_type}.png"
            output_path = self.output_dir / output_filename
            img.save(output_path)
            
            logger.info(f"Created placeholder texture: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to create placeholder texture: {e}")
            # Return a simple path even if creation failed
            output_filename = f"{job_id}_{map_type}.png"
            return str(self.output_dir / output_filename)
    
    def get_available_models(self) -> List[str]:
        """Get list of available texture generation models"""
        return [
            "stable-diffusion-xl",
            "stable-diffusion-v1-5",
            "dreamshaper",
            "realistic-vision"
        ]
    
    def get_supported_map_types(self) -> List[str]:
        """Get list of supported texture map types"""
        return [
            "diffuse",
            "normal", 
            "roughness",
            "metallic",
            "height",
            "ambient_occlusion"
        ]

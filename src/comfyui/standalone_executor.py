"""
Standalone ComfyUI Workflow Executor
For testing and development without external ComfyUI server
"""
import asyncio
import logging
import json
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class StandaloneComfyUIExecutor:
    """
    Standalone ComfyUI workflow executor for testing and development
    Simulates ComfyUI workflow execution without requiring external server
    """
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    async def check_connection(self) -> bool:
        """Always returns True for standalone mode"""
        return True
        
    def is_connected(self) -> bool:
        """Always returns True for standalone mode"""
        return True
        
    async def submit_workflow(self, workflow: Dict[str, Any]) -> Optional[str]:
        """
        Simulate workflow submission and execution
        Returns a mock prompt_id for testing
        """
        try:
            prompt_id = str(uuid.uuid4())
            logger.info(f"[STANDALONE] Simulating workflow execution: {prompt_id}")
            
            # Simulate processing time
            await asyncio.sleep(2)
            
            # Create mock output file
            output_file = self.output_dir / f"mock_texture_{prompt_id[:8]}.png"
            
            # Create a simple text file as mock output
            with open(output_file.with_suffix('.txt'), 'w') as f:
                f.write(f"Mock ComfyUI output for workflow: {prompt_id}\n")
                f.write(f"Workflow: {json.dumps(workflow, indent=2)}\n")
                f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            logger.info(f"[STANDALONE] Workflow completed: {output_file}")
            return prompt_id
            
        except Exception as e:
            logger.error(f"[STANDALONE] Workflow execution error: {e}")
            return None
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Return mock queue status"""
        return {
            "queue_running": [],
            "queue_pending": []
        }
    
    async def check_connection(self) -> bool:
        """Always return True for standalone mode"""
        return True
    
    async def get_available_models(self) -> List[str]:
        """Return mock available models"""
        return [
            "standalone_sd_v1.5",
            "standalone_sd_xl",
            "standalone_control_net"
        ]
    
    async def execute_simple_generation(
        self,
        prompt: str,
        negative_prompt: str = "",
        steps: int = 20,
        cfg: float = 7.0,
        width: int = 512,
        height: int = 512
    ) -> Dict[str, Any]:
        """Execute a simple texture generation workflow"""
        try:
            logger.info(f"[STANDALONE] Simple generation: {prompt}")
            
            # Simulate processing
            await asyncio.sleep(1.5)
            
            # Create mock result
            result = {
                "status": "completed",
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "parameters": {
                    "steps": steps,
                    "cfg": cfg,
                    "width": width,
                    "height": height
                },
                "output_files": [f"mock_texture_{int(time.time())}.png"],
                "execution_time": 1.5
            }
            
            logger.info(f"[STANDALONE] Simple generation completed")
            return result
            
        except Exception as e:
            logger.error(f"[STANDALONE] Simple generation error: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def close(self):
        """No cleanup needed for standalone mode"""
        logger.info("[STANDALONE] ComfyUI executor closed")

#!/bin/bash

# Miktos AI Bridge Startup Script
echo "🚀 Starting Miktos AI Bridge in Standalone Mode"
echo "==============================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run from the miktos-ai-bridge directory."
    exit 1
fi

# Export environment variables for standalone mode
export COMFYUI_STANDALONE_MODE=true
export COMFYUI_URL="http://localhost:8188"
export LOG_LEVEL="INFO"

echo "✅ Environment configured:"
echo "   - Standalone Mode: $COMFYUI_STANDALONE_MODE"
echo "   - ComfyUI URL: $COMFYUI_URL"
echo "   - Log Level: $LOG_LEVEL"

echo ""
echo "🔧 Starting server on http://localhost:8000..."
echo "   - Swagger UI: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/health"
echo "   - Status: http://localhost:8000/api/v1/status"
echo ""

# Start the server
python main.py

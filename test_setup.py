#!/usr/bin/env python3
"""
Simple test script to verify the AI Bridge setup
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🧠 Miktos AI Bridge - Test Script")
print("================================")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print("")

try:
    print("Testing imports...")
    import fastapi
    print("✅ FastAPI imported successfully")
    
    import uvicorn
    print("✅ Uvicorn imported successfully")
    
    import torch
    print("✅ PyTorch imported successfully")
    
    from src.core.config import settings
    print("✅ Config imported successfully")
    
    print("")
    print("🎉 All imports successful!")
    print("✅ AI Bridge setup is working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
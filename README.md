# Miktos AI Bridge

> High-performance Python FastAPI backend for AI workflow orchestration and ComfyUI integration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-FF6B6B?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMCA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDQgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSJjdXJyZW50Q29sb3IiLz4KPC9zdmc+)](https://github.com/comfyanonymous/ComfyUI)

The Miktos AI Bridge is a robust Python FastAPI backend that orchestrates AI workflows, manages ComfyUI integration, and provides high-performance APIs for the Miktos creative platform.

## ✨ Features

- **FastAPI Backend**: High-performance async API with automatic OpenAPI documentation
- **ComfyUI Integration**: Direct integration with ComfyUI for advanced AI workflows
- **Workflow Management**: Create, execute, and monitor complex AI pipelines
- **Real-time Monitoring**: WebSocket support for live progress updates
- **Background Processing**: Async task execution with Celery integration
- **Model Management**: Automatic model discovery and management
- **Security**: JWT authentication, rate limiting, and CORS protection
- **Extensible**: Plugin architecture for custom AI integrations

## 🚀 Quick Start

### Prerequisites

- **Python** 3.11+ (3.12 recommended)
- **Git** for cloning repositories
- **CUDA** (optional, for GPU acceleration)

### Installation

```bash
# Clone the repository
git clone https://github.com/Miktos-Universe/miktos-ai-bridge.git
cd miktos-ai-bridge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the development server
python main.py
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

### Docker Installation

```bash
# Build the Docker image
docker build -t miktos-ai-bridge .

# Run the container
docker run -p 8000:8000 -v $(pwd)/models:/app/models miktos-ai-bridge
```

## 🏗️ Architecture

### Core Components

```text
miktos-ai-bridge/
├── src/
│   ├── api/                    # FastAPI route definitions
│   │   ├── v1/                 # API version 1
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── workflows.py    # Workflow management
│   │   │   ├── tasks.py        # Task execution and monitoring
│   │   │   └── status.py       # System status and health
│   │   └── deps.py             # Dependency injection
│   ├── core/                   # Core business logic
│   │   ├── bridge.py           # Main bridge orchestrator
│   │   ├── config.py           # Configuration management
│   │   ├── security.py         # Authentication and security
│   │   └── exceptions.py       # Custom exception handling
│   ├── comfyui/               # ComfyUI integration
│   │   ├── client.py          # ComfyUI API client
│   │   ├── workflow_parser.py # Workflow parsing and validation
│   │   └── model_manager.py   # Model discovery and management
│   ├── connectors/            # External service integrations
│   │   ├── base.py            # Base connector interface
│   │   ├── comfyui.py         # ComfyUI connector implementation
│   │   └── huggingface.py     # Hugging Face integration
│   └── workflows/             # Workflow templates and management
│       ├── base.py            # Base workflow interface
│       ├── templates/         # Pre-built workflow templates
│       └── executor.py        # Workflow execution engine
├── tests/                     # Test suite
├── docs/                      # Documentation
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
└── main.py                    # Application entry point
```

### Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping
- **Celery**: Distributed task queue for background processing
- **Redis**: In-memory data store for caching and task queuing
- **WebSockets**: Real-time communication for progress updates
- **ComfyUI**: Backend integration for AI workflow execution

## 📡 API Endpoints

### Core Endpoints

```http
# Health and Status
GET  /health                    # Health check
GET  /api/v1/status            # Detailed system status

# Authentication
POST /api/v1/auth/token        # Get access token
POST /api/v1/auth/refresh      # Refresh token

# Workflow Management
GET    /api/v1/workflows       # List available workflows
POST   /api/v1/workflows       # Create new workflow
GET    /api/v1/workflows/{id}  # Get workflow details
PUT    /api/v1/workflows/{id}  # Update workflow
DELETE /api/v1/workflows/{id}  # Delete workflow

# Task Execution
POST /api/v1/execute-command   # Execute AI command
POST /api/v1/workflows/{id}/execute # Execute specific workflow
GET  /api/v1/task/{task_id}    # Get task status and results

# Model Management
GET  /api/v1/models           # List available AI models
POST /api/v1/models/refresh   # Refresh model list
```

### WebSocket Endpoints

```http
# Real-time Updates
WS /ws/status                 # System status updates
WS /ws/tasks/{task_id}        # Task progress updates
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file for local development:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=info

# ComfyUI Configuration
COMFYUI_URL=http://localhost:8188
COMFYUI_MODELS_PATH=./models
COMFYUI_OUTPUT_PATH=./output

# Database
DATABASE_URL=sqlite:///./miktos.db

# Redis (for Celery)
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External APIs
HUGGINGFACE_API_KEY=your-hf-key-here
OPENAI_API_KEY=your-openai-key-here
```

### Production Configuration

For production deployment, use environment variables or a configuration management system:

```bash
# Production settings
DEBUG=false
LOG_LEVEL=warning
DATABASE_URL=postgresql://user:pass@localhost/miktos
REDIS_URL=redis://redis-server:6379
```

## 🧪 Development

### Setting up Development Environment

```bash
# Clone and setup
git clone https://github.com/Miktos-Universe/miktos-ai-bridge.git
cd miktos-ai-bridge

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Start development server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_workflows.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/

# Security scanning
bandit -r src/
```

## 🚀 Deployment

### Docker Deployment

```dockerfile
# Build production image
docker build -t miktos-ai-bridge:latest .

# Run with environment file
docker run --env-file .env -p 8000:8000 miktos-ai-bridge:latest

# Docker Compose (recommended)
docker-compose up -d
```

### Production Deployment

```bash
# Using Gunicorn for production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using systemd service
sudo systemctl enable miktos-ai-bridge
sudo systemctl start miktos-ai-bridge

# Using PM2
pm2 start ecosystem.config.js
```

## 🔌 Integration

### ComfyUI Setup

1. Install ComfyUI in a separate directory
2. Configure the `COMFYUI_URL` environment variable
3. Ensure ComfyUI API is enabled
4. Place AI models in the configured models directory

### Desktop App Integration

The AI Bridge communicates with the Miktos Desktop app through:

- RESTful API endpoints for command execution
- WebSocket connections for real-time updates
- Status monitoring for connection health
- File-based output sharing

## 📊 Monitoring

### Health Checks

```bash
# Check service health
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/api/v1/status
```

### Logging

Logs are written to:

- Console output (development)
- Log files in `/logs/` directory (production)
- Structured JSON logging for production monitoring

### Metrics

- API request/response times
- Task execution metrics
- ComfyUI integration status
- System resource usage

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with proper tests
4. Run the test suite: `pytest`
5. Commit with conventional commits: `git commit -m 'feat: add amazing feature'`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- **[Miktos Desktop](https://github.com/Miktos-Universe/miktos-desktop)**: Cross-platform desktop application
- **[Miktos Workflows](https://github.com/Miktos-Universe/miktos-workflows)**: Pre-built workflow templates
- **[Miktos Docs](https://github.com/Miktos-Universe/miktos-docs)**: Comprehensive documentation

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com) for the excellent web framework
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) for AI workflow capabilities
- [Pydantic](https://pydantic-docs.helpmanual.io) for data validation
- All our contributors and the open-source community

---

Built with ❤️ by the Miktos team

[Organization](https://github.com/Miktos-Universe) • [Website](https://miktos.com) • [Twitter](https://twitter.com/MiktosAI)

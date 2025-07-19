# Contributing to Miktos AI Bridge

Thank you for your interest in contributing to the Miktos AI Bridge! This document provides guidelines for contributing to the Python FastAPI backend.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/miktos-ai-bridge.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -r requirements-dev.txt`
6. Start development server: `python main.py`

## Development Workflow

### Prerequisites

- Python 3.11+ (3.12 recommended)
- Git
- Redis (for Celery background tasks)
- PostgreSQL (for production, SQLite for development)

### Setting Up the Development Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Copy environment template
cp .env.example .env

# Start development server
python main.py
```

### Code Style and Standards

We follow Python best practices and use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/

# Run all quality checks
make quality
```

### Testing

We maintain high test coverage and require tests for all new functionality:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_workflows.py

# Run tests with verbose output
pytest -v

# Run tests for specific functionality
pytest -k "test_workflow"
```

### API Development

When adding new API endpoints:

1. **Use FastAPI best practices**
2. **Add proper type hints** with Pydantic models
3. **Include comprehensive docstrings**
4. **Add input validation**
5. **Implement proper error handling**
6. **Write unit tests**
7. **Update API documentation**

Example endpoint structure:

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

class WorkflowCreate(BaseModel):
    name: str
    description: str
    workflow_data: dict

@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(
    workflow: WorkflowCreate,
    current_user: User = Depends(get_current_user)
) -> WorkflowResponse:
    """Create a new workflow."""
    try:
        # Implementation here
        pass
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Submitting Changes

### Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes following the code style guidelines
3. Add tests for new functionality
4. Ensure all tests pass: `pytest`
5. Run code quality checks: `make quality`
6. Update documentation if needed
7. Commit with clear, conventional commit messages
8. Push to your fork
9. Create a Pull Request

### Commit Message Format

We use [Conventional Commits](https://conventionalcommits.org/) format:

```text
type(scope): description

feat(api): add workflow execution endpoint
fix(comfyui): resolve connection timeout issue
docs(readme): update installation instructions
test(workflows): add unit tests for workflow parser
refactor(core): improve error handling
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

### PR Requirements

- [ ] Code follows style guidelines (Black, isort, flake8)
- [ ] Type hints are properly used (mypy passes)
- [ ] Tests added/updated for changes
- [ ] All tests pass locally
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Security considerations addressed

## Development Guidelines

### Architecture Principles

- **Separation of Concerns**: Keep API routes, business logic, and data access separate
- **Dependency Injection**: Use FastAPI's dependency system for testability
- **Async/Await**: Use async patterns for I/O operations
- **Type Safety**: Use type hints throughout the codebase
- **Error Handling**: Implement comprehensive error handling with appropriate HTTP status codes

### API Design

- Follow RESTful principles
- Use appropriate HTTP methods (GET, POST, PUT, DELETE)
- Implement proper status codes
- Use Pydantic models for request/response validation
- Include comprehensive API documentation

### Performance Considerations

- Use async/await for database operations
- Implement proper connection pooling
- Cache frequently accessed data
- Use background tasks for long-running operations
- Monitor and optimize database queries

### Security Guidelines

- Validate all input data
- Use parameterized queries to prevent SQL injection
- Implement proper authentication and authorization
- Follow OWASP security guidelines
- Never log sensitive information
- Use environment variables for secrets

## Testing Guidelines

### Test Structure

```text
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_api/               # API endpoint tests
│   ├── test_auth.py
│   ├── test_workflows.py
│   └── test_status.py
├── test_core/              # Core business logic tests
│   ├── test_bridge.py
│   └── test_config.py
├── test_comfyui/          # ComfyUI integration tests
│   └── test_client.py
└── test_integration/       # Integration tests
    └── test_end_to_end.py
```

### Testing Best Practices

- Write tests for all new functionality
- Use meaningful test names that describe what is being tested
- Arrange, Act, Assert pattern for test structure
- Use fixtures for common test setup
- Mock external dependencies
- Test both success and error scenarios

### Example Test

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_workflow():
    """Test creating a new workflow."""
    workflow_data = {
        "name": "Test Workflow",
        "description": "A test workflow",
        "workflow_data": {"nodes": []}
    }
    
    response = client.post("/api/v1/workflows", json=workflow_data)
    
    assert response.status_code == 201
    assert response.json()["name"] == "Test Workflow"
```

## Documentation

### Code Documentation

- Use docstrings for all modules, classes, and functions
- Follow Google docstring format
- Include type hints for better IDE support
- Add inline comments for complex logic

### API Documentation

- FastAPI automatically generates OpenAPI documentation
- Ensure all endpoints have proper descriptions
- Use Pydantic models for request/response schemas
- Include examples in the documentation

## Reporting Issues

When reporting bugs or requesting features:

1. Check existing issues first
2. Use the appropriate issue template
3. Provide detailed reproduction steps
4. Include system information (Python version, OS, etc.)
5. Add relevant logs or error messages
6. Suggest potential solutions if you have ideas

## Questions and Support

Feel free to:

- Open a discussion on GitHub
- Reach out to maintainers
- Join our developer community
- Check the documentation

## Recognition

We appreciate all contributions and will recognize contributors in:

- Release notes
- Contributors file
- GitHub contributor graphs
- Special recognition for significant contributions

Thank you for contributing to Miktos AI Bridge!

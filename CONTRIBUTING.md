# Contributing to Libraries.io MCP Server

Thank you for your interest in contributing to the Libraries.io MCP Server! This document provides guidelines and instructions for developers who want to contribute to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Architecture Overview](#architecture-overview)
- [Development Workflow](#development-workflow)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)
- [Community Guidelines](#community-guidelines)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)
- Basic knowledge of Python and async programming

### First-Time Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/libraries-io-mcp-server.git
   cd libraries-io-mcp-server
   ```
3. **Set up your development environment** (see [Development Setup](#development-setup))
4. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
5. **Make your changes** and test them
6. **Submit a pull request** (see [Submitting Changes](#submitting-changes))

## Development Setup

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/librariesio/libraries-io-mcp-server.git
cd libraries-io-mcp-server

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 2. Environment Configuration

```bash
# Copy environment file
cp .env.example .env

# Edit the .env file with your configuration
# At minimum, you need a Libraries.io API key
```

### 3. Verify Setup

```bash
# Run tests to verify everything is working
pytest

# Run linting
flake8 src/
black --check src/
isort --check-only src/

# Run type checking
mypy src/
```

## Code Style Guidelines

### Python Style Guide

We follow the **PEP 8** style guide with some additional rules:

#### 1. Code Formatting

- **Line Length**: Maximum 88 characters (Black's default)
- **Indentation**: 4 spaces per level
- **Imports**: Use `isort` for import sorting
- **Quotes**: Prefer double quotes (`"`) for strings

#### 2. Naming Conventions

- **Functions and Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private Methods**: `_single_leading_underscore`
- **Protected Methods**: `__double_leading_underscore__`

#### 3. Function and Class Design

- **Functions**: Keep functions small and focused (under 50 lines)
- **Classes**: Single responsibility principle
- **Methods**: Keep under 30 lines when possible
- **Parameters**: Use type hints for all parameters and return values

#### 4. Type Hints

Use type hints consistently:

```python
from typing import List, Dict, Optional, AsyncIterator

def get_package_names(platform: str) -> List[str]:
    """Get package names for a platform."""
    return []

async def search_packages(
    query: str,
    platforms: Optional[List[str]] = None,
    limit: int = 10
) -> AsyncIterator[Dict[str, any]]:
    """Search for packages asynchronously."""
    # Implementation
```

#### 5. Error Handling

- Use specific exception types
- Provide meaningful error messages
- Log errors appropriately
- Use custom exceptions when appropriate

```python
from libraries_io_mcp.exceptions import LibrariesIOClientError

try:
    result = await client.get_package_info(platform, name)
except httpx.HTTPError as e:
    raise LibrariesIOClientError(f"Network error: {e}")
except Exception as e:
    raise LibrariesIOClientError(f"Unexpected error: {e}")
```

### Documentation Standards

#### 1. Docstrings

Use Google-style docstrings:

```python
def search_packages(
    query: str,
    platforms: Optional[List[str]] = None,
    limit: int = 10
) -> List[Dict[str, any]]:
    """Search for packages across multiple platforms.
    
    Args:
        query: Search query string
        platforms: List of platforms to search (optional)
        limit: Maximum number of results
        
    Returns:
        List of matching packages
        
    Raises:
        LibrariesIOClientError: If API request fails
    """
```

#### 2. Comments

- Use comments to explain **why** something is done, not **what**
- Keep comments up to date with code changes
- Use `#` followed by a space for comments

#### 3. TODO Comments

Use `TODO` comments sparingly and be specific:

```python
# TODO: Add rate limiting to prevent API abuse
# TODO: Implement caching for frequently accessed packages
```

## Testing

### Test Structure

```
tests/
├── conftest.py          # Test configuration and fixtures
├── unit/                # Unit tests
│   ├── test_client.py
│   ├── test_models.py
│   ├── test_tools.py
│   └── test_utils.py
├── integration/         # Integration tests
│   └── test_server_integration.py
└── fixtures/            # Test data
    └── mock_responses.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_client.py

# Run specific test
pytest tests/unit/test_client.py::test_get_package_info

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v
```

### Writing Tests

#### Unit Tests

```python
import pytest
from libraries_io_mcp.client import LibrariesIOClient
from libraries_io_mcp.exceptions import LibrariesIOClientError

@pytest.fixture
def client():
    """Create a test client."""
    return LibrariesIOClient(api_key="test_key")

def test_get_package_info_success(client):
    """Test successful package info retrieval."""
    # Mock the HTTP response
    with httpx.Client() as mock_client:
        # Setup mock response
        mock_client.get.return_value = httpx.Response(
            200,
            json={"name": "react", "platform": "npm"}
        )
        
        # Test the function
        result = client.get_package_info("npm", "react")
        
        # Assertions
        assert result["name"] == "react"
        assert result["platform"] == "npm"

def test_get_package_info_error(client):
    """Test error handling in package info retrieval."""
    with pytest.raises(LibrariesIOClientError):
        # Test error case
        client.get_package_info("invalid", "package")
```

#### Integration Tests

```python
import pytest
import asyncio
from libraries_io_mcp.server import create_server

@pytest.fixture
async def server():
    """Create a test server."""
    server = await create_server()
    yield server
    await server.shutdown()

@pytest.mark.asyncio
async def test_server_integration(server):
    """Test server integration with Libraries.io API."""
    # Test actual API integration
    result = await server.get_package_info("npm", "react")
    assert result["success"] is True
    assert result["data"]["name"] == "react"
```

### Test Coverage

- **Minimum Coverage**: 80% line coverage
- **Critical Modules**: 95% coverage for core modules
- **Test Types**: Unit tests for business logic, integration tests for API calls

## Submitting Changes

### Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** following the guidelines
3. **Update tests** for any new functionality
4. **Run the test suite** to ensure everything passes
5. **Update documentation** if needed
6. **Commit your changes** with clear messages
7. **Push to your fork** and create a pull request

### Commit Message Guidelines

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

#### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build or tool changes

#### Examples:
```
feat(tools): add package search functionality
fix(client): handle rate limit errors properly
docs(readme): update installation instructions
test(tools): add unit tests for search functionality
```

### Pull Request Template

```markdown
## Description
Brief description of the changes

## Changes Made
- [ ] Added new feature
- [ ] Fixed bug
- [ ] Updated tests
- [ ] Updated documentation

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] PR description is clear
- [ ] Breaking changes documented
```

## Architecture Overview

### Project Structure

```
src/libraries_io_mcp/
├── __init__.py          # Package initialization
├── client.py            # HTTP client for Libraries.io API
├── models.py            # Data models and schemas
├── server.py            # FastMCP server implementation
├── tools.py             # MCP tools implementation
├── resources.py         # MCP resources implementation
├── prompts.py           # MCP prompts implementation
├── utils.py             # Utility functions
└── exceptions.py        # Custom exceptions
```

### Core Components

#### 1. Client (`client.py`)
- Handles HTTP communication with Libraries.io API
- Manages authentication and rate limiting
- Provides low-level API methods

#### 2. Models (`models.py`)
- Pydantic models for data validation
- Request/response schemas
- Type definitions for all API interactions

#### 3. Server (`server.py`)
- FastMCP server implementation
- Tool and resource registration
- Request routing and handling

#### 4. Tools (`tools.py`)
- MCP tool implementations
- Business logic for package operations
- Error handling and validation

#### 5. Resources (`resources.py`)
- MCP resource implementations
- Data access patterns
- URI handling and parsing

#### 6. Prompts (`prompts.py`)
- MCP prompt templates
- AI interaction patterns
- Context generation

### Data Flow

```
User Request → MCP Client → Tool Function → API Client → Libraries.io API
                                                    ↓
Response ← Data Model ← HTTP Response ← JSON Response
```

### Design Patterns

1. **Repository Pattern**: Abstract data access through models
2. **Factory Pattern**: Create different types of API clients
3. **Strategy Pattern**: Handle different platform behaviors
4. **Observer Pattern**: Rate limiting and monitoring
5. **Command Pattern**: Tool execution and result handling

## Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/add-package-comparison

# Make changes
# Write tests
# Run tests
pytest

# Format code
black src/
isort src/

# Commit changes
git add .
git commit -m "feat(tools): add package comparison functionality"

# Push and create PR
git push origin feature/add-package-comparison
```

### 2. Bug Fix Development

```bash
# Create bugfix branch
git checkout -b fix/rate-limit-handling

# Identify and fix the bug
# Add regression tests
# Verify fix works
# Commit and push
git commit -m "fix(client): improve rate limit error handling"
```

### 3. Documentation Updates

```bash
# Create docs branch
git checkout -b docs/api-documentation

# Update documentation
# Add examples
# Update README if needed
git commit -m "docs(api): add comprehensive API documentation"
```

### 4. Release Process

1. **Update Version**: Bump version in `pyproject.toml`
2. **Update Changelog**: Add changes to `CHANGELOG.md`
3. **Run Tests**: Ensure all tests pass
4. **Create Release Tag**: `git tag v1.0.0`
5. **Push Changes**: `git push origin main --tags`

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Environment Information**:
   - Python version
   - Operating system
   - Package version

2. **Steps to Reproduce**:
   ```python
   # Code that reproduces the issue
   result = await get_package_info("npm", "react")
   ```

3. **Expected Behavior**:
   What should happen

4. **Actual Behavior**:
   What actually happened

5. **Error Messages**:
   Full error traceback if available

### Issue Template

```markdown
## Bug Report

**Environment:**
- Python: 3.9.0
- OS: Ubuntu 20.04
- Version: 0.1.0

**Steps to Reproduce:**
1. Run `get_package_info("npm", "nonexistent")`
2. Observe error

**Expected:**
Graceful error handling with meaningful message

**Actual:**
Generic HTTP error

**Error:**
```
Traceback (most recent call last):
  File "test.py", line 10, in <module>
    result = await get_package_info("npm", "nonexistent")
  File "libraries_io_mcp/client.py", line 45, in get_package_info
    response.raise_for_status()
httpx.HTTPStatusError: 404 Not Found
```
```

## Feature Requests

### Request Template

```markdown
## Feature Request

**Description:**
Add support for package version comparison functionality

**Use Case:**
Users want to compare different versions of the same package to see what changed

**Proposed Implementation:**
- Add `compare_versions` tool
- Accept package name, platform, and two version numbers
- Return changelog and differences

**Alternatives Considered:**
- Using existing `get_package_versions` and manual comparison
- Third-party changelog services

**Additional Context:**
This would help users decide whether to upgrade packages
```

## Community Guidelines

### Code of Conduct

This project follows a standard Code of Conduct:

1. **Be Respectful**: Treat all contributors with respect
2. **Be Inclusive**: Welcome contributors from all backgrounds
3. **Be Constructive**: Focus on positive, constructive feedback
4. **Be Collaborative**: Work together to improve the project

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General discussions and Q&A
- **Pull Requests**: Code contributions and reviews

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and linting
2. **Code Review**: At least one maintainer must approve
3. **Testing**: All tests must pass
4. **Documentation**: Documentation must be updated if needed

### Getting Help

- **Documentation**: Check existing docs first
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for general questions
- **Discord/Slack**: Join our community channels (if available)

## Additional Resources

### Learning Materials

- [Python Async Programming Guide](https://docs.python.org/3/library/asyncio.html)
- [FastMCP Documentation](https://fastmcp.readthedocs.io/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [HTTPX Documentation](https://www.python-httpx.org/)

### Tools and Utilities

- **IDE**: VS Code, PyCharm, or your preferred Python IDE
- **Linting**: Flake8, Black, isort
- **Type Checking**: MyPy
- **Testing**: Pytest, pytest-asyncio
- **Git**: GitKraken, SourceTree, or command line

### Contributing to Open Source

- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [Pull Request Etiquette](https://github.com/firstcontributions/first-contributions)
- [Code Review Comments](https://github.com/probot/reviewdog)

---

Thank you for contributing to the Libraries.io MCP Server! Your contributions help make this project better for everyone.
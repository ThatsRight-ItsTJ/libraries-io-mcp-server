
# Testing Procedures

This document provides comprehensive guidelines for testing the Libraries.io MCP Server, including testing strategies, procedures, and best practices.

## Testing Overview

### Testing Philosophy

The Libraries.io MCP Server follows a comprehensive testing strategy that ensures:

- **Quality**: High-quality, reliable code
- **Reliability**: Consistent behavior across different environments
- **Maintainability**: Easy to modify and extend
- **Performance**: Optimal performance under various conditions
- **Security**: Secure implementation resistant to vulnerabilities

### Testing Pyramid

```
┌─────────────────────────────────────────────────────────────────┐
│                      End-to-End Tests                           │
│                     (5% of test suite)                         │
├─────────────────────────────────────────────────────────────────┤
│                      Integration Tests                          │
│                    (20% of test suite)                         │
├─────────────────────────────────────────────────────────────────┤
│                      Unit Tests                                 │
│                   (75% of test suite)                          │
└─────────────────────────────────────────────────────────────────┘
```

### Test Categories

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows
4. **Performance Tests**: Test performance characteristics
5. **Security Tests**: Test security vulnerabilities
6. **Load Tests**: Test system under heavy load

## Test Structure

### Directory Layout

```
tests/
├── __init__.py
├── conftest.py                 # Test configuration and fixtures
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_client.py          # LibrariesIOClient tests
│   ├── test_tools.py           # Tool function tests
│   ├── test_models.py          # Data model tests
│   ├── test_utils.py           # Utility function tests
│   ├── test_middleware.py      # Middleware tests
│   └── test_server.py          # Server component tests
├── integration/                # Integration tests
│   ├── __init__.py
│   ├── test_server_integration.py    # Server integration tests
│   ├── test_api_integration.py       # API integration tests
│   ├── test_cache_integration.py     # Cache integration tests
│   └── test_mcp_integration.py       # MCP protocol tests
├── performance/                # Performance tests
│   ├── __init__.py
│   ├── test_benchmarks.py      # Performance benchmarks
│   ├── test_load_tests.py      # Load testing
│   └── test_memory_usage.py    # Memory usage tests
├── security/                   # Security tests
│   ├── __init__.py
│   ├── test_input_validation.py    # Input validation tests
│   ├── test_authentication.py      # Authentication tests
│   └── test_rate_limiting.py       # Rate limiting tests
└── fixtures/                   # Test data and fixtures
    ├── __init__.py
    ├── mock_responses.py       # Mock API responses
    ├── test_data.py            # Test data generators
    └── sample_packages.json    # Sample package data
```

### Test Configuration

#### conftest.py

```python
# Test configuration and fixtures
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any
import json
import os

from src.libraries_io_mcp.client import LibrariesIOClient
from src.libraries_io_mcp.server import LibrariesIOServer
from src.libraries_io_mcp.models import ToolResponse, PackageInfo


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing."""
    mock_client = AsyncMock()
    mock_client.get = AsyncMock()
    mock_client.post = AsyncMock()
    mock_client.put = AsyncMock()
    mock_client.delete = AsyncMock()
    return mock_client


@pytest.fixture
def mock_rate_limiter():
    """Mock rate limiter for testing."""
    mock_limiter = AsyncMock()
    mock_limiter.wait_if_needed = AsyncMock()
    return mock_limiter


@pytest.fixture
def mock_cache():
    """Mock cache for testing."""
    mock_cache = AsyncMock()
    mock_cache.get = AsyncMock(return_value=None)
    mock_cache.set = AsyncMock()
    mock_cache.clear = AsyncMock()
    return mock_cache


@pytest.fixture
def sample_package_data():
    """Sample package data for testing."""
    return {
        "name": "react",
        "platform": "npm",
        "description": "A JavaScript library for building user interfaces",
        "language": "JavaScript",
        "stars": 200000,
        "homepage": "https://reactjs.org",
        "repository_url": "https://github.com/facebook/react",
        "latest_release_number": "18.2.0",
        "latest_release_published_at": "2023-01-10T00:00:00Z",
        "created_at": "2013-05-24T00:00:00Z",
        "updated_at": "2023-01-10T00:00:00Z"
    }


@pytest.fixture
def sample_search_results():
    """Sample search results for testing."""
    return {
        "total_count": 100,
        "items": [
            {
                "name": "react",
                "platform": "npm",
                "description": "A JavaScript library for building user interfaces",
                "language": "JavaScript",
                "stars": 200000
            },
            {
                "name": "vue",
                "platform": "npm",
                "description": "The Progressive JavaScript Framework",
                "language": "JavaScript",
                "stars": 180000
            }
        ]
    }


@pytest.fixture
def sample_platforms():
    """Sample platforms data for testing."""
    return [
        {
            "name": "npm",
            "homepage": "https://www.npmjs.com",
            "color": "#cb3837",
            "project_count": 2000000,
            "default_language": "JavaScript",
            "package_type": "npm"
        },
        {
            "name": "PyPI",
            "homepage": "https://pypi.org",
            "color": "#3776ab",
            "project_count": 400000,
            "default_language": "Python",
            "package_type": "pypi"
        }
    ]


@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "api_key": "test_api_key",
        "base_url": "https://libraries.io/api/v1",
        "rate_limit_requests": 100,
        "rate_limit_window": 3600,
        "cache_ttl": 30,
        "timeout": 30.0,
        "max_retries": 3
    }


@pytest.fixture
async def test_client(test_config, mock_http_client, mock_rate_limiter, mock_cache):
    """Test LibrariesIOClient instance."""
    from src.libraries_io_mcp.client import LibrariesIOClient
    
    client = LibrariesIOClient(
        api_key=test_config["api_key"],
        config=test_config
    )
    
    # Replace real components with mocks
    client.http_client = mock_http_client
    client.rate_limiter = mock_rate_limiter
    client.cache = mock_cache
    
    return client


@pytest.fixture
def test_server(test_client):
    """Test server instance."""
    from src.libraries_io_mcp.server import LibrariesIOServer
    
    server = LibrariesIOServer(api_key="test_api_key")
    server.client = test_client
    return server
```

## Unit Testing

### Testing LibrariesIOClient

#### test_client.py

```python
# Unit tests for LibrariesIOClient
import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx
from datetime import datetime, timedelta

from src.libraries_io_mcp.client import LibrariesIOClient
from src.libraries_io_mcp.models import ToolResponse


class TestLibrariesIOClient:
    """Test suite for LibrariesIOClient."""
    


### Test Maintenance

#### 1. Regular Test Updates

```bash
# Update tests when code changes
git diff HEAD~1 --name-only | grep -E "\.(py)$" | xargs pytest -v

# Run tests before committing
pre-commit run pytest
```

#### 2. Test Coverage Monitoring

```bash
# Monitor test coverage
pytest --cov=src --cov-report=term-missing

# Set coverage threshold
pytest --cov=src --cov-fail-under=80
```

#### 3. Test Performance Monitoring

```bash
# Monitor test performance
pytest --durations=10

# Run slow tests separately
pytest --durations-min=1.0
```

### Test Reporting

#### 1. HTML Reports

```bash
# Generate HTML test report
pytest --html=reports/test_report.html --self-contained-html

# Generate coverage HTML report
pytest --cov=src --cov-report=html
```

#### 2. JSON Reports

```bash
# Generate JSON test report
pytest --json-report --json-report-file=reports/test_report.json

# Generate coverage JSON report
pytest --cov=src --cov-report=json
```

#### 3. CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -e ".[dev]"
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml --cov-report=term-missing
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
```

### Test Troubleshooting

#### 1. Common Test Issues

```python
# Fix flaky tests
@pytest.mark.asyncio
async def test_flaky_operation(self):
    """Test flaky operation with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = await self.client.get_package_info("npm", "react")
            if result.success:
                return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)  # Wait before retry
```

#### 2. Mock Issues

```python
# Fix mock issues
@pytest.fixture
def mock_response():
    """Mock response with proper setup."""
    mock = AsyncMock()
    mock.status_code = 200
    mock.json.return_value = {"name": "react"}
    return mock

# Use context managers for mocks
@pytest.mark.asyncio
async def test_with_context_manager(self):
    """Test with context manager for mocks."""
    with patch('src.libraries_io_mcp.client.LibrariesIOClient.get_package_info') as mock_get:
        mock_get.return_value = ToolResponse(success=True, data={"name": "react"})
        result = await self.client.get_package_info("npm", "react")
        assert result.success is True
```

#### 3. Async Test Issues

```python
# Fix async test issues
@pytest.mark.asyncio
async def test_async_operation(self):
    """Test async operation properly."""
    # Use asyncio.create_task for concurrent operations
    task1 = asyncio.create_task(self.client.get_package_info("npm", "react"))
    task2 = asyncio.create_task(self.client.get_package_info("npm", "vue"))
    
    results = await asyncio.gather(task1, task2)
    assert len(results) == 2
    assert all(result.success for result in results)
```

### Test Documentation

#### 1. Test Documentation Standards

```python
# Document tests properly
def test_get_package_info_success(self):
    """
    Test successful package info retrieval.
    
    This test verifies that the get_package_info method returns
    a successful response when given valid parameters.
    
    Args:
        test_client: Test LibrariesIOClient instance
        sample_package_data: Sample package data fixture
    
    Expected Behavior:
        - Returns a ToolResponse with success=True
        - Contains the correct package data
        - Includes response time information
        - Makes correct HTTP request
    """
    pass
```

#### 2. Test Data Documentation

```python
# Document test data
@pytest.fixture
def sample_package_data():
    """
    Sample package data for testing.
    
    Returns:
        dict: Sample package data with typical fields
        
    Fields:
        - name: Package name (str)
        - platform: Package platform (str)
        - description: Package description (str)
        - language: Programming language (str)
        - stars: Number of stars (int)
        - homepage: Homepage URL (str)
        - repository_url: Repository URL (str)
        - latest_release_number: Latest version (str)
        - latest_release_published_at: Release date (str)
        - created_at: Creation date (str)
        - updated_at: Last update date (str)
    """
    return {
        "name": "react",
        "platform": "npm",
        "description": "A JavaScript library for building user interfaces",
        "language": "JavaScript",
        "stars": 200000,
        "homepage": "https://reactjs.org",
        "repository_url": "https://github.com/facebook/react",
        "latest_release_number": "18.2.0",
        "latest_release_published_at": "2023-01-10T00:00:00Z",
        "created_at": "2013-05-24T00:00:00Z",
        "updated_at": "2023-01-10T00:00:00Z"
    }
```

### Test Automation

#### 1. Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-case-conflict
      - id: check-merge-conflict
      - id: debug-statements
      - id: mixed-line-ending

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-python-dateutil]

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, src/]

  - repo: https://github.com/pre-commit/mirrors-pylint
    rev: v3.0.0a6
    hooks:
      - id: pylint
        args: [--rcfile=.pylintrc]
        additional_dependencies: [pylint]

  - repo: https://github.com/pytest-dev/pytest
    rev: 7.4.0
    hooks:
      - id: pytest
        args: [--cov=src, --cov-report=term-missing, --cov-fail-under=80]
        pass_filenames: false
        always_run: true
```

#### 2. Git Hooks

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Pre-commit hook for running tests

echo "Running pre-commit tests..."

# Run unit tests
echo "Running unit tests..."
pytest tests/unit/ -v

# Run integration tests
echo "Running integration tests..."
pytest tests/integration/ -v

# Run security tests
echo "Running security tests..."
pytest tests/security/ -v

# Run linting
echo "Running linting..."
flake8 src/
black --check src/
isort --check-only src/

# Run type checking
echo "Running type checking..."
mypy src/

echo "Pre-commit tests completed successfully!"
```

Make the script executable:

```bash
chmod +x .git/hooks/pre-commit
```

### Test Strategy Evolution

#### 1. Test Strategy Review

Regular review of test strategy:

```bash
# Review test coverage
pytest --cov=src --cov-report=term-missing

# Review test performance
pytest --durations=10

# Review test reliability
pytest --tb=short
```

#### 2. Test Strategy Updates

Update test strategy based on project needs:

```python
# Add new test categories as needed
@pytest.mark.performance
async def test_performance_requirements(self):
    """Test performance requirements are met."""
    pass

@pytest.mark.security
async def test_security_requirements(self):
    """Test security requirements are met."""
    pass

@pytest.mark.compatibility
async def test_compatibility_requirements(self):
    """Test compatibility requirements are met."""
    pass
```

#### 3. Test Strategy Documentation

Keep test strategy documentation up to date:

```markdown
# Test Strategy

## Overview
- Unit tests: 75% of test suite
- Integration tests: 20% of test suite
- End-to-end tests: 5% of test suite

## Coverage Requirements
- Overall coverage: 80%
- Critical modules: 95%
- New code: 90%

## Performance Requirements
- Unit tests: < 1 second
- Integration tests: < 10 seconds
- End-to-end tests: < 60 seconds

## Security Requirements
- Input validation: 100%
- Error handling: 100%
- Rate limiting: 100%
```

## Conclusion

This comprehensive testing documentation provides a complete guide for testing the Libraries.io MCP Server. The testing strategy ensures:

- **Quality**: High-quality, reliable code through comprehensive testing
- **Reliability**: Consistent behavior across different environments
- **Maintainability**: Easy to modify and extend with clear test organization
- **Performance**: Optimal performance under various conditions
- **Security**: Secure implementation resistant to vulnerabilities

The testing framework supports:

- **Unit Testing**: Individual component testing in isolation
- **Integration Testing**: Component interaction testing
- **End-to-End Testing**: Complete workflow testing
- **Performance Testing**: Performance characteristics testing
- **Security Testing**: Security vulnerability testing
- **Load Testing**: System testing under heavy load

By following these testing procedures and best practices, the Libraries.io MCP Server will maintain high code quality and reliability throughout its development lifecycle.

For additional information about specific components, refer to:
- [API Documentation](docs/api.md)
- [Architecture Overview](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)
- [Code Style Guidelines](docs/code-style.md)
- [Monitoring Setup](docs/monitoring.md)

"""
Pytest configuration and fixtures for the Libraries.io MCP Server tests.

This module provides common fixtures and test configuration for all tests.
"""

import os
import pytest
import asyncio
import tempfile
from typing import Dict, Any, Generator, AsyncGenerator
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

import httpx
from respx import MockRouter

from src.libraries_io_mcp.client import LibrariesIOClient
from src.libraries_io_mcp.server import LibrariesIOServer
from src.libraries_io_mcp.models import (
    Platform, Package, PackageVersion, Dependency, Repository,
    User, Organization, SearchResult, RateLimitInfo
)
from src.libraries_io_mcp.utils import RateLimiter, MemoryCache, RetryHandler


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_api_key() -> str:
    """Return a test API key."""
    return "test_api_key_12345"


@pytest.fixture
def test_base_url() -> str:
    """Return a test base URL."""
    return "https://test.libraries.io/api"


@pytest.fixture
def mock_rate_limiter() -> RateLimiter:
    """Create a mock rate limiter for testing."""
    return RateLimiter(limit=100, window_seconds=60)


@pytest.fixture
def mock_cache() -> MemoryCache:
    """Create a mock cache for testing."""
    return MemoryCache(default_ttl=300, max_size=1000)


@pytest.fixture
def mock_retry_handler() -> RetryHandler:
    """Create a mock retry handler for testing."""
    return RetryHandler(max_retries=3, base_delay=1.0, max_delay=60.0)


@pytest.fixture
def mock_httpx_response() -> Mock:
    """Create a mock HTTPX response."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    mock_response.text = '{"success": true}'
    mock_response.headers = {
        "x-ratelimit-limit": "60",
        "x-ratelimit-remaining": "59",
        "x-ratelimit-reset": "1234567890"
    }
    return mock_response


@pytest.fixture
def respx_mock() -> MockRouter:
    """Create a respx mock router for HTTP mocking."""
    with MockRouter() as mock:
        yield mock


@pytest.fixture
async def libraries_io_client(
    test_api_key: str,
    test_base_url: str,
    mock_rate_limiter: RateLimiter,
    mock_cache: MemoryCache,
    mock_retry_handler: RetryHandler
) -> AsyncGenerator[LibrariesIOClient, None]:
    """Create a LibrariesIOClient instance for testing."""
    client = LibrariesIOClient(
        api_key=test_api_key,
        base_url=test_base_url,
        rate_limit=100,
        rate_limit_window=60,
        cache_ttl=300,
        cache_max_size=1000,
        max_retries=3,
        timeout=30.0
    )
    
    # Replace rate limiter, cache, and retry handler with mocks
    client.rate_limiter = mock_rate_limiter
    client.cache = mock_cache
    client.retry_handler = mock_retry_handler
    
    yield client
    
    await client.close()


@pytest.fixture
def libraries_io_server(test_api_key: str) -> LibrariesIOServer:
    """Create a LibrariesIOServer instance for testing."""
    return LibrariesIOServer(
        api_key=test_api_key,
        host="127.0.0.1",
        port=8001,
        log_level="DEBUG"
    )


@pytest.fixture
def sample_platform_data() -> Dict[str, Any]:
    """Sample platform data for testing."""
    return {
        "name": "npm",
        "project_count": 1500000,
        "homepage": "https://www.npmjs.com/",
        "color": "#cb3837",
        "default_language": "JavaScript",
        "package_type": "library"
    }


@pytest.fixture
def sample_platform(sample_platform_data: Dict[str, Any]) -> Platform:
    """Create a sample Platform instance for testing."""
    return Platform(**sample_platform_data)


@pytest.fixture
def sample_package_data() -> Dict[str, Any]:
    """Sample package data for testing."""
    return {
        "name": "react",
        "platform": "npm",
        "description": "A JavaScript library for building user interfaces",
        "homepage": "https://reactjs.org/",
        "repository_url": "https://github.com/facebook/react",
        "language": "JavaScript",
        "keywords": ["javascript", "ui", "library"],
        "licenses": "MIT",
        "latest_release_number": "18.2.0",
        "latest_release_published_at": "2023-01-01T00:00:00Z",
        "stars": 200000,
        "forks": 40000,
        "dependents_count": 50000,
        "status": "active"
    }


@pytest.fixture
def sample_package(sample_package_data: Dict[str, Any]) -> Package:
    """Create a sample Package instance for testing."""
    return Package(**sample_package_data)


@pytest.fixture
def sample_package_version_data() -> Dict[str, Any]:
    """Sample package version data for testing."""
    return {
        "number": "18.2.0",
        "published_at": "2023-01-01T00:00:00Z",
        "spdx_expression": "MIT",
        "original_license": "MIT",
        "status": "active"
    }


@pytest.fixture
def sample_package_version(sample_package_version_data: Dict[str, Any]) -> PackageVersion:
    """Create a sample PackageVersion instance for testing."""
    return PackageVersion(**sample_package_version_data)


@pytest.fixture
def sample_dependency_data() -> Dict[str, Any]:
    """Sample dependency data for testing."""
    return {
        "name": "react-dom",
        "platform": "npm",
        "requirement": "^18.0.0",
        "kind": "runtime",
        "optional": False
    }


@pytest.fixture
def sample_dependency(sample_dependency_data: Dict[str, Any]) -> Dependency:
    """Create a sample Dependency instance for testing."""
    return Dependency(**sample_dependency_data)


@pytest.fixture
def sample_repository_data() -> Dict[str, Any]:
    """Sample repository data for testing."""
    return {
        "url": "https://github.com/facebook/react",
        "homepage": "https://reactjs.org/",
        "description": "A JavaScript library for building user interfaces",
        "language": "JavaScript",
        "stars": 200000,
        "forks": 40000,
        "last_commit_at": "2023-01-01T00:00:00Z",
        "package_count": 5
    }


@pytest.fixture
def sample_repository(sample_repository_data: Dict[str, Any]) -> Repository:
    """Create a sample Repository instance for testing."""
    return Repository(**sample_repository_data)


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user data for testing."""
    return {
        "username": "octocat",
        "name": "The Octocat",
        "email": "octocat@example.com",
        "company": "GitHub",
        "location": "San Francisco",
        "blog": "https://github.blog",
        "bio": "GitHub mascot",
        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
        "followers_count": 1000,
        "following_count": 500,
        "public_gists_count": 10,
        "public_repos_count": 8
    }


@pytest.fixture
def sample_user(sample_user_data: Dict[str, Any]) -> User:
    """Create a sample User instance for testing."""
    return User(**sample_user_data)


@pytest.fixture
def sample_organization_data() -> Dict[str, Any]:
    """Sample organization data for testing."""
    return {
        "login": "facebook",
        "name": "Facebook",
        "description": "Social media company",
        "company": "Meta",
        "location": "Menlo Park, CA",
        "blog": "https://facebook.com",
        "email": "contact@facebook.com",
        "avatar_url": "https://github.com/images/error/facebook_200x200.jpg",
        "followers_count": 5000,
        "following_count": 100,
        "public_gists_count": 0,
        "public_repos_count": 50,
        "created_at": "2007-10-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_organization(sample_organization_data: Dict[str, Any]) -> Organization:
    """Create a sample Organization instance for testing."""
    return Organization(**sample_organization_data)


@pytest.fixture
def sample_search_result_data() -> Dict[str, Any]:
    """Sample search result data for testing."""
    return {
        "total_count": 100,
        "incomplete_results": False,
        "items": [
            {
                "name": "react",
                "platform": "npm",
                "description": "A JavaScript library for building user interfaces",
                "homepage": "https://reactjs.org/",
                "repository_url": "https://github.com/facebook/react",
                "language": "JavaScript",
                "keywords": ["javascript", "ui", "library"],
                "licenses": "MIT",
                "latest_release_number": "18.2.0",
                "latest_release_published_at": "2023-01-01T00:00:00Z",
                "stars": 200000,
                "forks": 40000,
                "dependents_count": 50000,
                "status": "active"
            }
        ]
    }


@pytest.fixture
def sample_search_result(sample_search_result_data: Dict[str, Any]) -> SearchResult:
    """Create a sample SearchResult instance for testing."""
    return SearchResult(**sample_search_result_data)


@pytest.fixture
def sample_rate_limit_info() -> RateLimitInfo:
    """Create a sample RateLimitInfo instance for testing."""
    return RateLimitInfo(
        limit=60,
        remaining=59,
        reset=1234567890.0,
        used=1
    )


@pytest.fixture
def mock_environment_variables(test_api_key: str) -> Generator[None, None, None]:
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {"LIBRARIES_IO_API_KEY": test_api_key}):
        yield


@pytest.fixture
def temp_dotenv_file(test_api_key: str) -> Generator[str, None, None]:
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write(f"LIBRARIES_IO_API_KEY={test_api_key}\n")
        f.write("TEST_VAR=test_value\n")
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Clean up
    os.unlink(temp_file_path)


@pytest.fixture
def mock_fastmcp_server() -> Mock:
    """Create a mock FastMCP server for testing."""
    mock_server = Mock()
    mock_server.add_tool = Mock()
    mock_server.serve = AsyncMock()
    return mock_server


@pytest.fixture
def mock_http_client() -> Mock:
    """Create a mock HTTP client for testing."""
    mock_client = Mock(spec=httpx.AsyncClient)
    mock_client.request = AsyncMock()
    mock_client.aclose = AsyncMock()
    return mock_client


@pytest.fixture
def test_timeout_context() -> float:
    """Return a test timeout value."""
    return 10.0


@pytest.fixture
def test_cache_ttl() -> int:
    """Return a test cache TTL value."""
    return 300


@pytest.fixture
def test_cache_max_size() -> int:
    """Return a test cache max size value."""
    return 1000


@pytest.fixture
def test_max_retries() -> int:
    """Return a test max retries value."""
    return 3


@pytest.fixture
def test_timeout() -> float:
    """Return a test timeout value."""
    return 30.0


@pytest.fixture
def test_rate_limit() -> int:
    """Return a test rate limit value."""
    return 60


@pytest.fixture
def test_rate_limit_window() -> int:
    """Return a test rate limit window value."""
    return 60


@pytest.fixture
def async_test_timeout() -> float:
    """Return an async test timeout value."""
    return 5.0


@pytest.fixture
def mock_async_context_manager() -> AsyncMock:
    """Create a mock async context manager for testing."""
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_context)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    return mock_context


@pytest.fixture
def mock_validation_error() -> Mock:
    """Create a mock validation error for testing."""
    mock_error = Mock()
    mock_error.errors = [{"loc": ("field",), "msg": "error message"}]
    return mock_error


@pytest.fixture
def mock_libraries_io_client_error() -> Mock:
    """Create a mock LibrariesIOClientError for testing."""
    mock_error = Mock()
    mock_error.__str__ = Mock(return_value="Test client error")
    return mock_error


@pytest.fixture
def mock_authentication_error() -> Mock:
    """Create a mock AuthenticationError for testing."""
    mock_error = Mock()
    mock_error.__str__ = Mock(return_value="Authentication failed")
    return mock_error


@pytest.fixture
def mock_not_found_error() -> Mock:
    """Create a mock NotFoundError for testing."""
    mock_error = Mock()
    mock_error.__str__ = Mock(return_value="Resource not found")
    return mock_error


@pytest.fixture
def mock_rate_limit_error() -> Mock:
    """Create a mock RateLimitError for testing."""
    mock_error = Mock()
    mock_error.__str__ = Mock(return_value="Rate limit exceeded")
    return mock_error


@pytest.fixture
def mock_server_error() -> Mock:
    """Create a mock ServerError for testing."""
    mock_error = Mock()
    mock_error.__str__ = Mock(return_value="Server error")
    return mock_error


@pytest.fixture
def test_platforms() -> list:
    """Return a list of test platforms."""
    return ["npm", "pypi", "maven", "gem", "nuget"]


@pytest.fixture
def test_languages() -> list:
    """Return a list of test languages."""
    return ["JavaScript", "Python", "Java", "Ruby", "C#"]


@pytest.fixture
def test_licenses() -> list:
    """Return a list of test licenses."""
    return ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause"]


@pytest.fixture
def test_package_names() -> list:
    """Return a list of test package names."""
    return ["react", "django", "spring", "rails", "nuget"]


@pytest.fixture
def test_queries() -> list:
    """Return a list of test search queries."""
    return ["react", "django", "machine learning", "web framework"]


@pytest.fixture
def test_page_numbers() -> list:
    """Return a list of test page numbers."""
    return [1, 2, 3, 10, 50]


@pytest.fixture
def test_per_page_values() -> list:
    """Return a list of test per_page values."""
    return [10, 20, 50, 100]


@pytest.fixture
def test_time_ranges() -> list:
    """Return a list of test time ranges."""
    return ["day", "week", "month"]


@pytest.fixture
def test_check_intervals() -> list:
    """Return a list of test check intervals."""
    return ["hourly", "daily", "weekly"]


@pytest.fixture
def test_use_cases() -> list:
    """Return a list of test use cases."""
    return ["commercial", "open_source", "academic"]


@pytest.fixture
def test_max_depth_values() -> list:
    """Return a list of test max depth values."""
    return [1, 2, 3, 5, 10]


@pytest.fixture
def test_criteria_options() -> list:
    """Return a list of test criteria options."""
    return ["similar", "popular", "recent"]


@pytest.fixture
def test_limit_values() -> list:
    """Return a list of test limit values."""
    return [5, 10, 20, 50, 100]


@pytest.fixture
def test_boolean_values() -> list:
    """Return a list of test boolean values."""
    return [True, False]


@pytest.fixture
def test_version_strings() -> list:
    """Return a list of test version strings."""
    return ["1.0.0", "2.1.3", "3.0.0-alpha", "1.2.3-beta.1"]


@pytest.fixture
def test_error_messages() -> list:
    """Return a list of test error messages."""
    return [
        "Invalid API key",
        "Resource not found",
        "Rate limit exceeded",
        "Server error",
        "Invalid parameters"
    ]


@pytest.fixture
def test_status_codes() -> list:
    """Return a list of test HTTP status codes."""
    return [200, 400, 401, 403, 404, 429, 500, 502, 503, 504]


@pytest.fixture
def test_header_values() -> Dict[str, str]:
    """Return a dictionary of test header values."""
    return {
        "User-Agent": "Test-Agent/1.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token"
    }


@pytest.fixture
def test_query_params() -> Dict[str, Any]:
    """Return a dictionary of test query parameters."""
    return {
        "platform": "npm",
        "language": "JavaScript",
        "license": "MIT",
        "page": 1,
        "per_page": 10
    }


@pytest.fixture
def test_request_data() -> Dict[str, Any]:
    """Return a dictionary of test request data."""
    return {
        "name": "test-package",
        "version": "1.0.0",
        "description": "Test package",
        "repository": "https://github.com/test/test-package"
    }


@pytest.fixture
def test_response_data() -> Dict[str, Any]:
    """Return a dictionary of test response data."""
    return {
        "success": True,
        "data": {
            "id": 1,
            "name": "test-package",
            "version": "1.0.0"
        },
        "message": "Success"
    }


@pytest.fixture
def test_error_response_data() -> Dict[str, Any]:
    """Return a dictionary of test error response data."""
    return {
        "success": False,
        "error": {
            "code": "INVALID_PARAMETERS",
            "message": "Invalid parameters provided"
        },
        "details": {
            "field": "name",
            "issue": "required field missing"
        }
    }


@pytest.fixture
def test_cache_key() -> str:
    """Return a test cache key."""
    return "test_endpoint_test_params"


@pytest.fixture
def test_cache_data() -> Dict[str, Any]:
    """Return test cache data."""
    return {
        "id": 1,
        "name": "test-package",
        "version": "1.0.0",
        "created_at": "2023-01-01T00:00:00Z"
    }


@pytest.fixture
def test_cache_expiration() -> float:
    """Return a test cache expiration time."""
    return 300.0  # 5 minutes


@pytest.fixture
def test_retry_attempts() -> list:
    """Return a list of test retry attempts."""
    return [1, 2, 3]


@pytest.fixture
def test_retry_delays() -> list:
    """Return a list of test retry delays."""
    return [1.0, 2.0, 4.0]


@pytest.fixture
def test_retry_max_delay() -> float:
    """Return a test retry max delay."""
    return 60.0


@pytest.fixture
def test_retry_base_delay() -> float:
    """Return a test retry base delay."""
    return 1.0


@pytest.fixture
def test_retry_max_retries() -> int:
    """Return a test retry max retries."""
    return 3


@pytest.fixture
def test_timeout_seconds() -> float:
    """Return a test timeout in seconds."""
    return 30.0


@pytest.fixture
def test_timeout_exception() -> Exception:
    """Return a test timeout exception."""
    return asyncio.TimeoutError("Test timeout")


@pytest.fixture
def test_rate_limit_info_dict() -> Dict[str, Any]:
    """Return a test rate limit info dictionary."""
    return {
        "limit": 60,
        "remaining": 59,
        "reset": 1234567890,
        "used": 1
    }


@pytest.fixture
def test_rate_limit_info_json() -> str:
    """Return a test rate limit info JSON string."""
    return '{"limit": 60, "remaining": 59, "reset": 1234567890, "used": 1}'


@pytest.fixture
def test_rate_limit_headers() -> Dict[str, str]:
    """Return test rate limit headers."""
    return {
        "x-ratelimit-limit": "60",
        "x-ratelimit-remaining": "59",
        "x-ratelimit-reset": "1234567890"
    }


@pytest.fixture
def test_retryable_status_codes() -> set:
    """Return a set of test retryable status codes."""
    return {429, 500, 502, 503, 504}


@pytest.fixture
def test_non_retryable_status_codes() -> set:
    """Return a set of test non-retryable status codes."""
    return {400, 401, 403, 404}


@pytest.fixture
def test_json_response() -> Dict[str, Any]:
    """Return a test JSON response."""
    return {
        "success": True,
        "data": {
            "items": [
                {"id": 1, "name": "item1"},
                {"id": 2, "name": "item2"}
            ]
        }
    }


@pytest.fixture
def test_json_response_string() -> str:
    """Return a test JSON response string."""
    return '{"success": true, "data": {"items": [{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}]}}'


@pytest.fixture
def test_invalid_json_response() -> str:
    """Return a test invalid JSON response string."""
    return "Invalid JSON response"


@pytest.fixture
def test_empty_response() -> str:
    """Return a test empty response string."""
    return ""


@pytest.fixture
def test_large_response() -> str:
    """Return a test large response string."""
    return "x" * 10000


@pytest.fixture
def test_special_characters_response() -> str:
    """Return a test response with special characters."""
    return '{"message": "Hello, 世界! 🌍", "special": "©®™"}'


@pytest.fixture
def test_unicode_response() -> str:
    """Return a test Unicode response."""
    return '{"greeting": "こんにちは", "emoji": "😊"}'


@pytest.fixture
def test_nested_response() -> Dict[str, Any]:
    """Return a test nested response."""
    return {
        "level1": {
            "level2": {
                "level3": {
                    "value": "deeply nested"
                }
            }
        }
    }


@pytest.fixture
def test_list_response() -> list:
    """Return a test list response."""
    return [
        {"id": 1, "name": "item1"},
        {"id": 2, "name": "item2"},
        {"id": 3, "name": "item3"}
    ]


@pytest.fixture
def test_empty_list_response() -> list:
    """Return a test empty list response."""
    return []


@pytest.fixture
def test_large_list_response() -> list:
    """Return a test large list response."""
    return [{"id": i, "name": f"item{i}"} for i in range(1000)]


@pytest.fixture
def test_mixed_response() -> Dict[str, Any]:
    """Return a test mixed response with different data types."""
    return {
        "string": "test",
        "number": 42,
        "float": 3.14,
        "boolean": True,
        "null": None,
        "list": [1, 2, 3],
        "dict": {"nested": "value"},
        "unicode": "Hello, 世界!",
        "special": "©®™"
    }


@pytest.fixture
def test_datetime_response() -> Dict[str, Any]:
    """Return a test datetime response."""
    return {
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-02T00:00:00Z",
        "timestamp": 1672531200
    }


@pytest.fixture
def test_invalid_datetime_response() -> Dict[str, Any]:
    """Return a test invalid datetime response."""
    return {
        "created_at": "invalid-date",
        "updated_at": "2023-01-02T00:00:00Z"
    }


@pytest.fixture
def test_large_number_response() -> Dict[str, Any]:
    """Return a test large number response."""
    return {
        "big_number": 12345678901234567890,
        "small_number": 42,
        "negative_number": -100,
        "float_number": 3.14159265359
    }


@pytest.fixture
def test_boolean_response() -> Dict[str, Any]:
    """Return a test boolean response."""
    return {
        "true_value": True,
        "false_value": False,
        "truthy_string": "true",
        "falsy_string": "false"
    }


@pytest.fixture
def test_none_response() -> Dict[str, Any]:
    """Return a test None response."""
    return {
        "null_value": None,
        "empty_string": "",
        "empty_list": [],
        "empty_dict": {}
    }


@pytest.fixture
def test_edge_case_response() -> Dict[str, Any]:
    """Return a test edge case response."""
    return {
        "empty_string": "",
        "whitespace_string": "   ",
        "newline_string": "line1\nline2",
        "tab_string": "col1\tcol2",
        "unicode_whitespace": "       ",
        "zero_number": 0,
        "negative_zero": -0,
        "infinity": float("inf"),
        "negative_infinity": float("-inf"),
        "nan": float("nan")
    }


@pytest.fixture
def test_security_issue_data() -> Dict[str, Any]:
    """Return test security issue data."""
    return {
        "type": "vulnerability",
        "severity": "high",
        "description": "Critical security vulnerability found",
        "cve": "CVE-2023-1234",
        "affected_versions": ["< 1.0.0"],
        "fixed_versions": [">= 1.0.1"]
    }


@pytest.fixture
def test_security_issues_list() -> list:
    """Return a test security issues list."""
    return [
        {
            "type": "vulnerability",
            "severity": "high",
            "description": "Critical security vulnerability found",
            "cve": "CVE-2023-1234"
        },
        {
            "type": "license",
            "severity": "medium",
            "description": "GPL license detected",
            "license": "GPL-3.0"
        }
    ]


@pytest.fixture
def test_audit_results() -> Dict[str, Any]:
    """Return test audit results."""
    return {
        "platform": "npm",
        "total_packages": 10,
        "audits": {
            "duplicates": [
                {
                    "package": "lodash",
                    "duplicates": [{"first_occurrence": {"version": "4.17.20"}, "duplicate_occurrence": {"version": "4.17.21"}}],
                    "severity": "high",
                    "recommendation": "Remove duplicate package entries"
                }
            ],
            "outdated": [
                {
                    "package": "react",
                    "current_version": "16.0.0",
                    "latest_version": "18.2.0",
                    "severity": "medium",
                    "recommendation": "Update to version 18.2.0"
                }
            ],
            "security": [
                {
                    "package": "vulnerable-package",
                    "version": "1.0.0",
                    "issue": {"type": "vulnerability", "severity": "high"},
                    "severity": "high",
                    "recommendation": "Update to latest version"
                }
            ],
            "recommendations": [
                {
                    "package": "low-popularity-package",
                    "type": "low_popularity",
                    "severity": "low",
                    "recommendation": "Consider alternatives - package has only 5 stars"
                }
            ]
        },
        "summary": {
            "duplicates_count": 1,
            "unused_count": 0,
            "outdated_count": 1,
            "security_issues_count": 1,
            "recommendations_count": 1
        },
        "project_health_score": 85,
        "health_status": "good"
    }


@pytest.fixture
def test_dependency_tree() -> Dict[str, Any]:
    """Return test dependency tree."""
    return {
        "name": "react",
        "platform": "npm",
        "depth": 0,
        "dependencies": [
            {
                "name": "react-dom",
                "platform": "npm",
                "depth": 1,
                "dependencies": [
                    {
                        "name": "scheduler",
                        "platform": "npm",
                        "depth": 2,
                        "dependencies": []
                    }
                ]
            },
            {
                "name": "prop-types",
                "platform": "npm",
                "depth": 1,
                "dependencies": []
            }
        ]
    }


@pytest.fixture
def test_dependency_analysis() -> Dict[str, Any]:
    """Return test dependency analysis."""
    return {
        "total_dependencies": 3,
        "unique_dependencies": 3,
        "max_depth": 2,
        "potential_duplicates": 0
    }


@pytest.fixture
def test_alternatives_data() -> Dict[str, Any]:
    """Return test alternatives data."""
    return {
        "original_package": {
            "name": "lodash",
            "platform": "npm",
            "language": "JavaScript",
            "description": "A modern JavaScript utility library delivering modularity, performance & extras."
        },
        "criteria": ["similar", "popular"],
        "alternatives": [
            {
                "name": "underscore",
                "platform": "npm",
                "description": "JavaScript's utility _ belt",
                "stars": 13000,
                "language": "JavaScript"
            },
            {
                "name": "ramda",
                "platform": "npm",
                "description": "Practical functional programming library for JavaScript",
                "stars": 22000,
                "language": "JavaScript"
            }
        ],
        "count": 2
    }


@pytest.fixture
def test_license_compatibility_data() -> Dict[str, Any]:
    """Return test license compatibility data."""
    return {
        "use_case": "commercial",
        "licenses": [
            {
                "license": "MIT",
                "normalized": "MIT",
                "compatible": True,
                "use_case": "commercial",
                "restrictions": ["No specific restrictions"]
            },
            {
                "license": "GPL-3.0",
                "normalized": "GPL-3.0",
                "compatible": False,
                "use_case": "commercial",
                "restrictions": [
                    "Must disclose source code",
                    "Derivatives must be licensed under GPL",
                    "Cannot be used in proprietary software"
                ]
            }
        ],
        "overall_compatible": False,
        "recommendations": [
            "Consider using permissively licensed alternatives for your use case",
            "Review commercial use restrictions for each license"
        ],
        "compatibility_rules": {
            "MIT": {"commercial": True, "open_source": True, "academic": True},
            "GPL-3.0": {"commercial": False, "open_source": True, "academic": True}
        }
    }


@pytest.fixture
def test_platform_stats_data() -> Dict[str, Any]:
    """Return test platform stats data."""
    return {
        "platform": "npm",
        "homepage": "https://www.npmjs.com/",
        "color": "#cb3837",
        "project_count": 1500000,
        "default_language": "JavaScript",
        "package_type": "library",
        "sample_statistics": {
            "sample_size": 10,
            "total_stars": 500000,
            "average_stars": 50000.0,
            "languages": {"JavaScript": 8, "TypeScript": 2},
            "most_common_language": "JavaScript"
        },
        "trending_packages": [
            {
                "name": "react",
                "platform": "npm",
                "description": "A JavaScript library for building user interfaces",
                "stars": 200000,
                "language": "JavaScript"
            }
        ],
        "supported": True
    }


@pytest.fixture
def test_dependency_report_data() -> Dict[str, Any]:
    """Return test dependency report data."""
    return {
        "generated_at": "2023-01-01T00:00:00Z",
        "packages_analyzed": 3,
        "packages": [
            {
                "platform": "npm",
                "name": "react",
                "status": "success",
                "description": "A JavaScript library for building user interfaces",
                "language": "JavaScript",
                "stars": 200000,
                "latest_version": "18.2.0",
                "homepage": "https://reactjs.org/",
                "repository_url": "https://github.com/facebook/react",
                "versions": "{'total': 50, 'latest': '18.2.0', 'oldest': '0.14.0'}",
                "dependencies": "{'total': 15, 'runtime': 12, 'development': 3}",
                "security": "[]"
            }
        ],
        "summary": {
            "total_packages": 3,
            "successful_analyses": 3,
            "failed_analyses": 0,
            "total_dependencies": 45,
            "unique_languages": ["JavaScript"],
            "security_issues": 0,
            "security_score": 100
        }
    }


@pytest.fixture
def test_package_tracking_data() -> Dict[str, Any]:
    """Return test package tracking data."""
    return {
        "package": {
            "name": "react",
            "platform": "npm",
            "current_version": "18.1.0",
            "latest_version": "18.2.0",
            "description": "A JavaScript library for building user interfaces"
        },
        "tracking": {
            "check_interval": "daily",
            "include_security": True,
            "has_update": True,
            "is_security_update": False,
            "time_since_update": "5 days ago"
        },
        "versions": {
            "total_versions": 50,
            "latest_published": "2023-01-01T00:00:00Z",
            "current_published": "2022-12-27T00:00:00Z"
        },
        "next_check": "2023-01-02 00:00:00"
    }


@pytest.fixture
def test_comparison_data() -> Dict[str, Any]:
    """Return test comparison data."""
    return {
        "packages": [
            {
                "package": "npm/react",
                "info": {
                    "name": "react",
                    "platform": "npm",
                    "description": "A JavaScript library for building user interfaces",
                    "stars": 200000,
                    "latest_release_number": "18.2.0"
                }
            },
            {
                "package": "npm/vue",
                "info": {
                    "name": "vue",
                    "platform": "npm",
                    "description": "The Progressive JavaScript Framework",
                    "stars": 180000,
                    "latest_release_number": "3.2.0"
                }
            }
        ],
        "features_compared": ["name", "platform", "description", "stars", "latest_release_number"],
        "total_packages": 2
    }


@pytest.fixture
def test_search_response_data() -> Dict[str, Any]:
    """Return test search response data."""
    return {
        "total_count": 100,
        "incomplete_results": False,
        "items": [
            {
                "name": "react",
                "platform": "npm",
                "description": "A JavaScript library for building user interfaces",
                "homepage": "https://reactjs.org/",
                "repository_url": "https://github.com/facebook/react",
                "language": "JavaScript",
                "keywords": ["javascript", "ui", "library"],
                "licenses": "MIT",
                "latest_release_number": "18.2.0",
                "latest_release_published_at": "2023-01-01T00:00:00Z",
                "stars": 200000,
                "forks": 40000,
                "dependents_count": 50000,
                "status": "active"
            }
        ],
        "page": 1,
        "per_page": 10
    }


@pytest.fixture
def test_error_response() -> Dict[str, Any]:
    """Return test error response."""
    return {
        "success": False,
        "error": "Invalid API key",
        "rate_limit_info": None
    }


@pytest.fixture
def test_rate_limited_response() -> Dict[str, Any]:
    """Return test rate limited response."""
    return {
        "success": False,
        "error": "Rate limit exceeded",
        "rate_limit_info": {
            "limit": 60,
            "remaining": 0,
            "reset": 1234567890,
            "used": 60
        }
    }


@pytest.fixture
def test_not_found_response() -> Dict[str, Any]:
    """Return test not found response."""
    return {
        "success": False,
        "error": "Package not found",
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_server_error_response() -> Dict[str, Any]:
    """Return test server error response."""
    return {
        "success": False,
        "error": "Internal server error",
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_timeout_response() -> Dict[str, Any]:
    """Return test timeout response."""
    return {
        "success": False,
        "error": "Request timeout",
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_network_error_response() -> Dict[str, Any]:
    """Return test network error response."""
    return {
        "success": False,
        "error": "Network error",
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_validation_error_response() -> Dict[str, Any]:
    """Return test validation error response."""
    return {
        "success": False,
        "error": "Validation error: Invalid parameters",
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_authentication_error_response() -> Dict[str, Any]:
    """Return test authentication error response."""
    return {
        "success": False,
        "error": "Authentication failed: Invalid API key",
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_forbidden_error_response() -> Dict[str, Any]:
    """Return test forbidden error response."""
    return {
        "success": False,
        "error": "Access denied: Insufficient permissions",
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_success() -> Dict[str, Any]:
    """Return test tool response success."""
    return {
        "success": True,
        "data": {
            "result": "success",
            "items": [1, 2, 3]
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_error() -> Dict[str, Any]:
    """Return test tool response error."""
    return {
        "success": False,
        "data": None,
        "error": "Tool execution failed",
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_empty() -> Dict[str, Any]:
    """Return test tool response empty."""
    return {
        "success": True,
        "data": None,
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_partial() -> Dict[str, Any]:
    """Return test tool response partial."""
    return {
        "success": True,
        "data": {
            "partial_result": "Some data",
            "incomplete": True
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_large() -> Dict[str, Any]:
    """Return test tool response large."""
    return {
        "success": True,
        "data": {
            "items": [{"id": i, "name": f"item{i}"} for i in range(1000)],
            "total": 1000
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_nested() -> Dict[str, Any]:
    """Return test tool response nested."""
    return {
        "success": True,
        "data": {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deeply nested",
                        "items": [1, 2, 3]
                    }
                }
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_metadata() -> Dict[str, Any]:
    """Return test tool response with metadata."""
    return {
        "success": True,
        "data": {
            "result": "success",
            "items": [1, 2, 3],
            "metadata": {
                "total_items": 3,
                "page": 1,
                "per_page": 10,
                "has_more": False
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_timing() -> Dict[str, Any]:
    """Return test tool response with timing."""
    return {
        "success": True,
        "data": {
            "result": "success",
            "items": [1, 2, 3],
            "timing": {
                "execution_time": 0.123,
                "cache_hit": True,
                "api_calls": 1
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_warnings() -> Dict[str, Any]:
    """Return test tool response with warnings."""
    return {
        "success": True,
        "data": {
            "result": "success",
            "items": [1, 2, 3],
            "warnings": [
                "Some data may be incomplete",
                "Rate limit approaching"
            ]
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 5,
            "reset": 1234567890,
            "used": 55
        }
    }


@pytest.fixture
def test_tool_response_with_suggestions() -> Dict[str, Any]:
    """Return test tool response with suggestions."""
    return {
        "success": True,
        "data": {
            "result": "success",
            "items": [1, 2, 3],
            "suggestions": [
                "Try a more specific search query",
                "Consider using filters to narrow results"
            ]
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_pagination() -> Dict[str, Any]:
    """Return test tool response with pagination."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3, 4, 5],
            "pagination": {
                "page": 1,
                "per_page": 5,
                "total_pages": 20,
                "total_items": 100,
                "has_next": True,
                "has_prev": False
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_filters() -> Dict[str, Any]:
    """Return test tool response with filters."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "filters": {
                "applied": ["platform", "language"],
                "available": ["platform", "language", "license", "keywords"],
                "counts": {
                    "platform": {"npm": 100, "pypi": 50},
                    "language": {"JavaScript": 80, "Python": 70}
                }
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_sorting() -> Dict[str, Any]:
    """Return test tool response with sorting."""
    return {
        "success": True,
        "data": {
            "items": [
                {"name": "item3", "score": 90},
                {"name": "item1", "score": 85},
                {"name": "item2", "score": 80}
            ],
            "sorting": {
                "by": "score",
                "order": "desc",
                "available": ["score", "name", "date"]
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_aggregation() -> Dict[str, Any]:
    """Return test tool response with aggregation."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "aggregation": {
                "by_platform": {
                    "npm": 100,
                    "pypi": 50,
                    "maven": 25
                },
                "by_language": {
                    "JavaScript": 80,
                    "Python": 70,
                    "Java": 25
                }
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_statistics() -> Dict[str, Any]:
    """Return test tool response with statistics."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3, 4, 5],
            "statistics": {
                "count": 5,
                "sum": 15,
                "average": 3.0,
                "min": 1,
                "max": 5,
                "median": 3
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_graph() -> Dict[str, Any]:
    """Return test tool response with graph data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "graph": {
                "nodes": [
                    {"id": 1, "label": "Node 1"},
                    {"id": 2, "label": "Node 2"},
                    {"id": 3, "label": "Node 3"}
                ],
                "edges": [
                    {"source": 1, "target": 2},
                    {"source": 2, "target": 3}
                ]
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_tree() -> Dict[str, Any]:
    """Return test tool response with tree data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "tree": {
                "root": {
                    "id": 1,
                    "label": "Root",
                    "children": [
                        {
                            "id": 2,
                            "label": "Child 1",
                            "children": []
                        },
                        {
                            "id": 3,
                            "label": "Child 2",
                            "children": []
                        }
                    ]
                }
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_matrix() -> Dict[str, Any]:
    """Return test tool response with matrix data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "matrix": {
                "rows": ["A", "B", "C"],
                "columns": ["X", "Y", "Z"],
                "data": [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ]
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_chart() -> Dict[str, Any]:
    """Return test tool response with chart data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "chart": {
                "type": "bar",
                "title": "Sample Chart",
                "data": {
                    "labels": ["Jan", "Feb", "Mar"],
                    "datasets": [
                        {
                            "label": "Dataset 1",
                            "data": [10, 20, 30]
                        }
                    ]
                }
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_timeline() -> Dict[str, Any]:
    """Return test tool response with timeline data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "timeline": {
                "events": [
                    {
                        "date": "2023-01-01",
                        "title": "Event 1",
                        "description": "First event"
                    },
                    {
                        "date": "2023-01-02",
                        "title": "Event 2",
                        "description": "Second event"
                    }
                ]
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_geo() -> Dict[str, Any]:
    """Return test tool response with geographic data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "geo": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-122.4194, 37.7749]
                        },
                        "properties": {
                            "name": "San Francisco"
                        }
                    }
                ]
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_network() -> Dict[str, Any]:
    """Return test tool response with network data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "network": {
                "nodes": [
                    {"id": 1, "group": 1},
                    {"id": 2, "group": 1},
                    {"id": 3, "group": 2}
                ],
                "links": [
                    {"source": 1, "target": 2},
                    {"source": 2, "target": 3}
                ]
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_calendar() -> Dict[str, Any]:
    """Return test tool response with calendar data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "calendar": {
                "year": 2023,
                "months": [
                    {
                        "name": "January",
                        "weeks": [
                            {
                                "days": [
                                    {"date": "2023-01-01", "events": []},
                                    {"date": "2023-01-02", "events": [{"title": "Event 1"}]}
                                ]
                            }
                        ]
                    }
                ]
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_code() -> Dict[str, Any]:
    """Return test tool response with code data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "code": {
                "language": "python",
                "content": "print('Hello, World!')",
                "highlighted": "<span class=\"keyword\">print</span><span class=\"punctuation\">(</span><span class=\"string\">'Hello, World!'</span><span class=\"punctuation\">)</span>"
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_file() -> Dict[str, Any]:
    """Return test tool response with file data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "file": {
                "name": "example.txt",
                "size": 1024,
                "type": "text/plain",
                "content": "This is a test file content"
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_image() -> Dict[str, Any]:
    """Return test tool response with image data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "image": {
                "url": "https://example.com/image.png",
                "width": 800,
                "height": 600,
                "format": "png",
                "size": 102400
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_audio() -> Dict[str, Any]:
    """Return test tool response with audio data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "audio": {
                "url": "https://example.com/audio.mp3",
                "duration": 180,
                "format": "mp3",
                "size": 2048000
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_video() -> Dict[str, Any]:
    """Return test tool response with video data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "video": {
                "url": "https://example.com/video.mp4",
                "duration": 300,
                "format": "mp4",
                "size": 10485760,
                "resolution": "1920x1080"
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_document() -> Dict[str, Any]:
    """Return test tool response with document data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "document": {
                "title": "Sample Document",
                "author": "John Doe",
                "pages": 10,
                "format": "pdf",
                "size": 512000
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_archive() -> Dict[str, Any]:
    """Return test tool response with archive data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "archive": {
                "name": "example.zip",
                "size": 1024000,
                "format": "zip",
                "files": [
                    {"name": "file1.txt", "size": 1024},
                    {"name": "file2.txt", "size": 2048}
                ]
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_database() -> Dict[str, Any]:
    """Return test tool response with database data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "database": {
                "name": "test_db",
                "tables": [
                    {
                        "name": "users",
                        "columns": ["id", "name", "email"],
                        "rows": 100
                    }
                ]
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }


@pytest.fixture
def test_tool_response_with_api() -> Dict[str, Any]:
    """Return test tool response with API data."""
    return {
        "success": True,
        "data": {
            "items": [1, 2, 3],
            "api": {
                "endpoint": "/api/v1/users",
                "method": "GET",
                "parameters": {
                    "page": 1,
                    "per_page": 10
                },
                "response": {
                    "total": 100,
                    "items": []
                }
            }
        },
        "error": None,
        "rate_limit_info": {
            "limit": 60,
            "remaining": 59,
            "reset": 1234567890,
            "used": 1
        }
    }
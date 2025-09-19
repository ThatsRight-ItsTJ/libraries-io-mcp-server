
"""
Unit tests for the Libraries.io client.

This module contains unit tests for the LibrariesIOClient class and its methods.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from src.libraries_io_mcp.client import (
    LibrariesIOClient,
    LibrariesIOClientError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    ServerError
)
from src.libraries_io_mcp.models import Platform, Package, PackageVersion, Dependency
from src.libraries_io_mcp.utils import RateLimitInfo
from tests.fixtures.mock_responses import MockResponses, MockScenarios


class TestLibrariesIOClient:
    """Test suite for LibrariesIOClient class."""

    @pytest.fixture
    def mock_httpx_client(self):
        """Mock httpx AsyncClient."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def mock_cache(self):
        """Mock cache instance."""
        with patch('src.libraries_io_mcp.utils.MemoryCache') as mock_cache_class:
            mock_cache = AsyncMock()
            mock_cache_class.return_value = mock_cache
            yield mock_cache

    @pytest.fixture
    def mock_rate_limiter(self):
        """Mock rate limiter instance."""
        with patch('src.libraries_io_mcp.utils.RateLimiter') as mock_limiter_class:
            mock_limiter = AsyncMock()
            mock_limiter_class.return_value = mock_limiter
            yield mock_limiter

    @pytest.fixture
    def mock_retry_handler(self):
        """Mock retry handler instance."""
        with patch('src.libraries_io_mcp.utils.RetryHandler') as mock_handler_class:
            mock_handler = AsyncMock()
            mock_handler_class.return_value = mock_handler
            yield mock_handler

    @pytest.fixture
    def client(self, mock_httpx_client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Create a LibrariesIOClient instance with mocked dependencies."""
        with patch('src.libraries_io_mcp.client.os.getenv', return_value='test_api_key'):
            client = LibrariesIOClient(api_key='test_api_key')
            yield client

    def test_client_initialization(self):
        """Test client initialization with API key."""
        with patch('src.libraries_io_mcp.client.os.getenv', return_value='test_api_key'):
            client = LibrariesIOClient(api_key='test_api_key')
            
            assert client.api_key == 'test_api_key'
            assert client.base_url == 'https://libraries.io/api'
            assert client.timeout == 30.0
            assert client.rate_limiter is not None
            assert client.cache is not None
            assert client.retry_handler is not None
            assert client.session is not None

    def test_client_initialization_with_env_var(self):
        """Test client initialization with environment variable."""
        with patch('src.libraries_io_mcp.client.os.getenv', return_value='env_api_key'):
            client = LibrariesIOClient()
            
            assert client.api_key == 'env_api_key'

    def test_client_initialization_without_api_key(self):
        """Test client initialization without API key raises ValueError."""
        with patch('src.libraries_io_mcp.client.os.getenv', return_value=None):
            with pytest.raises(ValueError, match="API key is required"):
                LibrariesIOClient()

    def test_client_initialization_with_custom_params(self):
        """Test client initialization with custom parameters."""
        with patch('src.libraries_io_mcp.client.os.getenv', return_value='test_api_key'):
            client = LibrariesIOClient(
                api_key='custom_key',
                base_url='https://custom.api.com',
                rate_limit=100,
                rate_limit_window=120,
                cache_ttl=600,
                cache_max_size=2000,
                max_retries=5,
                timeout=60.0
            )
            
            assert client.api_key == 'custom_key'
            assert client.base_url == 'https://custom.api.com'
            assert client.timeout == 60.0

    @pytest.mark.asyncio
    async def test_client_context_manager(self, client):
        """Test client as async context manager."""
        async with client:
            pass  # Just test that it enters and exits without error
        
        # Verify session was closed
        client.session.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_client_close(self, client):
        """Test client close method."""
        await client.close()
        
        # Verify session was closed
        client.session.aclose.assert_called_once()

    def test_get_cache_key(self, client):
        """Test cache key generation."""
        key1 = client._get_cache_key('test_endpoint', {'param1': 'value1'})
        key2 = client._get_cache_key('test_endpoint', {'param1': 'value1'})
        key3 = client._get_cache_key('test_endpoint', {'param1': 'value2'})
        
        # Same parameters should produce same key
        assert key1 == key2
        # Different parameters should produce different keys
        assert key1 != key3

    def test_add_api_key(self, client):
        """Test API key addition to parameters."""
        params = {'param1': 'value1'}
        result = client._add_api_key(params)
        
        assert result['param1'] == 'value1'
        assert result['api_key'] == 'test_api_key'

    def test_add_api_key_no_params(self, client):
        """Test API key addition with no parameters."""
        result = client._add_api_key()
        
        assert result['api_key'] == 'test_api_key'

    def test_handle_response_valid_json(self, client):
        """Test response handling with valid JSON."""
        mock_response = Mock()
        mock_response.json.return_value = {'key': 'value'}
        
        result = client._handle_response(mock_response)
        
        assert result == {'key': 'value'}

    def test_handle_response_invalid_json(self, client):
        """Test response handling with invalid JSON."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        with pytest.raises(LibrariesIOClientError, match="Invalid JSON response"):
            client._handle_response(mock_response)

    def test_check_rate_limit_with_headers(self, client):
        """Test rate limit checking with valid headers."""
        headers = {
            'x-ratelimit-limit': '100',
            'x-ratelimit-remaining': '50',
            'x-ratelimit-reset': '1640995200'
        }
        
        mock_response = Mock()
        mock_response.headers = headers
        
        # Should not raise any exception
        client._check_rate_limit(mock_response)
        
        # Verify rate limit info was updated
        assert client._rate_limit_info is not None
        assert client._rate_limit_info.limit == 100
        assert client._rate_limit_info.remaining == 50
        assert client._rate_limit_info.reset == 1640995200.0

    def test_check_rate_limit_exceeded(self, client):
        """Test rate limit checking when limit is exceeded."""
        headers = {
            'x-ratelimit-limit': '100',
            'x-ratelimit-remaining': '0',
            'x-ratelimit-reset': '1640995200'
        }
        
        mock_response = Mock()
        mock_response.headers = headers
        
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            client._check_rate_limit(mock_response)

    def test_handle_error_authentication_failed(self, client):
        """Test error handling for authentication failure."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = 'Authentication failed'
        
        error = client._handle_error(mock_response)
        
        assert isinstance(error, AuthenticationError)
        assert "Authentication failed" in str(error)

    def test_handle_error_not_found(self, client):
        """Test error handling for not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = 'Resource not found'
        
        error = client._handle_error(mock_response)
        
        assert isinstance(error, NotFoundError)
        assert "Resource not found" in str(error)

    def test_handle_error_rate_limit_exceeded(self, client):
        """Test error handling for rate limit exceeded."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = 'Rate limit exceeded'
        
        error = client._handle_error(mock_response)
        
        assert isinstance(error, RateLimitError)
        assert "Rate limit exceeded" in str(error)

    def test_handle_error_server_error(self, client):
        """Test error handling for server error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal server error'
        
        error = client._handle_error(mock_response)
        
        assert isinstance(error, ServerError)
        assert "Server error" in str(error)

    def test_handle_error_other_error(self, client):
        """Test error handling for other HTTP errors."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad request'
        
        error = client._handle_error(mock_response)
        
        assert isinstance(error, LibrariesIOClientError)
        assert "HTTP 400" in str(error)

    @pytest.mark.asyncio
    async def test_make_request_cache_hit(self, client, mock_cache):
        """Test request with cache hit."""
        mock_cache.get.return_value = {'cached': 'data'}
        
        result = await client._make_request('GET', 'test_endpoint')
        
        assert result == {'cached': 'data'}
        mock_cache.get.assert_called_once()
        # Should not make HTTP request
        client.session.request.assert_not_called()

    @pytest.mark.asyncio
    async def test_make_request_cache_miss(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test request with cache miss."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = {'new': 'data'}
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        result = await client._make_request('GET', 'test_endpoint')
        
        assert result == {'new': 'data'}
        mock_cache.get.assert_called_once()
        mock_rate_limiter.acquire.assert_called_once()
        mock_retry_handler.retry.assert_called_once()
        mock_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_with_params(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test request with parameters."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = {'param': 'value'}
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        params = {'param1': 'value1', 'param2': 'value2'}
        
        result = await client._make_request('GET', 'test_endpoint', params=params)
        
        assert result == {'param': 'value'}
        # Verify API key was added to params
        call_args = client.session.request.call_args
        assert call_args[1]['params']['api_key'] == 'test_api_key'

    @pytest.mark.asyncio
    async def test_make_request_with_data(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test request with data."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'data'}
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        data = {'key': 'value'}
        
        result = await client._make_request('POST', 'test_endpoint', data=data)
        
        assert result == {'response': 'data'}
        # Verify data was passed correctly
        call_args = client.session.request.call_args
        assert call_args[1]['json'] == data

    @pytest.mark.asyncio
    async def test_make_request_retry_failure(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test request with retry failure."""
        mock_cache.get.return_value = None
        mock_retry_handler.retry.side_effect = Exception("All retries failed")
        
        with pytest.raises(LibrariesIOClientError, match="Request failed"):
            await client._make_request('GET', 'test_endpoint')

    @pytest.mark.asyncio
    async def test_get_rate_limit_info(self, client):
        """Test getting rate limit information."""
        # Set up mock rate limit info
        client._rate_limit_info = RateLimitInfo(
            limit=100,
            remaining=50,
            reset=1640995200.0,
            used=50
        )
        
        result = client.get_rate_limit_info()
        
        assert result is not None
        assert result.limit == 100
        assert result.remaining == 50
        assert result.reset == 1640995200.0
        assert result.used == 50

    @pytest.mark.asyncio
    async def test_get_rate_limit_info_none(self, client):
        """Test getting rate limit info when none is available."""
        client._rate_limit_info = None
        
        result = client.get_rate_limit_info()
        
        assert result is None

    @pytest.mark.asyncio
    async def test_clear_cache(self, client, mock_cache):
        """Test clearing cache."""
        await client.clear_cache()
        
        mock_cache.clear.assert_called_once()
        client.logger.info.assert_called_with("Cache cleared")

    @pytest.mark.asyncio
    async def test_get_platforms_success(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test successful platforms request."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = MockResponses.get_platforms_response()
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        result = await client.get_platforms()
        
        assert len(result) == 5
        assert isinstance(result[0], Platform)
        assert result[0].name == 'npm'
        assert result[0].project_count == 2000000

    @pytest.mark.asyncio
    async def test_get_platforms_invalid_data(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test platforms request with invalid data."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = {'invalid': 'data'}
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        with pytest.raises(LibrariesIOClientError, match="Invalid platforms data"):
            await client.get_platforms()

    @pytest.mark.asyncio
    async def test_get_package_success(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test successful package request."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = MockResponses.get_package_response()
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        result = await client.get_package('npm', 'react')
        
        assert isinstance(result, Package)
        assert result.name == 'react'
        assert result.platform == 'npm'
        assert result.description is not None

    @pytest.mark.asyncio
    async def test_get_package_invalid_platform(self, client):
        """Test package request with invalid platform."""
        with pytest.raises(ValueError, match="Invalid platform"):
            await client.get_package('invalid_platform', 'react')

    @pytest.mark.asyncio
    async def test_get_package_versions_success(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test successful package versions request."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = MockResponses.get_package_versions_response()
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        result = await client.get_package_versions('npm', 'react')
        
        assert len(result) == 5
        assert isinstance(result[0], PackageVersion)
        assert result[0].number == '18.2.0'

    @pytest.mark.asyncio
    async def test_get_package_dependencies_success(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test successful package dependencies request."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = MockResponses.get_package_dependencies_response()
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        result = await client.get_package_dependencies('npm', 'react')
        
        assert len(result) > 0
        assert isinstance(result[0], Dependency)
        assert result[0].project.name == 'react'

    @pytest.mark.asyncio
    async def test_get_package_dependents_success(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test successful package dependents request."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = MockResponses.get_package_dependents_response()
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        result = await client.get_package_dependents('npm', 'react')
        
        assert len(result) > 0
        assert isinstance(result[0], Package)
        assert result[0].name == 'some-dependent'

    @pytest.mark.asyncio
    async def test_search_packages_success(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test successful search packages request."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = MockResponses.get_search_response()
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        result = await client.search_packages('react')
        
        assert result.total_count > 0
        assert len(result.packages) > 0
        assert result.packages[0].name == 'react'

    @pytest.mark.asyncio
    async def test_get_user_success(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test successful user request."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = MockResponses.get_user_response()
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        result = await client.get_user('octocat')
        
        assert result.username == 'octocat'
        assert result.name == 'The Octocat'

    @pytest.mark.asyncio
    async def test_get_user_packages_success(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test successful user packages request."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = MockResponses.get_user_packages_response()
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        result = await client.get_user_packages('octocat')
        
        assert len(result) > 0
        assert isinstance(result[0], Package)
        assert result[0].name == 'hello-world'

    @pytest.mark.asyncio
    async def test_get_organization_success(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test successful organization request."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = MockResponses.get_organization_response()
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        result = await client.get_organization('github')
        
        assert result.name == 'GitHub'
        assert result.type == 'Organization'

    @pytest.mark.asyncio
    async def test_get_organization_packages_success(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test successful organization packages request."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = MockResponses.get_organization_packages_response()
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        result = await client.get_organization_packages('github')
        
        assert len(result) > 0
        assert isinstance(result[0], Package)
        assert result[0].name == 'hello-world'

    @pytest.mark.asyncio
    async def test_get_repository_success(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test successful repository request."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = MockResponses.get_repository_response()
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        result = await client.get_repository('github', 'https://github.com/facebook/react')
        
        assert result.name == 'react'
        assert result.platform == 'GitHub'
        assert result.url == 'https://github.com/facebook/react'

    @pytest.mark.asyncio
    async def test_get_repository_invalid_platform(self, client):
        """Test repository request with invalid platform."""
        with pytest.raises(ValueError, match="Invalid platform for repository"):
            await client.get_repository('invalid_platform', 'https://github.com/facebook/react')

    @pytest.mark.asyncio
    async def test_get_repository_invalid_github_url(self, client):
        """Test repository request with invalid GitHub URL."""
        with pytest.raises(ValueError, match="GitHub repository URL must start with https://github.com/"):
            await client.get_repository('github', 'https://invalid.url/react')

    @pytest.mark.asyncio
    async def test_get_repository_invalid_github_format(self, client):
        """Test repository request with invalid GitHub URL format."""
        with pytest.raises(ValueError, match="Invalid GitHub repository URL format"):
            await client.get_repository('github', 'https://github.com/invalid')

    @pytest.mark.asyncio
    async def test_rate_limiting(self, client, mock_rate_limiter):
        """Test rate limiting behavior."""
        mock_rate_limiter.acquire = AsyncMock()
        
        # Call a method that should trigger rate limiting
        await client.get_platforms()
        
        # Verify rate limiter was called
        mock_rate_limiter.acquire.assert_called()

    @pytest.mark.asyncio
    async def test_caching(self, client, mock_cache):
        """Test caching behavior."""
        mock_cache.get = AsyncMock(return_value=None)
        mock_cache.set = AsyncMock()
        
        # Call a method twice
        await client.get_platforms()
        await client.get_platforms()
        
        # Verify cache was used on second call
        assert mock_cache.get.call_count == 2
        assert mock_cache.set.call_count == 1  # Only set on first call

    @pytest.mark.asyncio
    async def test_retry_logic(self, client, mock_retry_handler):
        """Test retry logic."""
        mock_retry_handler.retry = AsyncMock()
        
        # Call a method that should trigger retry logic
        await client.get_platforms()
        
        # Verify retry handler was called
        mock_retry_handler.retry.assert_called()

    @pytest.mark.asyncio
    async def test_error_handling_network_error(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test error handling for network errors."""
        mock_cache.get.return_value = None
        mock_retry_handler.retry.side_effect = Exception("Network error")
        
        with pytest.raises(LibrariesIOClientError, match="Request failed"):
            await client.get_platforms()

    @pytest.mark.asyncio
    async def test_error_handling_http_error(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test error handling for HTTP errors."""
        mock_cache.get.return_value = None
        
        # Mock the retry handler to raise an HTTP error
        from unittest.mock import Mock
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = 'Not found'
        
        mock_retry_handler.retry.side_effect = client._handle_error(mock_response)
        
        with pytest.raises(NotFoundError):
            await client.get_platforms()

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test concurrent requests."""
        mock_cache.get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = MockResponses.get_platforms_response()
        client.session.request.return_value = mock_response
        
        mock_retry_handler.retry.return_value = mock_response
        
        # Make multiple concurrent requests
        tasks = [client.get_platforms() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert len(results) == 5
        for result in results:
            assert len(result) == 5

    @pytest.mark.asyncio
    async def test_timeout_handling(self, client, mock_cache, mock_rate_limiter, mock_retry_handler):
        """Test timeout handling."""
        mock_cache.get.return_value = None
        
        # Mock a timeout error
        import asyncio
        mock_retry_handler.retry.side_effect = asyncio.TimeoutError("Request timed out")
        
        with pytest.raises(LibrariesIOClientError, match="Request failed"):
            await client.get_platforms()

    @pytest.mark.asyncio
    async def test_rate_limit_info_persistence(self, client):
        """Test rate limit info persistence across requests."""
        # Set initial rate limit info
        client._rate_limit_info = RateLimitInfo(
            limit=100,
            remaining=50,
            reset=1640995200.0,
            used=50
        )
        
        # Verify it persists
        result1 = client.get_rate_limit_info()
        assert result1 is not None
        
        # Update it (simulating a response)
        client._rate_limit_info = RateLimitInfo(
            limit=100,
            remaining=49,
            reset=1640995200.0,
            used=51
        )
        
        # Verify it was updated
        result2 = client.get_rate_limit_info()
        assert result2.remaining == 49
        assert result2.used == 51
"""
Unit tests for the Libraries.io MCP Server utilities.

This module contains unit tests for the utility functions and classes.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone, timedelta

from src.libraries_io_mcp.utils import (
    RateLimitInfo, RateLimiter, CacheEntry, MemoryCache, 
    RetryHandler, HTTPClientHelper, validate_platform, 
    sanitize_package_name, default_rate_limiter, 
    default_cache, default_retry_handler
)
from tests.test_utils import MockDataGenerator, TestMockHelpers, TestAssertionHelpers


class TestRateLimitInfo:
    """Test suite for RateLimitInfo dataclass."""
    
    def test_rate_limit_info_creation(self):
        """Test RateLimitInfo creation."""
        info = RateLimitInfo(
            limit=60,
            remaining=59,
            reset=1234567890.0,
            used=1
        )
        
        assert info.limit == 60
        assert info.remaining == 59
        assert info.reset == 1234567890.0
        assert info.used == 1
    
    def test_rate_limit_info_creation_minimal(self):
        """Test RateLimitInfo creation with minimal values."""
        info = RateLimitInfo(
            limit=1,
            remaining=0,
            reset=time.time() + 60,
            used=1
        )
        
        assert info.limit == 1
        assert info.remaining == 0
        assert info.reset > time.time()
        assert info.used == 1


class TestRateLimiter:
    """Test suite for RateLimiter class."""
    
    @pytest.fixture
    def rate_limiter(self):
        """RateLimiter fixture."""
        return RateLimiter(limit=10, window_seconds=60)
    
    @pytest.mark.asyncio
    async def test_rate_limiter_initialization(self):
        """Test RateLimiter initialization."""
        limiter = RateLimiter(limit=10, window_seconds=60)
        
        assert limiter.limit == 10
        assert limiter.window_seconds == 60
        assert limiter.tokens == 10
        assert limiter.last_refill <= time.time()
    
    @pytest.mark.asyncio
    async def test_rate_limiter_acquire_success(self, rate_limiter):
        """Test successful token acquisition."""
        await rate_limiter.acquire(1)
        
        assert rate_limiter.tokens == 9
    
    @pytest.mark.asyncio
    async def test_rate_limiter_acquire_multiple_tokens(self, rate_limiter):
        """Test multiple token acquisition."""
        await rate_limiter.acquire(3)
        
        assert rate_limiter.tokens == 7
    
    @pytest.mark.asyncio
    async def test_rate_limiter_acquire_all_tokens(self, rate_limiter):
        """Test acquiring all tokens."""
        await rate_limiter.acquire(10)
        
        assert rate_limiter.tokens == 0
    
    @pytest.mark.asyncio
    async def test_rate_limiter_acquire_insufficient_tokens(self, rate_limiter):
        """Test acquiring more tokens than available."""
        await rate_limiter.acquire(10)  # Use all tokens
        
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(rate_limiter.acquire(1), timeout=1.0)
    
    @pytest.mark.asyncio
    async def test_rate_limiter_refill(self, rate_limiter):
        """Test token refill after window."""
        # Use all tokens
        await rate_limiter.acquire(10)
        assert rate_limiter.tokens == 0
        
        # Wait for window to pass
        await asyncio.sleep(0.1)
        
        # Check if tokens are refilled
        info = rate_limiter.get_info()
        assert info.remaining == 10
        assert info.used == 0
    
    @pytest.mark.asyncio
    async def test_rate_limiter_get_info(self, rate_limiter):
        """Test getting rate limit info."""
        info = rate_limiter.get_info()
        
        assert isinstance(info, RateLimitInfo)
        assert info.limit == 10
        assert info.remaining <= 10
        assert info.reset > time.time()
        assert info.used >= 0
    
    @pytest.mark.asyncio
    async def test_rate_limiter_get_info_empty(self, rate_limiter):
        """Test getting rate limit info when no tokens used."""
        info = rate_limiter.get_info()
        
        assert info.limit == 10
        assert info.remaining == 10
        assert info.used == 0
    
    @pytest.mark.asyncio
    async def test_rate_limiter_get_info_all_used(self, rate_limiter):
        """Test getting rate limit info when all tokens used."""
        await rate_limiter.acquire(10)
        info = rate_limiter.get_info()
        
        assert info.limit == 10
        assert info.remaining == 0
        assert info.used == 10


class TestCacheEntry:
    """Test suite for CacheEntry class."""
    
    def test_cache_entry_creation(self):
        """Test CacheEntry creation."""
        data = {"test": "data"}
        expires_at = time.time() + 300  # 5 minutes from now
        entry = CacheEntry(data, expires_at)
        
        assert entry.data == data
        assert entry.expires_at == expires_at
        assert not entry.is_expired()
    
    def test_cache_entry_expiration(self):
        """Test CacheEntry expiration."""
        data = {"test": "data"}
        expires_at = time.time() - 1  # 1 second ago
        entry = CacheEntry(data, expires_at)
        
        assert entry.is_expired()
    
    def test_cache_entry_ttl(self):
        """Test CacheEntry TTL calculation."""
        data = {"test": "data"}
        expires_at = time.time() + 300  # 5 minutes from now
        entry = CacheEntry(data, expires_at)
        
        assert entry.ttl() > 0
        assert entry.ttl() <= 300
    
    def test_cache_entry_ttl_expired(self):
        """Test CacheEntry TTL calculation when expired."""
        data = {"test": "data"}
        expires_at = time.time() - 1  # 1 second ago
        entry = CacheEntry(data, expires_at)
        
        assert entry.ttl() == 0


class TestMemoryCache:
    """Test suite for MemoryCache class."""
    
    @pytest.fixture
    def memory_cache(self):
        """MemoryCache fixture."""
        return MemoryCache(default_ttl=300, max_size=100)
    
    @pytest.mark.asyncio
    async def test_memory_cache_initialization(self):
        """Test MemoryCache initialization."""
        cache = MemoryCache(default_ttl=300, max_size=100)
        
        assert cache.default_ttl == 300
        assert cache.max_size == 100
        assert len(cache._cache) == 0
        assert len(cache._access_times) == 0
    
    @pytest.mark.asyncio
    async def test_memory_cache_set_and_get(self, memory_cache):
        """Test setting and getting cache entries."""
        endpoint = "test/endpoint"
        params = {"param1": "value1"}
        data = {"test": "data"}
        
        await memory_cache.set(endpoint, params, data)
        cached_data = await memory_cache.get(endpoint, params)
        
        assert cached_data == data
    
    @pytest.mark.asyncio
    async def test_memory_cache_get_not_found(self, memory_cache):
        """Test getting non-existent cache entry."""
        endpoint = "test/endpoint"
        params = {"param1": "value1"}
        
        cached_data = await memory_cache.get(endpoint, params)
        
        assert cached_data is None
    
    @pytest.mark.asyncio
    async def test_memory_cache_get_expired(self, memory_cache):
        """Test getting expired cache entry."""
        endpoint = "test/endpoint"
        params = {"param1": "value1"}
        data = {"test": "data"}
        
        # Set with very short TTL
        await memory_cache.set(endpoint, params, data, ttl=0.1)
        
        # Wait for expiration
        await asyncio.sleep(0.2)
        
        cached_data = await memory_cache.get(endpoint, params)
        
        assert cached_data is None
    
    @pytest.mark.asyncio
    async def test_memory_cache_set_ttl(self, memory_cache):
        """Test setting cache entry with custom TTL."""
        endpoint = "test/endpoint"
        params = {"param1": "value1"}
        data = {"test": "data"}
        custom_ttl = 60
        
        await memory_cache.set(endpoint, params, data, ttl=custom_ttl)
        
        # Check that TTL is set correctly
        key = memory_cache._generate_key(endpoint, params)
        entry = memory_cache._cache[key]
        
        assert entry.ttl() <= custom_ttl
    
    @pytest.mark.asyncio
    async def test_memory_cache_clear(self, memory_cache):
        """Test clearing all cache entries."""
        endpoint = "test/endpoint"
        params = {"param1": "value1"}
        data = {"test": "data"}
        
        await memory_cache.set(endpoint, params, data)
        await memory_cache.clear()
        
        cached_data = await memory_cache.get(endpoint, params)
        
        assert cached_data is None
        assert len(memory_cache._cache) == 0
        assert len(memory_cache._access_times) == 0
    
    @pytest.mark.asyncio
    async def test_memory_cache_size(self, memory_cache):
        """Test getting cache size."""
        endpoint = "test/endpoint"
        params = {"param1": "value1"}
        data = {"test": "data"}
        
        size_before = await memory_cache.size()
        await memory_cache.set(endpoint, params, data)
        size_after = await memory_cache.size()
        
        assert size_before == 0
        assert size_after == 1
    
    @pytest.mark.asyncio
    async def test_memory_cache_eviction(self, memory_cache):
        """Test cache eviction when max size is reached."""
        # Fill cache to max size
        for i in range(memory_cache.max_size):
            endpoint = f"test/endpoint{i}"
            params = {"param": str(i)}
            data = {"test": f"data{i}"}
            await memory_cache.set(endpoint, params, data)
        
        # Add one more entry to trigger eviction
        endpoint = "test/endpoint_new"
        params = {"param": "new"}
        data = {"test": "data_new"}
        await memory_cache.set(endpoint, params, data)
        
        # Check that cache size is still max size
        size = await memory_cache.size()
        assert size == memory_cache.max_size
    
    @pytest.mark.asyncio
    async def test_memory_cache_generate_key(self, memory_cache):
        """Test cache key generation."""
        endpoint = "test/endpoint"
        params = {"param1": "value1", "param2": "value2"}
        
        key1 = memory_cache._generate_key(endpoint, params)
        key2 = memory_cache._generate_key(endpoint, params)
        
        assert key1 == key2
        assert isinstance(key1, str)
        assert len(key1) > 0
    
    @pytest.mark.asyncio
    async def test_memory_cache_generate_key_different_params(self, memory_cache):
        """Test cache key generation with different parameters."""
        endpoint = "test/endpoint"
        params1 = {"param1": "value1"}
        params2 = {"param1": "value2"}
        
        key1 = memory_cache._generate_key(endpoint, params1)
        key2 = memory_cache._generate_key(endpoint, params2)
        
        assert key1 != key2


class TestRetryHandler:
    """Test suite for RetryHandler class."""
    
    @pytest.fixture
    def retry_handler(self):
        """RetryHandler fixture."""
        return RetryHandler(max_retries=3, base_delay=0.1, max_delay=1.0)
    
    @pytest.mark.asyncio
    async def test_retry_handler_initialization(self):
        """Test RetryHandler initialization."""
        handler = RetryHandler(max_retries=3, base_delay=0.1, max_delay=1.0)
        
        assert handler.max_retries == 3
        assert handler.base_delay == 0.1
        assert handler.max_delay == 1.0
    
    @pytest.mark.asyncio
    async def test_retry_handler_success(self, retry_handler):
        """Test successful retry."""
        mock_func = AsyncMock(return_value="success")
        
        result = await retry_handler.retry(mock_func)
        
        assert result == "success"
        mock_func.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_retry_handler_retry_once(self, retry_handler):
        """Test retry with one failure."""
        mock_func = AsyncMock(side_effect=[Exception("First failure"), "success"])
        
        result = await retry_handler.retry(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_handler_retry_multiple(self, retry_handler):
        """Test retry with multiple failures."""
        mock_func = AsyncMock(side_effect=[
            Exception("First failure"),
            Exception("Second failure"),
            "success"
        ])
        
        result = await retry_handler.retry(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_handler_exhausted(self, retry_handler):
        """Test retry when all attempts fail."""
        mock_func = AsyncMock(side_effect=Exception("Always fails"))
        
        with pytest.raises(Exception, match="Always fails"):
            await retry_handler.retry(mock_func)
        
        assert mock_func.call_count == retry_handler.max_retries + 1
    
    @pytest.mark.asyncio
    async def test_retry_handler_delay_calculation(self, retry_handler):
        """Test delay calculation with exponential backoff."""
        call_times = []
        
        def mock_func():
            call_times.append(time.time())
            raise Exception("Failure")
        
        with pytest.raises(Exception):
            await retry_handler.retry(mock_func)
        
        # Check that delays are increasing
        assert len(call_times) == retry_handler.max_retries + 1
        for i in range(1, len(call_times)):
            delay = call_times[i] - call_times[i-1]
            expected_delay = min(retry_handler.max_delay, retry_handler.base_delay * (2 ** (i-1)))
            assert delay >= expected_delay * 0.9  # Allow some tolerance


class TestHTTPClientHelper:
    """Test suite for HTTPClientHelper class."""
    
    def test_parse_rate_limit_success(self):
        """Test successful rate limit parsing."""
        headers = {
            "x-ratelimit-limit": "60",
            "x-ratelimit-remaining": "59",
            "x-ratelimit-reset": "1234567890"
        }
        
        info = HTTPClientHelper.parse_rate_limit(headers)
        
        assert info is not None
        assert info.limit == 60
        assert info.remaining == 59
        assert info.reset == 1234567890.0
        assert info.used == 1
    
    def test_parse_rate_limit_partial_headers(self):
        """Test rate limit parsing with partial headers."""
        headers = {
            "x-ratelimit-limit": "60",
            "x-ratelimit-remaining": "59"
            # Missing reset header
        }
        
        info = HTTPClientHelper.parse_rate_limit(headers)
        
        assert info is None
    
    def test_parse_rate_limit_invalid_values(self):
        """Test rate limit parsing with invalid values."""
        headers = {
            "x-ratelimit-limit": "invalid",
            "x-ratelimit-remaining": "invalid",
            "x-ratelimit-reset": "invalid"
        }
        
        info = HTTPClientHelper.parse_rate_limit(headers)
        
        assert info is None
    
    def test_parse_rate_limit_empty_headers(self):
        """Test rate limit parsing with empty headers."""
        headers = {}
        
        info = HTTPClientHelper.parse_rate_limit(headers)
        
        assert info is None
    
    def test_should_retry_retryable_status_codes(self):
        """Test retryable status codes."""
        retryable_codes = {429, 500, 502, 503, 504}
        
        for code in retryable_codes:
            assert HTTPClientHelper.should_retry(code) is True
    
    def test_should_retry_non_retryable_status_codes(self):
        """Test non-retryable status codes."""
        non_retryable_codes = {200, 201, 400, 401, 403, 404}
        
        for code in non_retryable_codes:
            assert HTTPClientHelper.should_retry(code) is False
    
    def test_get_error_message_json_response(self):
        """Test error message extraction from JSON response."""
        response_text = '{"error": "Bad Request", "message": "Invalid input"}'
        
        message = HTTPClientHelper.get_error_message(response_text)
        
        assert message == "Bad Request"
    
    def test_get_error_message_json_response_no_message(self):
        """Test error message extraction from JSON response without message."""
        response_text = '{"error": "Bad Request"}'
        
        message = HTTPClientHelper.get_error_message(response_text)
        
        assert message == "Bad Request"
    
    def test_get_error_message_json_response_invalid(self):
        """Test error message extraction from invalid JSON response."""
        response_text = 'Invalid JSON response'
        
        message = HTTPClientHelper.get_error_message(response_text)
        
        assert message == "Invalid JSON response"
    
    def test_get_error_message_plain_text(self):
        """Test error message extraction from plain text response."""
        response_text = "Bad Request"
        
        message = HTTPClientHelper.get_error_message(response_text)
        
        assert message == "Bad Request"


class TestValidatePlatform:
    """Test suite for validate_platform function."""
    
    def test_validate_platform_valid(self):
        """Test valid platform validation."""
        valid_platforms = ["npm", "pypi", "maven", "gem", "nuget", "docker", "hex", "cran"]
        
        for platform in valid_platforms:
            assert validate_platform(platform) is True
    
    def test_validate_platform_invalid(self):
        """Test invalid platform validation."""
        invalid_platforms = ["invalid", "unknown", "", "INVALID", "pypi123"]
        
        for platform in invalid_platforms:
            assert validate_platform(platform) is False
    
    def test_validate_platform_case_insensitive(self):
        """Test case insensitive platform validation."""
        assert validate_platform("NPM") is True
        assert validate_platform("PyPI") is True
        assert validate_platform("MAVEN") is True
    
    def test_validate_platform_whitespace(self):
        """Test platform validation with whitespace."""
        assert validate_platform(" npm ") is True
        assert validate_platform(" pypi ") is True


class TestSanitizePackageName:
    """Test suite for sanitize_package_name function."""
    
    def test_sanitize_package_name_normal(self):
        """Test normal package name sanitization."""
        assert sanitize_package_name("react") == "react"
        assert sanitize_package_name("lodash") == "lodash"
        assert sanitize_package_name("express") == "express"
    
    def test_sanitize_package_name_with_whitespace(self):
        """Test package name sanitization with whitespace."""
        assert sanitize_package_name(" react ") == "react"
        assert sanitize_package_name("  lodash  ") == "lodash"
        assert sanitize_package_name(" express ") == "express"
    
    def test_sanitize_package_name_multiple_spaces(self):
        """Test package name sanitization with multiple spaces."""
        assert sanitize_package_name("react    router") == "react router"
        assert sanitize_package_name("lodash   underscore") == "lodash underscore"
        assert sanitize_package_name("express    body-parser") == "express body-parser"
    
    def test_sanitize_package_name_tabs_and_newlines(self):
        """Test package name sanitization with tabs and newlines."""
        assert sanitize_package_name("react\nrouter") == "react router"
        assert sanitize_package_name("lodash\tunderscore") == "lodash underscore"
        assert sanitize_package_name("express\r\nbody-parser") == "express body-parser"
    
    def test_sanitize_package_name_mixed_whitespace(self):
        """Test package name sanitization with mixed whitespace."""
        assert sanitize_package_name("  react   \n router  \t") == "react router"
        assert sanitize_package_name("  lodash   \t underscore  \n") == "lodash underscore"
    
    def test_sanitize_package_name_empty(self):
        """Test empty package name sanitization."""
        assert sanitize_package_name("") == ""
        assert sanitize_package_name("   ") == ""
        assert sanitize_package_name("\n\t\r") == ""


class TestDefaultInstances:
    """Test suite for default utility instances."""
    
    def test_default_rate_limiter(self):
        """Test default rate limiter instance."""
        assert isinstance(default_rate_limiter, RateLimiter)
        assert default_rate_limiter.limit == 60
        assert default_rate_limiter.window_seconds == 60
    
    def test_default_cache(self):
        """Test default cache instance."""
        assert isinstance(default_cache, MemoryCache)
        assert default_cache.default_ttl == 300
        assert default_cache.max_size == 1000
    
    def test_default_retry_handler(self):
        """Test default retry handler instance."""
        assert isinstance(default_retry_handler, RetryHandler)
        assert default_retry_handler.max_retries == 3
        assert default_retry_handler.base_delay == 1.0
        assert default_retry_handler.max_delay == 60.0


if __name__ == "__main__":
    pytest.main([__file__])
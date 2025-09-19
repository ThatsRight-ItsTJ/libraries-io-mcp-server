"""
Utility functions for the Libraries.io MCP Server.

This module contains utility functions and helper classes.
"""

import asyncio
import time
import hashlib
import json
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from contextlib import asynccontextmanager


@dataclass
class RateLimitInfo:
    """Rate limit information."""
    limit: int
    remaining: int
    reset: float
    used: int


class RateLimiter:
    """Rate limiter with token bucket algorithm."""
    
    def __init__(self, limit: int, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            limit: Maximum number of requests allowed in the window
            window_seconds: Duration of the rate limit window in seconds
        """
        self.limit = limit
        self.window_seconds = window_seconds
        self.tokens = limit
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens from the rate limiter.
        
        Args:
            tokens: Number of tokens to acquire
        """
        async with self._lock:
            now = time.time()
            time_passed = now - self.last_refill
            
            # Refill tokens based on time passed
            if time_passed >= self.window_seconds:
                self.tokens = self.limit
                self.last_refill = now
            else:
                # Calculate how many tokens to add
                tokens_to_add = int((time_passed / self.window_seconds) * self.limit)
                self.tokens = min(self.limit, self.tokens + tokens_to_add)
                self.last_refill = now
            
            # Wait if we don't have enough tokens
            while self.tokens < tokens:
                sleep_time = self.window_seconds - time_passed + 1
                await asyncio.sleep(sleep_time)
                now = time.time()
                time_passed = now - self.last_refill
                
                # Refill tokens
                if time_passed >= self.window_seconds:
                    self.tokens = self.limit
                    self.last_refill = now
                else:
                    tokens_to_add = int((time_passed / self.window_seconds) * self.limit)
                    self.tokens = min(self.limit, self.tokens + tokens_to_add)
                    self.last_refill = now
            
            # Consume tokens
            self.tokens -= tokens
    
    def get_info(self) -> RateLimitInfo:
        """Get current rate limit information."""
        now = time.time()
        time_passed = now - self.last_refill
        
        if time_passed >= self.window_seconds:
            remaining = self.limit
            used = 0
        else:
            tokens_to_add = int((time_passed / self.window_seconds) * self.limit)
            remaining = min(self.limit, self.tokens + tokens_to_add)
            used = self.limit - remaining
        
        reset = self.last_refill + self.window_seconds
        
        return RateLimitInfo(
            limit=self.limit,
            remaining=remaining,
            reset=reset,
            used=used
        )


class CacheEntry:
    """Cache entry with expiration."""
    
    def __init__(self, data: Any, expires_at: float):
        self.data = data
        self.expires_at = expires_at
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() > self.expires_at
    
    def ttl(self) -> float:
        """Get time to live in seconds."""
        return max(0, self.expires_at - time.time())


class MemoryCache:
    """In-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        """
        Initialize memory cache.
        
        Args:
            default_ttl: Default time to live in seconds
            max_size: Maximum number of cache entries
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = asyncio.Lock()
    
    def _generate_key(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key from endpoint and parameters."""
        key_data = {
            'endpoint': endpoint,
            'params': params or {}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """
        Get cached data.
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            
        Returns:
            Cached data or None if not found or expired
        """
        async with self._lock:
            key = self._generate_key(endpoint, params)
            
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            if entry.is_expired():
                # Remove expired entry
                del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                return None
            
            # Update access time
            self._access_times[key] = time.time()
            return entry.data
    
    async def set(self, endpoint: str, params: Optional[Dict[str, Any]], data: Any, ttl: Optional[int] = None) -> None:
        """
        Set cached data.
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            data: Data to cache
            ttl: Time to live in seconds (uses default if None)
        """
        async with self._lock:
            key = self._generate_key(endpoint, params)
            
            # Check if we need to evict entries
            if len(self._cache) >= self.max_size:
                await self._evict_oldest()
            
            # Set cache entry
            expires_at = time.time() + (ttl or self.default_ttl)
            self._cache[key] = CacheEntry(data, expires_at)
            self._access_times[key] = time.time()
    
    async def _evict_oldest(self) -> None:
        """Evict the oldest cache entry."""
        if not self._access_times:
            return
        
        oldest_key = min(self._access_times.items(), key=lambda x: x[1])[0]
        del self._cache[oldest_key]
        del self._access_times[oldest_key]
    
    async def clear(self) -> None:
        """Clear all cached data."""
        async with self._lock:
            self._cache.clear()
            self._access_times.clear()
    
    async def size(self) -> int:
        """Get current cache size."""
        async with self._lock:
            return len(self._cache)


class RetryHandler:
    """Retry handler with exponential backoff."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        """
        Initialize retry handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff
            max_delay: Maximum delay between retries
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    async def retry(self, func, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    break
                
                # Calculate delay with exponential backoff
                delay = min(self.max_delay, self.base_delay * (2 ** attempt))
                
                # Add jitter to avoid thundering herd
                jitter = delay * 0.1 * (hash(time.time()) % 100) / 100
                delay += jitter
                
                await asyncio.sleep(delay)
        
        if last_exception is not None:
            raise last_exception
        raise Exception("Unknown error occurred")


class HTTPClientHelper:
    """Helper class for HTTP client operations."""
    
    @staticmethod
    def parse_rate_limit(headers: Dict[str, str]) -> Optional[RateLimitInfo]:
        """
        Parse rate limit information from HTTP headers.
        
        Args:
            headers: HTTP headers
            
        Returns:
            RateLimitInfo if rate limit headers are present, None otherwise
        """
        try:
            limit = int(headers.get('x-ratelimit-limit', 0))
            remaining = int(headers.get('x-ratelimit-remaining', 0))
            reset = float(headers.get('x-ratelimit-reset', 0))
            used = limit - remaining
            
            return RateLimitInfo(limit=limit, remaining=remaining, reset=reset, used=used)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def should_retry(status_code: int) -> bool:
        """
        Check if status code indicates a retryable error.
        
        Args:
            status_code: HTTP status code
            
        Returns:
            True if error is retryable
        """
        retryable_status_codes = {429, 500, 502, 503, 504}
        return status_code in retryable_status_codes
    
    @staticmethod
    def get_error_message(response_text: str) -> str:
        """
        Extract error message from response text.
        
        Args:
            response_text: HTTP response text
            
        Returns:
            Error message
        """
        try:
            data = json.loads(response_text)
            if isinstance(data, dict):
                return data.get('message', str(data))
        except json.JSONDecodeError:
            pass
        
        return response_text


async def timeout_context(timeout_seconds: float):
    """
    Timeout decorator for async functions.
    
    Args:
        timeout_seconds: Timeout in seconds
        
    Raises:
        asyncio.TimeoutError if timeout occurs
    """
    try:
        # Create a future that will complete after timeout_seconds
        future = asyncio.Future()
        loop = asyncio.get_event_loop()
        loop.call_later(timeout_seconds, future.set_result, None)
        
        # Wait for the future to complete
        await future
    except asyncio.TimeoutError:
        raise asyncio.TimeoutError(f"Operation timed out after {timeout_seconds} seconds")


def validate_platform(platform: str) -> bool:
    """
    Validate platform name.
    
    Args:
        platform: Platform name
        
    Returns:
        True if platform is valid
    """
    # Common package manager platforms
    valid_platforms = {
        'npm', 'pypi', 'maven', 'gem', 'nuget', 'docker', 'hex', 'cran',
        'hackage', 'packagist', 'cocoapods', 'bower', 'composer', 'go',
        'elm', 'pub', 'dart', 'conan', 'bitbucket', 'github', 'gitlab'
    }
    return platform.lower() in valid_platforms


def sanitize_package_name(name: str) -> str:
    """
    Sanitize package name for API requests.
    
    Args:
        name: Package name
        
    Returns:
        Sanitized package name
    """
    # Remove leading/trailing whitespace
    name = name.strip()
    
    # Replace multiple spaces with single space
    name = ' '.join(name.split())
    
    return name


# Global instances (can be overridden)
default_rate_limiter = RateLimiter(60, 60)  # 60 requests per 60 seconds
default_cache = MemoryCache(300, 1000)  # 5 minute TTL, 1000 max entries
default_retry_handler = RetryHandler(3, 1.0, 60.0)  # 3 retries, exponential backoff


__all__ = [
    "RateLimitInfo",
    "RateLimiter", 
    "CacheEntry",
    "MemoryCache",
    "RetryHandler",
    "HTTPClientHelper",
    "timeout_context",
    "validate_platform",
    "sanitize_package_name",
    "default_rate_limiter",
    "default_cache", 
    "default_retry_handler",
]
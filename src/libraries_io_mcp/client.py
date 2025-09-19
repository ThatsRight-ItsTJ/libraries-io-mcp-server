"""
Libraries.io API client implementation.

This module contains the client for interacting with the Libraries.io API.
"""

import asyncio
import os
import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

import httpx
from pydantic import ValidationError

from .models import (
    Platform, Package, PackageVersion, Dependency, Repository,
    User, Organization, SearchResult, APIError, RateLimitInfo,
    PlatformsResponse, PackageResponse, DependenciesResponse,
    DependentsResponse, SearchResponse, UserResponse, OrganizationResponse,
    RepositoryResponse
)
from .utils import (
    RateLimiter, MemoryCache, RetryHandler, HTTPClientHelper,
    validate_platform, sanitize_package_name,
    default_rate_limiter, default_cache, default_retry_handler
)


class LibrariesIOClientError(Exception):
    """Base exception for Libraries.io client errors."""
    pass


class RateLimitError(LibrariesIOClientError):
    """Raised when rate limit is exceeded."""
    pass


class AuthenticationError(LibrariesIOClientError):
    """Raised when authentication fails."""
    pass


class NotFoundError(LibrariesIOClientError):
    """Raised when requested resource is not found."""
    pass


class ServerError(LibrariesIOClientError):
    """Raised when server error occurs."""
    pass


class LibrariesIOClient:
    """
    Async client for interacting with the Libraries.io API.
    
    This client provides methods for all major Libraries.io API endpoints
    with built-in rate limiting, caching, retry logic, and error handling.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://libraries.io/api",
        rate_limit: int = 60,
        rate_limit_window: int = 60,
        cache_ttl: int = 300,
        cache_max_size: int = 1000,
        max_retries: int = 3,
        timeout: float = 30.0,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Libraries.io API client.
        
        Args:
            api_key: API key for authentication (can also be set via LIBRARIES_IO_API_KEY env var)
            base_url: Base URL for the API
            rate_limit: Maximum number of requests per rate limit window
            rate_limit_window: Rate limit window duration in seconds
            cache_ttl: Default cache time-to-live in seconds
            cache_max_size: Maximum number of cache entries
            max_retries: Maximum number of retry attempts for failed requests
            timeout: Request timeout in seconds
            logger: Optional logger instance
        """
        self.api_key = api_key or os.getenv("LIBRARIES_IO_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set LIBRARIES_IO_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(rate_limit, rate_limit_window)
        
        # Initialize cache
        self.cache = MemoryCache(cache_ttl, cache_max_size)
        
        # Initialize retry handler
        self.retry_handler = RetryHandler(max_retries)
        
        # Initialize HTTP client
        self.session = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "User-Agent": "LibrariesIO-MCP-Client/1.0.0",
                "Accept": "application/json"
            }
        )
        
        # Logger
        self.logger = logger or logging.getLogger(__name__)
        
        # Rate limit info tracking
        self._rate_limit_info: Optional[RateLimitInfo] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP client session."""
        await self.session.aclose()
    
    def _get_cache_key(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key for endpoint and parameters."""
        # Add API key to params for cache key generation
        cache_params = params.copy() if params else {}
        cache_params['api_key'] = self.api_key
        
        import json
        key_data = {
            'endpoint': endpoint,
            'params': cache_params
        }
        key_string = json.dumps(key_data, sort_keys=True)
        import hashlib
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _add_api_key(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add API key to parameters."""
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        return params
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response and parse JSON."""
        try:
            return response.json()
        except ValueError as e:
            raise LibrariesIOClientError(f"Invalid JSON response: {e}")
    
    def _check_rate_limit(self, response: httpx.Response) -> None:
        """Check rate limit headers and update rate limit info."""
        rate_limit_info = HTTPClientHelper.parse_rate_limit(response.headers)
        if rate_limit_info:
            self._rate_limit_info = rate_limit_info
            
            # Log rate limit usage
            self.logger.debug(
                f"Rate limit: {rate_limit_info.used}/{rate_limit_info.limit} "
                f"({rate_limit_info.remaining} remaining, resets at {datetime.fromtimestamp(rate_limit_info.reset)})"
            )
            
            # Raise rate limit error if we're about to exceed
            if rate_limit_info.remaining <= 0:
                raise RateLimitError("Rate limit exceeded")
    
    def _handle_error(self, response: httpx.Response) -> LibrariesIOClientError:
        """Handle HTTP error responses."""
        self._check_rate_limit(response)
        
        error_message = HTTPClientHelper.get_error_message(response.text)
        
        if response.status_code == 401:
            return AuthenticationError(f"Authentication failed: {error_message}")
        elif response.status_code == 404:
            return NotFoundError(f"Resource not found: {error_message}")
        elif response.status_code == 429:
            return RateLimitError(f"Rate limit exceeded: {error_message}")
        elif 500 <= response.status_code < 600:
            return ServerError(f"Server error ({response.status_code}): {error_message}")
        else:
            return LibrariesIOClientError(f"HTTP {response.status_code}: {error_message}")
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic, rate limiting, and caching.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request data
            
        Returns:
            Response data as dictionary
            
        Raises:
            LibrariesIOClientError: If request fails
        """
        # Add API key to parameters
        params = self._add_api_key(params)
        
        # Generate cache key
        cache_key = self._get_cache_key(endpoint, params)
        
        # Check cache first
        cached_data = await self.cache.get(endpoint, params)
        if cached_data is not None:
            self.logger.debug(f"Cache hit for {endpoint}")
            return cached_data
        
        # Rate limiting
        await self.rate_limiter.acquire()
        
        # Make request with retry logic
        try:
            response = await self.retry_handler.retry(
                self._execute_request,
                method,
                endpoint,
                params,
                data
            )
            
            # Parse response
            data = self._handle_response(response)
            
            # Cache response
            await self.cache.set(endpoint, params, data)
            
            return data
            
        except LibrariesIOClientError:
            raise
        except Exception as e:
            raise LibrariesIOClientError(f"Request failed: {e}")
    
    async def _execute_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        """Execute single HTTP request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        self.logger.debug(f"Making {method} request to {url}")
        
        response = await self.session.request(
            method=method,
            url=url,
            params=params,
            json=data
        )
        
        # Check for errors
        if response.status_code >= 400:
            raise self._handle_error(response)
        
        # Check rate limit
        self._check_rate_limit(response)
        
        return response
    
    def get_rate_limit_info(self) -> Optional[RateLimitInfo]:
        """Get current rate limit information."""
        return self._rate_limit_info
    
    async def clear_cache(self) -> None:
        """Clear all cached data."""
        await self.cache.clear()
        self.logger.info("Cache cleared")
    
    # API Endpoints
    
    async def get_platforms(self) -> List[Platform]:
        """
        Get supported package managers/platforms.
        
        Returns:
            List of supported platforms
        """
        data = await self._make_request("GET", "platforms")
        
        try:
            return [Platform(**platform_data) for platform_data in data]
        except ValidationError as e:
            raise LibrariesIOClientError(f"Invalid platforms data: {e}")
    
    async def get_package(
        self,
        platform: str,
        name: str,
        include_versions: bool = False
    ) -> Package:
        """
        Get package information.
        
        Args:
            platform: Package manager platform
            name: Package name
            include_versions: Whether to include version information
            
        Returns:
            Package information
        """
        if not validate_platform(platform):
            raise ValueError(f"Invalid platform: {platform}")
        
        name = sanitize_package_name(name)
        
        params = {}
        if include_versions:
            params['include_versions'] = 'true'
        
        endpoint = f"projects/{platform}/{name}"
        data = await self._make_request("GET", endpoint, params)
        
        try:
            return Package(**data)
        except ValidationError as e:
            raise LibrariesIOClientError(f"Invalid package data: {e}")
    
    async def get_package_versions(
        self,
        platform: str,
        name: str
    ) -> List[PackageVersion]:
        """
        Get package versions.
        
        Args:
            platform: Package manager platform
            name: Package name
            
        Returns:
            List of package versions
        """
        if not validate_platform(platform):
            raise ValueError(f"Invalid platform: {platform}")
        
        name = sanitize_package_name(name)
        
        endpoint = f"projects/{platform}/{name}/versions"
        data = await self._make_request("GET", endpoint)
        
        try:
            return [PackageVersion(**version_data) for version_data in data]
        except ValidationError as e:
            raise LibrariesIOClientError(f"Invalid versions data: {e}")
    
    async def get_package_dependencies(
        self,
        platform: str,
        name: str,
        version: Optional[str] = None
    ) -> List[Dependency]:
        """
        Get package dependencies.
        
        Args:
            platform: Package manager platform
            name: Package name
            version: Package version (optional)
            
        Returns:
            List of dependencies
        """
        if not validate_platform(platform):
            raise ValueError(f"Invalid platform: {platform}")
        
        name = sanitize_package_name(name)
        
        endpoint = f"projects/{platform}/{name}/dependencies"
        params = {}
        if version:
            params['version'] = version
        
        data = await self._make_request("GET", endpoint, params)
        
        try:
            return [Dependency(**dep_data) for dep_data in data]
        except ValidationError as e:
            raise LibrariesIOClientError(f"Invalid dependencies data: {e}")
    
    async def get_package_dependents(
        self,
        platform: str,
        name: str,
        page: int = 1,
        per_page: int = 100
    ) -> List[Package]:
        """
        Get packages that depend on this package.
        
        Args:
            platform: Package manager platform
            name: Package name
            page: Page number
            per_page: Items per page (max 100)
            
        Returns:
            List of dependent packages
        """
        if not validate_platform(platform):
            raise ValueError(f"Invalid platform: {platform}")
        
        name = sanitize_package_name(name)
        
        endpoint = f"projects/{platform}/{name}/dependents"
        params = {
            'page': page,
            'per_page': min(per_page, 100)
        }
        
        data = await self._make_request("GET", endpoint, params)
        
        try:
            return [Package(**pkg_data) for pkg_data in data]
        except ValidationError as e:
            raise LibrariesIOClientError(f"Invalid dependents data: {e}")
    
    async def search_packages(
        self,
        query: str,
        platforms: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        licenses: Optional[List[str]] = None,
        page: int = 1,
        per_page: int = 10
    ) -> SearchResult:
        """
        Search for packages.
        
        Args:
            query: Search query
            platforms: Filter by platforms
            languages: Filter by languages
            licenses: Filter by licenses
            page: Page number
            per_page: Items per page (max 100)
            
        Returns:
            Search results
        """
        params = {
            'q': query,
            'page': page,
            'per_page': min(per_page, 100)
        }
        
        if platforms:
            params['platforms'] = ','.join(platforms)
        if languages:
            params['languages'] = ','.join(languages)
        if licenses:
            params['licenses'] = ','.join(licenses)
        
        data = await self._make_request("GET", "search", params)
        
        try:
            return SearchResult(**data)
        except ValidationError as e:
            raise LibrariesIOClientError(f"Invalid search data: {e}")
    
    async def get_user(self, username: str) -> User:
        """
        Get user information.
        
        Args:
            username: GitHub username
            
        Returns:
            User information
        """
        endpoint = f"user/{username}"
        data = await self._make_request("GET", endpoint)
        
        try:
            return User(**data)
        except ValidationError as e:
            raise LibrariesIOClientError(f"Invalid user data: {e}")
    
    async def get_user_packages(
        self,
        username: str,
        page: int = 1,
        per_page: int = 100
    ) -> List[Package]:
        """
        Get user's packages.
        
        Args:
            username: GitHub username
            page: Page number
            per_page: Items per page (max 100)
            
        Returns:
            List of user's packages
        """
        endpoint = f"user/{username}/packages"
        params = {
            'page': page,
            'per_page': min(per_page, 100)
        }
        
        data = await self._make_request("GET", endpoint, params)
        
        try:
            return [Package(**pkg_data) for pkg_data in data]
        except ValidationError as e:
            raise LibrariesIOClientError(f"Invalid user packages data: {e}")
    
    async def get_organization(self, org_name: str) -> Organization:
        """
        Get organization information.
        
        Args:
            org_name: GitHub organization name
            
        Returns:
            Organization information
        """
        endpoint = f"org/{org_name}"
        data = await self._make_request("GET", endpoint)
        
        try:
            return Organization(**data)
        except ValidationError as e:
            raise LibrariesIOClientError(f"Invalid organization data: {e}")
    
    async def get_organization_packages(
        self,
        org_name: str,
        page: int = 1,
        per_page: int = 100
    ) -> List[Package]:
        """
        Get organization's packages.
        
        Args:
            org_name: GitHub organization name
            page: Page number
            per_page: Items per page (max 100)
            
        Returns:
            List of organization's packages
        """
        endpoint = f"org/{org_name}/packages"
        params = {
            'page': page,
            'per_page': min(per_page, 100)
        }
        
        data = await self._make_request("GET", endpoint, params)
        
        try:
            return [Package(**pkg_data) for pkg_data in data]
        except ValidationError as e:
            raise LibrariesIOClientError(f"Invalid organization packages data: {e}")
    
    async def get_repository(self, platform: str, repo_url: str) -> Repository:
        """
        Get repository information.
        
        Args:
            platform: Platform (github, gitlab, bitbucket)
            repo_url: Repository URL
            
        Returns:
            Repository information
        """
        if platform not in ['github', 'gitlab', 'bitbucket']:
            raise ValueError(f"Invalid platform for repository: {platform}")
        
        # Extract owner/repo from URL
        if platform == 'github':
            if not repo_url.startswith('https://github.com/'):
                raise ValueError("GitHub repository URL must start with https://github.com/")
            parts = repo_url.replace('https://github.com/', '').split('/')
            if len(parts) < 2:
                raise ValueError("Invalid GitHub repository URL format")
            owner, repo = parts[0], parts[1]
            endpoint = f"github/{owner}/{repo}"
        elif platform == 'gitlab':
            if not repo_url.startswith('https://gitlab.com/'):
                raise ValueError("GitLab repository URL must start with https://gitlab.com/")
            parts = repo_url.replace('https://gitlab.com/', '').split('/')
            if len(parts) < 2:
                raise ValueError("Invalid GitLab repository URL format")
            owner, repo = parts[0], parts[1]
            endpoint = f"gitlab/{owner}/{repo}"
        elif platform == 'bitbucket':
            if not repo_url.startswith('https://bitbucket.org/'):
                raise ValueError("Bitbucket repository URL must start with https://bitbucket.org/")
            parts = repo_url.replace('https://bitbucket.org/', '').split('/')
            if len(parts) < 2:
                raise ValueError("Invalid Bitbucket repository URL format")
            owner, repo = parts[0], parts[1]
            endpoint = f"bitbucket/{owner}/{repo}"
        
        data = await self._make_request("GET", endpoint)
        
        try:
            return Repository(**data)
        except ValidationError as e:
            raise LibrariesIOClientError(f"Invalid repository data: {e}")


__all__ = ["LibrariesIOClient"]
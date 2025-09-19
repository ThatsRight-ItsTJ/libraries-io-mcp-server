"""
Resources for the Libraries.io MCP Server.

This module contains MCP resource implementations for Libraries.io data.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from fastmcp import FastMCP
from .client import LibrariesIOClient


def parse_resource_uri(uri: str) -> Dict[str, Any]:
    """
    Parse resource URI and extract parameters.
    
    Args:
        uri: Resource URI (e.g., "packages://npm/react/info")
        
    Returns:
        Dictionary with parsed parameters
        
    Raises:
        ValueError: If URI format is invalid
    """
    try:
        parsed = urlparse(uri)
        if not parsed.scheme:
            raise ValueError(f"Invalid URI format: {uri}")
        
        # For custom URI schemes like users://, the netloc might be empty
        # and the actual data might be in the path
        if not parsed.netloc and parsed.scheme in ['users', 'orgs', 'packages', 'platforms', 'search']:
            # For these schemes, the path contains the actual resource identifier
            result = {
                "scheme": parsed.scheme,
                "netloc": "",
                "path": parsed.path.strip('/'),
                "params": parse_qs(parsed.query)
            }
        else:
            result = {
                "scheme": parsed.scheme,
                "netloc": parsed.netloc,
                "path": parsed.path.strip('/'),
                "params": parse_qs(parsed.query)
            }
        
        # Parse path components
        path_parts = result["path"].split('/')
        
        if result["scheme"] == "packages":
            if len(path_parts) >= 3:
                result["platform"] = path_parts[0]
                result["name"] = path_parts[1]
                result["resource_type"] = path_parts[2]
            elif len(path_parts) >= 2:
                result["platform"] = path_parts[0]
                result["name"] = path_parts[1]
                result["resource_type"] = "info"  # default
        
        elif result["scheme"] == "platforms":
            if len(path_parts) == 1 and path_parts[0] == "supported":
                result["resource_type"] = "supported"
                result["platform"] = None
            elif len(path_parts) >= 1:
                result["platform"] = path_parts[0]
                result["resource_type"] = "stats"
        
        elif result["scheme"] == "search":
            result["resource_type"] = path_parts[0] if path_parts else "packages"
        
        elif result["scheme"] in ["users", "orgs"]:
            # For users:// and orgs:// schemes, the username/org is in netloc, resource type in path
            if parsed.netloc:
                result["username" if result["scheme"] == "users" else "org"] = parsed.netloc
            if path_parts and path_parts[0]:
                result["resource_type"] = path_parts[0]
            else:
                result["resource_type"] = "packages"
        
        return result
        
    except Exception as e:
        raise ValueError(f"Failed to parse URI {uri}: {e}")


def validate_platform(platform: str) -> bool:
    """Validate platform name."""
    from .utils import validate_platform as validate_platform_util
    return validate_platform_util(platform)


def sanitize_package_name(name: str) -> str:
    """Sanitize package name."""
    from .utils import sanitize_package_name as sanitize_package_name_util
    return sanitize_package_name_util(name)


def register_resources(server: FastMCP, client: LibrariesIOClient) -> None:
    """
    Register all MCP resources with the server.
    
    Args:
        server: FastMCP server instance
        client: LibrariesIOClient instance
    """
    
    # Platform Resources
    
    @server.resource("platforms://supported")
    async def get_supported_platforms() -> Dict[str, Any]:
        """
        Get list of all supported platforms.
        
        URI: platforms://supported
        
        Returns:
            Dictionary with list of supported platforms
        """
        try:
            platforms = await client.get_platforms()
            return {
                "resource_type": "platforms",
                "subtype": "supported",
                "total_count": len(platforms),
                "platforms": [platform.model_dump() for platform in platforms],
                "source": "libraries.io"
            }
        except Exception as e:
            logging.error(f"Failed to get supported platforms: {e}")
            raise
    
    @server.resource("platforms://{platform}/stats")
    async def get_platform_stats(platform: str) -> Dict[str, Any]:
        """
        Get platform-specific statistics.
        
        URI: platforms://{platform}/stats
        
        Args:
            platform: Platform name (extracted from URI)
            
        Returns:
            Platform statistics dictionary
        """
        try:
            if not validate_platform(platform):
                raise ValueError(f"Invalid platform: {platform}")
            
            # Use the platform stats endpoint from client
            stats_data = await client._make_request("GET", f"platform/{platform}")
            
            return {
                "resource_type": "platforms",
                "platform": platform,
                "statistics": stats_data,
                "source": "libraries.io"
            }
        except Exception as e:
            logging.error(f"Failed to get platform stats for {platform}: {e}")
            raise
    
    # Package Resources
    
    @server.resource("packages://{platform}/{name}/info")
    async def get_package_info(platform: str, name: str) -> Dict[str, Any]:
        """
        Get comprehensive package information.
        
        URI: packages://{platform}/{name}/info
        
        Args:
            platform: Package manager platform (extracted from URI)
            name: Package name (extracted from URI)
            
        Returns:
            Package information dictionary
        """
        try:
            if not validate_platform(platform):
                raise ValueError(f"Invalid platform: {platform}")
            
            name = sanitize_package_name(name)
            package = await client.get_package(platform, name, include_versions=True)
            
            return {
                "resource_type": "packages",
                "platform": platform,
                "name": name,
                "package": package.model_dump(),
                "source": "libraries.io"
            }
        except Exception as e:
            logging.error(f"Failed to get package info for {platform}/{name}: {e}")
            raise
    
    @server.resource("packages://{platform}/{name}/versions")
    async def get_package_versions(platform: str, name: str) -> Dict[str, Any]:
        """
        Get package version history.
        
        URI: packages://{platform}/{name}/versions
        
        Args:
            platform: Package manager platform (extracted from URI)
            name: Package name (extracted from URI)
            
        Returns:
            Package versions dictionary
        """
        try:
            if not validate_platform(platform):
                raise ValueError(f"Invalid platform: {platform}")
            
            name = sanitize_package_name(name)
            versions = await client.get_package_versions(platform, name)
            
            return {
                "resource_type": "packages",
                "platform": platform,
                "name": name,
                "versions": [version.model_dump() for version in versions],
                "total_count": len(versions),
                "source": "libraries.io"
            }
        except Exception as e:
            logging.error(f"Failed to get package versions for {platform}/{name}: {e}")
            raise
    
    @server.resource("packages://{platform}/{name}/dependencies")
    async def get_package_dependencies(platform: str, name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Get package dependencies.
        
        URI: packages://{platform}/{name}/dependencies[?version={version}]
        
        Args:
            platform: Package manager platform (extracted from URI)
            name: Package name (extracted from URI)
            version: Specific version (optional, from query params)
            
        Returns:
            Package dependencies dictionary
        """
        try:
            if not validate_platform(platform):
                raise ValueError(f"Invalid platform: {platform}")
            
            name = sanitize_package_name(name)
            dependencies = await client.get_package_dependencies(platform, name, version)
            
            return {
                "resource_type": "packages",
                "platform": platform,
                "name": name,
                "version": version,
                "dependencies": [dep.model_dump() for dep in dependencies],
                "total_count": len(dependencies),
                "source": "libraries.io"
            }
        except Exception as e:
            logging.error(f"Failed to get package dependencies for {platform}/{name}: {e}")
            raise
    
    @server.resource("packages://{platform}/{name}/dependents")
    async def get_package_dependents(platform: str, name: str, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        """
        Get packages that depend on this package.
        
        URI: packages://{platform}/{name}/dependents[?page={page}&per_page={per_page}]
        
        Args:
            platform: Package manager platform (extracted from URI)
            name: Package name (extracted from URI)
            page: Page number (optional, from query params, default: 1)
            per_page: Items per page (optional, from query params, default: 100, max: 100)
            
        Returns:
            Package dependents dictionary
        """
        try:
            if not validate_platform(platform):
                raise ValueError(f"Invalid platform: {platform}")
            
            name = sanitize_package_name(name)
            dependents = await client.get_package_dependents(platform, name, page, per_page)
            
            return {
                "resource_type": "packages",
                "platform": platform,
                "name": name,
                "page": page,
                "per_page": per_page,
                "dependents": [pkg.model_dump() for pkg in dependents],
                "total_count": len(dependents),
                "source": "libraries.io"
            }
        except Exception as e:
            logging.error(f"Failed to get package dependents for {platform}/{name}: {e}")
            raise
    
    # Search Resources
    
    @server.resource("search://packages")
    async def search_packages(query: str, platforms: Optional[str] = None,
                              languages: Optional[str] = None, licenses: Optional[str] = None,
                              page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Search for packages.
        
        URI: search://packages[?q={query}&platforms={platforms}&languages={languages}&licenses={licenses}&page={page}&per_page={per_page}]
        
        Args:
            query: Search query (required, from query params)
            platforms: Filter by platforms (optional, from query params)
            languages: Filter by languages (optional, from query params)
            licenses: Filter by licenses (optional, from query params)
            page: Page number (optional, from query params, default: 1)
            per_page: Items per page (optional, from query params, default: 10, max: 100)
            
        Returns:
            Search results dictionary
        """
        try:
            if not query:
                raise ValueError("Query parameter 'q' is required")
            
            # Parse comma-separated values
            platform_list = platforms.split(',') if platforms else None
            language_list = languages.split(',') if languages else None
            license_list = licenses.split(',') if licenses else None
            
            search_result = await client.search_packages(
                query=query,
                platforms=platform_list,
                languages=language_list,
                licenses=license_list,
                page=page,
                per_page=min(per_page, 100)
            )
            
            return {
                "resource_type": "search",
                "search_type": "packages",
                "query": query,
                "platforms": platform_list,
                "languages": language_list,
                "licenses": license_list,
                "page": page,
                "per_page": per_page,
                "total_count": search_result.total_count,
                "incomplete_results": search_result.incomplete_results,
                "items": [pkg.model_dump() for pkg in search_result.items],
                "source": "libraries.io"
            }
        except Exception as e:
            logging.error(f"Failed to search packages with query '{query}': {e}")
            raise
    
    @server.resource("search://trending")
    async def get_trending_packages(platform: Optional[str] = None,
                                   period: str = "weekly") -> Dict[str, Any]:
        """
        Get trending packages.
        
        URI: search://trending[?platform={platform}&period={period}]
        
        Args:
            platform: Filter by platform (optional, from query params)
            period: Time period (optional, from query params, default: "weekly")
            
        Returns:
            Trending packages dictionary
        """
        try:
            # Note: Libraries.io doesn't have a direct trending endpoint,
            # so we'll use search with popular keywords as a workaround
            trending_queries = {
                "weekly": ["popular", "trending", "hot"],
                "monthly": ["popular", "trending", "rising"],
                "daily": ["trending", "new", "hot"]
            }
            
            queries = trending_queries.get(period.lower(), ["popular", "trending"])
            
            # Search for popular packages
            all_results = []
            for query in queries[:3]:  # Limit to 3 queries to avoid rate limiting
                if platform:
                    search_result = await client.search_packages(
                        query=query,
                        platforms=[platform] if platform else None,
                        page=1,
                        per_page=min(20, 100 // len(queries))
                    )
                else:
                    search_result = await client.search_packages(
                        query=query,
                        page=1,
                        per_page=min(20, 100 // len(queries))
                    )
                all_results.extend(search_result.items)
            
            # Remove duplicates and sort by stars
            unique_results = {}
            for pkg in all_results:
                key = (pkg.platform, pkg.name)
                if key not in unique_results or (pkg.stars or 0) > (unique_results[key].stars or 0):
                    unique_results[key] = pkg
            
            sorted_results = sorted(
                unique_results.values(),
                key=lambda x: (x.stars or 0),
                reverse=True
            )[:50]  # Limit to top 50
            
            return {
                "resource_type": "search",
                "search_type": "trending",
                "platform": platform,
                "period": period,
                "total_count": len(sorted_results),
                "items": [pkg.model_dump() for pkg in sorted_results],
                "source": "libraries.io"
            }
        except Exception as e:
            logging.error(f"Failed to get trending packages: {e}")
            raise
    
    # User/Organization Resources
    
    @server.resource("users://{username}/packages")
    async def get_user_packages(username: str, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        """
        Get user's packages.
        
        URI: users://{username}/packages[?page={page}&per_page={per_page}]
        
        Args:
            username: GitHub username (extracted from URI)
            page: Page number (optional, from query params, default: 1)
            per_page: Items per page (optional, from query params, default: 100, max: 100)
            
        Returns:
            User packages dictionary
        """
        try:
            packages = await client.get_user_packages(username, page, per_page)
            
            return {
                "resource_type": "users",
                "username": username,
                "page": page,
                "per_page": per_page,
                "packages": [pkg.model_dump() for pkg in packages],
                "total_count": len(packages),
                "source": "libraries.io"
            }
        except Exception as e:
            logging.error(f"Failed to get user packages for {username}: {e}")
            raise
    
    @server.resource("orgs://{org}/packages")
    async def get_organization_packages(org: str, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        """
        Get organization's packages.
        
        URI: orgs://{org}/packages[?page={page}&per_page={per_page}]
        
        Args:
            org: GitHub organization name (extracted from URI)
            page: Page number (optional, from query params, default: 1)
            per_page: Items per page (optional, from query params, default: 100, max: 100)
            
        Returns:
            Organization packages dictionary
        """
        try:
            packages = await client.get_organization_packages(org, page, per_page)
            
            return {
                "resource_type": "orgs",
                "organization": org,
                "page": page,
                "per_page": per_page,
                "packages": [pkg.model_dump() for pkg in packages],
                "total_count": len(packages),
                "source": "libraries.io"
            }
        except Exception as e:
            logging.error(f"Failed to get organization packages for {org}: {e}")
            raise


__all__ = ["register_resources", "parse_resource_uri"]
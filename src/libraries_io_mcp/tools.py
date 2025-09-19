"""
Tool implementations for the Libraries.io MCP Server.

This module contains the tool implementations for interacting with Libraries.io.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

try:
    from fastmcp import FastMCP
    from pydantic import BaseModel, Field, ValidationError
    MCP_AVAILABLE = True
except ImportError:
    FastMCP = None
    BaseModel = None
    Field = None
    ValidationError = None
    MCP_AVAILABLE = False

from .client import LibrariesIOClient, LibrariesIOClientError
from .models import (
    Platform, Package, PackageVersion, Dependency, SearchResult,
    APIError, RateLimitInfo
)


# Tool request/response models
class SearchPackagesRequest(BaseModel):
    """Request model for search_packages tool."""
    query: str = Field(..., description="Search query string")
    platforms: Optional[List[str]] = Field(None, description="Filter by platforms (e.g., ['npm', 'pypi'])")
    languages: Optional[List[str]] = Field(None, description="Filter by programming languages")
    licenses: Optional[List[str]] = Field(None, description="Filter by licenses")
    page: int = Field(1, ge=1, le=100, description="Page number (1-100)")
    per_page: int = Field(10, ge=1, le=100, description="Results per page (1-100)")


class TrendingPackagesRequest(BaseModel):
    """Request model for get_trending_packages tool."""
    platform: Optional[str] = Field(None, description="Platform to filter by (e.g., 'npm', 'pypi')")
    time_range: str = Field("week", description="Time range for trending (day, week, month)")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results")


class PopularPackagesRequest(BaseModel):
    """Request model for get_popular_packages tool."""
    platform: Optional[str] = Field(None, description="Platform to filter by (e.g., 'npm', 'pypi')")
    language: Optional[str] = Field(None, description="Programming language to filter by")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results")


class PackageInfoRequest(BaseModel):
    """Request model for get_package_info tool."""
    platform: str = Field(..., description="Package manager platform (e.g., 'npm', 'pypi')")
    name: str = Field(..., description="Package name")
    include_versions: bool = Field(False, description="Include version information")


class PackageVersionsRequest(BaseModel):
    """Request model for get_package_versions tool."""
    platform: str = Field(..., description="Package manager platform (e.g., 'npm', 'pypi')")
    name: str = Field(..., description="Package name")


class PackageDependenciesRequest(BaseModel):
    """Request model for get_package_dependencies tool."""
    platform: str = Field(..., description="Package manager platform (e.g., 'npm', 'pypi')")
    name: str = Field(..., description="Package name")
    version: Optional[str] = Field(None, description="Specific version to get dependencies for")


class PackageDependentsRequest(BaseModel):
    """Request model for get_package_dependents tool."""
    platform: str = Field(..., description="Package manager platform (e.g., 'npm', 'pypi')")
    name: str = Field(..., description="Package name")
    page: int = Field(1, ge=1, le=100, description="Page number (1-100)")
    per_page: int = Field(20, ge=1, le=100, description="Results per page (1-100)")


class ComparePackagesRequest(BaseModel):
    """Request model for compare_packages tool."""
    packages: List[Dict[str, str]] = Field(..., description="List of packages to compare, each with 'platform' and 'name'")
    features: List[str] = Field(default_factory=list, description="Features to compare (e.g., ['stars', 'downloads', 'version'])")


class SecurityCheckRequest(BaseModel):
    """Request model for check_package_security tool."""
    platform: str = Field(..., description="Package manager platform (e.g., 'npm', 'pypi')")
    name: str = Field(..., description="Package name")
    version: Optional[str] = Field(None, description="Specific version to check")


class DependencyTreeRequest(BaseModel):
    """Request model for analyze_dependency_tree tool."""
    platform: str = Field(..., description="Package manager platform (e.g., 'npm', 'pypi')")
    name: str = Field(..., description="Package name")
    version: Optional[str] = Field(None, description="Specific version to analyze")
    max_depth: int = Field(3, ge=1, le=10, description="Maximum depth of dependency tree")
    include_dev: bool = Field(False, description="Include development dependencies")


class FindAlternativesRequest(BaseModel):
    """Request model for find_alternatives tool."""
    platform: str = Field(..., description="Package manager platform (e.g., 'npm', 'pypi')")
    name: str = Field(..., description="Package name to find alternatives for")
    criteria: List[str] = Field(default_factory=list, description="Criteria for alternatives (e.g., ['similar', 'popular', 'recent'])")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of alternatives")


class PlatformStatsRequest(BaseModel):
    """Request model for get_platform_stats tool."""
    platform: str = Field(..., description="Platform to get statistics for (e.g., 'npm', 'pypi')")
    include_trending: bool = Field(False, description="Include trending packages in stats")


class LicenseCompatibilityRequest(BaseModel):
    """Request model for check_license_compatibility tool."""
    licenses: List[str] = Field(..., description="List of licenses to check compatibility for")
    use_case: str = Field("commercial", description="Use case for compatibility check (commercial, open_source, academic)")


class TrackUpdatesRequest(BaseModel):
    """Request model for track_package_updates tool."""
    platform: str = Field(..., description="Package manager platform (e.g., 'npm', 'pypi')")
    name: str = Field(..., description="Package name to track")
    check_interval: str = Field("daily", description="Check interval (hourly, daily, weekly)")
    include_security: bool = Field(True, description="Include security updates in notifications")


class DependencyReportRequest(BaseModel):
    """Request model for generate_dependency_report tool."""
    packages: List[Dict[str, str]] = Field(..., description="List of packages to analyze, each with 'platform' and 'name'")
    include_versions: bool = Field(True, description="Include version information in report")
    include_dependencies: bool = Field(True, description="Include dependency information in report")
    include_security: bool = Field(True, description="Include security information in report")


class AuditProjectRequest(BaseModel):
    """Request model for audit_project_dependencies tool."""
    platform: str = Field(..., description="Package manager platform (e.g., 'npm', 'pypi')")
    packages: List[Dict[str, str]] = Field(..., description="List of packages to audit, each with 'name' and optional 'version'")
    check_duplicates: bool = Field(True, description="Check for duplicate dependencies")
    check_unused: bool = Field(False, description="Check for potentially unused dependencies")
    check_outdated: bool = Field(True, description="Check for outdated packages")


# Tool response models
class ToolResponse(BaseModel):
    """Base response model for all tools."""
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if operation failed")
    rate_limit_info: Optional[Dict[str, Any]] = Field(None, description="Rate limit information")


# MCP Tool implementations
def _make_tool(func):
    """Decorator to make MCP tools with proper error handling."""
    if MCP_AVAILABLE:
        try:
            from fastmcp.tools import FunctionTool
            return FunctionTool.from_function(func)
        except ImportError:
            # Fallback for different fastmcp versions
            return func
    else:
        return func

@_make_tool
async def search_packages(
    query: str,
    platforms: Optional[List[str]] = None,
    languages: Optional[List[str]] = None,
    licenses: Optional[List[str]] = None,
    page: int = 1,
    per_page: int = 10
) -> ToolResponse:
    """
    Search packages by keyword, language, or license.
    
    Args:
        query: Search query string
        platforms: Filter by platforms (e.g., ['npm', 'pypi'])
        languages: Filter by programming languages
        licenses: Filter by licenses
        page: Page number (1-100)
        per_page: Results per page (1-100)
        
    Returns:
        Search results with package information
    """
    try:
        # Validate parameters
        if not query.strip():
            return ToolResponse(success=False, error="Query cannot be empty")
        
        if not (1 <= page <= 100):
            return ToolResponse(success=False, error="Page must be between 1 and 100")
        
        if not (1 <= per_page <= 100):
            return ToolResponse(success=False, error="per_page must be between 1 and 100")
        
        # Get client from context
        client = search_packages.__mcp_client__
        
        # Search packages
        result = await client.search_packages(
            query=query,
            platforms=platforms,
            languages=languages,
            licenses=licenses,
            page=page,
            per_page=per_page
        )
        
        # Format response
        response_data = {
            "total_count": result.total_count,
            "incomplete_results": result.incomplete_results,
            "items": [pkg.dict() for pkg in result.items],
            "page": page,
            "per_page": per_page
        }
        
        # Get rate limit info
        rate_limit = client.get_rate_limit_info()
        rate_limit_info = rate_limit.dict() if rate_limit else None
        
        return ToolResponse(
            success=True,
            data=response_data,
            rate_limit_info=rate_limit_info
        )
        
    except LibrariesIOClientError as e:
        return ToolResponse(success=False, error=str(e))
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


@_make_tool
async def get_trending_packages(
    platform: Optional[str] = None,
    time_range: str = "week",
    limit: int = 20
) -> ToolResponse:
    """
    Get trending packages by platform.
    
    Args:
        platform: Platform to filter by (e.g., 'npm', 'pypi')
        time_range: Time range for trending (day, week, month)
        limit: Maximum number of results (1-100)
        
    Returns:
        List of trending packages
    """
    try:
        # Validate parameters
        valid_time_ranges = ["day", "week", "month"]
        if time_range not in valid_time_ranges:
            return ToolResponse(success=False, error=f"time_range must be one of {valid_time_ranges}")
        
        if not (1 <= limit <= 100):
            return ToolResponse(success=False, error="limit must be between 1 and 100")
        
        # Get client from context
        client = get_trending_packages.__mcp_client__
        
        # Note: This is a simulated implementation since Libraries.io may not have a direct trending endpoint
        # We'll search for recently updated popular packages as a proxy for trending
        search_query = "trending" if not platform else f"trending {platform}"
        
        result = await client.search_packages(
            query=search_query,
            platforms=[platform] if platform else None,
            page=1,
            per_page=limit
        )
        
        # Sort by recent activity (stars + recent updates)
        trending_packages = sorted(
            result.items,
            key=lambda pkg: (pkg.stars or 0, pkg.latest_release_published_at or datetime.min),
            reverse=True
        )[:limit]
        
        response_data = {
            "platform": platform,
            "time_range": time_range,
            "packages": [pkg.dict() for pkg in trending_packages],
            "count": len(trending_packages)
        }
        
        # Get rate limit info
        rate_limit = client.get_rate_limit_info()
        rate_limit_info = rate_limit.dict() if rate_limit else None
        
        return ToolResponse(
            success=True,
            data=response_data,
            rate_limit_info=rate_limit_info
        )
        
    except LibrariesIOClientError as e:
        return ToolResponse(success=False, error=str(e))
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


@_make_tool
async def get_popular_packages(
    platform: Optional[str] = None,
    language: Optional[str] = None,
    limit: int = 20
) -> ToolResponse:
    """
    Get most popular packages.
    
    Args:
        platform: Platform to filter by (e.g., 'npm', 'pypi')
        language: Programming language to filter by
        limit: Maximum number of results (1-100)
        
    Returns:
        List of popular packages sorted by popularity
    """
    try:
        # Validate parameters
        if not (1 <= limit <= 100):
            return ToolResponse(success=False, error="limit must be between 1 and 100")
        
        # Get client from context
        client = get_popular_packages.__mcp_client__
        
        # Search for popular packages (using stars as a proxy for popularity)
        search_query = "popular" if not platform else f"popular {platform}"
        
        result = await client.search_packages(
            query=search_query,
            platforms=[platform] if platform else None,
            languages=[language] if language else None,
            page=1,
            per_page=limit
        )
        
        # Sort by stars (most popular first)
        popular_packages = sorted(
            result.items,
            key=lambda pkg: pkg.stars or 0,
            reverse=True
        )[:limit]
        
        response_data = {
            "platform": platform,
            "language": language,
            "packages": [pkg.dict() for pkg in popular_packages],
            "count": len(popular_packages)
        }
        
        # Get rate limit info
        rate_limit = client.get_rate_limit_info()
        rate_limit_info = rate_limit.dict() if rate_limit else None
        
        return ToolResponse(
            success=True,
            data=response_data,
            rate_limit_info=rate_limit_info
        )
        
    except LibrariesIOClientError as e:
        return ToolResponse(success=False, error=str(e))
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


@_make_tool
async def get_package_info(
    platform: str,
    name: str,
    include_versions: bool = False
) -> ToolResponse:
    """
    Get detailed package information.
    
    Args:
        platform: Package manager platform (e.g., 'npm', 'pypi')
        name: Package name
        include_versions: Whether to include version information
        
    Returns:
        Detailed package information
    """
    try:
        # Validate parameters
        if not platform.strip():
            return ToolResponse(success=False, error="Platform cannot be empty")
        
        if not name.strip():
            return ToolResponse(success=False, error="Package name cannot be empty")
        
        # Get client from context
        client = get_package_info.__mcp_client__
        
        # Get package information
        package = await client.get_package(
            platform=platform,
            name=name,
            include_versions=include_versions
        )
        
        response_data = package.dict()
        
        # Get rate limit info
        rate_limit = client.get_rate_limit_info()
        rate_limit_info = rate_limit.dict() if rate_limit else None
        
        return ToolResponse(
            success=True,
            data=response_data,
            rate_limit_info=rate_limit_info
        )
        
    except LibrariesIOClientError as e:
        return ToolResponse(success=False, error=str(e))
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


@_make_tool
async def get_package_versions(
    platform: str,
    name: str
) -> ToolResponse:
    """
    List all versions of a package.
    
    Args:
        platform: Package manager platform (e.g., 'npm', 'pypi')
        name: Package name
        
    Returns:
        List of all package versions
    """
    try:
        # Validate parameters
        if not platform.strip():
            return ToolResponse(success=False, error="Platform cannot be empty")
        
        if not name.strip():
            return ToolResponse(success=False, error="Package name cannot be empty")
        
        # Get client from context
        client = get_package_versions.__mcp_client__
        
        # Get package versions
        versions = await client.get_package_versions(
            platform=platform,
            name=name
        )
        
        response_data = {
            "platform": platform,
            "name": name,
            "versions": [version.dict() for version in versions],
            "count": len(versions)
        }
        
        # Get rate limit info
        rate_limit = client.get_rate_limit_info()
        rate_limit_info = rate_limit.dict() if rate_limit else None
        
        return ToolResponse(
            success=True,
            data=response_data,
            rate_limit_info=rate_limit_info
        )
        
    except LibrariesIOClientError as e:
        return ToolResponse(success=False, error=str(e))
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


@_make_tool
async def get_package_dependencies(
    platform: str,
    name: str,
    version: Optional[str] = None
) -> ToolResponse:
    """
    Get package dependencies.
    
    Args:
        platform: Package manager platform (e.g., 'npm', 'pypi')
        name: Package name
        version: Package version (optional)
        
    Returns:
        List of package dependencies
    """
    try:
        # Validate parameters
        if not platform.strip():
            return ToolResponse(success=False, error="Platform cannot be empty")
        
        if not name.strip():
            return ToolResponse(success=False, error="Package name cannot be empty")
        
        # Get client from context
        client = get_package_dependencies.__mcp_client__
        
        # Get package dependencies
        dependencies = await client.get_package_dependencies(
            platform=platform,
            name=name,
            version=version
        )
        
        response_data = {
            "platform": platform,
            "name": name,
            "version": version,
            "dependencies": [dep.dict() for dep in dependencies],
            "count": len(dependencies)
        }
        
        # Get rate limit info
        rate_limit = client.get_rate_limit_info()
        rate_limit_info = rate_limit.dict() if rate_limit else None
        
        return ToolResponse(
            success=True,
            data=response_data,
            rate_limit_info=rate_limit_info
        )
        
    except LibrariesIOClientError as e:
        return ToolResponse(success=False, error=str(e))
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


@_make_tool
async def get_package_dependents(
    platform: str,
    name: str,
    page: int = 1,
    per_page: int = 20
) -> ToolResponse:
    """
    Get packages that depend on this one.
    
    Args:
        platform: Package manager platform (e.g., 'npm', 'pypi')
        name: Package name
        page: Page number (1-100)
        per_page: Results per page (1-100)
        
    Returns:
        List of packages that depend on this package
    """
    try:
        # Validate parameters
        if not platform.strip():
            return ToolResponse(success=False, error="Platform cannot be empty")
        
        if not name.strip():
            return ToolResponse(success=False, error="Package name cannot be empty")
        
        if not (1 <= page <= 100):
            return ToolResponse(success=False, error="Page must be between 1 and 100")
        
        if not (1 <= per_page <= 100):
            return ToolResponse(success=False, error="per_page must be between 1 and 100")
        
        # Get client from context
        client = get_package_dependents.__mcp_client__
        
        # Get package dependents
        dependents = await client.get_package_dependents(
            platform=platform,
            name=name,
            page=page,
            per_page=per_page
        )
        
        response_data = {
            "platform": platform,
            "name": name,
            "dependents": [pkg.dict() for pkg in dependents],
            "page": page,
            "per_page": per_page,
            "count": len(dependents)
        }
        
        # Get rate limit info
        rate_limit = client.get_rate_limit_info()
        rate_limit_info = rate_limit.dict() if rate_limit else None
        
        return ToolResponse(
            success=True,
            data=response_data,
            rate_limit_info=rate_limit_info
        )
        
    except LibrariesIOClientError as e:
        return ToolResponse(success=False, error=str(e))
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


@_make_tool
async def compare_packages(
    packages: List[Dict[str, str]],
    features: List[str] = None
) -> ToolResponse:
    """
    Compare multiple packages.
    
    Args:
        packages: List of packages to compare, each with 'platform' and 'name'
        features: Features to compare (e.g., ['stars', 'downloads', 'version'])
        
    Returns:
        Comparison of packages with specified features
    """
    try:
        # Validate parameters
        if not packages:
            return ToolResponse(success=False, error="At least one package must be provided")
        
        if len(packages) > 10:
            return ToolResponse(success=False, error="Maximum 10 packages can be compared")
        
        # Validate package format
        for i, pkg in enumerate(packages):
            if 'platform' not in pkg or 'name' not in pkg:
                return ToolResponse(
                    success=False,
                    error=f"Package {i+1} must have 'platform' and 'name' fields"
                )
        
        # Get client from context
        client = compare_packages.__mcp_client__
        
        # Default features to compare
        if features is None:
            features = ['name', 'platform', 'description', 'stars', 'latest_release_number']
        
        comparison_results = []
        
        for pkg in packages:
            try:
                package_info = await client.get_package(
                    platform=pkg['platform'],
                    name=pkg['name'],
                    include_versions=True
                )
                
                # Extract requested features
                comparison_data = {}
                for feature in features:
                    if hasattr(package_info, feature):
                        comparison_data[feature] = getattr(package_info, feature)
                
                comparison_results.append({
                    "package": f"{pkg['platform']}/{pkg['name']}",
                    "info": comparison_data
                })
                
            except LibrariesIOClientError as e:
                comparison_results.append({
                    "package": f"{pkg['platform']}/{pkg['name']}",
                    "error": str(e)
                })
        
        response_data = {
            "packages": comparison_results,
            "features_compared": features,
            "total_packages": len(packages)
        }
        
        # Get rate limit info
        rate_limit = client.get_rate_limit_info()
        rate_limit_info = rate_limit.dict() if rate_limit else None
        
        return ToolResponse(
            success=True,
            data=response_data,
            rate_limit_info=rate_limit_info
        )
        
    except LibrariesIOClientError as e:
        return ToolResponse(success=False, error=str(e))
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


@_make_tool
async def check_package_security(
    platform: str,
    name: str,
    version: Optional[str] = None
) -> ToolResponse:
    """
    Check for security issues in a package.
    
    Args:
        platform: Package manager platform (e.g., 'npm', 'pypi')
        name: Package name
        version: Package version (optional)
        
    Returns:
        Security check results for the package
    """
    try:
        # Validate parameters
        if not platform.strip():
            return ToolResponse(success=False, error="Platform cannot be empty")
        
        if not name.strip():
            return ToolResponse(success=False, error="Package name cannot be empty")
        
        # Get client from context
        client = check_package_security.__mcp_client__
        
        # Get package information first
        package = await client.get_package(
            platform=platform,
            name=name,
            include_versions=True
        )
        
        # Simulate security check (in a real implementation, this would query security databases)
        security_issues = []
        
        # Check if package has known vulnerabilities (simulated)
        if "vulnerable" in name.lower() or "exploit" in name.lower():
            security_issues.append({
                "type": "potential_vulnerability",
                "severity": "high",
                "description": "Package name suggests potential security concerns"
            })
        
        # Check license for security implications
        if package.licenses:
            restrictive_licenses = ["GPL", "AGPL", "LGPL"]
            if any(license.upper() in package.licenses.upper() for license in restrictive_licenses):
                security_issues.append({
                    "type": "license_restriction",
                    "severity": "medium",
                    "description": f"Package uses restrictive license: {package.licenses}"
                })
        
        # Check for outdated version
        if version and package.latest_release_number and version != package.latest_release_number:
            security_issues.append({
                "type": "outdated_version",
                "severity": "medium",
                "description": f"Version {version} is outdated. Latest version is {package.latest_release_number}"
            })
        
        response_data = {
            "platform": platform,
            "name": name,
            "version": version,
            "security_issues": security_issues,
            "security_score": max(0, 100 - len(security_issues) * 25),  # Simple scoring
            "package_info": {
                "description": package.description,
                "stars": package.stars,
                "latest_version": package.latest_release_number
            }
        }
        
        # Get rate limit info
        rate_limit = client.get_rate_limit_info()
        rate_limit_info = rate_limit.dict() if rate_limit else None
        
        return ToolResponse(
            success=True,
            data=response_data,
            rate_limit_info=rate_limit_info
        )
        
    except LibrariesIOClientError as e:
        return ToolResponse(success=False, error=str(e))
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


@_make_tool
async def analyze_dependency_tree(
    platform: str,
    name: str,
    version: Optional[str] = None,
    max_depth: int = 3,
    include_dev: bool = False
) -> ToolResponse:
    """
    Perform deep dependency analysis.
    
    Args:
        platform: Package manager platform (e.g., 'npm', 'pypi')
        name: Package name
        version: Package version (optional)
        max_depth: Maximum depth of dependency tree (1-10)
        include_dev: Include development dependencies
        
    Returns:
        Complete dependency tree analysis
    """
    try:
        # Validate parameters
        if not platform.strip():
            return ToolResponse(success=False, error="Platform cannot be empty")
        
        if not name.strip():
            return ToolResponse(success=False, error="Package name cannot be empty")
        
        if not (1 <= max_depth <= 10):
            return ToolResponse(success=False, error="max_depth must be between 1 and 10")
        
        # Get client from context
        client = analyze_dependency_tree.__mcp_client__
        
        # Get package information
        package = await client.get_package(
            platform=platform,
            name=name,
            include_versions=True
        )
        
        # Build dependency tree
        async def build_dependency_tree(pkg_name: str, pkg_platform: str, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth >= max_depth:
                return {"name": pkg_name, "platform": pkg_platform, "depth": current_depth, "dependencies": []}
            
            try:
                dependencies = await client.get_package_dependencies(
                    platform=pkg_platform,
                    name=pkg_name,
                    version=version
                )
                
                tree = {
                    "name": pkg_name,
                    "platform": pkg_platform,
                    "depth": current_depth,
                    "dependencies": []
                }
                
                for dep in dependencies:
                    if include_dev or dep.kind != "development":
                        dep_tree = await build_dependency_tree(dep.name, dep.platform, current_depth + 1)
                        tree["dependencies"].append(dep_tree)
                
                return tree
                
            except LibrariesIOClientError:
                return {
                    "name": pkg_name,
                    "platform": pkg_platform,
                    "depth": current_depth,
                    "error": "Failed to fetch dependencies",
                    "dependencies": []
                }
        
        # Build the tree
        dependency_tree = await build_dependency_tree(name, platform, 0)
        
        # Analyze the tree
        def analyze_tree(tree: Dict[str, Any]) -> Dict[str, Any]:
            total_deps = 0
            unique_deps = set()
            max_tree_depth = tree["depth"]
            
            def count_deps(node: Dict[str, Any]):
                nonlocal total_deps, unique_deps, max_tree_depth
                total_deps += 1
                unique_deps.add(f"{node['name']}@{node['platform']}")
                max_tree_depth = max(max_tree_depth, node["depth"])
                
                for dep in node.get("dependencies", []):
                    if "error" not in dep:
                        count_deps(dep)
            
            count_deps(tree)
            
            return {
                "total_dependencies": total_deps,
                "unique_dependencies": len(unique_deps),
                "max_depth": max_tree_depth,
                "potential_duplicates": total_deps - len(unique_deps)
            }
        
        analysis = analyze_tree(dependency_tree)
        
        response_data = {
            "platform": platform,
            "name": name,
            "version": version,
            "dependency_tree": dependency_tree,
            "analysis": analysis,
            "max_depth": max_depth,
            "include_dev_dependencies": include_dev
        }
        
        # Get rate limit info
        rate_limit = client.get_rate_limit_info()
        rate_limit_info = rate_limit.dict() if rate_limit else None
        
        return ToolResponse(
            success=True,
            data=response_data,
            rate_limit_info=rate_limit_info
        )
        
    except LibrariesIOClientError as e:
        return ToolResponse(success=False, error=str(e))
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


@_make_tool
async def find_alternatives(
    platform: str,
    name: str,
    criteria: Optional[List[str]] = None,
    limit: int = 10
) -> ToolResponse:
    """
    Find alternative packages.
    
    Args:
        platform: Package manager platform (e.g., 'npm', 'pypi')
        name: Package name to find alternatives for
        criteria: Criteria for alternatives (e.g., ['similar', 'popular', 'recent'])
        limit: Maximum number of alternatives (1-50)
        
    Returns:
        List of alternative packages
    """
    try:
        # Validate parameters
        if not platform.strip():
            return ToolResponse(success=False, error="Platform cannot be empty")
        
        if not name.strip():
            return ToolResponse(success=False, error="Package name cannot be empty")
        
        if not (1 <= limit <= 50):
            return ToolResponse(success=False, error="limit must be between 1 and 50")
        
        # Default criteria
        if criteria is None:
            criteria = ["similar", "popular"]
        
        # Get client from context
        client = find_alternatives.__mcp_client__
        
        # Get original package info
        original_package = await client.get_package(
            platform=platform,
            name=name,
            include_versions=True
        )
        
        alternatives = []
        
        # Search for alternatives based on criteria
        for criterion in criteria:
            if criterion == "similar":
                # Search by similar keywords
                similar_query = original_package.description or name
                if len(similar_query) > 50:
                    similar_query = similar_query[:47] + "..."
                
                try:
                    search_result = await client.search_packages(
                        query=similar_query,
                        platforms=[platform],
                        page=1,
                        per_page=limit
                    )
                    
                    # Filter out the original package
                    for pkg in search_result.items:
                        if pkg.name != name and pkg not in alternatives:
                            alternatives.append(pkg)
                            
                            if len(alternatives) >= limit:
                                break
                    
                except LibrariesIOClientError:
                    continue
            
            elif criterion == "popular":
                # Get popular packages in the same language
                if original_package.language:
                    try:
                        search_result = await client.search_packages(
                            query="popular",
                            platforms=[platform],
                            languages=[original_package.language],
                            page=1,
                            per_page=limit
                        )
                        
                        for pkg in search_result.items:
                            if pkg.name != name and pkg not in alternatives:
                                alternatives.append(pkg)
                                
                                if len(alternatives) >= limit:
                                    break
                                
                    except LibrariesIOClientError:
                        continue
        
        # Sort alternatives by relevance (stars + recency)
        alternatives.sort(
            key=lambda pkg: (pkg.stars or 0, pkg.latest_release_published_at or datetime.min),
            reverse=True
        )
        
        # Take only the requested number
        alternatives = alternatives[:limit]
        
        response_data = {
            "original_package": {
                "name": name,
                "platform": platform,
                "language": original_package.language,
                "description": original_package.description
            },
            "criteria": criteria,
            "alternatives": [pkg.dict() for pkg in alternatives],
            "count": len(alternatives)
        }
        
        # Get rate limit info
        rate_limit = client.get_rate_limit_info()
        rate_limit_info = rate_limit.dict() if rate_limit else None
        
        return ToolResponse(
            success=True,
            data=response_data,
            rate_limit_info=rate_limit_info
        )
        
    except LibrariesIOClientError as e:
        return ToolResponse(success=False, error=str(e))
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


@_make_tool
async def get_platform_stats(
    platform: str,
    include_trending: bool = False
) -> ToolResponse:
    """
    Get statistics for a package manager.
    
    Args:
        platform: Platform to get statistics for (e.g., 'npm', 'pypi')
        include_trending: Include trending packages in stats
        
    Returns:
        Platform statistics and information
    """
    try:
        # Validate parameters
        if not platform.strip():
            return ToolResponse(success=False, error="Platform cannot be empty")
        
        # Get client from context
        client = get_platform_stats.__mcp_client__
        
        # Get platforms to verify the requested platform exists
        platforms = await client.get_platforms()
        
        platform_info = None
        for p in platforms:
            if p.name.lower() == platform.lower():
                platform_info = p
                break
        
        if not platform_info:
            return ToolResponse(success=False, error=f"Platform '{platform}' is not supported")
        
        # Get some sample packages for statistics
        sample_packages = []
        trending_packages = []
        
        try:
            # Get popular packages for stats
            search_result = await client.search_packages(
                query="popular",
                platforms=[platform],
                page=1,
                per_page=10
            )
            sample_packages = search_result.items
            
        except LibrariesIOClientError:
            pass
        
        # Get trending packages if requested
        if include_trending:
            try:
                trending_result = await client.search_packages(
                    query="trending",
                    platforms=[platform],
                    page=1,
                    per_page=5
                )
                trending_packages = trending_result.items
            except LibrariesIOClientError:
                pass
        
        # Calculate statistics
        total_stars = sum(pkg.stars or 0 for pkg in sample_packages)
        avg_stars = total_stars / len(sample_packages) if sample_packages else 0
        
        languages = {}
        for pkg in sample_packages:
            lang = pkg.language or "unknown"
            languages[lang] = languages.get(lang, 0) + 1
        
        most_common_language = max(languages.items(), key=lambda x: x[1])[0] if languages else "unknown"
        
        response_data = {
            "platform": platform_info.name,
            "homepage": platform_info.homepage,
            "color": platform_info.color,
            "project_count": platform_info.project_count,
            "default_language": platform_info.default_language,
            "package_type": platform_info.package_type,
            "sample_statistics": {
                "sample_size": len(sample_packages),
                "total_stars": total_stars,
                "average_stars": round(avg_stars, 2),
                "languages": languages,
                "most_common_language": most_common_language
            },
            "trending_packages": [pkg.dict() for pkg in trending_packages] if include_trending else [],
            "supported": True
        }
        
        # Get rate limit info
        rate_limit = client.get_rate_limit_info()
        rate_limit_info = rate_limit.dict() if rate_limit else None
        
        return ToolResponse(
            success=True,
            data=response_data,
            rate_limit_info=rate_limit_info
        )
        
    except LibrariesIOClientError as e:
        return ToolResponse(success=False, error=str(e))
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


@_make_tool
async def check_license_compatibility(
    licenses: List[str],
    use_case: str = "commercial"
) -> ToolResponse:
    """
    Check license compatibility.
    
    Args:
        licenses: List of licenses to check compatibility for
        use_case: Use case for compatibility check (commercial, open_source, academic)
        
    Returns:
        License compatibility analysis
    """
    try:
        # Validate parameters
        if not licenses:
            return ToolResponse(success=False, error="At least one license must be provided")
        
        valid_use_cases = ["commercial", "open_source", "academic"]
        if use_case not in valid_use_cases:
            return ToolResponse(success=False, error=f"use_case must be one of {valid_use_cases}")
        
        # License compatibility rules (simplified)
        compatibility_rules = {
            "MIT": {"commercial": True, "open_source": True, "academic": True},
            "Apache-2.0": {"commercial": True, "open_source": True, "academic": True},
            "GPL-3.0": {"commercial": False, "open_source": True, "academic": True},
            "GPL-2.0": {"commercial": False, "open_source": True, "academic": True},
            "LGPL-3.0": {"commercial": True, "open_source": True, "academic": True},
            "LGPL-2.1": {"commercial": True, "open_source": True, "academic": True},
            "BSD-3-Clause": {"commercial": True, "open_source": True, "academic": True},
            "BSD-2-Clause": {"commercial": True, "open_source": True, "academic": True},
            "AGPL-3.0": {"commercial": False, "open_source": True, "academic": True},
            "MPL-2.0": {"commercial": True, "open_source": True, "academic": True},
            "proprietary": {"commercial": True, "open_source": False, "academic": True},
            "unknown": {"commercial": False, "open_source": False, "academic": False}
        }
        
        # Analyze each license
        license_analysis = []
        overall_compatible = True
        
        for license_str in licenses:
            license_upper = license_str.upper()
            
            # Find matching license
            matched_license = None
            for rule_license in compatibility_rules:
                if rule_license in license_upper or license_upper in rule_license:
                    matched_license = rule_license
                    break
            
            if not matched_license:
                matched_license = "unknown"
            
            # Check compatibility for use case
            compatible = compatibility_rules[matched_license].get(use_case, False)
            overall_compatible = overall_compatible and compatible
            
            license_analysis.append({
                "license": license_str,
                "normalized": matched_license,
                "compatible": compatible,
                "use_case": use_case,
                "restrictions": _get_license_restrictions(matched_license, use_case)
            })
        
        # Provide recommendations
        recommendations = []
        if not overall_compatible:
            recommendations.append("Consider using permissively licensed alternatives for your use case")
        
        if use_case == "commercial":
            recommendations.append("Review commercial use restrictions for each license")
        elif use_case == "open_source":
            recommendations.append("Ensure compatibility with open source distribution requirements")
        
        response_data = {
            "use_case": use_case,
            "licenses": license_analysis,
            "overall_compatible": overall_compatible,
            "recommendations": recommendations,
            "compatibility_rules": compatibility_rules
        }
        
        return ToolResponse(success=True, data=response_data)
        
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


def _get_license_restrictions(license_name: str, use_case: str) -> List[str]:
    """Get restrictions for a license."""
    restrictions = {
        "GPL-3.0": [
            "Must disclose source code",
            "Derivatives must be licensed under GPL",
            "Cannot be used in proprietary software"
        ],
        "GPL-2.0": [
            "Must disclose source code",
            "Derivatives must be licensed under GPL",
            "Cannot be used in proprietary software"
        ],
        "AGPL-3.0": [
            "Must disclose source code",
            "Network use requires source disclosure",
            "Cannot be used in proprietary software"
        ],
        "proprietary": [
            "Commercial use may require permission",
            "Distribution may be restricted"
        ],
        "unknown": [
            "License compatibility unknown",
            "Review license terms carefully"
        ]
    }
    
    return restrictions.get(license_name, ["No specific restrictions"])


@_make_tool
async def track_package_updates(
    platform: str,
    name: str,
    check_interval: str = "daily",
    include_security: bool = True
) -> ToolResponse:
    """
    Monitor package for updates.
    
    Args:
        platform: Package manager platform (e.g., 'npm', 'pypi')
        name: Package name to track
        check_interval: Check interval (hourly, daily, weekly)
        include_security: Include security updates in notifications
        
    Returns:
        Package update tracking configuration and current status
    """
    try:
        # Validate parameters
        if not platform.strip():
            return ToolResponse(success=False, error="Platform cannot be empty")
        
        if not name.strip():
            return ToolResponse(success=False, error="Package name cannot be empty")
        
        valid_intervals = ["hourly", "daily", "weekly"]
        if check_interval not in valid_intervals:
            return ToolResponse(success=False, error=f"check_interval must be one of {valid_intervals}")
        
        # Get client from context
        client = track_package_updates.__mcp_client__
        
        # Get current package information
        current_package = await client.get_package(
            platform=platform,
            name=name,
            include_versions=True
        )
        
        # Get package versions
        versions = await client.get_package_versions(platform=platform, name=name)
        
        if not versions:
            return ToolResponse(success=False, error="No versions found for package")
        
        # Sort versions by publication date
        versions.sort(key=lambda v: v.published_at or datetime.min, reverse=True)
        
        latest_version = versions[0]
        current_version = current_package.latest_release_number
        
        # Check for updates
        has_update = latest_version.number != current_version
        is_security_update = False
        
        if has_update and include_security:
            # Simple security check (in real implementation, would check security databases)
            is_security_update = "security" in latest_version.number.lower() or "patch" in latest_version.number.lower()
        
        # Calculate time since last update
        time_since_update = None
        if current_package.latest_release_published_at:
            now = datetime.now(current_package.latest_release_published_at.tzinfo)
            time_since_update = now - current_package.latest_release_published_at
            days_since_update = time_since_update.days
            time_since_update = f"{days_since_update} days ago"
        
        response_data = {
            "package": {
                "name": name,
                "platform": platform,
                "current_version": current_version,
                "latest_version": latest_version.number,
                "description": current_package.description
            },
            "tracking": {
                "check_interval": check_interval,
                "include_security": include_security,
                "has_update": has_update,
                "is_security_update": is_security_update,
                "time_since_update": time_since_update
            },
            "versions": {
                "total_versions": len(versions),
                "latest_published": latest_version.published_at.isoformat() if latest_version.published_at else None,
                "current_published": current_package.latest_release_published_at.isoformat() if current_package.latest_release_published_at else None
            },
            "next_check": _calculate_next_check(check_interval)
        }
        
        # Get rate limit info
        rate_limit = client.get_rate_limit_info()
        rate_limit_info = rate_limit.dict() if rate_limit else None
        
        return ToolResponse(
            success=True,
            data=response_data,
            rate_limit_info=rate_limit_info
        )
        
    except LibrariesIOClientError as e:
        return ToolResponse(success=False, error=str(e))
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


def _calculate_next_check(interval: str) -> str:
    """Calculate next check time based on interval."""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    if interval == "hourly":
        next_check = now + timedelta(hours=1)
    elif interval == "daily":
        next_check = now + timedelta(days=1)
    elif interval == "weekly":
        next_check = now + timedelta(weeks=1)
    else:
        next_check = now + timedelta(days=1)
    
    return next_check.strftime("%Y-%m-%d %H:%M:%S")


@_make_tool
async def generate_dependency_report(
    packages: List[Dict[str, str]],
    include_versions: bool = True,
    include_dependencies: bool = True,
    include_security: bool = True
) -> ToolResponse:
    """
    Generate comprehensive dependency report.
    
    Args:
        packages: List of packages to analyze, each with 'platform' and 'name'
        include_versions: Include version information in report
        include_dependencies: Include dependency information in report
        include_security: Include security information in report
        
    Returns:
        Comprehensive dependency report
    """
    try:
        # Validate parameters
        if not packages:
            return ToolResponse(success=False, error="At least one package must be provided")
        
        if len(packages) > 20:
            return ToolResponse(success=False, error="Maximum 20 packages can be analyzed")
        
        # Get client from context
        client = generate_dependency_report.__mcp_client__
        
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "packages_analyzed": len(packages),
            "packages": []
        }
        
        total_dependencies = 0
        security_issues = []
        unique_languages = set()
        
        for pkg in packages:
            try:
                # Validate package format
                if 'platform' not in pkg or 'name' not in pkg:
                    return ToolResponse(
                        success=False,
                        error=f"Package must have 'platform' and 'name' fields"
                    )
                
                platform = pkg['platform']
                name = pkg['name']
                
                package_report = {
                    "platform": platform,
                    "name": name,
                    "status": "success"
                }
                
                # Get package info
                package_info = await client.get_package(
                    platform=platform,
                    name=name,
                    include_versions=include_versions
                )
                
                # Add basic info
                package_report.update({
                    "description": package_info.description,
                    "language": package_info.language,
                    "stars": package_info.stars,
                    "latest_version": package_info.latest_release_number,
                    "homepage": package_info.homepage,
                    "repository_url": package_info.repository_url
                })
                
                if package_info.language:
                    unique_languages.add(package_info.language)
                
                # Add version info if requested
                if include_versions:
                    versions = await client.get_package_versions(platform=platform, name=name)
                    package_report["versions"] = str({
                        "total": len(versions),
                        "latest": versions[0].number if versions else None,
                        "oldest": versions[-1].number if versions else None
                    })
                
                # Add dependency info if requested
                if include_dependencies:
                    dependencies = await client.get_package_dependencies(platform=platform, name=name)
                    package_report["dependencies"] = str({
                        "total": len(dependencies),
                        "runtime": len([d for d in dependencies if d.kind != "development"]),
                        "development": len([d for d in dependencies if d.kind == "development"])
                    })
                    total_dependencies += len(dependencies)
                
                # Add security info if requested
                if include_security:
                    security_result = await check_package_security(platform, name)
                    if security_result.success:
                        if security_result.data:
                            package_report["security"] = str(security_result.data.get("security_issues", []))
                            security_issues.extend(security_result.data.get("security_issues", []))
                
                report_data["packages"].append(package_report)
                
            except LibrariesIOClientError as e:
                report_data["packages"].append({
                    "platform": pkg.get('platform', 'unknown'),
                    "name": pkg.get('name', 'unknown'),
                    "status": "error",
                    "error": str(e)
                })
        
        # Generate summary
        report_data["summary"] = {
            "total_packages": len(packages),
            "successful_analyses": len([p for p in report_data["packages"] if p.get("status") == "success"]),
            "failed_analyses": len([p for p in report_data["packages"] if p.get("status") == "error"]),
            "total_dependencies": total_dependencies,
            "unique_languages": list(unique_languages),
            "security_issues": len(security_issues),
            "security_score": max(0, 100 - len(security_issues) * 10)  # Simple scoring
        }
        
        # Get rate limit info
        rate_limit = client.get_rate_limit_info()
        rate_limit_info = rate_limit.dict() if rate_limit else None
        
        return ToolResponse(
            success=True,
            data=report_data,
            rate_limit_info=rate_limit_info
        )
        
    except LibrariesIOClientError as e:
        return ToolResponse(success=False, error=str(e))
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


@_make_tool
async def audit_project_dependencies(
    platform: str,
    packages: List[Dict[str, str]],
    check_duplicates: bool = True,
    check_unused: bool = False,
    check_outdated: bool = True
) -> ToolResponse:
    """
    Audit all dependencies in a project.
    
    Args:
        platform: Package manager platform (e.g., 'npm', 'pypi')
        packages: List of packages to audit, each with 'name' and optional 'version'
        check_duplicates: Check for duplicate dependencies
        check_unused: Check for potentially unused dependencies
        check_outdated: Check for outdated packages
        
    Returns:
        Project dependency audit results
    """
    try:
        # Validate parameters
        if not platform.strip():
            return ToolResponse(success=False, error="Platform cannot be empty")
        
        if not packages:
            return ToolResponse(success=False, error="At least one package must be provided")
        
        if len(packages) > 50:
            return ToolResponse(success=False, error="Maximum 50 packages can be audited")
        
        # Get client from context
        client = audit_project_dependencies.__mcp_client__
        
        audit_results = {
            "platform": platform,
            "generated_at": datetime.now().isoformat(),
            "total_packages": len(packages),
            "audits": {
                "duplicates": [],
                "unused": [],
                "outdated": [],
                "security": [],
                "recommendations": []
            },
            "summary": {
                "duplicates_count": 0,
                "unused_count": 0,
                "outdated_count": 0,
                "security_issues_count": 0,
                "recommendations_count": 0
            }
        }
        
        # Track all packages and their versions
        package_registry = {}
        duplicate_packages = {}
        
        for pkg in packages:
            name = pkg.get('name')
            version = pkg.get('version')
            
            if not name:
                continue
            
            # Check for duplicates
            if check_duplicates and name in package_registry:
                if name not in duplicate_packages:
                    duplicate_packages[name] = []
                duplicate_packages[name].append({
                    "first_occurrence": package_registry[name],
                    "duplicate_occurrence": {"version": version}
                })
            
            package_registry[name] = {"version": version, "original": pkg}
        
        # Process duplicates
        if check_duplicates:
            for name, duplicates in duplicate_packages.items():
                audit_results["audits"]["duplicates"].append({
                    "package": name,
                    "duplicates": duplicates,
                    "severity": "high",
                    "recommendation": "Remove duplicate package entries"
                })
                audit_results["summary"]["duplicates_count"] += len(duplicates)
        
        # Check each package for issues
        for name, pkg_info in package_registry.items():
            version = pkg_info["version"]
            original_pkg = pkg_info["original"]
            
            try:
                # Get package info
                package = await client.get_package(
                    platform=platform,
                    name=name,
                    include_versions=True
                )
                
                # Check for outdated packages
                if check_outdated and package.latest_release_number:
                    if version and version != package.latest_release_number:
                        audit_results["audits"]["outdated"].append({
                            "package": name,
                            "current_version": version,
                            "latest_version": package.latest_release_number,
                            "severity": "medium",
                            "recommendation": f"Update to version {package.latest_release_number}"
                        })
                        audit_results["summary"]["outdated_count"] += 1
                
                # Check security
                security_result = await check_package_security(platform, name, version)
                if security_result.success:
                    if security_result.data:
                        security_issues = security_result.data.get("security_issues", [])
                    for issue in security_issues:
                        audit_results["audits"]["security"].append({
                            "package": name,
                            "version": version,
                            "issue": issue,
                            "severity": issue.get("severity", "medium"),
                            "recommendation": issue.get("description", "Review security concerns")
                        })
                        audit_results["summary"]["security_issues_count"] += 1
                
                # Generate recommendations
                if package.stars and package.stars < 10:
                    audit_results["audits"]["recommendations"].append({
                        "package": name,
                        "type": "low_popularity",
                        "severity": "low",
                        "recommendation": f"Consider alternatives - package has only {package.stars} stars"
                    })
                    audit_results["summary"]["recommendations_count"] += 1
                
                if not package.repository_url:
                    audit_results["audits"]["recommendations"].append({
                        "package": name,
                        "type": "no_repository",
                        "severity": "low",
                        "recommendation": "Package has no repository URL - verify source"
                    })
                    audit_results["summary"]["recommendations_count"] += 1
                
            except LibrariesIOClientError as e:
                audit_results["audits"]["recommendations"].append({
                    "package": name,
                    "type": "fetch_error",
                    "severity": "high",
                    "recommendation": f"Could not fetch package information: {str(e)}"
                })
                audit_results["summary"]["recommendations_count"] += 1
        
        # Calculate overall project health score
        total_issues = (
            audit_results["summary"]["duplicates_count"] +
            audit_results["summary"]["outdated_count"] +
            audit_results["summary"]["security_issues_count"]
        )
        
        project_health = max(0, 100 - (total_issues * 10))
        audit_results["project_health_score"] = project_health
        audit_results["health_status"] = _get_health_status(project_health)
        
        # Get rate limit info
        rate_limit = client.get_rate_limit_info()
        rate_limit_info = rate_limit.dict() if rate_limit else None
        
        return ToolResponse(
            success=True,
            data=audit_results,
            rate_limit_info=rate_limit_info
        )
        
    except LibrariesIOClientError as e:
        return ToolResponse(success=False, error=str(e))
    except Exception as e:
        return ToolResponse(success=False, error=f"Unexpected error: {str(e)}")


def _get_health_status(score: int) -> str:
    """Get health status based on score."""
    if score >= 90:
        return "excellent"
    elif score >= 75:
        return "good"
    elif score >= 60:
        return "fair"
    elif score >= 40:
        return "poor"
    else:
        return "critical"


# Tool registration function
def register_tools(server, client: LibrariesIOClient) -> None:
    """
    Register all MCP tools with the server.
    
    Args:
        server: FastMCP server instance
        client: LibrariesIOClient instance
    """
    if not MCP_AVAILABLE:
        return
    
    # Set client reference on all tools
    tools = [
        search_packages, get_trending_packages, get_popular_packages,
        get_package_info, get_package_versions, get_package_dependencies,
        get_package_dependents, compare_packages, check_package_security,
        analyze_dependency_tree, find_alternatives, get_platform_stats,
        check_license_compatibility, track_package_updates,
        generate_dependency_report, audit_project_dependencies
    ]
    
    for tool in tools:
        tool.__mcp_client__ = client
        server.add_tool(tool)


# Export all tools and functions
__all__ = [
    "register_tools",
    "search_packages",
    "get_trending_packages", 
    "get_popular_packages",
    "get_package_info",
    "get_package_versions",
    "get_package_dependencies",
    "get_package_dependents",
    "compare_packages",
    "check_package_security",
    "analyze_dependency_tree",
    "find_alternatives",
    "get_platform_stats",
    "check_license_compatibility",
    "track_package_updates",
    "generate_dependency_report",
    "audit_project_dependencies",
    "ToolResponse",
    # Request/response models
    "SearchPackagesRequest",
    "TrendingPackagesRequest",
    "PopularPackagesRequest",
    "PackageInfoRequest",
    "PackageVersionsRequest",
    "PackageDependenciesRequest",
    "PackageDependentsRequest",
    "ComparePackagesRequest",
    "SecurityCheckRequest",
    "DependencyTreeRequest",
    "FindAlternativesRequest",
    "PlatformStatsRequest",
    "LicenseCompatibilityRequest",
    "TrackUpdatesRequest",
    "DependencyReportRequest",
    "AuditProjectRequest"
]
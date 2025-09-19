"""
Data models for the Libraries.io MCP Server.

This module contains Pydantic models for data validation and serialization.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class Platform(BaseModel):
    """Model for a supported package manager/platform."""
    
    name: str = Field(..., description="Name of the platform/package manager")
    project_count: int = Field(..., description="Number of projects on this platform")
    homepage: str = Field(..., description="Homepage URL for the platform")
    color: str = Field(..., description="Hex color code for the platform")
    default_language: Optional[str] = Field(None, description="Default programming language")
    package_type: Optional[str] = Field(None, description="Type of packages (library, framework, etc.)")


class PackageVersion(BaseModel):
    """Model for a package version."""
    
    number: str = Field(..., description="Version number")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    spdx_expression: Optional[str] = Field(None, description="SPDX license expression")
    original_license: Optional[str] = Field(None, description="Original license string")
    status: Optional[str] = Field(None, description="Version status (active, deprecated, etc.)")


class Package(BaseModel):
    """Model for a package/project."""
    
    name: str = Field(..., description="Package name")
    platform: str = Field(..., description="Platform/package manager")
    description: Optional[str] = Field(None, description="Package description")
    homepage: Optional[str] = Field(None, description="Homepage URL")
    repository_url: Optional[str] = Field(None, description="Repository URL")
    language: Optional[str] = Field(None, description="Primary programming language")
    keywords: List[str] = Field(default_factory=list, description="Package keywords")
    licenses: Optional[str] = Field(None, description="License information")
    latest_release_number: Optional[str] = Field(None, description="Latest version number")
    latest_release_published_at: Optional[datetime] = Field(None, description="Latest version publication date")
    stars: Optional[int] = Field(None, description="Number of stars on repository")
    forks: Optional[int] = Field(None, description="Number of forks")
    dependents_count: int = Field(default=0, description="Number of dependent packages")
    versions: List[PackageVersion] = Field(default_factory=list, description="Available versions")
    status: Optional[str] = Field(None, description="Package status")


class Dependency(BaseModel):
    """Model for a package dependency."""
    
    name: str = Field(..., description="Dependency name")
    platform: str = Field(..., description="Dependency platform")
    requirement: Optional[str] = Field(None, description="Version requirement")
    kind: Optional[str] = Field(None, description="Dependency kind (runtime, development, etc.)")
    optional: bool = Field(default=False, description="Whether dependency is optional")


class Repository(BaseModel):
    """Model for a repository."""
    
    url: str = Field(..., description="Repository URL")
    homepage: Optional[str] = Field(None, description="Homepage URL")
    description: Optional[str] = Field(None, description="Repository description")
    language: Optional[str] = Field(None, description="Primary programming language")
    stars: Optional[int] = Field(None, description="Number of stars")
    forks: Optional[int] = Field(None, description="Number of forks")
    last_commit_at: Optional[datetime] = Field(None, description="Last commit date")
    package_count: Optional[int] = Field(None, description="Number of packages from this repo")


class User(BaseModel):
    """Model for a user."""
    
    username: str = Field(..., description="Username")
    name: Optional[str] = Field(None, description="Display name")
    email: Optional[str] = Field(None, description="Email address")
    company: Optional[str] = Field(None, description="Company")
    location: Optional[str] = Field(None, description="Location")
    blog: Optional[str] = Field(None, description="Blog URL")
    bio: Optional[str] = Field(None, description="Biography")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    followers_count: Optional[int] = Field(None, description="Number of followers")
    following_count: Optional[int] = Field(None, description="Number of following")
    public_gists_count: Optional[int] = Field(None, description="Number of public gists")
    public_repos_count: Optional[int] = Field(None, description="Number of public repositories")


class Organization(BaseModel):
    """Model for an organization."""
    
    login: str = Field(..., description="Organization login")
    name: Optional[str] = Field(None, description="Display name")
    description: Optional[str] = Field(None, description="Organization description")
    company: Optional[str] = Field(None, description="Company")
    location: Optional[str] = Field(None, description="Location")
    blog: Optional[str] = Field(None, description="Blog URL")
    email: Optional[str] = Field(None, description="Email address")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    followers_count: Optional[int] = Field(None, description="Number of followers")
    following_count: Optional[int] = Field(None, description="Number of following")
    public_gists_count: Optional[int] = Field(None, description="Number of public gists")
    public_repos_count: Optional[int] = Field(None, description="Number of public repositories")
    created_at: Optional[datetime] = Field(None, description="Creation date")
    updated_at: Optional[datetime] = Field(None, description="Last update date")


class SearchResult(BaseModel):
    """Model for search results."""
    
    total_count: int = Field(..., description="Total number of results")
    incomplete_results: bool = Field(..., description="Whether results are incomplete")
    items: List[Package] = Field(..., description="Search result items")


class APIError(BaseModel):
    """Model for API errors."""
    
    message: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    documentation_url: Optional[str] = Field(None, description="URL to documentation")
    errors: Optional[List[str]] = Field(None, description="Detailed error list")


class RateLimitInfo(BaseModel):
    """Model for rate limit information."""
    
    limit: int = Field(..., description="Rate limit limit")
    remaining: int = Field(..., description="Rate limit remaining")
    reset: Optional[datetime] = Field(None, description="Rate limit reset time")
    used: int = Field(..., description="Rate limit used")


# Response wrapper models
class PaginatedResponse(BaseModel):
    """Base model for paginated responses."""
    
    total_count: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    items: List[Any] = Field(..., description="Response items")


class PlatformsResponse(BaseModel):
    """Response model for platforms endpoint."""
    
    platforms: List[Platform] = Field(..., description="List of supported platforms")


class PackageResponse(BaseModel):
    """Response model for package endpoint."""
    
    package: Package = Field(..., description="Package information")


class DependenciesResponse(BaseModel):
    """Response model for dependencies endpoint."""
    
    dependencies: List[Dependency] = Field(..., description="List of dependencies")


class DependentsResponse(BaseModel):
    """Response model for dependents endpoint."""
    
    dependents: List[Package] = Field(..., description="List of dependent packages")


class SearchResponse(BaseModel):
    """Response model for search endpoint."""
    
    total_count: int = Field(..., description="Total number of results")
    incomplete_results: bool = Field(..., description="Whether results are incomplete")
    items: List[Package] = Field(..., description="Search result items")


class UserResponse(BaseModel):
    """Response model for user endpoint."""
    
    user: User = Field(..., description="User information")


class OrganizationResponse(BaseModel):
    """Response model for organization endpoint."""
    
    organization: Organization = Field(..., description="Organization information")


class RepositoryResponse(BaseModel):
    """Response model for repository endpoint."""
    
    repository: Repository = Field(..., description="Repository information")


__all__ = [
    "Platform",
    "PackageVersion", 
    "Package",
    "Dependency",
    "Repository",
    "User",
    "Organization",
    "SearchResult",
    "APIError",
    "RateLimitInfo",
    "PaginatedResponse",
    "PlatformsResponse",
    "PackageResponse",
    "DependenciesResponse",
    "DependentsResponse",
    "SearchResponse",
    "UserResponse",
    "OrganizationResponse",
    "RepositoryResponse",
]
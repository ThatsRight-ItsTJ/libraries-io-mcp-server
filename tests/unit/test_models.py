"""
Unit tests for the data models.

This module contains unit tests for the Pydantic models used in the Libraries.io MCP Server.
"""

import pytest
from datetime import datetime, timezone
from typing import List, Optional

from src.libraries_io_mcp.models import (
    Platform, Package, PackageVersion, Dependency, Repository,
    User, Organization, SearchResult, APIError, RateLimitInfo,
    PlatformsResponse, PackageResponse, DependenciesResponse,
    DependentsResponse, SearchResponse, UserResponse, OrganizationResponse,
    RepositoryResponse
)


class TestPlatform:
    """Test suite for Platform model."""

    def test_platform_creation(self):
        """Test Platform model creation."""
        platform = Platform(
            name="npm",
            project_count=2000000,
            homepage="https://www.npmjs.com/",
            color="#cb3837",
            default_language="JavaScript",
            package_type="library"
        )
        
        assert platform.name == "npm"
        assert platform.project_count == 2000000
        assert platform.homepage == "https://www.npmjs.com/"
        assert platform.color == "#cb3837"
        assert platform.default_language == "JavaScript"
        assert platform.package_type == "library"

    def test_platform_optional_fields(self):
        """Test Platform model with optional fields."""
        platform = Platform(
            name="pypi",
            project_count=500000,
            homepage="https://pypi.org/",
            color="#3776ab"
        )
        
        assert platform.name == "pypi"
        assert platform.project_count == 500000
        assert platform.homepage == "https://pypi.org/"
        assert platform.color == "#3776ab"
        assert platform.default_language is None
        assert platform.package_type is None

    def test_platform_invalid_data(self):
        """Test Platform model with invalid data."""
        with pytest.raises(ValueError):
            Platform(
                name="",  # Empty name should fail validation
                project_count=2000000,
                homepage="https://www.npmjs.com/",
                color="#cb3837"
            )

    def test_platform_model_dump(self):
        """Test Platform model serialization."""
        platform = Platform(
            name="npm",
            project_count=2000000,
            homepage="https://www.npmjs.com/",
            color="#cb3837"
        )
        
        data = platform.model_dump()
        
        assert data["name"] == "npm"
        assert data["project_count"] == 2000000
        assert data["homepage"] == "https://www.npmjs.com/"
        assert data["color"] == "#cb3837"


class TestPackageVersion:
    """Test suite for PackageVersion model."""

    def test_package_version_creation(self):
        """Test PackageVersion model creation."""
        version = PackageVersion(
            number="1.0.0",
            published_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            spdx_expression="MIT",
            original_license="MIT",
            status="active"
        )
        
        assert version.number == "1.0.0"
        assert version.published_at == datetime(2023, 1, 1, tzinfo=timezone.utc)
        assert version.spdx_expression == "MIT"
        assert version.original_license == "MIT"
        assert version.status == "active"

    def test_package_version_optional_fields(self):
        """Test PackageVersion model with optional fields."""
        version = PackageVersion(number="1.0.0")
        
        assert version.number == "1.0.0"
        assert version.published_at is None
        assert version.spdx_expression is None
        assert version.original_license is None
        assert version.status is None

    def test_package_version_invalid_version_number(self):
        """Test PackageVersion model with invalid version number."""
        with pytest.raises(ValueError):
            PackageVersion(number="")  # Empty version number should fail validation


class TestPackage:
    """Test suite for Package model."""

    def test_package_creation(self):
        """Test Package model creation."""
        package = Package(
            name="react",
            platform="npm",
            description="A JavaScript library for building user interfaces",
            homepage="https://reactjs.org/",
            repository_url="https://github.com/facebook/react",
            language="JavaScript",
            keywords=["ui", "javascript", "frontend"],
            licenses="MIT",
            latest_release_number="18.2.0",
            latest_release_published_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            stars=200000,
            forks=40000,
            watchers=5000,
            dependent_repositories_count=1000000,
            rank=1
        )
        
        assert package.name == "react"
        assert package.platform == "npm"
        assert package.description == "A JavaScript library for building user interfaces"
        assert package.homepage == "https://reactjs.org/"
        assert package.repository_url == "https://github.com/facebook/react"
        assert package.language == "JavaScript"
        assert package.keywords == ["ui", "javascript", "frontend"]
        assert package.licenses == "MIT"
        assert package.latest_release_number == "18.2.0"
        assert package.latest_release_published_at == datetime(2023, 1, 1, tzinfo=timezone.utc)
        assert package.stars == 200000
        assert package.forks == 40000
        assert package.watchers == 5000
        assert package.dependent_repositories_count == 1000000
        assert package.rank == 1

    def test_package_optional_fields(self):
        """Test Package model with optional fields."""
        package = Package(
            name="test-package",
            platform="npm"
        )
        
        assert package.name == "test-package"
        assert package.platform == "npm"
        assert package.description is None
        assert package.homepage is None
        assert package.repository_url is None
        assert package.language is None
        assert package.keywords == []
        assert package.licenses is None
        assert package.latest_release_number is None
        assert package.latest_release_published_at is None
        assert package.stars is None
        assert package.forks is None
        assert package.watchers is None
        assert package.dependent_repositories_count is None
        assert package.rank is None

    def test_package_invalid_data(self):
        """Test Package model with invalid data."""
        with pytest.raises(ValueError):
            Package(
                name="",  # Empty name should fail validation
                platform="npm"
            )

    def test_package_model_dump(self):
        """Test Package model serialization."""
        package = Package(
            name="react",
            platform="npm",
            description="A JavaScript library for building user interfaces"
        )
        
        data = package.model_dump()
        
        assert data["name"] == "react"
        assert data["platform"] == "npm"
        assert data["description"] == "A JavaScript library for building user interfaces"


class TestDependency:
    """Test suite for Dependency model."""

    def test_dependency_creation(self):
        """Test Dependency model creation."""
        dependency = Dependency(
            project=Package(
                name="react",
                platform="npm",
                description="A JavaScript library for building user interfaces"
            ),
            requirement=">=16.0.0",
            kind="runtime",
            optional=False,
            development=False
        )
        
        assert dependency.project.name == "react"
        assert dependency.project.platform == "npm"
        assert dependency.requirement == ">=16.0.0"
        assert dependency.kind == "runtime"
        assert dependency.optional is False
        assert dependency.development is False

    def test_dependency_optional_fields(self):
        """Test Dependency model with optional fields."""
        dependency = Dependency(
            project=Package(name="test", platform="npm"),
            requirement="1.0.0"
        )
        
        assert dependency.project.name == "test"
        assert dependency.project.platform == "npm"
        assert dependency.requirement == "1.0.0"
        assert dependency.kind is None
        assert dependency.optional is None
        assert dependency.development is None

    def test_dependency_invalid_data(self):
        """Test Dependency model with invalid data."""
        with pytest.raises(ValueError):
            Dependency(
                project=None,  # None project should fail validation
                requirement="1.0.0"
            )


class TestRepository:
    """Test suite for Repository model."""

    def test_repository_creation(self):
        """Test Repository model creation."""
        repository = Repository(
            name="react",
            platform="GitHub",
            url="https://github.com/facebook/react",
            homepage="https://reactjs.org/",
            description="A JavaScript library for building user interfaces",
            language="JavaScript",
            stars=200000,
            forks=40000,
            watchers=5000,
            created_at=datetime(2013, 5, 24, tzinfo=timezone.utc),
            last_activity_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            last_pushed_at=datetime(2023, 1, 1, tzinfo=timezone.utc)
        )
        
        assert repository.name == "react"
        assert repository.platform == "GitHub"
        assert repository.url == "https://github.com/facebook/react"
        assert repository.homepage == "https://reactjs.org/"
        assert repository.description == "A JavaScript library for building user interfaces"
        assert repository.language == "JavaScript"
        assert repository.stars == 200000
        assert repository.forks == 40000
        assert repository.watchers == 5000
        assert repository.created_at == datetime(2013, 5, 24, tzinfo=timezone.utc)
        assert repository.last_activity_at == datetime(2023, 1, 1, tzinfo=timezone.utc)
        assert repository.last_pushed_at == datetime(2023, 1, 1, tzinfo=timezone.utc)

    def test_repository_optional_fields(self):
        """Test Repository model with optional fields."""
        repository = Repository(
            name="test-repo",
            platform="GitHub",
            url="https://github.com/test/repo"
        )
        
        assert repository.name == "test-repo"
        assert repository.platform == "GitHub"
        assert repository.url == "https://github.com/test/repo"
        assert repository.homepage is None
        assert repository.description is None
        assert repository.language is None
        assert repository.stars is None
        assert repository.forks is None
        assert repository.watchers is None
        assert repository.created_at is None
        assert repository.last_activity_at is None
        assert repository.last_pushed_at is None

    def test_repository_invalid_data(self):
        """Test Repository model with invalid data."""
        with pytest.raises(ValueError):
            Repository(
                name="",  # Empty name should fail validation
                platform="GitHub",
                url="https://github.com/test/repo"
            )


class TestUser:
    """Test suite for User model."""

    def test_user_creation(self):
        """Test User model creation."""
        user = User(
            username="octocat",
            name="The Octocat",
            type="User",
            company="GitHub",
            location="San Francisco",
            email="octocat@github.com",
            hireable=False,
            blog="https://github.blog",
            public_repos=8,
            public_gists=8,
            followers=9224,
            following=9,
            created_at=datetime(2011, 1, 25, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 1, tzinfo=timezone.utc)
        )
        
        assert user.username == "octocat"
        assert user.name == "The Octocat"
        assert user.type == "User"
        assert user.company == "GitHub"
        assert user.location == "San Francisco"
        assert user.email == "octocat@github.com"
        assert user.hireable is False
        assert user.blog == "https://github.blog"
        assert user.public_repos == 8
        assert user.public_gists == 8
        assert user.followers == 9224
        assert user.following == 9
        assert user.created_at == datetime(2011, 1, 25, tzinfo=timezone.utc)
        assert user.updated_at == datetime(2023, 1, 1, tzinfo=timezone.utc)

    def test_user_optional_fields(self):
        """Test User model with optional fields."""
        user = User(
            username="testuser",
            name="Test User",
            type="User"
        )
        
        assert user.username == "testuser"
        assert user.name == "Test User"
        assert user.type == "User"
        assert user.company is None
        assert user.location is None
        assert user.email is None
        assert user.hireable is None
        assert user.blog is None
        assert user.public_repos is None
        assert user.public_gists is None
        assert user.followers is None
        assert user.following is None
        assert user.created_at is None
        assert user.updated_at is None

    def test_user_invalid_data(self):
        """Test User model with invalid data."""
        with pytest.raises(ValueError):
            User(
                username="",  # Empty username should fail validation
                name="Test User",
                type="User"
            )


class TestOrganization:
    """Test suite for Organization model."""

    def test_organization_creation(self):
        """Test Organization model creation."""
        organization = Organization(
            name="github",
            type="Organization",
            company="GitHub",
            location="San Francisco",
            email="support@github.com",
            hireable=False,
            blog="https://github.blog",
            public_repos=100,
            public_gists=0,
            followers=0,
            following=0,
            created_at=datetime(2008, 2, 8, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 1, tzinfo=timezone.utc)
        )
        
        assert organization.name == "github"
        assert organization.type == "Organization"
        assert organization.company == "GitHub"
        assert organization.location == "San Francisco"
        assert organization.email == "support@github.com"
        assert organization.hireable is False
        assert organization.blog == "https://github.blog"
        assert organization.public_repos == 100
        assert organization.public_gists == 0
        assert organization.followers == 0
        assert organization.following == 0
        assert organization.created_at == datetime(2008, 2, 8, tzinfo=timezone.utc)
        assert organization.updated_at == datetime(2023, 1, 1, tzinfo=timezone.utc)

    def test_organization_optional_fields(self):
        """Test Organization model with optional fields."""
        organization = Organization(
            name="test-org",
            type="Organization"
        )
        
        assert organization.name == "test-org"
        assert organization.type == "Organization"
        assert organization.company is None
        assert organization.location is None
        assert organization.email is None
        assert organization.hireable is None
        assert organization.blog is None
        assert organization.public_repos is None
        assert organization.public_gists is None
        assert organization.followers is None
        assert organization.following is None
        assert organization.created_at is None
        assert organization.updated_at is None

    def test_organization_invalid_data(self):
        """Test Organization model with invalid data."""
        with pytest.raises(ValueError):
            Organization(
                name="",  # Empty name should fail validation
                type="Organization"
            )


class TestSearchResult:
    """Test suite for SearchResult model."""

    def test_search_result_creation(self):
        """Test SearchResult model creation."""
        search_result = SearchResult(
            total_count=100,
            packages=[
                Package(
                    name="react",
                    platform="npm",
                    description="A JavaScript library for building user interfaces"
                ),
                Package(
                    name="vue",
                    platform="npm",
                    description="The Progressive JavaScript Framework"
                )
            ]
        )
        
        assert search_result.total_count == 100
        assert len(search_result.packages) == 2
        assert search_result.packages[0].name == "react"
        assert search_result.packages[1].name == "vue"

    def test_search_result_empty_packages(self):
        """Test SearchResult model with empty packages list."""
        search_result = SearchResult(
            total_count=0,
            packages=[]
        )
        
        assert search_result.total_count == 0
        assert search_result.packages == []

    def test_search_result_invalid_data(self):
        """Test SearchResult model with invalid data."""
        with pytest.raises(ValueError):
            SearchResult(
                total_count=-1,  # Negative total count should fail validation
                packages=[]
            )


class TestAPIError:
    """Test suite for APIError model."""

    def test_api_error_creation(self):
        """Test APIError model creation."""
        error = APIError(
            message="Invalid API key",
            documentation_url="https://docs.libraries.io/api/errors/invalid-api-key"
        )
        
        assert error.message == "Invalid API key"
        assert error.documentation_url == "https://docs.libraries.io/api/errors/invalid-api-key"

    def test_api_error_optional_fields(self):
        """Test APIError model with optional fields."""
        error = APIError(message="Test error")
        
        assert error.message == "Test error"
        assert error.documentation_url is None

    def test_api_error_invalid_data(self):
        """Test APIError model with invalid data."""
        with pytest.raises(ValueError):
            APIError(
                message="",  # Empty message should fail validation
                documentation_url="https://docs.libraries.io/api/errors/invalid-api-key"
            )


class TestRateLimitInfo:
    """Test suite for RateLimitInfo model."""

    def test_rate_limit_info_creation(self):
        """Test RateLimitInfo model creation."""
        rate_limit = RateLimitInfo(
            limit=100,
            remaining=50,
            reset=1640995200.0,
            used=50
        )
        
        assert rate_limit.limit == 100
        assert rate_limit.remaining == 50
        assert rate_limit.reset == 1640995200.0
        assert rate_limit.used == 50

    def test_rate_limit_info_negative_values(self):
        """Test RateLimitInfo model with negative values."""
        rate_limit = RateLimitInfo(
            limit=100,
            remaining=-1,  # Negative remaining should be allowed
            reset=1640995200.0,
            used=101  # Used > limit should be allowed
        )
        
        assert rate_limit.limit == 100
        assert rate_limit.remaining == -1
        assert rate_limit.reset == 1640995200.0
        assert rate_limit.used == 101

    def test_rate_limit_info_model_dump(self):
        """Test RateLimitInfo model serialization."""
        rate_limit = RateLimitInfo(
            limit=100,
            remaining=50,
            reset=1640995200.0,
            used=50
        )
        
        data = rate_limit.model_dump()
        
        assert data["limit"] == 100
        assert data["remaining"] == 50
        assert data["reset"] == 1640995200.0
        assert data["used"] == 50


class TestResponseModels:
    """Test suite for response wrapper models."""

    def test_platforms_response(self):
        """Test PlatformsResponse model."""
        platforms = [
            Platform(name="npm", project_count=2000000, homepage="https://www.npmjs.com/", color="#cb3837"),
            Platform(name="pypi", project_count=500000, homepage="https://pypi.org/", color="#3776ab")
        ]
        
        response = PlatformsResponse(platforms=platforms)
        
        assert len(response.platforms) == 2
        assert response.platforms[0].name == "npm"
        assert response.platforms[1].name == "pypi"

    def test_package_response(self):
        """Test PackageResponse model."""
        package = Package(
            name="react",
            platform="npm",
            description="A JavaScript library for building user interfaces"
        )
        
        response = PackageResponse(package=package)
        
        assert response.package.name == "react"
        assert response.package.platform == "npm"

    def test_dependencies_response(self):
        """Test DependenciesResponse model."""
        dependencies = [
            Dependency(
                project=Package(name="react", platform="npm"),
                requirement=">=16.0.0"
            ),
            Dependency(
                project=Package(name="redux", platform="npm"),
                requirement=">=4.0.0"
            )
        ]
        
        response = DependenciesResponse(dependencies=dependencies)
        
        assert len(response.dependencies) == 2
        assert response.dependencies[0].project.name == "react"
        assert response.dependencies[1].project.name == "redux"

    def test_dependents_response(self):
        """Test DependentsResponse model."""
        dependents = [
            Package(name="my-app", platform="npm"),
            Package(name="another-app", platform="npm")
        ]
        
        response = DependentsResponse(dependents=dependents)
        
        assert len(response.dependents) == 2
        assert response.dependents[0].name == "my-app"
        assert response.dependents[1].name == "another-app"

    def test_search_response(self):
        """Test SearchResponse model."""
        packages = [
            Package(name="react", platform="npm"),
            Package(name="vue", platform="npm")
        ]
        
        response = SearchResponse(
            total_count=100,
            packages=packages
        )
        
        assert response.total_count == 100
        assert len(response.packages) == 2
        assert response.packages[0].name == "react"
        assert response.packages[1].name == "vue"

    def test_user_response(self):
        """Test UserResponse model."""
        user = User(
            username="octocat",
            name="The Octocat",
            type="User"
        )
        
        response = UserResponse(user=user)
        
        assert response.user.username == "octocat"
        assert response.user.name == "The Octocat"

    def test_organization_response(self):
        """Test OrganizationResponse model."""
        organization = Organization(
            name="github",
            type="Organization"
        )
        
        response = OrganizationResponse(organization=organization)
        
        assert response.organization.name == "github"
        assert response.organization.type == "Organization"

    def test_repository_response(self):
        """Test RepositoryResponse model."""
        repository = Repository(
            name="react",
            platform="GitHub",
            url="https://github.com/facebook/react"
        )
        
        response = RepositoryResponse(repository=repository)
        
        assert response.repository.name == "react"
        assert response.repository.platform == "GitHub"


class TestModelValidation:
    """Test suite for model validation."""

    def test_platform_validation(self):
        """Test Platform model validation."""
        # Valid platform
        platform = Platform(
            name="npm",
            project_count=2000000,
            homepage="https://www.npmjs.com/",
            color="#cb3837"
        )
        assert platform.model_validate(platform.model_dump()) == platform
        
        # Invalid platform - negative project count
        with pytest.raises(ValueError):
            Platform(
                name="npm",
                project_count=-1,
                homepage="https://www.npmjs.com/",
                color="#cb3837"
            )

    def test_package_validation(self):
        """Test Package model validation."""
        # Valid package
        package = Package(
            name="react",
            platform="npm",
            description="A JavaScript library for building user interfaces"
        )
        assert package.model_validate(package.model_dump()) == package
        
        # Invalid package - empty name
        with pytest.raises(ValueError):
            Package(
                name="",
                platform="npm"
            )

    def test_dependency_validation(self):
        """Test Dependency model validation."""
        # Valid dependency
        dependency = Dependency(
            project=Package(name="react", platform="npm"),
            requirement=">=16.0.0"
        )
        assert dependency.model_validate(dependency.model_dump()) == dependency
        
        # Invalid dependency - None project
        with pytest.raises(ValueError):
            Dependency(
                project=None,
                requirement=">=16.0.0"
            )

    def test_repository_validation(self):
        """Test Repository model validation."""
        # Valid repository
        repository = Repository(
            name="react",
            platform="GitHub",
            url="https://github.com/facebook/react"
        )
        assert repository.model_validate(repository.model_dump()) == repository
        
        # Invalid repository - empty name
        with pytest.raises(ValueError):
            Repository(
                name="",
                platform="GitHub",
                url="https://github.com/facebook/react"
            )

    def test_user_validation(self):
        """Test User model validation."""
        # Valid user
        user = User(
            username="octocat",
            name="The Octocat",
            type="User"
        )
        assert user.model_validate(user.model_dump()) == user
        
        # Invalid user - empty username
        with pytest.raises(ValueError):
            User(
                username="",
                name="The Octocat",
                type="User"
            )

    def test_organization_validation(self):
        """Test Organization model validation."""
        # Valid organization
        organization = Organization(
            name="github",
            type="Organization"
        )
        assert organization.model_validate(organization.model_dump()) == organization
        
        # Invalid organization - empty name
        with pytest.raises(ValueError):
            Organization(
                name="",
                type="Organization"
            )

    def test_search_result_validation(self):
        """Test SearchResult model validation."""
        # Valid search result
        search_result = SearchResult(
            total_count=100,
            packages=[
                Package(name="react", platform="npm"),
                Package(name="vue", platform="npm")
            ]
        )
        assert search_result.model_validate(search_result.model_dump()) == search_result
        
        # Invalid search result - negative total count
        with pytest.raises(ValueError):
            SearchResult(
                total_count=-1,
                packages=[]
            )

    def test_api_error_validation(self):
        """Test APIError model validation."""
        # Valid API error
        error = APIError(message="Test error")
        assert error.model_validate(error.model_dump()) == error
        
        # Invalid API error - empty message
        with pytest.raises(ValueError):
            APIError(message="")

    def test_rate_limit_info_validation(self):
        """Test RateLimitInfo model validation."""
        # Valid rate limit info
        rate_limit = RateLimitInfo(
            limit=100,
            remaining=50,
            reset=1640995200.0,
            used=50
        )
        assert rate_limit.model_validate(rate_limit.model_dump()) == rate_limit


class TestModelSerialization:
    """Test suite for model serialization."""

    def test_platform_serialization(self):
        """Test Platform model serialization."""
        platform = Platform(
            name="npm",
            project_count=2000000,
            homepage="https://www.npmjs.com/",
            color="#cb3837"
        )
        
        # Test model_dump
        data = platform.model_dump()
        assert data["name"] == "npm"
        assert data["project_count"] == 2000000
        
        # Test model_dump_json
        json_data = platform.model_dump_json()
        assert "npm" in json_data
        assert "2000000" in json_data
        
        # Test model_dump with exclude
        data_excluded = platform.model_dump(exclude={"project_count"})
        assert "project_count" not in data_excluded

    def test_package_serialization(self):
        """Test Package model serialization."""
        package = Package(
            name="react",
            platform="npm",
            description="A JavaScript library for building user interfaces",
            keywords=["ui", "javascript", "frontend"]
        )
        
        # Test model_dump
        data = package.model_dump()
        assert data["name"] == "react"
        assert data["platform"] == "npm"
        assert data["description"] == "A JavaScript library for building user interfaces"
        assert data["keywords"] == ["ui", "javascript", "frontend"]
        
        # Test model_dump with include
        data_included = package.model_dump(include={"name", "platform"})
        assert "name" in data_included
        assert "platform" in data_included
        assert "description" not in data_included

    def test_dependency_serialization(self):
        """Test Dependency model serialization."""
        dependency = Dependency(
            project=Package(name="react", platform="npm"),
            requirement=">=16.0.0"
        )
        
        # Test model_dump
        data = dependency.model_dump()
        assert data["project"]["name"] == "react"
        assert data["project"]["platform"] == "npm"
        assert data["requirement"] == ">=16.0.0"

    def test_repository_serialization(self):
        """Test Repository model serialization."""
        repository = Repository(
            name="react",
            platform="GitHub",
            url="https://github.com/facebook/react",
            stars=200000
        )
        
        # Test model_dump
        data = repository.model_dump()
        assert data["name"] == "react"
        assert data["platform"] == "GitHub"
        assert data["url"] == "https://github.com/facebook/react"
        assert data["stars"] == 200000

    def test_user_serialization(self):
        """Test User model serialization."""
        user = User(
            username="octocat",
            name="The Octocat",
            type="User",
            followers=9224
        )
        
        # Test model_dump
        data = user.model_dump()
        assert data["username"] == "octocat"
        assert data["name"] == "The Octocat"
        assert data["type"] == "User"
        assert data["followers"] == 9224

    def test_organization_serialization(self):
        """Test Organization model serialization."""
        organization = Organization(
            name="github",
            type="Organization",
            public_repos=100
        )
        
        # Test model_dump
        data = organization.model_dump()
        assert data["name"] == "github"
        assert data["type"] == "Organization"
        assert data["public_repos"] == 100

    def test_search_result_serialization(self):
        """Test SearchResult model serialization."""
        search_result = SearchResult(
            total_count=100,
            packages=[
                Package(name="react", platform="npm"),
                Package(name="vue", platform="npm")
            ]
        )
        
        # Test model_dump
        data = search_result.model_dump()
        assert data["total_count"] == 100
        assert len(data["packages"]) == 2
        assert data["packages"][0]["name"] == "react"
        assert data["packages"][1]["name"] == "vue"

    def test_api_error_serialization(self):
        """Test APIError model serialization."""
        error = APIError(
            message="Invalid API key",
            documentation_url="https://docs.libraries.io/api/errors/invalid-api-key"
        )
        
        # Test model_dump
        data = error.model_dump()
        assert data["message"] == "Invalid API key"
        assert data["documentation_url"] == "https://docs.libraries.io/api/errors/invalid-api-key"

    def test_rate_limit_info_serialization(self):
        """Test RateLimitInfo model serialization."""
        rate_limit = RateLimitInfo(
            limit=100,
            remaining=50,
            reset=1640995200.0,
            used=50
        )
        
        # Test model_dump
        data = rate_limit.model_dump()
        assert data["limit"] == 100
        assert data["remaining"] == 50
        assert data["reset"] == 1640995200.0
        assert data["used"] == 50


class TestModelInheritance:
    """Test suite for model inheritance and relationships."""

    def test_package_in_dependency(self):
        """Test Package model used in Dependency."""
        package = Package(
            name="react",
            platform="npm",
            description="A JavaScript library for building user interfaces"
        )
        
        dependency = Dependency(
            project=package,
            requirement=">=16.0.0"
        )
        
        assert dependency.project.name == "react"
        assert dependency.project.platform == "npm"
        assert dependency.project.description == "A JavaScript library for building user interfaces"

    def test_package_in_search_result(self):
        """Test Package model used in SearchResult."""
        packages = [
            Package(name="react", platform="npm"),
            Package(name="vue", platform="npm"),
            Package(name="angular", platform="npm")
        ]
        
        search_result = SearchResult(
            total_count=100,
            packages=packages
        )
        
        assert search_result.total_count == 100
        assert len(search_result.packages) == 3
        assert all(isinstance(pkg, Package) for pkg in search_result.packages)
        assert search_result.packages[0].name == "react"
        assert search_result.packages[1].name == "vue"
        assert search_result.packages[2].name == "angular"

    def test_platform_in_package(self):
        """Test Platform model referenced in Package."""
        # This test ensures that the Platform model can be referenced
        # even though it's not directly used in the Package model
        platform = Platform(
            name="npm",
            project_count=2000000,
            homepage="https://www.npmjs.com/",
            color="#cb3837"
        )
        
        package = Package(
            name="react",
            platform="npm",  # String reference to platform
            description="A JavaScript library for building user interfaces"
        )
        
        assert package.platform == "npm"
        assert platform.name == "npm"


class TestModelPerformance:
    """Test suite for model performance."""

    def test_large_list_serialization(self):
        """Test serialization of large lists."""
        # Create a large list of packages
        packages = [
            Package(
                name=f"package-{i}",
                platform="npm",
                description=f"Test package {i}"
            )
            for i in range(1000)
        ]
        
        search_result = SearchResult(
            total_count=10000,
            packages=packages
        )
        
        # Test serialization performance
        import time
        start_time = time.time()
        
        data = search_result.model_dump()
        
        end_time = time.time()
        serialization_time = end_time - start_time
        
        # Verify data integrity
        assert len(data["packages"]) == 1000
        assert data["packages"][0]["name"] == "package-0"
        assert data["packages"][-1]["name"] == "package-999"
        assert data["total_count"] == 10000
        
        # Serialization should be fast (less than 1 second for 1000 items)
        assert serialization_time < 1.0

    def test_deep_nesting_serialization(self):
        """Test serialization of deeply nested models."""
        # Create a deeply nested structure
        package = Package(
            name="react",
            platform="npm",
            description="A JavaScript library for building user interfaces"
        )
        
        dependency = Dependency(
            project=package,
            requirement=">=16.0.0"
        )
        
        dependencies = [dependency]
        dependencies_response = DependenciesResponse(dependencies=dependencies)
        
        # Test serialization
        data = dependencies_response.model_dump()
        
        # Verify deep nesting is preserved
        assert data["dependencies"][0]["project"]["name"] == "react"
        assert data["dependencies"][0]["project"]["platform"] == "npm"
        assert data["dependencies"][0]["project"]["description"] == "A JavaScript library for building user interfaces"
        assert data["dependencies"][0]["requirement"] == ">=16.0.0"


class TestModelEdgeCases:
    """Test suite for model edge cases."""

    def test_package_with_special_characters(self):
        """Test Package model with special characters."""
        package = Package(
            name="package-with-special-chars_123",
            platform="npm",
            description="Package with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            keywords=["special", "chars", "test!"]
        )
        
        data = package.model_dump()
        
        assert data["name"] == "package-with-special-chars_123"
        assert "special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?" in data["description"]
        assert data["keywords"] == ["special", "chars", "test!"]

    def test_package_with_unicode(self):
        """Test Package model with Unicode characters."""
        package = Package(
            name="package-中文",
            platform="npm",
            description="Package with Chinese characters: 中文测试",
            keywords=["中文", "测试"]
        )
        
        data = package.model_dump()
        
        assert data["name"] == "package-中文"
        assert "中文测试" in data["description"]
        assert data["keywords"] == ["中文", "测试"]

    def test_package_with_long_strings(self):
        """Test Package model with very long strings."""
        long_description = "A" * 10000  # 10KB string
        long_name = "package-" + "a" * 1000  # 1KB name
        
        package = Package(
            name=long_name,
            platform="npm",
            description=long_description
        )
        
        data = package.model_dump()
        
        assert data["name"] == long_name
        assert data["description"] == long_description
        assert len(data["description"]) == 10000

    def test_package_with_empty_lists(self):
        """Test Package model with empty lists."""
        package = Package(
            name="test-package",
            platform="npm",
            keywords=[]  # Empty keywords list
        )
        
        data = package.model_dump()
        
        assert data["keywords"] == []

    def test_package_with_none_values(self):
        """Test Package model with None values."""
        package = Package(
            name="test-package",
            platform="npm",
            description=None,
            homepage=None,
            repository_url=None,
            language=None,
            licenses=None,
            latest_release_number=None,
            latest_release_published_at=None,
            stars=None,
            forks=None,
            watchers=None,
            dependent_repositories_count=None,
            rank=None
        )
        
        data = package.model_dump()
        
        assert data["description"] is None
        assert data["homepage"] is None
        assert data["repository_url"] is None
        assert data["language"] is None
        assert data["licenses"] is None
        assert data["latest_release_number"] is None
        assert data["latest_release_published_at"] is None
        assert data["stars"] is None
        assert data["forks"] is None
        assert data["watchers"] is None
        assert data["dependent_repositories_count"] is None
        assert data["rank"] is None

    def test_package_with_zero_values(self):
        """Test Package model with zero values."""
        package = Package(
            name="test-package",
            platform="npm",
            stars=0,
            forks=0,
            watchers=0,
            dependent_repositories_count=0,
            rank=0
        )
        
        data = package.model_dump()
        
        assert data["stars"] == 0
        assert data["forks"] == 0
        assert data["watchers"] == 0
        assert data["dependent_repositories_count"] == 0
        assert data["rank"] == 0

    def test_package_with_boolean_values(self):
        """Test Package model with boolean values."""
        # Note: Package model doesn't have boolean fields, but we test
        # that boolean values in related models work correctly
        
        user = User(
            username="testuser",
            name="Test User",
            type="User",
            hireable=True
        )
        
        data = user.model_dump()
        
        assert data["hireable"] is True

    def test_package_with_datetime_values(self):
        """Test Package model with datetime values."""
        test_datetime = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        package = Package(
            name="test-package",
            platform="npm",
            latest_release_published_at=test_datetime
        )
        
        data = package.model_dump()
        
        assert data["latest_release_published_at"] == test_datetime.isoformat()

    def test_package_with_future_datetime(self):
        """Test Package model with future datetime values."""
        future_datetime = datetime(2050, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        package = Package(
            name="test-package",
            platform="npm",
            latest_release_published_at=future_datetime
        )
        
        data = package.model_dump()
        
        assert data["latest_release_published_at"] == future_datetime.isoformat()

    def test_package_with_past_datetime(self):
        """Test Package model with past datetime values."""
        past_datetime = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        package = Package(
            name="test-package",
            platform="npm",
            latest_release_published_at=past_datetime
        )
        
        data = package.model_dump()
        
        assert data["latest_release_published_at"] == past_datetime.isoformat()
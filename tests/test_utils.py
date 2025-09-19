
"""
Test utilities and helper functions for the Libraries.io MCP Server tests.

This module provides utility functions, mock data generators, and assertion helpers
for testing the Libraries.io MCP Server components.
"""

import json
import random
import string
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch
import asyncio

from src.libraries_io_mcp.models import (
    Platform, Package, PackageVersion, Dependency, Repository,
    User, Organization, SearchResult, RateLimitInfo
)
from src.libraries_io_mcp.utils import RateLimiter, MemoryCache, RetryHandler


class MockDataGenerator:
    """Mock data generator for testing purposes."""
    
    @staticmethod
    def random_string(length: int = 10) -> str:
        """Generate a random string."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def random_int(min_val: int = 1, max_val: int = 1000) -> int:
        """Generate a random integer."""
        return random.randint(min_val, max_val)
    
    @staticmethod
    def random_float(min_val: float = 0.0, max_val: float = 100.0) -> float:
        """Generate a random float."""
        return random.uniform(min_val, max_val)
    
    @staticmethod
    def random_bool() -> bool:
        """Generate a random boolean."""
        return random.choice([True, False])
    
    @staticmethod
    def random_date(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> datetime:
        """Generate a random datetime."""
        if start_date is None:
            start_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        if end_date is None:
            end_date = datetime.now(timezone.utc)
        
        start_timestamp = start_date.timestamp()
        end_timestamp = end_date.timestamp()
        
        random_timestamp = random.uniform(start_timestamp, end_timestamp)
        return datetime.fromtimestamp(random_timestamp, tz=timezone.utc)
    
    @staticmethod
    def random_list(items: List[Any], min_length: int = 1, max_length: int = 10) -> List[Any]:
        """Generate a random list from given items."""
        length = random.randint(min_length, max_length)
        return [random.choice(items) for _ in range(length)]
    
    @staticmethod
    def random_dict(keys: List[str], value_generator: Optional[Callable] = None) -> Dict[str, Any]:
        """Generate a random dictionary."""
        if value_generator is None:
            value_generator = MockDataGenerator.random_string
        
        return {key: value_generator() for key in keys}
    
    @staticmethod
    def generate_platform_data() -> Dict[str, Any]:
        """Generate random platform data."""
        return {
            "name": random.choice(["npm", "pypi", "maven", "gem", "nuget", "docker", "hex", "cran"]),
            "project_count": MockDataGenerator.random_int(1000, 1000000),
            "homepage": f"https://www.{MockDataGenerator.random_string(8)}.com/",
            "color": f"#{''.join(random.choices('0123456789abcdef', k=6))}",
            "default_language": random.choice(["JavaScript", "Python", "Java", "Ruby", "C#", "Go", "Rust"]),
            "package_type": random.choice(["library", "framework", "tool", "application"])
        }
    
    @staticmethod
    def generate_platform() -> Platform:
        """Generate a random Platform instance."""
        return Platform(**MockDataGenerator.generate_platform_data())
    
    @staticmethod
    def generate_package_data() -> Dict[str, Any]:
        """Generate random package data."""
        return {
            "name": MockDataGenerator.random_string(10),
            "platform": random.choice(["npm", "pypi", "maven", "gem", "nuget"]),
            "description": MockDataGenerator.random_string(50),
            "homepage": f"https://www.{MockDataGenerator.random_string(8)}.com/",
            "repository_url": f"https://github.com/{MockDataGenerator.random_string(8)}/{MockDataGenerator.random_string(8)}",
            "language": random.choice(["JavaScript", "Python", "Java", "Ruby", "C#", "Go", "Rust"]),
            "keywords": MockDataGenerator.random_list([MockDataGenerator.random_string(8)], 1, 5),
            "licenses": random.choice(["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "ISC"]),
            "latest_release_number": f"{MockDataGenerator.random_int(1, 20)}.{MockDataGenerator.random_int(0, 20)}.{MockDataGenerator.random_int(0, 20)}",
            "latest_release_published_at": MockDataGenerator.random_date().isoformat(),
            "stars": MockDataGenerator.random_int(0, 1000000),
            "forks": MockDataGenerator.random_int(0, 100000),
            "dependents_count": MockDataGenerator.random_int(0, 100000),
            "status": random.choice(["active", "deprecated", "archived"])
        }
    
    @staticmethod
    def generate_package() -> Package:
        """Generate a random Package instance."""
        return Package(**MockDataGenerator.generate_package_data())
    
    @staticmethod
    def generate_package_version_data() -> Dict[str, Any]:
        """Generate random package version data."""
        return {
            "number": f"{MockDataGenerator.random_int(1, 20)}.{MockDataGenerator.random_int(0, 20)}.{MockDataGenerator.random_int(0, 20)}",
            "published_at": MockDataGenerator.random_date().isoformat(),
            "spdx_expression": random.choice(["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "ISC"]),
            "original_license": random.choice(["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "ISC"]),
            "status": random.choice(["active", "deprecated", "yanked"])
        }
    
    @staticmethod
    def generate_package_version() -> PackageVersion:
        """Generate a random PackageVersion instance."""
        return PackageVersion(**MockDataGenerator.generate_package_version_data())
    
    @staticmethod
    def generate_dependency_data() -> Dict[str, Any]:
        """Generate random dependency data."""
        return {
            "name": MockDataGenerator.random_string(10),
            "platform": random.choice(["npm", "pypi", "maven", "gem", "nuget"]),
            "requirement": f">={MockDataGenerator.random_int(1, 20)}.{MockDataGenerator.random_int(0, 20)}.{MockDataGenerator.random_int(0, 20)}",
            "kind": random.choice(["runtime", "development", "optional", "peer"]),
            "optional": MockDataGenerator.random_bool()
        }
    
    @staticmethod
    def generate_dependency() -> Dependency:
        """Generate a random Dependency instance."""
        return Dependency(**MockDataGenerator.generate_dependency_data())
    
    @staticmethod
    def generate_repository_data() -> Dict[str, Any]:
        """Generate random repository data."""
        return {
            "url": f"https://github.com/{MockDataGenerator.random_string(8)}/{MockDataGenerator.random_string(8)}",
            "homepage": f"https://www.{MockDataGenerator.random_string(8)}.com/",
            "description": MockDataGenerator.random_string(100),
            "language": random.choice(["JavaScript", "Python", "Java", "Ruby", "C#", "Go", "Rust"]),
            "stars": MockDataGenerator.random_int(0, 1000000),
            "forks": MockDataGenerator.random_int(0, 100000),
            "last_commit_at": MockDataGenerator.random_date().isoformat(),
            "package_count": MockDataGenerator.random_int(1, 100)
        }
    
    @staticmethod
    def generate_repository() -> Repository:
        """Generate a random Repository instance."""
        return Repository(**MockDataGenerator.generate_repository_data())
    
    @staticmethod
    def generate_user_data() -> Dict[str, Any]:
        """Generate random user data."""
        return {
            "username": MockDataGenerator.random_string(8),
            "name": MockDataGenerator.random_string(20),
            "email": f"{MockDataGenerator.random_string(8)}@example.com",
            "company": MockDataGenerator.random_string(15),
            "location": MockDataGenerator.random_string(20),
            "blog": f"https://www.{MockDataGenerator.random_string(8)}.com/",
            "bio": MockDataGenerator.random_string(100),
            "avatar_url": f"https://github.com/images/error/{MockDataGenerator.random_string(8)}.gif",
            "followers_count": MockDataGenerator.random_int(0, 10000),
            "following_count": MockDataGenerator.random_int(0, 10000),
            "public_gists_count": MockDataGenerator.random_int(0, 1000),
            "public_repos_count": MockDataGenerator.random_int(0, 1000)
        }
    
    @staticmethod
    def generate_user() -> User:
        """Generate a random User instance."""
        return User(**MockDataGenerator.generate_user_data())
    
    @staticmethod
    def generate_organization_data() -> Dict[str, Any]:
        """Generate random organization data."""
        return {
            "login": MockDataGenerator.random_string(8),
            "name": MockDataGenerator.random_string(20),
            "description": MockDataGenerator.random_string(100),
            "company": MockDataGenerator.random_string(15),
            "location": MockDataGenerator.random_string(20),
            "blog": f"https://www.{MockDataGenerator.random_string(8)}.com/",
            "email": f"{MockDataGenerator.random_string(8)}@example.com",
            "avatar_url": f"https://github.com/images/error/{MockDataGenerator.random_string(8)}_200x200.jpg",
            "followers_count": MockDataGenerator.random_int(0, 50000),
            "following_count": MockDataGenerator.random_int(0, 1000),
            "public_gists_count": MockDataGenerator.random_int(0, 100),
            "public_repos_count": MockDataGenerator.random_int(0, 1000),
            "created_at": MockDataGenerator.random_date().isoformat(),
            "updated_at": MockDataGenerator.random_date().isoformat()
        }
    
    @staticmethod
    def generate_organization() -> Organization:
        """Generate a random Organization instance."""
        return Organization(**MockDataGenerator.generate_organization_data())
    
    @staticmethod
    def generate_search_result_data() -> Dict[str, Any]:
        """Generate random search result data."""
        return {
            "total_count": MockDataGenerator.random_int(1, 10000),
            "incomplete_results": MockDataGenerator.random_bool(),
            "items": [MockDataGenerator.generate_package_data() for _ in range(MockDataGenerator.random_int(1, 10))]
        }
    
    @staticmethod
    def generate_search_result() -> SearchResult:
        """Generate a random SearchResult instance."""
        return SearchResult(**MockDataGenerator.generate_search_result_data())
    
    @staticmethod
    def generate_rate_limit_info() -> RateLimitInfo:
        """Generate a random RateLimitInfo instance."""
        return RateLimitInfo(
            limit=MockDataGenerator.random_int(10, 1000),
            remaining=MockDataGenerator.random_int(0, 1000),
            reset=datetime.now(timezone.utc).timestamp() + MockDataGenerator.random_int(60, 3600),
            used=MockDataGenerator.random_int(0, 1000)
        )
    
    @staticmethod
    def generate_platforms(count: int = 5) -> List[Platform]:
        """Generate a list of random Platform instances."""
        return [MockDataGenerator.generate_platform() for _ in range(count)]
    
    @staticmethod
    def generate_packages(count: int = 5) -> List[Package]:
        """Generate a list of random Package instances."""
        return [MockDataGenerator.generate_package() for _ in range(count)]
    
    @staticmethod
    def generate_package_versions(count: int = 5) -> List[PackageVersion]:
        """Generate a list of random PackageVersion instances."""
        return [MockDataGenerator.generate_package_version() for _ in range(count)]
    
    @staticmethod
    def generate_dependencies(count: int = 5) -> List[Dependency]:
        """Generate a list of random Dependency instances."""
        return [MockDataGenerator.generate_dependency() for _ in range(count)]
    
    @staticmethod
    def generate_repositories(count: int = 5) -> List[Repository]:
        """Generate a list of random Repository instances."""
        return [MockDataGenerator.generate_repository() for _ in range(count)]
    
    @staticmethod
    def generate_users(count: int = 5) -> List[User]:
        """Generate a list of random User instances."""
        return [MockDataGenerator.generate_user() for _ in range(count)]
    
    @staticmethod
    def generate_organizations(count: int = 5) -> List[Organization]:
        """Generate a list of random Organization instances."""
        return [MockDataGenerator.generate_organization() for _ in range(count)]
    
    @staticmethod
    def generate_search_results(count: int = 5) -> List[SearchResult]:
        """Generate a list of random SearchResult instances."""
        return [MockDataGenerator.generate_search_result() for _ in range(count)]
    
    @staticmethod
    def generate_rate_limit_infos(count: int = 5) -> List[RateLimitInfo]:
        """Generate a list of random RateLimitInfo instances."""
        return [MockDataGenerator.generate_rate_limit_info() for _ in range(count)]


class TestAssertionHelpers:
    """Helper functions for common test assertions."""
    
    @staticmethod
    def assert_rate_limit_info(rate_limit_info: RateLimitInfo) -> None:
        """Assert that RateLimitInfo has valid values."""
        assert isinstance(rate_limit_info, RateLimitInfo)
        assert rate_limit_info.limit > 0
        assert rate_limit_info.remaining >= 0
        assert rate_limit_info.remaining <= rate_limit_info.limit
        assert rate_limit_info.reset is not None
        assert rate_limit_info.reset > 0
        assert rate_limit_info.used >= 0
        assert rate_limit_info.used <= rate_limit_info.limit
    
    @staticmethod
    def assert_platform(platform: Platform) -> None:
        """Assert that Platform has valid values."""
        assert isinstance(platform, Platform)
        assert isinstance(platform.name, str)
        assert len(platform.name) > 0
        assert isinstance(platform.project_count, int)
        assert platform.project_count >= 0
        assert isinstance(platform.homepage, str)
        assert len(platform.homepage) > 0
        assert platform.homepage.startswith("http")
        assert isinstance(platform.color, str)
        assert len(platform.color) > 0
        assert platform.color.startswith("#")
    
    @staticmethod
    def assert_package(package: Package) -> None:
        """Assert that Package has valid values."""
        assert isinstance(package, Package)
        assert isinstance(package.name, str)
        assert len(package.name) > 0
        assert isinstance(package.platform, str)
        assert len(package.platform) > 0
        assert package.description is None or isinstance(package.description, str)
        assert package.homepage is None or isinstance(package.homepage, str)
        assert package.homepage is None or package.homepage.startswith("http")
        assert package.repository_url is None or isinstance(package.repository_url, str)
        assert package.repository_url is None or package.repository_url.startswith("http")
        assert package.language is None or isinstance(package.language, str)
        assert isinstance(package.keywords, list)
        assert all(isinstance(keyword, str) for keyword in package.keywords)
        assert package.licenses is None or isinstance(package.licenses, str)
        assert package.latest_release_number is None or isinstance(package.latest_release_number, str)
        assert package.latest_release_published_at is None or isinstance(package.latest_release_published_at, datetime)
        assert isinstance(package.stars, int)
        assert package.stars >= 0
        assert isinstance(package.forks, int)
        assert package.forks >= 0
        assert isinstance(package.dependents_count, int)
        assert package.dependents_count >= 0
        assert isinstance(package.status, str)
        assert len(package.status) > 0
    
    @staticmethod
    def assert_package_version(package_version: PackageVersion) -> None:
        """Assert that PackageVersion has valid values."""
        assert isinstance(package_version, PackageVersion)
        assert isinstance(package_version.number, str)
        assert len(package_version.number) > 0
        assert package_version.published_at is None or isinstance(package_version.published_at, datetime)
        assert package_version.spdx_expression is None or isinstance(package_version.spdx_expression, str)
        assert package_version.original_license is None or isinstance(package_version.original_license, str)
        assert package_version.status is None or isinstance(package_version.status, str)
    
    @staticmethod
    def assert_dependency(dependency: Dependency) -> None:
        """Assert that Dependency has valid values."""
        assert isinstance(dependency, Dependency)
        assert isinstance(dependency.name, str)
        assert len(dependency.name) > 0
        assert isinstance(dependency.platform, str)
        assert len(dependency.platform) > 0
        assert isinstance(dependency.requirement, str)
        assert len(dependency.requirement) > 0
        assert isinstance(dependency.kind, str)
        assert len(dependency.kind) > 0
        assert isinstance(dependency.optional, bool)
    
    @staticmethod
    def assert_repository(repository: Repository) -> None:
        """Assert that Repository has valid values."""
        assert isinstance(repository, Repository)
        assert isinstance(repository.url, str)
        assert len(repository.url) > 0
        assert repository.url.startswith("http")
        assert isinstance(repository.homepage, str)
        assert len(repository.homepage) > 0
        assert repository.homepage.startswith("http")
        assert isinstance(repository.description, str)
        assert len(repository.description) > 0
        assert isinstance(repository.language, str)
        assert len(repository.language) > 0
        assert isinstance(repository.stars, int)
        assert repository.stars >= 0
        assert isinstance(repository.forks, int)
        assert repository.forks >= 0
        assert isinstance(repository.last_commit_at, datetime)
        assert isinstance(repository.package_count, int)
        assert repository.package_count >= 0
    
    @staticmethod
    def assert_user(user: User) -> None:
        """Assert that User has valid values."""
        assert isinstance(user, User)
        assert isinstance(user.username, str)
        assert len(user.username) > 0
        assert isinstance(user.name, str)
        assert len(user.name) > 0
        assert isinstance(user.email, str)
        assert len(user.email) > 0
        assert "@" in user.email
        assert user.company is None or isinstance(user.company, str)
        assert user.location is None or isinstance(user.location, str)
        assert user.blog is None or isinstance(user.blog, str)
        assert user.blog is None or user.blog.startswith("http")
        assert isinstance(user.bio, str)
        assert len(user.bio) > 0
        assert isinstance(user.avatar_url, str)
        assert len(user.avatar_url) > 0
        assert isinstance(user.followers_count, int)
        assert user.followers_count >= 0
        assert isinstance(user.following_count, int)
        assert user.following_count >= 0
        assert isinstance(user.public_gists_count, int)
        assert user.public_gists_count >= 0
        assert isinstance(user.public_repos_count, int)
        assert user.public_repos_count >= 0
    
    @staticmethod
    def assert_organization(organization: Organization) -> None:
        """Assert that Organization has valid values."""
        assert isinstance(organization, Organization)
        assert isinstance(organization.login, str)
        assert len(organization.login) > 0
        assert isinstance(organization.name, str)
        assert len(organization.name) > 0
        assert organization.description is None or isinstance(organization.description, str)
        assert organization.company is None or isinstance(organization.company, str)
        assert organization.location is None or isinstance(organization.location, str)
        assert organization.blog is None or isinstance(organization.blog, str)
        assert organization.blog is None or organization.blog.startswith("http")
        assert organization.email is None or isinstance(organization.email, str)
        assert isinstance(organization.avatar_url, str)
        assert len(organization.avatar_url) > 0
        assert isinstance(organization.followers_count, int)
        assert organization.followers_count >= 0
        assert isinstance(organization.following_count, int)
        assert organization.following_count >= 0
        assert isinstance(organization.public_gists_count, int)
        assert organization.public_gists_count >= 0
        assert isinstance(organization.public_repos_count, int)
        assert organization.public_repos_count >= 0
        assert isinstance(organization.created_at, datetime)
        assert isinstance(organization.updated_at, datetime)
    
    @staticmethod
    def assert_search_result(search_result: SearchResult) -> None:
        """Assert that SearchResult has valid values."""
        assert isinstance(search_result, SearchResult)
        assert isinstance(search_result.total_count, int)
        assert search_result.total_count >= 0
        assert isinstance(search_result.incomplete_results, bool)
        assert isinstance(search_result.items, list)
        assert all(isinstance(item, Package) for item in search_result.items)
    
    @staticmethod
    def assert_dict_structure(data: Dict[str, Any], expected_keys: List[str]) -> None:
        """Assert that dictionary has expected keys."""
        assert isinstance(data, dict)
        for key in expected_keys:
            assert key in data, f"Expected key '{key}' not found in dictionary"
    
    @staticmethod
    def assert_list_structure(data: List[Any], expected_length: Optional[int] = None) -> None:
        """Assert that list has expected structure."""
        assert isinstance(data, list)
        if expected_length is not None:
            assert len(data) == expected_length, f"Expected list length {expected_length}, got {len(data)}"
    
    @staticmethod
    def assert_response_success(response: Dict[str, Any]) -> None:
        """Assert that response has success structure."""
        TestAssertionHelpers.assert_dict_structure(response, ["success"])
        assert isinstance(response["success"], bool)
        if response["success"]:
            assert "data" in response
            assert response["data"] is not None
        else:
            assert "error" in response
            assert response["error"] is not None
            assert isinstance(response["error"], str)
    
    @staticmethod
    def assert_rate_limit_headers(headers: Dict[str, str]) -> None:
        """Assert that rate limit headers are valid."""
        assert isinstance(headers, dict)
        assert "x-ratelimit-limit" in headers
        assert "x-ratelimit-remaining" in headers
        assert "x-ratelimit-reset" in headers
        
        assert isinstance(headers["x-ratelimit-limit"], str)
        assert isinstance(headers["x-ratelimit-remaining"], str)
        assert isinstance(headers["x-ratelimit-reset"], str)
        
        assert headers["x-ratelimit-limit"].isdigit()
        assert headers["x-ratelimit-remaining"].isdigit()
        assert headers["x-ratelimit-reset"].isdigit()
        
        limit = int(headers["x-ratelimit-limit"])
        remaining = int(headers["x-ratelimit-remaining"])
        reset = int(headers["x-ratelimit-reset"])
        
        assert limit > 0
        assert remaining >= 0
        assert remaining <= limit
        assert reset > 0
    
    @staticmethod
    def assert_json_response(response_text: str) -> Dict[str, Any]:
        """Assert that response text is valid JSON and return parsed data."""
        assert isinstance(response_text, str)
        assert len(response_text) > 0
        
        try:
            data = json.loads(response_text)
            assert isinstance(data, dict)
            return data
        except json.JSONDecodeError as e:
            raise AssertionError(f"Invalid JSON response: {e}")
    
    @staticmethod
    def assert_error_response(response: Dict[str, Any], expected_error: Optional[str] = None) -> None:
        """Assert that response is an error response."""
        assert isinstance(response, dict)
        assert "success" in response
        assert isinstance(response["success"], bool)
        assert not response["success"]
        
        assert "error" in response
        assert isinstance(response["error"], str)
        assert len(response["error"]) > 0
        
        if expected_error:
            assert expected_error in response["error"]
    
    @staticmethod
    def assert_success_response(response: Dict[str, Any], expected_data: Optional[Dict[str, Any]] = None) -> None:
        """Assert that response is a success response."""
        assert isinstance(response, dict)
        assert "success" in response
        assert isinstance(response["success"], bool)
        assert response["success"]
        
        assert "data" in response
        assert response["data"] is not None
        
        if expected_data:
            assert isinstance(response["data"], dict)
            for key, value in expected_data.items():
                assert key in response["data"]
                if value is not None:
                    assert response["data"][key] == value
    
    @staticmethod
    def assert_pagination_data(pagination: Dict[str, Any]) -> None:
        """Assert that pagination data is valid."""
        assert isinstance(pagination, dict)
        expected_keys = ["page", "per_page", "total_pages", "total_items", "has_next", "has_prev"]
        for key in expected_keys:
            assert key in pagination, f"Expected pagination key '{key}' not found"
        
        assert isinstance(pagination["page"], int)
        assert pagination["page"] >= 1
        
        assert isinstance(pagination["per_page"], int)
        assert pagination["per_page"] >= 1
        
        assert isinstance(pagination["total_pages"], int)
        assert pagination["total_pages"] >= 0
        
        assert isinstance(pagination["total_items"], int)
        assert pagination["total_items"] >= 0
        
        assert isinstance(pagination["has_next"], bool)
        assert isinstance(pagination["has_prev"], bool)
        
        # Validate logical consistency
        if pagination["total_pages"] > 0:
            assert pagination["page"] <= pagination["total_pages"]
        
        if pagination["total_items"] > 0:
            assert pagination["total_pages"] >= 1
    
    @staticmethod
    def assert_filter_data(filters: Dict[str, Any]) -> None:
        """Assert that filter data is valid."""
        assert isinstance(filters, dict)
        expected_keys = ["applied", "available", "counts"]
        for key in expected_keys:
            assert key in filters, f"Expected filter key '{key}' not found"
        
        assert isinstance(filters["applied"], list)
        assert all(isinstance(item, str) for item in filters["applied"])
        
        assert isinstance(filters["available"], list)
        assert all(isinstance(item, str) for item in filters["available"])
        
        assert isinstance(filters["counts"], dict)
        for key, value in filters["counts"].items():
            assert isinstance(key, str)
            assert isinstance(value, dict)
            for sub_key, sub_value in value.items():
                assert isinstance(sub_key, str)
                assert isinstance(sub_value, int)
                assert sub_value >= 0
    
    @staticmethod
    def assert_sorting_data(sorting: Dict[str, Any]) -> None:
        """Assert that sorting data is valid."""
        assert isinstance(sorting, dict)
        expected_keys = ["by", "order", "available"]
        for key in expected_keys:
            assert key in sorting, f"Expected sorting key '{key}' not found"
        
        assert isinstance(sorting["by"], str)
        assert len(sorting["by"]) > 0
        
        assert isinstance(sorting["order"], str)
        assert sorting["order"] in ["asc", "desc"]
        
        assert isinstance(sorting["available"], list)
        assert all(isinstance(item, str) for item in sorting["available"])
    
    @staticmethod
    def assert_aggregation_data(aggregation: Dict[str, Any]) -> None:
        """Assert that aggregation data is valid."""
        assert isinstance(aggregation, dict)
        for key, value in aggregation.items():
            assert isinstance(key, str)
            assert isinstance(value, dict)
            for sub_key, sub_value in value.items():
                assert isinstance(sub_key, str)
                assert isinstance(sub_value, int)
                assert sub_value >= 0
    
    @staticmethod
    def assert_statistics_data(statistics: Dict[str, Any]) -> None:
        """Assert that statistics data is valid."""
        assert isinstance(statistics, dict)
        expected_keys = ["count", "sum", "average", "min", "max", "median"]
        for key in expected_keys:
            assert key in statistics, f"Expected statistics key '{key}' not found"
        
        assert isinstance(statistics["count"], int)
        assert statistics["count"] >= 0
        
        assert isinstance(statistics["sum"], (int, float))
        
        assert isinstance(statistics["average"], (int, float))
        
        assert isinstance(statistics["min"], (int, float))
        
        assert isinstance(statistics["max"], (int, float))
        
        assert isinstance(statistics["median"], (int, float))
    
    @staticmethod
    def assert_graph_data(graph: Dict[str, Any]) -> None:
        """Assert that graph data is valid."""
        assert isinstance(graph, dict)
        expected_keys = ["nodes", "edges"]
        for key in expected_keys:
            assert key in graph, f"Expected graph key '{key}' not found"
        
        assert isinstance(graph["nodes"], list)
        for node in graph["nodes"]:
            assert isinstance(node, dict)
            assert "id" in node
            assert "label" in node
            assert isinstance(node["id"], (int, str))
            assert isinstance(node["label"], str)
        
        assert isinstance(graph["edges"], list)
        for edge in graph["edges"]:
            assert isinstance(edge, dict)
            assert "source" in edge
            assert "target" in edge
            assert isinstance(edge["source"], (int, str))
            assert isinstance(edge["target"], (int, str))
    
    @staticmethod
    def assert_tree_data(tree: Dict[str, Any]) -> None:
        """Assert that tree data is valid."""
        assert isinstance(tree, dict)
        assert "root" in tree
        assert isinstance(tree["root"], dict)
        assert "id" in tree["root"]
        assert "label" in tree["root"]
        assert "children" in tree["root"]
        assert isinstance(tree["root"]["children"], list)
        
        # Recursively check children
        for child in tree["root"]["children"]:
            TestAssertionHelpers.assert_tree_data({"root": child})
    
    @staticmethod
    def assert_matrix_data(matrix: Dict[str, Any]) -> None:
        """Assert that matrix data is valid."""
        assert isinstance(matrix, dict)
        expected_keys = ["rows", "columns", "data"]
        for key in expected_keys:
            assert key in matrix, f"Expected matrix key '{key}' not found"
        
        assert isinstance(matrix["rows"], list)
        assert all(isinstance(item, str) for item in matrix["rows"])
        
        assert isinstance(matrix["columns"], list)
        assert all(isinstance(item, str) for item in matrix["columns"])
        
        assert isinstance(matrix["data"], list)
        assert len(matrix["data"]) == len(matrix["rows"])
        for row in matrix["data"]:
            assert isinstance(row, list)
            assert len(row) == len(matrix["columns"])
            assert all(isinstance(item, (int, float)) for item in row)
    
    @staticmethod
    def assert_chart_data(chart: Dict[str, Any]) -> None:
        """Assert that chart data is valid."""
        assert isinstance(chart, dict)
        expected_keys = ["type", "title", "data"]
        for key in expected_keys:
            assert key in chart, f"Expected chart key '{key}' not found"
        
        assert isinstance(chart["type"], str)
        assert len(chart["type"]) > 0
        
        assert isinstance(chart["title"], str)
        assert len(chart["title"]) > 0
        
        assert isinstance(chart["data"], dict)
        assert "labels" in chart["data"]
        assert "datasets" in chart["data"]
        
        assert isinstance(chart["data"]["labels"], list)
        assert all(isinstance(item, str) for item in chart["data"]["labels"])
        
        assert isinstance(chart["data"]["datasets"], list)
        for dataset in chart["data"]["datasets"]:
            assert isinstance(dataset, dict)
            assert "label" in dataset
            assert "data" in dataset
            assert isinstance(dataset["label"], str)
            assert isinstance(dataset["data"], list)
            assert all(isinstance(item, (int, float)) for item in dataset["data"])
    
    @staticmethod
    def assert_timeline_data(timeline: Dict[str, Any]) -> None:
        """Assert that timeline data is valid."""
        assert isinstance(timeline, dict)
        expected_keys = ["events"]
        for key in expected_keys:
            assert key in timeline, f"Expected timeline key '{key}' not found"
        
        assert isinstance(timeline["events"], list)
        for event in timeline["events"]:
            assert isinstance(event, dict)
            assert "date" in event
            assert "title" in event
            assert "description" in event
            assert isinstance(event["date"], str)
            assert isinstance(event["title"], str)
            assert isinstance(event["description"], str)
    
    @staticmethod
    def assert_geo_data(geo: Dict[str, Any]) -> None:
        """Assert that geographic data is valid."""
        assert isinstance(geo, dict)
        expected_keys = ["type", "features"]
        for key in expected_keys:
            assert key in geo, f"Expected geo key '{key}' not found"
        
        assert isinstance(geo["type"], str)
        assert geo["type"] == "FeatureCollection"
        
        assert isinstance(geo["features"], list)
        for feature in geo["features"]:
            assert isinstance(feature, dict)
            assert "type" in feature
            assert "geometry" in feature
            assert "properties" in feature
            assert feature["type"] == "Feature"
            
            assert isinstance(feature["geometry"], dict)
            assert "type" in feature["geometry"]
            assert "coordinates" in feature["geometry"]
            
            assert isinstance(feature["properties"], dict)
    
    @staticmethod
    def assert_network_data(network: Dict[str, Any]) -> None:
        """Assert that network data is valid."""
        assert isinstance(network, dict)
        expected_keys = ["nodes", "links"]
        for key in expected_keys:
            assert key in network, f"Expected network key '{key}' not found"
        
        assert isinstance(network["nodes"], list)
        for node in network["nodes"]:
            assert isinstance(node, dict)
            assert "id" in node
            assert "group" in node
            assert isinstance(node["id"], (int, str))
            assert isinstance(node["group"], int)
        
        assert isinstance(network["links"], list)
        for link in network["links"]:
            assert isinstance(link, dict)
            assert "source" in link
            assert "target" in link
            assert isinstance(link["source"], (int, str))
            assert isinstance(link["target"], (int, str))
    
    @staticmethod
    def assert_calendar_data(calendar: Dict[str, Any]) -> None:
        """Assert that calendar data is valid."""
        assert isinstance(calendar, dict)
        expected_keys = ["year", "months"]
        for key in expected_keys:
            assert key in calendar, f"Expected calendar key '{key}' not found"
        
        assert isinstance(calendar["year"], int)
        assert calendar["year"] >= 1900
        
        assert isinstance(calendar["months"], list)
        for month in calendar["months"]:
            assert isinstance(month, dict)
            assert "name" in month
            assert "weeks" in month
            assert isinstance(month["name"], str)
            assert isinstance(month["weeks"], list)
            
            for week in month["weeks"]:
                assert isinstance(week, dict)
                assert "days" in week
                assert isinstance(week["days"], list)
                
                for day in week["days"]:
                    assert isinstance(day, dict)
                    assert "date" in day
                    assert "events" in day
                    assert isinstance(day["date"], str)
                    assert isinstance(day["events"], list)
    
    @staticmethod
    def assert_code_data(code: Dict[str, Any]) -> None:
        """Assert that code data is valid."""
        assert isinstance(code, dict)
        expected_keys = ["language", "content", "highlighted"]
        for key in expected_keys:
            assert key in code, f"Expected code key '{key}' not found"
        
        assert isinstance(code["language"], str)
        assert len(code["language"]) > 0
        
        assert isinstance(code["content"], str)
        assert len(code["content"]) > 0
        
        assert isinstance(code["highlighted"], str)
        assert len(code["highlighted"]) > 0
    
    @staticmethod
    def assert_file_data(file: Dict[str, Any]) -> None:
        """Assert that file data is valid."""
        assert isinstance(file, dict)
        expected_keys = ["name", "size", "type", "content"]
        for key in expected_keys:
            assert key in file, f"Expected file key '{key}' not found"
        
        assert isinstance(file["name"], str)
        assert len(file["name"]) > 0
        
        assert isinstance(file["size"], int)
        assert file["size"] >= 0
        
        assert isinstance(file["type"], str)
        assert len(file["type"]) > 0
        
        assert isinstance(file["content"], str)
    
    @staticmethod
    def assert_image_data(image: Dict[str, Any]) -> None:
        """Assert that image data is valid."""
        assert isinstance(image, dict)
        expected_keys = ["url", "width", "height", "format", "size"]
        for key in expected_keys:
            assert key in image, f"Expected image key '{key}' not found"
        
        assert isinstance(image["url"], str)
        assert len(image["url"]) > 0
        assert image["url"].startswith("http")
        
        assert isinstance(image["width"], int)
        assert image["width"] > 0
        
        assert isinstance(image["height"], int)
        assert image["height"] > 0
        
        assert isinstance(image["format"], str)
        assert len(image["format"]) > 0
        
        assert isinstance(image["size"], int)
        assert image["size"] >= 0
    
    @staticmethod
    def assert_audio_data(audio: Dict[str, Any]) -> None:
        """Assert that audio data is valid."""
        assert isinstance(audio, dict)
        expected_keys = ["url", "duration", "format", "size"]
        for key in expected_keys:
            assert key in audio, f"Expected audio key '{key}' not found"
        
        assert isinstance(audio["url"], str)
        assert len(audio["url"]) > 0
        assert audio["url"].startswith("http")
        
        assert isinstance(audio["duration"], int)
        assert audio["duration"] > 0
        
        assert isinstance(audio["format"], str)
        assert len(audio["format"]) > 0
        
        assert isinstance(audio["size"], int)
        assert audio["size"] >= 0
    
    @staticmethod
    def assert_video_data(video: Dict[str, Any]) -> None:
        """Assert that video data is valid."""
        assert isinstance(video, dict)
        expected_keys = ["url", "duration", "format", "size", "resolution"]
        for key in expected_keys:
            assert key in video, f"Expected video key '{key}' not found"
        
        assert isinstance(video["url"], str)
        assert len(video["url"]) > 0
        assert video["url"].startswith("http")
        
        assert isinstance(video["duration"], int)
        assert video["duration"] > 0
        
        assert isinstance(video["format"], str)
        assert len(video["format"]) > 0
        
        assert isinstance(video["size"], int)
        assert video["size"] >= 0
        
        assert isinstance(video["resolution"], str)
        assert len(video["resolution"]) > 0
        assert "x" in video["resolution"]
    
    @staticmethod
    def assert_document_data(document: Dict[str, Any]) -> None:
        """Assert that document data is valid."""
        assert isinstance(document, dict)
        expected_keys = ["title", "author", "pages", "format", "size"]
        for key in expected_keys:
            assert key in document, f"Expected document key '{key}' not found"
        
        assert isinstance(document["title"], str)
        assert len(document["title"]) > 0
        
        assert isinstance(document["author"], str)
        assert len(document["author"]) > 0
        
        assert isinstance(document["pages"], int)
        assert document["pages"] > 0
        
        assert isinstance(document["format"], str)
        assert len(document["format"]) > 0
        
        assert isinstance(document["size"], int)
        assert document["size"] >= 0
    
    @staticmethod
    def assert_archive_data(archive: Dict[str, Any]) -> None:
        """Assert that archive data is valid."""
        assert isinstance(archive, dict)
        expected_keys = ["name", "size", "format", "files"]
        for key in expected_keys:
            assert key in archive, f"Expected archive key '{key}' not found"
        
        assert isinstance(archive["name"], str)
        assert len(archive["name"]) > 0
        
        assert isinstance(archive["size"], int)
        assert archive["size"] >= 0
        
        assert isinstance(archive["format"], str)
        assert len(archive["format"]) > 0
        
        assert isinstance(archive["files"], list)
        for file in archive["files"]:
            assert isinstance(file, dict)
            assert "name" in file
            assert "size" in file
            assert isinstance(file["name"], str)
            assert isinstance(file["size"], int)
            assert file["size"] >= 0
    
    @staticmethod
    def assert_database_data(database: Dict[str, Any]) -> None:
        """Assert that database data is valid."""
        assert isinstance(database, dict)
        expected_keys = ["name", "tables"]
        for key in expected_keys:
            assert key in database, f"Expected database key '{key}' not found"
        
        assert isinstance(database["name"], str)
        assert len(database["name"]) > 0
        
        assert isinstance(database["tables"], list)
        for table in database["tables"]:
            assert isinstance(table, dict)
            assert "name" in table
            assert "columns" in table
            assert "rows" in table
            assert isinstance(table["name"], str)
            assert isinstance(table["columns"], list)
            assert all(isinstance(col, str) for col in table["columns"])
            assert isinstance(table["rows"], int)
            assert table["rows"] >= 0
    
    @staticmethod
    def assert_api_data(api: Dict[str, Any]) -> None:
        """Assert that API data is valid."""
        assert isinstance(api, dict)
        expected_keys = ["endpoint", "method", "parameters", "response"]
        for key in expected_keys:
            assert key in api, f"Expected API key '{key}' not found"
        
        assert isinstance(api["endpoint"], str)
        assert len(api["endpoint"]) > 0
        
        assert isinstance(api["method"], str)
        assert api["method"].upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]
        
        assert isinstance(api["parameters"], dict)
        
        assert isinstance(api["response"], dict)


class TestMockHelpers:
    """Helper functions for creating and managing mocks."""
    
    @staticmethod
    def create_mock_http_response(
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: str = "",
        headers: Optional[Dict[str, str]] = None
    ) -> Mock:
        """Create a mock HTTP response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data or {}
        mock_response.text = text or ""
        mock_response.headers = headers or {}
        return mock_response
    
    @staticmethod
    def create_mock_rate_limiter(
        limit: int = 60,
        remaining: int = 59,
        reset: float = 1234567890.0,
        used: int = 1
    ) -> Mock:
        """Create a mock rate limiter."""
        mock_limiter = Mock(spec=RateLimiter)
        mock_limiter.limit = limit
        mock_limiter.remaining = remaining
        mock_limiter.reset = reset
        mock_limiter.used = used
        mock_limiter.acquire = AsyncMock()
        return mock_limiter
    
    @staticmethod
    def create_mock_cache(
        data: Optional[Dict[str, Any]] = None,
        size: int = 0
    ) -> Mock:
        """Create a mock cache."""
        mock_cache = Mock(spec=MemoryCache)
        mock_cache.data = data or {}
        mock_cache.size = size
        mock_cache.get = AsyncMock(return_value=data)
        mock_cache.set = AsyncMock()
        mock_cache.clear = AsyncMock()
        mock_cache.size = AsyncMock(return_value=size)
        return mock_cache
    
    @staticmethod
    def create_mock_retry_handler(
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0
    ) -> Mock:
        """Create a mock retry handler."""
        mock_handler = Mock(spec=RetryHandler)
        mock_handler.max_retries = max_retries
        mock_handler.base_delay = base_delay
        mock_handler.max_delay = max_delay
        mock_handler.retry = AsyncMock()
        return mock_handler
    
    @staticmethod
    def create_mock_client(
        api_key: str = "test_key",
        base_url: str = "https://test.api.com",
        rate_limiter: Optional[Mock] = None,
        cache: Optional[Mock] = None,
        retry_handler: Optional[Mock] = None
    ) -> Mock:
        """Create a mock client."""
        mock_client = Mock()
        mock_client.api_key = api_key
        mock_client.base_url = base_url
        mock_client.rate_limiter = rate_limiter or TestMockHelpers.create_mock_rate_limiter()
        mock_client.cache = cache or TestMockHelpers.create_mock_cache()
        mock_client.retry_handler = retry_handler or TestMockHelpers.create_mock_retry_handler()
        mock_client.get_rate_limit_info = Mock(return_value=None)
        mock_client.clear_cache = AsyncMock()
        return mock_client
    
    @staticmethod
    def create_mock_server(
        host: str = "127.0.0.1",
        port: int = 8000,
        log_level: str = "DEBUG"
    ) -> Mock:
        """Create a mock server."""
        mock_server = Mock()
        mock_server.host = host
        mock_server.port = port
        mock_server.log_level = log_level
        mock_server.add_tool = Mock()
        mock_server.serve = AsyncMock()
        return mock_server
    
    @staticmethod
    def create_mock_tool(
        name: str = "test_tool",
        description: str = "Test tool",
        parameters: Optional[Dict[str, Any]] = None
    ) -> Mock:
        """Create a mock tool."""
        mock_tool = Mock()
        mock_tool.__name__ = name
        mock_tool.__doc__ = description
        mock_tool.parameters = parameters or {}
        mock_tool.return_value = {"success": True, "data": {}}
        return mock_tool
    
    @staticmethod
    def create_mock_async_context_manager(
        return_value: Any = None
    ) -> Mock:
        """Create a mock async context manager."""
        mock_context = Mock()
        mock_context.__aenter__ = AsyncMock(return_value=return_value)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        return mock_context
    
    @staticmethod
    def create_mock_validation_error(
        errors: Optional[List[Dict[str, Any]]] = None
    ) -> Mock:
        """Create a mock validation error."""
        mock_error = Mock()
        mock_error.errors = errors or [{"loc": ("field",), "msg": "error message"}]
        return mock_error
    
    @staticmethod
    def create_mock_client_error(
        message: str = "Test client error"
    ) -> Mock:
        """Create a mock client error."""
        mock_error = Mock()
        mock_error.__str__ = Mock(return_value=message)
        return mock_error
    
    @staticmethod
    def create_mock_authentication_error(
        message: str = "Authentication failed"
    ) -> Mock:
        """Create a mock authentication error."""
        mock_error = Mock()
        mock_error.__str__ = Mock(return_value=message)
        return mock_error
    
    @staticmethod
    def create_mock_not_found_error(
        message: str = "Resource not found"
    ) -> Mock:
        """Create a mock not found error."""
        mock_error = Mock()
        mock_error.__str__ = Mock(return_value=message)
        return mock_error
    
    @staticmethod
    def create_mock_rate_limit_error(
        message: str = "Rate limit exceeded"
    ) -> Mock:
        """Create a mock rate limit error."""
        mock_error = Mock()
        mock_error.__str__ = Mock(return_value=message)
        return mock_error
    
    @staticmethod
    def create_mock_server_error(
        message: str = "Server error"
    ) -> Mock:
        """Create a mock server error."""
        mock_error = Mock()
        mock_error.__str__ = Mock(return_value=message)
        return mock_error
    
    @staticmethod
    def create_mock_timeout_error(
        message: str = "Timeout error"
    ) -> Mock:
        """Create a mock timeout error."""
        mock_error = Mock()
        mock_error.__str__ = Mock(return_value=message)
        return mock_error
    
    @staticmethod
    def create_mock_network_error(
        message: str = "Network error"
    ) -> Mock:
        """Create a mock network error."""
        mock_error = Mock()
        mock_error.__str__ = Mock(return_value=message)
        return mock_error
    
    @staticmethod
    def create_mock_json_error(
        message: str = "JSON decode error"
    ) -> Mock:
        """Create a mock JSON error."""
        mock_error = Mock()
        mock_error.__str__ = Mock(return_value=message)
        return mock_error
    
    @staticmethod
    def create_mock_http_error(
        status_code: int = 400,
        message: str = "HTTP error"
    ) -> Mock:
        """Create a mock HTTP error."""
        mock_error = Mock()
        mock_error.status_code = status_code
        mock_error.__str__ = Mock(return_value=message)
        return mock_error
    
    @staticmethod
    def create_mock_rate_limit_info(
        limit: int = 60,
        remaining: int = 59,
        reset: float = 1234567890.0,
        used: int = 1
    ) -> RateLimitInfo:
        """Create a mock rate limit info."""
        return RateLimitInfo(
            limit=limit,
            remaining=remaining,
            reset=reset,
            used=used
        )
    
    @staticmethod
    def create_mock_platform(
        name: str = "npm",
        project_count: int = 1000000,
        homepage: str = "https://www.npmjs.com/",
        color: str = "#cb3837",
        default_language: str = "JavaScript",
        package_type: str = "library"
    ) -> Platform:
        """Create a mock platform."""
        return Platform(
            name=name,
            project_count=project_count,
            homepage=homepage,
            color=color,
            default_language=default_language,
            package_type=package_type
        )
    
    @staticmethod
    def create_mock_package(
        name: str = "react",
        platform: str = "npm",
        description: str = "A JavaScript library for building user interfaces",
        homepage: str = "https://reactjs.org/",
        repository_url: str = "https://github.com/facebook/react",
        language: str = "JavaScript",
        keywords: List[str] = None,
        licenses: str = "MIT",
        latest_release_number: str = "18.2.0",
        latest_release_published_at: datetime = None,
        stars: int = 200000,
        forks: int = 40000,
        dependents_count: int = 50000,
        status: str = "active"
    ) -> Package:
        """Create a mock package."""
        return Package(
            name=name,
            platform=platform,
            description=description,
            homepage=homepage,
            repository_url=repository_url,
            language=language,
            keywords=keywords or ["javascript", "ui", "library"],
            licenses=licenses,
            latest_release_number=latest_release_number,
            latest_release_published_at=latest_release_published_at or datetime.now(timezone.utc),
            stars=stars,
            forks=forks,
            dependents_count=dependents_count,
            status=status
        )
    
    @staticmethod
    def create_mock_package_version(
        number: str = "18.2.0",
        published_at: Optional[datetime] = None,
        spdx_expression: str = "MIT",
        original_license: str = "MIT",
        status: str = "active"
    ) -> PackageVersion:
        """Create a mock package version."""
        return PackageVersion(
            number=number,
            published_at=published_at or datetime.now(timezone.utc),
            spdx_expression=spdx_expression,
            original_license=original_license,
            status=status
        )
    
    @staticmethod
    def create_mock_dependency(
        name: str = "react-dom",
        platform: str = "npm",
        requirement: str = "^18.0.0",
        kind: str = "runtime",
        optional: bool = False
    ) -> Dependency:
        """Create a mock dependency."""
        return Dependency(
            name=name,
            platform=platform,
            requirement=requirement,
            kind=kind,
            optional=optional
        )
    
    @staticmethod
    def create_mock_repository(
        url: str = "https://github.com/facebook/react",
        homepage: str = "https://reactjs.org/",
        description: str = "A JavaScript library for building user interfaces",
        language: str = "JavaScript",
        stars: int = 200000,
        forks: int = 40000,
        last_commit_at: Optional[datetime] = None,
        package_count: int = 5
    ) -> Repository:
        """Create a mock repository."""
        return Repository(
            url=url,
            homepage=homepage,
            description=description,
            language=language,
            stars=stars,
            forks=forks,
            last_commit_at=last_commit_at or datetime.now(timezone.utc),
            package_count=package_count
        )
    
    @staticmethod
    def create_mock_user(
        username: str = "octocat",
        name: str = "The Octocat",
        email: str = "octocat@example.com",
        company: str = "GitHub",
        location: str = "San Francisco",
        blog: str = "https://github.blog",
        bio: str = "GitHub mascot",
        avatar_url: str = "https://github.com/images/error/octocat_happy.gif",
        followers_count: int = 1000,
        following_count: int = 500,
        public_gists_count: int = 10,
        public_repos_count: int = 8
    ) -> User:
        """Create a mock user."""
        return User(
            username=username,
            name=name,
            email=email,
            company=company,
            location=location,
            blog=blog,
            bio=bio,
            avatar_url=avatar_url,
            followers_count=followers_count,
            following_count=following_count,
            public_gists_count=public_gists_count,
            public_repos_count=public_repos_count
        )
    
    @staticmethod
    def create_mock_organization(
        login: str = "facebook",
        name: str = "Facebook",
        description: str = "Social media company",
        company: str = "Meta",
        location: str = "Menlo Park, CA",
        blog: str = "https://facebook.com",
        email: str = "contact@facebook.com",
        avatar_url: str = "https://github.com/images/error/facebook_200x200.jpg",
        followers_count: int = 5000,
        following_count: int = 100,
        public_gists_count: int = 0,
        public_repos_count: int = 50,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ) -> Organization:
        """Create a mock organization."""
        return Organization(
            login=login,
            name=name,
            description=description,
            company=company,
            location=location,
            blog=blog,
            email=email,
            avatar_url=avatar_url,
            followers_count=followers_count,
            following_count=following_count,
            public_gists_count=public_gists_count,
            public_repos_count=public_repos_count,
            created_at=created_at or datetime.now(timezone.utc),
            updated_at=updated_at or datetime.now(timezone.utc)
        )
    
    @staticmethod
    def create_mock_search_result(
        total_count: int = 100,
        incomplete_results: bool = False,
        items: Optional[List[Package]] = None
    ) -> SearchResult:
        """Create a mock search result."""
        return SearchResult(
            total_count=total_count,
            incomplete_results=incomplete_results,
            items=items or [TestMockHelpers.create_mock_package()]
        )
    
    @staticmethod
    def create_mock_tool_response(
        success: bool = True,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        rate_limit_info: Optional[RateLimitInfo] = None
    ) -> Dict[str, Any]:
        """Create a mock tool response."""
        return {
            "success": success,
            "data": data,
            "error": error,
            "rate_limit_info": rate_limit_info and rate_limit_info.dict()
        }
    
    @staticmethod
    def create_mock_rate_limit_headers(
        limit: int = 60,
        remaining: int = 59,
        reset: int = 1234567890
    ) -> Dict[str, str]:
        """Create mock rate limit headers."""
        return {
            "x-ratelimit-limit": str(limit),
            "x-ratelimit-remaining": str(remaining),
            "x-ratelimit-reset": str(reset)
        }
    
    @staticmethod
    def create_mock_json_response(
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a mock JSON response."""
        return json.dumps(data or {"success": True})
    
    @staticmethod
    def create_mock_error_response(
        error: str = "Test error",
        status_code: int = 400
    ) -> Dict[str, Any]:
        """Create a mock error response."""
        return {
            "success": False,
            "error": error,
            "status_code": status_code
        }
    
    @staticmethod
    def create_mock_success_response(
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a mock success response."""
        return {
            "success": True,
            "data": data or {}
        }
    
    @staticmethod
    def create_mock_pagination_data(
        page: int = 1,
        per_page: int = 10,
        total_pages: int = 10,
        total_items: int = 100,
        has_next: bool = True,
        has_prev: bool = False
    ) -> Dict[str, Any]:
        """Create mock pagination data."""
        return {
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_items": total_items,
            "has_next": has_next,
            "has_prev": has_prev
        }
    
    @staticmethod
    def create_mock_filter_data(
        applied: Optional[List[str]] = None,
        available: Optional[List[str]] = None,
        counts: Optional[Dict[str, Dict[str, int]]] = None
    ) -> Dict[str, Any]:
        """Create mock filter data."""
        return {
            "applied": applied or [],
            "available": available or ["language", "platform", "license"],
            "counts": counts or {
                "language": {"JavaScript": 100, "Python": 80, "Java": 60},
                "platform": {"npm": 150, "pypi": 90},
                "license": {"MIT": 120, "Apache-2.0": 70}
            }
        }
    
    @staticmethod
    def create_mock_sorting_data(
        by: str = "stars",
        order: str = "desc",
        available: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create mock sorting data."""
        return {
            "by": by,
            "order": order,
            "available": available or ["stars", "name", "updated_at", "created_at"]
        }
    
    @staticmethod
    def create_mock_aggregation_data(
        data: Optional[Dict[str, Dict[str, int]]] = None
    ) -> Dict[str, Any]:
        """Create mock aggregation data."""
        return data or {
            "language": {"JavaScript": 100, "Python": 80, "Java": 60},
            "platform": {"npm": 150, "pypi": 90},
            "license": {"MIT": 120, "Apache-2.0": 70}
        }
    
    @staticmethod
    def create_mock_statistics_data(
        count: int = 100,
        sum_val: float = 1000.0,
        average: float = 10.0,
        min_val: float = 1.0,
        max_val: float = 50.0,
        median: float = 8.5
    ) -> Dict[str, Any]:
        """Create mock statistics data."""
        return {
            "count": count,
            "sum": sum_val,
            "average": average,
            "min": min_val,
            "max": max_val,
            "median": median
        }
    
    @staticmethod
    def create_mock_graph_data(
        nodes: Optional[List[Dict[str, Any]]] = None,
        edges: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create mock graph data."""
        return {
            "nodes": nodes or [
                {"id": 1, "label": "React"},
                {"id": 2, "label": "ReactDOM"},
                {"id": 3, "label": "JavaScript"}
            ],
            "edges": edges or [
                {"source": 1, "target": 2},
                {"source": 1, "target": 3}
            ]
        }
    
    @staticmethod
    def create_mock_tree_data(
        root: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create mock tree data."""
        return {
            "root": root or {
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
    
    @staticmethod
    def create_mock_matrix_data(
        rows: Optional[List[str]] = None,
        columns: Optional[List[str]] = None,
        data: Optional[List[List[Union[int, float]]]] = None
    ) -> Dict[str, Any]:
        """Create mock matrix data."""
        return {
            "rows": rows or ["Package A", "Package B", "Package C"],
            "columns": columns or ["Stars", "Forks", "Issues"],
            "data": data or [
                [100, 50, 10],
                [200, 75, 15],
                [150, 60, 8]
            ]
        }
    
    @staticmethod
    def create_mock_chart_data(
        chart_type: str = "bar",
        title: str = "Package Statistics",
        labels: Optional[List[str]] = None,
        datasets: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create mock chart data."""
        return {
            "type": chart_type,
            "title": title,
            "data": {
                "labels": labels or ["Jan", "Feb", "Mar", "Apr", "May"],
                "datasets": datasets or [
                    {
                        "label": "Downloads",
                        "data": [1000, 1500, 1200, 1800, 2000]
                    }
                ]
            }
        }
    
    @staticmethod
    def create_mock_timeline_data(
        events: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create mock timeline data."""
        return {
            "events": events or [
                {
                    "date": "2024-01-01",
                    "title": "Project Started",
                    "description": "Initial project setup and planning"
                },
                {
                    "date": "2024-02-15",
                    "title": "Version 1.0 Released",
                    "description": "First stable version released"
                },
                {
                    "date": "2024-03-20",
                    "title": "Version 1.1 Released",
                    "description": "Bug fixes and performance improvements"
                }
            ]
        }
    
    @staticmethod
    def create_mock_geo_data(
        features: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create mock geographic data."""
        return {
            "type": "FeatureCollection",
            "features": features or [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-122.4194, 37.7749]
                    },
                    "properties": {
                        "name": "San Francisco",
                        "value": 100
                    }
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-74.0060, 40.7128]
                    },
                    "properties": {
                        "name": "New York",
                        "value": 150
                    }
                }
            ]
        }
    
    @staticmethod
    def create_mock_network_data(
        nodes: Optional[List[Dict[str, Any]]] = None,
        links: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create mock network data."""
        return {
            "nodes": nodes or [
                {"id": 1, "group": 1},
                {"id": 2, "group": 1},
                {"id": 3, "group": 2}
            ],
            "links": links or [
                {"source": 1, "target": 2},
                {"source": 1, "target": 3}
            ]
        }
    
    @staticmethod
    def create_mock_calendar_data(
        year: int = 2024,
        months: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create mock calendar data."""
        return {
            "year": year,
            "months": months or [
                {
                    "name": "January",
                    "weeks": [
                        {
                            "days": [
                                {
                                    "date": "2024-01-01",
                                    "events": []
                                },
                                {
                                    "date": "2024-01-02",
                                    "events": [
                                        {
                                            "title": "Event 1",
                                            "description": "Test event"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    
    @staticmethod
    def create_mock_code_data(
        language: str = "python",
        content: str = "print('Hello, World!')",
        highlighted: str = "<span class='keyword'>print</span><span class='punctuation'>(</span><span class='string'>'Hello, World!'</span><span class='punctuation'>)</span>"
    ) -> Dict[str, Any]:
        """Create mock code data."""
        return {
            "language": language,
            "content": content,
            "highlighted": highlighted
        }
    
    @staticmethod
    def create_mock_file_data(
        name: str = "example.py",
        size: int = 1024,
        file_type: str = "text/x-python",
        content: str = "print('Hello, World!')"
    ) -> Dict[str, Any]:
        """Create mock file data."""
        return {
            "name": name,
            "size": size,
            "type": file_type,
            "content": content
        }
    
    @staticmethod
    def create_mock_image_data(
        url: str = "https://example.com/image.jpg",
        width: int = 800,
        height: int = 600,
        format: str = "jpeg",
        size: int = 102400
    ) -> Dict[str, Any]:
        """Create mock image data."""
        return {
            "url": url,
            "width": width,
            "height": height,
            "format": format,
            "size": size
        }
    
    @staticmethod
    def create_mock_audio_data(
        url: str = "https://example.com/audio.mp3",
        duration: int = 180,
        format: str = "mp3",
        size: int = 2048000
    ) -> Dict[str, Any]:
        """Create mock audio data."""
        return {
            "url": url,
            "duration": duration,
            "format": format,
            "size": size
        }
    
    @staticmethod
    def create_mock_video_data(
        url: str = "https://example.com/video.mp4",
        duration: int = 300,
        format: str = "mp4",
        size: int = 10485760,
        resolution: str = "1920x1080"
    ) -> Dict[str, Any]:
        """Create mock video data."""
        return {
            "url": url,
            "duration": duration,
            "format": format,
            "size": size,
            "resolution": resolution
        }
    
    @staticmethod
    def create_mock_document_data(
        title: str = "Example Document",
        author: str = "John Doe",
        pages: int = 10,
        format: str = "pdf",
        size: int = 512000
    ) -> Dict[str, Any]:
        """Create mock document data."""
        return {
            "title": title,
            "author": author,
            "pages": pages,
            "format": format,
            "size": size
        }
    
    @staticmethod
    def create_mock_archive_data(
        name: str = "example.tar.gz",
        size: int = 1024000,
        format: str = "tar.gz",
        files: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create mock archive data."""
        return {
            "name": name,
            "size": size,
            "format": format,
            "files": files or [
                {"name": "file1.txt", "size": 1024},
                {"name": "file2.txt", "size": 2048}
            ]
        }
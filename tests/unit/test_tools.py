"""
Unit tests for the Libraries.io MCP Server tools.

This module contains unit tests for the tool functions used in the Libraries.io MCP Server.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, Optional

from src.libraries_io_mcp.tools import (
    get_platforms_tool,
    get_package_tool,
    get_package_versions_tool,
    get_package_dependencies_tool,
    get_package_dependents_tool,
    search_packages_tool,
    get_user_tool,
    get_user_packages_tool,
    get_organization_tool,
    get_organization_packages_tool,
    get_repository_tool,
    ToolsError
)
from src.libraries_io_mcp.client import LibrariesIOClient
from src.libraries_io_mcp.models import (
    Platform, Package, PackageVersion, Dependency, Repository,
    User, Organization, SearchResult
)
from tests.test_utils import MockDataGenerator


class TestGetPlatformsTool:
    """Test suite for get_platforms_tool function."""

    @pytest.mark.asyncio
    async def test_get_platforms_tool_success(self):
        """Test successful get_platforms_tool execution."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_platforms.return_value = [
            Platform(name="npm", project_count=2000000, homepage="https://www.npmjs.com/", color="#cb3837"),
            Platform(name="pypi", project_count=500000, homepage="https://pypi.org/", color="#3776ab")
        ]
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            result = await get_platforms_tool({})
            
            # Verify result
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["name"] == "npm"
            assert result[1]["name"] == "pypi"
            
            # Verify client was called
            mock_client.get_platforms.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_platforms_tool_with_client(self):
        """Test get_platforms_tool with provided client."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_platforms.return_value = [
            Platform(name="npm", project_count=2000000, homepage="https://www.npmjs.com/", color="#cb3837")
        ]
        
        # Call with client
        result = await get_platforms_tool({"client": mock_client})
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "npm"
        
        # Verify client was used
        mock_client.get_platforms.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_platforms_tool_client_error(self):
        """Test get_platforms_tool with client error."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_platforms.side_effect = Exception("API Error")
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            with pytest.raises(ToolsError, match="Failed to get platforms"):
                await get_platforms_tool({})

    @pytest.mark.asyncio
    async def test_get_platforms_tool_invalid_client(self):
        """Test get_platforms_tool with invalid client."""
        # Call with invalid client
        with pytest.raises(ToolsError, match="Invalid client"):
            await get_platforms_tool({"client": "invalid_client"})


class TestGetPackageTool:
    """Test suite for get_package_tool function."""

    @pytest.mark.asyncio
    async def test_get_package_tool_success(self):
        """Test successful get_package_tool execution."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_package.return_value = Package(
            name="react",
            platform="npm",
            description="A JavaScript library for building user interfaces",
            homepage="https://reactjs.org/",
            repository_url="https://github.com/facebook/react",
            language="JavaScript",
            keywords=["ui", "javascript", "frontend"],
            licenses="MIT",
            latest_release_number="18.2.0",
            latest_release_published_at=MockDataGenerator.generate_datetime(),
            stars=200000,
            forks=40000,
            watchers=5000,
            dependent_repositories_count=1000000,
            rank=1
        )
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            result = await get_package_tool({
                "platform": "npm",
                "name": "react"
            })
            
            # Verify result
            assert isinstance(result, dict)
            assert result["name"] == "react"
            assert result["platform"] == "npm"
            assert result["description"] == "A JavaScript library for building user interfaces"
            
            # Verify client was called
            mock_client.get_package.assert_called_once_with("npm", "react")

    @pytest.mark.asyncio
    async def test_get_package_tool_with_client(self):
        """Test get_package_tool with provided client."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_package.return_value = Package(
            name="vue",
            platform="npm",
            description="The Progressive JavaScript Framework"
        )
        
        # Call with client
        result = await get_package_tool({
            "platform": "npm",
            "name": "vue",
            "client": mock_client
        })
        
        # Verify result
        assert isinstance(result, dict)
        assert result["name"] == "vue"
        assert result["platform"] == "npm"
        
        # Verify client was used
        mock_client.get_package.assert_called_once_with("npm", "vue")

    @pytest.mark.asyncio
    async def test_get_package_tool_missing_params(self):
        """Test get_package_tool with missing parameters."""
        with pytest.raises(ToolsError, match="Missing required parameters"):
            await get_package_tool({})

    @pytest.mark.asyncio
    async def test_get_package_tool_invalid_platform(self):
        """Test get_package_tool with invalid platform."""
        with pytest.raises(ToolsError, match="Invalid platform"):
            await get_package_tool({
                "platform": "invalid_platform",
                "name": "react"
            })

    @pytest.mark.asyncio
    async def test_get_package_tool_client_error(self):
        """Test get_package_tool with client error."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_package.side_effect = Exception("API Error")
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            with pytest.raises(ToolsError, match="Failed to get package"):
                await get_package_tool({
                    "platform": "npm",
                    "name": "react"
                })

    @pytest.mark.asyncio
    async def test_get_package_tool_invalid_client(self):
        """Test get_package_tool with invalid client."""
        with pytest.raises(ToolsError, match="Invalid client"):
            await get_package_tool({
                "platform": "npm",
                "name": "react",
                "client": "invalid_client"
            })


class TestGetPackageVersionsTool:
    """Test suite for get_package_versions_tool function."""

    @pytest.mark.asyncio
    async def test_get_package_versions_tool_success(self):
        """Test successful get_package_versions_tool execution."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_package_versions.return_value = [
            PackageVersion(
                number="18.2.0",
                published_at=MockDataGenerator.generate_datetime(),
                spdx_expression="MIT",
                original_license="MIT",
                status="active"
            ),
            PackageVersion(
                number="18.1.0",
                published_at=MockDataGenerator.generate_datetime(),
                spdx_expression="MIT",
                original_license="MIT",
                status="active"
            )
        ]
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            result = await get_package_versions_tool({
                "platform": "npm",
                "name": "react"
            })
            
            # Verify result
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["number"] == "18.2.0"
            assert result[1]["number"] == "18.1.0"
            
            # Verify client was called
            mock_client.get_package_versions.assert_called_once_with("npm", "react")

    @pytest.mark.asyncio
    async def test_get_package_versions_tool_with_client(self):
        """Test get_package_versions_tool with provided client."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_package_versions.return_value = [
            PackageVersion(number="1.0.0")
        ]
        
        # Call with client
        result = await get_package_versions_tool({
            "platform": "npm",
            "name": "vue",
            "client": mock_client
        })
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["number"] == "1.0.0"
        
        # Verify client was used
        mock_client.get_package_versions.assert_called_once_with("npm", "vue")

    @pytest.mark.asyncio
    async def test_get_package_versions_tool_missing_params(self):
        """Test get_package_versions_tool with missing parameters."""
        with pytest.raises(ToolsError, match="Missing required parameters"):
            await get_package_versions_tool({})

    @pytest.mark.asyncio
    async def test_get_package_versions_tool_invalid_platform(self):
        """Test get_package_versions_tool with invalid platform."""
        with pytest.raises(ToolsError, match="Invalid platform"):
            await get_package_versions_tool({
                "platform": "invalid_platform",
                "name": "react"
            })

    @pytest.mark.asyncio
    async def test_get_package_versions_tool_client_error(self):
        """Test get_package_versions_tool with client error."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_package_versions.side_effect = Exception("API Error")
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            with pytest.raises(ToolsError, match="Failed to get package versions"):
                await get_package_versions_tool({
                    "platform": "npm",
                    "name": "react"
                })


class TestGetPackageDependenciesTool:
    """Test suite for get_package_dependencies_tool function."""

    @pytest.mark.asyncio
    async def test_get_package_dependencies_tool_success(self):
        """Test successful get_package_dependencies_tool execution."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_package_dependencies.return_value = [
            Dependency(
                project=Package(
                    name="react-dom",
                    platform="npm",
                    description="React package for DOM rendering"
                ),
                requirement=">=16.0.0",
                kind="runtime",
                optional=False,
                development=False
            ),
            Dependency(
                project=Package(
                    name="scheduler",
                    platform="npm",
                    description="React package for scheduling"
                ),
                requirement=">=0.13.0",
                kind="runtime",
                optional=False,
                development=False
            )
        ]
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            result = await get_package_dependencies_tool({
                "platform": "npm",
                "name": "react"
            })
            
            # Verify result
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["project"]["name"] == "react-dom"
            assert result[1]["project"]["name"] == "scheduler"
            
            # Verify client was called
            mock_client.get_package_dependencies.assert_called_once_with("npm", "react")

    @pytest.mark.asyncio
    async def test_get_package_dependencies_tool_with_client(self):
        """Test get_package_dependencies_tool with provided client."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_package_dependencies.return_value = [
            Dependency(
                project=Package(name="axios", platform="npm"),
                requirement=">=1.0.0"
            )
        ]
        
        # Call with client
        result = await get_package_dependencies_tool({
            "platform": "npm",
            "name": "vue",
            "client": mock_client
        })
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["project"]["name"] == "axios"
        
        # Verify client was used
        mock_client.get_package_dependencies.assert_called_once_with("npm", "vue")

    @pytest.mark.asyncio
    async def test_get_package_dependencies_tool_missing_params(self):
        """Test get_package_dependencies_tool with missing parameters."""
        with pytest.raises(ToolsError, match="Missing required parameters"):
            await get_package_dependencies_tool({})

    @pytest.mark.asyncio
    async def test_get_package_dependencies_tool_invalid_platform(self):
        """Test get_package_dependencies_tool with invalid platform."""
        with pytest.raises(ToolsError, match="Invalid platform"):
            await get_package_dependencies_tool({
                "platform": "invalid_platform",
                "name": "react"
            })

    @pytest.mark.asyncio
    async def test_get_package_dependencies_tool_client_error(self):
        """Test get_package_dependencies_tool with client error."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_package_dependencies.side_effect = Exception("API Error")
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            with pytest.raises(ToolsError, match="Failed to get package dependencies"):
                await get_package_dependencies_tool({
                    "platform": "npm",
                    "name": "react"
                })


class TestGetPackageDependentsTool:
    """Test suite for get_package_dependents_tool function."""

    @pytest.mark.asyncio
    async def test_get_package_dependents_tool_success(self):
        """Test successful get_package_dependents_tool execution."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_package_dependents.return_value = [
            Package(
                name="my-app",
                platform="npm",
                description="My application using React"
            ),
            Package(
                name="another-app",
                platform="npm",
                description="Another application using React"
            )
        ]
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            result = await get_package_dependents_tool({
                "platform": "npm",
                "name": "react"
            })
            
            # Verify result
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["name"] == "my-app"
            assert result[1]["name"] == "another-app"
            
            # Verify client was called
            mock_client.get_package_dependents.assert_called_once_with("npm", "react")

    @pytest.mark.asyncio
    async def test_get_package_dependents_tool_with_client(self):
        """Test get_package_dependents_tool with provided client."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_package_dependents.return_value = [
            Package(name="vue-app", platform="npm")
        ]
        
        # Call with client
        result = await get_package_dependents_tool({
            "platform": "npm",
            "name": "vue",
            "client": mock_client
        })
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "vue-app"
        
        # Verify client was used
        mock_client.get_package_dependents.assert_called_once_with("npm", "vue")

    @pytest.mark.asyncio
    async def test_get_package_dependents_tool_missing_params(self):
        """Test get_package_dependents_tool with missing parameters."""
        with pytest.raises(ToolsError, match="Missing required parameters"):
            await get_package_dependents_tool({})

    @pytest.mark.asyncio
    async def test_get_package_dependents_tool_invalid_platform(self):
        """Test get_package_dependents_tool with invalid platform."""
        with pytest.raises(ToolsError, match="Invalid platform"):
            await get_package_dependents_tool({
                "platform": "invalid_platform",
                "name": "react"
            })

    @pytest.mark.asyncio
    async def test_get_package_dependents_tool_client_error(self):
        """Test get_package_dependents_tool with client error."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_package_dependents.side_effect = Exception("API Error")
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            with pytest.raises(ToolsError, match="Failed to get package dependents"):
                await get_package_dependents_tool({
                    "platform": "npm",
                    "name": "react"
                })


class TestSearchPackagesTool:
    """Test suite for search_packages_tool function."""

    @pytest.mark.asyncio
    async def test_search_packages_tool_success(self):
        """Test successful search_packages_tool execution."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.search_packages.return_value = SearchResult(
            total_count=100,
            packages=[
                Package(
                    name="react",
                    platform="npm",
                    description="A JavaScript library for building user interfaces"
                ),
                Package(
                    name="react-dom",
                    platform="npm",
                    description="React package for DOM rendering"
                )
            ]
        )
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            result = await search_packages_tool({
                "query": "react"
            })
            
            # Verify result
            assert isinstance(result, dict)
            assert result["total_count"] == 100
            assert len(result["packages"]) == 2
            assert result["packages"][0]["name"] == "react"
            assert result["packages"][1]["name"] == "react-dom"
            
            # Verify client was called
            mock_client.search_packages.assert_called_once_with("react")

    @pytest.mark.asyncio
    async def test_search_packages_tool_with_client(self):
        """Test search_packages_tool with provided client."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.search_packages.return_value = SearchResult(
            total_count=50,
            packages=[Package(name="vue", platform="npm")]
        )
        
        # Call with client
        result = await search_packages_tool({
            "query": "vue",
            "client": mock_client
        })
        
        # Verify result
        assert isinstance(result, dict)
        assert result["total_count"] == 50
        assert len(result["packages"]) == 1
        assert result["packages"][0]["name"] == "vue"
        
        # Verify client was used
        mock_client.search_packages.assert_called_once_with("vue")

    @pytest.mark.asyncio
    async def test_search_packages_tool_missing_params(self):
        """Test search_packages_tool with missing parameters."""
        with pytest.raises(ToolsError, match="Missing required parameters"):
            await search_packages_tool({})

    @pytest.mark.asyncio
    async def test_search_packages_tool_client_error(self):
        """Test search_packages_tool with client error."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.search_packages.side_effect = Exception("API Error")
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            with pytest.raises(ToolsError, match="Failed to search packages"):
                await search_packages_tool({
                    "query": "react"
                })


class TestGetUserTool:
    """Test suite for get_user_tool function."""

    @pytest.mark.asyncio
    async def test_get_user_tool_success(self):
        """Test successful get_user_tool execution."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_user.return_value = User(
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
            created_at=MockDataGenerator.generate_datetime(),
            updated_at=MockDataGenerator.generate_datetime()
        )
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            result = await get_user_tool({
                "username": "octocat"
            })
            
            # Verify result
            assert isinstance(result, dict)
            assert result["username"] == "octocat"
            assert result["name"] == "The Octocat"
            assert result["type"] == "User"
            
            # Verify client was called
            mock_client.get_user.assert_called_once_with("octocat")

    @pytest.mark.asyncio
    async def test_get_user_tool_with_client(self):
        """Test get_user_tool with provided client."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_user.return_value = User(
            username="testuser",
            name="Test User",
            type="User"
        )
        
        # Call with client
        result = await get_user_tool({
            "username": "testuser",
            "client": mock_client
        })
        
        # Verify result
        assert isinstance(result, dict)
        assert result["username"] == "testuser"
        assert result["name"] == "Test User"
        
        # Verify client was used
        mock_client.get_user.assert_called_once_with("testuser")

    @pytest.mark.asyncio
    async def test_get_user_tool_missing_params(self):
        """Test get_user_tool with missing parameters."""
        with pytest.raises(ToolsError, match="Missing required parameters"):
            await get_user_tool({})

    @pytest.mark.asyncio
    async def test_get_user_tool_client_error(self):
        """Test get_user_tool with client error."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_user.side_effect = Exception("API Error")
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            with pytest.raises(ToolsError, match="Failed to get user"):
                await get_user_tool({
                    "username": "octocat"
                })


class TestGetUserPackagesTool:
    """Test suite for get_user_packages_tool function."""

    @pytest.mark.asyncio
    async def test_get_user_packages_tool_success(self):
        """Test successful get_user_packages_tool execution."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_user_packages.return_value = [
            Package(
                name="hello-world",
                platform="npm",
                description="A simple hello world package"
            ),
            Package(
                name="test-package",
                platform="npm",
                description="A test package"
            )
        ]
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            result = await get_user_packages_tool({
                "username": "octocat"
            })
            
            # Verify result
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["name"] == "hello-world"
            assert result[1]["name"] == "test-package"
            
            # Verify client was called
            mock_client.get_user_packages.assert_called_once_with("octocat")

    @pytest.mark.asyncio
    async def test_get_user_packages_tool_with_client(self):
        """Test get_user_packages_tool with provided client."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_user_packages.return_value = [
            Package(name="user-package", platform="npm")
        ]
        
        # Call with client
        result = await get_user_packages_tool({
            "username": "testuser",
            "client": mock_client
        })
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "user-package"
        
        # Verify client was used
        mock_client.get_user_packages.assert_called_once_with("testuser")

    @pytest.mark.asyncio
    async def test_get_user_packages_tool_missing_params(self):
        """Test get_user_packages_tool with missing parameters."""
        with pytest.raises(ToolsError, match="Missing required parameters"):
            await get_user_packages_tool({})

    @pytest.mark.asyncio
    async def test_get_user_packages_tool_client_error(self):
        """Test get_user_packages_tool with client error."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_user_packages.side_effect = Exception("API Error")
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            with pytest.raises(ToolsError, match="Failed to get user packages"):
                await get_user_packages_tool({
                    "username": "octocat"
                })


class TestGetOrganizationTool:
    """Test suite for get_organization_tool function."""

    @pytest.mark.asyncio
    async def test_get_organization_tool_success(self):
        """Test successful get_organization_tool execution."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_organization.return_value = Organization(
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
            created_at=MockDataGenerator.generate_datetime(),
            updated_at=MockDataGenerator.generate_datetime()
        )
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            result = await get_organization_tool({
                "name": "github"
            })
            
            # Verify result
            assert isinstance(result, dict)
            assert result["name"] == "github"
            assert result["type"] == "Organization"
            assert result["company"] == "GitHub"
            
            # Verify client was called
            mock_client.get_organization.assert_called_once_with("github")

    @pytest.mark.asyncio
    async def test_get_organization_tool_with_client(self):
        """Test get_organization_tool with provided client."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_organization.return_value = Organization(
            name="test-org",
            type="Organization"
        )
        
        # Call with client
        result = await get_organization_tool({
            "name": "test-org",
            "client": mock_client
        })
        
        # Verify result
        assert isinstance(result, dict)
        assert result["name"] == "test-org"
        assert result["type"] == "Organization"
        
        # Verify client was used
        mock_client.get_organization.assert_called_once_with("test-org")

    @pytest.mark.asyncio
    async def test_get_organization_tool_missing_params(self):
        """Test get_organization_tool with missing parameters."""
        with pytest.raises(ToolsError, match="Missing required parameters"):
            await get_organization_tool({})

    @pytest.mark.asyncio
    async def test_get_organization_tool_client_error(self):
        """Test get_organization_tool with client error."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_organization.side_effect = Exception("API Error")
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            with pytest.raises(ToolsError, match="Failed to get organization"):
                await get_organization_tool({
                    "name": "github"
                })


class TestGetOrganizationPackagesTool:
    """Test suite for get_organization_packages_tool function."""

    @pytest.mark.asyncio
    async def test_get_organization_packages_tool_success(self):
        """Test successful get_organization_packages_tool execution."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_organization_packages.return_value = [
            Package(
                name="hello-world",
                platform="npm",
                description="A simple hello world package"
            ),
            Package(
                name="test-package",
                platform="npm",
                description="A test package"
            )
        ]
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            result = await get_organization_packages_tool({
                "name": "github"
            })
            
            # Verify result
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["name"] == "hello-world"
            assert result[1]["name"] == "test-package"
            
            # Verify client was called
            mock_client.get_organization_packages.assert_called_once_with("github")

    @pytest.mark.asyncio
    async def test_get_organization_packages_tool_with_client(self):
        """Test get_organization_packages_tool with provided client."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_organization_packages.return_value = [
            Package(name="org-package", platform="npm")
        ]
        
        # Call with client
        result = await get_organization_packages_tool({
            "name": "test-org",
            "client": mock_client
        })
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "org-package"
        
        # Verify client was used
        mock_client.get_organization_packages.assert_called_once_with("test-org")

    @pytest.mark.asyncio
    async def test_get_organization_packages_tool_missing_params(self):
        """Test get_organization_packages_tool with missing parameters."""
        with pytest.raises(ToolsError, match="Missing required parameters"):
            await get_organization_packages_tool({})

    @pytest.mark.asyncio
    async def test_get_organization_packages_tool_client_error(self):
        """Test get_organization_packages_tool with client error."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_organization_packages.side_effect = Exception("API Error")
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            with pytest.raises(ToolsError, match="Failed to get organization packages"):
                await get_organization_packages_tool({
                    "name": "github"
                })


class TestGetRepositoryTool:
    """Test suite for get_repository_tool function."""

    @pytest.mark.asyncio
    async def test_get_repository_tool_success(self):
        """Test successful get_repository_tool execution."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_repository.return_value = Repository(
            name="react",
            platform="GitHub",
            url="https://github.com/facebook/react",
            homepage="https://reactjs.org/",
            description="A JavaScript library for building user interfaces",
            language="JavaScript",
            stars=200000,
            forks=40000,
            watchers=5000,
            created_at=MockDataGenerator.generate_datetime(),
            last_activity_at=MockDataGenerator.generate_datetime(),
            last_pushed_at=MockDataGenerator.generate_datetime()
        )
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            result = await get_repository_tool({
                "platform": "github",
                "url": "https://github.com/facebook/react"
            })
            
            # Verify result
            assert isinstance(result, dict)
            assert result["name"] == "react"
            assert result["platform"] == "GitHub"
            assert result["url"] == "https://github.com/facebook/react"
            assert result["description"] == "A JavaScript library for building user interfaces"
            
            # Verify client was called
            mock_client.get_repository.assert_called_once_with("github", "https://github.com/facebook/react")

    @pytest.mark.asyncio
    async def test_get_repository_tool_with_client(self):
        """Test get_repository_tool with provided client."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_repository.return_value = Repository(
            name="vue",
            platform="GitHub",
            url="https://github.com/vuejs/vue"
        )
        
        # Call with client
        result = await get_repository_tool({
            "platform": "github",
            "url": "https://github.com/vuejs/vue",
            "client": mock_client
        })
        
        # Verify result
        assert isinstance(result, dict)
        assert result["name"] == "vue"
        assert result["platform"] == "GitHub"
        assert result["url"] == "https://github.com/vuejs/vue"
        
        # Verify client was used
        mock_client.get_repository.assert_called_once_with("github", "https://github.com/vuejs/vue")

    @pytest.mark.asyncio
    async def test_get_repository_tool_missing_params(self):
        """Test get_repository_tool with missing parameters."""
        with pytest.raises(ToolsError, match="Missing required parameters"):
            await get_repository_tool({})

    @pytest.mark.asyncio
    async def test_get_repository_tool_invalid_platform(self):
        """Test get_repository_tool with invalid platform."""
        with pytest.raises(ToolsError, match="Invalid platform for repository"):
            await get_repository_tool({
                "platform": "invalid_platform",
                "url": "https://github.com/facebook/react"
            })

    @pytest.mark.asyncio
    async def test_get_repository_tool_invalid_url(self):
        """Test get_repository_tool with invalid URL."""
        with pytest.raises(ToolsError, match="GitHub repository URL must start with https://github.com/"):
            await get_repository_tool({
                "platform": "github",
                "url": "https://invalid.url/react"
            })

    @pytest.mark.asyncio
    async def test_get_repository_tool_invalid_format(self):
        """Test get_repository_tool with invalid URL format."""
        with pytest.raises(ToolsError, match="Invalid GitHub repository URL format"):
            await get_repository_tool({
                "platform": "github",
                "url": "https://github.com/invalid"
            })

    @pytest.mark.asyncio
    async def test_get_repository_tool_client_error(self):
        """Test get_repository_tool with client error."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_repository.side_effect = Exception("API Error")
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            with pytest.raises(ToolsError, match="Failed to get repository"):
                await get_repository_tool({
                    "platform": "github",
                    "url": "https://github.com/facebook/react"
                })


class TestToolsError:
    """Test suite for ToolsError class."""

    def test_tools_error_creation(self):
        """Test ToolsError creation."""
        error = ToolsError("Test error message")
        
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_tools_error_with_cause(self):
        """Test ToolsError with cause."""
        original_error = ValueError("Original error")
        error = ToolsError("Test error", cause=original_error)
        
        assert str(error) == "Test error"
        assert error.__cause__ is original_error

    def test_tools_error_with_params(self):
        """Test ToolsError with parameters."""
        error = ToolsError("Missing {param}", param="required")
        
        assert str(error) == "Missing required"


class TestToolsIntegration:
    """Test suite for tools integration."""

    @pytest.mark.asyncio
    async def test_tools_with_rate_limiting(self):
        """Test tools with rate limiting."""
        from src.libraries_io_mcp.utils import RateLimiter
        
        # Create rate limiter
        rate_limiter = RateLimiter(limit=5, window_seconds=60)
        
        # Mock client with rate limiting
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_platforms.return_value = [
            Platform(name="npm", project_count=2000000, homepage="https://www.npmjs.com/", color="#cb3837")
        ]
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            # Call tool multiple times
            for i in range(3):
                result = await get_platforms_tool({
                    "client": mock_client,
                    "_rate_limiter": rate_limiter
                })
                assert len(result) == 1
            
            # Verify rate limiter was used
            assert rate_limiter.tokens < 5

    @pytest.mark.asyncio
    async def test_tools_with_caching(self):
        """Test tools with caching."""
        from src.libraries_io_mcp.utils import MemoryCache
        
        # Create cache
        cache = MemoryCache(default_ttl=300, max_size=100)
        
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_package.return_value = Package(
            name="react",
            platform="npm",
            description="A JavaScript library for building user interfaces"
        )
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            # Call tool twice
            result1 = await get_package_tool({
                "platform": "npm",
                "name": "react",
                "client": mock_client,
                "_cache": cache
            })
            
            result2 = await get_package_tool({
                "platform": "npm",
                "name": "react",
                "client": mock_client,
                "_cache": cache
            })
            
            # Verify results are the same
            assert result1 == result2
            
            # Verify cache was used
            assert mock_client.get_package.call_count == 1

    @pytest.mark.asyncio
    async def test_tools_with_retry(self):
        """Test tools with retry."""
        from src.libraries_io_mcp.utils import RetryHandler
        
        # Create retry handler
        retry_handler = RetryHandler(max_retries=2, base_delay=0.1)
        
        # Mock client with retry
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_package.side_effect = [
            Exception("First failure"),
            Package(
                name="react",
                platform="npm",
                description="A JavaScript library for building user interfaces"
            )
        ]
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            # Call tool with retry
            result = await get_package_tool({
                "platform": "npm",
                "name": "react",
                "client": mock_client,
                "_retry_handler": retry_handler
            })
            
            # Verify result
            assert result["name"] == "react"
            assert result["platform"] == "npm"
            
            # Verify retry was used
            assert mock_client.get_package.call_count == 2

    @pytest.mark.asyncio
    async def test_tools_concurrent_execution(self):
        """Test tools concurrent execution."""
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_platforms.return_value = [
            Platform(name=f"platform-{i}", project_count=1000, homepage=f"https://platform{i}.com/", color="#123456")
            for i in range(5)
        ]
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            # Create concurrent tasks
            tasks = [
                get_platforms_tool({}) for _ in range(5)
            ]
            
            # Execute concurrently
            results = await asyncio.gather(*tasks)
            
            # Verify all results
            assert len(results) == 5
            for i, result in enumerate(results):
                assert len(result) == 5
                assert result[0]["name"] == f"platform-{i}"
            
            # Verify client was called multiple times
            assert mock_client.get_platforms.call_count == 5


class TestToolsPerformance:
    """Test suite for tools performance."""

    @pytest.mark.asyncio
    async def test_tools_performance(self):
        """Test tools performance."""
        import time
        
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_platforms.return_value = [
            Platform(name=f"platform-{i}", project_count=1000, homepage=f"https://platform{i}.com/", color="#123456")
            for i in range(10)
        ]
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            # Measure performance
            start_time = time.time()
            
            # Call tool
            result = await get_platforms_tool({})
            
            end_time = time.time()
            
            # Verify result
            assert len(result) == 10
            
            # Should be fast (less than 1 second)
            assert end_time - start_time < 1.0

    @pytest.mark.asyncio
    async def test_tools_large_result_performance(self):
        """Test tools performance with large results."""
        import time
        
        # Create large result
        large_result = [
            Platform(
                name=f"platform-{i}",
                project_count=1000000,
                homepage=f"https://platform{i}.com/",
                color="#123456",
                default_language="Python",
                package_type="library"
            )
            for i in range(100)
        ]
        
        # Mock client
        mock_client = AsyncMock(spec=LibrariesIOClient)
        mock_client.get_platforms.return_value = large_result
        
        # Mock client factory
        with patch('src.libraries_io_mcp.tools.create_client', return_value=mock_client):
            # Measure performance
            start_time = time.time()
            
            # Call tool
            result = await get_platforms_tool({})
            
            end_time = time.time()
            
            # Verify result
            assert len(result) == 100
            
            # Should be fast (less than 2 seconds)
            assert end_time - start_time < 2.0


if __name__ == "__main__":
    pytest.main([__file__])
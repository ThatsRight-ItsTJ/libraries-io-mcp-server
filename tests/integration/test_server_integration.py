"""
Integration tests for the Libraries.io MCP Server.

This module contains integration tests that test the entire MCP server functionality,
including the server, client, and tools working together.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, Optional

from src.libraries_io_mcp.server import LibrariesIOServer
from src.libraries_io_mcp.client import LibrariesIOClient
from src.libraries_io_mcp.tools import (
    get_platforms_tool, get_package_tool, search_packages_tool
)
from src.libraries_io_mcp.models import Platform, Package, SearchResult


class TestServerIntegration:
    """Test suite for server integration."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock(spec=LibrariesIOClient)
        client.get_platforms.return_value = [
            Platform(name="npm", project_count=2000000, homepage="https://www.npmjs.com/", color="#cb3837"),
            Platform(name="pypi", project_count=500000, homepage="https://pypi.org/", color="#3776ab")
        ]
        client.get_package.return_value = Package(
            name="react",
            platform="npm",
            description="A JavaScript library for building user interfaces",
            homepage="https://reactjs.org/",
            repository_url="https://github.com/facebook/react",
            language="JavaScript",
            keywords=["ui", "javascript", "frontend"],
            licenses="MIT",
            latest_release_number="18.2.0",
            latest_release_published_at="2023-01-01T00:00:00Z",
            stars=200000,
            forks=40000,
            watchers=5000,
            dependent_repositories_count=1000000,
            rank=1
        )
        client.search_packages.return_value = SearchResult(
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
        return client

    @pytest.fixture
    def server(self, mock_client):
        """Create a server instance for testing."""
        with patch('src.libraries_io_mcp.server.create_client', return_value=mock_client):
            server = LibrariesIOServer()
            yield server

    @pytest.mark.asyncio
    async def test_server_initialization(self, server):
        """Test server initialization."""
        assert server.name == "libraries-io"
        assert server.version == "1.0.0"
        assert server.description == "MCP server for Libraries.io"
        assert server.tools is not None
        assert len(server.tools) > 0

    @pytest.mark.asyncio
    async def test_server_list_tools(self, server):
        """Test server list tools functionality."""
        tools = await server.list_tools()
        
        assert tools is not None
        assert len(tools) > 0
        
        # Check that expected tools are present
        tool_names = [tool.name for tool in tools]
        assert "get_platforms" in tool_names
        assert "get_package" in tool_names
        assert "search_packages" in tool_names

    @pytest.mark.asyncio
    async def test_server_call_tool_get_platforms(self, server, mock_client):
        """Test server call tool with get_platforms."""
        # Mock the client's get_platforms method
        mock_client.get_platforms.return_value = [
            Platform(name="npm", project_count=2000000, homepage="https://www.npmjs.com/", color="#cb3837"),
            Platform(name="pypi", project_count=500000, homepage="https://pypi.org/", color="#3776ab")
        ]
        
        # Call the tool
        result = await server.call_tool("get_platforms", {})
        
        # Verify result
        assert result is not None
        assert "content" in result
        assert isinstance(result["content"], list)
        assert len(result["content"]) == 2
        assert result["content"][0]["name"] == "npm"
        assert result["content"][1]["name"] == "pypi"

    @pytest.mark.asyncio
    async def test_server_call_tool_get_package(self, server, mock_client):
        """Test server call tool with get_package."""
        # Mock the client's get_package method
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
            latest_release_published_at="2023-01-01T00:00:00Z",
            stars=200000,
            forks=40000,
            watchers=5000,
            dependent_repositories_count=1000000,
            rank=1
        )
        
        # Call the tool
        result = await server.call_tool("get_package", {
            "platform": "npm",
            "name": "react"
        })
        
        # Verify result
        assert result is not None
        assert "content" in result
        assert isinstance(result["content"], dict)
        assert result["content"]["name"] == "react"
        assert result["content"]["platform"] == "npm"
        assert result["content"]["description"] == "A JavaScript library for building user interfaces"

    @pytest.mark.asyncio
    async def test_server_call_tool_search_packages(self, server, mock_client):
        """Test server call tool with search_packages."""
        # Mock the client's search_packages method
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
        
        # Call the tool
        result = await server.call_tool("search_packages", {
            "query": "react"
        })
        
        # Verify result
        assert result is not None
        assert "content" in result
        assert isinstance(result["content"], dict)
        assert result["content"]["total_count"] == 100
        assert len(result["content"]["packages"]) == 2
        assert result["content"]["packages"][0]["name"] == "react"
        assert result["content"]["packages"][1]["name"] == "react-dom"

    @pytest.mark.asyncio
    async def test_server_call_tool_invalid_tool(self, server):
        """Test server call tool with invalid tool name."""
        with pytest.raises(Exception, match="Unknown tool"):
            await server.call_tool("invalid_tool", {})

    @pytest.mark.asyncio
    async def test_server_call_tool_missing_params(self, server):
        """Test server call tool with missing parameters."""
        with pytest.raises(Exception, match="Missing required parameters"):
            await server.call_tool("get_package", {})

    @pytest.mark.asyncio
    async def test_server_call_tool_invalid_params(self, server):
        """Test server call tool with invalid parameters."""
        with pytest.raises(Exception, match="Invalid platform"):
            await server.call_tool("get_package", {
                "platform": "invalid_platform",
                "name": "react"
            })

    @pytest.mark.asyncio
    async def test_server_call_tool_client_error(self, server, mock_client):
        """Test server call tool with client error."""
        # Mock the client to raise an error
        mock_client.get_package.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="Failed to get package"):
            await server.call_tool("get_package", {
                "platform": "npm",
                "name": "react"
            })

    @pytest.mark.asyncio
    async def test_server_call_tool_rate_limited(self, server, mock_client):
        """Test server call tool with rate limiting."""
        from src.libraries_io_mcp.utils import RateLimiter
        
        # Create rate limiter
        rate_limiter = RateLimiter(limit=1, window_seconds=60)
        
        # Mock the client's get_platforms method
        mock_client.get_platforms.return_value = [
            Platform(name="npm", project_count=2000000, homepage="https://www.npmjs.com/", color="#cb3837")
        ]
        
        # Call the tool with rate limiter
        result = await server.call_tool("get_platforms", {
            "_rate_limiter": rate_limiter
        })
        
        # Verify result
        assert result is not None
        assert "content" in result
        assert len(result["content"]) == 1
        assert result["content"][0]["name"] == "npm"

    @pytest.mark.asyncio
    async def test_server_call_tool_cached(self, server, mock_client):
        """Test server call tool with caching."""
        from src.libraries_io_mcp.utils import MemoryCache
        
        # Create cache
        cache = MemoryCache(default_ttl=300, max_size=100)
        
        # Mock the client's get_package method
        mock_client.get_package.return_value = Package(
            name="react",
            platform="npm",
            description="A JavaScript library for building user interfaces"
        )
        
        # Call the tool twice with cache
        result1 = await server.call_tool("get_package", {
            "platform": "npm",
            "name": "react",
            "_cache": cache
        })
        
        result2 = await server.call_tool("get_package", {
            "platform": "npm",
            "name": "react",
            "_cache": cache
        })
        
        # Verify results are the same
        assert result1 == result2
        
        # Verify client was called only once
        assert mock_client.get_package.call_count == 1

    @pytest.mark.asyncio
    async def test_server_call_tool_with_retry(self, server, mock_client):
        """Test server call tool with retry."""
        from src.libraries_io_mcp.utils import RetryHandler
        
        # Create retry handler
        retry_handler = RetryHandler(max_retries=2, base_delay=0.1)
        
        # Mock the client's get_package method to fail once then succeed
        mock_client.get_package.side_effect = [
            Exception("First failure"),
            Package(
                name="react",
                platform="npm",
                description="A JavaScript library for building user interfaces"
            )
        ]
        
        # Call the tool with retry
        result = await server.call_tool("get_package", {
            "platform": "npm",
            "name": "react",
            "_retry_handler": retry_handler
        })
        
        # Verify result
        assert result is not None
        assert "content" in result
        assert result["content"]["name"] == "react"
        assert result["content"]["platform"] == "npm"
        
        # Verify client was called twice
        assert mock_client.get_package.call_count == 2

    @pytest.mark.asyncio
    async def test_server_concurrent_calls(self, server, mock_client):
        """Test server concurrent calls."""
        # Mock the client's get_platforms method
        mock_client.get_platforms.return_value = [
            Platform(name=f"platform-{i}", project_count=1000, homepage=f"https://platform{i}.com/", color="#123456")
            for i in range(5)
        ]
        
        # Create concurrent tasks
        tasks = [
            server.call_tool("get_platforms", {}) for _ in range(5)
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all results
        assert len(results) == 5
        for i, result in enumerate(results):
            assert result is not None
            assert "content" in result
            assert len(result["content"]) == 5
            assert result["content"][0]["name"] == f"platform-{i}"

    @pytest.mark.asyncio
    async def test_server_large_response_handling(self, server, mock_client):
        """Test server handling of large responses."""
        # Create large response
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
        
        # Mock the client's get_platforms method
        mock_client.get_platforms.return_value = large_result
        
        # Call the tool
        result = await server.call_tool("get_platforms", {})
        
        # Verify result
        assert result is not None
        assert "content" in result
        assert len(result["content"]) == 100
        
        # Verify all platforms are present
        platform_names = [p["name"] for p in result["content"]]
        for i in range(100):
            assert f"platform-{i}" in platform_names

    @pytest.mark.asyncio
    async def test_server_error_handling(self, server, mock_client):
        """Test server error handling."""
        # Mock the client to raise an error
        mock_client.get_package.side_effect = Exception("API Error")
        
        # Call the tool and expect error
        with pytest.raises(Exception, match="Failed to get package"):
            await server.call_tool("get_package", {
                "platform": "npm",
                "name": "react"
            })

    @pytest.mark.asyncio
    async def test_server_tool_not_found(self, server):
        """Test server handling of unknown tools."""
        with pytest.raises(Exception, match="Unknown tool"):
            await server.call_tool("unknown_tool", {})

    @pytest.mark.asyncio
    async def test_server_tool_validation(self, server):
        """Test server tool parameter validation."""
        # Test with invalid platform
        with pytest.raises(Exception, match="Invalid platform"):
            await server.call_tool("get_package", {
                "platform": "invalid_platform",
                "name": "react"
            })
        
        # Test with missing parameters
        with pytest.raises(Exception, match="Missing required parameters"):
            await server.call_tool("get_package", {})
        
        # Test with empty parameters
        with pytest.raises(Exception, match="Missing required parameters"):
            await server.call_tool("get_package", {})

    @pytest.mark.asyncio
    async def test_server_tool_execution(self, server, mock_client):
        """Test server tool execution flow."""
        # Mock the client's get_package method
        mock_client.get_package.return_value = Package(
            name="react",
            platform="npm",
            description="A JavaScript library for building user interfaces"
        )
        
        # Call the tool
        result = await server.call_tool("get_package", {
            "platform": "npm",
            "name": "react"
        })
        
        # Verify result
        assert result is not None
        assert "content" in result
        assert isinstance(result["content"], dict)
        assert result["content"]["name"] == "react"
        assert result["content"]["platform"] == "npm"
        assert result["content"]["description"] == "A JavaScript library for building user interfaces"
        
        # Verify client was called
        mock_client.get_package.assert_called_once_with("npm", "react")

    @pytest.mark.asyncio
    async def test_server_tool_with_custom_client(self, server):
        """Test server tool with custom client."""
        # Create custom client
        custom_client = Mock(spec=LibrariesIOClient)
        custom_client.get_platforms.return_value = [
            Platform(name="custom", project_count=1000, homepage="https://custom.com/", color="#123456")
        ]
        
        # Call the tool with custom client
        result = await server.call_tool("get_platforms", {
            "client": custom_client
        })
        
        # Verify result
        assert result is not None
        assert "content" in result
        assert len(result["content"]) == 1
        assert result["content"][0]["name"] == "custom"
        
        # Verify custom client was used
        custom_client.get_platforms.assert_called_once()

    @pytest.mark.asyncio
    async def test_server_tool_with_invalid_client(self, server):
        """Test server tool with invalid client."""
        with pytest.raises(Exception, match="Invalid client"):
            await server.call_tool("get_platforms", {
                "client": "invalid_client"
            })

    @pytest.mark.asyncio
    async def test_server_tool_timeout(self, server, mock_client):
        """Test server tool timeout handling."""
        import asyncio
        
        # Mock the client to take a long time
        async def slow_get_package(platform, name):
            await asyncio.sleep(2.0)  # 2 seconds delay
            return Package(
                name=name,
                platform=platform,
                description="Slow response"
            )
        
        mock_client.get_package.side_effect = slow_get_package
        
        # Call the tool with timeout
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                server.call_tool("get_package", {
                    "platform": "npm",
                    "name": "react"
                }),
                timeout=1.0  # 1 second timeout
            )

    @pytest.mark.asyncio
    async def test_server_tool_cancellation(self, server, mock_client):
        """Test server tool cancellation handling."""
        # Mock the client to never return
        async def never_return(platform, name):
            await asyncio.sleep(10.0)  # 10 seconds delay
            return Package(
                name=name,
                platform=platform,
                description="Never returns"
            )
        
        mock_client.get_package.side_effect = never_return
        
        # Create task and cancel it
        task = asyncio.create_task(
            server.call_tool("get_package", {
                "platform": "npm",
                "name": "react"
            })
        )
        
        # Cancel after a short delay
        await asyncio.sleep(0.1)
        task.cancel()
        
        # Verify cancellation
        with pytest.raises(asyncio.CancelledError):
            await task


class TestClientServerIntegration:
    """Test suite for client-server integration."""

    @pytest.mark.asyncio
    async def test_client_server_interaction(self):
        """Test client-server interaction."""
        # Create server
        server = LibrariesIOServer()
        
        # Create client
        client = LibrariesIOClient(api_key="test_key")
        
        # Mock the client's methods
        with patch.object(client, 'get_platforms', return_value=[
            Platform(name="npm", project_count=2000000, homepage="https://www.npmjs.com/", color="#cb3837")
        ]):
            # Call server tool through client
            result = await server.call_tool("get_platforms", {
                "client": client
            })
            
            # Verify result
            assert result is not None
            assert "content" in result
            assert len(result["content"]) == 1
            assert result["content"][0]["name"] == "npm"
            
            # Verify client was called
            client.get_platforms.assert_called_once()

    @pytest.mark.asyncio
    async def test_client_server_error_propagation(self):
        """Test client-server error propagation."""
        # Create server
        server = LibrariesIOServer()
        
        # Create client
        client = LibrariesIOClient(api_key="test_key")
        
        # Mock the client to raise an error
        with patch.object(client, 'get_package', side_effect=Exception("API Error")):
            # Call server tool and expect error
            with pytest.raises(Exception, match="Failed to get package"):
                await server.call_tool("get_package", {
                    "platform": "npm",
                    "name": "react",
                    "client": client
                })

    @pytest.mark.asyncio
    async def test_client_server_rate_limiting(self):
        """Test client-server rate limiting."""
        from src.libraries_io_mcp.utils import RateLimiter
        
        # Create server
        server = LibrariesIOServer()
        
        # Create client
        client = LibrariesIOClient(api_key="test_key")
        
        # Create rate limiter
        rate_limiter = RateLimiter(limit=1, window_seconds=60)
        
        # Mock the client's methods
        with patch.object(client, 'get_platforms', return_value=[
            Platform(name="npm", project_count=2000000, homepage="https://www.npmjs.com/", color="#cb3837")
        ]):
            # Call server tool with rate limiter
            result = await server.call_tool("get_platforms", {
                "client": client,
                "_rate_limiter": rate_limiter
            })
            
            # Verify result
            assert result is not None
            assert "content" in result
            assert len(result["content"]) == 1
            assert result["content"][0]["name"] == "npm"
            
            # Verify rate limiter was used
            assert rate_limiter.tokens < 1

    @pytest.mark.asyncio
    async def test_client_server_caching(self):
        """Test client-server caching."""
        from src.libraries_io_mcp.utils import MemoryCache
        
        # Create server
        server = LibrariesIOServer()
        
        # Create client
        client = LibrariesIOClient(api_key="test_key")
        
        # Create cache
        cache = MemoryCache(default_ttl=300, max_size=100)
        
        # Mock the client's methods
        with patch.object(client, 'get_package', return_value=Package(
            name="react",
            platform="npm",
            description="A JavaScript library for building user interfaces"
        )):
            # Call server tool twice with cache
            result1 = await server.call_tool("get_package", {
                "platform": "npm",
                "name": "react",
                "client": client,
                "_cache": cache
            })
            
            result2 = await server.call_tool("get_package", {
                "platform": "npm",
                "name": "react",
                "client": client,
                "_cache": cache
            })
            
            # Verify results are the same
            assert result1 == result2
            
            # Verify client was called only once
            assert client.get_package.call_count == 1


class TestFullIntegration:
    """Test suite for full integration testing."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test full workflow from server to client to API."""
        # Create server
        server = LibrariesIOServer()
        
        # Create client
        client = LibrariesIOClient(api_key="test_key")
        
        # Mock the client's methods
        with patch.object(client, 'get_platforms', return_value=[
            Platform(name="npm", project_count=2000000, homepage="https://www.npmjs.com/", color="#cb3837"),
            Platform(name="pypi", project_count=500000, homepage="https://pypi.org/", color="#3776ab")
        ]), \
             patch.object(client, 'get_package', return_value=Package(
                 name="react",
                 platform="npm",
                 description="A JavaScript library for building user interfaces"
             )), \
             patch.object(client, 'search_packages', return_value=SearchResult(
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
             )):
            
            # Test get_platforms
            platforms_result = await server.call_tool("get_platforms", {
                "client": client
            })
            assert len(platforms_result["content"]) == 2
            
            # Test get_package
            package_result = await server.call_tool("get_package", {
                "platform": "npm",
                "name": "react",
                "client": client
            })
            assert package_result["content"]["name"] == "react"
            
            # Test search_packages
            search_result = await server.call_tool("search_packages", {
                "query": "react",
                "client": client
            })
            assert search_result["content"]["total_count"] == 100
            assert len(search_result["content"]["packages"]) == 2

    @pytest.mark.asyncio
    async def test_full_workflow_with_utilities(self):
        """Test full workflow with utilities."""
        from src.libraries_io_mcp.utils import RateLimiter, MemoryCache, RetryHandler
        
        # Create server
        server = LibrariesIOServer()
        
        # Create client
        client = LibrariesIOClient(api_key="test_key")
        
        # Create utilities
        rate_limiter = RateLimiter(limit=5, window_seconds=60)
        cache = MemoryCache(default_ttl=300, max_size=100)
        retry_handler = RetryHandler(max_retries=2, base_delay=0.1)
        
        # Mock the client's methods
        with patch.object(client, 'get_platforms', return_value=[
            Platform(name="npm", project_count=2000000, homepage="https://www.npmjs.com/", color="#cb3837")
        ]), \
             patch.object(client, 'get_package', side_effect=[
                 Exception("First failure"),
                 Package(
                     name="react",
                     platform="npm",
                     description="A JavaScript library for building user interfaces"
                 )
             ]):
            
            # Test with rate limiting
            platforms_result = await server.call_tool("get_platforms", {
                "client": client,
                "_rate_limiter": rate_limiter
            })
            assert len(platforms_result["content"]) == 1
            
            # Test with caching and retry
            package_result = await server.call_tool("get_package", {
                "platform": "npm",
                "name": "react",
                "client": client,
                "_cache": cache,
                "_retry_handler": retry_handler
            })
            assert package_result["content"]["name"] == "react"
            
            # Verify retry was used
            assert client.get_package.call_count == 2

    @pytest.mark.asyncio
    async def test_full_workflow_concurrent(self):
        """Test full workflow with concurrent requests."""
        # Create server
        server = LibrariesIOServer()
        
        # Create client
        client = LibrariesIOClient(api_key="test_key")
        
        # Mock the client's methods
        with patch.object(client, 'get_platforms', return_value=[
            Platform(name=f"platform-{i}", project_count=1000, homepage=f"https://platform{i}.com/", color="#123456")
            for i in range(5)
        ]), \
             patch.object(client, 'get_package', return_value=Package(
                 name="react",
                 platform="npm",
                 description="A JavaScript library for building user interfaces"
             )):
            
            # Create concurrent tasks
            tasks = [
                server.call_tool("get_platforms", {"client": client}) for _ in range(3)
            ] + [
                server.call_tool("get_package", {
                    "platform": "npm",
                    "name": "react",
                    "client": client
                }) for _ in range(2)
            ]
            
            # Execute concurrently
            results = await asyncio.gather(*tasks)
            
            # Verify all results
            assert len(results) == 5
            
            # Verify platform results
            for i in range(3):
                assert len(results[i]["content"]) == 5
                assert results[i]["content"][0]["name"] == f"platform-{i}"
            
            # Verify package results
            for i in range(3, 5):
                assert results[i]["content"]["name"] == "react"
                assert results[i]["content"]["platform"] == "npm"


if __name__ == "__main__":
    pytest.main([__file__])
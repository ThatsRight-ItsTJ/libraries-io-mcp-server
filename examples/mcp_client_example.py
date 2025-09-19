"""
MCP Client Example for Libraries.io MCP Server

This example demonstrates how to use the Libraries.io MCP Server
as an MCP client with various MCP tools and resources.
"""

import asyncio
import json
from typing import Dict, Any, List
from libraries_io_mcp.client import LibrariesIOClient
from libraries_io_mcp.server import create_server

class MCPClientExample:
    """Example MCP client for Libraries.io MCP Server."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = LibrariesIOClient(api_key=api_key)
        self.server = create_server()
    
    async def search_packages_example(self) -> Dict[str, Any]:
        """Example of searching for packages."""
        print("=== Searching for packages ===")
        
        # Search for React packages
        result = await self.client.search_packages(
            query="react",
            platforms=["npm"],
            page=1,
            per_page=5
        )
        
        if result.success:
            print(f"Found {len(result.data.get('packages', []))} packages:")
            for pkg in result.data.get('packages', []):
                print(f"  - {pkg.get('name', 'N/A')} ({pkg.get('platform', 'N/A')})")
                print(f"    Stars: {pkg.get('stars', 'N/A')}")
                print(f"    Description: {pkg.get('description', 'N/A')[:100]}...")
        else:
            print(f"Search failed: {result.error}")
        
        return result.data or {}
    
    async def get_package_info_example(self) -> Dict[str, Any]:
        """Example of getting package information."""
        print("\n=== Getting package information ===")
        
        # Get React package info
        result = await self.client.get_package_info(
            platform="npm",
            name="react",
            include_versions=True
        )
        
        if result.success:
            package = result.data
            print(f"Package: {package.get('name', 'N/A')}")
            print(f"Platform: {package.get('platform', 'N/A')}")
            print(f"Description: {package.get('description', 'N/A')}")
            print(f"Stars: {package.get('stars', 'N/A')}")
            print(f"Language: {package.get('language', 'N/A')}")
            print(f"Latest Version: {package.get('latest_version', 'N/A')}")
            print(f"Homepage: {package.get('homepage', 'N/A')}")
            
            if package.get('repository_url'):
                print(f"Repository: {package['repository_url']}")
        else:
            print(f"Package info failed: {result.error}")
        
        return result.data or {}
    
    async def get_package_dependencies_example(self) -> Dict[str, Any]:
        """Example of getting package dependencies."""
        print("\n=== Getting package dependencies ===")
        
        # Get React dependencies
        result = await self.client.get_package_dependencies(
            platform="npm",
            name="react"
        )
        
        if result.success:
            dependencies = result.data
            print(f"Found {len(dependencies)} dependencies:")
            
            # Group by dependency type
            runtime_deps = [d for d in dependencies if d.get('kind') != 'development']
            dev_deps = [d for d in dependencies if d.get('kind') == 'development']
            
            print(f"Runtime dependencies: {len(runtime_deps)}")
            print(f"Development dependencies: {len(dev_deps)}")
            
            print("\nTop runtime dependencies:")
            for dep in runtime_deps[:5]:
                print(f"  - {dep.get('name', 'N/A')} ({dep.get('platform', 'N/A')})")
            
            print("\nTop development dependencies:")
            for dep in dev_deps[:3]:
                print(f"  - {dep.get('name', 'N/A')} ({dep.get('platform', 'N/A')})")
        else:
            print(f"Dependencies failed: {result.error}")
        
        return result.data or {}
    
    async def get_trending_packages_example(self) -> Dict[str, Any]:
        """Example of getting trending packages."""
        print("\n=== Getting trending packages ===")
        
        # Get trending packages
        result = await self.client.get_trending_packages(
            platform="npm",
            page=1,
            per_page=10
        )
        
        if result.success:
            trending = result.data
            print(f"Top {len(trending.get('packages', []))} trending packages:")
            
            for i, pkg in enumerate(trending.get('packages', []), 1):
                print(f"{i}. {pkg.get('name', 'N/A')} ({pkg.get('platform', 'N/A')})")
                print(f"   Stars: {pkg.get('stars', 'N/A')}")
                print(f"   Language: {pkg.get('language', 'N/A')}")
        else:
            print(f"Trending packages failed: {result.error}")
        
        return result.data or {}
    
    async def compare_packages_example(self) -> Dict[str, Any]:
        """Example of comparing packages."""
        print("\n=== Comparing packages ===")
        
        # Compare popular JavaScript frameworks
        result = await self.client.compare_packages(
            packages=[
                {"platform": "npm", "name": "react"},
                {"platform": "npm", "name": "vue"},
                {"platform": "npm", "name": "angular"},
                {"platform": "npm", "name": "svelte"}
            ]
        )
        
        if result.success:
            comparison = result.data
            print(f"Comparison of {len(comparison.get('packages', []))} packages:")
            
            # Sort by stars
            sorted_packages = sorted(
                comparison.get('packages', []),
                key=lambda x: x.get('stars', 0),
                reverse=True
            )
            
            for pkg in sorted_packages:
                print(f"\n{pkg.get('name', 'N/A')} ({pkg.get('platform', 'N/A')}):")
                print(f"  Stars: {pkg.get('stars', 'N/A')}")
                print(f"  Language: {pkg.get('language', 'N/A')}")
                print(f"  Description: {pkg.get('description', 'N/A')[:100]}...")
        else:
            print(f"Comparison failed: {result.error}")
        
        return result.data or {}
    
    async def analyze_project_health_example(self) -> Dict[str, Any]:
        """Example of analyzing project health."""
        print("\n=== Analyzing project health ===")
        
        # Analyze a sample project
        result = await self.client.audit_project_dependencies(
            platform="npm",
            packages=[
                {"name": "react", "version": "^18.0.0"},
                {"name": "react-dom", "version": "^18.0.0"},
                {"name": "typescript", "version": "^4.9.0"},
                {"name": "@types/react", "version": "^18.0.0"},
                {"name": "webpack", "version": "^5.0.0"}
            ],
            check_duplicates=True,
            check_outdated=True,
            check_unused=False
        )
        
        if result.success:
            audit = result.data
            print(f"Project Health Analysis:")
            print(f"  Total Packages: {audit.get('total_packages', 'N/A')}")
            print(f"  Health Score: {audit.get('project_health_score', 'N/A')}/100")
            print(f"  Status: {audit.get('health_status', 'N/A')}")
            
            summary = audit.get('summary', {})
            print(f"\nIssues Found:")
            print(f"  - Duplicates: {summary.get('duplicates_count', 0)}")
            print(f"  - Outdated: {summary.get('outdated_count', 0)}")
            print(f"  - Security Issues: {summary.get('security_issues_count', 0)}")
            
            if summary.get('recommendations_count', 0) > 0:
                print(f"  - Recommendations: {summary.get('recommendations_count', 0)}")
        else:
            print(f"Project health analysis failed: {result.error}")
        
        return result.data or {}
    
    async def get_platform_statistics_example(self) -> Dict[str, Any]:
        """Example of getting platform statistics."""
        print("\n=== Getting platform statistics ===")
        
        # Get npm platform statistics
        result = await self.client.get_platform_stats(
            platform="npm",
            include_trending=True
        )
        
        if result.success:
            stats = result.data
            print(f"npm Platform Statistics:")
            print(f"  Project Count: {stats.get('project_count', 'N/A')}")
            print(f"  Homepage: {stats.get('homepage', 'N/A')}")
            print(f"  Default Language: {stats.get('default_language', 'N/A')}")
            print(f"  Package Type: {stats.get('package_type', 'N/A')}")
            
            if stats.get('sample_statistics'):
                sample_stats = stats['sample_statistics']
                print(f"\nSample Statistics (from {sample_stats.get('sample_size', 0)} packages):")
                print(f"  Total Stars: {sample_stats.get('total_stars', 'N/A')}")
                print(f"  Average Stars: {sample_stats.get('average_stars', 'N/A')}")
                print(f"  Most Common Language: {sample_stats.get('most_common_language', 'N/A')}")
            
            if stats.get('trending_packages'):
                print(f"\nTop Trending Packages:")
                for pkg in stats['trending_packages'][:3]:
                    print(f"  - {pkg.get('name', 'N/A')} ({pkg.get('stars', 'N/A')} stars)")
        else:
            print(f"Platform statistics failed: {result.error}")
        
        return result.data or {}
    
    async def run_all_examples(self):
        """Run all example functions."""
        print("Libraries.io MCP Server - Client Examples")
        print("=" * 50)
        
        try:
            # Run all examples
            await self.search_packages_example()
            await self.get_package_info_example()
            await self.get_package_dependencies_example()
            await self.get_trending_packages_example()
            await self.compare_packages_example()
            await self.analyze_project_health_example()
            await self.get_platform_statistics_example()
            
            print("\n" + "=" * 50)
            print("All examples completed successfully!")
            
        except Exception as e:
            print(f"Error running examples: {e}")
            raise
    
    async def close(self):
        """Close the client and server."""
        await self.client.close()
        if hasattr(self.server, 'close'):
            await self.server.close()

async def main():
    """Main function to run the MCP client examples."""
    # Get API key from environment
    api_key = input("Enter your Libraries.io API key (or press Enter to use environment variable): ").strip()
    
    if not api_key:
        api_key = input("Please enter your Libraries.io API key: ").strip()
    
    if not api_key:
        print("No API key provided. Please set LIBRARIES_IO_API_KEY environment variable.")
        return
    
    # Create and run client example
    client_example = MCPClientExample(api_key)
    
    try:
        await client_example.run_all_examples()
    finally:
        await client_example.close()

if __name__ == "__main__":
    asyncio.run(main())
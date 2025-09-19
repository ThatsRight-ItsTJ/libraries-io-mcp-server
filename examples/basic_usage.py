"""
Basic Usage Examples for Libraries.io MCP Server

This file demonstrates basic usage patterns for the Libraries.io MCP Server.
"""

import asyncio
import os
from libraries_io_mcp.client import LibrariesIOClient
from libraries_io_mcp.tools import (
    search_packages,
    get_package_info,
    get_package_versions,
    get_package_dependencies,
    get_trending_packages,
    get_popular_packages
)

async def main():
    """Basic usage examples."""
    
    # Initialize client
    api_key = os.getenv("LIBRARIES_IO_API_KEY")
    if not api_key:
        print("Please set LIBRARIES_IO_API_KEY environment variable")
        return
    
    client = LibrariesIOClient(api_key=api_key)
    
    print("=== Basic Usage Examples ===\n")
    
    # Example 1: Search for packages
    print("1. Searching for packages...")
    try:
        search_result = await search_packages(
            query="react",
            platforms=["npm"],
            per_page=5
        )
        
        if search_result.success:
            if search_result.data:
                packages = search_result.data.get('packages', [])
                print(f"Found {len(packages)} packages:")
                for pkg in packages:
                    print(f"  - {pkg.get('name', 'N/A')} ({pkg.get('platform', 'N/A')}) - {pkg.get('description', 'N/A')}")
            else:
                print("No search data returned")
        else:
            print(f"Search failed: {search_result.error}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Get package information
    print("2. Getting package information...")
    try:
        package_result = await get_package_info(
            platform="npm",
            name="react",
            include_versions=True
        )
        
        if package_result.success:
            package = package_result.data
            if package:
                print(f"Package: {package.get('name', 'N/A')}")
                print(f"Platform: {package.get('platform', 'N/A')}")
                print(f"Description: {package.get('description', 'N/A')}")
                print(f"Stars: {package.get('stars', 'N/A')}")
                print(f"Latest Version: {package.get('latest_version', 'N/A')}")
                print(f"Language: {package.get('language', 'N/A')}")
                print(f"Homepage: {package.get('homepage', 'N/A')}")
            else:
                print("No package data returned")
        else:
            print(f"Package info failed: {package_result.error}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Get package versions
    print("3. Getting package versions...")
    try:
        versions_result = await get_package_versions(
            platform="npm",
            name="react"
        )
        
        if versions_result.success:
            versions = versions_result.data
            if versions:
                print(f"Found {len(versions)} versions:")
                for version in list(versions)[:5]:  # Show first 5 versions
                    print(f"  - {version.get('number', 'N/A')} (published: {version.get('published_at', 'N/A')})" if isinstance(version, dict) else f"  - {version}")
            else:
                print("No versions data returned")
        else:
            print(f"Versions failed: {versions_result.error}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 4: Get package dependencies
    print("4. Getting package dependencies...")
    try:
        deps_result = await get_package_dependencies(
            platform="npm",
            name="react"
        )
        
        if deps_result.success:
            dependencies = deps_result.data
            if dependencies:
                print(f"Found {len(dependencies)} dependencies:")
                for dep in list(dependencies)[:5]:  # Show first 5 dependencies
                    print(f"  - {dep.get('name', 'N/A')} ({dep.get('platform', 'N/A')}) - {dep.get('kind', 'N/A')}" if isinstance(dep, dict) else f"  - {dep}")
            else:
                print("No dependencies data returned")
        else:
            print(f"Dependencies failed: {deps_result.error}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 5: Get trending packages
    print("5. Getting trending packages...")
    try:
        trending_result = await get_trending_packages(
            platform="npm"
        )
        
        if trending_result.success:
            trending = trending_result.data
            if trending and trending.get('packages'):
                print(f"Top {len(trending['packages'])} trending packages:")
                for pkg in trending['packages']:
                    print(f"  - {pkg.get('name', 'N/A')} ({pkg.get('platform', 'N/A')}) - {pkg.get('stars', 'N/A')} stars")
            else:
                print("No trending packages data returned")
        else:
            print(f"Trending packages failed: {trending_result.error}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 6: Get popular packages
    print("6. Getting popular packages...")
    try:
        popular_result = await get_popular_packages(
            platform="npm"
        )
        
        if popular_result.success:
            popular = popular_result.data
            if popular and popular.get('packages'):
                print(f"Top {len(popular['packages'])} popular packages:")
                for pkg in popular['packages']:
                    print(f"  - {pkg.get('name', 'N/A')} ({pkg.get('platform', 'N/A')}) - {pkg.get('stars', 'N/A')} stars")
            else:
                print("No popular packages data returned")
        else:
            print(f"Popular packages failed: {popular_result.error}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
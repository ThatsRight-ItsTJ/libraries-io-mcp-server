"""
MCP Server Example for Libraries.io MCP Server

This example demonstrates how to run and use the Libraries.io MCP Server
as a standalone server.
"""

import asyncio
import os
import uvicorn
from libraries_io_mcp.server import create_server

async def main():
    """Main function to run the MCP server example."""
    
    print("Libraries.io MCP Server - Example")
    print("=" * 40)
    
    # Get configuration from environment
    api_key = os.getenv("LIBRARIES_IO_API_KEY")
    if not api_key:
        print("Error: LIBRARIES_IO_API_KEY environment variable is required")
        print("Please set your Libraries.io API key:")
        print("  export LIBRARIES_IO_API_KEY=your_api_key_here")
        return
    
    # Create server
    server = create_server()
    
    print(f"Starting Libraries.io MCP Server...")
    print(f"API Key: {'*' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else '*' * len(api_key)}")
    print(f"Base URL: {os.getenv('LIBRARIES_IO_BASE_URL', 'https://libraries.io/api/v1')}")
    print(f"Rate Limit: {os.getenv('RATE_LIMIT_REQUESTS', '100')} requests per {os.getenv('RATE_LIMIT_WINDOW', '3600')} seconds")
    print()
    
    # Print available tools
    print("Available MCP Tools:")
    tools = [
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
        "audit_project_dependencies"
    ]
    
    for i, tool in enumerate(tools, 1):
        print(f"  {i:2d}. {tool}")
    
    print()
    print("Available MCP Resources:")
    resources = [
        "packages://{platform}/{name}",
        "packages://{platform}/{name}/versions",
        "packages://{platform}/{name}/dependencies",
        "packages://{platform}/{name}/dependents",
        "search://packages",
        "search://trending",
        "users://{username}/packages",
        "orgs://{org}/packages"
    ]
    
    for i, resource in enumerate(resources, 1):
        print(f"  {i:2d}. {resource}")
    
    print()
    print("Available MCP Prompts:")
    prompts = [
        "package_analysis_prompt",
        "dependency_analysis_prompt",
        "ecosystem_exploration_prompt",
        "evaluate_package",
        "audit_dependencies",
        "analyze_project_health",
        "recommend_packages",
        "migration_guide",
        "security_assessment",
        "license_compliance_check",
        "maintenance_status_report"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"  {i:2d}. {prompt}")
    
    print()
    print("Starting server on http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        # Run the server
        config = uvicorn.Config(
            app=server,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        server_instance = uvicorn.Server(config)
        await server_instance.serve()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error starting server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
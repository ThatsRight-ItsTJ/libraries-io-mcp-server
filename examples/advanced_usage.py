"""
Advanced Usage Examples for Libraries.io MCP Server

This file demonstrates advanced usage patterns including:
- Package comparison and analysis
- Dependency tree analysis
- Security checking
- License compatibility
- Project auditing
"""

import asyncio
import os
from libraries_io_mcp.client import LibrariesIOClient
from libraries_io_mcp.tools import (
    compare_packages,
    analyze_dependency_tree,
    check_package_security,
    check_license_compatibility,
    audit_project_dependencies,
    get_platform_stats,
    find_alternatives
)

async def main():
    """Advanced usage examples."""
    
    # Initialize client
    api_key = os.getenv("LIBRARIES_IO_API_KEY")
    if not api_key:
        print("Please set LIBRARIES_IO_API_KEY environment variable")
        return
    
    client = LibrariesIOClient(api_key=api_key)
    
    print("=== Advanced Usage Examples ===\n")
    
    # Example 1: Compare packages
    print("1. Comparing packages...")
    try:
        compare_result = await compare_packages(
            packages=[
                {"platform": "npm", "name": "react"},
                {"platform": "npm", "name": "vue"},
                {"platform": "npm", "name": "angular"}
            ]
        )
        
        if compare_result.success:
            comparison = compare_result.data
            print(f"Comparison of {len(comparison['packages'])} packages:")
            for pkg in comparison['packages']:
                print(f"  - {pkg['name']} ({pkg['platform']}):")
                print(f"    Stars: {pkg.get('stars', 'N/A')}")
                print(f"    Language: {pkg.get('language', 'N/A')}")
                print(f"    Description: {pkg.get('description', 'N/A')[:100]}...")
        else:
            print(f"Comparison failed: {compare_result.error}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Analyze dependency tree
    print("2. Analyzing dependency tree...")
    try:
        tree_result = await analyze_dependency_tree(
            platform="npm",
            name="react",
            max_depth=2
        )
        
        if tree_result.success:
            tree = tree_result.data
            print(f"Dependency tree for react (depth {tree['max_depth']}):")
            print(f"Total dependencies: {tree['total_dependencies']}")
            print(f"Runtime dependencies: {tree['runtime_dependencies']}")
            print(f"Development dependencies: {tree['development_dependencies']}")
            
            print("\nTop dependencies:")
            for dep in tree['top_dependencies'][:5]:
                print(f"  - {dep['name']} ({dep['platform']}) - {dep['kind']}")
        else:
            print(f"Dependency tree analysis failed: {tree_result.error}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Check package security
    print("3. Checking package security...")
    try:
        security_result = await check_package_security(
            platform="npm",
            name="react"
        )
        
        if security_result.success:
            security = security_result.data
            print(f"Security analysis for react:")
            print(f"Security issues: {len(security.get('security_issues', []))}")
            
            if security.get('security_issues'):
                print("Security issues found:")
                for issue in security['security_issues']:
                    print(f"  - {issue.get('type', 'Unknown')}: {issue.get('description', 'No description')}")
            else:
                print("No security issues found")
        else:
            print(f"Security check failed: {security_result.error}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 4: Check license compatibility
    print("4. Checking license compatibility...")
    try:
        license_result = await check_license_compatibility(
            licenses=["MIT", "Apache-2.0"],
            use_case="commercial"
        )
        
        if license_result.success:
            license_check = license_result.data
            print(f"License compatibility check for commercial use:")
            print(f"Overall compatible: {license_check['overall_compatible']}")
            
            print("\nLicense analysis:")
            for license_info in license_check['licenses']:
                print(f"  - {license_info['license']}: {license_info['compatible']} ({license_info['use_case']})")
            
            if license_check.get('recommendations'):
                print("\nRecommendations:")
                for rec in license_check['recommendations']:
                    print(f"  - {rec}")
        else:
            print(f"License compatibility check failed: {license_result.error}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 5: Find alternatives
    print("5. Finding package alternatives...")
    try:
        alternatives_result = await find_alternatives(
            platform="npm",
            name="jquery",
            criteria=["stars", "downloads", "recent_updates"]
        )
        
        if alternatives_result.success:
            alternatives = alternatives_result.data
            print(f"Alternatives to jquery:")
            print(f"Found {len(alternatives['alternatives'])} alternatives")
            
            print("\nTop alternatives:")
            for alt in alternatives['alternatives'][:5]:
                print(f"  - {alt['name']} ({alt['platform']}): {alt.get('score', 'N/A')}/10")
                print(f"    Stars: {alt.get('stars', 'N/A')}, Language: {alt.get('language', 'N/A')}")
        else:
            print(f"Finding alternatives failed: {alternatives_result.error}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 6: Get platform statistics
    print("6. Getting platform statistics...")
    try:
        stats_result = await get_platform_stats(
            platform="npm",
            include_trending=True
        )
        
        if stats_result.success:
            stats = stats_result.data
            print(f"npm platform statistics:")
            print(f"Project count: {stats.get('project_count', 'N/A')}")
            print(f"Homepage: {stats.get('homepage', 'N/A')}")
            
            if stats.get('sample_statistics'):
                sample_stats = stats['sample_statistics']
                print(f"\nSample statistics (from {sample_stats['sample_size']} packages):")
                print(f"Total stars: {sample_stats['total_stars']}")
                print(f"Average stars: {sample_stats['average_stars']}")
                print(f"Most common language: {sample_stats['most_common_language']}")
            
            if stats.get('trending_packages'):
                print(f"\nTrending packages:")
                for pkg in stats['trending_packages'][:3]:
                    print(f"  - {pkg.get('name', 'N/A')} ({pkg.get('stars', 'N/A')} stars)")
        else:
            print(f"Platform stats failed: {stats_result.error}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 7: Audit project dependencies
    print("7. Auditing project dependencies...")
    try:
        audit_result = await audit_project_dependencies(
            platform="npm",
            packages=[
                {"name": "react", "version": "^18.0.0"},
                {"name": "vue", "version": "^3.0.0"},
                {"name": "angular", "version": "^15.0.0"}
            ],
            check_duplicates=True,
            check_outdated=True,
            check_unused=False
        )
        
        if audit_result.success:
            audit = audit_result.data
            print(f"Project audit results:")
            print(f"Total packages: {audit['total_packages']}")
            print(f"Project health score: {audit['project_health_score']}/100 ({audit['health_status']})")
            
            print("\nAudit summary:")
            summary = audit['summary']
            print(f"  - Duplicates: {summary['duplicates_count']}")
            print(f"  - Outdated: {summary['outdated_count']}")
            print(f"  - Security issues: {summary['security_issues_count']}")
            print(f"  - Recommendations: {summary['recommendations_count']}")
            
            if audit.get('audits', {}).get('duplicates'):
                print("\nDuplicate packages found:")
                for dup in audit['audits']['duplicates']:
                    print(f"  - {dup['package']}: {dup['recommendation']}")
            
            if audit.get('audits', {}).get('outdated'):
                print("\nOutdated packages:")
                for outdated in audit['audits']['outdated']:
                    print(f"  - {outdated['package']}: {outdated['current_version']} -> {outdated['latest_version']}")
        else:
            print(f"Project audit failed: {audit_result.error}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
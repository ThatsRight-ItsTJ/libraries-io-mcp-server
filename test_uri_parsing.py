#!/usr/bin/env python3
"""
Test script for URI parsing functionality.
"""

import re
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse


def parse_resource_uri(uri: str) -> Dict[str, Any]:
    """
    Parse resource URI and extract parameters.
    
    Args:
        uri: Resource URI (e.g., "packages://npm/react/info")
        
    Returns:
        Dictionary with parsed parameters
        
    Raises:
        ValueError: If URI format is invalid
    """
    try:
        parsed = urlparse(uri)
        if not parsed.scheme:
            raise ValueError(f"Invalid URI format: {uri}")
        
        # For custom URI schemes like users://, the netloc might be empty
        # and the actual data might be in the path
        if not parsed.netloc and parsed.scheme in ['users', 'orgs', 'packages', 'platforms', 'search']:
            # For these schemes, the path contains the actual resource identifier
            result = {
                "scheme": parsed.scheme,
                "netloc": "",
                "path": parsed.path.strip('/'),
                "params": parse_qs(parsed.query)
            }
        else:
            result = {
                "scheme": parsed.scheme,
                "netloc": parsed.netloc,
                "path": parsed.path.strip('/'),
                "params": parse_qs(parsed.query)
            }
        
        # Parse path components
        path_parts = result["path"].split('/')
        
        if result["scheme"] == "packages":
            if len(path_parts) >= 3:
                result["platform"] = path_parts[0]
                result["name"] = path_parts[1]
                result["resource_type"] = path_parts[2]
            elif len(path_parts) >= 2:
                result["platform"] = path_parts[0]
                result["name"] = path_parts[1]
                result["resource_type"] = "info"  # default
        
        elif result["scheme"] == "platforms":
            if len(path_parts) == 1 and path_parts[0] == "supported":
                result["resource_type"] = "supported"
                result["platform"] = None
            elif len(path_parts) >= 1:
                result["platform"] = path_parts[0]
                result["resource_type"] = "stats"
        
        elif result["scheme"] == "search":
            result["resource_type"] = path_parts[0] if path_parts else "packages"
        
        elif result["scheme"] in ["users", "orgs"]:
            # For users:// and orgs:// schemes, the username/org is in netloc, resource type in path
            if parsed.netloc:
                result["username" if result["scheme"] == "users" else "org"] = parsed.netloc
            if path_parts and path_parts[0]:
                result["resource_type"] = path_parts[0]
            else:
                result["resource_type"] = "packages"
        
        return result
        
    except Exception as e:
        raise ValueError(f"Failed to parse URI {uri}: {e}")


def validate_platform(platform: str) -> bool:
    """Validate platform name."""
    valid_platforms = {
        'npm', 'pypi', 'maven', 'gem', 'nuget', 'docker', 'hex', 'cran',
        'hackage', 'packagist', 'cocoapods', 'bower', 'composer', 'go',
        'elm', 'pub', 'dart', 'conan', 'bitbucket', 'github', 'gitlab'
    }
    return platform.lower() in valid_platforms


def sanitize_package_name(name: str) -> str:
    """Sanitize package name."""
    # Remove leading/trailing whitespace
    name = name.strip()
    
    # Replace multiple spaces with single space
    name = ' '.join(name.split())
    
    return name


# Test URI parsing
test_uris = [
    'platforms://supported',
    'platforms://npm/stats',
    'packages://npm/react/info',
    'packages://pypi/django/versions',
    'packages://npm/react/dependencies?version=18.0.0',
    'packages://pypi/django/dependents?page=1&per_page=50',
    'search://packages?q=react',
    'search://packages?q=django&platforms=pypi,npm',
    'search://trending?platform=npm',
    'search://trending?period=monthly',
    'users://octoc/packages',
    'users://octoc/packages?page=2',
    'orgs://django/packages',
    'orgs://django/packages?per_page=25'
]

print('Testing URI parsing:')
print('=' * 60)

for uri in test_uris:
    try:
        result = parse_resource_uri(uri)
        print(f'✓ {uri}')
        print(f'  Path: {result["path"]}')
        print(f'  Path Parts: {result["path"].split("/")}')
        print(f'  Scheme: {result["scheme"]}')
        print(f'  Resource Type: {result.get("resource_type", "N/A")}')
        
        if result["scheme"] == "packages":
            print(f'  Platform: {result["platform"]}')
            print(f'  Name: {result["name"]}')
        elif result["scheme"] == "platforms":
            print(f'  Platform: {result["platform"]}')
        elif result["scheme"] == "users":
            print(f'  Username: {result["username"]}')
        elif result["scheme"] == "orgs":
            print(f'  Organization: {result["org"]}')
        
        if result["params"]:
            print(f'  Query Params: {result["params"]}')
        
        print()
        
    except Exception as e:
        print(f'✗ {uri} -> Error: {e}')
        print()

# Test validation functions
print('Testing validation functions:')
print('=' * 60)

test_platforms = ['npm', 'pypi', 'maven', 'invalid_platform']
for platform in test_platforms:
    is_valid = validate_platform(platform)
    print(f'Platform "{platform}": {"✓ Valid" if is_valid else "✗ Invalid"}')

test_names = ['react', '  django  ', 'package with spaces', '']
for name in test_names:
    sanitized = sanitize_package_name(name)
    print(f'Name "{name}" -> "{sanitized}"')
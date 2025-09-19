
# API Documentation

This document provides comprehensive API documentation for the Libraries.io MCP Server, including all available tools, resources, and prompts.

## Overview

The Libraries.io MCP Server provides three types of MCP components:

1. **Tools** - Actions that AI assistants can perform (e.g., search packages, get package info)
2. **Resources** - Data access points for contextual information (e.g., package details, platform stats)
3. **Prompts** - AI interaction templates for common workflows (e.g., package analysis, dependency audit)

## Tools

### Package Discovery Tools

#### `search_packages`

Search for packages across multiple platforms with various filtering options.

**Parameters:**
- `query` (string, required): Search query string
- `platforms` (list[string], optional): Filter by platforms (e.g., ['npm', 'pypi'])
- `languages` (list[string], optional): Filter by programming languages
- `licenses` (list[string], optional): Filter by licenses
- `page` (integer, default: 1, min: 1, max: 100): Page number
- `per_page` (integer, default: 10, min: 1, max: 100): Results per page

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "total_count": integer,
    "incomplete_results": boolean,
    "items": [
      {
        "name": string,
        "platform": string,
        "description": string,
        "language": string,
        "latest_version": string,
        "stars": integer,
        "homepage": string,
        "repository_url": string,
        "dependents_count": integer
      }
    ]
  },
  "rate_limit_info": {
    "limit": integer,
    "remaining": integer,
    "reset": string,
    "used": integer
  }
}
```

**Example Usage:**
```python
# Search for React packages on npm
result = await search_packages(
    query="react",
    platforms=["npm"],
    per_page=20
)

# Search for Python packages with MIT license
result = await search_packages(
    query="web framework",
    platforms=["pypi"],
    licenses=["MIT"],
    languages=["Python"]
)
```

#### `get_trending_packages`

Get trending packages by platform and time range.

**Parameters:**
- `platform` (string, optional): Platform to filter by (e.g., 'npm', 'pypi')
- `time_range` (string, default: "week", options: ["day", "week", "month"]): Time range for trending
- `limit` (integer, default: 20, min: 1, max: 100): Maximum number of results

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "platform": string,
    "time_range": string,
    "total_count": integer,
    "packages": [
      {
        "name": string,
        "platform": string,
        "description": string,
        "stars": integer,
        "language": string,
        "latest_version": string,
        "homepage": string,
        "repository_url": string,
        "dependents_count": integer
      }
    ]
  },
  "rate_limit_info": {
    "limit": integer,
    "remaining": integer,
    "reset": string,
    "used": integer
  }
}
```

**Example Usage:**
```python
# Get trending packages for the week
result = await get_trending_packages(
    platform="npm",
    time_range="week",
    limit=10
)

# Get trending Python packages for the month
result = await get_trending_packages(
    platform="pypi",
    time_range="month",
    limit=15
)
```

#### `get_popular_packages`

Get the most popular packages by platform and language.

**Parameters:**
- `platform` (string, optional): Platform to filter by (e.g., 'npm', 'pypi')
- `language` (string, optional): Programming language to filter by
- `limit` (integer, default: 20, min: 1, max: 100): Maximum number of results

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "platform": string,
    "language": string,
    "total_count": integer,
    "packages": [
      {
        "name": string,
        "platform": string,
        "description": string,
        "stars": integer,
        "language": string,
        "latest_version": string,
        "homepage": string,
        "repository_url": string,
        "dependents_count": integer
      }
    ]
  },
  "rate_limit_info": {
    "limit": integer,
    "remaining": integer,
    "reset": string,
    "used": integer
  }
}
```

**Example Usage:**
```python
# Get popular JavaScript packages
result = await get_popular_packages(
    platform="npm",
    language="JavaScript",
    limit=10
)

# Get popular Python packages
result = await get_popular_packages(
    platform="pypi",
    language="Python",
    limit=20
)
```

### Package Analysis Tools

#### `get_package_info`

Get detailed information about a specific package.

**Parameters:**
- `platform` (string, required): Package manager platform (e.g., 'npm', 'pypi')
- `name` (string, required): Package name
- `include_versions` (boolean, default: false): Include version information

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "name": string,
    "platform": string,
    "description": string,
    "homepage": string,
    "repository_url": string,
    "language": string,
    "keywords": [string],
    "licenses": string,
    "latest_release_number": string,
    "latest_release_published_at": string,
    "stars": integer,
    "forks": integer,
    "dependents_count": integer,
    "versions": [
      {
        "number": string,
        "published_at": string,
        "spdx_expression": string,
        "original_license": string,
        "status": string
      }
    ]
  },
  "rate_limit_info": {
    "limit": integer,
    "remaining": integer,
    "reset": string,
    "used": integer
  }
}
```

**Example Usage:**
```python
# Get detailed info about React package
result = await get_package_info(
    platform="npm",
    name="react",
    include_versions=True
)

# Get info about FastAPI package
result = await get_package_info(
    platform="pypi",
    name="fastapi"
)
```

#### `get_package_versions`

Get all versions of a package.

**Parameters:**
- `platform` (string, required): Package manager platform (e.g., 'npm', 'pypi')
- `name` (string, required): Package name

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "platform": string,
    "name": string,
    "versions": [
      {
        "number": string,
        "published_at": string,
        "spdx_expression": string,
        "original_license": string,
        "status": string
      }
    ],
    "total_count": integer
  },
  "rate_limit_info": {
    "limit": integer,
    "remaining": integer,
    "reset": string,
    "used": integer
  }
}
```

**Example Usage:**
```python
# Get all versions of Express.js
result = await get_package_versions(
    platform="npm",
    name="express"
)

# Get all versions of Django
result = await get_package_versions(
    platform="pypi",
    name="django"
)
```

#### `get_package_dependencies`

Get dependencies for a specific package version.

**Parameters:**
- `platform` (string, required): Package manager platform (e.g., 'npm', 'pypi')
- `name` (string, required): Package name
- `version` (string, optional): Specific version to get dependencies for

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "platform": string,
    "name": string,
    "version": string,
    "dependencies": [
      {
        "name": string,
        "platform": string,
        "requirement": string,
        "kind": string,
        "optional": boolean
      }
    ],
    "total_count": integer
  },
  "rate_limit_info": {
    "limit": integer,
    "remaining": integer,
    "reset": string,
    "used": integer
  }
}
```

**Example Usage:**
```python
# Get dependencies for React 18.0.0
result = await get_package_dependencies(
    platform="npm",
    name="react",
    version="18.0.0"
)

# Get latest dependencies for FastAPI
result = await get_package_dependencies(
    platform="pypi",
    name="fastapi"
)
```

#### `get_package_dependents`

Get packages that depend on a specific package.

**Parameters:**
- `platform` (string, required): Package manager platform (e.g., 'npm', 'pypi')
- `name` (string, required): Package name
- `page` (integer, default: 1, min: 1, max: 100): Page number
- `per_page` (integer, default: 20, min: 1, max: 100): Results per page

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "platform": string,
    "name": string,
    "page": integer,
    "per_page": integer,
    "dependents": [
      {
        "name": string,
        "platform": string,
        "description": string,
        "language": string,
        "latest_version": string,
        "stars": integer,
        "homepage": string,
        "repository_url": string,
        "dependents_count": integer
      }
    ],
    "total_count": integer
  },
  "rate_limit_info": {
    "limit": integer,
    "remaining": integer,
    "reset": string,
    "used": integer
  }
}
```

**Example Usage:**
```python
# Get packages that depend on React
result = await get_package_dependents(
    platform="npm",
    name="react",
    per_page=50
)

# Get Python packages that depend on requests
result = await get_package_dependents(
    platform="pypi",
    name="requests",
    page=1,
    per_page=100
)
```

#### `compare_packages`

Compare multiple packages side by side.

**Parameters:**
- `packages` (list[object], required): List of packages to compare, each with 'platform' and 'name'
- `features` (list[string], optional): Features to compare (e.g., ['stars', 'downloads', 'version'])

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "packages": [
      {
        "platform": string,
        "name": string,
        "description": string,
        "language": string,
        "latest_version": string,
        "stars": integer,
        "forks": integer,
        "dependents_count": integer,
        "homepage": string,
        "repository_url": string,
        "licenses": string,
        "features": {
          "stars": integer,
          "downloads": integer,
          "version": string
        }
      }
    ],
    "comparison": {
      "best_by_stars": string,
      "best_by_dependents": string,
      "most_recent": string,
      "language_distribution": {
        "language": count
      }
    }
  },
  "rate_limit_info": {
    "limit": integer,
    "remaining": integer,
    "reset": string,
    "used": integer
  }
}
```

**Example Usage:**
```python
# Compare popular web frameworks
result = await compare_packages(
    packages=[
        {"platform": "npm", "name": "express"},
        {"platform": "npm", "name": "fastify"},
        {"platform": "pypi", "name": "flask"}
    ],
    features=["stars", "dependents_count", "latest_version"]
)

# Compare database packages
result = await compare_packages(
    packages=[
        {"platform": "npm", "name": "mongoose"},
        {"platform": "pypi", "name": "sqlalchemy"}
    ]
)
```

#### `check_package_security`

Check for security vulnerabilities in a package.

**Parameters:**
- `platform` (string, required): Package manager platform (e.g., 'npm', 'pypi')
- `name` (string, required): Package name
- `version` (string, optional): Specific version to check

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "package": {
      "name": string,
      "platform": string,
      "version": string
    },
    "security_issues": [
      {
        "id": string,
        "title": string,
        "description": string,
        "severity": "critical" | "high" | "medium" | "low",
        "affected_versions": [string],
        "fixed_versions": [string],
        "published_at": string,
        "url": string
      }
    ],
    "security_score": integer,
    "last_checked": string
  },
  "rate_limit_info": {
    "limit": integer,
    "remaining": integer,
    "reset": string,
    "used": integer
  }
}
```

**Example Usage:**
```python
# Check security for a specific package version
result = await check_package_security(
    platform="npm",
    name="lodash",
    version="4.17.21"
)

# Check latest version security
result = await check_package_security(
    platform="pypi",
    name="requests"
)
```

### Ecosystem Analysis Tools

#### `analyze_dependency_tree`

Perform deep dependency tree analysis.

**Parameters:**
- `platform` (string, required): Package manager platform (e.g., 'npm', 'pypi')
- `name` (string, required): Package name
- `version` (string, optional): Specific version to analyze
- `max_depth` (integer, default: 3, min: 1, max: 10): Maximum depth to analyze
- `include_dev` (boolean, default: false): Include development dependencies

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "package": {
      "name": string,
      "platform": string,
      "version": string
    },
    "dependency_tree": {
      "root": {
        "name": string,
        "platform": string,
        "version": string,
        "dependencies": [...]
      },
      "total_dependencies": integer,
      "max_depth": integer,
      "unique_packages": integer
    },
    "analysis": {
      "license_compatibility": {
        "compatible": boolean,
        "issues": [string]
      },
      "security_risks": {
        "vulnerable_packages": integer,
        "total_vulnerabilities": integer
      },
      "update_opportunities": [
        {
          "package": string,
          "current_version": string,
          "latest_version": string,
          "update_type": "major" | "minor" | "patch"
        }
      ],
      "dependency_bloat": {
        "total_size": string,
        "unused_dependencies": [string]
      }
    }
  },
  "rate_limit_info": {
    "limit": integer,
    "remaining": integer,
    "reset": string,
    "used": integer
  }
}
```

**Example Usage:**
```python
# Analyze dependency tree for React app
result = await analyze_dependency_tree(
    platform="npm",
    name="create-react-app",
    version="5.0.1",
    max_depth=5,
    include_dev=True
)

# Analyze Python package dependencies
result = await analyze_dependency_tree(
    platform="pypi",
    name="django",
    max_depth=3
)
```

#### `find_alternatives`

Find alternative packages based on criteria.

**Parameters:**
- `platform` (string, required): Package manager platform (e.g., 'npm', 'pypi')
- `name` (string, required): Package name to find alternatives for
- `criteria` (list[string], optional): Alternative criteria (e.g., ['similar', 'lighter', 'more_popular'])
- `limit` (integer, default: 10, min: 1, max: 50): Maximum number of alternatives

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "original_package": {
      "name": string,
      "platform": string,
      "description": string,
      "stars": integer,
      "language": string
    },
    "alternatives": [
      {
        "name": string,
        "platform": string,
        "description": string,
        "stars": integer,
        "language": string,
        "similarity_score": float,
        "advantages": [string],
        "disadvantages": [string],
        "use_cases": [string]
      }
    ],
    "criteria_used": [string],
    "total_count": integer
  },
  "rate_limit_info": {
    "limit": integer,
    "remaining": integer,
    "reset": string,
    "used": integer
  }
}
```

**Example Usage:**
```python
# Find lighter alternatives to React
result = await find_alternatives(
    platform="npm",
    name="react",
    criteria=["lighter", "similar"],
    limit=5
)

# Find more popular alternatives to Express
result = await find_alternatives(
    platform="npm",
    name="express",
    criteria=["more_popular", "similar"]
)
```

#### `get_platform_stats`

Get comprehensive statistics for a package manager platform.

**Parameters:**
- `platform` (string, required): Platform name (e.g., 'npm', 'pypi')
- `include_trending` (boolean, default: false): Include trending packages in statistics

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "platform": {
      "name": string,
      "homepage": string,
      "color": string,
      "project_count": integer,
      "default_language": string,
      "package_type": string
    },
    "sample_statistics": {
      "sample_size": integer,
      "total_stars": integer,
      "average_stars": float,
      "languages": {
        "language": count
      },
      "most_common_language": string
    },
    "trending_packages": [
      {
        "name": string,
        "platform": string,
        "description": string,
        "stars": integer,
        "language": string,
        "latest_version": string
      }
    ],
    "supported": boolean
  },
  "rate_limit_info": {
    "limit": integer,
    "remaining": integer,
    "reset": string,
    "used": integer
  }
}
```

**Example Usage:**
```python
# Get comprehensive npm statistics
result = await get_platform_stats(
    platform="npm",
    include_trending=True
)

# Get PyPI platform statistics
result = await get_platform_stats(
    platform="pypi"
)
```

#### `check_license_compatibility`

Check license compatibility for multiple licenses.

**Parameters:**
- `licenses` (list[string], required): List of licenses to check compatibility for
- `use_case` (string, default: "commercial", options: ["commercial", "open_source", "academic"]): Use case for compatibility check

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "use_case": string,
    "licenses": [
      {
        "license": string,
        "normalized": string,
        "compatible": boolean,
        "use_case": string,
        "restrictions": [string]
      }
    ],
    "overall_compatible": boolean,
    "recommendations": [string],
    "compatibility_rules": {
      "license": {
        "commercial": boolean,
        "open_source": boolean,
        "academic": boolean
      }
    }
  }
}
```

**Example Usage:**
```python
# Check license compatibility for commercial use
result = await check_license_compatibility(
    licenses=["MIT", "Apache-2.0", "GPL-3.0"],
    use_case="commercial"
)

# Check license compatibility for open source project
result = await check_license_compatibility(
    licenses=["MIT", "BSD-3-Clause"],
    use_case="open_source"
)
```

### Project Management Tools

#### `track_package_updates`

Monitor a package for updates and changes.

**Parameters:**
- `platform` (string, required): Package manager platform (e.g., 'npm', 'pypi')
- `name` (string, required): Package name to track
- `check_interval` (string, default: "daily", options: ["hourly", "daily", "weekly"]): Check interval
- `include_security` (boolean, default: true): Include security updates in notifications

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "package": {
      "name": string,
      "platform": string,
      "current_version": string,
      "latest_version": string,
      "description": string
    },
    "tracking": {
      "check_interval": string,
      "include_security": boolean,
      "has_update": boolean,
      "is_security_update": boolean,
      "time_since_update": string
    },
    "versions": {
      "total_versions": integer,
      "latest_published": string,
      "current_published": string
    },
    "next_check": string
  },
  "rate_limit_info": {
    "limit": integer,
    "remaining": integer,
    "reset": string,
    "used": integer
  }
}
```

**Example Usage:**
```python
# Track React package for daily updates
result = await track_package_updates(
    platform="npm",
    name="react",
    check_interval="daily",
    include_security=True
)

# Track Python package for weekly updates
result = await track_package_updates(
    platform="pypi",
    name="django",
    check_interval="weekly"
)
```

#### `generate_dependency_report`

Generate a comprehensive dependency report for multiple packages.

**Parameters:**
- `packages` (list[object], required): List of packages to analyze, each with 'platform' and 'name'
- `include_versions` (boolean, default: true): Include version information in report
- `include_dependencies` (boolean, default: true): Include dependency information in report
- `include_security` (boolean, default: true): Include security information in report

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "generated_at": string,
    "packages_analyzed": integer,
    "packages": [
      {
        "platform": string,
        "name": string,
        "status": "success" | "error",
        "description": string,
        "language": string,
        "stars": integer,
        "latest_version": string,
        "homepage": string,
        "repository_url": string,
        "versions": {
          "total": integer,
          "latest": string,
          "oldest": string
        },
        "dependencies": {
          "total": integer,
          "runtime": integer,
          "development": integer
        },
        "security": {
          "security_issues": [string]
        }
      }
    ],
    "summary": {
      "total_packages": integer,
      "successful_analyses": integer,
      "failed_analyses": integer,
      "total_dependencies": integer,
      "unique_languages": [string],
      "security_issues": integer,
      "security_score": integer
    }
  },
  "rate_limit_info": {
    "limit": integer,
    "remaining": integer,
    "reset": string,
    "used": integer
  }
}
```

**Example Usage:**
```python
# Generate comprehensive dependency report
result = await generate_dependency_report(
    packages=[
        {"platform": "npm", "name": "react"},
        {"platform": "npm", "name": "express"},
        {"platform": "pypi", "name": "django"}
    ],
    include_versions=True,
    include_dependencies=True,
    include_security=True
)
```

#### `audit_project_dependencies`

Audit all dependencies in a project for various issues.

**Parameters:**
- `platform` (string, required): Package manager platform (e.g., 'npm', 'pypi')
- `packages` (list[object], required): List of packages to audit, each with 'name' and optional 'version'
- `check_duplicates` (boolean, default: true): Check for duplicate dependencies
- `check_unused` (boolean, default: false): Check for potentially unused dependencies
- `check_outdated` (boolean, default: true): Check for outdated packages

**Return Type:**
```json
{
  "success": boolean,
  "data": {
    "platform": string,
    "generated_at": string,
    "total_packages": integer,
    "audits": {
      "duplicates": [
        {
          "package": string,
          "duplicates": [...],
          "severity": "high" | "medium" | "low",
          "recommendation": string
        }
      ],
      "unused": [...],
      "outdated": [
        {
          "package": string,
          "current_version": string,
          "latest_version": string,
          "severity": "high" | "medium" | "low",
          "recommendation": string
        }
      ],
      "security": [...],
      "recommendations": [...]
    },
    "summary": {
      "duplicates_count": integer,
      "unused_count": integer,
      "outdated_count": integer,
      "security_issues_count": integer,
      "recommendations_count": integer
    },
    "project_health_score": integer,
    "health_status": "excellent" | "good" | "fair" | "poor" | "critical"
  },
  "rate_limit_info": {
    "limit": integer,
    "remaining": integer,
    "reset": string,
    "used": integer
  }
}
```

**Example Usage:**
```python
# Audit npm project dependencies
result = await audit_project_dependencies(
    platform="npm",
    packages=[
        {"name": "react", "version": "18.0.0"},
        {"name": "express"},
        {"name": "lodash"}
    ],
    check_duplicates=True,
    check_unused=False,
    check_outdated=True
)

# Audit Python project dependencies
result = await audit_project_dependencies(
    platform="pypi",
    packages=[
        {"name": "django"},
        {"name": "requests"},
        {"name": "numpy"}
    ]
)
```

## Resources

### Platform Resources

#### `platforms://supported`

Get list of all supported platforms.

**URI:** `platforms://supported`

**Return Type:**
```json
{
  "resource_type": "platforms",
  "subtype": "supported",
  "total_count": integer,
  "platforms": [
    {
      "name": string,
      "project_count": integer,
      "homepage": string,
      "color": string,
      "default_language": string,
      "package_type": string
    }
  ],
  "source": "libraries.io"
}
```

**Example Usage:**
```python
# Access via MCP client
result = await client.read_resource("platforms://supported")
```

#### `platforms://{platform}/stats`

Get platform-specific statistics.

**URI:** `platforms://{platform}/stats`

**Parameters:**
- `platform`: Platform name (extracted from URI)

**Return Type:**
```json
{
  "resource_type": "platforms",
  "platform": string,
  "statistics": {
    "total_projects": integer,
    "total_packages": integer,
    "total_repositories": integer,
    "most_popular_language": string,
    "average_stars": float,
    "total_downloads": integer
  },
  "source": "libraries.io"
}
```

**Example Usage:**
```python
# Get npm statistics
result = await client.read_resource("platforms://npm/stats")

# Get PyPI statistics
result = await client.read_resource("platforms://pypi/stats")
```

### Package Resources

#### `packages://{platform}/{name}/info`

Get comprehensive package information.

**URI:** `packages://{platform}/{name}/info`

**Parameters:**
- `platform`: Package manager platform (extracted from URI)
- `name`: Package name (extracted from URI)

**Return Type:**
```json
{
  "resource_type": "packages",
  "platform": string,
  "name": string,
  "package": {
    "name": string,
    "platform": string,
    "description": string,
    "homepage": string,
    "repository_url": string,
    "language": string,
    "keywords": [string],
    "licenses": string,
    "latest_release_number": string,
    "latest_release_published_at": string,
    "stars": integer,
    "forks": integer,
    "dependents_count": integer,
    "versions": [...]
  },
  "source": "libraries.io"
}
```

**Example Usage:**
```python
# Get React package info
result = await client.read_resource("packages://npm/react/info")

# Get Django package info
result = await client.read_resource("packages://pypi/django/info")
```

#### `packages://{platform}/{name}/versions`

Get package version history.

**URI:** `packages://{platform}/{name}/versions`

**Parameters:**
- `platform`: Package manager platform (extracted from URI)
- `name`: Package name (extracted from URI)

**Return Type:**
```json
{
  "resource_type": "packages",
  "platform": string,
  "name": string,
  "versions": [
    {
      "number": string,
      "published_at": string,
      "spdx_expression": string,
      "original_license": string,
      "status": string
    }
  ],
  "total_count": integer,
  "source": "libraries.io"
}
```

**Example Usage:**
```python
# Get React versions
result = await client.read_resource("packages://npm/react/versions")

# Get Django versions
result = await client.read_resource("packages://pypi/django/versions")
```

#### `packages://{platform}/{name}/dependencies`

Get package dependencies.

**URI:** `packages://{platform}/{name}/dependencies[?version={version}]`

**Parameters:**
- `platform`: Package manager platform (extracted from URI)
- `name`: Package name (extracted from URI)
- `version`: Specific version (optional, from query params)

**Return Type:**
```json
{
  "resource_type": "packages",
  "platform": string,
  "name": string,
  "version": string,
  "dependencies": [
    {
      "name": string,
      "platform": string,
      "requirement": string,
      "kind": string,
      "optional": boolean
    }
  ],
  "total_count": integer,
  "source": "libraries.io"
}
```

**Example Usage:**
```python
# Get React dependencies
result = await client.read_resource("packages://npm/react/dependencies")

# Get dependencies for specific version
result = await client.read_resource("packages://npm/react/dependencies?version=18.0.0")
```

#### `packages://{platform}/{name}/dependents`

Get packages that depend on this package.

**URI:** `packages://{platform}/{name}/dependents[?page={page}&per_page={per_page}]`

**Parameters:**
- `platform`: Package manager platform (extracted from URI)
- `name`: Package name (extracted from URI)
- `page`: Page number (optional, from query params, default: 1)
- `per_page`: Items per page (optional, from query params, default: 100, max: 100)

**Return Type:**
```json
{
  "resource_type": "packages",
  "platform": string,
  "name": string,
  "page": integer,
  "per_page": integer,
  "dependents": [
    {
      "name": string,
      "platform": string,
      "description": string,
      "language": string,
      "latest_version": string,
      "stars": integer,
      "homepage": string,
      "repository_url": string,
      "dependents_count": integer
    }
  ],
  "total_count": integer,
  "source": "libraries.io"
}
```

**Example Usage:**
```python
# Get React dependents
result = await client.read_resource("packages://npm/react/dependents")

# Get dependents with pagination
result = await client.read_resource("packages://npm/react/dependents?page=1&per_page=50")
```

### Search Resources

#### `search://packages`

Search for packages.

**URI:** `search://packages[?q={query}&platforms={platforms}&languages={languages}&licenses={licenses}&page={page}&per_page={per_page}]`

**Parameters:**
- `query`: Search query (required, from query params)
- `platforms`: Filter by platforms (optional, from query params)
- `languages`: Filter by languages (optional, from query params)
- `licenses`: Filter by licenses (optional, from query params)
- `page`: Page number (optional, from query params, default: 1)
- `per_page`: Items per page (optional, from query params, default: 10, max: 100)

**Return Type:**
```json
{
  "resource_type": "search",
  "search_type": "packages",
  "query": string,
  "platforms": [string],
  "languages": [string],
  "licenses": [string],
  "page": integer,
  "per_page": integer,
  "total_count": integer,
  "incomplete_results": boolean,
  "items": [
    {
      "name": string,
      "platform": string,
      "description": string,
      "language": string,
      "latest_version": string,
      "stars": integer,
      "homepage": string,
      "repository_url": string,
      "dependents_count": integer
    }
  ],
  "source": "libraries.io"
}
```

**Example Usage:**
```python
# Search for React packages
result = await client.read_resource("search://packages?q=react&platforms=npm")

# Search with multiple filters
result = await client.read_resource("search://packages?q=web%20framework&platforms=pypi&languages=Python&licenses=MIT&page=1&per_page=20")
```

#### `search://trending`

Get trending packages.

**URI:** `search://trending[?platform={platform}&period={period}]`

**Parameters:**
- `platform`: Filter by platform (optional, from query params)
- `period`: Time period (optional, from query params, default: "weekly")

**Return Type:**
```json
{
  "resource_type": "search",
  "search_type": "trending",
  "platform": string,
  "period": string,
  "total_count": integer,
  "items": [
    {
      "name": string,
      "platform": string,
      "description": string,
      "stars": integer,
      "language": string,
      "latest_version": string,
      "homepage": string,
      "repository_url": string,
      "dependents_count": integer
    }
  ],
  "source": "libraries.io"
}
```

**Example Usage:**
```python
# Get trending packages
result = await client.read_resource("search://trending")

# Get trending npm packages for the week
result = await client.read_resource("search://trending?platform=npm&period=weekly")

# Get trending Python packages for the month
result = await client.read_resource("search://trending?platform=pypi&period=monthly")
```

### User/Organization Resources

#### `users://{username}/packages`

Get user's packages.

**URI:** `users://{username}/packages[?page={page}&per_page={per_page}]`

**Parameters:**
- `username`: GitHub username (extracted from URI)
- `page`: Page number (optional, from query params, default: 1)
- `per_page`: Items per page (optional, from query params, default: 100, max: 100)

**Return Type:**
```json
{
  "resource_type": "users",
  "username": string,
  "page": integer,
  "per_page": integer,
  "packages": [
    {
      "name": string,
      "platform": string,
      "description": string,
      "language": string,
      "latest_version": string,
      "stars": integer,
      "homepage": string,
      "repository_url": string,
      "dependents_count": integer
    }
  ],
  "total_count": integer,
  "source": "libraries.io"
}
```

**Example Usage:**
```python
# Get user's packages
result = await client.read_resource("users://octoc/packages")

# Get user's packages with pagination
result = await client.read_resource("users://octoc/packages?page=1&per_page=50")
```

### Organization Resources

#### `orgs://{org}/packages`

Get organization's packages.

**URI:** `orgs://{org}/packages[?page={page}&per_page={per_page}]`

**Parameters:**
- `org`: GitHub organization name (extracted from URI)
- `page`: Page number (optional, from query params, default: 1)
- `per_page`: Items per page (optional, from query params, default: 100, max: 100)

**Return Type:**
```json
{
  "resource_type": "orgs",
  "organization": string,
  "page": integer,
  "per_page": integer,
  "packages": [
    {
      "name": string,
      "platform": string,
      "description": string,
      "language": string,
      "latest_version": string,
      "stars": integer,
      "homepage": string,
      "repository_url": string,
      "dependents_count": integer
    }
  ],
  "total_count": integer,
  "source": "libraries.io"
}
```

**Example Usage:**
```python
# Get organization's packages
result = await client.read_resource("orgs://facebook/packages")

# Get organization's packages with pagination
result = await client.read_resource("orgs://google/packages?page=1&per_page=100")
```

## Prompts

### Package Analysis Prompts

#### `package_analysis_prompt`

Generate a comprehensive package analysis prompt.

**Parameters:**
- `platform` (string, required): Package manager platform (e.g., 'npm', 'pypi')
- `name` (string, required): Package name

**Return Type:** String prompt for AI analysis

**Example Usage:**
```python
# Generate analysis prompt for React
prompt = await package_analysis_prompt(
    platform="npm",
    name="react"
)

# Generate analysis prompt for Django
prompt = await package_analysis_prompt(
    platform="pypi",
    name="django"
)
```

#### `dependency_analysis_prompt`

Generate a dependency analysis prompt.

**Parameters:**
- `platform` (string, required): Package manager platform (e.g., 'npm', 'pypi')
- `name` (string, required): Package name
- `version` (string, optional): Specific version

**Return Type:** String prompt for AI analysis

**Example Usage:**
```python
# Generate dependency analysis prompt
prompt = await dependency_analysis_prompt(
    platform="npm",
    name="react",
    version="18.0.0"
)

# Generate dependency analysis prompt without specific version
prompt = await dependency_analysis_prompt(
    platform="pypi",
    name="django"
)
```

### Ecosystem Analysis Prompts

#### `ecosystem_exploration_prompt`

Generate an ecosystem exploration prompt.

**Parameters:**
- `platform` (string, required): Package manager platform (e.g., 'npm', 'pypi')
- `language` (string, optional): Programming language filter

**Return Type:** String prompt for AI analysis

**Example Usage:**
```python
# Generate ecosystem exploration prompt
prompt = await ecosystem_exploration_prompt(
    platform="npm",
    language="JavaScript"
)

# Generate ecosystem exploration prompt without language filter
prompt = await ecosystem_exploration_prompt(
    platform="pypi"
)
```

### Project Management Prompts

#### `evaluate_package`

Generate a package evaluation prompt.

**Parameters:**
- `package_name` (string, required): Name of the package to evaluate
- `platform` (string, default: "npm"): Package manager platform

**Return Type:** String prompt for AI evaluation

**Example Usage:**
```python
# Generate evaluation prompt
prompt = await evaluate_package(
    package_name="express",
    platform="npm"
)

# Generate evaluation prompt for Python package
prompt = await evaluate_package(
    package_name="flask",
    platform="pypi"
)
```

#### `audit_dependencies`

Generate a dependency audit prompt.

**Parameters:**
- `dependencies` (list, required): List of dependencies to audit

**Return Type:** String prompt for AI audit

**Example Usage:**
```python
# Generate dependency audit prompt
prompt = await audit_dependencies([
    {"platform": "npm", "name": "react"},
    {"platform": "npm", "name": "express"},
    {"platform": "pypi", "name": "django"}
])
```

#### `analyze_project_health`

Generate a project health analysis prompt.

**Parameters:**
- `project_name` (string, required): Name of the project to analyze
- `platform` (string, default: "npm"): Package manager platform

**Return Type:** String prompt for AI analysis

**Example Usage:**
```python
# Generate project health analysis prompt
prompt = await analyze_project_health(
    project_name="my-web-app",
    platform="npm"
)

# Generate project health analysis prompt for Python project
prompt = await analyze_project_health(
    project_name="django-blog",
    platform="pypi"
)
```

### Recommendation Prompts

#### `recommend_packages`

Generate package recommendation prompts.

**Parameters:**
- `requirements` (string, required): Description of requirements or use case
- `platform` (string, default: "npm"): Package manager platform
- `language` (string, optional): Programming language filter
- `limit` (integer, default: 10): Maximum number of recommendations

**Return Type:** String prompt for AI recommendations

**Example Usage:**
```python
# Generate package recommendations for web framework
prompt = await recommend_packages(
    requirements="Need a lightweight web framework with good TypeScript support",
    platform="npm",
    language="TypeScript",
    limit=5
)

# Generate package recommendations for data processing
prompt = await recommend_packages(
    requirements="Need data processing and visualization libraries",
    platform="pypi",
    language="Python"
)
```

#### `migration_guide`

Generate a migration guide prompt.

**Parameters:**
- `package_name` (string, required): Name of the package to migrate
- `current_version` (string, required): Current version to migrate from
- `target_version` (string, required): Target version to migrate to
- `platform` (string, default: "npm"): Package manager platform

**Return Type:** String prompt for AI migration guidance

**Example Usage:**
```python
# Generate migration guide prompt
prompt = await migration_guide(
    package_name="react",
    current_version="16.0.0",
    target_version="18.0.0",
    platform="npm"
)

# Generate migration guide prompt for Python package
prompt = await migration_guide(
    package_name="django",
    current_version="3.2.0",
    target_version="4.0.0",
    platform="pypi"
)
```

### Security Prompts

#### `security_assessment`

Generate a security assessment prompt.

**Parameters:**
- `project_name` (string, required): Name of the project to assess
- `platform` (string, default: "npm"): Package manager platform
- `include_dependencies` (boolean, default: true): Whether to include dependency analysis

**Return Type:** String prompt for AI security assessment

**Example Usage:**
```python
# Generate security assessment prompt
prompt = await security_assessment(
    project_name="my-web-app",
    platform="npm",
    include_dependencies=True
)

# Generate security assessment prompt without dependencies
prompt = await security_assessment(
    project_name="django-blog",
    platform="pypi",
    include_dependencies=False
)
```

#### `license_compliance_check`

Generate a license compliance check prompt.

**Parameters:**
- `dependencies` (list, required): List of dependencies to check
- `policy_requirements` (string, default: "permissive"): License policy requirements

**Return Type:** String prompt for AI compliance checking

**Example Usage:**
```python
# Generate license compliance check prompt
prompt = await license_compliance_check(
    dependencies=[
        {"platform": "npm", "name": "react"},
        {"platform": "npm", "name": "express"}
    ],
    policy_requirements="permissive"
)

# Generate license compliance check prompt for strict policy
prompt = await license_compliance_check(
    dependencies=[
        {"platform": "pypi", "name": "django"},
        {"platform": "pypi", "name": "requests"}
    ],
    policy_requirements="strict"
)
```

### Maintenance Prompts

#### `maintenance_status_report`

Generate a maintenance status report prompt.

**Parameters:**
- `project_name` (string, required): Name of the project to analyze
- `platform` (string, default: "npm"): Package manager platform
- `time_period` (string, default: "6 months"): Time period for analysis

**Return Type:** String prompt for AI maintenance analysis

**Example Usage:**
```python
# Generate maintenance status report prompt
prompt = await maintenance_status_report(
    project_name="my-web-app",
    platform="npm",
    time_period="6 months"
)

# Generate maintenance status report prompt for Python project
prompt = await maintenance_status_report(
    project_name="django-blog",
    platform="pypi",
    time_period="12 months"
)
```

## Common Use Cases

### 1. Package Discovery and Selection

```python
# Search for packages with specific criteria
search_result = await search_packages(
    query="web framework",
    platforms=["npm", "pypi"],
    languages=["JavaScript", "Python"],
    licenses=["MIT", "Apache-2.0"],
    per_page=20
)

# Get trending packages for inspiration
trending = await get_trending_packages(
    platform="npm",
    time_range="week",
    limit=10
)

# Find alternatives to a specific package
alternatives = await find_alternatives(
    platform="npm",
    name="express",
    criteria=["lighter", "similar"],
    limit=5
)
```

### 2. Package Analysis and Evaluation

```python
# Get detailed package information
package_info = await get_package_info(
    platform="npm",
    name="react",
    include_versions=True
)

# Check package security
security_check = await check_package_security(
    platform="npm",
    name="react",
    version="18.0.0"
)

# Compare multiple packages
comparison = await compare_packages(
    packages=[
        {"platform": "npm", "name": "react"},
        {"platform": "npm", "name": "vue"},
        {"platform": "npm", "name": "svelte"}
    ],
    features=["stars", "dependents_count", "latest_version"]
)
```

### 3. Dependency Management

```python
# Analyze dependency tree
dependency_analysis = await analyze_dependency_tree(
    platform="npm",
    name="create-react-app",
    max_depth=5,
    include_dev=True
)

# Generate dependency report
dependency_report = await generate_dependency_report(
    packages=[
        {"platform": "npm", "name": "react"},
        {"platform": "npm", "name": "express"},
        {"platform": "pypi", "name": "django"}
    ],
    include_versions=True,
    include_dependencies=True,
    include_security=True
)

# Audit project dependencies
audit_result = await audit_project_dependencies(
    platform="npm",
    packages=[
        {"name": "react", "version": "18.0.0"},
        {"name": "express"},
        {"name": "lodash"}
    ],
    check_duplicates=True,
    check_outdated=True,
    check_unused=False
)
```

### 4. Ecosystem Analysis

```python
# Get platform statistics
platform_stats = await get_platform_stats(
    platform="npm",
    include_trending=True
)

# Explore ecosystem
ecosystem_prompt = await ecosystem_exploration_prompt(
    platform="pypi",
    language="Python"
)

# Check license compatibility
license_check = await check_license_compatibility(
    licenses=["MIT", "Apache-2.0", "BSD-3-Clause"],
    use_case="commercial"
)
```

### 5. Project Management

```python
# Track package updates
update_tracking = await track_package_updates(
    platform="npm",
    name="react",
    check_interval="daily",
    include_security=True
)

# Generate project health analysis
health_analysis = await analyze_project_health(
    project_name="my-web-app",
    platform="npm"
)

# Generate maintenance report
maintenance_report = await maintenance_status_report(
    project_name="django-blog",
    platform="pypi",
    time_period="6 months"
)
```

## Error Handling

### Common Error Responses

All tools return a consistent error format:

```json
{
  "success": false,
  "error": "Error message describing what went wrong",
  "details": {
    "code": "ERROR_CODE",
    "field": "field_name",
    "message": "Detailed error description"
  }
}
```

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `INVALID_PLATFORM` | Invalid package manager platform | Check platform name against supported platforms |
| `PACKAGE_NOT_FOUND` | Package not found | Verify package name and platform |
| `RATE_LIMIT_EXCEEDED` | API rate limit exceeded | Wait and retry, or implement rate limiting |
| `INVALID_PARAMETERS` | Invalid tool parameters | Check parameter types and values |
| `NETWORK_ERROR` | Network connectivity issue | Check internet connection and API status |
| `AUTHENTICATION_ERROR` | Invalid API key | Verify API key and permissions |
| `SERVER_ERROR` | Internal server error | Check server logs and retry |

### Error Handling Best Practices

```python
# Example error handling
try:
    result = await get_package_info(platform="npm", name="react")
    if not result.success:
        print(f"Error: {result.error}")
        # Handle specific error types
        if "rate_limit" in result.error.lower():
            # Implement backoff strategy
            await asyncio.sleep(60)
            result = await get_package_info(platform="npm", name="react")
except Exception as e:
    print(f"Unexpected error: {e}")
    # Implement fallback or retry logic
```

## Rate Limiting

### Rate Limit Information

All API responses include rate limit information:

```json
{
  "rate_limit_info": {
    "limit": 1000,
    "remaining": 850,
    "reset": "2024-01-15T12:00:00Z",
    "used": 150
  }
}
```

### Rate Limit Best Practices

1. **Monitor remaining requests**: Check `rate_limit_info.remaining` before making requests
2. **Implement exponential backoff**: Wait longer when approaching rate limits
3. **Cache responses**: Store frequently accessed data locally
4. **Batch requests**: Group multiple operations when possible
5. **Respect reset time**: Wait until `rate_limit_info.reset` before retrying

### Example Rate Limit Handling

```python
async def make_api_request_with_retry(tool_func, *args, max_retries=3):
    for attempt in range(max_retries):
        result = await tool_func(*args)
        
        if result.success:
            return result
        
        # Check if it's a rate limit error
        if "rate_limit" in result.error.lower():
            wait_time = min(60 * (2 ** attempt), 300)  # Exponential backoff, max 5 minutes
            await asyncio.sleep(wait_time)
            continue
        
        # For other errors, fail fast
        return result
    
    return result  # Return final failure result
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Package not found" errors

**Problem:** Package search or info requests fail with "Package not found"

**Solutions:**
- Verify the package name is spelled correctly
- Check if the platform is supported
- Try searching with different keywords
- Verify the package exists on the platform

```python
# Debug package search
search_result = await search_packages(
    query="package name",
    platforms=["npm"]
)
if not search_result.success:
    print(f"Search failed: {search_result.error}")
    # Try with different query
    search_result = await search_packages(
        query="package",
        platforms=["npm"]
    )
```

#### 2. Rate limit exceeded errors

**Problem:** API requests fail with rate limit exceeded

**Solutions:**
- Implement rate limiting in your application
- Add delays between requests
- Use caching for frequently accessed data
- Monitor rate limit headers

```python
# Implement rate limiting
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.last_request_time = datetime.min
        self.request_count = 0
    
    async def wait_if_needed(self):
        now = datetime.now()
        time_since_last = (now - self.last_request_time).total_seconds()
        
        if time_since_last < 60:  # Within the same minute
            if self.request_count >= self.requests_per_minute:
                wait_time = 60 - time_since_last
                await asyncio.sleep(wait_time)
                self.request_count = 0
        
        self.last_request_time = now
        self.request_count += 1

# Usage
rate_limiter = RateLimiter()

async def safe_api_call(tool_func, *args):
    await rate_limiter.wait_if_needed()
    return await tool_func(*args)
```

#### 3. Network connectivity issues

**Problem:** API requests fail due to network errors

**Solutions:**
- Check internet connection
- Verify API endpoint availability
- Implement retry logic with exponential backoff
- Use timeout settings

```python
# Network error handling with retries
async def resilient_api_call(tool_func, *args, max_retries=3, timeout=30):
    for attempt in range(max_retries):
        try:
            result = await asyncio.wait_for(tool_func(*args), timeout=timeout)
            return result
        except asyncio.TimeoutError:
            print(f"Timeout on attempt {attempt + 1}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            print(f"Network error on attempt {attempt + 1}: {e}")
            await asyncio.sleep(2 ** attempt)
    
    return {"success": False, "error": "Network error after retries"}
```

#### 4. Authentication issues

**Problem:** API requests fail with authentication errors

**Solutions:**
- Verify API key is valid and has sufficient permissions
- Check environment variable configuration
- Ensure API key hasn't expired
- Verify API key format

```python
# Authentication check
async def test_authentication():
    try:
        # Test with a simple request
        result = await get_platform_stats(platform="npm")
        if result.success:
            print("Authentication successful")
            return True
        else:
            print(f"Authentication failed: {result.error}")
            return False
    except Exception as e:
        print(f"Authentication error: {e}")
        return False
```

#### 5. Data parsing issues

**Problem:** API responses contain unexpected data formats

**Solutions:**
- Check API response structure
- Validate data types
- Handle missing fields gracefully
- Use proper error handling

```python
# Safe data parsing
def safe_parse_package_data(data):
    try:
        return {
            "name": data.get("name", "unknown"),
            "platform": data.get("platform", "unknown"),
            "description": data.get("description", ""),
            "stars": data.get("stars", 0),
            "language": data.get("language", "unknown")
        }
    except Exception as e:
        print(f"Data parsing error: {e}")
        return {
            "name": "unknown",
            "platform": "unknown",
            "description": "",
            "stars": 0,
            "language": "unknown"
        }
```

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("libraries_io_mcp")

# Make API calls with debug logging
logger.debug("Making API call to get package info")
result = await get_package_info(platform="npm", name="react")
logger.debug(f"API call result: {result}")
```

### Performance Optimization

#### 1. Caching Strategy

```python
import asyncio
from datetime import datetime, timedelta

class Cache:
    def __init__(self, ttl_minutes=30):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, datetime.now())

# Usage
cache = Cache()

async def cached_get_package_info(platform, name):
    cache_key = f"{platform}:{name}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data
    
    result = await get_package_info(platform, name)
    if result.success:
        cache.set(cache_key, result)
    
    return result
```

#### 2. Batch Processing

```python
async def batch_get_package_info(packages):
    """Get package info for multiple packages efficiently."""
    results = []
    
    for package in packages:
        result = await get_package_info(
            platform=package["platform"],
            name=package["name"]
        )
        results.append(result)
    
    return results

# Usage
packages = [
    {"platform": "npm", "name": "react"},
    {"platform": "npm", "name": "express"},
    {"platform": "pypi", "name": "django"}
]

results = await batch_get_package_info(packages)
```

#### 3. Parallel Processing

```python
import asyncio

async def parallel_package_analysis(packages):
    """Analyze multiple packages in parallel."""
    tasks = []
    
    for package in packages:
        task = asyncio.create_task(
            get_package_info(
                platform=package["platform"],
                name=package["name"]
            )
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# Usage
packages = [
    {"platform": "npm", "name": "react"},
    {"platform": "npm", "name": "express"},
    {"platform": "pypi", "name": "django"}
]

results = await parallel_package_analysis(packages)
```

## Best Practices

### 1. Error Handling

- Always check `result.success` before accessing data
- Implement retry logic for transient errors
- Log errors for debugging
- Provide meaningful error messages to users

### 2. Rate Limiting

- Monitor rate limit headers
- Implement exponential backoff
- Cache frequently accessed data
- Batch requests when possible

### 3. Data Validation

- Validate input parameters
- Check API response structure
- Handle missing or null values
- Use type hints and validation

### 4. Performance Optimization

- Use caching for frequently accessed data
- Implement parallel processing for batch operations
- Minimize API calls with efficient queries
- Use pagination for large result sets

### 5. Security

- Never expose API keys in client-side code
- Use environment variables for sensitive data
- Validate all user inputs
- Implement proper access controls

## Integration Examples

### 1. Claude Desktop Integration

```python
# Example of using Libraries.io tools in Claude Desktop
async def analyze_project_dependencies(project_name):
    """Analyze project dependencies using Claude Desktop."""
    
    # Get project dependencies
    dependencies = await get_project_dependencies(project_name)
    
    # Analyze each dependency
    analysis_results = []
    for dep in dependencies:
        result = await get_package_info(
            platform=dep["platform"],
            name=dep["name"]
        )
        
        if result.success:
            analysis_results.append({
                "package": dep["name"],
                "platform": dep["platform"],
                "info": result.data,
                "security_check": await check_package_security(
                    platform=dep["platform"],
                    name=dep["name"]
                )
            })
    
    return analysis_results
```

### 2. Web Application Integration

```python
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any

app = FastAPI()

@app.get("/api/packages/search")
async def search_packages_api(
    q: str,
    platforms: str = None,
    languages: str = None,
    licenses: str = None,
    page: int = 1,
    per_page: int = 10
):
    """Search packages via REST API."""
    try:
        result = await search_packages(
            query=q,
            platforms=platforms.split(',') if platforms else None,
            languages=languages.split(',') if languages else None,
            licenses=licenses.split(',') if licenses else None,
            page=page,
            per_page=per_page
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)
        
        return result.data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. CLI Tool Integration

```python
import click
import asyncio

@click.command()
@click.option('--platform', required=True, help='Package manager platform')
@click.option('--name', required=True, help='Package name')
@click.option('--include-versions', is_flag=True, help='Include version information')
async def get_package_info_cli(platform, name, include_versions):
    """Get package information via CLI."""
    try:
        result = await get_package_info(
            platform=platform,
            name=name,
            include_versions=include_versions
        )
        
        if result.success:
            package = result.data
            click.echo(f"Package: {package['name']}")
            click.echo(f"Platform: {package['platform']}")
            click.echo(f"Description: {package['description']}")
            click.echo(f"Stars: {package['stars']}")
            click.echo(f"Latest Version: {package['latest_version']}")
        else:
            click.echo(f"Error: {result.error}", err=True)
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

if __name__ == "__main__":
    asyncio.run(get_package_info_cli())
```

## Conclusion

The Libraries.io MCP Server provides a comprehensive set of tools, resources, and prompts for AI assistants to interact with open source package ecosystems. By following the API documentation and implementing best practices, you can build powerful applications that leverage the vast Libraries.io database.

## Additional Troubleshooting Resources

### Community Support

For additional support and questions:
- Check the [GitHub Issues](https://github.com/librariesio/libraries-io-mcp-server/issues)
- Review the [troubleshooting guide](docs/troubleshooting.md)
- Join the [community discussions](https://github.com/librariesio/libraries-io-mcp-server/discussions)

### Performance Monitoring

Monitor your API usage and performance:

```python
import time
from datetime import datetime

class APIMonitor:
    def __init__(self):
        self.request_times = []
        self.error_count = 0
        self.success_count = 0
    
    def log_request(self, success: bool, duration: float):
        self.request_times.append((datetime.now(), duration, success))
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def get_stats(self):
        recent_requests = [r for r in self.request_times if (datetime.now() - r[0]).seconds < 3600]
        avg_duration = sum(r[1] for r in recent_requests) / len(recent_requests) if recent_requests else 0
        error_rate = self.error_count / (self.success_count + self.error_count) if (self.success_count + self.error_count) > 0 else 0
        
        return {
            "total_requests": len(self.request_times),
            "success_rate": (self.success_count / (self.success_count + self.error_count)) * 100 if (self.success_count + self.error_count) > 0 else 0,
            "average_response_time": avg_duration,
            "error_rate": error_rate * 100
        }

# Usage
monitor = APIMonitor()

# Log requests
start_time = time.time()
result = await get_package_info(platform="npm", name="react")
duration = time.time() - start_time
monitor.log_request(result.success, duration)

# Get statistics
stats = monitor.get_stats()
print(f"API Statistics: {stats}")
```

### Advanced Error Recovery

Implement sophisticated error recovery strategies:

```python
import asyncio
from datetime import datetime, timedelta

class AdvancedErrorRecovery:
    def __init__(self, max_retries=5, base_delay=1):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.circuit_breaker_state = "closed"  # closed, open, half-open
        self.failure_count = 0
        self.last_failure_time = None
    
    async def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with advanced error recovery."""
        
        if self.circuit_breaker_state == "open":
            if datetime.now() - self.last_failure_time < timedelta(minutes=5):
                raise Exception("Circuit breaker is open - requests temporarily disabled")
            else:
                self.circuit_breaker_state = "half-open"
        
        for attempt in range(self.max_retries):
            try:
                result = await func(*args, **kwargs)
                
                if self.circuit_breaker_state == "half-open":
                    self.circuit_breaker_state = "closed"
                    self.failure_count = 0
                
                return result
                
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = datetime.now()
                
                if self.failure_count >= 5:
                    self.circuit_breaker_state = "open"
                    raise Exception("Circuit breaker opened due to too many failures")
                
                # Exponential backoff with jitter
                delay = self.base_delay * (2 ** attempt) + (hash(str(datetime.now())) % 1000) / 1000
                await asyncio.sleep(delay)
        
        raise Exception(f"Failed after {self.max_retries} attempts")

# Usage
recovery = AdvancedErrorRecovery()

# Execute with error recovery
try:
    result = await recovery.execute_with_retry(get_package_info, platform="npm", name="react")
    print(f"Success: {result}")
except Exception as e:
    print(f"Failed: {e}")
```

### Data Consistency Checks

Ensure data consistency across API calls:

```python
class DataConsistencyChecker:
    def __init__(self):
        self.package_cache = {}
    
    async def check_package_consistency(self, platform: str, name: str):
        """Check if package data is consistent across different API calls."""
        
        cache_key = f"{platform}:{name}"
        
        # Get package info
        info_result = await get_package_info(platform=platform, name=name)
        if not info_result.success:
            return {"consistent": False, "error": info_result.error}
        
        # Get package versions
        versions_result = await get_package_versions(platform=platform, name=name)
        if not versions_result.success:
            return {"consistent": False, "error": versions_result.error}
        
        # Check consistency
        package_info = info_result.data
        package_versions = versions_result.data
        
        inconsistencies = []
        
        # Check if latest version matches
        if package_info.get("latest_version") != package_versions.get("versions", [{}])[0].get("number"):
            inconsistencies.append("Latest version mismatch")
        
        # Check if version count matches
        if len(package_versions.get("versions", [])) != package_info.get("version_count", 0):
            inconsistencies.append("Version count mismatch")
        
        # Check if package has dependencies but none listed
        if package_info.get("has_dependencies") and not package_versions.get("dependencies"):
            inconsistencies.append("Dependencies missing")
        
        return {
            "consistent": len(inconsistencies) == 0,
            "inconsistencies": inconsistencies,
            "package_info": package_info,
            "package_versions": package_versions
        }

# Usage
checker = DataConsistencyChecker()
consistency_result = await checker.check_package_consistency("npm", "react")
print(f"Data consistency: {consistency_result}")
```

### API Health Check

Implement comprehensive API health checks:

```python
async def comprehensive_health_check():
    """Perform comprehensive health check of the MCP server."""
    
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "healthy",
        "checks": {}
    }
    
    # Test basic connectivity
    try:
        result = await get_platform_stats(platform="npm")
        health_status["checks"]["basic_connectivity"] = {
            "status": "healthy" if result.success else "unhealthy",
            "response_time": getattr(result, 'response_time', 0),
            "error": result.error if not result.success else None
        }
    except Exception as e:
        health_status["checks"]["basic_connectivity"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["overall_status"] = "unhealthy"
    
    # Test rate limiting
    try:
        rate_limit_info = None
        for _ in range(3):
            result = await search_packages(query="test", per_page=1)
            if result.success and hasattr(result, 'rate_limit_info'):
                rate_limit_info = result.rate_limit_info
                break
        
        health_status["checks"]["rate_limiting"] = {
            "status": "healthy" if rate_limit_info else "unhealthy",
            "rate_limit_info": rate_limit_info
        }
    except Exception as e:
        health_status["checks"]["rate_limiting"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Test data consistency
    try:
        checker = DataConsistencyChecker()
        consistency_result = await checker.check_package_consistency("npm", "react")
        health_status["checks"]["data_consistency"] = {
            "status": "healthy" if consistency_result["consistent"] else "unhealthy",
            "inconsistencies": consistency_result["inconsistencies"]
        }
    except Exception as e:
        health_status["checks"]["data_consistency"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Test authentication
    try:
        auth_result = await get_trending_packages(platform="npm", limit=1)
        health_status["checks"]["authentication"] = {
            "status": "healthy" if auth_result.success else "unhealthy",
            "error": auth_result.error if not auth_result.success else None
        }
    except Exception as e:
        health_status["checks"]["authentication"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Determine overall status
    for check_name, check_result in health_status["checks"].items():
        if check_result["status"] == "unhealthy":
            health_status["overall_status"] = "degraded"
            break
    
    return health_status

# Usage
health_status = await comprehensive_health_check()
print(f"Health Status: {health_status}")
```

### Memory Usage Optimization

Optimize memory usage for large-scale operations:

```python
import gc
import psutil
import os

class MemoryOptimizer:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
    
    def get_memory_usage(self):
        """Get current memory usage."""
        memory_info = self.process.memory_info()
        return {
            "rss": memory_info.rss / 1024 / 1024,  # MB
            "vms": memory_info.vms / 1024 / 1024,  # MB
            "percent": self.process.memory_percent()
        }
    
    async def process_large_dataset(self, packages, batch_size=50):
        """Process large dataset with memory optimization."""
        memory_before = self.get_memory_usage()
        
        results = []
        
        for i in range(0, len(packages), batch_size):
            batch = packages[i:i + batch_size]
            
            # Process batch
            batch_results = []
            for package in batch:
                try:
                    result = await get_package_info(
                        platform=package["platform"],
                        name=package["name"]
                    )
                    batch_results.append(result)
                except Exception as e:
                    batch_results.append({"success": False, "error": str(e)})
            
            results.extend(batch_results)
            
            # Clean up memory
            del batch_results
            gc.collect()
            
            # Check memory usage
            memory_current = self.get_memory_usage()
            if memory_current["percent"] > 80:  # If using more than 80% memory
                print(f"High memory usage: {memory_current['percent']}%")
                # Force garbage collection
                gc.collect()
                memory_after_gc = self.get_memory_usage()
                print(f"Memory after GC: {memory_after_gc['percent']}%")
        
        memory_after = self.get_memory_usage()
        
        return {
            "results": results,
            "memory_before": memory_before,
            "memory_after": memory_after,
            "memory_delta": memory_after["rss"] - memory_before["rss"]
        }

# Usage
optimizer = MemoryOptimizer()

# Process large dataset
large_packages = [{"platform": "npm", "name": f"package_{i}"} for i in range(1000)]
result = await optimizer.process_large_dataset(large_packages)
print(f"Processed {len(result['results'])} packages")
print(f"Memory usage: {result['memory_delta']:.2f} MB increase")
```

### Load Testing

Implement load testing for your application:

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from statistics import mean, median

class LoadTester:
    def __init__(self, max_concurrent=10):
        self.max_concurrent = max_concurrent
    
    async def simulate_load(self, test_func, num_requests=100, duration_seconds=30):
        """Simulate load on the API."""
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        results = []
        active_requests = 0
        
        async def make_request():
            nonlocal active_requests
            active_requests += 1
            
            try:
                request_start = time.time()
                result = await test_func()
                request_end = time.time()
                
                results.append({
                    "success": result.success,
                    "response_time": request_end - request_start,
                    "error": result.error if not result.success else None
                })
                
                return result
            finally:
                active_requests -= 1
        
        # Create tasks
        tasks = []
        for i in range(num_requests):
            if time.time() >= end_time:
                break
            
            # Wait if too many concurrent requests
            while active_requests >= self.max_concurrent:
                await asyncio.sleep(0.1)
            
            task = asyncio.create_task(make_request())
            tasks.append(task)
            
            # Add delay between requests
            await asyncio.sleep(0.1)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate statistics
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        response_times = [r["response_time"] for r in successful_requests]
        
        return {
            "total_requests": len(results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": (len(successful_requests) / len(results)) * 100 if results else 0,
            "average_response_time": mean(response_times) if response_times else 0,
            "median_response_time": median(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "requests_per_second": len(results) / duration_seconds if duration_seconds > 0 else 0
        }

# Usage
tester = LoadTester(max_concurrent=20)

# Test search functionality
async def test_search():
    return await search_packages(query="test", per_page=10)

load_test_results = await tester.simulate_load(test_search, num_requests=100, duration_seconds=30)
print(f"Load Test Results: {load_test_results}")
```

### Configuration Validation

Validate your configuration before making API calls:

```python
import os
from typing import Dict, Any

class ConfigurationValidator:
    def __init__(self):
        self.required_env_vars = [
            "LIBRARIES_IO_API_KEY",
            "LIBRARIES_IO_BASE_URL"
        ]
        self.optional_env_vars = [
            "RATE_LIMIT_REQUESTS",
            "RATE_LIMIT_WINDOW",
            "REQUEST_TIMEOUT",
            "MAX_RETRIES"
        ]
    
    def validate_environment(self) -> Dict[str, Any]:
        """Validate environment configuration."""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "config": {}
        }
        
        # Check required variables
        for var in self.required_env_vars:
            if var not in os.environ:
                validation_result["errors"].append(f"Missing required environment variable: {var}")
                validation_result["valid"] = False
            else:
                validation_result["config"][var] = os.environ[var]
        
        # Check optional variables
        for var in self.optional_env_vars:
            if var in os.environ:
                validation_result["config"][var] = os.environ[var]
        
        # Validate API key format
        api_key = validation_result["config"].get("LIBRARIES_IO_API_KEY", "")
        if len(api_key) < 10:
            validation_result["warnings"].append("API key appears to be too short")
        
        # Validate base URL
        base_url = validation_result["config"].get("LIBRARIES_IO_BASE_URL", "")
        if not base_url.startswith("http"):
            validation_result["errors"].append("Base URL must start with http:// or https://")
            validation_result["valid"] = False
        
        # Validate rate limiting
        rate_limit_requests = validation_result["config"].get("RATE_LIMIT_REQUESTS", "100")
        try:
            int(rate_limit_requests)
        except ValueError:
            validation_result["errors"].append("RATE_LIMIT_REQUESTS must be an integer")
            validation_result["valid"] = False
        
        return validation_result
    
    def validate_client_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate client configuration."""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate timeout
        timeout = config.get("timeout", 30)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            validation_result["errors"].append("Timeout must be a positive number")
            validation_result["valid"] = False
        
        # Validate max retries
        max_retries = config.get("max_retries", 3)
        if not isinstance(max_retries, int) or max_retries < 0:
            validation_result["errors"].append("Max retries must be a non-negative integer")
            validation_result["valid"] = False
        
        # Validate rate limiting
        rate_limit = config.get("rate_limit", {})
        if not isinstance(rate_limit, dict):
            validation_result["errors"].append("Rate limit must be a dictionary")
            validation_result["valid"] = False
        
        return validation_result

# Usage
validator = ConfigurationValidator()

# Validate environment
env_validation = validator.validate_environment()
print(f"Environment Validation: {env_validation}")

# Validate client config
client_config = {
    "timeout": 30,
    "max_retries": 3,
    "rate_limit": {"requests_per_minute": 60}
}
config_validation = validator.validate_client_config(client_config)
print(f"Config Validation: {config_validation}")
```

### Advanced Logging

Implement comprehensive logging for debugging and monitoring:

```python
import logging
import json
from datetime import datetime
from typing import Dict, Any

class APILogger:
    def __init__(self, log_level=logging.INFO):
        self.logger = logging.getLogger("libraries_io_mcp")
        self.logger.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler('libraries_io_mcp.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # JSON formatter for structured logging
        json_formatter = JSONFormatter()
        json_file_handler = logging.FileHandler('libraries_io_mcp.json')
        json_file_handler.setFormatter(json_formatter)
        self.logger.addHandler(json_file_handler)
    
    def log_api_call(self, tool_name: str, params: Dict[str, Any], result: Dict[str, Any]):
        """Log API call with structured data."""
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "parameters": params,
            "success": result.get("success", False),
            "response_time": getattr(result, 'response_time', 0),
            "error": result.get("error", None),
            "rate_limit_info": getattr(result, 'rate_limit_info', None)
        }
        
        if result.get("success"):
            self.logger.info(f"API Call Success: {tool_name}", extra={"data": log_data})
        else:
            self.logger.error(f"API Call Failed: {tool_name}", extra={"data": log_data})
    
    def log_performance_metrics(self, metrics: Dict[str, Any]):
        """Log performance metrics."""
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        self.logger.info("Performance Metrics", extra={"data": log_data})
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log error with context."""
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        
        self.logger.error("Error occurred", extra={"data": log_data}, exc_info=True)

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra data if present
        if hasattr(record, 'data'):
            log_data.update(record.data)
        
        return json.dumps(log_data)

# Usage
logger = APILogger()

# Log API call
result = await get_package_info(platform="npm", name="react")
logger.log_api_call("get_package_info", {"platform": "npm", "name": "react"}, result)

# Log performance metrics
metrics = {
    "requests_per_second": 10.5,
    "average_response_time": 1.2,
    "success_rate": 98.5
}
logger.log_performance_metrics(metrics)

# Log error
try:
    result = await get_package_info(platform="invalid", name="test")
except Exception as e:
    logger.log_error(e, {"tool": "get_package_info", "params": {"platform": "invalid", "name": "test"}})
```

### Security Best Practices

Implement additional security measures:

```python
import hashlib
import hmac
import secrets
from typing import Dict, Any

class SecurityManager:
    def __init__(self):
        self.api_key_hash = None
        self.request_signatures = {}
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for secure storage."""
        salt = secrets.token_hex(16)
        key_hash = hashlib.pbkdf2_hmac('sha256', api_key.encode(), salt.encode(), 100000)
        return f"{salt}:{key_hash.hex()}"
    
    def verify_api_key(self, api_key: str, hashed_key: str) -> bool:
        """Verify API key against hash."""
        try:
            salt, key_hash = hashed_key.split(':')
            computed_hash = hashlib.pbkdf2_hmac('sha256', api_key.encode(), salt.encode(), 100000)
            return hmac.compare_digest(computed_hash.hex(), key_hash)
        except Exception:
            return False
    
    def generate_request_signature(self, request_data: Dict[str, Any], api_key: str) -> str:
        """Generate request signature for integrity verification."""
        # Create signature string
        signature_string = json.dumps(request_data, sort_keys=True)
        
        # Generate signature
        signature = hmac.new(
            api_key.encode(),
            signature_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_request_signature(self, request_data: Dict[str, Any], signature: str, api_key: str) -> bool:
        """Verify request signature."""
        expected_signature = self.generate_request_signature(request_data, api_key)
        return hmac.compare_digest(expected_signature, signature)
    
    def sanitize_input(self, input_data: str) -> str:
        """Sanitize input to prevent injection attacks."""
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '(', ')', '{', '}', '[', ']']
        sanitized = input_data
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized
    
    def validate_package_name(self, package_name: str) -> bool:
        """Validate package name format."""
        if not package_name or len(package_name) > 100:
            return False
        
        # Check for invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ']
        for char in invalid_chars:
            if char in package_name:
                return False
        
        return True
    
    def validate_platform(self, platform: str) -> bool:
        """Validate platform name."""
        valid_platforms = ['npm', 'pypi', 'maven', 'nuget', 'gem', 'cargo', 'go', 'docker']
        return platform.lower() in valid_platforms

# Usage
security_manager = SecurityManager()

# Hash API key
api_key = "your_api_key_here"
hashed_key = security_manager.hash_api_key(api_key)
print(f"Hashed API key: {hashed_key}")

# Verify API key
is_valid = security_manager.verify_api_key(api_key, hashed_key)
print(f"API key valid: {is_valid}")

# Sanitize input
user_input = "package<script>alert('xss')</script>"
sanitized_input = security_manager.sanitize_input(user_input)
print(f"Sanitized input: {sanitized_input}")

# Validate package name
package_name = "react"
is_valid_name = security_manager.validate_package_name(package_name)
print(f"Package name valid: {is_valid_name}")
```

### Conclusion

The Libraries.io MCP Server provides a comprehensive set of tools, resources, and prompts for AI assistants to interact with open source package ecosystems. By following the API documentation and implementing best practices, you can build powerful applications that leverage the vast Libraries.io database.

For additional support and questions:
- Check the [GitHub Issues](https://github.com/librariesio/libraries-io-mcp-server/issues)
- Review the [troubleshooting guide](docs/troubleshooting.md)
- Join the [community discussions](https://github.com/librariesio/libraries-io-mcp-server/discussions)

The troubleshooting section has been enhanced with advanced topics including:
- Performance monitoring and optimization
- Advanced error recovery strategies
- Data consistency checks
- API health monitoring
- Memory usage optimization
- Load testing capabilities
- Configuration validation
- Comprehensive logging
- Security best practices

These additional resources will help you build robust, production-ready applications using the Libraries.io MCP Server.
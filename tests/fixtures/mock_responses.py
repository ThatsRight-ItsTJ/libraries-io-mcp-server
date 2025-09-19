"""
Mock responses for testing the Libraries.io MCP Server.

This module contains mock API responses for testing purposes.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


class MockResponses:
    """Collection of mock API responses for testing."""
    
    @staticmethod
    def get_platforms_response() -> List[Dict[str, Any]]:
        """Mock response for platforms endpoint."""
        return [
            {
                "name": "npm",
                "project_count": 2000000,
                "homepage": "https://www.npmjs.com/",
                "color": "#cb3837",
                "default_language": "JavaScript",
                "package_type": "library"
            },
            {
                "name": "pypi",
                "project_count": 350000,
                "homepage": "https://pypi.org/",
                "color": "#3776ab",
                "default_language": "Python",
                "package_type": "library"
            },
            {
                "name": "maven",
                "project_count": 8000,
                "homepage": "https://maven.apache.org/",
                "color": "#c71e1d",
                "default_language": "Java",
                "package_type": "library"
            },
            {
                "name": "gem",
                "project_count": 150000,
                "homepage": "https://rubygems.org/",
                "color": "#cc342d",
                "default_language": "Ruby",
                "package_type": "library"
            },
            {
                "name": "nuget",
                "project_count": 100000,
                "homepage": "https://www.nuget.org/",
                "color": "#004880",
                "default_language": "C#",
                "package_type": "library"
            }
        ]
    
    @staticmethod
    def get_package_response() -> Dict[str, Any]:
        """Mock response for package endpoint."""
        return {
            "name": "react",
            "platform": "npm",
            "description": "A declarative, efficient, and flexible JavaScript library for building user interfaces.",
            "homepage": "https://reactjs.org/",
            "repository_url": "https://github.com/facebook/react",
            "language": "JavaScript",
            "keywords": [
                "react",
                "react-component",
                "ui",
                "ux",
                "javascript",
                "html",
                "css"
            ],
            "licenses": "MIT",
            "latest_release_number": "18.2.0",
            "latest_release_published_at": "2023-03-06T20:15:00.000Z",
            "stars": 200000,
            "forks": 42000,
            "dependent_repositories": 1500000,
            "dependent_repositories_count": 1500000
        }
    
    @staticmethod
    def get_package_versions_response() -> List[Dict[str, Any]]:
        """Mock response for package versions endpoint."""
        return [
            {
                "number": "18.2.0",
                "published_at": "2023-03-06T20:15:00.000Z",
                "spdx_expression": "MIT",
                "original_license": "MIT",
                "status": "active"
            },
            {
                "number": "18.1.0",
                "published_at": "2023-01-10T15:30:00.000Z",
                "spdx_expression": "MIT",
                "original_license": "MIT",
                "status": "active"
            },
            {
                "number": "18.0.0",
                "published_at": "2022-11-09T12:00:00.000Z",
                "spdx_expression": "MIT",
                "original_license": "MIT",
                "status": "active"
            },
            {
                "number": "17.0.2",
                "published_at": "2022-10-25T09:45:00.000Z",
                "spdx_expression": "MIT",
                "original_license": "MIT",
                "status": "active"
            },
            {
                "number": "17.0.1",
                "published_at": "2022-10-22T14:20:00.000Z",
                "spdx_expression": "MIT",
                "original_license": "MIT",
                "status": "active"
            }
        ]
    
    @staticmethod
    def get_package_dependencies_response() -> List[Dict[str, Any]]:
        """Mock response for package dependencies endpoint."""
        return [
            {
                "project": {
                    "name": "react-dom",
                    "platform": "npm"
                },
                "requirements": ">=18.0.0",
                "kind": "runtime",
                "optional": False,
                "resolved": "18.2.0"
            },
            {
                "project": {
                    "name": "react-reconciler",
                    "platform": "npm"
                },
                "requirements": ">=18.0.0",
                "kind": "runtime",
                "optional": False,
                "resolved": "18.2.0"
            },
            {
                "project": {
                    "name": "scheduler",
                    "platform": "npm"
                },
                "requirements": ">=0.23.0",
                "kind": "runtime",
                "optional": False,
                "resolved": "0.23.0"
            },
            {
                "project": {
                    "name": "@types/react",
                    "platform": "npm"
                },
                "requirements": ">=18.0.0",
                "kind": "development",
                "optional": True,
                "resolved": "18.2.0"
            },
            {
                "project": {
                    "name": "@types/react-dom",
                    "platform": "npm"
                },
                "requirements": ">=18.0.0",
                "kind": "development",
                "optional": True,
                "resolved": "18.2.0"
            }
        ]
    
    @staticmethod
    def get_package_dependents_response() -> List[Dict[str, Any]]:
        """Mock response for package dependents endpoint."""
        return [
            {
                "name": "next",
                "platform": "npm",
                "description": "The React Framework for Production",
                "homepage": "https://nextjs.org/",
                "language": "JavaScript",
                "keywords": [
                    "react",
                    "next",
                    "framework",
                    "javascript"
                ],
                "licenses": "MIT",
                "stars": 100000,
                "forks": 20000,
                "dependent_repositories": 50000
            },
            {
                "name": "create-react-app",
                "platform": "npm",
                "description": "Create React apps with no build configuration.",
                "homepage": "https://create-react-app.dev/",
                "language": "JavaScript",
                "keywords": [
                    "react",
                    "create-react-app",
                    "javascript"
                ],
                "licenses": "MIT",
                "stars": 95000,
                "forks": 25000,
                "dependent_repositories": 30000
            },
            {
                "name": "react-router-dom",
                "platform": "npm",
                "description": "Declarative routing for React",
                "homepage": "https://reactrouter.com/",
                "language": "JavaScript",
                "keywords": [
                    "react",
                    "router",
                    "routing",
                    "javascript"
                ],
                "licenses": "MIT",
                "stars": 48000,
                "forks": 8000,
                "dependent_repositories": 15000
            }
        ]
    
    @staticmethod
    def get_search_response() -> Dict[str, Any]:
        """Mock response for search endpoint."""
        return {
            "total": 150,
            "items": [
                {
                    "name": "react",
                    "platform": "npm",
                    "description": "A declarative, efficient, and flexible JavaScript library for building user interfaces.",
                    "homepage": "https://reactjs.org/",
                    "language": "JavaScript",
                    "keywords": [
                        "react",
                        "react-component",
                        "ui",
                        "ux",
                        "javascript"
                    ],
                    "licenses": "MIT",
                    "stars": 200000,
                    "forks": 42000,
                    "dependent_repositories": 1500000
                },
                {
                    "name": "react-dom",
                    "platform": "npm",
                    "description": "React package for working with the DOM.",
                    "homepage": "https://reactjs.org/",
                    "language": "JavaScript",
                    "keywords": [
                        "react",
                        "react-dom",
                        "javascript"
                    ],
                    "licenses": "MIT",
                    "stars": 25000,
                    "forks": 3000,
                    "dependent_repositories": 500000
                },
                {
                    "name": "react-router",
                    "platform": "npm",
                    "description": "A complete routing library for React",
                    "homepage": "https://reacttraining.com/react-router/",
                    "language": "JavaScript",
                    "keywords": [
                        "react",
                        "router",
                        "routing",
                        "javascript"
                    ],
                    "licenses": "MIT",
                    "stars": 48000,
                    "forks": 8000,
                    "dependent_repositories": 15000
                }
            ],
            "page": 1,
            "per_page": 10
        }
    
    @staticmethod
    def get_user_response() -> Dict[str, Any]:
        """Mock response for user endpoint."""
        return {
            "login": "facebook",
            "name": "Facebook",
            "type": "organization",
            "avatar_url": "https://avatars.githubusercontent.com/u/69631?v=4",
            "blog": "https://code.facebook.com/",
            "location": "Menlo Park, CA",
            "email": "opensource@fb.com",
            "public_repos": 100,
            "public_gists": 50,
            "followers": 1000,
            "following": 500,
            "created_at": "2007-05-23T15:22:27.000Z",
            "updated_at": "2023-01-01T00:00:00.000Z"
        }
    
    @staticmethod
    def get_user_packages_response() -> List[Dict[str, Any]]:
        """Mock response for user packages endpoint."""
        return [
            {
                "name": "react",
                "platform": "npm",
                "description": "A declarative, efficient, and flexible JavaScript library for building user interfaces.",
                "homepage": "https://reactjs.org/",
                "language": "JavaScript",
                "keywords": [
                    "react",
                    "react-component",
                    "ui",
                    "ux",
                    "javascript"
                ],
                "licenses": "MIT",
                "stars": 200000,
                "forks": 42000,
                "dependent_repositories": 1500000
            },
            {
                "name": "react-dom",
                "platform": "npm",
                "description": "React package for working with the DOM.",
                "homepage": "https://reactjs.org/",
                "language": "JavaScript",
                "keywords": [
                    "react",
                    "react-dom",
                    "javascript"
                ],
                "licenses": "MIT",
                "stars": 25000,
                "forks": 3000,
                "dependent_repositories": 500000
            }
        ]
    
    @staticmethod
    def get_organization_response() -> Dict[str, Any]:
        """Mock response for organization endpoint."""
        return {
            "login": "facebook",
            "name": "Facebook",
            "type": "organization",
            "avatar_url": "https://avatars.githubusercontent.com/u/69631?v=4",
            "blog": "https://code.facebook.com/",
            "location": "Menlo Park, CA",
            "email": "opensource@fb.com",
            "public_repos": 100,
            "public_gists": 50,
            "followers": 1000,
            "following": 500,
            "created_at": "2007-05-23T15:22:27.000Z",
            "updated_at": "2023-01-01T00:00:00.000Z"
        }
    
    @staticmethod
    def get_organization_packages_response() -> List[Dict[str, Any]]:
        """Mock response for organization packages endpoint."""
        return [
            {
                "name": "react",
                "platform": "npm",
                "description": "A declarative, efficient, and flexible JavaScript library for building user interfaces.",
                "homepage": "https://reactjs.org/",
                "language": "JavaScript",
                "keywords": [
                    "react",
                    "react-component",
                    "ui",
                    "ux",
                    "javascript"
                ],
                "licenses": "MIT",
                "stars": 200000,
                "forks": 42000,
                "dependent_repositories": 1500000
            },
            {
                "name": "react-native",
                "platform": "npm",
                "description": "A framework for building native applications using React.",
                "homepage": "https://reactnative.dev/",
                "language": "JavaScript",
                "keywords": [
                    "react",
                    "react-native",
                    "mobile",
                    "javascript"
                ],
                "licenses": "MIT",
                "stars": 110000,
                "forks": 25000,
                "dependent_repositories": 80000
            }
        ]
    
    @staticmethod
    def get_repository_response() -> Dict[str, Any]:
        """Mock response for repository endpoint."""
        return {
            "name": "react",
            "platform": "github",
            "description": "A declarative, efficient, and flexible JavaScript library for building user interfaces.",
            "homepage": "https://reactjs.org/",
            "language": "JavaScript",
            "stars": 200000,
            "forks": 42000,
            "watchers": 5000,
            "created_at": "2013-05-24T02:18:36.000Z",
            "updated_at": "2023-01-01T00:00:00.000Z",
            "pushed_at": "2023-01-01T00:00:00.000Z",
            "default_branch": "main",
            "size": 100000,
            "stargazers_count": 200000,
            "watchers_count": 5000,
            "forks_count": 42000,
            "open_issues_count": 1000,
            "has_issues": True,
            "has_wiki": True,
            "has_pages": False,
            "has_downloads": True,
            "archived": False,
            "disabled": False,
            "license": {
                "key": "mit",
                "name": "MIT License",
                "spdx_id": "MIT",
                "url": "https://api.github.com/licenses/mit"
            }
        }
    
    @staticmethod
    def get_error_response(status_code: int, message: str) -> Dict[str, Any]:
        """Mock error response."""
        return {
            "error": {
                "status": status_code,
                "message": message
            }
        }
    
    @staticmethod
    def get_rate_limit_headers() -> Dict[str, str]:
        """Mock rate limit headers."""
        return {
            "x-ratelimit-limit": "60",
            "x-ratelimit-remaining": "59",
            "x-ratelimit-reset": "1234567890",
            "x-ratelimit-used": "1"
        }
    
    @staticmethod
    def get_empty_response() -> Dict[str, Any]:
        """Mock empty response."""
        return {}
    
    @staticmethod
    def get_large_response() -> Dict[str, Any]:
        """Mock large response for performance testing."""
        packages = []
        for i in range(100):
            packages.append({
                "name": f"package-{i}",
                "platform": "npm",
                "description": f"Test package {i}",
                "homepage": f"https://example.com/package-{i}",
                "language": "JavaScript",
                "keywords": ["test", "package"],
                "licenses": "MIT",
                "stars": 1000 + i,
                "forks": 100 + i,
                "dependent_repositories": 10000 + i
            })
        
        return {
            "total": 100,
            "items": packages,
            "page": 1,
            "per_page": 100
        }


class MockRequestData:
    """Collection of mock request data for testing."""
    
    @staticmethod
    def get_package_request() -> Dict[str, Any]:
        """Mock package request data."""
        return {
            "platform": "npm",
            "name": "react",
            "include_versions": True,
            "include_dependencies": True
        }
    
    @staticmethod
    def get_search_request() -> Dict[str, Any]:
        """Mock search request data."""
        return {
            "query": "react",
            "platforms": ["npm"],
            "languages": ["JavaScript"],
            "licenses": ["MIT"],
            "page": 1,
            "per_page": 10
        }
    
    @staticmethod
    def get_dependencies_request() -> Dict[str, Any]:
        """Mock dependencies request data."""
        return {
            "platform": "npm",
            "name": "react",
            "version": "18.2.0"
        }
    
    @staticmethod
    def get_dependents_request() -> Dict[str, Any]:
        """Mock dependents request data."""
        return {
            "platform": "npm",
            "name": "react",
            "page": 1,
            "per_page": 20
        }
    
    @staticmethod
    def get_compare_request() -> Dict[str, Any]:
        """Mock compare request data."""
        return {
            "platform": "npm",
            "packages": ["react", "vue", "angular"]
        }
    
    @staticmethod
    def get_security_request() -> Dict[str, Any]:
        """Mock security request data."""
        return {
            "platform": "npm",
            "name": "react",
            "version": "18.2.0"
        }
    
    @staticmethod
    def get_dependency_tree_request() -> Dict[str, Any]:
        """Mock dependency tree request data."""
        return {
            "platform": "npm",
            "name": "react",
            "max_depth": 3
        }
    
    @staticmethod
    def get_alternatives_request() -> Dict[str, Any]:
        """Mock alternatives request data."""
        return {
            "platform": "npm",
            "name": "react",
            "criteria": ["stars", "downloads", "recent_updates"]
        }
    
    @staticmethod
    def get_platform_stats_request() -> Dict[str, Any]:
        """Mock platform stats request data."""
        return {
            "platform": "npm"
        }
    
    @staticmethod
    def get_license_compatibility_request() -> Dict[str, Any]:
        """Mock license compatibility request data."""
        return {
            "platform": "npm",
            "name": "react",
            "target_license": "MIT"
        }
    
    @staticmethod
    def get_track_updates_request() -> Dict[str, Any]:
        """Mock track updates request data."""
        return {
            "platform": "npm",
            "name": "react",
            "check_updates": True
        }
    
    @staticmethod
    def get_dependency_report_request() -> Dict[str, Any]:
        """Mock dependency report request data."""
        return {
            "packages": [
                {"platform": "npm", "name": "react"},
                {"platform": "npm", "name": "vue"}
            ],
            "include_versions": True,
            "include_dependencies": True,
            "include_security": True
        }
    
    @staticmethod
    def get_audit_project_request() -> Dict[str, Any]:
        """Mock audit project request data."""
        return {
            "platform": "npm",
            "packages": [
                {"name": "react"},
                {"name": "vue"},
                {"name": "angular"}
            ],
            "check_duplicates": True,
            "check_unused": False,
            "check_outdated": True
        }


class MockScenarios:
    """Collection of mock scenarios for testing edge cases."""
    
    @staticmethod
    def get_rate_limited_scenario():
        """Mock scenario for rate limiting."""
        return {
            "status_code": 429,
            "headers": MockResponses.get_rate_limit_headers(),
            "response": MockResponses.get_error_response(429, "Rate limit exceeded")
        }
    
    @staticmethod
    def get_not_found_scenario():
        """Mock scenario for not found error."""
        return {
            "status_code": 404,
            "headers": {},
            "response": MockResponses.get_error_response(404, "Package not found")
        }
    
    @staticmethod
    def get_authentication_failed_scenario():
        """Mock scenario for authentication failure."""
        return {
            "status_code": 401,
            "headers": {},
            "response": MockResponses.get_error_response(401, "Authentication failed")
        }
    
    @staticmethod
    def get_server_error_scenario():
        """Mock scenario for server error."""
        return {
            "status_code": 500,
            "headers": {},
            "response": MockResponses.get_error_response(500, "Internal server error")
        }
    
    @staticmethod
    def get_timeout_scenario():
        """Mock scenario for timeout."""
        return {
            "status_code": 408,
            "headers": {},
            "response": MockResponses.get_error_response(408, "Request timeout")
        }
    
    @staticmethod
    def get_network_error_scenario():
        """Mock scenario for network error."""
        return {
            "status_code": 0,
            "headers": {},
            "response": None,
            "error": "Network error"
        }
    
    @staticmethod
    def get_invalid_response_scenario():
        """Mock scenario for invalid response."""
        return {
            "status_code": 200,
            "headers": {},
            "response": "Invalid JSON response"
        }
    
    @staticmethod
    def get_empty_response_scenario():
        """Mock scenario for empty response."""
        return {
            "status_code": 200,
            "headers": {},
            "response": MockResponses.get_empty_response()
        }
    
    @staticmethod
    def get_large_response_scenario():
        """Mock scenario for large response."""
        return {
            "status_code": 200,
            "headers": {},
            "response": MockResponses.get_large_response()
        }


# Export all mock responses
__all__ = [
    "MockResponses",
    "MockRequestData", 
    "MockScenarios"
]
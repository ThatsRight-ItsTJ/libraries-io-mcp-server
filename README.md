# Libraries.io MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0-green.svg)](https://github.com/pydantic/fastmcp)

A comprehensive Model Context Protocol (MCP) server that provides AI assistants with seamless access to Libraries.io's vast database of 9.96M+ open source packages across 33+ package managers including NPM, PyPI, Maven, Go, NuGet, and more.

## 🚀 Overview

The Libraries.io MCP Server transforms how AI assistants interact with open source ecosystems by providing:

- **Package Discovery**: Search, filter, and discover packages across multiple platforms
- **Deep Analysis**: Comprehensive dependency analysis, security checks, and license compatibility
- **Ecosystem Insights**: Platform statistics, trending packages, and alternative recommendations
- **Project Management**: Dependency auditing, update tracking, and comprehensive reporting
- **Real-time Data**: Access to current package information, versions, and dependencies

## ✨ Features

### 🔍 Package Discovery & Search
- Search packages by keywords, languages, licenses, and platforms
- Discover trending and popular packages
- Filter results by specific criteria
- Compare multiple packages side-by-side

### 📊 Package Analysis
- Detailed package information and metadata
- Complete version history and release tracking
- Dependency tree analysis with configurable depth
- Security vulnerability assessments
- License compatibility checking

### 🌍 Ecosystem Analysis
- Platform-specific statistics and insights
- Alternative package recommendations
- Dependency impact analysis
- Package ecosystem health scoring

### 🛠️ Project Management
- Comprehensive dependency auditing
- Update monitoring and tracking
- Security-focused dependency reports
- Project health scoring and recommendations

## 📋 Installation

### Prerequisites

- Python 3.8 or higher
- A Libraries.io API key ([Get your API key here](https://libraries.io/api))
- An MCP-compatible client (Claude Desktop, etc.)

### Quick Installation

```bash
# Clone the repository
git clone https://github.com/librariesio/libraries-io-mcp-server.git
cd libraries-io-mcp-server

# Install dependencies
pip install -r requirements.txt

# Or using uv (recommended)
uv sync
```

### Development Installation

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
isort src/

# Lint code
flake8 src/
```

## ⚙️ Configuration

### Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your configuration:
```bash
# Required: Your Libraries.io API key
LIBRARIES_IO_API_KEY=your_api_key_here

# Optional: Base URL for the Libraries.io API (default: https://libraries.io/api)
LIBRARIES_IO_BASE_URL=https://libraries.io/api

# Optional: Rate limiting configuration
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60

# Optional: Logging level
LOG_LEVEL=INFO
```

### API Key Setup

1. Visit [Libraries.io API](https://libraries.io/api)
2. Sign up for an account if you don't have one
3. Generate an API key
4. Add it to your environment variables or `.env` file

## 🚀 Usage

### With Claude Desktop

1. Configure Claude Desktop with the provided configuration files:
   - [`claude-desktop-config.json`](claude-desktop-config.json) for basic setup
   - [`claude-desktop-config-advanced.json`](claude-desktop-config-advanced.json) for advanced configuration

2. Add to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "libraries-io": {
      "command": "uv",
      "args": [
        "run",
        "fastmcp",
        "run",
        "src/libraries_io_mcp/server.py"
      ],
      "env": {
        "LIBRARIES_IO_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### With Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run directly with Docker
docker run -d \
  --name libraries-io-mcp-server \
  -p 8000:8000 \
  -e LIBRARIES_IO_API_KEY=your_api_key_here \
  libraries-io-mcp-server
```

### Direct Server Usage

```bash
# Start the server
python -m src.libraries_io_mcp.server

# Or using uv
uv run fastmcp run src/libraries_io_mcp/server.py
```

## 🛠️ Available Tools

### Package Discovery
- [`search_packages`](docs/api.md#search_packages) - Search packages by keyword, language, or license
- [`get_trending_packages`](docs/api.md#get_trending_packages) - Get trending packages by platform
- [`get_popular_packages`](docs/api.md#get_popular_packages) - Get most popular packages

### Package Analysis
- [`get_package_info`](docs/api.md#get_package_info) - Get detailed package information
- [`get_package_versions`](docs/api.md#get_package_versions) - List all versions of a package
- [`get_package_dependencies`](docs/api.md#get_package_dependencies) - Get package dependencies
- [`get_package_dependents`](docs/api.md#get_package_dependents) - Get packages that depend on this one
- [`compare_packages`](docs/api.md#compare_packages) - Compare multiple packages
- [`check_package_security`](docs/api.md#check_package_security) - Check for security issues

### Ecosystem Analysis
- [`analyze_dependency_tree`](docs/api.md#analyze_dependency_tree) - Deep dependency analysis
- [`find_alternatives`](docs/api.md#find_alternatives) - Find alternative packages
- [`get_platform_stats`](docs/api.md#get_platform_stats) - Get statistics for a package manager
- [`check_license_compatibility`](docs/api.md#check_license_compatibility) - Check license compatibility

### Project Management
- [`track_package_updates`](docs/api.md#track_package_updates) - Monitor package for updates
- [`generate_dependency_report`](docs/api.md#generate_dependency_report) - Generate comprehensive dependency report
- [`audit_project_dependencies`](docs/api.md#audit_project_dependencies) - Audit all dependencies in a project

## 📚 Documentation

### Core Documentation
- [API Reference](docs/api.md) - Complete API documentation for all tools and resources
- [Deployment Guide](docs/deployment.md) - Multiple deployment options and configurations
- [Development Guide](CONTRIBUTING.md) - Contributing guidelines and development setup

### Integration Guides
- [Claude Desktop Integration](CLAUDE_DESKTOP.md) - Step-by-step Claude Desktop setup
- [Docker Deployment](DOCKER.md) - Container deployment and scaling
- [Examples](examples/) - Usage examples and sample workflows

### Additional Resources
- [Architecture Overview](docs/architecture.md) - System architecture and design patterns
- [Testing Guide](docs/testing.md) - Testing procedures and best practices
- [Security Guidelines](SECURITY.md) - Security best practices and reporting
- [Changelog](CHANGELOG.md) - Version history and updates

## 🔧 Development

### Project Structure
```
libraries-io-mcp-server/
├── src/
│   └── libraries_io_mcp/
│       ├── __init__.py
│       ├── server.py           # Main FastMCP server
│       ├── client.py           # Libraries.io API client
│       ├── models.py           # Pydantic data models
│       ├── tools.py            # MCP tools implementation
│       ├── resources.py        # MCP resources implementation
│       ├── prompts.py          # MCP prompts implementation
│       └── utils.py            # Utility functions
├── tests/
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── fixtures/               # Test fixtures
├── docs/                       # Documentation
├── examples/                   # Usage examples
├── .env.example               # Environment template
├── pyproject.toml             # Project configuration
└── requirements.txt           # Dependencies
```

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/librariesio/libraries-io-mcp-server.git
cd libraries-io-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Set up environment variables
cp .env.example .env
# Edit .env with your API key

# Run tests
pytest

# Run with coverage
pytest --cov=src/libraries_io_mcp

# Format code
black src/
isort src/

# Lint code
flake8 src/
mypy src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/libraries_io_mcp --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run tests in parallel
pytest -n auto
```

## 🏗️ Architecture

The Libraries.io MCP Server is built with a modular architecture:

- **FastMCP Server**: Core MCP protocol implementation
- **Libraries.io Client**: HTTP client with caching and rate limiting
- **Tools**: MCP tools for package discovery and analysis
- **Resources**: MCP resources for contextual data access
- **Prompts**: AI interaction templates and workflows
- **Models**: Pydantic data models for validation and serialization

## 📊 Performance & Scaling

### Built-in Optimizations
- **Intelligent Caching**: Reduces API calls and improves response times
- **Rate Limiting**: Respects Libraries.io API limits and prevents abuse
- **Async Operations**: Concurrent request processing for better performance
- **Request Deduplication**: Eliminates duplicate API calls

### Scaling Strategies
- **Horizontal Scaling**: Multiple server instances behind a load balancer
- **Caching Layer**: Redis integration for distributed caching
- **Load Balancing**: Nginx or cloud load balancers
- **Container Orchestration**: Kubernetes for automated scaling

## 🔒 Security

### Security Features
- **API Key Management**: Secure storage and rotation
- **Input Validation**: Comprehensive parameter validation
- **Rate Limiting**: Prevents abuse and ensures fair usage
- **Error Handling**: Graceful degradation and secure error messages

### Security Best Practices
- Never commit API keys to version control
- Use environment variables for sensitive information
- Implement proper access controls
- Regular security audits and updates

See [Security Guidelines](SECURITY.md) for detailed security information.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for:

- Development setup and workflow
- Code style and quality standards
- Testing procedures
- Pull request process
- Issue reporting

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Format your code: `black src/ && isort src/`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📈 Monitoring & Observability

### Logging
- Structured logging with correlation IDs
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- Request/response logging for debugging

### Metrics
- API usage statistics
- Response time monitoring
- Cache hit rates
- Error rate tracking

### Health Checks
- API connectivity monitoring
- Cache health checks
- Memory usage tracking
- Service availability monitoring

## 🐛 Troubleshooting

### Common Issues

1. **API Key Issues**
   - Verify your API key is valid and has sufficient permissions
   - Check that the environment variable is set correctly
   - Ensure you haven't exceeded rate limits

2. **Connection Problems**
   - Check network connectivity to Libraries.io API
   - Verify firewall settings
   - Check proxy configurations if applicable

3. **Performance Issues**
   - Monitor API usage and rate limits
   - Check cache hit rates
   - Review server logs for errors

### Getting Help

- Check the [troubleshooting section](docs/troubleshooting.md)
- Review [GitHub Issues](https://github.com/librariesio/libraries-io-mcp-server/issues)
- Create a new issue with detailed information

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Libraries.io](https://libraries.io) for providing the comprehensive open source package database
- [FastMCP](https://github.com/pydantic/fastmcp) for the excellent MCP framework
- [Pydantic](https://pydantic.dev) for data validation and serialization
- [httpx](https://github.com/encode/httpx) for async HTTP client functionality

## 📞 Support

For support and questions:

- 🐛 Issues: [GitHub Issues](https://github.com/librariesio/libraries-io-mcp-server/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/librariesio/libraries-io-mcp-server/discussions)
- 📖 Documentation: [Full Documentation](https://librariesio.github.io/libraries-io-mcp-server/)

---

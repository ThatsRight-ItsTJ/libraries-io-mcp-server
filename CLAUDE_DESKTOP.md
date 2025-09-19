# Claude Desktop Integration - Libraries.io MCP Server

This guide provides step-by-step instructions for integrating the Libraries.io MCP Server with Claude Desktop, enabling seamless access to open source package information and analysis tools.

## Prerequisites

Before you begin, ensure you have the following:

1. **Claude Desktop** installed on your system
2. **Python 3.8+** installed
3. **uv** package manager installed (recommended)
4. **Libraries.io API key** - [Get your API key here](https://libraries.io/api)

## Quick Setup

### 1. Install uv (if not already installed)

```bash
# Using curl (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Using PowerShell (Windows)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Add uv to your PATH (if not done automatically)
# For macOS/Linux:
export PATH="$HOME/.cargo/bin:$PATH"
# For Windows:
# Add %USERPROFILE%\.cargo\bin to your PATH
```

### 2. Clone and Setup the Project

```bash
# Clone the repository
git clone https://github.com/librariesio/libraries-io-mcp-server.git
cd libraries-io-mcp-server

# Install dependencies
uv sync
```

### 3. Get Your Libraries.io API Key

1. Visit [Libraries.io API](https://libraries.io/api)
2. Sign up for an account if you don't have one
3. Generate an API key
4. Set it as an environment variable:

```bash
# For macOS/Linux
export LIBRARIES_IO_API_KEY="your_api_key_here"

# For Windows (Command Prompt)
set LIBRARIES_IO_API_KEY="your_api_key_here"

# For Windows (PowerShell)
$env:LIBRARIES_IO_API_KEY="your_api_key_here"
```

### 4. Configure Claude Desktop

#### Method 1: Using the Configuration File

1. **Find your Claude Desktop configuration directory:**
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`

2. **Create a backup** of your existing configuration file

3. **Copy the configuration** from [`claude-desktop-config.json`](claude-desktop-config.json) in this repository

4. **Update the configuration** with your API key:

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
        "LIBRARIES_IO_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

#### Method 2: Manual Configuration

1. Open your Claude Desktop configuration file in a text editor
2. Add the following configuration:

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
        "LIBRARIES_IO_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

### 5. Restart Claude Desktop

1. Completely quit Claude Desktop
2. Restart the application
3. The Libraries.io MCP Server should now be connected

## Advanced Configuration

### Development Environment

For development purposes, you can use a different configuration:

```json
{
  "mcpServers": {
    "libraries-io-dev": {
      "command": "uv",
      "args": [
        "run",
        "fastmcp",
        "dev",
        "src/libraries_io_mcp/server.py"
      ],
      "env": {
        "LIBRARIES_IO_API_KEY": "your_api_key_here",
        "LIBRARIES_IO_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Production Deployment

For production deployment, consider using absolute paths:

```json
{
  "mcpServers": {
    "libraries-io": {
      "command": "/usr/local/bin/uv",
      "args": [
        "run",
        "fastmcp",
        "run",
        "/path/to/libraries-io-mcp-server/src/libraries_io_mcp/server.py"
      ],
      "env": {
        "LIBRARIES_IO_API_KEY": "${env:LIBRARIES_IO_API_KEY}"
      }
    }
  }
}
```

### Multiple API Keys (Advanced)

If you need to use different API keys for different environments:

```json
{
  "mcpServers": {
    "libraries-io-prod": {
      "command": "uv",
      "args": [
        "run",
        "fastmcp",
        "run",
        "src/libraries_io_mcp/server.py"
      ],
      "env": {
        "LIBRARIES_IO_API_KEY": "${env:LIBRARIES_IO_API_KEY_PROD}",
        "LIBRARIES_IO_BASE_URL": "https://libraries.io/api"
      }
    },
    "libraries-io-staging": {
      "command": "uv",
      "args": [
        "run",
        "fastmcp",
        "run",
        "src/libraries_io_mcp/server.py"
      ],
      "env": {
        "LIBRARIES_IO_API_KEY": "${env:LIBRARIES_IO_API_KEY_STAGING}",
        "LIBRARIES_IO_BASE_URL": "https://staging.libraries.io/api"
      }
    }
  }
}
```

## Environment Variables

### Required Variables

- `LIBRARIES_IO_API_KEY`: Your Libraries.io API key

### Optional Variables

- `LIBRARIES_IO_BASE_URL`: Base URL for the Libraries.io API (default: `https://libraries.io/api`)
- `LIBRARIES_IO_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `RATE_LIMIT_REQUESTS`: Maximum requests per minute (default: 60)
- `RATE_LIMIT_WINDOW`: Rate limit window in seconds (default: 60)

## Troubleshooting

### Common Issues

#### 1. "uv command not found"

**Solution**: Ensure uv is installed and in your PATH
```bash
# Check if uv is installed
uv --version

# If not installed, follow the installation steps above
```

#### 2. "API key not found"

**Solution**: Verify your API key is set correctly
```bash
# Check if the environment variable is set
echo $LIBRARIES_IO_API_KEY

# If not set, set it again
export LIBRARIES_IO_API_KEY="your_api_key_here"
```

#### 3. "Module not found" errors

**Solution**: Ensure all dependencies are installed
```bash
# Reinstall dependencies
uv sync
```

#### 4. "Connection refused" or "Server not responding"

**Solution**: 
1. Check if the server is running on the correct port
2. Verify the server path is correct
3. Check firewall settings

### Debug Mode

Enable debug logging to troubleshoot issues:

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
        "LIBRARIES_IO_API_KEY": "your_api_key_here",
        "LIBRARIES_IO_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Testing the Connection

You can test if the MCP server is working by:

1. **Using MCP Inspector**:
```bash
uv run fastmcp inspect src/libraries_io_mcp/server.py
```

2. **Checking Claude Desktop logs**:
   - Look for "Libraries.io MCP Server" in the application logs
   - Check for any error messages during startup

### Configuration Validation

Validate your JSON configuration using an online JSON validator or:

```bash
# Using Python to validate JSON
python -m json.tool claude-desktop-config.json
```

## Available Tools

Once connected, Claude Desktop will have access to the following Libraries.io tools:

### Package Discovery
- `search_packages` - Search packages by keyword, language, or license
- `get_trending_packages` - Get trending packages by platform
- `get_popular_packages` - Get most popular packages

### Package Analysis
- `get_package_info` - Get detailed package information
- `get_package_versions` - List all versions of a package
- `get_package_dependencies` - Get package dependencies
- `get_package_dependents` - Get packages that depend on this one
- `compare_packages` - Compare multiple packages

### Ecosystem Analysis
- `analyze_dependency_tree` - Deep dependency analysis
- `find_alternatives` - Find alternative packages
- `get_platform_stats` - Get statistics for a package manager
- `check_license_compatibility` - Check license compatibility

### Project Management
- `track_package_updates` - Monitor package for updates
- `generate_dependency_report` - Generate comprehensive dependency report
- `audit_project_dependencies` - Audit all dependencies in a project

## Best Practices

### Security
- Never commit your API key to version control
- Use environment variables for sensitive information
- Consider using different API keys for development and production

### Performance
- The server includes built-in caching to reduce API calls
- Rate limiting is automatically handled (60 requests/minute)
- Use specific search queries to get better results

### Maintenance
- Regularly update the uv package and dependencies
- Monitor your Libraries.io API usage
- Keep an eye on server logs for any issues

## Support

If you encounter any issues:

1. Check the [troubleshooting section](#troubleshooting) above
2. Review the [GitHub Issues](https://github.com/librariesio/libraries-io-mcp-server/issues)
3. Create a new issue with:
   - Your operating system
   - Claude Desktop version
   - Error messages
   - Steps to reproduce the issue

## Contributing

We welcome contributions to improve the Claude Desktop integration! Please see our [contributing guidelines](CONTRIBUTING.md) for more information.
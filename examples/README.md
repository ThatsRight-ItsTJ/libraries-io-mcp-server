# Examples Directory

This directory contains various examples demonstrating how to use the Libraries.io MCP Server.

## Available Examples

### 1. `basic_usage.py`
Demonstrates basic usage patterns for the Libraries.io MCP Server.

**Features:**
- Package searching
- Getting package information
- Retrieving package versions
- Fetching package dependencies
- Getting trending and popular packages

**Usage:**
```bash
cd examples
python basic_usage.py
```

### 2. `advanced_usage.py`
Shows advanced usage patterns including package comparison, dependency analysis, security checking, and more.

**Features:**
- Package comparison and analysis
- Dependency tree analysis
- Security checking
- License compatibility checking
- Finding package alternatives
- Platform statistics
- Project dependency auditing

**Usage:**
```bash
cd examples
python advanced_usage.py
```

### 3. `server_example.py`
Demonstrates how to run the MCP Server as a standalone service.

**Features:**
- Server startup and configuration
- Lists available tools, resources, and prompts
- Basic server management

**Usage:**
```bash
cd examples
python server_example.py
```

## Prerequisites

Before running any examples, make sure you have:

1. **Python 3.8+** installed
2. **Libraries.io API Key** - Get one from [Libraries.io](https://libraries.io/api)
3. **Required dependencies** installed:
   ```bash
   pip install -r ../requirements.txt
   ```

## Environment Setup

### 1. Set your API key

```bash
# Option 1: Environment variable
export LIBRARIES_IO_API_KEY="your_api_key_here"

# Option 2: Create a .env file
cp ../.env.example .env
# Edit .env with your API key
```

### 2. Install dependencies

```bash
# Install project dependencies
pip install -e "..[dev]"

# Or install from requirements
pip install -r ../requirements.txt
```

## Running Examples

### Basic Usage Example

```bash
cd examples
python basic_usage.py
```

This will demonstrate:
- Searching for packages
- Getting detailed package information
- Retrieving package versions
- Fetching dependencies
- Getting trending packages

### Advanced Usage Example

```bash
cd examples
python advanced_usage.py
```

This will demonstrate:
- Comparing multiple packages
- Analyzing dependency trees
- Checking for security issues
- Verifying license compatibility
- Finding alternative packages
- Getting platform statistics
- Auditing project dependencies

### Server Example

```bash
cd examples
python server_example.py
```

This will:
- Start the MCP Server
- Show available tools, resources, and prompts
- Display server configuration
- Run the server on `http://localhost:8000`

## Example Output

### Basic Usage Output

```
=== Basic Usage Examples ===

1. Searching for packages...
Found 5 packages:
  - react (npm) - A JavaScript library for building user interfaces
  - vue (npm) - The Progressive JavaScript Framework
  - angular (npm) - One framework. Mobile & desktop.
  - svelte (npm) - Cybernetically enhanced web apps
  - preact (npm) - Fast 3kB React alternative with the same modern API

2. Getting package information...
Package: react
Platform: npm
Description: A JavaScript library for building user interfaces
Stars: 200000
Latest Version: 18.2.0
Language: JavaScript
Homepage: https://reactjs.org

3. Getting package versions...
Found 150 versions:
  - 18.2.0 (published: 2023-01-01)
  - 18.1.0 (published: 2022-12-01)
  - 18.0.0 (published: 2022-11-01)
  - 17.0.2 (published: 2022-10-01)
  - 17.0.1 (published: 2022-09-01)
```

### Advanced Usage Output

```
=== Advanced Usage Examples ===

1. Comparing packages...
Comparison of 3 packages:
  - react (npm):
    Stars: 200000
    Language: JavaScript
    Description: A JavaScript library for building user interfaces...
  - vue (npm):
    Stars: 180000
    Language: JavaScript
    Description: The Progressive JavaScript Framework...
  - angular (npm):
    Stars: 90000
    Language: TypeScript
    Description: One framework. Mobile & desktop...

2. Analyzing dependency tree...
Dependency tree for react (depth 2):
Total dependencies: 45
Runtime dependencies: 12
Development dependencies: 33

Top dependencies:
  - object-assign (npm) - runtime
  - loose-envify (npm) - runtime
  - scheduler (npm) - runtime
  - react-dom (npm) - runtime
  - react-is (npm) - runtime

3. Checking package security...
Security analysis for react:
Security issues: 0
No security issues found

4. Checking license compatibility...
License compatibility check for commercial use:
Overall compatible: True

License analysis:
  - MIT: True (commercial)
  - Apache-2.0: True (commercial)

Recommendations:
  - Review commercial use restrictions for each license
```

## Common Issues and Solutions

### 1. API Key Not Found

**Error:** `Please set LIBRARIES_IO_API_KEY environment variable`

**Solution:**
```bash
export LIBRARIES_IO_API_KEY="your_api_key_here"
```

### 2. Rate Limiting

**Error:** `Rate limit exceeded`

**Solution:**
- Wait for the rate limit window to reset
- Use a different API key
- Reduce the number of requests in your example

### 3. Network Issues

**Error:** `Connection error` or `Timeout`

**Solution:**
- Check your internet connection
- Verify the Libraries.io API is accessible
- Increase timeout settings if needed

### 4. Package Not Found

**Error:** `Package not found`

**Solution:**
- Verify the package name and platform are correct
- Check if the package exists on Libraries.io
- Try searching for similar packages

## Customization

### Modifying Examples

You can modify the examples to:

1. **Change search parameters:**
   ```python
   search_result = await search_packages(
       query="your_query",
       platforms=["npm", "pypi"],
       per_page=10
   )
   ```

2. **Add more packages to comparison:**
   ```python
   compare_result = await compare_packages(
       packages=[
           {"platform": "npm", "name": "package1"},
           {"platform": "npm", "name": "package2"},
           {"platform": "pypi", "name": "package3"}
       ]
   )
   ```

3. **Customize analysis depth:**
   ```python
   tree_result = await analyze_dependency_tree(
       platform="npm",
       name="package_name",
       max_depth=3
   )
   ```

### Creating Your Own Examples

You can create new example files by:

1. Importing the required modules:
   ```python
   from libraries_io_mcp.client import LibrariesIOClient
   from libraries_io_mcp.tools import search_packages, get_package_info
   ```

2. Creating a client instance:
   ```python
   client = LibrariesIOClient(api_key="your_api_key")
   ```

3. Using the tools:
   ```python
   result = await search_packages(query="your_query")
   ```

## Best Practices

1. **Always handle errors:**
   ```python
   try:
       result = await search_packages(query="react")
       if result.success:
           # Process result
       else:
           print(f"Error: {result.error}")
   except Exception as e:
       print(f"Unexpected error: {e}")
   ```

2. **Use appropriate timeouts:**
   ```python
   client = LibrariesIOClient(
       api_key="your_api_key",
       timeout=30.0  # 30 second timeout
   )
   ```

3. **Respect rate limits:**
   ```python
   # Check rate limit info
   rate_limit = client.get_rate_limit_info()
   print(f"Requests remaining: {rate_limit.remaining}")
   ```

4. **Clean up resources:**
   ```python
   # Close client when done
   await client.close()
   ```

## Contributing

If you have additional examples or improvements:

1. Fork the repository
2. Create a new example file
3. Add it to this README
4. Submit a pull request

## Support

For questions about the examples:
- Check the [main documentation](../README.md)
- Review the [API documentation](../docs/api.md)
- Create an issue on [GitHub](https://github.com/librariesio/libraries-io-mcp-server/issues)
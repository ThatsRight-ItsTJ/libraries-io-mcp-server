# Docker Deployment

This document provides instructions for deploying the Libraries.io MCP Server using Docker.

## Quick Start

### Prerequisites
- Docker (version 20.10 or later)
- Docker Compose (version 1.29 or later)
- A Libraries.io API key

### Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Libraries.io API key:
```bash
LIBRARIES_IO_API_KEY=your_api_key_here
LOG_LEVEL=INFO
```

### Build and Run

#### Option 1: Using Docker Compose (Recommended)

```bash
# Build and start the service
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop the service
docker-compose down
```

#### Option 2: Using Docker directly

```bash
# Build the image
docker build -t libraries-io-mcp-server .

# Run the container
docker run -d \
  --name libraries-io-mcp-server \
  -p 8000:8000 \
  -e LIBRARIES_IO_API_KEY=your_api_key_here \
  -e LOG_LEVEL=INFO \
  libraries-io-mcp-server
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LIBRARIES_IO_API_KEY` | Your Libraries.io API key | - | Yes |
| `HOST` | Server host address | `0.0.0.0` | No |
| `PORT` | Server port | `8000` | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` | No |

### Production Deployment

For production deployment, use the `production` profile which includes nginx reverse proxy:

```bash
# Start with nginx reverse proxy
docker-compose --profile production up -d --build
```

## Health Checks

The container includes a health check that monitors the server status. You can check the health status:

```bash
# Check container health
docker ps

# View health logs
docker logs libraries-io-mcp-server
```

## Logs

### View Logs

```bash
# View real-time logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f libraries-io-mcp-server

# View last 100 lines
docker-compose logs --tail=100 libraries-io-mcp-server
```

### Log Management

Logs are written to stdout/stderr and can be collected by:
- Docker logging drivers
- External logging services (Fluentd, Logstash, etc.)
- Volume mounting for persistent storage

## Development

### Development Mode

For development, you can mount the source code to reflect changes immediately:

```bash
# Development with hot-reload
docker-compose up --build

# Or using docker run:
docker run -d \
  --name libraries-io-mcp-server-dev \
  -p 8000:8000 \
  -v $(pwd)/src:/app/src \
  -e LIBRARIES_IO_API_KEY=your_api_key_here \
  libraries-io-mcp-server
```

### Building for Different Architectures

To build images for different architectures (ARM64, AMD64):

```bash
# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 -t libraries-io-mcp-server:latest .

# Push to registry
docker buildx build --platform linux/amd64,linux/arm64 -t your-registry/libraries-io-mcp-server:latest --push .
```

## Security Best Practices

1. **Use non-root user**: The container runs as a non-root user (`appuser`) by default
2. **Environment variables**: Store sensitive data in environment variables, not in the image
3. **Image scanning**: Scan images for vulnerabilities using tools like Trivy or Clair
4. **Regular updates**: Keep base images updated to patch security vulnerabilities
5. **Resource limits**: Set appropriate resource limits in production

```yaml
# Example docker-compose with resource limits
services:
  libraries-io-mcp-server:
    # ... other configuration
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   
   # Use a different port
   docker-compose up -d --build -e PORT=8001
   ```

2. **Permission denied**
   ```bash
   # Ensure your user has docker permissions
   sudo usermod -aG docker $USER
   ```

3. **Health check failures**
   ```bash
   # Check detailed health status
   docker inspect libraries-io-mcp-server --format='{{.State.Health}}'
   
   # View server logs
   docker logs libraries-io-mcp-server
   ```

### Debug Mode

Run the container in interactive mode for debugging:

```bash
docker run -it --rm \
  --name libraries-io-mcp-server-debug \
  -p 8000:8000 \
  -e LIBRARIES_IO_API_KEY=your_api_key_here \
  -e LOG_LEVEL=DEBUG \
  libraries-io-mcp-server sh
```

## Monitoring and Observability

### Health Endpoint

The server exposes a health check endpoint at:
```
http://localhost:8000/health
```

### Metrics

The server can be configured to expose metrics for monitoring:
```bash
# Enable metrics collection
docker run -e METRICS_ENABLED=true libraries-io-mcp-server
```

## Backup and Recovery

### Data Persistence

For data persistence, mount volumes:
```yaml
services:
  libraries-io-mcp-server:
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
```

### Backup Strategy

1. Regular backups of configuration files
2. Database backups (if using persistent storage)
3. Image versioning for rollbacks

## Scaling

### Horizontal Scaling

For horizontal scaling, use multiple instances behind a load balancer:

```yaml
version: '3.8'
services:
  libraries-io-mcp-server:
    deploy:
      replicas: 3
  load-balancer:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - libraries-io-mcp-server
```

## Support

For issues related to Docker deployment:
1. Check container logs: `docker logs libraries-io-mcp-server`
2. Verify environment variables are set correctly
3. Ensure the Libraries.io API key is valid
4. Check network connectivity to the Libraries.io API

For more information about the Libraries.io MCP Server, see the main [README.md](README.md).
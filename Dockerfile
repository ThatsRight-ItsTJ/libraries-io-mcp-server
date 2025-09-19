# Multi-stage build for optimized image size and security
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Copy dependency files
COPY pyproject.toml .
COPY requirements.txt .

# Install production dependencies only
RUN uv pip install --system --no-dev -e .

# Production stage
FROM python:3.11-slim as production

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY src/ ./src/
COPY pyproject.toml .
COPY requirements.txt .

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables for production
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV LIBRARIES_IO_API_KEY=""
ENV HOST=0.0.0.0
ENV PORT=8000
ENV LOG_LEVEL=INFO

# Expose port for the MCP server
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set entrypoint
ENTRYPOINT ["python", "-m", "libraries_io_mcp.server"]

# Default command
CMD ["--host", "0.0.0.0", "--port", "8000", "--log-level", "INFO"]

# Monitoring and Logging Setup

This document provides comprehensive guidelines for setting up monitoring, logging, and observability for the Libraries.io MCP Server. Proper monitoring ensures system reliability, performance, and quick issue detection.

## Overview

The Libraries.io MCP Server implements a multi-layered monitoring strategy that includes:

- **Application Logging**: Structured logging with multiple levels
- **Performance Monitoring**: Request/response times, error rates, and system metrics
- **Health Checks**: Service availability and dependency status
- **Alerting**: Real-time notifications for critical issues
- **Distributed Tracing**: Request flow tracking across services
- **Metrics Collection**: System and application metrics

## Logging Configuration

### 1. Logging Setup

#### Basic Logging Configuration

```python
# src/libraries_io_mcp/logging_config.py
"""Logging configuration for the Libraries.io MCP Server."""

import logging
import logging.handlers
import sys
import os
from typing import Optional, Dict, Any
from datetime import datetime
import json


class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
        
        # Add request context if present
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        
        # Add user context if present
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        
        return json.dumps(log_entry, default=str)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "json",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_file: bool = True,
    enable_syslog: bool = False
) -> None:
    """
    Setup logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        log_format: Log format (json, text)
        max_bytes: Maximum log file size in bytes
        backup_count: Number of backup log files to keep
        enable_console: Enable console logging
        enable_file: Enable file logging
        enable_syslog: Enable syslog logging
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    if log_format == "json":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if enable_file and log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Syslog handler
    if enable_syslog:
        try:
            syslog_handler = logging.handlers.SysLogHandler()
            syslog_handler.setLevel(logging.WARNING)
            syslog_handler.setFormatter(formatter)
            root_logger.addHandler(syslog_handler)
        except Exception as e:
            logging.warning(f"Failed to setup syslog handler: {e}")
    
    # Set up specific loggers
    setup_loggers()


def setup_loggers() -> None:
    """Setup specific loggers for the application."""
    
    # Libraries.io MCP logger
    mcp_logger = logging.getLogger("libraries_io_mcp")
    mcp_logger.setLevel(logging.DEBUG)
    
    # HTTP client logger
    http_logger = logging.getLogger("httpx")
    http_logger.setLevel(logging.WARNING)
    
    # FastMCP logger
    fastmcp_logger = logging.getLogger("fastmcp")
    fastmcp_logger.setLevel(logging.INFO)
    
    # uvicorn logger (if using)
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


# Context manager for request logging
class RequestLogger:
    """Context manager for request logging."""
    
    def __init__(self, logger: logging.Logger, request_id: str):
        self.logger = logger
        self.request_id = request_id
        self.start_time = datetime.now()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(
                "Request completed",
                extra={
                    "request_id": self.request_id,
                    "duration": duration,
                    "status": "success"
                }
            )
        else:
            self.logger.error(
                "Request failed",
                extra={
                    "request_id": self.request_id,
                    "duration": duration,
                    "status": "error",
                    "exception": str(exc_val)
                },
                exc_info=True
            )
```

#### Logging Configuration File

```python
# src/libraries_io_mcp/config/logging_config.py
"""Logging configuration management."""

import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    
    # Basic settings
    level: str = Field("INFO", env="LOG_LEVEL")
    format: str = Field("json", env="LOG_FORMAT")
    
    # File settings
    file_path: Optional[str] = Field(None, env="LOG_FILE")
    max_bytes: int = Field(10 * 1024 * 1024, env="LOG_MAX_BYTES")  # 10MB
    backup_count: int = Field(5, env="LOG_BACKUP_COUNT")
    
    # Handler settings
    enable_console: bool = Field(True, env="LOG_ENABLE_CONSOLE")
    enable_file: bool = Field(True, env="LOG_ENABLE_FILE")
    enable_syslog: bool = Field(False, env="LOG_ENABLE_SYSLOG")
    
    # Structured logging settings
    enable_structured: bool = Field(True, env="LOG_ENABLE_STRUCTURED")
    include_request_id: bool = Field(True, env="LOG_INCLUDE_REQUEST_ID")
    include_user_id: bool = Field(False, env="LOG_INCLUDE_USER_ID")
    
    # Application-specific settings
    enable_http_logging: bool = Field(True, env="LOG_ENABLE_HTTP")
    enable_mcp_logging: bool = Field(True, env="LOG_ENABLE_MCP")
    enable_performance_logging: bool = Field(True, env="LOG_ENABLE_PERFORMANCE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_logging_config() -> LoggingConfig:
    """Get logging configuration."""
    return LoggingConfig()


def setup_logging_from_config(config: LoggingConfig) -> None:
    """Setup logging from configuration."""
    from .logging_config import setup_logging
    
    setup_logging(
        level=config.level,
        log_file=config.file_path,
        log_format=config.format,
        max_bytes=config.max_bytes,
        backup_count=config.backup_count,
        enable_console=config.enable_console,
        enable_file=config.enable_file,
        enable_syslog=config.enable_syslog
    )
```

### 2. Logging Usage

#### Application Logging

```python
# src/libraries_io_mcp/client.py
"""Libraries.io API client with logging."""

import logging
import time
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
import httpx

from .models import PackageInfo, SearchResults
from .logging_config import RequestLogger, get_logger

logger = get_logger(__name__)


class LibrariesIOClient:
    """Client for interacting with the Libraries.io API."""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize the client."""
        self.api_key = api_key
        self.base_url = kwargs.get("base_url", "https://libraries.io/api/v1")
        self.timeout = kwargs.get("timeout", 30.0)
        self.max_retries = kwargs.get("max_retries", 3)
        
        # Setup HTTP client
        self.http_client = httpx.AsyncClient(
            timeout=self.timeout,
            base_url=self.base_url,
            headers={
                "User-Agent": "LibrariesIO-MCP-Server/1.0",
                "Authorization": f"Bearer {api_key}"
            }
        )
        
        logger.info(
            "Initialized LibrariesIOClient",
            extra={
                "base_url": self.base_url,
                "timeout": self.timeout,
                "max_retries": self.max_retries
            }
        )
    
    @asynccontextmanager
    async def _log_request(self, operation: str, **kwargs):
        """Context manager for logging requests."""
        request_id = kwargs.get("request_id", "unknown")
        start_time = time.time()
        
        logger.info(
            f"Starting {operation}",
            extra={
                "request_id": request_id,
                "operation": operation,
                "params": {k: v for k, v in kwargs.items() if k != "request_id"}
            }
        )
        
        try:
            yield
            duration = time.time() - start_time
            
            logger.info(
                f"Completed {operation}",
                extra={
                    "request_id": request_id,
                    "operation": operation,
                    "duration": duration,
                    "status": "success"
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(
                f"Failed {operation}",
                extra={
                    "request_id": request_id,
                    "operation": operation,
                    "duration": duration,
                    "status": "error",
                    "exception": str(e)
                },
                exc_info=True
            )
            raise
    
    async def get_package_info(self, platform: str, name: str, **kwargs) -> PackageInfo:
        """Get package information."""
        request_id = kwargs.get("request_id", "unknown")
        
        async with self._log_request("get_package_info", platform=platform, name=name, **kwargs):
            try:
                response = await self.http_client.get(
                    f"/packages/{platform}/{name}",
                    params={"include_versions": kwargs.get("include_versions", False)}
                )
                response.raise_for_status()
                
                data = response.json()
                logger.debug(
                    "Package info retrieved",
                    extra={
                        "request_id": request_id,
                        "platform": platform,
                        "name": name,
                        "package_name": data.get("name"),
                        "stars": data.get("stars")
                    }
                )
                
                return PackageInfo(**data)
                
            except httpx.HTTPStatusError as e:
                logger.warning(
                    f"HTTP error getting package info: {e.response.status_code}",
                    extra={
                        "request_id": request_id,
                        "platform": platform,
                        "name": name,
                        "status_code": e.response.status_code
                    }
                )
                raise
                
            except httpx.RequestError as e:
                logger.error(
                    f"Network error getting package info: {e}",
                    extra={
                        "request_id": request_id,
                        "platform": platform,
                        "name": name,
                        "error": str(e)
                    }
                )
                raise
    
    async def search_packages(self, query: str, **kwargs) -> SearchResults:
        """Search for packages."""
        request_id = kwargs.get("request_id", "unknown")
        
        async with self._log_request("search_packages", query=query, **kwargs):
            try:
                params = {"q": query, **kwargs}
                response = await self.http_client.get("/search", params=params)
                response.raise_for_status()
                
                data = response.json()
                logger.debug(
                    "Package search completed",
                    extra={
                        "request_id": request_id,
                        "query": query,
                        "total_results": data.get("total_count", 0),
                        "returned_results": len(data.get("items", []))
                    }
                )
                
                return SearchResults(**data)
                
            except httpx.HTTPStatusError as e:
                logger.warning(
                    f"HTTP error searching packages: {e.response.status_code}",
                    extra={
                        "request_id": request_id,
                        "query": query,
                        "status_code": e.response.status_code
                    }
                )
                raise
                
            except httpx.RequestError as e:
                logger.error(
                    f"Network error searching packages: {e}",
                    extra={
                        "request_id": request_id,
                        "query": query,
                        "error": str(e)
                    }
                )
                raise
    
    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
        logger.info("HTTP client closed")
```

#### MCP Server Logging

```python
# src/libraries_io_mcp/server.py
"""MCP server with logging."""

import logging
import time
from typing import Dict, Any, Optional
from fastmcp import Server
from contextlib import asynccontextmanager

from .client import LibrariesIOClient
from .logging_config import get_logger, RequestLogger

logger = get_logger(__name__)


class MCPServer:
    """MCP server for Libraries.io."""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize the MCP server."""
        self.api_key = api_key
        self.client = LibrariesIOClient(api_key, **kwargs)
        self.server = Server("libraries-io")
        
        # Setup tools
        self._setup_tools()
        
        logger.info("MCP server initialized")
    
    def _setup_tools(self):
        """Setup MCP tools."""
        from .tools import register_tools
        
        register_tools(self.server, self.client)
        logger.info("MCP tools registered")
    
    @asynccontextmanager
    async def _log_request(self, tool_name: str, **kwargs):
        """Context manager for logging MCP requests."""
        request_id = kwargs.get("request_id", "unknown")
        start_time = time.time()
        
        logger.info(
            f"MCP tool called: {tool_name}",
            extra={
                "request_id": request_id,
                "tool": tool_name,
                "parameters": {k: v for k, v in kwargs.items() if k != "request_id"}
            }
        )
        
        try:
            yield
            duration = time.time() - start_time
            
            logger.info(
                f"MCP tool completed: {tool_name}",
                extra={
                    "request_id": request_id,
                    "tool": tool_name,
                    "duration": duration,
                    "status": "success"
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(
                f"MCP tool failed: {tool_name}",
                extra={
                    "request_id": request_id,
                    "tool": tool_name,
                    "duration": duration,
                    "status": "error",
                    "exception": str(e)
                },
                exc_info=True
            )
            raise
    
    async def handle_request(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Handle MCP request."""
        async with self._log_request(tool_name, **kwargs):
            try:
                # Get tool function
                tool_func = getattr(self.server.tools, tool_name, None)
                if not tool_func:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                # Execute tool
                result = await tool_func(**kwargs)
                
                logger.debug(
                    f"Tool result: {tool_name}",
                    extra={
                        "request_id": kwargs.get("request_id", "unknown"),
                        "tool": tool_name,
                        "success": result.get("success", False)
                    }
                )
                
                return result
                
            except Exception as e:
                logger.error(
                    f"Error handling MCP request: {tool_name}",
                    extra={
                        "request_id": kwargs.get("request_id", "unknown"),
                        "tool": tool_name,
                        "error": str(e)
                    },
                    exc_info=True
                )
                raise
    
    async def start(self, host: str = "localhost", port: int = 8000):
        """Start the MCP server."""
        logger.info(f"Starting MCP server on {host}:{port}")
        
        try:
            await self.server.start(host=host, port=port)
            logger.info("MCP server started successfully")
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}", exc_info=True)
            raise
    
    async def stop(self):
        """Stop the MCP server."""
        logger.info("Stopping MCP server")
        
        try:
            await self.server.stop()
            await self.client.close()
            logger.info("MCP server stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping MCP server: {e}", exc_info=True)
            raise
```

### 3. Performance Logging

```python
# src/libraries_io_mcp/performance.py
"""Performance monitoring and logging."""

import time
import functools
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from contextlib import contextmanager

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data class."""
    
    operation: str
    duration: float
    success: bool
    timestamp: datetime
    extra_data: Optional[Dict[str, Any]] = None


class PerformanceMonitor:
    """Performance monitoring class."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = []
        self.logger = get_logger("performance")
    
    def record_metric(self, metric: PerformanceMetrics):
        """Record a performance metric."""
        self.metrics.append(metric)
        
        # Log metric
        self.logger.info(
            f"Performance metric: {metric.operation}",
            extra={
                "operation": metric.operation,
                "duration": metric.duration,
                "success": metric.success,
                "timestamp": metric.timestamp.isoformat(),
                **(metric.extra_data or {})
            }
        )
        
        # Log slow operations
        if metric.duration > 1.0:  # Log operations taking more than 1 second
            self.logger.warning(
                f"Slow operation detected: {metric.operation} took {metric.duration:.2f}s",
                extra={
                    "operation": metric.operation,
                    "duration": metric.duration,
                    "threshold": 1.0
                }
            )
    
    def get_metrics(self, operation: Optional[str] = None) -> list:
        """Get performance metrics."""
        if operation:
            return [m for m in self.metrics if m.operation == operation]
        return self.metrics
    
    def get_average_duration(self, operation: str) -> Optional[float]:
        """Get average duration for an operation."""
        metrics = self.get_metrics(operation)
        if not metrics:
            return None
        
        total_duration = sum(m.duration for m in metrics)
        return total_duration / len(metrics)
    
    def get_success_rate(self, operation: str) -> Optional[float]:
        """Get success rate for an operation."""
        metrics = self.get_metrics(operation)
        if not metrics:
            return None
        
        successful = sum(1 for m in metrics if m.success)
        return successful / len(metrics)


# Global performance monitor
performance_monitor = PerformanceMonitor()


def monitor_performance(operation_name: Optional[str] = None):
    """Decorator for monitoring performance."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            success = False
            
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                raise
            finally:
                duration = time.time() - start_time
                timestamp = datetime.now()
                
                # Record metric
                metric = PerformanceMetrics(
                    operation=op_name,
                    duration=duration,
                    success=success,
                    timestamp=timestamp,
                    extra_data={
                        "function": func.__name__,
                        "module": func.__module__,
                        "args_count": len(args),
                        "kwargs_count": len(kwargs)
                    }
                )
                
                performance_monitor.record_metric(metric)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            success = False
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                raise
            finally:
                duration = time.time() - start_time
                timestamp = datetime.now()
                
                # Record metric
                metric = PerformanceMetrics(
                    operation=op_name,
                    duration=duration,
                    success=success,
                    timestamp=timestamp,
                    extra_data={
                        "function": func.__name__,
                        "module": func.__module__,
                        "args_count": len(args),
                        "kwargs_count": len(kwargs)
                    }
                )
                
                performance_monitor.record_metric(metric)
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


@contextmanager
def performance_context(operation_name: str, **extra_data):
    """Context manager for performance monitoring."""
    start_time = time.time()
    success = False
    
    try:
        yield
        success = True
    except Exception as e:
        raise
    finally:
        duration = time.time() - start_time
        timestamp = datetime.now()
        
        # Record metric
        metric = PerformanceMetrics(
            operation=operation_name,
            duration=duration,
            success=success,
            timestamp=timestamp,
            extra_data=extra_data
        )
        
        performance_monitor.record_metric(metric)
```

## Health Checks

### 1. Health Check Implementation

```python
# src/libraries_io_mcp/health.py
"""Health check implementation."""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

from .client import LibrariesIOClient
from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class HealthStatus:
    """Health status data class."""
    
    service: str
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class HealthChecker:
    """Health checker for monitoring service health."""
    
    def __init__(self, client: LibrariesIOClient):
        """Initialize health checker."""
        self.client = client
        self.logger = get_logger("health")
        self.checks = {}
        self.last_health_check = None
    
    def register_check(self, name: str, check_func: callable, interval: int = 30):
        """Register a health check."""
        self.checks[name] = {
            "func": check_func,
            "interval": interval,
            "last_check": None,
            "last_status": None
        }
        
        self.logger.info(f"Registered health check: {name}")
    
    async def run_check(self, name: str) -> HealthStatus:
        """Run a specific health check."""
        if name not in self.checks:
            raise ValueError(f"Unknown health check: {name}")
        
        check_info = self.checks[name]
        check_func = check_info["func"]
        
        start_time = time.time()
        status = HealthStatus(
            service=name,
            status="healthy",
            timestamp=datetime.now()
        )
        
        try:
            result = await check_func(self.client)
            status.response_time = time.time() - start_time
            status.details = result
            
            # Update check info
            check_info["last_check"] = status.timestamp
            check_info["last_status"] = status
            
            self.logger.debug(f"Health check {name} passed")
            
        except Exception as e:
            status.status = "unhealthy"
            status.error_message = str(e)
            status.response_time = time.time() - start_time
            
            # Update check info
            check_info["last_check"] = status.timestamp
            check_info["last_status"] = status
            
            self.logger.error(f"Health check {name} failed: {e}")
        
        return status
    
    async def run_all_checks(self) -> Dict[str, HealthStatus]:
        """Run all health checks."""
        results = {}
        
        for name in self.checks:
            try:
                results[name] = await self.run_check(name)
            except Exception as e:
                self.logger.error(f"Error running health check {name}: {e}")
                results[name] = HealthStatus(
                    service=name,
                    status="unhealthy",
                    timestamp=datetime.now(),
                    error_message=str(e)
                )
        
        self.last_health_check = datetime.now()
        
        # Log overall health status
        overall_status = self.get_overall_status(results)
        self.logger.info(
            f"Health check completed - Overall status: {overall_status}",
            extra={
                "total_checks": len(results),
                "healthy_checks": len([r for r in results.values() if r.status == "healthy"]),
                "degraded_checks": len([r for r in results.values() if r.status == "degraded"]),
                "unhealthy_checks": len([r for r in results.values() if r.status == "unhealthy"])
            }
        )
        
        return results
    
    def get_overall_status(self, results: Dict[str, HealthStatus]) -> str:
        """Get overall health status."""
        if not results:
            return "unknown"
        
        healthy_count = len([r for r in results.values() if r.status == "healthy"])
        degraded_count = len([r for r in results.values() if r.status == "degraded"])
        unhealthy_count = len([r for r in results.values() if r.status == "unhealthy"])
        
        if unhealthy_count > 0:
            return "unhealthy"
        elif degraded_count > 0:
            return "degraded"
        else:
            return "healthy"
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary."""
        if not self.last_health_check:
            return {"status": "unknown", "message": "No health checks run yet"}
        
        results = {}
        for name, check_info in self.checks.items():
            if check_info["last_status"]:
                results[name] = {
                    "status": check_info["last_status"].status,
                    "last_check": check_info["last_check"].isoformat(),
                    "response_time": check_info["last_status"].response_time,
                    "error_message": check_info["last_status"].error_message
                }
        
        overall_status = self.get_overall_status(results)
        
        return {
            "status": overall_status,
            "last_check": self.last_health_check.isoformat(),
            "checks": results,
            "summary": {
                "total": len(results),
                "healthy": len([r for r in results.values() if r["status"] == "healthy"]),
                "degraded": len([r for r in results.values() if r["status"] == "degraded"]),
                "unhealthy": len([r for r in results.values() if r["status"] == "unhealthy"])
            }
        }


def create_default_health_checker(client: LibrariesIOClient) -> HealthChecker:
    """Create default health checker with standard checks."""
    checker = HealthChecker(client)
    
    # Register standard health checks
    checker.register_check("api_connectivity", check_api_connectivity, interval=30)
    checker.register_check("rate_limit_status", check_rate_limit_status, interval=60)
    checker.register_check("cache_performance", check_cache_performance, interval=120)
    checker.register_check("database_connectivity", check_database_connectivity, interval=60)
    
    return checker


async def check_api_connectivity(client: LibrariesIOClient) -> Dict[str, Any]:
    """Check API connectivity."""
    start_time = time.time()
    
    try:
        # Simple API call to check connectivity
        response = await client.http_client.get("/platforms")
        response.raise_for_status()
        
        duration = time.time() - start_time
        
        return {
            "status": "healthy",
            "response_time": duration,
            "status_code": response.status_code,
            "platforms_count": len(response.json()) if response.content else 0
        }
        
    except Exception as e:
        raise Exception(f"API connectivity check failed: {e}")


async def check_rate_limit_status(client: LibrariesIOClient) -> Dict[str, Any]:
    """Check rate limit status."""
    try:
        # Get rate limit info
        rate_limit_info = client.rate_limiter.get_rate_limit_info()
        
        return {
            "status": "healthy",
            "remaining_requests": rate_limit_info.remaining if rate_limit_info else 0,
            "reset_time": rate_limit_info.reset_time.isoformat() if rate_limit_info else None,
            "limit": rate_limit_info.limit if rate_limit_info else 0
        }
        
    except Exception as e:
        raise Exception(f"Rate limit check failed: {e}")


async def check_cache_performance(client: LibrariesIOClient) -> Dict[str, Any]:
    """Check cache performance."""
    try:
        # Get cache stats
        cache_stats = client.cache.get_stats()
        
        hit_rate = cache_stats.hits / (cache_stats.hits + cache_stats.misses) if (cache_stats.hits + cache_stats.misses) > 0 else 0
        
        return {
            "status": "healthy" if hit_rate > 0.5 else "degraded",
            "hit_rate": hit_rate,
            "hits": cache_stats.hits,
            "misses": cache_stats.misses,
            "size": cache_stats.size
        }
        
    except Exception as e:
        raise Exception(f"Cache performance check failed: {e}")


async def check_database_connectivity(client: LibrariesIOClient) -> Dict[str, Any]:
    """Check database connectivity."""
    try:
        # This would check database connectivity if using a database
        # For now, we'll just return a healthy status
        return {
            "status": "healthy",
            "message": "Database connectivity check not implemented"
        }
        
    except Exception as e:
        raise Exception(f"Database connectivity check failed: {e}")
```

### 2. Health Check Endpoint

```python
# src/libraries_io_mcp/api/health.py
"""Health check API endpoints."""

import asyncio
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from .health import HealthChecker, create_default_health_checker
from .logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "service": "libraries-io-mcp-server"
    }


@router.get("/health/detailed")
async def detailed_health_check(health_checker: HealthChecker) -> Dict[str, Any]:
    """Detailed health check endpoint."""
    try:
        results = await health_checker.run_all_checks()
        summary = health_checker.get_health_summary()
        
        return summary
        
    except Exception as e:
        logger.error(f"Error in detailed health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/{check_name}")
async def specific_health_check(
    check_name: str,
    health_checker: HealthChecker
) -> Dict[str, Any]:
    """Specific health check endpoint."""
    try:
        result = await health_checker.run_check(check_name)
        
        return {
            "check": check_name,
            "status": result.status,
            "timestamp": result.timestamp.isoformat(),
            "response_time": result.response_time,
            "error_message": result.error_message,
            "details": result.details
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in specific health check {check_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/metrics")
async def health_metrics(health_checker: HealthChecker) -> Dict[str, Any]:
    """Health metrics endpoint."""
    try:
        summary = health_checker.get_health_summary()
        
        # Calculate additional metrics
        metrics = {
            "uptime": asyncio.get_event_loop().time(),
            "checks_total": summary["summary"]["total"],
            "checks_healthy": summary["summary"]["healthy"],
            "checks_degraded": summary["summary"]["degraded"],
            "checks_unhealthy": summary["summary"]["unhealthy"],
            "health_score": calculate_health_score(summary["summary"])
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting health metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def calculate_health_score(summary: Dict[str, int]) -> float:
    """Calculate health score based on check results."""
    total = summary["total"]
    if total == 0:
        return 0.0
    
    healthy = summary["healthy"]
    degraded = summary["degraded"]
    unhealthy = summary["unhealthy"]
    
    # Calculate score: 100% healthy = 100, 0% healthy = 0
    score = (healthy * 100 + degraded * 50 + unhealthy * 0) / total
    return round(score, 2)
```

## Metrics Collection

### 1. Metrics Implementation

```python
# src/libraries_io_mcp/metrics.py
"""Metrics collection and reporting."""

import asyncio
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class MetricData:
    """Metric data structure."""
    
    name: str
    value: float
    timestamp: datetime
    tags: Optional[Dict[str, str]] = None
    labels: Optional[Dict[str, str]] = None


class MetricsCollector:
    """Metrics collector for application metrics."""
    
    def __init__(self, max_metrics: int = 10000):
        """Initialize metrics collector."""
        self.max_metrics = max_metrics
        self.metrics = deque(maxlen=max_metrics)
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.Lock()
        
        self.logger = get_logger("metrics")
    
    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: str = "gauge",
        tags: Optional[Dict[str, str]] = None,
        labels: Optional[Dict[str, str]] = None
    ):
        """Record a metric."""
        with self.lock:
            metric = MetricData(
                name=name,
                value=value,
                timestamp=datetime.now(),
                tags=tags or {},
                labels=labels or {}
            )
            
            self.metrics.append(metric)
            
            # Update specific metric type
            if metric_type == "counter":
                self.counters[name] += value
            elif metric_type == "gauge":
                self.gauges[name] = value
            elif metric_type == "histogram":
                self.histograms[name].append(value)
            
            self.logger.debug(
                f"Recorded metric: {name}={value}",
                extra={
                    "metric_name": name,
                    "metric_value": value,
                    "metric_type": metric_type,
                    "tags": tags,
                    "labels": labels
                }
            )
    
    def increment_counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        self.record_metric(name, value, "counter", tags)
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric."""
        self.record_metric(name, value, "gauge", tags)
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a histogram metric."""
        self.record_metric(name, value, "histogram", tags)
    
    def get_metrics(
        self,
        name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[MetricData]:
        """Get metrics with optional filtering."""
        with self.lock:
            metrics = list(self.metrics)
            
            # Filter by name
            if name:
                metrics = [m for m in metrics if m.name == name]
            
            # Filter by time range
            if start_time:
                metrics = [m for m in metrics if m.timestamp >= start_time]
            
            if end_time:
                metrics = [m for m in metrics if m.timestamp <= end_time]
            
            return metrics
    
    def get_counter(self, name: str) -> int:
        """Get counter value."""
        with self.lock:
            return self.counters.get(name, 0)
    
    def get_gauge(self, name: str) -> float:
        """Get gauge value."""
        with self.lock:
            return self.gauges.get(name, 0.0)
    
    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """Get histogram statistics."""
        with self.lock:
            values = list(self.histograms.get(name, []))
            if not values:
                return {}
            
            values_sorted = sorted(values)
            count = len(values_sorted)
            
            return {
                "count": count,
                "min": min(values_sorted),
                "max": max(values_sorted),
                "mean": sum(values_sorted) / count,
                "median": values_sorted[count // 2],
                "p95": values_sorted[int(count * 0.95)],
                "p99": values_sorted[int(count * 0.99)]
            }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        with self.lock:
            return {
                "total_metrics": len(self.metrics),
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {
                    name: self.get_histogram_stats(name)
                    for name in self.histograms.keys()
                }
            }


# Global metrics collector
metrics_collector = MetricsCollector()


class MetricsMiddleware:
    """Middleware for collecting HTTP metrics."""
    
    def __init__(self, app, metrics_collector: MetricsCollector):
        """Initialize metrics middleware."""
        self.app = app
        self.metrics_collector = metrics_collector
        self.logger = get_logger("metrics.middleware")
    
    async def __call__(self, scope, receive, send):
        """Process HTTP request and collect metrics."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        method = scope["method"]
        path = scope["path"]
        status_code = 200
        
        async def send_wrapper(message):
            """Wrapper for send to capture status code."""
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time
            
            # Record metrics
            self.metrics_collector.increment_counter("http_requests_total")
            self.metrics_collector.increment_counter(
                f"http_requests_total_{status_code}",
                tags={"status_code": str(status_code)}
            )
            self.metrics_collector.record_histogram(
                "http_request_duration_seconds",
                duration,
                tags={
                    "method": method,
                    "path": path,
                    "status_code": str(status_code)
                }
            )
            
            self.logger.debug(
                f"HTTP request: {method} {path} {status_code} {duration:.3f}s",
                extra={
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration": duration
                }
            )


def setup_metrics(app):
    """Setup metrics middleware for FastAPI app."""
    middleware = MetricsMiddleware(app, metrics_collector)
    return middleware
```

### 2. Metrics Exporters

```python
# src/libraries_io_mcp/metrics_exporters.py
"""Metrics exporters for different backends."""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
from abc import ABC, abstractmethod

from .metrics import MetricsCollector, MetricData
from .logging_config import get_logger

logger = get_logger(__name__)


class MetricsExporter(ABC):
    """Abstract base class for metrics exporters."""
    
    def __init__(self, name: str):
        """Initialize metrics exporter."""
        self.name = name
        self.logger = get_logger(f"metrics.exporter.{name}")
    
    @abstractmethod
    async def export_metrics(self, metrics: List[MetricData]) -> bool:
        """Export metrics to the backend."""
        pass
    
    @abstractmethod
    async def close(self):
        """Close the exporter."""
        pass


class PrometheusExporter(MetricsExporter):
    """Prometheus metrics exporter."""
    
    def __init__(self, pushgateway_url: str, job_name: str = "libraries-io-mcp"):
        """Initialize Prometheus exporter."""
        super().__init__("prometheus")
        self.pushgateway_url = pushgateway_url
        self.job_name = job_name
        self.session = None
    
    async def export_metrics(self, metrics: List[MetricData]) -> bool:
        """Export metrics to Prometheus PushGateway."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Convert metrics to Prometheus format
            prometheus_metrics = self._convert_to_prometheus_format(metrics)
            
            # Push to PushGateway
            data = "\n".join(prometheus_metrics)
            
            async with self.session.post(
                f"{self.pushgateway_url}/metrics/job/{self.job_name}",
                data=data,
                headers={"Content-Type": "text/plain"}
            ) as response:
                if response.status == 200:
                    self.logger.info("Metrics exported to Prometheus successfully")
                    return True
                else:
                    self.logger.error(
                        f"Failed to export metrics to Prometheus: {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error exporting metrics to Prometheus: {e}")
            return False
    
    def _convert_to_prometheus_format(self, metrics: List[MetricData]) -> List[str]:
        """Convert metrics to Prometheus format."""
        prometheus_metrics = []
        
        for metric in metrics:
            # Convert metric name to Prometheus format
            prom_name = metric.name.replace(".", "_").replace("-", "_")
            
            # Convert tags to labels
            labels = []
            for key, value in metric.tags.items():
                labels.append(f'{key}="{value}"')
            
            label_str = "{" + ",".join(labels) + "}" if labels else ""
            
            # Create Prometheus metric line
            metric_line = f"{prom_name}{label_str} {metric.value} {int(metric.timestamp.timestamp() * 1000)}"
            prometheus_metrics.append(metric_line)
        
        return prometheus_metrics
    
    async def close(self):
        """Close the exporter."""
        if self.session:
            await self.session.close()


class InfluxDBExporter(MetricsExporter):
    """InfluxDB metrics exporter."""
    
    def __init__(self, url: str, token: str, org: str, bucket: str):
        """Initialize InfluxDB exporter."""
        super().__init__("influxdb")
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.session = None
    
    async def export_metrics(self, metrics: List[MetricData]) -> bool:
        """Export metrics to InfluxDB."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Convert metrics to InfluxDB line protocol format
            influxdb_data = self._convert_to_influxdb_format(metrics)
            
            # Write to InfluxDB
            headers = {
                "Authorization": f"Token {self.token}",
                "Content-Type": "application/octet-stream"
            }
            
            async with self.session.post(
                f"{self.url}/api/v2/write?org={self.org}&bucket={self.bucket}",
                data=influxdb_data,
                headers=headers
            ) as response:
                if response.status == 204:
                    self.logger.info("Metrics exported to InfluxDB successfully")
                    return True
                else:
                    self.logger.error(
                        f"Failed to export metrics to InfluxDB: {response.status}"
                    )
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error exporting metrics to InfluxDB: {e}")
            return False
    
    def _convert_to_influxdb_format(self, metrics: List[MetricData]) -> str:
        """Convert metrics to InfluxDB line protocol format."""
        lines = []
        
        for metric in metrics:
            # Convert metric name to measurement name
            measurement = metric.name.replace(".", "_").replace("-", "_")
            
            # Convert tags to tag fields
            tag_fields = []
            for key, value in metric.tags.items():
                tag_fields.append(f"{key}={value}")
            
            # Convert labels to field fields
            field_fields = []
            for key, value in metric.labels.items():
                field_fields.append(f'{key}="{value}"')
            
            # Add value field
            field_fields.append(f"value={metric.value}")
            
            # Create InfluxDB line
            tag_str = "," + ",".join(tag_fields) if tag_fields else ""
            field_str = ",".join(field_fields)
            
            timestamp = int(metric.timestamp.timestamp() * 1_000_000_000)  # nanoseconds
            
            line = f"{measurement}{tag_str} {field_str} {timestamp}"
            lines.append(line)
        
        return "\n".join(lines)
    
    async def close(self):
        """Close the exporter."""
        if self.session:
            await self.session.close()


class JSONExporter(MetricsExporter):
    """JSON metrics exporter."""
    
    def __init__(self, output_file: str):
        """Initialize JSON exporter."""
        super().__init__("json")
        self.output_file = output_file
        self.session = None
    
    async def export_metrics(self, metrics: List[MetricData]) -> bool:
        """Export metrics to JSON file."""
        try:
            # Convert metrics to JSON format
            json_data = {
                "export_timestamp": datetime.now().isoformat(),
                "metrics": [asdict(metric) for metric in metrics]
            }
            
            # Write to file
            with open(self.output_file, "w") as f:
                json.dump(json_data, f, indent=2, default=str)
            
            self.logger.info(f"Metrics exported to JSON file: {self.output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting metrics to JSON: {e}")
            return False
    
    async def close(self):
        """Close the exporter."""
        pass


class MetricsManager:
    """Manager for multiple metrics exporters."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        """Initialize metrics manager."""
        self.metrics_collector = metrics_collector
        self.exporters = []
        self.logger = get_logger("metrics.manager")
    
    def add_exporter(self, exporter: MetricsExporter):
        """Add a metrics exporter."""
        self.exporters.append(exporter)
        self.logger.info(f"Added metrics exporter: {exporter.name}")
    
    async def export_metrics(self) -> Dict[str, bool]:
        """Export metrics to all configured exporters."""
        metrics = self.metrics_collector.get_metrics()
        
        if not metrics:
            self.logger.warning("No metrics to export")
            return {}
        
        results = {}
        
        for exporter in self.exporters:
            try:
                success = await exporter.export_metrics(metrics)
                results[exporter.name] = success
                
                if success:
                    self.logger.info(f"Successfully exported metrics to {exporter.name}")
                else:
                    self.logger.error(f"Failed to export metrics to {exporter.name}")
                    
            except Exception as e:
                self.logger.error(f"Error exporting metrics to {exporter.name}: {e}")
                results[exporter.name] = False
        
        return results
    
    async def close(self):
        """Close all exporters."""
        for exporter in self.exporters:
            try:
                await exporter.close()
                self.logger.info(f"Closed exporter: {exporter.name}")
            except Exception as e:
                self.logger.error(f"Error closing exporter {exporter.name}: {e}")
```

## Alerting

### 1. Alert Implementation

```python
# src/libraries_io_mcp/alerting.py
"""Alerting system for monitoring and notifications."""

import asyncio
import smtplib
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from abc import ABC, abstractmethod

from .metrics import MetricsCollector, MetricData
from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class Alert:
    """Alert data structure."""
    
    id: str
    name: str
    severity: str  # "low", "medium", "high", "critical"
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class AlertRule:
    """Alert rule definition."""
    
    def __init__(
        self,
        name: str,
        condition: Callable[[List[MetricData]], bool],
        severity: str,
        message_template: str,
        cooldown_minutes: int = 5,
        enabled: bool = True
    ):
        """Initialize alert rule."""
        self.name = name
        self.condition = condition
        self.severity = severity
        self.message_template = message_template
        self.cooldown_minutes = cooldown_minutes
        self.enabled = enabled
        self.last_triggered = None
    
    def should_trigger(self, metrics: List[MetricData]) -> bool:
        """Check if alert should trigger."""
        if not self.enabled:
            return False
        
        # Check cooldown
        if self.last_triggered:
            cooldown_delta = timedelta(minutes=self.cooldown_minutes)
            if datetime.now() - self.last_triggered < cooldown_delta:
                return False
        
        # Check condition
        return self.condition(metrics)
    
    def trigger(self, metrics: List[MetricData]) -> Alert:
        """Trigger the alert."""
        self.last_triggered = datetime.now()
        
        # Create message
        message = self.message_template.format(
            timestamp=datetime.now().isoformat(),
            **{f"metric_{i}": m.value for i, m in enumerate(metrics)}
        )
        
        return Alert(
            id=f"{self.name}_{int(datetime.now().timestamp())}",
            name=self.name,
            severity=self.severity,
            message=message,
            timestamp=datetime.now(),
            metadata={"metrics": [asdict(m) for m in metrics]}
        )


class AlertChannel(ABC):
    """Abstract base class for alert channels."""
    
    def __init__(self, name: str):
        """Initialize alert channel."""
        self.name = name
        self.logger = get_logger(f"alerting.channel.{name}")
    
    @abstractmethod
    async def send_alert(self, alert: Alert) -> bool:
        """Send alert to the channel."""
        pass
    
    @abstractmethod
    async def send_alert_resolved(self, alert: Alert) -> bool:
        """Send alert resolved notification."""
        pass


class EmailAlertChannel(AlertChannel):
    """Email alert channel."""
    
    def __init__(
        self,
        name: str,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
        to_emails: List[str],
        use_tls: bool = True
    ):
        """Initialize email alert channel."""
        super().__init__(name)
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails
        self.use_tls = use_tls
    
    async def send_alert(self, alert: Alert) -> bool:
        """Send email alert."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"[{alert.severity.upper()}] {alert.name}"
            
            body = f"""
            Alert Details:
            - Name: {alert.name}
            - Severity: {alert.severity}
            - Message: {alert.message}
            - Timestamp: {alert.timestamp.isoformat()}
            - ID: {alert.id}
            
            Metadata:
            {json.dumps(alert.metadata or {}, indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            self.logger.info(f"Email alert sent: {alert.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
            return False
    
    async def send_alert_resolved(self, alert: Alert) -> bool:
        """Send email alert resolved notification."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = f"[RESOLVED] {alert.name}"
            
            body = f"""
            Alert Resolved:
            - Name: {alert.name}
            - Severity: {alert.severity}
            - Message: {alert.message}
            - Triggered: {alert.timestamp.isoformat()}
            - Resolved: {alert.resolved_at.isoformat()}
            - ID: {alert.id}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            self.logger.info(f"Email alert resolved notification sent: {alert.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert resolved notification: {e}")
            return False


class WebhookAlertChannel(AlertChannel):
    """Webhook alert channel."""
    
    def __init__(self, name: str, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        """Initialize webhook alert channel."""
        super().__init__(name)
        self.webhook_url = webhook_url
        self.headers = headers or {}
        self.session = None
    
    async def send_alert(self, alert: Alert) -> bool:
        """Send webhook alert."""
        if not self.session:
            import aiohttp
            self.session = aiohttp.ClientSession()
        
        try:
            payload = {
                "alert_id": alert.id,
                "name": alert.name,
                "severity": alert.severity,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved,
                "metadata": alert.metadata
            }
            
            async with self.session.post(
                self.webhook_url,
                json=payload,
                headers=self.headers
            ) as response:
                if response.status == 200:
                    self.logger.info(f"Webhook alert sent: {alert.name}")
                    return True
                else:
                    self.logger.error(f"Failed to send webhook alert: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Failed to send webhook alert: {e}")
            return False
    
    async def send_alert_resolved(self, alert: Alert) -> bool:
        """Send webhook alert resolved notification."""
        if not self.session:
            import aiohttp
            self.session = aiohttp.ClientSession()
        
        try:
            payload = {
                "alert_id": alert.id,
                "name": alert.name,
                "severity": alert.severity,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved,
                "resolved_at": alert.resolved_at.isoformat(),
                "metadata": alert.metadata
            }
            
            async with self.session.post(
                self.webhook_url,
                json=payload,
                headers=self.headers
            ) as response:
                if response.status == 200:
                    self.logger.info(f"Webhook alert resolved notification sent: {alert.name}")
                    return True
                else:
                    self.logger.error(f"Failed to send webhook alert resolved notification: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Failed to send webhook alert resolved notification: {e}")
            return False
    
    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()


class AlertManager:
    """Manager for alerts and alerting system."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        """Initialize alert manager."""
        self.metrics_collector = metrics_collector
        self.alert_rules = []
        self.alert_channels = []
        self.active_alerts = {}
        self.logger = get_logger("alerting.manager")
    
    def add_alert_rule(self, rule: AlertRule):
        """Add an alert rule."""
        self.alert_rules.append(rule)
        self.logger.info(f"Added alert rule: {rule.name}")
    
    def add_alert_channel(self, channel: AlertChannel):
        """Add an alert channel."""
        self.alert_channels.append(channel)
        self.logger.info(f"Added alert channel: {channel.name}")
    
    async def check_alerts(self):
        """Check all alert rules."""
        metrics = self.metrics_collector.get_metrics()
        
        for rule in self.alert_rules:
            try:
                if rule.should_trigger(metrics):
                    alert = rule.trigger(metrics)
                    await self._handle_alert(alert)
                    
            except Exception as e:
                self.logger.error(f"Error checking alert rule {rule.name}: {e}")
    
    async def _handle_alert(self, alert: Alert):
        """Handle an alert."""
        # Check if alert is already active
        if alert.id in self.active_alerts:
            self.logger.debug(f"Alert already active: {alert.name}")
            return
        
        # Store alert
        self.active_alerts[alert.id] = alert
        
        # Send alert to all channels
        success_channels = []
        for channel in self.alert_channels:
            try:
                success = await channel.send_alert(alert)
                if success:
                    success_channels.append(channel.name)
            except Exception as e:
                self.logger.error(f"Failed to send alert to {channel.name}: {e}")
        
        # Log alert
        self.logger.warning(
            f"Alert triggered: {alert.name} ({alert.severity})",
            extra={
                "alert_id": alert.id,
                "alert_name": alert.name,
                "alert_severity": alert.severity,
                "alert_message": alert.message,
                "success_channels": success_channels
            }
        )
    
    async def resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        if alert_id not in self.active_alerts:
            self.logger.warning(f"Alert not found: {alert_id}")
            return
        
        alert = self.active_alerts[alert_id]
        alert.resolved = True
        alert.resolved_at = datetime.now()
        
        # Remove from active alerts
        del self.active_alerts[alert_id]
        
        # Send resolved notification to all channels
        success_channels = []
        for channel in self.alert_channels:
            try:
                success = await channel.send_alert_resolved(alert)
                if success:
                    success_channels.append(channel.name)
            except Exception as e:
                self.logger.error(f"Failed to send alert resolved to {channel.name}: {e}")
        
        # Log alert resolution
        self.logger.info(
            f"Alert resolved: {alert.name}",
            extra={
                "alert_id": alert.id,
                "alert_name": alert.name,
                "success_channels": success_channels
            }
        )
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return list(self.active_alerts.values())
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary."""
        active_alerts = self.get_active_alerts()
        
        severity_counts = {}
        for alert in active_alerts:
            severity_counts[alert.severity] = severity_counts.get(alert.se
            "alert_severity": alert.severity,
            "success_channels": success_channels
        }
        )
    
    async def close(self):
        """Close the alert manager."""
        for channel in self.alert_channels:
            try:
                if hasattr(channel, 'close'):
                    await channel.close()
            except Exception as e:
                self.logger.error(f"Error closing alert channel {channel.name}: {e}")


def create_default_alert_rules() -> List[AlertRule]:
    """Create default alert rules."""
    rules = []
    
    # High error rate rule
    def high_error_rate_condition(metrics: List[MetricData]) -> bool:
        error_metrics = [m for m in metrics if m.name == "http_requests_total_500"]
        return len(error_metrics) > 10  # More than 10 errors in the last check
    
    rules.append(AlertRule(
        name="high_error_rate",
        condition=high_error_rate_condition,
        severity="high",
        message="High error rate detected: {metric_0} errors in the last period",
        cooldown_minutes=10
    ))
    
    # High response time rule
    def high_response_time_condition(metrics: List[MetricData]) -> bool:
        response_time_metrics = [m for m in metrics if m.name == "http_request_duration_seconds"]
        if not response_time_metrics:
            return False
        
        avg_response_time = sum(m.value for m in response_time_metrics) / len(response_time_metrics)
        return avg_response_time > 2.0  # Average response time > 2 seconds
    
    rules.append(AlertRule(
        name="high_response_time",
        condition=high_response_time_condition,
        severity="medium",
        message="High response time detected: average {metric_0:.2f}s",
        cooldown_minutes=5
    ))
    
    # Low success rate rule
    def low_success_rate_condition(metrics: List[MetricData]) -> bool:
        total_requests = 0
        error_requests = 0
        
        for metric in metrics:
            if metric.name == "http_requests_total":
                total_requests += metric.value
            elif metric.name.startswith("http_requests_total_4") or metric.name.startswith("http_requests_total_5"):
                error_requests += metric.value
        
        if total_requests == 0:
            return False
        
        success_rate = (total_requests - error_requests) / total_requests
        return success_rate < 0.95  # Success rate < 95%
    
    rules.append(AlertRule(
        name="low_success_rate",
        condition=low_success_rate_condition,
        severity="high",
        message="Low success rate detected: {metric_0:.1%} success rate",
        cooldown_minutes=5
    ))
    
    return rules


def create_default_alert_channels() -> List[AlertChannel]:
    """Create default alert channels."""
    channels = []
    
    # Email channel (if configured)
    import os
    if os.getenv("SMTP_SERVER") and os.getenv("SMTP_USERNAME") and os.getenv("SMTP_PASSWORD"):
        channels.append(EmailAlertChannel(
            name="email",
            smtp_server=os.getenv("SMTP_SERVER"),
            smtp_port=int(os.getenv("SMTP_PORT", 587)),
            username=os.getenv("SMTP_USERNAME"),
            password=os.getenv("SMTP_PASSWORD"),
            from_email=os.getenv("SMTP_FROM_EMAIL", "alerts@libraries-io-mcp-server"),
            to_emails=os.getenv("SMTP_TO_EMAILS", "").split(","),
            use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        ))
    
    # Webhook channel (if configured)
    if os.getenv("WEBHOOK_URL"):
        channels.append(WebhookAlertChannel(
            name="webhook",
            webhook_url=os.getenv("WEBHOOK_URL"),
            headers={"Authorization": f"Bearer {os.getenv('WEBHOOK_TOKEN')}"}
        ))
    
    return channels
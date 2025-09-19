# Scaling Strategies

This document provides comprehensive guidance for scaling the Libraries.io MCP Server to handle increased load, larger datasets, and higher concurrency. Implementing these strategies will ensure your server remains performant and reliable as usage grows.

## Overview

Scaling the Libraries.io MCP Server involves addressing several key areas:

- **Vertical Scaling**: Increasing resources of a single server
- **Horizontal Scaling**: Adding more servers to distribute load
- **Database Scaling**: Scaling database storage and query performance
- **Caching Scaling**: Implementing distributed caching
- **Load Balancing**: Distributing traffic across multiple servers
- **Auto-scaling**: Automatically adjusting resources based on demand

## Scaling Approaches

### 1. Vertical Scaling

Vertical scaling involves increasing the resources of a single server.

#### Implementation

```python
# src/libraries_io_mcp/scaling/vertical_scaling.py
"""Vertical scaling implementation."""

import asyncio
import os
import psutil
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ResourceUsage:
    """Resource usage data structure."""
    
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, float]
    
    def is_overloaded(self, thresholds: Dict[str, float]) -> bool:
        """Check if resource usage exceeds thresholds."""
        return (
            self.cpu_percent > thresholds.get("cpu", 80) or
            self.memory_percent > thresholds.get("memory", 85) or
            self.disk_percent > thresholds.get("disk", 90)
        )


class VerticalScaler:
    """Vertical scaling manager."""
    
    def __init__(self, check_interval: int = 60):
        """Initialize vertical scaler."""
        self.check_interval = check_interval
        self.resource_history: list = []
        self.scaling_actions = []
        self.logger = get_logger("vertical_scaler")
        
        logger.info("Vertical scaler initialized")
    
    async def monitor_resources(self):
        """Monitor system resources."""
        while True:
            try:
                # Get resource usage
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                resource_usage = ResourceUsage(
                    timestamp=datetime.now(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    disk_percent=disk.percent,
                    network_io={
                        "bytes_sent": network.bytes_sent,
                        "bytes_recv": network.bytes_recv,
                        "packets_sent": network.packets_sent,
                        "packets_recv": network.packets_recv
                    }
                )
                
                # Store resource usage
                self.resource_history.append(resource_usage)
                
                # Keep only recent history
                if len(self.resource_history) > 1000:
                    self.resource_history = self.resource_history[-1000:]
                
                # Check for scaling needs
                await self._check_scaling_needs(resource_usage)
                
                self.logger.debug(
                    f"Resource usage: CPU {cpu_percent:.1f}%, "
                    f"Memory {memory.percent:.1f}%, "
                    f"Disk {disk.percent:.1f}%"
                )
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Resource monitoring error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_scaling_needs(self, resource_usage: ResourceUsage):
        """Check if scaling is needed."""
        thresholds = {
            "cpu": 80,
            "memory": 85,
            "disk": 90
        }
        
        if resource_usage.is_overloaded(thresholds):
            self.logger.warning(
                f"Resource overload detected: "
                f"CPU {resource_usage.cpu_percent:.1f}%, "
                f"Memory {resource_usage.memory_percent:.1f}%, "
                f"Disk {resource_usage.disk_percent:.1f}%"
            )
            
            # Trigger scaling action
            await self._trigger_scaling(resource_usage)
    
    async def _trigger_scaling(self, resource_usage: ResourceUsage):
        """Trigger scaling action."""
        action = {
            "timestamp": datetime.now(),
            "type": "vertical_scaling_needed",
            "resource_usage": {
                "cpu_percent": resource_usage.cpu_percent,
                "memory_percent": resource_usage.memory_percent,
                "disk_percent": resource_usage.disk_percent
            },
            "recommendations": self._get_scaling_recommendations(resource_usage)
        }
        
        self.scaling_actions.append(action)
        self.logger.info(f"Scaling action triggered: {action}")
        
        # In a real implementation, this would trigger actual scaling
        # For now, we'll just log the action
        await self._execute_scaling_action(action)
    
    def _get_scaling_recommendations(self, resource_usage: ResourceUsage) -> list:
        """Get scaling recommendations."""
        recommendations = []
        
        if resource_usage.cpu_percent > 80:
            recommendations.append("Increase CPU cores or upgrade to a more powerful instance")
        
        if resource_usage.memory_percent > 85:
            recommendations.append("Increase RAM allocation")
        
        if resource_usage.disk_percent > 90:
            recommendations.append("Increase disk space or implement data cleanup")
        
        return recommendations
    
    async def _execute_scaling_action(self, action: Dict[str, Any]):
        """Execute scaling action."""
        # This would be implemented based on your cloud provider
        # For now, we'll just log the action
        self.logger.info(f"Executing scaling action: {action}")
        
        # Example: Increase CPU cores
        if action["resource_usage"]["cpu_percent"] > 80:
            await self._increase_cpu_cores()
        
        # Example: Increase memory
        if action["resource_usage"]["memory_percent"] > 85:
            await self._increase_memory()
    
    async def _increase_cpu_cores(self):
        """Increase CPU cores."""
        # This would be implemented based on your cloud provider
        self.logger.info("Increasing CPU cores")
        
        # Example: Update cloud instance type
        # await self.cloud_client.update_instance_type("c5.2xlarge")
    
    async def _increase_memory(self):
        """Increase memory."""
        # This would be implemented based on your cloud provider
        self.logger.info("Increasing memory")
        
        # Example: Update cloud instance type
        # await self.cloud_client.update_instance_type("r5.2xlarge")
    
    def get_resource_history(self, hours: int = 24) -> list:
        """Get resource history for specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            usage for usage in self.resource_history
            if usage.timestamp >= cutoff_time
        ]
    
    def get_scaling_actions(self) -> list:
        """Get scaling actions history."""
        return self.scaling_actions.copy()


# Example usage
async def example_usage():
    """Example usage of vertical scaling."""
    scaler = VerticalScaler(check_interval=30)
    
    # Start monitoring
    monitor_task = asyncio.create_task(scaler.monitor_resources())
    
    # Let it run for a while
    await asyncio.sleep(120)
    
    # Get resource history
    history = scaler.get_resource_history(hours=1)
    print(f"Resource history: {len(history)} entries")
    
    # Get scaling actions
    actions = scaler.get_scaling_actions()
    print(f"Scaling actions: {len(actions)} actions")
    
    # Stop monitoring
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass
```

### 2. Horizontal Scaling

Horizontal scaling involves adding more servers to distribute the load.

#### Implementation

```python
# src/libraries_io_mcp/scaling/horizontal_scaling.py
"""Horizontal scaling implementation."""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import aiohttp

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ServerInfo:
    """Server information data structure."""
    
    id: str
    name: str
    host: str
    port: int
    status: str  # "active", "inactive", "draining"
    created_at: datetime
    last_heartbeat: Optional[datetime] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    request_count: int = 0
    active_connections: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "request_count": self.request_count,
            "active_connections": self.active_connections
        }


class HorizontalScaler:
    """Horizontal scaling manager."""
    
    def __init__(
        self,
        min_servers: int = 2,
        max_servers: int = 10,
        scaling_threshold: float = 0.7,
        cooldown_minutes: int = 5,
        cloud_provider: Optional[str] = None
    ):
        """Initialize horizontal scaler."""
        self.min_servers = min_servers
        self.max_servers = max_servers
        self.scaling_threshold = scaling_threshold
        self.cooldown_minutes = cooldown_minutes
        self.cloud_provider = cloud_provider
        
        self.servers: Dict[str, ServerInfo] = {}
        self.scaling_history: List[Dict[str, Any]] = []
        self.last_scaling_action = None
        
        self.logger = get_logger("horizontal_scaler")
        
        logger.info(
            "Horizontal scaler initialized",
            extra={
                "min_servers": min_servers,
                "max_servers": max_servers,
                "scaling_threshold": scaling_threshold,
                "cooldown_minutes": cooldown_minutes
            }
        )
    
    async def add_server(self, server_info: ServerInfo) -> bool:
        """Add a new server."""
        if len(self.servers) >= self.max_servers:
            self.logger.warning(f"Maximum servers reached: {self.max_servers}")
            return False
        
        self.servers[server_info.id] = server_info
        self.logger.info(f"Added server: {server_info.name} ({server_info.id})")
        
        # Trigger health check
        await self._check_server_health(server_info.id)
        
        return True
    
    async def remove_server(self, server_id: str) -> bool:
        """Remove a server."""
        if server_id not in self.servers:
            return False
        
        server = self.servers[server_id]
        server.status = "draining"
        
        self.logger.info(f"Removing server: {server.name} ({server_id})")
        
        # Drain server
        await self._drain_server(server_id)
        
        # Remove from active servers
        del self.servers[server_id]
        
        return True
    
    async def _drain_server(self, server_id: str):
        """Drain server connections."""
        server = self.servers.get(server_id)
        if not server:
            return
        
        # This would typically involve:
        # 1. Stop accepting new connections
        # 2. Wait for existing connections to complete
        # 3. Update load balancer to remove server from rotation
        
        self.logger.info(f"Draining server: {server.name}")
        
        # Simulate draining
        while server.active_connections > 0:
            await asyncio.sleep(1)
            server.active_connections = max(0, server.active_connections - 1)
        
        server.status = "inactive"
        self.logger.info(f"Server drained: {server.name}")
    
    async def _check_server_health(self, server_id: str):
        """Check server health."""
        server = self.servers.get(server_id)
        if not server:
            return
        
        try:
            # This would make an HTTP request to the server health endpoint
            # For now, we'll simulate it
            await asyncio.sleep(0.1)  # Simulate health check
            
            server.status = "active"
            server.last_heartbeat = datetime.now()
            
            self.logger.debug(f"Server health check passed: {server.name}")
            
        except Exception as e:
            server.status = "inactive"
            self.logger.error(f"Server health check failed: {server.name} - {e}")
    
    async def check_scaling_needs(self):
        """Check if scaling is needed."""
        if not self.servers:
            return
        
        # Calculate average load
        total_cpu = sum(s.cpu_usage for s in self.servers.values())
        total_memory = sum(s.memory_usage for s in self.servers.values())
        total_connections = sum(s.active_connections for s in self.servers.values())
        
        avg_cpu = total_cpu / len(self.servers)
        avg_memory = total_memory / len(self.servers)
        avg_connections = total_connections / len(self.servers)
        
        # Check if scaling is needed
        needs_scaling = (
            avg_cpu > self.scaling_threshold or
            avg_memory > self.scaling_threshold or
            avg_connections > 1000  # Example threshold
        )
        
        # Check cooldown
        if self.last_scaling_action:
            cooldown_time = datetime.now() - self.last_scaling_action
            if cooldown_time < timedelta(minutes=self.cooldown_minutes):
                needs_scaling = False
        
        if needs_scaling:
            await self._trigger_scaling(avg_cpu, avg_memory, avg_connections)
    
    async def _trigger_scaling(self, avg_cpu: float, avg_memory: float, avg_connections: float):
        """Trigger scaling action."""
        current_servers = len([s for s in self.servers.values() if s.status == "active"])
        
        if current_servers >= self.max_servers:
            self.logger.warning("Maximum servers reached, cannot scale up")
            return
        
        # Determine scaling direction
        if avg_cpu > self.scaling_threshold or avg_memory > self.scaling_threshold:
            # Scale up
            await self._scale_up()
        elif current_servers > self.min_servers and avg_connections < 500:
            # Scale down
            await self._scale_down()
    
    async def _scale_up(self):
        """Scale up by adding servers."""
        current_servers = len([s for s in self.servers.values() if s.status == "active"])
        
        if current_servers >= self.max_servers:
            return
        
        # Create new server
        server_id = f"server_{int(time.time())}"
        server_info = ServerInfo(
            id=server_id,
            name=f"server-{current_servers + 1}",
            host=f"server-{current_servers + 1}.example.com",
            port=8000 + current_servers + 1,
            status="pending",
            created_at=datetime.now()
        )
        
        # Add server
        await self.add_server(server_info)
        
        # Record scaling action
        action = {
            "timestamp": datetime.now(),
            "type": "scale_up",
            "server_id": server_id,
            "reason": "high_cpu_or_memory"
        }
        
        self.scaling_history.append(action)
        self.last_scaling_action = datetime.now()
        
        self.logger.info(f"Scaled up: added {server_info.name}")
    
    async def _scale_down(self):
        """Scale down by removing servers."""
        current_servers = len([s for s in self.servers.values() if s.status == "active"])
        
        if current_servers <= self.min_servers:
            return
        
        # Find server to remove (least loaded)
        servers_to_remove = [
            s for s in self.servers.values()
            if s.status == "active"
        ]
        
        if not servers_to_remove:
            return
        
        # Sort by load (ascending)
        servers_to_remove.sort(key=lambda s: s.cpu_usage + s.memory_usage)
        
        server_to_remove = servers_to_remove[0]
        
        # Remove server
        await self.remove_server(server_to_remove.id)
        
        # Record scaling action
        action = {
            "timestamp": datetime.now(),
            "type": "scale_down",
            "server_id": server_to_remove.id,
            "reason": "low_load"
        }
        
        self.scaling_history.append(action)
        self.last_scaling_action = datetime.now()
        
        self.logger.info(f"Scaled down: removed {server_to_remove.name}")
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get current server status."""
        active_servers = [s for s in self.servers.values() if s.status == "active"]
        inactive_servers = [s for s in self.servers.values() if s.status == "inactive"]
        draining_servers = [s for s in self.servers.values() if s.status == "draining"]
        
        return {
            "total_servers": len(self.servers),
            "active_servers": len(active_servers),
            "inactive_servers": len(inactive_servers),
            "draining_servers": len(draining_servers),
            "servers": [s.to_dict() for s in self.servers.values()]
        }
    
    def get_scaling_history(self) -> List[Dict[str, Any]]:
        """Get scaling history."""
        return self.scaling_history.copy()


class LoadBalancer:
    """Load balancer for distributing traffic."""
    
    def __init__(self, servers: List[ServerInfo]):
        """Initialize load balancer."""
        self.servers = servers
        self.current_index = 0
        self.logger = get_logger("load_balancer")
    
    def get_server(self) -> Optional[ServerInfo]:
        """Get next server using round-robin."""
        active_servers = [s for s in self.servers if s.status == "active"]
        
        if not active_servers:
            return None
        
        server = active_servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(active_servers)
        
        return server
    
    def get_least_loaded_server(self) -> Optional[ServerInfo]:
        """Get least loaded server."""
        active_servers = [s for s in self.servers if s.status == "active"]
        
        if not active_servers:
            return None
        
        # Sort by load (ascending)
        active_servers.sort(key=lambda s: s.cpu_usage + s.memory_usage)
        
        return active_servers[0]
    
    def get_server_by_weight(self) -> Optional[ServerInfo]:
        """Get server by weighted load balancing."""
        active_servers = [s for s in self.servers if s.status == "active"]
        
        if not active_servers:
            return None
        
        # Calculate weights based on capacity
        total_capacity = sum(100 - s.cpu_usage - s.memory_usage for s in active_servers)
        
        if total_capacity <= 0:
            return active_servers[0]
        
        # Select server based on weight
        import random
        weight = random.uniform(0, total_capacity)
        cumulative_weight = 0
        
        for server in active_servers:
            server_weight = 100 - server.cpu_usage - server.memory_usage
            cumulative_weight += server_weight
            
            if weight <= cumulative_weight:
                return server
        
        return active_servers[-1]


# Example usage
async def example_usage():
    """Example usage of horizontal scaling."""
    # Create servers
    servers = [
        ServerInfo(
            id="server1",
            name="server-1",
            host="server-1.example.com",
            port=8000,
            status="active",
            created_at=datetime.now()
        ),
        ServerInfo(
            id="server2",
            name="server-2",
            host="server-2.example.com",
            port=8001,
            status="active",
            created_at=datetime.now()
        )
    ]
    
    # Create load balancer
    load_balancer = LoadBalancer(servers)
    
    # Create horizontal scaler
    scaler = HorizontalScaler(
        min_servers=2,
        max_servers=5,
        scaling_threshold=0.7
    )
    
    # Add servers to scaler
    for server in servers:
        await scaler.add_server(server)
    
    # Simulate load
    for server in servers:
        server.cpu_usage = 0.6
        server.memory_usage = 0.5
        server.active_connections = 800
    
    # Check scaling needs
    await scaler.check_scaling_needs()
    
    # Get server status
    status = scaler.get_server_status()
    print("Server status:", status)
    
    # Get scaling history
    history = scaler.get_scaling_history()
    print("Scaling history:", history)
```

### 3. Database Scaling

Database scaling involves optimizing database performance and handling increased data volume.

#### Implementation

```python
# src/libraries_io_mcp/scaling/database_scaling.py
"""Database scaling implementation."""

import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import aiosqlite

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class DatabaseMetrics:
    """Database metrics data structure."""
    
    timestamp: datetime
    query_count: int
    avg_query_time: float
    slow_query_count: int
    connection_count: int
    table_sizes: Dict[str, int]
    cache_hit_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "query_count": self.query_count,
            "avg_query_time": self.avg_query_time,
            "slow_query_count": self.slow_query_count,
            "connection_count": self.connection_count,
            "table_sizes": self.table_sizes,
            "cache_hit_rate": self.cache_hit_rate
        }


class DatabaseScaler:
    """Database scaling manager."""
    
    def __init__(
        self,
        max_connections: int = 100,
        max_query_time: float = 1.0,
        max_table_size_mb: int = 1000,
        read_replicas: int = 0
    ):
        """Initialize database scaler."""
        self.max_connections = max_connections
        self.max_query_time = max_query_time
        self.max_table_size_mb = max_table_size_mb
        self.read_replicas = read_replicas
        
        self.metrics_history: List[DatabaseMetrics] = []
        self.scaling_actions: List[Dict[str, Any]] = []
        
        self.logger = get_logger("database_scaler")
        
        logger.info(
            "Database scaler initialized",
            extra={
                "max_connections": max_connections,
                "max_query_time": max_query_time,
                "max_table_size_mb": max_table_size_mb,
                "read_replicas": read_replicas
            }
        )
    
    async def check_database_health(self, db_path: str) -> DatabaseMetrics:
        """Check database health and metrics."""
        try:
            # Connect to database
            async with aiosqlite.connect(db_path) as db:
                # Get query count
                query_count_result = await db.execute("SELECT COUNT(*) FROM sqlite_master")
                query_count = (await query_count_result.fetchone())[0]
                
                # Get table sizes
                table_sizes = {}
                tables_result = await db.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = await tables_result.fetchall()
                
                for table in tables:
                    table_name = table[0]
                    size_result = await db.execute(f"SELECT COUNT(*) FROM {table_name}")
                    size = (await size_result.fetchone())[0]
                    table_sizes[table_name] = size
                
                # Get connection count (simulated)
                connection_count = 10  # This would be actual connection count
                
                # Get cache hit rate (simulated)
                cache_hit_rate = 0.8
                
                # Create metrics
                metrics = DatabaseMetrics(
                    timestamp=datetime.now(),
                    query_count=query_count,
                    avg_query_time=0.1,  # This would be actual average
                    slow_query_count=0,   # This would be actual count
                    connection_count=connection_count,
                    table_sizes=table_sizes,
                    cache_hit_rate=cache_hit_rate
                )
                
                # Store metrics
                self.metrics_history.append(metrics)
                
                # Keep only recent metrics
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                
                return metrics
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            raise
    
    async def check_scaling_needs(self, db_path: str):
        """Check if database scaling is needed."""
        metrics = await self.check_database_health(db_path)
        
        # Check various scaling triggers
        needs_scaling = False
        scaling_reason = []
        
        # Check connection count
        if metrics.connection_count > self.max_connections * 0.8:
            needs_scaling = True
            scaling_reason.append("high_connection_count")
        
        # Check query performance
        if metrics.avg_query_time > self.max_query_time:
            needs_scaling = True
            scaling_reason.append("slow_queries")
        
        # Check table sizes
        large_tables = [
            table for table, size in metrics.table_sizes.items()
            if size > self.max_table_size_mb * 1000  # Convert to rows
        ]
        
        if large_tables:
            needs_scaling = True
            scaling_reason.append(f"large_tables: {', '.join(large_tables)}")
        
        # Check cache hit rate
        if metrics.cache_hit_rate < 0.5:
            needs_scaling = True
            scaling_reason.append("low_cache_hit_rate")
        
        if needs_scaling:
            await self._trigger_scaling(metrics, scaling_reason)
    
    async def _trigger_scaling(self, metrics: DatabaseMetrics, reasons: List[str]):
        """Trigger database scaling action."""
        action = {
            "timestamp": datetime.now(),
            "type": "database_scaling_needed",
            "metrics": metrics.to_dict(),
            "reasons": reasons,
            "recommendations": self._get_scaling_recommendations(metrics, reasons)
        }
        
        self.scaling_actions.append(action)
        self.logger.info(f"Database scaling triggered: {reasons}")
        
        # Execute scaling action
        await self._execute_scaling_action(action)
    
    def _get_scaling_recommendations(self, metrics: DatabaseMetrics, reasons: List[str]) -> List[str]:
        """Get scaling recommendations."""
        recommendations = []
        
        if "high_connection_count" in reasons:
            recommendations.append("Increase connection pool size or implement connection pooling")
        
        if "slow_queries" in reasons:
            recommendations.append("Add database indexes or optimize queries")
        
        if "large_tables" in reasons:
            recommendations.append("Implement table partitioning or data archiving")
        
        if "low_cache_hit_rate" in reasons:
            recommendations.append("Increase cache size or optimize cache strategy")
        
        if self.read_replicas == 0:
            recommendations.append("Consider adding read replicas for better read performance")
        
        return recommendations
    
    async def _execute_scaling_action(self, action: Dict[str, Any]):
        """Execute database scaling action."""
        reasons = action["reasons"]
        
        if "high_connection_count" in reasons:
            await self._increase_connection_pool()
        
        if "slow_queries" in reasons:
            await self._optimize_queries()
        
        if "large_tables" in reasons:
            await self._partition_tables()
        
        if "low_cache_hit_rate" in reasons:
            await self._increase_cache_size()
        
        if self.read_replicas == 0 and len(reasons) > 1:
            await self._add_read_replica()
    
    async def _increase_connection_pool(self):
        """Increase connection pool size."""
        self.logger.info("Increasing connection pool size")
        # This would be implemented based on your database configuration
        # Example: Update connection pool settings
    
    async def _optimize_queries(self):
        """Optimize database queries."""
        self.logger.info("Optimizing database queries")
        # This would involve:
        # 1. Analyzing slow queries
        # 2. Adding appropriate indexes
        # 3. Rewriting inefficient queries
    
    async def _partition_tables(self):
        """Partition large tables."""
        self.logger.info("Partitioning large tables")
        # This would involve:
        # 1. Identifying large tables
        # 2. Creating partitions based on date or other criteria
        # 3. Merging data to partitions
    
    async def _increase_cache_size(self):
        """Increase cache size."""
        self.logger.info("Increasing cache size")
        # This would be implemented based on your cache configuration
        # Example: Increase Redis memory limit
    
    async def _add_read_replica(self):
        """Add read replica."""
        self.logger.info("Adding read replica")
        # This would involve:
        # 1. Creating a new database instance
        # 2. Setting up replication
        # 3. Configuring read routing
    
    def get_database_metrics(self, hours: int = 24) -> List[DatabaseMetrics]:
        """Get database metrics for specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            metrics for metrics in self.metrics_history
            if metrics.timestamp >= cutoff_time
        ]
    
    def get_scaling_actions(self) -> List[Dict[str, Any]]:
        """Get scaling actions history."""
        return self.scaling_actions.copy()


class DatabaseSharding:
    """Database sharding implementation."""
    
    def __init__(self, shard_count: int = 4):
        """Initialize database sharding."""
        self.shard_count = shard_count
        self.shards: Dict[int, str] = {}  # shard_id -> db_path
        self.shard_mapping: Dict[str, int] = {}  # table_name -> shard_id
        
        self.logger = get_logger("database_sharding")
        
        logger.info(f"Database sharding initialized with {shard_count} shards")
    
    def add_shard(self, shard_id: int, db_path: str):
        """Add a database shard."""
        self.shards[shard_id] = db_path
        self.logger.info(f"Added shard {shard_id}: {db_path}")
    
    def get_shard_for_table(self, table_name: str) -> int:
        """Get shard ID for a table."""
        if table_name not in self.shard_mapping:
            # Simple hash-based sharding
            shard_id = hash(table_name) % self.shard_count
            self.shard_mapping[table_name] = shard_id
            self.logger.debug(f"Mapped table {table_name} to shard {shard_id}")
        
        return self.shard_mapping[table_name]
    
    async def execute_query(self, table_name: str, query: str, params: tuple = None) -> List[Dict]:
        """Execute query on appropriate shard."""
        shard_id = self.get_shard_for_table(table_name)
        db_path = self.shards.get(shard_id)
        
        if not db_path:
            raise ValueError(f"No shard found for table {table_name}")
        
        try:
            async with aiosqlite.connect(db_path) as db:
                cursor = await db.execute(query, params or ())
                columns = [description[0] for description in cursor.description]
                rows = await cursor.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Query failed on shard {shard_id}: {e}")
            raise
    
    async def execute_on_all_shards(self, query: str, params: tuple = None) -> Dict[int, List[Dict]]:
        """Execute query on all shards."""
        results = {}
        
        for shard_id, db_path in self.shards.items():
            try:
                async with aiosqlite.connect(db_path) as db:
                    cursor = await db.execute(query, params or ())
                    columns = [description[0] for description in cursor.description]
                    rows = await cursor.fetchall()
                    
                    results[shard_id] = [dict(zip(columns, row)) for row in rows]
                    
            except Exception as e:
                self.logger.error(f"Query failed on shard {shard_id}: {e}")
                results[shard_id] = []
        
        return results


# Example usage
async def example_usage():
    """Example usage of database scaling."""
    # Create database scaler
    scaler = DatabaseScaler(
        max_connections=50,
        max_query_time=0.5,
        max_table_size_mb=500,
        read_replicas=1
    )
    
    # Check database health
    metrics = await scaler.check_database_health("example.db")
    print("Database metrics:", metrics.to_dict())
    
    # Check scaling needs
    await scaler.check_scaling_needs("example.db")
    
    # Get scaling actions
    actions = scaler.get_scaling_actions()
    print("Scaling actions:", actions)
    
    # Create database sharding
    sharding = DatabaseSharding(shard_count=4)
    
    # Add shards
    for i in range(4):
        sharding.add_shard(i, f"shard_{i}.db")
    
    # Execute query
    results = await sharding.execute_query("packages", "SELECT * FROM packages LIMIT 10")
    print("Sharded query results:", results)
```

### 4. Caching Scaling

Caching scaling involves implementing distributed caching and cache optimization strategies.

#### Implementation

```python
# src/libraries_io_mcp/scaling/caching_scaling.py
"""Caching scaling implementation."""

import asyncio
import time
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class CacheMetrics:
    """Cache metrics data structure."""
    
    timestamp: datetime
    hit_count: int
    miss_count: int
    eviction_count: int
    memory_usage: int
    item_count: int
    avg_response_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "hit_count": self.hit_count,
            "miss_count": miss_count,
            "eviction_count": self.eviction_count,
            "memory_usage": self.memory_usage,
            "item_count": self.item_count,
            "avg_response_time": self.avg_response_time
        }


class DistributedCache:
    """Distributed cache implementation."""
    
    def __init__(self, nodes: List[str], replication_factor: int = 2):
        """Initialize distributed cache."""
        self.nodes = nodes
        self.replication_factor = replication_factor
        self.ring = {}  # Consistent hashing ring
        self.virtual_nodes = 100  # Number of virtual nodes per physical node
        
        self.metrics_history: List[CacheMetrics] = []
        self.scaling_actions: List[Dict[str, Any]] = []
        
        self._build_consistent_hash_ring()
        
        self.logger = get_logger("distributed_cache")
        
        logger.info(
            "Distributed cache initialized",
            extra={
                "nodes": nodes,
                "replication_factor": replication_factor,
                "virtual_nodes": virtual_nodes
            }
        )
    
    def _build_consistent_hash_ring(self):
        """Build consistent hashing ring."""
        self.ring = {}
        
        for node in self.nodes:
            for i in range(self.virtual_nodes):
                virtual_key = f"{node}:{i}"
                hash_value = hash(virtual_key) % 2**32
                self.ring[hash_value] = node
        
        # Sort the ring
        self.sorted_keys = sorted(self.ring.keys())
    
    def _get_nodes_for_key(self, key: str) -> List[str]:
        """Get nodes for a key using consistent hashing."""
        if not self.sorted_keys:
            return []
        
        # Calculate hash of key
        key_hash = hash(key) % 2**32
        
        # Find the first node in the ring
        for ring_key in self.sorted_keys:
            if key_hash <= ring_key:
                node = self.ring[ring_key]
                break
        else:
            # Wrap around to the first node
            node = self.ring[self.sorted_keys[0]]
        
        # Get the next N nodes for replication
        nodes = [node]
        current_index = self.sorted_keys.index(ring_key)
        
        for i in range(1, self.replication_factor):
            next_index = (current_index + i) % len(self.sorted_keys)
            next_node = self.ring[self.sorted_keys[next_index]]
            if next_node not in nodes:
                nodes.append(next_node)
        
        return nodes
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        nodes = self._get_nodes_for_key(key)
        
        # Try nodes in order
        for node in nodes:
            try:
                # This would make an HTTP request to the cache node
                # For now, we'll simulate it
                value = await self._get_from_node(node, key)
                if value is not None:
                    return value
            except Exception as e:
                logger.error(f"Failed to get from node {node}: {e}")
                continue
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        nodes = self._get_nodes_for_key(key)
        
        success = True
        for node in nodes:
            try:
                await self._set_on_node(node, key, value, ttl)
            except Exception as e:
                logger.error(f"Failed to set on node {node}: {e}")
                success = False
        
        return success
    
    async def _get_from_node(self, node: str, key: str) -> Optional[Any]:
        """Get value from a specific node."""
        # This would make an HTTP request to the cache node
        # For now, we'll simulate it
        await asyncio.sleep(0.01)  # Simulate network latency
        
        # Simulate cache hit/miss
        if hash(key) % 2 == 0:  # Simulate 50% hit rate
            return {"key": key, "value": f"value_{key}"}
        else:
            return None
    
    async def _set_on_node(self, node: str, key: str, value: Any, ttl: Optional[int]):
        """Set value on a specific node."""
        # This would make an HTTP request to the cache node
        # For now, we'll simulate it
        await asyncio.sleep(0.01)  # Simulate network latency
    
    async def check_cache_health(self) -> CacheMetrics:
        """Check cache health and metrics."""
        # This would collect metrics from all cache nodes
        # For now, we'll simulate it
        
        hit_count = 1000
        miss_count = 500
        eviction_count = 10
        memory_usage = 500 * 1024 * 1024  # 500MB
        item_count = 5000
        avg_response_time = 0.01  # 10ms
        
        metrics = CacheMetrics(
            timestamp=datetime.now(),
            hit_count=hit_count,
            miss_count=miss_count,
            eviction_count=eviction_count,
            memory_usage=memory_usage,
            item_count=item_count,
            avg_response_time=avg_response_time
        )
        
        # Store metrics
        self.metrics_history.append(metrics)
        
        # Keep only recent metrics
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return metrics
    
    async def check_scaling_needs(self):
        """Check if cache scaling is needed."""
        metrics = await self.check_cache_health()
        
        # Check various scaling triggers
        needs_scaling = False
        scaling_reason = []
        
        # Check hit rate
        total_requests = metrics.hit_count + metrics.miss_count
        hit_rate = metrics.hit_count / total_requests if total_requests > 0 else 0
        
        if hit_rate < 0.8:  # Less than 80% hit rate
            needs_scaling = True
            scaling_reason.append("low_hit_rate")
        
        # Check memory usage
        if metrics.memory_usage > 1024 * 1024 * 1024:  # 1GB
            needs_scaling = True
            scaling_reason.append("high_memory_usage")
        
        # Check response time
        if metrics.avg_response_time > 0.05:  # 50ms
            needs_scaling = True
            scaling_reason.append("high_response_time")
        
        # Check eviction rate
        if metrics.eviction_count > 100:
            needs_scaling = True
            scaling_reason.append("high_eviction_rate")
        
        if needs_scaling:
            await self._trigger_scaling(metrics, scaling_reason)
    
    async def _trigger_scaling(self, metrics: CacheMetrics, reasons: List[str]):
        """Trigger cache scaling action."""
        action = {
            "timestamp": datetime.now(),
            "type": "cache_scaling_needed",
            "metrics": metrics.to_dict(),
            "reasons": reasons,
            "recommendations": self._get_scaling_recommendations(metrics, reasons)
        }
        
        self.scaling_actions.append(action)
        self.logger.info(f"Cache scaling triggered: {reasons}")
        
        # Execute scaling action
        await self._execute_scaling_action(action)
    
    def _get_scaling_recommendations(self, metrics: CacheMetrics, reasons: List[str]) -> List[str]:
        """Get scaling recommendations."""
        recommendations = []
        
        if "low_hit_rate" in reasons:
            recommendations.append("Increase cache size or optimize cache keys")
        
        if "high_memory_usage" in reasons:
            recommendations.append("Add more cache nodes or increase memory per node")
        
        if "high_response_time" in reasons:
            recommendations.append("Add more cache nodes or optimize network topology")
        
        if "high_eviction_rate" in reasons:
            recommendations.append("Increase cache size or optimize cache eviction policy")
        
        return recommendations
    
    async def _execute_scaling_action(self, action: Dict[str, Any]):
        """Execute cache scaling action."""
        reasons = action["reasons"]
        
        if "low_hit_rate" in reasons or "high_memory_usage" in reasons:
            await self._add_cache_node()
        
        if "high_response_time" in reasons:
            await self._optimize_network_topology()
        
        if "high_eviction_rate" in reasons:
            await self._optimize_eviction_policy()
    
    async def _add_cache_node(self):
        """Add a new cache node."""
        new_node = f"cache_node_{len(self.nodes) + 1}"
        self.nodes.append(new_node)
        
        # Rebuild consistent hashing ring
        self._build_consistent_hash_ring()
        
        self.logger.info(f"Added cache node: {new_node}")
    
    async def _optimize_network_topology(self):
        """Optimize network topology."""
        self.logger.info("Optimizing network topology")
        # This would involve:
        # 1. Analyzing network latency between nodes
        # 2. Reorganizing nodes for better performance
        # 3. Adjusting replication factors
    
    async def _optimize_eviction_policy(self):
        """Optimize cache eviction policy."""
        self.logger.info("Optimizing cache eviction policy")
        # This would involve:
        # 1. Analyzing access patterns
        # 2. Adjusting eviction thresholds
        # 3. Implementing more sophisticated eviction policies
    
    def get_cache_metrics(self, hours: int = 24) -> List[CacheMetrics]:
        """Get cache metrics for specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            metrics for metrics in self.metrics_history
            if metrics.timestamp >= cutoff_time
        ]
    
    def get_scaling_actions(self) -> List[Dict[str, Any]]:
        """Get scaling actions history."""
        return self.scaling_actions.copy()


class CacheTiering:
    """Cache tiering implementation."""
    
    def __init__(self):
        """Initialize cache tiering."""
        self.l1_cache = {}  # Fast, small cache (e.g., Redis)
        self.l2_cache = {}  # Slower, larger cache (e.g., Memcached)
        self.l3_cache = {}  # Slowest, largest cache (e.g., Database)
        
        self.logger = get_logger("cache_tiering")
        
        logger.info("Cache tiering initialized")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with tiering."""
        # Try L1 cache first
        if key in self.l1_cache:
            value = self.l1_cache[key]
            # Promote to L1 if accessed frequently
            if self._should_promote(key):
                await self._promote_to_l1(key, value)
            return value
        
        # Try L2 cache
        if key in self.l2_cache:
            value = self.l2_cache[key]
            # Promote to L1
            await self._promote_to_l1(key, value)
            return value
        
        # Try L3 cache
        if key in self.l3_cache:
            value = self.l3_cache[key]
            # Promote to L2
            await self._promote_to_l2(key, value)
            return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with tiering."""
        # Always set in L1
        self.l1_cache[key] = value
        
        # Set in L2 if value is large or frequently accessed
        if self._should_store_in_l2(key, value):
            self.l2_cache[key] = value
        
        # Set in L3 if value is very large
        if self._should_store_in_l3(key, value):
            self.l3_cache[key] = value
    
    def _should_promote(self, key: str) -> bool:
        """Check if key should be promoted to L1."""
        # This would track access frequency
        return hash(key) % 10 == 0  # Simulate promotion
    
    def _should_store_in_l2(self, key: str, value: Any) -> bool:
        """Check if value should be stored in L2."""
        # This would check size and access patterns
        return len(str(value)) > 1000  # Store large values in L2
    
    def _should_store_in_l3(self, key: str, value: Any) -> bool:
        """Check if value should be stored in L3."""
        # This would check size and access patterns
        return len(str(value)) > 10000  # Store very large values in L3
    
    async def _promote_to_l1(self, key: str, value: Any):
        """Promote value to L1 cache."""
        self.l1_cache[key] = value
        self.logger.debug(f"Promoted {key} to L1 cache")
    
    async def _promote_to_l2(self, key: str, value: Any):
        """Promote value to L2 cache."""
        self.l2_cache[key] = value
        self.logger.debug(f"Promoted {key} to L2 cache")
    
    def cleanup(self):
        """Clean up cache tiers."""
        # Remove expired items
        current_time = time.time()
        
        # L1 cleanup
        self.l1_cache = {
            k: v for k, v in self.l1_cache.items()
            if current_time - v.get("timestamp", 0) < 3600  # 1 hour TTL
        }
        
        # L2 cleanup
        self.l2_cache = {
            k: v for k, v in self.l2_cache.items()
            if current_time - v.get("timestamp", 0) < 86400  # 24 hour TTL
        }
        
        # L3 cleanup
        self.l3_cache = {
            k: v for k, v in self.l3_cache.items()
            if current_time - v.get("timestamp", 0) < 604800  # 7 day TTL
        }
        
        self.logger.info("Cache cleanup completed")


# Example usage
async def example_usage():
    """Example usage of caching scaling."""
    # Create distributed cache
    cache = DistributedCache(
        nodes=["cache1.example.com", "cache2.example.com"],
        replication_factor=2
    )
    
    # Check cache health
    metrics = await cache.check_cache_health()
    print("Cache metrics:", metrics.to_dict())
    
    # Check scaling needs
    await cache.check_scaling_needs()
    
    # Get scaling actions
    actions = cache.get_scaling_actions()
    print("Scaling actions:", actions)
    
    # Create cache tiering
    tiering = CacheTiering()
    
    # Set values
    await tiering.set("small_key", "small_value")
    await tiering.set("medium_key", "medium_value" * 100)
    await tiering.set("large_key", "large_value" * 10000)
    
    # Get values
    small_value = await tiering.get("small_key")
    medium_value = await tiering.get("medium_key")
    large_value = await tiering.get("large_key")
    
    print("Small value:", small_value)
    print("Medium value:", medium_value[:100] + "..." if medium_value else None)
    print("Large value:", large_value[:100] + "..." if large_value else None)
    
    # Cleanup cache
    tiering.cleanup()
```

### 5. Auto-scaling

Auto-scaling automatically adjusts resources based on demand.

#### Implementation

```python
# src/libraries_io_mcp/scaling/auto_scaling.py
"""Auto-scaling implementation."""

import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from .logging_config import get_logger

logger = get_logger(__name__)


class ScalingDirection(Enum):
    """Scaling direction enumeration."""
    
    UP = "up"
    DOWN = "down"
    NONE = "none"


@dataclass
class ScalingPolicy:
    """Scaling policy data structure."""
    
    name: str
    metric_name: str
    threshold: float
    direction: ScalingDirection
    cooldown_minutes: int
    min_instances: int
    max_instances: int
    adjustment_type: str  # "change_count", "change_percent", "target_count"
    adjustment_value: float
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "metric_name": self.metric_name,
            "threshold": self.threshold,
            "direction": self.direction.value,
            "cooldown_minutes": self.cooldown_minutes,
            "min_instances": self.min_instances,
            "max_instances": self.max_instances,
            "adjustment_type": self.adjustment_type,
            "adjustment_value": self.adjustment_value,
            "enabled": self.enabled
        }


@dataclass
class MetricData:
    """Metric data structure."""
    
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }


class AutoScaler:
    """Auto-scaling manager."""
    
    def __init__(
        self,
        min_instances: int = 2,
        max_instances: int = 10,
        check_interval: int = 60,
        cloud_provider: Optional[str] = None
    ):
        """Initialize auto-scaler."""
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.check_interval = check_interval
        self.cloud_provider = cloud_provider
        
        self.policies: List[ScalingPolicy] = []
        self.metrics_history: List[MetricData] = []
        self.scaling_actions: List[Dict[str, Any]] = []
        self.current_instance_count = min_instances
        
        self.last_scaling_action = None
        self.scaling_lock = asyncio.Lock()
        
        self.logger = get_logger("auto_scaler")
        
        logger.info(
            "Auto-scaler initialized",
            extra={
                "min_instances": min_instances,
                "max_instances": max_instances,
                "check_interval": check_interval
            }
        )
    
    def add_policy(self, policy: ScalingPolicy):
        """Add scaling policy."""
        self.policies.append(policy)
        self.logger.info(f"Added scaling policy: {policy.name}")
    
    def remove_policy(self, policy_name: str):
        """Remove scaling policy."""
        self.policies = [p for p in self.policies if p.name != policy_name]
        self.logger.info(f"Removed scaling policy: {policy_name}")
    
    async def collect_metrics(self):
        """Collect metrics for scaling decisions."""
        # This would collect metrics from various sources
        # For now, we'll simulate it
        
        metrics = [
            MetricData(
                name="cpu_usage",
                value=75.0,
                timestamp=datetime.now(),
                tags={"service": "libraries-io-mcp"}
            ),
            MetricData(
                name="memory_usage",
                value=80.0,
                timestamp=datetime.now(),
                tags={"service": "libraries-io-mcp"}
            ),
            MetricData(
                name="request_count",
                value=1000.0,
                timestamp=datetime.now(),
                tags={"service": "libraries-io-mcp"}
            ),
            MetricData(
                name="response_time",
                value=0.5,
                timestamp=datetime.now(),
                tags={"service": "libraries-io-mcp"}
            )
        ]
        
        # Store metrics
        self.metrics_history.extend(metrics)
        
        # Keep only recent metrics
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return metrics
    
    async def check_scaling_needs(self):
        """Check if scaling is needed."""
        async with self.scaling_lock:
            # Collect metrics
            metrics = await self.collect_metrics()
            
            # Check each policy
            for policy in self.policies:
                if not policy.enabled:
                    continue
                
                # Get relevant metric
                metric = next(
                    (m for m in metrics if m.name == policy.metric_name),
                    None
                )
                
                if not metric:
                    continue
                
                # Check if scaling is needed
                needs_scaling = False
                scaling_direction = ScalingDirection.NONE
                
                if policy.direction == ScalingDirection.UP and metric.value > policy.threshold:
                    needs_scaling = True
                    scaling_direction = ScalingDirection.UP
                elif policy.direction == ScalingDirection.DOWN and metric.value < policy.threshold:
                    needs_scaling = True
                    scaling_direction = ScalingDirection.DOWN
                
                if needs_scaling:
                    # Check cooldown
                    if self._is_in_cooldown(policy):
                        self.logger.debug(f"Policy {policy.name} in cooldown, skipping")
                        continue
                    
                    # Execute scaling
                    await self._execute_scaling(policy, metric, scaling_direction)
    
    def _is_in_cooldown(self, policy: ScalingPolicy) -> bool:
        """Check if policy is in cooldown."""
        if not self.last_scaling_action:
            return False
        
        cooldown_time = datetime.now() - self.last_scaling_action
        return cooldown_time < timedelta(minutes=policy.cooldown_minutes)
    
    async def _execute_scaling(
        self,
        policy: ScalingPolicy,
        metric: MetricData,
        direction: ScalingDirection
    ):
        """Execute scaling action."""
        # Calculate new instance count
        new_count = self._calculate_new_instance_count(policy, direction)
        
        # Ensure within bounds
        new_count = max(policy.min_instances, min(policy.max_instances, new_count))
        
        # Only scale if there's a significant change
        if abs(new_count - self.current_instance_count) < 1:
            self.logger.debug(f"No significant scaling change needed: {self.current_instance_count} -> {new_count}")
            return
        
        # Execute scaling
        if direction == ScalingDirection.UP:
            await self._scale_up(new_count)
        else:
            await self._scale_down(new_count)
        
        # Record scaling action
        action = {
            "timestamp": datetime.now(),
            "policy": policy.name,
            "metric": metric.name,
            "metric_value": metric.value,
            "direction": direction.value,
            "from_count": self.current_instance_count,
            "to_count": new_count,
            "reason": f"{metric.name} {direction.value} threshold: {policy.threshold}"
        }
        
        self.scaling_actions.append(action)
        self.last_scaling_action = datetime.now()
        
        self.logger.info(
            f"Scaling executed: {self.current_instance_count} -> {new_count} "
            f"(policy: {policy.name}, metric: {metric.name})"
        )
    
    def _calculate_new_instance_count(
        self,
        policy: ScalingPolicy,
        direction: ScalingDirection
    ) -> int:
        """Calculate new instance count based on policy."""
        if policy.adjustment_type == "change_count":
            change = int(policy.adjustment_value)
            if direction == ScalingDirection.UP:
                return self.current_instance_count + change
            else:
                return self.current_instance_count - change
        
        elif policy.adjustment_type == "change_percent":
            change_percent = policy.adjustment_value / 100
            if direction == ScalingDirection.UP:
                new_count = int(self.current_instance_count * (1 + change_percent))
            else:
                new_count = int(self.current_instance_count * (1 - change_percent))
            return max(1, new_count)
        
        elif policy.adjustment_type == "target_count":
            return int(policy.adjustment_value)
        
        else:
            return self.current_instance_count
    
    async def _scale_up(self, new_count: int):
        """Scale up to new instance count."""
        if new_count <= self.current_instance_count:
            return
        
        # Add new instances
        for i in range(self.current_instance_count, new_count):
            await self._add_instance(i + 1)
        
        self.current_instance_count = new_count
        self.logger.info(f"Scaled up to {new_count} instances")
    
    async def _scale_down(self, new_count: int):
        """Scale down to new instance count."""
        if new_count >= self.current_instance_count:
            return
        
        # Remove instances (starting with the least loaded)
        for i in range(self.current_instance_count - 1, new_count - 1, -1):
            await self._remove_instance(i + 1)
        
        self.current_instance_count = new_count
        self.logger.info(f"Scaled down to {new_count} instances")
    
    async def _add_instance(self, instance_id: int):
        """Add a new instance."""
        # This would be implemented based on your cloud provider
        self.logger.info(f"Adding instance: {instance_id}")
        
        # Example: Create cloud instance
        # await self.cloud_provider.create_instance(f"instance-{instance_id}")
        
        # Wait for instance to be ready
        await asyncio.sleep(30)  # Simulate instance startup time
    
    async def _remove_instance(self, instance_id: int):
        """Remove an instance."""
        # This would be implemented based on your cloud provider
        self.logger.info(f"Removing instance: {instance_id}")
        
        # Drain instance connections
        await self._drain_instance(instance_id)
        
        # Example: Terminate cloud instance
        # await self.cloud_provider.terminate_instance(f"instance-{instance_id}")
    
    async def _drain_instance(self, instance_id: int):
        """Drain instance connections."""
        self.logger.info(f"Draining instance: {instance_id}")
        
        # This would involve:
        # 1. Stop accepting new connections
        # 2. Wait for existing connections to complete
        # 3. Update load balancer to remove instance
        
        # Simulate draining
        await asyncio.sleep(60)  # Simulate draining time
    
    def get_scaling_policies(self) -> List[Dict[str, Any]]:
        """Get scaling policies."""
        return [policy.to_dict() for policy in self.policies]
    
    def get_scaling_actions(self) -> List[Dict[str, Any]]:
        """Get scaling actions history."""
        return self.scaling_actions.copy()
    
    def get_current_instance_count(self) -> int:
        """Get current instance count."""
        return self.current_instance_count


# Example usage
async def example_usage():
    """Example usage of auto-scaling."""
    # Create auto-scaler
    scaler = AutoScaler(
        min_instances=2,
        max_instances=10,
        check_interval=30
    )
    
    # Add scaling policies
    scaler.add_policy(ScalingPolicy(
        name="cpu_scaling",
        metric_name="cpu_usage",
        threshold=80.0,
        direction=ScalingDirection.UP,
        cooldown_minutes=5,
        min_instances=2,
        max_instances=10,
        adjustment_type="change_count",
        adjustment_value=1
    ))
    
    scaler.add_policy(ScalingPolicy(
        name="memory_scaling",
        metric_name="memory_usage",
        threshold=85.0,
        direction=ScalingDirection.UP,
        cooldown_minutes=10,
        min_instances=2,
        max_instances=10,
        adjustment_type="change_percent",
        adjustment_value=50  # 50%
    ))
    
    scaler.add_policy(ScalingPolicy(
        name="request_scaling",
        metric_name="request_count",
        threshold=500.0,
        direction=ScalingDirection.DOWN,
        cooldown_minutes=15,
        min_instances=2,
        max_instances=10,
        adjustment_type="target_count",
        adjustment_value=2
    ))
    
    # Start scaling checks
    check_task = asyncio.create_task(scaler.check_scaling_needs())
    
    # Let it run for a while
    await asyncio.sleep(120)
    
    # Get scaling policies
    policies = scaler.get_scaling_policies()
    print("Scaling policies:", policies)
    
    # Get scaling actions
    actions = scaler.get_scaling_actions()
    print("Scaling actions:", actions)
    
    # Get current instance count
    current_count = scaler.get_current_instance_count()
    print(f"Current instance count: {current_count}")
    
    # Stop scaling checks
    check_task.cancel()
    try:
        await check_task
    except asyncio.CancelledError:
        pass
```

## Scaling Best Practices

### 1. Monitoring and Alerting

- **Monitor key metrics**: CPU, memory, disk, network, response times
- **Set appropriate thresholds**: Based on your application's requirements
- **Implement alerts**: For critical scaling events
- **Track scaling effectiveness**: Measure the impact of scaling actions

### 2. Gradual Scaling

- **Use cooldown periods**: Prevent rapid scaling oscillations
- **Scale in increments**: Rather than jumping between extremes
- **Monitor after scaling**: Ensure scaling actions are effective
- **Roll back if needed**: Have rollback mechanisms for failed scaling

### 3. Cost Optimization

- **Right-size resources**: Use appropriate instance types
- **Use spot instances**: For fault-tolerant workloads
- **Schedule scaling**: For predictable workloads
- **Monitor costs**: Track scaling-related expenses

### 4. Reliability

- **Implement health checks**: Ensure only healthy instances receive traffic
- **Use multiple availability zones**: For fault tolerance
- **Plan for failures**: Have backup scaling strategies
- **Test scaling**: Regularly test scaling under various conditions

### 5. Security

- **Secure communication**: Use TLS for inter-node communication
- **Implement access controls**: Restrict scaling operations
- **Monitor for anomalies**: Detect unusual scaling patterns
- **Regular audits**: Review scaling policies and actions

## Conclusion

Scaling the Libraries.io MCP Server requires a comprehensive approach that addresses multiple dimensions of the system. By implementing vertical scaling, horizontal scaling, database scaling, caching scaling, and auto-scaling strategies, you can ensure your system remains performant and reliable as usage grows.

### Key Takeaways

1. **Vertical Scaling**: Good for temporary increases, but has physical limits
2. **Horizontal Scaling**: More scalable, but requires load balancing and state management
3. **Database Scaling**: Critical for handling large datasets and complex queries
4. **Caching Scaling**: Essential for reducing load on databases and improving response times
5. **Auto-scaling**: Automatically adjusts resources based on demand

### Implementation Priority

1. **High Priority**: Basic monitoring, horizontal scaling, database optimization
2. **Medium Priority**: Caching scaling, auto-scaling policies
3. **Low Priority**: Advanced scaling strategies, complex sharding

### Resources

- [AWS Auto Scaling Documentation](https://docs.aws.amazon.com/autoscaling/)
- [Kubernetes Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Redis Clustering](https://redis.io/docs/manual/scaling/)
- [Database Sharding](https://www.mongodb.com/docs/manual/sharding/)
- [Consistent Hashing](https://en.wikipedia.org/wiki/Consistent_hashing)

By following these scaling strategies and best practices, you can ensure the Libraries.io MCP Server scales effectively to meet growing demands while maintaining performance and reliability.
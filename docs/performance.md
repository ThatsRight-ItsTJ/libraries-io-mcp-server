    result2 = await queue.get_task_result(task2)
    
    print(f"Task 1 result: {result1}")
    print(f"Task 2 result: {result2}")
    
    # Stop queue
    await queue.stop()


class BackgroundTaskManager:
    """Manager for background tasks."""
    
    def __init__(self, task_queue: TaskQueue):
        """Initialize background task manager."""
        self.task_queue = task_queue
        self.background_tasks = {}
        self.logger = get_logger("background_tasks")
    
    async def schedule_background_task(
        self,
        name: str,
        func: Callable,
        interval: float,
        args: tuple = (),
        kwargs: dict = None,
        max_retries: int = 3
    ) -> str:
        """Schedule a background task to run periodically."""
        kwargs = kwargs or {}
        
        async def background_task():
            """Background task wrapper."""
            while True:
                try:
                    await func(*args, **kwargs)
                    await asyncio.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Background task {name} failed: {e}")
                    await asyncio.sleep(interval)
        
        # Create task
        task_id = await self.task_queue.add_task(
            name=name,
            func=background_task,
            max_retries=max_retries,
            priority=1  # Low priority for background tasks
        )
        
        self.background_tasks[name] = task_id
        self.logger.info(f"Scheduled background task: {name}")
        
        return task_id
    
    async def stop_background_task(self, name: str) -> bool:
        """Stop a background task."""
        if name not in self.background_tasks:
            return False
        
        task_id = self.background_tasks[name]
        success = await self.task_queue.cancel_task(task_id)
        
        if success:
            del self.background_tasks[name]
            self.logger.info(f"Stopped background task: {name}")
        
        return success
    
    async def get_background_tasks(self) -> Dict[str, str]:
        """Get all background tasks."""
        return self.background_tasks.copy()
```

### 5. Memory Optimization

#### Memory Management

```python
# src/libraries_io_mcp/optimization/memory.py
"""Memory optimization strategies."""

import gc
import psutil
import tracemalloc
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import weakref

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class MemorySnapshot:
    """Memory snapshot data structure."""
    
    timestamp: datetime
    current_usage: int
    peak_usage: int
    objects_count: int
    top_objects: List[Dict[str, Any]] = field(default_factory=list)


class MemoryOptimizer:
    """Memory optimizer for managing memory usage."""
    
    def __init__(self, max_memory_mb: int = 500, snapshot_interval: int = 60):
        """Initialize memory optimizer."""
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.snapshot_interval = snapshot_interval
        self.snapshots: List[MemorySnapshot] = []
        self.large_objects: Set[weakref.ref] = set()
        self.object_tracking: Dict[str, Any] = {}
        
        # Start memory tracing
        tracemalloc.start()
        
        logger.info(
            "Memory optimizer initialized",
            extra={
                "max_memory_mb": max_memory_mb,
                "snapshot_interval": snapshot_interval
            }
        )
    
    def track_object(self, name: str, obj: Any):
        """Track an object for memory optimization."""
        self.object_tracking[name] = obj
        
        # Track large objects
        if isinstance(obj, (list, dict, set)):
            size = len(obj)
            if size > 1000:  # Track objects with more than 1000 items
                ref = weakref.ref(obj, self._on_object_deleted)
                self.large_objects.add(ref)
                logger.debug(f"Tracking large object: {name} (size: {size})")
    
    def _on_object_deleted(self, ref: weakref.ref):
        """Callback when tracked object is deleted."""
        self.large_objects.discard(ref)
        logger.debug("Large object garbage collected")
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss": memory_info.rss,  # Resident Set Size
            "vms": memory_info.vms,  # Virtual Memory Size
            "percent": process.memory_percent(),
            "available": psutil.virtual_memory().available,
            "total": psutil.virtual_memory().total
        }
    
    def take_snapshot(self) -> MemorySnapshot:
        """Take a memory snapshot."""
        current, peak = tracemalloc.get_traced_memory()
        
        # Get top memory consuming objects
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        top_objects = []
        for stat in top_stats[:10]:  # Top 10 memory consumers
            top_objects.append({
                "file": stat.traceback.format()[-2] if stat.traceback else "unknown",
                "line": stat.traceback.format()[-1].strip() if stat.traceback else "unknown",
                "size": stat.size,
                "count": stat.count
            })
        
        snapshot = MemorySnapshot(
            timestamp=datetime.now(),
            current_usage=current,
            peak_usage=peak,
            objects_count=len(self.object_tracking),
            top_objects=top_objects
        )
        
        self.snapshots.append(snapshot)
        
        # Keep only recent snapshots
        if len(self.snapshots) > 100:
            self.snapshots = self.snapshots[-100:]
        
        logger.debug(
            f"Memory snapshot taken: {current / 1024 / 1024:.2f}MB peak: {peak / 1024 / 1024:.2f}MB"
        )
        
        return snapshot
    
    async def optimize_memory(self):
        """Optimize memory usage."""
        logger.info("Starting memory optimization")
        
        # Take snapshot before optimization
        before_snapshot = self.take_snapshot()
        
        # Force garbage collection
        collected = gc.collect()
        logger.info(f"Garbage collection: {collected} objects collected")
        
        # Clear large object caches if memory is high
        memory_usage = self.get_memory_usage()
        if memory_usage["rss"] > self.max_memory_bytes * 0.8:  # 80% of max memory
            logger.warning("High memory usage detected, clearing caches")
            
            # Clear object tracking
            self.object_tracking.clear()
            
            # Clear large objects
            self.large_objects.clear()
            
            # Force garbage collection again
            collected = gc.collect()
            logger.info(f"Garbage collection after cleanup: {collected} objects collected")
        
        # Take snapshot after optimization
        after_snapshot = self.take_snapshot()
        
        # Log optimization results
        memory_freed = before_snapshot.current_usage - after_snapshot.current_usage
        logger.info(
            f"Memory optimization completed: {memory_freed / 1024 / 1024:.2f}MB freed"
        )
        
        return {
            "before": {
                "memory_mb": before_snapshot.current_usage / 1024 / 1024,
                "peak_mb": before_snapshot.peak_usage / 1024 / 1024,
                "objects": before_snapshot.objects_count
            },
            "after": {
                "memory_mb": after_snapshot.current_usage / 1024 / 1024,
                "peak_mb": after_snapshot.peak_usage / 1024 / 1024,
                "objects": after_snapshot.objects_count
            },
            "freed_mb": memory_freed / 1024 / 1024
        }
    
    def get_memory_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Get memory usage trend."""
        if not self.snapshots:
            return {"trend": "unknown", "snapshots": []}
        
        # Filter snapshots by time range
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_snapshots = [
            s for s in self.snapshots
            if s.timestamp >= cutoff_time
        ]
        
        if not recent_snapshots:
            return {"trend": "unknown", "snapshots": []}
        
        # Calculate trend
        first_usage = recent_snapshots[0].current_usage
        last_usage = recent_snapshots[-1].current_usage
        
        if last_usage > first_usage * 1.1:  # 10% increase
            trend = "increasing"
        elif last_usage < first_usage * 0.9:  # 10% decrease
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "snapshots": [
                {
                    "timestamp": s.timestamp.isoformat(),
                    "memory_mb": s.current_usage / 1024 / 1024,
                    "peak_mb": s.peak_usage / 1024 / 1024
                }
                for s in recent_snapshots
            ]
        }
    
    def get_memory_recommendations(self) -> List[str]:
        """Get memory optimization recommendations."""
        recommendations = []
        
        memory_usage = self.get_memory_usage()
        
        # Check memory usage
        if memory_usage["percent"] > 80:
            recommendations.append("High memory usage detected. Consider increasing available memory or optimizing memory usage.")
        
        # Check for memory leaks
        if len(self.snapshots) >= 2:
            recent_snapshots = self.snapshots[-5:]  # Last 5 snapshots
            memory_increase = (
                recent_snapshots[-1].current_usage - recent_snapshots[0].current_usage
            )
            
            if memory_increase > 100 * 1024 * 1024:  # 100MB increase
                recommendations.append("Memory usage is increasing rapidly. Possible memory leak detected.")
        
        # Check large objects
        if len(self.large_objects) > 10:
            recommendations.append(f"Too many large objects tracked ({len(self.large_objects)}). Consider optimizing data structures.")
        
        # Check garbage collection
        if gc.garbage:
            recommendations.append(f"Uncollectable garbage detected: {len(gc.garbage)} objects")
        
        return recommendations
    
    async def start_monitoring(self):
        """Start memory monitoring."""
        logger.info("Starting memory monitoring")
        
        while True:
            try:
                # Take snapshot
                snapshot = self.take_snapshot()
                
                # Check memory usage
                memory_usage = self.get_memory_usage()
                
                if memory_usage["rss"] > self.max_memory_bytes:
                    logger.warning(
                        f"Memory usage exceeded limit: {memory_usage['rss'] / 1024 / 1024:.2f}MB > {self.max_memory_bytes / 1024 / 1024:.2f}MB"
                    )
                    
                    # Optimize memory
                    await self.optimize_memory()
                
                # Wait for next interval
                await asyncio.sleep(self.snapshot_interval)
                
            except asyncio.CancelledError:
                logger.info("Memory monitoring stopped")
                break
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                await asyncio.sleep(self.snapshot_interval)
    
    def stop_monitoring(self):
        """Stop memory monitoring."""
        tracemalloc.stop()
        logger.info("Memory monitoring stopped")


class DataStructureOptimizer:
    """Optimizer for data structures."""
    
    @staticmethod
    def optimize_list(data: List[Any]) -> List[Any]:
        """Optimize list memory usage."""
        if not data:
            return data
        
        # Check if list can be converted to tuple (immutable)
        if all(isinstance(x, (int, float, str, bool)) for x in data):
            return list(data)  # Keep as list for mutability
        
        # Check for duplicates
        if len(data) != len(set(data)):
            logger.debug("List contains duplicates, consider using set if order doesn't matter")
        
        return data
    
    @staticmethod
    def optimize_dict(data: Dict[Any, Any]) -> Dict[Any, Any]:
        """Optimize dictionary memory usage."""
        if not data:
            return data
        
        # Check if keys can be interned
        keys = list(data.keys())
        if all(isinstance(k, str) for k in keys):
            interned_keys = [sys.intern(k) for k in keys]
            if len(interned_keys) != len(set(interned_keys)):
                data = {sys.intern(k): data[k] for k in data.keys()}
                logger.debug("Dictionary keys interned for memory optimization")
        
        return data
    
    @staticmethod
    def optimize_set(data: Set[Any]) -> Set[Any]:
        """Optimize set memory usage."""
        if not data:
            return data
        
        # Check if elements can be interned
        if all(isinstance(x, str) for x in data):
            interned_elements = {sys.intern(x) for x in data}
            if len(interned_elements) != len(data):
                data = interned_elements
                logger.debug("Set elements interned for memory optimization")
        
        return data


# Example usage
async def example_usage():
    """Example usage of memory optimization."""
    # Create memory optimizer
    optimizer = MemoryOptimizer(max_memory_mb=100, snapshot_interval=30)
    
    # Track some objects
    large_list = list(range(10000))
    large_dict = {f"key_{i}": f"value_{i}" for i in range(5000)}
    
    optimizer.track_object("large_list", large_list)
    optimizer.track_object("large_dict", large_dict)
    
    # Take snapshot
    snapshot = optimizer.take_snapshot()
    print(f"Memory usage: {snapshot.current_usage / 1024 / 1024:.2f}MB")
    
    # Get recommendations
    recommendations = optimizer.get_memory_recommendations()
    print("Recommendations:", recommendations)
    
    # Optimize memory
    result = await optimizer.optimize_memory()
    print("Optimization result:", result)
    
    # Get memory trend
    trend = optimizer.get_memory_trend(hours=1)
    print("Memory trend:", trend)
```

### 6. Network Optimization

#### HTTP Client Optimization

```python
# src/libraries_io_mcp/optimization/network.py
"""Network optimization strategies."""

import asyncio
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import aiohttp
from urllib.parse import urlparse

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class RequestStats:
    """Request statistics."""
    
    url: str
    method: str
    status_code: int
    duration: float
    size: int
    timestamp: datetime
    cache_hit: bool = False
    retry_count: int = 0


class NetworkOptimizer:
    """Network optimizer for HTTP requests."""
    
    def __init__(
        self,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 30.0,
        max_retries: int = 3,
        timeout: float = 30.0
    ):
        """Initialize network optimizer."""
        self.max_connections = max_connections
        self.max_keepalive_connections = max_keepalive_connections
        self.keepalive_expiry = keepalive_expiry
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Connection pool
        self.connector = aiohttp.TCPConnector(
            limit=max_connections,
            limit_per_host=max_keepalive_connections,
            ttl_dns_cache=300,
            ttl_dns_cache_per_host=300,
            use_dns_cache=True,
            keepalive_timeout=keepalive_expiry,
            enable_cleanup_closed=True
        )
        
        # Session
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=aiohttp.ClientTimeout(total=timeout),
            headers={
                "User-Agent": "LibrariesIO-MCP-Server/1.0",
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive"
            }
        )
        
        # Request tracking
        self.request_stats: List[RequestStats] = []
        self.active_requests = 0
        self.lock = asyncio.Lock()
        
        logger.info(
            "Network optimizer initialized",
            extra={
                "max_connections": max_connections,
                "max_keepalive_connections": max_keepalive_connections,
                "keepalive_expiry": keepalive_expiry,
                "max_retries": max_retries,
                "timeout": timeout
            }
        )
    
    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cache_key: Optional[str] = None,
        cache_ttl: Optional[int] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with optimization."""
        start_time = time.time()
        
        # Check cache
        if cache_key and cache_ttl:
            cached_response = await self._get_cached_response(cache_key)
            if cached_response and (time.time() - cached_response["timestamp"]) < cache_ttl:
                logger.debug(f"Request cache hit: {cache_key}")
                return cached_response["data"]
        
        # Make request with retries
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=headers
                ) as response:
                    response.raise_for_status()
                    
                    # Parse JSON response
                    data = await response.json()
                    
                    # Cache response
                    if cache_key and cache_ttl:
                        await self._cache_response(cache_key, data, cache_ttl)
                    
                    # Record stats
                    duration = time.time() - start_time
                    size = len(str(data))
                    
                    async with self.lock:
                        stats = RequestStats(
                            url=url,
                            method=method,
                            status_code=response.status,
                            duration=duration,
                            size=size,
                            timestamp=datetime.now(),
                            cache_hit=False,
                            retry_count=attempt
                        )
                        self.request_stats.append(stats)
                        self.active_requests += 1
                    
                    logger.debug(
                        f"Request successful: {method} {url} ({duration:.3f}s, {size} bytes)"
                    )
                    
                    return data
                    
            except aiohttp.ClientError as e:
                last_error = e
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}. Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {self.max_retries + 1} attempts: {e}")
                    raise
            except Exception as e:
                last_error = e
                logger.error(f"Request failed: {e}")
                raise
        
        # This should never be reached, but just in case
        raise last_error or Exception("Unknown request error")
    
    async def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response."""
        # This would normally use a cache backend
        # For now, we'll just return None
        return None
    
    async def _cache_response(self, cache_key: str, data: Dict[str, Any], ttl: int):
        """Cache response."""
        # This would normally use a cache backend
        # For now, we'll just log it
        logger.debug(f"Caching response: {cache_key} (TTL: {ttl}s)")
    
    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        return await self.request("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        return await self.request("POST", url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make PUT request."""
        return await self.request("PUT", url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        return await self.request("DELETE", url, **kwargs)
    
    def get_request_stats(self) -> Dict[str, Any]:
        """Get request statistics."""
        if not self.request_stats:
            return {"total_requests": 0, "avg_duration": 0}
        
        total_requests = len(self.request_stats)
        total_duration = sum(s.duration for s in self.request_stats)
        avg_duration = total_duration / total_requests
        
        # Calculate success rate
        successful_requests = sum(1 for s in self.request_stats if 200 <= s.status_code < 300)
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        # Find slowest request
        slowest_request = max(self.request_stats, key=lambda s: s.duration)
        
        # Find most requested URL
        url_counts = {}
        for stats in self.request_stats:
            url_counts[stats.url] = url_counts.get(stats.url, 0) + 1
        
        most_requested_url = max(url_counts.items(), key=lambda x: x[1]) if url_counts else ("None", 0)
        
        return {
            "total_requests": total_requests,
            "avg_duration": avg_duration,
            "success_rate": success_rate,
            "slowest_request": {
                "url": slowest_request.url,
                "duration": slowest_request.duration,
                "status_code": slowest_request.status_code
            },
            "most_requested_url": {
                "url": most_requested_url[0],
                "count": most_requested_url[1]
            },
            "active_requests": self.active_requests
        }
    
    def get_network_recommendations(self) -> List[str]:
        """Get network optimization recommendations."""
        recommendations = []
        
        if not self.request_stats:
            return recommendations
        
        # Check for slow requests
        slow_requests = [s for s in self.request_stats if s.duration > 5.0]
        if slow_requests:
            recommendations.append(
                f"Found {len(slow_requests)} slow requests (>5s). Consider optimizing or caching these endpoints."
            )
        
        # Check for high error rates
        error_requests = [s for s in self.request_stats if s.status_code >= 400]
        if error_requests:
            error_rate = len(error_requests) / len(self.request_stats)
            if error_rate > 0.1:  # 10% error rate
                recommendations.append(
                    f"High error rate detected ({error_rate:.1%}). Check API endpoints and error handling."
                )
        
        # Check for retry-heavy requests
        retry_heavy_requests = [s for s in self.request_stats if s.retry_count > 2]
        if retry_heavy_requests:
            recommendations.append(
                f"Found {len(retry_heavy_requests)} requests with high retry counts. Check network connectivity and API limits."
            )
        
        return recommendations
    
    async def close(self):
        """Close network optimizer."""
        await self.session.close()
        logger.info("Network optimizer closed")


class RequestBatcher:
    """Request batcher for combining multiple requests."""
    
    def __init__(self, batch_size: int = 10, batch_timeout: float = 0.1):
        """Initialize request batcher."""
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.pending_requests = []
        self.batch_timer = None
        
        logger.info(
            "Request batcher initialized",
            extra={
                "batch_size": batch_size,
                "batch_timeout": batch_timeout
            }
        )
    
    async def add_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        callback: Optional[callable] = None
    ) -> asyncio.Future:
        """Add request to batch."""
        future = asyncio.Future()
        
        request = {
            "method": method,
            "url": url,
            "params": params,
            "callback": callback,
            "future": future
        }
        
        self.pending_requests.append(request)
        
        # Schedule batch processing
        if self.batch_timer is None:
            self.batch_timer = asyncio.create_task(self._process_batch())
        
        return future
    
    async def _process_batch(self):
        """Process batch of requests."""
        await asyncio.sleep(self.batch_timeout)
        
        if not self.pending_requests:
            self.batch_timer = None
            return
        
        batch = self.pending_requests[:self.batch_size]
        self.pending_requests = self.pending_requests[self.batch_size:]
        
        logger.debug(f"Processing batch of {len(batch)} requests")
        
        try:
            # Process requests in parallel
            tasks = []
            for request in batch:
                task = self._execute_request(request)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle results
            for request, result in zip(batch, results):
                if isinstance(result, Exception):
                    request["future"].set_exception(result)
                else:
                    request["future"].set_result(result)
                        
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            
            # Handle failures
            for request in batch:
                request["future"].set_exception(e)
        
        finally:
            self.batch_timer = None
    
    async def _execute_request(self, request: Dict[str, Any]):
        """Execute a single request."""
        try:
            # This would use the network optimizer
            # For now, we'll just return a mock response
            return {"status": "success", "data": {}}
        except Exception as e:
            logger.error(f"Request execution failed: {e}")
            raise
    
    async def flush(self):
        """Flush all pending requests."""
        if self.pending_requests:
            logger.info(f"Flushing {len(self.pending_requests)} pending requests")
            await self._process_batch()


# Example usage
async def example_usage():
    """Example usage of network optimization."""
    # Create network optimizer
    optimizer = NetworkOptimizer(
        max_connections=50,
        max_keepalive_connections=10,
        max_retries=3
    )
    
    # Make requests
    try:
        response1 = await optimizer.get("https://api.libraries.io/api/v1/platforms")
        response2 = await optimizer.get("https://api.libraries.io/api/v1/search", params={"q": "react"})
        
        print("Request 1:", response1)
        print("Request 2:", response2)
        
        # Get stats
        stats = optimizer.get_request_stats()
        print("Request stats:", stats)
        
        # Get recommendations
        recommendations = optimizer.get_network_recommendations()
        print("Recommendations:", recommendations)
        
    finally:
        await optimizer.close()
```

## Performance Monitoring Dashboard

### 1. Dashboard Implementation

```python
# src/libraries_io_mcp/optimization/dashboard.py
"""Performance monitoring dashboard."""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    request_count: int
    avg_response_time: float
    error_rate: float
    active_connections: int
    cache_hit_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class PerformanceDashboard:
    """Performance monitoring dashboard."""
    
    def __init__(self, max_metrics: int = 1000):
        """Initialize performance dashboard."""
        self.max_metrics = max_metrics
        self.metrics: List[PerformanceMetrics] = []
        self.alerts = []
        
        logger.info("Performance dashboard initialized")
    
    def add_metrics(self, metrics: PerformanceMetrics):
        """Add performance metrics."""
        self.metrics.append(metrics)
        
        # Keep only recent metrics
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
        
        # Check for alerts
        self._check_alerts(metrics)
    
    def _check_alerts(self, metrics: PerformanceMetrics):
        """Check for performance alerts."""
        alerts = []
        
        # CPU usage alert
        if metrics.cpu_usage > 80:
            alerts.append({
                "type": "cpu_high",
                "message": f"High CPU usage: {metrics.cpu_usage:.1f}%",
                "severity": "high",
                "timestamp": metrics.timestamp
            })
        
        # Memory usage alert
        if metrics.memory_usage > 85:
            alerts.append({
                "type": "memory_high",
                "message": f"High memory usage: {metrics.memory_usage:.1f}%",
                "severity": "high",
                "timestamp": metrics.timestamp
            })
        
        # Response time alert
        if metrics.avg_response_time > 2.0:
            alerts.append({
                "type": "response_time_high",
                "message": f"High response time: {metrics.avg_response_time:.2f}s",
                "severity": "medium",
                "timestamp": metrics.timestamp
            })
        
        # Error rate alert
        if metrics.error_rate > 0.05:  # 5%
            alerts.append({
                "type": "error_rate_high",
                "message": f"High error rate: {metrics.error_rate:.1%}",
                "severity": "high",
                "timestamp": metrics.timestamp
            })
        
        # Add alerts
        for alert in alerts:
            self.alerts.append(alert)
            logger.warning(f"Performance alert: {alert['message']}")
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current metrics."""
        return self.metrics[-1] if self.metrics else None
    
    def get_metrics_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics trend."""
        if not self.metrics:
            return {"trend": "unknown", "metrics": []}
        
        # Filter metrics by time range
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {"trend": "unknown", "metrics": []}
        
        # Calculate trends
        cpu_trend = self._calculate_trend([m.cpu_usage for m in recent_metrics])
        memory_trend = self._calculate_trend([m.memory_usage for m in recent_metrics])
        response_time_trend = self._calculate_trend([m.avg_response_time for m in recent_metrics])
        error_rate_trend = self._calculate_trend([m.error_rate for m in recent_metrics])
        
        return {
            "trend": "stable",
            "metrics": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "cpu_usage": m.cpu_usage,
                    "memory_usage": m.memory_usage,
                    "request_count": m.request_count,
                    "avg_response_time": m.avg_response_time,
                    "error_rate": m.error_rate,
                    "active_connections": m.active_connections,
                    "cache_hit_rate": m.cache_hit_rate
                }
                for m in recent_metrics
            ],
            "trends": {
                "cpu": cpu_trend,
                "memory": memory_trend,
                "response_time": response_time_trend,
                "error_rate": error_rate_trend
            }
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from values."""
        if len(values) < 2:
            return "stable"
        
        first = values[0]
        last = values[-1]
        
        if last > first * 1.1:  # 10% increase
            return "increasing"
        elif last < first * 0.9:  # 10% decrease
            return "decreasing"
        else:
            return "stable"
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data."""
        current_metrics = self.get_current_metrics()
        
        if not current_metrics:
            return {"status": "no_data"}
        
        return {
            "current_metrics": asdict(current_metrics),
            "metrics_trend": self.get_metrics_trend(hours=1),
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "summary": {
                "total_requests": sum(m.request_count for m in self.metrics),
                "avg_response_time": sum(m.avg_response_time for m in self.metrics) / len(self.metrics),
                "avg_cpu_usage": sum(m.cpu_usage for m in self.metrics) / len(self.metrics),
                "avg_memory_usage": sum(m.memory_usage for m in self.metrics) / len(self.metrics),
                "total_alerts": len(self.alerts)
            }
        }
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get all alerts."""
        return self.alerts.copy()
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts.clear()
        logger.info("Performance alerts cleared")


# Example usage
async def example_usage():
    """Example usage of performance dashboard."""
    # Create dashboard
    dashboard = PerformanceDashboard(max_metrics=100)
    
    # Add some metrics
    for i in range(10):
        metrics = PerformanceMetrics(
            timestamp=datetime.now() - timedelta(minutes=i),
            cpu_usage=50 + i * 2,
            memory_usage=60 + i,
            request_count=100 + i * 10,
            avg_response_time=0.5 + i * 0.1,
            error_rate=0.01 + i * 0.005,
            active_connections=10 + i,
            cache_hit_rate=0.8 + i * 0.01
        )
        dashboard.add_metrics(metrics)
    
    # Get dashboard data
    data = dashboard.get_dashboard_data()
    print("Dashboard data:", json.dumps(data, indent=2))
    
    # Get alerts
    alerts = dashboard.get_alerts()
    print("Alerts:", alerts)
```

## Performance Testing

### 1. Load Testing

```python
# src/libraries_io_mcp/optimization/load_testing.py
"""Load testing utilities."""

import asyncio
import time
import statistics
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import random

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class LoadTestResult:
    """Load test result data structure."""
    
    test_name: str
    start_time: datetime
    end_time: datetime
    duration: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    response_times: List[float]
    errors: List[Dict[str, Any]] = field(default_factory=list)
    throughput: float = 0.0
    avg_response_time: float = 0.0
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    
    def calculate_stats(self):
        """Calculate statistics."""
        if not self.response_times:
            return
        
        self.avg_response_time = statistics.mean(self.response_times)
        self.min_response_time = min(self.response_times)
        self.max_response_time = max(self.response_times)
        self.p95_response_time = statistics.quantiles(self.response_times, n=20)[18]  # 95th percentile
        self.p99_response_time = statistics.quantiles(self.response_times, n=100)[98]  # 99th percentile
        self.throughput = self.total_requests / self.duration if self.duration > 0 else 0


class LoadTester:
    """Load testing utility."""
    
    def __init__(self, name: str):
        """Initialize load tester."""
        self.name = name
        self.logger = get_logger(f"load_test.{name}")
    
    async def run_load_test(
        self,
        test_func: Callable,
        concurrent_users: int,
        duration: int,
        ramp_up: int = 0,
        **kwargs
    ) -> LoadTestResult:
        """Run a load test."""
        start_time = datetime.now()
        self.logger.info(
            f"Starting load test: {concurrent_users} users, {duration}s duration"
        )
        
        # Track results
        response_times = []
        errors = []
        successful_requests = 0
        failed_requests = 0
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrent_users)
        
        # Ramp up users
        if ramp_up > 0:
            ramp_up_delay = ramp_up / concurrent_users
            self.logger.info(f"Ramping up users over {ramp_up}s")
        
        async def user_task(user_id: int):
            """Task for a single user."""
            if ramp_up > 0:
                await asyncio.sleep(random.uniform(0, ramp_up))
            
            async with semaphore:
                try:
                    user_start = time.time()
                    result = await test_func(user_id=user_id, **kwargs)
                    response_time = time.time() - user_start
                    
                    response_times.append(response_time)
                    successful_requests += 1
                    
                    self.logger.debug(
                        f"User {user_id} completed in {response_time:.3f}s"
                    )
                    
                except Exception as e:
                    failed_requests += 1
                    errors.append({
                        "user_id": user_id,
                        "error": str(e),
                        "timestamp": datetime.now()
                    })
                    self.logger.error(f"User {user_id} failed: {e}")
        
        # Create and start user tasks
        tasks = []
        for i in range(concurrent_users):
            task = asyncio.create_task(user_task(i))
            tasks.append(task)
        
        # Wait for test duration
        await asyncio.sleep(duration)
        
        # Cancel remaining tasks
        for task in tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = datetime.now()
        test_duration = (end_time - start_time).total_seconds()
        
        # Create result
        result = LoadTestResult(
            test_name=self.name,
            start_time=start_time,
            end_time=end_time,
            duration=test_duration,
            total_requests=successful_requests + failed_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            response_times=response_times,
            errors=errors
        )
        
        # Calculate statistics
        result.calculate_stats()
        
        # Log results
        self.logger.info(
            f"Load test completed: {result.total_requests} requests, "
            f"{result.successful_requests} successful, "
            f"{result.failed_requests} failed, "
            f"{result.throughput:.2f} req/s, "
            f"avg response time: {result.avg_response_time:.3f}s"
        )
        
        return result
    
    async def run_spike_test(
        self,
        test_func: Callable,
        normal_users: int,
        spike_users: int,
        spike_duration: int,
        total_duration: int,
        **kwargs
    ) -> LoadTestResult:
        """Run a spike test."""
        self.logger.info(
            f"Starting spike test: {normal_users} normal users, "
            f"{spike_users} spike users for {spike_duration}s"
        )
        
        # Start normal load
        normal_task = asyncio.create_task(
            self.run_load_test(
                test_func,
                concurrent_users=normal_users,
                duration=total_duration,
                **kwargs
            )
        )
        
        # Wait for normal load to stabilize
        await asyncio.sleep(10)
        
        # Add spike load
        spike_task = asyncio.create_task(
            self.run_load_test(
                test_func,
                concurrent_users=spike_users,
                duration=spike_duration,
                **kwargs
            )
        )
        
        # Wait for spike to complete
        await spike_task
        
        # Wait for normal load to complete
        result = await normal_task
        
        self.logger.info("Spike test completed")
        return result
    
    async def run_stress_test(
        self,
        test_func: Callable,
        start_users: int,
        max_users: int,
        increment_users: int,
        increment_interval: int,
        max_duration: int,
        **kwargs
    ) -> LoadTestResult:
        """Run a stress test."""
        self.logger.info(
            f"Starting stress test: {start_users} -> {max_users} users, "
            f"{increment_users} users every {increment_interval}s"
        )
        
        start_time = datetime.now()
        response_times = []
        errors = []
        successful_requests = 0
        failed_requests = 0
        
        current_users = start_users
        end_time = start_time + timedelta(seconds=max_duration)
        
        while datetime.now() < end_time and current_users <= max_users:
            # Run load test for current user count
            result = await self.run_load_test(
                test_func,
                concurrent_users=current_users,
                duration=increment_interval,
                **kwargs
            )
            
            # Aggregate results
            response_times.extend(result.response_times)
            errors.extend(result.errors)
            successful_requests += result.successful_requests
            failed_requests += result.failed_requests
            
            # Increment users
            current_users += increment_users
            
            self.logger.info(
                f"Stress test: {current_users - increment_users} -> {current_users} users"
            )
        
        # Create final result
        final_result = LoadTestResult(
            test_name=f"{self.name}_stress",
            start_time=start_time,
            end_time=datetime.now(),
            duration=(datetime.now() - start_time).total_seconds(),
            total_requests=successful_requests + failed_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            response_times=response_times,
            errors=errors
        )
        
        # Calculate statistics
        final_result.calculate_stats()
        
        self.logger.info("Stress test completed")
        return final_result


# Example usage
async def example_usage():
    """Example usage of load testing."""
    # Create load tester
    tester = LoadTester("api_test")
    
    # Define test function
    async def api_test(user_id: int, endpoint: str = "/test"):
        """API test function."""
        await asyncio.sleep(random.uniform(0.1, 0.5))  # Simulate API call
        return {"user_id": user_id, "endpoint": endpoint}
    
    # Run load test
    result = await tester.run_load_test(
        test_func=api_test,
        concurrent_users=10,
        duration=30,
        endpoint="/api/test"
    )
    
    print("Load test result:", result)
    
    # Run spike test
    spike_result = await tester.run_spike_test(
        test_func=api_test,
        normal_users=5,
        spike_users=20,
        spike_duration=10,
        total_duration=60,
        endpoint="/api/spike"
    )
    
    print("Spike test result:", spike_result)
    
    # Run stress test
    stress_result = await tester.run_stress_test(
        test_func=api_test,
        start_users=5,
        max_users=50,
        increment_users=5,
        increment_interval=10,
        max_duration=120,
        endpoint="/api/stress"
    )
    
    print("Stress test result:", stress_result)
```

## Conclusion

This comprehensive performance optimization guide provides detailed strategies and implementations for optimizing the Libraries.io MCP Server. By implementing these techniques, you can ensure your server runs efficiently, handles high loads effectively, and provides responsive service to users.

### Key Takeaways

1. **API Optimization**: Use request batching and connection pooling to reduce overhead
2. **Caching**: Implement multi-level caching with different backends for optimal performance
3. **Database Optimization**: Use connection pooling, query caching, and proper indexing
4. **Asynchronous Processing**: Use task queues for background operations and non-blocking I/O
5. **Memory Management**: Monitor memory usage and optimize data structures
6. **Network Optimization**: Use HTTP connection pooling and request batching
7. **Performance Monitoring**: Implement comprehensive monitoring and alerting
8. **Load Testing**: Regularly test performance under various load conditions

### Implementation Priority

1. **High Priority**: Connection pooling, caching, basic monitoring
2. **Medium Priority**: Request batching, database optimization, memory management
3. **Low Priority**: Advanced monitoring, load testing, stress testing

### Resources

- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [aiohttp Documentation](https://docs.aiohttp.org/)
- [Redis Documentation](https://redis.io/documentation)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [psutil Documentation](https://psutil.readthedocs.io/)

By following these optimization strategies and regularly monitoring performance, you can ensure the Libraries.io MCP Server remains fast, reliable, and scalable as usage grows.
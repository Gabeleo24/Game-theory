"""
Performance Monitoring and Metrics for ADS599 Capstone Soccer Intelligence System
Implements comprehensive monitoring of container resources, processing times, and performance metrics
for optimized data processing workflows.
"""

import time
import psutil
import threading
import logging
import json
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
from contextlib import contextmanager
import pandas as pd
import numpy as np
from collections import defaultdict, deque

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from ..utils.config import Config
from ..utils.logger import get_logger


@dataclass
class SystemMetrics:
    """System resource metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_available_gb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    load_average: List[float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ProcessingMetrics:
    """Processing performance metrics."""
    operation_name: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    memory_before_mb: float
    memory_after_mb: float
    memory_peak_mb: float
    cpu_percent_avg: float
    rows_processed: int
    throughput_rows_per_sec: float
    cache_hits: int
    cache_misses: int
    errors_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        return data


@dataclass
class ContainerMetrics:
    """Docker container metrics."""
    container_name: str
    cpu_percent: float
    memory_usage_mb: float
    memory_limit_mb: float
    memory_percent: float
    network_rx_mb: float
    network_tx_mb: float
    block_read_mb: float
    block_write_mb: float
    pids: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system for soccer intelligence workflows.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the performance monitor."""
        self.config = config or Config()
        self.logger = get_logger(__name__)
        
        # Monitoring configuration
        self.monitoring_config = self.config.get('performance.monitoring', {})
        self.metrics_enabled = self.monitoring_config.get('metrics.enable_timing', True)
        self.memory_tracking = self.monitoring_config.get('metrics.enable_memory_tracking', True)
        self.cpu_tracking = self.monitoring_config.get('metrics.enable_cpu_tracking', True)
        self.io_tracking = self.monitoring_config.get('metrics.enable_io_tracking', True)
        
        # Alert thresholds
        self.alert_config = self.monitoring_config.get('alerts', {})
        self.memory_threshold = self.alert_config.get('memory_threshold', 0.9)
        self.cpu_threshold = self.alert_config.get('cpu_threshold', 0.9)
        self.disk_threshold = self.alert_config.get('disk_threshold', 0.9)
        self.response_time_threshold = self.alert_config.get('response_time_threshold', 30)
        
        # Logging configuration
        self.log_config = self.monitoring_config.get('logging', {})
        self.log_slow_operations = self.log_config.get('log_slow_operations', True)
        self.slow_operation_threshold = self.log_config.get('slow_operation_threshold', 10)
        
        # Data storage
        self.metrics_history = deque(maxlen=1000)  # Keep last 1000 metrics
        self.processing_history = deque(maxlen=500)  # Keep last 500 operations
        self.container_history = deque(maxlen=1000)  # Keep last 1000 container metrics
        
        # Thread safety
        self.metrics_lock = threading.Lock()
        
        # System monitoring
        self.process = psutil.Process()
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_interval = 5  # seconds
        
        # Docker client
        self.docker_client = None
        if DOCKER_AVAILABLE:
            try:
                self.docker_client = docker.from_env()
            except Exception as e:
                self.logger.warning(f"Docker client initialization failed: {e}")
        
        # Redis client for metrics storage
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'redis'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    password=os.getenv('REDIS_PASSWORD', 'redispass123'),
                    db=1  # Use different DB for metrics
                )
                self.redis_client.ping()
            except Exception as e:
                self.logger.warning(f"Redis metrics client initialization failed: {e}")
                self.redis_client = None
        
        self.logger.info("Performance monitor initialized")
    
    def start_monitoring(self) -> None:
        """Start continuous system monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop continuous system monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                
                # Collect container metrics
                container_metrics = self._collect_container_metrics()
                
                # Store metrics
                with self.metrics_lock:
                    self.metrics_history.append(system_metrics)
                    if container_metrics:
                        self.container_history.extend(container_metrics)
                
                # Store in Redis if available
                if self.redis_client:
                    self._store_metrics_in_redis(system_metrics, container_metrics)
                
                # Check for alerts
                self._check_alerts(system_metrics)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_used_gb = memory.used / (1024 ** 3)
        memory_available_gb = memory.available / (1024 ** 3)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_usage_percent = (disk.used / disk.total) * 100
        disk_free_gb = disk.free / (1024 ** 3)
        
        # Network metrics
        network = psutil.net_io_counters()
        
        # Load average
        load_avg = list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0.0, 0.0, 0.0]
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_gb=memory_used_gb,
            memory_available_gb=memory_available_gb,
            disk_usage_percent=disk_usage_percent,
            disk_free_gb=disk_free_gb,
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv,
            load_average=load_avg
        )
    
    def _collect_container_metrics(self) -> List[ContainerMetrics]:
        """Collect Docker container metrics."""
        if not self.docker_client:
            return []
        
        container_metrics = []
        
        try:
            containers = self.docker_client.containers.list()
            
            for container in containers:
                if 'soccer-intelligence' in container.name:
                    stats = container.stats(stream=False)
                    
                    # Calculate CPU percentage
                    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                               stats['precpu_stats']['cpu_usage']['total_usage']
                    system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                                  stats['precpu_stats']['system_cpu_usage']
                    cpu_percent = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
                    
                    # Memory metrics
                    memory_usage = stats['memory_stats']['usage']
                    memory_limit = stats['memory_stats']['limit']
                    memory_percent = (memory_usage / memory_limit) * 100
                    
                    # Network metrics
                    network_rx = sum(net['rx_bytes'] for net in stats['networks'].values()) / (1024 ** 2)
                    network_tx = sum(net['tx_bytes'] for net in stats['networks'].values()) / (1024 ** 2)
                    
                    # Block I/O metrics
                    block_read = stats['blkio_stats']['io_service_bytes_recursive'][0]['value'] / (1024 ** 2) if stats['blkio_stats']['io_service_bytes_recursive'] else 0
                    block_write = stats['blkio_stats']['io_service_bytes_recursive'][1]['value'] / (1024 ** 2) if len(stats['blkio_stats']['io_service_bytes_recursive']) > 1 else 0
                    
                    container_metrics.append(ContainerMetrics(
                        container_name=container.name,
                        cpu_percent=cpu_percent,
                        memory_usage_mb=memory_usage / (1024 ** 2),
                        memory_limit_mb=memory_limit / (1024 ** 2),
                        memory_percent=memory_percent,
                        network_rx_mb=network_rx,
                        network_tx_mb=network_tx,
                        block_read_mb=block_read,
                        block_write_mb=block_write,
                        pids=stats['pids_stats']['current']
                    ))
                    
        except Exception as e:
            self.logger.warning(f"Error collecting container metrics: {e}")
        
        return container_metrics
    
    def _store_metrics_in_redis(self, system_metrics: SystemMetrics, 
                               container_metrics: List[ContainerMetrics]) -> None:
        """Store metrics in Redis for persistence."""
        if not self.redis_client:
            return
        
        try:
            timestamp = int(time.time())
            
            # Store system metrics
            self.redis_client.zadd(
                'system_metrics',
                {json.dumps(system_metrics.to_dict()): timestamp}
            )
            
            # Store container metrics
            for container_metric in container_metrics:
                self.redis_client.zadd(
                    f'container_metrics:{container_metric.container_name}',
                    {json.dumps(container_metric.to_dict()): timestamp}
                )
            
            # Clean old metrics (keep last 24 hours)
            cutoff_time = timestamp - (24 * 60 * 60)
            self.redis_client.zremrangebyscore('system_metrics', 0, cutoff_time)
            
            for container_metric in container_metrics:
                self.redis_client.zremrangebyscore(
                    f'container_metrics:{container_metric.container_name}',
                    0, cutoff_time
                )
                
        except Exception as e:
            self.logger.warning(f"Error storing metrics in Redis: {e}")
    
    def _check_alerts(self, metrics: SystemMetrics) -> None:
        """Check metrics against alert thresholds."""
        alerts = []
        
        if metrics.memory_percent > self.memory_threshold * 100:
            alerts.append(f"High memory usage: {metrics.memory_percent:.1f}%")
        
        if metrics.cpu_percent > self.cpu_threshold * 100:
            alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        
        if metrics.disk_usage_percent > self.disk_threshold * 100:
            alerts.append(f"High disk usage: {metrics.disk_usage_percent:.1f}%")
        
        for alert in alerts:
            self.logger.warning(f"PERFORMANCE ALERT: {alert}")
    
    @contextmanager
    def monitor_operation(self, operation_name: str, rows_count: int = 0):
        """Context manager for monitoring specific operations."""
        start_time = datetime.now()
        memory_before = self.process.memory_info().rss / (1024 ** 2)  # MB
        cpu_times_before = self.process.cpu_times()
        
        # Initialize tracking variables
        memory_peak = memory_before
        cpu_percent_samples = []
        cache_hits = 0
        cache_misses = 0
        errors_count = 0
        
        # Start CPU monitoring thread
        cpu_monitoring_active = True
        
        def cpu_monitor():
            while cpu_monitoring_active:
                try:
                    cpu_percent_samples.append(self.process.cpu_percent())
                    current_memory = self.process.memory_info().rss / (1024 ** 2)
                    nonlocal memory_peak
                    memory_peak = max(memory_peak, current_memory)
                    time.sleep(0.5)
                except:
                    pass
        
        cpu_thread = threading.Thread(target=cpu_monitor, daemon=True)
        cpu_thread.start()
        
        try:
            yield {
                'cache_hits': lambda: cache_hits,
                'cache_misses': lambda: cache_misses,
                'errors': lambda: errors_count,
                'add_cache_hit': lambda: setattr(cache_hits, 'value', getattr(cache_hits, 'value', 0) + 1),
                'add_cache_miss': lambda: setattr(cache_misses, 'value', getattr(cache_misses, 'value', 0) + 1),
                'add_error': lambda: setattr(errors_count, 'value', getattr(errors_count, 'value', 0) + 1)
            }
        except Exception as e:
            errors_count += 1
            raise
        finally:
            cpu_monitoring_active = False
            cpu_thread.join(timeout=1)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            memory_after = self.process.memory_info().rss / (1024 ** 2)  # MB
            
            cpu_percent_avg = np.mean(cpu_percent_samples) if cpu_percent_samples else 0.0
            throughput = rows_count / max(duration, 0.001) if rows_count > 0 else 0.0
            
            # Create processing metrics
            processing_metrics = ProcessingMetrics(
                operation_name=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                memory_before_mb=memory_before,
                memory_after_mb=memory_after,
                memory_peak_mb=memory_peak,
                cpu_percent_avg=cpu_percent_avg,
                rows_processed=rows_count,
                throughput_rows_per_sec=throughput,
                cache_hits=cache_hits,
                cache_misses=cache_misses,
                errors_count=errors_count
            )
            
            # Store metrics
            with self.metrics_lock:
                self.processing_history.append(processing_metrics)
            
            # Log slow operations
            if self.log_slow_operations and duration > self.slow_operation_threshold:
                self.logger.warning(
                    f"Slow operation detected: {operation_name} took {duration:.2f}s "
                    f"(threshold: {self.slow_operation_threshold}s)"
                )
            
            # Store in Redis
            if self.redis_client:
                try:
                    self.redis_client.zadd(
                        'processing_metrics',
                        {json.dumps(processing_metrics.to_dict()): int(time.time())}
                    )
                except Exception as e:
                    self.logger.warning(f"Error storing processing metrics in Redis: {e}")
            
            self.logger.info(
                f"Operation '{operation_name}' completed: {duration:.2f}s, "
                f"{rows_count} rows, {throughput:.0f} rows/s, "
                f"Memory: {memory_before:.1f}MB -> {memory_after:.1f}MB (peak: {memory_peak:.1f}MB)"
            )
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get current system performance summary."""
        current_metrics = self._collect_system_metrics()
        
        # Calculate averages from recent history
        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 measurements
        
        if recent_metrics:
            avg_cpu = np.mean([m.cpu_percent for m in recent_metrics])
            avg_memory = np.mean([m.memory_percent for m in recent_metrics])
        else:
            avg_cpu = current_metrics.cpu_percent
            avg_memory = current_metrics.memory_percent
        
        return {
            'current': current_metrics.to_dict(),
            'averages': {
                'cpu_percent_avg_10min': avg_cpu,
                'memory_percent_avg_10min': avg_memory
            },
            'alerts': {
                'memory_alert': current_metrics.memory_percent > self.memory_threshold * 100,
                'cpu_alert': current_metrics.cpu_percent > self.cpu_threshold * 100,
                'disk_alert': current_metrics.disk_usage_percent > self.disk_threshold * 100
            }
        }
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get processing performance summary."""
        recent_operations = list(self.processing_history)[-50:]  # Last 50 operations
        
        if not recent_operations:
            return {'message': 'No processing operations recorded'}
        
        # Calculate statistics
        durations = [op.duration_seconds for op in recent_operations]
        throughputs = [op.throughput_rows_per_sec for op in recent_operations if op.throughput_rows_per_sec > 0]
        memory_deltas = [op.memory_after_mb - op.memory_before_mb for op in recent_operations]
        
        # Group by operation name
        operations_by_name = defaultdict(list)
        for op in recent_operations:
            operations_by_name[op.operation_name].append(op)
        
        operation_stats = {}
        for name, ops in operations_by_name.items():
            operation_stats[name] = {
                'count': len(ops),
                'avg_duration': np.mean([op.duration_seconds for op in ops]),
                'avg_throughput': np.mean([op.throughput_rows_per_sec for op in ops if op.throughput_rows_per_sec > 0]),
                'total_rows': sum(op.rows_processed for op in ops),
                'error_rate': sum(op.errors_count for op in ops) / len(ops)
            }
        
        return {
            'overall_stats': {
                'total_operations': len(recent_operations),
                'avg_duration': np.mean(durations),
                'median_duration': np.median(durations),
                'avg_throughput': np.mean(throughputs) if throughputs else 0,
                'avg_memory_delta_mb': np.mean(memory_deltas),
                'slow_operations_count': len([d for d in durations if d > self.slow_operation_threshold])
            },
            'operation_breakdown': operation_stats,
            'recent_operations': [op.to_dict() for op in recent_operations[-10:]]  # Last 10 operations
        }

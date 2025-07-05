#!/bin/bash
# Container Optimization Script for ADS599 Capstone Soccer Intelligence System
# Optimizes container performance for data collection and analysis workflows

set -e

# ============================================================================
# Configuration Variables
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Performance tuning parameters
MEMORY_LIMIT="${MEMORY_LIMIT:-6g}"
CPU_LIMIT="${CPU_LIMIT:-4}"
WORKER_PROCESSES="${WORKER_PROCESSES:-2}"
CACHE_SIZE="${CACHE_SIZE:-1g}"

# ============================================================================
# Logging Functions
# ============================================================================

log_info() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_warn() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [WARN] $1"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR] $1"
}

# ============================================================================
# System Optimization Functions
# ============================================================================

optimize_python_performance() {
    log_info "Optimizing Python performance..."
    
    # Set Python optimization flags
    export PYTHONOPTIMIZE=2
    export PYTHONHASHSEED=random
    export PYTHONIOENCODING=utf-8
    
    # Configure garbage collection
    export PYTHONGC=1
    
    # Optimize pandas performance
    export PANDAS_COMPUTE_BACKEND=numba
    
    log_info "Python performance optimization completed"
}

optimize_memory_usage() {
    log_info "Optimizing memory usage..."
    
    # Configure memory limits for different components
    cat > /tmp/memory_config.py << EOF
import os
import gc
import pandas as pd
import numpy as np

# Configure pandas memory optimization
pd.set_option('mode.copy_on_write', True)
pd.set_option('compute.use_bottleneck', True)
pd.set_option('compute.use_numexpr', True)

# Configure numpy memory optimization
np.seterr(all='ignore')

# Enable aggressive garbage collection
gc.set_threshold(700, 10, 10)

# Memory monitoring function
def monitor_memory():
    import psutil
    process = psutil.Process()
    memory_info = process.memory_info()
    return {
        'rss': memory_info.rss / 1024 / 1024,  # MB
        'vms': memory_info.vms / 1024 / 1024,  # MB
        'percent': process.memory_percent()
    }

# Memory cleanup function
def cleanup_memory():
    gc.collect()
    import ctypes
    libc = ctypes.CDLL("libc.so.6")
    libc.malloc_trim(0)
EOF
    
    log_info "Memory optimization configuration created"
}

optimize_data_processing() {
    log_info "Optimizing data processing workflows..."
    
    # Create optimized data processing configuration
    cat > /tmp/processing_config.yaml << EOF
# Data Processing Optimization Configuration
processing:
  # Chunk processing for large datasets
  chunk_size: 10000
  parallel_processing: true
  max_workers: ${WORKER_PROCESSES}
  
  # Memory management
  memory_limit_mb: $((${MEMORY_LIMIT%g} * 1024))
  cache_size_mb: $((${CACHE_SIZE%g} * 1024))
  
  # I/O optimization
  buffer_size: 65536
  compression: 'gzip'
  compression_level: 6
  
  # API optimization
  connection_pool_size: 10
  request_timeout: 30
  retry_attempts: 3
  backoff_factor: 0.3
  
  # Database optimization
  batch_insert_size: 1000
  connection_pool_max: 20
  connection_pool_min: 5
EOF
    
    log_info "Data processing optimization completed"
}

optimize_shapley_analysis() {
    log_info "Optimizing Shapley value analysis..."
    
    # Create Shapley-specific optimization configuration
    cat > /tmp/shapley_config.yaml << EOF
# Shapley Analysis Optimization Configuration
shapley:
  # Computational optimization
  parallel_computation: true
  n_jobs: ${WORKER_PROCESSES}
  batch_size: 100
  
  # Memory optimization
  use_sparse_matrices: true
  memory_efficient_mode: true
  
  # Sampling optimization
  sampling_strategy: 'stratified'
  min_samples: 1000
  max_samples: 10000
  
  # Caching optimization
  cache_intermediate_results: true
  cache_directory: '/app/data/cache/shapley'
  cache_compression: true
EOF
    
    log_info "Shapley analysis optimization completed"
}

# ============================================================================
# Container Resource Optimization
# ============================================================================

optimize_container_resources() {
    log_info "Optimizing container resources..."
    
    # Create resource limits configuration
    cat > /tmp/docker-resource-limits.yml << EOF
# Docker Resource Limits for Optimal Performance
version: '3.8'

x-resource-limits: &resource-limits
  deploy:
    resources:
      limits:
        memory: ${MEMORY_LIMIT}
        cpus: '${CPU_LIMIT}'
      reservations:
        memory: $((${MEMORY_LIMIT%g} / 2))g
        cpus: '$((${CPU_LIMIT} / 2))'

x-common-environment: &common-environment
  PYTHONOPTIMIZE: 2
  PYTHONHASHSEED: random
  PYTHONIOENCODING: utf-8
  PANDAS_COMPUTE_BACKEND: numba
  OMP_NUM_THREADS: ${WORKER_PROCESSES}
  NUMEXPR_MAX_THREADS: ${WORKER_PROCESSES}
  MKL_NUM_THREADS: ${WORKER_PROCESSES}

services:
  soccer-intelligence:
    <<: *resource-limits
    environment:
      <<: *common-environment
    
  data-collector:
    <<: *resource-limits
    environment:
      <<: *common-environment
      WORKER_TYPE: data_collection
    
  analysis-worker:
    <<: *resource-limits
    environment:
      <<: *common-environment
      WORKER_TYPE: analysis
EOF
    
    log_info "Container resource optimization completed"
}

# ============================================================================
# Database Optimization
# ============================================================================

optimize_database_performance() {
    log_info "Optimizing database performance..."
    
    # Create PostgreSQL optimization configuration
    cat > /tmp/postgresql-optimization.conf << EOF
# PostgreSQL Performance Optimization for Soccer Intelligence System

# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB
maintenance_work_mem = 64MB

# Connection settings
max_connections = 100
shared_preload_libraries = 'pg_stat_statements'

# Checkpoint settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Query optimization
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
EOF
    
    # Create Redis optimization configuration
    cat > /tmp/redis-optimization.conf << EOF
# Redis Performance Optimization for Soccer Intelligence System

# Memory management
maxmemory ${CACHE_SIZE}
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000

# Network optimization
tcp-keepalive 300
timeout 0

# Performance tuning
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
EOF
    
    log_info "Database optimization completed"
}

# ============================================================================
# Monitoring and Health Checks
# ============================================================================

setup_performance_monitoring() {
    log_info "Setting up performance monitoring..."
    
    # Create monitoring script
    cat > /tmp/monitor-performance.py << EOF
#!/usr/bin/env python3
"""
Performance monitoring script for Soccer Intelligence System
"""

import time
import psutil
import json
import logging
from datetime import datetime
from pathlib import Path

class PerformanceMonitor:
    def __init__(self, log_file='/app/logs/performance.log'):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def collect_metrics(self):
        """Collect system performance metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free / (1024**3)
        }
        
        return metrics
    
    def log_metrics(self, metrics):
        """Log performance metrics"""
        self.logger.info(f"Performance metrics: {json.dumps(metrics)}")
        
        # Alert on high resource usage
        if metrics['cpu_percent'] > 80:
            self.logger.warning(f"High CPU usage: {metrics['cpu_percent']}%")
        
        if metrics['memory_percent'] > 85:
            self.logger.warning(f"High memory usage: {metrics['memory_percent']}%")
        
        if metrics['disk_percent'] > 90:
            self.logger.warning(f"High disk usage: {metrics['disk_percent']}%")
    
    def run_monitoring(self, interval=60):
        """Run continuous monitoring"""
        while True:
            try:
                metrics = self.collect_metrics()
                self.log_metrics(metrics)
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(interval)

if __name__ == "__main__":
    monitor = PerformanceMonitor()
    monitor.run_monitoring()
EOF
    
    chmod +x /tmp/monitor-performance.py
    log_info "Performance monitoring setup completed"
}

# ============================================================================
# Main Optimization Function
# ============================================================================

main() {
    log_info "Starting container optimization for Soccer Intelligence System"
    
    # Run all optimization functions
    optimize_python_performance
    optimize_memory_usage
    optimize_data_processing
    optimize_shapley_analysis
    optimize_container_resources
    optimize_database_performance
    setup_performance_monitoring
    
    # Copy optimization files to appropriate locations
    if [ -d "/app" ]; then
        log_info "Copying optimization configurations to application directory..."
        
        mkdir -p /app/config/optimization
        cp /tmp/processing_config.yaml /app/config/optimization/ 2>/dev/null || true
        cp /tmp/shapley_config.yaml /app/config/optimization/ 2>/dev/null || true
        cp /tmp/memory_config.py /app/config/optimization/ 2>/dev/null || true
        cp /tmp/monitor-performance.py /app/scripts/ 2>/dev/null || true
        
        log_info "Optimization configurations copied"
    fi
    
    log_info "Container optimization completed successfully"
    log_info "Optimized for:"
    log_info "  - Memory limit: ${MEMORY_LIMIT}"
    log_info "  - CPU limit: ${CPU_LIMIT}"
    log_info "  - Worker processes: ${WORKER_PROCESSES}"
    log_info "  - Cache size: ${CACHE_SIZE}"
}

# Execute main function
main "$@"

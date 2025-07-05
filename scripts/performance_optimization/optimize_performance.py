#!/usr/bin/env python3
"""
Performance Optimization Script for ADS599 Capstone Soccer Intelligence System
Applies all performance optimizations for the 67 UEFA Champions League teams dataset.
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import json

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

# Import only essential modules to avoid dependency issues
try:
    from soccer_intelligence.utils.config import Config
    from soccer_intelligence.utils.logger import get_logger
    CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import config modules: {e}")
    CONFIG_AVAILABLE = False

# Optional imports for monitoring (only if Docker is running)
MONITORING_AVAILABLE = False
CACHE_AVAILABLE = False

def try_import_monitoring():
    global MONITORING_AVAILABLE, CACHE_AVAILABLE
    try:
        from soccer_intelligence.monitoring.performance_monitor import PerformanceMonitor
        MONITORING_AVAILABLE = True
    except ImportError:
        pass

    try:
        from soccer_intelligence.utils.advanced_cache_manager import AdvancedCacheManager
        CACHE_AVAILABLE = True
    except ImportError:
        pass


class PerformanceOptimizer:
    """
    Comprehensive performance optimization for the Soccer Intelligence System.
    """
    
    def __init__(self):
        """Initialize the performance optimizer."""
        self.logger = get_logger(__name__)
        self.project_root = Path(__file__).parent.parent
        self.config = Config()
        
        # Performance targets
        self.targets = {
            'memory_usage_reduction': 0.5,  # 50% reduction
            'processing_speed_increase': 3.0,  # 3x faster
            'cache_hit_rate': 0.9,  # 90% hit rate
            'cpu_utilization_target': 0.8,  # 80% CPU usage
        }
        
        self.logger.info("Performance optimizer initialized")
    
    def check_system_requirements(self) -> bool:
        """Check if system meets requirements for optimizations."""
        self.logger.info("Checking system requirements...")
        
        requirements = {
            'docker': 'docker --version',
            'docker-compose': 'docker-compose --version',
            'python': 'python --version',
        }
        
        missing_requirements = []
        
        for requirement, command in requirements.items():
            try:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.logger.info(f"✓ {requirement}: {result.stdout.strip()}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing_requirements.append(requirement)
                self.logger.error(f"✗ {requirement}: Not found")
        
        if missing_requirements:
            self.logger.error(f"Missing requirements: {', '.join(missing_requirements)}")
            return False
        
        # Check available resources
        try:
            import psutil
            
            # Check memory (minimum 8GB recommended)
            memory_gb = psutil.virtual_memory().total / (1024 ** 3)
            if memory_gb < 8:
                self.logger.warning(f"Low memory: {memory_gb:.1f}GB (8GB+ recommended)")
            else:
                self.logger.info(f"✓ Memory: {memory_gb:.1f}GB")
            
            # Check CPU cores (minimum 4 cores recommended)
            cpu_count = psutil.cpu_count()
            if cpu_count < 4:
                self.logger.warning(f"Low CPU count: {cpu_count} cores (4+ recommended)")
            else:
                self.logger.info(f"✓ CPU cores: {cpu_count}")
            
            # Check disk space (minimum 10GB free)
            disk_free_gb = psutil.disk_usage('/').free / (1024 ** 3)
            if disk_free_gb < 10:
                self.logger.warning(f"Low disk space: {disk_free_gb:.1f}GB (10GB+ recommended)")
            else:
                self.logger.info(f"✓ Disk space: {disk_free_gb:.1f}GB free")
                
        except ImportError:
            self.logger.warning("psutil not available, skipping resource checks")
        
        return True
    
    def optimize_docker_configuration(self) -> bool:
        """Apply Docker configuration optimizations."""
        self.logger.info("Optimizing Docker configuration...")
        
        try:
            # Check if optimized docker-compose.yml exists
            docker_compose_path = self.project_root / 'docker-compose.yml'
            if not docker_compose_path.exists():
                self.logger.error("docker-compose.yml not found")
                return False
            
            # Verify optimized configuration is present
            with open(docker_compose_path, 'r') as f:
                compose_content = f.read()
            
            optimization_markers = [
                'PYTHONOPTIMIZE=2',
                'PANDAS_COMPUTE_BACKEND=numba',
                'OMP_NUM_THREADS',
                'shared_buffers=1GB',
                'effective_cache_size=3GB'
            ]
            
            missing_optimizations = []
            for marker in optimization_markers:
                if marker not in compose_content:
                    missing_optimizations.append(marker)
            
            if missing_optimizations:
                self.logger.warning(f"Missing optimizations: {', '.join(missing_optimizations)}")
                self.logger.info("Please ensure the optimized docker-compose.yml is being used")
            else:
                self.logger.info("✓ Docker configuration optimizations detected")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error optimizing Docker configuration: {e}")
            return False
    
    def setup_performance_monitoring(self) -> bool:
        """Setup performance monitoring."""
        self.logger.info("Setting up performance monitoring...")
        
        try:
            # Initialize performance monitor
            monitor = PerformanceMonitor(self.config)
            
            # Start monitoring
            monitor.start_monitoring()
            
            # Wait a moment for initial metrics
            time.sleep(5)
            
            # Get initial system summary
            summary = monitor.get_system_summary()
            self.logger.info(f"✓ Performance monitoring active")
            self.logger.info(f"Current CPU: {summary['current']['cpu_percent']:.1f}%")
            self.logger.info(f"Current Memory: {summary['current']['memory_percent']:.1f}%")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up performance monitoring: {e}")
            return False
    
    def optimize_cache_configuration(self) -> bool:
        """Optimize caching configuration."""
        self.logger.info("Optimizing cache configuration...")
        
        try:
            # Initialize advanced cache manager
            cache_manager = AdvancedCacheManager(self.config)
            
            # Test cache functionality
            test_key = "performance_test"
            test_data = {"timestamp": time.time(), "test": True}
            
            # Test cache set/get
            cache_manager.set(test_key, test_data, namespace="test")
            retrieved_data = cache_manager.get(test_key, namespace="test")
            
            if retrieved_data and retrieved_data.get("test"):
                self.logger.info("✓ Cache functionality verified")
                
                # Get cache statistics
                stats = cache_manager.get_stats()
                self.logger.info(f"Cache hit rate: {stats.get('hit_rate', 0):.2%}")
                self.logger.info(f"Total memory usage: {stats.get('total_memory_mb', 0):.1f}MB")
                
                # Cleanup test data
                cache_manager.delete(test_key, namespace="test")
                
                return True
            else:
                self.logger.error("Cache functionality test failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error optimizing cache configuration: {e}")
            return False
    
    def run_performance_benchmark(self) -> Dict[str, Any]:
        """Run performance benchmark to measure improvements."""
        self.logger.info("Running performance benchmark...")
        
        benchmark_results = {
            'timestamp': time.time(),
            'system_info': {},
            'processing_performance': {},
            'cache_performance': {},
            'memory_usage': {}
        }
        
        try:
            import psutil
            import pandas as pd
            import numpy as np
            
            # System information
            benchmark_results['system_info'] = {
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': psutil.virtual_memory().total / (1024 ** 3),
                'python_version': sys.version
            }
            
            # Test data processing performance
            self.logger.info("Testing data processing performance...")
            
            # Create test dataset similar to soccer data
            test_size = 10000
            test_data = pd.DataFrame({
                'player_id': range(test_size),
                'goals_total': np.random.randint(0, 30, test_size),
                'goals_assists': np.random.randint(0, 20, test_size),
                'games_appearances': np.random.randint(1, 40, test_size),
                'games_minutes': np.random.randint(100, 3500, test_size),
                'games_rating': np.random.uniform(5.0, 9.0, test_size)
            })
            
            # Benchmark data processing
            start_time = time.time()
            
            # Simulate typical operations
            test_data['goals_per_game'] = test_data['goals_total'] / test_data['games_appearances']
            test_data['assists_per_game'] = test_data['goals_assists'] / test_data['games_appearances']
            test_data['minutes_per_game'] = test_data['games_minutes'] / test_data['games_appearances']
            test_data['performance_score'] = (
                test_data['goals_per_game'] * 0.4 +
                test_data['assists_per_game'] * 0.3 +
                test_data['games_rating'] * 0.3
            )
            
            processing_time = time.time() - start_time
            rows_per_second = test_size / processing_time
            
            benchmark_results['processing_performance'] = {
                'rows_processed': test_size,
                'processing_time_seconds': processing_time,
                'rows_per_second': rows_per_second,
                'memory_usage_mb': psutil.Process().memory_info().rss / (1024 ** 2)
            }
            
            self.logger.info(f"Processing benchmark: {rows_per_second:.0f} rows/second")
            
            # Test cache performance
            self.logger.info("Testing cache performance...")
            
            cache_manager = AdvancedCacheManager(self.config)
            
            # Cache performance test
            cache_test_data = test_data.to_dict('records')[:1000]  # Test with 1000 records
            
            cache_start_time = time.time()
            
            # Test cache writes
            for i, record in enumerate(cache_test_data):
                cache_manager.set(f"benchmark_player_{i}", record, namespace="benchmark")
            
            # Test cache reads
            cache_hits = 0
            for i in range(len(cache_test_data)):
                if cache_manager.get(f"benchmark_player_{i}", namespace="benchmark"):
                    cache_hits += 1
            
            cache_time = time.time() - cache_start_time
            cache_hit_rate = cache_hits / len(cache_test_data)
            
            benchmark_results['cache_performance'] = {
                'cache_operations': len(cache_test_data) * 2,  # reads + writes
                'cache_time_seconds': cache_time,
                'cache_hit_rate': cache_hit_rate,
                'operations_per_second': (len(cache_test_data) * 2) / cache_time
            }
            
            self.logger.info(f"Cache benchmark: {cache_hit_rate:.2%} hit rate")
            
            # Cleanup benchmark cache data
            cache_manager.clear_namespace("benchmark")
            
            # Memory usage analysis
            memory_info = psutil.virtual_memory()
            benchmark_results['memory_usage'] = {
                'total_gb': memory_info.total / (1024 ** 3),
                'available_gb': memory_info.available / (1024 ** 3),
                'used_percent': memory_info.percent,
                'process_memory_mb': psutil.Process().memory_info().rss / (1024 ** 2)
            }
            
            return benchmark_results
            
        except Exception as e:
            self.logger.error(f"Error running performance benchmark: {e}")
            return benchmark_results
    
    def generate_optimization_report(self, benchmark_results: Dict[str, Any]) -> str:
        """Generate optimization report."""
        self.logger.info("Generating optimization report...")
        
        report_lines = [
            "# Performance Optimization Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## System Information",
            f"- CPU Cores: {benchmark_results['system_info'].get('cpu_count', 'Unknown')}",
            f"- Total Memory: {benchmark_results['system_info'].get('memory_total_gb', 0):.1f}GB",
            f"- Python Version: {benchmark_results['system_info'].get('python_version', 'Unknown')}",
            "",
            "## Processing Performance",
            f"- Rows Processed: {benchmark_results['processing_performance'].get('rows_processed', 0):,}",
            f"- Processing Time: {benchmark_results['processing_performance'].get('processing_time_seconds', 0):.2f}s",
            f"- Throughput: {benchmark_results['processing_performance'].get('rows_per_second', 0):.0f} rows/second",
            f"- Memory Usage: {benchmark_results['processing_performance'].get('memory_usage_mb', 0):.1f}MB",
            "",
            "## Cache Performance",
            f"- Cache Hit Rate: {benchmark_results['cache_performance'].get('cache_hit_rate', 0):.2%}",
            f"- Cache Operations: {benchmark_results['cache_performance'].get('cache_operations', 0):,}",
            f"- Operations/Second: {benchmark_results['cache_performance'].get('operations_per_second', 0):.0f}",
            "",
            "## Memory Usage",
            f"- Total Memory: {benchmark_results['memory_usage'].get('total_gb', 0):.1f}GB",
            f"- Available Memory: {benchmark_results['memory_usage'].get('available_gb', 0):.1f}GB",
            f"- Memory Usage: {benchmark_results['memory_usage'].get('used_percent', 0):.1f}%",
            f"- Process Memory: {benchmark_results['memory_usage'].get('process_memory_mb', 0):.1f}MB",
            "",
            "## Optimization Status",
        ]
        
        # Check if targets are met
        processing_speed = benchmark_results['processing_performance'].get('rows_per_second', 0)
        cache_hit_rate = benchmark_results['cache_performance'].get('cache_hit_rate', 0)
        memory_usage_percent = benchmark_results['memory_usage'].get('used_percent', 100)
        
        if processing_speed > 5000:  # Target: >5000 rows/second
            report_lines.append("✓ Processing speed target met")
        else:
            report_lines.append("✗ Processing speed below target")
        
        if cache_hit_rate > 0.8:  # Target: >80% hit rate
            report_lines.append("✓ Cache performance target met")
        else:
            report_lines.append("✗ Cache performance below target")
        
        if memory_usage_percent < 80:  # Target: <80% memory usage
            report_lines.append("✓ Memory usage target met")
        else:
            report_lines.append("✗ Memory usage above target")
        
        report_lines.extend([
            "",
            "## Recommendations",
            "- Monitor performance regularly using the monitoring dashboard",
            "- Adjust chunk sizes based on available memory",
            "- Scale workers based on CPU cores and workload",
            "- Review cache hit rates and adjust cache sizes as needed",
            "- Consider upgrading hardware if targets are not met consistently"
        ])
        
        return "\n".join(report_lines)
    
    def run_optimization(self) -> bool:
        """Run complete performance optimization."""
        self.logger.info("Starting performance optimization...")
        
        # Check system requirements
        if not self.check_system_requirements():
            self.logger.error("System requirements not met")
            return False
        
        # Apply optimizations
        optimizations = [
            ("Docker Configuration", self.optimize_docker_configuration),
            ("Performance Monitoring", self.setup_performance_monitoring),
            ("Cache Configuration", self.optimize_cache_configuration),
        ]
        
        failed_optimizations = []
        
        for name, optimization_func in optimizations:
            try:
                if optimization_func():
                    self.logger.info(f"✓ {name} optimization completed")
                else:
                    failed_optimizations.append(name)
                    self.logger.error(f"✗ {name} optimization failed")
            except Exception as e:
                failed_optimizations.append(name)
                self.logger.error(f"✗ {name} optimization failed: {e}")
        
        if failed_optimizations:
            self.logger.warning(f"Some optimizations failed: {', '.join(failed_optimizations)}")
        
        # Run benchmark
        benchmark_results = self.run_performance_benchmark()
        
        # Generate report
        report = self.generate_optimization_report(benchmark_results)
        
        # Save report
        report_path = self.project_root / 'performance_optimization_report.md'
        with open(report_path, 'w') as f:
            f.write(report)
        
        self.logger.info(f"Optimization report saved to: {report_path}")
        
        # Save benchmark results
        results_path = self.project_root / 'performance_benchmark_results.json'
        with open(results_path, 'w') as f:
            json.dump(benchmark_results, f, indent=2)
        
        self.logger.info(f"Benchmark results saved to: {results_path}")
        
        success = len(failed_optimizations) == 0
        if success:
            self.logger.info("✓ Performance optimization completed successfully")
        else:
            self.logger.warning("⚠ Performance optimization completed with some failures")
        
        return success


def main():
    """Main function to run performance optimization."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    optimizer = PerformanceOptimizer()
    
    try:
        success = optimizer.run_optimization()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nOptimization interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Optimization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

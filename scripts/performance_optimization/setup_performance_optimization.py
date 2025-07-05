#!/usr/bin/env python3
"""
Standalone Performance Optimization Setup for ADS599 Capstone Soccer Intelligence System
Sets up performance optimizations without complex dependencies.
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json


class SimplePerformanceOptimizer:
    """
    Simple performance optimizer that focuses on Docker and system setup.
    """
    
    def __init__(self):
        """Initialize the performance optimizer."""
        self.project_root = Path(__file__).parent.parent
        self.logger = self._setup_logging()
        self.docker_compose_cmd = None  # Will be set after checking availability

        self.logger.info("Simple performance optimizer initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def check_docker_status(self) -> bool:
        """Check if Docker is running and accessible."""
        self.logger.info("Checking Docker status...")
        
        try:
            # Check if Docker daemon is running
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info("✓ Docker daemon is running")
            return True
        except subprocess.CalledProcessError:
            self.logger.error("✗ Docker daemon is not running")
            self.logger.info("Please start Docker Desktop or Docker daemon")
            return False
        except FileNotFoundError:
            self.logger.error("✗ Docker is not installed")
            self.logger.info("Please install Docker Desktop")
            return False
    
    def check_docker_compose_status(self) -> Tuple[bool, str]:
        """Check if docker-compose is available and return the command to use."""
        self.logger.info("Checking Docker Compose status...")

        # Try docker-compose first (older syntax)
        try:
            result = subprocess.run(
                ['docker-compose', '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info(f"✓ Docker Compose: {result.stdout.strip()}")
            return True, 'docker-compose'
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Try docker compose (newer syntax)
        try:
            result = subprocess.run(
                ['docker', 'compose', 'version'],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info(f"✓ Docker Compose: {result.stdout.strip()}")
            return True, 'docker compose'
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error("✗ Docker Compose is not available")
            return False, ''
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check available system resources."""
        self.logger.info("Checking system resources...")
        
        resources = {}
        
        try:
            import psutil
            
            # Memory check
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024 ** 3)
            resources['memory_gb'] = memory_gb
            
            if memory_gb >= 8:
                self.logger.info(f"✓ Memory: {memory_gb:.1f}GB (sufficient)")
            else:
                self.logger.warning(f"⚠ Memory: {memory_gb:.1f}GB (8GB+ recommended)")
            
            # CPU check
            cpu_count = psutil.cpu_count()
            resources['cpu_count'] = cpu_count
            
            if cpu_count >= 4:
                self.logger.info(f"✓ CPU cores: {cpu_count} (sufficient)")
            else:
                self.logger.warning(f"⚠ CPU cores: {cpu_count} (4+ recommended)")
            
            # Disk space check
            disk = psutil.disk_usage('/')
            disk_free_gb = disk.free / (1024 ** 3)
            resources['disk_free_gb'] = disk_free_gb
            
            if disk_free_gb >= 10:
                self.logger.info(f"✓ Disk space: {disk_free_gb:.1f}GB free (sufficient)")
            else:
                self.logger.warning(f"⚠ Disk space: {disk_free_gb:.1f}GB free (10GB+ recommended)")
                
        except ImportError:
            self.logger.warning("psutil not available, skipping detailed resource checks")
            # Basic checks without psutil
            resources = {'memory_gb': 'unknown', 'cpu_count': 'unknown', 'disk_free_gb': 'unknown'}
        
        return resources
    
    def create_environment_file(self) -> bool:
        """Create optimized environment file."""
        self.logger.info("Creating optimized environment file...")
        
        env_file = self.project_root / '.env'
        
        # Check if .env already exists
        if env_file.exists():
            self.logger.info("Environment file already exists, backing up...")
            backup_file = self.project_root / '.env.backup'
            env_file.rename(backup_file)
            self.logger.info(f"Backup created: {backup_file}")
        
        # Create optimized .env file
        env_content = """# Performance Optimized Environment Configuration
# Generated by setup_performance_optimization.py

# Resource Limits
MEMORY_LIMIT=8g
CPU_LIMIT=4
WORKER_PROCESSES=4
CACHE_SIZE=2g

# Database Configuration
POSTGRES_DB=soccer_intelligence
POSTGRES_USER=soccerapp
POSTGRES_PASSWORD=soccerpass123
POSTGRES_SHARED_BUFFERS=1GB
POSTGRES_EFFECTIVE_CACHE_SIZE=3GB
POSTGRES_WORK_MEM=64MB

# Redis Configuration
REDIS_PASSWORD=redispass123
REDIS_MAXMEMORY=1536mb
REDIS_MAXMEMORY_POLICY=allkeys-lru

# API Keys (add your actual keys here)
API_FOOTBALL_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key_here
TWITTER_BEARER_TOKEN=your_twitter_token_here
SPORTMONKS_API_KEY=your_sportmonks_key_here

# Performance Optimization Flags
PYTHONOPTIMIZE=2
PYTHONHASHSEED=random
PYTHONIOENCODING=utf-8
PANDAS_COMPUTE_BACKEND=numba
OMP_NUM_THREADS=4
NUMEXPR_MAX_THREADS=4
MKL_NUM_THREADS=4
OPENBLAS_NUM_THREADS=4
"""
        
        try:
            with open(env_file, 'w') as f:
                f.write(env_content)
            self.logger.info(f"✓ Environment file created: {env_file}")
            self.logger.info("Please update the API keys in the .env file with your actual keys")
            return True
        except Exception as e:
            self.logger.error(f"✗ Failed to create environment file: {e}")
            return False
    
    def start_optimized_containers(self) -> bool:
        """Start containers with optimized configuration."""
        self.logger.info("Starting optimized containers...")

        if not self.docker_compose_cmd:
            self.logger.error("Docker Compose command not available")
            return False

        try:
            # Change to project directory
            os.chdir(self.project_root)

            # Stop any existing containers
            self.logger.info("Stopping existing containers...")
            if self.docker_compose_cmd == 'docker-compose':
                down_cmd = ['docker-compose', 'down']
                up_cmd = ['docker-compose', '--profile', 'production', 'up', '-d']
                ps_cmd = ['docker-compose', 'ps']
            else:  # docker compose
                down_cmd = ['docker', 'compose', 'down']
                up_cmd = ['docker', 'compose', '--profile', 'production', 'up', '-d']
                ps_cmd = ['docker', 'compose', 'ps']

            subprocess.run(
                down_cmd,
                capture_output=True,
                check=False  # Don't fail if no containers are running
            )

            # Start optimized containers
            self.logger.info("Starting optimized containers...")
            result = subprocess.run(
                up_cmd,
                capture_output=True,
                text=True,
                check=True
            )

            self.logger.info("✓ Containers started successfully")

            # Wait for containers to be ready
            self.logger.info("Waiting for containers to be ready...")
            time.sleep(30)

            # Check container status
            result = subprocess.run(
                ps_cmd,
                capture_output=True,
                text=True,
                check=True
            )

            self.logger.info("Container status:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    self.logger.info(f"  {line}")

            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"✗ Failed to start containers: {e}")
            if e.stderr:
                self.logger.error(f"Error output: {e.stderr}")
            return False
    
    def run_basic_performance_test(self) -> Dict[str, Any]:
        """Run basic performance test without complex dependencies."""
        self.logger.info("Running basic performance test...")
        
        test_results = {
            'timestamp': time.time(),
            'container_status': {},
            'basic_metrics': {}
        }
        
        try:
            # Check container status
            result = subprocess.run(
                ['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'],
                capture_output=True,
                text=True,
                check=True
            )
            
            containers = []
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if 'soccer-intelligence' in line:
                    containers.append(line.strip())
            
            test_results['container_status'] = {
                'running_containers': len(containers),
                'containers': containers
            }
            
            self.logger.info(f"Found {len(containers)} running soccer-intelligence containers")
            
            # Test basic container connectivity
            if containers:
                self.logger.info("Testing container connectivity...")
                
                # Test main application container
                try:
                    result = subprocess.run(
                        ['docker', 'exec', 'soccer-intelligence-app', 'python', '--version'],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=10
                    )
                    test_results['basic_metrics']['python_version'] = result.stdout.strip()
                    self.logger.info(f"✓ Application container responsive: {result.stdout.strip()}")
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    self.logger.warning("⚠ Application container not responsive")
                
                # Test database container
                try:
                    result = subprocess.run(
                        ['docker', 'exec', 'soccer-intelligence-db', 'pg_isready', '-U', 'soccerapp'],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=10
                    )
                    test_results['basic_metrics']['database_status'] = 'ready'
                    self.logger.info("✓ Database container ready")
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    self.logger.warning("⚠ Database container not ready")
                
                # Test Redis container
                try:
                    result = subprocess.run(
                        ['docker', 'exec', 'soccer-intelligence-cache', 'redis-cli', 'ping'],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=10
                    )
                    test_results['basic_metrics']['redis_status'] = result.stdout.strip()
                    self.logger.info(f"✓ Redis container ready: {result.stdout.strip()}")
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    self.logger.warning("⚠ Redis container not ready")
            
        except Exception as e:
            self.logger.error(f"Error during performance test: {e}")
        
        return test_results
    
    def generate_setup_report(self, test_results: Dict[str, Any]) -> str:
        """Generate setup report."""
        self.logger.info("Generating setup report...")
        
        report_lines = [
            "# Performance Optimization Setup Report",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Setup Status",
        ]
        
        # Container status
        container_count = test_results.get('container_status', {}).get('running_containers', 0)
        if container_count > 0:
            report_lines.append(f"✓ {container_count} containers running")
        else:
            report_lines.append("✗ No containers running")
        
        # Basic metrics
        basic_metrics = test_results.get('basic_metrics', {})
        
        if 'python_version' in basic_metrics:
            report_lines.append(f"✓ Application container: {basic_metrics['python_version']}")
        else:
            report_lines.append("✗ Application container not responsive")
        
        if basic_metrics.get('database_status') == 'ready':
            report_lines.append("✓ Database container ready")
        else:
            report_lines.append("✗ Database container not ready")
        
        if basic_metrics.get('redis_status') == 'PONG':
            report_lines.append("✓ Redis container ready")
        else:
            report_lines.append("✗ Redis container not ready")
        
        report_lines.extend([
            "",
            "## Next Steps",
            "1. Verify all containers are running: `docker-compose ps`",
            "2. Check container logs: `docker-compose logs`",
            "3. Access monitoring dashboard: http://localhost:3000 (if monitoring profile enabled)",
            "4. Test performance optimizations with your data processing workflows",
            "",
            "## Troubleshooting",
            "- If containers fail to start, check Docker Desktop is running",
            "- If memory issues occur, reduce MEMORY_LIMIT in .env file",
            "- If performance is still slow, consider upgrading hardware",
            "- Check logs with: `docker-compose logs [service-name]`"
        ])
        
        return "\n".join(report_lines)
    
    def run_optimization_setup(self) -> bool:
        """Run complete optimization setup."""
        self.logger.info("Starting performance optimization setup...")

        # Check prerequisites
        if not self.check_docker_status():
            return False

        compose_available, compose_cmd = self.check_docker_compose_status()
        if not compose_available:
            return False

        # Store the docker compose command to use
        self.docker_compose_cmd = compose_cmd

        # Check system resources
        resources = self.check_system_resources()

        # Create optimized environment
        if not self.create_environment_file():
            return False

        # Start optimized containers
        if not self.start_optimized_containers():
            return False

        # Run basic performance test
        test_results = self.run_basic_performance_test()

        # Generate report
        report = self.generate_setup_report(test_results)

        # Save report
        report_path = self.project_root / 'performance_setup_report.md'
        with open(report_path, 'w') as f:
            f.write(report)

        self.logger.info(f"Setup report saved to: {report_path}")

        # Save test results
        results_path = self.project_root / 'performance_setup_results.json'
        with open(results_path, 'w') as f:
            json.dump(test_results, f, indent=2)

        self.logger.info(f"Test results saved to: {results_path}")

        # Check if setup was successful
        container_count = test_results.get('container_status', {}).get('running_containers', 0)
        success = container_count > 0

        if success:
            self.logger.info("✓ Performance optimization setup completed successfully!")
            self.logger.info("Your containers are now running with optimized configuration.")
            self.logger.info("You can now run your data processing workflows with improved performance.")
        else:
            self.logger.warning("⚠ Setup completed with issues. Check the report for details.")

        return success


def main():
    """Main function to run performance optimization setup."""
    optimizer = SimplePerformanceOptimizer()
    
    try:
        success = optimizer.run_optimization_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

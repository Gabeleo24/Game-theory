#!/usr/bin/env python3
"""
Real Madrid KPI System Startup Script
Comprehensive orchestration of Docker containers for Real Madrid soccer intelligence
Optimized for team collaboration and algorithm optimization
"""

import os
import sys
import subprocess
import time
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Optional
import docker
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealMadridKPISystem:
    """Real Madrid KPI system orchestrator."""
    
    def __init__(self):
        """Initialize the system orchestrator."""
        self.docker_client = docker.from_env()
        self.compose_file = "docker-compose.yml"
        self.project_name = "real-madrid-soccer-intelligence"
        self.services_status = {}
        self.compose_cmd = ['docker-compose']  # Default to legacy
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        logger.info("🔍 Checking system prerequisites...")
        
        # Check Docker
        try:
            self.docker_client.ping()
            logger.info("✅ Docker is running")
        except Exception as e:
            logger.error(f"❌ Docker is not running: {e}")
            return False
        
        # Check Docker Compose (try both v2 and legacy)
        compose_available = False
        try:
            result = subprocess.run(['docker', 'compose', 'version'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ Docker Compose v2 is available")
                self.compose_cmd = ['docker', 'compose']
                compose_available = True
        except Exception:
            pass

        if not compose_available:
            try:
                result = subprocess.run(['docker-compose', '--version'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("✅ Docker Compose (legacy) is available")
                    self.compose_cmd = ['docker-compose']
                    compose_available = True
            except Exception as e:
                logger.error(f"❌ Docker Compose check failed: {e}")

        if not compose_available:
            logger.error("❌ Docker Compose is not available")
            return False
        
        # Check compose file
        if not os.path.exists(self.compose_file):
            logger.error(f"❌ Docker Compose file not found: {self.compose_file}")
            return False
        
        logger.info("✅ All prerequisites met")
        return True
    
    def create_required_directories(self):
        """Create required directories for the system."""
        logger.info("📁 Creating required directories...")
        
        directories = [
            "data/real_madrid",
            "data/kpi",
            "data/algorithms",
            "data/models",
            "logs/kpi",
            "logs/algorithms",
            "logs/data_collection",
            "logs/match_analysis",
            "database/backups",
            "database/exports"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"  Created: {directory}")
    
    def setup_environment_variables(self):
        """Setup environment variables for the system."""
        logger.info("🔧 Setting up environment variables...")
        
        env_vars = {
            'COMPOSE_PROJECT_NAME': self.project_name,
            'POSTGRES_DB': 'soccer_intelligence',
            'POSTGRES_USER': 'soccerapp',
            'POSTGRES_PASSWORD': 'soccerpass123',
            'REDIS_PASSWORD': 'redispass123',
            'API_FOOTBALL_KEY': '5ced20dec7f4b2226c8944c88c6d86aa',
            'SPORTMONKS_API_KEY': 'TmPuKHKnA7OJdHxp8zGzF5oevN0mgyqOOOaqgWMOr7KrhpaZeg9xB2ajoq2p'
        }
        
        for key, value in env_vars.items():
            os.environ[key] = value
        
        logger.info("✅ Environment variables configured")
    
    def start_core_services(self):
        """Start core services (PostgreSQL and Redis)."""
        logger.info("🚀 Starting core services...")
        
        core_services = ['postgres', 'redis']
        
        for service in core_services:
            logger.info(f"  Starting {service}...")
            result = subprocess.run(
                self.compose_cmd + ['up', '-d', service],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {service} started successfully")
                self.services_status[service] = 'running'
            else:
                logger.error(f"❌ Failed to start {service}: {result.stderr}")
                self.services_status[service] = 'failed'
                return False
        
        # Wait for services to be healthy
        logger.info("⏳ Waiting for core services to be healthy...")
        self.wait_for_service_health(['postgres', 'redis'])
        
        return True
    
    def wait_for_service_health(self, services: List[str], timeout: int = 120):
        """Wait for services to be healthy."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_healthy = True
            
            for service in services:
                try:
                    containers = self.docker_client.containers.list(
                        filters={'label': f'com.docker.compose.service={service}'}
                    )
                    
                    if not containers:
                        all_healthy = False
                        continue
                    
                    container = containers[0]
                    if container.attrs['State']['Health']['Status'] != 'healthy':
                        all_healthy = False
                        continue
                        
                except Exception:
                    all_healthy = False
                    continue
            
            if all_healthy:
                logger.info("✅ All core services are healthy")
                return True
            
            time.sleep(5)
        
        logger.warning("⚠️ Timeout waiting for services to be healthy")
        return False
    
    def start_application_services(self):
        """Start application services."""
        logger.info("🚀 Starting application services...")
        
        app_services = ['real-madrid-app']
        
        for service in app_services:
            logger.info(f"  Starting {service}...")
            result = subprocess.run(
                self.compose_cmd + ['up', '-d', service],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {service} started successfully")
                self.services_status[service] = 'running'
            else:
                logger.error(f"❌ Failed to start {service}: {result.stderr}")
                self.services_status[service] = 'failed'
        
        return True
    
    def run_data_collection(self):
        """Run data collection for Real Madrid."""
        logger.info("📊 Starting Real Madrid data collection...")
        
        result = subprocess.run(
            self.compose_cmd + ['run', '--rm', 'real-madrid-data-collector'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Data collection completed successfully")
            return True
        else:
            logger.error(f"❌ Data collection failed: {result.stderr}")
            return False
    
    def run_kpi_analysis(self):
        """Run KPI analysis for Real Madrid."""
        logger.info("📈 Starting Real Madrid KPI analysis...")
        
        result = subprocess.run(
            self.compose_cmd + ['run', '--rm', 'real-madrid-kpi-analyzer'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ KPI analysis completed successfully")
            return True
        else:
            logger.error(f"❌ KPI analysis failed: {result.stderr}")
            return False
    
    def run_algorithm_optimization(self):
        """Run algorithm optimization for KPIs."""
        logger.info("🤖 Starting algorithm optimization...")
        
        result = subprocess.run(
            self.compose_cmd + ['run', '--rm', 'real-madrid-algorithm-tester'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Algorithm optimization completed successfully")
            return True
        else:
            logger.error(f"❌ Algorithm optimization failed: {result.stderr}")
            return False
    
    def start_development_environment(self):
        """Start development environment."""
        logger.info("💻 Starting development environment...")
        
        result = subprocess.run(
            self.compose_cmd + ['--profile', 'development', 'up', '-d'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Development environment started")
            logger.info("🌐 Jupyter Lab available at: http://localhost:8888")
            logger.info("📊 Streamlit dashboard available at: http://localhost:8501")
            return True
        else:
            logger.error(f"❌ Failed to start development environment: {result.stderr}")
            return False
    
    def start_dashboard(self):
        """Start web dashboard."""
        logger.info("🌐 Starting web dashboard...")
        
        result = subprocess.run(
            self.compose_cmd + ['--profile', 'dashboard', 'up', '-d'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Web dashboard started")
            logger.info("🌐 Dashboard available at: http://localhost:8080")
            return True
        else:
            logger.error(f"❌ Failed to start dashboard: {result.stderr}")
            return False
    
    def show_system_status(self):
        """Show current system status."""
        logger.info("📊 System Status:")
        
        try:
            result = subprocess.run(
                self.compose_cmd + ['ps'],
                capture_output=True, text=True
            )
            
            print("\n" + "="*80)
            print("REAL MADRID KPI SYSTEM STATUS")
            print("="*80)
            print(result.stdout)
            print("="*80)
            
        except Exception as e:
            logger.error(f"❌ Failed to get system status: {e}")
    
    def stop_system(self):
        """Stop the entire system."""
        logger.info("🛑 Stopping Real Madrid KPI system...")
        
        result = subprocess.run(
            self.compose_cmd + ['down'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ System stopped successfully")
        else:
            logger.error(f"❌ Failed to stop system: {result.stderr}")
    
    def cleanup_system(self):
        """Clean up system resources."""
        logger.info("🧹 Cleaning up system resources...")
        
        # Stop and remove containers
        subprocess.run(self.compose_cmd + ['down', '-v'], capture_output=True)
        
        # Remove unused images
        subprocess.run(['docker', 'image', 'prune', '-f'], capture_output=True)
        
        logger.info("✅ System cleanup completed")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Real Madrid KPI System Manager')
    parser.add_argument('action', choices=[
        'start', 'stop', 'status', 'cleanup', 'dev', 'dashboard',
        'collect-data', 'analyze-kpi', 'optimize-algorithms', 'full-analysis'
    ], help='Action to perform')
    
    args = parser.parse_args()
    
    system = RealMadridKPISystem()
    
    if args.action == 'start':
        logger.info("🚀 Starting Real Madrid KPI System")
        
        if not system.check_prerequisites():
            sys.exit(1)
        
        system.create_required_directories()
        system.setup_environment_variables()
        
        if system.start_core_services():
            system.start_application_services()
            system.show_system_status()
        else:
            sys.exit(1)
    
    elif args.action == 'stop':
        system.stop_system()
    
    elif args.action == 'status':
        system.show_system_status()
    
    elif args.action == 'cleanup':
        system.cleanup_system()
    
    elif args.action == 'dev':
        if system.check_prerequisites():
            system.create_required_directories()
            system.setup_environment_variables()
            system.start_core_services()
            system.start_development_environment()
    
    elif args.action == 'dashboard':
        if system.check_prerequisites():
            system.setup_environment_variables()
            system.start_core_services()
            system.start_dashboard()
    
    elif args.action == 'collect-data':
        system.run_data_collection()
    
    elif args.action == 'analyze-kpi':
        system.run_kpi_analysis()
    
    elif args.action == 'optimize-algorithms':
        system.run_algorithm_optimization()
    
    elif args.action == 'full-analysis':
        logger.info("🎯 Running full Real Madrid analysis pipeline")
        
        if not system.check_prerequisites():
            sys.exit(1)
        
        system.create_required_directories()
        system.setup_environment_variables()
        
        if system.start_core_services():
            system.start_application_services()
            
            # Run complete analysis pipeline
            if system.run_data_collection():
                if system.run_kpi_analysis():
                    system.run_algorithm_optimization()
                    logger.info("✅ Full analysis pipeline completed successfully")
                else:
                    logger.error("❌ KPI analysis failed")
            else:
                logger.error("❌ Data collection failed")
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()

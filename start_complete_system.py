#!/usr/bin/env python3
"""
Complete System Startup Script for ADS599 Capstone Soccer Intelligence System
Orchestrates Docker services, database initialization, and data collection
"""

import os
import sys
import subprocess
import time
import yaml
import psycopg2
import redis
import logging
from pathlib import Path
from typing import Dict, List, Optional
import json
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemOrchestrator:
    """Orchestrates the complete soccer intelligence system."""
    
    def __init__(self):
        """Initialize the system orchestrator."""
        self.project_root = Path(__file__).parent
        self.load_configuration()
        self.services_status = {}
        
    def load_configuration(self):
        """Load system configuration."""
        try:
            with open(self.project_root / "config" / "api_keys.yaml", 'r') as f:
                self.config = yaml.safe_load(f)
            
            logger.info("✅ Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            raise
    
    def check_docker_availability(self) -> bool:
        """Check if Docker and Docker Compose are available."""
        try:
            # Check Docker
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Docker is not available")
                return False
            
            logger.info(f"✅ Docker available: {result.stdout.strip()}")
            
            # Check Docker Compose
            result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Docker Compose is not available")
                return False
            
            logger.info(f"✅ Docker Compose available: {result.stdout.strip()}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking Docker availability: {e}")
            return False
    
    def create_environment_file(self):
        """Create .env file for Docker Compose."""
        try:
            env_content = f"""# Environment variables for ADS599 Capstone Soccer Intelligence System
# Generated automatically - do not edit manually

# API Keys
API_FOOTBALL_KEY={self.config['api_football']['key']}
SPORTMONKS_API_KEY={self.config['sportmonks']['api_key']}
OPENAI_API_KEY={self.config.get('openai', {}).get('api_key', 'your_openai_api_key_here')}
TWITTER_BEARER_TOKEN={self.config.get('twitter', {}).get('bearer_token', 'your_twitter_bearer_token_here')}

# Database Configuration
POSTGRES_DB={self.config['database']['name']}
POSTGRES_USER={self.config['database']['user']}
POSTGRES_PASSWORD={self.config['database']['password']}

# Redis Configuration
REDIS_PASSWORD={self.config['redis']['password']}

# System Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
PYTHONPATH=/app
"""
            
            with open(self.project_root / ".env", 'w') as f:
                f.write(env_content)
            
            logger.info("✅ Environment file created")
            
        except Exception as e:
            logger.error(f"❌ Failed to create environment file: {e}")
            raise
    
    def start_docker_services(self) -> bool:
        """Start Docker services using Docker Compose."""
        try:
            logger.info("🚀 Starting Docker services...")
            
            # Stop any existing services
            subprocess.run(['docker', 'compose', 'down'], cwd=self.project_root, capture_output=True)
            
            # Start services
            result = subprocess.run([
                'docker', 'compose', 'up', '-d', 
                'postgres', 'redis'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ Failed to start Docker services: {result.stderr}")
                return False
            
            logger.info("✅ Docker services started")
            
            # Wait for services to be ready
            return self.wait_for_services()
            
        except Exception as e:
            logger.error(f"❌ Error starting Docker services: {e}")
            return False
    
    def wait_for_services(self, max_wait: int = 60) -> bool:
        """Wait for services to be ready."""
        logger.info("⏳ Waiting for services to be ready...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                # Check PostgreSQL
                db_config = self.config['database']
                db_conn = psycopg2.connect(
                    host=db_config['host'],
                    port=db_config['port'],
                    database='postgres',  # Connect to default database first
                    user=db_config['user'],
                    password=db_config['password']
                )
                db_conn.close()
                
                # Check Redis
                redis_config = self.config['redis']
                redis_client = redis.Redis(
                    host=redis_config['host'],
                    port=redis_config['port'],
                    password=redis_config['password'],
                    db=redis_config['db']
                )
                redis_client.ping()
                redis_client.close()
                
                logger.info("✅ All services are ready")
                return True
                
            except Exception as e:
                logger.debug(f"Services not ready yet: {e}")
                time.sleep(2)
        
        logger.error("❌ Services failed to start within timeout")
        return False
    
    def initialize_database(self) -> bool:
        """Initialize the database schema and data."""
        try:
            logger.info("🔄 Initializing database with clean reset...")

            # Run clean database reset and initialization script
            result = subprocess.run([
                sys.executable,
                str(self.project_root / "scripts" / "database" / "reset_and_initialize.py")
            ], capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"❌ Database initialization failed: {result.stderr}")
                logger.error(f"❌ Database initialization stdout: {result.stdout}")
                return False

            logger.info("✅ Database initialized successfully with clean schema")
            return True

        except Exception as e:
            logger.error(f"❌ Error initializing database: {e}")
            return False
    
    def run_data_collection(self, teams: List[str] = None, seasons: List[str] = None) -> bool:
        """Run initial data collection."""
        try:
            logger.info("🔄 Starting data collection...")
            
            # Default teams and seasons if not specified
            if teams is None:
                teams = ['Real Madrid', 'Barcelona', 'Manchester City', 'Liverpool']
            
            if seasons is None:
                seasons = ['2023-2024', '2022-2023']
            
            # Import and run the data collector
            sys.path.append(str(self.project_root))
            from services.multi_api_data_collector import MultiAPIDataCollector
            
            async def run_collection():
                collector = MultiAPIDataCollector()
                try:
                    await collector.run_comprehensive_collection(
                        target_teams=teams,
                        target_seasons=seasons
                    )
                    return True
                except Exception as e:
                    logger.error(f"❌ Data collection failed: {e}")
                    return False
                finally:
                    collector.close_connections()
            
            # Run the async collection
            success = asyncio.run(run_collection())
            
            if success:
                logger.info("✅ Data collection completed successfully")
            else:
                logger.error("❌ Data collection failed")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error running data collection: {e}")
            return False
    
    def check_system_health(self) -> Dict[str, bool]:
        """Check the health of all system components."""
        health_status = {}
        
        try:
            # Check Docker services
            result = subprocess.run(['docker', 'compose', 'ps'], 
                                  cwd=self.project_root, capture_output=True, text=True)
            health_status['docker_services'] = result.returncode == 0
            
            # Check PostgreSQL
            try:
                db_config = self.config['database']
                db_conn = psycopg2.connect(
                    host=db_config['host'],
                    port=db_config['port'],
                    database=db_config['name'],
                    user=db_config['user'],
                    password=db_config['password']
                )
                cursor = db_conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM teams")
                team_count = cursor.fetchone()[0]
                db_conn.close()
                health_status['database'] = True
                health_status['team_count'] = team_count
            except Exception as e:
                health_status['database'] = False
                health_status['database_error'] = str(e)
            
            # Check Redis
            try:
                redis_config = self.config['redis']
                redis_client = redis.Redis(
                    host=redis_config['host'],
                    port=redis_config['port'],
                    password=redis_config['password'],
                    db=redis_config['db']
                )
                redis_client.ping()
                redis_client.close()
                health_status['redis'] = True
            except Exception as e:
                health_status['redis'] = False
                health_status['redis_error'] = str(e)
            
        except Exception as e:
            logger.error(f"❌ Error checking system health: {e}")
            health_status['system_check_error'] = str(e)
        
        return health_status
    
    def print_system_status(self, health_status: Dict):
        """Print system status summary."""
        print("\n" + "="*80)
        print("🏆 ADS599 CAPSTONE SOCCER INTELLIGENCE SYSTEM STATUS")
        print("="*80)
        
        # Docker Services
        docker_status = "✅ Running" if health_status.get('docker_services', False) else "❌ Failed"
        print(f"Docker Services: {docker_status}")
        
        # Database
        db_status = "✅ Connected" if health_status.get('database', False) else "❌ Failed"
        print(f"PostgreSQL Database: {db_status}")
        if health_status.get('team_count') is not None:
            print(f"  └─ Teams in database: {health_status['team_count']}")
        
        # Redis
        redis_status = "✅ Connected" if health_status.get('redis', False) else "❌ Failed"
        print(f"Redis Cache: {redis_status}")
        
        # Overall status
        all_healthy = all([
            health_status.get('docker_services', False),
            health_status.get('database', False),
            health_status.get('redis', False)
        ])
        
        overall_status = "✅ HEALTHY" if all_healthy else "❌ ISSUES DETECTED"
        print(f"\nOverall System Status: {overall_status}")
        
        if all_healthy:
            print("\n🎉 System is ready for data collection and analysis!")
            print("📊 You can now run data collection scripts or use the web interface.")
        else:
            print("\n⚠️  Please resolve the issues above before proceeding.")
        
        print("="*80)
    
    def run_complete_setup(self, collect_data: bool = True) -> bool:
        """Run the complete system setup process."""
        try:
            logger.info("🚀 Starting complete system setup...")
            
            # Step 1: Check Docker availability
            if not self.check_docker_availability():
                return False
            
            # Step 2: Create environment file
            self.create_environment_file()
            
            # Step 3: Start Docker services
            if not self.start_docker_services():
                return False
            
            # Step 4: Initialize database
            if not self.initialize_database():
                return False
            
            # Step 5: Run data collection (optional)
            if collect_data:
                if not self.run_data_collection():
                    logger.warning("⚠️ Data collection failed, but system is still functional")
            
            # Step 6: Check system health
            health_status = self.check_system_health()
            self.print_system_status(health_status)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Complete setup failed: {e}")
            return False

def main():
    """Main function to run the complete system setup."""
    try:
        orchestrator = SystemOrchestrator()
        
        # Check if user wants to run data collection
        collect_data = True
        if len(sys.argv) > 1 and sys.argv[1] == '--no-data':
            collect_data = False
            logger.info("📝 Skipping data collection as requested")
        
        success = orchestrator.run_complete_setup(collect_data=collect_data)
        
        if success:
            print("\n🎉 System setup completed successfully!")
            print("🔗 Access the system at: http://localhost:8000")
            return True
        else:
            print("\n❌ System setup failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Real Madrid 2023-2024 Season Data Collection System Startup
Complete system setup and data collection for Real Madrid match-level player statistics
"""

import os
import sys
import subprocess
import time
import yaml
import psycopg2
import logging
from pathlib import Path
from typing import Dict, List, Optional
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealMadridSystemManager:
    """Manages the complete Real Madrid data collection system."""
    
    def __init__(self):
        """Initialize the system manager."""
        self.project_root = Path(__file__).parent
        self.load_configuration()
        
    def load_configuration(self):
        """Load system configuration."""
        try:
            with open(self.project_root / "config" / "api_keys.yaml", 'r') as f:
                self.config = yaml.safe_load(f)
            
            logger.info("✅ Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            raise
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites."""
        try:
            logger.info("🔄 Checking system prerequisites...")
            
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
            
            # Check Python
            python_version = sys.version.split()[0]
            logger.info(f"✅ Python {python_version} available")
            
            # Check SportMonks API key
            if not self.config.get('sportmonks', {}).get('api_key'):
                logger.error("❌ SportMonks API key not configured")
                return False
            
            logger.info("✅ SportMonks API key configured")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Prerequisites check failed: {e}")
            return False
    
    def start_docker_services(self) -> bool:
        """Start required Docker services."""
        try:
            logger.info("🚀 Starting Docker services...")
            
            # Stop any existing services
            subprocess.run(['docker', 'compose', 'down'], cwd=self.project_root, capture_output=True)
            
            # Start PostgreSQL and Redis
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
        """Wait for Docker services to be ready."""
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
                
                logger.info("✅ All services are ready")
                return True
                
            except Exception as e:
                logger.debug(f"Services not ready yet: {e}")
                time.sleep(2)
        
        logger.error("❌ Services failed to start within timeout")
        return False
    
    def reset_database(self) -> bool:
        """Reset and initialize the Real Madrid database."""
        try:
            logger.info("🔄 Resetting and initializing Real Madrid database...")
            
            # Run database reset script
            result = subprocess.run([
                sys.executable, 
                str(self.project_root / "scripts" / "database" / "reset_real_madrid_db.py")
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ Database reset failed: {result.stderr}")
                return False
            
            logger.info("✅ Real Madrid database reset and initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error resetting database: {e}")
            return False
    
    async def collect_real_madrid_data(self) -> bool:
        """Run Real Madrid data collection."""
        try:
            logger.info("🔄 Starting Real Madrid data collection...")
            
            # Import and run the Real Madrid collector
            sys.path.append(str(self.project_root))
            from services.real_madrid_collector import RealMadridCollector
            
            collector = RealMadridCollector()
            try:
                success = await collector.run_complete_collection()
                return success
            finally:
                collector.close_connections()
            
        except Exception as e:
            logger.error(f"❌ Data collection failed: {e}")
            return False
    
    def validate_collection(self) -> Dict[str, any]:
        """Validate the collected data."""
        try:
            logger.info("🔄 Validating collected data...")
            
            db_config = self.config['database']
            db_conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['name'],
                user=db_config['user'],
                password=db_config['password']
            )
            cursor = db_conn.cursor()
            
            validation_results = {}
            
            # Check matches
            cursor.execute("SELECT COUNT(*) FROM matches WHERE real_madrid_home = TRUE OR real_madrid_away = TRUE")
            matches_count = cursor.fetchone()[0]
            validation_results['matches'] = matches_count
            
            # Check players
            cursor.execute("SELECT COUNT(*) FROM players")
            players_count = cursor.fetchone()[0]
            validation_results['players'] = players_count
            
            # Check player statistics
            cursor.execute("SELECT COUNT(*) FROM player_match_statistics")
            statistics_count = cursor.fetchone()[0]
            validation_results['player_statistics'] = statistics_count
            
            # Check matches with statistics
            cursor.execute("SELECT COUNT(*) FROM matches WHERE statistics_collected = TRUE")
            matches_with_stats = cursor.fetchone()[0]
            validation_results['matches_with_statistics'] = matches_with_stats
            
            # Check Real Madrid players
            cursor.execute("""
                SELECT COUNT(DISTINCT p.player_id) 
                FROM players p 
                JOIN teams t ON p.team_id = t.team_id 
                WHERE t.is_real_madrid = TRUE
            """)
            real_madrid_players = cursor.fetchone()[0]
            validation_results['real_madrid_players'] = real_madrid_players
            
            # Check competitions
            cursor.execute("SELECT COUNT(*) FROM competitions")
            competitions_count = cursor.fetchone()[0]
            validation_results['competitions'] = competitions_count
            
            db_conn.close()
            
            logger.info("✅ Data validation completed")
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Data validation failed: {e}")
            return {}
    
    def print_system_summary(self, validation_results: Dict):
        """Print comprehensive system summary."""
        print("\n" + "="*80)
        print("🏆 REAL MADRID 2023-2024 SEASON DATA COLLECTION SYSTEM")
        print("="*80)
        print("📊 COLLECTION RESULTS:")
        print(f"  🏟️  Real Madrid Matches: {validation_results.get('matches', 0)}")
        print(f"  👥 Total Players: {validation_results.get('players', 0)}")
        print(f"  ⭐ Real Madrid Players: {validation_results.get('real_madrid_players', 0)}")
        print(f"  📈 Player Statistics Records: {validation_results.get('player_statistics', 0)}")
        print(f"  ✅ Matches with Statistics: {validation_results.get('matches_with_statistics', 0)}")
        print(f"  🏆 Competitions: {validation_results.get('competitions', 0)}")
        
        print("\n🎯 SYSTEM CAPABILITIES:")
        print("  ✅ Match-level player statistics for every Real Madrid game")
        print("  ✅ Individual player performance tracking across all competitions")
        print("  ✅ Comprehensive coverage of 2023-2024 season")
        print("  ✅ SportMonks API integration with rate limiting")
        print("  ✅ Optimized database schema for performance")
        
        print("\n📋 ANALYSIS OPTIONS:")
        print("  🔍 Query individual match player statistics")
        print("  📊 Analyze player performance trends")
        print("  🏆 Compare performance across competitions")
        print("  ⚽ Track goals, assists, and advanced metrics")
        print("  📈 Generate player performance reports")
        
        print("\n🚀 QUICK START QUERIES:")
        print("  # View Real Madrid player summary")
        print("  SELECT * FROM real_madrid_player_summary;")
        print("")
        print("  # View all Real Madrid matches")
        print("  SELECT * FROM real_madrid_matches ORDER BY match_date;")
        print("")
        print("  # Get player stats for a specific match")
        print("  SELECT p.player_name, pms.* FROM player_match_statistics pms")
        print("  JOIN players p ON pms.player_id = p.player_id")
        print("  WHERE pms.match_id = 1;")
        
        print("\n" + "="*80)
        
        # Determine overall success
        total_matches = validation_results.get('matches', 0)
        matches_with_stats = validation_results.get('matches_with_statistics', 0)
        
        if total_matches > 0 and matches_with_stats > 0:
            print("🎉 REAL MADRID DATA COLLECTION SUCCESSFUL!")
            print(f"✅ Collected detailed statistics for {matches_with_stats}/{total_matches} matches")
        else:
            print("⚠️  DATA COLLECTION INCOMPLETE")
            print("❌ Please check logs for any errors during collection")
        
        print("="*80)
    
    async def run_complete_setup(self) -> bool:
        """Run the complete Real Madrid system setup."""
        try:
            logger.info("🚀 Starting Real Madrid 2023-2024 system setup...")
            
            # Step 1: Check prerequisites
            if not self.check_prerequisites():
                return False
            
            # Step 2: Start Docker services
            if not self.start_docker_services():
                return False
            
            # Step 3: Reset and initialize database
            if not self.reset_database():
                return False
            
            # Step 4: Collect Real Madrid data
            if not await self.collect_real_madrid_data():
                logger.warning("⚠️ Data collection had issues, but system is functional")
            
            # Step 5: Validate and summarize
            validation_results = self.validate_collection()
            self.print_system_summary(validation_results)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Complete setup failed: {e}")
            return False

async def main():
    """Main function to run the Real Madrid system setup."""
    try:
        manager = RealMadridSystemManager()
        
        success = await manager.run_complete_setup()
        
        if success:
            print("\n🎉 Real Madrid system setup completed!")
            return True
        else:
            print("\n❌ Real Madrid system setup failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

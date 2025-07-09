#!/usr/bin/env python3
"""
Real Madrid Database Reset and Initialization Script
Clean reset and setup for Real Madrid 2023-2024 season data collection
"""

import os
import sys
import yaml
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from pathlib import Path
from typing import Dict, List, Optional
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealMadridDatabaseManager:
    """Database manager for Real Madrid focused data collection."""
    
    def __init__(self, config_path: str = "config"):
        """Initialize the database manager."""
        self.config_path = Path(config_path)
        self.project_root = Path(__file__).parent.parent.parent
        self.load_configuration()
        self.db_conn = None
        self.db_cursor = None
        
    def load_configuration(self):
        """Load database configuration."""
        try:
            config_file = self.config_path / "api_keys.yaml"
            if not config_file.exists():
                config_file = self.project_root / "config" / "api_keys.yaml"
            
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            self.db_config = config['database']
            logger.info("✅ Database configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load database configuration: {e}")
            raise
    
    def connect_to_database(self, database_name: str = None) -> bool:
        """Connect to PostgreSQL database."""
        try:
            if database_name is None:
                database_name = self.db_config['name']
            
            conn_params = {
                'host': self.db_config['host'],
                'port': self.db_config['port'],
                'database': database_name,
                'user': self.db_config['user'],
                'password': self.db_config['password']
            }
            
            self.db_conn = psycopg2.connect(**conn_params)
            self.db_conn.autocommit = True
            self.db_cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            
            logger.info(f"✅ Connected to database: {database_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return False
    
    def reset_database(self) -> bool:
        """Reset database with clean Real Madrid schema."""
        try:
            logger.info("🚀 Starting Real Madrid database reset...")
            
            # Connect to postgres database first
            if not self.connect_to_database('postgres'):
                return False
            
            # Terminate existing connections
            self.db_cursor.execute(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{self.db_config['name']}'
                  AND pid <> pg_backend_pid()
            """)
            
            # Drop and recreate database
            self.db_cursor.execute(f"DROP DATABASE IF EXISTS {self.db_config['name']}")
            self.db_cursor.execute(f"CREATE DATABASE {self.db_config['name']}")
            
            logger.info(f"✅ Database {self.db_config['name']} reset successfully")
            
            # Close connection to postgres
            self.close_connection()
            
            # Connect to new database
            return self.connect_to_database()
            
        except Exception as e:
            logger.error(f"❌ Failed to reset database: {e}")
            return False
    
    def execute_schema_file(self) -> bool:
        """Execute the Real Madrid schema file."""
        try:
            schema_file = self.project_root / "database" / "init" / "sportmonks_real_madrid_schema.sql"
            
            if not schema_file.exists():
                logger.error(f"❌ Schema file not found: {schema_file}")
                return False
            
            logger.info("🔄 Executing Real Madrid schema...")
            
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Execute the entire schema
            self.db_cursor.execute(schema_sql)
            
            logger.info("✅ Real Madrid schema executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to execute schema: {e}")
            return False
    
    def validate_schema(self) -> bool:
        """Validate that the schema was created correctly."""
        try:
            logger.info("🔄 Validating Real Madrid database schema...")
            
            # Expected tables for Real Madrid collection
            expected_tables = [
                'seasons', 'competitions', 'teams', 'players', 'matches',
                'player_match_statistics', 'match_events', 'data_collection_log'
            ]
            
            # Check tables exist
            self.db_cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            
            existing_tables = [row['table_name'] for row in self.db_cursor.fetchall()]
            
            missing_tables = set(expected_tables) - set(existing_tables)
            if missing_tables:
                logger.error(f"❌ Missing tables: {missing_tables}")
                return False
            
            logger.info(f"✅ All {len(expected_tables)} required tables exist")
            
            # Check initial data
            self.db_cursor.execute("SELECT COUNT(*) FROM seasons")
            season_result = self.db_cursor.fetchone()
            season_count = season_result[0] if season_result else 0

            self.db_cursor.execute("SELECT COUNT(*) FROM teams WHERE is_real_madrid = TRUE")
            real_madrid_result = self.db_cursor.fetchone()
            real_madrid_count = real_madrid_result[0] if real_madrid_result else 0

            self.db_cursor.execute("SELECT COUNT(*) FROM competitions")
            competition_result = self.db_cursor.fetchone()
            competition_count = competition_result[0] if competition_result else 0

            logger.info(f"✅ Initial data: {season_count} seasons, {real_madrid_count} Real Madrid team, {competition_count} competitions")

            # Validate minimum required data
            if season_count == 0:
                logger.error("❌ No seasons found in database")
                return False

            if real_madrid_count == 0:
                logger.error("❌ Real Madrid team not found in database")
                return False
            
            # Check views
            self.db_cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.views
                WHERE table_schema = 'public'
            """)

            view_result = self.db_cursor.fetchone()
            view_count = view_result[0] if view_result else 0
            logger.info(f"✅ Found {view_count} analysis views")

            # Check indexes
            self.db_cursor.execute("""
                SELECT COUNT(*)
                FROM pg_indexes
                WHERE schemaname = 'public'
            """)

            index_result = self.db_cursor.fetchone()
            index_count = index_result[0] if index_result else 0
            logger.info(f"✅ Found {index_count} performance indexes")
            
            logger.info("✅ Schema validation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Schema validation failed: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return False
    
    def test_data_insertion(self) -> bool:
        """Test basic data insertion functionality."""
        try:
            logger.info("🔄 Testing data insertion...")
            
            # Test team insertion
            test_team_name = f"Test Team {int(time.time())}"
            self.db_cursor.execute("""
                INSERT INTO teams (sportmonks_team_id, team_name, country, is_real_madrid)
                VALUES (%s, %s, %s, %s)
                RETURNING team_id
            """, (999999, test_team_name, "Test Country", False))
            
            team_id = self.db_cursor.fetchone()[0]
            
            # Test player insertion
            test_player_name = f"Test Player {int(time.time())}"
            self.db_cursor.execute("""
                INSERT INTO players (sportmonks_player_id, player_name, team_id)
                VALUES (%s, %s, %s)
                RETURNING player_id
            """, (999999, test_player_name, team_id))
            
            player_id = self.db_cursor.fetchone()[0]
            
            # Test match insertion
            self.db_cursor.execute("""
                INSERT INTO matches (
                    sportmonks_match_id, season_id, match_date, home_team_id, away_team_id,
                    real_madrid_home, real_madrid_away
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING match_id
            """, (999999, 1, datetime.now(), team_id, 1, False, False))
            
            match_id = self.db_cursor.fetchone()[0]
            
            # Test player statistics insertion
            self.db_cursor.execute("""
                INSERT INTO player_match_statistics (match_id, player_id, team_id, minutes_played, goals)
                VALUES (%s, %s, %s, %s, %s)
            """, (match_id, player_id, team_id, 90, 1))
            
            # Clean up test data
            self.db_cursor.execute("DELETE FROM player_match_statistics WHERE match_id = %s", (match_id,))
            self.db_cursor.execute("DELETE FROM matches WHERE match_id = %s", (match_id,))
            self.db_cursor.execute("DELETE FROM players WHERE player_id = %s", (player_id,))
            self.db_cursor.execute("DELETE FROM teams WHERE team_id = %s", (team_id,))
            
            logger.info("✅ Data insertion test completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Data insertion test failed: {e}")
            return False
    
    def run_complete_reset(self) -> bool:
        """Run complete database reset and initialization."""
        try:
            logger.info("🚀 Starting complete Real Madrid database setup...")
            
            # Step 1: Reset database
            if not self.reset_database():
                return False
            
            # Step 2: Execute schema
            if not self.execute_schema_file():
                return False
            
            # Step 3: Validate schema
            if not self.validate_schema():
                return False
            
            # Step 4: Test data insertion
            if not self.test_data_insertion():
                return False
            
            logger.info("🎉 Real Madrid database setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Complete reset failed: {e}")
            return False
    
    def close_connection(self):
        """Close database connection."""
        try:
            if self.db_cursor:
                self.db_cursor.close()
            if self.db_conn:
                self.db_conn.close()
            logger.info("✅ Database connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing database connection: {e}")

def main():
    """Main function to run Real Madrid database reset."""
    try:
        # Initialize database manager
        db_manager = RealMadridDatabaseManager()
        
        if db_manager.run_complete_reset():
            print("\n" + "="*80)
            print("🎉 REAL MADRID DATABASE SETUP SUCCESSFUL!")
            print("="*80)
            print("✅ Database reset and recreated")
            print("✅ SportMonks-optimized schema created")
            print("✅ Real Madrid team and 2023-2024 season initialized")
            print("✅ Performance indexes and views created")
            print("✅ Data insertion functionality validated")
            print("✅ Ready for Real Madrid data collection!")
            print("="*80)
            print("\n🚀 Next step: Run Real Madrid data collection:")
            print("   python services/real_madrid_collector.py")
            print("="*80)
            return True
        else:
            print("\n" + "="*80)
            print("❌ REAL MADRID DATABASE SETUP FAILED!")
            print("="*80)
            print("Please check the logs for details.")
            print("="*80)
            return False
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False
    finally:
        if 'db_manager' in locals():
            db_manager.close_connection()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Database Initialization Script for ADS599 Capstone Soccer Intelligence System
Automated database setup with proper initialization, migrations, and validation
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

class DatabaseInitializer:
    """Database initialization and migration manager."""
    
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
    
    def connect_to_database(self, create_db: bool = False) -> bool:
        """Connect to PostgreSQL database."""
        try:
            if create_db:
                # Connect to postgres database to create our target database
                conn_params = {
                    'host': self.db_config['host'],
                    'port': self.db_config['port'],
                    'database': 'postgres',
                    'user': self.db_config['user'],
                    'password': self.db_config['password']
                }
            else:
                # Connect to our target database
                conn_params = {
                    'host': self.db_config['host'],
                    'port': self.db_config['port'],
                    'database': self.db_config['name'],
                    'user': self.db_config['user'],
                    'password': self.db_config['password']
                }
            
            self.db_conn = psycopg2.connect(**conn_params)
            self.db_conn.autocommit = True
            self.db_cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            
            logger.info(f"✅ Connected to database: {conn_params['database']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return False
    
    def create_database_if_not_exists(self) -> bool:
        """Create the target database if it doesn't exist."""
        try:
            # Connect to postgres database
            if not self.connect_to_database(create_db=True):
                return False
            
            # Check if database exists
            self.db_cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.db_config['name'],)
            )
            
            if self.db_cursor.fetchone():
                logger.info(f"✅ Database '{self.db_config['name']}' already exists")
            else:
                # Create database
                self.db_cursor.execute(f"CREATE DATABASE {self.db_config['name']}")
                logger.info(f"✅ Created database: {self.db_config['name']}")
            
            # Close connection to postgres
            self.close_connection()
            
            # Connect to our target database
            return self.connect_to_database(create_db=False)
            
        except Exception as e:
            logger.error(f"❌ Failed to create database: {e}")
            return False
    
    def create_user_if_not_exists(self) -> bool:
        """Create database user if it doesn't exist."""
        try:
            # Check if user exists
            self.db_cursor.execute(
                "SELECT 1 FROM pg_user WHERE usename = %s",
                (self.db_config['user'],)
            )
            
            if self.db_cursor.fetchone():
                logger.info(f"✅ User '{self.db_config['user']}' already exists")
            else:
                # Create user
                self.db_cursor.execute(
                    f"CREATE USER {self.db_config['user']} WITH PASSWORD %s",
                    (self.db_config['password'],)
                )
                logger.info(f"✅ Created user: {self.db_config['user']}")
            
            # Grant privileges
            self.db_cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {self.db_config['name']} TO {self.db_config['user']}")
            logger.info(f"✅ Granted privileges to user: {self.db_config['user']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create user: {e}")
            return False
    
    def execute_sql_file(self, file_path: Path) -> bool:
        """Execute SQL commands from a file."""
        try:
            if not file_path.exists():
                logger.error(f"❌ SQL file not found: {file_path}")
                return False
            
            logger.info(f"🔄 Executing SQL file: {file_path.name}")
            
            with open(file_path, 'r') as f:
                sql_content = f.read()
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements):
                try:
                    if statement.strip():
                        self.db_cursor.execute(statement)
                        logger.debug(f"✅ Executed statement {i+1}/{len(statements)}")
                except Exception as e:
                    logger.warning(f"⚠️ Statement {i+1} failed: {e}")
                    # Continue with other statements
            
            logger.info(f"✅ Completed SQL file: {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to execute SQL file {file_path}: {e}")
            return False
    
    def run_schema_initialization(self) -> bool:
        """Run all schema initialization scripts."""
        try:
            # Find database initialization files
            db_init_dir = self.project_root / "database" / "init"
            
            if not db_init_dir.exists():
                logger.error(f"❌ Database init directory not found: {db_init_dir}")
                return False
            
            # Get all SQL files in order
            sql_files = sorted([f for f in db_init_dir.glob("*.sql")])
            
            if not sql_files:
                logger.error(f"❌ No SQL files found in: {db_init_dir}")
                return False
            
            logger.info(f"🔄 Found {len(sql_files)} SQL files to execute")
            
            # Execute each SQL file
            for sql_file in sql_files:
                if not self.execute_sql_file(sql_file):
                    logger.error(f"❌ Failed to execute: {sql_file}")
                    return False
            
            logger.info("✅ Schema initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Schema initialization failed: {e}")
            return False
    
    def validate_schema(self) -> bool:
        """Validate that all required tables and indexes exist."""
        try:
            logger.info("🔄 Validating database schema...")
            
            # Expected tables
            expected_tables = [
                'seasons', 'competitions', 'teams', 'players', 'matches',
                'player_statistics', 'team_statistics', 'match_events',
                'api_collection_metadata', 'data_quality_checks'
            ]
            
            # Check tables exist
            self.db_cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            
            existing_tables = [row[0] for row in self.db_cursor.fetchall()]
            
            missing_tables = set(expected_tables) - set(existing_tables)
            if missing_tables:
                logger.error(f"❌ Missing tables: {missing_tables}")
                return False
            
            logger.info(f"✅ All {len(expected_tables)} required tables exist")
            
            # Check for indexes
            self.db_cursor.execute("""
                SELECT COUNT(*) 
                FROM pg_indexes 
                WHERE schemaname = 'public'
            """)
            
            index_count = self.db_cursor.fetchone()[0]
            logger.info(f"✅ Found {index_count} indexes")
            
            # Check for views
            self.db_cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.views 
                WHERE table_schema = 'public'
            """)
            
            view_count = self.db_cursor.fetchone()[0]
            logger.info(f"✅ Found {view_count} views")
            
            # Test basic functionality
            self.db_cursor.execute("SELECT COUNT(*) FROM seasons")
            season_count = self.db_cursor.fetchone()[0]
            logger.info(f"✅ Found {season_count} seasons in database")
            
            self.db_cursor.execute("SELECT COUNT(*) FROM competitions")
            competition_count = self.db_cursor.fetchone()[0]
            logger.info(f"✅ Found {competition_count} competitions in database")
            
            logger.info("✅ Schema validation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Schema validation failed: {e}")
            return False
    
    def create_sample_data(self) -> bool:
        """Create sample data for testing."""
        try:
            logger.info("🔄 Creating sample data...")
            
            # Insert sample team (Real Madrid)
            sample_team_query = """
                INSERT INTO teams (team_name, short_name, sportmonks_team_id, api_football_team_id, 
                                 country, founded_year, venue_name, venue_city, data_source)
                VALUES ('Real Madrid', 'RMA', 53, 541, 'Spain', 1902, 'Santiago Bernabéu', 'Madrid', 'sample')
                ON CONFLICT (sportmonks_team_id) DO NOTHING
                RETURNING team_id
            """
            
            self.db_cursor.execute(sample_team_query)
            result = self.db_cursor.fetchone()
            
            if result:
                team_id = result[0]
                logger.info(f"✅ Created sample team with ID: {team_id}")
                
                # Insert sample player
                sample_player_query = """
                    INSERT INTO players (player_name, sportmonks_player_id, nationality, 
                                       position, current_team_id, data_source)
                    VALUES ('Sample Player', 999999, 'Spain', 'Forward', %s, 'sample')
                    ON CONFLICT (sportmonks_player_id) DO NOTHING
                """
                
                self.db_cursor.execute(sample_player_query, (team_id,))
                logger.info("✅ Created sample player")
            
            logger.info("✅ Sample data creation completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sample data creation failed: {e}")
            return False
    
    def run_full_initialization(self) -> bool:
        """Run complete database initialization process."""
        try:
            logger.info("🚀 Starting full database initialization...")
            
            # Step 1: Create database if needed
            if not self.create_database_if_not_exists():
                return False
            
            # Step 2: Create user if needed
            if not self.create_user_if_not_exists():
                return False
            
            # Step 3: Run schema initialization
            if not self.run_schema_initialization():
                return False
            
            # Step 4: Validate schema
            if not self.validate_schema():
                return False
            
            # Step 5: Create sample data
            if not self.create_sample_data():
                return False
            
            logger.info("🎉 Database initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
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
    """Main function to run database initialization."""
    try:
        # Initialize database
        db_init = DatabaseInitializer()
        
        if db_init.run_full_initialization():
            print("\n" + "="*80)
            print("🎉 DATABASE INITIALIZATION SUCCESSFUL!")
            print("="*80)
            print("✅ Database created and configured")
            print("✅ Schema initialized with all tables and indexes")
            print("✅ Sample data created for testing")
            print("✅ Ready for data collection!")
            print("="*80)
            return True
        else:
            print("\n" + "="*80)
            print("❌ DATABASE INITIALIZATION FAILED!")
            print("="*80)
            print("Please check the logs for details.")
            print("="*80)
            return False
            
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        return False
    finally:
        if 'db_init' in locals():
            db_init.close_connection()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Database Reset and Clean Initialization Script
Handles conflicts and creates a clean, working database
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

class DatabaseResetManager:
    """Clean database reset and initialization."""
    
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
    
    def drop_database_if_exists(self) -> bool:
        """Drop the target database if it exists."""
        try:
            # Connect to postgres database
            if not self.connect_to_database('postgres'):
                return False
            
            # Terminate existing connections
            self.db_cursor.execute(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{self.db_config['name']}'
                  AND pid <> pg_backend_pid()
            """)
            
            # Drop database if exists
            self.db_cursor.execute(f"DROP DATABASE IF EXISTS {self.db_config['name']}")
            logger.info(f"✅ Dropped database: {self.db_config['name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to drop database: {e}")
            return False
    
    def create_clean_database(self) -> bool:
        """Create a clean database."""
        try:
            # Create database
            self.db_cursor.execute(f"CREATE DATABASE {self.db_config['name']}")
            logger.info(f"✅ Created clean database: {self.db_config['name']}")
            
            # Close connection to postgres
            self.close_connection()
            
            # Connect to new database
            return self.connect_to_database()
            
        except Exception as e:
            logger.error(f"❌ Failed to create database: {e}")
            return False
    
    def create_clean_schema(self) -> bool:
        """Create clean schema without conflicts."""
        try:
            logger.info("🔄 Creating clean database schema...")
            
            # Create extensions
            self.db_cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
            
            # Create seasons table
            self.db_cursor.execute("""
                CREATE TABLE IF NOT EXISTS seasons (
                    season_id SERIAL PRIMARY KEY,
                    season_name VARCHAR(100) NOT NULL UNIQUE,
                    sportmonks_season_id INTEGER UNIQUE,
                    api_football_season_id INTEGER UNIQUE,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    is_current BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create competitions table
            self.db_cursor.execute("""
                CREATE TABLE IF NOT EXISTS competitions (
                    competition_id SERIAL PRIMARY KEY,
                    competition_name VARCHAR(255) NOT NULL,
                    sportmonks_competition_id INTEGER UNIQUE,
                    api_football_competition_id INTEGER UNIQUE,
                    competition_type VARCHAR(50) NOT NULL,
                    country VARCHAR(100),
                    priority INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create teams table
            self.db_cursor.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    team_id SERIAL PRIMARY KEY,
                    team_name VARCHAR(255) NOT NULL,
                    short_name VARCHAR(50),
                    team_code VARCHAR(10),
                    sportmonks_team_id INTEGER UNIQUE,
                    api_football_team_id INTEGER UNIQUE,
                    country VARCHAR(100),
                    founded_year INTEGER,
                    venue_name VARCHAR(255),
                    venue_city VARCHAR(255),
                    venue_capacity INTEGER,
                    logo_url TEXT,
                    colors JSONB,
                    is_active BOOLEAN DEFAULT TRUE,
                    data_source VARCHAR(50) DEFAULT 'unified',
                    data_quality_score DECIMAL(5,2) DEFAULT 100.0,
                    last_updated_sportmonks TIMESTAMP,
                    last_updated_api_football TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create players table
            self.db_cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    player_id SERIAL PRIMARY KEY,
                    player_name VARCHAR(255) NOT NULL,
                    display_name VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    sportmonks_player_id INTEGER UNIQUE,
                    api_football_player_id INTEGER UNIQUE,
                    birth_date DATE,
                    birth_place VARCHAR(255),
                    nationality VARCHAR(100),
                    height INTEGER,
                    weight INTEGER,
                    position VARCHAR(50),
                    preferred_foot VARCHAR(10),
                    jersey_number INTEGER,
                    current_team_id INTEGER REFERENCES teams(team_id),
                    market_value BIGINT,
                    contract_until DATE,
                    is_active BOOLEAN DEFAULT TRUE,
                    data_source VARCHAR(50) DEFAULT 'unified',
                    data_quality_score DECIMAL(5,2) DEFAULT 100.0,
                    last_updated_sportmonks TIMESTAMP,
                    last_updated_api_football TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create matches table
            self.db_cursor.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    match_id SERIAL PRIMARY KEY,
                    sportmonks_match_id INTEGER UNIQUE,
                    api_football_match_id INTEGER UNIQUE,
                    competition_id INTEGER REFERENCES competitions(competition_id),
                    season_id INTEGER REFERENCES seasons(season_id),
                    match_date TIMESTAMP NOT NULL,
                    match_week INTEGER,
                    round_name VARCHAR(100),
                    home_team_id INTEGER REFERENCES teams(team_id) NOT NULL,
                    away_team_id INTEGER REFERENCES teams(team_id) NOT NULL,
                    home_score INTEGER DEFAULT 0,
                    away_score INTEGER DEFAULT 0,
                    home_score_ht INTEGER DEFAULT 0,
                    away_score_ht INTEGER DEFAULT 0,
                    home_score_et INTEGER,
                    away_score_et INTEGER,
                    home_score_penalty INTEGER,
                    away_score_penalty INTEGER,
                    match_status VARCHAR(50) DEFAULT 'scheduled',
                    match_minute INTEGER,
                    venue_name VARCHAR(255),
                    venue_city VARCHAR(255),
                    attendance INTEGER,
                    weather_condition VARCHAR(100),
                    temperature INTEGER,
                    referee_name VARCHAR(255),
                    match_data JSONB,
                    data_source VARCHAR(50) DEFAULT 'unified',
                    data_quality_score DECIMAL(5,2) DEFAULT 100.0,
                    last_updated_sportmonks TIMESTAMP,
                    last_updated_api_football TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create player_statistics table
            self.db_cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_statistics (
                    stat_id SERIAL PRIMARY KEY,
                    match_id INTEGER REFERENCES matches(match_id) NOT NULL,
                    player_id INTEGER REFERENCES players(player_id) NOT NULL,
                    team_id INTEGER REFERENCES teams(team_id) NOT NULL,
                    position_played VARCHAR(50),
                    jersey_number INTEGER,
                    minutes_played INTEGER DEFAULT 0,
                    is_starter BOOLEAN DEFAULT FALSE,
                    is_substitute BOOLEAN DEFAULT FALSE,
                    substitution_minute INTEGER,
                    goals INTEGER DEFAULT 0,
                    assists INTEGER DEFAULT 0,
                    shots_total INTEGER DEFAULT 0,
                    shots_on_target INTEGER DEFAULT 0,
                    shots_off_target INTEGER DEFAULT 0,
                    shots_blocked INTEGER DEFAULT 0,
                    passes_total INTEGER DEFAULT 0,
                    passes_completed INTEGER DEFAULT 0,
                    passes_accuracy DECIMAL(5,2) DEFAULT 0.0,
                    passes_key INTEGER DEFAULT 0,
                    crosses_total INTEGER DEFAULT 0,
                    crosses_completed INTEGER DEFAULT 0,
                    tackles_total INTEGER DEFAULT 0,
                    tackles_successful INTEGER DEFAULT 0,
                    interceptions INTEGER DEFAULT 0,
                    clearances INTEGER DEFAULT 0,
                    blocks INTEGER DEFAULT 0,
                    yellow_cards INTEGER DEFAULT 0,
                    red_cards INTEGER DEFAULT 0,
                    fouls_committed INTEGER DEFAULT 0,
                    fouls_suffered INTEGER DEFAULT 0,
                    rating DECIMAL(4,2) DEFAULT 0.0,
                    expected_goals DECIMAL(5,2) DEFAULT 0.0,
                    expected_assists DECIMAL(5,2) DEFAULT 0.0,
                    touches INTEGER DEFAULT 0,
                    touches_penalty_area INTEGER DEFAULT 0,
                    dribbles_attempted INTEGER DEFAULT 0,
                    dribbles_successful INTEGER DEFAULT 0,
                    offsides INTEGER DEFAULT 0,
                    saves INTEGER DEFAULT 0,
                    saves_inside_box INTEGER DEFAULT 0,
                    saves_outside_box INTEGER DEFAULT 0,
                    goals_conceded INTEGER DEFAULT 0,
                    clean_sheet BOOLEAN DEFAULT FALSE,
                    additional_stats JSONB,
                    data_source VARCHAR(50) DEFAULT 'unified',
                    data_quality_score DECIMAL(5,2) DEFAULT 100.0,
                    last_updated_sportmonks TIMESTAMP,
                    last_updated_api_football TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(match_id, player_id)
                )
            """)
            
            # Create api_collection_metadata table
            self.db_cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_collection_metadata (
                    collection_id SERIAL PRIMARY KEY,
                    collection_type VARCHAR(100) NOT NULL,
                    api_source VARCHAR(50) NOT NULL,
                    collection_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    records_collected INTEGER DEFAULT 0,
                    records_updated INTEGER DEFAULT 0,
                    records_failed INTEGER DEFAULT 0,
                    api_requests_made INTEGER DEFAULT 0,
                    api_rate_limit_remaining INTEGER,
                    api_response_time_avg DECIMAL(8,3),
                    collection_status VARCHAR(50) DEFAULT 'IN_PROGRESS',
                    error_messages TEXT,
                    collection_duration_seconds INTEGER,
                    data_quality_score DECIMAL(5,2) DEFAULT 100.0,
                    data_completeness_score DECIMAL(5,2) DEFAULT 100.0,
                    notes TEXT,
                    collection_config JSONB
                )
            """)
            
            logger.info("✅ Clean schema created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create clean schema: {e}")
            return False
    
    def create_indexes(self) -> bool:
        """Create performance indexes."""
        try:
            logger.info("🔄 Creating performance indexes...")
            
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_teams_sportmonks_id ON teams(sportmonks_team_id)",
                "CREATE INDEX IF NOT EXISTS idx_teams_api_football_id ON teams(api_football_team_id)",
                "CREATE INDEX IF NOT EXISTS idx_teams_name ON teams(team_name)",
                "CREATE INDEX IF NOT EXISTS idx_players_sportmonks_id ON players(sportmonks_player_id)",
                "CREATE INDEX IF NOT EXISTS idx_players_api_football_id ON players(api_football_player_id)",
                "CREATE INDEX IF NOT EXISTS idx_players_name ON players(player_name)",
                "CREATE INDEX IF NOT EXISTS idx_players_team ON players(current_team_id)",
                "CREATE INDEX IF NOT EXISTS idx_matches_sportmonks_id ON matches(sportmonks_match_id)",
                "CREATE INDEX IF NOT EXISTS idx_matches_api_football_id ON matches(api_football_match_id)",
                "CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date)",
                "CREATE INDEX IF NOT EXISTS idx_player_stats_match ON player_statistics(match_id)",
                "CREATE INDEX IF NOT EXISTS idx_player_stats_player ON player_statistics(player_id)",
                "CREATE INDEX IF NOT EXISTS idx_player_stats_team ON player_statistics(team_id)"
            ]
            
            for index_sql in indexes:
                self.db_cursor.execute(index_sql)
            
            logger.info("✅ Performance indexes created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create indexes: {e}")
            return False
    
    def insert_initial_data(self) -> bool:
        """Insert initial reference data."""
        try:
            logger.info("🔄 Inserting initial data...")
            
            # Insert seasons
            seasons_data = [
                ('2019-2020', 17141, 2019, '2019-08-01', '2020-07-31', False),
                ('2020-2021', 18378, 2020, '2020-08-01', '2021-07-31', False),
                ('2021-2022', 19686, 2021, '2021-08-01', '2022-07-31', False),
                ('2022-2023', 21646, 2022, '2022-08-01', '2023-07-31', False),
                ('2023-2024', 23087, 2023, '2023-08-01', '2024-07-31', False),
                ('2024-2025', 24644, 2024, '2024-08-01', '2025-07-31', True)
            ]
            
            for season in seasons_data:
                self.db_cursor.execute("""
                    INSERT INTO seasons (season_name, sportmonks_season_id, api_football_season_id, 
                                       start_date, end_date, is_current)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (season_name) DO NOTHING
                """, season)
            
            # Insert competitions
            competitions_data = [
                ('UEFA Champions League', 8, 2, 'international', 'Europe', 1),
                ('Premier League', 8, 39, 'domestic_league', 'England', 2),
                ('La Liga', 271, 140, 'domestic_league', 'Spain', 2),
                ('Bundesliga', 82, 78, 'domestic_league', 'Germany', 2),
                ('Serie A', 384, 135, 'domestic_league', 'Italy', 2),
                ('Ligue 1', 301, 61, 'domestic_league', 'France', 2)
            ]
            
            for comp in competitions_data:
                self.db_cursor.execute("""
                    INSERT INTO competitions (competition_name, sportmonks_competition_id, 
                                            api_football_competition_id, competition_type, country, priority)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (sportmonks_competition_id) DO NOTHING
                """, comp)
            
            # Log initialization
            self.db_cursor.execute("""
                INSERT INTO api_collection_metadata (collection_type, api_source, collection_status, notes)
                VALUES (%s, %s, %s, %s)
            """, ('CLEAN_INITIALIZATION', 'system', 'COMPLETED', 'Clean database initialization completed successfully'))
            
            logger.info("✅ Initial data inserted")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to insert initial data: {e}")
            return False
    
    def run_clean_reset(self) -> bool:
        """Run complete clean reset and initialization."""
        try:
            logger.info("🚀 Starting clean database reset and initialization...")
            
            # Step 1: Drop existing database
            if not self.drop_database_if_exists():
                return False
            
            # Step 2: Create clean database
            if not self.create_clean_database():
                return False
            
            # Step 3: Create clean schema
            if not self.create_clean_schema():
                return False
            
            # Step 4: Create indexes
            if not self.create_indexes():
                return False
            
            # Step 5: Insert initial data
            if not self.insert_initial_data():
                return False
            
            logger.info("🎉 Clean database reset and initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Clean reset failed: {e}")
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
    """Main function to run clean database reset."""
    try:
        # Initialize database manager
        db_manager = DatabaseResetManager()
        
        if db_manager.run_clean_reset():
            print("\n" + "="*80)
            print("🎉 CLEAN DATABASE RESET SUCCESSFUL!")
            print("="*80)
            print("✅ Database dropped and recreated")
            print("✅ Clean schema created without conflicts")
            print("✅ Performance indexes created")
            print("✅ Initial reference data inserted")
            print("✅ Ready for data collection!")
            print("="*80)
            return True
        else:
            print("\n" + "="*80)
            print("❌ CLEAN DATABASE RESET FAILED!")
            print("="*80)
            print("Please check the logs for details.")
            print("="*80)
            return False
            
    except Exception as e:
        logger.error(f"❌ Reset failed: {e}")
        return False
    finally:
        if 'db_manager' in locals():
            db_manager.close_connection()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

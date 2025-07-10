#!/usr/bin/env python3
"""
PostgreSQL Schema Initialization for Sports Analytics Engine
Creates the complete relational database schema for soccer intelligence system
"""

import psycopg2
import psycopg2.extras
import yaml
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PostgreSQLSchemaInitializer:
    """Initialize PostgreSQL schema for sports analytics."""
    
    def __init__(self):
        """Initialize with database configuration."""
        self.load_config()
        self.setup_connection()
    
    def load_config(self):
        """Load database configuration."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'api_keys.yaml')
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            self.db_config = config['database']
            logger.info("Configuration loaded successfully")
        except FileNotFoundError:
            logger.error("Config file not found")
            raise
    
    def setup_connection(self):
        """Setup PostgreSQL connection."""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['name'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            logger.info("PostgreSQL connection established")
        except psycopg2.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def create_schema(self):
        """Create complete database schema."""
        logger.info("Creating database schema...")
        
        # Drop existing tables (in reverse dependency order)
        drop_tables = [
            "player_match_statistics",
            "team_match_statistics", 
            "match_events",
            "lineups",
            "player_transfers",
            "player_contracts",
            "fixtures",
            "squad_members",
            "team_seasons",
            "players",
            "teams",
            "venues",
            "competitions",
            "seasons"
        ]
        
        for table in drop_tables:
            try:
                self.cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                logger.info(f"Dropped table: {table}")
            except Exception as e:
                logger.warning(f"Could not drop table {table}: {e}")
        
        # Create tables in dependency order
        self.create_reference_tables()
        self.create_entity_tables()
        self.create_relationship_tables()
        self.create_statistics_tables()
        self.create_business_tables()
        
        # Commit all changes
        self.conn.commit()
        logger.info("Database schema created successfully")
    
    def create_reference_tables(self):
        """Create reference tables."""
        logger.info("Creating reference tables...")
        
        # Seasons table
        self.cursor.execute("""
            CREATE TABLE seasons (
                id SERIAL PRIMARY KEY,
                season_name VARCHAR(20) NOT NULL UNIQUE,
                start_date DATE,
                end_date DATE,
                is_current BOOLEAN DEFAULT FALSE,
                sportmonks_id INTEGER,
                api_football_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Competitions table
        self.cursor.execute("""
            CREATE TABLE competitions (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                country VARCHAR(50),
                type VARCHAR(50),
                level INTEGER,
                sportmonks_id INTEGER,
                api_football_id INTEGER,
                logo_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Venues table
        self.cursor.execute("""
            CREATE TABLE venues (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                city VARCHAR(50),
                country VARCHAR(50),
                capacity INTEGER,
                surface VARCHAR(20),
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        logger.info("Reference tables created")
    
    def create_entity_tables(self):
        """Create main entity tables."""
        logger.info("Creating entity tables...")
        
        # Teams table
        self.cursor.execute("""
            CREATE TABLE teams (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                short_name VARCHAR(10),
                code VARCHAR(5),
                country VARCHAR(50),
                founded_year INTEGER,
                venue_id INTEGER REFERENCES venues(id),
                logo_url TEXT,
                sportmonks_id INTEGER,
                api_football_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Players table
        self.cursor.execute("""
            CREATE TABLE players (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                display_name VARCHAR(100) NOT NULL,
                date_of_birth DATE,
                nationality VARCHAR(50),
                height INTEGER,
                weight INTEGER,
                position VARCHAR(20),
                sportmonks_id INTEGER,
                api_football_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        logger.info("Entity tables created")
    
    def create_relationship_tables(self):
        """Create relationship tables."""
        logger.info("Creating relationship tables...")
        
        # Team seasons table
        self.cursor.execute("""
            CREATE TABLE team_seasons (
                id SERIAL PRIMARY KEY,
                team_id INTEGER NOT NULL REFERENCES teams(id),
                season_id INTEGER NOT NULL REFERENCES seasons(id),
                competition_id INTEGER NOT NULL REFERENCES competitions(id),
                position INTEGER,
                points INTEGER,
                matches_played INTEGER,
                wins INTEGER,
                draws INTEGER,
                losses INTEGER,
                goals_for INTEGER,
                goals_against INTEGER,
                goal_difference INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(team_id, season_id, competition_id)
            )
        """)
        
        # Squad members table
        self.cursor.execute("""
            CREATE TABLE squad_members (
                id SERIAL PRIMARY KEY,
                player_id INTEGER NOT NULL REFERENCES players(id),
                team_id INTEGER NOT NULL REFERENCES teams(id),
                season_id INTEGER NOT NULL REFERENCES seasons(id),
                jersey_number INTEGER,
                position VARCHAR(20),
                is_captain BOOLEAN DEFAULT FALSE,
                contract_start DATE,
                contract_end DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(player_id, team_id, season_id)
            )
        """)
        
        # Fixtures table
        self.cursor.execute("""
            CREATE TABLE fixtures (
                id SERIAL PRIMARY KEY,
                season_id INTEGER NOT NULL REFERENCES seasons(id),
                competition_id INTEGER NOT NULL REFERENCES competitions(id),
                home_team_id INTEGER NOT NULL REFERENCES teams(id),
                away_team_id INTEGER NOT NULL REFERENCES teams(id),
                venue_id INTEGER REFERENCES venues(id),
                match_date TIMESTAMP,
                status VARCHAR(20),
                home_score INTEGER,
                away_score INTEGER,
                half_time_home INTEGER,
                half_time_away INTEGER,
                extra_time_home INTEGER,
                extra_time_away INTEGER,
                penalty_home INTEGER,
                penalty_away INTEGER,
                sportmonks_id INTEGER,
                api_football_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        logger.info("Relationship tables created")
    
    def create_statistics_tables(self):
        """Create statistics tables."""
        logger.info("Creating statistics tables...")
        
        # Team match statistics
        self.cursor.execute("""
            CREATE TABLE team_match_statistics (
                id SERIAL PRIMARY KEY,
                fixture_id INTEGER NOT NULL REFERENCES fixtures(id),
                team_id INTEGER NOT NULL REFERENCES teams(id),
                possession_percentage DECIMAL(5,2),
                shots_total INTEGER,
                shots_on_target INTEGER,
                shots_off_target INTEGER,
                shots_blocked INTEGER,
                corner_kicks INTEGER,
                offsides INTEGER,
                fouls INTEGER,
                yellow_cards INTEGER,
                red_cards INTEGER,
                passes_total INTEGER,
                passes_completed INTEGER,
                pass_accuracy DECIMAL(5,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fixture_id, team_id)
            )
        """)
        
        # Player match statistics
        self.cursor.execute("""
            CREATE TABLE player_match_statistics (
                id SERIAL PRIMARY KEY,
                fixture_id INTEGER NOT NULL REFERENCES fixtures(id),
                player_id INTEGER NOT NULL REFERENCES players(id),
                team_id INTEGER NOT NULL REFERENCES teams(id),
                minutes_played INTEGER,
                goals INTEGER DEFAULT 0,
                assists INTEGER DEFAULT 0,
                shots_total INTEGER DEFAULT 0,
                shots_on_target INTEGER DEFAULT 0,
                passes_total INTEGER DEFAULT 0,
                passes_completed INTEGER DEFAULT 0,
                pass_accuracy DECIMAL(5,2),
                key_passes INTEGER DEFAULT 0,
                tackles_total INTEGER DEFAULT 0,
                tackles_won INTEGER DEFAULT 0,
                interceptions INTEGER DEFAULT 0,
                clearances INTEGER DEFAULT 0,
                dribbles_attempted INTEGER DEFAULT 0,
                dribbles_successful INTEGER DEFAULT 0,
                fouls_committed INTEGER DEFAULT 0,
                fouls_drawn INTEGER DEFAULT 0,
                yellow_cards INTEGER DEFAULT 0,
                red_cards INTEGER DEFAULT 0,
                rating DECIMAL(3,1),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fixture_id, player_id)
            )
        """)
        
        # Lineups table
        self.cursor.execute("""
            CREATE TABLE lineups (
                id SERIAL PRIMARY KEY,
                fixture_id INTEGER NOT NULL REFERENCES fixtures(id),
                player_id INTEGER NOT NULL REFERENCES players(id),
                team_id INTEGER NOT NULL REFERENCES teams(id),
                position VARCHAR(20),
                is_starter BOOLEAN DEFAULT TRUE,
                substituted_in_minute INTEGER,
                substituted_out_minute INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Match events table
        self.cursor.execute("""
            CREATE TABLE match_events (
                id SERIAL PRIMARY KEY,
                fixture_id INTEGER NOT NULL REFERENCES fixtures(id),
                team_id INTEGER NOT NULL REFERENCES teams(id),
                player_id INTEGER REFERENCES players(id),
                minute INTEGER,
                event_type VARCHAR(50),
                event_detail VARCHAR(100),
                assist_player_id INTEGER REFERENCES players(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        logger.info("Statistics tables created")
    
    def create_business_tables(self):
        """Create business-related tables."""
        logger.info("Creating business tables...")
        
        # Player contracts table
        self.cursor.execute("""
            CREATE TABLE player_contracts (
                id SERIAL PRIMARY KEY,
                player_id INTEGER NOT NULL REFERENCES players(id),
                team_id INTEGER NOT NULL REFERENCES teams(id),
                start_date DATE,
                end_date DATE,
                salary_annual DECIMAL(12,2),
                contract_type VARCHAR(50),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Player transfers table
        self.cursor.execute("""
            CREATE TABLE player_transfers (
                id SERIAL PRIMARY KEY,
                player_id INTEGER NOT NULL REFERENCES players(id),
                from_team_id INTEGER REFERENCES teams(id),
                to_team_id INTEGER NOT NULL REFERENCES teams(id),
                transfer_date DATE,
                transfer_fee DECIMAL(12,2),
                transfer_type VARCHAR(50),
                season_id INTEGER REFERENCES seasons(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        logger.info("Business tables created")
    
    def create_indexes(self):
        """Create database indexes for performance."""
        logger.info("Creating database indexes...")
        
        indexes = [
            "CREATE INDEX idx_players_position ON players(position)",
            "CREATE INDEX idx_fixtures_date ON fixtures(match_date)",
            "CREATE INDEX idx_fixtures_teams ON fixtures(home_team_id, away_team_id)",
            "CREATE INDEX idx_player_stats_fixture ON player_match_statistics(fixture_id)",
            "CREATE INDEX idx_player_stats_player ON player_match_statistics(player_id)",
            "CREATE INDEX idx_squad_members_team_season ON squad_members(team_id, season_id)",
            "CREATE INDEX idx_team_seasons_competition ON team_seasons(competition_id, season_id)"
        ]
        
        for index_sql in indexes:
            try:
                self.cursor.execute(index_sql)
                logger.info(f"Created index: {index_sql.split()[2]}")
            except Exception as e:
                logger.warning(f"Could not create index: {e}")
    
    def insert_sample_data(self):
        """Insert sample reference data."""
        logger.info("Inserting sample data...")
        
        # Insert sample season
        self.cursor.execute("""
            INSERT INTO seasons (season_name, start_date, end_date, is_current)
            VALUES ('2023-24', '2023-08-01', '2024-05-31', TRUE)
            ON CONFLICT (season_name) DO NOTHING
        """)
        
        # Insert sample competition
        self.cursor.execute("""
            INSERT INTO competitions (name, country, type, level)
            VALUES ('Premier League', 'England', 'League', 1)
        """)
        
        # Insert sample venue
        self.cursor.execute("""
            INSERT INTO venues (name, city, country, capacity)
            VALUES ('Etihad Stadium', 'Manchester', 'England', 55017)
        """)
        
        # Insert Manchester City
        self.cursor.execute("""
            INSERT INTO teams (name, short_name, code, country, venue_id)
            VALUES ('Manchester City', 'Man City', 'MCI', 'England', 1)
        """)
        
        logger.info("Sample data inserted")
    
    def close_connection(self):
        """Close database connection."""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()
        logger.info("Database connection closed")

def main():
    """Main execution function."""
    initializer = PostgreSQLSchemaInitializer()
    
    try:
        print("Initializing PostgreSQL schema for Sports Analytics Engine...")
        
        # Create schema
        initializer.create_schema()
        
        # Create indexes
        initializer.create_indexes()
        
        # Insert sample data
        initializer.insert_sample_data()
        
        print("PostgreSQL schema initialization completed successfully!")
        print("Database is ready for sports analytics data.")
        
    except Exception as e:
        logger.error(f"Schema initialization failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        initializer.close_connection()

if __name__ == "__main__":
    main()

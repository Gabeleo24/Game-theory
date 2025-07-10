#!/usr/bin/env python3
"""
Create FBRef PostgreSQL Schema
Design and implement PostgreSQL tables for Manchester City FBRef match-by-match data
"""

import psycopg2
import psycopg2.extras
import yaml
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FBRefPostgreSQLSchema:
    """Create PostgreSQL schema for FBRef data integration."""
    
    def __init__(self):
        """Initialize database connection."""
        self.load_config()
        self.setup_connection()
        
    def load_config(self):
        """Load database configuration."""
        try:
            with open('config/api_keys.yaml', 'r') as f:
                config = yaml.safe_load(f)
            self.db_config = config['database']
            logger.info("✅ Configuration loaded")
        except FileNotFoundError:
            logger.error("❌ Config file not found")
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
            logger.info("✅ PostgreSQL connection established")
        except psycopg2.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def create_fbref_schema(self):
        """Create dedicated schema for FBRef data."""
        
        logger.info("🏗️ Creating FBRef schema")
        
        # Create schema
        self.cursor.execute("CREATE SCHEMA IF NOT EXISTS fbref")
        
        # Set search path to include fbref schema
        self.cursor.execute("SET search_path TO fbref, public")
        
        logger.info("✅ FBRef schema created")
    
    def create_fbref_match_results(self):
        """Create FBRef match results table."""
        
        logger.info("📊 Creating fbref_match_results table")
        
        self.cursor.execute("""
            DROP TABLE IF EXISTS fbref.fbref_match_results CASCADE
        """)
        
        self.cursor.execute("""
            CREATE TABLE fbref.fbref_match_results (
                id SERIAL PRIMARY KEY,
                
                -- Match Information
                season VARCHAR(10) NOT NULL DEFAULT '2023-24',
                match_date DATE NOT NULL,
                competition VARCHAR(50) NOT NULL,
                matchday INTEGER,
                home_away VARCHAR(10) NOT NULL CHECK (home_away IN ('Home', 'Away')),
                opponent VARCHAR(100) NOT NULL,
                manchester_city_score INTEGER NOT NULL,
                opponent_score INTEGER NOT NULL,
                result VARCHAR(10) NOT NULL CHECK (result IN ('Win', 'Loss', 'Draw')),
                
                -- Team Performance Statistics
                possession_percentage DECIMAL(5,2) DEFAULT 0.0,
                shots_total INTEGER DEFAULT 0,
                shots_on_target INTEGER DEFAULT 0,
                shots_off_target INTEGER DEFAULT 0,
                shots_blocked INTEGER DEFAULT 0,
                corners INTEGER DEFAULT 0,
                offsides INTEGER DEFAULT 0,
                fouls_committed INTEGER DEFAULT 0,
                fouls_suffered INTEGER DEFAULT 0,
                yellow_cards INTEGER DEFAULT 0,
                red_cards INTEGER DEFAULT 0,
                
                -- Passing Statistics
                passes_total INTEGER DEFAULT 0,
                passes_completed INTEGER DEFAULT 0,
                pass_accuracy DECIMAL(5,2) DEFAULT 0.0,
                
                -- Defensive Statistics
                tackles_total INTEGER DEFAULT 0,
                tackles_won INTEGER DEFAULT 0,
                interceptions INTEGER DEFAULT 0,
                clearances INTEGER DEFAULT 0,
                blocks INTEGER DEFAULT 0,
                
                -- Additional Match Info
                attendance INTEGER,
                referee VARCHAR(100),
                venue VARCHAR(100),
                weather_conditions TEXT,
                
                -- Calculated fields
                goal_difference INTEGER GENERATED ALWAYS AS (manchester_city_score - opponent_score) STORED,
                points INTEGER GENERATED ALWAYS AS (
                    CASE 
                        WHEN result = 'Win' THEN 3
                        WHEN result = 'Draw' THEN 1
                        ELSE 0
                    END
                ) STORED,
                
                -- Metadata
                data_source VARCHAR(20) DEFAULT 'FBRef',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Constraints
                UNIQUE(match_date, opponent, competition)
            )
        """)
        
        # Create indexes
        self.cursor.execute("""
            CREATE INDEX idx_fbref_match_date ON fbref.fbref_match_results(match_date)
        """)
        self.cursor.execute("""
            CREATE INDEX idx_fbref_competition ON fbref.fbref_match_results(competition)
        """)
        self.cursor.execute("""
            CREATE INDEX idx_fbref_opponent ON fbref.fbref_match_results(opponent)
        """)
        
        logger.info("✅ fbref_match_results table created")
    
    def create_fbref_player_performances(self):
        """Create FBRef player match performances table."""
        
        logger.info("🎭 Creating fbref_player_performances table")
        
        self.cursor.execute("""
            DROP TABLE IF EXISTS fbref.fbref_player_performances CASCADE
        """)
        
        self.cursor.execute("""
            CREATE TABLE fbref.fbref_player_performances (
                id SERIAL PRIMARY KEY,
                match_result_id INTEGER REFERENCES fbref.fbref_match_results(id) ON DELETE CASCADE,
                
                -- Player Information
                player_name VARCHAR(100) NOT NULL,
                team_name VARCHAR(100) NOT NULL DEFAULT 'Manchester City',
                
                -- Playing Time
                started BOOLEAN DEFAULT FALSE,
                minutes_played INTEGER DEFAULT 0,
                position VARCHAR(10),
                formation_position VARCHAR(10),
                substituted_in INTEGER,
                substituted_out INTEGER,
                
                -- Offensive Statistics
                goals INTEGER DEFAULT 0,
                assists INTEGER DEFAULT 0,
                shots_total INTEGER DEFAULT 0,
                shots_on_target INTEGER DEFAULT 0,
                shots_off_target INTEGER DEFAULT 0,
                shots_blocked INTEGER DEFAULT 0,
                big_chances_created INTEGER DEFAULT 0,
                big_chances_missed INTEGER DEFAULT 0,
                
                -- Passing Statistics
                passes_total INTEGER DEFAULT 0,
                passes_completed INTEGER DEFAULT 0,
                pass_accuracy DECIMAL(5,2) DEFAULT 0.0,
                key_passes INTEGER DEFAULT 0,
                through_balls INTEGER DEFAULT 0,
                long_balls INTEGER DEFAULT 0,
                crosses_total INTEGER DEFAULT 0,
                crosses_accurate INTEGER DEFAULT 0,
                
                -- Defensive Statistics
                tackles_total INTEGER DEFAULT 0,
                tackles_won INTEGER DEFAULT 0,
                tackle_success_rate DECIMAL(5,2) DEFAULT 0.0,
                interceptions INTEGER DEFAULT 0,
                clearances INTEGER DEFAULT 0,
                blocks INTEGER DEFAULT 0,
                headed_clearances INTEGER DEFAULT 0,
                
                -- Duels and Physical
                duels_total INTEGER DEFAULT 0,
                duels_won INTEGER DEFAULT 0,
                duel_success_rate DECIMAL(5,2) DEFAULT 0.0,
                aerial_duels_total INTEGER DEFAULT 0,
                aerial_duels_won INTEGER DEFAULT 0,
                aerial_success_rate DECIMAL(5,2) DEFAULT 0.0,
                
                -- Disciplinary
                yellow_cards INTEGER DEFAULT 0,
                red_cards INTEGER DEFAULT 0,
                fouls_committed INTEGER DEFAULT 0,
                fouls_suffered INTEGER DEFAULT 0,
                
                -- Advanced Metrics
                touches INTEGER DEFAULT 0,
                dribbles_attempted INTEGER DEFAULT 0,
                dribbles_successful INTEGER DEFAULT 0,
                dribble_success_rate DECIMAL(5,2) DEFAULT 0.0,
                dispossessed INTEGER DEFAULT 0,
                distance_covered DECIMAL(5,2) DEFAULT 0.0,
                sprints INTEGER DEFAULT 0,
                
                -- Performance Rating
                rating DECIMAL(3,1) DEFAULT 0.0,
                
                -- Expected Goals/Assists
                expected_goals DECIMAL(4,2) DEFAULT 0.0,
                expected_assists DECIMAL(4,2) DEFAULT 0.0,
                
                -- Calculated per-90 statistics
                goals_per_90 DECIMAL(4,2) GENERATED ALWAYS AS (
                    CASE WHEN minutes_played > 0 THEN (goals * 90.0 / minutes_played) ELSE 0 END
                ) STORED,
                assists_per_90 DECIMAL(4,2) GENERATED ALWAYS AS (
                    CASE WHEN minutes_played > 0 THEN (assists * 90.0 / minutes_played) ELSE 0 END
                ) STORED,
                
                -- Metadata
                data_source VARCHAR(20) DEFAULT 'FBRef',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Constraints
                UNIQUE(match_result_id, player_name)
            )
        """)
        
        # Create indexes
        self.cursor.execute("""
            CREATE INDEX idx_fbref_player_name ON fbref.fbref_player_performances(player_name)
        """)
        self.cursor.execute("""
            CREATE INDEX idx_fbref_match_result ON fbref.fbref_player_performances(match_result_id)
        """)
        self.cursor.execute("""
            CREATE INDEX idx_fbref_position ON fbref.fbref_player_performances(position)
        """)
        
        logger.info("✅ fbref_player_performances table created")
    
    def create_fbref_player_season_stats(self):
        """Create FBRef player season statistics table."""
        
        logger.info("📈 Creating fbref_player_season_stats table")
        
        self.cursor.execute("""
            DROP TABLE IF EXISTS fbref.fbref_player_season_stats CASCADE
        """)
        
        self.cursor.execute("""
            CREATE TABLE fbref.fbref_player_season_stats (
                id SERIAL PRIMARY KEY,
                
                -- Player Information
                player_name VARCHAR(100) NOT NULL,
                position VARCHAR(20),
                nationality VARCHAR(50),
                age INTEGER,
                
                -- Season Information
                season VARCHAR(10) NOT NULL DEFAULT '2023-24',
                team_name VARCHAR(100) NOT NULL DEFAULT 'Manchester City',
                
                -- Appearance Statistics
                matches_played INTEGER DEFAULT 0,
                starts INTEGER DEFAULT 0,
                total_minutes INTEGER DEFAULT 0,
                
                -- Offensive Statistics
                goals INTEGER DEFAULT 0,
                assists INTEGER DEFAULT 0,
                shots INTEGER DEFAULT 0,
                shots_on_target INTEGER DEFAULT 0,
                shot_accuracy DECIMAL(5,2) DEFAULT 0.0,
                
                -- Passing Statistics
                passes_attempted INTEGER DEFAULT 0,
                passes_completed INTEGER DEFAULT 0,
                avg_pass_accuracy DECIMAL(5,2) DEFAULT 0.0,
                
                -- Defensive Statistics
                tackles INTEGER DEFAULT 0,
                tackles_won INTEGER DEFAULT 0,
                interceptions INTEGER DEFAULT 0,
                clearances INTEGER DEFAULT 0,
                blocks INTEGER DEFAULT 0,
                
                -- Disciplinary
                yellow_cards INTEGER DEFAULT 0,
                red_cards INTEGER DEFAULT 0,
                fouls_committed INTEGER DEFAULT 0,
                fouls_suffered INTEGER DEFAULT 0,
                
                -- Performance Metrics
                avg_rating DECIMAL(3,1) DEFAULT 0.0,
                total_distance_km DECIMAL(6,1) DEFAULT 0.0,
                
                -- Per-90 Statistics
                goals_per_90 DECIMAL(4,2) DEFAULT 0.0,
                assists_per_90 DECIMAL(4,2) DEFAULT 0.0,
                shots_per_90 DECIMAL(4,2) DEFAULT 0.0,
                passes_per_90 DECIMAL(5,1) DEFAULT 0.0,
                tackles_per_90 DECIMAL(4,1) DEFAULT 0.0,
                
                -- Metadata
                data_source VARCHAR(20) DEFAULT 'FBRef',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Constraints
                UNIQUE(player_name, season, team_name)
            )
        """)
        
        # Create indexes
        self.cursor.execute("""
            CREATE INDEX idx_fbref_season_player ON fbref.fbref_player_season_stats(player_name)
        """)
        self.cursor.execute("""
            CREATE INDEX idx_fbref_season_position ON fbref.fbref_player_season_stats(position)
        """)
        
        logger.info("✅ fbref_player_season_stats table created")
    
    def create_fbref_competitions(self):
        """Create FBRef competitions summary table."""
        
        logger.info("🏆 Creating fbref_competitions table")
        
        self.cursor.execute("""
            DROP TABLE IF EXISTS fbref.fbref_competitions CASCADE
        """)
        
        self.cursor.execute("""
            CREATE TABLE fbref.fbref_competitions (
                id SERIAL PRIMARY KEY,
                
                -- Competition Information
                competition_name VARCHAR(50) NOT NULL,
                competition_type VARCHAR(30) NOT NULL,
                season VARCHAR(10) NOT NULL DEFAULT '2023-24',
                
                -- Performance Statistics
                total_matches INTEGER DEFAULT 0,
                matches_won INTEGER DEFAULT 0,
                matches_drawn INTEGER DEFAULT 0,
                matches_lost INTEGER DEFAULT 0,
                goals_for INTEGER DEFAULT 0,
                goals_against INTEGER DEFAULT 0,
                
                -- Competition Results
                final_position VARCHAR(50),
                trophy_won BOOLEAN DEFAULT FALSE,
                
                -- Calculated Statistics
                win_percentage DECIMAL(5,2) GENERATED ALWAYS AS (
                    CASE WHEN total_matches > 0 THEN (matches_won * 100.0 / total_matches) ELSE 0 END
                ) STORED,
                goal_difference INTEGER GENERATED ALWAYS AS (goals_for - goals_against) STORED,
                
                -- Metadata
                data_source VARCHAR(20) DEFAULT 'FBRef',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Constraints
                UNIQUE(competition_name, season)
            )
        """)
        
        logger.info("✅ fbref_competitions table created")
    
    def create_update_triggers(self):
        """Create triggers to automatically update timestamps."""
        
        logger.info("⚡ Creating update triggers")
        
        # Create update function
        self.cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql'
        """)
        
        # Create triggers for each table
        tables = [
            'fbref_match_results',
            'fbref_player_performances', 
            'fbref_player_season_stats',
            'fbref_competitions'
        ]
        
        for table in tables:
            self.cursor.execute(f"""
                CREATE TRIGGER update_{table}_updated_at
                BEFORE UPDATE ON fbref.{table}
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
            """)
        
        logger.info("✅ Update triggers created")
    
    def create_complete_schema(self):
        """Create complete FBRef schema."""
        
        print("🏗️ Creating Complete FBRef PostgreSQL Schema")
        print("=" * 60)
        
        try:
            # Create schema
            self.create_fbref_schema()
            
            # Create tables
            self.create_fbref_match_results()
            self.create_fbref_player_performances()
            self.create_fbref_player_season_stats()
            self.create_fbref_competitions()
            
            # Create triggers
            self.create_update_triggers()
            
            # Commit all changes
            self.conn.commit()
            
            print("\n✅ FBRef PostgreSQL schema created successfully!")
            print("📊 Tables created:")
            print("   • fbref.fbref_match_results")
            print("   • fbref.fbref_player_performances")
            print("   • fbref.fbref_player_season_stats")
            print("   • fbref.fbref_competitions")
            print("⚡ Update triggers enabled")
            
            return True
            
        except Exception as e:
            print(f"❌ Schema creation failed: {e}")
            self.conn.rollback()
            return False
        
        finally:
            self.conn.close()

def main():
    """Main execution function."""
    
    schema_creator = FBRefPostgreSQLSchema()
    success = schema_creator.create_complete_schema()
    
    if success:
        print("\n🎉 Ready to migrate FBRef data to PostgreSQL!")
    else:
        print("\n💥 Schema creation failed. Check logs for details.")

if __name__ == "__main__":
    main()

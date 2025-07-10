#!/usr/bin/env python3
"""
Create Match-by-Match Database Schema
Extends the existing FBRef database with comprehensive match and player match performance tables
"""

import sqlite3
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MatchDatabaseSchema:
    """Create and manage match-by-match database schema."""
    
    def __init__(self, db_path="data/fbref_scraped/fbref_data.db"):
        """Initialize with database path."""
        self.db_path = db_path
        
    def create_match_tables(self):
        """Create comprehensive match and player match performance tables."""
        
        logger.info("🏗️ Creating match-by-match database schema")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Match Results Table - Team-level match information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_results (
                match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                season TEXT NOT NULL DEFAULT '2023-24',
                match_date DATE NOT NULL,
                competition TEXT NOT NULL,
                matchday INTEGER,
                home_away TEXT NOT NULL CHECK (home_away IN ('Home', 'Away')),
                opponent TEXT NOT NULL,
                manchester_city_score INTEGER NOT NULL,
                opponent_score INTEGER NOT NULL,
                result TEXT NOT NULL CHECK (result IN ('Win', 'Loss', 'Draw')),
                
                -- Team Performance Statistics
                possession_percentage REAL DEFAULT 0.0,
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
                pass_accuracy REAL DEFAULT 0.0,
                
                -- Defensive Statistics
                tackles_total INTEGER DEFAULT 0,
                tackles_won INTEGER DEFAULT 0,
                interceptions INTEGER DEFAULT 0,
                clearances INTEGER DEFAULT 0,
                blocks INTEGER DEFAULT 0,
                
                -- Additional Match Info
                attendance INTEGER,
                referee TEXT,
                venue TEXT,
                weather_conditions TEXT,
                
                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Constraints
                UNIQUE(match_date, opponent, competition)
            )
        ''')
        
        # 2. Player Match Performances Table - Individual player stats per match
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_match_performances (
                performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                player_name TEXT NOT NULL,
                team_name TEXT NOT NULL DEFAULT 'Manchester City',
                
                -- Playing Time
                started BOOLEAN DEFAULT 0,
                minutes_played INTEGER DEFAULT 0,
                position TEXT,
                formation_position TEXT,
                substituted_in INTEGER DEFAULT NULL,  -- Minute substituted in
                substituted_out INTEGER DEFAULT NULL, -- Minute substituted out
                
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
                pass_accuracy REAL DEFAULT 0.0,
                key_passes INTEGER DEFAULT 0,
                through_balls INTEGER DEFAULT 0,
                long_balls INTEGER DEFAULT 0,
                crosses_total INTEGER DEFAULT 0,
                crosses_accurate INTEGER DEFAULT 0,
                
                -- Defensive Statistics
                tackles_total INTEGER DEFAULT 0,
                tackles_won INTEGER DEFAULT 0,
                tackle_success_rate REAL DEFAULT 0.0,
                interceptions INTEGER DEFAULT 0,
                clearances INTEGER DEFAULT 0,
                blocks INTEGER DEFAULT 0,
                headed_clearances INTEGER DEFAULT 0,
                
                -- Duels and Physical
                duels_total INTEGER DEFAULT 0,
                duels_won INTEGER DEFAULT 0,
                duel_success_rate REAL DEFAULT 0.0,
                aerial_duels_total INTEGER DEFAULT 0,
                aerial_duels_won INTEGER DEFAULT 0,
                aerial_success_rate REAL DEFAULT 0.0,
                
                -- Disciplinary
                yellow_cards INTEGER DEFAULT 0,
                red_cards INTEGER DEFAULT 0,
                fouls_committed INTEGER DEFAULT 0,
                fouls_suffered INTEGER DEFAULT 0,
                
                -- Advanced Metrics
                touches INTEGER DEFAULT 0,
                dribbles_attempted INTEGER DEFAULT 0,
                dribbles_successful INTEGER DEFAULT 0,
                dribble_success_rate REAL DEFAULT 0.0,
                dispossessed INTEGER DEFAULT 0,
                distance_covered REAL DEFAULT 0.0,
                sprints INTEGER DEFAULT 0,
                
                -- Performance Rating
                rating REAL DEFAULT 0.0,
                
                -- Expected Goals/Assists (if available)
                expected_goals REAL DEFAULT 0.0,
                expected_assists REAL DEFAULT 0.0,
                
                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Foreign Keys and Constraints
                FOREIGN KEY (match_id) REFERENCES match_results(match_id),
                FOREIGN KEY (player_name) REFERENCES players(player_name),
                UNIQUE(match_id, player_name)
            )
        ''')
        
        # 3. Match Events Table - Key events during matches
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                minute INTEGER NOT NULL,
                event_type TEXT NOT NULL CHECK (event_type IN (
                    'Goal', 'Assist', 'Yellow Card', 'Red Card', 'Substitution',
                    'Penalty', 'Own Goal', 'VAR Decision', 'Injury'
                )),
                player_name TEXT,
                team_name TEXT,
                description TEXT,
                
                -- Additional event details
                assist_player TEXT,
                penalty_outcome TEXT, -- 'Scored', 'Missed', 'Saved'
                var_decision TEXT,    -- 'Goal Allowed', 'Goal Disallowed', 'Penalty Given', etc.
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (match_id) REFERENCES match_results(match_id)
            )
        ''')
        
        # 4. Competition Information Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitions (
                competition_id INTEGER PRIMARY KEY AUTOINCREMENT,
                competition_name TEXT UNIQUE NOT NULL,
                competition_type TEXT NOT NULL CHECK (competition_type IN (
                    'Domestic League', 'Domestic Cup', 'International Cup', 'Friendly'
                )),
                season TEXT NOT NULL DEFAULT '2023-24',
                total_matches INTEGER DEFAULT 0,
                matches_won INTEGER DEFAULT 0,
                matches_drawn INTEGER DEFAULT 0,
                matches_lost INTEGER DEFAULT 0,
                goals_for INTEGER DEFAULT 0,
                goals_against INTEGER DEFAULT 0,
                final_position TEXT,
                trophy_won BOOLEAN DEFAULT 0,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better query performance (after tables are created)
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_match_date ON match_results(match_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_match_competition ON match_results(competition)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_match_opponent ON match_results(opponent)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_player_match ON player_match_performances(match_id, player_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_player_name ON player_match_performances(player_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_match_events ON match_events(match_id, minute)')
            logger.info("✅ Database indexes created successfully")
        except sqlite3.OperationalError as e:
            logger.warning(f"⚠️ Index creation warning: {e}")
            # Continue anyway as indexes are optional for functionality
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Match database schema created successfully")
        
    def populate_competitions(self):
        """Populate the competitions table with Manchester City's 2023-24 competitions."""
        
        logger.info("📊 Populating competitions data")
        
        competitions_data = [
            {
                'competition_name': 'Premier League',
                'competition_type': 'Domestic League',
                'season': '2023-24',
                'total_matches': 38,
                'matches_won': 28,
                'matches_drawn': 7,
                'matches_lost': 3,
                'goals_for': 96,
                'goals_against': 34,
                'final_position': '1st',
                'trophy_won': 1
            },
            {
                'competition_name': 'Champions League',
                'competition_type': 'International Cup',
                'season': '2023-24',
                'total_matches': 8,
                'matches_won': 5,
                'matches_drawn': 1,
                'matches_lost': 2,
                'goals_for': 18,
                'goals_against': 9,
                'final_position': 'Quarter-finals',
                'trophy_won': 0
            },
            {
                'competition_name': 'FA Cup',
                'competition_type': 'Domestic Cup',
                'season': '2023-24',
                'total_matches': 6,
                'matches_won': 5,
                'matches_drawn': 0,
                'matches_lost': 1,
                'goals_for': 15,
                'goals_against': 4,
                'final_position': 'Final',
                'trophy_won': 1
            },
            {
                'competition_name': 'EFL Cup',
                'competition_type': 'Domestic Cup',
                'season': '2023-24',
                'total_matches': 3,
                'matches_won': 2,
                'matches_drawn': 0,
                'matches_lost': 1,
                'goals_for': 6,
                'goals_against': 2,
                'final_position': 'Fourth Round',
                'trophy_won': 0
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM competitions WHERE season = '2023-24'")
        
        for comp in competitions_data:
            cursor.execute('''
                INSERT INTO competitions 
                (competition_name, competition_type, season, total_matches, matches_won, 
                 matches_drawn, matches_lost, goals_for, goals_against, final_position, trophy_won)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                comp['competition_name'], comp['competition_type'], comp['season'],
                comp['total_matches'], comp['matches_won'], comp['matches_drawn'],
                comp['matches_lost'], comp['goals_for'], comp['goals_against'],
                comp['final_position'], comp['trophy_won']
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Populated {len(competitions_data)} competitions")
        
    def verify_schema(self):
        """Verify the database schema was created correctly."""
        
        logger.info("🔍 Verifying database schema")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['match_results', 'player_match_performances', 'match_events', 'competitions']
        
        for table in expected_tables:
            if table in tables:
                logger.info(f"✅ Table '{table}' exists")
                
                # Get column count
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                logger.info(f"   📊 {len(columns)} columns defined")
            else:
                logger.error(f"❌ Table '{table}' missing")
        
        # Check existing data
        cursor.execute("SELECT COUNT(*) FROM players WHERE team_name = 'Manchester City'")
        player_count = cursor.fetchone()[0]
        logger.info(f"📊 {player_count} Manchester City players in database")
        
        cursor.execute("SELECT COUNT(*) FROM competitions")
        comp_count = cursor.fetchone()[0]
        logger.info(f"📊 {comp_count} competitions defined")
        
        conn.close()
        
        logger.info("✅ Schema verification complete")

def main():
    """Main execution function."""
    
    print("🏗️ Creating Match-by-Match Database Schema")
    print("=" * 60)
    
    schema_manager = MatchDatabaseSchema()
    
    # Create the schema
    schema_manager.create_match_tables()
    
    # Populate competitions
    schema_manager.populate_competitions()
    
    # Verify everything was created correctly
    schema_manager.verify_schema()
    
    print("\n✅ Database schema ready for match data!")
    print("📊 Next steps:")
    print("   1. Generate match schedule and results")
    print("   2. Create player match performances")
    print("   3. Validate data consistency")

if __name__ == "__main__":
    main()

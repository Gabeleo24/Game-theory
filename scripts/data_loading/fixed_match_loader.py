#!/usr/bin/env python3
"""
FIXED MATCH LOADER - PROPER PLAYER DEDUPLICATION
Fixes the critical data integrity issues found in the original loader
"""

import json
import psycopg2
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FixedMatchLoader:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'soccer_intelligence',
            'user': 'soccerapp',
            'password': 'soccerpass123'
        }
        self.conn = None
        self.cursor = None
        
        # Cache for deduplication
        self.team_cache = {}  # team_name -> team_id
        self.player_cache = {}  # (player_name, team_id) -> player_id
        
    def connect_db(self):
        """Connect to database."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logger.info("[PASS] Connected to database")
            return True
        except Exception as e:
            logger.error(f"[FAIL] Database connection failed: {e}")
            return False
    
    def create_fixed_tables(self):
        """Create properly structured tables with constraints."""
        
        # Drop existing tables to start fresh
        drop_queries = [
            "DROP TABLE IF EXISTS fixed_match_player_stats CASCADE;",
            "DROP TABLE IF EXISTS fixed_matches CASCADE;",
            "DROP TABLE IF EXISTS fixed_teams CASCADE;",
            "DROP TABLE IF EXISTS fixed_players CASCADE;"
        ]
        
        for query in drop_queries:
            self.cursor.execute(query)
        
        # Create properly structured tables
        create_queries = [
            """
            CREATE TABLE fixed_teams (
                team_id SERIAL PRIMARY KEY,
                team_name VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE fixed_players (
                player_id SERIAL PRIMARY KEY,
                player_name VARCHAR(100) NOT NULL,
                team_id INTEGER REFERENCES fixed_teams(team_id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(player_name, team_id)  -- Prevent duplicates per team
            );
            """,
            """
            CREATE TABLE fixed_matches (
                match_id SERIAL PRIMARY KEY,
                home_team_id INTEGER REFERENCES fixed_teams(team_id),
                away_team_id INTEGER REFERENCES fixed_teams(team_id),
                match_date DATE,
                competition VARCHAR(50),
                season VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE fixed_match_player_stats (
                stat_id SERIAL PRIMARY KEY,
                match_id INTEGER REFERENCES fixed_matches(match_id),
                player_id INTEGER REFERENCES fixed_players(player_id),
                team_id INTEGER REFERENCES fixed_teams(team_id),
                
                -- Basic Info
                position VARCHAR(10),
                minutes_played INTEGER DEFAULT 0,
                
                -- Attacking Stats
                goals INTEGER DEFAULT 0,
                assists INTEGER DEFAULT 0,
                shots_total INTEGER DEFAULT 0,
                shots_on_target INTEGER DEFAULT 0,
                
                -- Passing Stats
                passes_total INTEGER DEFAULT 0,
                passes_completed INTEGER DEFAULT 0,
                pass_accuracy DECIMAL(5,2) DEFAULT 0,
                
                -- Defensive Stats
                tackles_total INTEGER DEFAULT 0,
                tackles_won INTEGER DEFAULT 0,
                interceptions INTEGER DEFAULT 0,
                
                -- Discipline
                fouls_committed INTEGER DEFAULT 0,
                fouls_drawn INTEGER DEFAULT 0,
                yellow_cards INTEGER DEFAULT 0,
                red_cards INTEGER DEFAULT 0,
                
                -- Performance
                rating DECIMAL(3,1) DEFAULT 0,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(match_id, player_id)  -- One record per player per match
            );
            """
        ]
        
        for query in create_queries:
            self.cursor.execute(query)
        
        # Create indexes for performance
        index_queries = [
            "CREATE INDEX idx_fixed_players_name ON fixed_players(player_name);",
            "CREATE INDEX idx_fixed_players_team ON fixed_players(team_id);",
            "CREATE INDEX idx_fixed_match_stats_match ON fixed_match_player_stats(match_id);",
            "CREATE INDEX idx_fixed_match_stats_player ON fixed_match_player_stats(player_id);",
            "CREATE INDEX idx_fixed_matches_date ON fixed_matches(match_date);"
        ]
        
        for query in index_queries:
            self.cursor.execute(query)
        
        self.conn.commit()
        logger.info("[PASS] Created fixed tables with proper constraints and indexes")
    
    def get_or_create_team(self, team_name):
        """Get existing team or create new one (with caching)."""
        if team_name in self.team_cache:
            return self.team_cache[team_name]
        
        try:
            # Try to get existing team
            self.cursor.execute(
                "SELECT team_id FROM fixed_teams WHERE team_name = %s",
                (team_name,)
            )
            result = self.cursor.fetchone()
            
            if result:
                team_id = result[0]
            else:
                # Create new team
                self.cursor.execute(
                    "INSERT INTO fixed_teams (team_name) VALUES (%s) RETURNING team_id",
                    (team_name,)
                )
                team_id = self.cursor.fetchone()[0]
            
            # Cache the result
            self.team_cache[team_name] = team_id
            return team_id
            
        except Exception as e:
            logger.error(f"[FAIL] Error with team {team_name}: {e}")
            return None
    
    def get_or_create_player(self, player_name, team_id):
        """Get existing player or create new one (with caching)."""
        cache_key = (player_name, team_id)
        if cache_key in self.player_cache:
            return self.player_cache[cache_key]
        
        try:
            # Try to get existing player
            self.cursor.execute(
                "SELECT player_id FROM fixed_players WHERE player_name = %s AND team_id = %s",
                (player_name, team_id)
            )
            result = self.cursor.fetchone()
            
            if result:
                player_id = result[0]
            else:
                # Create new player
                self.cursor.execute(
                    "INSERT INTO fixed_players (player_name, team_id) VALUES (%s, %s) RETURNING player_id",
                    (player_name, team_id)
                )
                player_id = self.cursor.fetchone()[0]
            
            # Cache the result
            self.player_cache[cache_key] = player_id
            return player_id
            
        except Exception as e:
            logger.error(f"[FAIL] Error with player {player_name}: {e}")
            return None
    
    def insert_match(self, home_team_id, away_team_id, match_date, competition, season):
        """Insert match and return match_id."""
        try:
            self.cursor.execute(
                """INSERT INTO fixed_matches 
                   (home_team_id, away_team_id, match_date, competition, season) 
                   VALUES (%s, %s, %s, %s, %s) RETURNING match_id""",
                (home_team_id, away_team_id, match_date, competition, season)
            )
            return self.cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"[FAIL] Error inserting match: {e}")
            return None
    
    def insert_player_stats(self, match_id, player_id, team_id, stats):
        """Insert player statistics for a match."""
        try:
            # Calculate pass accuracy safely
            pass_accuracy = 0
            passes_total = int(stats.get('passes_total', 0))
            passes_completed = int(stats.get('passes_completed', 0))
            if passes_total > 0:
                pass_accuracy = (passes_completed / passes_total) * 100
            
            self.cursor.execute(
                """INSERT INTO fixed_match_player_stats 
                   (match_id, player_id, team_id, position, minutes_played, goals, assists,
                    shots_total, shots_on_target, passes_total, passes_completed, pass_accuracy,
                    tackles_total, tackles_won, interceptions, fouls_committed, fouls_drawn,
                    yellow_cards, red_cards, rating)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (match_id, player_id) DO NOTHING""",  # Prevent duplicates
                (
                    match_id, player_id, team_id,
                    stats.get('position', 'N/A'),
                    int(stats.get('minutes_played', 0)),
                    int(stats.get('goals', 0)),
                    int(stats.get('assists', 0)),
                    int(stats.get('shots_total', 0)),
                    int(stats.get('shots_on_target', 0)),
                    passes_total,
                    passes_completed,
                    round(pass_accuracy, 2),
                    int(stats.get('tackles_total', 0)),
                    int(stats.get('tackles_won', 0)),
                    int(stats.get('interceptions', 0)),
                    int(stats.get('fouls_committed', 0)),
                    int(stats.get('fouls_drawn', 0)),
                    int(stats.get('yellow_cards', 0)),
                    int(stats.get('red_cards', 0)),
                    float(stats.get('rating', 0.0))
                )
            )
            return True
        except Exception as e:
            logger.error(f"[FAIL] Error inserting player stats: {e}")
            return False
    
    def load_match_file(self, file_path):
        """Load a single match file with proper deduplication."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                match_data = json.load(f)

            # Extract match info
            match_info = match_data.get('match_info', {})
            home_team = match_info.get('home_team', 'Unknown')
            away_team = match_info.get('away_team', 'Unknown')
            match_date = match_info.get('date', '2023-01-01')
            competition = match_info.get('competition', 'La Liga')
            season = match_info.get('season', '2023-2024')

            logger.info(f"[SUCCESS] Loading: {home_team} vs {away_team} ({match_date})")

            # Get or create teams (with caching)
            home_team_id = self.get_or_create_team(home_team)
            away_team_id = self.get_or_create_team(away_team)
            real_madrid_team_id = self.get_or_create_team('Real Madrid')

            if not home_team_id or not away_team_id or not real_madrid_team_id:
                logger.error("[FAIL] Failed to get/create teams")
                return False

            # Insert match
            match_id = self.insert_match(home_team_id, away_team_id, match_date, competition, season)
            if not match_id:
                logger.error("[FAIL] Failed to insert match")
                return False

            # Process players with deduplication
            total_players = 0

            # Real Madrid players (always assign to Real Madrid team)
            real_madrid_players = match_data.get('real_madrid_players', [])
            for player_data in real_madrid_players:
                player_name = player_data.get('player_name', 'Unknown')
                player_id = self.get_or_create_player(player_name, real_madrid_team_id)
                if player_id and self.insert_player_stats(match_id, player_id, real_madrid_team_id, player_data):
                    total_players += 1

            # Opponent players (assign to the team that's NOT Real Madrid)
            opponent_players = match_data.get('opponent_players', [])
            opponent_team_id = away_team_id if home_team == 'Real Madrid' else home_team_id

            for player_data in opponent_players:
                player_name = player_data.get('player_name', 'Unknown')
                player_id = self.get_or_create_player(player_name, opponent_team_id)
                if player_id and self.insert_player_stats(match_id, player_id, opponent_team_id, player_data):
                    total_players += 1

            self.conn.commit()
            logger.info(f"[PASS] Loaded {total_players} players for match {match_id}")
            return True

        except Exception as e:
            logger.error(f"[FAIL] Error loading {file_path}: {e}")
            self.conn.rollback()
            return False
    
    def load_all_matches(self):
        """Load all Real Madrid match files with proper deduplication."""
        data_dir = Path("data/focused/players/real_madrid_2023_2024/individual_matches")
        
        if not data_dir.exists():
            logger.error(f"[FAIL] Data directory not found: {data_dir}")
            return False
        
        match_files = list(data_dir.glob("*.json"))
        logger.info(f"[FILES] Found {len(match_files)} match files")
        
        loaded_count = 0
        for file_path in match_files:
            if self.load_match_file(file_path):
                loaded_count += 1
        
        logger.info(f"[RESULT] Successfully loaded {loaded_count}/{len(match_files)} matches")
        return loaded_count > 0
    
    def verify_data_integrity(self):
        """Verify that deduplication worked correctly."""
        logger.info(f"\n{'='*80}")
        logger.info(f"[ANALYSIS] DATA INTEGRITY VERIFICATION")
        logger.info(f"{'='*80}")
        
        # Check for duplicate players
        self.cursor.execute("""
            SELECT player_name, COUNT(DISTINCT player_id) as player_count
            FROM fixed_players
            GROUP BY player_name
            HAVING COUNT(DISTINCT player_id) > 1
            ORDER BY player_count DESC
            LIMIT 10
        """)
        
        duplicates = self.cursor.fetchall()
        if duplicates:
            logger.warning(f"[WARNING] DUPLICATE PLAYERS FOUND:")
            for name, count in duplicates:
                logger.warning(f"   {name}: {count} different player IDs")
        else:
            logger.info(f"[PASS] No duplicate players found!")
        
        # Check data summary
        self.cursor.execute("""
            SELECT 
                COUNT(DISTINCT t.team_name) as teams,
                COUNT(DISTINCT p.player_name) as players,
                COUNT(DISTINCT m.match_id) as matches,
                COUNT(*) as player_records
            FROM fixed_match_player_stats mps
            JOIN fixed_players p ON mps.player_id = p.player_id
            JOIN fixed_teams t ON mps.team_id = t.team_id
            JOIN fixed_matches m ON mps.match_id = m.match_id
        """)
        
        summary = self.cursor.fetchone()
        teams, players, matches, records = summary
        
        logger.info(f"\n[DATA] FIXED DATASET SUMMARY:")
        logger.info(f"   Teams: {teams}")
        logger.info(f"   Unique Players: {players}")
        logger.info(f"   Matches: {matches}")
        logger.info(f"   Player Records: {records}")
        
        # Check Real Madrid players specifically
        self.cursor.execute("""
            SELECT COUNT(DISTINCT p.player_name) as unique_players
            FROM fixed_players p
            JOIN fixed_teams t ON p.team_id = t.team_id
            WHERE t.team_name = 'Real Madrid'
        """)
        
        rm_players = self.cursor.fetchone()[0]
        logger.info(f"   Real Madrid Players: {rm_players}")
        
        return True
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

def main():
    """Main function."""
    logger.info("FIXED MATCH LOADER - PROPER DEDUPLICATION! ")
    
    loader = FixedMatchLoader()
    
    if not loader.connect_db():
        return
    
    # Create fixed tables
    loader.create_fixed_tables()
    
    # Load all matches with proper deduplication
    if loader.load_all_matches():
        logger.info("[PASS] Data loading complete!")
        
        # Verify data integrity
        loader.verify_data_integrity()
    else:
        logger.error("[FAIL] Data loading failed!")
    
    loader.close()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SIMPLE MATCH-LEVEL PLAYER STATS LOADER
Creates exactly what you want: Elche-style player statistics tables
"""

import json
import psycopg2
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleMatchLoader:
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
    
    def create_simple_tables(self):
        """Create simplified tables for match-level data."""
        
        # Drop existing tables to start fresh
        drop_queries = [
            "DROP TABLE IF EXISTS match_player_stats CASCADE;",
            "DROP TABLE IF EXISTS simple_matches CASCADE;",
            "DROP TABLE IF EXISTS simple_teams CASCADE;",
            "DROP TABLE IF EXISTS simple_players CASCADE;"
        ]
        
        for query in drop_queries:
            self.cursor.execute(query)
        
        # Create simple tables
        create_queries = [
            """
            CREATE TABLE simple_teams (
                team_id SERIAL PRIMARY KEY,
                team_name VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE simple_players (
                player_id SERIAL PRIMARY KEY,
                player_name VARCHAR(100) NOT NULL,
                team_id INTEGER REFERENCES simple_teams(team_id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE simple_matches (
                match_id SERIAL PRIMARY KEY,
                home_team_id INTEGER REFERENCES simple_teams(team_id),
                away_team_id INTEGER REFERENCES simple_teams(team_id),
                match_date DATE,
                competition VARCHAR(50),
                season VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE match_player_stats (
                stat_id SERIAL PRIMARY KEY,
                match_id INTEGER REFERENCES simple_matches(match_id),
                player_id INTEGER REFERENCES simple_players(player_id),
                team_id INTEGER REFERENCES simple_teams(team_id),
                
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
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        ]
        
        for query in create_queries:
            self.cursor.execute(query)
        
        self.conn.commit()
        logger.info("[PASS] Created simplified tables for match-level data")
    
    def insert_team(self, team_name):
        """Insert team and return team_id."""
        try:
            self.cursor.execute(
                "INSERT INTO simple_teams (team_name) VALUES (%s) ON CONFLICT (team_name) DO NOTHING RETURNING team_id",
                (team_name,)
            )
            result = self.cursor.fetchone()
            
            if result:
                return result[0]
            else:
                # Team already exists, get its ID
                self.cursor.execute("SELECT team_id FROM simple_teams WHERE team_name = %s", (team_name,))
                return self.cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"[FAIL] Error inserting team {team_name}: {e}")
            return None
    
    def insert_player(self, player_name, team_id):
        """Insert player and return player_id."""
        try:
            self.cursor.execute(
                "INSERT INTO simple_players (player_name, team_id) VALUES (%s, %s) RETURNING player_id",
                (player_name, team_id)
            )
            return self.cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"[FAIL] Error inserting player {player_name}: {e}")
            return None
    
    def insert_match(self, home_team_id, away_team_id, match_date, competition, season):
        """Insert match and return match_id."""
        try:
            self.cursor.execute(
                """INSERT INTO simple_matches 
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
            # Calculate pass accuracy - handle string values
            pass_accuracy = 0
            passes_total = int(stats.get('passes_total', 0))
            passes_completed = int(stats.get('passes_completed', 0))
            if passes_total > 0:
                pass_accuracy = (passes_completed / passes_total) * 100
            
            self.cursor.execute(
                """INSERT INTO match_player_stats
                   (match_id, player_id, team_id, position, minutes_played, goals, assists,
                    shots_total, shots_on_target, passes_total, passes_completed, pass_accuracy,
                    tackles_total, tackles_won, interceptions, fouls_committed, fouls_drawn,
                    yellow_cards, red_cards, rating)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
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
        """Load a single match file."""
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
            
            # Insert teams
            home_team_id = self.insert_team(home_team)
            away_team_id = self.insert_team(away_team)
            
            if not home_team_id or not away_team_id:
                logger.error("[FAIL] Failed to insert teams")
                return False
            
            # Insert match
            match_id = self.insert_match(home_team_id, away_team_id, match_date, competition, season)
            if not match_id:
                logger.error("[FAIL] Failed to insert match")
                return False
            
            # Process players
            total_players = 0
            
            # Real Madrid players
            real_madrid_players = match_data.get('real_madrid_players', [])
            for player_data in real_madrid_players:
                player_name = player_data.get('player_name', 'Unknown')
                player_id = self.insert_player(player_name, home_team_id)
                if player_id and self.insert_player_stats(match_id, player_id, home_team_id, player_data):
                    total_players += 1
            
            # Opponent players
            opponent_players = match_data.get('opponent_players', [])
            for player_data in opponent_players:
                player_name = player_data.get('player_name', 'Unknown')
                player_id = self.insert_player(player_name, away_team_id)
                if player_id and self.insert_player_stats(match_id, player_id, away_team_id, player_data):
                    total_players += 1
            
            self.conn.commit()
            logger.info(f"[PASS] Loaded {total_players} players for match {match_id}")
            return True
            
        except Exception as e:
            logger.error(f"[FAIL] Error loading {file_path}: {e}")
            self.conn.rollback()
            return False
    
    def load_all_matches(self):
        """Load all Real Madrid match files."""
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
    
    def display_sample_match(self):
        """Display a sample match in Elche style."""
        try:
            # Get a match with good data
            self.cursor.execute("""
                SELECT m.match_id, ht.team_name as home_team, at.team_name as away_team, 
                       m.match_date, COUNT(*) as player_count
                FROM simple_matches m
                JOIN simple_teams ht ON m.home_team_id = ht.team_id
                JOIN simple_teams at ON m.away_team_id = at.team_id
                JOIN match_player_stats mps ON m.match_id = mps.match_id
                GROUP BY m.match_id, ht.team_name, at.team_name, m.match_date
                ORDER BY player_count DESC
                LIMIT 1
            """)
            
            result = self.cursor.fetchone()
            if result:
                match_id, home_team, away_team, match_date, player_count = result
                
                logger.info(f"\n{'='*80}")
                logger.info(f"[SUCCESS] {home_team} vs {away_team} - {match_date}")
                logger.info(f"[DATA] {player_count} players")
                logger.info(f"{'='*80}")
                
                # Get player stats
                self.cursor.execute("""
                    SELECT 
                        p.player_name,
                        mps.position,
                        mps.minutes_played,
                        mps.goals,
                        mps.assists,
                        mps.shots_total,
                        mps.shots_on_target,
                        mps.passes_total,
                        mps.passes_completed,
                        mps.pass_accuracy,
                        mps.tackles_total,
                        mps.interceptions,
                        mps.fouls_committed,
                        mps.yellow_cards,
                        mps.red_cards,
                        mps.rating,
                        t.team_name
                    FROM match_player_stats mps
                    JOIN simple_players p ON mps.player_id = p.player_id
                    JOIN simple_teams t ON mps.team_id = t.team_id
                    WHERE mps.match_id = %s
                    ORDER BY t.team_name, mps.rating DESC
                """, (match_id,))
                
                results = self.cursor.fetchall()
                
                current_team = None
                for row in results:
                    if row[16] != current_team:  # team_name
                        current_team = row[16]
                        logger.info(f"\n🔥 {current_team}")
                        logger.info("-" * 60)
                        logger.info(f"{'Player':<20} {'Pos':<4} {'Min':>3} {'Gls':>2} {'Ast':>2} {'Sh':>3} {'SoT':>3} {'Pass':>4} {'Cmp':>4} {'Cmp%':>5} {'Rating':>6}")
                        logger.info("-" * 60)
                    
                    logger.info(f"{row[0]:<20} {row[1]:<4} {row[2]:>3} {row[3]:>2} {row[4]:>2} {row[5]:>3} {row[6]:>3} {row[7]:>4} {row[8]:>4} {row[9]:>5.1f} {row[15]:>6.1f}")
                
                return True
            else:
                logger.warning("[FAIL] No matches found")
                return False
                
        except Exception as e:
            logger.error(f"[FAIL] Error displaying match: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

def main():
    """Main function."""
    logger.info("SIMPLE MATCH-LEVEL LOADER - ELCHE STYLE! ")
    
    loader = SimpleMatchLoader()
    
    if not loader.connect_db():
        return
    
    # Create tables
    loader.create_simple_tables()
    
    # Load all matches
    if loader.load_all_matches():
        logger.info("[PASS] Data loading complete!")
        
        # Display sample
        loader.display_sample_match()
    else:
        logger.error("[FAIL] Data loading failed!")
    
    loader.close()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
MATCH PLAYER VIEWER - ELCHE STYLE
View any match's player statistics in the beautiful format you wanted!
"""

import psycopg2
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MatchPlayerViewer:
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
            return True
        except Exception as e:
            logger.error(f"[FAIL] Database connection failed: {e}")
            return False
    
    def list_available_matches(self):
        """List all available matches."""
        try:
            self.cursor.execute("""
                SELECT 
                    m.match_id,
                    ht.team_name as home_team,
                    at.team_name as away_team,
                    m.match_date,
                    m.competition,
                    COUNT(*) as player_count
                FROM simple_matches m
                JOIN simple_teams ht ON m.home_team_id = ht.team_id
                JOIN simple_teams at ON m.away_team_id = at.team_id
                JOIN match_player_stats mps ON m.match_id = mps.match_id
                GROUP BY m.match_id, ht.team_name, at.team_name, m.match_date, m.competition
                ORDER BY m.match_date DESC
            """)
            
            results = self.cursor.fetchall()
            
            logger.info(f"\n{'='*80}")
            logger.info(f"[SUCCESS] AVAILABLE MATCHES ({len(results)} total)")
            logger.info(f"{'='*80}")
            logger.info(f"{'ID':<4} {'Date':<12} {'Home Team':<20} {'Away Team':<20} {'Competition':<15} {'Players':<8}")
            logger.info("-" * 80)
            
            for row in results:
                match_id, home_team, away_team, match_date, competition, player_count = row
                logger.info(f"{match_id:<4} {str(match_date):<12} {home_team:<20} {away_team:<20} {competition:<15} {player_count:<8}")
            
            return results
            
        except Exception as e:
            logger.error(f"[FAIL] Error listing matches: {e}")
            return []
    
    def view_match(self, match_id):
        """View detailed player stats for a specific match."""
        try:
            # Get match info
            self.cursor.execute("""
                SELECT 
                    ht.team_name as home_team,
                    at.team_name as away_team,
                    m.match_date,
                    m.competition,
                    COUNT(*) as player_count
                FROM simple_matches m
                JOIN simple_teams ht ON m.home_team_id = ht.team_id
                JOIN simple_teams at ON m.away_team_id = at.team_id
                JOIN match_player_stats mps ON m.match_id = mps.match_id
                WHERE m.match_id = %s
                GROUP BY ht.team_name, at.team_name, m.match_date, m.competition
            """, (match_id,))
            
            match_info = self.cursor.fetchone()
            if not match_info:
                logger.error(f"[FAIL] Match {match_id} not found!")
                return False
            
            home_team, away_team, match_date, competition, player_count = match_info
            
            logger.info(f"\n{'='*80}")
            logger.info(f"[SUCCESS] {home_team} vs {away_team}")
            logger.info(f"[DATE] {match_date} | [SUCCESS] {competition}")
            logger.info(f"👥 {player_count} players")
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
                    mps.tackles_won,
                    mps.interceptions,
                    mps.fouls_committed,
                    mps.fouls_drawn,
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
                team_name = row[18]
                
                if team_name != current_team:
                    current_team = team_name
                    logger.info(f"\n🔥 {current_team}")
                    logger.info("-" * 80)
                    logger.info(f"{'Player':<20} {'Pos':<4} {'Min':>3} {'Gls':>3} {'Ast':>3} {'Sh':>3} {'SoT':>3} {'Pass':>4} {'Cmp':>4} {'Cmp%':>5} {'Tkl':>3} {'Int':>3} {'Fls':>3} {'YC':>2} {'RC':>2} {'Rating':>6}")
                    logger.info("-" * 80)
                
                player_name, position, minutes, goals, assists, shots_total, shots_on_target, passes_total, passes_completed, pass_accuracy, tackles_total, tackles_won, interceptions, fouls_committed, fouls_drawn, yellow_cards, red_cards, rating, _ = row
                
                logger.info(f"{player_name:<20} {position:<4} {minutes:>3} {goals:>3} {assists:>3} {shots_total:>3} {shots_on_target:>3} {passes_total:>4} {passes_completed:>4} {pass_accuracy:>5.1f} {tackles_total:>3} {interceptions:>3} {fouls_committed:>3} {yellow_cards:>2} {red_cards:>2} {rating:>6.1f}")
            
            return True
            
        except Exception as e:
            logger.error(f"[FAIL] Error viewing match {match_id}: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

def main():
    """Main function."""
    viewer = MatchPlayerViewer()
    
    if not viewer.connect_db():
        return
    
    if len(sys.argv) > 1:
        # View specific match
        try:
            match_id = int(sys.argv[1])
            viewer.view_match(match_id)
        except ValueError:
            logger.error("[FAIL] Please provide a valid match ID number")
    else:
        # List all matches
        matches = viewer.list_available_matches()
        if matches:
            logger.info(f"\n[RECOMMENDATION] To view a specific match, run:")
            logger.info(f"   python {sys.argv[0]} <match_id>")
            logger.info(f"\n[RECOMMENDATION] Example:")
            logger.info(f"   python {sys.argv[0]} 4")
    
    viewer.close()

if __name__ == "__main__":
    main()

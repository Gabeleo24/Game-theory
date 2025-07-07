#!/usr/bin/env python3
"""
Common Database Queries with Automatic Logging
Pre-built queries for common database operations with automatic logging.
"""

from sql_logger import SQLLogger
from datetime import datetime

class CommonQueries:
    """Common database queries with automatic logging."""
    
    def __init__(self, log_dir: str = "logs/sql_logs"):
        """Initialize with SQL logger."""
        self.logger = SQLLogger(log_dir)
    
    def database_overview(self):
        """Get complete database overview with logging."""
        self.logger.log_process_start("Database Overview", "Complete status of all tables and data")
        
        # Table counts
        self.logger.execute_and_log("""
            SELECT 
                'teams' as table_name, COUNT(*) as record_count FROM teams
            UNION ALL
            SELECT 
                'players' as table_name, COUNT(*) as record_count FROM players
            UNION ALL
            SELECT 
                'matches' as table_name, COUNT(*) as record_count FROM matches
            UNION ALL
            SELECT 
                'player_statistics' as table_name, COUNT(*) as record_count FROM player_statistics
            ORDER BY record_count DESC;
        """, "Database Table Record Counts")
        
        self.logger.log_process_end("Database Overview", True)
    
    def player_cards_analysis(self):
        """Complete player cards analysis with logging."""
        self.logger.log_process_start("Player Cards Analysis", "Comprehensive player disciplinary analysis")
        
        # Overview statistics
        self.logger.execute_and_log("""
            SELECT 
                COUNT(*) as total_player_statistics,
                SUM(yellow_cards) as total_yellow_cards,
                SUM(red_cards) as total_red_cards,
                COUNT(CASE WHEN yellow_cards > 0 THEN 1 END) as players_with_yellow_cards,
                COUNT(CASE WHEN red_cards > 0 THEN 1 END) as players_with_red_cards,
                ROUND(AVG(yellow_cards::numeric), 2) as avg_yellow_per_player,
                ROUND(AVG(red_cards::numeric), 2) as avg_red_per_player
            FROM player_statistics;
        """, "Player Cards Overview Statistics")
        
        # Top players by yellow cards
        self.logger.execute_and_log("""
            SELECT 
                p.player_name,
                t.team_name,
                t.country,
                ps.season_year,
                ps.yellow_cards,
                ps.red_cards,
                ps.minutes_played,
                ps.goals,
                ps.assists,
                ps.position,
                CASE 
                    WHEN ps.minutes_played > 0 
                    THEN ROUND((ps.yellow_cards::numeric / ps.minutes_played * 90), 2)
                    ELSE 0 
                END as yellow_cards_per_90min
            FROM player_statistics ps
            JOIN players p ON ps.player_id = p.player_id
            JOIN teams t ON ps.team_id = t.team_id
            WHERE ps.yellow_cards > 0
            ORDER BY ps.yellow_cards DESC, ps.red_cards DESC
            LIMIT 20;
        """, "Top 20 Players by Yellow Cards")
        
        # Players with red cards
        self.logger.execute_and_log("""
            SELECT 
                p.player_name,
                t.team_name,
                t.country,
                ps.season_year,
                ps.red_cards,
                ps.yellow_cards,
                ps.minutes_played,
                ps.goals,
                ps.assists,
                ps.position
            FROM player_statistics ps
            JOIN players p ON ps.player_id = p.player_id
            JOIN teams t ON ps.team_id = t.team_id
            WHERE ps.red_cards > 0
            ORDER BY ps.red_cards DESC, ps.yellow_cards DESC
            LIMIT 20;
        """, "Players with Red Cards")
        
        # Team disciplinary records
        self.logger.execute_and_log("""
            SELECT 
                t.team_name,
                t.country,
                ps.season_year,
                COUNT(*) as players_with_cards,
                SUM(ps.yellow_cards) as total_yellow_cards,
                SUM(ps.red_cards) as total_red_cards,
                ROUND(AVG(ps.yellow_cards::numeric), 2) as avg_yellow_per_player,
                ROUND(AVG(ps.red_cards::numeric), 2) as avg_red_per_player
            FROM player_statistics ps
            JOIN teams t ON ps.team_id = t.team_id
            WHERE ps.yellow_cards > 0 OR ps.red_cards > 0
            GROUP BY t.team_id, t.team_name, t.country, ps.season_year
            ORDER BY total_yellow_cards DESC, total_red_cards DESC
            LIMIT 20;
        """, "Team Disciplinary Records by Season")
        
        # Cards by position
        self.logger.execute_and_log("""
            SELECT 
                ps.position,
                COUNT(*) as players,
                SUM(ps.yellow_cards) as total_yellow_cards,
                SUM(ps.red_cards) as total_red_cards,
                ROUND(AVG(ps.yellow_cards::numeric), 2) as avg_yellow_per_player,
                ROUND(AVG(ps.red_cards::numeric), 2) as avg_red_per_player,
                ROUND(SUM(ps.yellow_cards)::numeric / NULLIF(SUM(ps.minutes_played), 0) * 90, 3) as yellow_per_90min,
                ROUND(SUM(ps.red_cards)::numeric / NULLIF(SUM(ps.minutes_played), 0) * 90, 3) as red_per_90min
            FROM player_statistics ps
            WHERE ps.position IS NOT NULL AND ps.position != '' AND (ps.yellow_cards > 0 OR ps.red_cards > 0)
            GROUP BY ps.position
            ORDER BY avg_yellow_per_player DESC;
        """, "Cards Analysis by Position")
        
        self.logger.log_process_end("Player Cards Analysis", True)
    
    def match_analysis(self):
        """Match analysis with logging."""
        self.logger.log_process_start("Match Analysis", "Analysis of match results and patterns")
        
        # Match overview
        self.logger.execute_and_log("""
            SELECT 
                COUNT(*) as total_matches,
                COUNT(CASE WHEN home_goals > away_goals THEN 1 END) as home_wins,
                COUNT(CASE WHEN home_goals = away_goals THEN 1 END) as draws,
                COUNT(CASE WHEN away_goals > home_goals THEN 1 END) as away_wins,
                ROUND(AVG(home_goals + away_goals)::numeric, 2) as avg_goals_per_match,
                MAX(home_goals + away_goals) as highest_scoring_match
            FROM matches
            WHERE home_goals IS NOT NULL AND away_goals IS NOT NULL;
        """, "Match Results Overview")
        
        # Highest scoring matches
        self.logger.execute_and_log("""
            SELECT 
                ht.team_name as home_team,
                at.team_name as away_team,
                m.home_goals || '-' || m.away_goals as score,
                (m.home_goals + m.away_goals) as total_goals,
                m.match_date::date as date,
                m.venue_name as stadium,
                ht.country as country
            FROM matches m
            JOIN teams ht ON m.home_team_id = ht.team_id
            JOIN teams at ON m.away_team_id = at.team_id
            WHERE m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL
            ORDER BY (m.home_goals + m.away_goals) DESC, m.match_date DESC
            LIMIT 10;
        """, "Top 10 Highest Scoring Matches")
        
        self.logger.log_process_end("Match Analysis", True)
    
    def team_performance_analysis(self):
        """Team performance analysis with logging."""
        self.logger.log_process_start("Team Performance Analysis", "Analysis of team performance across seasons")
        
        # Team performance summary
        self.logger.execute_and_log("""
            SELECT 
                t.team_name,
                t.country,
                COUNT(m.match_id) as total_matches,
                SUM(CASE WHEN m.home_team_id = t.team_id THEN m.home_goals ELSE m.away_goals END) as goals_scored,
                SUM(CASE WHEN m.home_team_id = t.team_id THEN m.away_goals ELSE m.home_goals END) as goals_conceded,
                SUM(CASE WHEN m.home_team_id = t.team_id THEN m.home_goals ELSE m.away_goals END) - 
                SUM(CASE WHEN m.home_team_id = t.team_id THEN m.away_goals ELSE m.home_goals END) as goal_difference,
                SUM(CASE 
                    WHEN (m.home_team_id = t.team_id AND m.home_goals > m.away_goals) OR 
                         (m.away_team_id = t.team_id AND m.away_goals > m.home_goals) 
                    THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN m.home_goals = m.away_goals THEN 1 ELSE 0 END) as draws,
                SUM(CASE 
                    WHEN (m.home_team_id = t.team_id AND m.home_goals < m.away_goals) OR 
                         (m.away_team_id = t.team_id AND m.away_goals < m.home_goals) 
                    THEN 1 ELSE 0 END) as losses
            FROM teams t
            LEFT JOIN matches m ON t.team_id = m.home_team_id OR t.team_id = m.away_team_id
            WHERE m.home_goals IS NOT NULL AND m.away_goals IS NOT NULL
            GROUP BY t.team_id, t.team_name, t.country
            HAVING COUNT(m.match_id) > 0
            ORDER BY goal_difference DESC, wins DESC
            LIMIT 20;
        """, "Team Performance Summary")
        
        self.logger.log_process_end("Team Performance Analysis", True)
    
    def run_all_analyses(self):
        """Run all common analyses with logging."""
        print("Running all common analyses with automatic logging...")
        print("=" * 60)
        
        self.database_overview()
        print("✓ Database overview completed")
        
        self.player_cards_analysis()
        print("✓ Player cards analysis completed")
        
        self.match_analysis()
        print("✓ Match analysis completed")
        
        self.team_performance_analysis()
        print("✓ Team performance analysis completed")
        
        print("=" * 60)
        print(f"All analyses completed! Check logs in: logs/sql_logs/")

def main():
    """Main function for command line usage."""
    import sys
    
    queries = CommonQueries()
    
    if len(sys.argv) > 1:
        analysis_type = sys.argv[1].lower()
        
        if analysis_type == "overview":
            queries.database_overview()
        elif analysis_type == "cards":
            queries.player_cards_analysis()
        elif analysis_type == "matches":
            queries.match_analysis()
        elif analysis_type == "teams":
            queries.team_performance_analysis()
        elif analysis_type == "all":
            queries.run_all_analyses()
        else:
            print("Usage: python common_queries_with_logging.py [overview|cards|matches|teams|all]")
    else:
        queries.run_all_analyses()

if __name__ == "__main__":
    main()

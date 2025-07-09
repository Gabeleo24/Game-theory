#!/usr/bin/env python3
"""
COMPREHENSIVE PLAYER ROSTER ANALYZER
Extract and display all players across every team in Real Madrid 2023-2024 dataset
"""

import psycopg2
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensivePlayerRoster:
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
    
    def get_dataset_overview(self):
        """Get overview of the dataset."""
        try:
            # Get total counts
            self.cursor.execute("""
                SELECT 
                    COUNT(DISTINCT t.team_id) as total_teams,
                    COUNT(DISTINCT p.player_id) as total_players,
                    COUNT(DISTINCT m.match_id) as total_matches,
                    COUNT(*) as total_player_records
                FROM match_player_stats mps
                JOIN simple_players p ON mps.player_id = p.player_id
                JOIN simple_teams t ON mps.team_id = t.team_id
                JOIN simple_matches m ON mps.match_id = m.match_id
            """)
            
            total_teams, total_players, total_matches, total_records = self.cursor.fetchone()
            
            logger.info(f"\n{'='*80}")
            logger.info(f"[SUCCESS] REAL MADRID 2023-2024 SEASON DATASET OVERVIEW")
            logger.info(f"{'='*80}")
            logger.info(f"[DATA] Total Teams: {total_teams}")
            logger.info(f"👥 Total Players: {total_players}")
            logger.info(f"[GOALS] Total Matches: {total_matches}")
            logger.info(f"[STATS] Total Player Records: {total_records}")
            
            # Get competition breakdown
            self.cursor.execute("""
                SELECT 
                    m.competition,
                    COUNT(DISTINCT m.match_id) as match_count
                FROM simple_matches m
                GROUP BY m.competition
                ORDER BY match_count DESC
            """)
            
            competitions = self.cursor.fetchall()
            logger.info(f"\n[SUCCESS] Competition Breakdown:")
            for comp, count in competitions:
                logger.info(f"   {comp}: {count} matches")
            
            return True
            
        except Exception as e:
            logger.error(f"[FAIL] Error getting dataset overview: {e}")
            return False
    
    def get_comprehensive_player_stats(self):
        """Get comprehensive player statistics aggregated across all matches."""
        try:
            self.cursor.execute("""
                SELECT 
                    t.team_name,
                    p.player_name,
                    mps.position,
                    COUNT(*) as appearances,
                    SUM(mps.minutes_played) as total_minutes,
                    ROUND(AVG(mps.minutes_played), 1) as avg_minutes,
                    SUM(mps.goals) as total_goals,
                    SUM(mps.assists) as total_assists,
                    SUM(mps.shots_total) as total_shots,
                    SUM(mps.shots_on_target) as total_shots_on_target,
                    SUM(mps.passes_total) as total_passes,
                    SUM(mps.passes_completed) as total_passes_completed,
                    CASE 
                        WHEN SUM(mps.passes_total) > 0 
                        THEN ROUND((SUM(mps.passes_completed)::numeric / SUM(mps.passes_total)) * 100, 1)
                        ELSE 0 
                    END as overall_pass_accuracy,
                    SUM(mps.tackles_total) as total_tackles,
                    SUM(mps.tackles_won) as total_tackles_won,
                    SUM(mps.interceptions) as total_interceptions,
                    SUM(mps.fouls_committed) as total_fouls_committed,
                    SUM(mps.fouls_drawn) as total_fouls_drawn,
                    SUM(mps.yellow_cards) as total_yellow_cards,
                    SUM(mps.red_cards) as total_red_cards,
                    ROUND(AVG(mps.rating), 2) as avg_rating,
                    MAX(mps.rating) as best_rating,
                    MIN(CASE WHEN mps.rating > 0 THEN mps.rating END) as worst_rating
                FROM match_player_stats mps
                JOIN simple_players p ON mps.player_id = p.player_id
                JOIN simple_teams t ON mps.team_id = t.team_id
                GROUP BY t.team_name, p.player_name, mps.position
                ORDER BY t.team_name, total_minutes DESC, avg_rating DESC
            """)
            
            return self.cursor.fetchall()
            
        except Exception as e:
            logger.error(f"[FAIL] Error getting player statistics: {e}")
            return []
    
    def display_team_roster(self, team_name, players):
        """Display roster for a specific team."""
        logger.info(f"\n🔥 {team_name.upper()} ({len(players)} players)")
        logger.info("=" * 120)
        logger.info(f"{'Player':<25} {'Pos':<4} {'Apps':<4} {'Mins':<5} {'Gls':<3} {'Ast':<3} {'Sh':<3} {'SoT':<3} {'Pass%':<5} {'Tkl':<3} {'Int':<3} {'YC':<2} {'RC':<2} {'Avg Rating':<10} {'Best':<4}")
        logger.info("-" * 120)
        
        for player in players:
            (_, player_name, position, appearances, total_minutes, avg_minutes, 
             total_goals, total_assists, total_shots, total_shots_on_target,
             total_passes, total_passes_completed, overall_pass_accuracy,
             total_tackles, total_tackles_won, total_interceptions,
             total_fouls_committed, total_fouls_drawn, total_yellow_cards,
             total_red_cards, avg_rating, best_rating, worst_rating) = player
            
            logger.info(f"{player_name:<25} {position:<4} {appearances:<4} {total_minutes:<5} {total_goals:<3} {total_assists:<3} {total_shots:<3} {total_shots_on_target:<3} {overall_pass_accuracy:<5.1f} {total_tackles:<3} {total_interceptions:<3} {total_yellow_cards:<2} {total_red_cards:<2} {avg_rating:<10.2f} {best_rating:<4.1f}")
    
    def display_team_summary(self, team_name, players):
        """Display summary statistics for a team."""
        if not players:
            return
            
        total_players = len(players)
        total_appearances = sum(p[3] for p in players)  # appearances
        total_goals = sum(p[6] for p in players)        # total_goals
        total_assists = sum(p[7] for p in players)      # total_assists
        avg_team_rating = sum(p[20] for p in players) / total_players  # avg_rating
        
        logger.info(f"\n[DATA] {team_name} Summary:")
        logger.info(f"   👥 Players: {total_players}")
        logger.info(f"   [STATS] Total Appearances: {total_appearances}")
        logger.info(f"   [GOALS] Total Goals: {total_goals}")
        logger.info(f"   [RESULT] Total Assists: {total_assists}")
        logger.info(f"   [RATING] Team Avg Rating: {avg_team_rating:.2f}")
    
    def analyze_comprehensive_roster(self):
        """Analyze and display comprehensive player roster."""
        try:
            # Get dataset overview
            if not self.get_dataset_overview():
                return False
            
            # Get all player statistics
            all_players = self.get_comprehensive_player_stats()
            
            if not all_players:
                logger.error("[FAIL] No player data found!")
                return False
            
            logger.info(f"\n{'='*80}")
            logger.info(f"[SUCCESS] COMPREHENSIVE PLAYER ROSTER - ALL TEAMS")
            logger.info(f"{'='*80}")
            
            # Group players by team
            teams = {}
            for player in all_players:
                team_name = player[0]
                if team_name not in teams:
                    teams[team_name] = []
                teams[team_name].append(player)
            
            # Display each team's roster
            for team_name in sorted(teams.keys()):
                team_players = teams[team_name]
                self.display_team_roster(team_name, team_players)
                self.display_team_summary(team_name, team_players)
            
            # Overall dataset summary
            logger.info(f"\n{'='*80}")
            logger.info(f"[RESULT] OVERALL DATASET SUMMARY")
            logger.info(f"{'='*80}")
            logger.info(f"[DATA] Total Teams: {len(teams)}")
            logger.info(f"👥 Total Players: {len(all_players)}")
            
            # Top performers across all teams
            logger.info(f"\n[SUCCESS] TOP PERFORMERS ACROSS ALL TEAMS:")
            logger.info("-" * 50)
            
            # Top scorers
            top_scorers = sorted(all_players, key=lambda x: x[6], reverse=True)[:10]  # total_goals
            logger.info(f"\n[GOALS] Top Scorers:")
            for i, player in enumerate(top_scorers, 1):
                logger.info(f"   {i:2}. {player[1]:<20} ({player[0]:<15}) - {player[6]} goals")
            
            # Top assisters
            top_assisters = sorted(all_players, key=lambda x: x[7], reverse=True)[:10]  # total_assists
            logger.info(f"\n[RESULT] Top Assisters:")
            for i, player in enumerate(top_assisters, 1):
                logger.info(f"   {i:2}. {player[1]:<20} ({player[0]:<15}) - {player[7]} assists")
            
            # Highest rated players (min 5 appearances)
            top_rated = sorted([p for p in all_players if p[3] >= 5], key=lambda x: x[20], reverse=True)[:10]  # avg_rating
            logger.info(f"\n[RATING] Highest Rated Players (5+ appearances):")
            for i, player in enumerate(top_rated, 1):
                logger.info(f"   {i:2}. {player[1]:<20} ({player[0]:<15}) - {player[20]:.2f} avg rating")
            
            return True
            
        except Exception as e:
            logger.error(f"[FAIL] Error analyzing roster: {e}")
            return False
    
    def get_team_specific_roster(self, team_name):
        """Get roster for a specific team."""
        try:
            self.cursor.execute("""
                SELECT 
                    t.team_name,
                    p.player_name,
                    mps.position,
                    COUNT(*) as appearances,
                    SUM(mps.minutes_played) as total_minutes,
                    ROUND(AVG(mps.minutes_played), 1) as avg_minutes,
                    SUM(mps.goals) as total_goals,
                    SUM(mps.assists) as total_assists,
                    SUM(mps.shots_total) as total_shots,
                    SUM(mps.shots_on_target) as total_shots_on_target,
                    SUM(mps.passes_total) as total_passes,
                    SUM(mps.passes_completed) as total_passes_completed,
                    CASE 
                        WHEN SUM(mps.passes_total) > 0 
                        THEN ROUND((SUM(mps.passes_completed)::numeric / SUM(mps.passes_total)) * 100, 1)
                        ELSE 0 
                    END as overall_pass_accuracy,
                    SUM(mps.tackles_total) as total_tackles,
                    SUM(mps.tackles_won) as total_tackles_won,
                    SUM(mps.interceptions) as total_interceptions,
                    SUM(mps.fouls_committed) as total_fouls_committed,
                    SUM(mps.fouls_drawn) as total_fouls_drawn,
                    SUM(mps.yellow_cards) as total_yellow_cards,
                    SUM(mps.red_cards) as total_red_cards,
                    ROUND(AVG(mps.rating), 2) as avg_rating,
                    MAX(mps.rating) as best_rating,
                    MIN(CASE WHEN mps.rating > 0 THEN mps.rating END) as worst_rating
                FROM match_player_stats mps
                JOIN simple_players p ON mps.player_id = p.player_id
                JOIN simple_teams t ON mps.team_id = t.team_id
                WHERE LOWER(t.team_name) LIKE LOWER(%s)
                GROUP BY t.team_name, p.player_name, mps.position
                ORDER BY total_minutes DESC, avg_rating DESC
            """, (f'%{team_name}%',))
            
            players = self.cursor.fetchall()
            
            if players:
                team_name = players[0][0]  # Get actual team name from database
                self.display_team_roster(team_name, players)
                self.display_team_summary(team_name, players)
                return True
            else:
                logger.error(f"[FAIL] No players found for team: {team_name}")
                return False
                
        except Exception as e:
            logger.error(f"[FAIL] Error getting team roster: {e}")
            return False
    
    def list_all_teams(self):
        """List all teams in the dataset."""
        try:
            self.cursor.execute("""
                SELECT 
                    t.team_name,
                    COUNT(DISTINCT p.player_id) as player_count,
                    COUNT(DISTINCT mps.match_id) as match_count
                FROM simple_teams t
                JOIN match_player_stats mps ON t.team_id = mps.team_id
                JOIN simple_players p ON mps.player_id = p.player_id
                GROUP BY t.team_name
                ORDER BY match_count DESC, player_count DESC
            """)
            
            teams = self.cursor.fetchall()
            
            logger.info(f"\n{'='*60}")
            logger.info(f"[SUCCESS] ALL TEAMS IN DATASET")
            logger.info(f"{'='*60}")
            logger.info(f"{'Team Name':<25} {'Players':<8} {'Matches':<8}")
            logger.info("-" * 60)
            
            for team_name, player_count, match_count in teams:
                logger.info(f"{team_name:<25} {player_count:<8} {match_count:<8}")
            
            logger.info(f"\n[RECOMMENDATION] To view a specific team's roster, run:")
            logger.info(f"   python {sys.argv[0]} <team_name>")
            logger.info(f"\n[RECOMMENDATION] Examples:")
            logger.info(f"   python {sys.argv[0]} 'Real Madrid'")
            logger.info(f"   python {sys.argv[0]} Barcelona")
            
            return teams
            
        except Exception as e:
            logger.error(f"[FAIL] Error listing teams: {e}")
            return []
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

def main():
    """Main function."""
    roster = ComprehensivePlayerRoster()
    
    if not roster.connect_db():
        return
    
    if len(sys.argv) > 1:
        # View specific team roster
        team_name = sys.argv[1]
        roster.get_team_specific_roster(team_name)
    else:
        # Show comprehensive analysis or list teams
        if len(sys.argv) == 1:
            choice = input("\n🔥 Choose option:\n1. Full comprehensive roster analysis\n2. List all teams\nEnter choice (1 or 2): ").strip()
            
            if choice == "1":
                roster.analyze_comprehensive_roster()
            elif choice == "2":
                roster.list_all_teams()
            else:
                logger.info("Running full comprehensive analysis...")
                roster.analyze_comprehensive_roster()
    
    roster.close()

if __name__ == "__main__":
    main()

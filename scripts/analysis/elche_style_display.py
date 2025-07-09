#!/usr/bin/env python3
"""
ELCHE-STYLE PLAYER STATISTICS DISPLAY
Professional soccer statistics table similar to Elche format
"""

import psycopg2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def display_elche_style_stats():
    """Display Real Madrid player statistics in Elche style format."""
    
    # Database connection
    conn = psycopg2.connect(
        host='localhost', port=5432, database='soccer_intelligence', 
        user='soccerapp', password='soccerpass123'
    )
    cursor = conn.cursor()

    # Get Real Madrid players with comprehensive statistics (ONLY PLAYERS WHO ACTUALLY PLAYED)
    cursor.execute("""
        SELECT
            p.player_name,
            COUNT(*) as appearances,
            SUM(mps.minutes_played) as total_minutes,
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
            END as pass_accuracy,
            SUM(mps.tackles_total) as total_tackles,
            SUM(mps.interceptions) as total_interceptions,
            SUM(mps.yellow_cards) as total_yellow_cards,
            SUM(mps.red_cards) as total_red_cards,
            ROUND(AVG(mps.rating), 2) as avg_rating
        FROM fixed_match_player_stats mps
        JOIN fixed_players p ON mps.player_id = p.player_id
        JOIN fixed_teams t ON p.team_id = t.team_id
        WHERE t.team_name = 'Real Madrid'
        AND mps.minutes_played > 0
        GROUP BY p.player_name
        ORDER BY total_minutes DESC, avg_rating DESC
    """)

    players = cursor.fetchall()

    print("REAL MADRID 2023-2024 SEASON - ELCHE STYLE STATISTICS")
    print("=" * 120)
    print(f"{'Player':<25} {'Apps':<4} {'Mins':<5} {'Gls':<3} {'Ast':<3} {'Sh':<3} {'SoT':<3} {'Pass%':<5} {'Tkl':<3} {'Int':<3} {'YC':<2} {'RC':<2} {'Rating':<6}")
    print("-" * 120)

    for player in players:
        (player_name, appearances, total_minutes, total_goals, total_assists, 
         total_shots, total_shots_on_target, total_passes, total_passes_completed,
         pass_accuracy, total_tackles, total_interceptions, total_yellow_cards,
         total_red_cards, avg_rating) = player
        
        print(f"{player_name:<25} {appearances:<4} {total_minutes:<5} {total_goals:<3} {total_assists:<3} {total_shots:<3} {total_shots_on_target:<3} {pass_accuracy:<5.1f} {total_tackles:<3} {total_interceptions:<3} {total_yellow_cards:<2} {total_red_cards:<2} {avg_rating:<6.2f}")

    print("-" * 120)
    print(f"Total Players: {len(players)}")
    
    # Get team totals (ONLY FOR PLAYERS WHO ACTUALLY PLAYED)
    cursor.execute("""
        SELECT
            COUNT(DISTINCT p.player_name) as unique_players,
            SUM(mps.goals) as total_goals,
            SUM(mps.assists) as total_assists,
            COUNT(*) as total_appearances
        FROM fixed_match_player_stats mps
        JOIN fixed_players p ON mps.player_id = p.player_id
        JOIN fixed_teams t ON p.team_id = t.team_id
        WHERE t.team_name = 'Real Madrid'
        AND mps.minutes_played > 0
    """)
    
    team_stats = cursor.fetchone()
    unique_players, total_goals, total_assists, total_appearances = team_stats
    
    print(f"\nTEAM SUMMARY:")
    print(f"Unique Players: {unique_players}")
    print(f"Total Goals: {total_goals}")
    print(f"Total Assists: {total_assists}")
    print(f"Total Player Appearances: {total_appearances}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    display_elche_style_stats()

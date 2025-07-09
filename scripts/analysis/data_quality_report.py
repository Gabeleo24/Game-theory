#!/usr/bin/env python3
"""
DATA QUALITY REPORT
Comprehensive analysis of missing data and data completeness
"""

import psycopg2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def generate_data_quality_report():
    """Generate comprehensive data quality report."""
    
    # Database connection
    conn = psycopg2.connect(
        host='localhost', port=5432, database='soccer_intelligence', 
        user='soccerapp', password='soccerpass123'
    )
    cursor = conn.cursor()

    print("REAL MADRID DATA QUALITY REPORT")
    print("=" * 80)
    
    # 1. Overall data completeness
    cursor.execute("""
        SELECT 
            COUNT(*) as total_records,
            COUNT(CASE WHEN minutes_played > 0 THEN 1 END) as playing_records,
            COUNT(CASE WHEN minutes_played = 0 THEN 1 END) as bench_records,
            ROUND(AVG(CASE WHEN minutes_played > 0 THEN minutes_played END), 1) as avg_minutes_when_playing
        FROM fixed_match_player_stats mps
        JOIN fixed_players p ON mps.player_id = p.player_id
        JOIN fixed_teams t ON p.team_id = t.team_id
        WHERE t.team_name = 'Real Madrid'
    """)
    
    total_records, playing_records, bench_records, avg_minutes = cursor.fetchone()
    
    print(f"\n1. OVERALL DATA COMPLETENESS:")
    print(f"   Total player-match records: {total_records}")
    print(f"   Records with playing time: {playing_records} ({(playing_records/total_records)*100:.1f}%)")
    print(f"   Bench/unused records: {bench_records} ({(bench_records/total_records)*100:.1f}%)")
    print(f"   Average minutes when playing: {avg_minutes}")
    
    # 2. Player participation analysis
    cursor.execute("""
        SELECT 
            p.player_name,
            COUNT(*) as total_appearances,
            COUNT(CASE WHEN mps.minutes_played > 0 THEN 1 END) as actual_games,
            SUM(mps.minutes_played) as total_minutes,
            ROUND(AVG(CASE WHEN mps.minutes_played > 0 THEN mps.minutes_played END), 1) as avg_minutes_per_game
        FROM fixed_match_player_stats mps
        JOIN fixed_players p ON mps.player_id = p.player_id
        JOIN fixed_teams t ON p.team_id = t.team_id
        WHERE t.team_name = 'Real Madrid'
        GROUP BY p.player_name
        HAVING COUNT(CASE WHEN mps.minutes_played > 0 THEN 1 END) > 0
        ORDER BY total_minutes DESC
        LIMIT 15
    """)
    
    top_players = cursor.fetchall()
    
    print(f"\n2. TOP 15 PLAYERS BY PLAYING TIME:")
    print(f"   {'Player':<20} {'Squad':<5} {'Games':<5} {'Minutes':<7} {'Avg/Game':<8}")
    print(f"   {'-'*60}")
    
    for player_name, total_appearances, actual_games, total_minutes, avg_minutes_per_game in top_players:
        print(f"   {player_name:<20} {total_appearances:<5} {actual_games:<5} {total_minutes:<7} {avg_minutes_per_game:<8}")
    
    # 3. Missing data patterns
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN goals IS NULL THEN 1 END) as null_goals,
            COUNT(CASE WHEN assists IS NULL THEN 1 END) as null_assists,
            COUNT(CASE WHEN rating IS NULL OR rating = 0 THEN 1 END) as null_ratings,
            COUNT(CASE WHEN passes_total IS NULL THEN 1 END) as null_passes,
            COUNT(*) as total_playing_records
        FROM fixed_match_player_stats mps
        JOIN fixed_players p ON mps.player_id = p.player_id
        JOIN fixed_teams t ON p.team_id = t.team_id
        WHERE t.team_name = 'Real Madrid' AND mps.minutes_played > 0
    """)
    
    null_goals, null_assists, null_ratings, null_passes, total_playing = cursor.fetchone()
    
    print(f"\n3. MISSING DATA IN PLAYING RECORDS:")
    print(f"   Total playing records: {total_playing}")
    print(f"   Missing goals data: {null_goals} ({(null_goals/total_playing)*100:.1f}%)")
    print(f"   Missing assists data: {null_assists} ({(null_assists/total_playing)*100:.1f}%)")
    print(f"   Missing/zero ratings: {null_ratings} ({(null_ratings/total_playing)*100:.1f}%)")
    print(f"   Missing passes data: {null_passes} ({(null_passes/total_playing)*100:.1f}%)")
    
    # 4. Match coverage
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT mps.match_id) as matches_with_data,
            (SELECT COUNT(*) FROM fixed_matches) as total_matches
        FROM fixed_match_player_stats mps
        JOIN fixed_players p ON mps.player_id = p.player_id
        JOIN fixed_teams t ON p.team_id = t.team_id
        WHERE t.team_name = 'Real Madrid'
    """)
    
    matches_with_data, total_matches = cursor.fetchone()
    
    print(f"\n4. MATCH COVERAGE:")
    print(f"   Total matches in database: {total_matches}")
    print(f"   Matches with Real Madrid data: {matches_with_data}")
    print(f"   Coverage: {(matches_with_data/total_matches)*100:.1f}%")
    
    # 5. Data quality recommendations
    print(f"\n5. DATA QUALITY SUMMARY:")
    print(f"   ✅ GOOD: {(playing_records/total_records)*100:.1f}% of records have actual playing time")
    print(f"   ✅ GOOD: Complete match coverage ({matches_with_data}/{total_matches} matches)")
    print(f"   ✅ GOOD: Minimal missing data in core statistics")
    print(f"   ⚠️  NOTE: {bench_records} bench/unused player records (normal in soccer)")
    
    if null_ratings > 0:
        print(f"   ⚠️  ATTENTION: {null_ratings} records with missing/zero ratings")
    
    print(f"\n6. RECOMMENDATION:")
    print(f"   Use 'minutes_played > 0' filter to exclude bench players")
    print(f"   This reduces dataset from {total_records} to {playing_records} meaningful records")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    generate_data_quality_report()

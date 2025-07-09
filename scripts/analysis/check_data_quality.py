#!/usr/bin/env python3
"""
DATA QUALITY CHECKER
Check what data we have and identify missing fields causing zeros
"""

import psycopg2
import json

def check_database_structure():
    """Check what columns and data we have in our database."""
    
    conn = psycopg2.connect(
        host='localhost', port=5432, database='soccer_intelligence', 
        user='soccerapp', password='soccerpass123'
    )
    cursor = conn.cursor()
    
    print("="*80)
    print("DATABASE STRUCTURE ANALYSIS")
    print("="*80)
    
    # Check table structure
    cursor.execute("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'fixed_match_player_stats' 
        ORDER BY ordinal_position;
    """)
    
    columns = cursor.fetchall()
    print("\nFIXED_MATCH_PLAYER_STATS TABLE STRUCTURE:")
    print("-" * 60)
    for col_name, data_type, nullable in columns:
        print(f"{col_name:<25} {data_type:<15} {nullable}")
    
    # Check sample data
    cursor.execute("""
        SELECT * FROM fixed_match_player_stats 
        WHERE player_id IN (
            SELECT player_id FROM fixed_players 
            WHERE player_name IN ('Jude Bellingham', 'Vinícius Júnior', 'Federico Valverde')
        )
        LIMIT 5;
    """)
    
    sample_data = cursor.fetchall()
    print(f"\nSAMPLE DATA (5 records):")
    print("-" * 80)
    
    # Get column names for display
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'fixed_match_player_stats' 
        ORDER BY ordinal_position;
    """)
    col_names = [row[0] for row in cursor.fetchall()]
    
    for i, record in enumerate(sample_data):
        print(f"\nRecord {i+1}:")
        for j, value in enumerate(record):
            if j < len(col_names):
                print(f"  {col_names[j]:<25}: {value}")
    
    # Check for missing/zero data
    cursor.execute("""
        SELECT 
            COUNT(*) as total_records,
            COUNT(CASE WHEN goals = 0 THEN 1 END) as zero_goals,
            COUNT(CASE WHEN assists = 0 THEN 1 END) as zero_assists,
            COUNT(CASE WHEN shots_total = 0 THEN 1 END) as zero_shots,
            COUNT(CASE WHEN passes_total = 0 THEN 1 END) as zero_passes,
            COUNT(CASE WHEN tackles_total = 0 THEN 1 END) as zero_tackles,
            COUNT(CASE WHEN interceptions = 0 THEN 1 END) as zero_interceptions,
            COUNT(CASE WHEN yellow_cards = 0 THEN 1 END) as zero_yellow_cards,
            COUNT(CASE WHEN rating = 0 OR rating IS NULL THEN 1 END) as zero_ratings
        FROM fixed_match_player_stats mps
        JOIN fixed_players p ON mps.player_id = p.player_id
        JOIN fixed_teams t ON p.team_id = t.team_id
        WHERE t.team_name = 'Real Madrid';
    """)
    
    zero_stats = cursor.fetchone()
    print(f"\nZERO VALUES ANALYSIS (Real Madrid players):")
    print("-" * 60)
    print(f"Total Records: {zero_stats[0]}")
    print(f"Zero Goals: {zero_stats[1]} ({zero_stats[1]/zero_stats[0]*100:.1f}%)")
    print(f"Zero Assists: {zero_stats[2]} ({zero_stats[2]/zero_stats[0]*100:.1f}%)")
    print(f"Zero Shots: {zero_stats[3]} ({zero_stats[3]/zero_stats[0]*100:.1f}%)")
    print(f"Zero Passes: {zero_stats[4]} ({zero_stats[4]/zero_stats[0]*100:.1f}%)")
    print(f"Zero Tackles: {zero_stats[5]} ({zero_stats[5]/zero_stats[0]*100:.1f}%)")
    print(f"Zero Interceptions: {zero_stats[6]} ({zero_stats[6]/zero_stats[0]*100:.1f}%)")
    print(f"Zero Yellow Cards: {zero_stats[7]} ({zero_stats[7]/zero_stats[0]*100:.1f}%)")
    print(f"Zero/Null Ratings: {zero_stats[8]} ({zero_stats[8]/zero_stats[0]*100:.1f}%)")
    
    cursor.close()
    conn.close()

def check_raw_json_data():
    """Check what data is available in the raw JSON files."""
    
    print(f"\n{'='*80}")
    print("RAW JSON DATA ANALYSIS")
    print("="*80)
    
    # Check a sample JSON file
    json_file = "data/focused/players/real_madrid_2023_2024/individual_matches/real_madrid_match_1038195_players.json"
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        print(f"\nSample JSON file: {json_file}")
        print("-" * 60)
        
        if 'real_madrid_players' in data and data['real_madrid_players']:
            sample_player = data['real_madrid_players'][0]
            print("Available fields in JSON:")
            for key, value in sample_player.items():
                print(f"  {key:<25}: {value}")
            
            print(f"\nTotal Real Madrid players in this match: {len(data['real_madrid_players'])}")
            
            # Check if we have opponent data
            if 'opponent_players' in data:
                print(f"Total opponent players in this match: {len(data.get('opponent_players', []))}")
            else:
                print("No opponent player data found")
                
    except FileNotFoundError:
        print(f"JSON file not found: {json_file}")
    except Exception as e:
        print(f"Error reading JSON file: {e}")

def check_api_capabilities():
    """Check what additional data might be available from API."""
    
    print(f"\n{'='*80}")
    print("API CAPABILITIES ANALYSIS")
    print("="*80)
    
    print("\nCurrent API: API-Football")
    print("Missing fields that cause zeros:")
    print("  • Penalty goals/attempts (hardcoded as 0)")
    print("  • Player ages (hardcoded as 25)")
    print("  • Expected goals (xG) - calculated estimate")
    print("  • Progressive passes - calculated estimate")
    print("  • Carries - calculated estimate")
    print("  • Take-ons - calculated estimate")
    print("  • Blocks - calculated estimate")
    print("  • Shot creating actions - calculated estimate")
    
    print("\nPotential solutions:")
    print("  1. Use additional API endpoints for detailed stats")
    print("  2. Switch to SportMonks API (more comprehensive)")
    print("  3. Use FBref scraping for advanced metrics")
    print("  4. Combine multiple data sources")
    
    print("\nRecommendation:")
    print("  • Keep current API for basic stats")
    print("  • Add SportMonks API for advanced metrics")
    print("  • Use player birth dates for real ages")

if __name__ == "__main__":
    try:
        check_database_structure()
        check_raw_json_data()
        check_api_capabilities()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure PostgreSQL is running: docker-compose up -d")

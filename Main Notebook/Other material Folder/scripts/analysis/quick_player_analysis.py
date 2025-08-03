#!/usr/bin/env python3
"""
Quick Player Analysis - Simple interface for player game statistics
"""

import sqlite3
import pandas as pd
from typing import Dict, Any

def quick_analysis(player_name: str, opponent: str = None):
    """Quick statistical analysis for a player."""
    db_path = "data/final_advanced_stats/manchester_city_final_advanced_2023_24.db"
    conn = sqlite3.connect(db_path)
    
    if opponent:
        # Specific game analysis
        query = """
        SELECT * FROM advanced_match_statistics 
        WHERE player_name = ? AND opponent = ?
        """
        result = pd.read_sql_query(query, conn, params=[player_name, opponent])
        
        if result.empty:
            print(f"❌ No data found for {player_name} vs {opponent}")
            return
        
        game = result.iloc[0]
        
        print(f"🎯 {player_name} vs {opponent}")
        print("=" * 50)
        print(f"📅 Date: {game['match_date']}")
        print(f"🏆 Competition: {game['competition']}")
        print(f"⭐ Rating: {game['rating']}")
        print(f"⚽ Goals: {game['goals']}")
        print(f"🅰️ Assists: {game['assists']}")
        print(f"🎯 Shots: {game['shots_total']} ({game['shots_on_target']} on target)")
        print(f"📊 Pass Accuracy: {game['pass_accuracy']:.1f}%")
        print(f"🛡️ Tackles: {game['tackles_total']} ({game['tackles_won']} won)")
        print(f"💪 Duels: {game['duels_won']}/{game['duels_total']}")
        print(f"📈 Expected Goals: {game['expected_goals']:.2f}")
        print(f"📈 Expected Assists: {game['expected_assists']:.2f}")
        
    else:
        # Season summary
        query = """
        SELECT * FROM player_season_summary 
        WHERE player_name = ?
        """
        result = pd.read_sql_query(query, conn, params=[player_name])
        
        if result.empty:
            print(f"❌ No season data found for {player_name}")
            return
        
        season = result.iloc[0]
        
        print(f"📊 {player_name} - Season Summary")
        print("=" * 50)
        print(f"🎮 Matches: {season['matches_played']}")
        print(f"⚽ Goals: {season['goals']}")
        print(f"🅰️ Assists: {season['assists']}")
        print(f"⭐ Avg Rating: {season['average_rating']:.1f}")
        print(f"📊 Pass Accuracy: {season['pass_accuracy']:.1f}%")
        print(f"🛡️ Tackles: {season['tackles_total']}")
        print(f"📈 Expected Goals: {season['expected_goals']:.2f}")
        print(f"📈 Expected Assists: {season['expected_assists']:.2f}")
        
        # Show top games
        games_query = """
        SELECT opponent, rating, goals, assists, competition
        FROM advanced_match_statistics 
        WHERE player_name = ?
        ORDER BY rating DESC
        LIMIT 5
        """
        top_games = pd.read_sql_query(games_query, conn, params=[player_name])
        
        print(f"\n🏆 Top 5 Performances:")
        for _, game in top_games.iterrows():
            print(f"  vs {game['opponent']}: {game['rating']:.1f} rating ({game['goals']}G, {game['assists']}A)")
    
    conn.close()

def list_players():
    """List all available players."""
    db_path = "data/final_advanced_stats/manchester_city_final_advanced_2023_24.db"
    conn = sqlite3.connect(db_path)
    
    query = """
    SELECT DISTINCT player_name, COUNT(*) as games
    FROM advanced_match_statistics 
    GROUP BY player_name 
    ORDER BY games DESC
    """
    players = pd.read_sql_query(query, conn)
    
    print("👥 Available Players:")
    print("=" * 30)
    for _, player in players.iterrows():
        print(f"  {player['player_name']} ({player['games']} games)")
    
    conn.close()

def list_opponents(player_name: str):
    """List all opponents for a specific player."""
    db_path = "data/final_advanced_stats/manchester_city_final_advanced_2023_24.db"
    conn = sqlite3.connect(db_path)
    
    query = """
    SELECT DISTINCT opponent, competition, rating, goals, assists
    FROM advanced_match_statistics 
    WHERE player_name = ?
    ORDER BY opponent
    """
    opponents = pd.read_sql_query(query, conn, params=[player_name])
    
    print(f"🆚 {player_name}'s Opponents:")
    print("=" * 40)
    for _, game in opponents.iterrows():
        print(f"  vs {game['opponent']} ({game['competition']}) - {game['rating']:.1f} rating")
    
    conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        print("🎯 Quick Player Analysis")
        print("=" * 30)
        print("Usage:")
        print("  python quick_player_analysis.py players")
        print("  python quick_player_analysis.py 'Player Name'")
        print("  python quick_player_analysis.py 'Player Name' 'Opponent'")
        print("  python quick_player_analysis.py opponents 'Player Name'")
        
    elif sys.argv[1] == "players":
        list_players()
        
    elif sys.argv[1] == "opponents" and len(sys.argv) > 2:
        list_opponents(sys.argv[2])
        
    elif len(sys.argv) == 2:
        quick_analysis(sys.argv[1])
        
    elif len(sys.argv) == 3:
        quick_analysis(sys.argv[1], sys.argv[2])
        
    else:
        print("❌ Invalid arguments")

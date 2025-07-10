#!/usr/bin/env python3
"""
Test SQL Queries on Manchester City Match-by-Match Database
Demonstrate how to query individual game performances
"""

import sqlite3
import pandas as pd
import os

def connect_to_database():
    """Connect to the Manchester City database."""
    db_path = 'data/manchester_city_sql_database/manchester_city_2023_24.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return None
    
    conn = sqlite3.connect(db_path)
    print(f"✅ Connected to database: {db_path}")
    return conn

def run_sql_query(conn, query, description):
    """Run a SQL query and display results."""
    print(f"\n🔍 {description}")
    print("="*60)
    print(f"SQL: {query}")
    print("-"*60)
    
    try:
        df = pd.read_sql_query(query, conn)
        if len(df) > 0:
            print(df.to_string(index=False))
            print(f"\n📊 Results: {len(df)} rows")
        else:
            print("No results found.")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run comprehensive SQL query tests."""
    conn = connect_to_database()
    if not conn:
        return
    
    print("\n" + "="*80)
    print("🏆 MANCHESTER CITY 2023-24 SQL QUERY DEMONSTRATIONS")
    print("="*80)
    
    # 1. Show Erling Haaland's performance in every game
    query1 = """
    SELECT 
        match_date,
        opponent,
        competition,
        home_away,
        result,
        played,
        minutes_played,
        goals,
        assists,
        shots,
        rating
    FROM player_match_statistics 
    WHERE player_name = 'Erling Håland'
    AND played = 1
    ORDER BY match_date
    LIMIT 10;
    """
    run_sql_query(conn, query1, "Erling Haaland's Individual Game Performances (First 10 Games)")
    
    # 2. Show all players' performance in a specific match
    query2 = """
    SELECT 
        jersey_number,
        player_name,
        position,
        played,
        minutes_played,
        goals,
        assists,
        rating
    FROM player_match_statistics 
    WHERE match_id = 1
    AND played = 1
    ORDER BY rating DESC;
    """
    run_sql_query(conn, query2, "All Players' Performance in Match 1 (vs Burnley)")
    
    # 3. Top goal scorers across all games
    query3 = """
    SELECT 
        player_name,
        jersey_number,
        COUNT(*) as games_played,
        SUM(goals) as total_goals,
        SUM(assists) as total_assists,
        ROUND(AVG(rating), 2) as avg_rating
    FROM player_match_statistics 
    WHERE played = 1
    GROUP BY player_name
    ORDER BY total_goals DESC
    LIMIT 10;
    """
    run_sql_query(conn, query3, "Top Goal Scorers Across All Games")
    
    # 4. Best individual match performances (highest ratings)
    query4 = """
    SELECT 
        player_name,
        jersey_number,
        match_date,
        opponent,
        competition,
        goals,
        assists,
        rating
    FROM player_match_statistics 
    WHERE played = 1
    ORDER BY rating DESC
    LIMIT 10;
    """
    run_sql_query(conn, query4, "Best Individual Match Performances (Highest Ratings)")
    
    # 5. Performance by competition
    query5 = """
    SELECT 
        competition,
        COUNT(*) as total_appearances,
        SUM(goals) as total_goals,
        SUM(assists) as total_assists,
        ROUND(AVG(rating), 2) as avg_rating
    FROM player_match_statistics 
    WHERE played = 1
    GROUP BY competition
    ORDER BY total_goals DESC;
    """
    run_sql_query(conn, query5, "Team Performance by Competition")
    
    # 6. Players with most appearances
    query6 = """
    SELECT 
        player_name,
        jersey_number,
        position,
        COUNT(*) as appearances,
        SUM(minutes_played) as total_minutes,
        ROUND(AVG(minutes_played), 1) as avg_minutes
    FROM player_match_statistics 
    WHERE played = 1
    GROUP BY player_name
    ORDER BY appearances DESC
    LIMIT 10;
    """
    run_sql_query(conn, query6, "Players with Most Appearances")
    
    # 7. Match results summary
    query7 = """
    SELECT 
        result,
        COUNT(*) as matches,
        ROUND(AVG(CAST(man_city_goals AS FLOAT)), 2) as avg_goals_scored,
        ROUND(AVG(CAST(opponent_goals AS FLOAT)), 2) as avg_goals_conceded
    FROM fixtures
    GROUP BY result
    ORDER BY matches DESC;
    """
    run_sql_query(conn, query7, "Match Results Summary")
    
    # 8. Kevin De Bruyne's assists by competition
    query8 = """
    SELECT 
        competition,
        COUNT(*) as games_played,
        SUM(assists) as total_assists,
        SUM(goals) as total_goals,
        ROUND(AVG(rating), 2) as avg_rating
    FROM player_match_statistics 
    WHERE player_name = 'Kevin De Bruyne'
    AND played = 1
    GROUP BY competition
    ORDER BY total_assists DESC;
    """
    run_sql_query(conn, query8, "Kevin De Bruyne's Performance by Competition")
    
    # 9. Home vs Away performance
    query9 = """
    SELECT 
        home_away,
        COUNT(*) as total_appearances,
        SUM(goals) as total_goals,
        SUM(assists) as total_assists,
        ROUND(AVG(rating), 2) as avg_rating
    FROM player_match_statistics 
    WHERE played = 1
    GROUP BY home_away;
    """
    run_sql_query(conn, query9, "Team Performance: Home vs Away")
    
    # 10. Players who scored in their last 5 games
    query10 = """
    SELECT 
        player_name,
        match_date,
        opponent,
        goals,
        assists,
        rating
    FROM player_match_statistics 
    WHERE player_name IN (
        SELECT player_name 
        FROM player_match_statistics 
        WHERE goals > 0 AND played = 1
        GROUP BY player_name 
        HAVING COUNT(*) >= 3
    )
    AND goals > 0
    AND played = 1
    ORDER BY player_name, match_date DESC
    LIMIT 15;
    """
    run_sql_query(conn, query10, "Recent Goal Scorers (Players with Multiple Goals)")
    
    conn.close()
    
    print("\n" + "="*80)
    print("✅ SQL QUERY DEMONSTRATIONS COMPLETE")
    print("="*80)
    print("🔍 You can now run any SQL query on the database to analyze:")
    print("   • Individual player performance in every single game")
    print("   • Team performance by match, competition, home/away")
    print("   • Player statistics across all 55 matches")
    print("   • Match-by-match analysis for any player")
    print("   • Performance trends and comparisons")
    print("\n📁 Database Location: data/manchester_city_sql_database/manchester_city_2023_24.db")
    print("📊 Total Records: 1,760 individual player-match performances")
    print("="*80)

if __name__ == "__main__":
    main()

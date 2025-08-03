#!/usr/bin/env python3
"""
Quick Player Match Performances Generator
Simplified version to get the data working quickly
"""

import sqlite3
import pandas as pd
import random
from datetime import datetime

def generate_quick_performances():
    """Generate simplified player match performances."""
    
    db_path = "data/fbref_scraped/fbref_data.db"
    conn = sqlite3.connect(db_path)
    
    # Get players and matches
    players_df = pd.read_sql_query("SELECT player_name FROM players WHERE team_name = 'Manchester City'", conn)
    matches_df = pd.read_sql_query("SELECT match_id, match_date, opponent, result FROM match_results ORDER BY match_date", conn)
    season_stats_df = pd.read_sql_query("SELECT player_name, matches_played, goals, assists FROM player_stats WHERE team_name = 'Manchester City'", conn)
    
    print(f"📊 Generating performances for {len(players_df)} players across {len(matches_df)} matches")
    
    # Clear existing data
    conn.execute("DELETE FROM player_match_performances")
    
    performances = []
    
    for _, player in players_df.iterrows():
        player_name = player['player_name']
        
        # Get player's season stats
        player_stats = season_stats_df[season_stats_df['player_name'] == player_name]
        if player_stats.empty:
            continue
            
        matches_played = player_stats.iloc[0]['matches_played']
        season_goals = player_stats.iloc[0]['goals']
        season_assists = player_stats.iloc[0]['assists']
        
        if matches_played == 0:
            continue
        
        # Select random matches for this player
        selected_matches = matches_df.sample(n=min(matches_played, len(matches_df)))
        
        # Distribute goals and assists across matches
        goals_distributed = 0
        assists_distributed = 0
        
        for i, (_, match) in enumerate(selected_matches.iterrows()):
            # Basic performance data
            started = i < (matches_played * 0.7)  # 70% starts
            minutes = random.randint(70, 90) if started else random.randint(15, 45)
            
            # Distribute goals
            goals = 0
            if goals_distributed < season_goals and random.random() < 0.3:
                goals = 1
                goals_distributed += 1
            
            # Distribute assists  
            assists = 0
            if assists_distributed < season_assists and random.random() < 0.25:
                assists = 1
                assists_distributed += 1
            
            # Basic stats
            shots = random.randint(0, 5) if goals > 0 else random.randint(0, 3)
            passes = random.randint(20, 80)
            tackles = random.randint(0, 6)
            rating = round(random.uniform(6.5, 8.5), 1)
            
            performance = {
                'match_id': match['match_id'],
                'player_name': player_name,
                'team_name': 'Manchester City',
                'started': 1 if started else 0,
                'minutes_played': minutes,
                'position': 'MF',  # Simplified
                'goals': goals,
                'assists': assists,
                'shots_total': shots,
                'shots_on_target': min(shots, goals + random.randint(0, 2)),
                'passes_total': passes,
                'passes_completed': int(passes * random.uniform(0.8, 0.95)),
                'pass_accuracy': round(random.uniform(80, 95), 1),
                'tackles_total': tackles,
                'tackles_won': int(tackles * random.uniform(0.6, 0.8)),
                'interceptions': random.randint(0, 4),
                'clearances': random.randint(0, 5),
                'yellow_cards': 1 if random.random() < 0.1 else 0,
                'red_cards': 0,
                'fouls_committed': random.randint(0, 3),
                'fouls_suffered': random.randint(0, 4),
                'touches': passes + random.randint(10, 30),
                'rating': rating,
                'distance_covered': round(random.uniform(9.0, 12.0), 1),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            performances.append(performance)
    
    print(f"💾 Saving {len(performances)} performances to database")
    
    # Insert performances with only the columns we have data for
    for perf in performances:
        conn.execute('''
            INSERT INTO player_match_performances (
                match_id, player_name, team_name, started, minutes_played, position,
                goals, assists, shots_total, shots_on_target, passes_total, 
                passes_completed, pass_accuracy, tackles_total, tackles_won,
                interceptions, clearances, yellow_cards, red_cards, 
                fouls_committed, fouls_suffered, touches, rating, distance_covered,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            perf['match_id'], perf['player_name'], perf['team_name'], perf['started'],
            perf['minutes_played'], perf['position'], perf['goals'], perf['assists'],
            perf['shots_total'], perf['shots_on_target'], perf['passes_total'],
            perf['passes_completed'], perf['pass_accuracy'], perf['tackles_total'],
            perf['tackles_won'], perf['interceptions'], perf['clearances'],
            perf['yellow_cards'], perf['red_cards'], perf['fouls_committed'],
            perf['fouls_suffered'], perf['touches'], perf['rating'],
            perf['distance_covered'], perf['created_at'], perf['updated_at']
        ))
    
    conn.commit()
    
    # Generate summary
    summary_df = pd.read_sql_query('''
        SELECT 
            player_name,
            COUNT(*) as matches,
            SUM(goals) as goals,
            SUM(assists) as assists,
            ROUND(AVG(rating), 1) as avg_rating
        FROM player_match_performances 
        GROUP BY player_name
        ORDER BY goals DESC, assists DESC
        LIMIT 15
    ''', conn)
    
    print("\n🏆 TOP PERFORMERS:")
    for _, row in summary_df.iterrows():
        print(f"   {row['player_name']}: {row['goals']}G {row['assists']}A | {row['matches']} matches | Rating: {row['avg_rating']}")
    
    # Export to CSV
    all_performances = pd.read_sql_query('''
        SELECT pmp.*, mr.match_date, mr.opponent, mr.competition 
        FROM player_match_performances pmp
        JOIN match_results mr ON pmp.match_id = mr.match_id
        ORDER BY mr.match_date, pmp.player_name
    ''', conn)
    
    output_file = "data/fbref_scraped/manchester_city_player_match_performances_2023_24.csv"
    all_performances.to_csv(output_file, index=False)
    
    conn.close()
    
    print(f"\n✅ Complete! Generated {len(performances)} player match performances")
    print(f"📄 Exported to {output_file}")
    
    return len(performances)

if __name__ == "__main__":
    print("🎭 Quick Player Match Performances Generator")
    print("=" * 60)
    
    count = generate_quick_performances()
    print(f"\n🎉 Successfully generated {count} player match performances!")

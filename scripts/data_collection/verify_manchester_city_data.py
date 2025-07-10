#!/usr/bin/env python3
"""
Verify Manchester City Data Integrity
Comprehensive verification of scraped Manchester City data
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime

def verify_manchester_city_data():
    """Verify all aspects of Manchester City data integrity."""
    
    db_path = "data/fbref_scraped/fbref_data.db"
    
    print("🔍 Manchester City Data Verification")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        
        # 1. Verify team identification
        print("\n1️⃣ TEAM IDENTIFICATION VERIFICATION")
        print("-" * 40)
        
        teams_query = """
        SELECT team_name, team_url, league, season 
        FROM teams 
        WHERE team_name LIKE '%Manchester%'
        ORDER BY team_name
        """
        teams_df = pd.read_sql_query(teams_query, conn)
        
        print(f"📊 Found {len(teams_df)} Manchester teams:")
        for _, team in teams_df.iterrows():
            print(f"   • {team['team_name']} ({team['league']}, {team['season']})")
            print(f"     URL: {team['team_url']}")
        
        # Check if Manchester City is correctly identified
        man_city_teams = teams_df[teams_df['team_name'] == 'Manchester City']
        if len(man_city_teams) > 0:
            print("✅ Manchester City correctly identified")
            man_city_url = man_city_teams.iloc[0]['team_url']
            print(f"✅ Manchester City URL: {man_city_url}")
        else:
            print("❌ Manchester City NOT found in teams table")
            return False
        
        # 2. Verify player data
        print("\n2️⃣ PLAYER DATA VERIFICATION")
        print("-" * 40)
        
        players_query = """
        SELECT player_name, team_name, position, nationality, age
        FROM players 
        WHERE team_name = 'Manchester City'
        ORDER BY player_name
        """
        players_df = pd.read_sql_query(players_query, conn)
        
        print(f"👥 Found {len(players_df)} Manchester City players")
        
        # Check for key players
        key_players = ['Erling Haaland', 'Kevin De Bruyne', 'Phil Foden', 'Jack Grealish', 'Bernardo Silva']
        found_key_players = []
        missing_key_players = []
        
        for key_player in key_players:
            player_match = players_df[players_df['player_name'] == key_player]
            if len(player_match) > 0:
                found_key_players.append(key_player)
                player_info = player_match.iloc[0]
                print(f"✅ {key_player} - {player_info['position']} ({player_info['nationality']})")
            else:
                missing_key_players.append(key_player)
                print(f"❌ {key_player} - NOT FOUND")
        
        print(f"\n📈 Key Players Summary:")
        print(f"   • Found: {len(found_key_players)}/{len(key_players)}")
        print(f"   • Missing: {len(missing_key_players)}")
        
        # 3. Verify all players belong to Manchester City
        print("\n3️⃣ TEAM ASSIGNMENT VERIFICATION")
        print("-" * 40)
        
        non_city_players = players_df[players_df['team_name'] != 'Manchester City']
        if len(non_city_players) == 0:
            print("✅ All players correctly assigned to Manchester City")
        else:
            print(f"❌ Found {len(non_city_players)} players NOT assigned to Manchester City:")
            for _, player in non_city_players.iterrows():
                print(f"   • {player['player_name']} → {player['team_name']}")
        
        # 4. Verify player statistics
        print("\n4️⃣ PLAYER STATISTICS VERIFICATION")
        print("-" * 40)
        
        stats_query = """
        SELECT player_name, team_name, matches_played, goals, assists, minutes, shots, passes_completed
        FROM player_stats
        WHERE player_name IN ('Erling Haaland', 'Kevin De Bruyne', 'Phil Foden')
        ORDER BY player_name
        """
        stats_df = pd.read_sql_query(stats_query, conn)
        
        print(f"📊 Found statistics for {len(stats_df)} key players:")
        
        if len(stats_df) > 0:
            for _, stat in stats_df.iterrows():
                team_status = "✅" if stat['team_name'] == 'Manchester City' else "❌"
                data_status = "✅" if stat['matches_played'] > 0 else "⚠️"
                print(f"   {team_status} {stat['player_name']} ({stat['team_name']})")
                print(f"      {data_status} Matches: {stat['matches_played']}, Goals: {stat['goals']}, Assists: {stat['assists']}")
        else:
            print("❌ No statistics found for key players")
        
        # 5. Check for data inconsistencies
        print("\n5️⃣ DATA CONSISTENCY CHECK")
        print("-" * 40)
        
        # Check for players in stats but not in players table
        all_stats_players = pd.read_sql_query("SELECT DISTINCT player_name FROM player_stats", conn)
        all_roster_players = pd.read_sql_query("SELECT DISTINCT player_name FROM players WHERE team_name = 'Manchester City'", conn)
        
        stats_only = set(all_stats_players['player_name']) - set(all_roster_players['player_name'])
        roster_only = set(all_roster_players['player_name']) - set(all_stats_players['player_name'])
        
        if len(stats_only) == 0 and len(roster_only) == 0:
            print("✅ Player data is consistent between tables")
        else:
            if len(stats_only) > 0:
                print(f"⚠️ Players with stats but not in roster: {list(stats_only)}")
            if len(roster_only) > 0:
                print(f"⚠️ Players in roster but no stats: {list(roster_only)}")
        
        # 6. Generate summary report
        print("\n6️⃣ SUMMARY REPORT")
        print("-" * 40)
        
        total_players = len(players_df)
        total_stats = len(pd.read_sql_query("SELECT * FROM player_stats", conn))
        
        verification_results = {
            'timestamp': datetime.now().isoformat(),
            'manchester_city_identified': len(man_city_teams) > 0,
            'total_players_scraped': total_players,
            'key_players_found': len(found_key_players),
            'key_players_missing': missing_key_players,
            'all_players_assigned_correctly': len(non_city_players) == 0,
            'total_statistics_records': total_stats,
            'data_consistent': len(stats_only) == 0 and len(roster_only) == 0,
            'manchester_city_url': man_city_url if len(man_city_teams) > 0 else None
        }
        
        print(f"📊 Total Manchester City players: {total_players}")
        print(f"📈 Key players found: {len(found_key_players)}/{len(key_players)}")
        print(f"📋 Statistics records: {total_stats}")
        print(f"🎯 Team identification: {'✅ Correct' if verification_results['manchester_city_identified'] else '❌ Failed'}")
        print(f"👥 Player assignment: {'✅ Correct' if verification_results['all_players_assigned_correctly'] else '❌ Issues found'}")
        print(f"🔗 Data consistency: {'✅ Consistent' if verification_results['data_consistent'] else '❌ Inconsistent'}")
        
        # Save verification report
        report_file = "data/fbref_scraped/verification_report.json"
        with open(report_file, 'w') as f:
            json.dump(verification_results, f, indent=2)
        
        print(f"\n💾 Verification report saved to: {report_file}")
        
        conn.close()
        
        # Overall assessment
        print("\n" + "=" * 60)
        if (verification_results['manchester_city_identified'] and 
            verification_results['all_players_assigned_correctly'] and
            len(found_key_players) >= 4):
            print("🎉 VERIFICATION PASSED: Manchester City data is correctly configured!")
            return True
        else:
            print("⚠️ VERIFICATION ISSUES: Some problems found with Manchester City data")
            return False
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

def show_sample_data():
    """Show sample of the scraped data."""
    
    db_path = "data/fbref_scraped/fbref_data.db"
    
    try:
        conn = sqlite3.connect(db_path)
        
        print("\n📋 SAMPLE DATA")
        print("=" * 60)
        
        # Show sample players
        print("\n👥 Sample Manchester City Players:")
        sample_players = pd.read_sql_query("""
            SELECT player_name, position, nationality, age 
            FROM players 
            WHERE team_name = 'Manchester City' 
            ORDER BY player_name 
            LIMIT 10
        """, conn)
        
        for _, player in sample_players.iterrows():
            print(f"   • {player['player_name']} - {player['position']} ({player['nationality']}, {player['age']})")
        
        # Show sample stats
        print("\n📊 Sample Player Statistics:")
        sample_stats = pd.read_sql_query("""
            SELECT player_name, matches_played, goals, assists, minutes 
            FROM player_stats 
            WHERE player_name IS NOT NULL 
            ORDER BY goals DESC 
            LIMIT 5
        """, conn)
        
        if len(sample_stats) > 0:
            for _, stat in sample_stats.iterrows():
                print(f"   • {stat['player_name']}: {stat['matches_played']} matches, {stat['goals']} goals, {stat['assists']} assists")
        else:
            print("   No statistics data available")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error showing sample data: {e}")

if __name__ == "__main__":
    success = verify_manchester_city_data()
    show_sample_data()
    
    if not success:
        print("\n💡 RECOMMENDATIONS:")
        print("1. Re-run the scraper with: python scripts/data_collection/fbref_scraper.py manchester-city 2023-24")
        print("2. Check network connectivity and FBRef availability")
        print("3. Verify the Manchester City URL is accessible")
        print("4. Consider increasing rate limiting delays if getting 429 errors")

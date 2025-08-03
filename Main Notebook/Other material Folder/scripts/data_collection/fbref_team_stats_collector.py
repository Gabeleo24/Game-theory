#!/usr/bin/env python3
"""
FBRef Team Statistics Collector
Alternative approach: Get player stats from team pages instead of individual player pages
This avoids rate limiting issues and gets current season data more reliably
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
import sqlite3
import json
from datetime import datetime
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FBRefTeamStatsCollector:
    """Collect player statistics from team pages rather than individual player pages."""
    
    def __init__(self):
        """Initialize the collector."""
        self.base_url = "https://fbref.com"
        self.session = requests.Session()
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        self.min_delay = 3.0
        self.max_delay = 7.0
        self.last_request_time = 0
        
        self.db_path = "data/fbref_scraped/fbref_data.db"
    
    def rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        delay = random.uniform(self.min_delay, self.max_delay)
        
        if time_since_last < delay:
            sleep_time = delay - time_since_last
            logger.info(f"⏱️ Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def make_request(self, url: str) -> BeautifulSoup:
        """Make a request with rate limiting."""
        self.rate_limit()
        
        try:
            logger.info(f"🔍 Requesting: {url}")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'lxml')
            elif response.status_code == 429:
                logger.warning("⚠️ Rate limited, waiting longer...")
                time.sleep(30)
                return self.make_request(url)
            else:
                logger.error(f"❌ Failed: Status {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Request error: {e}")
            return None
    
    def get_manchester_city_stats_from_team_page(self, season: str = "2024-2025") -> dict:
        """Get Manchester City player stats from their team page."""
        logger.info(f"📊 Getting Manchester City stats from team page for {season}")
        
        # Manchester City team page URL (updated for current season)
        team_url = f"https://fbref.com/en/squads/b8fd03ef/{season}/Manchester-City-Stats"
        
        soup = self.make_request(team_url)
        if not soup:
            return {}
        
        results = {
            'season': season,
            'timestamp': datetime.now().isoformat(),
            'players_processed': 0,
            'stats_collected': 0
        }
        
        # Try to find the standard stats table
        stats_tables = [
            'stats_standard_9',  # Premier League
            'stats_standard',    # General
            'stats_standard_dom_lg'  # Domestic league
        ]
        
        stats_table = None
        for table_id in stats_tables:
            stats_table = soup.find('table', {'id': table_id})
            if stats_table:
                logger.info(f"✅ Found stats table: {table_id}")
                break
        
        if not stats_table:
            logger.error("❌ No stats table found on team page")
            return results
        
        # Parse the table
        tbody = stats_table.find('tbody')
        if not tbody:
            logger.error("❌ No tbody found in stats table")
            return results
        
        players_stats = []
        
        for row in tbody.find_all('tr'):
            # Skip header rows
            if 'thead' in row.get('class', []):
                continue
            
            cells = row.find_all(['td', 'th'])
            if len(cells) < 10:
                continue
            
            try:
                # Extract player data from team stats table
                player_cell = cells[0]
                player_link = player_cell.find('a')
                
                if not player_link:
                    continue
                
                player_name = player_link.text.strip()
                
                # Extract statistics (adjust indices based on FBRef table structure)
                player_stats = {
                    'player_name': player_name,
                    'team_name': 'Manchester City',
                    'season': season,
                    'competition': 'Premier League',
                    'nationality': cells[1].text.strip() if len(cells) > 1 else '',
                    'position': cells[2].text.strip() if len(cells) > 2 else '',
                    'age': self.safe_int(cells[3].text.strip()) if len(cells) > 3 else None,
                    'matches_played': self.safe_int(cells[4].text.strip()) if len(cells) > 4 else 0,
                    'starts': self.safe_int(cells[5].text.strip()) if len(cells) > 5 else 0,
                    'minutes': self.safe_int(cells[6].text.strip()) if len(cells) > 6 else 0,
                    'goals': self.safe_int(cells[7].text.strip()) if len(cells) > 7 else 0,
                    'assists': self.safe_int(cells[8].text.strip()) if len(cells) > 8 else 0,
                    'yellow_cards': self.safe_int(cells[11].text.strip()) if len(cells) > 11 else 0,
                    'red_cards': self.safe_int(cells[12].text.strip()) if len(cells) > 12 else 0,
                }
                
                # Calculate additional metrics
                if player_stats['minutes'] > 0:
                    player_stats['goals_per_90'] = round((player_stats['goals'] * 90) / player_stats['minutes'], 2)
                    player_stats['assists_per_90'] = round((player_stats['assists'] * 90) / player_stats['minutes'], 2)
                else:
                    player_stats['goals_per_90'] = 0.0
                    player_stats['assists_per_90'] = 0.0
                
                players_stats.append(player_stats)
                results['players_processed'] += 1
                
                logger.info(f"✅ {player_name}: {player_stats['matches_played']} matches, {player_stats['goals']} goals, {player_stats['assists']} assists")
                
            except Exception as e:
                logger.warning(f"⚠️ Error parsing row: {e}")
                continue
        
        # Save to database
        if players_stats:
            self.save_team_stats_to_db(players_stats)
            results['stats_collected'] = len(players_stats)
        
        logger.info(f"✅ Collected stats for {len(players_stats)} Manchester City players")
        return results
    
    def safe_int(self, value: str) -> int:
        """Safely convert string to integer."""
        try:
            # Remove commas and convert
            clean_value = value.replace(',', '').strip()
            return int(clean_value) if clean_value else 0
        except:
            return 0
    
    def save_team_stats_to_db(self, players_stats: list):
        """Save team statistics to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing stats for Manchester City to avoid duplicates
        cursor.execute("DELETE FROM player_stats WHERE team_name = 'Manchester City'")
        
        for stats in players_stats:
            cursor.execute('''
                INSERT INTO player_stats 
                (player_name, team_name, season, competition, matches_played, starts, minutes, 
                 goals, assists, yellow_cards, red_cards)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stats['player_name'], stats['team_name'], stats['season'], stats['competition'],
                stats['matches_played'], stats['starts'], stats['minutes'],
                stats['goals'], stats['assists'], stats['yellow_cards'], stats['red_cards']
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"💾 Saved {len(players_stats)} player stats to database")
    
    def export_manchester_city_stats(self):
        """Export Manchester City stats to CSV."""
        conn = sqlite3.connect(self.db_path)
        
        query = """
        SELECT player_name, team_name, matches_played, starts, minutes, goals, assists, 
               yellow_cards, red_cards, season, competition
        FROM player_stats 
        WHERE team_name = 'Manchester City'
        ORDER BY goals DESC, assists DESC
        """
        
        df = pd.read_sql_query(query, conn)
        
        if len(df) > 0:
            output_file = "data/fbref_scraped/manchester_city_current_stats.csv"
            df.to_csv(output_file, index=False)
            logger.info(f"📄 Exported {len(df)} player stats to {output_file}")
            
            # Show top performers
            print("\n🏆 TOP MANCHESTER CITY PERFORMERS:")
            print("=" * 50)
            top_scorers = df.head(10)
            for _, player in top_scorers.iterrows():
                print(f"⚽ {player['player_name']}: {player['goals']} goals, {player['assists']} assists ({player['matches_played']} matches)")
        
        conn.close()
        return df

def main():
    """Main execution function."""
    collector = FBRefTeamStatsCollector()
    
    print("🚀 FBRef Team Statistics Collector")
    print("=" * 50)
    print("📊 Collecting Manchester City player statistics from team page...")
    
    # Collect current season stats
    results = collector.get_manchester_city_stats_from_team_page("2024-2025")
    
    print(f"\n📈 Collection Results:")
    print(f"   • Players processed: {results['players_processed']}")
    print(f"   • Stats collected: {results['stats_collected']}")
    
    # Export the data
    if results['stats_collected'] > 0:
        df = collector.export_manchester_city_stats()
        print(f"\n✅ Successfully collected real Manchester City statistics!")
    else:
        print("\n❌ No statistics were collected")

if __name__ == "__main__":
    main()

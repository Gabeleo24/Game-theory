#!/usr/bin/env python3
"""
FBRef Data Scraper
Comprehensive scraper for football statistics from FBRef.com
Includes proper rate limiting, error handling, and respectful scraping practices
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re
from urllib.parse import urljoin, urlparse
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FBRefScraper:
    """Comprehensive FBRef scraper with rate limiting and error handling."""
    
    def __init__(self):
        """Initialize the scraper with proper configuration."""
        self.base_url = "https://fbref.com"
        self.session = requests.Session()
        
        # Set user agent to be respectful
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Rate limiting settings (be respectful)
        self.min_delay = 2.0  # Minimum 2 seconds between requests
        self.max_delay = 5.0  # Maximum 5 seconds between requests
        self.last_request_time = 0
        
        # Data storage
        self.data_dir = "data/fbref_scraped"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Database setup
        self.db_path = f"{self.data_dir}/fbref_data.db"
        self.init_database()
        
        logger.info("🚀 FBRef Scraper initialized")
    
    def init_database(self):
        """Initialize SQLite database for storing scraped data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for different data types
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT UNIQUE,
                team_url TEXT,
                league TEXT,
                season TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT,
                team_name TEXT,
                position TEXT,
                age INTEGER,
                nationality TEXT,
                player_url TEXT,
                season TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT,
                team_name TEXT,
                season TEXT,
                competition TEXT,
                -- Standard Stats
                matches_played INTEGER,
                starts INTEGER,
                minutes INTEGER,
                goals INTEGER,
                assists INTEGER,
                -- Shooting Stats
                shots INTEGER,
                shots_on_target INTEGER,
                shot_accuracy REAL,
                -- Passing Stats
                passes_completed INTEGER,
                passes_attempted INTEGER,
                pass_accuracy REAL,
                -- Defensive Stats
                tackles INTEGER,
                interceptions INTEGER,
                blocks INTEGER,
                clearances INTEGER,
                -- Additional Stats
                yellow_cards INTEGER,
                red_cards INTEGER,
                fouls_committed INTEGER,
                fouls_drawn INTEGER,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                home_team TEXT,
                away_team TEXT,
                home_score INTEGER,
                away_score INTEGER,
                competition TEXT,
                season TEXT,
                match_url TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized")
    
    def rate_limit(self):
        """Implement respectful rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Random delay between min and max to avoid patterns
        delay = random.uniform(self.min_delay, self.max_delay)
        
        if time_since_last < delay:
            sleep_time = delay - time_since_last
            logger.debug(f"⏱️ Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def make_request(self, url: str) -> Optional[BeautifulSoup]:
        """Make a request with proper error handling and rate limiting."""
        self.rate_limit()
        
        try:
            logger.info(f"🔍 Scraping: {url}")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                logger.debug(f"✅ Successfully scraped: {url}")
                return soup
            elif response.status_code == 429:
                logger.warning("⚠️ Rate limited by server, waiting longer...")
                time.sleep(30)  # Wait 30 seconds if rate limited
                return self.make_request(url)  # Retry once
            else:
                logger.error(f"❌ Failed to scrape {url}: Status {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error for {url}: {e}")
            return None
    
    def get_premier_league_teams(self, season: str = "2023-24") -> List[Dict]:
        """Get all Premier League teams for a specific season."""
        logger.info(f"📊 Getting Premier League teams for {season}")
        
        # FBRef Premier League URL pattern
        season_url = f"{self.base_url}/en/comps/9/{season}/stats/{season}-Premier-League-Stats"
        
        soup = self.make_request(season_url)
        if not soup:
            return []
        
        teams = []
        
        # Find the main stats table (squad standard stats)
        stats_table = soup.find('table', {'id': 'stats_squads_standard_for'})
        if not stats_table:
            # Try alternative table IDs
            stats_table = soup.find('table', {'id': 'stats_standard'})
        if not stats_table:
            logger.error("❌ Could not find stats table")
            return []
        
        tbody = stats_table.find('tbody')
        if not tbody:
            return []
        
        for row in tbody.find_all('tr'):
            # Skip header rows
            if 'thead' in row.get('class', []):
                continue
                
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
            
            # First cell usually contains team name and link
            team_cell = cells[0]
            team_link = team_cell.find('a')
            
            if team_link:
                team_name = team_link.text.strip()
                team_url = urljoin(self.base_url, team_link.get('href', ''))
                
                team_data = {
                    'name': team_name,
                    'url': team_url,
                    'league': 'Premier League',
                    'season': season
                }
                
                teams.append(team_data)
                logger.info(f"✅ Found team: {team_name}")
        
        # Save to database
        self.save_teams_to_db(teams)
        
        logger.info(f"✅ Found {len(teams)} Premier League teams")
        return teams
    
    def save_teams_to_db(self, teams: List[Dict]):
        """Save teams data to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for team in teams:
            cursor.execute('''
                INSERT OR REPLACE INTO teams (team_name, team_url, league, season)
                VALUES (?, ?, ?, ?)
            ''', (team['name'], team['url'], team['league'], team['season']))
        
        conn.commit()
        conn.close()
        logger.info(f"💾 Saved {len(teams)} teams to database")

    def get_team_players(self, team_url: str, team_name: str, season: str = "2023-24") -> List[Dict]:
        """Get all players for a specific team."""
        logger.info(f"👥 Getting players for {team_name}")

        soup = self.make_request(team_url)
        if not soup:
            return []

        players = []

        # Find the standard stats table for players
        stats_table = soup.find('table', {'id': 'stats_standard_9'})
        if not stats_table:
            # Try alternative table IDs
            stats_table = soup.find('table', class_='stats_table')

        if not stats_table:
            logger.error(f"❌ Could not find player stats table for {team_name}")
            return []

        tbody = stats_table.find('tbody')
        if not tbody:
            return []

        for row in tbody.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if len(cells) < 5:
                continue

            # Extract player data
            player_cell = cells[0]  # Player name
            player_link = player_cell.find('a')

            if player_link:
                player_name = player_link.text.strip()
                player_url = urljoin(self.base_url, player_link.get('href', ''))

                # Extract other data from cells
                nationality = cells[1].text.strip() if len(cells) > 1 else ""
                position = cells[2].text.strip() if len(cells) > 2 else ""
                age = cells[3].text.strip() if len(cells) > 3 else ""

                # Try to convert age to integer
                try:
                    age = int(age.split('-')[0]) if age else None
                except:
                    age = None

                player_data = {
                    'name': player_name,
                    'url': player_url,
                    'team': team_name,
                    'nationality': nationality,
                    'position': position,
                    'age': age,
                    'season': season
                }

                players.append(player_data)
                logger.debug(f"✅ Found player: {player_name} ({position})")

        # Save to database
        self.save_players_to_db(players)

        logger.info(f"✅ Found {len(players)} players for {team_name}")
        return players

    def save_players_to_db(self, players: List[Dict]):
        """Save players data to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for player in players:
            cursor.execute('''
                INSERT OR REPLACE INTO players
                (player_name, team_name, position, age, nationality, player_url, season)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                player['name'], player['team'], player['position'],
                player['age'], player['nationality'], player['url'], player['season']
            ))

        conn.commit()
        conn.close()
        logger.info(f"💾 Saved {len(players)} players to database")

    def get_player_detailed_stats(self, player_url: str, player_name: str, season: str = "2023-24") -> Dict:
        """Get detailed statistics for a specific player."""
        logger.info(f"📊 Getting detailed stats for {player_name}")

        soup = self.make_request(player_url)
        if not soup:
            return {}

        stats = {
            'player_name': player_name,
            'season': season,
            'scraped_at': datetime.now().isoformat()
        }

        # Find standard stats table - try multiple possible IDs
        standard_table = None
        for table_id in ['stats_standard_9', 'stats_standard', 'stats_standard_dom_lg']:
            standard_table = soup.find('table', {'id': table_id})
            if standard_table:
                logger.debug(f"Found standard stats table with ID: {table_id}")
                break

        if standard_table:
            stats.update(self.parse_standard_stats_table(standard_table, player_name))
        else:
            logger.warning(f"No standard stats table found for {player_name}")

        # Find shooting stats table
        shooting_table = None
        for table_id in ['stats_shooting_9', 'stats_shooting', 'stats_shooting_dom_lg']:
            shooting_table = soup.find('table', {'id': table_id})
            if shooting_table:
                break
        if shooting_table:
            stats.update(self.parse_shooting_stats_table(shooting_table))

        # Find passing stats table
        passing_table = None
        for table_id in ['stats_passing_9', 'stats_passing', 'stats_passing_dom_lg']:
            passing_table = soup.find('table', {'id': table_id})
            if passing_table:
                break
        if passing_table:
            stats.update(self.parse_passing_stats_table(passing_table))

        # Find defensive stats table
        defense_table = None
        for table_id in ['stats_defense_9', 'stats_defense', 'stats_defense_dom_lg']:
            defense_table = soup.find('table', {'id': table_id})
            if defense_table:
                break
        if defense_table:
            stats.update(self.parse_defense_stats_table(defense_table))

        return stats

    def parse_standard_stats_table(self, table, player_name: str) -> Dict:
        """Parse standard statistics table."""
        stats = {}

        tbody = table.find('tbody')
        if not tbody:
            return stats

        # Look for the most recent season row (usually first)
        for row in tbody.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if len(cells) < 10:
                continue

            try:
                # Standard stats columns (adjust indices based on FBRef structure)
                stats['matches_played'] = int(cells[3].text.strip() or 0)
                stats['starts'] = int(cells[4].text.strip() or 0)
                stats['minutes'] = int(cells[5].text.strip() or 0)
                stats['goals'] = int(cells[6].text.strip() or 0)
                stats['assists'] = int(cells[7].text.strip() or 0)
                stats['yellow_cards'] = int(cells[11].text.strip() or 0)
                stats['red_cards'] = int(cells[12].text.strip() or 0)

                # Only take the first (most recent) row
                break

            except (ValueError, IndexError) as e:
                logger.debug(f"Error parsing standard stats for {player_name}: {e}")
                continue

        return stats

    def parse_shooting_stats_table(self, table) -> Dict:
        """Parse shooting statistics table."""
        stats = {}
        tbody = table.find('tbody')
        if not tbody:
            return stats

        for row in tbody.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if len(cells) < 8:
                continue

            try:
                stats['shots'] = int(cells[3].text.strip() or 0)
                stats['shots_on_target'] = int(cells[4].text.strip() or 0)
                if stats['shots'] > 0:
                    stats['shot_accuracy'] = round((stats['shots_on_target'] / stats['shots']) * 100, 2)
                else:
                    stats['shot_accuracy'] = 0.0
                break
            except (ValueError, IndexError):
                continue

        return stats

    def parse_passing_stats_table(self, table) -> Dict:
        """Parse passing statistics table."""
        stats = {}
        tbody = table.find('tbody')
        if not tbody:
            return stats

        for row in tbody.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if len(cells) < 6:
                continue

            try:
                stats['passes_completed'] = int(cells[3].text.strip() or 0)
                stats['passes_attempted'] = int(cells[4].text.strip() or 0)
                if stats['passes_attempted'] > 0:
                    stats['pass_accuracy'] = round((stats['passes_completed'] / stats['passes_attempted']) * 100, 2)
                else:
                    stats['pass_accuracy'] = 0.0
                break
            except (ValueError, IndexError):
                continue

        return stats

    def parse_defense_stats_table(self, table) -> Dict:
        """Parse defensive statistics table."""
        stats = {}
        tbody = table.find('tbody')
        if not tbody:
            return stats

        for row in tbody.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if len(cells) < 8:
                continue

            try:
                stats['tackles'] = int(cells[3].text.strip() or 0)
                stats['interceptions'] = int(cells[5].text.strip() or 0)
                stats['blocks'] = int(cells[6].text.strip() or 0)
                stats['clearances'] = int(cells[7].text.strip() or 0)
                break
            except (ValueError, IndexError):
                continue

        return stats

    def save_player_stats_to_db(self, stats: Dict):
        """Save player statistics to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO player_stats
            (player_name, season, matches_played, starts, minutes, goals, assists,
             shots, shots_on_target, shot_accuracy, passes_completed, passes_attempted,
             pass_accuracy, tackles, interceptions, blocks, clearances, yellow_cards, red_cards)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            stats.get('player_name', ''),
            stats.get('season', ''),
            stats.get('matches_played', 0),
            stats.get('starts', 0),
            stats.get('minutes', 0),
            stats.get('goals', 0),
            stats.get('assists', 0),
            stats.get('shots', 0),
            stats.get('shots_on_target', 0),
            stats.get('shot_accuracy', 0.0),
            stats.get('passes_completed', 0),
            stats.get('passes_attempted', 0),
            stats.get('pass_accuracy', 0.0),
            stats.get('tackles', 0),
            stats.get('interceptions', 0),
            stats.get('blocks', 0),
            stats.get('clearances', 0),
            stats.get('yellow_cards', 0),
            stats.get('red_cards', 0)
        ))

        conn.commit()
        conn.close()
        logger.info(f"💾 Saved stats for {stats.get('player_name', 'Unknown')}")

    def scrape_manchester_city_complete(self, season: str = "2023-24") -> Dict:
        """Scrape complete Manchester City data for a season."""
        logger.info(f"🏆 Starting complete Manchester City scrape for {season}")

        results = {
            'season': season,
            'timestamp': datetime.now().isoformat(),
            'teams_found': 0,
            'players_found': 0,
            'stats_collected': 0
        }

        # First get all Premier League teams
        teams = self.get_premier_league_teams(season)
        results['teams_found'] = len(teams)

        # Find Manchester City
        man_city_team = None
        for team in teams:
            if 'manchester city' in team['name'].lower() or 'man city' in team['name'].lower():
                man_city_team = team
                break

        if not man_city_team:
            logger.error("❌ Manchester City not found in Premier League teams")
            return results

        logger.info(f"🎯 Found Manchester City: {man_city_team['name']}")

        # Get all Manchester City players
        players = self.get_team_players(man_city_team['url'], man_city_team['name'], season)
        results['players_found'] = len(players)

        # Get detailed stats for each player
        stats_collected = 0
        for i, player in enumerate(players):
            logger.info(f"📊 Processing player {i+1}/{len(players)}: {player['name']}")

            player_stats = self.get_player_detailed_stats(player['url'], player['name'], season)
            if player_stats:
                # Ensure team name is set correctly
                player_stats['team_name'] = man_city_team['name']
                player_stats['competition'] = 'Premier League'
                player_stats['player_name'] = player['name']  # Ensure player name is set
                self.save_player_stats_to_db(player_stats)
                stats_collected += 1
            else:
                logger.warning(f"No stats collected for {player['name']}")

        results['stats_collected'] = stats_collected

        # Save summary
        summary_file = f"{self.data_dir}/manchester_city_{season}_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"✅ Manchester City scrape completed: {stats_collected} player stats collected")
        return results

    def export_to_csv(self):
        """Export all scraped data to CSV files."""
        logger.info("📄 Exporting data to CSV files")

        conn = sqlite3.connect(self.db_path)

        # Export teams
        teams_df = pd.read_sql_query("SELECT * FROM teams", conn)
        teams_file = f"{self.data_dir}/teams.csv"
        teams_df.to_csv(teams_file, index=False)
        logger.info(f"✅ Exported {len(teams_df)} teams to {teams_file}")

        # Export players
        players_df = pd.read_sql_query("SELECT * FROM players", conn)
        players_file = f"{self.data_dir}/players.csv"
        players_df.to_csv(players_file, index=False)
        logger.info(f"✅ Exported {len(players_df)} players to {players_file}")

        # Export player stats
        stats_df = pd.read_sql_query("SELECT * FROM player_stats", conn)
        stats_file = f"{self.data_dir}/player_stats.csv"
        stats_df.to_csv(stats_file, index=False)
        logger.info(f"✅ Exported {len(stats_df)} player stats to {stats_file}")

        conn.close()

        return {
            'teams_file': teams_file,
            'players_file': players_file,
            'stats_file': stats_file,
            'teams_count': len(teams_df),
            'players_count': len(players_df),
            'stats_count': len(stats_df)
        }

    def get_summary_report(self) -> Dict:
        """Generate a summary report of scraped data."""
        conn = sqlite3.connect(self.db_path)

        # Get counts
        teams_count = pd.read_sql_query("SELECT COUNT(*) as count FROM teams", conn).iloc[0]['count']
        players_count = pd.read_sql_query("SELECT COUNT(*) as count FROM players", conn).iloc[0]['count']
        stats_count = pd.read_sql_query("SELECT COUNT(*) as count FROM player_stats", conn).iloc[0]['count']

        # Get latest scrape time
        latest_scrape = pd.read_sql_query(
            "SELECT MAX(scraped_at) as latest FROM player_stats", conn
        ).iloc[0]['latest']

        # Get top scorers
        top_scorers = pd.read_sql_query(
            "SELECT player_name, team_name, goals FROM player_stats ORDER BY goals DESC LIMIT 10", conn
        ).to_dict('records')

        conn.close()

        return {
            'summary': {
                'teams_scraped': teams_count,
                'players_scraped': players_count,
                'stats_records': stats_count,
                'latest_scrape': latest_scrape
            },
            'top_scorers': top_scorers,
            'database_path': self.db_path,
            'data_directory': self.data_dir
        }

def main():
    """Main execution function with CLI interface."""
    import sys

    scraper = FBRefScraper()

    print("🚀 FBRef Data Scraper")
    print("=" * 50)

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'manchester-city':
            season = sys.argv[2] if len(sys.argv) > 2 else "2023-24"
            print(f"🏆 Scraping Manchester City data for {season} season...")
            results = scraper.scrape_manchester_city_complete(season)
            print("\n📊 Scraping Results:")
            print(f"   • Teams found: {results['teams_found']}")
            print(f"   • Players found: {results['players_found']}")
            print(f"   • Stats collected: {results['stats_collected']}")

        elif command == 'premier-league':
            season = sys.argv[2] if len(sys.argv) > 2 else "2023-24"
            print(f"⚽ Scraping Premier League teams for {season} season...")
            teams = scraper.get_premier_league_teams(season)
            print(f"✅ Found {len(teams)} Premier League teams")

        elif command == 'export':
            print("📄 Exporting data to CSV files...")
            export_results = scraper.export_to_csv()
            print("\n📁 Export Results:")
            print(f"   • Teams: {export_results['teams_count']} → {export_results['teams_file']}")
            print(f"   • Players: {export_results['players_count']} → {export_results['players_file']}")
            print(f"   • Stats: {export_results['stats_count']} → {export_results['stats_file']}")

        elif command == 'summary':
            print("📋 Generating summary report...")
            report = scraper.get_summary_report()
            print("\n📊 Database Summary:")
            print(f"   • Teams scraped: {report['summary']['teams_scraped']}")
            print(f"   • Players scraped: {report['summary']['players_scraped']}")
            print(f"   • Stats records: {report['summary']['stats_records']}")
            print(f"   • Latest scrape: {report['summary']['latest_scrape']}")
            print(f"   • Database: {report['database_path']}")

            if report['top_scorers']:
                print("\n🥅 Top Scorers:")
                for i, scorer in enumerate(report['top_scorers'][:5], 1):
                    print(f"   {i}. {scorer['player_name']} ({scorer['team_name']}) - {scorer['goals']} goals")

        else:
            print("❌ Unknown command")
            print_usage()

    else:
        print_usage()

def print_usage():
    """Print usage instructions."""
    print("\n📖 Usage:")
    print("  python fbref_scraper.py manchester-city [season]  # Scrape Manchester City data")
    print("  python fbref_scraper.py premier-league [season]   # Scrape Premier League teams")
    print("  python fbref_scraper.py export                    # Export data to CSV")
    print("  python fbref_scraper.py summary                   # Show summary report")
    print("\nExamples:")
    print("  python fbref_scraper.py manchester-city 2023-24")
    print("  python fbref_scraper.py premier-league 2022-23")
    print("  python fbref_scraper.py export")
    print("\n⚠️  Note: This scraper respects FBRef's servers with 2-5 second delays between requests")

if __name__ == "__main__":
    main()

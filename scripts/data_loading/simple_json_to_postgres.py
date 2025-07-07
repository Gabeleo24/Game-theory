#!/usr/bin/env python3
"""
Simple JSON to PostgreSQL Data Loader
Loads existing JSON data files into PostgreSQL database using psycopg2
"""

import json
import psycopg2
from pathlib import Path
import logging
from datetime import datetime
import sys
import os

class SimpleJSONLoader:
    def __init__(self, db_config=None):
        """Initialize the data loader."""
        self.db_config = db_config or {
            'host': 'localhost',
            'port': 5432,
            'database': 'soccer_intelligence',
            'user': 'soccerapp',
            'password': 'soccerpass123'
        }
        
        self.data_dir = Path('data')
        self.focused_dir = self.data_dir / 'focused'
        self.conn = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def connect_db(self):
        """Connect to PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            self.conn.autocommit = True
            
            # Test connection
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
            
            self.logger.info("✅ Successfully connected to PostgreSQL database")
            return True
            
        except Exception as e:
            self.logger.warning(f"❌ Database connection failed: {e}")
            self.logger.info("💡 To load data into PostgreSQL:")
            self.logger.info("   1. Start Docker: docker compose up postgres -d")
            self.logger.info("   2. Wait for database to be ready (30 seconds)")
            self.logger.info("   3. Run this script again")
            return False
    
    def analyze_data(self):
        """Analyze available JSON data."""
        self.logger.info("📊 Analyzing available JSON data...")
        
        analysis = {}
        
        # Check core teams file
        core_teams_file = self.focused_dir / 'core_champions_league_teams.json'
        if core_teams_file.exists():
            try:
                with open(core_teams_file, 'r') as f:
                    core_data = json.load(f)
                    analysis['core_teams'] = core_data.get('total_teams', 0)
                    analysis['core_teams_available'] = True
            except Exception as e:
                self.logger.error(f"Error reading core teams file: {e}")
                analysis['core_teams_available'] = False
        
        # Count team files
        team_files = list(self.focused_dir.glob('*teams*.json'))
        analysis['team_files'] = len(team_files)
        
        # Count match files
        match_files = list(self.focused_dir.glob('*matches*.json'))
        analysis['match_files'] = len(match_files)
        
        # Check team directories
        teams_dir = self.focused_dir / 'teams'
        if teams_dir.exists():
            team_dirs = [d for d in teams_dir.iterdir() if d.is_dir() and d.name.startswith('team_')]
            analysis['team_directories'] = len(team_dirs)
        else:
            analysis['team_directories'] = 0
        
        self.logger.info(f"📈 Data Analysis Results:")
        self.logger.info(f"   Core teams file: {'✅' if analysis.get('core_teams_available') else '❌'}")
        self.logger.info(f"   Core teams count: {analysis.get('core_teams', 0)}")
        self.logger.info(f"   Team files: {analysis['team_files']}")
        self.logger.info(f"   Match files: {analysis['match_files']}")
        self.logger.info(f"   Team directories: {analysis['team_directories']}")
        
        return analysis
    
    def load_core_teams(self):
        """Load core Champions League teams."""
        self.logger.info("🏆 Loading core Champions League teams...")
        
        core_teams_file = self.focused_dir / 'core_champions_league_teams.json'
        if not core_teams_file.exists():
            self.logger.warning("Core teams file not found")
            return 0
        
        try:
            with open(core_teams_file, 'r') as f:
                data = json.load(f)
            
            teams = data.get('teams', [])
            loaded_count = 0
            
            with self.conn.cursor() as cur:
                for team in teams:
                    try:
                        # Insert team with basic info
                        cur.execute("""
                            INSERT INTO teams (team_id, team_name, logo_url)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (team_id) DO UPDATE SET
                                team_name = EXCLUDED.team_name,
                                logo_url = EXCLUDED.logo_url
                        """, (team['id'], team['name'], team.get('logo')))
                        loaded_count += 1
                        
                    except Exception as e:
                        self.logger.error(f"Error inserting team {team.get('name', 'Unknown')}: {e}")
            
            self.logger.info(f"✅ Loaded {loaded_count} core teams")
            return loaded_count
            
        except Exception as e:
            self.logger.error(f"Error loading core teams: {e}")
            return 0
    
    def load_expanded_teams(self):
        """Load expanded team data with venue information."""
        self.logger.info("🏟️ Loading expanded team data...")
        
        expanded_files = list(self.focused_dir.glob('*teams*expanded*.json'))
        if not expanded_files:
            self.logger.warning("No expanded team files found")
            return 0
        
        loaded_count = 0
        
        for file_path in expanded_files:
            try:
                with open(file_path, 'r') as f:
                    teams_data = json.load(f)
                
                if not isinstance(teams_data, list):
                    continue
                
                with self.conn.cursor() as cur:
                    for item in teams_data:
                        if not isinstance(item, dict) or 'team' not in item:
                            continue
                        
                        team = item['team']
                        venue = item.get('venue', {})
                        
                        try:
                            # Update team with expanded info
                            cur.execute("""
                                INSERT INTO teams (
                                    team_id, team_name, team_code, country, founded,
                                    venue_name, venue_capacity, logo_url
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (team_id) DO UPDATE SET
                                    team_name = EXCLUDED.team_name,
                                    team_code = EXCLUDED.team_code,
                                    country = EXCLUDED.country,
                                    founded = EXCLUDED.founded,
                                    venue_name = EXCLUDED.venue_name,
                                    venue_capacity = EXCLUDED.venue_capacity,
                                    logo_url = EXCLUDED.logo_url
                            """, (
                                team['id'], team['name'], team.get('code'),
                                team.get('country'), team.get('founded'),
                                venue.get('name'), venue.get('capacity'),
                                team.get('logo')
                            ))
                            loaded_count += 1
                            
                        except Exception as e:
                            self.logger.error(f"Error updating team {team.get('name', 'Unknown')}: {e}")
                
                self.logger.info(f"Processed {file_path.name}")
                
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
        
        self.logger.info(f"✅ Updated {loaded_count} teams with expanded data")
        return loaded_count
    
    def load_sample_matches(self, limit=1000):
        """Load a sample of match data."""
        self.logger.info(f"⚽ Loading sample match data (limit: {limit})...")
        
        match_files = list(self.focused_dir.glob('*matches*.json'))
        if not match_files:
            self.logger.warning("No match files found")
            return 0
        
        loaded_count = 0
        
        for file_path in match_files[:3]:  # Process first 3 files
            if loaded_count >= limit:
                break
                
            try:
                with open(file_path, 'r') as f:
                    matches_data = json.load(f)
                
                if not isinstance(matches_data, list):
                    continue
                
                with self.conn.cursor() as cur:
                    for match in matches_data:
                        if loaded_count >= limit:
                            break
                            
                        if not isinstance(match, dict):
                            continue
                        
                        fixture = match.get('fixture', {})
                        teams = match.get('teams', {})
                        goals = match.get('goals', {})
                        league = match.get('league', {})
                        
                        try:
                            # Insert match
                            cur.execute("""
                                INSERT INTO matches (
                                    match_id, competition_id, season_year, match_date,
                                    home_team_id, away_team_id, home_goals, away_goals,
                                    match_status, venue_name
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (match_id) DO NOTHING
                            """, (
                                fixture.get('id'),
                                league.get('id'),
                                league.get('season'),
                                fixture.get('date'),
                                teams.get('home', {}).get('id'),
                                teams.get('away', {}).get('id'),
                                goals.get('home'),
                                goals.get('away'),
                                fixture.get('status', {}).get('long'),
                                fixture.get('venue', {}).get('name')
                            ))
                            loaded_count += 1
                            
                        except Exception as e:
                            self.logger.error(f"Error inserting match {fixture.get('id', 'Unknown')}: {e}")
                
                self.logger.info(f"Processed {file_path.name}")
                
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
        
        self.logger.info(f"✅ Loaded {loaded_count} matches")
        return loaded_count
    
    def check_database_status(self):
        """Check current database status."""
        self.logger.info("🔍 Checking database status...")
        
        try:
            with self.conn.cursor() as cur:
                # Check table counts
                tables = ['teams', 'matches', 'players', 'player_statistics']
                status = {}
                
                for table in tables:
                    try:
                        cur.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cur.fetchone()[0]
                        status[table] = count
                    except Exception as e:
                        status[table] = f"Error: {e}"
                
                self.logger.info("📊 Current database status:")
                for table, count in status.items():
                    self.logger.info(f"   {table}: {count}")
                
                return status
                
        except Exception as e:
            self.logger.error(f"Error checking database status: {e}")
            return {}
    
    def run_basic_load(self):
        """Run basic data loading process."""
        self.logger.info("🚀 Starting basic JSON to PostgreSQL data loading...")
        
        # Analyze data
        analysis = self.analyze_data()
        
        # Connect to database
        if not self.connect_db():
            return False
        
        try:
            # Check initial status
            initial_status = self.check_database_status()
            
            # Load data
            teams_core = self.load_core_teams()
            teams_expanded = self.load_expanded_teams()
            matches = self.load_sample_matches(limit=1000)
            
            # Check final status
            final_status = self.check_database_status()
            
            self.logger.info("✅ Basic data loading completed!")
            self.logger.info("📈 Summary:")
            self.logger.info(f"   Core teams loaded: {teams_core}")
            self.logger.info(f"   Teams updated: {teams_expanded}")
            self.logger.info(f"   Sample matches loaded: {matches}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error during data loading: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
        
        finally:
            if self.conn:
                self.conn.close()

def main():
    """Main function to run the data loader."""
    print("🚀 Starting Simple JSON to PostgreSQL data loading...")
    print("📊 This will load a sample of your JSON data into the database")
    print()
    
    loader = SimpleJSONLoader()
    
    success = loader.run_basic_load()
    
    if success:
        print("\n✅ Data loading completed successfully!")
        print("🔍 You can now access your data via:")
        print("   - psql -h localhost -p 5432 -U soccerapp -d soccer_intelligence")
        print("   - Python scripts with psycopg2")
        print("   - Analysis tools")
    else:
        print("\n❌ Data loading failed. Check the logs for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

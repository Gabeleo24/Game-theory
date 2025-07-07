#!/usr/bin/env python3
"""
JSON to PostgreSQL Data Loader
Loads existing JSON data files into PostgreSQL database for analysis
"""

import json
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from pathlib import Path
import logging
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class JSONToPostgresLoader:
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
        self.engine = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def connect_db(self):
        """Connect to PostgreSQL database."""
        try:
            connection_string = f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
            self.engine = create_engine(connection_string)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            
            self.logger.info("Successfully connected to PostgreSQL database")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            return False
    
    def load_teams_data(self):
        """Load teams data from JSON files."""
        self.logger.info("Loading teams data...")
        
        teams_data = []
        team_files = list(self.focused_dir.glob('*teams*.json'))
        
        for file_path in team_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    for team in data:
                        if isinstance(team, dict) and 'team' in team:
                            team_info = team['team']
                            teams_data.append({
                                'team_id': team_info.get('id'),
                                'team_name': team_info.get('name'),
                                'team_code': team_info.get('code'),
                                'country': team_info.get('country'),
                                'founded': team_info.get('founded'),
                                'venue_name': team_info.get('venue', {}).get('name') if team_info.get('venue') else None,
                                'venue_capacity': team_info.get('venue', {}).get('capacity') if team_info.get('venue') else None,
                                'logo_url': team_info.get('logo')
                            })
                
                self.logger.info(f"Processed {file_path.name}")
                
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
        
        # Remove duplicates based on team_id
        unique_teams = {}
        for team in teams_data:
            if team['team_id'] and team['team_id'] not in unique_teams:
                unique_teams[team['team_id']] = team
        
        teams_df = pd.DataFrame(list(unique_teams.values()))
        
        if not teams_df.empty:
            # Insert into database
            teams_df.to_sql('teams', self.engine, if_exists='append', index=False, method='multi')
            self.logger.info(f"Loaded {len(teams_df)} teams into database")
        
        return len(teams_df)
    
    def load_matches_data(self):
        """Load matches data from JSON files."""
        self.logger.info("Loading matches data...")
        
        matches_data = []
        match_files = list(self.focused_dir.glob('*matches*.json'))
        
        for file_path in match_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    for match in data:
                        if isinstance(match, dict):
                            fixture = match.get('fixture', {})
                            teams = match.get('teams', {})
                            goals = match.get('goals', {})
                            score = match.get('score', {})
                            
                            matches_data.append({
                                'match_id': fixture.get('id'),
                                'competition_id': match.get('league', {}).get('id'),
                                'season_year': match.get('league', {}).get('season'),
                                'match_date': fixture.get('date'),
                                'round': match.get('league', {}).get('round'),
                                'home_team_id': teams.get('home', {}).get('id'),
                                'away_team_id': teams.get('away', {}).get('id'),
                                'home_goals': goals.get('home'),
                                'away_goals': goals.get('away'),
                                'home_goals_halftime': score.get('halftime', {}).get('home'),
                                'away_goals_halftime': score.get('halftime', {}).get('away'),
                                'match_status': fixture.get('status', {}).get('long'),
                                'venue_name': fixture.get('venue', {}).get('name'),
                                'venue_city': fixture.get('venue', {}).get('city'),
                                'referee': fixture.get('referee')
                            })
                
                self.logger.info(f"Processed {file_path.name}")
                
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
        
        # Remove duplicates based on match_id
        unique_matches = {}
        for match in matches_data:
            if match['match_id'] and match['match_id'] not in unique_matches:
                unique_matches[match['match_id']] = match
        
        matches_df = pd.DataFrame(list(unique_matches.values()))
        
        if not matches_df.empty:
            # Convert date strings to datetime
            matches_df['match_date'] = pd.to_datetime(matches_df['match_date'], errors='coerce')
            
            # Insert into database
            matches_df.to_sql('matches', self.engine, if_exists='append', index=False, method='multi')
            self.logger.info(f"Loaded {len(matches_df)} matches into database")
        
        return len(matches_df)
    
    def load_player_statistics(self):
        """Load player statistics from team-specific directories."""
        self.logger.info("Loading player statistics...")
        
        player_stats_data = []
        players_data = []
        
        # Check for player statistics in team directories
        teams_dir = self.focused_dir / 'teams'
        if teams_dir.exists():
            for team_dir in teams_dir.iterdir():
                if team_dir.is_dir():
                    team_id = team_dir.name.replace('team_', '')
                    
                    # Look for season directories
                    for season_dir in team_dir.iterdir():
                        if season_dir.is_dir() and season_dir.name.isdigit():
                            season_year = int(season_dir.name)
                            
                            # Look for player statistics files
                            for stats_file in season_dir.glob('*player*statistics*.json'):
                                try:
                                    with open(stats_file, 'r') as f:
                                        data = json.load(f)
                                    
                                    if isinstance(data, list):
                                        for player_data in data:
                                            if isinstance(player_data, dict):
                                                player = player_data.get('player', {})
                                                statistics = player_data.get('statistics', [])
                                                
                                                # Add player info
                                                players_data.append({
                                                    'player_id': player.get('id'),
                                                    'player_name': player.get('name'),
                                                    'first_name': player.get('firstname'),
                                                    'last_name': player.get('lastname'),
                                                    'age': player.get('age'),
                                                    'birth_date': player.get('birth', {}).get('date'),
                                                    'birth_place': player.get('birth', {}).get('place'),
                                                    'birth_country': player.get('birth', {}).get('country'),
                                                    'nationality': player.get('nationality'),
                                                    'height': player.get('height'),
                                                    'weight': player.get('weight'),
                                                    'photo_url': player.get('photo')
                                                })
                                                
                                                # Add statistics
                                                for stat in statistics:
                                                    if isinstance(stat, dict):
                                                        games = stat.get('games', {})
                                                        goals = stat.get('goals', {})
                                                        passes = stat.get('passes', {})
                                                        tackles = stat.get('tackles', {})
                                                        fouls = stat.get('fouls', {})
                                                        cards = stat.get('cards', {})
                                                        
                                                        player_stats_data.append({
                                                            'player_id': player.get('id'),
                                                            'team_id': int(team_id),
                                                            'season_year': season_year,
                                                            'position': games.get('position'),
                                                            'minutes_played': games.get('minutes'),
                                                            'goals': goals.get('total', 0),
                                                            'assists': goals.get('assists', 0),
                                                            'shots_total': stat.get('shots', {}).get('total', 0),
                                                            'shots_on_target': stat.get('shots', {}).get('on', 0),
                                                            'passes_total': passes.get('total', 0),
                                                            'passes_completed': passes.get('accuracy', 0),
                                                            'tackles_total': tackles.get('total', 0),
                                                            'tackles_won': tackles.get('blocks', 0),
                                                            'interceptions': tackles.get('interceptions', 0),
                                                            'fouls_drawn': fouls.get('drawn', 0),
                                                            'fouls_committed': fouls.get('committed', 0),
                                                            'yellow_cards': cards.get('yellow', 0),
                                                            'red_cards': cards.get('red', 0),
                                                            'rating': games.get('rating')
                                                        })
                                    
                                    self.logger.info(f"Processed {stats_file}")
                                    
                                except Exception as e:
                                    self.logger.error(f"Error processing {stats_file}: {e}")
        
        # Load players data
        if players_data:
            unique_players = {}
            for player in players_data:
                if player['player_id'] and player['player_id'] not in unique_players:
                    unique_players[player['player_id']] = player
            
            players_df = pd.DataFrame(list(unique_players.values()))
            players_df['birth_date'] = pd.to_datetime(players_df['birth_date'], errors='coerce')
            
            players_df.to_sql('players', self.engine, if_exists='append', index=False, method='multi')
            self.logger.info(f"Loaded {len(players_df)} players into database")
        
        # Load player statistics
        if player_stats_data:
            stats_df = pd.DataFrame(player_stats_data)
            stats_df = stats_df.dropna(subset=['player_id', 'team_id'])
            
            stats_df.to_sql('player_statistics', self.engine, if_exists='append', index=False, method='multi')
            self.logger.info(f"Loaded {len(stats_df)} player statistics records into database")
        
        return len(players_data), len(player_stats_data)
    
    def test_database_connection(self):
        """Test if we can connect to the database without Docker."""
        try:
            # Try to connect directly
            connection_string = f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
            engine = create_engine(connection_string)

            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                self.logger.info("✅ Database connection successful!")
                return engine

        except Exception as e:
            self.logger.warning(f"❌ Database connection failed: {e}")
            self.logger.info("💡 To load data into PostgreSQL:")
            self.logger.info("   1. Start Docker: docker compose up postgres -d")
            self.logger.info("   2. Wait for database to be ready (30 seconds)")
            self.logger.info("   3. Run this script again")
            return None

    def analyze_json_data_structure(self):
        """Analyze the JSON data structure to understand what we have."""
        self.logger.info("📊 Analyzing available JSON data...")

        analysis = {
            'team_files': 0,
            'match_files': 0,
            'team_directories': 0,
            'player_files': 0,
            'estimated_teams': 0,
            'estimated_matches': 0
        }

        # Count team files
        team_files = list(self.focused_dir.glob('*teams*.json'))
        analysis['team_files'] = len(team_files)

        # Count match files
        match_files = list(self.focused_dir.glob('*matches*.json'))
        analysis['match_files'] = len(match_files)

        # Count team directories
        teams_dir = self.focused_dir / 'teams'
        if teams_dir.exists():
            team_dirs = [d for d in teams_dir.iterdir() if d.is_dir() and d.name.startswith('team_')]
            analysis['team_directories'] = len(team_dirs)

        # Check core teams file
        core_teams_file = self.focused_dir / 'core_champions_league_teams.json'
        if core_teams_file.exists():
            try:
                with open(core_teams_file, 'r') as f:
                    core_data = json.load(f)
                    analysis['estimated_teams'] = core_data.get('total_teams', 0)
            except:
                pass

        # Estimate matches from a sample file
        if match_files:
            try:
                with open(match_files[0], 'r') as f:
                    sample_matches = json.load(f)
                    if isinstance(sample_matches, list):
                        analysis['estimated_matches'] = len(sample_matches) * len(match_files)
            except:
                pass

        self.logger.info(f"📈 Data Analysis Results:")
        self.logger.info(f"   Team files: {analysis['team_files']}")
        self.logger.info(f"   Match files: {analysis['match_files']}")
        self.logger.info(f"   Team directories: {analysis['team_directories']}")
        self.logger.info(f"   Estimated teams: {analysis['estimated_teams']}")
        self.logger.info(f"   Estimated matches: {analysis['estimated_matches']}")

        return analysis

    def run_full_load(self):
        """Run complete data loading process."""
        self.logger.info("🚀 Starting JSON to PostgreSQL data loading process...")

        # First analyze what data we have
        analysis = self.analyze_json_data_structure()

        # Test database connection
        engine = self.test_database_connection()
        if not engine:
            return False

        self.engine = engine

        try:
            self.logger.info("📊 Loading data in order (respecting foreign key constraints)...")

            # Load data in order (respecting foreign key constraints)
            teams_count = self.load_teams_data()
            matches_count = self.load_matches_data()
            players_count, stats_count = self.load_player_statistics()

            self.logger.info("✅ Data loading completed successfully!")
            self.logger.info(f"📈 Final Summary:")
            self.logger.info(f"   Teams loaded: {teams_count}")
            self.logger.info(f"   Matches loaded: {matches_count}")
            self.logger.info(f"   Players loaded: {players_count}")
            self.logger.info(f"   Player statistics loaded: {stats_count}")

            return True

        except Exception as e:
            self.logger.error(f"❌ Error during data loading: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

def main():
    """Main function to run the data loader."""
    loader = JSONToPostgresLoader()
    
    print("🚀 Starting JSON to PostgreSQL data loading...")
    print("📊 This will load your existing JSON data into the database for analysis")
    print()
    
    success = loader.run_full_load()
    
    if success:
        print("✅ Data loading completed successfully!")
        print("🔍 You can now access your data via:")
        print("   - Direct SQL queries")
        print("   - Python pandas DataFrames")
        print("   - Jupyter notebooks")
        print("   - Analysis scripts")
    else:
        print("❌ Data loading failed. Check the logs for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

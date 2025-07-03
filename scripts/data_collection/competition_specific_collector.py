#!/usr/bin/env python3
"""
Competition-Specific Player Statistics Collector
Specialized collection for Champions League, domestic leagues, Europa League, and domestic cups.
"""

import json
import requests
import time
import yaml
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import sys

# Add src to path for imports
sys.path.append('src')

class CompetitionSpecificCollector:
    """Collect player statistics organized by competition type."""
    
    def __init__(self):
        """Initialize the competition-specific collector."""
        self.setup_configuration()
        self.setup_directories()
        self.load_core_data()
        
        # Competition configurations
        self.competition_configs = {
            'champions_league': {'id': 2, 'name': 'UEFA Champions League', 'type': 'european'},
            'europa_league': {'id': 3, 'name': 'UEFA Europa League', 'type': 'european'},
            'premier_league': {'id': 39, 'name': 'Premier League', 'type': 'domestic_league'},
            'la_liga': {'id': 140, 'name': 'La Liga', 'type': 'domestic_league'},
            'serie_a': {'id': 135, 'name': 'Serie A', 'type': 'domestic_league'},
            'bundesliga': {'id': 78, 'name': 'Bundesliga', 'type': 'domestic_league'},
            'ligue_1': {'id': 61, 'name': 'Ligue 1', 'type': 'domestic_league'},
            'fa_cup': {'id': 45, 'name': 'FA Cup', 'type': 'domestic_cup'},
            'copa_del_rey': {'id': 143, 'name': 'Copa del Rey', 'type': 'domestic_cup'},
            'coppa_italia': {'id': 137, 'name': 'Coppa Italia', 'type': 'domestic_cup'},
            'dfb_pokal': {'id': 81, 'name': 'DFB Pokal', 'type': 'domestic_cup'}
        }
        
        # API tracking
        self.request_count = 0
        self.daily_limit = 75000
        
        # Data storage
        self.competition_player_stats = defaultdict(lambda: defaultdict(list))
        
    def setup_configuration(self):
        """Setup API configuration."""
        try:
            with open('config/api_keys.yaml', 'r') as f:
                config = yaml.safe_load(f)
                self.api_key = config['api_football']['key']
        except:
            self.api_key = "5ced20dec7f4b2226c8944c88c6d86aa"
        
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'v3.football.api-sports.io'
        }
    
    def setup_directories(self):
        """Setup output directories."""
        self.output_dir = Path('data/focused/players/competition_stats')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for each competition type
        for comp_type in ['european', 'domestic_league', 'domestic_cup']:
            (self.output_dir / comp_type).mkdir(exist_ok=True)
    
    def load_core_data(self):
        """Load core teams and existing player data."""
        # Load core teams
        with open('data/focused/core_champions_league_teams.json', 'r') as f:
            core_teams_data = json.load(f)
            self.core_teams = {team['id']: team for team in core_teams_data['teams']}
        
        # Load team-league mapping
        with open('data/focused/team_league_mapping.json', 'r') as f:
            self.team_league_mapping = json.load(f)
        
        print(f"Loaded {len(self.core_teams)} core teams for competition-specific collection")
    
    def make_api_request(self, endpoint, params=None, description="API call"):
        """Make rate-limited API request."""
        if self.request_count >= self.daily_limit:
            raise Exception(f"Daily API limit reached")
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            self.request_count += 1
            
            print(f"Request {self.request_count}: {description}")
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', data)
            elif response.status_code == 429:
                print("Rate limit hit. Waiting...")
                time.sleep(60)
                return self.make_api_request(endpoint, params, description)
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def collect_competition_players(self, competition_key, season):
        """Collect player statistics for a specific competition and season."""
        competition = self.competition_configs[competition_key]
        league_id = competition['id']
        
        print(f"\nCollecting {competition['name']} players for season {season}")
        
        # Get teams that participated in this competition
        participating_teams = self.get_participating_teams(league_id, season)
        
        competition_players = []
        
        for team_id in participating_teams:
            if team_id not in self.core_teams:
                continue  # Only collect for core teams
            
            team_name = self.core_teams[team_id]['name']
            print(f"   Collecting {team_name} players...")
            
            # Get players for this team in this competition
            players_data = self.make_api_request(
                'players',
                {'team': team_id, 'season': season, 'league': league_id},
                f"{team_name} {competition['name']} {season}"
            )
            
            if players_data:
                for player_data in players_data:
                    processed_player = self.process_competition_player_data(
                        player_data, team_id, competition_key, season
                    )
                    if processed_player:
                        competition_players.append(processed_player)
            
            time.sleep(0.5)  # Rate limiting
        
        # Save competition-specific data
        self.save_competition_data(competition_key, season, competition_players)
        
        return competition_players
    
    def get_participating_teams(self, league_id, season):
        """Get teams that participated in a specific competition."""
        # For now, return all core teams - in a full implementation,
        # this would query the API for actual participants
        return list(self.core_teams.keys())
    
    def process_competition_player_data(self, player_data, team_id, competition_key, season):
        """Process player data for specific competition context."""
        player = player_data.get('player', {})
        statistics = player_data.get('statistics', [])
        
        if not player or not statistics:
            return None
        
        # Find statistics for the specific competition
        competition_stats = None
        competition_id = self.competition_configs[competition_key]['id']
        
        for stat in statistics:
            league = stat.get('league', {})
            if league.get('id') == competition_id:
                competition_stats = stat
                break
        
        if not competition_stats:
            return None
        
        return {
            'player_info': {
                'id': player.get('id'),
                'name': player.get('name'),
                'age': player.get('age'),
                'nationality': player.get('nationality'),
                'position': competition_stats.get('games', {}).get('position'),
                'photo': player.get('photo')
            },
            'team_info': {
                'team_id': team_id,
                'team_name': self.core_teams[team_id]['name']
            },
            'competition_info': {
                'competition_key': competition_key,
                'competition_name': self.competition_configs[competition_key]['name'],
                'competition_type': self.competition_configs[competition_key]['type'],
                'season': season
            },
            'performance_metrics': self.extract_performance_metrics(competition_stats),
            'advanced_metrics': self.calculate_advanced_metrics(competition_stats)
        }
    
    def extract_performance_metrics(self, stats):
        """Extract key performance metrics from statistics."""
        games = stats.get('games', {})
        goals = stats.get('goals', {})
        passes = stats.get('passes', {})
        tackles = stats.get('tackles', {})
        
        return {
            'appearances': games.get('appearences', 0),
            'minutes_played': games.get('minutes', 0),
            'goals': goals.get('total', 0),
            'assists': goals.get('assists', 0),
            'pass_accuracy': passes.get('accuracy', 0),
            'key_passes': passes.get('key', 0),
            'tackles': tackles.get('total', 0),
            'interceptions': tackles.get('interceptions', 0),
            'rating': games.get('rating')
        }
    
    def calculate_advanced_metrics(self, stats):
        """Calculate advanced performance metrics."""
        games = stats.get('games', {})
        goals = stats.get('goals', {})
        passes = stats.get('passes', {})
        
        appearances = games.get('appearences', 0)
        minutes = games.get('minutes', 0)
        
        if appearances == 0 or minutes == 0:
            return {}
        
        return {
            'goals_per_game': goals.get('total', 0) / appearances,
            'assists_per_game': goals.get('assists', 0) / appearances,
            'minutes_per_appearance': minutes / appearances,
            'goal_contributions_per_90': ((goals.get('total', 0) + goals.get('assists', 0)) * 90) / minutes if minutes > 0 else 0,
            'passes_per_90': (passes.get('total', 0) * 90) / minutes if minutes > 0 else 0
        }
    
    def save_competition_data(self, competition_key, season, players_data):
        """Save competition-specific player data."""
        competition = self.competition_configs[competition_key]
        comp_type = competition['type']
        
        output_file = self.output_dir / comp_type / f'{competition_key}_players_{season}.json'
        
        data_to_save = {
            'competition_info': {
                'key': competition_key,
                'name': competition['name'],
                'type': comp_type,
                'season': season
            },
            'collection_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_players': len(players_data),
                'core_teams_represented': len(set(p['team_info']['team_id'] for p in players_data))
            },
            'players': players_data
        }
        
        with open(output_file, 'w') as f:
            json.dump(data_to_save, f, indent=2, default=str)
        
        print(f"Saved {len(players_data)} players to {output_file}")
    
    def collect_all_competitions(self, seasons=[2022, 2023]):
        """Collect player statistics for all competitions."""
        print(f"Starting competition-specific collection for seasons: {seasons}")
        
        total_collected = 0
        
        for season in seasons:
            print(f"\n{'='*60}")
            print(f"SEASON {season}")
            print(f"{'='*60}")
            
            for comp_key in self.competition_configs.keys():
                try:
                    players = self.collect_competition_players(comp_key, season)
                    total_collected += len(players)
                    print(f"Collected {len(players)} players for {comp_key} {season}")
                    
                except Exception as e:
                    print(f"Error collecting {comp_key} {season}: {e}")
                    continue
        
        print(f"\nTotal players collected across all competitions: {total_collected}")
        return total_collected

def main():
    """Main execution function."""
    print("COMPETITION-SPECIFIC PLAYER STATISTICS COLLECTION")
    print("=" * 60)
    
    collector = CompetitionSpecificCollector()
    
    try:
        total_players = collector.collect_all_competitions()
        print(f"\nCollection completed! Total players: {total_players}")
        
    except Exception as e:
        print(f"Error during collection: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

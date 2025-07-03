#!/usr/bin/env python3
"""
Comprehensive Player Statistics Collection System
Collects detailed player statistics for all players from the 67 core Champions League teams
across all competitions (Champions League, domestic leagues, Europa League, domestic cups).
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

class PlayerStatisticsCollector:
    """Comprehensive player statistics collection for Champions League teams."""
    
    def __init__(self):
        """Initialize the player statistics collector."""
        self.setup_configuration()
        self.setup_directories()
        self.load_core_teams_data()
        
        # API tracking
        self.request_count = 0
        self.daily_limit = 75000
        self.requests_made = []
        
        # Data storage
        self.player_data = {}
        self.player_team_mapping = defaultdict(list)
        self.competition_stats = defaultdict(dict)
        
    def setup_configuration(self):
        """Setup API configuration and headers."""
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
        
        print(f"Player Statistics Collector initialized")
        print(f"API Key configured: {self.api_key[:10]}...")
    
    def setup_directories(self):
        """Setup output directories for player statistics."""
        self.output_dir = Path('data/focused/players')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different data types
        (self.output_dir / 'team_rosters').mkdir(exist_ok=True)
        (self.output_dir / 'individual_stats').mkdir(exist_ok=True)
        (self.output_dir / 'competition_stats').mkdir(exist_ok=True)
        (self.output_dir / 'season_stats').mkdir(exist_ok=True)
        (self.output_dir / 'mappings').mkdir(exist_ok=True)
        
        print(f"Output directories created in: {self.output_dir}")
    
    def load_core_teams_data(self):
        """Load the 67 core Champions League teams data."""
        core_teams_file = Path('data/focused/core_champions_league_teams.json')
        team_mapping_file = Path('data/focused/team_league_mapping.json')
        
        with open(core_teams_file, 'r') as f:
            core_teams_data = json.load(f)
            self.core_teams = {team['id']: team for team in core_teams_data['teams']}
        
        with open(team_mapping_file, 'r') as f:
            self.team_league_mapping = json.load(f)
        
        print(f"Loaded {len(self.core_teams)} core Champions League teams")
        print(f"Loaded {len(self.team_league_mapping)} team-league mappings")
    
    def make_api_request(self, endpoint, params=None, description="API call"):
        """Make rate-limited API request with error handling."""
        if self.request_count >= self.daily_limit:
            raise Exception(f"Daily API limit of {self.daily_limit} reached")
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            self.request_count += 1
            
            # Track request
            self.requests_made.append({
                'timestamp': datetime.now().isoformat(),
                'endpoint': endpoint,
                'params': params,
                'description': description,
                'status_code': response.status_code
            })
            
            print(f"Request {self.request_count}: {description} - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'response' in data:
                    return data['response']
                return data
            
            elif response.status_code == 429:
                print(f"Rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
                return self.make_api_request(endpoint, params, description)
            
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Request failed for {description}: {e}")
            return None
    
    def collect_team_players(self, team_id, season):
        """Collect all players for a specific team and season."""
        print(f"\nCollecting players for team {team_id} ({self.core_teams.get(team_id, {}).get('name', 'Unknown')}) - Season {season}")
        
        # Get team players
        players_data = self.make_api_request(
            'players',
            {'team': team_id, 'season': season},
            f"Team {team_id} players {season}"
        )
        
        if not players_data:
            return []
        
        team_players = []
        
        for player_data in players_data:
            player = player_data.get('player', {})
            statistics = player_data.get('statistics', [])
            
            if not player or not statistics:
                continue
            
            player_id = player.get('id')
            player_name = player.get('name', 'Unknown')
            
            # Process player statistics
            processed_stats = self.process_player_statistics(player, statistics, team_id, season)
            
            if processed_stats:
                team_players.append(processed_stats)
                
                # Update player-team mapping
                self.player_team_mapping[player_id].append({
                    'team_id': team_id,
                    'team_name': self.core_teams.get(team_id, {}).get('name', 'Unknown'),
                    'season': season,
                    'league_id': self.team_league_mapping.get(str(team_id), {}).get('league_id'),
                    'league_name': self.team_league_mapping.get(str(team_id), {}).get('league_name')
                })
                
                print(f"   Processed: {player_name} (ID: {player_id})")
        
        # Save team roster
        roster_file = self.output_dir / 'team_rosters' / f'team_{team_id}_players_{season}.json'
        with open(roster_file, 'w') as f:
            json.dump({
                'team_id': team_id,
                'team_name': self.core_teams.get(team_id, {}).get('name'),
                'season': season,
                'total_players': len(team_players),
                'collection_timestamp': datetime.now().isoformat(),
                'players': team_players
            }, f, indent=2, default=str)
        
        print(f"Saved {len(team_players)} players to {roster_file}")
        return team_players
    
    def process_player_statistics(self, player, statistics, team_id, season):
        """Process and structure player statistics data."""
        player_id = player.get('id')
        
        processed_data = {
            'player_info': {
                'id': player_id,
                'name': player.get('name'),
                'firstname': player.get('firstname'),
                'lastname': player.get('lastname'),
                'age': player.get('age'),
                'birth': player.get('birth', {}),
                'nationality': player.get('nationality'),
                'height': player.get('height'),
                'weight': player.get('weight'),
                'injured': player.get('injured'),
                'photo': player.get('photo')
            },
            'team_info': {
                'team_id': team_id,
                'team_name': self.core_teams.get(team_id, {}).get('name'),
                'season': season
            },
            'statistics': []
        }
        
        # Process each competition's statistics
        for stat in statistics:
            league = stat.get('league', {})
            team = stat.get('team', {})
            games = stat.get('games', {})
            goals = stat.get('goals', {})
            passes = stat.get('passes', {})
            tackles = stat.get('tackles', {})
            duels = stat.get('duels', {})
            dribbles = stat.get('dribbles', {})
            fouls = stat.get('fouls', {})
            cards = stat.get('cards', {})
            penalty = stat.get('penalty', {})
            shots = stat.get('shots', {})
            
            competition_stats = {
                'league_info': {
                    'id': league.get('id'),
                    'name': league.get('name'),
                    'country': league.get('country'),
                    'logo': league.get('logo'),
                    'flag': league.get('flag'),
                    'season': league.get('season')
                },
                'team_info': {
                    'id': team.get('id'),
                    'name': team.get('name'),
                    'logo': team.get('logo')
                },
                'performance_stats': {
                    'appearances': games.get('appearences', 0),
                    'lineups': games.get('lineups', 0),
                    'minutes': games.get('minutes', 0),
                    'number': games.get('number'),
                    'position': games.get('position'),
                    'rating': games.get('rating'),
                    'captain': games.get('captain', False)
                },
                'scoring_stats': {
                    'goals_total': goals.get('total', 0),
                    'goals_conceded': goals.get('conceded', 0),
                    'assists': goals.get('assists', 0),
                    'saves': goals.get('saves', 0)
                },
                'passing_stats': {
                    'passes_total': passes.get('total', 0),
                    'passes_key': passes.get('key', 0),
                    'passes_accuracy': passes.get('accuracy', 0)
                },
                'defensive_stats': {
                    'tackles_total': tackles.get('total', 0),
                    'tackles_blocks': tackles.get('blocks', 0),
                    'tackles_interceptions': tackles.get('interceptions', 0)
                },
                'duel_stats': {
                    'duels_total': duels.get('total', 0),
                    'duels_won': duels.get('won', 0)
                },
                'dribbling_stats': {
                    'dribbles_attempts': dribbles.get('attempts', 0),
                    'dribbles_success': dribbles.get('success', 0),
                    'dribbles_past': dribbles.get('past', 0)
                },
                'discipline_stats': {
                    'fouls_drawn': fouls.get('drawn', 0),
                    'fouls_committed': fouls.get('committed', 0),
                    'cards_yellow': cards.get('yellow', 0),
                    'cards_yellowred': cards.get('yellowred', 0),
                    'cards_red': cards.get('red', 0)
                },
                'penalty_stats': {
                    'penalty_won': penalty.get('won', 0),
                    'penalty_committed': penalty.get('commited', 0),
                    'penalty_scored': penalty.get('scored', 0),
                    'penalty_missed': penalty.get('missed', 0),
                    'penalty_saved': penalty.get('saved', 0)
                },
                'shooting_stats': {
                    'shots_total': shots.get('total', 0),
                    'shots_on': shots.get('on', 0)
                }
            }
            
            processed_data['statistics'].append(competition_stats)
        
        return processed_data
    
    def collect_all_team_players(self, seasons=[2019, 2020, 2021, 2022, 2023]):
        """Collect players for all core teams across specified seasons."""
        print(f"\nStarting comprehensive player collection for {len(self.core_teams)} teams")
        print(f"Seasons: {seasons}")
        print(f"Estimated API requests: {len(self.core_teams) * len(seasons)}")
        
        total_players_collected = 0
        
        for team_id in self.core_teams.keys():
            team_name = self.core_teams[team_id]['name']
            print(f"\n{'='*60}")
            print(f"Processing Team: {team_name} (ID: {team_id})")
            print(f"{'='*60}")
            
            for season in seasons:
                try:
                    players = self.collect_team_players(team_id, season)
                    total_players_collected += len(players)
                    
                    # Rate limiting - wait between requests
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error collecting players for {team_name} {season}: {e}")
                    continue
        
        print(f"\n{'='*60}")
        print(f"COLLECTION COMPLETE")
        print(f"{'='*60}")
        print(f"Total players collected: {total_players_collected}")
        print(f"API requests made: {self.request_count}")
        print(f"Remaining requests: {self.daily_limit - self.request_count}")
        
        return total_players_collected

    def save_player_team_mappings(self):
        """Save comprehensive player-team mapping data."""
        print("\nSaving player-team mappings...")

        # Convert defaultdict to regular dict for JSON serialization
        mapping_data = {
            'total_players': len(self.player_team_mapping),
            'collection_timestamp': datetime.now().isoformat(),
            'mappings': dict(self.player_team_mapping)
        }

        mapping_file = self.output_dir / 'mappings' / 'player_team_mappings.json'
        with open(mapping_file, 'w') as f:
            json.dump(mapping_data, f, indent=2, default=str)

        print(f"Saved mappings for {len(self.player_team_mapping)} players to {mapping_file}")

        # Create transfer analysis
        transfers = self.analyze_player_transfers()
        transfer_file = self.output_dir / 'mappings' / 'player_transfers.json'
        with open(transfer_file, 'w') as f:
            json.dump(transfers, f, indent=2, default=str)

        print(f"Saved transfer analysis to {transfer_file}")

        return mapping_data

    def analyze_player_transfers(self):
        """Analyze player transfers between core teams."""
        transfers = {
            'players_with_multiple_teams': [],
            'transfer_summary': {
                'total_players': len(self.player_team_mapping),
                'players_with_transfers': 0,
                'total_transfers': 0
            }
        }

        for player_id, team_history in self.player_team_mapping.items():
            if len(team_history) > 1:
                # Player has been with multiple teams
                transfers['players_with_multiple_teams'].append({
                    'player_id': player_id,
                    'total_teams': len(team_history),
                    'team_history': sorted(team_history, key=lambda x: x['season'])
                })
                transfers['transfer_summary']['players_with_transfers'] += 1
                transfers['transfer_summary']['total_transfers'] += len(team_history) - 1

        return transfers

    def save_api_usage_report(self):
        """Save API usage report for tracking."""
        report = {
            'collection_session': {
                'timestamp': datetime.now().isoformat(),
                'total_requests': self.request_count,
                'remaining_requests': self.daily_limit - self.request_count,
                'usage_percentage': (self.request_count / self.daily_limit) * 100
            },
            'request_details': self.requests_made,
            'efficiency_metrics': {
                'requests_per_team': self.request_count / len(self.core_teams) if self.core_teams else 0,
                'estimated_players_per_request': len(self.player_team_mapping) / self.request_count if self.request_count > 0 else 0
            }
        }

        report_file = self.output_dir / 'api_usage_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"API usage report saved to {report_file}")
        return report

def main():
    """Main execution function."""
    print("COMPREHENSIVE PLAYER STATISTICS COLLECTION")
    print("=" * 60)
    print("Collecting player statistics for 67 Champions League teams")
    
    collector = PlayerStatisticsCollector()
    
    try:
        # Collect players for all teams and seasons
        total_players = collector.collect_all_team_players()

        # Save player-team mappings and transfer analysis
        mapping_data = collector.save_player_team_mappings()

        # Save API usage report
        api_report = collector.save_api_usage_report()

        print(f"\n{'='*60}")
        print(f"PLAYER COLLECTION COMPLETED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"Total players processed: {total_players}")
        print(f"Unique players: {mapping_data['total_players']}")
        print(f"API requests used: {api_report['collection_session']['total_requests']}")
        print(f"API requests remaining: {api_report['collection_session']['remaining_requests']}")
        print(f"Usage percentage: {api_report['collection_session']['usage_percentage']:.2f}%")

    except Exception as e:
        print(f"Error during player collection: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())

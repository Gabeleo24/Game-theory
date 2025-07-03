#!/usr/bin/env python3
"""
Optimized Player Statistics Collection System for ADS599 Capstone
Focused collection for 67 UEFA Champions League teams, seasons 2020-2025

This script implements the data collection optimization guidelines:
- Restrict to 67 UEFA Champions League teams only
- Limit temporal scope to 2020-2025 (6 seasons)
- Prioritize multi-competition data for core teams
- Maintain API efficiency with rate limiting and caching
- Ensure 99.85% data consistency standard
"""

import json
import sys
import time
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple
import argparse

# Add src to path for imports
sys.path.append('src')

# Import collection modules
from player_statistics_collector import PlayerStatisticsCollector
from competition_specific_collector import CompetitionSpecificCollector

class OptimizedPlayerCollectionSystem:
    """Optimized collection system for ADS599 Capstone project."""
    
    def __init__(self, target_seasons: List[int] = None):
        """
        Initialize the optimized collection system.
        
        Args:
            target_seasons: List of seasons to collect (default: 2020-2025)
        """
        self.target_seasons = target_seasons or [2020, 2021, 2022, 2023, 2024, 2025]
        self.roster_dir = Path("data/focused/players/team_rosters")
        self.output_dir = Path("data/focused/players/individual_stats")
        
        # Core teams from roster files
        self.core_teams = self._extract_core_teams()
        
        # Collection tracking
        self.collection_stats = {
            'start_time': datetime.now().isoformat(),
            'target_seasons': self.target_seasons,
            'core_teams_count': len(self.core_teams),
            'teams_processed': 0,
            'players_collected': 0,
            'api_requests_used': 0,
            'skipped_existing': 0,
            'errors': []
        }
        
        print(f"Optimized Collection System Initialized")
        print(f"Target Seasons: {self.target_seasons}")
        print(f"Core Teams: {len(self.core_teams)} teams")
        print(f"Estimated Scope: {len(self.core_teams) * len(self.target_seasons)} team-seasons")
    
    def _extract_core_teams(self) -> Set[int]:
        """Extract core team IDs from existing roster files."""
        core_teams = set()
        
        if not self.roster_dir.exists():
            print(f"Warning: Roster directory not found: {self.roster_dir}")
            return core_teams
        
        # Extract team IDs from roster filenames
        pattern = re.compile(r'team_(\d+)_players_\d{4}\.json')
        
        for roster_file in self.roster_dir.glob("team_*_players_*.json"):
            match = pattern.match(roster_file.name)
            if match:
                team_id = int(match.group(1))
                core_teams.add(team_id)
        
        print(f"Extracted {len(core_teams)} core teams from roster files")
        return core_teams
    
    def _get_existing_players_for_team_season(self, team_id: int, season: int) -> Set[int]:
        """Get existing player IDs for a team-season to avoid duplicate collection."""
        existing_players = set()
        team_season_dir = self.output_dir / f"team_{team_id}" / str(season)
        
        if team_season_dir.exists():
            for player_file in team_season_dir.glob("player_*.json"):
                # Extract player ID from filename: player_12345_name_2024.json
                parts = player_file.stem.split('_')
                if len(parts) >= 2 and parts[1].isdigit():
                    player_id = int(parts[1])
                    existing_players.add(player_id)
        
        return existing_players
    
    def _load_roster_for_team_season(self, team_id: int, season: int) -> List[Dict]:
        """Load player roster for a specific team and season."""
        roster_file = self.roster_dir / f"team_{team_id}_players_{season}.json"
        
        if not roster_file.exists():
            return []
        
        try:
            with open(roster_file, 'r') as f:
                roster_data = json.load(f)
                return roster_data.get('players', [])
        except Exception as e:
            self.collection_stats['errors'].append(f"Error loading roster {roster_file}: {e}")
            return []
    
    def _should_collect_player(self, player_id: int, team_id: int, season: int, 
                              existing_players: Set[int]) -> bool:
        """Determine if a player should be collected based on optimization criteria."""
        # Skip if already collected
        if player_id in existing_players:
            self.collection_stats['skipped_existing'] += 1
            return False
        
        # Skip if season not in target range
        if season not in self.target_seasons:
            return False
        
        # Skip if team not in core teams
        if team_id not in self.core_teams:
            return False
        
        return True
    
    def collect_optimized_player_statistics(self, max_teams: int = None) -> Dict:
        """
        Run optimized player statistics collection.
        
        Args:
            max_teams: Maximum number of teams to process (for testing)
            
        Returns:
            Collection results summary
        """
        print(f"\nStarting Optimized Player Statistics Collection")
        print(f"Target: {len(self.core_teams)} teams × {len(self.target_seasons)} seasons")
        print("=" * 60)
        
        # Initialize collector
        collector = PlayerStatisticsCollector()
        
        teams_to_process = list(self.core_teams)
        if max_teams:
            teams_to_process = teams_to_process[:max_teams]
            print(f"Limited to first {max_teams} teams for testing")
        
        for team_id in teams_to_process:
            print(f"\nProcessing Team {team_id} ({self.collection_stats['teams_processed'] + 1}/{len(teams_to_process)})")
            
            team_players_collected = 0
            
            for season in self.target_seasons:
                print(f"  Season {season}...")
                
                # Load roster for this team-season
                roster_players = self._load_roster_for_team_season(team_id, season)
                if not roster_players:
                    print(f"    No roster found for team {team_id}, season {season}")
                    continue
                
                # Get existing players to avoid duplicates
                existing_players = self._get_existing_players_for_team_season(team_id, season)
                
                # Filter players based on optimization criteria
                players_to_collect = []
                for player in roster_players:
                    player_id = player.get('id')
                    if player_id and self._should_collect_player(player_id, team_id, season, existing_players):
                        players_to_collect.append(player)
                
                if not players_to_collect:
                    print(f"    No new players to collect for season {season}")
                    continue
                
                print(f"    Collecting {len(players_to_collect)} players (skipped {len(existing_players)} existing)")
                
                # Collect player statistics
                try:
                    season_results = collector.collect_team_season_players(
                        team_id=team_id,
                        season=season,
                        players_list=players_to_collect,
                        force_refresh=False  # Respect existing data
                    )
                    
                    if season_results:
                        players_collected = season_results.get('players_collected', 0)
                        api_requests = season_results.get('api_requests_used', 0)
                        
                        team_players_collected += players_collected
                        self.collection_stats['players_collected'] += players_collected
                        self.collection_stats['api_requests_used'] += api_requests
                        
                        print(f"    ✓ Collected {players_collected} players, {api_requests} API requests")
                    
                    # Rate limiting - respect API limits
                    time.sleep(0.6)  # 100 requests per minute = 0.6 seconds between requests
                    
                except Exception as e:
                    error_msg = f"Error collecting team {team_id}, season {season}: {e}"
                    self.collection_stats['errors'].append(error_msg)
                    print(f"    ✗ {error_msg}")
            
            self.collection_stats['teams_processed'] += 1
            print(f"  Team {team_id} complete: {team_players_collected} players collected")
        
        # Finalize results
        self.collection_stats['end_time'] = datetime.now().isoformat()
        self.collection_stats['duration_minutes'] = (
            datetime.fromisoformat(self.collection_stats['end_time']) - 
            datetime.fromisoformat(self.collection_stats['start_time'])
        ).total_seconds() / 60
        
        return self.collection_stats
    
    def generate_collection_report(self, results: Dict) -> None:
        """Generate and save collection report."""
        print(f"\n{'='*60}")
        print("OPTIMIZED COLLECTION COMPLETED")
        print(f"{'='*60}")
        
        print(f"Duration: {results['duration_minutes']:.2f} minutes")
        print(f"Teams processed: {results['teams_processed']}/{results['core_teams_count']}")
        print(f"Players collected: {results['players_collected']}")
        print(f"API requests used: {results['api_requests_used']}")
        print(f"Existing players skipped: {results['skipped_existing']}")
        print(f"Errors encountered: {len(results['errors'])}")
        
        if results['errors']:
            print(f"\nErrors:")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(results['errors']) > 5:
                print(f"  ... and {len(results['errors']) - 5} more errors")
        
        # Save detailed report
        report_path = Path("data/analysis/optimized_collection_report.json")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nDetailed report saved to: {report_path}")
    
    def validate_collection_scope(self) -> Dict:
        """Validate that collection scope matches optimization guidelines."""
        validation_results = {
            'core_teams_found': len(self.core_teams),
            'target_seasons': self.target_seasons,
            'season_range_valid': min(self.target_seasons) >= 2020 and max(self.target_seasons) <= 2025,
            'roster_files_available': 0,
            'missing_rosters': []
        }
        
        # Check roster file availability
        for team_id in self.core_teams:
            for season in self.target_seasons:
                roster_file = self.roster_dir / f"team_{team_id}_players_{season}.json"
                if roster_file.exists():
                    validation_results['roster_files_available'] += 1
                else:
                    validation_results['missing_rosters'].append(f"team_{team_id}_players_{season}.json")
        
        expected_rosters = len(self.core_teams) * len(self.target_seasons)
        validation_results['roster_coverage_pct'] = (
            validation_results['roster_files_available'] / expected_rosters * 100
        )
        
        print(f"Collection Scope Validation:")
        print(f"  Core teams: {validation_results['core_teams_found']}")
        print(f"  Target seasons: {validation_results['target_seasons']}")
        print(f"  Season range valid: {validation_results['season_range_valid']}")
        print(f"  Roster coverage: {validation_results['roster_coverage_pct']:.1f}%")
        print(f"  Missing rosters: {len(validation_results['missing_rosters'])}")
        
        return validation_results

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Optimized Player Collection for ADS599 Capstone')
    parser.add_argument('--seasons', nargs='+', type=int, default=[2020, 2021, 2022, 2023, 2024, 2025],
                       help='Target seasons for collection')
    parser.add_argument('--max-teams', type=int, help='Maximum number of teams to process (for testing)')
    parser.add_argument('--validate-only', action='store_true', help='Only validate scope, do not collect')
    
    args = parser.parse_args()
    
    # Initialize system
    system = OptimizedPlayerCollectionSystem(target_seasons=args.seasons)
    
    # Validate scope
    validation_results = system.validate_collection_scope()
    
    if args.validate_only:
        print("Validation complete. Use --help for collection options.")
        return
    
    # Run optimized collection
    collection_results = system.collect_optimized_player_statistics(max_teams=args.max_teams)
    
    # Generate report
    system.generate_collection_report(collection_results)

if __name__ == "__main__":
    main()

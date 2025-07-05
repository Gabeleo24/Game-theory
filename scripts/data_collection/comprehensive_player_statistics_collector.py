#!/usr/bin/env python3
"""
Comprehensive Player Statistics Collector for ADS599 Capstone Project

This system collects detailed individual player performance data for each match,
including formations, tactical changes, and match-by-match statistics.

Features:
- Individual player match performance collection
- Team formation and tactical analysis
- Integration with existing team statistics
- Comprehensive data validation and quality assurance
- Efficient API usage with intelligent caching
"""

import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
import logging

# Import our enhanced API client
from enhanced_player_statistics_api_client import (
    EnhancedPlayerStatisticsAPIClient,
    PlayerMatchPerformance,
    TeamFormation
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensivePlayerStatisticsCollector:
    """Main collector for comprehensive player statistics across all teams and seasons."""
    
    def __init__(self):
        """Initialize the comprehensive player statistics collector."""
        self.api_client = EnhancedPlayerStatisticsAPIClient()
        self.output_dir = Path("data/focused/players")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing team data to get fixture IDs
        self.team_data_dir = Path("data/focused/teams")
        self.core_teams = self._load_core_teams()
        
        # Collection tracking
        self.collection_stats = {
            'teams_processed': 0,
            'seasons_processed': 0,
            'matches_processed': 0,
            'players_processed': 0,
            'formations_collected': 0,
            'events_collected': 0,
            'api_requests_made': 0,
            'errors_encountered': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Data validation tracking
        self.validation_stats = {
            'valid_player_performances': 0,
            'invalid_player_performances': 0,
            'valid_formations': 0,
            'invalid_formations': 0,
            'consistency_checks_passed': 0,
            'consistency_checks_failed': 0
        }
    
    def _load_core_teams(self) -> Dict[int, Dict[str, Any]]:
        """Load core team information from roster files."""
        core_teams = {}
        roster_dir = Path("data/focused/players/team_rosters")

        if not roster_dir.exists():
            logger.warning(f"Roster directory not found: {roster_dir}")
            return core_teams

        # Look for files with pattern team_{team_id}_players_{season}.json
        for roster_file in roster_dir.glob("team_*_players_*.json"):
            try:
                with open(roster_file, 'r') as f:
                    roster_data = json.load(f)

                team_id = roster_data.get('team_id')
                if team_id and team_id not in core_teams:  # Only add if not already added
                    core_teams[team_id] = {
                        'name': roster_data.get('team_name', f'Team {team_id}'),
                        'league_id': roster_data.get('league_id'),
                        'league_name': roster_data.get('league_name', 'Unknown League')
                    }
            except Exception as e:
                logger.warning(f"Error loading roster file {roster_file}: {e}")

        logger.info(f"Loaded {len(core_teams)} core teams")
        return core_teams
    
    def _get_team_fixtures(self, team_id: int, season: int) -> List[Dict[str, Any]]:
        """Get all fixtures for a team in a specific season from existing team data."""
        team_stats_file = self.team_data_dir / f"team_{team_id}" / str(season) / f"team_{team_id}_statistics_{season}.json"

        if not team_stats_file.exists():
            if season == 2019:
                logger.info(f"Team statistics file not found for 2019 (expected): {team_stats_file}")
                logger.info(f"Note: 2019 team data may need to be collected first")
            else:
                logger.warning(f"Team statistics file not found: {team_stats_file}")
            return []
        
        try:
            with open(team_stats_file, 'r') as f:
                team_data = json.load(f)
            
            # Extract match details
            match_details = team_data.get('match_details', [])
            fixtures = []
            
            for match in match_details:
                fixture_id = match.get('fixture_id')
                if fixture_id:
                    fixtures.append({
                        'fixture_id': fixture_id,
                        'date': match.get('date'),
                        'league': match.get('league', {}),
                        'teams': match.get('teams', {}),
                        'score': match.get('score', {}),
                        'venue': match.get('venue', {})
                    })
            
            logger.info(f"Found {len(fixtures)} fixtures for team {team_id} season {season}")
            return fixtures
            
        except Exception as e:
            logger.error(f"Error loading team statistics for team {team_id} season {season}: {e}")
            return []
    
    def _collect_match_player_data(self, fixture_id: int, team_id: int, match_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect comprehensive player data for a single match.
        
        Args:
            fixture_id: Match fixture ID
            team_id: Team ID
            match_info: Basic match information
            
        Returns:
            Comprehensive match player data
        """
        logger.info(f"  Collecting player data for fixture {fixture_id}")
        
        # Collect player statistics
        player_performances = self.api_client.get_match_player_statistics(fixture_id)
        
        # Collect formation data
        formations = self.api_client.get_match_lineups(fixture_id)
        
        # Collect match events
        events = self.api_client.get_match_events(fixture_id)
        
        # Filter data for the specific team
        team_player_performances = [p for p in player_performances if p.team_id == team_id]
        team_formation = next((f for f in formations if f.team_id == team_id), None)
        team_events = [e for e in events if e.get('team', {}).get('id') == team_id]
        
        # Process and structure the data
        match_data = {
            'fixture_id': fixture_id,
            'match_info': match_info,
            'player_performances': self._process_player_performances(team_player_performances),
            'formation_data': self._process_formation_data(team_formation) if team_formation else None,
            'match_events': self._process_match_events(team_events),
            'tactical_summary': self._generate_tactical_summary(team_player_performances, team_formation, team_events)
        }
        
        # Update collection statistics
        self.collection_stats['matches_processed'] += 1
        self.collection_stats['players_processed'] += len(team_player_performances)
        if team_formation:
            self.collection_stats['formations_collected'] += 1
        self.collection_stats['events_collected'] += len(team_events)
        
        return match_data
    
    def _process_player_performances(self, performances: List[PlayerMatchPerformance]) -> List[Dict[str, Any]]:
        """Process and validate player performance data."""
        processed_performances = []
        
        for performance in performances:
            # Validate performance data
            if self._validate_player_performance(performance):
                processed_data = {
                    'player_info': {
                        'player_id': performance.player_id,
                        'player_name': performance.player_name,
                        'position': performance.position
                    },
                    'performance_metrics': {
                        'minutes_played': performance.minutes_played,
                        'rating': performance.rating,
                        'goals': performance.goals,
                        'assists': performance.assists,
                        'shots': {
                            'total': performance.shots_total,
                            'on_target': performance.shots_on_target
                        },
                        'passes': {
                            'total': performance.passes_total,
                            'completed': performance.passes_completed,
                            'accuracy': performance.pass_accuracy
                        },
                        'defensive': {
                            'tackles': performance.tackles,
                            'interceptions': performance.interceptions
                        },
                        'discipline': {
                            'fouls_committed': performance.fouls_committed,
                            'fouls_drawn': performance.fouls_drawn,
                            'yellow_cards': performance.yellow_cards,
                            'red_cards': performance.red_cards
                        }
                    },
                    'substitution_info': {
                        'substitution_in': performance.substitution_in,
                        'substitution_out': performance.substitution_out
                    }
                }
                processed_performances.append(processed_data)
                self.validation_stats['valid_player_performances'] += 1
            else:
                self.validation_stats['invalid_player_performances'] += 1
                logger.warning(f"Invalid player performance data for player {performance.player_id}")
        
        return processed_performances
    
    def _process_formation_data(self, formation: TeamFormation) -> Dict[str, Any]:
        """Process and validate formation data."""
        if not self._validate_formation(formation):
            self.validation_stats['invalid_formations'] += 1
            return None
        
        self.validation_stats['valid_formations'] += 1
        
        return {
            'formation': formation.formation,
            'starting_eleven': [
                {
                    'player_id': player.get('player', {}).get('id'),
                    'player_name': player.get('player', {}).get('name'),
                    'position': player.get('player', {}).get('pos'),
                    'grid_position': player.get('player', {}).get('grid'),
                    'jersey_number': player.get('player', {}).get('number')
                }
                for player in formation.starting_eleven
            ],
            'substitutes': [
                {
                    'player_id': player.get('player', {}).get('id'),
                    'player_name': player.get('player', {}).get('name'),
                    'position': player.get('player', {}).get('pos'),
                    'jersey_number': player.get('player', {}).get('number')
                }
                for player in formation.substitutes
            ],
            'coach': {
                'coach_id': formation.coach.get('id'),
                'coach_name': formation.coach.get('name'),
                'photo': formation.coach.get('photo')
            }
        }
    
    def _process_match_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and structure match events."""
        processed_events = []
        
        for event in events:
            processed_event = {
                'time_elapsed': event.get('time', {}).get('elapsed'),
                'time_extra': event.get('time', {}).get('extra'),
                'event_type': event.get('type'),
                'detail': event.get('detail'),
                'player': {
                    'player_id': event.get('player', {}).get('id'),
                    'player_name': event.get('player', {}).get('name')
                },
                'assist': {
                    'player_id': event.get('assist', {}).get('id'),
                    'player_name': event.get('assist', {}).get('name')
                } if event.get('assist') else None,
                'comments': event.get('comments')
            }
            processed_events.append(processed_event)
        
        return processed_events
    
    def _generate_tactical_summary(self, performances: List[PlayerMatchPerformance], 
                                 formation: Optional[TeamFormation], 
                                 events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate tactical summary for the match."""
        if not performances:
            return {}
        
        # Calculate team-level metrics from individual performances
        total_minutes = sum(p.minutes_played for p in performances)
        total_passes = sum(p.passes_total for p in performances if p.passes_total)
        total_tackles = sum(p.tackles for p in performances if p.tackles)
        total_shots = sum(p.shots_total for p in performances if p.shots_total)
        
        # Count substitutions
        substitutions = [e for e in events if e.get('type') == 'subst']
        
        return {
            'formation_used': formation.formation if formation else None,
            'total_player_minutes': total_minutes,
            'team_passing_stats': {
                'total_passes': total_passes,
                'average_pass_accuracy': sum(p.pass_accuracy for p in performances if p.pass_accuracy) / len([p for p in performances if p.pass_accuracy]) if performances else 0
            },
            'team_defensive_stats': {
                'total_tackles': total_tackles,
                'total_interceptions': sum(p.interceptions for p in performances if p.interceptions)
            },
            'team_attacking_stats': {
                'total_shots': total_shots,
                'total_goals': sum(p.goals for p in performances),
                'total_assists': sum(p.assists for p in performances)
            },
            'substitutions_made': len(substitutions),
            'cards_received': {
                'yellow': sum(p.yellow_cards for p in performances),
                'red': sum(p.red_cards for p in performances)
            }
        }
    
    def _validate_player_performance(self, performance: PlayerMatchPerformance) -> bool:
        """Validate individual player performance data."""
        try:
            # Basic validation rules
            if performance.minutes_played < 0 or performance.minutes_played > 120:
                return False
            if performance.goals < 0 or performance.assists < 0:
                return False
            if performance.pass_accuracy is not None and (performance.pass_accuracy < 0 or performance.pass_accuracy > 100):
                return False
            if performance.rating is not None and (performance.rating < 0 or performance.rating > 10):
                return False
            
            return True
        except Exception:
            return False
    
    def _validate_formation(self, formation: TeamFormation) -> bool:
        """Validate formation data."""
        try:
            # Check if formation string is valid
            if not formation.formation or not isinstance(formation.formation, str):
                return False
            
            # Check if starting eleven has 11 players
            if len(formation.starting_eleven) != 11:
                return False
            
            return True
        except Exception:
            return False
    
    def collect_team_season_player_data(self, team_id: int, season: int) -> Dict[str, Any]:
        """
        Collect comprehensive player data for a team's entire season.
        
        Args:
            team_id: Team ID
            season: Season year
            
        Returns:
            Complete season player data
        """
        logger.info(f"Collecting player data for team {team_id} season {season}")
        
        # Get all fixtures for the team/season
        fixtures = self._get_team_fixtures(team_id, season)
        
        if not fixtures:
            logger.warning(f"No fixtures found for team {team_id} season {season}")
            return {}
        
        # Collect player data for each match
        match_statistics = []
        formations_used = {}
        all_events = []
        
        for i, fixture in enumerate(fixtures):
            try:
                logger.info(f"  Processing match {i+1}/{len(fixtures)}: {fixture['fixture_id']}")
                
                match_data = self._collect_match_player_data(
                    fixture['fixture_id'], 
                    team_id, 
                    fixture
                )
                
                if match_data:
                    match_statistics.append(match_data)
                    
                    # Track formations used
                    if match_data.get('formation_data', {}).get('formation'):
                        formation = match_data['formation_data']['formation']
                        formations_used[formation] = formations_used.get(formation, 0) + 1
                    
                    # Collect all events
                    all_events.extend(match_data.get('match_events', []))
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing fixture {fixture['fixture_id']}: {e}")
                self.collection_stats['errors_encountered'] += 1
                continue
        
        # Generate season summary
        season_data = {
            'team_id': team_id,
            'season': season,
            'collection_timestamp': datetime.now().isoformat(),
            'match_statistics': match_statistics,
            'season_summary': self._generate_season_summary(match_statistics, formations_used, all_events),
            'formations_analysis': self._analyze_formations(formations_used),
            'player_season_stats': self._aggregate_player_season_stats(match_statistics)
        }
        
        return season_data

    def _generate_season_summary(self, match_statistics: List[Dict[str, Any]],
                               formations_used: Dict[str, int],
                               all_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive season summary."""
        if not match_statistics:
            return {}

        total_matches = len(match_statistics)
        total_players_used = set()
        total_goals = 0
        total_assists = 0
        total_minutes = 0

        for match in match_statistics:
            for player_perf in match.get('player_performances', []):
                total_players_used.add(player_perf['player_info']['player_id'])
                total_goals += player_perf['performance_metrics']['goals']
                total_assists += player_perf['performance_metrics']['assists']
                total_minutes += player_perf['performance_metrics']['minutes_played']

        return {
            'total_matches': total_matches,
            'total_players_used': len(total_players_used),
            'total_goals_scored': total_goals,
            'total_assists': total_assists,
            'total_player_minutes': total_minutes,
            'most_used_formation': max(formations_used.items(), key=lambda x: x[1])[0] if formations_used else None,
            'formations_variety': len(formations_used),
            'average_players_per_match': total_minutes / (total_matches * 90) if total_matches > 0 else 0
        }

    def _analyze_formations(self, formations_used: Dict[str, int]) -> Dict[str, Any]:
        """Analyze formation usage patterns."""
        if not formations_used:
            return {}

        total_matches = sum(formations_used.values())

        return {
            'formations_used': formations_used,
            'formation_percentages': {
                formation: (count / total_matches) * 100
                for formation, count in formations_used.items()
            },
            'most_frequent_formation': max(formations_used.items(), key=lambda x: x[1]),
            'formation_variety_score': len(formations_used) / total_matches if total_matches > 0 else 0
        }

    def _aggregate_player_season_stats(self, match_statistics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate individual player statistics across the season."""
        player_stats = defaultdict(lambda: {
            'appearances': 0,
            'minutes_played': 0,
            'goals': 0,
            'assists': 0,
            'shots_total': 0,
            'shots_on_target': 0,
            'passes_total': 0,
            'passes_completed': 0,
            'tackles': 0,
            'interceptions': 0,
            'yellow_cards': 0,
            'red_cards': 0,
            'average_rating': 0,
            'ratings_count': 0,
            'positions_played': set()
        })

        for match in match_statistics:
            for player_perf in match.get('player_performances', []):
                player_id = player_perf['player_info']['player_id']
                player_name = player_perf['player_info']['player_name']
                metrics = player_perf['performance_metrics']

                # Update player stats
                stats = player_stats[player_id]
                stats['player_name'] = player_name
                stats['appearances'] += 1
                stats['minutes_played'] += metrics['minutes_played']
                stats['goals'] += metrics['goals']
                stats['assists'] += metrics['assists']
                stats['shots_total'] += metrics['shots']['total']
                stats['shots_on_target'] += metrics['shots']['on_target']
                stats['passes_total'] += metrics['passes']['total']
                stats['passes_completed'] += metrics['passes']['completed']
                stats['tackles'] += metrics['defensive']['tackles']
                stats['interceptions'] += metrics['defensive']['interceptions']
                stats['yellow_cards'] += metrics['discipline']['yellow_cards']
                stats['red_cards'] += metrics['discipline']['red_cards']

                # Handle rating average
                if metrics['rating']:
                    stats['average_rating'] = (
                        (stats['average_rating'] * stats['ratings_count'] + metrics['rating']) /
                        (stats['ratings_count'] + 1)
                    )
                    stats['ratings_count'] += 1

                # Track positions
                if player_perf['player_info']['position']:
                    stats['positions_played'].add(player_perf['player_info']['position'])

        # Convert sets to lists for JSON serialization
        for player_id, stats in player_stats.items():
            stats['positions_played'] = list(stats['positions_played'])
            # Calculate derived metrics
            if stats['minutes_played'] > 0:
                stats['goals_per_90'] = (stats['goals'] / stats['minutes_played']) * 90
                stats['assists_per_90'] = (stats['assists'] / stats['minutes_played']) * 90
            else:
                stats['goals_per_90'] = 0
                stats['assists_per_90'] = 0

        return dict(player_stats)

    def save_team_season_data(self, team_id: int, season: int, season_data: Dict[str, Any]):
        """Save team season player data to files."""
        team_dir = self.output_dir / f"team_{team_id}" / str(season)
        team_dir.mkdir(parents=True, exist_ok=True)

        # Save main player statistics file
        main_file = team_dir / f"team_{team_id}_player_match_statistics_{season}.json"
        with open(main_file, 'w') as f:
            json.dump(season_data, f, indent=2, default=str)

        # Save formations analysis separately
        formations_file = team_dir / f"team_{team_id}_formations_{season}.json"
        formations_data = {
            'team_id': team_id,
            'season': season,
            'collection_timestamp': season_data['collection_timestamp'],
            'formations_analysis': season_data['formations_analysis']
        }
        with open(formations_file, 'w') as f:
            json.dump(formations_data, f, indent=2, default=str)

        # Save player season summary
        player_summary_file = team_dir / f"team_{team_id}_player_season_summary_{season}.json"
        player_summary_data = {
            'team_id': team_id,
            'season': season,
            'collection_timestamp': season_data['collection_timestamp'],
            'season_summary': season_data['season_summary'],
            'player_season_stats': season_data['player_season_stats']
        }
        with open(player_summary_file, 'w') as f:
            json.dump(player_summary_data, f, indent=2, default=str)

        logger.info(f"Saved player data for team {team_id} season {season}")

    def collect_all_teams_player_data(self, seasons: List[int] = None, max_teams: Optional[int] = None) -> Dict[str, Any]:
        """
        Collect player data for all teams across specified seasons.

        Args:
            seasons: List of seasons to collect (default: 2019-2024)
            max_teams: Maximum number of teams to process (for testing)

        Returns:
            Collection summary
        """
        # Default to 2019-2024 if no seasons specified
        if seasons is None:
            seasons = [2019, 2020, 2021, 2022, 2023, 2024]

        self.collection_stats['start_time'] = datetime.now()

        teams_to_process = list(self.core_teams.keys())
        if max_teams:
            teams_to_process = teams_to_process[:max_teams]
            logger.info(f"Limited to first {max_teams} teams for testing")

        logger.info(f"Starting player data collection for {len(teams_to_process)} teams across {len(seasons)} seasons")
        logger.info(f"Target seasons: {seasons}")

        for i, team_id in enumerate(teams_to_process):
            team_name = self.core_teams[team_id]['name']
            logger.info(f"\nProcessing Team {i+1}/{len(teams_to_process)}: {team_name} (ID: {team_id})")

            for season in seasons:
                try:
                    logger.info(f"  Season {season}...")

                    # Check if data already exists
                    existing_file = self.output_dir / f"team_{team_id}" / str(season) / f"team_{team_id}_player_match_statistics_{season}.json"
                    if existing_file.exists():
                        logger.info(f"    Data already exists, skipping...")
                        continue

                    # Special handling for 2019 season
                    if season == 2019:
                        # Check if team statistics exist for 2019
                        team_stats_file = self.team_data_dir / f"team_{team_id}" / str(season) / f"team_{team_id}_statistics_{season}.json"
                        if not team_stats_file.exists():
                            logger.info(f"    Skipping 2019 - team statistics not available yet")
                            logger.info(f"    Note: Run team statistics collection for 2019 first")
                            continue

                    # Collect season data
                    season_data = self.collect_team_season_player_data(team_id, season)

                    if season_data:
                        # Save the data
                        self.save_team_season_data(team_id, season, season_data)
                        self.collection_stats['seasons_processed'] += 1
                        logger.info(f"    ✓ Season {season} complete")
                    else:
                        if season == 2019:
                            logger.info(f"    No data collected for season {season} (team data may be incomplete)")
                        else:
                            logger.warning(f"    No data collected for season {season}")

                except Exception as e:
                    logger.error(f"Error processing team {team_id} season {season}: {e}")
                    self.collection_stats['errors_encountered'] += 1
                    continue

            self.collection_stats['teams_processed'] += 1
            logger.info(f"  Team {team_name} complete")

        self.collection_stats['end_time'] = datetime.now()

        # Generate final report
        return self._generate_collection_report()

    def _generate_collection_report(self) -> Dict[str, Any]:
        """Generate comprehensive collection report."""
        duration = (self.collection_stats['end_time'] - self.collection_stats['start_time']).total_seconds() / 60
        api_stats = self.api_client.get_api_statistics()

        report = {
            'collection_summary': {
                'duration_minutes': duration,
                'teams_processed': self.collection_stats['teams_processed'],
                'seasons_processed': self.collection_stats['seasons_processed'],
                'matches_processed': self.collection_stats['matches_processed'],
                'players_processed': self.collection_stats['players_processed'],
                'formations_collected': self.collection_stats['formations_collected'],
                'events_collected': self.collection_stats['events_collected'],
                'errors_encountered': self.collection_stats['errors_encountered']
            },
            'api_usage': api_stats,
            'data_quality': self.validation_stats,
            'efficiency_metrics': {
                'matches_per_minute': self.collection_stats['matches_processed'] / duration if duration > 0 else 0,
                'players_per_minute': self.collection_stats['players_processed'] / duration if duration > 0 else 0,
                'api_efficiency': (api_stats['cached_requests'] / (api_stats['total_requests'] + api_stats['cached_requests'])) * 100 if (api_stats['total_requests'] + api_stats['cached_requests']) > 0 else 0
            }
        }

        # Save report
        report_file = self.output_dir / 'comprehensive_player_statistics_collection_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return report

def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Comprehensive Player Statistics Collection for ADS599 Capstone')
    parser.add_argument('--seasons', nargs='+', type=int, default=[2019, 2020, 2021, 2022, 2023, 2024],
                       help='Target seasons for collection (default: 2019-2024)')
    parser.add_argument('--max-teams', type=int, help='Maximum number of teams to process (for testing)')
    parser.add_argument('--validate-only', action='store_true', help='Only validate existing data, do not collect')
    parser.add_argument('--skip-2019', action='store_true', help='Skip 2019 season if team data not available')

    args = parser.parse_args()

    # Handle skip-2019 option
    seasons_to_collect = args.seasons
    if args.skip_2019 and 2019 in seasons_to_collect:
        seasons_to_collect = [s for s in seasons_to_collect if s != 2019]
        logger.info("Skipping 2019 season as requested")

    # Initialize collector
    collector = ComprehensivePlayerStatisticsCollector()

    if args.validate_only:
        logger.info("Validation mode - checking existing player data quality")
        # TODO: Implement validation-only mode
        return

    # Start collection
    logger.info("="*70)
    logger.info("COMPREHENSIVE PLAYER STATISTICS COLLECTION")
    logger.info("="*70)
    logger.info(f"Target seasons: {seasons_to_collect}")

    try:
        report = collector.collect_all_teams_player_data(seasons_to_collect, args.max_teams)

        # Print summary
        logger.info("\n" + "="*70)
        logger.info("COLLECTION COMPLETED")
        logger.info("="*70)
        logger.info(f"Duration: {report['collection_summary']['duration_minutes']:.2f} minutes")
        logger.info(f"Teams processed: {report['collection_summary']['teams_processed']}")
        logger.info(f"Seasons processed: {report['collection_summary']['seasons_processed']}")
        logger.info(f"Matches processed: {report['collection_summary']['matches_processed']}")
        logger.info(f"Players processed: {report['collection_summary']['players_processed']}")
        logger.info(f"API requests made: {report['api_usage']['total_requests']}")
        logger.info(f"Cache efficiency: {report['efficiency_metrics']['api_efficiency']:.1f}%")
        logger.info(f"Errors encountered: {report['collection_summary']['errors_encountered']}")

    except KeyboardInterrupt:
        logger.info("\nCollection interrupted by user")
    except Exception as e:
        logger.error(f"Collection failed: {e}")
        raise

if __name__ == "__main__":
    main()

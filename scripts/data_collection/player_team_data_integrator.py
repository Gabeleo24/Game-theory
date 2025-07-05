#!/usr/bin/env python3
"""
Player-Team Data Integration System for ADS599 Capstone Project

This module provides seamless integration between individual player statistics
and existing team statistics, ensuring data consistency and enabling
comprehensive analysis across both individual and team performance levels.

Features:
- Link player statistics to team match data via fixture IDs
- Validate consistency between player and team data
- Generate integrated analysis reports
- Support for cross-referencing and data validation
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlayerTeamDataIntegrator:
    """Integration system for player and team statistics data."""
    
    def __init__(self):
        """Initialize the player-team data integrator."""
        self.team_data_dir = Path("data/focused/teams")
        self.player_data_dir = Path("data/focused/players")
        
        # Integration tracking
        self.integration_stats = {
            'teams_integrated': 0,
            'seasons_integrated': 0,
            'matches_linked': 0,
            'players_linked': 0,
            'consistency_checks_passed': 0,
            'consistency_checks_failed': 0,
            'data_quality_score': 0.0
        }
        
        # Validation results
        self.validation_results = {
            'fixture_id_matches': [],
            'player_count_discrepancies': [],
            'formation_consistency_issues': [],
            'score_consistency_issues': [],
            'missing_player_data': [],
            'missing_team_data': []
        }
    
    def validate_team_player_consistency(self, team_id: int, season: int) -> Dict[str, Any]:
        """
        Validate consistency between team and player data for a specific team/season.

        Args:
            team_id: Team ID
            season: Season year

        Returns:
            Validation results and consistency metrics
        """
        logger.info(f"Validating consistency for team {team_id} season {season}")

        # Load team statistics
        team_stats = self._load_team_statistics(team_id, season)
        if not team_stats:
            if season == 2019:
                logger.info(f"No team statistics found for team {team_id} season {season} (2019 data may not be collected yet)")
                return {'status': 'no_team_data_2019', 'message': '2019 team data not available'}
            else:
                logger.warning(f"No team statistics found for team {team_id} season {season}")
                return {'status': 'no_team_data'}

        # Load player statistics
        player_stats = self._load_player_statistics(team_id, season)
        if not player_stats:
            if season == 2019:
                logger.info(f"No player statistics found for team {team_id} season {season} (expected if not collected yet)")
                return {'status': 'no_player_data_2019', 'message': '2019 player data not available'}
            else:
                logger.warning(f"No player statistics found for team {team_id} season {season}")
                return {'status': 'no_player_data'}
        
        # Perform consistency checks
        validation_results = {
            'team_id': team_id,
            'season': season,
            'validation_timestamp': datetime.now().isoformat(),
            'fixture_consistency': self._validate_fixture_consistency(team_stats, player_stats),
            'score_consistency': self._validate_score_consistency(team_stats, player_stats),
            'formation_consistency': self._validate_formation_consistency(team_stats, player_stats),
            'player_count_consistency': self._validate_player_count_consistency(team_stats, player_stats),
            'overall_consistency_score': 0.0
        }
        
        # Calculate overall consistency score
        consistency_scores = [
            validation_results['fixture_consistency']['consistency_score'],
            validation_results['score_consistency']['consistency_score'],
            validation_results['formation_consistency']['consistency_score'],
            validation_results['player_count_consistency']['consistency_score']
        ]
        validation_results['overall_consistency_score'] = sum(consistency_scores) / len(consistency_scores)
        
        return validation_results
    
    def _load_team_statistics(self, team_id: int, season: int) -> Optional[Dict[str, Any]]:
        """Load team statistics data."""
        team_file = self.team_data_dir / f"team_{team_id}" / str(season) / f"team_{team_id}_statistics_{season}.json"
        
        if not team_file.exists():
            return None
        
        try:
            with open(team_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading team statistics: {e}")
            return None
    
    def _load_player_statistics(self, team_id: int, season: int) -> Optional[Dict[str, Any]]:
        """Load player statistics data."""
        player_file = self.player_data_dir / f"team_{team_id}" / str(season) / f"team_{team_id}_player_match_statistics_{season}.json"
        
        if not player_file.exists():
            return None
        
        try:
            with open(player_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading player statistics: {e}")
            return None
    
    def _validate_fixture_consistency(self, team_stats: Dict[str, Any], player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that fixture IDs match between team and player data."""
        team_fixtures = set()
        player_fixtures = set()
        
        # Extract fixture IDs from team data
        for match in team_stats.get('match_details', []):
            if match.get('fixture_id'):
                team_fixtures.add(match['fixture_id'])
        
        # Extract fixture IDs from player data
        for match in player_stats.get('match_statistics', []):
            if match.get('fixture_id'):
                player_fixtures.add(match['fixture_id'])
        
        # Calculate consistency
        common_fixtures = team_fixtures.intersection(player_fixtures)
        team_only_fixtures = team_fixtures - player_fixtures
        player_only_fixtures = player_fixtures - team_fixtures
        
        consistency_score = len(common_fixtures) / len(team_fixtures.union(player_fixtures)) if team_fixtures.union(player_fixtures) else 0
        
        return {
            'consistency_score': consistency_score,
            'total_team_fixtures': len(team_fixtures),
            'total_player_fixtures': len(player_fixtures),
            'common_fixtures': len(common_fixtures),
            'team_only_fixtures': list(team_only_fixtures),
            'player_only_fixtures': list(player_only_fixtures)
        }
    
    def _validate_score_consistency(self, team_stats: Dict[str, Any], player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that match scores are consistent between team and player data."""
        score_matches = 0
        score_mismatches = []
        total_comparisons = 0
        
        # Create fixture ID to score mapping for team data
        team_scores = {}
        for match in team_stats.get('match_details', []):
            fixture_id = match.get('fixture_id')
            if fixture_id and match.get('score'):
                team_scores[fixture_id] = {
                    'home': match['score'].get('fulltime', {}).get('home'),
                    'away': match['score'].get('fulltime', {}).get('away')
                }
        
        # Compare with player data
        for match in player_stats.get('match_statistics', []):
            fixture_id = match.get('fixture_id')
            if fixture_id in team_scores:
                total_comparisons += 1
                
                # Calculate goals from player data
                player_goals = sum(
                    player['performance_metrics']['goals'] 
                    for player in match.get('player_performances', [])
                )
                
                # Get team score for comparison
                team_score = team_scores[fixture_id]
                
                # Determine if this team was home or away and get expected goals
                match_info = match.get('match_info', {})
                teams = match_info.get('teams', {})
                home_team_id = teams.get('home', {}).get('id')
                away_team_id = teams.get('away', {}).get('id')
                
                expected_goals = None
                if home_team_id == player_stats.get('team_id'):
                    expected_goals = team_score.get('home')
                elif away_team_id == player_stats.get('team_id'):
                    expected_goals = team_score.get('away')
                
                if expected_goals is not None and player_goals == expected_goals:
                    score_matches += 1
                else:
                    score_mismatches.append({
                        'fixture_id': fixture_id,
                        'expected_goals': expected_goals,
                        'player_goals': player_goals
                    })
        
        consistency_score = score_matches / total_comparisons if total_comparisons > 0 else 0
        
        return {
            'consistency_score': consistency_score,
            'total_comparisons': total_comparisons,
            'score_matches': score_matches,
            'score_mismatches': score_mismatches
        }
    
    def _validate_formation_consistency(self, team_stats: Dict[str, Any], player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Validate formation data consistency."""
        formation_matches = 0
        formation_mismatches = []
        total_comparisons = 0
        
        # This is a placeholder for formation validation
        # In practice, team statistics might not have formation data
        # so we'll focus on player formation data consistency
        
        for match in player_stats.get('match_statistics', []):
            fixture_id = match.get('fixture_id')
            formation_data = match.get('formation_data')
            
            if formation_data:
                total_comparisons += 1
                
                # Validate formation structure
                formation = formation_data.get('formation')
                starting_eleven = formation_data.get('starting_eleven', [])
                
                if formation and len(starting_eleven) == 11:
                    formation_matches += 1
                else:
                    formation_mismatches.append({
                        'fixture_id': fixture_id,
                        'formation': formation,
                        'starting_eleven_count': len(starting_eleven)
                    })
        
        consistency_score = formation_matches / total_comparisons if total_comparisons > 0 else 1.0
        
        return {
            'consistency_score': consistency_score,
            'total_comparisons': total_comparisons,
            'formation_matches': formation_matches,
            'formation_mismatches': formation_mismatches
        }
    
    def _validate_player_count_consistency(self, team_stats: Dict[str, Any], player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that player counts are reasonable for each match."""
        valid_player_counts = 0
        invalid_player_counts = []
        total_matches = 0
        
        for match in player_stats.get('match_statistics', []):
            fixture_id = match.get('fixture_id')
            player_performances = match.get('player_performances', [])
            total_matches += 1
            
            # Check if player count is reasonable (should be 11-18 players typically)
            player_count = len(player_performances)
            if 11 <= player_count <= 18:
                valid_player_counts += 1
            else:
                invalid_player_counts.append({
                    'fixture_id': fixture_id,
                    'player_count': player_count
                })
        
        consistency_score = valid_player_counts / total_matches if total_matches > 0 else 0
        
        return {
            'consistency_score': consistency_score,
            'total_matches': total_matches,
            'valid_player_counts': valid_player_counts,
            'invalid_player_counts': invalid_player_counts
        }
    
    def generate_integrated_match_report(self, team_id: int, season: int, fixture_id: int) -> Dict[str, Any]:
        """
        Generate comprehensive integrated report for a specific match.
        
        Args:
            team_id: Team ID
            season: Season year
            fixture_id: Match fixture ID
            
        Returns:
            Integrated match report combining team and player data
        """
        # Load data
        team_stats = self._load_team_statistics(team_id, season)
        player_stats = self._load_player_statistics(team_id, season)
        
        if not team_stats or not player_stats:
            return {'error': 'Missing data'}
        
        # Find specific match data
        team_match = None
        player_match = None
        
        for match in team_stats.get('match_details', []):
            if match.get('fixture_id') == fixture_id:
                team_match = match
                break
        
        for match in player_stats.get('match_statistics', []):
            if match.get('fixture_id') == fixture_id:
                player_match = match
                break
        
        if not team_match or not player_match:
            return {'error': 'Match not found in both datasets'}
        
        # Generate integrated report
        integrated_report = {
            'fixture_id': fixture_id,
            'team_id': team_id,
            'season': season,
            'match_basic_info': {
                'date': team_match.get('date'),
                'venue': team_match.get('venue', {}),
                'referee': team_match.get('referee'),
                'league': team_match.get('league', {}),
                'teams': team_match.get('teams', {}),
                'score': team_match.get('score', {})
            },
            'team_performance': {
                'statistics': team_match.get('statistics', {}),
                'events': team_match.get('events', [])
            },
            'player_performance': {
                'formation': player_match.get('formation_data', {}),
                'individual_stats': player_match.get('player_performances', []),
                'tactical_summary': player_match.get('tactical_summary', {}),
                'match_events': player_match.get('match_events', [])
            },
            'integrated_analysis': self._generate_integrated_analysis(team_match, player_match)
        }
        
        return integrated_report
    
    def _generate_integrated_analysis(self, team_match: Dict[str, Any], player_match: Dict[str, Any]) -> Dict[str, Any]:
        """Generate integrated analysis combining team and player perspectives."""
        analysis = {}
        
        # Calculate team vs individual statistics correlation
        team_stats = team_match.get('statistics', {})
        player_performances = player_match.get('player_performances', [])
        
        if team_stats and player_performances:
            # Sum individual player statistics
            total_player_goals = sum(p['performance_metrics']['goals'] for p in player_performances)
            total_player_shots = sum(p['performance_metrics']['shots']['total'] for p in player_performances)
            total_player_passes = sum(p['performance_metrics']['passes']['total'] for p in player_performances)
            
            # Compare with team statistics
            team_goals = team_stats.get('goals', {}).get('for', 0)
            team_shots = team_stats.get('shots', {}).get('total', 0)
            team_passes = team_stats.get('passes', {}).get('total', 0)
            
            analysis['statistics_correlation'] = {
                'goals_match': total_player_goals == team_goals,
                'shots_correlation': abs(total_player_shots - team_shots) / max(team_shots, 1) if team_shots else 0,
                'passes_correlation': abs(total_player_passes - team_passes) / max(team_passes, 1) if team_passes else 0
            }
        
        # Analyze formation effectiveness
        formation_data = player_match.get('formation_data', {})
        if formation_data:
            analysis['formation_analysis'] = {
                'formation_used': formation_data.get('formation'),
                'tactical_effectiveness': self._assess_tactical_effectiveness(player_performances, team_match)
            }
        
        return analysis
    
    def _assess_tactical_effectiveness(self, player_performances: List[Dict[str, Any]], team_match: Dict[str, Any]) -> Dict[str, Any]:
        """Assess tactical effectiveness based on player and team performance."""
        # This is a simplified tactical assessment
        # In practice, this would involve more sophisticated analysis
        
        total_players = len(player_performances)
        if total_players == 0:
            return {}
        
        # Calculate average player rating
        ratings = [p['performance_metrics']['rating'] for p in player_performances if p['performance_metrics']['rating']]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Assess possession effectiveness
        total_passes = sum(p['performance_metrics']['passes']['total'] for p in player_performances)
        completed_passes = sum(p['performance_metrics']['passes']['completed'] for p in player_performances)
        pass_accuracy = (completed_passes / total_passes * 100) if total_passes > 0 else 0
        
        # Assess attacking effectiveness
        total_shots = sum(p['performance_metrics']['shots']['total'] for p in player_performances)
        shots_on_target = sum(p['performance_metrics']['shots']['on_target'] for p in player_performances)
        shot_accuracy = (shots_on_target / total_shots * 100) if total_shots > 0 else 0
        
        return {
            'average_player_rating': avg_rating,
            'pass_accuracy': pass_accuracy,
            'shot_accuracy': shot_accuracy,
            'tactical_score': (avg_rating * 10 + pass_accuracy + shot_accuracy) / 3
        }

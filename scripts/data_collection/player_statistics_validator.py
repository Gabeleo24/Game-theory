#!/usr/bin/env python3
"""
Player Statistics Data Validation System for ADS599 Capstone Project

This module provides comprehensive validation and quality assurance for
player statistics data, ensuring data integrity and consistency across
the entire dataset.

Features:
- Comprehensive data quality validation
- Integration consistency checks
- Performance benchmarking
- Automated quality reporting
- Data completeness assessment
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlayerStatisticsValidator:
    """Comprehensive validation system for player statistics data."""
    
    def __init__(self):
        """Initialize the player statistics validator."""
        self.player_data_dir = Path("data/focused/players")
        self.team_data_dir = Path("data/focused/teams")
        
        # Validation thresholds
        self.validation_thresholds = {
            'min_matches_per_season': 10,
            'min_players_per_match': 11,
            'max_players_per_match': 18,
            'min_minutes_starter': 45,
            'max_minutes_per_match': 120,
            'min_pass_accuracy': 0,
            'max_pass_accuracy': 100,
            'min_rating': 0,
            'max_rating': 10,
            'expected_formation_patterns': ['3-4-3', '3-5-2', '4-2-3-1', '4-3-3', '4-4-2', '4-5-1', '5-3-2', '5-4-1']
        }
        
        # Validation results
        self.validation_results = {
            'teams_validated': 0,
            'seasons_validated': 0,
            'matches_validated': 0,
            'players_validated': 0,
            'validation_errors': [],
            'quality_scores': {},
            'completeness_scores': {},
            'consistency_scores': {}
        }
    
    def validate_team_season_data(self, team_id: int, season: int) -> Dict[str, Any]:
        """
        Validate all player data for a specific team and season.

        Args:
            team_id: Team ID
            season: Season year

        Returns:
            Comprehensive validation results
        """
        logger.info(f"Validating player data for team {team_id} season {season}")

        # Load player data
        player_data = self._load_player_data(team_id, season)
        if not player_data:
            if season == 2019:
                return {'status': 'no_data_2019', 'team_id': team_id, 'season': season, 'message': '2019 player data not available'}
            else:
                return {'status': 'no_data', 'team_id': team_id, 'season': season}
        
        validation_result = {
            'team_id': team_id,
            'season': season,
            'validation_timestamp': datetime.now().isoformat(),
            'data_completeness': self._validate_data_completeness(player_data),
            'data_quality': self._validate_data_quality(player_data),
            'statistical_consistency': self._validate_statistical_consistency(player_data),
            'formation_analysis': self._validate_formation_data(player_data),
            'player_performance_validation': self._validate_player_performances(player_data),
            'overall_quality_score': 0.0
        }
        
        # Calculate overall quality score
        quality_components = [
            validation_result['data_completeness']['completeness_score'],
            validation_result['data_quality']['quality_score'],
            validation_result['statistical_consistency']['consistency_score'],
            validation_result['formation_analysis']['formation_quality_score'],
            validation_result['player_performance_validation']['performance_quality_score']
        ]
        
        validation_result['overall_quality_score'] = sum(quality_components) / len(quality_components)
        
        # Update global validation results
        self.validation_results['teams_validated'] += 1
        self.validation_results['seasons_validated'] += 1
        self.validation_results['quality_scores'][f"{team_id}_{season}"] = validation_result['overall_quality_score']
        
        return validation_result
    
    def _load_player_data(self, team_id: int, season: int) -> Optional[Dict[str, Any]]:
        """Load player statistics data for validation."""
        player_file = self.player_data_dir / f"team_{team_id}" / str(season) / f"team_{team_id}_player_match_statistics_{season}.json"
        
        if not player_file.exists():
            logger.warning(f"Player data file not found: {player_file}")
            return None
        
        try:
            with open(player_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading player data: {e}")
            return None
    
    def _validate_data_completeness(self, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data completeness and coverage."""
        match_statistics = player_data.get('match_statistics', [])
        total_matches = len(match_statistics)
        
        # Check match coverage
        matches_with_players = 0
        matches_with_formations = 0
        matches_with_events = 0
        total_players = 0
        
        for match in match_statistics:
            player_performances = match.get('player_performances', [])
            formation_data = match.get('formation_data')
            match_events = match.get('match_events', [])
            
            if player_performances:
                matches_with_players += 1
                total_players += len(player_performances)
            
            if formation_data:
                matches_with_formations += 1
            
            if match_events:
                matches_with_events += 1
        
        # Calculate completeness scores
        player_coverage = matches_with_players / total_matches if total_matches > 0 else 0
        formation_coverage = matches_with_formations / total_matches if total_matches > 0 else 0
        events_coverage = matches_with_events / total_matches if total_matches > 0 else 0
        
        completeness_score = (player_coverage + formation_coverage + events_coverage) / 3
        
        return {
            'completeness_score': completeness_score,
            'total_matches': total_matches,
            'matches_with_players': matches_with_players,
            'matches_with_formations': matches_with_formations,
            'matches_with_events': matches_with_events,
            'total_players': total_players,
            'average_players_per_match': total_players / total_matches if total_matches > 0 else 0,
            'coverage_details': {
                'player_coverage': player_coverage,
                'formation_coverage': formation_coverage,
                'events_coverage': events_coverage
            }
        }
    
    def _validate_data_quality(self, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data quality and detect anomalies."""
        match_statistics = player_data.get('match_statistics', [])
        quality_issues = []
        valid_records = 0
        total_records = 0
        
        for match in match_statistics:
            for player_perf in match.get('player_performances', []):
                total_records += 1
                metrics = player_perf.get('performance_metrics', {})
                
                # Validate individual metrics
                issues = self._validate_player_metrics(metrics, match.get('fixture_id'))
                if not issues:
                    valid_records += 1
                else:
                    quality_issues.extend(issues)
        
        quality_score = valid_records / total_records if total_records > 0 else 0
        
        return {
            'quality_score': quality_score,
            'total_records': total_records,
            'valid_records': valid_records,
            'quality_issues': quality_issues[:10],  # Limit to first 10 issues
            'total_quality_issues': len(quality_issues)
        }
    
    def _validate_player_metrics(self, metrics: Dict[str, Any], fixture_id: int) -> List[str]:
        """Validate individual player performance metrics."""
        issues = []
        
        # Validate minutes played
        minutes = metrics.get('minutes_played', 0)
        if minutes < 0 or minutes > self.validation_thresholds['max_minutes_per_match']:
            issues.append(f"Invalid minutes played: {minutes} (fixture: {fixture_id})")
        
        # Validate rating
        rating = metrics.get('rating')
        if rating is not None:
            if rating < self.validation_thresholds['min_rating'] or rating > self.validation_thresholds['max_rating']:
                issues.append(f"Invalid rating: {rating} (fixture: {fixture_id})")
        
        # Validate pass accuracy
        pass_accuracy = metrics.get('passes', {}).get('accuracy')
        if pass_accuracy is not None:
            if pass_accuracy < self.validation_thresholds['min_pass_accuracy'] or pass_accuracy > self.validation_thresholds['max_pass_accuracy']:
                issues.append(f"Invalid pass accuracy: {pass_accuracy} (fixture: {fixture_id})")
        
        # Validate goals and assists (should be non-negative)
        goals = metrics.get('goals', 0)
        assists = metrics.get('assists', 0)
        if goals < 0:
            issues.append(f"Negative goals: {goals} (fixture: {fixture_id})")
        if assists < 0:
            issues.append(f"Negative assists: {assists} (fixture: {fixture_id})")
        
        # Validate shots
        shots = metrics.get('shots', {})
        shots_total = shots.get('total', 0)
        shots_on_target = shots.get('on_target', 0)
        if shots_on_target > shots_total:
            issues.append(f"Shots on target ({shots_on_target}) > total shots ({shots_total}) (fixture: {fixture_id})")
        
        return issues
    
    def _validate_statistical_consistency(self, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate statistical consistency across matches."""
        match_statistics = player_data.get('match_statistics', [])
        consistency_issues = []
        
        # Track player statistics across matches
        player_stats = defaultdict(list)
        
        for match in match_statistics:
            for player_perf in match.get('player_performances', []):
                player_id = player_perf.get('player_info', {}).get('player_id')
                if player_id:
                    metrics = player_perf.get('performance_metrics', {})
                    player_stats[player_id].append({
                        'fixture_id': match.get('fixture_id'),
                        'minutes': metrics.get('minutes_played', 0),
                        'rating': metrics.get('rating'),
                        'goals': metrics.get('goals', 0),
                        'assists': metrics.get('assists', 0)
                    })
        
        # Check for statistical anomalies
        for player_id, matches in player_stats.items():
            if len(matches) >= 3:  # Only check players with multiple matches
                ratings = [m['rating'] for m in matches if m['rating'] is not None]
                if ratings:
                    rating_std = statistics.stdev(ratings) if len(ratings) > 1 else 0
                    rating_mean = statistics.mean(ratings)
                    
                    # Flag extreme rating variations
                    if rating_std > 2.0:  # High standard deviation
                        consistency_issues.append(f"Player {player_id}: High rating variation (std: {rating_std:.2f})")
                    
                    # Flag unrealistic consistent high ratings
                    if rating_mean > 8.5 and rating_std < 0.3:
                        consistency_issues.append(f"Player {player_id}: Suspiciously consistent high ratings")
        
        consistency_score = max(0, 1 - (len(consistency_issues) / len(player_stats))) if player_stats else 1
        
        return {
            'consistency_score': consistency_score,
            'total_players_analyzed': len(player_stats),
            'consistency_issues': consistency_issues[:10],  # Limit output
            'total_consistency_issues': len(consistency_issues)
        }
    
    def _validate_formation_data(self, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate formation data quality."""
        match_statistics = player_data.get('match_statistics', [])
        formation_issues = []
        valid_formations = 0
        total_formations = 0
        formation_usage = defaultdict(int)
        
        for match in match_statistics:
            formation_data = match.get('formation_data')
            if formation_data:
                total_formations += 1
                formation = formation_data.get('formation')
                starting_eleven = formation_data.get('starting_eleven', [])
                
                # Validate formation
                if formation in self.validation_thresholds['expected_formation_patterns']:
                    if len(starting_eleven) == 11:
                        valid_formations += 1
                        formation_usage[formation] += 1
                    else:
                        formation_issues.append(f"Formation {formation} has {len(starting_eleven)} players (fixture: {match.get('fixture_id')})")
                else:
                    formation_issues.append(f"Unexpected formation: {formation} (fixture: {match.get('fixture_id')})")
        
        formation_quality_score = valid_formations / total_formations if total_formations > 0 else 0
        
        return {
            'formation_quality_score': formation_quality_score,
            'total_formations': total_formations,
            'valid_formations': valid_formations,
            'formation_usage': dict(formation_usage),
            'formation_issues': formation_issues[:10],
            'total_formation_issues': len(formation_issues)
        }
    
    def _validate_player_performances(self, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate overall player performance data quality."""
        match_statistics = player_data.get('match_statistics', [])
        performance_issues = []
        valid_performances = 0
        total_performances = 0
        
        for match in match_statistics:
            player_performances = match.get('player_performances', [])
            
            # Check player count per match
            player_count = len(player_performances)
            if self.validation_thresholds['min_players_per_match'] <= player_count <= self.validation_thresholds['max_players_per_match']:
                valid_performances += 1
            else:
                performance_issues.append(f"Invalid player count: {player_count} (fixture: {match.get('fixture_id')})")
            
            total_performances += 1
            
            # Check for duplicate players in same match
            player_ids = [p.get('player_info', {}).get('player_id') for p in player_performances]
            if len(player_ids) != len(set(player_ids)):
                performance_issues.append(f"Duplicate players in match (fixture: {match.get('fixture_id')})")
        
        performance_quality_score = valid_performances / total_performances if total_performances > 0 else 0
        
        return {
            'performance_quality_score': performance_quality_score,
            'total_matches_analyzed': total_performances,
            'valid_match_performances': valid_performances,
            'performance_issues': performance_issues[:10],
            'total_performance_issues': len(performance_issues)
        }
    
    def generate_comprehensive_validation_report(self, teams: Optional[List[int]] = None, 
                                               seasons: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive validation report for specified teams and seasons.
        
        Args:
            teams: List of team IDs to validate (None for all)
            seasons: List of seasons to validate (None for all)
            
        Returns:
            Comprehensive validation report
        """
        logger.info("Generating comprehensive validation report")
        
        # Discover available data if not specified
        if teams is None or seasons is None:
            available_teams, available_seasons = self._discover_available_data()
            teams = teams or available_teams
            seasons = seasons or available_seasons
        
        # Reset validation results
        self.validation_results = {
            'teams_validated': 0,
            'seasons_validated': 0,
            'matches_validated': 0,
            'players_validated': 0,
            'validation_errors': [],
            'quality_scores': {},
            'completeness_scores': {},
            'consistency_scores': {}
        }
        
        team_season_results = []
        
        # Validate each team-season combination
        for team_id in teams:
            for season in seasons:
                try:
                    result = self.validate_team_season_data(team_id, season)
                    if result.get('status') != 'no_data':
                        team_season_results.append(result)
                except Exception as e:
                    error_msg = f"Validation error for team {team_id} season {season}: {e}"
                    logger.error(error_msg)
                    self.validation_results['validation_errors'].append(error_msg)
        
        # Generate summary statistics
        if team_season_results:
            quality_scores = [r['overall_quality_score'] for r in team_season_results]
            summary_stats = {
                'total_validations': len(team_season_results),
                'average_quality_score': statistics.mean(quality_scores),
                'median_quality_score': statistics.median(quality_scores),
                'min_quality_score': min(quality_scores),
                'max_quality_score': max(quality_scores),
                'quality_score_std': statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0
            }
        else:
            summary_stats = {'total_validations': 0}
        
        # Generate final report
        validation_report = {
            'validation_timestamp': datetime.now().isoformat(),
            'summary_statistics': summary_stats,
            'validation_results': self.validation_results,
            'team_season_results': team_season_results,
            'recommendations': self._generate_recommendations(team_season_results)
        }
        
        # Save report
        report_file = self.player_data_dir / 'player_statistics_validation_report.json'
        with open(report_file, 'w') as f:
            json.dump(validation_report, f, indent=2, default=str)
        
        logger.info(f"Validation report saved to {report_file}")
        return validation_report
    
    def _discover_available_data(self) -> Tuple[List[int], List[int]]:
        """Discover available teams and seasons in the player data directory."""
        teams = []
        seasons = set()
        
        if self.player_data_dir.exists():
            for team_dir in self.player_data_dir.iterdir():
                if team_dir.is_dir() and team_dir.name.startswith('team_'):
                    try:
                        team_id = int(team_dir.name.replace('team_', ''))
                        teams.append(team_id)
                        
                        # Discover seasons for this team
                        for season_dir in team_dir.iterdir():
                            if season_dir.is_dir() and season_dir.name.isdigit():
                                seasons.add(int(season_dir.name))
                    except ValueError:
                        continue
        
        return sorted(teams), sorted(list(seasons))
    
    def _generate_recommendations(self, team_season_results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if not team_season_results:
            recommendations.append("No data available for validation")
            return recommendations
        
        # Analyze quality scores
        quality_scores = [r['overall_quality_score'] for r in team_season_results]
        avg_quality = statistics.mean(quality_scores)
        
        if avg_quality < 0.7:
            recommendations.append("Overall data quality is below acceptable threshold (70%). Consider data collection improvements.")
        
        if avg_quality < 0.5:
            recommendations.append("Data quality is critically low. Immediate attention required.")
        
        # Check for specific issues
        low_quality_teams = [r for r in team_season_results if r['overall_quality_score'] < 0.6]
        if low_quality_teams:
            recommendations.append(f"{len(low_quality_teams)} team-season combinations have quality scores below 60%")
        
        # Formation analysis
        formation_issues = sum(1 for r in team_season_results if r.get('formation_analysis', {}).get('formation_quality_score', 1) < 0.8)
        if formation_issues > 0:
            recommendations.append(f"{formation_issues} team-season combinations have formation data quality issues")
        
        return recommendations

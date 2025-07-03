#!/usr/bin/env python3
"""
Player Statistics Validation and Integration System
Validates collected player data and integrates with Shapley value analysis framework.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import sys

# Add src to path for imports
sys.path.append('src')

class PlayerStatisticsValidator:
    """Validate and integrate player statistics data."""
    
    def __init__(self):
        """Initialize the validator."""
        self.setup_directories()
        self.load_collected_data()
        
        # Validation results
        self.validation_results = {
            'data_quality': {},
            'completeness': {},
            'consistency': {},
            'integration_readiness': {}
        }
        
    def setup_directories(self):
        """Setup directories for validation outputs."""
        self.input_dir = Path('data/focused/players')
        self.output_dir = Path('data/analysis/player_validation')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_collected_data(self):
        """Load all collected player statistics data."""
        print("Loading collected player statistics data...")
        
        self.team_rosters = {}
        self.competition_stats = {}
        self.player_mappings = {}
        
        # Load team rosters
        roster_dir = self.input_dir / 'team_rosters'
        if roster_dir.exists():
            for roster_file in roster_dir.glob('*.json'):
                with open(roster_file, 'r') as f:
                    data = json.load(f)
                    key = f"{data['team_id']}_{data['season']}"
                    self.team_rosters[key] = data
        
        # Load competition statistics
        comp_dir = self.input_dir / 'competition_stats'
        if comp_dir.exists():
            for comp_type_dir in comp_dir.iterdir():
                if comp_type_dir.is_dir():
                    for comp_file in comp_type_dir.glob('*.json'):
                        with open(comp_file, 'r') as f:
                            data = json.load(f)
                            key = f"{data['competition_info']['key']}_{data['competition_info']['season']}"
                            self.competition_stats[key] = data
        
        # Load player mappings
        mapping_file = self.input_dir / 'mappings' / 'player_team_mappings.json'
        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                self.player_mappings = json.load(f)
        
        print(f"Loaded {len(self.team_rosters)} team rosters")
        print(f"Loaded {len(self.competition_stats)} competition datasets")
        print(f"Loaded mappings for {self.player_mappings.get('total_players', 0)} players")
    
    def validate_data_quality(self):
        """Validate the quality of collected player data."""
        print("\nValidating data quality...")
        
        quality_issues = {
            'missing_player_info': [],
            'invalid_statistics': [],
            'inconsistent_data': [],
            'duplicate_entries': []
        }
        
        total_players = 0
        valid_players = 0
        
        # Validate team rosters
        for roster_key, roster_data in self.team_rosters.items():
            players = roster_data.get('players', [])
            total_players += len(players)
            
            for player in players:
                player_info = player.get('player_info', {})
                statistics = player.get('statistics', [])
                
                # Check for missing essential information
                if not player_info.get('id') or not player_info.get('name'):
                    quality_issues['missing_player_info'].append({
                        'roster': roster_key,
                        'player': player_info,
                        'issue': 'Missing ID or name'
                    })
                    continue
                
                # Check for valid statistics
                if not statistics:
                    quality_issues['invalid_statistics'].append({
                        'roster': roster_key,
                        'player_id': player_info.get('id'),
                        'issue': 'No statistics available'
                    })
                    continue
                
                # Validate statistics structure
                valid_stats = True
                for stat in statistics:
                    if not self.validate_statistics_structure(stat):
                        quality_issues['invalid_statistics'].append({
                            'roster': roster_key,
                            'player_id': player_info.get('id'),
                            'issue': 'Invalid statistics structure'
                        })
                        valid_stats = False
                        break
                
                if valid_stats:
                    valid_players += 1
        
        self.validation_results['data_quality'] = {
            'total_players_processed': total_players,
            'valid_players': valid_players,
            'validation_rate': (valid_players / total_players * 100) if total_players > 0 else 0,
            'quality_issues': quality_issues,
            'issues_summary': {
                'missing_info': len(quality_issues['missing_player_info']),
                'invalid_stats': len(quality_issues['invalid_statistics']),
                'inconsistent_data': len(quality_issues['inconsistent_data']),
                'duplicates': len(quality_issues['duplicate_entries'])
            }
        }
        
        print(f"Data quality validation complete:")
        print(f"  Total players: {total_players}")
        print(f"  Valid players: {valid_players}")
        print(f"  Validation rate: {self.validation_results['data_quality']['validation_rate']:.2f}%")
        
        return self.validation_results['data_quality']
    
    def validate_statistics_structure(self, stat):
        """Validate the structure of a player statistics entry."""
        required_fields = ['league_info', 'performance_stats', 'scoring_stats']
        
        for field in required_fields:
            if field not in stat:
                return False
        
        # Check for numeric fields
        performance = stat.get('performance_stats', {})
        numeric_fields = ['appearances', 'minutes']
        
        for field in numeric_fields:
            value = performance.get(field)
            if value is not None and not isinstance(value, (int, float)):
                return False
        
        return True
    
    def validate_completeness(self):
        """Validate completeness of data collection."""
        print("\nValidating data completeness...")
        
        # Load core teams for reference
        with open('data/focused/core_champions_league_teams.json', 'r') as f:
            core_teams_data = json.load(f)
            core_teams = {team['id']: team for team in core_teams_data['teams']}
        
        completeness_report = {
            'teams_coverage': {},
            'seasons_coverage': {},
            'competitions_coverage': {},
            'missing_data': []
        }
        
        # Check team coverage
        teams_with_data = set()
        for roster_key in self.team_rosters.keys():
            team_id = int(roster_key.split('_')[0])
            teams_with_data.add(team_id)
        
        missing_teams = set(core_teams.keys()) - teams_with_data
        
        completeness_report['teams_coverage'] = {
            'total_core_teams': len(core_teams),
            'teams_with_data': len(teams_with_data),
            'coverage_percentage': (len(teams_with_data) / len(core_teams) * 100),
            'missing_teams': [{'id': tid, 'name': core_teams[tid]['name']} for tid in missing_teams]
        }
        
        # Check season coverage
        seasons_found = set()
        for roster_key in self.team_rosters.keys():
            season = int(roster_key.split('_')[1])
            seasons_found.add(season)
        
        expected_seasons = {2019, 2020, 2021, 2022, 2023}
        missing_seasons = expected_seasons - seasons_found
        
        completeness_report['seasons_coverage'] = {
            'expected_seasons': list(expected_seasons),
            'seasons_with_data': list(seasons_found),
            'missing_seasons': list(missing_seasons),
            'coverage_percentage': (len(seasons_found) / len(expected_seasons) * 100)
        }
        
        self.validation_results['completeness'] = completeness_report
        
        print(f"Completeness validation complete:")
        print(f"  Team coverage: {completeness_report['teams_coverage']['coverage_percentage']:.2f}%")
        print(f"  Season coverage: {completeness_report['seasons_coverage']['coverage_percentage']:.2f}%")
        
        return completeness_report
    
    def validate_consistency(self):
        """Validate consistency across different data sources."""
        print("\nValidating data consistency...")
        
        consistency_issues = {
            'player_info_mismatches': [],
            'statistics_inconsistencies': [],
            'mapping_errors': []
        }
        
        # Cross-reference player information across different sources
        player_info_by_id = defaultdict(list)
        
        # Collect player info from all sources
        for roster_data in self.team_rosters.values():
            for player in roster_data.get('players', []):
                player_info = player.get('player_info', {})
                player_id = player_info.get('id')
                if player_id:
                    player_info_by_id[player_id].append(player_info)
        
        # Check for inconsistencies
        for player_id, info_list in player_info_by_id.items():
            if len(info_list) > 1:
                # Check if all entries have consistent information
                base_info = info_list[0]
                for info in info_list[1:]:
                    if info.get('name') != base_info.get('name'):
                        consistency_issues['player_info_mismatches'].append({
                            'player_id': player_id,
                            'issue': 'Name mismatch',
                            'values': [base_info.get('name'), info.get('name')]
                        })
        
        self.validation_results['consistency'] = {
            'total_issues': sum(len(issues) for issues in consistency_issues.values()),
            'issues_by_type': consistency_issues,
            'consistency_score': 100 - (sum(len(issues) for issues in consistency_issues.values()) / len(player_info_by_id) * 100)
        }
        
        print(f"Consistency validation complete:")
        print(f"  Total issues found: {self.validation_results['consistency']['total_issues']}")
        print(f"  Consistency score: {self.validation_results['consistency']['consistency_score']:.2f}%")
        
        return self.validation_results['consistency']
    
    def prepare_shapley_integration(self):
        """Prepare player data for Shapley value analysis integration."""
        print("\nPreparing data for Shapley value integration...")
        
        shapley_ready_data = {
            'players_by_team': {},
            'performance_matrices': {},
            'contribution_metrics': {}
        }
        
        # Organize players by team and season for Shapley analysis
        for roster_key, roster_data in self.team_rosters.items():
            team_id, season = roster_key.split('_')
            
            if team_id not in shapley_ready_data['players_by_team']:
                shapley_ready_data['players_by_team'][team_id] = {}
            
            players_data = []
            for player in roster_data.get('players', []):
                player_metrics = self.extract_shapley_metrics(player)
                if player_metrics:
                    players_data.append(player_metrics)
            
            shapley_ready_data['players_by_team'][team_id][season] = players_data
        
        # Save Shapley-ready data
        shapley_file = self.output_dir / 'shapley_ready_player_data.json'
        with open(shapley_file, 'w') as f:
            json.dump(shapley_ready_data, f, indent=2, default=str)
        
        self.validation_results['integration_readiness'] = {
            'shapley_ready_teams': len(shapley_ready_data['players_by_team']),
            'total_player_records': sum(
                len(seasons.get(season, [])) 
                for seasons in shapley_ready_data['players_by_team'].values()
                for season in seasons.keys()
            ),
            'output_file': str(shapley_file)
        }
        
        print(f"Shapley integration preparation complete:")
        print(f"  Teams prepared: {self.validation_results['integration_readiness']['shapley_ready_teams']}")
        print(f"  Player records: {self.validation_results['integration_readiness']['total_player_records']}")
        
        return shapley_ready_data
    
    def extract_shapley_metrics(self, player_data):
        """Extract metrics suitable for Shapley value calculation."""
        player_info = player_data.get('player_info', {})
        statistics = player_data.get('statistics', [])
        
        if not statistics:
            return None
        
        # Aggregate statistics across all competitions
        total_stats = {
            'appearances': 0,
            'minutes': 0,
            'goals': 0,
            'assists': 0,
            'passes_total': 0,
            'passes_key': 0,
            'tackles': 0,
            'interceptions': 0
        }
        
        for stat in statistics:
            perf_stats = stat.get('performance_stats', {})
            scoring_stats = stat.get('scoring_stats', {})
            passing_stats = stat.get('passing_stats', {})
            defensive_stats = stat.get('defensive_stats', {})
            
            total_stats['appearances'] += perf_stats.get('appearances', 0)
            total_stats['minutes'] += perf_stats.get('minutes', 0)
            total_stats['goals'] += scoring_stats.get('goals_total', 0)
            total_stats['assists'] += scoring_stats.get('assists', 0)
            total_stats['passes_total'] += passing_stats.get('passes_total', 0)
            total_stats['passes_key'] += passing_stats.get('passes_key', 0)
            total_stats['tackles'] += defensive_stats.get('tackles_total', 0)
            total_stats['interceptions'] += defensive_stats.get('tackles_interceptions', 0)
        
        return {
            'player_id': player_info.get('id'),
            'player_name': player_info.get('name'),
            'position': self.determine_primary_position(statistics),
            'metrics': total_stats,
            'normalized_metrics': self.normalize_metrics(total_stats)
        }
    
    def determine_primary_position(self, statistics):
        """Determine player's primary position from statistics."""
        positions = []
        for stat in statistics:
            pos = stat.get('performance_stats', {}).get('position')
            if pos:
                positions.append(pos)
        
        if positions:
            # Return most common position
            return max(set(positions), key=positions.count)
        return 'Unknown'
    
    def normalize_metrics(self, stats):
        """Normalize metrics for Shapley value calculation."""
        minutes = stats.get('minutes', 1)
        if minutes == 0:
            minutes = 1
        
        return {
            'goals_per_90': (stats.get('goals', 0) * 90) / minutes,
            'assists_per_90': (stats.get('assists', 0) * 90) / minutes,
            'key_passes_per_90': (stats.get('passes_key', 0) * 90) / minutes,
            'tackles_per_90': (stats.get('tackles', 0) * 90) / minutes,
            'interceptions_per_90': (stats.get('interceptions', 0) * 90) / minutes
        }
    
    def generate_validation_report(self):
        """Generate comprehensive validation report."""
        print("\nGenerating validation report...")
        
        report = {
            'validation_summary': {
                'timestamp': datetime.now().isoformat(),
                'total_validations': 4,
                'validations_completed': len(self.validation_results)
            },
            'results': self.validation_results,
            'recommendations': self.generate_recommendations()
        }
        
        report_file = self.output_dir / 'player_statistics_validation_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Validation report saved to: {report_file}")
        return report
    
    def generate_recommendations(self):
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Data quality recommendations
        quality = self.validation_results.get('data_quality', {})
        if quality.get('validation_rate', 0) < 95:
            recommendations.append({
                'category': 'data_quality',
                'priority': 'high',
                'recommendation': 'Improve data collection to achieve >95% validation rate',
                'current_rate': quality.get('validation_rate', 0)
            })
        
        # Completeness recommendations
        completeness = self.validation_results.get('completeness', {})
        team_coverage = completeness.get('teams_coverage', {}).get('coverage_percentage', 0)
        if team_coverage < 90:
            recommendations.append({
                'category': 'completeness',
                'priority': 'medium',
                'recommendation': 'Collect data for missing teams to improve coverage',
                'current_coverage': team_coverage
            })
        
        return recommendations

def main():
    """Main execution function."""
    print("PLAYER STATISTICS VALIDATION AND INTEGRATION")
    print("=" * 60)
    
    validator = PlayerStatisticsValidator()
    
    try:
        # Run all validations
        validator.validate_data_quality()
        validator.validate_completeness()
        validator.validate_consistency()
        validator.prepare_shapley_integration()
        
        # Generate final report
        report = validator.generate_validation_report()
        
        print(f"\nValidation completed successfully!")
        print(f"Report saved with {len(report['recommendations'])} recommendations")
        
    except Exception as e:
        print(f"Error during validation: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
"""
Team Statistics Collection Validator
Validates comprehensive team statistics and match details collection
against quality standards and completeness requirements.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Any
from collections import defaultdict

class TeamStatisticsValidator:
    """Validates team statistics collection quality and completeness."""
    
    def __init__(self):
        """Initialize the validator."""
        self.target_seasons = [2019, 2020, 2021, 2022, 2023, 2024]
        self.consistency_target = 99.85
        
        # Paths
        self.roster_dir = Path("data/focused/players/team_rosters")
        self.teams_dir = Path("data/focused/teams")
        self.reports_dir = Path("data/analysis")
        
        # Core teams
        self.core_teams = self._extract_core_teams()
        
        # Validation results
        self.validation_results = {
            'validation_timestamp': datetime.now().isoformat(),
            'target_parameters': {
                'core_teams': len(self.core_teams),
                'target_seasons': self.target_seasons,
                'consistency_target': self.consistency_target
            },
            'file_structure_validation': {},
            'data_quality_validation': {},
            'coverage_validation': {},
            'consistency_validation': {},
            'integration_validation': {},
            'overall_assessment': {}
        }
    
    def _extract_core_teams(self) -> Set[int]:
        """Extract core team IDs from roster files."""
        core_teams = set()
        pattern = re.compile(r'team_(\d+)_players_\d{4}\.json')
        
        if self.roster_dir.exists():
            for roster_file in self.roster_dir.glob("team_*_players_*.json"):
                match = pattern.match(roster_file.name)
                if match:
                    team_id = int(match.group(1))
                    core_teams.add(team_id)
        
        return core_teams
    
    def validate_file_structure(self) -> Dict[str, Any]:
        """Validate the file structure and organization."""
        print("Validating File Structure...")
        
        structure_results = {
            'teams_directory_exists': self.teams_dir.exists(),
            'team_directories_found': 0,
            'season_directories_found': 0,
            'statistics_files_found': 0,
            'correct_naming_convention': 0,
            'structure_issues': []
        }
        
        if not self.teams_dir.exists():
            structure_results['structure_issues'].append("Teams directory does not exist")
            return structure_results
        
        # Check team directories
        for team_dir in self.teams_dir.glob("team_*"):
            team_id_match = re.search(r'team_(\d+)', team_dir.name)
            if team_id_match:
                team_id = int(team_id_match.group(1))
                if team_id in self.core_teams:
                    structure_results['team_directories_found'] += 1
                    
                    # Check season directories
                    for season_dir in team_dir.glob("*"):
                        if season_dir.is_dir() and season_dir.name.isdigit():
                            season = int(season_dir.name)
                            if season in self.target_seasons:
                                structure_results['season_directories_found'] += 1
                                
                                # Check statistics files
                                expected_file = season_dir / f"team_{team_id}_statistics_{season}.json"
                                if expected_file.exists():
                                    structure_results['statistics_files_found'] += 1
                                    structure_results['correct_naming_convention'] += 1
                                else:
                                    structure_results['structure_issues'].append(
                                        f"Missing statistics file: {expected_file}"
                                    )
        
        return structure_results
    
    def validate_data_quality(self) -> Dict[str, Any]:
        """Validate the quality and completeness of team statistics data."""
        print("Validating Data Quality...")
        
        quality_results = {
            'total_files_checked': 0,
            'valid_files': 0,
            'invalid_files': 0,
            'files_with_issues': 0,
            'data_quality_issues': [],
            'required_fields_validation': {},
            'data_type_validation': {},
            'content_validation': {}
        }
        
        required_fields = ['team_id', 'season', 'league_statistics', 'match_details', 'season_summary']
        
        if self.teams_dir.exists():
            for team_dir in self.teams_dir.glob("team_*"):
                team_id_match = re.search(r'team_(\d+)', team_dir.name)
                if team_id_match:
                    team_id = int(team_id_match.group(1))
                    if team_id in self.core_teams:
                        for season_dir in team_dir.glob("*"):
                            if season_dir.is_dir() and season_dir.name.isdigit():
                                season = int(season_dir.name)
                                if season in self.target_seasons:
                                    stats_file = season_dir / f"team_{team_id}_statistics_{season}.json"
                                    
                                    if stats_file.exists():
                                        quality_results['total_files_checked'] += 1
                                        
                                        try:
                                            with open(stats_file, 'r') as f:
                                                team_data = json.load(f)
                                            
                                            file_valid = True
                                            file_issues = []
                                            
                                            # Check required fields
                                            missing_fields = []
                                            for field in required_fields:
                                                if field not in team_data:
                                                    missing_fields.append(field)
                                                    file_valid = False
                                            
                                            if missing_fields:
                                                file_issues.append(f"Missing fields: {missing_fields}")
                                            
                                            # Validate data types and content
                                            if 'team_id' in team_data and team_data['team_id'] != team_id:
                                                file_issues.append("Team ID mismatch")
                                                file_valid = False
                                            
                                            if 'season' in team_data and team_data['season'] != season:
                                                file_issues.append("Season mismatch")
                                                file_valid = False
                                            
                                            if 'league_statistics' in team_data:
                                                if not isinstance(team_data['league_statistics'], dict):
                                                    file_issues.append("League statistics not a dictionary")
                                                    file_valid = False
                                            
                                            if 'match_details' in team_data:
                                                if not isinstance(team_data['match_details'], list):
                                                    file_issues.append("Match details not a list")
                                                    file_valid = False
                                                else:
                                                    # Check match details structure
                                                    for i, match in enumerate(team_data['match_details'][:5]):  # Check first 5
                                                        if not isinstance(match, dict):
                                                            file_issues.append(f"Match {i} not a dictionary")
                                                            file_valid = False
                                                            break
                                            
                                            if 'season_summary' in team_data:
                                                summary = team_data['season_summary']
                                                if not isinstance(summary, dict):
                                                    file_issues.append("Season summary not a dictionary")
                                                    file_valid = False
                                                else:
                                                    # Check summary fields
                                                    summary_fields = ['total_matches', 'total_goals_scored', 'total_goals_conceded']
                                                    for field in summary_fields:
                                                        if field not in summary:
                                                            file_issues.append(f"Missing summary field: {field}")
                                                        elif not isinstance(summary[field], (int, float)):
                                                            file_issues.append(f"Invalid summary field type: {field}")
                                            
                                            if file_valid:
                                                quality_results['valid_files'] += 1
                                            else:
                                                quality_results['invalid_files'] += 1
                                            
                                            if file_issues:
                                                quality_results['files_with_issues'] += 1
                                                quality_results['data_quality_issues'].extend([
                                                    f"{stats_file}: {issue}" for issue in file_issues
                                                ])
                                        
                                        except Exception as e:
                                            quality_results['invalid_files'] += 1
                                            quality_results['data_quality_issues'].append(
                                                f"Error reading {stats_file}: {e}"
                                            )
        
        return quality_results
    
    def validate_coverage(self) -> Dict[str, Any]:
        """Validate team and season coverage."""
        print("Validating Coverage...")
        
        coverage_results = {
            'team_coverage': {},
            'season_coverage': {},
            'competition_coverage': {},
            'match_coverage': {}
        }
        
        team_coverage = {}
        season_coverage = {season: 0 for season in self.target_seasons}
        competition_coverage = defaultdict(int)
        total_matches = 0
        
        if self.teams_dir.exists():
            for team_dir in self.teams_dir.glob("team_*"):
                team_id_match = re.search(r'team_(\d+)', team_dir.name)
                if team_id_match:
                    team_id = int(team_id_match.group(1))
                    if team_id in self.core_teams:
                        team_seasons = []
                        team_matches = 0
                        
                        for season_dir in team_dir.glob("*"):
                            if season_dir.is_dir() and season_dir.name.isdigit():
                                season = int(season_dir.name)
                                if season in self.target_seasons:
                                    stats_file = season_dir / f"team_{team_id}_statistics_{season}.json"
                                    
                                    if stats_file.exists():
                                        try:
                                            with open(stats_file, 'r') as f:
                                                team_data = json.load(f)
                                            
                                            team_seasons.append(season)
                                            season_coverage[season] += 1
                                            
                                            # Count matches and competitions
                                            matches = team_data.get('match_details', [])
                                            team_matches += len(matches)
                                            total_matches += len(matches)
                                            
                                            for match in matches:
                                                comp_name = match.get('league', {}).get('name', 'Unknown')
                                                competition_coverage[comp_name] += 1
                                        
                                        except Exception:
                                            pass  # Already handled in quality validation
                        
                        team_coverage[team_id] = {
                            'seasons': team_seasons,
                            'season_count': len(team_seasons),
                            'matches': team_matches
                        }
        
        coverage_results['team_coverage'] = {
            'teams_with_data': len(team_coverage),
            'total_core_teams': len(self.core_teams),
            'coverage_percentage': (len(team_coverage) / len(self.core_teams)) * 100,
            'complete_teams': len([t for t in team_coverage.values() if t['season_count'] == len(self.target_seasons)]),
            'average_seasons_per_team': sum(t['season_count'] for t in team_coverage.values()) / len(team_coverage) if team_coverage else 0
        }
        
        coverage_results['season_coverage'] = season_coverage
        coverage_results['competition_coverage'] = dict(competition_coverage)
        coverage_results['match_coverage'] = {
            'total_matches': total_matches,
            'average_matches_per_team': total_matches / len(team_coverage) if team_coverage else 0
        }
        
        return coverage_results
    
    def validate_consistency(self) -> Dict[str, Any]:
        """Validate data consistency across the collection."""
        print("Validating Consistency...")
        
        consistency_results = {
            'consistency_percentage': 0.0,
            'meets_target': False,
            'consistency_issues': [],
            'team_id_consistency': True,
            'season_consistency': True,
            'data_format_consistency': True
        }
        
        total_files = 0
        consistent_files = 0
        
        if self.teams_dir.exists():
            for team_dir in self.teams_dir.glob("team_*"):
                team_id_match = re.search(r'team_(\d+)', team_dir.name)
                if team_id_match:
                    team_id = int(team_id_match.group(1))
                    if team_id in self.core_teams:
                        for season_dir in team_dir.glob("*"):
                            if season_dir.is_dir() and season_dir.name.isdigit():
                                season = int(season_dir.name)
                                if season in self.target_seasons:
                                    stats_file = season_dir / f"team_{team_id}_statistics_{season}.json"
                                    
                                    if stats_file.exists():
                                        total_files += 1
                                        
                                        try:
                                            with open(stats_file, 'r') as f:
                                                team_data = json.load(f)
                                            
                                            file_consistent = True
                                            
                                            # Check team ID consistency
                                            if team_data.get('team_id') != team_id:
                                                consistency_results['consistency_issues'].append(
                                                    f"Team ID mismatch in {stats_file}"
                                                )
                                                consistency_results['team_id_consistency'] = False
                                                file_consistent = False
                                            
                                            # Check season consistency
                                            if team_data.get('season') != season:
                                                consistency_results['consistency_issues'].append(
                                                    f"Season mismatch in {stats_file}"
                                                )
                                                consistency_results['season_consistency'] = False
                                                file_consistent = False
                                            
                                            # Check data format consistency
                                            required_structure = {
                                                'league_statistics': dict,
                                                'match_details': list,
                                                'season_summary': dict
                                            }
                                            
                                            for field, expected_type in required_structure.items():
                                                if field in team_data and not isinstance(team_data[field], expected_type):
                                                    consistency_results['consistency_issues'].append(
                                                        f"Data format inconsistency in {stats_file}: {field}"
                                                    )
                                                    consistency_results['data_format_consistency'] = False
                                                    file_consistent = False
                                            
                                            if file_consistent:
                                                consistent_files += 1
                                        
                                        except Exception as e:
                                            consistency_results['consistency_issues'].append(
                                                f"Error reading {stats_file}: {e}"
                                            )
        
        if total_files > 0:
            consistency_results['consistency_percentage'] = (consistent_files / total_files) * 100
            consistency_results['meets_target'] = consistency_results['consistency_percentage'] >= self.consistency_target
        
        return consistency_results
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of team statistics collection."""
        print("Running Comprehensive Team Statistics Validation")
        print("=" * 60)
        
        # Run individual validations
        self.validation_results['file_structure_validation'] = self.validate_file_structure()
        self.validation_results['data_quality_validation'] = self.validate_data_quality()
        self.validation_results['coverage_validation'] = self.validate_coverage()
        self.validation_results['consistency_validation'] = self.validate_consistency()
        
        # Calculate overall assessment
        structure_score = 1 if self.validation_results['file_structure_validation']['teams_directory_exists'] else 0
        quality_score = 1 if self.validation_results['data_quality_validation']['valid_files'] > 0 else 0
        coverage_score = 1 if self.validation_results['coverage_validation']['team_coverage']['coverage_percentage'] >= 80 else 0
        consistency_score = 1 if self.validation_results['consistency_validation']['meets_target'] else 0
        
        total_score = structure_score + quality_score + coverage_score + consistency_score
        
        self.validation_results['overall_assessment'] = {
            'structure_score': structure_score,
            'quality_score': quality_score,
            'coverage_score': coverage_score,
            'consistency_score': consistency_score,
            'total_score': total_score,
            'max_score': 4,
            'overall_percentage': (total_score / 4) * 100,
            'validation_passed': total_score >= 3  # 75% threshold
        }
        
        return self.validation_results
    
    def generate_validation_report(self, results: Dict[str, Any]) -> None:
        """Generate and save validation report."""
        print(f"\n{'='*60}")
        print("TEAM STATISTICS VALIDATION REPORT")
        print(f"{'='*60}")
        
        # Overall assessment
        overall = results['overall_assessment']
        print(f"Overall Score: {overall['total_score']}/{overall['max_score']} ({overall['overall_percentage']:.1f}%)")
        print(f"Validation Status: {'✓ PASSED' if overall['validation_passed'] else '✗ FAILED'}")
        
        # File structure
        structure = results['file_structure_validation']
        print(f"\nFile Structure:")
        print(f"  Teams directory: {'✓' if structure['teams_directory_exists'] else '✗'}")
        print(f"  Team directories: {structure['team_directories_found']}")
        print(f"  Statistics files: {structure['statistics_files_found']}")
        
        # Data quality
        quality = results['data_quality_validation']
        print(f"\nData Quality:")
        print(f"  Files checked: {quality['total_files_checked']}")
        print(f"  Valid files: {quality['valid_files']}")
        print(f"  Invalid files: {quality['invalid_files']}")
        
        # Coverage
        coverage = results['coverage_validation']
        team_cov = coverage['team_coverage']
        print(f"\nCoverage:")
        print(f"  Team coverage: {team_cov['teams_with_data']}/{team_cov['total_core_teams']} ({team_cov['coverage_percentage']:.1f}%)")
        print(f"  Complete teams: {team_cov['complete_teams']}")
        print(f"  Total matches: {coverage['match_coverage']['total_matches']}")
        
        # Consistency
        consistency = results['consistency_validation']
        print(f"\nConsistency:")
        print(f"  Consistency: {consistency['consistency_percentage']:.2f}%")
        print(f"  Meets target: {'✓' if consistency['meets_target'] else '✗'}")
        
        # Save detailed report
        report_path = self.reports_dir / "team_statistics_validation_report.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nDetailed validation report saved to: {report_path}")

def main():
    """Main validation function."""
    validator = TeamStatisticsValidator()
    results = validator.run_comprehensive_validation()
    validator.generate_validation_report(results)

if __name__ == "__main__":
    main()

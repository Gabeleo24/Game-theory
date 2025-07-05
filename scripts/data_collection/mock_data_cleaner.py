#!/usr/bin/env python3
"""
Mock Data Cleaner for ADS599 Capstone Project

This script identifies and removes mock data files from the team statistics collection,
ensuring only authentic API data remains.

Mock data patterns:
- Identical statistics (38 games, 25 wins, 8 draws, 5 losses, 75 goals for, 25 against)
- Mock team names ("Team XXX" instead of real names)
- Old timestamps (before API fix)
- Empty logo URLs or generic patterns
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Any
import argparse

class MockDataCleaner:
    def __init__(self, data_dir: str = "data/focused/teams"):
        self.data_dir = Path(data_dir)
        self.mock_patterns = {
            # Classic mock data patterns
            'fixtures_total': 38,
            'wins_total': 25,
            'draws_total': 8,
            'losses_total': 5,
            'goals_for_total': 75,
            'goals_against_total': 25
        }
        self.cutoff_timestamp = "2025-07-03T21:00:00"  # Before our API fix
        self.mock_files = []
        self.real_files = []
        self.scan_results = {
            'total_files': 0,
            'mock_files': 0,
            'real_files': 0,
            'mock_patterns_found': {},
            'teams_with_mock_data': set(),
            'seasons_with_mock_data': set()
        }

    def scan_for_mock_data(self) -> Dict[str, Any]:
        """Scan all team statistics files to identify mock data."""
        print("🔍 Scanning for mock data patterns...")
        
        if not self.data_dir.exists():
            print(f"❌ Data directory not found: {self.data_dir}")
            return self.scan_results
        
        # Scan all team directories
        for team_dir in self.data_dir.iterdir():
            if not team_dir.is_dir() or not team_dir.name.startswith('team_'):
                continue
                
            team_id = team_dir.name.replace('team_', '')
            
            # Scan all season directories
            for season_dir in team_dir.iterdir():
                if not season_dir.is_dir():
                    continue
                    
                season = season_dir.name
                
                # Check statistics file
                stats_file = season_dir / f"team_{team_id}_statistics_{season}.json"
                if stats_file.exists():
                    self.scan_results['total_files'] += 1
                    
                    if self._is_mock_data(stats_file, team_id, season):
                        self.mock_files.append(stats_file)
                        self.scan_results['mock_files'] += 1
                        self.scan_results['teams_with_mock_data'].add(team_id)
                        self.scan_results['seasons_with_mock_data'].add(season)
                    else:
                        self.real_files.append(stats_file)
                        self.scan_results['real_files'] += 1
        
        return self.scan_results

    def _is_mock_data(self, file_path: Path, team_id: str, season: str) -> bool:
        """Check if a file contains mock data patterns."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check timestamp (files before API fix are likely mock)
            timestamp = data.get('collection_timestamp', '')
            if timestamp and timestamp < self.cutoff_timestamp:
                self._record_mock_pattern('old_timestamp', file_path)
                return True
            
            # Check for mock team names
            league_stats = data.get('league_statistics', {})
            for league_id, league_data in league_stats.items():
                team_info = league_data.get('team_info', {})
                team_name = team_info.get('name', '')
                
                if team_name.startswith(f'Team {team_id}'):
                    self._record_mock_pattern('mock_team_name', file_path)
                    return True
                
                # Check for empty or missing logo
                logo = team_info.get('logo', '')
                if not logo or logo == '':
                    self._record_mock_pattern('empty_logo', file_path)
                    return True
            
            # Check for classic mock statistics patterns
            season_summary = data.get('season_summary', {})
            if self._has_mock_statistics(season_summary):
                self._record_mock_pattern('mock_statistics', file_path)
                return True
            
            # Check league statistics for mock patterns
            for league_id, league_data in league_stats.items():
                fixtures = league_data.get('fixtures', {})
                if self._has_mock_fixtures(fixtures):
                    self._record_mock_pattern('mock_fixtures', file_path)
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
            return False

    def _has_mock_statistics(self, season_summary: Dict) -> bool:
        """Check if season summary has mock statistics patterns."""
        if not season_summary:
            return False
            
        # Check for exact mock values
        total_matches = season_summary.get('total_matches', 0)
        total_wins = season_summary.get('total_wins', 0)
        total_draws = season_summary.get('total_draws', 0)
        total_losses = season_summary.get('total_losses', 0)
        total_goals_scored = season_summary.get('total_goals_scored', 0)
        total_goals_conceded = season_summary.get('total_goals_conceded', 0)
        
        # Classic mock pattern
        if (total_matches == 38 and total_wins == 25 and total_draws == 8 and 
            total_losses == 5 and total_goals_scored == 75 and total_goals_conceded == 25):
            return True
            
        return False

    def _has_mock_fixtures(self, fixtures: Dict) -> bool:
        """Check if fixtures data has mock patterns."""
        if not fixtures:
            return False
            
        played = fixtures.get('played', {})
        wins = fixtures.get('wins', {})
        draws = fixtures.get('draws', {})
        losses = fixtures.get('loses', {})  # Note: API uses 'loses' not 'losses'
        
        # Check for exact mock values
        if (played.get('total') == 38 and wins.get('total') == 25 and 
            draws.get('total') == 8 and losses.get('total') == 5):
            return True
            
        return False

    def _record_mock_pattern(self, pattern_type: str, file_path: Path):
        """Record a mock pattern found."""
        if pattern_type not in self.scan_results['mock_patterns_found']:
            self.scan_results['mock_patterns_found'][pattern_type] = []
        self.scan_results['mock_patterns_found'][pattern_type].append(str(file_path))

    def delete_mock_files(self, dry_run: bool = True) -> Dict[str, Any]:
        """Delete identified mock data files."""
        if not self.mock_files:
            print("✅ No mock files to delete!")
            return {'deleted': 0, 'errors': []}
        
        results = {'deleted': 0, 'errors': []}
        
        if dry_run:
            print(f"🔍 DRY RUN: Would delete {len(self.mock_files)} mock files:")
            for file_path in self.mock_files:
                print(f"  - {file_path}")
            return results
        
        print(f"🗑️  Deleting {len(self.mock_files)} mock files...")
        
        for file_path in self.mock_files:
            try:
                file_path.unlink()
                results['deleted'] += 1
                print(f"  ✓ Deleted: {file_path}")
                
                # Also delete empty directories
                parent_dir = file_path.parent
                if parent_dir.exists() and not any(parent_dir.iterdir()):
                    parent_dir.rmdir()
                    print(f"  ✓ Removed empty directory: {parent_dir}")
                    
            except Exception as e:
                error_msg = f"Error deleting {file_path}: {e}"
                results['errors'].append(error_msg)
                print(f"  ❌ {error_msg}")
        
        return results

    def generate_report(self) -> None:
        """Generate a comprehensive report of the scan results."""
        print("\n" + "="*70)
        print("MOCK DATA SCAN REPORT")
        print("="*70)
        
        print(f"📊 Total files scanned: {self.scan_results['total_files']}")
        print(f"🎭 Mock files found: {self.scan_results['mock_files']}")
        print(f"✅ Real files found: {self.scan_results['real_files']}")
        
        if self.scan_results['mock_files'] > 0:
            print(f"\n🎭 Mock Data Patterns Found:")
            for pattern, files in self.scan_results['mock_patterns_found'].items():
                print(f"  - {pattern}: {len(files)} files")
            
            print(f"\n📋 Teams with mock data: {len(self.scan_results['teams_with_mock_data'])}")
            teams_list = sorted(list(self.scan_results['teams_with_mock_data']))
            print(f"  {', '.join(teams_list[:10])}" + ("..." if len(teams_list) > 10 else ""))
            
            print(f"\n📅 Seasons with mock data: {sorted(list(self.scan_results['seasons_with_mock_data']))}")
        else:
            print("\n🎉 No mock data found! All files contain authentic API data.")

def main():
    parser = argparse.ArgumentParser(description='Clean mock data from team statistics')
    parser.add_argument('--data-dir', default='data/focused/teams', 
                       help='Directory containing team statistics')
    parser.add_argument('--delete', action='store_true', 
                       help='Actually delete mock files (default: dry run)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose output')
    
    args = parser.parse_args()
    
    cleaner = MockDataCleaner(args.data_dir)
    
    # Scan for mock data
    scan_results = cleaner.scan_for_mock_data()
    
    # Generate report
    cleaner.generate_report()
    
    # Delete mock files if requested
    if scan_results['mock_files'] > 0:
        delete_results = cleaner.delete_mock_files(dry_run=not args.delete)
        
        if args.delete:
            print(f"\n🗑️  Deletion Results:")
            print(f"  ✓ Files deleted: {delete_results['deleted']}")
            if delete_results['errors']:
                print(f"  ❌ Errors: {len(delete_results['errors'])}")
                for error in delete_results['errors']:
                    print(f"    - {error}")

if __name__ == "__main__":
    main()

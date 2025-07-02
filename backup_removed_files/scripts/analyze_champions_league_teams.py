#!/usr/bin/env python3
"""
Champions League Team Analysis Script
Analyzes the current Champions League dataset to identify the core 32 group stage teams
and create a focused dataset structure for ADS599 Capstone requirements.
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict
import sys
import os

# Add src to path for imports
sys.path.append('src')

class ChampionsLeagueAnalyzer:
    """Analyzer for Champions League team data and structure."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.data_dir = Path('data/processed')
        self.cl_teams_by_year = {}
        self.cl_standings_by_year = {}
        self.core_32_teams = set()
        self.team_info = {}
        
    def load_champions_league_data(self):
        """Load Champions League data from all available years."""
        print("Loading Champions League data...")
        
        # Load team data for each year
        for year in [2019, 2020, 2021, 2022, 2023]:
            teams_file = self.data_dir / f'champions_league_teams_{year}_expanded.json'
            standings_file = self.data_dir / f'champions_league_standings_{year}_expanded.json'
            
            if teams_file.exists():
                with open(teams_file, 'r') as f:
                    self.cl_teams_by_year[year] = json.load(f)
                print(f"   Loaded {len(self.cl_teams_by_year[year])} teams for {year}")
            
            if standings_file.exists():
                with open(standings_file, 'r') as f:
                    self.cl_standings_by_year[year] = json.load(f)
                print(f"   Loaded standings data for {year}")
    
    def identify_group_stage_teams(self):
        """Identify teams that reached the group stage (core 32 teams)."""
        print("\nIdentifying group stage teams...")

        group_stage_teams = defaultdict(int)

        for year, standings_data in self.cl_standings_by_year.items():
            print(f"\nAnalyzing {year} group stage:")

            if not standings_data:
                continue

            # Extract teams from group stage standings
            for league_data in standings_data:
                if 'league' in league_data and 'standings' in league_data:
                    standings = league_data['league']['standings']

                    for group in standings:
                        for team_standing in group:
                            if 'team' in team_standing:
                                team = team_standing['team']
                                team_id = team['id']
                                team_name = team['name']

                                # Only count teams in actual groups (not qualifying)
                                group_name = team_standing.get('group', '')
                                if 'Group' in str(group_name) and group_name != '':
                                    group_stage_teams[team_id] += 1
                                    self.team_info[team_id] = {
                                        'name': team_name,
                                        'logo': team.get('logo', ''),
                                        'appearances': group_stage_teams[team_id]
                                    }
                                    print(f"   {team_name} (ID: {team_id}) - Group: {group_name}")

        # Identify core teams (appeared in group stage at least once)
        self.core_32_teams = set(group_stage_teams.keys())
        print(f"\nIdentified {len(self.core_32_teams)} unique teams that reached group stage")

        return group_stage_teams
    
    def map_teams_to_domestic_leagues(self):
        """Map Champions League teams to their domestic leagues."""
        print("\nMapping teams to domestic leagues...")
        
        # Known league mappings based on team countries/names
        league_mappings = {
            # Premier League (England)
            39: {
                'name': 'Premier League',
                'country': 'England',
                'teams': []
            },
            # La Liga (Spain)
            140: {
                'name': 'La Liga',
                'country': 'Spain',
                'teams': []
            },
            # Serie A (Italy)
            135: {
                'name': 'Serie A',
                'country': 'Italy',
                'teams': []
            },
            # Bundesliga (Germany)
            78: {
                'name': 'Bundesliga',
                'country': 'Germany',
                'teams': []
            },
            # Ligue 1 (France)
            61: {
                'name': 'Ligue 1',
                'country': 'France',
                'teams': []
            }
        }
        
        # Load domestic league data to map teams
        for league_id, league_info in league_mappings.items():
            for year in [2021, 2022, 2023]:
                league_name = league_info['name'].lower().replace(' ', '_')
                teams_file = self.data_dir / f'{league_name}_teams_{year}_expanded.json'
                
                if teams_file.exists():
                    with open(teams_file, 'r') as f:
                        domestic_teams = json.load(f)
                    
                    for team_data in domestic_teams:
                        team = team_data.get('team', {})
                        team_id = team.get('id')
                        
                        if team_id in self.core_32_teams:
                            if team_id not in league_info['teams']:
                                league_info['teams'].append(team_id)
                                print(f"   {team.get('name')} (ID: {team_id}) -> {league_info['name']}")
        
        return league_mappings
    
    def analyze_dataset_coverage(self):
        """Analyze current dataset coverage for the core 32 teams."""
        print("\nAnalyzing dataset coverage for core 32 teams...")
        
        coverage_report = {
            'champions_league': 0,
            'domestic_leagues': 0,
            'other_competitions': 0,
            'total_files': 0
        }
        
        # Count files related to core teams
        for file_path in self.data_dir.glob('*.json'):
            file_name = file_path.name
            
            if 'champions_league' in file_name:
                coverage_report['champions_league'] += 1
            elif any(league in file_name for league in ['la_liga', 'premier_league', 'serie_a', 'bundesliga', 'ligue_1']):
                coverage_report['domestic_leagues'] += 1
            elif any(comp in file_name for comp in ['europa_league', 'copa_del_rey', 'fa_cup', 'coppa_italia', 'dfb_pokal']):
                coverage_report['other_competitions'] += 1
            
            coverage_report['total_files'] += 1
        
        print(f"   Champions League files: {coverage_report['champions_league']}")
        print(f"   Domestic league files: {coverage_report['domestic_leagues']}")
        print(f"   Other competition files: {coverage_report['other_competitions']}")
        print(f"   Total files: {coverage_report['total_files']}")
        
        return coverage_report
    
    def generate_core_teams_list(self):
        """Generate a comprehensive list of the core 32 Champions League teams."""
        print("\nGenerating core 32 teams list...")
        
        core_teams_data = []
        
        for team_id in self.core_32_teams:
            if team_id in self.team_info:
                team_data = self.team_info[team_id].copy()
                team_data['id'] = team_id
                core_teams_data.append(team_data)
        
        # Sort by appearances (most frequent first)
        core_teams_data.sort(key=lambda x: x['appearances'], reverse=True)
        
        # Save to file
        output_file = self.data_dir / 'core_32_champions_league_teams.json'
        with open(output_file, 'w') as f:
            json.dump(core_teams_data, f, indent=2)
        
        print(f"   Saved core teams list to {output_file}")
        print(f"   Total core teams identified: {len(core_teams_data)}")
        
        return core_teams_data
    
    def create_analysis_report(self):
        """Create a comprehensive analysis report."""
        print("\nCreating analysis report...")
        
        group_stage_teams = self.identify_group_stage_teams()
        league_mappings = self.map_teams_to_domestic_leagues()
        coverage_report = self.analyze_dataset_coverage()
        core_teams_data = self.generate_core_teams_list()
        
        report = {
            'analysis_summary': {
                'total_unique_teams': len(self.core_32_teams),
                'years_analyzed': list(self.cl_standings_by_year.keys()),
                'dataset_files_analyzed': coverage_report['total_files']
            },
            'core_teams': core_teams_data,
            'league_distribution': league_mappings,
            'dataset_coverage': coverage_report,
            'recommendations': [
                "Focus data collection on the identified core teams",
                "Maintain multi-competition context for these teams",
                "Prioritize Champions League, domestic league, and major cup data",
                "Filter existing dataset to reduce noise from non-core teams"
            ]
        }
        
        # Save report
        report_file = self.data_dir / 'champions_league_analysis_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"   Analysis report saved to {report_file}")
        
        return report

def main():
    """Main execution function."""
    print("CHAMPIONS LEAGUE TEAM ANALYSIS")
    print("=" * 60)
    
    analyzer = ChampionsLeagueAnalyzer()
    
    try:
        # Load data
        analyzer.load_champions_league_data()
        
        # Create comprehensive analysis
        report = analyzer.create_analysis_report()
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print(f"Core teams identified: {report['analysis_summary']['total_unique_teams']}")
        print(f"Years analyzed: {', '.join(map(str, report['analysis_summary']['years_analyzed']))}")
        print(f"Dataset files: {report['analysis_summary']['dataset_files_analyzed']}")
        
        print("\nTop 10 most frequent Champions League teams:")
        for i, team in enumerate(report['core_teams'][:10], 1):
            print(f"   {i:2d}. {team['name']} (ID: {team['id']}) - {team['appearances']} appearances")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

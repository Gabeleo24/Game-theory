#!/usr/bin/env python3
"""
Champions League Team Filter
Creates a focused dataset containing only the core Champions League teams
and their data across all competitions they participate in.
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict, Counter
import sys
import os

# Add src to path for imports
sys.path.append('src')

class ChampionsLeagueTeamFilter:
    """Filter to identify and extract core Champions League teams."""
    
    def __init__(self):
        """Initialize the filter."""
        self.data_dir = Path('data/processed')
        self.output_dir = Path('data/focused')
        self.output_dir.mkdir(exist_ok=True)
        
        self.core_teams = {}
        self.team_league_mapping = {}
        self.filtered_files = []
        
    def extract_champions_league_teams(self):
        """Extract all teams that participated in Champions League group stages."""
        print("Extracting Champions League teams from group stages...")
        
        teams_by_frequency = Counter()
        team_details = {}
        
        # Process multiple years to get comprehensive list
        for year in [2019, 2020, 2021, 2022, 2023]:
            standings_file = self.data_dir / f'champions_league_standings_{year}_expanded.json'
            
            if not standings_file.exists():
                print(f"   Warning: {standings_file} not found")
                continue
                
            print(f"   Processing {year}...")
            
            with open(standings_file, 'r') as f:
                standings_data = json.load(f)
            
            year_teams = 0
            for league_data in standings_data:
                if 'league' in league_data and 'standings' in league_data['league']:
                    standings = league_data['league']['standings']
                    
                    for group in standings:
                        for team_standing in group:
                            if 'team' in team_standing and 'group' in team_standing:
                                team = team_standing['team']
                                group_name = team_standing['group']
                                
                                # Only include actual group stage teams
                                if 'Group' in str(group_name):
                                    team_id = team['id']
                                    teams_by_frequency[team_id] += 1
                                    team_details[team_id] = {
                                        'id': team_id,
                                        'name': team['name'],
                                        'logo': team.get('logo', ''),
                                        'latest_year': year
                                    }
                                    year_teams += 1
            
            print(f"      Found {year_teams} team entries for {year}")
        
        # Sort teams by frequency (most appearances first)
        sorted_teams = teams_by_frequency.most_common()
        
        print(f"\nTotal unique teams found: {len(sorted_teams)}")
        print("Top 20 most frequent Champions League teams:")
        
        for i, (team_id, appearances) in enumerate(sorted_teams[:20], 1):
            team_name = team_details[team_id]['name']
            print(f"   {i:2d}. {team_name} (ID: {team_id}) - {appearances} appearances")
        
        # Store core teams (all teams that made group stage)
        self.core_teams = {team_id: team_details[team_id] for team_id, _ in sorted_teams}
        
        # Save core teams list
        core_teams_file = self.output_dir / 'core_champions_league_teams.json'
        with open(core_teams_file, 'w') as f:
            json.dump({
                'total_teams': len(self.core_teams),
                'teams': list(self.core_teams.values()),
                'frequency_data': dict(teams_by_frequency)
            }, f, indent=2)
        
        print(f"\nCore teams saved to: {core_teams_file}")
        return self.core_teams
    
    def map_teams_to_domestic_leagues(self):
        """Map Champions League teams to their domestic leagues."""
        print("\nMapping teams to domestic leagues...")
        
        league_configs = {
            'premier_league': {'id': 39, 'name': 'Premier League', 'country': 'England'},
            'la_liga': {'id': 140, 'name': 'La Liga', 'country': 'Spain'},
            'serie_a': {'id': 135, 'name': 'Serie A', 'country': 'Italy'},
            'bundesliga': {'id': 78, 'name': 'Bundesliga', 'country': 'Germany'},
            'ligue_1': {'id': 61, 'name': 'Ligue 1', 'country': 'France'}
        }
        
        team_league_mapping = {}
        
        for league_key, league_info in league_configs.items():
            print(f"   Checking {league_info['name']}...")
            
            # Check multiple years to ensure comprehensive mapping
            for year in [2021, 2022, 2023]:
                teams_file = self.data_dir / f'{league_key}_teams_{year}_expanded.json'
                
                if teams_file.exists():
                    with open(teams_file, 'r') as f:
                        domestic_teams = json.load(f)
                    
                    for team_data in domestic_teams:
                        team = team_data.get('team', {})
                        team_id = team.get('id')
                        
                        if team_id in self.core_teams:
                            team_league_mapping[team_id] = {
                                'league_id': league_info['id'],
                                'league_name': league_info['name'],
                                'country': league_info['country'],
                                'team_name': team.get('name', ''),
                                'team_id': team_id
                            }
                            print(f"      {team.get('name')} -> {league_info['name']}")
        
        self.team_league_mapping = team_league_mapping
        
        # Save mapping
        mapping_file = self.output_dir / 'team_league_mapping.json'
        with open(mapping_file, 'w') as f:
            json.dump(team_league_mapping, f, indent=2)
        
        print(f"\nTeam-league mapping saved to: {mapping_file}")
        print(f"Mapped {len(team_league_mapping)} teams to domestic leagues")
        
        return team_league_mapping
    
    def filter_dataset_files(self):
        """Filter existing dataset files to include only core Champions League teams."""
        print("\nFiltering dataset files for core Champions League teams...")
        
        core_team_ids = set(self.core_teams.keys())
        filtered_count = 0
        
        # Process all JSON files in the data directory
        for file_path in self.data_dir.glob('*.json'):
            if file_path.name.startswith('core_') or file_path.name.startswith('champions_league_analysis'):
                continue  # Skip our own output files
                
            print(f"   Processing {file_path.name}...")
            
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                filtered_data = self._filter_data_by_teams(data, core_team_ids)
                
                if filtered_data:
                    # Save filtered data
                    output_file = self.output_dir / f'focused_{file_path.name}'
                    with open(output_file, 'w') as f:
                        json.dump(filtered_data, f, indent=2)
                    
                    self.filtered_files.append({
                        'original': file_path.name,
                        'filtered': output_file.name,
                        'original_size': len(data) if isinstance(data, list) else 1,
                        'filtered_size': len(filtered_data) if isinstance(filtered_data, list) else 1
                    })
                    filtered_count += 1
                    
            except Exception as e:
                print(f"      Error processing {file_path.name}: {e}")
        
        print(f"\nFiltered {filtered_count} files")
        return self.filtered_files
    
    def _filter_data_by_teams(self, data, core_team_ids):
        """Filter data structure to include only core teams."""
        if isinstance(data, list):
            filtered_items = []
            for item in data:
                if self._contains_core_team(item, core_team_ids):
                    filtered_items.append(item)
            return filtered_items
        elif isinstance(data, dict):
            if self._contains_core_team(data, core_team_ids):
                return data
        
        return None
    
    def _contains_core_team(self, item, core_team_ids):
        """Check if a data item contains a core team."""
        if isinstance(item, dict):
            # Check for team ID in various possible locations
            team_id = None
            
            # Direct team reference
            if 'team' in item and isinstance(item['team'], dict):
                team_id = item['team'].get('id')
            
            # Team ID directly in item
            elif 'id' in item:
                team_id = item['id']
            
            # Home/away team references
            elif 'teams' in item:
                teams = item['teams']
                if isinstance(teams, dict):
                    home_id = teams.get('home', {}).get('id') if isinstance(teams.get('home'), dict) else None
                    away_id = teams.get('away', {}).get('id') if isinstance(teams.get('away'), dict) else None
                    return (home_id in core_team_ids) or (away_id in core_team_ids)
            
            # Standings data
            elif 'standings' in item:
                # This is likely a league standings structure
                return True  # Keep all standings data as it may contain our teams
            
            return team_id in core_team_ids if team_id else False
        
        return False
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        print("\nGenerating summary report...")
        
        # Count teams by league
        league_distribution = defaultdict(list)
        for team_id, mapping in self.team_league_mapping.items():
            league_name = mapping['league_name']
            team_name = mapping['team_name']
            league_distribution[league_name].append(team_name)
        
        # Create comprehensive report
        report = {
            'summary': {
                'total_core_teams': len(self.core_teams),
                'teams_mapped_to_leagues': len(self.team_league_mapping),
                'filtered_files': len(self.filtered_files),
                'analysis_date': pd.Timestamp.now().isoformat()
            },
            'league_distribution': dict(league_distribution),
            'core_teams_list': list(self.core_teams.values()),
            'filtered_files_summary': self.filtered_files,
            'recommendations': [
                f"Focus analysis on {len(self.core_teams)} core Champions League teams",
                "Use filtered dataset files from data/focused/ directory",
                "Maintain multi-competition context for comprehensive analysis",
                "Prioritize teams with multiple Champions League appearances"
            ]
        }
        
        # Save report
        report_file = self.output_dir / 'champions_league_focus_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Summary report saved to: {report_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("CHAMPIONS LEAGUE FOCUS SUMMARY")
        print("="*60)
        print(f"Core teams identified: {report['summary']['total_core_teams']}")
        print(f"Teams mapped to major leagues: {report['summary']['teams_mapped_to_leagues']}")
        print(f"Dataset files filtered: {report['summary']['filtered_files']}")
        
        print("\nLeague Distribution:")
        for league, teams in league_distribution.items():
            print(f"   {league}: {len(teams)} teams")
            for team in sorted(teams)[:5]:  # Show first 5 teams
                print(f"      - {team}")
            if len(teams) > 5:
                print(f"      ... and {len(teams) - 5} more")
        
        return report

def main():
    """Main execution function."""
    print("CHAMPIONS LEAGUE TEAM FILTER")
    print("=" * 60)
    
    filter_system = ChampionsLeagueTeamFilter()
    
    try:
        # Extract core teams
        core_teams = filter_system.extract_champions_league_teams()
        
        # Map to domestic leagues
        team_mapping = filter_system.map_teams_to_domestic_leagues()
        
        # Filter dataset files
        filtered_files = filter_system.filter_dataset_files()
        
        # Generate summary report
        report = filter_system.generate_summary_report()
        
        print("\nFILTERING COMPLETE - Focused dataset ready for analysis")
        
    except Exception as e:
        print(f"Error during filtering: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

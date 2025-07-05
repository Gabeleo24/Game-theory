#!/usr/bin/env python3
"""
Single Team Collection Script
Collect all games and statistics for a specific team across all seasons 2019-2024
"""

import sys
import argparse
from pathlib import Path

# Add the comprehensive collector
sys.path.append('scripts/data_collection')
from comprehensive_team_statistics_collector import ComprehensiveTeamStatisticsCollector

def collect_single_team(team_id: int, seasons: list = None):
    """
    Collect all data for a specific team across specified seasons.
    
    Args:
        team_id: The specific team ID to collect
        seasons: List of seasons (default: 2019-2024)
    """
    if seasons is None:
        seasons = [2019, 2020, 2021, 2022, 2023, 2024]
    
    print(f"Collecting all games and statistics for Team {team_id}")
    print(f"Seasons: {seasons}")
    print("=" * 60)
    
    # Initialize collector
    collector = ComprehensiveTeamStatisticsCollector(target_seasons=seasons)
    
    # Override core teams to only include the target team
    collector.core_teams = {team_id}
    collector.collection_stats['core_teams_count'] = 1
    
    # Run collection for this specific team
    results = collector.collect_comprehensive_team_statistics(max_teams=1)
    
    # Generate report
    collector.generate_collection_report(results)
    
    # Show collected data summary
    print(f"\n{'='*60}")
    print(f"COLLECTION SUMMARY FOR TEAM {team_id}")
    print(f"{'='*60}")
    
    team_dir = Path(f"data/focused/teams/team_{team_id}")
    if team_dir.exists():
        total_matches = 0
        for season in seasons:
            season_file = team_dir / str(season) / f"team_{team_id}_statistics_{season}.json"
            if season_file.exists():
                import json
                with open(season_file, 'r') as f:
                    data = json.load(f)
                matches = len(data.get('match_details', []))
                total_matches += matches
                print(f"Season {season}: {matches} matches collected")
        
        print(f"\nTotal matches collected: {total_matches}")
        print(f"Data location: {team_dir}")
    else:
        print("No data collected - check for errors above")

def main():
    parser = argparse.ArgumentParser(description='Collect all games for a specific team')
    parser.add_argument('team_id', type=int, help='Team ID to collect data for')
    parser.add_argument('--seasons', nargs='+', type=int, 
                       default=[2019, 2020, 2021, 2022, 2023, 2024],
                       help='Seasons to collect (default: 2019-2024)')
    
    args = parser.parse_args()
    
    collect_single_team(args.team_id, args.seasons)

if __name__ == "__main__":
    main()

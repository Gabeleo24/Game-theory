#!/usr/bin/env python3
"""
2024-2025 Player Data Collection Script

This script extends the existing player statistics collection system to gather
team roster data for 2024 and 2025 seasons for all teams in the capstone project.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the existing player statistics collector
try:
    from scripts.data_collection.player_statistics_collector import PlayerStatisticsCollector
except ImportError:
    print("Error: Could not import PlayerStatisticsCollector")
    print("Make sure the player statistics collector is available")
    sys.exit(1)

def main():
    """Main execution function for collecting 2024-2025 player data"""
    print("Extended Player Data Collection for 2024-2025 Seasons")
    print("=" * 60)
    print("This script will collect player statistics for 2024 and 2025 seasons")
    print("for all teams in the capstone project.")
    print()

    # Define the seasons we want to collect
    target_seasons = [2024, 2025]

    print(f"Target seasons: {target_seasons}")
    print(f"Estimated API requests: 67 teams × {len(target_seasons)} seasons = {67 * len(target_seasons)} requests")
    print()

    # Ask for confirmation
    response = input("Do you want to proceed with the data collection? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("Collection cancelled.")
        return 0

    try:
        # Initialize the collector
        print("\nInitializing PlayerStatisticsCollector...")
        collector = PlayerStatisticsCollector()
        print(f"Collector initialized with {len(collector.core_teams)} core teams")

        # Start collection
        start_time = datetime.now()
        print(f"\nStarting collection at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Collect players for 2024 and 2025 seasons
        total_players = collector.collect_all_team_players(seasons=target_seasons)

        # Save mappings and generate reports
        mapping_data = collector.save_player_team_mappings()
        api_report = collector.save_api_usage_report()

        # Calculate duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Print final results
        print(f"\n{'='*60}")
        print("EXTENDED COLLECTION COMPLETED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"Collection duration: {duration:.2f} seconds")
        print(f"Seasons processed: {target_seasons}")
        print(f"Total players collected: {total_players}")
        print(f"Unique players: {mapping_data['total_players']}")
        print(f"API requests used: {api_report['collection_session']['total_requests']}")
        print(f"API requests remaining: {api_report['collection_session']['remaining_requests']}")
        print(f"Usage percentage: {api_report['collection_session']['usage_percentage']:.2f}%")
        print()
        print("✓ Team roster files for 2024 and 2025 have been created!")
        print("✓ You can now run the individual player statistics extraction script")
        print("  to generate individual player files for 2024 and 2025 seasons.")

        return 0

    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\nError during collection: {e}")
        print("Please check your API configuration and try again.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
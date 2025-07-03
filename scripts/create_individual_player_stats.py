#!/usr/bin/env python3
"""
Individual Player Statistics Generator

This script processes team roster files and creates individual player statistics files
organized by team and season. Each player gets their own comprehensive statistics file
containing performance metrics across all competitions.

Directory Structure:
data/focused/players/individual_stats/
├── team_{team_id}/
│   ├── {season}/
│   │   ├── player_{player_id}_{player_name_slug}_{season}.json
│   │   └── ...
│   └── ...
└── ...

File Structure:
{
  "player_info": {...},
  "team_context": {...},
  "season_summary": {...},
  "competition_stats": [...],
  "aggregated_stats": {...},
  "metadata": {...}
}
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PlayerStatsExtractor:
    def __init__(self, base_path: str = "data/focused/players"):
        self.base_path = Path(base_path)
        self.team_rosters_path = self.base_path / "team_rosters"
        self.individual_stats_path = self.base_path / "individual_stats"

        # Create individual stats directory if it doesn't exist
        self.individual_stats_path.mkdir(parents=True, exist_ok=True)

    def slugify_name(self, name: str) -> str:
        """Convert player name to URL-friendly slug"""
        # Remove special characters and replace spaces with underscores
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '_', slug)
        return slug.strip('_')

    def calculate_aggregated_stats(self, statistics: List[Dict]) -> Dict[str, Any]:
        """Calculate aggregated statistics across all competitions"""
        aggregated = {
            "total_appearances": 0,
            "total_lineups": 0,
            "total_minutes": 0,
            "total_goals": 0,
            "total_assists": 0,
            "total_yellow_cards": 0,
            "total_red_cards": 0,
            "competitions_played": len(statistics),
            "average_rating": None,
            "goals_per_90": 0,
            "assists_per_90": 0,
            "minutes_per_appearance": 0
        }

        total_rating_sum = 0
        rating_count = 0

        for stat in statistics:
            perf = stat.get("performance_stats", {})
            scoring = stat.get("scoring_stats", {})
            discipline = stat.get("discipline_stats", {})

            # Aggregate basic stats
            aggregated["total_appearances"] += perf.get("appearances", 0) or 0
            aggregated["total_lineups"] += perf.get("lineups", 0) or 0
            aggregated["total_minutes"] += perf.get("minutes", 0) or 0
            aggregated["total_goals"] += scoring.get("goals_total", 0) or 0
            aggregated["total_assists"] += scoring.get("assists", 0) or 0
            aggregated["total_yellow_cards"] += discipline.get("cards_yellow", 0) or 0
            aggregated["total_red_cards"] += discipline.get("cards_red", 0) or 0

            # Handle rating calculation
            rating = perf.get("rating")
            if rating and rating != "null":
                try:
                    rating_val = float(rating)
                    total_rating_sum += rating_val
                    rating_count += 1
                except (ValueError, TypeError):
                    pass

        # Calculate derived stats
        if rating_count > 0:
            aggregated["average_rating"] = round(total_rating_sum / rating_count, 2)

        if aggregated["total_minutes"] > 0:
            aggregated["goals_per_90"] = round((aggregated["total_goals"] * 90) / aggregated["total_minutes"], 2)
            aggregated["assists_per_90"] = round((aggregated["total_assists"] * 90) / aggregated["total_minutes"], 2)

        if aggregated["total_appearances"] > 0:
            aggregated["minutes_per_appearance"] = round(aggregated["total_minutes"] / aggregated["total_appearances"], 1)

        return aggregated

    def create_season_summary(self, player_data: Dict, aggregated_stats: Dict) -> Dict[str, Any]:
        """Create a season summary for the player"""
        return {
            "season": player_data["team_info"]["season"],
            "team_id": player_data["team_info"]["team_id"],
            "team_name": player_data["team_info"]["team_name"],
            "primary_position": self.get_primary_position(player_data["statistics"]),
            "total_competitions": len(player_data["statistics"]),
            "key_metrics": {
                "appearances": aggregated_stats["total_appearances"],
                "goals": aggregated_stats["total_goals"],
                "assists": aggregated_stats["total_assists"],
                "minutes": aggregated_stats["total_minutes"],
                "average_rating": aggregated_stats["average_rating"]
            }
        }

    def get_primary_position(self, statistics: List[Dict]) -> str:
        """Determine the player's primary position based on most appearances"""
        position_counts = {}

        for stat in statistics:
            position = stat.get("performance_stats", {}).get("position")
            appearances = stat.get("performance_stats", {}).get("appearances", 0) or 0

            if position and appearances > 0:
                if position not in position_counts:
                    position_counts[position] = 0
                position_counts[position] += appearances

        if position_counts:
            return max(position_counts, key=position_counts.get)
        return "Unknown"

    def process_team_roster_file(self, file_path: Path) -> None:
        """Process a single team roster file and extract individual player stats"""
        logger.info(f"Processing {file_path.name}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                roster_data = json.load(f)

            team_id = roster_data["team_id"]
            team_name = roster_data["team_name"]
            season = roster_data["season"]

            # Create team directory
            team_dir = self.individual_stats_path / f"team_{team_id}"
            team_dir.mkdir(exist_ok=True)

            # Create season directory
            season_dir = team_dir / str(season)
            season_dir.mkdir(exist_ok=True)

            # Process each player
            for player_data in roster_data["players"]:
                self.create_individual_player_file(player_data, season_dir, team_name)

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

    def create_individual_player_file(self, player_data: Dict, season_dir: Path, team_name: str) -> None:
        """Create an individual player statistics file"""
        player_info = player_data["player_info"]
        player_id = player_info["id"]
        player_name = player_info["name"]
        season = player_data["team_info"]["season"]

        # Create filename
        name_slug = self.slugify_name(player_name)
        filename = f"player_{player_id}_{name_slug}_{season}.json"
        file_path = season_dir / filename

        # Calculate aggregated statistics
        aggregated_stats = self.calculate_aggregated_stats(player_data["statistics"])

        # Create individual player statistics structure
        individual_stats = {
            "player_info": player_info,
            "team_context": {
                "team_id": player_data["team_info"]["team_id"],
                "team_name": player_data["team_info"]["team_name"],
                "season": season
            },
            "season_summary": self.create_season_summary(player_data, aggregated_stats),
            "competition_stats": player_data["statistics"],
            "aggregated_stats": aggregated_stats,
            "metadata": {
                "file_created": datetime.now().isoformat(),
                "source_file": f"team_{player_data['team_info']['team_id']}_players_{season}.json",
                "data_structure_version": "1.0"
            }
        }

        # Write the file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(individual_stats, f, indent=2, ensure_ascii=False)
            logger.info(f"Created: {filename}")
        except Exception as e:
            logger.error(f"Error creating file for {player_name}: {e}")

    def process_all_team_rosters(self, seasons_filter=None) -> None:
        """Process all team roster files and create individual player statistics"""
        logger.info("Starting individual player statistics extraction...")

        roster_files = list(self.team_rosters_path.glob("team_*_players_*.json"))

        if not roster_files:
            logger.warning("No team roster files found!")
            return

        # Filter by seasons if specified
        if seasons_filter:
            filtered_files = []
            for file_path in roster_files:
                # Extract season from filename (e.g., team_33_players_2024.json -> 2024)
                filename = file_path.name
                try:
                    season = int(filename.split('_')[-1].split('.')[0])
                    if season in seasons_filter:
                        filtered_files.append(file_path)
                except (ValueError, IndexError):
                    logger.warning(f"Could not extract season from filename: {filename}")
                    continue
            roster_files = filtered_files
            logger.info(f"Filtered to {len(roster_files)} files for seasons: {seasons_filter}")

        logger.info(f"Found {len(roster_files)} team roster files to process")

        processed_count = 0
        for file_path in sorted(roster_files):
            self.process_team_roster_file(file_path)
            processed_count += 1

        logger.info(f"Completed processing {processed_count} team roster files")
        self.generate_summary_report()

    def generate_summary_report(self) -> None:
        """Generate a summary report of the extraction process"""
        logger.info("Generating summary report...")

        total_teams = len(list(self.individual_stats_path.glob("team_*")))
        total_files = len(list(self.individual_stats_path.glob("team_*/*/player_*.json")))

        summary = {
            "extraction_completed": datetime.now().isoformat(),
            "total_teams_processed": total_teams,
            "total_player_files_created": total_files,
            "directory_structure": str(self.individual_stats_path),
            "file_naming_convention": "player_{player_id}_{player_name_slug}_{season}.json"
        }

        summary_path = self.individual_stats_path / "extraction_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"Summary report saved to: {summary_path}")
        logger.info(f"Total teams: {total_teams}, Total player files: {total_files}")

def main():
    """Main execution function"""
    # Check if specific seasons were requested
    seasons_filter = None
    if len(sys.argv) > 1:
        try:
            seasons_filter = [int(season) for season in sys.argv[1:]]
            print(f"Processing only seasons: {seasons_filter}")
        except ValueError:
            print("Error: Season arguments must be integers (e.g., 2024 2025)")
            sys.exit(1)

    extractor = PlayerStatsExtractor()
    extractor.process_all_team_rosters(seasons_filter=seasons_filter)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Individual Player Statistics Validation Script

This script validates the generated individual player statistics files
to ensure data integrity and completeness.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StatsValidator:
    def __init__(self, stats_path: str = "data/focused/players/individual_stats"):
        self.stats_path = Path(stats_path)
        self.validation_results = {
            "total_files_checked": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "errors": []
        }

    def validate_file_structure(self, file_path: Path) -> bool:
        """Validate the structure of an individual player statistics file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check required top-level keys
            required_keys = ["player_info", "team_context", "season_summary",
                           "competition_stats", "aggregated_stats", "metadata"]

            for key in required_keys:
                if key not in data:
                    self.validation_results["errors"].append(f"{file_path}: Missing key '{key}'")
                    return False

            # Validate player_info structure
            player_info = data["player_info"]
            if "id" not in player_info or "name" not in player_info:
                self.validation_results["errors"].append(f"{file_path}: Invalid player_info structure")
                return False

            # Validate aggregated_stats
            aggregated = data["aggregated_stats"]
            required_agg_keys = ["total_appearances", "total_goals", "total_assists",
                               "total_minutes", "competitions_played"]

            for key in required_agg_keys:
                if key not in aggregated:
                    self.validation_results["errors"].append(f"{file_path}: Missing aggregated stat '{key}'")
                    return False

            # Validate that competition_stats is a list
            if not isinstance(data["competition_stats"], list):
                self.validation_results["errors"].append(f"{file_path}: competition_stats must be a list")
                return False

            return True

        except json.JSONDecodeError as e:
            self.validation_results["errors"].append(f"{file_path}: JSON decode error - {e}")
            return False
        except Exception as e:
            self.validation_results["errors"].append(f"{file_path}: Validation error - {e}")
            return False

    def validate_all_files(self) -> Dict[str, Any]:
        """Validate all individual player statistics files"""
        logger.info("Starting validation of individual player statistics files...")

        player_files = list(self.stats_path.glob("team_*/*/player_*.json"))

        if not player_files:
            logger.warning("No player statistics files found!")
            return self.validation_results

        logger.info(f"Found {len(player_files)} player files to validate")

        for file_path in player_files:
            self.validation_results["total_files_checked"] += 1

            if self.validate_file_structure(file_path):
                self.validation_results["valid_files"] += 1
            else:
                self.validation_results["invalid_files"] += 1

        # Generate summary
        logger.info(f"Validation completed:")
        logger.info(f"  Total files checked: {self.validation_results['total_files_checked']}")
        logger.info(f"  Valid files: {self.validation_results['valid_files']}")
        logger.info(f"  Invalid files: {self.validation_results['invalid_files']}")

        if self.validation_results["errors"]:
            logger.warning(f"Found {len(self.validation_results['errors'])} errors:")
            for error in self.validation_results["errors"][:10]:  # Show first 10 errors
                logger.warning(f"  {error}")
            if len(self.validation_results["errors"]) > 10:
                logger.warning(f"  ... and {len(self.validation_results['errors']) - 10} more errors")

        return self.validation_results

def main():
    """Main execution function"""
    validator = StatsValidator()
    results = validator.validate_all_files()

    # Save validation results
    results_path = Path("data/focused/players/individual_stats/validation_results.json")
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info(f"Validation results saved to: {results_path}")

    # Return exit code based on validation results
    if results["invalid_files"] > 0:
        exit(1)
    else:
        logger.info("All files passed validation!")
        exit(0)

if __name__ == "__main__":
    main()
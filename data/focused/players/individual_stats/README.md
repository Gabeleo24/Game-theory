# Individual Player Statistics

This directory contains individual player statistics files extracted from team roster data. Each player has their own comprehensive statistics file organized by team and season.

## Directory Structure

```
individual_stats/
├── team_{team_id}/
│   ├── {season}/
│   │   ├── player_{player_id}_{player_name_slug}_{season}.json
│   │   └── ...
│   └── ...
└── extraction_summary.json
```

## File Structure

Each individual player statistics file contains:

```json
{
  "player_info": {
    "id": 882,
    "name": "David de Gea",
    "firstname": "David",
    "lastname": "de Gea Quintana",
    "age": 35,
    "birth": {
      "date": "1990-11-07",
      "place": "Madrid",
      "country": "Spain"
    },
    "nationality": "Spain",
    "height": "192 cm",
    "weight": "76 kg",
    "injured": false,
    "photo": "https://media.api-sports.io/football/players/882.png"
  },
  "team_context": {
    "team_id": 33,
    "team_name": "Manchester United",
    "season": 2019
  },
  "season_summary": {
    "season": 2019,
    "team_id": 33,
    "team_name": "Manchester United",
    "primary_position": "Goalkeeper",
    "total_competitions": 6,
    "key_metrics": {
      "appearances": 47,
      "goals": 0,
      "assists": 0,
      "minutes": 4128,
      "average_rating": 6.85
    }
  },
  "competition_stats": [
    {
      "league_info": {
        "id": 39,
        "name": "Premier League",
        "country": "England",
        "season": 2019
      },
      "team_info": {
        "id": 33,
        "name": "Manchester United"
      },
      "performance_stats": {
        "appearances": 38,
        "lineups": 38,
        "minutes": 3420,
        "position": "Goalkeeper",
        "rating": "6.878947",
        "captain": false
      },
      "scoring_stats": {
        "goals_total": 0,
        "goals_conceded": 36,
        "assists": null,
        "saves": 96
      },
      "passing_stats": {
        "passes_total": 786,
        "passes_key": null,
        "passes_accuracy": null
      },
      "defensive_stats": {
        "tackles_total": null,
        "tackles_blocks": null,
        "tackles_interceptions": null
      },
      "duel_stats": {
        "duels_total": 13,
        "duels_won": 13
      },
      "dribbling_stats": {
        "dribbles_attempts": null,
        "dribbles_success": null,
        "dribbles_past": null
      },
      "discipline_stats": {
        "fouls_drawn": 6,
        "fouls_committed": null,
        "cards_yellow": 2,
        "cards_yellowred": 0,
        "cards_red": 0
      },
      "penalty_stats": {
        "penalty_won": null,
        "penalty_committed": null,
        "penalty_scored": 0,
        "penalty_missed": 0,
        "penalty_saved": 3
      },
      "shooting_stats": {
        "shots_total": null,
        "shots_on": null
      }
    }
  ],
  "aggregated_stats": {
    "total_appearances": 47,
    "total_lineups": 46,
    "total_minutes": 4128,
    "total_goals": 0,
    "total_assists": 0,
    "total_yellow_cards": 2,
    "total_red_cards": 0,
    "competitions_played": 6,
    "average_rating": 6.85,
    "goals_per_90": 0.0,
    "assists_per_90": 0.0,
    "minutes_per_appearance": 87.8
  },
  "metadata": {
    "file_created": "2025-07-03T12:00:00.000000",
    "source_file": "team_33_players_2019.json",
    "data_structure_version": "1.0"
  }
}
```

## Key Features

- **Comprehensive Statistics**: Includes all performance metrics across different competitions
- **Aggregated Data**: Season totals and calculated metrics like goals per 90 minutes
- **Competition Breakdown**: Detailed stats for each competition the player participated in
- **Metadata**: File creation info and source tracking
- **Consistent Naming**: Standardized file naming convention for easy identification

## Usage

Individual player files can be used for:
- Player performance analysis
- Cross-competition comparison
- Season-by-season tracking
- Integration with analysis frameworks
- Machine learning model inputs

## Generation

To generate individual player statistics files, run:

```bash
# Generate for all available seasons
python scripts/create_individual_player_stats.py

# Generate for specific seasons only (e.g., 2024 and 2025)
python scripts/create_individual_player_stats.py 2024 2025
```

This will process team roster files and create individual player statistics organized by team and season.

## Extending to 2024-2025 Seasons

To collect and generate individual player statistics for 2024 and 2025 seasons:

1. **Update Configuration**: The configuration has been updated to include 2024 and 2025 seasons
2. **Collect Team Roster Data**: Run the data collection script to gather 2024-2025 data:
   ```bash
   python scripts/collect_2024_2025_player_data.py
   ```
3. **Generate Individual Stats**: After collection, generate individual player files:
   ```bash
   python scripts/create_individual_player_stats.py 2024 2025
   ```

**Note**: Data collection requires API access and will use your API quota. The system will collect data for all 67 teams across both seasons (approximately 134 API requests).
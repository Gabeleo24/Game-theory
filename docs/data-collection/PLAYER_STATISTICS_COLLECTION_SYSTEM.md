# Player Statistics Collection System

## Overview

The Player Statistics Collection System is a comprehensive framework designed to collect, validate, and integrate detailed player statistics for all players from the 67 core Champions League teams identified in our focused dataset. The system collects data across all competitions (Champions League, domestic leagues, Europa League, domestic cups) for the 2019-2023 period.

## System Architecture

### Core Components

1. **Player Statistics Collector** (`player_statistics_collector.py`)
   - Main collection engine for team-based player statistics
   - Handles API integration with rate limiting
   - Processes and structures player data
   - Creates player-team mappings and transfer analysis

2. **Competition-Specific Collector** (`competition_specific_collector.py`)
   - Specialized collection for different competition types
   - Organizes data by European competitions, domestic leagues, and cups
   - Calculates competition-specific performance metrics

3. **Player Statistics Validator** (`player_statistics_validator.py`)
   - Validates data quality, completeness, and consistency
   - Prepares data for Shapley value analysis integration
   - Generates comprehensive validation reports

4. **Comprehensive Collection Orchestrator** (`comprehensive_player_collection.py`)
   - Main execution script that coordinates all collection phases
   - Supports multiple collection modes
   - Generates final reports and summaries

## Data Collection Scope

### Teams Covered
- **67 Core Champions League Teams** from the focused dataset
- Teams that participated in Champions League group stages (2019-2023)
- Multi-competition context maintained for comprehensive analysis

### Competitions Included
- **UEFA Champions League** (Priority 1)
- **UEFA Europa League** (Priority 2)
- **Domestic Leagues**: Premier League, La Liga, Serie A, Bundesliga, Ligue 1
- **Domestic Cups**: FA Cup, Copa del Rey, Coppa Italia, DFB Pokal

### Time Period
- **Primary Collection**: 2019-2023 (5 seasons)
- **Competition-Specific**: 2022-2023 (recent detailed data)

## Statistical Categories Collected

### Basic Performance Metrics
- Appearances, lineups, minutes played
- Position, rating, captain status

### Scoring Statistics
- Goals (total, conceded), assists, saves

### Passing Statistics
- Total passes, key passes, pass accuracy

### Defensive Statistics
- Tackles (total, blocks, interceptions)

### Advanced Metrics
- Duels (total, won)
- Dribbles (attempts, success, past)
- Discipline (fouls, cards)
- Penalties (won, committed, scored, missed, saved)
- Shooting (total shots, shots on target)

## Data Structure

### Directory Organization
```
data/focused/players/
├── team_rosters/           # Team-based player lists by season
├── individual_stats/       # Individual player statistics
├── competition_stats/      # Competition-specific data
│   ├── european/          # Champions League, Europa League
│   ├── domestic_league/   # Premier League, La Liga, etc.
│   └── domestic_cup/      # FA Cup, Copa del Rey, etc.
├── season_stats/          # Season-by-season aggregations
└── mappings/              # Player-team mappings and transfers
```

### File Naming Conventions
- Team rosters: `team_{team_id}_players_{season}.json`
- Competition stats: `{competition_key}_players_{season}.json`
- Player mappings: `player_team_mappings.json`
- Transfer analysis: `player_transfers.json`

## Usage Instructions

### Basic Collection
```bash
# Full collection (all phases)
python scripts/data_collection/comprehensive_player_collection.py --mode full

# Basic player collection only
python scripts/data_collection/comprehensive_player_collection.py --mode basic_only

# Competition-specific collection only
python scripts/data_collection/comprehensive_player_collection.py --mode competition_only

# Validation only (requires existing data)
python scripts/data_collection/comprehensive_player_collection.py --mode validation_only
```

### Custom Seasons
```bash
# Specify seasons for basic collection
python scripts/data_collection/comprehensive_player_collection.py --seasons 2021 2022 2023

# Specify seasons for competition collection
python scripts/data_collection/comprehensive_player_collection.py --comp-seasons 2023
```

### Individual Components
```bash
# Run basic player collection
python scripts/data_collection/player_statistics_collector.py

# Run competition-specific collection
python scripts/data_collection/competition_specific_collector.py

# Run validation
python scripts/analysis/player_statistics_validator.py
```

## Configuration

### API Configuration
- Configure API keys in `config/api_keys.yaml`
- Rate limiting: 60 requests/minute, 75,000 daily limit
- Error handling with automatic retries

### Collection Settings
- Modify `config/player_collection_config.yaml` for:
  - Seasons to collect
  - Competition priorities
  - Quality control thresholds
  - Output formatting options

## Data Quality and Validation

### Quality Metrics
- **Validation Rate**: Percentage of players with complete, valid data
- **Completeness Score**: Coverage of core teams and seasons
- **Consistency Score**: Data consistency across sources

### Validation Thresholds
- Minimum validation rate: 95%
- Minimum completeness rate: 90%
- Minimum consistency score: 95%

### Quality Assurance Features
- Automatic data structure validation
- Duplicate detection and removal
- Cross-reference consistency checks
- Missing data identification and reporting

## Integration with Shapley Value Analysis

### Prepared Metrics
The system prepares player data specifically for Shapley value calculation:

- **Normalized per-90-minute statistics**
- **Position-specific metric weights**
- **Team contribution matrices**
- **Multi-competition performance aggregation**

### Output Format
```json
{
  "player_id": 12345,
  "player_name": "Player Name",
  "position": "Midfielder",
  "metrics": {
    "goals_per_90": 0.25,
    "assists_per_90": 0.15,
    "key_passes_per_90": 2.1,
    "tackles_per_90": 1.8
  },
  "team_contributions": {
    "offensive": 0.65,
    "defensive": 0.35
  }
}
```

## Performance Optimization

### Rate Limiting
- Intelligent request spacing to avoid API limits
- Automatic retry with exponential backoff
- Request tracking and usage monitoring

### Memory Management
- Batch processing for large datasets
- Periodic cache clearing
- Efficient JSON serialization

### Error Recovery
- Graceful handling of API failures
- Partial collection recovery
- Detailed error logging and reporting

## Output Reports

### Collection Summary
- Total players collected
- API requests used
- Collection duration
- Success rates by phase

### Validation Report
- Data quality scores
- Completeness analysis
- Consistency findings
- Integration readiness assessment

### Transfer Analysis
- Players with multiple team associations
- Transfer patterns between core teams
- Career progression tracking

## Expected Results

### Data Volume
- **Estimated Players**: 2,000-3,000 unique players
- **Total Player Records**: 8,000-12,000 (across seasons/teams)
- **API Requests**: 2,000-5,000 (depending on collection scope)

### File Sizes
- Team rosters: 50-200 KB per file
- Competition stats: 100-500 KB per file
- Total dataset: 50-100 MB

## Troubleshooting

### Common Issues
1. **API Rate Limits**: System automatically handles with delays
2. **Missing Data**: Validation report identifies gaps
3. **Memory Issues**: Reduce batch sizes in configuration
4. **Network Errors**: Automatic retry with exponential backoff

### Log Files
- Main log: `logs/player_collection/main.log`
- API requests: `logs/player_collection/api_requests.log`
- Errors: `logs/player_collection/errors.log`

## Integration Points

### Existing Systems
- **Champions League Team Filter**: Uses core teams list
- **Shapley Value Analysis**: Prepared data format
- **Multi-Competition Framework**: Maintains competition context

### Future Extensions
- Real-time data updates
- Additional statistical categories
- Machine learning feature preparation
- Performance prediction models

## Technical Requirements

### Dependencies
- Python 3.8+
- requests
- pandas
- numpy
- pyyaml
- pathlib

### System Resources
- Memory: 2-4 GB recommended
- Storage: 500 MB for complete dataset
- Network: Stable internet connection for API access

## Maintenance

### Regular Updates
- Seasonal data collection (annually)
- API key rotation (as needed)
- Configuration updates for new competitions
- Validation threshold adjustments

### Data Backup
- Automatic backup creation
- 30-day retention policy
- Compressed storage options
- Recovery procedures documented

## Quick Start Example

### Minimal Collection Example
```python
from scripts.data_collection.player_statistics_collector import PlayerStatisticsCollector

# Initialize collector
collector = PlayerStatisticsCollector()

# Collect players for a specific team and season
players = collector.collect_team_players(team_id=50, season=2023)  # Manchester City 2023

# Save mappings
mapping_data = collector.save_player_team_mappings()

print(f"Collected {len(players)} players for Manchester City 2023")
```

### Full System Example
```python
from scripts.data_collection.comprehensive_player_collection import ComprehensivePlayerCollectionSystem

# Initialize comprehensive system
system = ComprehensivePlayerCollectionSystem(collection_mode='full')

# Run complete collection
results = system.run_comprehensive_collection()

print(f"Collection completed with {results['summary']['success_rate']:.2f}% success rate")
```

This comprehensive player statistics collection system provides the foundation for advanced soccer analytics research, enabling detailed player performance analysis and team composition optimization through the integration with Shapley value methodologies.

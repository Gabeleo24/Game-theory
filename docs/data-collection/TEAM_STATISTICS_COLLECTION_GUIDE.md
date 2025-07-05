# Comprehensive Team Statistics Collection Guide

This guide provides instructions for collecting comprehensive team statistics and match details for all 67 UEFA Champions League teams across seasons 2019-2024, complementing the existing player statistics for complete Shapley value analysis.

## Overview

The team statistics collection system gathers:
- **Team-level statistics** for each season (goals, wins/draws/losses, league positions)
- **Individual match details** for all games (results, scores, competition types)
- **Multi-competition coverage** (Champions League, domestic leagues, cups)
- **Advanced match statistics** (possession, shots, cards when available)

## Data Requirements

### Team-Level Statistics (Per Season)
- **Performance Metrics**: Goals scored/conceded, wins/draws/losses
- **League Information**: Final position, total points earned
- **Competition Coverage**: Champions League, domestic league, domestic cups
- **Additional Stats**: Clean sheets, cards, penalty statistics

### Individual Match Details
- **Match Information**: Results, scores, dates, venues
- **Competition Context**: League/cup type, round information
- **Team Perspective**: Home/away designation, opponent details
- **Advanced Statistics**: Possession, shots, cards (when available)

### Data Organization
- **Structure**: Organized by team ID and season (similar to player statistics)
- **Format**: JSON files compatible with existing analysis scripts
- **Naming**: `team_{team_id}_statistics_{season}.json`
- **Location**: `data/focused/teams/team_{team_id}/{season}/`

## Quick Start

### 1. Validate Prerequisites
```bash
# Ensure core teams are identified
python scripts/data_collection/comprehensive_team_statistics_collector.py --validate-only

# Check existing data structure
python scripts/analysis/team_statistics_validator.py
```

### 2. Run Team Statistics Collection

#### Full Collection (All 67 Teams, 2019-2024)
```bash
# Complete collection for all teams and seasons
python scripts/data_collection/comprehensive_team_statistics_collector.py

# With specific seasons
python scripts/data_collection/comprehensive_team_statistics_collector.py --seasons 2022 2023 2024
```

#### Test Collection (Limited Scope)
```bash
# Test with first 5 teams
python scripts/data_collection/comprehensive_team_statistics_collector.py --max-teams 5

# Test with specific seasons and limited teams
python scripts/data_collection/comprehensive_team_statistics_collector.py --max-teams 3 --seasons 2023 2024
```

### 3. Monitor Collection Progress
The collector provides real-time updates:
- Teams processed and remaining
- Seasons completed per team
- API requests used and cache efficiency
- Match details collected
- Error tracking and handling

### 4. Validate Collection Quality
```bash
# Comprehensive validation
python scripts/analysis/team_statistics_validator.py

# Check specific aspects
python scripts/data_collection/comprehensive_team_statistics_collector.py --validate-only
```

## Configuration

### Collection Configuration
File: `config/team_statistics_collection_config.yaml`

Key settings:
```yaml
collection_scope:
  teams:
    source: "data/focused/players/team_rosters/"
    core_teams_only: true
    expected_count: 67
  seasons:
    target_seasons: [2019, 2020, 2021, 2022, 2023, 2024]

api_efficiency:
  rate_limiting:
    requests_per_minute: 100
    delay_between_requests: 0.6
    delay_between_teams: 2.0
  caching:
    enabled: true
    cache_expiry_days: 30
```

### Competition Coverage
The system automatically collects data from:

**Primary Competitions**:
- UEFA Champions League
- Premier League, La Liga, Serie A, Bundesliga, Ligue 1

**Secondary Competitions**:
- UEFA Europa League
- FA Cup, Copa del Rey, Coppa Italia, DFB Pokal, Coupe de France

## Data Structure

### Team Statistics File Structure
```json
{
  "team_id": 541,
  "season": 2024,
  "collection_timestamp": "2024-01-15T10:30:00",
  "league_statistics": {
    "2": {
      "league_id": 2,
      "league_name": "UEFA Champions League",
      "league_type": "champions_league",
      "team_info": {...},
      "fixtures": {...},
      "goals": {...}
    },
    "140": {
      "league_id": 140,
      "league_name": "La Liga",
      "league_type": "domestic_league",
      ...
    }
  },
  "match_details": [
    {
      "fixture_id": 1234567,
      "date": "2024-03-15T20:00:00",
      "league": {
        "id": 2,
        "name": "UEFA Champions League",
        "type": "champions_league",
        "round": "Round of 16"
      },
      "teams": {
        "team_id": 541,
        "team_location": "home",
        "opponent_id": 50,
        "opponent_name": "Manchester City"
      },
      "score": {
        "team_score": 3,
        "opponent_score": 1,
        "result": "win"
      },
      "venue": {...},
      "statistics": [...]
    }
  ],
  "season_summary": {
    "total_matches": 58,
    "total_goals_scored": 87,
    "total_goals_conceded": 42,
    "total_wins": 35,
    "total_draws": 12,
    "total_losses": 11,
    "competitions_played": ["UEFA Champions League", "La Liga", "Copa del Rey"],
    "home_record": {"wins": 20, "draws": 5, "losses": 3},
    "away_record": {"wins": 15, "draws": 7, "losses": 8},
    "competition_breakdown": {...}
  }
}
```

## Performance Expectations

### Collection Scope
- **Teams**: 67 UEFA Champions League teams
- **Seasons**: 6 seasons (2019-2024)
- **Total Scope**: 402 team-seasons
- **Estimated Matches**: 15,000-20,000 individual matches

### Performance Targets
- **Collection Speed**: ~8 teams per hour
- **API Efficiency**: ~5,000 requests per hour
- **Data Quality**: 99.85% consistency
- **Team Coverage**: 100% of 67 core teams

### API Usage Optimization
- **Rate Limiting**: 100 requests per minute (respects API limits)
- **Caching**: 30-day cache to avoid duplicate requests
- **Smart Collection**: Skips existing data automatically
- **Estimated Total**: 6,000-8,000 API requests for full collection

## Quality Assurance

### Validation Metrics
- **File Structure**: Correct directory organization and naming
- **Data Quality**: Required fields present and valid
- **Coverage**: All teams and seasons represented
- **Consistency**: 99.85% data consistency target

### Error Handling
- **Automatic Retry**: Failed requests retried up to 3 times
- **Graceful Degradation**: Collection continues despite individual failures
- **Error Logging**: Detailed error tracking and reporting
- **Recovery**: Ability to resume from interruption points

## Integration with Existing Analysis

### Shapley Value Analysis Integration
The team statistics complement player statistics for comprehensive analysis:

```bash
# After team statistics collection, run integrated analysis
python scripts/analysis/simple_shapley_analysis.py
python scripts/analysis/multi_season_comparative_analysis.py

# Team-level performance analysis
python scripts/analysis/team_performance_analyzer.py  # (to be created)
```

### Data Compatibility
- **Consistent Team IDs**: Uses same team identifiers as player statistics
- **Season Alignment**: Matches player statistics season coverage
- **JSON Structure**: Compatible with existing analysis scripts
- **File Organization**: Follows established data organization patterns

## Troubleshooting

### Common Issues

#### 1. Missing Team Roster Files
```bash
# Check if roster files exist
ls data/focused/players/team_rosters/ | grep "team_.*_players_"

# If missing, collect rosters first
python scripts/collect_2024_2025_player_data.py
```

#### 2. API Rate Limiting
```bash
# Check current API usage
python scripts/analysis/team_statistics_validator.py

# Adjust rate limiting if needed
# Edit config/team_statistics_collection_config.yaml
```

#### 3. Incomplete Data Collection
```bash
# Resume collection from where it left off
python scripts/data_collection/comprehensive_team_statistics_collector.py

# Check specific team data
python scripts/data_collection/comprehensive_team_statistics_collector.py --max-teams 1
```

#### 4. Data Quality Issues
```bash
# Run comprehensive validation
python scripts/analysis/team_statistics_validator.py

# Check specific validation aspects
python scripts/data_collection/comprehensive_team_statistics_collector.py --validate-only
```

### Performance Optimization

#### 1. Cache Utilization
- Enable caching to avoid duplicate API requests
- Cache expires after 30 days for data freshness
- Monitor cache efficiency in collection reports

#### 2. Batch Processing
- Process teams in batches to manage API quota
- Use `--max-teams` parameter for controlled collection
- Resume collection as needed

#### 3. Error Recovery
- Collection automatically skips existing data
- Failed requests are retried with exponential backoff
- Detailed error logging for troubleshooting

## Expected Output

### File Organization
```
data/focused/teams/
├── team_541/                    # Real Madrid
│   ├── 2019/
│   │   └── team_541_statistics_2019.json
│   ├── 2020/
│   │   └── team_541_statistics_2020.json
│   └── ...
├── team_529/                    # Barcelona
│   ├── 2019/
│   │   └── team_529_statistics_2019.json
│   └── ...
└── ...
```

### Collection Reports
- `data/analysis/comprehensive_team_statistics_collection_report.json` - Collection summary
- `data/analysis/team_statistics_validation_report.json` - Quality validation
- `data/cache/team_statistics/` - Cached API responses

### Success Criteria
- ✅ All 67 core teams have data files
- ✅ Target seasons (2019-2024) are covered
- ✅ Data consistency ≥ 99.85%
- ✅ Match details include all major competitions
- ✅ API usage stays within efficient limits
- ✅ Data is ready for integrated Shapley analysis

This comprehensive team statistics collection provides the foundation for complete team-level analysis, enabling advanced Shapley value calculations that consider both individual player contributions and overall team performance across multiple competitions and seasons.

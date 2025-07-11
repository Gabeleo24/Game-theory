# Real Madrid 2023-24 Season Dataset

## Overview
This dataset contains comprehensive match-by-match data for Real Madrid's 2023-24 season, including team-level match results and individual player performances across all competitions.

## Dataset Statistics
- **Total Matches**: 46
- **Player Performances**: 672
- **Active Players**: 24
- **Competitions**: La Liga, Champions League, Copa del Rey, UEFA Super Cup, FIFA Club World Cup
- **Season Record**: 28 wins (60.9% win rate)

## Files Included

### 1. real_madrid_match_results_2023_24.csv
Team-level match results with statistics like possession, shots, passes, etc.

### 2. real_madrid_player_match_performances_2023_24.csv
Individual player statistics for each match they participated in.

### 3. real_madrid_player_season_aggregates_2023_24.csv
Season totals and averages calculated from match-level data.

### 4. real_madrid_competition_summary_2023_24.csv
Performance breakdown by competition.

## Key Features
- ✅ Complete match schedule across all competitions
- ✅ Individual player performances for every match
- ✅ Realistic statistics based on actual team performance
- ✅ Validated data relationships and integrity
- ✅ Ready for analysis and visualization
- ✅ Compatible with Manchester City dataset structure

## Usage Examples

### SQL Queries
```sql
-- Top scorers
SELECT player_name, SUM(goals) as total_goals
FROM player_match_performances
GROUP BY player_name
ORDER BY total_goals DESC;

-- Performance vs big teams
SELECT opponent, AVG(rating) as avg_rating
FROM player_match_performances pmp
JOIN match_results mr ON pmp.match_id = mr.match_id
WHERE opponent IN ('Barcelona', 'Atlético Madrid', 'Manchester City')
GROUP BY opponent;
```

### Python Analysis
```python
import pandas as pd

# Load data
matches = pd.read_csv('real_madrid_match_results_2023_24.csv')
performances = pd.read_csv('real_madrid_player_match_performances_2023_24.csv')

# Analyze home vs away performance
home_away = matches.groupby('home_away')['result'].value_counts()
```

## Data Quality
- Validation Status: ✅ PASS
- All foreign key relationships validated
- Statistical realism checks passed
- Compatible with Manchester City dataset structure

Generated: 2025-07-10 17:37:34

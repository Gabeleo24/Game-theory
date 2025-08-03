# Manchester City 2023-24 Season Dataset

## Overview
This dataset contains comprehensive match-by-match data for Manchester City's 2023-24 season, including team-level match results and individual player performances across all competitions.

## Dataset Statistics
- **Total Matches**: 57
- **Player Performances**: 784
- **Active Players**: 31
- **Competitions**: Premier League, Champions League, FA Cup, EFL Cup
- **Season Record**: 37 wins (64.9% win rate)

## Files Included

### 1. manchester_city_match_results_2023_24.csv
Team-level match results with statistics like possession, shots, passes, etc.

### 2. manchester_city_player_match_performances_2023_24.csv  
Individual player statistics for each match they participated in.

### 3. manchester_city_player_season_aggregates_2023_24.csv
Season totals and averages calculated from match-level data.

### 4. manchester_city_competition_summary_2023_24.csv
Performance breakdown by competition.

## Key Features
- ✅ Complete match schedule across all competitions
- ✅ Individual player performances for every match
- ✅ Realistic statistics based on actual team performance
- ✅ Validated data relationships and integrity
- ✅ Ready for analysis and visualization

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
WHERE opponent IN ('Arsenal', 'Liverpool', 'Chelsea')
GROUP BY opponent;
```

### Python Analysis
```python
import pandas as pd

# Load data
matches = pd.read_csv('manchester_city_match_results_2023_24.csv')
performances = pd.read_csv('manchester_city_player_match_performances_2023_24.csv')

# Analyze home vs away performance
home_away = matches.groupby('home_away')['result'].value_counts()
```

## Data Quality
- Validation Status: ✅ PASS
- All foreign key relationships validated
- Statistical realism checks passed
- Minor warnings noted in documentation

Generated: 2025-07-09 23:12:07

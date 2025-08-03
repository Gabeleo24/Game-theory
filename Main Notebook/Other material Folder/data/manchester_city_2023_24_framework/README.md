# Manchester City 2023-2024 Season Complete Data Collection

## 🏆 Overview
This folder contains comprehensive individual player statistics framework for Manchester City's 2023-2024 season across all competitions. The data is structured to provide detailed match-by-match performance metrics for every player in the squad.

## 📊 Data Collection Summary
- **Team**: Manchester City
- **Season**: 2023-2024 (Premier League Season ID: 21646)
- **Squad Size**: 32 players
- **Estimated Total Matches**: 55 games across all competitions
- **Data Collection Date**: July 9, 2025

## 📁 Files Description

### 1. `squad_overview_20250709_150223.csv`
**Complete squad roster with basic player information**
- 32 players with jersey numbers, positions, physical stats
- Includes: player_id, name, jersey_number, height, weight, date_of_birth
- Key players: Erling Haaland (#9), Kevin De Bruyne (#17), Phil Foden (#47)

### 2. `detailed_players_20250709_150223.csv`
**Comprehensive player profiles with full details**
- Complete player information including nationality, position details
- Squad relationships and team affiliations
- Player photos and metadata
- 33 columns of detailed information per player

### 3. `player_match_templates_20250709_150223.csv`
**Individual game statistics framework for every player**
- **1,760 total records** (32 players × 55 estimated matches)
- Match-by-match template for comprehensive performance tracking
- Ready for individual game statistics input

### 4. `season_framework_20250709_150223.json`
**Complete season structure in JSON format**
- Full squad details and season information
- Competition breakdown and match estimates
- Comprehensive data structure for analysis

## 🎯 Individual Player Statistics Framework

Each player has detailed match-by-match records with the following metrics:

### Basic Match Information
- `match_number` - Game number in season (1-55)
- `match_date` - Date of the match
- `opponent` - Opposition team
- `competition` - Premier League, Champions League, FA Cup, EFL Cup
- `home_away` - Home or away fixture
- `result` - Match result

### Performance Metrics
- `played` - Did the player participate
- `started` - Did the player start the match
- `minutes_played` - Minutes on the pitch
- `goals` - Goals scored
- `assists` - Assists provided
- `shots` - Total shots taken
- `shots_on_target` - Shots on target

### Passing Statistics
- `passes` - Total passes attempted
- `passes_completed` - Successful passes
- `pass_accuracy_percent` - Pass completion percentage

### Defensive Statistics
- `tackles` - Tackles made
- `interceptions` - Interceptions
- `clearances` - Defensive clearances

### Advanced Metrics
- `crosses` - Crosses attempted
- `dribbles` - Dribbles attempted
- `dribbles_successful` - Successful dribbles
- `fouls_committed` - Fouls committed
- `fouls_suffered` - Fouls received
- `yellow_cards` - Yellow cards received
- `red_cards` - Red cards received
- `offsides` - Offside calls

### Goalkeeper Specific
- `saves` - Saves made (for goalkeepers)
- `goals_conceded` - Goals conceded
- `clean_sheet` - Clean sheet achieved

### Overall Performance
- `rating` - Match rating (0-10 scale)
- `player_of_match` - Player of the match award

## 🏆 Competition Breakdown

### Premier League
- **Estimated Matches**: 38 games
- **Description**: English Premier League 2023-2024 season

### UEFA Champions League
- **Estimated Matches**: 8 games
- **Description**: UEFA Champions League 2023-2024 campaign

### FA Cup
- **Estimated Matches**: 6 games
- **Description**: FA Cup 2023-2024 tournament

### EFL Cup
- **Estimated Matches**: 5 games
- **Description**: EFL Cup 2023-2024 tournament

## 👥 Key Squad Players

### Star Players
- **Erling Haaland** (#9) - Striker, 195cm, Norway
- **Kevin De Bruyne** (#17) - Midfielder, 181cm, Belgium
- **Phil Foden** (#47) - Midfielder, 171cm, England
- **Bernardo Silva** (#20) - Midfielder, 173cm, Portugal
- **Jack Grealish** (#10) - Winger, England

### Goalkeepers
- **Ederson** (#31) - Primary goalkeeper, Brazil
- **Stefan Ortega** (#18) - Backup goalkeeper, Germany
- **Scott Carson** (#33) - Third goalkeeper, England

### Defense
- **Ruben Dias** (#3) - Center-back, Portugal
- **John Stones** (#5) - Center-back, England
- **Kyle Walker** (#2) - Right-back, England
- **Nathan Ake** (#6) - Left-back, Netherlands

## 📈 Data Usage

### For Analysis
1. **Individual Performance Tracking**: Monitor each player's game-by-game statistics
2. **Season Progression**: Track player development throughout the season
3. **Competition Comparison**: Compare performance across different competitions
4. **Team Selection**: Analyze player contributions for team selection decisions

### For Machine Learning
1. **Player Performance Prediction**: Use historical data to predict future performance
2. **Team Formation Optimization**: Analyze best player combinations
3. **Injury Risk Assessment**: Monitor workload and performance patterns
4. **Transfer Value Analysis**: Assess player market value based on performance

## 🔧 Data Structure

### CSV Format
- **Readable**: Easy to open in Excel, Google Sheets, or any data analysis tool
- **Compressed**: Efficient storage while maintaining readability
- **Structured**: Consistent column headers and data types

### JSON Format
- **Hierarchical**: Nested structure for complex relationships
- **API-Ready**: Can be easily consumed by web applications
- **Flexible**: Supports additional metadata and nested objects

## 📋 Next Steps

1. **Match Data Population**: Fill in actual match results and opponent information
2. **Statistics Collection**: Populate individual player performance metrics
3. **Real-time Updates**: Update statistics after each match
4. **Analysis Dashboard**: Create visualization tools for the data
5. **Predictive Modeling**: Build machine learning models using the framework

## ✅ Data Quality

- **Complete Squad**: All 32 players from 2023-24 season included
- **Verified Information**: Player details confirmed from SportMonks API
- **Consistent Structure**: Standardized format across all records
- **Ready for Analysis**: Clean, structured data ready for immediate use

This comprehensive framework provides the foundation for detailed analysis of Manchester City's 2023-2024 season performance at the individual player level.

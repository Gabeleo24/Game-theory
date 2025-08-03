# SportMonks API Database Summary

## ✅ Confirmed Working Data Sources

Based on comprehensive testing conducted on 2025-07-09, here's exactly what data we can pull from SportMonks API for our database:

### 🏟️ Team Data
**Endpoint**: `teams/{id}`
**Status**: ✅ Working
**Sample**: Manchester City (ID: 9)

```json
{
  "id": 9,
  "sport_id": 1,
  "country_id": 462,
  "venue_id": 151,
  "gender": "male",
  "name": "Manchester City",
  "short_code": "MCI",
  "image_path": "https://cdn.sportmonks.com/images/soccer/teams/9/9.png",
  "founded": 1880,
  "type": "domestic",
  "placeholder": false,
  "last_played_at": "2025-07-01 01:00:00"
}
```

### 👥 Squad Data
**Endpoint**: `squads/seasons/{season_id}/teams/{team_id}`
**Status**: ✅ Working
**Sample**: 32 players for 2023-2024 season

```json
{
  "id": 483841211,
  "player_id": 105,
  "team_id": 9,
  "season_id": 21646,
  "has_values": true,
  "position_id": 24,
  "jersey_number": 33
}
```

### 👤 Player Data
**Endpoint**: `players/{id}`
**Status**: ✅ Working
**Sample**: Scott Carson (ID: 105)

```json
{
  "id": 105,
  "sport_id": 1,
  "country_id": 462,
  "nationality_id": 462,
  "city_id": 98462,
  "position_id": 24,
  "detailed_position_id": 24,
  "type_id": 24,
  "common_name": "S. Carson",
  "firstname": "Scott",
  "lastname": "Carson",
  "name": "Scott Carson",
  "display_name": "Scott Carson",
  "image_path": "https://cdn.sportmonks.com/images/soccer/players/9/105.png",
  "height": 188,
  "weight": 85,
  "date_of_birth": "1985-09-03",
  "gender": "male"
}
```

### 🏆 Seasons Data
**Endpoint**: `seasons`
**Status**: ✅ Working
**Sample**: 25 seasons available

```json
{
  "id": 21646,
  "sport_id": 1,
  "league_id": 8,
  "tie_breaker_rule_id": 1526,
  "name": "2023/2024",
  "finished": false,
  "pending": false,
  "is_current": true,
  "starting_at": "2023-08-12",
  "ending_at": "2024-05-19",
  "standings_recalculated_at": "2024-05-20 08:28:07",
  "games_in_current_week": false
}
```

### ⚽ Fixtures Data
**Endpoint**: `fixtures`
**Status**: ✅ Working
**Sample**: Match data available

```json
{
  "id": 463,
  "sport_id": 1,
  "league_id": 8,
  "season_id": 2,
  "stage_id": 2,
  "group_id": null,
  "aggregate_id": null,
  "round_id": 43,
  "state_id": 5,
  "venue_id": 209,
  "name": "Tottenham Hotspur vs Manchester City",
  "starting_at": "2010-08-14 11:45:00",
  "result_info": "Game ended in draw.",
  "leg": "1/1",
  "details": null,
  "length": 90,
  "placeholder": false,
  "has_odds": false,
  "has_premium_odds": false,
  "starting_at_timestamp": 1281786300
}
```

## 📊 Database Schema Recommendations

### Core Tables
Based on working endpoints, we can create these tables:

1. **teams**
   - Primary key: `id`
   - Fields: name, short_code, country_id, venue_id, founded, etc.

2. **players**
   - Primary key: `id`
   - Fields: name, firstname, lastname, height, weight, date_of_birth, etc.

3. **seasons**
   - Primary key: `id`
   - Fields: name, league_id, starting_at, ending_at, finished, etc.

4. **team_squads**
   - Links players to teams by season
   - Fields: player_id, team_id, season_id, position_id, jersey_number

5. **matches**
   - Primary key: `id`
   - Fields: name, season_id, league_id, starting_at, result_info, etc.

### Key Relationships
- `team_squads.team_id` → `teams.id`
- `team_squads.player_id` → `players.id`
- `team_squads.season_id` → `seasons.id`
- `matches.season_id` → `seasons.id`

## 🚀 Data Collection Capabilities

### What We Can Collect Right Now:
✅ **Team Information** - Complete team profiles
✅ **Player Profiles** - Detailed player information
✅ **Squad Compositions** - Team rosters by season
✅ **Season Data** - Competition seasons and dates
✅ **Match Fixtures** - Basic match information

### Collection Statistics (Test Run):
- **Team**: Manchester City complete profile
- **Seasons**: 25 seasons available
- **Squad Data**: 66 player entries across 2 seasons
- **Individual Players**: 6 detailed player profiles
- **Fixtures**: 20 match records

## 🔧 Technical Implementation

### API Configuration
- **Base URL**: `https://api.sportmonks.com/v3/football`
- **Rate Limit**: 3000 requests/hour (1.2 second delays)
- **Authentication**: API token required
- **Response Format**: JSON

### Working Season IDs
- 2023-2024: 21646
- 2022-2023: 19734
- 2021-2022: 19686
- 2020-2021: 18378
- 2019-2020: 17141

### Team IDs (Confirmed)
- Manchester City: 9

## 📋 Next Steps for Database Creation

### Phase 1: Core Data Collection
1. ✅ Set up API connection and authentication
2. ✅ Create data collection scripts for working endpoints
3. ✅ Test data collection with Manchester City
4. 🔄 Expand to collect all 67 UEFA Champions League teams
5. 🔄 Collect historical data for 2019-2024 seasons

### Phase 2: Database Implementation
1. Create PostgreSQL database schema
2. Implement data insertion scripts
3. Set up data validation and quality checks
4. Create automated collection pipeline

### Phase 3: Advanced Data
1. Investigate additional endpoints for:
   - Match statistics
   - Player performance metrics
   - Team statistics
   - Match events (goals, cards, substitutions)

## 🎯 Immediate Action Items

1. **Expand Team Collection**: Find team IDs for all 67 UEFA Champions League teams
2. **Historical Data**: Collect squad and match data for 2019-2024 seasons
3. **Database Setup**: Create PostgreSQL tables based on confirmed schema
4. **Data Pipeline**: Automate collection process with error handling
5. **Data Quality**: Implement validation and consistency checks

## 📈 Expected Database Size

Based on test collection:
- **Teams**: ~67 records
- **Players**: ~2,000+ records (30 players × 67 teams)
- **Seasons**: ~25 records
- **Team Squads**: ~10,000+ records (67 teams × 6 seasons × 25 players)
- **Matches**: ~5,000+ records (67 teams × 6 seasons × ~12 matches/season)

## ✅ Conclusion

SportMonks API provides excellent data for our soccer intelligence database. We have confirmed working endpoints for all core data types needed for comprehensive team and player analysis. The next step is to scale up collection to all target teams and implement the database infrastructure.

# SportMonks API Database Capabilities

## Overview
This document outlines what data we can pull from the SportMonks API for our soccer intelligence database. Based on comprehensive API exploration conducted on 2025-07-09.

## API Configuration
- **Base URL**: `https://api.sportmonks.com/v3/football`
- **Authentication**: API token required
- **Rate Limits**: 3000 requests per hour
- **Test Team**: Manchester City (ID: 9)

## Available Data Endpoints

### 1. Teams Data (`teams/{id}`)
**Endpoint**: `teams/9` (Manchester City)
**Description**: Core team information for database teams table

**Available Fields**:
- `id` (INTEGER) - Unique team identifier
- `sport_id` (INTEGER) - Sport type (1 = football)
- `country_id` (INTEGER) - Country reference
- `venue_id` (INTEGER) - Home venue reference
- `gender` (VARCHAR) - Team gender (male/female)
- `name` (VARCHAR) - Full team name
- `short_code` (VARCHAR) - Team abbreviation (e.g., "MCI")
- `image_path` (VARCHAR) - Team logo URL
- `founded` (INTEGER) - Year founded
- `type` (VARCHAR) - Team type (domestic/international)
- `placeholder` (BOOLEAN) - Is placeholder team
- `last_played_at` (TIMESTAMP) - Last match date

**Sample Data**:
```json
{
  "id": 9,
  "name": "Manchester City",
  "short_code": "MCI",
  "founded": 1880,
  "country_id": 462,
  "venue_id": 151
}
```

### 2. Team Squads (`squads/seasons/{season_id}/teams/{team_id}`)
**Endpoint**: `squads/seasons/21646/teams/9`
**Description**: Team squad data linking players to teams by season

**Available Fields**:
- `id` (INTEGER) - Squad entry ID
- `player_id` (INTEGER) - Player reference
- `team_id` (INTEGER) - Team reference
- `season_id` (INTEGER) - Season reference
- `has_values` (BOOLEAN) - Has statistical data
- `position_id` (INTEGER) - Player position
- `jersey_number` (INTEGER) - Squad number

**Use Case**: Links players to teams for specific seasons

### 3. Players Data (`players/{id}`)
**Endpoint**: `players/105` (example player)
**Description**: Individual player information

**Available Fields**:
- `id` (INTEGER) - Unique player identifier
- `sport_id` (INTEGER) - Sport type
- `country_id` (INTEGER) - Birth country
- `nationality_id` (INTEGER) - Nationality
- `city_id` (INTEGER) - Birth city
- `position_id` (INTEGER) - Playing position
- `detailed_position_id` (INTEGER) - Specific position
- `type_id` (INTEGER) - Player type
- `common_name` (VARCHAR) - Display name
- `firstname` (VARCHAR) - First name
- `lastname` (VARCHAR) - Last name
- `name` (VARCHAR) - Full name
- `display_name` (VARCHAR) - Preferred display name
- `image_path` (VARCHAR) - Player photo URL
- `height` (INTEGER) - Height in cm
- `weight` (INTEGER) - Weight in kg
- `date_of_birth` (DATE) - Birth date
- `gender` (VARCHAR) - Gender

### 4. Fixtures/Matches (`fixtures`)
**Endpoint**: `fixtures`
**Description**: Match/game data

**Available Fields**:
- `id` (INTEGER) - Unique match identifier
- `sport_id` (INTEGER) - Sport type
- `league_id` (INTEGER) - Competition reference
- `season_id` (INTEGER) - Season reference
- `stage_id` (INTEGER) - Competition stage
- `group_id` (INTEGER) - Group stage reference (nullable)
- `aggregate_id` (INTEGER) - Aggregate match reference (nullable)
- `round_id` (INTEGER) - Round reference
- `state_id` (INTEGER) - Match state (scheduled/live/finished)
- `venue_id` (INTEGER) - Venue reference
- `name` (VARCHAR) - Match name (e.g., "Team A vs Team B")
- `starting_at` (TIMESTAMP) - Match start time
- `result_info` (VARCHAR) - Result description
- `leg` (VARCHAR) - Leg information (1/1, 1/2, etc.)
- `details` (TEXT) - Additional details (nullable)
- `length` (INTEGER) - Match duration in minutes
- `placeholder` (BOOLEAN) - Is placeholder match
- `has_odds` (BOOLEAN) - Has betting odds
- `has_premium_odds` (BOOLEAN) - Has premium odds
- `starting_at_timestamp` (INTEGER) - Unix timestamp

**Sample Match**:
```json
{
  "id": 463,
  "name": "Tottenham Hotspur vs Manchester City",
  "starting_at": "2010-08-14 11:45:00",
  "result_info": "Game ended in draw.",
  "length": 90
}
```

### 5. Seasons Data (`seasons`)
**Endpoint**: `seasons`
**Description**: Competition seasons information

**Available Fields**:
- `id` (INTEGER) - Season identifier
- `sport_id` (INTEGER) - Sport type
- `league_id` (INTEGER) - League/competition reference
- `tie_breaker_rule_id` (INTEGER) - Tiebreaker rules
- `name` (VARCHAR) - Season name (e.g., "2023/2024")
- `finished` (BOOLEAN) - Is season completed
- `pending` (BOOLEAN) - Is season pending
- `is_current` (BOOLEAN) - Is current season
- `starting_at` (DATE) - Season start date
- `ending_at` (DATE) - Season end date
- `standings_recalculated_at` (TIMESTAMP) - Last standings update
- `games_in_current_week` (BOOLEAN) - Has games this week

## Database Schema Recommendations

### Core Tables Structure
Based on the API exploration, we recommend these core tables:

1. **teams** - Store team information
2. **players** - Store player information  
3. **seasons** - Store season/competition information
4. **matches** - Store fixture/match information
5. **team_squads** - Link players to teams by season
6. **player_statistics** - Store match-level player performance (requires additional endpoints)
7. **match_events** - Store match events (goals, cards, etc.)

### Key Relationships
- `team_squads.team_id` → `teams.id`
- `team_squads.player_id` → `players.id`
- `team_squads.season_id` → `seasons.id`
- `matches.season_id` → `seasons.id`
- `matches.league_id` → `competitions.id`

## Data Collection Strategy

### 1. Initial Setup
- Collect all available seasons
- Collect team information for target teams
- Collect player information for squad members

### 2. Match Data Collection
- Collect fixtures for target teams and seasons
- For each match, collect detailed match data with includes
- Store match events, lineups, and statistics

### 3. Player Statistics
- Collect match-level player statistics
- Link to specific matches and players
- Store performance metrics per game

## Rate Limiting Considerations
- 3000 requests per hour limit
- Implement 1.2 second delays between requests
- Use caching for repeated data
- Batch requests efficiently

## Next Steps
1. Implement data collection scripts for each endpoint
2. Create database tables based on schema
3. Set up automated data collection pipeline
4. Implement data quality checks and validation
5. Create data analysis and visualization tools

## Working Endpoints Summary
✅ `teams/{id}` - Team information
✅ `squads/seasons/{season_id}/teams/{team_id}` - Squad data
✅ `players/{id}` - Player information
✅ `fixtures` - Match data
✅ `seasons` - Season information

## Endpoints Requiring Further Investigation
🔍 Player statistics endpoints
🔍 Match lineups and events
🔍 Team statistics
🔍 Competition standings
🔍 Match details with includes

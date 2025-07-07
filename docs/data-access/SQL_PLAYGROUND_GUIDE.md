# SQL Playground Guide - ADS599 Capstone Soccer Intelligence System

## Overview

The SQL Playground provides an interactive environment for exploring the soccer intelligence database with automatic query logging, result formatting, and comprehensive analysis capabilities. This guide shows you how to use the SQL playground for data exploration and analysis.

## Quick Start

### 1. Start the Database
```bash
# Start PostgreSQL container
docker-compose up postgres -d

# Verify it's running
docker-compose ps postgres
```

### 2. Access the SQL Playground
```bash
# Interactive SQL with logging
./run_sql_with_logs.sh

# Direct database access
docker exec -it soccer-intelligence-db psql -U soccerapp -d soccer_intelligence

# Show database structure
./show_database_structure.sh
```

## Database Schema Overview

### Core Tables
- **teams** (67 records) - UEFA Champions League teams
- **players** (3,980+ records) - Player profiles and details
- **competitions** (7 records) - League and competition data
- **matches** (98+ records) - Match results and details
- **player_statistics** (8,080+ records) - Individual player performance metrics
- **shapley_analysis** - Shapley value analysis results

### Key Relationships
```sql
-- Player statistics relationships
player_statistics.player_id → players.player_id
player_statistics.team_id → teams.team_id
player_statistics.match_id → matches.match_id
player_statistics.competition_id → competitions.competition_id

-- Match relationships
matches.home_team_id → teams.team_id
matches.away_team_id → teams.team_id
```

## SQL Playground Commands

### Pre-Built Analyses
```bash
# Database overview
./run_sql_with_logs.sh analysis overview

# Player card analysis
./run_sql_with_logs.sh analysis cards

# Team performance analysis
./run_sql_with_logs.sh analysis teams

# Match analysis
./run_sql_with_logs.sh analysis matches

# Run all analyses
./run_sql_with_logs.sh analysis all
```

### Custom Queries
```bash
# Single query with description
./run_sql_with_logs.sh query "SELECT * FROM teams LIMIT 5" "Sample teams query"

# Query from file
./run_sql_with_logs.sh file my_query.sql "Custom analysis"

# View recent logs
./run_sql_with_logs.sh logs
```

## Essential SQL Queries

### 1. Database Exploration
```sql
-- List all tables
\dt

-- Table structure
\d player_statistics

-- Record counts
SELECT 
    'teams' as table_name, COUNT(*) as records FROM teams
UNION ALL
SELECT 'players', COUNT(*) FROM players
UNION ALL
SELECT 'matches', COUNT(*) FROM matches
UNION ALL
SELECT 'player_statistics', COUNT(*) FROM player_statistics;
```

### 2. Team Analysis
```sql
-- Top teams by total goals
SELECT 
    t.team_name,
    t.country,
    SUM(ps.goals) as total_goals,
    COUNT(DISTINCT ps.player_id) as players_count
FROM teams t
JOIN player_statistics ps ON t.team_id = ps.team_id
GROUP BY t.team_id, t.team_name, t.country
ORDER BY total_goals DESC
LIMIT 10;
```

### 3. Player Performance
```sql
-- Top goal scorers with team info
SELECT 
    p.player_name,
    p.nationality,
    t.team_name,
    SUM(ps.goals) as total_goals,
    SUM(ps.assists) as total_assists,
    AVG(ps.player_rating) as avg_rating,
    SUM(ps.minutes_played) as total_minutes
FROM player_statistics ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams t ON ps.team_id = t.team_id
WHERE ps.minutes_played > 90  -- At least one full match
GROUP BY p.player_id, p.player_name, p.nationality, t.team_name
ORDER BY total_goals DESC
LIMIT 20;
```

### 4. Match Analysis
```sql
-- High-scoring matches
SELECT 
    m.match_date,
    ht.team_name as home_team,
    at.team_name as away_team,
    m.home_goals,
    m.away_goals,
    (m.home_goals + m.away_goals) as total_goals,
    c.competition_name
FROM matches m
JOIN teams ht ON m.home_team_id = ht.team_id
JOIN teams at ON m.away_team_id = at.team_id
JOIN competitions c ON m.competition_id = c.competition_id
WHERE (m.home_goals + m.away_goals) >= 6
ORDER BY total_goals DESC, m.match_date DESC;
```

### 5. Advanced Analytics
```sql
-- Player efficiency (goals per 90 minutes)
SELECT 
    p.player_name,
    t.team_name,
    SUM(ps.goals) as total_goals,
    SUM(ps.minutes_played) as total_minutes,
    ROUND(
        (SUM(ps.goals)::DECIMAL / (SUM(ps.minutes_played) / 90.0)), 2
    ) as goals_per_90min,
    ROUND(AVG(ps.player_rating), 2) as avg_rating
FROM player_statistics ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams t ON ps.team_id = t.team_id
WHERE ps.minutes_played > 450  -- At least 5 full matches
GROUP BY p.player_id, p.player_name, t.team_name
HAVING SUM(ps.goals) > 0
ORDER BY goals_per_90min DESC
LIMIT 15;
```

### 6. Competition Comparison
```sql
-- Performance by competition
SELECT 
    c.competition_name,
    COUNT(DISTINCT ps.player_id) as unique_players,
    COUNT(DISTINCT ps.team_id) as unique_teams,
    SUM(ps.goals) as total_goals,
    AVG(ps.player_rating) as avg_rating,
    SUM(ps.yellow_cards) as total_yellow_cards,
    SUM(ps.red_cards) as total_red_cards
FROM player_statistics ps
JOIN competitions c ON ps.competition_id = c.competition_id
GROUP BY c.competition_id, c.competition_name
ORDER BY total_goals DESC;
```

## Advanced Features

### 1. Query Logging
All queries executed through the SQL playground are automatically logged with:
- Timestamp and description
- Query execution time
- Result summary
- Formatted results
- Error handling

### 2. Result Formatting
Results are automatically formatted as:
- Readable tables
- CSV export format
- INSERT statements for result replication
- Summary statistics

### 3. Performance Monitoring
```sql
-- Query performance analysis
EXPLAIN ANALYZE 
SELECT p.player_name, SUM(ps.goals) as total_goals
FROM player_statistics ps
JOIN players p ON ps.player_id = p.player_id
GROUP BY p.player_id, p.player_name
ORDER BY total_goals DESC
LIMIT 10;
```

## Data Quality Checks

### 1. Data Completeness
```sql
-- Check for missing data
SELECT 
    'goals' as metric,
    COUNT(*) as total_records,
    COUNT(goals) as non_null_records,
    ROUND(COUNT(goals)::DECIMAL / COUNT(*) * 100, 2) as completeness_pct
FROM player_statistics
UNION ALL
SELECT 
    'player_rating',
    COUNT(*),
    COUNT(player_rating),
    ROUND(COUNT(player_rating)::DECIMAL / COUNT(*) * 100, 2)
FROM player_statistics;
```

### 2. Data Validation
```sql
-- Validate data ranges
SELECT 
    'Invalid ratings' as check_type,
    COUNT(*) as count
FROM player_statistics 
WHERE player_rating < 0 OR player_rating > 10
UNION ALL
SELECT 
    'Negative goals',
    COUNT(*)
FROM player_statistics 
WHERE goals < 0;
```

## Tips and Best Practices

### 1. Query Optimization
- Use LIMIT for large result sets
- Add WHERE clauses to filter data
- Use indexes for better performance
- Use EXPLAIN ANALYZE for query optimization

### 2. Data Exploration
- Start with simple queries and build complexity
- Use aggregate functions for summary statistics
- Join tables to get comprehensive views
- Filter by season_year for temporal analysis

### 3. Result Management
- Use descriptive names for saved queries
- Document complex queries with comments
- Save frequently used queries as files
- Use the logging system for result tracking

## Troubleshooting

### Common Issues
```sql
-- Check database connection
SELECT current_database(), current_user, version();

-- Check table existence
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check data availability
SELECT COUNT(*) FROM player_statistics;
```

### Performance Issues
```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_tup_read DESC;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Resources

### Documentation
- **Database Schema**: `docker/postgres/init.sql`
- **Data Access Guide**: `docs/data-access/DATA_ACCESS_GUIDE.md`
- **SQL Logging**: `logs/README_SQL_LOGGING.md`

### Scripts
- **SQL Logger**: `scripts/sql_logging/sql_logger.py`
- **Common Queries**: `scripts/sql_logging/common_queries_with_logging.py`
- **Database Structure**: `./show_database_structure.sh`

### Log Files
- **Query Logs**: `logs/sql_logs/`
- **Session Logs**: Automatic session tracking
- **Error Logs**: Comprehensive error reporting

---

The SQL Playground provides a powerful, logged, and user-friendly environment for exploring your soccer intelligence data. Use it to discover insights, validate hypotheses, and develop advanced analytics for your ADS599 Capstone project.

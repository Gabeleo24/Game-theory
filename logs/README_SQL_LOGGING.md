# SQL Logging System

## Overview

Automatic SQL query logging system that saves all database processes, queries, and results to timestamped log files for tracking, analysis, and documentation.

## Features

- **Automatic Query Logging**: Every SQL query is logged with timestamp and description
- **Results Preservation**: Query results saved in formatted tables and as INSERT statements
- **Process Tracking**: Complete database process workflows logged
- **Multiple Output Formats**: Both human-readable and machine-readable formats
- **Easy Access**: Simple command-line interface for running queries with logging

## Directory Structure

```
logs/
├── sql_logs/                          # Main logging directory
│   ├── sql_session_YYYYMMDD_HHMMSS.log    # Session logs
│   ├── query_TIMESTAMP_description.sql     # Individual query logs
│   └── README_SQL_LOGGING.md               # This file
└── scripts/
    └── sql_logging/
        ├── sql_logger.py                   # Core logging functionality
        ├── common_queries_with_logging.py  # Pre-built queries
        └── run_query_with_logging.py       # Command-line query runner
```

## Usage Methods

### 1. Simple Command Line Interface

```bash
# Run pre-built analyses
./run_sql_with_logs.sh analysis cards
./run_sql_with_logs.sh analysis overview
./run_sql_with_logs.sh analysis all

# Run custom queries
./run_sql_with_logs.sh query "SELECT * FROM teams LIMIT 5" "Sample teams query"

# Run queries from files
./run_sql_with_logs.sh file my_query.sql "Custom analysis"

# View recent logs
./run_sql_with_logs.sh logs
```

### 2. Python Scripts

```python
# Using the SQL logger directly
from scripts.sql_logging.sql_logger import SQLLogger

logger = SQLLogger()
results = logger.execute_and_log(
    "SELECT * FROM player_statistics WHERE yellow_cards > 10",
    "High yellow card players"
)

# Using pre-built queries
from scripts.sql_logging.common_queries_with_logging import CommonQueries

queries = CommonQueries()
queries.player_cards_analysis()  # Runs complete player cards analysis with logging
```

### 3. Direct Database Queries with Logging

```python
# Single query execution
from scripts.sql_logging.sql_logger import execute_and_log_query

results = execute_and_log_query(
    "SELECT team_name, COUNT(*) FROM teams GROUP BY country",
    "Teams by country analysis"
)
```

## Log File Formats

### Session Log Files
- **Filename**: `sql_session_YYYYMMDD_HHMMSS.log`
- **Content**: Complete session activity with timestamps
- **Format**: Standard logging format with INFO/ERROR levels

### Query Result Files
- **Filename**: `query_TIMESTAMP_description.sql`
- **Content**: 
  - Original SQL query
  - Results summary (row count, columns)
  - Formatted results table
  - INSERT statements for data recreation

### Example Query Log File Structure

```sql
-- SQL Query Log
-- Timestamp: 2025-07-06 16:32:00
-- Description: Top 20 Players by Yellow Cards
-- Results: 20 rows
-- ============================================================

-- ORIGINAL QUERY:
/*
SELECT p.player_name, t.team_name, ps.yellow_cards
FROM player_statistics ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams t ON ps.team_id = t.team_id
WHERE ps.yellow_cards > 0
ORDER BY ps.yellow_cards DESC
LIMIT 20;
*/

-- RESULTS SUMMARY:
-- Total rows: 20
-- Columns: player_name, team_name, yellow_cards

-- RESULTS TABLE:
-- --------------------------------------------------------------------------------
-- player_name     | team_name       | yellow_cards    
-- --------------------------------------------------------------------------------
-- Piqué           | Barcelona       | 19              
-- O. Alderete     | Valencia        | 17              
-- ...

-- RESULTS AS INSERT STATEMENTS:
-- INSERT INTO query_results (player_name, team_name, yellow_cards) VALUES ('Piqué', 'Barcelona', 19);
-- INSERT INTO query_results (player_name, team_name, yellow_cards) VALUES ('O. Alderete', 'Valencia', 17);
-- ...
```

## Pre-Built Analyses Available

### 1. Database Overview
- Table record counts
- Data completeness summary
- System status check

### 2. Player Cards Analysis
- Player disciplinary statistics
- Top players by yellow/red cards
- Team disciplinary records
- Position-based card analysis

### 3. Match Analysis
- Match results overview
- Highest scoring matches
- Goal statistics and patterns

### 4. Team Performance Analysis
- Team performance summaries
- Win/loss records
- Goal differences and rankings

## Configuration

### Database Connection
Default configuration in `sql_logger.py`:
```python
db_config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'soccer_intelligence',
    'user': 'soccerapp',
    'password': 'soccerpass123'
}
```

### Log Directory
Default: `logs/sql_logs/`
Can be customized when creating SQLLogger instance:
```python
logger = SQLLogger(log_dir="custom/log/path")
```

## Benefits

### 1. Process Documentation
- Complete audit trail of all database operations
- Reproducible analysis workflows
- Historical query tracking

### 2. Results Preservation
- Query results saved for future reference
- Data backup through INSERT statements
- Easy sharing of analysis results

### 3. Debugging and Optimization
- Query performance tracking
- Error logging and troubleshooting
- Process workflow analysis

### 4. Collaboration
- Shareable query logs
- Standardized analysis documentation
- Team workflow coordination

## File Management

### Automatic Cleanup (Recommended)
```bash
# Remove logs older than 30 days
find logs/sql_logs/ -name "*.log" -mtime +30 -delete
find logs/sql_logs/ -name "*.sql" -mtime +30 -delete
```

### Log Rotation
- Session logs: One per execution session
- Query logs: One per individual query
- Automatic timestamping prevents conflicts

## Integration with Analysis Workflows

### 1. Research Documentation
- All queries automatically documented
- Results preserved for papers/reports
- Reproducible research workflows

### 2. Data Pipeline Tracking
- ETL process logging
- Data quality monitoring
- Pipeline debugging

### 3. Performance Analysis
- Query execution tracking
- Database performance monitoring
- Optimization opportunity identification

## Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   chmod +x run_sql_with_logs.sh
   mkdir -p logs/sql_logs
   ```

2. **Database Connection Issues**
   - Verify PostgreSQL is running: `docker ps`
   - Check connection parameters in `sql_logger.py`

3. **Python Import Errors**
   - Ensure you're in the project root directory
   - Check Python path configuration

### Log File Locations
- **Session logs**: `logs/sql_logs/sql_session_*.log`
- **Query results**: `logs/sql_logs/query_*.sql`
- **Error logs**: Check session log files for ERROR entries

## Examples

### Quick Start
```bash
# Run complete player cards analysis with logging
./run_sql_with_logs.sh analysis cards

# Check what was logged
./run_sql_with_logs.sh logs

# View specific results
cat logs/sql_logs/query_*_Top_20_Players_by_Yellow_Cards.sql
```

### Custom Analysis
```bash
# Run custom team analysis
./run_sql_with_logs.sh query "
SELECT t.team_name, COUNT(ps.player_id) as player_count, 
       SUM(ps.yellow_cards) as total_yellows
FROM teams t 
JOIN player_statistics ps ON t.team_id = ps.team_id 
GROUP BY t.team_name 
ORDER BY total_yellows DESC 
LIMIT 10
" "Team Yellow Card Totals"
```

---

*SQL Logging System - Automatic documentation for all database processes*

# FBref Data Collection

This document explains how to collect football statistics from FBref.com for the Soccer Performance Intelligence System.

## Overview

FBref.com is a comprehensive football statistics website that provides detailed player and team statistics, including advanced metrics like Expected Goals (xG) and Expected Assists (xA). The FBref collector complements API-Football data with deeper statistical analysis.

## Features

### Data Types Available
- **League Tables**: Current standings, points, goal difference
- **Player Statistics**: Goals, assists, xG, xA, shooting, passing, defense, possession
- **Team Statistics**: Comprehensive team performance metrics
- **Advanced Goalkeeping**: PSxG+/- and detailed goalkeeper stats
- **Historical Data**: Multiple seasons of data

### Supported Leagues
- Premier League (England)
- La Liga (Spain)
- Serie A (Italy)
- Bundesliga (Germany)
- Ligue 1 (France)
- UEFA Champions League
- And many more international competitions

## Installation

The FBref collector is already included in the Soccer Intelligence System. Ensure you have the required dependencies:

```bash
pip install requests beautifulsoup4 pandas
```

## Usage

### Basic Usage

```python
from src.soccer_intelligence.data_collection.fbref import FBrefCollector

# Initialize collector
collector = FBrefCollector(cache_dir="data/raw/fbref")

# Get Premier League table
table_df = collector.get_league_table("/en/comps/9/Premier-League-Stats")

# Get player statistics
player_stats = collector.get_player_stats("/en/comps/9/Premier-League-Stats", "stats")

# Get team statistics
team_stats = collector.get_team_stats("/en/comps/9/Premier-League-Stats", "stats")

# Close collector
collector.close()
```

### Command Line Scripts

#### Test the Collector
```bash
python scripts/testing/test_fbref_collector.py
```

#### Demo Collection
```bash
python scripts/data_collection/fbref_demo.py
```

#### Comprehensive Data Collection
```bash
# Collect all major leagues
python scripts/data_collection/collect_fbref_data.py --all

# Collect specific league
python scripts/data_collection/collect_fbref_data.py --league "Premier League"

# Collect Champions League
python scripts/data_collection/collect_fbref_data.py --champions-league

# Collect with custom season
python scripts/data_collection/collect_fbref_data.py --league "La Liga" --season "2023-2024"
```

## Data Structure

### League Table
```csv
Rk,Squad,MP,W,D,L,GF,GA,GD,Pts,season,scraped_at
1,Liverpool,38,25,9,4,86,41,+45,84,2024-2025,2025-06-30 12:00:00
```

### Player Statistics
```csv
Player,Nation,Pos,Squad,Age,MP,Starts,Min,Gls,Ast,xG,xAG,stat_type,scraped_at
Mohamed Salah,eg EGY,RW,Liverpool,32,38,37,3102,29,18,25.2,12.8,stats,2025-06-30 12:00:00
```

### Team Statistics
```csv
Squad,MP,W,D,L,GF,GA,GD,Pts,Gls,Ast,xG,xAG,stat_type,scraped_at
Liverpool,38,25,9,4,86,41,+45,84,86,58,78.5,52.3,stats,2025-06-30 12:00:00
```

## Rate Limiting and Caching

### Respectful Scraping
- Default 2-second delay between requests
- Automatic caching to avoid repeated requests
- Session management for efficient connections
- User-Agent headers for proper identification

### Cache Management
- Data cached in `data/raw/fbref/` directory
- Cached responses used when available
- Cache organized by URL for easy management

## Integration with Soccer Intelligence System

### Complementing API-Football
- API-Football: Real-time match data, fixtures, live scores
- FBref: Detailed statistics, historical analysis, advanced metrics

### Enhancing RAG System
- Rich statistical content for player queries
- Formation-specific tactical analysis
- Historical performance trends

### Supporting Shapley Analysis
- Detailed player performance metrics
- Advanced statistics for contribution analysis
- Multi-dimensional performance data

## Available Statistics Types

### Player Statistics
- `stats`: Standard statistics (goals, assists, minutes)
- `shooting`: Shot statistics, xG, shot accuracy
- `passing`: Pass completion, progressive passes, key passes
- `defense`: Tackles, interceptions, blocks, clearances
- `possession`: Touches, dribbles, carries, progressive carries
- `keepers`: Goalkeeper statistics
- `keepersadv`: Advanced goalkeeper metrics (PSxG+/-)

### Team Statistics
- `stats`: Team performance overview
- `shooting`: Team shooting statistics
- `passing`: Team passing statistics
- `defense`: Team defensive statistics
- `possession`: Team possession statistics

## Error Handling

The collector includes comprehensive error handling:
- Network timeouts and connection errors
- HTML parsing errors
- Missing data graceful handling
- Logging for debugging

## Best Practices

### Data Collection
1. **Start Small**: Test with single league before collecting all data
2. **Use Caching**: Enable caching to avoid repeated requests
3. **Monitor Rate Limits**: Respect FBref's servers with appropriate delays
4. **Regular Updates**: Collect data regularly for current season analysis

### Data Storage
1. **Organized Structure**: Use clear naming conventions for files
2. **Version Control**: Include timestamps and season information
3. **Backup Important Data**: Keep copies of critical datasets
4. **Clean Old Data**: Remove outdated cached files periodically

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure project root is in Python path
2. **Network Errors**: Check internet connection and FBref availability
3. **Parsing Errors**: FBref may change HTML structure occasionally
4. **Rate Limiting**: Increase delay if getting blocked

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Legal and Ethical Considerations

### Terms of Service
- Review FBref's robots.txt and terms of service
- Use data responsibly and for educational/research purposes
- Respect rate limits and server resources

### Data Attribution
- Credit FBref.com as data source in publications
- Follow academic citation standards for research use
- Respect intellectual property rights

## Future Enhancements

### Planned Features
- Women's football leagues support
- Historical seasons data collection
- Match-by-match detailed statistics
- Player comparison tools
- Automated data quality checks

### Integration Opportunities
- Combine with SportMonks API data
- Enhanced social media correlation
- Real-time data updates
- Machine learning feature engineering

## Support

For issues with the FBref collector:
1. Check the troubleshooting section
2. Review error logs in the console
3. Test with the basic test script
4. Verify network connectivity to FBref.com

Remember to always respect FBref's servers and use the data responsibly for your Soccer Performance Intelligence System research.

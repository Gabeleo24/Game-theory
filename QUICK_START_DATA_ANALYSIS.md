# Quick Start Guide for Data Analysis

## 🎯 Your Data is Ready!

### Database Access
- **Host**: localhost:5432
- **Database**: soccer_intelligence
- **Username**: soccerapp
- **Password**: soccerpass123

### Connect via Python
```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://soccerapp:soccerpass123@localhost:5432/soccer_intelligence')
teams_df = pd.read_sql("SELECT * FROM teams", engine)
print(f"Found {len(teams_df)} teams")
```

### Connect via psql
```bash
psql -h localhost -p 5432 -U soccerapp -d soccer_intelligence
```

### Available Tables
- `teams` - Team information
- `players` - Player profiles
- `matches` - Match results
- `player_statistics` - Player performance data
- `team_statistics` - Team performance data
- `competitions` - League/competition data

### Sample Queries
```sql
-- Top 10 teams by points
SELECT team_name, SUM(points) as total_points 
FROM team_statistics ts 
JOIN teams t ON ts.team_id = t.team_id 
GROUP BY team_name 
ORDER BY total_points DESC 
LIMIT 10;

-- Top scorers
SELECT p.player_name, SUM(ps.goals) as total_goals
FROM player_statistics ps
JOIN players p ON ps.player_id = p.player_id
GROUP BY p.player_name
ORDER BY total_goals DESC
LIMIT 10;
```

### Next Steps
1. **Explore the data**: Use the sample queries above
2. **Run analysis**: Execute `python scripts/analysis/data_analysis_starter.py`
3. **Start Jupyter**: Run `docker-compose --profile development up jupyter -d`
4. **Access Jupyter**: Navigate to http://localhost:8888
5. **Create notebooks**: Start building your own analysis

### Useful Scripts
- `scripts/analysis/data_analysis_starter.py` - Sample analysis
- `scripts/data_loading/json_to_postgres.py` - Reload data
- `docs/data-access/DATA_ACCESS_GUIDE.md` - Detailed guide

Happy analyzing! 🚀

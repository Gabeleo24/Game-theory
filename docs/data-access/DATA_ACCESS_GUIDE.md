# Data Access and Analysis Guide

## Overview

This guide shows you where to find PostgreSQL data and how to access it for preprocessing and analysis. The ADS599 Capstone Soccer Intelligence System stores data in multiple formats and locations.

## 🗄️ **PostgreSQL Data Location**

### **Docker Container Setup**
Your PostgreSQL database runs in a Docker container with the following configuration:

```yaml
# From docker-compose.yml
postgres:
  container_name: soccer-intelligence-db
  ports:
    - "5432:5432"
  environment:
    - POSTGRES_DB=soccer_intelligence
    - POSTGRES_USER=soccerapp
    - POSTGRES_PASSWORD=soccerpass123
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
```

### **Database Schema**
The database contains these main tables:
- `teams` - Team information (67 Champions League teams)
- `players` - Player profiles and details
- `competitions` - League and competition data
- `matches` - Match results and details
- `player_statistics` - Individual player performance metrics
- `team_statistics` - Team performance aggregates
- `shapley_analysis` - Shapley value analysis results

## 📊 **Current Data Locations**

### **1. File-Based Data (JSON)**
```
data/
├── focused/                    # Main dataset (67 Champions League teams)
│   ├── teams/                 # Team-specific data by season
│   ├── players/               # Player statistics by team
│   ├── focused_*_matches_*.json    # Match data by league/season
│   └── focused_*_teams_*.json      # Team data by league/season
├── cache/                     # API response cache
│   ├── team_statistics/       # Cached team stats
│   └── player_statistics/     # Cached player stats
├── analysis/                  # Analysis results
└── processed/                 # Processed datasets
```

### **2. PostgreSQL Database**
- **Host**: `localhost:5432` (when Docker is running)
- **Database**: `soccer_intelligence`
- **User**: `soccerapp`
- **Password**: `soccerpass123`

## 🚀 **Quick Start: Access Your Data**

### **Option 1: Direct Database Access**

#### **Start the Database**
```bash
# Start PostgreSQL container
docker-compose up postgres -d

# Check if it's running
docker-compose ps postgres
```

#### **Connect to Database**
```bash
# Using psql (if installed locally)
psql -h localhost -p 5432 -U soccerapp -d soccer_intelligence

# Using Docker exec
docker exec -it soccer-intelligence-db psql -U soccerapp -d soccer_intelligence

# Using pgAdmin (web interface)
# Navigate to: http://localhost:8080 (if pgAdmin is configured)
```

#### **Basic Queries**
```sql
-- Check available tables
\dt

-- View team data
SELECT team_id, team_name, country FROM teams LIMIT 10;

-- View recent matches
SELECT m.match_date, ht.team_name as home_team, at.team_name as away_team, 
       m.home_goals, m.away_goals
FROM matches m
JOIN teams ht ON m.home_team_id = ht.team_id
JOIN teams at ON m.away_team_id = at.team_id
ORDER BY m.match_date DESC LIMIT 10;

-- Player statistics summary
SELECT p.player_name, ps.goals, ps.assists, ps.rating
FROM player_statistics ps
JOIN players p ON ps.player_id = p.player_id
WHERE ps.season_year = 2023
ORDER BY ps.rating DESC LIMIT 10;
```

### **Option 2: Python Data Access**

#### **Database Connection Script**
```python
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import json
from pathlib import Path

class SoccerDataAccess:
    def __init__(self):
        # Database connection
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'soccer_intelligence',
            'user': 'soccerapp',
            'password': 'soccerpass123'
        }
        self.engine = None
        self.data_dir = Path('data')
    
    def connect_db(self):
        """Connect to PostgreSQL database."""
        connection_string = f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
        self.engine = create_engine(connection_string)
        return self.engine
    
    def get_teams(self):
        """Get all teams from database."""
        query = "SELECT * FROM teams ORDER BY team_name"
        return pd.read_sql(query, self.engine)
    
    def get_player_stats(self, season_year=2023, team_id=None):
        """Get player statistics for a specific season."""
        query = """
        SELECT p.player_name, ps.*, t.team_name
        FROM player_statistics ps
        JOIN players p ON ps.player_id = p.player_id
        JOIN teams t ON ps.team_id = t.team_id
        WHERE ps.season_year = %s
        """
        params = [season_year]
        
        if team_id:
            query += " AND ps.team_id = %s"
            params.append(team_id)
        
        query += " ORDER BY ps.rating DESC"
        return pd.read_sql(query, self.engine, params=params)
    
    def get_match_data(self, season_year=2023, competition_id=None):
        """Get match data for analysis."""
        query = """
        SELECT m.*, ht.team_name as home_team, at.team_name as away_team,
               c.competition_name
        FROM matches m
        JOIN teams ht ON m.home_team_id = ht.team_id
        JOIN teams at ON m.away_team_id = at.team_id
        JOIN competitions c ON m.competition_id = c.competition_id
        WHERE m.season_year = %s
        """
        params = [season_year]
        
        if competition_id:
            query += " AND m.competition_id = %s"
            params.append(competition_id)
        
        query += " ORDER BY m.match_date"
        return pd.read_sql(query, self.engine, params=params)
    
    def load_json_data(self, filename):
        """Load JSON data files."""
        file_path = self.data_dir / 'focused' / filename
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    
    def get_champions_league_teams(self):
        """Get the 67 core Champions League teams."""
        file_path = self.data_dir / 'focused' / 'core_champions_league_teams.json'
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return None

# Usage example
data_access = SoccerDataAccess()
engine = data_access.connect_db()

# Get data for analysis
teams_df = data_access.get_teams()
player_stats_df = data_access.get_player_stats(season_year=2023)
matches_df = data_access.get_match_data(season_year=2023, competition_id=2)  # Champions League

print(f"Teams: {len(teams_df)}")
print(f"Player stats: {len(player_stats_df)}")
print(f"Matches: {len(matches_df)}")
```

### **Option 3: Jupyter Notebook Setup**

#### **Start Development Environment**
```bash
# Start development container with Jupyter
docker-compose --profile development up -d

# Access Jupyter at: http://localhost:8888
```

#### **Sample Notebook Code**
```python
# Cell 1: Setup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import json
from pathlib import Path

# Database connection
engine = create_engine('postgresql://soccerapp:soccerpass123@postgres:5432/soccer_intelligence')

# Cell 2: Load Data
# Get team data
teams_query = "SELECT * FROM teams"
teams_df = pd.read_sql(teams_query, engine)

# Get player statistics
player_stats_query = """
SELECT p.player_name, ps.goals, ps.assists, ps.rating, ps.minutes_played,
       t.team_name, c.competition_name, ps.season_year
FROM player_statistics ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams t ON ps.team_id = t.team_id
JOIN competitions c ON ps.competition_id = c.competition_id
WHERE ps.season_year = 2023
"""
player_stats_df = pd.read_sql(player_stats_query, engine)

# Cell 3: Basic Analysis
print("Dataset Overview:")
print(f"Teams: {len(teams_df)}")
print(f"Player records: {len(player_stats_df)}")
print(f"Competitions: {player_stats_df['competition_name'].nunique()}")

# Cell 4: Visualizations
plt.figure(figsize=(12, 6))

# Goals distribution
plt.subplot(1, 2, 1)
plt.hist(player_stats_df['goals'], bins=20, alpha=0.7)
plt.title('Goals Distribution')
plt.xlabel('Goals')
plt.ylabel('Frequency')

# Rating vs Goals
plt.subplot(1, 2, 2)
plt.scatter(player_stats_df['goals'], player_stats_df['rating'], alpha=0.6)
plt.title('Rating vs Goals')
plt.xlabel('Goals')
plt.ylabel('Rating')

plt.tight_layout()
plt.show()
```

## 📈 **Data Analysis Examples**

### **1. Team Performance Analysis**
```python
def analyze_team_performance(team_id, season_year=2023):
    """Analyze team performance across competitions."""
    query = """
    SELECT ts.*, c.competition_name
    FROM team_statistics ts
    JOIN competitions c ON ts.competition_id = c.competition_id
    WHERE ts.team_id = %s AND ts.season_year = %s
    """
    return pd.read_sql(query, engine, params=[team_id, season_year])

# Example: Analyze Manchester City (team_id = 50)
man_city_stats = analyze_team_performance(50, 2023)
print(man_city_stats)
```

### **2. Player Comparison**
```python
def compare_players(player_ids, season_year=2023):
    """Compare multiple players' performance."""
    query = """
    SELECT p.player_name, ps.goals, ps.assists, ps.rating, 
           ps.minutes_played, t.team_name
    FROM player_statistics ps
    JOIN players p ON ps.player_id = p.player_id
    JOIN teams t ON ps.team_id = t.team_id
    WHERE ps.player_id = ANY(%s) AND ps.season_year = %s
    """
    return pd.read_sql(query, engine, params=[player_ids, season_year])

# Example: Compare top players
top_players = compare_players([1, 2, 3], 2023)
print(top_players)
```

### **3. Shapley Value Analysis**
```python
def get_shapley_analysis(team_id=None, season_year=2023):
    """Get Shapley value analysis results."""
    query = """
    SELECT sa.*, p.player_name, t.team_name
    FROM shapley_analysis sa
    JOIN players p ON sa.player_id = p.player_id
    JOIN teams t ON sa.team_id = t.team_id
    WHERE sa.season_year = %s
    """
    params = [season_year]
    
    if team_id:
        query += " AND sa.team_id = %s"
        params.append(team_id)
    
    query += " ORDER BY sa.shapley_value DESC"
    return pd.read_sql(query, engine, params=params)

# Get Shapley analysis
shapley_results = get_shapley_analysis(season_year=2023)
print(shapley_results.head())
```

## 🔧 **Data Preprocessing Pipeline**

### **Create Preprocessing Script**
```python
# scripts/preprocessing/data_preprocessor.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sqlalchemy import create_engine

class SoccerDataPreprocessor:
    def __init__(self, db_connection_string):
        self.engine = create_engine(db_connection_string)
        self.scaler = StandardScaler()
        self.label_encoders = {}
    
    def load_and_preprocess(self, season_year=2023):
        """Load and preprocess data for machine learning."""
        
        # Load player statistics
        player_query = """
        SELECT ps.*, p.nationality, t.country as team_country
        FROM player_statistics ps
        JOIN players p ON ps.player_id = p.player_id
        JOIN teams t ON ps.team_id = t.team_id
        WHERE ps.season_year = %s AND ps.minutes_played > 0
        """
        df = pd.read_sql(player_query, self.engine, params=[season_year])
        
        # Handle missing values
        numeric_columns = ['goals', 'assists', 'shots_total', 'passes_total', 'rating']
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        # Create derived features
        df['goals_per_minute'] = df['goals'] / (df['minutes_played'] + 1)
        df['assists_per_minute'] = df['assists'] / (df['minutes_played'] + 1)
        df['pass_accuracy'] = df['passes_completed'] / (df['passes_total'] + 1)
        
        # Encode categorical variables
        categorical_columns = ['position', 'nationality', 'team_country']
        for col in categorical_columns:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].fillna('Unknown'))
                self.label_encoders[col] = le
        
        # Scale numerical features
        feature_columns = ['goals', 'assists', 'rating', 'goals_per_minute', 'assists_per_minute']
        df[feature_columns] = self.scaler.fit_transform(df[feature_columns])
        
        return df
    
    def prepare_for_shapley(self, df):
        """Prepare data specifically for Shapley analysis."""
        # Select features for Shapley analysis
        shapley_features = [
            'goals', 'assists', 'shots_total', 'shots_on_target',
            'passes_total', 'passes_completed', 'tackles_total',
            'minutes_played', 'rating'
        ]
        
        return df[shapley_features].fillna(0)

# Usage
preprocessor = SoccerDataPreprocessor('postgresql://soccerapp:soccerpass123@localhost:5432/soccer_intelligence')
processed_data = preprocessor.load_and_preprocess(2023)
shapley_data = preprocessor.prepare_for_shapley(processed_data)

print(f"Processed data shape: {processed_data.shape}")
print(f"Shapley data shape: {shapley_data.shape}")
```

## 🎯 **Recommended Next Steps**

### **1. Start Database**
```bash
# Start PostgreSQL
docker-compose up postgres -d

# Verify it's running
docker-compose ps
```

### **2. Load Sample Data**
```bash
# Run data collection to populate database
python scripts/data_collection/comprehensive_team_statistics_collector.py --max-teams 5

# Or load from existing JSON files
python scripts/data_loading/json_to_postgres.py
```

### **3. Begin Analysis**
```bash
# Start Jupyter for interactive analysis
docker-compose --profile development up jupyter -d

# Access at: http://localhost:8888
```

### **4. Run Preprocessing**
```python
# In Jupyter or Python script
from scripts.preprocessing.data_preprocessor import SoccerDataPreprocessor

preprocessor = SoccerDataPreprocessor('postgresql://soccerapp:soccerpass123@localhost:5432/soccer_intelligence')
data = preprocessor.load_and_preprocess(2023)

# Now ready for machine learning, Shapley analysis, etc.
```

## 📚 **Additional Resources**

- **Database Schema**: `docker/postgres/init.sql`
- **Configuration**: `config/` directory
- **Sample Data**: `data/focused/` directory
- **Analysis Examples**: `notebooks/` directory (if available)
- **API Documentation**: `docs/data-collection/` folder

This setup gives you multiple ways to access and analyze your soccer intelligence data, from direct SQL queries to Python-based machine learning pipelines!

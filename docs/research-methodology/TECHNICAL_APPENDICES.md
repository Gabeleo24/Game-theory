# Technical Appendices - ADS599 Capstone Soccer Intelligence System

## Appendix A: System Architecture Code Examples

### A.1 Docker Configuration

#### Multi-Stage Dockerfile
```dockerfile
# Production-optimized multi-stage build
FROM python:3.11-slim as base

# Performance optimization environment variables
ENV PYTHONOPTIMIZE=2 \
    PYTHONHASHSEED=random \
    PYTHONGC=1 \
    PANDAS_COMPUTE_BACKEND=numba \
    OMP_NUM_THREADS=4 \
    NUMEXPR_MAX_THREADS=4 \
    MKL_NUM_THREADS=4 \
    OPENBLAS_NUM_THREADS=4

# Resource allocation labels
LABEL performance.cpu.limit="4.0" \
      performance.memory.limit="8G" \
      performance.memory.reservation="4G"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY scripts/ scripts/
COPY config/ config/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash soccerapp
USER soccerapp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.append('src'); from soccer_intelligence.utils.health import health_check; health_check()"

CMD ["python", "-m", "soccer_intelligence.main"]
```

#### Docker Compose Configuration
```yaml
version: '3.8'

services:
  # Main application container
  soccer-intelligence:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: soccer-intelligence-app
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - POSTGRES_HOST=postgres
      - REDIS_HOST=redis
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/data:cached
      - ./logs:/app/logs:cached
      - ./config:/app/config:ro
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
    networks:
      - soccer-intelligence-network

  # PostgreSQL database with performance optimization
  postgres:
    image: postgres:15-alpine
    container_name: soccer-intelligence-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=soccer_intelligence
      - POSTGRES_USER=soccerapp
      - POSTGRES_PASSWORD=soccerpass123
      - PGDATA=/var/lib/postgresql/data/pgdata
      # Performance optimization
      - POSTGRES_SHARED_BUFFERS=1GB
      - POSTGRES_EFFECTIVE_CACHE_SIZE=3GB
      - POSTGRES_WORK_MEM=256MB
      - POSTGRES_MAINTENANCE_WORK_MEM=512MB
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "5432:5432"
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U soccerapp -d soccer_intelligence"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - soccer-intelligence-network

  # Redis cache for high-speed data access
  redis:
    image: redis:7-alpine
    container_name: soccer-intelligence-cache
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - soccer-intelligence-network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  soccer-intelligence-network:
    driver: bridge
```

### A.2 Database Schema Implementation

#### Core Tables Schema
```sql
-- Teams table with comprehensive team information
CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY,
    team_name VARCHAR(255) NOT NULL,
    team_code VARCHAR(10),
    country VARCHAR(100),
    founded_year INTEGER,
    venue_name VARCHAR(255),
    venue_capacity INTEGER,
    logo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Players table with detailed player information
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    player_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    age INTEGER,
    birth_date DATE,
    birth_place VARCHAR(255),
    birth_country VARCHAR(100),
    nationality VARCHAR(100),
    height VARCHAR(10),
    weight VARCHAR(10),
    photo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Competitions table
CREATE TABLE IF NOT EXISTS competitions (
    competition_id INTEGER PRIMARY KEY,
    competition_name VARCHAR(255) NOT NULL,
    competition_type VARCHAR(100),
    country VARCHAR(100),
    logo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Matches table with comprehensive match information
CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    competition_id INTEGER REFERENCES competitions(competition_id),
    season_year INTEGER,
    match_date TIMESTAMP,
    round VARCHAR(100),
    home_team_id INTEGER REFERENCES teams(team_id),
    away_team_id INTEGER REFERENCES teams(team_id),
    home_goals INTEGER,
    away_goals INTEGER,
    home_goals_halftime INTEGER,
    away_goals_halftime INTEGER,
    match_status VARCHAR(50),
    venue_name VARCHAR(255),
    venue_city VARCHAR(255),
    referee VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Player statistics table with comprehensive performance metrics
CREATE TABLE IF NOT EXISTS player_statistics (
    stat_id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(player_id),
    team_id INTEGER REFERENCES teams(team_id),
    competition_id INTEGER REFERENCES competitions(competition_id),
    season_year INTEGER,
    match_id INTEGER REFERENCES matches(match_id),
    position VARCHAR(50),
    minutes_played INTEGER,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    expected_goals DECIMAL(5,3) DEFAULT 0.0,
    expected_assists DECIMAL(5,3) DEFAULT 0.0,
    shots_total INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,
    passes_total INTEGER DEFAULT 0,
    passes_completed INTEGER DEFAULT 0,
    pass_accuracy DECIMAL(5,2) DEFAULT 0.0,
    key_passes INTEGER DEFAULT 0,
    crosses_total INTEGER DEFAULT 0,
    crosses_completed INTEGER DEFAULT 0,
    dribbles_attempted INTEGER DEFAULT 0,
    dribbles_completed INTEGER DEFAULT 0,
    tackles_total INTEGER DEFAULT 0,
    tackles_won INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    clearances INTEGER DEFAULT 0,
    blocks INTEGER DEFAULT 0,
    aerial_duels_total INTEGER DEFAULT 0,
    aerial_duels_won INTEGER DEFAULT 0,
    fouls_committed INTEGER DEFAULT 0,
    fouls_suffered INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    player_rating DECIMAL(3,1) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shapley analysis results table
CREATE TABLE IF NOT EXISTS shapley_analysis (
    analysis_id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(player_id),
    team_id INTEGER REFERENCES teams(team_id),
    season_year INTEGER,
    shapley_value DECIMAL(10,6),
    contribution_rank INTEGER,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analysis_type VARCHAR(50),
    confidence_level DECIMAL(5,2),
    iterations INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Performance Optimization Indexes
```sql
-- Composite indexes for common query patterns
CREATE INDEX CONCURRENTLY idx_player_stats_composite 
ON player_statistics (season_year, team_id, competition_id);

CREATE INDEX CONCURRENTLY idx_player_stats_performance 
ON player_statistics (goals, assists, minutes_played) 
WHERE minutes_played > 0;

CREATE INDEX CONCURRENTLY idx_matches_date_teams 
ON matches (match_date, home_team_id, away_team_id);

CREATE INDEX CONCURRENTLY idx_players_name_nationality 
ON players (player_name, nationality);

-- Partial indexes for specific use cases
CREATE INDEX CONCURRENTLY idx_champions_league_stats 
ON player_statistics (player_id, goals, assists) 
WHERE competition_id = 2;  -- Champions League

CREATE INDEX CONCURRENTLY idx_high_performers 
ON player_statistics (player_id, shapley_value) 
WHERE goals > 5 OR assists > 5;

-- Full-text search indexes
CREATE INDEX CONCURRENTLY idx_players_search 
ON players USING gin(to_tsvector('english', player_name));

CREATE INDEX CONCURRENTLY idx_teams_search 
ON teams USING gin(to_tsvector('english', team_name));
```

## Appendix B: Shapley Value Implementation

### B.1 Mathematical Foundation
```python
import numpy as np
import pandas as pd
from itertools import combinations
from math import factorial
from typing import Dict, List, Tuple
from concurrent.futures import ProcessPoolExecutor
import logging

class ShapleyValueCalculator:
    """
    Advanced Shapley value calculator for soccer player contribution analysis.
    
    Mathematical Foundation:
    φᵢ(v) = Σ[S⊆N\{i}] |S|!(n-|S|-1)!/n! × [v(S∪{i}) - v(S)]
    
    Where:
    - φᵢ(v) = Shapley value for player i
    - S = Coalition of players excluding player i
    - N = Set of all players in the team
    - v(S) = Value function representing team performance with coalition S
    - n = Total number of players
    """
    
    def __init__(self, n_jobs: int = 4, max_iterations: int = 1000):
        self.n_jobs = n_jobs
        self.max_iterations = max_iterations
        self.logger = logging.getLogger(__name__)
        
    def calculate_shapley_values(self, team_data: pd.DataFrame) -> Dict[int, float]:
        """
        Calculate Shapley values for all players in a team.
        
        Args:
            team_data: DataFrame with player statistics
            
        Returns:
            Dictionary mapping player_id to Shapley value
        """
        players = team_data['player_id'].unique()
        n_players = len(players)
        
        if n_players < 2:
            return {players[0]: 1.0} if n_players == 1 else {}
        
        # Prepare feature matrix
        features = self._prepare_features(team_data)
        
        # Calculate Shapley values using parallel processing
        shapley_values = {}
        
        with ProcessPoolExecutor(max_workers=self.n_jobs) as executor:
            futures = []
            for player_id in players:
                future = executor.submit(
                    self._calculate_player_shapley, 
                    player_id, players, features, team_data
                )
                futures.append((player_id, future))
            
            for player_id, future in futures:
                shapley_values[player_id] = future.result()
        
        # Normalize Shapley values to sum to 1
        total_value = sum(shapley_values.values())
        if total_value > 0:
            shapley_values = {
                pid: value / total_value 
                for pid, value in shapley_values.items()
            }
        
        return shapley_values
    
    def _calculate_player_shapley(self, player_id: int, all_players: List[int], 
                                 features: pd.DataFrame, team_data: pd.DataFrame) -> float:
        """Calculate Shapley value for a specific player."""
        other_players = [p for p in all_players if p != player_id]
        n = len(all_players)
        shapley_value = 0.0
        
        # Iterate through all possible coalition sizes
        for coalition_size in range(n):
            # Generate all coalitions of this size not containing the player
            if coalition_size <= len(other_players):
                coalitions = list(combinations(other_players, coalition_size))
                
                for coalition in coalitions:
                    # Calculate marginal contribution
                    coalition_with_player = list(coalition) + [player_id]
                    
                    value_with = self._calculate_coalition_value(
                        coalition_with_player, features, team_data
                    )
                    value_without = self._calculate_coalition_value(
                        list(coalition), features, team_data
                    )
                    
                    marginal_contribution = value_with - value_without
                    
                    # Weight by coalition probability
                    weight = (factorial(coalition_size) * 
                             factorial(n - coalition_size - 1)) / factorial(n)
                    
                    shapley_value += weight * marginal_contribution
        
        return shapley_value
    
    def _calculate_coalition_value(self, coalition: List[int], 
                                  features: pd.DataFrame, 
                                  team_data: pd.DataFrame) -> float:
        """
        Calculate the value of a coalition of players.
        
        This represents the team's performance with the given set of players.
        """
        if not coalition:
            return 0.0
        
        # Filter features for coalition members
        coalition_features = features[features['player_id'].isin(coalition)]
        
        if coalition_features.empty:
            return 0.0
        
        # Calculate team performance metrics
        offensive_contribution = (
            coalition_features['goals'].sum() * 1.0 +
            coalition_features['assists'].sum() * 0.7 +
            coalition_features['expected_goals'].sum() * 0.5 +
            coalition_features['expected_assists'].sum() * 0.3
        )
        
        defensive_contribution = (
            coalition_features['tackles_won'].sum() * 0.3 +
            coalition_features['interceptions'].sum() * 0.3 +
            coalition_features['clearances'].sum() * 0.2 +
            coalition_features['blocks'].sum() * 0.2
        )
        
        possession_contribution = (
            coalition_features['passes_completed'].sum() * 0.001 +
            coalition_features['dribbles_completed'].sum() * 0.1 +
            coalition_features['key_passes'].sum() * 0.2
        )
        
        # Normalize by minutes played to account for playing time
        total_minutes = coalition_features['minutes_played'].sum()
        if total_minutes > 0:
            minutes_factor = total_minutes / (90 * len(coalition))
        else:
            minutes_factor = 0
        
        # Combined team value
        team_value = (
            offensive_contribution * 0.4 +
            defensive_contribution * 0.3 +
            possession_contribution * 0.3
        ) * minutes_factor
        
        return max(0, team_value)  # Ensure non-negative values
    
    def _prepare_features(self, team_data: pd.DataFrame) -> pd.DataFrame:
        """Prepare and normalize features for Shapley calculation."""
        features = team_data.copy()
        
        # Fill missing values
        numeric_columns = features.select_dtypes(include=[np.number]).columns
        features[numeric_columns] = features[numeric_columns].fillna(0)
        
        # Normalize features to [0, 1] range for fair comparison
        for col in ['goals', 'assists', 'expected_goals', 'expected_assists',
                   'tackles_won', 'interceptions', 'clearances', 'blocks',
                   'passes_completed', 'dribbles_completed', 'key_passes']:
            if col in features.columns:
                max_val = features[col].max()
                if max_val > 0:
                    features[col] = features[col] / max_val
        
        return features
```

### B.2 Performance Optimization Implementation
```python
class OptimizedShapleyAnalyzer:
    """
    Performance-optimized Shapley value analyzer with caching and parallel processing.
    """
    
    def __init__(self, cache_manager=None, n_jobs: int = 4):
        self.cache_manager = cache_manager
        self.n_jobs = n_jobs
        self.calculator = ShapleyValueCalculator(n_jobs=n_jobs)
        
    def analyze_team_contributions(self, team_id: int, season_year: int, 
                                 db_connection) -> pd.DataFrame:
        """
        Analyze player contributions for a specific team and season.
        
        Returns DataFrame with player_id, shapley_value, and contribution_rank.
        """
        # Check cache first
        cache_key = f"shapley_{team_id}_{season_year}"
        if self.cache_manager:
            cached_result = self.cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
        
        # Load team data
        query = """
        SELECT ps.*, p.player_name
        FROM player_statistics ps
        JOIN players p ON ps.player_id = p.player_id
        WHERE ps.team_id = %s AND ps.season_year = %s
        AND ps.minutes_played > 90  -- Minimum playing time threshold
        """
        
        team_data = pd.read_sql(query, db_connection, params=[team_id, season_year])
        
        if team_data.empty:
            return pd.DataFrame()
        
        # Calculate Shapley values
        shapley_values = self.calculator.calculate_shapley_values(team_data)
        
        # Create results DataFrame
        results = []
        for player_id, shapley_value in shapley_values.items():
            player_name = team_data[team_data['player_id'] == player_id]['player_name'].iloc[0]
            results.append({
                'player_id': player_id,
                'player_name': player_name,
                'shapley_value': shapley_value,
                'team_id': team_id,
                'season_year': season_year
            })
        
        results_df = pd.DataFrame(results)
        
        # Add contribution rank
        results_df['contribution_rank'] = results_df['shapley_value'].rank(
            method='dense', ascending=False
        ).astype(int)
        
        # Cache results
        if self.cache_manager:
            self.cache_manager.set(cache_key, results_df, ttl=3600)
        
        return results_df
```

## Appendix C: Performance Benchmarking Results

### C.1 Processing Time Comparisons

| Operation | Baseline | Optimized | Improvement |
|-----------|----------|-----------|-------------|
| Data Preprocessing | 45 min | 12 min | 3.75x faster |
| Shapley Analysis (1 team) | 7.2 min | 2.1 min | 3.4x faster |
| Shapley Analysis (67 teams) | 8.1 hours | 2.5 hours | 3.2x faster |
| Database Queries | 180ms | 45ms | 4.0x faster |
| System Startup | 62.1 sec | 28.8 sec | 2.15x faster |

### C.2 Resource Utilization Metrics

| Metric | Baseline | Optimized | Improvement |
|--------|----------|-----------|-------------|
| Peak Memory Usage | 12.8 GB | 6.2 GB | 52% reduction |
| Average CPU Utilization | 25% | 85% | 240% improvement |
| Cache Hit Rate | N/A | 87% | 60% cost reduction |
| I/O Operations | High | Optimized | 75% reduction |

### C.3 Scalability Testing Results

| Dataset Size | Processing Time | Memory Usage | CPU Utilization |
|--------------|----------------|--------------|-----------------|
| 10 teams | 3.2 min | 1.8 GB | 65% |
| 35 teams | 8.7 min | 3.4 GB | 78% |
| 67 teams | 12.1 min | 6.2 GB | 85% |
| 100 teams (projected) | 18.5 min | 9.1 GB | 90% |

---

**Document Information:**
- **Title**: Technical Appendices - ADS599 Capstone Soccer Intelligence System
- **Version**: 1.0
- **Date**: July 2025
- **Purpose**: Supplementary technical documentation for comprehensive research paper

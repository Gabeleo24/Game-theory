# Soccer Intelligence System - Real Madrid 2023-2024

A focused soccer analytics system for analyzing Real Madrid's 2023-2024 season performance with match-level player statistics.

## [SUCCESS] Features

- **Match-Level Player Statistics**: Individual player performance for every game
- **Comprehensive Team Analysis**: All 27 teams Real Madrid faced during 2023-2024
- **Multi-Competition Coverage**: La Liga, UEFA Champions League, Copa del Rey
- **Beautiful Data Display**: Elche-style player statistics tables

## [DATA] Dataset

- **52 Matches** across all competitions
- **2,209 Player Records** from 27 teams
- **Complete Statistics**: Goals, assists, shots, passes, tackles, cards, ratings
- **Real Madrid Focus**: Detailed analysis of Real Madrid's season

## Quick Start

### 1. Start Database
```bash
docker-compose up -d
```

### 2. Load Data
```bash
python scripts/data_loading/simple_match_loader.py
```

### 3. View Elche-Style Statistics (Professional Display)
```bash
# View comprehensive Elche-style player statistics
python scripts/analysis/view_elche_stats.py

# Or use the full professional version
python scripts/analysis/elche_style_professional.py
```

### 4. View Match Statistics
```bash
# List all matches
python scripts/analysis/match_player_viewer.py

# View specific match (e.g., Champions League Final)
python scripts/analysis/match_player_viewer.py 4
```

### 5. View Team Rosters
```bash
# View all teams and players
python scripts/analysis/comprehensive_player_roster.py

# View Real Madrid roster
python scripts/analysis/comprehensive_player_roster.py "Real Madrid"
```

## [FILES] Project Structure

```
├── data/focused/players/real_madrid_2023_2024/    # Match data
├── scripts/
│   ├── data_loading/simple_match_loader.py        # Load match data
│   └── analysis/
│       ├── view_elche_stats.py                    # Elche-style statistics (Quick)
│       ├── elche_style_professional.py            # Professional Elche display
│       ├── match_player_viewer.py                 # View match stats
│       └── comprehensive_player_roster.py         # View team rosters
├── config/                                        # Configuration files
├── docker-compose.yml                             # Database setup
└── README.md                                      # This file
```

## [RESULT] Key Results

- **Top Scorer**: Jude Bellingham (12 goals)
- **Top Assister**: Vinícius Júnior (7 assists)  
- **Highest Rated**: Lucas Vázquez (7.83 avg rating)
- **Complete Season**: All 52 matches analyzed

## [FIXED] Requirements

- Python 3.8+
- Docker & Docker Compose
- PostgreSQL (via Docker)

## [STATS] Analysis Capabilities

- Individual match player performance
- Season-long player statistics
- Team-by-team roster analysis
- Cross-competition performance tracking
- Performance rating analysis

---

**Real Madrid 2023-2024 Season**: Champions League Winners [SUCCESS] 
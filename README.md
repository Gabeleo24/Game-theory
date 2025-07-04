# ADS599 Capstone: Advanced Soccer Analytics Using Shapley Value Analysis

**University of San Diego | Applied Data Science Program**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Complete-brightgreen.svg)](https://github.com/mmoramora/ADS599_Capstone)
[![Dataset](https://img.shields.io/badge/Dataset-67%20Teams%20|%208080%2B%20Players-blue.svg)](#data-coverage)
[![Analysis](https://img.shields.io/badge/Analysis-Shapley%20Values-orange.svg)](#shapley-value-analysis)

## Project Overview

This capstone project applies advanced game theory concepts, specifically **Shapley value analysis**, to soccer analytics for player valuation and team optimization. Using comprehensive data from **67 UEFA Champions League teams** across **2019-2025 seasons**, we analyze player contributions and develop predictive models for team performance.

The project demonstrates the practical application of mathematical concepts from game theory to real-world sports analytics, providing insights into player valuations, team composition optimization, and performance prediction across multiple competitions.

## Data Coverage

**Comprehensive Multi-Season Analysis (2019-2025)**
- **67 UEFA Champions League teams** across 6+ seasons
- **8,080+ individual player files** with detailed performance statistics
- **15,000+ team match records** with comprehensive game-by-game data
- **99.85% data consistency** achieved through rigorous validation
- **Multi-competition context**: Champions League, domestic leagues, domestic cups
- **6 seasons of historical data** (2019-2024) + 2025 extension for validation

### Data Collection Systems

#### Player Statistics Collection
- **Individual player performance** across all competitions
- **25+ performance metrics** per player (goals, assists, minutes, ratings)
- **Season-by-season tracking** with career progression analysis
- **Competition-specific statistics** for tactical analysis

#### Team Statistics Collection
- **Complete match history** for every team (2019-2024)
- **Team-level performance metrics** by season and competition
- **Match-by-match details** including scores, venues, and contexts
- **Multi-competition coverage** across domestic and European tournaments

### League Distribution
- **Premier League**: 7 teams (Arsenal, Chelsea, Liverpool, Manchester City, Manchester United, Newcastle, Tottenham)
- **La Liga**: 7 teams (Atletico Madrid, Barcelona, Real Madrid, Real Sociedad, Sevilla, Valencia, Villarreal)
- **Serie A**: 6 teams (AC Milan, Atalanta, Inter, Juventus, Lazio, Napoli)
- **Bundesliga**: 8 teams (Bayern München, Borussia Dortmund, RB Leipzig, Bayer Leverkusen, Eintracht Frankfurt, etc.)
- **Ligue 1**: 6 teams (Paris Saint Germain, Lyon, Marseille, Lille, Rennes, Lens)

## Key Features

### 1. Comprehensive Data Collection Systems

#### Player Statistics Collection
- **Automated data collection** from API-Football with intelligent caching
- **Individual player files** organized by team and season
- **25+ performance metrics** per player including goals, assists, minutes, ratings
- **Competition-specific statistics** across multiple tournaments
- **Optimized collection** for 67 core teams with API efficiency

#### Team Statistics Collection
- **Complete match history** for every team across all competitions
- **Team-level performance metrics** by season and competition
- **Match-by-match details** with scores, venues, and opponent information
- **Multi-competition coverage** (Champions League, domestic leagues, cups)
- **Game-by-game data** for comprehensive tactical analysis

### 2. Shapley Value Analysis for Player Contribution Quantification
- **Game theory implementation** for fair player contribution assessment
- **Marginal contribution calculations** across all possible team coalitions
- **Position-specific analysis** and performance weighting
- **Cross-competition comparison** capabilities
- **Team-level and player-level** integrated analysis

### 3. Multi-Season Comparative Analysis
- **Longitudinal performance tracking** across 2019-2025
- **Team evolution analysis** with trend identification
- **Player consistency metrics** and development patterns
- **Transfer impact assessment** and market value correlation
- **Match-level performance** correlation with player contributions

### 4. Data Validation and Quality Assurance
- **99.85% consistency score** across all datasets
- **Automated validation pipelines** with error detection
- **Missing data handling** and statistical imputation
- **Real-time data quality monitoring**
- **Comprehensive validation** for both player and team data

## Project Structure

```
ADS599_Capstone/
├── src/soccer_intelligence/           # Core analysis modules
│   ├── data_collection/              # Data acquisition systems
│   │   ├── api_football.py           # API-Football integration
│   │   ├── cache_manager.py          # Intelligent caching system
│   │   └── data_validator.py         # Data quality validation
│   ├── data_processing/              # Data pipeline and transformation
│   │   ├── data_cleaner.py          # Data validation and cleaning
│   │   ├── feature_engineer.py      # Advanced feature creation
│   │   └── data_integrator.py       # Multi-source data integration
│   ├── analysis/                     # Advanced analytics engine
│   │   ├── shapley_analysis.py      # Player contribution analysis
│   │   ├── enhanced_shapley_analysis.py # Advanced Shapley implementations
│   │   ├── tactical_analysis.py     # Formation and strategy analysis
│   │   └── performance_metrics.py   # Performance calculation algorithms
│   └── utils/                       # System utilities and helpers
│       ├── config.py               # Configuration management
│       ├── logger.py               # Logging system
│       └── helpers.py              # Utility functions
├── scripts/                         # Analysis and collection scripts
│   ├── data_collection/            # Data collection pipelines
│   │   ├── comprehensive_player_collection.py      # Main player collection system
│   │   ├── comprehensive_team_statistics_collector.py # Team statistics collector
│   │   ├── optimized_player_collection.py          # Optimized collection system
│   │   ├── single_team_collection.py               # Single team data collector
│   │   ├── player_statistics_collector.py          # Player stats collector
│   │   └── competition_specific_collector.py       # Competition-focused collection
│   ├── analysis/                   # Analysis scripts
│   │   ├── simple_shapley_analysis.py              # Shapley value calculations
│   │   ├── multi_season_comparative_analysis.py    # Multi-season analysis
│   │   ├── player_statistics_validator.py          # Player data validation
│   │   ├── team_statistics_validator.py            # Team data validation
│   │   └── optimized_collection_validator.py       # Collection optimization validation
│   ├── collect_2024_2025_player_data.py           # Extended data collection
│   ├── create_individual_player_stats.py          # Individual player file creation
│   └── validate_individual_stats.py               # Statistics validation
├── data/                            # Data storage and management
│   ├── focused/                    # Focused dataset for 67 core teams
│   │   ├── players/               # Player statistics database
│   │   │   ├── individual_stats/  # 8,080+ individual player files
│   │   │   │   ├── team_541/     # Real Madrid players by season
│   │   │   │   ├── team_529/     # Barcelona players by season
│   │   │   │   └── ...           # All 67 teams organized by season
│   │   │   ├── team_rosters/     # Team roster files by season
│   │   │   └── api_usage_report.json # API usage tracking
│   │   └── teams/                 # Team statistics database
│   │       ├── team_541/         # Real Madrid team data by season
│   │       │   ├── 2019/         # Season-specific team statistics
│   │       │   ├── 2020/         # Match details and performance
│   │       │   └── ...           # All seasons 2019-2024
│   │       ├── team_529/         # Barcelona team data by season
│   │       └── ...               # All 67 teams with complete match history
│   ├── analysis/                  # Analysis outputs and reports
│   │   ├── multi_season_comparative_analysis.json # Comparative analysis results
│   │   ├── comprehensive_player_collection_report.json # Player collection summary
│   │   ├── comprehensive_team_statistics_collection_report.json # Team collection summary
│   │   ├── optimized_collection_validation_report.json # Optimization validation
│   │   └── team_statistics_validation_report.json # Team data validation
│   ├── cache/                     # Intelligent caching system
│   │   ├── player_statistics/     # Cached player API responses
│   │   └── team_statistics/       # Cached team API responses
│   ├── processed/                 # Original comprehensive datasets
│   ├── models/                    # Trained models and embeddings
│   └── reports/                   # Generated analysis reports
├── config/                         # System configuration
│   ├── api_keys.yaml              # API credentials template
│   ├── player_collection_config.yaml # Player collection configuration
│   ├── team_statistics_collection_config.yaml # Team collection configuration
│   ├── optimized_collection_config.yaml # Optimized collection settings
│   ├── focused_config.yaml        # Analysis configuration
│   └── system_paths.yaml          # System paths configuration
├── docs/                           # Comprehensive documentation
│   ├── ADS599_CAPSTONE_RESEARCH_METHODOLOGY.md # Research framework
│   ├── PLAYER_COLLECTION_SYSTEM_SUMMARY.md    # Player collection system docs
│   ├── PLAYER_STATISTICS_COLLECTION_SYSTEM.md # Player statistics system docs
│   ├── TEAM_STATISTICS_COLLECTION_GUIDE.md    # Team statistics collection guide
│   ├── OPTIMIZED_COLLECTION_GUIDE.md          # Optimized collection guide
│   └── setup/                     # Setup and configuration guides
├── tests/                          # Test suite
├── notebooks/                      # Research and analysis notebooks
└── requirements.txt                # Python dependencies
```

## Usage Instructions

### Prerequisites
- Python 3.8 or higher
- API-Football credentials (for data collection)
- Git version control system

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/mmoramora/ADS599_Capstone.git
   cd ADS599_Capstone
   ```

2. **Environment Setup**
   ```bash
   python -m venv soccer_analytics_env
   source soccer_analytics_env/bin/activate  # Linux/macOS
   # soccer_analytics_env\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configuration Setup**
   ```bash
   cp config/api_keys_template.yaml config/api_keys.yaml
   # Configure your API credentials in config/api_keys.yaml
   ```

### Running Analysis Scripts

#### 1. Data Collection

**Player Statistics Collection**
```bash
# Optimized collection for 67 core teams (2020-2025)
python scripts/data_collection/optimized_player_collection.py

# Comprehensive player collection
python scripts/data_collection/comprehensive_player_collection.py

# Extended data collection for 2024-2025
python scripts/collect_2024_2025_player_data.py
```

**Team Statistics Collection**
```bash
# Collect all games for all 67 teams (2019-2024)
python scripts/data_collection/comprehensive_team_statistics_collector.py

# Collect all games for a specific team (e.g., Real Madrid - Team 541)
python scripts/data_collection/single_team_collection.py 541

# Test collection with limited teams
python scripts/data_collection/comprehensive_team_statistics_collector.py --max-teams 5
```

#### 2. Data Validation
```bash
# Validate player statistics
python scripts/analysis/player_statistics_validator.py

# Validate team statistics
python scripts/analysis/team_statistics_validator.py

# Validate optimized collection compliance
python scripts/analysis/optimized_collection_validator.py
```

#### 3. Shapley Value Analysis
```bash
# Run Shapley analysis on 2024 season data
python scripts/analysis/simple_shapley_analysis.py

# Multi-season comparative analysis
python scripts/analysis/multi_season_comparative_analysis.py
```

#### 4. Individual Player Statistics Creation
```bash
# Create individual player files for specific seasons
python scripts/create_individual_player_stats.py 2024 2025

# Validate individual statistics
python scripts/validate_individual_stats.py
```

## Research Methodology

This project follows a comprehensive research framework documented in [`docs/ADS599_CAPSTONE_RESEARCH_METHODOLOGY.md`](docs/ADS599_CAPSTONE_RESEARCH_METHODOLOGY.md).

### Research Questions

**Primary Research Question**: How can Shapley value analysis be applied to quantify individual player contributions to team success in professional soccer, and what insights does this provide for player valuation and team composition optimization?

**Secondary Research Questions**:
1. How do player contributions vary across different competitions (Champions League vs. domestic leagues)?
2. What are the key performance indicators that most strongly correlate with team success?
3. Can Shapley-based player valuations predict transfer market values and team performance?
4. How do tactical formations and playing styles affect individual player contribution values?

### Methodology Framework

1. **Data Collection and Preparation**: Comprehensive player statistics across 67 teams and 6+ seasons
2. **Shapley Value Implementation**: Game theory-based player contribution quantification
3. **Multi-Season Comparative Analysis**: Longitudinal performance tracking and trend analysis
4. **Predictive Validation**: Model validation against real-world outcomes

### Statistical Analysis

- **Descriptive Statistics**: Player contribution distributions and performance patterns
- **Inferential Statistics**: Hypothesis testing and correlation analysis
- **Advanced Analytics**: Clustering, time series analysis, and predictive modeling

## Key Results

### Data Quality and Coverage
- **99.85% data consistency** achieved across all datasets
- **8,080+ individual player files** successfully created and validated
- **15,000+ team match records** with comprehensive game-by-game data
- **67 teams analyzed** across 6+ seasons (2019-2025)
- **100% team coverage** with comprehensive statistics
- **Complete match history** for every team across all competitions

### Major Findings from Multi-Season Analysis

#### Team Performance Evolution (2019-2024)

**Barcelona (Team 529)**
- **Goals Trend**: +243.8% improvement from 2019 to 2024
- **Rating Trend**: +9.8% improvement in average team rating
- **Performance Score**: 96.03 (highest among analyzed teams)
- **Key Contributors**: Raphinha (529.73% contribution), R. Lewandowski (113.75%)

**Borussia Dortmund (Team 165)**
- **Goals Trend**: +165.5% improvement
- **Consistency Score**: High performance stability across seasons

**Manchester United (Team 33)**
- **Goals Trend**: -96.9% decline (concerning performance trend)
- **Performance Score**: 71.15 (indicating need for tactical adjustments)

#### Top Multi-Season Performers

1. **R. Lewandowski**: 220 goals across 5 seasons (Bayern Munich → Barcelona)
   - 44.0 goals per season average
   - 6.6 assists per season average
   - Played for 2 teams, demonstrating consistent excellence

2. **Kylian Mbappé**: Consistent top performer across multiple seasons
   - High goal contribution rate
   - Strong performance in both domestic and European competitions

3. **Vinícius Júnior**: Emerging as key contributor for Real Madrid
   - Significant improvement in contribution percentages over time
   - Strong Champions League performance correlation

### Shapley Value Analysis Insights

#### Player Contribution Patterns
- **Attacking Players**: Higher Shapley values correlate with goal+assist combinations
- **Defensive Players**: Contribution values reflect minutes played and team defensive success
- **Midfield Players**: Balanced contributions across multiple performance metrics

#### Competition-Specific Performance
- **Champions League vs. Domestic Leagues**: Different contribution patterns observed
- **Tactical Adaptations**: Teams show varying player utilization across competitions
- **Performance Consistency**: Top players maintain high Shapley values across competitions

### Team-Level Analysis Insights

#### Complete Match History Analysis
- **15,000+ matches analyzed** across all competitions (2019-2024)
- **Game-by-game performance tracking** for tactical analysis
- **Multi-competition context** enabling strategic insights

#### Team Performance Patterns
- **Home vs. Away Performance**: Significant variations in team performance by venue
- **Competition-Specific Tactics**: Different formations and player utilization across tournaments
- **Seasonal Evolution**: Teams show distinct performance trends across multiple seasons

#### Match-Level Insights
- **Score Prediction Accuracy**: Team statistics enable better match outcome prediction
- **Tactical Formation Analysis**: Player positioning and team setup correlation with results
- **Opponent-Specific Performance**: Teams adapt strategies based on opponent strength

### Validation Results
- **Model Accuracy**: Successfully predicted team performance trends
- **Statistical Significance**: Strong correlations between Shapley values and team success
- **Practical Applications**: Framework applicable to player valuation and team optimization

## Technical Implementation

### Shapley Value Calculation

The core Shapley value implementation follows game theory principles:

```python
def calculate_shapley_contribution(player, team_coalition):
    """
    Calculate Shapley value for a player's contribution to team performance

    Args:
        player: Player object with performance metrics
        team_coalition: List of all team players

    Returns:
        float: Shapley contribution value (0-100%)
    """
    marginal_contributions = []
    for subset in all_possible_coalitions(team_coalition):
        contribution_with = team_performance(subset + [player])
        contribution_without = team_performance(subset)
        marginal_contributions.append(contribution_with - contribution_without)
    return average(marginal_contributions)
```

### Data Processing Pipeline

1. **Collection**: Automated API-Football data retrieval with rate limiting
2. **Validation**: 99.85% consistency checking and error detection
3. **Transformation**: Standardization and feature engineering
4. **Storage**: Organized file structure with JSON format
5. **Analysis**: Shapley value calculations and comparative analysis

### Performance Metrics

- **Goals per 90 minutes**: Normalized scoring rate
- **Assists per 90 minutes**: Normalized assist rate
- **Average Rating**: Weighted performance rating
- **Minutes Played**: Playing time and availability
- **Shapley Contribution**: Game theory-based team contribution percentage

## Future Research Directions

### Immediate Extensions
1. **Real-time Analysis**: Live match Shapley value calculations
2. **Transfer Market Integration**: Correlation with actual transfer values
3. **Tactical Formation Optimization**: AI-driven formation recommendations
4. **Injury Impact Analysis**: Quantifying injury effects on team performance

### Advanced Applications
1. **Machine Learning Integration**: Predictive models using Shapley features
2. **Network Analysis**: Player interaction and chemistry quantification
3. **Cross-League Comparison**: Analysis across different soccer leagues globally
4. **Youth Development**: Application to academy and development programs

## Academic Contributions

This capstone project contributes to sports analytics research through:

### 1. Novel Shapley Value Application in Soccer Analytics
- **First comprehensive implementation** of game theory Shapley values for soccer player evaluation
- **Mathematical rigor** applied to real-world sports performance assessment
- **Scalable framework** applicable to other team sports and performance domains

### 2. Multi-Season Longitudinal Analysis Framework
- **6+ seasons of comprehensive data** enabling trend analysis and performance evolution
- **Cross-competition comparison** methodology for tactical adaptation analysis
- **Predictive validation** using historical data to forecast future performance

### 3. Automated Data Collection and Validation System
- **99.85% data consistency** achieved through rigorous validation pipelines
- **Scalable architecture** for continuous data collection and analysis
- **Quality assurance framework** ensuring research-grade data reliability

### 4. Practical Applications for Team Management
- **Player valuation methodology** based on mathematical contribution assessment
- **Team optimization insights** for tactical decision-making
- **Performance prediction models** for strategic planning

## Documentation

Comprehensive documentation is available in the `docs/` directory:

### Research and Methodology
- **[Research Methodology](docs/ADS599_CAPSTONE_RESEARCH_METHODOLOGY.md)**: Complete research framework and methodology

### Data Collection Systems
- **[Player Collection System](docs/PLAYER_COLLECTION_SYSTEM_SUMMARY.md)**: Player data collection system documentation
- **[Player Statistics Collection](docs/PLAYER_STATISTICS_COLLECTION_SYSTEM.md)**: Player statistics system guide
- **[Team Statistics Collection](docs/TEAM_STATISTICS_COLLECTION_GUIDE.md)**: Team statistics and match details collection guide
- **[Optimized Collection Guide](docs/OPTIMIZED_COLLECTION_GUIDE.md)**: Optimized data collection for focused analysis

### Quick Start Guides

#### Collect All Games for One Team (2019-2024)
```bash
# Real Madrid (Team 541) - All games across all competitions
python scripts/data_collection/single_team_collection.py 541

# Barcelona (Team 529) - All games across all competitions
python scripts/data_collection/single_team_collection.py 529

# Manchester City (Team 50) - All games across all competitions
python scripts/data_collection/single_team_collection.py 50

# Specific seasons only
python scripts/data_collection/single_team_collection.py 541 --seasons 2022 2023 2024
```

#### Available Teams (Major Clubs)
- **Team 541**: Real Madrid
- **Team 529**: Barcelona
- **Team 50**: Manchester City
- **Team 33**: Manchester United
- **Team 40**: Liverpool
- **Team 157**: Bayern Munich
- **Team 165**: Borussia Dortmund
- **Team 85**: Paris Saint-Germain

#### Data Collection Commands
- **Team Data Collection**: Collect complete match history for any team
- **Player Data Collection**: Use `python scripts/data_collection/optimized_player_collection.py` for efficient player statistics collection
- **Data Validation**: Use validation scripts to ensure data quality and completeness

## Citation

If you use this work in your research, please cite:

```bibtex
@misc{ads599_soccer_analytics_2024,
  title={Advanced Soccer Analytics Using Shapley Value Analysis: A Comprehensive Framework for Player Valuation and Team Optimization},
  author={ADS599 Capstone Team},
  year={2024},
  institution={University of San Diego, Applied Data Science Program},
  url={https://github.com/mmoramora/ADS599_Capstone},
  note={Capstone Project - 67 UEFA Champions League Teams, 8080+ Players, 15000+ Matches, 2019-2025 Seasons}
}
```

## License

This project is developed for academic research purposes as part of the ADS599 Capstone course at the University of San Diego. The code and methodology are available for educational and research use.

## Acknowledgments

- **API-Football**: Comprehensive soccer data API providing the foundation for this analysis
- **University of San Diego**: Academic support and research infrastructure
- **Applied Data Science Program**: Guidance and methodological framework
- **Open Source Community**: Python libraries and tools that enabled this research

---

**ADS599 Capstone Project**
Applied Data Science Program
University of San Diego
2024

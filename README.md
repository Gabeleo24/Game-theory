# Soccer Performance Intelligence System - Champions League Focus

**ADS599 Capstone Project | University of San Diego**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Optimized-brightgreen.svg)](https://github.com/mmoramora/ADS599_Capstone)
[![Dataset](https://img.shields.io/badge/Dataset-Champions%20League%20Focused-blue.svg)](#dataset-scope)

## Abstract

This repository presents a focused Soccer Performance Intelligence System developed for advanced tactical analysis and player evaluation of **67 Champions League teams** across multiple competitions. The system integrates multi-source data collection, Shapley value analysis for player contribution assessment, and Retrieval-Augmented Generation (RAG) capabilities for formation-specific insights. This research contributes to the field of sports analytics by providing a novel framework for tactical intelligence in elite European soccer, maintaining multi-competition context while focusing on the highest level of club football.

## Dataset Scope

**Champions League Focused Analysis (2019-2023)**
- **67 unique Champions League teams** across 5 years of competition
- **34 teams mapped** to major domestic leagues (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)
- **Multi-competition context**: Champions League, domestic leagues, Europa League, domestic cups
- **116 focused dataset files** optimized for academic research
- **7.16 MB space optimization** through intelligent data filtering

## Research Objectives

1. **Champions League Team Analysis**: Focus on elite European teams while maintaining multi-competition performance context
2. **Shapley Value Implementation**: Apply game theory principles to quantify player contributions across different competition formats
3. **Tactical Intelligence**: Analyze formation effectiveness between Champions League and domestic league performance
4. **Cross-Competition Performance**: Generate insights on how elite teams adapt tactics across different competition contexts
5. **Academic Research Framework**: Provide manageable yet comprehensive dataset for capstone-level sports analytics research

## System Architecture

The Soccer Performance Intelligence System employs a modular architecture designed for scalability and extensibility:

### Core Components

- **Data Collection Layer**: Multi-source data acquisition with intelligent caching mechanisms
- **Processing Engine**: Advanced data cleaning, transformation, and feature engineering
- **Analytics Module**: Shapley value calculations and tactical analysis algorithms
- **Intelligence Layer**: RAG-powered query system for formation-specific insights
- **Visualization Interface**: Comprehensive reporting and tactical visualization tools

## Repository Structure

```
ADS599_Capstone/
├── src/soccer_intelligence/           # Core system modules
│   ├── data_collection/              # Multi-source data acquisition
│   │   ├── api_football.py           # API-Football integration
│   │   ├── social_media.py           # Social media data collection
│   │   ├── wikipedia.py              # Historical context extraction
│   │   └── cache_manager.py          # Intelligent caching system
│   ├── data_processing/              # Data pipeline and transformation
│   │   ├── data_cleaner.py          # Data validation and cleaning
│   │   ├── feature_engineer.py      # Advanced feature creation
│   │   ├── data_transformer.py      # Data format standardization
│   │   └── data_integrator.py       # Multi-source data integration
│   ├── analysis/                     # Advanced analytics engine
│   │   ├── shapley_analysis.py      # Player contribution analysis
│   │   ├── tactical_analysis.py     # Formation and strategy analysis
│   │   ├── performance_metrics.py   # Performance calculation algorithms
│   │   └── enhanced_shapley_analysis.py # Advanced Shapley implementations
│   ├── rag_system/                  # Retrieval-Augmented Generation
│   │   ├── rag_engine.py           # Core RAG implementation
│   │   ├── vector_store.py         # Vector database management
│   │   ├── query_processor.py      # Natural language query processing
│   │   └── fbref_rag_enhancer.py   # Enhanced RAG capabilities
│   └── utils/                       # System utilities and helpers
│       ├── config.py               # Configuration management
│       ├── logger.py               # Logging system
│       └── helpers.py              # Utility functions
├── scripts/                         # Optimized utility scripts
│   ├── data_collection/            # Data collection scripts
│   │   └── clean_data_collection.py        # Professional data collection
│   ├── analysis/                   # Analysis and filtering scripts
│   │   └── champions_league_team_filter.py # Champions League team filtering
│   ├── configuration/              # System configuration scripts
│   │   └── update_system_config.py         # Configuration management
│   └── maintenance/                # System maintenance scripts
│       ├── project_cleanup.py              # Project optimization
│       └── system_validation.py            # System integrity validation
├── data/                            # Data storage and management
│   ├── processed/                  # Original comprehensive datasets (149 files)
│   ├── focused/                    # Champions League focused datasets (116 files)
│   │   ├── core_champions_league_teams.json    # 67 core teams data
│   │   ├── team_league_mapping.json            # Team-to-league mappings
│   │   ├── champions_league_focus_report.json  # Analysis report
│   │   └── focused_*.json                      # Filtered competition data
│   └── analysis/                   # Analysis outputs and reports
│   └── models/                     # Trained models and embeddings
├── config/                         # System configuration (optimized)
│   ├── api_keys.yaml              # API credentials (configured)
│   ├── focused_config.yaml        # Champions League focused configuration
│   ├── data_collection_focused.yaml # Focused data collection strategy
│   ├── analysis_templates.yaml    # Pre-configured analysis templates
│   └── system_paths.yaml          # Updated system paths
├── docs/                           # Technical documentation
│   ├── CHAMPIONS_LEAGUE_FOCUS_PLAN.md    # Focused implementation plan
│   └── setup/                     # Setup and configuration documentation
├── tests/                          # Comprehensive test suite
├── notebooks/                      # Research and analysis notebooks
├── backup_removed_files/           # Backup of removed redundant files
└── requirements.txt                # Python dependencies
```

## Champions League Focused Dataset

### Dataset Overview
The system now operates with a **focused dataset** containing only the most relevant data for Champions League team analysis:

- **67 unique Champions League teams** (2019-2023 group stage participants)
- **116 focused dataset files** in `data/focused/` directory
- **Multi-competition coverage** for each core team:
  - UEFA Champions League matches and standings
  - Domestic league performance (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)
  - UEFA Europa League participation
  - Domestic cup competitions (FA Cup, Copa del Rey, Coppa Italia, DFB-Pokal)
  - Transfer and injury data for core teams

### League Distribution
- **Premier League**: 7 teams (Arsenal, Chelsea, Liverpool, Manchester City, Manchester United, Newcastle, Tottenham)
- **La Liga**: 7 teams (Atletico Madrid, Barcelona, Real Madrid, Real Sociedad, Sevilla, Valencia, Villarreal)
- **Serie A**: 6 teams (AC Milan, Atalanta, Inter, Juventus, Lazio, Napoli)
- **Bundesliga**: 8 teams (Bayern München, Borussia Dortmund, RB Leipzig, Bayer Leverkusen, Eintracht Frankfurt, etc.)
- **Ligue 1**: 6 teams (Paris Saint Germain, Lyon, Marseille, Lille, Rennes, Lens)

### Optimization Results
- **Space Saved**: 7.16 MB through intelligent filtering
- **Files Removed**: 31 redundant data files + 12 temporary scripts
- **Efficiency Gain**: 36% reduction in file count while maintaining analytical depth
- **API Efficiency**: 74,715 requests still available for specialized analysis

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- Git version control system
- API credentials for data sources (API-Football, OpenAI, Twitter)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/mmoramora/ADS599_Capstone.git
   cd ADS599_Capstone
   ```

2. **Environment Setup**
   ```bash
   python -m venv soccer_intelligence_env
   source soccer_intelligence_env/bin/activate  # Linux/macOS
   # soccer_intelligence_env\Scripts\activate  # Windows
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

### API Configuration

Create and configure `config/api_keys.yaml` with your credentials:

```yaml
# API-Football Configuration
api_football:
  key: "your_api_football_key"
  base_url: "https://v3.football.api-sports.io"
  rate_limit: 100  # requests per minute

# OpenAI Configuration (for RAG system)
openai:
  api_key: "your_openai_api_key"
  model: "gpt-4"
  max_tokens: 2000

# Twitter API Configuration
twitter:
  bearer_token: "your_twitter_bearer_token"
  api_key: "your_twitter_api_key"
  api_secret: "your_twitter_api_secret"
  access_token: "your_twitter_access_token"
  access_token_secret: "your_twitter_access_token_secret"
```

## System Usage

### Champions League Focused Analysis

The system is now optimized for Champions League team analysis with focused datasets and streamlined operations.

#### Quick Start - Focused Analysis
```bash
# Validate system integrity after optimization
python scripts/maintenance/system_validation.py

# Run Champions League team filtering (if needed)
python scripts/analysis/champions_league_team_filter.py

# Update system configuration for focused analysis
python scripts/configuration/update_system_config.py

# Run professional data collection for core teams
python scripts/data_collection/clean_data_collection.py
```

#### Champions League Team Analysis
```python
# Load core Champions League teams
import json
with open('data/focused/core_champions_league_teams.json', 'r') as f:
    core_teams_data = json.load(f)

print(f"Analyzing {len(core_teams_data['teams'])} Champions League teams")

# Load team-league mapping
with open('data/focused/team_league_mapping.json', 'r') as f:
    team_mapping = json.load(f)

# Access focused datasets
from pathlib import Path
focused_files = list(Path('data/focused').glob('focused_*.json'))
print(f"Available focused datasets: {len(focused_files)} files")
```

#### System Configuration
```python
# Load focused system configuration
import yaml
with open('config/focused_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

print(f"System focus: {config['project']['scope']}")
print(f"Core teams: {config['data']['core_teams_count']}")
```

### Data Collection Operations

```python
from src.soccer_intelligence.data_collection import APIFootballClient

# Initialize data collection client
client = APIFootballClient()

# Collect league data
la_liga_data = client.get_league_data(league_id=140, season=2023)
premier_league_data = client.get_league_data(league_id=39, season=2023)

# Collect team statistics
team_stats = client.get_team_statistics(team_id=529, season=2023)  # Barcelona

# Collect match details with advanced statistics
match_details = client.get_match_statistics(fixture_id=1035462)
```

### Champions League Advanced Analytics

#### Shapley Value Analysis for Core Teams
```python
from src.soccer_intelligence.analysis import ShapleyAnalyzer

# Initialize analyzer for Champions League teams
shapley_analyzer = ShapleyAnalyzer()

# Analyze top Champions League teams (e.g., Real Madrid - ID: 541)
real_madrid_contributions = shapley_analyzer.calculate_contributions(
    team_id=541,
    competitions=['champions_league', 'la_liga'],
    season=2023
)

# Compare performance across competitions
performance_comparison = shapley_analyzer.compare_competitions(
    team_id=541,
    competitions=['champions_league', 'la_liga']
)
```

#### Multi-Competition Tactical Analysis
```python
from src.soccer_intelligence.analysis import TacticalAnalyzer

tactical_analyzer = TacticalAnalyzer()

# Analyze formation effectiveness across competitions
formation_effectiveness = tactical_analyzer.analyze_cross_competition_tactics(
    team_id=50,  # Manchester City
    formations=['4-3-3', '4-2-3-1'],
    competitions=['champions_league', 'premier_league']
)

# Generate Champions League specific recommendations
cl_recommendations = tactical_analyzer.champions_league_tactical_analysis(
    team_id=529,  # Barcelona
    opponent_analysis=True
)
```

#### RAG-Powered Intelligence Queries
```python
from src.soccer_intelligence.rag_system import RAGEngine

# Initialize RAG system for Champions League intelligence
rag_engine = RAGEngine()

# Query formation effectiveness
formation_insights = rag_engine.query(
    "How effective is 4-3-3 formation for Barcelona in Champions League vs La Liga?"
)

# Analyze tactical adaptations
tactical_adaptations = rag_engine.query(
    "What tactical changes do Premier League teams make for Champions League matches?"
)
```

### RAG-Powered Intelligence Queries

```python
from src.soccer_intelligence.rag_system import RAGEngine

# Initialize RAG system
rag_engine = RAGEngine()

# Query formation-specific insights
formation_query = rag_engine.query(
    "What are the optimal player positions for a 4-2-3-1 formation against high-pressing teams?"
)

# Query tactical analysis
tactical_query = rag_engine.query(
    "How do Shapley values indicate player importance in defensive transitions?"
)

# Query performance insights
performance_query = rag_engine.query(
    "Which metrics best predict team success in Champions League matches?"
)
```

## Research Notebooks

The repository includes comprehensive Jupyter notebooks for research and analysis:

| Notebook | Description | Research Focus |
|----------|-------------|----------------|
| `01_data_collection_analysis.ipynb` | Multi-source data collection and validation | Data acquisition methodologies |
| `02_data_processing_pipeline.ipynb` | Data cleaning and feature engineering | Data preprocessing techniques |
| `03_shapley_value_analysis.ipynb` | Player contribution analysis using game theory | Shapley value implementation |
| `04_tactical_intelligence.ipynb` | Formation analysis and tactical insights | Strategic soccer analytics |
| `05_rag_system_demonstration.ipynb` | RAG system capabilities and queries | Natural language soccer intelligence |
| `06_performance_evaluation.ipynb` | System performance and validation | Model evaluation and metrics |

## Dataset Information

The system has collected and processed a comprehensive soccer dataset:

- **Coverage**: 5 major European leagues (La Liga, Premier League, Serie A, Bundesliga, Ligue 1)
- **Temporal Scope**: 2019-2023 seasons (5 years of historical data)
- **Data Volume**: 178 data files, 44.64 MB of research-grade data
- **Competitions**: Champions League, Europa League, domestic cups
- **Granularity**: Team statistics, match details, player performance, injury data, transfer information

## Testing and Quality Assurance

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_data_collection.py -v
pytest tests/test_shapley_analysis.py -v
pytest tests/test_rag_system.py -v

# Run tests with coverage report
pytest tests/ --cov=src/soccer_intelligence --cov-report=html
```

### Code Quality

```bash
# Code formatting
black src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/
```

## Research Contributions

This project contributes to sports analytics research through:

1. **Novel Shapley Value Application**: First comprehensive implementation of Shapley values for soccer tactical analysis
2. **Multi-Source Integration**: Advanced framework for combining structured and unstructured soccer data
3. **RAG-Powered Intelligence**: Innovative application of retrieval-augmented generation for sports analytics
4. **Tactical Intelligence Framework**: Systematic approach to formation analysis and strategic recommendations

## Academic Citations

If you use this work in your research, please cite:

```bibtex
@misc{soccer_intelligence_2024,
  title={Soccer Performance Intelligence System: A Multi-Source Approach to Tactical Analysis},
  author={ADS599 Capstone Team},
  year={2024},
  institution={University of San Diego},
  url={https://github.com/mmoramora/ADS599_Capstone}
}
```

## License and Usage

This project is developed for academic research purposes as part of the ADS599 Capstone course at the University of San Diego. The code is available under an academic license for educational and research use.

## Research Team

**ADS599 Capstone Team**
Applied Data Science Program
University of San Diego

## Acknowledgments

We acknowledge the following organizations and resources that made this research possible:

- **API-Football**: Comprehensive soccer data API providing real-time and historical match data
- **OpenAI**: Advanced language models enabling the RAG system implementation
- **Twitter API**: Social media data for sentiment analysis and fan engagement insights
- **Wikipedia**: Historical context and player biographical information
- **University of San Diego**: Academic support and research infrastructure
- **Open Source Community**: Libraries and frameworks that enabled this research

## Contact

For questions about this research or collaboration opportunities, please contact the research team through the University of San Diego Applied Data Science Program.

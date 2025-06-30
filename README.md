# Soccer Performance Intelligence System

**ADS599 Capstone Project | University of San Diego**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/mmoramora/ADS599_Capstone)

## Abstract

This repository presents a comprehensive Soccer Performance Intelligence System developed for advanced tactical analysis and player evaluation. The system integrates multi-source data collection, Shapley value analysis for player contribution assessment, and Retrieval-Augmented Generation (RAG) capabilities for formation-specific insights. This research contributes to the field of sports analytics by providing a novel framework for tactical intelligence in professional soccer.

## Research Objectives

1. **Multi-Source Data Integration**: Develop a robust pipeline for collecting and processing soccer data from API-Football, social media platforms, and Wikipedia
2. **Shapley Value Implementation**: Apply game theory principles to quantify individual player contributions to team performance
3. **Tactical Intelligence**: Create an intelligent query system for formation-specific analysis and strategic recommendations
4. **Performance Analytics**: Generate actionable insights for tactical decision-making in professional soccer

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
│   │   ├── api_football_client.py    # API-Football integration
│   │   ├── twitter_collector.py      # Social media data collection
│   │   └── wikipedia_collector.py    # Historical context extraction
│   ├── data_processing/              # Data pipeline and transformation
│   │   ├── data_cleaner.py          # Data validation and cleaning
│   │   ├── feature_engineer.py      # Advanced feature creation
│   │   └── data_transformer.py      # Data format standardization
│   ├── analysis/                     # Advanced analytics engine
│   │   ├── shapley_analyzer.py      # Player contribution analysis
│   │   ├── tactical_analyzer.py     # Formation and strategy analysis
│   │   └── performance_metrics.py   # Performance calculation algorithms
│   ├── rag_system/                  # Retrieval-Augmented Generation
│   │   ├── rag_engine.py           # Core RAG implementation
│   │   ├── vector_store.py         # Vector database management
│   │   └── query_processor.py      # Natural language query processing
│   └── utils/                       # System utilities and helpers
├── data/                            # Data storage and management
│   ├── raw/                        # Original API responses and cached data
│   ├── processed/                  # Cleaned and transformed datasets
│   └── models/                     # Trained models and embeddings
├── config/                         # System configuration
│   ├── api_keys.yaml              # API credentials (template)
│   └── system_config.yaml         # System parameters
├── tests/                          # Comprehensive test suite
├── notebooks/                      # Research and analysis notebooks
└── docs/                          # Technical documentation
```

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

### Quick Start

```python
# Initialize the Soccer Intelligence System
from src.soccer_intelligence import SoccerIntelligenceSystem

# Create system instance
system = SoccerIntelligenceSystem()

# Verify system configuration
system.verify_setup()
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

### Advanced Analytics

```python
from src.soccer_intelligence.analysis import ShapleyAnalyzer, TacticalAnalyzer

# Initialize analyzers
shapley_analyzer = ShapleyAnalyzer()
tactical_analyzer = TacticalAnalyzer()

# Calculate player contributions using Shapley values
player_contributions = shapley_analyzer.calculate_contributions(
    match_data=match_details,
    team_id=529
)

# Analyze tactical formations
formation_analysis = tactical_analyzer.analyze_formation(
    formation="4-3-3",
    team_data=team_stats
)

# Generate tactical recommendations
recommendations = tactical_analyzer.recommend_formation(
    opponent_data=opponent_stats,
    team_strengths=team_analysis
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

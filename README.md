# Soccer Performance Intelligence System

## ADS599 Capstone Project

A comprehensive system for analyzing soccer performance using multi-source data, Shapley values for tactical analysis, and RAG capabilities for formation-specific player queries.

## Project Overview

This project implements an intelligent soccer performance analysis system that combines:

- **Multi-source Data Collection**: API-Football, social media, and Wikipedia data
- **Shapley Value Analysis**: For tactical system evaluation and player contribution assessment
- **RAG System**: Retrieval-Augmented Generation for formation-specific player queries
- **Performance Intelligence**: Advanced analytics for tactical insights

## Features

- Real-time data collection from API-Football with intelligent caching
- Social media sentiment analysis for player and team insights
- Wikipedia data extraction for historical context
- Shapley value calculations for player contribution analysis
- RAG-powered query system for formation-specific insights
- Comprehensive tactical analysis and visualization

## Project Structure

```
ADS599_Capstone/
├── src/
│   └── soccer_intelligence/
│       ├── data_collection/     # Data collection modules
│       ├── data_processing/     # Data cleaning and transformation
│       ├── analysis/           # Shapley analysis and tactical insights
│       ├── rag_system/         # RAG implementation
│       └── utils/              # Common utilities
├── data/
│   ├── raw/                    # Raw data and API responses
│   ├── processed/              # Cleaned and processed data
│   └── models/                 # Trained models and embeddings
├── notebooks/                  # Jupyter notebooks for analysis
├── tests/                      # Unit tests
├── docs/                       # Documentation
└── config/                     # Configuration files
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mmoramora/ADS599_Capstone.git
cd ADS599_Capstone
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up configuration:
```bash
cp config/config_template.yaml config/config.yaml
# Edit config.yaml with your API keys
```

## Configuration

Create a `config/api_keys.yaml` file with your API credentials:

```yaml
api_football:
  key: "your_api_football_key"
  base_url: "https://v3.football.api-sports.io"

openai:
  api_key: "your_openai_api_key"

twitter:
  bearer_token: "your_twitter_bearer_token"
```

## Usage

### Data Collection

```python
from src.soccer_intelligence.data_collection import APIFootballClient

client = APIFootballClient()
matches = client.get_matches(league_id=140, season=2023)  # La Liga
```

### Shapley Analysis

```python
from src.soccer_intelligence.analysis import ShapleyAnalyzer

analyzer = ShapleyAnalyzer()
contributions = analyzer.calculate_player_contributions(match_data)
```

### RAG Queries

```python
from src.soccer_intelligence.rag_system import RAGEngine

rag = RAGEngine()
response = rag.query("What are the best formations for counter-attacking?")
```

## Notebooks

- `01_data_collection.ipynb`: Data collection demonstration
- `02_data_processing.ipynb`: Data cleaning and feature engineering
- `03_shapley_analysis.ipynb`: Shapley value analysis examples
- `04_rag_system.ipynb`: RAG system demonstration
- `05_tactical_insights.ipynb`: Comprehensive tactical analysis

## Testing

Run tests with:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of the ADS599 Capstone course and is for educational purposes.

## Team

ADS599 Capstone Team - University of San Diego

## Acknowledgments

- API-Football for providing comprehensive soccer data
- OpenAI for RAG capabilities
- The open-source community for the excellent libraries used in this project

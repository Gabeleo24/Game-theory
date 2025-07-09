# Real Madrid KPI System - Complete Setup Guide

## Overview

This comprehensive Docker-based system provides advanced soccer intelligence analytics specifically optimized for Real Madrid. The system integrates multiple APIs (SportMonks, API-Football), uses Redis for high-performance caching, PostgreSQL for data storage, and includes specialized KPI analysis and algorithm optimization services.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose v2.37.1+
- 8GB+ RAM recommended
- 20GB+ free disk space

### 1. Start the Complete System
```bash
# Start core services and run full analysis
python start_real_madrid_kpi_system.py full-analysis
```

### 2. Start Development Environment
```bash
# Start with Jupyter Lab and development tools
python start_real_madrid_kpi_system.py dev
```

### 3. Start Web Dashboard
```bash
# Start interactive KPI dashboard
python start_real_madrid_kpi_system.py dashboard
```

## 🏗️ System Architecture

### Core Services
- **PostgreSQL Database**: Optimized for soccer analytics with 8GB memory allocation
- **Redis Cache**: High-performance caching with 4GB memory for API responses and KPI calculations
- **Real Madrid App**: Main application container with API integrations

### Specialized Services
- **KPI Analyzer**: Advanced Real Madrid performance metrics analysis
- **Algorithm Optimizer**: Machine learning system to find best KPI prediction algorithms
- **Data Collector**: Unified SportMonks and API-Football data collection
- **Match Analyzer**: Comprehensive match-level analysis and reporting

### Development Services
- **Jupyter Lab**: Available at http://localhost:8888
- **Streamlit Dashboard**: Available at http://localhost:8501
- **Web Dashboard**: Available at http://localhost:8080

## 📊 Key Performance Indicators (KPIs)

### Offensive KPIs
- Goals per match
- Shots on target ratio
- Scoring efficiency
- Key passes per match
- Dribbles success rate

### Defensive KPIs
- Goals conceded per match
- Clean sheets percentage
- Tackles success rate
- Interceptions per match
- Defensive actions per match

### Tactical KPIs
- Pass accuracy
- Possession percentage
- Discipline score
- Formation effectiveness

### Player KPIs
- Average match rating
- Goals/assists per match
- Minutes played consistency
- Position-specific metrics

## 🤖 Algorithm Optimization

The system tests multiple machine learning algorithms to find the best predictors for each KPI:

### Algorithms Tested
- Random Forest Regressor
- Gradient Boosting Regressor
- Linear Regression
- Ridge Regression
- Lasso Regression
- Support Vector Regression
- Neural Networks (MLP)

### Optimization Metrics
- R² Score (coefficient of determination)
- Mean Squared Error (MSE)
- Mean Absolute Error (MAE)
- Cross-validation scores
- Prediction accuracy
- Feature importance rankings

## 🔧 Configuration

### API Keys (config/api_keys.yaml)
```yaml
api_football:
  key: "5ced20dec7f4b2226c8944c88c6d86aa"

sportmonks:
  api_key: "TmPuKHKnA7OJdHxp8zGzF5oevN0mgyqOOOaqgWMOr7KrhpaZeg9xB2ajoq2p"

database:
  host: "postgres"
  name: "soccer_intelligence"
  user: "soccerapp"
  password: "soccerpass123"

redis:
  host: "redis"
  password: "redispass123"
```

### Real Madrid Configuration
- Team ID (SportMonks): 53
- Team ID (API-Football): 541
- Focus Season: 2023-2024
- Competitions: La Liga, Champions League, Copa del Rey

## 📈 Usage Examples

### 1. Run KPI Analysis
```bash
# Analyze Real Madrid KPIs for current season
python start_real_madrid_kpi_system.py analyze-kpi
```

### 2. Optimize Algorithms
```bash
# Find best algorithms for KPI prediction
python start_real_madrid_kpi_system.py optimize-algorithms
```

### 3. Collect Fresh Data
```bash
# Update Real Madrid data from APIs
python start_real_madrid_kpi_system.py collect-data
```

### 4. Check System Status
```bash
# View all running services
python start_real_madrid_kpi_system.py status
```

## 🐳 Docker Services

### Core Infrastructure
```bash
# Start only database and cache
docker compose up -d postgres redis
```

### Development Profile
```bash
# Start development environment
docker compose --profile development up -d
```

### KPI Analysis Profile
```bash
# Start KPI analysis services
docker compose --profile kpi-analysis up -d
```

### Algorithm Testing Profile
```bash
# Start algorithm optimization
docker compose --profile algorithm-testing up -d
```

## 📁 Data Organization

```
data/
├── focused/           # Core team data
├── real_madrid/       # Real Madrid specific data
├── kpi/              # KPI analysis results
├── algorithms/       # Algorithm optimization results
├── models/           # Trained ML models
├── analysis/         # Analysis outputs
└── reports/          # Generated reports

logs/
├── kpi/              # KPI analysis logs
├── algorithms/       # Algorithm optimization logs
├── data_collection/  # Data collection logs
└── match_analysis/   # Match analysis logs
```

## 🔍 Monitoring and Debugging

### View Logs
```bash
# View application logs
docker compose logs real-madrid-app

# View KPI analyzer logs
docker compose logs real-madrid-kpi-analyzer

# View all logs
docker compose logs -f
```

### Database Access
```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U soccerapp -d soccer_intelligence
```

### Redis Access
```bash
# Connect to Redis
docker compose exec redis redis-cli -a redispass123
```

## 🛠️ Troubleshooting

### Common Issues

1. **Services not starting**: Check Docker memory allocation (8GB+ recommended)
2. **API rate limits**: Monitor API usage in logs
3. **Database connection issues**: Ensure PostgreSQL is healthy before starting apps
4. **Redis connection issues**: Check Redis password configuration

### System Cleanup
```bash
# Stop all services and clean up
python start_real_madrid_kpi_system.py cleanup
```

### Reset System
```bash
# Complete system reset
docker compose down -v
docker system prune -f
python start_real_madrid_kpi_system.py start
```

## 📊 Expected Outputs

### KPI Analysis Results
- Team performance metrics by competition
- Player rankings and statistics
- Performance trends over time
- Improvement recommendations

### Algorithm Optimization Results
- Best algorithms for each KPI type
- Feature importance rankings
- Model performance comparisons
- Prediction accuracy metrics

### Match Analysis Reports
- Individual match breakdowns
- Player performance analysis
- Tactical insights
- Opposition analysis

## 🎯 Team Collaboration

### For Analysts
- Access Jupyter Lab at http://localhost:8888
- Use read-only data access for exploration
- Generate reports using provided templates

### For Developers
- Full system access through development profile
- Modify algorithms and KPI definitions
- Test new features in isolated environment

### For Researchers
- Academic tools and research environment
- Access to comprehensive documentation
- Statistical analysis capabilities

## 🚀 Next Steps

1. **Start the system**: `python start_real_madrid_kpi_system.py full-analysis`
2. **Explore results**: Check generated reports in `data/analysis/`
3. **Optimize algorithms**: Review algorithm performance in `data/algorithms/`
4. **Customize KPIs**: Modify KPI definitions in analysis scripts
5. **Scale analysis**: Add more teams or seasons as needed

## 📞 Support

For issues or questions:
1. Check logs: `docker compose logs [service-name]`
2. Review system status: `python start_real_madrid_kpi_system.py status`
3. Consult troubleshooting section above
4. Reset system if needed: `python start_real_madrid_kpi_system.py cleanup`

---

**Real Madrid KPI System** - Advanced Soccer Intelligence Analytics
*Optimized for team collaboration and algorithm optimization*

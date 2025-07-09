# Real Madrid 2023-2024 Match Analysis System - Docker Setup Guide

## 🏆 Overview

This Docker setup provides a complete containerized environment for analyzing Real Madrid's historic 2023-2024 Champions League winning season. The system includes database, web interface, analysis tools, and automated report generation for all 52 matches.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Docker Compose v2.0+ (included with Docker Desktop)
- At least 4GB RAM available for containers
- 2GB free disk space

### One-Command Setup
```bash
# Start the complete Real Madrid analysis system
./start-real-madrid-analysis.sh start
```

### Manual Setup
```bash
# Start core services
docker compose -f docker-compose.real-madrid.yml up -d postgres redis real_madrid_app

# Start web interface
docker compose -f docker-compose.real-madrid.yml up -d match_analyzer_web
```

## 📊 Available Services

### Core Services
- **🏆 Real Madrid App** (`real_madrid_app`): Main analysis application
- **🗄️ PostgreSQL Database** (`postgres`): Soccer intelligence database
- **🌐 Web Interface** (`match_analyzer_web`): Browser-based match viewer
- **🔄 Redis Cache** (`redis`): Performance optimization

### Development Services
- **👨‍💻 Development Environment** (`real_madrid_dev`): Jupyter Lab + analysis tools
- **📊 Match Generator** (`match_generator`): Automated report generation
- **📈 Premium Display** (`premium_display`): Enhanced statistics viewer

## 🎯 Service Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Web Interface | http://localhost:8080 | Browse matches and view analysis |
| Jupyter Lab | http://localhost:8888 | Development and data exploration |
| Streamlit | http://localhost:8501 | Interactive dashboards |
| PostgreSQL | localhost:5432 | Direct database access |
| Redis | localhost:6379 | Cache management |

## 🔧 Management Commands

### System Control
```bash
# Start the system
./start-real-madrid-analysis.sh start

# Stop the system
./start-real-madrid-analysis.sh stop

# Restart all services
./start-real-madrid-analysis.sh restart

# Check system status
./start-real-madrid-analysis.sh status
```

### Analysis Operations
```bash
# Generate all 52 match reports
./start-real-madrid-analysis.sh generate

# Display premium statistics
./start-real-madrid-analysis.sh stats

# Start development environment
./start-real-madrid-analysis.sh dev
```

### Monitoring and Debugging
```bash
# View application logs
./start-real-madrid-analysis.sh logs real_madrid_app

# View web interface logs
./start-real-madrid-analysis.sh logs match_analyzer_web

# View database logs
./start-real-madrid-analysis.sh logs postgres
```

## 📁 Directory Structure

```
/
├── docker-compose.real-madrid.yml    # Main Docker Compose configuration
├── Dockerfile                        # Application container definition
├── Dockerfile.web                    # Web interface container
├── start-real-madrid-analysis.sh     # Management script
├── requirements.txt                  # Python dependencies
├── logs/match_analysis/              # Generated match reports
│   └── 2023-2024/
│       ├── uefa_champions_league/    # Champions League matches
│       ├── la_liga/                  # La Liga matches
│       ├── copa_del_rey/             # Copa del Rey matches
│       └── summary/                  # Master summary files
├── data/                             # Application data
├── config/                           # Configuration files
└── scripts/                          # Analysis scripts
```

## 🏆 Real Madrid Analysis Features

### Match Analysis
- **52 Complete Matches**: All games from 2023-2024 season
- **Individual Player Stats**: Goals, assists, minutes, shots, passes, tackles
- **Enhanced Metrics**: xG, xAG, SCA, progressive actions
- **Positional Analysis**: Goalkeepers, defenders, midfielders, forwards
- **Tactical Insights**: Formation analysis and key performers

### Competition Coverage
- **13 UEFA Champions League matches** (including final victory)
- **38 La Liga matches** (complete domestic season)
- **1 Copa del Rey match** (knockout competition)

### Key Matches Available
- **Champions League Final**: Real Madrid 2-0 Borussia Dortmund
- **El Clasico**: Real Madrid 3-2 Barcelona
- **Manchester City Quarterfinals**: Dramatic comeback
- **Bayern Munich Semifinals**: Classic encounters

## 🔄 Automated Workflows

### Match Report Generation
```bash
# Generate comprehensive reports for all 52 matches
docker compose -f docker-compose.real-madrid.yml --profile generator run --rm match_generator
```

### Premium Statistics Display
```bash
# Show enhanced Real Madrid statistics
docker compose -f docker-compose.real-madrid.yml --profile display run --rm premium_display
```

### Development Environment
```bash
# Start Jupyter Lab for analysis
docker compose -f docker-compose.real-madrid.yml up -d real_madrid_dev
```

## 📊 Database Configuration

### Connection Details
- **Host**: localhost (or `postgres` from within containers)
- **Port**: 5432
- **Database**: soccer_intelligence
- **Username**: soccerapp
- **Password**: soccerpass123

### Key Tables
- `fixed_matches`: Match information and metadata
- `fixed_match_player_stats`: Individual player performance data
- `fixed_teams`: Team information
- `fixed_players`: Player profiles
- `premium_real_madrid_stats`: Enhanced statistics table

## 🌐 Web Interface Features

### Match Browser
- Browse all 52 Real Madrid matches
- Filter by competition (Champions League, La Liga, Copa del Rey)
- View match details and player statistics
- Interactive match selection

### API Endpoints
- `GET /api/matches`: List all available matches
- `GET /api/match/<id>`: Detailed match and player data
- `GET /reports`: Access generated match reports

## 🔧 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check if PostgreSQL is running
docker compose -f docker-compose.real-madrid.yml ps postgres

# Restart database
docker compose -f docker-compose.real-madrid.yml restart postgres
```

**Web Interface Not Loading**
```bash
# Check web service status
docker compose -f docker-compose.real-madrid.yml logs match_analyzer_web

# Restart web interface
docker compose -f docker-compose.real-madrid.yml restart match_analyzer_web
```

**Out of Memory**
```bash
# Check container resource usage
docker stats

# Increase Docker Desktop memory allocation to 6GB+
```

### Performance Optimization

**Database Performance**
- PostgreSQL configured with optimized settings
- Indexes on key columns for fast queries
- Connection pooling enabled

**Container Resources**
- Production containers: 4 CPU cores, 8GB RAM limit
- Development containers: 2 CPU cores, 4GB RAM limit
- Shared memory optimization for large datasets

## 🧹 Cleanup and Maintenance

### Stop Services
```bash
# Stop all services
./start-real-madrid-analysis.sh stop
```

### Complete Cleanup
```bash
# Remove all containers, volumes, and data
./start-real-madrid-analysis.sh cleanup
```

### Backup Data
```bash
# Backup database
docker compose -f docker-compose.real-madrid.yml exec postgres pg_dump -U soccerapp soccer_intelligence > backup.sql

# Backup match reports
tar -czf match_reports_backup.tar.gz logs/match_analysis/
```

## 🎯 Next Steps

1. **Start the system**: `./start-real-madrid-analysis.sh start`
2. **Generate reports**: `./start-real-madrid-analysis.sh generate`
3. **Access web interface**: http://localhost:8080
4. **Explore development tools**: `./start-real-madrid-analysis.sh dev`

## 🏆 Success Indicators

✅ **System Running**: All containers healthy and accessible  
✅ **Database Connected**: PostgreSQL accepting connections  
✅ **Web Interface Active**: Match browser loading at localhost:8080  
✅ **Reports Generated**: 52 match analysis files created  
✅ **Development Ready**: Jupyter Lab accessible for analysis  

---

**Real Madrid 2023-2024 Champions League Winners** 🏆  
*Complete containerized analysis system for the historic season*

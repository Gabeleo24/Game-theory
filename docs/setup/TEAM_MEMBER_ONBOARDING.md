# Team Member Onboarding Guide - ADS599 Capstone Soccer Intelligence System

## Welcome to the Team!

This guide will help you get the complete ADS599 Capstone Soccer Intelligence System setup on your local machine, giving you the same access and capabilities as other team members.

## Prerequisites

### Required Software
- **Git** (latest version)
- **Docker Desktop** (latest version)
- **Docker Compose** v2.0+ (included with Docker Desktop)
- **Python 3.11+** (recommended)
- **Code Editor** (VS Code recommended)

### System Requirements
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **OS**: Windows 10+, macOS 10.15+, or Linux

## Quick Setup (5 Minutes)

### 1. Clone the Repository
```bash
# Clone the project repository
git clone https://github.com/mmoramora/ADS599_Capstone.git
cd ADS599_Capstone

# Verify you're on the main branch
git branch
```

### 2. Run Team Setup Script
```bash
# Make setup script executable (Linux/macOS)
chmod +x scripts/setup/team_member_setup.sh

# Run automated setup
./scripts/setup/team_member_setup.sh

# For Windows users
# scripts/setup/team_member_setup.bat
```

### 3. Configure API Keys (Required)
```bash
# Copy API key template
cp config/api_keys_template.yaml config/api_keys.yaml

# Edit with your API keys (see API Keys section below)
nano config/api_keys.yaml  # or use your preferred editor
```

### 4. Start the System
```bash
# Start all services
docker-compose up -d

# Verify everything is running
docker-compose ps
```

### 5. Verify Setup
```bash
# Test database connection
./scripts/setup/verify_setup.sh

# Access the system
echo "🎉 Setup complete! Access points:"
echo "📊 Database: localhost:5432"
echo "🔍 pgAdmin: http://localhost:8080"
echo "📓 Jupyter: http://localhost:8888"
echo "📈 Streamlit: http://localhost:8501"
```

## Detailed Setup Instructions

### API Keys Configuration

#### SportMonks API Key
1. **Get API Key**: Visit [SportMonks API](https://www.sportmonks.com/football-api)
2. **Sign up** for a free account
3. **Copy your API key** from the dashboard
4. **Add to config**:
```yaml
# config/api_keys.yaml
api_football:
  key: "YOUR_SPORTMONKS_API_KEY_HERE"
  base_url: "https://soccer.sportmonks.com/api/v2.0"
```

#### Optional: OpenAI API Key (for advanced features)
```yaml
# config/api_keys.yaml
openai:
  api_key: "YOUR_OPENAI_API_KEY_HERE"  # Optional
```

### Team Development Environment

#### VS Code Setup (Recommended)
```bash
# Install recommended extensions
code --install-extension ms-python.python
code --install-extension ms-vscode.vscode-docker
code --install-extension ms-toolsai.jupyter
code --install-extension bradlc.vscode-tailwindcss

# Open project in VS Code
code .
```

#### Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Team Collaboration Setup

### Git Configuration
```bash
# Configure Git with your information
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Set up branch protection (team leads only)
git config branch.main.pushRemote origin
```

### Shared Development Workflow

#### 1. Feature Branch Workflow
```bash
# Always start from main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: description of your changes"

# Push feature branch
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

#### 2. Team Communication
- **Slack/Discord**: Join team communication channel
- **GitHub Issues**: Use for bug reports and feature requests
- **GitHub Projects**: Track progress and assignments
- **Weekly Standups**: Scheduled team meetings

### Shared Resources Access

#### Database Access
```bash
# Connect to shared development database
docker exec -it soccer-intelligence-db psql -U soccerapp -d soccer_intelligence

# Or use pgAdmin web interface
# URL: http://localhost:8080
# Email: admin@admin.com
# Password: admin
```

#### Jupyter Notebooks
```bash
# Start Jupyter Lab
docker-compose --profile development up jupyter -d

# Access at: http://localhost:8888
# Password: soccer_intelligence
```

#### Shared Analysis Environment
```bash
# Start full development environment
docker-compose --profile development up -d

# Available services:
# - Jupyter Lab: http://localhost:8888
# - Streamlit Dashboard: http://localhost:8501
# - pgAdmin: http://localhost:8080
# - Redis Commander: http://localhost:8081
```

## Team Member Roles and Permissions

### Data Analyst Role
**Access**: Read-only database, Jupyter notebooks, visualization tools
```bash
# Start analyst environment
docker-compose --profile analyst up -d

# Available tools:
# - Jupyter Lab with pre-loaded notebooks
# - Streamlit dashboard for visualizations
# - SQL Playground for data exploration
```

### Developer Role
**Access**: Full system access, code modification, deployment
```bash
# Start full development environment
docker-compose --profile development up -d

# Additional access:
# - Source code modification
# - Database schema changes
# - Docker configuration updates
```

### Research Role
**Access**: Analysis tools, documentation, research notebooks
```bash
# Start research environment
docker-compose --profile research up -d

# Specialized tools:
# - Research notebooks
# - Statistical analysis tools
# - Academic documentation access
```

## Common Team Tasks

### 1. Data Collection
```bash
# Collect data for specific teams
python scripts/data_collection/team_statistics_collector.py --teams "Manchester City,Barcelona"

# Collect player statistics
python scripts/data_collection/player_statistics_collector.py --season 2024
```

### 2. Analysis Workflows
```bash
# Run Shapley value analysis
python scripts/analysis/shapley_analysis.py --team-id 50 --season 2024

# Generate team reports
python scripts/analysis/team_performance_report.py --team-id 50
```

### 3. Database Operations
```bash
# Load new data
python scripts/data_loading/json_to_postgres.py

# Run data quality checks
./scripts/data_loading/validate_data.sh

# Backup database
./scripts/backup/backup_database.sh
```

## Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Reset Docker environment
docker-compose down -v
docker system prune -f
docker-compose up -d

# Check Docker resources
docker system df
```

#### Database Connection Issues
```bash
# Check database status
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Reset database
docker-compose down postgres
docker volume rm ads599_capstone_postgres_data
docker-compose up postgres -d
```

#### Permission Issues
```bash
# Fix file permissions (Linux/macOS)
sudo chown -R $USER:$USER .
chmod +x scripts/**/*.sh

# Windows: Run as Administrator
```

### Getting Help

#### Team Support Channels
1. **GitHub Issues**: Technical problems and bug reports
2. **Team Chat**: Quick questions and coordination
3. **Documentation**: Check `docs/` directory first
4. **Code Reviews**: Request help through pull requests

#### Self-Help Resources
- **Documentation**: `docs/` directory
- **Setup Verification**: `./scripts/setup/verify_setup.sh`
- **System Health Check**: `./scripts/monitoring/health_check.sh`
- **Log Analysis**: `docker-compose logs [service-name]`

## Team Best Practices

### Code Standards
- **Python**: Follow PEP 8 style guide
- **SQL**: Use consistent formatting and comments
- **Documentation**: Update docs with any changes
- **Testing**: Write tests for new features

### Data Management
- **Backup**: Regular database backups
- **Version Control**: Track data schema changes
- **Quality**: Validate data before committing
- **Security**: Never commit API keys or sensitive data

### Collaboration
- **Communication**: Keep team informed of changes
- **Documentation**: Document your work
- **Code Review**: Review team members' code
- **Knowledge Sharing**: Share insights and learnings

## Next Steps

### After Setup
1. **Explore Documentation**: Read through `docs/research-methodology/`
2. **Run Sample Analysis**: Try the SQL Playground Guide
3. **Join Team Meeting**: Attend next team standup
4. **Pick First Task**: Check GitHub Issues for assignments

### Learning Resources
- **Soccer Analytics**: `docs/research-methodology/ADS599_CAPSTONE_COMPREHENSIVE_RESEARCH_PAPER.md`
- **System Architecture**: `docs/architecture/README.md`
- **Data Access**: `docs/data-access/DATA_ACCESS_GUIDE.md`
- **Performance Optimization**: `docs/performance-optimization/PERFORMANCE_OPTIMIZATION_GUIDE.md`

---

**Welcome to the ADS599 Capstone Soccer Intelligence Team!** 🚀

You now have access to the complete system and can collaborate effectively with the team. If you encounter any issues during setup, please reach out to the team leads or create a GitHub issue.

**Team Leads**: [Add team lead contact information]  
**Project Repository**: https://github.com/mmoramora/ADS599_Capstone  
**Documentation**: Complete guides available in `docs/` directory

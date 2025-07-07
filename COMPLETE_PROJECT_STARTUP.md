# ADS599 Capstone Complete Project Startup Guide

## 🚀 **One-Command Complete Setup**

Get the entire ADS599 Capstone Soccer Intelligence System running in **5 minutes**:

```bash
# 1. Clone the complete project
git clone https://github.com/mmoramora/ADS599_Capstone.git
cd ADS599_Capstone

# 2. Run complete automated setup
./scripts/setup/team_member_setup.sh

# 3. Configure your API key
nano config/api_keys.yaml  # Add your SportMonks API key

# 4. Start complete system
docker-compose --profile team up -d
```

**That's it!** Your complete soccer intelligence system is now running.

## 🎯 **What You Get - Complete System**

### **📊 Database & Analytics**
- ✅ **PostgreSQL Database**: 67 UEFA Champions League teams, 8,080+ player statistics
- ✅ **Redis Cache**: High-performance data caching and optimization
- ✅ **Complete Dataset**: 2019-2024 seasons across multiple competitions
- ✅ **99.85% Data Consistency**: Multi-source integration with quality validation

### **📓 Jupyter Collaboration**
- ✅ **Role-Based Environments**: Analyst, Developer, Researcher access
- ✅ **Shared Notebooks**: Team collaboration with version control
- ✅ **Storage**: `/Users/home/Documents/GitHub/ADS599_Capstone/notebooks/`
- ✅ **Security**: API key protection, output cleaning, Git integration

### **🔧 Development Tools**
- ✅ **pgAdmin**: Database management at http://localhost:8080
- ✅ **Redis Commander**: Cache management at http://localhost:8081
- ✅ **SQL Playground**: Interactive database exploration
- ✅ **Performance Monitoring**: Resource usage and optimization

### **📚 Research Documentation**
- ✅ **Academic Paper**: Publication-ready research documentation
- ✅ **Technical Appendices**: Code examples and performance metrics
- ✅ **Methodology**: Shapley value analysis implementation
- ✅ **Presentations**: Academic and industry presentation materials

## 🎭 **Choose Your Role**

### 🔍 **Data Analyst**
```bash
# Start analyst environment
./scripts/team/manage_team_access.sh start-analyst
```
- **Access**: http://localhost:8888 (token: `analyst_secure_token_2024`)
- **Focus**: Data exploration, visualization, reporting
- **Database**: Read-only access to all data
- **Resources**: 4GB RAM, 2 CPU cores

### 💻 **Developer**
```bash
# Start developer environment
./scripts/team/manage_team_access.sh start-developer
```
- **Jupyter**: http://localhost:8889 (token: `developer_secure_token_2024`)
- **pgAdmin**: http://localhost:8080 (admin@admin.com / admin)
- **Redis**: http://localhost:8081
- **Focus**: System development, optimization, deployment
- **Database**: Full read/write access
- **Resources**: 8GB RAM, 4 CPU cores

### 📚 **Researcher**
```bash
# Start researcher environment
./scripts/team/manage_team_access.sh start-researcher
```
- **Access**: http://localhost:8890 (token: `researcher_secure_token_2024`)
- **Focus**: Academic research, methodology, publications
- **Database**: Read-only with research views
- **Tools**: LaTeX, citations, academic writing
- **Resources**: 6GB RAM, 3 CPU cores

## 📊 **Explore the Data**

### **Quick Database Exploration**
```bash
# Interactive SQL playground
./run_sql_with_logs.sh

# Show database structure
./show_database_structure.sh

# Sample analysis
./run_sql_with_logs.sh analysis overview
```

### **Sample Queries**
```sql
-- Top UEFA Champions League goal scorers
SELECT 
    p.player_name,
    t.team_name,
    SUM(ps.goals) as total_goals,
    SUM(ps.assists) as total_assists,
    AVG(ps.player_rating) as avg_rating
FROM player_statistics ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams t ON ps.team_id = t.team_id
JOIN competitions c ON ps.competition_id = c.competition_id
WHERE c.competition_name LIKE '%Champions League%'
  AND ps.minutes_played > 90
GROUP BY p.player_id, p.player_name, t.team_name
ORDER BY total_goals DESC
LIMIT 10;

-- Team performance by season
SELECT 
    t.team_name,
    ps.season_year,
    COUNT(*) as players,
    AVG(ps.goals) as avg_goals,
    AVG(ps.assists) as avg_assists,
    AVG(ps.player_rating) as avg_rating
FROM player_statistics ps
JOIN teams t ON ps.team_id = t.team_id
GROUP BY t.team_id, t.team_name, ps.season_year
ORDER BY ps.season_year DESC, avg_rating DESC;
```

## 📓 **Start with Jupyter Notebooks**

### **Create Your First Analysis**
```bash
# Create notebook from template
./scripts/jupyter/manage_notebooks.sh create-notebook my_first_analysis

# Location: /Users/home/Documents/GitHub/ADS599_Capstone/notebooks/shared/
```

### **Sample Notebook Code**
```python
# Standard setup for all analyses
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Connect to database (use your role-appropriate credentials)
# Analyst: analyst_user/analyst_secure_pass (read-only)
# Developer: soccerapp/soccerpass123 (full access)
# Researcher: research_user/research_secure_pass (read-only)

engine = create_engine('postgresql://analyst_user:analyst_secure_pass@postgres:5432/soccer_intelligence')

# Load UEFA Champions League data
query = """
SELECT p.player_name, t.team_name, ps.goals, ps.assists, ps.player_rating
FROM player_statistics ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams t ON ps.team_id = t.team_id
JOIN competitions c ON ps.competition_id = c.competition_id
WHERE c.competition_name LIKE '%Champions League%'
  AND ps.minutes_played > 90
ORDER BY ps.goals DESC
LIMIT 20
"""

df = pd.read_sql(query, engine)
print(f"Loaded {len(df)} Champions League player records")
display(df.head())

# Create visualization
plt.figure(figsize=(12, 6))
plt.scatter(df['goals'], df['assists'], alpha=0.7, s=df['player_rating']*10)
plt.xlabel('Goals')
plt.ylabel('Assists')
plt.title('UEFA Champions League: Goals vs Assists (Size = Player Rating)')
plt.show()
```

## 🔬 **Advanced Analytics**

### **Shapley Value Analysis**
```bash
# Run Shapley value analysis for a team
python scripts/analysis/shapley_analysis.py --team-id 50 --season 2024

# Generate comprehensive team report
python scripts/analysis/team_performance_report.py --team-id 50
```

### **Performance Optimization**
```bash
# Check system performance
./scripts/monitoring/health_check.sh

# View resource usage
./scripts/team/manage_team_access.sh status
```

## 🛠️ **Management Commands**

### **System Management**
```bash
# Check status of all services
docker-compose ps

# Start complete team environment
docker-compose --profile team up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart postgres

# View logs
docker-compose logs jupyter-analyst
```

### **Notebook Management**
```bash
# List all notebooks
./scripts/jupyter/manage_notebooks.sh list-notebooks

# Create new notebook
./scripts/jupyter/manage_notebooks.sh create-notebook [name]

# Backup all notebooks
./scripts/jupyter/manage_notebooks.sh backup

# Clean outputs before Git commit
./scripts/jupyter/manage_notebooks.sh clean-outputs

# Security scan
python scripts/jupyter/notebook_security_manager.py scan
```

### **Data Management**
```bash
# Backup database
./scripts/backup/backup_database.sh

# Load new data
python scripts/data_loading/json_to_postgres.py

# Validate data quality
./scripts/data_loading/validate_data.sh
```

## 🔐 **Security & Best Practices**

### **API Key Management**
- ✅ **Never commit API keys** to Git
- ✅ **Use config/api_keys.yaml** for credentials
- ✅ **Pre-commit hooks** prevent accidental commits
- ✅ **Each team member** manages their own keys

### **Database Access**
- ✅ **Role-based permissions** (analyst: read-only, developer: full access)
- ✅ **Secure connections** with proper credentials
- ✅ **Audit logging** for all database access
- ✅ **Regular backups** with 30-day retention

### **Notebook Collaboration**
- ✅ **Clean outputs** before committing
- ✅ **Naming convention**: `YYYY-MM-DD_author_purpose_version.ipynb`
- ✅ **Security scanning** for sensitive data
- ✅ **Version control** with Git integration

## 📚 **Documentation & Resources**

### **Quick References**
- **This Guide**: `COMPLETE_PROJECT_STARTUP.md`
- **Jupyter Setup**: `JUPYTER_COLLABORATION_SETUP.md`
- **Team Collaboration**: `TEAM_COLLABORATION_QUICK_START.md`
- **Storage Config**: `NOTEBOOK_STORAGE_CONFIGURATION.md`

### **Complete Documentation**
- **Research Paper**: `docs/research-methodology/ADS599_CAPSTONE_COMPREHENSIVE_RESEARCH_PAPER.md`
- **Technical Guides**: `docs/` directory
- **API Documentation**: Source code with comprehensive comments
- **Database Schema**: `docker/postgres/init.sql`

### **Support Resources**
- **GitHub Issues**: Technical problems and bug reports
- **Team Meetings**: Collaboration and coordination
- **Code Reviews**: Learning and improvement
- **Documentation**: Comprehensive guides and tutorials

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Docker Won't Start**
```bash
# Check Docker Desktop is running
docker --version

# Restart Docker services
docker-compose down
docker-compose up -d

# Check system resources
docker system df
```

#### **Database Connection Issues**
```bash
# Check database status
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Test connection
docker exec -it soccer-intelligence-db pg_isready -U soccerapp
```

#### **Jupyter Won't Load**
```bash
# Check Jupyter status
docker-compose ps | grep jupyter

# Restart Jupyter environment
./scripts/jupyter/manage_notebooks.sh stop-jupyter all
./scripts/jupyter/manage_notebooks.sh start-jupyter all

# Check logs
docker logs jupyter-analyst
```

## ✅ **Success Checklist**

### **Setup Complete When**:
- [ ] All Docker services running (`docker-compose ps`)
- [ ] Database accessible (`./scripts/setup/verify_setup.sh`)
- [ ] Jupyter environments accessible (check URLs)
- [ ] Can create and run notebooks
- [ ] SQL playground working
- [ ] API keys configured
- [ ] No security issues in scan

### **Ready for Analysis When**:
- [ ] Can query UEFA Champions League data
- [ ] Notebooks create and save properly
- [ ] Visualizations render correctly
- [ ] Git workflow established
- [ ] Team collaboration active

## 🎉 **You're Ready!**

Your complete ADS599 Capstone Soccer Intelligence System is now running with:

- ✅ **67 UEFA Champions League teams** with comprehensive data
- ✅ **8,080+ player statistics** across 6 seasons (2019-2024)
- ✅ **Role-based Jupyter environments** for team collaboration
- ✅ **Professional database** with PostgreSQL and Redis
- ✅ **Advanced analytics** including Shapley value analysis
- ✅ **Complete documentation** for academic submission
- ✅ **Security and backup** systems
- ✅ **Performance optimization** with 3.2x speed improvements

**Start exploring, analyzing, and collaborating!** 🚀⚽📊

---

**Quick Commands Summary**:
- **Complete Setup**: `./scripts/setup/team_member_setup.sh`
- **Start System**: `docker-compose --profile team up -d`
- **Verify Setup**: `./scripts/setup/verify_setup.sh`
- **Create Notebook**: `./scripts/jupyter/manage_notebooks.sh create-notebook [name]`
- **SQL Playground**: `./run_sql_with_logs.sh`
- **System Status**: `./scripts/team/manage_team_access.sh status`
- **Stop System**: `docker-compose down`

# GitHub Codespace Installation Guide
ADS599 Capstone Soccer Intelligence System

## 🚀 **One-Command Installation**

Open a GitHub Codespace and run this single command to install everything:

```bash
curl -fsSL https://raw.githubusercontent.com/mmoramora/ADS599_Capstone/main/scripts/setup/codespace_installation.sh | bash
```

**That's it!** The complete soccer intelligence system will be installed and ready to use.

## 📋 **Prerequisites**

### **GitHub Codespace Requirements**
- GitHub account with Codespaces access
- Repository: `https://github.com/mmoramora/ADS599_Capstone`
- Recommended: 4-core, 8GB RAM Codespace

### **API Key Setup (Required)**
1. Get free SportMonks API key: [sportmonks.com/football-api](https://www.sportmonks.com/football-api)
2. Add as Codespace secret:
   - Go to repository **Settings** > **Secrets and variables** > **Codespaces**
   - Add secret: `SPORTMONKS_API_KEY` with your API key value

## 🎯 **Step-by-Step Installation**

### **Step 1: Create GitHub Codespace**
1. Go to: `https://github.com/mmoramora/ADS599_Capstone`
2. Click **Code** > **Codespaces** > **Create codespace on main**
3. Wait for Codespace to initialize

### **Step 2: Run Installation Script**
```bash
# Download and run the installation script
curl -fsSL https://raw.githubusercontent.com/mmoramora/ADS599_Capstone/main/scripts/setup/codespace_installation.sh | bash
```

### **Step 3: Start Services**
```bash
# Start all services
./start_codespace.sh
```

### **Step 4: Access Applications**
- **Jupyter Lab**: `https://[your-codespace]-8888.app.github.dev`
  - Token: `codespace_secure_token_2024`
- **pgAdmin**: `https://[your-codespace]-8080.app.github.dev`
  - Email: `admin@admin.com` / Password: `admin`

## 📊 **What Gets Installed**

### **🗄️ Database & Analytics**
- ✅ **PostgreSQL Database**: 67 UEFA Champions League teams, 8,080+ player statistics
- ✅ **Redis Cache**: High-performance data caching
- ✅ **Complete Dataset**: 2019-2024 seasons across multiple competitions
- ✅ **99.85% Data Consistency**: Multi-source integration with quality validation

### **📓 Jupyter Environment**
- ✅ **JupyterLab**: Complete data science environment
- ✅ **All Libraries**: pandas, numpy, matplotlib, seaborn, plotly, sqlalchemy
- ✅ **Notebook Storage**: `/workspaces/ADS599_Capstone/notebooks/`
- ✅ **Templates**: Ready-to-use analysis templates

### **🔧 Development Tools**
- ✅ **pgAdmin**: Database management interface
- ✅ **Docker**: Containerized services
- ✅ **Git Integration**: Version control with notebook handling
- ✅ **Python Environment**: All required packages

## 🛠️ **Management Commands**

### **Service Management**
```bash
# Start all services
./start_codespace.sh

# Stop all services
./stop_codespace.sh

# Check service status
./status_codespace.sh
```

### **Docker Commands**
```bash
# View running containers
docker-compose -f docker-compose.yml -f docker-compose.codespace.yml ps

# View logs
docker-compose -f docker-compose.yml -f docker-compose.codespace.yml logs [service-name]

# Restart specific service
docker-compose -f docker-compose.yml -f docker-compose.codespace.yml restart [service-name]
```

## 📓 **Quick Start Analysis**

### **Create Your First Notebook**
1. Open Jupyter Lab: `https://[your-codespace]-8888.app.github.dev`
2. Navigate to `notebooks/shared/templates/`
3. Copy `data_analysis_template.ipynb`
4. Start analyzing UEFA Champions League data!

### **Sample Analysis Code**
```python
# Connect to database
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://soccerapp:soccerpass123@postgres:5432/soccer_intelligence')

# Load UEFA Champions League data
query = """
SELECT 
    p.player_name,
    t.team_name,
    ps.goals,
    ps.assists,
    ps.player_rating
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
```

## 🔐 **Security & Configuration**

### **API Key Management**
- ✅ **Codespace Secrets**: API keys stored securely as GitHub secrets
- ✅ **Environment Variables**: Automatic injection into containers
- ✅ **No Hardcoding**: Never commit API keys to repository

### **Database Access**
- ✅ **Secure Connections**: PostgreSQL with proper authentication
- ✅ **Role-Based Access**: Different access levels for different use cases
- ✅ **Audit Logging**: Complete database access tracking

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Services Won't Start**
```bash
# Check Docker status
docker ps

# Restart all services
./stop_codespace.sh
./start_codespace.sh

# Check logs
docker-compose -f docker-compose.yml -f docker-compose.codespace.yml logs
```

#### **Database Connection Issues**
```bash
# Check database status
docker-compose -f docker-compose.yml -f docker-compose.codespace.yml ps postgres

# Test connection
docker exec -it postgres psql -U soccerapp -d soccer_intelligence -c "SELECT COUNT(*) FROM teams;"
```

#### **Jupyter Won't Load**
```bash
# Check Jupyter container
docker-compose -f docker-compose.yml -f docker-compose.codespace.yml ps jupyter-codespace

# Restart Jupyter
docker-compose -f docker-compose.yml -f docker-compose.codespace.yml restart jupyter-codespace

# Check logs
docker-compose -f docker-compose.yml -f docker-compose.codespace.yml logs jupyter-codespace
```

#### **Port Access Issues**
- Ensure Codespace ports are public
- Check port forwarding in Codespace interface
- Verify URLs use correct Codespace domain

## 📚 **Resources**

### **Documentation**
- **Project Overview**: `PROJECT_OVERVIEW.md`
- **Team Collaboration**: `TEAM_COLLABORATION_QUICK_START.md`
- **Research Paper**: `docs/research-methodology/`
- **Technical Docs**: `docs/`

### **Sample Queries**
```sql
-- Top goal scorers
SELECT p.player_name, t.team_name, SUM(ps.goals) as total_goals
FROM player_statistics ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams t ON ps.team_id = t.team_id
GROUP BY p.player_id, p.player_name, t.team_name
ORDER BY total_goals DESC
LIMIT 10;

-- Team performance by season
SELECT t.team_name, ps.season_year, AVG(ps.player_rating) as avg_rating
FROM player_statistics ps
JOIN teams t ON ps.team_id = t.team_id
GROUP BY t.team_id, t.team_name, ps.season_year
ORDER BY ps.season_year DESC, avg_rating DESC;
```

## ✅ **Success Checklist**

### **Installation Complete When**:
- [ ] All Docker services running
- [ ] Jupyter Lab accessible via Codespace URL
- [ ] pgAdmin accessible via Codespace URL
- [ ] Database contains UEFA Champions League data
- [ ] Can create and run notebooks
- [ ] API key configured as Codespace secret

### **Ready for Analysis When**:
- [ ] Can query database successfully
- [ ] Notebooks save and load properly
- [ ] Visualizations render correctly
- [ ] All Python libraries available

## 🎉 **You're Ready!**

Your complete ADS599 Capstone Soccer Intelligence System is now running in GitHub Codespace with:

- ✅ **67 UEFA Champions League teams** with comprehensive data
- ✅ **8,080+ player statistics** across 6 seasons (2019-2024)
- ✅ **Cloud-based Jupyter environment** accessible from anywhere
- ✅ **Professional database** with PostgreSQL and Redis
- ✅ **Advanced analytics** including Shapley value analysis
- ✅ **Zero local setup** - everything runs in the cloud

**Start analyzing UEFA Champions League data immediately!** 🚀⚽📊

---

**Quick Commands**:
- **Install**: `curl -fsSL https://raw.githubusercontent.com/mmoramora/ADS599_Capstone/main/scripts/setup/codespace_installation.sh | bash`
- **Start**: `./start_codespace.sh`
- **Status**: `./status_codespace.sh`
- **Stop**: `./stop_codespace.sh`

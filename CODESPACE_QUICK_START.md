# GitHub Codespace Quick Start
ADS599 Capstone Soccer Intelligence System

## 🚀 **One-Command Installation**

Open this repository in GitHub Codespace and run:

```bash
curl -fsSL https://raw.githubusercontent.com/mmoramora/ADS599_Capstone/main/scripts/setup/codespace_installation.sh | bash
```

## 📋 **Before You Start**

### **1. Create GitHub Codespace**
- Go to: [ADS599_Capstone Repository](https://github.com/mmoramora/ADS599_Capstone)
- Click **Code** → **Codespaces** → **Create codespace on main**
- Choose **4-core, 8GB RAM** for best performance

### **2. Set API Key (Required)**
1. Get free SportMonks API key: [sportmonks.com/football-api](https://www.sportmonks.com/football-api)
2. In GitHub repository:
   - Go to **Settings** → **Secrets and variables** → **Codespaces**
   - Add secret: `SPORTMONKS_API_KEY` = `your_api_key_here`

## ⚡ **Quick Setup (3 steps)**

### **Step 1: Install Everything**
```bash
# One command installs the complete system
curl -fsSL https://raw.githubusercontent.com/mmoramora/ADS599_Capstone/main/scripts/setup/codespace_installation.sh | bash
```

### **Step 2: Start Services**
```bash
# Start all services
./start_codespace.sh
```

### **Step 3: Access Applications**
- **Jupyter Lab**: Click the forwarded port 8888 in Codespace
  - Token: `codespace_secure_token_2024`
- **pgAdmin**: Click the forwarded port 8080 in Codespace
  - Email: `admin@admin.com` / Password: `admin`

## 📊 **What You Get**

### **🗄️ Complete Database**
- ✅ **67 UEFA Champions League Teams** (2019-2024)
- ✅ **8,080+ Player Statistics** with comprehensive metrics
- ✅ **PostgreSQL + Redis** for high-performance queries
- ✅ **99.85% Data Consistency** across sources

### **📓 Analysis Environment**
- ✅ **JupyterLab** with all data science libraries
- ✅ **Ready-to-use templates** for immediate analysis
- ✅ **Shared notebooks** for team collaboration
- ✅ **Advanced analytics** including Shapley value analysis

### **🔧 Management Tools**
- ✅ **pgAdmin** for database management
- ✅ **Docker containers** for isolated services
- ✅ **Git integration** with notebook handling
- ✅ **Automated backups** and data validation

## 🛠️ **Management Commands**

```bash
# Start all services
./start_codespace.sh

# Check service status
./status_codespace.sh

# Stop all services
./stop_codespace.sh
```

## 📓 **Quick Analysis Example**

1. **Open Jupyter Lab** (port 8888)
2. **Navigate to** `notebooks/shared/templates/`
3. **Copy** `data_analysis_template.ipynb`
4. **Run this code**:

```python
import pandas as pd
from sqlalchemy import create_engine

# Connect to database
engine = create_engine('postgresql://soccerapp:soccerpass123@postgres:5432/soccer_intelligence')

# Load Champions League data
query = """
SELECT p.player_name, t.team_name, ps.goals, ps.assists
FROM player_statistics ps
JOIN players p ON ps.player_id = p.player_id
JOIN teams t ON ps.team_id = t.team_id
JOIN competitions c ON ps.competition_id = c.competition_id
WHERE c.competition_name LIKE '%Champions League%'
ORDER BY ps.goals DESC
LIMIT 10
"""

df = pd.read_sql(query, engine)
print(f"Top {len(df)} Champions League goal scorers:")
display(df)
```

## 🚨 **Troubleshooting**

### **Services Won't Start**
```bash
# Restart everything
./stop_codespace.sh
./start_codespace.sh
```

### **Can't Access Jupyter/pgAdmin**
- Check **Ports** tab in Codespace
- Make sure ports 8888 and 8080 are **public**
- Use the generated URLs from port forwarding

### **Database Connection Issues**
```bash
# Check database status
docker-compose -f docker-compose.yml -f docker-compose.codespace.yml ps postgres

# Test connection
docker exec -it postgres psql -U soccerapp -d soccer_intelligence -c "SELECT COUNT(*) FROM teams;"
```

## 📚 **Documentation**

- **Complete Guide**: `CODESPACE_INSTALLATION_GUIDE.md`
- **Project Overview**: `PROJECT_OVERVIEW.md`
- **Team Collaboration**: `TEAM_COLLABORATION_QUICK_START.md`
- **Research Paper**: `docs/research-methodology/`

## ✅ **Success Checklist**

- [ ] Codespace created and running
- [ ] API key set as Codespace secret
- [ ] Installation script completed successfully
- [ ] Services started with `./start_codespace.sh`
- [ ] Jupyter Lab accessible via port forwarding
- [ ] pgAdmin accessible via port forwarding
- [ ] Can query database and see UEFA Champions League data
- [ ] Can create and run notebooks

## 🎉 **Ready to Analyze!**

You now have a complete cloud-based soccer intelligence system with:

- 🏆 **UEFA Champions League data** for 67 teams across 6 seasons
- 📊 **Professional analytics environment** with Jupyter Lab
- 🗄️ **High-performance database** with PostgreSQL and Redis
- 🔬 **Advanced analytics** including Shapley value analysis
- ☁️ **Zero local setup** - everything runs in the cloud

**Start analyzing soccer data immediately!** ⚽📊

---

**Need help?** Check the full installation guide or create a GitHub issue.

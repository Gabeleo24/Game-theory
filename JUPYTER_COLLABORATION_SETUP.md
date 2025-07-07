# Jupyter Notebook Collaboration System - ADS599 Capstone

## 🚀 Quick Setup for Team Members

### 1. One-Command Setup
```bash
# Setup complete Jupyter collaboration environment
./scripts/jupyter/setup_jupyter_collaboration.sh
```

### 2. Start Your Role-Specific Environment
```bash
# For Data Analysts
./scripts/jupyter/manage_notebooks.sh start-jupyter analyst

# For Developers  
./scripts/jupyter/manage_notebooks.sh start-jupyter developer

# For Researchers
./scripts/jupyter/manage_notebooks.sh start-jupyter researcher

# Start all environments
./scripts/jupyter/manage_notebooks.sh start-jupyter all
```

### 3. Access Your Jupyter Environment
- **🔍 Analyst**: http://localhost:8888 (token: `analyst_secure_token_2024`)
- **💻 Developer**: http://localhost:8889 (token: `developer_secure_token_2024`)  
- **📚 Researcher**: http://localhost:8890 (token: `researcher_secure_token_2024`)

## 📊 What You Get

### **Role-Based Access Control**
- **Analysts**: Read-only database, visualization tools, 4GB RAM
- **Developers**: Full system access, admin tools, 8GB RAM
- **Researchers**: Research tools, LaTeX support, 6GB RAM

### **Shared Collaboration Environment**
- ✅ **Same Data Access**: All working from identical UEFA Champions League dataset
- ✅ **Organized Structure**: Shared, personal, research, and archive directories
- ✅ **Version Control**: Git integration with automatic output cleaning
- ✅ **Security**: Role-based permissions and API key protection
- ✅ **Templates**: Ready-to-use notebook templates for quick start

### **Professional Workflow**
- ✅ **Naming Convention**: Standardized notebook naming
- ✅ **Code Review**: Pull request workflow for collaboration
- ✅ **Backup System**: Automatic notebook backups
- ✅ **Conflict Resolution**: Tools for handling merge conflicts

## 📁 Notebook Organization

**Storage Location**: `/Users/home/Documents/GitHub/ADS599_Capstone/notebooks/`

```
/Users/home/Documents/GitHub/ADS599_Capstone/notebooks/
├── shared/                 # 👥 Team collaboration notebooks
│   ├── templates/         # 📄 Notebook templates
│   ├── data_exploration/  # 🔍 Exploratory data analysis
│   ├── team_analysis/     # 🤝 Team projects
│   ├── reports/           # 📊 Generated reports
│   └── tutorials/         # 📚 Learning materials
├── personal/              # 👤 Individual workspaces
│   ├── analyst_workspace/
│   ├── developer_workspace/
│   └── researcher_workspace/
├── research/              # 🔬 Academic research
│   ├── methodology/
│   ├── literature_review/
│   ├── statistical_analysis/
│   └── publications/
└── archive/               # 📦 Completed work
```

**Note**: Notebooks are stored on your host system at the path above and mounted into Docker containers at `/app/notebooks/` for access within Jupyter environments.

## 🛠️ Management Commands

### **Environment Management**
```bash
# Check status of all environments
./scripts/jupyter/manage_notebooks.sh status

# Stop specific environment
./scripts/jupyter/manage_notebooks.sh stop-jupyter analyst

# Stop all environments
./scripts/jupyter/manage_notebooks.sh stop-jupyter all
```

### **Notebook Management**
```bash
# Create new notebook from template
./scripts/jupyter/manage_notebooks.sh create-notebook my_analysis

# List all notebooks
./scripts/jupyter/manage_notebooks.sh list-notebooks

# Backup all notebooks
./scripts/jupyter/manage_notebooks.sh backup

# Clean notebook outputs (before committing)
./scripts/jupyter/manage_notebooks.sh clean-outputs

# Sync with Git (cleans outputs and commits)
./scripts/jupyter/manage_notebooks.sh sync
```

### **Security Management**
```bash
# Scan notebooks for security issues
python scripts/jupyter/notebook_security_manager.py scan

# Generate security report
python scripts/jupyter/notebook_security_manager.py report

# Sanitize specific notebook
python scripts/jupyter/notebook_security_manager.py sanitize notebook.ipynb
```

## 🔐 Security Features

### **Built-in Protection**
- ✅ **API Key Detection**: Automatic scanning for hardcoded credentials
- ✅ **Role-Based Database Access**: Appropriate permissions for each role
- ✅ **Output Cleaning**: Automatic removal of outputs before Git commits
- ✅ **Sensitive Data Masking**: Protection of personal information
- ✅ **Security Auditing**: Regular security scans and reports

### **Database Access by Role**
```python
# Analyst (Read-Only)
engine = create_engine('postgresql://analyst_user:analyst_secure_pass@postgres:5432/soccer_intelligence')

# Developer (Full Access)
engine = create_engine('postgresql://soccerapp:soccerpass123@postgres:5432/soccer_intelligence')

# Researcher (Read-Only + Research Views)
engine = create_engine('postgresql://research_user:research_secure_pass@postgres:5432/soccer_intelligence')
```

## 📝 Collaboration Workflow

### **1. Creating Notebooks**
```bash
# Use command line
./scripts/jupyter/manage_notebooks.sh create-notebook team_analysis

# Or use Jupyter interface with templates
# Navigate to shared/templates/ and copy template
```

### **2. Naming Convention**
**Format**: `{date}_{author}_{purpose}_{version}.ipynb`

**Examples**:
- `2024-07-07_alice_player_analysis_v1.ipynb`
- `2024-07-07_bob_shapley_implementation_v2.ipynb`

### **3. Git Workflow**
```bash
# 1. Create feature branch
git checkout -b feature/notebook-analysis-name

# 2. Clean outputs and commit
./scripts/jupyter/manage_notebooks.sh clean-outputs
git add notebooks/shared/your_notebook.ipynb
git commit -m "feat: Add player performance analysis"

# 3. Push and create pull request
git push origin feature/notebook-analysis-name
```

### **4. Review Process**
- [ ] Notebook runs from clean state
- [ ] Clear documentation and comments  
- [ ] No hardcoded credentials
- [ ] Appropriate data access for role
- [ ] Results are reproducible

## 🎯 Quick Start Examples

### **Data Analysis Template**
```python
# Standard setup for all notebooks
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Role-appropriate database connection
engine = create_engine('postgresql://[role_user]:[role_pass]@postgres:5432/soccer_intelligence')

# Load and analyze data
query = """
SELECT p.player_name, t.team_name, ps.goals, ps.assists
FROM player_statistics ps
JOIN players p ON ps.player_id = p.player_id  
JOIN teams t ON ps.team_id = t.team_id
WHERE ps.minutes_played > 90
LIMIT 10
"""

df = pd.read_sql(query, engine)
display(df)
```

### **Visualization Example**
```python
# Create interactive visualizations
import plotly.express as px

fig = px.scatter(df, x='goals', y='assists', 
                hover_data=['player_name', 'team_name'],
                title='Goals vs Assists Analysis')
fig.show()
```

## 🚨 Troubleshooting

### **Environment Won't Start**
```bash
# Check Docker status
docker ps | grep jupyter

# Restart environment
./scripts/jupyter/manage_notebooks.sh stop-jupyter analyst
./scripts/jupyter/manage_notebooks.sh start-jupyter analyst

# Check logs
docker logs jupyter-analyst
```

### **Database Connection Issues**
```python
# Test connection
import psycopg2
try:
    conn = psycopg2.connect(
        host="postgres", port="5432", 
        database="soccer_intelligence",
        user="your_role_user", password="your_role_password"
    )
    print("✅ Connected successfully")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### **Git Conflicts**
```bash
# Backup your version
cp notebooks/shared/conflicted.ipynb notebooks/personal/my_backup.ipynb

# Pull latest and manually merge
git pull origin main
# Edit notebook to resolve conflicts
# Test merged version

# Commit resolved version
git add notebooks/shared/conflicted.ipynb
git commit -m "resolve: Merge notebook conflicts"
```

## 📚 Resources

### **Documentation**
- **Complete Guide**: `docs/jupyter-collaboration/JUPYTER_COLLABORATION_GUIDE.md`
- **Team Collaboration**: `docs/team-collaboration/README.md`
- **Database Access**: `docs/data-access/DATA_ACCESS_GUIDE.md`
- **Security Guidelines**: Generated by security manager

### **Templates Available**
- **Data Analysis**: `notebooks/shared/templates/data_analysis_template.ipynb`
- **Research Methodology**: `notebooks/shared/templates/research_methodology_template.ipynb`
- **Visualization**: `notebooks/shared/templates/visualization_template.ipynb`

### **Support**
- **GitHub Issues**: Technical problems and bugs
- **Team Meetings**: Collaboration questions
- **Documentation**: Comprehensive guides in `docs/`
- **Code Reviews**: Learning and improvement

## ✅ Success Checklist

### **Setup Complete When**:
- [ ] Jupyter environment starts successfully
- [ ] Can access role-appropriate database
- [ ] Can create notebooks from templates
- [ ] Git integration working (clean outputs)
- [ ] Security scans pass without issues

### **Ready for Collaboration When**:
- [ ] All team members have access
- [ ] Shared notebooks directory populated
- [ ] Git workflow established
- [ ] Code review process active
- [ ] Regular backups running

---

## 🎉 **You're Ready!**

Your ADS599 Capstone team now has a **professional-grade Jupyter collaboration system** with:

- ✅ **Role-based secure access** for analysts, developers, and researchers
- ✅ **Shared data environment** with UEFA Champions League dataset
- ✅ **Version control integration** with automatic output cleaning
- ✅ **Security management** with API key protection
- ✅ **Professional workflow** with templates and best practices

**Start collaborating and analyzing!** 🚀📓

---

**Quick Commands Reference**:
- **Setup**: `./scripts/jupyter/setup_jupyter_collaboration.sh`
- **Start**: `./scripts/jupyter/manage_notebooks.sh start-jupyter [role]`
- **Status**: `./scripts/jupyter/manage_notebooks.sh status`
- **Create**: `./scripts/jupyter/manage_notebooks.sh create-notebook [name]`
- **Security**: `python scripts/jupyter/notebook_security_manager.py scan`

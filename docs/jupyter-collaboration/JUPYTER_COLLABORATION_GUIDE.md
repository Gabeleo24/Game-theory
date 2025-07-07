# Jupyter Notebook Collaboration Guide
ADS599 Capstone Soccer Intelligence System

## Overview

This guide provides comprehensive instructions for collaborative Jupyter notebook development in the ADS599 Capstone Soccer Intelligence System. The system supports role-based access, shared environments, and secure collaboration workflows.

## Quick Start

### 1. Setup Jupyter Collaboration
```bash
# Run the setup script
./scripts/jupyter/setup_jupyter_collaboration.sh

# Start your role-specific environment
./scripts/jupyter/manage_notebooks.sh start-jupyter [your-role]
```

### 2. Access Your Environment
- **Analyst**: http://localhost:8888 (token: `analyst_secure_token_2024`)
- **Developer**: http://localhost:8889 (token: `developer_secure_token_2024`)
- **Researcher**: http://localhost:8890 (token: `researcher_secure_token_2024`)

### 3. Create Your First Notebook
```bash
# Create a new notebook from template
./scripts/jupyter/manage_notebooks.sh create-notebook my_analysis

# Or use the web interface to create from templates
```

## Role-Based Environments

### 🔍 Data Analyst Environment
**Purpose**: Data exploration, visualization, and reporting
**Access Level**: Read-only data with analysis tools

**Features**:
- Read-only database access (analyst_user/analyst_secure_pass)
- Jupyter Lab with visualization extensions
- Shared notebook access for collaboration
- 4GB memory limit, 2 CPU cores

**Available Extensions**:
- JupyterLab Git integration
- Plotly for interactive visualizations
- Variable inspector for debugging
- Spreadsheet-like data manipulation

**Data Access**:
```python
# Database connection for analysts
from sqlalchemy import create_engine
engine = create_engine('postgresql://analyst_user:analyst_secure_pass@postgres:5432/soccer_intelligence')
```

### 💻 Developer Environment
**Purpose**: Full-stack development and system maintenance
**Access Level**: Complete system access

**Features**:
- Full database access (soccerapp/soccerpass123)
- Complete project file access
- Docker socket access for container management
- 8GB memory limit, 4 CPU cores

**Additional Extensions**:
- Docker container management
- System resource monitoring
- Full file system access
- Development tools integration

**Data Access**:
```python
# Database connection for developers
from sqlalchemy import create_engine
engine = create_engine('postgresql://soccerapp:soccerpass123@postgres:5432/soccer_intelligence')
```

### 📚 Researcher Environment
**Purpose**: Academic research and methodology development
**Access Level**: Read-only data with research tools

**Features**:
- Read-only database access (research_user/research_secure_pass)
- Research-focused notebook directory
- LaTeX support for academic writing
- 6GB memory limit, 3 CPU cores

**Research Extensions**:
- LaTeX rendering for equations
- Citation management
- Academic writing tools
- Literature review support

**Data Access**:
```python
# Database connection for researchers
from sqlalchemy import create_engine
engine = create_engine('postgresql://research_user:research_secure_pass@postgres:5432/soccer_intelligence')
```

## Notebook Organization

### Directory Structure
```
/Users/home/Documents/GitHub/ADS599_Capstone/notebooks/
├── shared/                 # Collaborative notebooks (all roles)
│   ├── templates/         # Notebook templates
│   ├── data_exploration/  # Exploratory data analysis
│   ├── team_analysis/     # Team collaboration projects
│   ├── reports/           # Generated reports
│   └── tutorials/         # Learning materials
├── personal/              # Individual workspaces
│   ├── analyst_workspace/
│   ├── developer_workspace/
│   └── researcher_workspace/
├── research/              # Academic research (researchers + developers)
│   ├── methodology/
│   ├── literature_review/
│   ├── statistical_analysis/
│   └── publications/
└── archive/               # Completed and deprecated notebooks
    ├── completed_projects/
    ├── deprecated_analyses/
    └── backup_notebooks/
```

**Storage Location**: All notebooks are stored in `/Users/home/Documents/GitHub/ADS599_Capstone/notebooks/` on the host system and mounted to `/app/notebooks/` inside the Docker containers.

### Naming Convention
**Format**: `{date}_{author}_{purpose}_{version}.ipynb`

**Examples**:
- `2024-07-07_alice_player_analysis_v1.ipynb`
- `2024-07-07_bob_shapley_implementation_v2.ipynb`
- `2024-07-07_carol_research_methodology_v1.ipynb`

## Collaboration Workflow

### 1. Creating New Notebooks

#### Using Command Line
```bash
# Create from template
./scripts/jupyter/manage_notebooks.sh create-notebook team_analysis

# This creates: 2024-07-07_yourname_team_analysis_v1.ipynb
```

#### Using Jupyter Interface
1. Navigate to appropriate directory (`shared/`, `personal/`, `research/`)
2. Click "New" → "Notebook" → "Python 3"
3. Rename following naming convention
4. Copy template structure from `shared/templates/`

### 2. Notebook Development Process

#### Step 1: Setup and Documentation
```python
# First cell - Always include project header
"""
# Analysis Title
**Author:** Your Name
**Date:** 2024-07-07
**Purpose:** Brief description of analysis
**Team Role:** analyst/developer/researcher

## Analysis Overview
Brief description of objectives and methodology.

## Data Sources
- Database tables used
- API endpoints accessed
- File sources

## Key Findings
Summary of main insights (update at end)
"""
```

#### Step 2: Environment Setup
```python
# Standard imports for all notebooks
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Database connection
from sqlalchemy import create_engine
import sys
sys.path.append('/app/src')
from soccer_intelligence.utils.config import Config

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
plt.style.use('seaborn-v0_8')

print("✅ Environment setup complete")
```

#### Step 3: Data Loading and Validation
```python
# Role-appropriate database connection
# (Use your role-specific credentials)
engine = create_engine('postgresql://[role_user]:[role_pass]@postgres:5432/soccer_intelligence')

# Test connection and load data
try:
    test_query = "SELECT COUNT(*) as total_teams FROM teams"
    result = pd.read_sql(test_query, engine)
    print(f"✅ Database connected. Total teams: {result['total_teams'].iloc[0]}")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

### 3. Sharing and Review Process

#### Before Sharing
```bash
# Clean outputs and check notebook
./scripts/jupyter/manage_notebooks.sh clean-outputs

# Test notebook execution from clean state
# (Restart kernel and run all cells)
```

#### Git Workflow
```bash
# 1. Create feature branch
git checkout -b feature/notebook-analysis-name

# 2. Add and commit notebook
git add notebooks/shared/your_notebook.ipynb
git commit -m "feat: Add team analysis notebook for player performance"

# 3. Push and create pull request
git push origin feature/notebook-analysis-name
# Create PR on GitHub
```

#### Review Checklist
- [ ] Notebook runs from clean state
- [ ] Clear documentation and comments
- [ ] Appropriate data access for role
- [ ] No hardcoded credentials or API keys
- [ ] Results are reproducible
- [ ] Conclusions are well-documented

## Data Access and Security

### Database Connections by Role

#### Analyst (Read-Only)
```python
# Secure read-only access
engine = create_engine('postgresql://analyst_user:analyst_secure_pass@postgres:5432/soccer_intelligence')

# Available tables (SELECT only)
tables = ['teams', 'players', 'matches', 'player_statistics', 'competitions']
```

#### Developer (Full Access)
```python
# Full database access
engine = create_engine('postgresql://soccerapp:soccerpass123@postgres:5432/soccer_intelligence')

# Can create tables, modify data, run admin queries
```

#### Researcher (Read-Only + Research Views)
```python
# Research-focused access
engine = create_engine('postgresql://research_user:research_secure_pass@postgres:5432/soccer_intelligence')

# Access to research-specific views and aggregated data
```

### API Key Management
```python
# NEVER hardcode API keys in notebooks
# Use environment variables or config files

# Correct approach:
from soccer_intelligence.utils.config import Config
config = Config()
api_key = config.get('api_football.key')

# Incorrect approach (NEVER do this):
# api_key = "your_actual_api_key_here"  # ❌ NEVER!
```

### Sensitive Data Handling
```python
# Mask sensitive information in outputs
def mask_sensitive_data(df, columns):
    """Mask sensitive columns for display"""
    masked_df = df.copy()
    for col in columns:
        if col in masked_df.columns:
            masked_df[col] = '***MASKED***'
    return masked_df

# Example usage
display_df = mask_sensitive_data(player_df, ['email', 'phone', 'address'])
display(display_df)
```

## Version Control and Backup

### Automatic Backup
```bash
# Backup all notebooks
./scripts/jupyter/manage_notebooks.sh backup

# Backups stored in: backups/notebooks/notebook_backup_YYYYMMDD_HHMMSS.tar.gz
```

### Git Integration
```bash
# Sync notebooks with Git (cleans outputs first)
./scripts/jupyter/manage_notebooks.sh sync

# Clean outputs manually
./scripts/jupyter/manage_notebooks.sh clean-outputs
```

### Conflict Resolution

#### When Conflicts Occur
1. **Backup your version**:
   ```bash
   cp notebooks/shared/conflicted_notebook.ipynb notebooks/personal/my_backup.ipynb
   ```

2. **Pull latest changes**:
   ```bash
   git pull origin main
   ```

3. **Manual merge**:
   - Open both versions in Jupyter
   - Copy your unique contributions
   - Test merged version thoroughly

4. **Commit resolved version**:
   ```bash
   git add notebooks/shared/conflicted_notebook.ipynb
   git commit -m "resolve: Merge notebook conflicts"
   ```

## Performance and Resource Management

### Memory Management
```python
# Monitor memory usage
import psutil
import os

def check_memory_usage():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Current memory usage: {memory_mb:.1f} MB")
    
    # Role-specific limits
    limits = {
        'analyst': 4096,    # 4GB
        'developer': 8192,  # 8GB
        'researcher': 6144  # 6GB
    }
    
    role = os.environ.get('JUPYTER_ROLE', 'unknown')
    if role in limits and memory_mb > limits[role] * 0.8:
        print(f"⚠️ Warning: Approaching memory limit for {role} role")

# Call periodically in long-running notebooks
check_memory_usage()
```

### Efficient Data Loading
```python
# Load data in chunks for large datasets
def load_data_efficiently(query, engine, chunk_size=10000):
    """Load large datasets in chunks"""
    chunks = []
    for chunk in pd.read_sql(query, engine, chunksize=chunk_size):
        # Process chunk if needed
        chunks.append(chunk)
    return pd.concat(chunks, ignore_index=True)

# Example usage
large_df = load_data_efficiently(
    "SELECT * FROM player_statistics WHERE season_year >= 2020",
    engine
)
```

## Troubleshooting

### Common Issues

#### Jupyter Won't Start
```bash
# Check Docker status
docker ps | grep jupyter

# Restart specific environment
./scripts/jupyter/manage_notebooks.sh stop-jupyter analyst
./scripts/jupyter/manage_notebooks.sh start-jupyter analyst

# Check logs
docker logs jupyter-analyst
```

#### Database Connection Issues
```python
# Test database connectivity
import psycopg2

try:
    conn = psycopg2.connect(
        host="postgres",
        port="5432",
        database="soccer_intelligence",
        user="your_role_user",
        password="your_role_password"
    )
    print("✅ Database connection successful")
    conn.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

#### Memory Issues
```bash
# Check resource usage
./scripts/jupyter/manage_notebooks.sh status

# Restart with clean state
docker restart jupyter-[your-role]
```

#### Git Conflicts
```bash
# Reset to clean state (CAUTION: loses local changes)
git checkout -- notebooks/

# Or resolve manually as described in conflict resolution section
```

## Best Practices

### Code Quality
- Use clear variable names and comments
- Follow PEP 8 style guidelines
- Create functions for repeated code
- Import modules at the top
- Use type hints where appropriate

### Documentation
- Document analysis objectives clearly
- Explain methodology and assumptions
- Interpret results and findings
- Note limitations and caveats
- Provide next steps and recommendations

### Collaboration
- Communicate changes to team
- Use descriptive commit messages
- Review others' notebooks constructively
- Share insights and learnings
- Maintain consistent coding standards

### Security
- Never commit API keys or credentials
- Use role-appropriate database access
- Mask sensitive information in outputs
- Follow data privacy guidelines
- Report security concerns immediately

## Resources

### Templates
- `notebooks/shared/templates/data_analysis_template.ipynb`
- `notebooks/shared/templates/research_methodology_template.ipynb`
- `notebooks/shared/templates/visualization_template.ipynb`

### Documentation
- Project documentation: `docs/`
- Database schema: `docker/postgres/init.sql`
- API documentation: Source code
- Team collaboration: `docs/team-collaboration/`

### Support
- GitHub Issues: Technical problems
- Team meetings: Collaboration questions
- Documentation: Comprehensive guides
- Code reviews: Learning and improvement

---

**Happy collaborating!** 🚀📓

This Jupyter collaboration system enables your team to work together effectively while maintaining security, organization, and academic standards for your ADS599 Capstone project.

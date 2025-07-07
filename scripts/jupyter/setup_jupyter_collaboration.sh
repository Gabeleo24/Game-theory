#!/bin/bash

# Jupyter Notebook Collaboration Setup Script
# ADS599 Capstone Soccer Intelligence System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker Compose command exists
if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    print_error "Docker Compose is not available"
    exit 1
fi

echo "=========================================="
echo "📓 Jupyter Collaboration Setup"
echo "=========================================="
echo ""

# Function to create notebook directory structure
setup_notebook_directories() {
    print_status "Setting up notebook directory structure..."

    # Define the specific notebook path
    NOTEBOOKS_PATH="/Users/home/Documents/GitHub/ADS599_Capstone/notebooks"
    BACKUPS_PATH="/Users/home/Documents/GitHub/ADS599_Capstone/backups/notebooks"

    # Create main notebook directories
    mkdir -p "$NOTEBOOKS_PATH"/{shared,personal,research,archive}

    # Create shared subdirectories
    mkdir -p "$NOTEBOOKS_PATH"/shared/{templates,data_exploration,team_analysis,reports,tutorials}

    # Create personal workspaces
    mkdir -p "$NOTEBOOKS_PATH"/personal/{analyst_workspace,developer_workspace,researcher_workspace}

    # Create research subdirectories
    mkdir -p "$NOTEBOOKS_PATH"/research/{methodology,literature_review,statistical_analysis,publications}

    # Create archive subdirectories
    mkdir -p "$NOTEBOOKS_PATH"/archive/{completed_projects,deprecated_analyses,backup_notebooks}

    # Create backup directory
    mkdir -p "$BACKUPS_PATH"

    print_success "Notebook directory structure created at: $NOTEBOOKS_PATH"
}

# Function to create notebook templates
create_notebook_templates() {
    print_status "Creating notebook templates..."

    # Define the specific template path
    TEMPLATES_PATH="/Users/home/Documents/GitHub/ADS599_Capstone/notebooks/shared/templates"

    # Data Analysis Template
    cat > "$TEMPLATES_PATH"/data_analysis_template.ipynb << 'EOF'
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Data Analysis Template\n",
    "**Author:** [Your Name]  \n",
    "**Date:** [Date]  \n",
    "**Purpose:** [Analysis Purpose]  \n",
    "**Team Role:** [analyst/developer/researcher]  \n",
    "\n",
    "## Analysis Overview\n",
    "Brief description of the analysis objectives and methodology.\n",
    "\n",
    "## Data Sources\n",
    "- Database tables used\n",
    "- API endpoints accessed\n",
    "- File sources\n",
    "\n",
    "## Key Findings\n",
    "Summary of main insights and conclusions."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Environment Setup and Imports"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Standard imports\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "import warnings\n",
    "warnings.filterwarnings('ignore')\n",
    "\n",
    "# Database connection\n",
    "import psycopg2\n",
    "from sqlalchemy import create_engine\n",
    "import os\n",
    "\n",
    "# Project-specific imports\n",
    "import sys\n",
    "sys.path.append('/app/src')\n",
    "from soccer_intelligence.utils.config import Config\n",
    "from soccer_intelligence.utils.database import DatabaseManager\n",
    "\n",
    "# Set display options\n",
    "pd.set_option('display.max_columns', None)\n",
    "pd.set_option('display.max_rows', 100)\n",
    "plt.style.use('seaborn-v0_8')\n",
    "sns.set_palette('husl')\n",
    "\n",
    "print(\"✅ Environment setup complete\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Database Connection and Data Loading"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Database connection based on role\n",
    "# Note: Use appropriate credentials for your role\n",
    "\n",
    "# For analysts and researchers (read-only)\n",
    "# engine = create_engine('postgresql://analyst_user:analyst_secure_pass@postgres:5432/soccer_intelligence')\n",
    "\n",
    "# For developers (full access)\n",
    "# engine = create_engine('postgresql://soccerapp:soccerpass123@postgres:5432/soccer_intelligence')\n",
    "\n",
    "# Test connection\n",
    "try:\n",
    "    # Replace with your role-appropriate connection\n",
    "    engine = create_engine('postgresql://soccerapp:soccerpass123@postgres:5432/soccer_intelligence')\n",
    "    \n",
    "    # Test query\n",
    "    test_query = \"SELECT COUNT(*) as total_teams FROM teams\"\n",
    "    result = pd.read_sql(test_query, engine)\n",
    "    print(f\"✅ Database connected successfully. Total teams: {result['total_teams'].iloc[0]}\")\n",
    "    \n",
    "except Exception as e:\n",
    "    print(f\"❌ Database connection failed: {e}\")\n",
    "    print(\"Please check your database credentials and connection.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Data Exploration"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Load and explore your data here\n",
    "# Example: Load player statistics\n",
    "\n",
    "query = \"\"\"\n",
    "SELECT \n",
    "    p.player_name,\n",
    "    t.team_name,\n",
    "    ps.season_year,\n",
    "    ps.goals,\n",
    "    ps.assists,\n",
    "    ps.minutes_played\n",
    "FROM player_statistics ps\n",
    "JOIN players p ON ps.player_id = p.player_id\n",
    "JOIN teams t ON ps.team_id = t.team_id\n",
    "WHERE ps.minutes_played > 90\n",
    "LIMIT 10\n",
    "\"\"\"\n",
    "\n",
    "df = pd.read_sql(query, engine)\n",
    "print(\"Sample data:\")\n",
    "display(df.head())\n",
    "print(f\"\\nDataset shape: {df.shape}\")\n",
    "print(f\"Data types:\\n{df.dtypes}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Analysis and Visualization"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Your analysis code here\n",
    "# Example: Basic visualization\n",
    "\n",
    "if not df.empty:\n",
    "    plt.figure(figsize=(12, 6))\n",
    "    \n",
    "    plt.subplot(1, 2, 1)\n",
    "    plt.scatter(df['goals'], df['assists'], alpha=0.7)\n",
    "    plt.xlabel('Goals')\n",
    "    plt.ylabel('Assists')\n",
    "    plt.title('Goals vs Assists')\n",
    "    \n",
    "    plt.subplot(1, 2, 2)\n",
    "    df['goals'].hist(bins=20, alpha=0.7)\n",
    "    plt.xlabel('Goals')\n",
    "    plt.ylabel('Frequency')\n",
    "    plt.title('Distribution of Goals')\n",
    "    \n",
    "    plt.tight_layout()\n",
    "    plt.show()\n",
    "else:\n",
    "    print(\"No data available for visualization\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Results and Conclusions"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Key Findings\n",
    "- [Finding 1]\n",
    "- [Finding 2]\n",
    "- [Finding 3]\n",
    "\n",
    "### Recommendations\n",
    "- [Recommendation 1]\n",
    "- [Recommendation 2]\n",
    "\n",
    "### Next Steps\n",
    "- [Next step 1]\n",
    "- [Next step 2]\n",
    "\n",
    "### Notes for Team\n",
    "- [Important notes for team members]\n",
    "- [Data quality observations]\n",
    "- [Methodology considerations]"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
EOF

    print_success "Data analysis template created"
}

# Function to create Jupyter configuration files
create_jupyter_configs() {
    print_status "Creating Jupyter configuration files..."

    # Create Jupyter config directory
    CONFIG_PATH="/Users/home/Documents/GitHub/ADS599_Capstone/config/jupyter"
    mkdir -p "$CONFIG_PATH"
    
    # Analyst Jupyter config
    cat > "$CONFIG_PATH"/jupyter_config_analyst.py << 'EOF'
# Jupyter Configuration for Analyst Role
# ADS599 Capstone Soccer Intelligence System

c = get_config()

# Server configuration
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.allow_root = True
c.ServerApp.open_browser = False
c.ServerApp.notebook_dir = '/app/notebooks/shared'

# Security configuration
c.ServerApp.token = 'analyst_secure_token_2024'
c.ServerApp.password = 'argon2:$argon2id$v=19$m=10240,t=10,p=8$soccer_intelligence_analyst'
c.ServerApp.allow_origin = '*'
c.ServerApp.disable_check_xsrf = False

# Resource limits
c.ResourceUseDisplay.mem_limit = 4 * 1024**3  # 4GB
c.ResourceUseDisplay.track_cpu_percent = True

# File access restrictions
c.ContentsManager.allow_hidden = False
c.FileContentsManager.delete_to_trash = True

# Kernel management
c.MappingKernelManager.cull_idle_timeout = 1800  # 30 minutes
c.MappingKernelManager.cull_interval = 300       # 5 minutes

# Extensions
c.ServerApp.jpserver_extensions = {
    'jupyterlab': True,
    'jupyterlab_git': True,
    'jupyterlab_plotly': True
}
EOF

    # Developer Jupyter config
    cat > "$CONFIG_PATH"/jupyter_config_developer.py << 'EOF'
# Jupyter Configuration for Developer Role
# ADS599 Capstone Soccer Intelligence System

c = get_config()

# Server configuration
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8889
c.ServerApp.allow_root = True
c.ServerApp.open_browser = False
c.ServerApp.notebook_dir = '/app'

# Security configuration
c.ServerApp.token = 'developer_secure_token_2024'
c.ServerApp.password = 'argon2:$argon2id$v=19$m=10240,t=10,p=8$soccer_intelligence_dev'
c.ServerApp.allow_origin = '*'
c.ServerApp.disable_check_xsrf = False

# Resource limits
c.ResourceUseDisplay.mem_limit = 8 * 1024**3  # 8GB
c.ResourceUseDisplay.track_cpu_percent = True

# Full file access for developers
c.ContentsManager.allow_hidden = True
c.FileContentsManager.delete_to_trash = True

# Kernel management
c.MappingKernelManager.cull_idle_timeout = 3600  # 1 hour
c.MappingKernelManager.cull_interval = 300       # 5 minutes

# Extensions
c.ServerApp.jpserver_extensions = {
    'jupyterlab': True,
    'jupyterlab_git': True,
    'jupyterlab_plotly': True,
    'jupyterlab_system_monitor': True
}
EOF

    # Researcher Jupyter config
    cat > "$CONFIG_PATH"/jupyter_config_researcher.py << 'EOF'
# Jupyter Configuration for Researcher Role
# ADS599 Capstone Soccer Intelligence System

c = get_config()

# Server configuration
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8890
c.ServerApp.allow_root = True
c.ServerApp.open_browser = False
c.ServerApp.notebook_dir = '/app/notebooks/research'

# Security configuration
c.ServerApp.token = 'researcher_secure_token_2024'
c.ServerApp.password = 'argon2:$argon2id$v=19$m=10240,t=10,p=8$soccer_intelligence_research'
c.ServerApp.allow_origin = '*'
c.ServerApp.disable_check_xsrf = False

# Resource limits
c.ResourceUseDisplay.mem_limit = 6 * 1024**3  # 6GB
c.ResourceUseDisplay.track_cpu_percent = True

# File access restrictions
c.ContentsManager.allow_hidden = False
c.FileContentsManager.delete_to_trash = True

# Kernel management
c.MappingKernelManager.cull_idle_timeout = 1800  # 30 minutes
c.MappingKernelManager.cull_interval = 300       # 5 minutes

# Extensions
c.ServerApp.jpserver_extensions = {
    'jupyterlab': True,
    'jupyterlab_git': True,
    'jupyterlab_plotly': True,
    'jupyterlab_latex': True
}
EOF

    print_success "Jupyter configuration files created"
}

# Function to setup Git integration for notebooks
setup_git_integration() {
    print_status "Setting up Git integration for notebooks..."
    
    # Install nbstripout for clean notebook commits
    pip install nbstripout
    
    # Configure nbstripout
    nbstripout --install --attributes .gitattributes
    
    # Create .gitattributes for notebook handling
    cat >> .gitattributes << 'EOF'

# Jupyter Notebook handling
*.ipynb filter=nbstripout
*.ipynb diff=ipynb
*.ipynb merge=nbstripout-merge
EOF

    # Create notebook-specific .gitignore
    cat > notebooks/.gitignore << 'EOF'
# Jupyter Notebook checkpoints
.ipynb_checkpoints/

# Jupyter Lab workspace files
.jupyter/

# Temporary files
*.tmp
*.temp

# Large output files
*.png
*.jpg
*.jpeg
*.gif
*.pdf
*.svg

# Data files (should be in data/ directory)
*.csv
*.json
*.xlsx
*.parquet

# Cache files
__pycache__/
*.pyc
*.pyo
*.pyd

# Personal workspace files (keep personal work private)
personal/*/private_*
personal/*/.private/
EOF

    print_success "Git integration configured"
}

# Function to create collaboration guidelines
create_collaboration_guidelines() {
    print_status "Creating collaboration guidelines..."
    
    cat > notebooks/COLLABORATION_GUIDELINES.md << 'EOF'
# Jupyter Notebook Collaboration Guidelines
ADS599 Capstone Soccer Intelligence System

## Notebook Organization

### Directory Structure
- `shared/` - Notebooks accessible to all team members
- `personal/` - Individual workspaces (role-specific)
- `research/` - Academic research and methodology
- `archive/` - Completed and deprecated notebooks

### Naming Convention
Format: `{date}_{author}_{purpose}_{version}.ipynb`

Examples:
- `2024-07-07_alice_player_analysis_v1.ipynb`
- `2024-07-07_bob_shapley_implementation_v2.ipynb`
- `2024-07-07_carol_research_methodology_v1.ipynb`

## Collaboration Workflow

### 1. Creating New Notebooks
1. Use appropriate template from `shared/templates/`
2. Follow naming convention
3. Add clear documentation in first cell
4. Include author, date, purpose, and team role

### 2. Sharing Notebooks
1. Place in appropriate shared directory
2. Test execution from clean state
3. Clear all outputs before committing
4. Add descriptive commit message
5. Create pull request for review

### 3. Reviewing Notebooks
1. Check code quality and documentation
2. Verify reproducibility
3. Test with different data subsets
4. Provide constructive feedback
5. Approve after addressing concerns

## Best Practices

### Code Quality
- Use clear variable names
- Add comments for complex logic
- Follow PEP 8 style guidelines
- Import modules at the top
- Use functions for repeated code

### Documentation
- Document analysis objectives
- Explain methodology and assumptions
- Interpret results and findings
- Note limitations and caveats
- Provide next steps and recommendations

### Data Security
- Never commit API keys or credentials
- Use environment variables for sensitive data
- Mask sensitive information in outputs
- Follow role-based access permissions

### Performance
- Clear outputs before committing
- Avoid loading large datasets unnecessarily
- Use efficient pandas operations
- Monitor memory usage
- Cache intermediate results when appropriate

## Conflict Resolution

### Version Conflicts
1. Create backup of your version
2. Pull latest changes from main branch
3. Manually merge conflicting sections
4. Test merged notebook thoroughly
5. Commit resolved version

### Collaboration Issues
1. Communicate early and often
2. Use GitHub issues for technical problems
3. Schedule team meetings for complex conflicts
4. Document decisions and rationale

## Role-Specific Guidelines

### Analysts
- Focus on data exploration and visualization
- Use read-only database connections
- Share insights through clear visualizations
- Document data quality observations

### Developers
- Implement new features and optimizations
- Test code thoroughly before sharing
- Document API changes and new functions
- Maintain backward compatibility

### Researchers
- Focus on methodology and academic rigor
- Document statistical assumptions
- Provide literature references
- Ensure reproducibility of analyses

## Resources

### Templates
- `shared/templates/data_analysis_template.ipynb`
- `shared/templates/research_methodology_template.ipynb`
- `shared/templates/visualization_template.ipynb`

### Documentation
- Project documentation in `docs/`
- Database schema in `docker/postgres/init.sql`
- API documentation in source code

### Support
- GitHub Issues for technical problems
- Team meetings for collaboration questions
- Documentation in `docs/team-collaboration/`
EOF

    print_success "Collaboration guidelines created"
}

# Main setup function
main() {
    print_status "Starting Jupyter collaboration setup..."
    
    setup_notebook_directories
    create_notebook_templates
    create_jupyter_configs
    setup_git_integration
    create_collaboration_guidelines
    
    print_success "Jupyter collaboration setup complete!"
    echo ""
    echo "📓 Jupyter Environments:"
    echo "  Analyst:    http://localhost:8888 (token: analyst_secure_token_2024)"
    echo "  Developer:  http://localhost:8889 (token: developer_secure_token_2024)"
    echo "  Researcher: http://localhost:8890 (token: researcher_secure_token_2024)"
    echo ""
    echo "📁 Notebook Structure:"
    echo "  Shared:     notebooks/shared/"
    echo "  Personal:   notebooks/personal/"
    echo "  Research:   notebooks/research/"
    echo "  Archive:    notebooks/archive/"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Start Jupyter environments with role-specific Docker profiles"
    echo "  2. Review collaboration guidelines in notebooks/COLLABORATION_GUIDELINES.md"
    echo "  3. Use templates in notebooks/shared/templates/"
    echo "  4. Follow naming convention for new notebooks"
    echo ""
    echo "🚀 Ready for team collaboration!"
}

# Execute main function
main "$@"

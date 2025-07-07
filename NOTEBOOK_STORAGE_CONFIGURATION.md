# Jupyter Notebook Storage Configuration
ADS599 Capstone Soccer Intelligence System

## ✅ Storage Location Configured

Your Jupyter notebook collaboration system is now configured to store all notebooks at:

**Host Path**: `/Users/home/Documents/GitHub/ADS599_Capstone/notebooks/`

## 📁 Directory Structure Created

```
/Users/home/Documents/GitHub/ADS599_Capstone/notebooks/
├── shared/                 # Team collaboration notebooks
│   ├── templates/         # Ready-to-use templates
│   │   └── data_analysis_template.ipynb
│   ├── data_exploration/  # Exploratory data analysis
│   ├── team_analysis/     # Collaborative projects
│   ├── reports/           # Generated reports
│   └── tutorials/         # Learning materials
├── personal/              # Individual workspaces
│   ├── analyst_workspace/
│   ├── developer_workspace/
│   └── researcher_workspace/
├── research/              # Academic research
│   ├── methodology/
│   ├── literature_review/
│   ├── statistical_analysis/
│   └── publications/
└── archive/               # Completed work
    ├── completed_projects/
    ├── deprecated_analyses/
    └── backup_notebooks/
```

## 🔧 Configuration Details

### Docker Volume Mounts
The Docker Compose configuration now uses absolute paths:

```yaml
# Analyst Environment
volumes:
  - /Users/home/Documents/GitHub/ADS599_Capstone/notebooks:/app/notebooks:cached

# Developer Environment  
volumes:
  - /Users/home/Documents/GitHub/ADS599_Capstone:/app:cached

# Researcher Environment
volumes:
  - /Users/home/Documents/GitHub/ADS599_Capstone/notebooks:/app/notebooks:cached
```

### Path Mapping
- **Host Storage**: `/Users/home/Documents/GitHub/ADS599_Capstone/notebooks/`
- **Container Access**: `/app/notebooks/` (mounted from host)
- **Git Repository**: Notebooks are part of the Git repository
- **Backup Location**: `/Users/home/Documents/GitHub/ADS599_Capstone/backups/notebooks/`

## 🚀 Quick Start

### 1. Verify Setup
```bash
# Check that everything is configured correctly
./scripts/jupyter/verify_notebook_paths.sh
```

### 2. Start Jupyter Environments
```bash
# Start your role-specific environment
./scripts/jupyter/manage_notebooks.sh start-jupyter analyst
./scripts/jupyter/manage_notebooks.sh start-jupyter developer
./scripts/jupyter/manage_notebooks.sh start-jupyter researcher

# Or start all environments
./scripts/jupyter/manage_notebooks.sh start-jupyter all
```

### 3. Access Jupyter
- **Analyst**: http://localhost:8888 (token: `analyst_secure_token_2024`)
- **Developer**: http://localhost:8889 (token: `developer_secure_token_2024`)
- **Researcher**: http://localhost:8890 (token: `researcher_secure_token_2024`)

### 4. Create Your First Notebook
```bash
# Create from template
./scripts/jupyter/manage_notebooks.sh create-notebook my_analysis

# This creates: /Users/home/Documents/GitHub/ADS599_Capstone/notebooks/shared/2024-07-07_yourname_my_analysis_v1.ipynb
```

## 📊 Benefits of This Configuration

### **Predictable Storage**
- ✅ Notebooks stored at known, accessible location
- ✅ Easy to find and access files outside of Jupyter
- ✅ Integration with host file system and editors
- ✅ Consistent path handling across all tools

### **Team Collaboration**
- ✅ All team members use the same storage structure
- ✅ Shared notebooks accessible to appropriate roles
- ✅ Version control integration with Git
- ✅ Backup and synchronization capabilities

### **Development Workflow**
- ✅ Direct file access for debugging and editing
- ✅ Integration with IDEs and text editors
- ✅ Easy file sharing and collaboration
- ✅ Consistent development environment

## 🛠️ Management Commands

### **Environment Management**
```bash
# Check status
./scripts/jupyter/manage_notebooks.sh status

# Stop environments
./scripts/jupyter/manage_notebooks.sh stop-jupyter all
```

### **Notebook Operations**
```bash
# List all notebooks
./scripts/jupyter/manage_notebooks.sh list-notebooks

# Backup notebooks
./scripts/jupyter/manage_notebooks.sh backup

# Clean outputs before Git commit
./scripts/jupyter/manage_notebooks.sh clean-outputs

# Sync with Git
./scripts/jupyter/manage_notebooks.sh sync
```

### **Security Management**
```bash
# Scan for security issues
python scripts/jupyter/notebook_security_manager.py scan

# Generate security report
python scripts/jupyter/notebook_security_manager.py report
```

## 🔍 Verification

### **Check Directory Structure**
```bash
ls -la /Users/home/Documents/GitHub/ADS599_Capstone/notebooks/
```

### **Verify Docker Mounts**
```bash
# Start an environment and check mount
./scripts/jupyter/manage_notebooks.sh start-jupyter analyst
docker exec jupyter-analyst ls -la /app/notebooks/
```

### **Test Notebook Creation**
```bash
# Create test notebook
./scripts/jupyter/manage_notebooks.sh create-notebook test_notebook

# Verify it exists on host
ls -la /Users/home/Documents/GitHub/ADS599_Capstone/notebooks/shared/
```

## 📚 Documentation

### **Complete Guides**
- **Setup Guide**: `JUPYTER_COLLABORATION_SETUP.md`
- **Detailed Documentation**: `docs/jupyter-collaboration/JUPYTER_COLLABORATION_GUIDE.md`
- **Team Collaboration**: `docs/team-collaboration/README.md`

### **Configuration Files**
- **Jupyter Config**: `config/jupyter_collaboration_config.yaml`
- **Docker Compose**: `docker-compose.yml` (updated with absolute paths)
- **Git Attributes**: `.gitattributes` (notebook handling)

### **Scripts and Tools**
- **Setup**: `./scripts/jupyter/setup_jupyter_collaboration.sh`
- **Management**: `./scripts/jupyter/manage_notebooks.sh`
- **Verification**: `./scripts/jupyter/verify_notebook_paths.sh`
- **Security**: `scripts/jupyter/notebook_security_manager.py`

## ✅ Ready for Team Collaboration!

Your Jupyter notebook system is now configured with:

- ✅ **Specific storage location** for predictable file access
- ✅ **Complete directory structure** for organized collaboration
- ✅ **Role-based environments** with appropriate permissions
- ✅ **Version control integration** with automatic output cleaning
- ✅ **Security management** with API key protection
- ✅ **Backup and synchronization** capabilities
- ✅ **Professional workflow** with templates and best practices

**All notebooks will be stored at**: `/Users/home/Documents/GitHub/ADS599_Capstone/notebooks/`

**Start collaborating**: Run `./scripts/jupyter/manage_notebooks.sh start-jupyter all` and access your role-specific Jupyter environment!

---

**Note**: This configuration ensures that all team members store notebooks in the same location structure, enabling consistent collaboration and file management across the ADS599 Capstone project.

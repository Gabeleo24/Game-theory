# Team Collaboration Quick Start Guide

## 🚀 For Team Leads: Setting Up Team Access

Your ADS599 Capstone Soccer Intelligence System now has a complete team collaboration framework! Here's how to get your team members up and running quickly.

## 📋 Quick Setup for New Team Members

### Step 1: Send Team Members This Setup Command
```bash
# Clone and setup in one go
git clone https://github.com/mmoramora/ADS599_Capstone.git
cd ADS599_Capstone
./scripts/setup/team_member_setup.sh
```

### Step 2: They Configure Their API Keys
```bash
# Copy template and edit with their API keys
cp config/api_keys_template.yaml config/api_keys.yaml
# Edit config/api_keys.yaml with their SportMonks API key
```

### Step 3: They Start Their Role-Specific Environment
```bash
# For data analysts
./scripts/team/manage_team_access.sh start-analyst

# For developers  
./scripts/team/manage_team_access.sh start-developer

# For researchers
./scripts/team/manage_team_access.sh start-researcher
```

## 👥 Team Member Roles

### 🔍 **Data Analyst**
- **Access**: Read-only database, Jupyter notebooks, Streamlit dashboards
- **Tools**: Database analysis, visualization, reporting
- **Ports**: Jupyter (8888), Streamlit (8501), Database (5432)

### 💻 **Developer** 
- **Access**: Full system access, code modification, deployment
- **Tools**: Complete development environment, database admin, cache management
- **Ports**: Jupyter (8889), Streamlit (8502), pgAdmin (8080), Redis (8081), Database (5432)

### 📚 **Researcher**
- **Access**: Read-only database, research notebooks, documentation
- **Tools**: Academic analysis, methodology development, documentation
- **Ports**: Jupyter (8890), Database (5432)

## 🛠️ Team Management Commands

### Add Team Members
```bash
# Add team members with their roles
./scripts/team/manage_team_access.sh add-member "Alice Johnson" analyst
./scripts/team/manage_team_access.sh add-member "Bob Wilson" developer  
./scripts/team/manage_team_access.sh add-member "Carol Davis" researcher
```

### Start Team Environments
```bash
# Start all team environments at once
./scripts/team/manage_team_access.sh start-team

# Or start individual environments
./scripts/team/manage_team_access.sh start-analyst
./scripts/team/manage_team_access.sh start-developer
./scripts/team/manage_team_access.sh start-researcher
```

### Monitor Team Status
```bash
# Check what's running and access points
./scripts/team/manage_team_access.sh status

# List all team members
./scripts/team/manage_team_access.sh list-members
```

## 🔐 Security Features

### ✅ **Automatic Security**
- API keys excluded from version control
- Pre-commit hooks prevent accidental key commits
- Role-based database access permissions
- Secure configuration templates

### ✅ **Team Safety**
- Each member manages their own API keys
- Read-only access for analysts and researchers
- Full access only for developers
- Audit logging for database access

## 📊 What Each Team Member Gets

### **Shared Access**
- ✅ Same PostgreSQL database with 67 UEFA Champions League teams
- ✅ 8,080+ player statistics records
- ✅ Comprehensive Shapley value analysis capabilities
- ✅ Complete documentation and research papers
- ✅ SQL Playground for data exploration

### **Role-Specific Tools**
- **Analysts**: Jupyter + Streamlit for analysis and visualization
- **Developers**: Full development stack + admin tools
- **Researchers**: Research-focused Jupyter + documentation access

## 🎯 Team Workflow

### **Git Collaboration**
```bash
# Standard workflow for all team members
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
# Make changes
git commit -m "feat: description"
git push origin feature/your-feature-name
# Create Pull Request on GitHub
```

### **Code Review Process**
1. Create Pull Request with detailed description
2. Automated checks run (pre-commit hooks)
3. Team member review required
4. Merge after approval

## 📚 Documentation Available

### **For Team Members**
- **Complete Setup Guide**: `docs/setup/TEAM_MEMBER_ONBOARDING.md`
- **Team Collaboration**: `docs/team-collaboration/README.md`
- **SQL Playground**: `docs/data-access/SQL_PLAYGROUND_GUIDE.md`
- **Research Documentation**: `docs/research-methodology/`

### **For Team Leads**
- **Team Management**: `scripts/team/manage_team_access.sh --help`
- **Configuration**: `config/team_collaboration_config.yaml`
- **Monitoring**: Built-in status and health checks

## 🚨 Troubleshooting

### **If Team Member Setup Fails**
```bash
# Run verification script
./scripts/setup/verify_setup.sh

# Check Docker status
docker ps

# Restart if needed
./scripts/team/manage_team_access.sh stop-all
./scripts/team/manage_team_access.sh start-[role]
```

### **Common Issues**
- **Docker not running**: Start Docker Desktop
- **Port conflicts**: Check if ports 5432, 8080, 8888 are available
- **Permission issues**: Run setup script as administrator (Windows) or with proper permissions (Linux/macOS)

## 🎉 Success Indicators

### **Team Member Setup Complete When**:
- ✅ `./scripts/setup/verify_setup.sh` passes all checks
- ✅ Can access their role-specific Jupyter environment
- ✅ Can connect to database with appropriate permissions
- ✅ Can run SQL queries through the playground
- ✅ Can access shared documentation and research papers

### **Team Collaboration Active When**:
- ✅ Multiple team members can work simultaneously
- ✅ Database handles concurrent connections
- ✅ Git workflow with pull requests working
- ✅ Role-based access functioning properly
- ✅ Shared analysis and development happening

## 📞 Support Resources

### **For Team Members**
- **Setup Issues**: `docs/setup/TEAM_MEMBER_ONBOARDING.md`
- **Usage Questions**: `docs/team-collaboration/README.md`
- **Technical Problems**: Create GitHub Issue
- **Data Access**: `docs/data-access/DATA_ACCESS_GUIDE.md`

### **For Team Leads**
- **Team Management**: This guide + `scripts/team/manage_team_access.sh`
- **Configuration**: `config/team_collaboration_config.yaml`
- **Monitoring**: `./scripts/team/manage_team_access.sh status`
- **Advanced Setup**: `docs/` directory comprehensive guides

---

## 🎯 **Bottom Line**

Your team now has a **professional-grade collaboration system** where:

1. **New members** can be productive in **5 minutes** with automated setup
2. **Role-based access** ensures security and appropriate permissions  
3. **Shared resources** enable collaborative analysis and development
4. **Complete documentation** supports academic and industry standards
5. **Git workflow** maintains code quality and team coordination

**Your ADS599 Capstone project is now ready for team collaboration at scale!** 🚀

---

**Quick Commands Summary**:
- **Add member**: `./scripts/team/manage_team_access.sh add-member "Name" role`
- **Start team**: `./scripts/team/manage_team_access.sh start-team`  
- **Check status**: `./scripts/team/manage_team_access.sh status`
- **Member setup**: `./scripts/setup/team_member_setup.sh`
- **Verify setup**: `./scripts/setup/verify_setup.sh`

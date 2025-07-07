# Team Collaboration System - ADS599 Capstone Soccer Intelligence

## Overview

The ADS599 Capstone Soccer Intelligence System includes a comprehensive team collaboration framework that allows multiple team members to work together effectively with role-based access, shared resources, and coordinated development environments.

## Quick Team Setup

### For New Team Members
```bash
# 1. Clone the repository
git clone https://github.com/mmoramora/ADS599_Capstone.git
cd ADS599_Capstone

# 2. Run automated setup
./scripts/setup/team_member_setup.sh

# 3. Configure API keys
cp config/api_keys_template.yaml config/api_keys.yaml
# Edit config/api_keys.yaml with your API keys

# 4. Verify setup
./scripts/setup/verify_setup.sh

# 5. Start your role-specific environment
./scripts/team/manage_team_access.sh start-[your-role]
```

### For Team Leads
```bash
# Add new team members
./scripts/team/manage_team_access.sh add-member "John Doe" analyst
./scripts/team/manage_team_access.sh add-member "Jane Smith" developer

# Start team environments
./scripts/team/manage_team_access.sh start-team

# Monitor team status
./scripts/team/manage_team_access.sh status
```

## Team Roles and Access

### 🔍 Data Analyst
**Purpose**: Data exploration, visualization, and analysis
**Access Level**: Read-only data access with analysis tools

**Services Available**:
- PostgreSQL database (read-only)
- Jupyter Lab for analysis
- Streamlit for visualizations
- Redis cache for performance

**Access Points**:
- Database: `localhost:5432` (analyst_user/analyst_pass)
- Jupyter: `http://localhost:8888`
- Streamlit: `http://localhost:8501`

**Start Environment**:
```bash
./scripts/team/manage_team_access.sh start-analyst
```

### 💻 Developer
**Purpose**: Full-stack development, system maintenance, and deployment
**Access Level**: Complete system access

**Services Available**:
- PostgreSQL database (full access)
- Jupyter Lab for development
- Streamlit for testing
- pgAdmin for database management
- Redis Commander for cache management

**Access Points**:
- Database: `localhost:5432` (soccerapp/soccerpass123)
- Jupyter: `http://localhost:8889`
- Streamlit: `http://localhost:8502`
- pgAdmin: `http://localhost:8080`
- Redis Commander: `http://localhost:8081`

**Start Environment**:
```bash
./scripts/team/manage_team_access.sh start-developer
```

### 📚 Researcher
**Purpose**: Academic research, methodology development, and documentation
**Access Level**: Read-only data with research tools

**Services Available**:
- PostgreSQL database (read-only)
- Jupyter Lab with research tools
- Documentation access

**Access Points**:
- Database: `localhost:5432` (research_user/research_pass)
- Jupyter: `http://localhost:8890`

**Start Environment**:
```bash
./scripts/team/manage_team_access.sh start-researcher
```

## Team Management Commands

### Environment Management
```bash
# Start specific role environment
./scripts/team/manage_team_access.sh start-analyst
./scripts/team/manage_team_access.sh start-developer
./scripts/team/manage_team_access.sh start-researcher

# Start all team environments
./scripts/team/manage_team_access.sh start-team

# Stop all environments
./scripts/team/manage_team_access.sh stop-all

# Check environment status
./scripts/team/manage_team_access.sh status
```

### Member Management
```bash
# Add team members
./scripts/team/manage_team_access.sh add-member "Alice Johnson" analyst
./scripts/team/manage_team_access.sh add-member "Bob Wilson" developer
./scripts/team/manage_team_access.sh add-member "Carol Davis" researcher

# List all team members
./scripts/team/manage_team_access.sh list-members

# Remove team member
./scripts/team/manage_team_access.sh remove-member "Alice Johnson"
```

## Shared Resources

### Database Access
All team members share the same PostgreSQL database with role-based permissions:

- **Analysts**: Read-only access to all tables
- **Developers**: Full read/write access
- **Researchers**: Read-only access with research-specific views

### Jupyter Notebooks
Shared notebook environment with:
- **Common Notebooks**: Shared analysis templates
- **Personal Workspaces**: Individual member directories
- **Collaborative Notebooks**: Team analysis projects

### Data Storage
Organized data access:
- **Raw Data**: Read-only for analysts and researchers
- **Processed Data**: Shared analysis results
- **Reports**: Collaborative report generation

## Collaboration Workflow

### Git Workflow
```bash
# 1. Always start from main
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes and commit
git add .
git commit -m "feat: description of changes"

# 4. Push and create pull request
git push origin feature/your-feature-name
# Create PR on GitHub
```

### Code Review Process
1. **Create Pull Request**: Detailed description and testing notes
2. **Automated Checks**: CI/CD pipeline validation
3. **Peer Review**: At least one team member review
4. **Testing**: Verify changes don't break existing functionality
5. **Merge**: Approved changes merged to main branch

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General project discussions
- **Pull Request Reviews**: Code-specific discussions
- **Team Meetings**: Regular sync meetings

## Security and Best Practices

### API Key Management
```bash
# Each team member manages their own API keys
cp config/api_keys_template.yaml config/api_keys.yaml
# Edit with your personal API keys
# Never commit this file to version control
```

### Data Security
- **Database Backups**: Automated daily backups
- **Access Logging**: All database access logged
- **Role-Based Access**: Minimum necessary permissions
- **Secure Configuration**: Sensitive data excluded from version control

### Development Standards
- **Code Style**: Follow PEP 8 for Python
- **Documentation**: Comment complex functions
- **Testing**: Write tests for new features
- **Commit Messages**: Use conventional commit format

## Troubleshooting

### Common Issues

#### Environment Won't Start
```bash
# Check Docker status
docker ps

# Restart Docker services
./scripts/team/manage_team_access.sh stop-all
./scripts/team/manage_team_access.sh start-[your-role]

# Check logs
docker-compose logs [service-name]
```

#### Database Connection Issues
```bash
# Verify database is running
docker-compose ps postgres

# Test connection
docker exec -it soccer-intelligence-db pg_isready -U soccerapp

# Reset database if needed
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
1. **Check Documentation**: Review guides in `docs/` directory
2. **Run Verification**: `./scripts/setup/verify_setup.sh`
3. **Check Status**: `./scripts/team/manage_team_access.sh status`
4. **Create Issue**: GitHub Issues for technical problems
5. **Team Communication**: Reach out to team leads

## Advanced Features

### Custom Environments
Create custom Docker Compose profiles for specific needs:
```yaml
# In docker-compose.yml
services:
  custom-service:
    profiles: ["custom"]
    # Service configuration
```

### Monitoring and Analytics
- **Resource Usage**: Monitor CPU, memory, and disk usage
- **Performance Metrics**: Track query performance and response times
- **Health Checks**: Automated service health monitoring

### Backup and Recovery
```bash
# Backup database
./scripts/backup/backup_database.sh

# Restore from backup
./scripts/backup/restore_database.sh backup_file.sql
```

## Resources

### Documentation
- **Setup Guide**: `docs/setup/TEAM_MEMBER_ONBOARDING.md`
- **Data Access**: `docs/data-access/DATA_ACCESS_GUIDE.md`
- **SQL Playground**: `docs/data-access/SQL_PLAYGROUND_GUIDE.md`
- **Research Documentation**: `docs/research-methodology/`

### Configuration Files
- **Team Collaboration**: `config/team_collaboration_config.yaml`
- **API Keys Template**: `config/api_keys_template.yaml`
- **Docker Compose**: `docker-compose.yml`

### Scripts and Tools
- **Setup Scripts**: `scripts/setup/`
- **Team Management**: `scripts/team/`
- **Data Collection**: `scripts/data_collection/`
- **Analysis Tools**: `scripts/analysis/`

---

**Welcome to the ADS599 Capstone Soccer Intelligence Team!** 🚀

This collaboration system ensures that all team members can work together effectively while maintaining security, organization, and productivity. Each role has the appropriate access level and tools needed for their contributions to the project.

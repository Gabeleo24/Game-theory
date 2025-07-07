#!/bin/bash

# ADS599 Capstone - Team Member Setup Script
# This script sets up the complete development environment for new team members

set -e  # Exit on any error

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Welcome message
echo "=========================================="
echo "🚀 ADS599 Capstone Team Member Setup"
echo "=========================================="
echo ""

# Check prerequisites
print_status "Checking prerequisites..."

# Check Git
if command_exists git; then
    print_success "Git is installed: $(git --version)"
else
    print_error "Git is not installed. Please install Git first."
    exit 1
fi

# Check Docker
if command_exists docker; then
    print_success "Docker is installed: $(docker --version)"
else
    print_error "Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

# Check Docker Compose
if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
    if command_exists docker-compose; then
        print_success "Docker Compose is installed: $(docker-compose --version)"
        DOCKER_COMPOSE_CMD="docker-compose"
    else
        print_success "Docker Compose is installed: $(docker compose version)"
        DOCKER_COMPOSE_CMD="docker compose"
    fi
else
    print_error "Docker Compose is not installed. Please install Docker Desktop with Compose."
    exit 1
fi

# Check Python (optional but recommended)
if command_exists python3; then
    print_success "Python is installed: $(python3 --version)"
    PYTHON_CMD="python3"
else
    print_warning "Python not found. Some scripts may not work locally."
fi

echo ""

# Step 1: Setup project directories
print_status "Setting up project structure..."

# Ensure we're in the project root
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Create necessary directories
mkdir -p {data/{cache,analysis,backups},logs,backups/{database,notebooks}}
print_success "Project directories created"

# Step 2: Setup Jupyter collaboration
print_status "Setting up Jupyter collaboration environment..."

if [ -f "scripts/jupyter/setup_jupyter_collaboration.sh" ]; then
    ./scripts/jupyter/setup_jupyter_collaboration.sh
    print_success "Jupyter collaboration environment configured"
else
    print_warning "Jupyter setup script not found, skipping..."
fi

# Step 3: Setup API keys template
print_status "Setting up API configuration..."

if [ ! -f "config/api_keys.yaml" ]; then
    if [ -f "config/api_keys_template.yaml" ]; then
        cp config/api_keys_template.yaml config/api_keys.yaml
        print_success "API keys template created at config/api_keys.yaml"
        print_warning "⚠️  IMPORTANT: Edit config/api_keys.yaml with your SportMonks API key"
        echo "   Get your free API key at: https://www.sportmonks.com/football-api"
    else
        print_warning "API keys template not found"
    fi
else
    print_success "API keys configuration already exists"
fi

# Step 4: Setup Git hooks and configuration
print_status "Configuring Git integration..."

# Setup Git hooks for notebook handling
if command_exists nbstripout; then
    nbstripout --install --attributes .gitattributes 2>/dev/null || true
    print_success "Git hooks configured for notebook handling"
else
    print_status "nbstripout will be installed when Jupyter setup runs"
fi

# Configure Git user if not set
if [ -z "$(git config user.name)" ]; then
    print_warning "Git user not configured. Please set your Git identity:"
    echo "  git config --global user.name 'Your Name'"
    echo "  git config --global user.email 'your.email@example.com'"
fi

# Step 5: Build Docker images
print_status "Building Docker images (this may take a few minutes)..."
$DOCKER_COMPOSE_CMD build --no-cache
print_success "Docker images built successfully"

# Step 6: Start core services
print_status "Starting core services..."
$DOCKER_COMPOSE_CMD up -d postgres redis

# Wait for services to be ready
print_status "Waiting for services to initialize..."
sleep 10

# Check if services are healthy
if $DOCKER_COMPOSE_CMD ps postgres | grep -q "healthy"; then
    print_success "PostgreSQL database is ready"
else
    print_warning "PostgreSQL may still be initializing..."
fi

if $DOCKER_COMPOSE_CMD ps redis | grep -q "Up"; then
    print_success "Redis cache is ready"
else
    print_warning "Redis may still be initializing..."
fi

# Step 7: Verify setup
print_status "Verifying installation..."

# Create verification script if it doesn't exist
if [ ! -f "scripts/setup/verify_setup.sh" ]; then
    cat > scripts/setup/verify_setup.sh << 'EOF'
#!/bin/bash
echo "🔍 Verifying ADS599 Capstone Setup..."

# Check Docker services
echo "📊 Docker Services:"
docker-compose ps

# Check database connection
echo ""
echo "🗄️ Database Connection:"
if docker exec soccer-intelligence-db pg_isready -U soccerapp >/dev/null 2>&1; then
    echo "✅ PostgreSQL database is accessible"
else
    echo "❌ PostgreSQL database connection failed"
fi

# Check Redis connection
echo ""
echo "⚡ Redis Cache:"
if docker exec soccer-intelligence-redis redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis cache is accessible"
else
    echo "❌ Redis cache connection failed"
fi

# Check notebook storage
echo ""
echo "📓 Notebook Storage:"
if [ -d "/Users/home/Documents/GitHub/ADS599_Capstone/notebooks" ]; then
    echo "✅ Notebook storage configured at: /Users/home/Documents/GitHub/ADS599_Capstone/notebooks"
    echo "   Directories: $(ls -1 /Users/home/Documents/GitHub/ADS599_Capstone/notebooks | wc -l) created"
else
    echo "❌ Notebook storage not found"
fi

# Check API configuration
echo ""
echo "🔑 API Configuration:"
if [ -f "config/api_keys.yaml" ]; then
    echo "✅ API keys configuration file exists"
    if grep -q "your_api_key_here" config/api_keys.yaml; then
        echo "⚠️  Please update config/api_keys.yaml with your actual API key"
    else
        echo "✅ API keys appear to be configured"
    fi
else
    echo "❌ API keys configuration not found"
fi

echo ""
echo "🚀 Setup verification complete!"
EOF
    chmod +x scripts/setup/verify_setup.sh
fi

# Run verification
./scripts/setup/verify_setup.sh

echo ""
print_success "🎉 ADS599 Capstone Soccer Intelligence System Setup Complete!"
echo ""
echo "📊 What's Available:"
echo "  ✅ PostgreSQL Database (67 UEFA Champions League teams)"
echo "  ✅ Redis Cache (High-performance data caching)"
echo "  ✅ Jupyter Collaboration Environment"
echo "  ✅ Complete Project Documentation"
echo "  ✅ Security and Backup Systems"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. 🔑 Configure API Keys:"
echo "   Edit config/api_keys.yaml with your SportMonks API key"
echo "   Get free key at: https://www.sportmonks.com/football-api"
echo ""
echo "2. 🎭 Choose Your Role and Start:"
echo ""
echo "   📊 Data Analyst:"
echo "   ./scripts/jupyter/manage_notebooks.sh start-jupyter analyst"
echo "   Access: http://localhost:8888 (token: analyst_secure_token_2024)"
echo ""
echo "   💻 Developer:"
echo "   ./scripts/jupyter/manage_notebooks.sh start-jupyter developer"
echo "   Access: http://localhost:8889 (token: developer_secure_token_2024)"
echo ""
echo "   📚 Researcher:"
echo "   ./scripts/jupyter/manage_notebooks.sh start-jupyter researcher"
echo "   Access: http://localhost:8890 (token: researcher_secure_token_2024)"
echo ""
echo "   🚀 All Environments:"
echo "   $DOCKER_COMPOSE_CMD --profile team up -d"
echo ""
echo "3. 📓 Create Your First Notebook:"
echo "   ./scripts/jupyter/manage_notebooks.sh create-notebook my_first_analysis"
echo ""
echo "4. 🗄️ Explore the Database:"
echo "   ./run_sql_with_logs.sh"
echo "   pgAdmin: http://localhost:8080 (admin@admin.com / admin)"
echo ""
echo "📚 Documentation:"
echo "  📖 Complete Startup Guide: CAPSTONE_PROJECT_STARTUP_GUIDE.md"
echo "  📓 Jupyter Collaboration: JUPYTER_COLLABORATION_SETUP.md"
echo "  🔬 Research Paper: docs/research-methodology/"
echo "  🛠️ Technical Docs: docs/"
echo ""
echo "🆘 Need Help?"
echo "  🔍 Verify setup: ./scripts/setup/verify_setup.sh"
echo "  📊 Check status: $DOCKER_COMPOSE_CMD ps"
echo "  📋 View logs: $DOCKER_COMPOSE_CMD logs [service-name]"
echo "  🐛 GitHub Issues: Report problems and get support"
echo ""
print_success "Happy analyzing! 🚀⚽📊"
elif command_exists python; then
    print_success "Python is installed: $(python --version)"
    PYTHON_CMD="python"
else
    print_warning "Python is not installed. Some features may not work."
    PYTHON_CMD=""
fi

echo ""

# Setup project directories
print_status "Setting up project directories..."

# Create necessary directories
mkdir -p data/{cache,analysis,reports,models}
mkdir -p logs/sql_logs
mkdir -p notebooks
mkdir -p tests

print_success "Project directories created"

# Setup configuration
print_status "Setting up configuration files..."

# Copy API keys template if it doesn't exist
if [ ! -f "config/api_keys.yaml" ]; then
    if [ -f "config/api_keys_template.yaml" ]; then
        cp config/api_keys_template.yaml config/api_keys.yaml
        print_success "API keys template copied to config/api_keys.yaml"
        print_warning "⚠️  IMPORTANT: Edit config/api_keys.yaml with your actual API keys!"
    else
        print_error "API keys template not found!"
    fi
else
    print_success "API keys configuration already exists"
fi

# Setup Git hooks (optional)
print_status "Setting up Git configuration..."

# Set up git hooks directory
if [ -d ".git" ]; then
    mkdir -p .git/hooks
    
    # Create pre-commit hook to prevent committing API keys
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook to prevent committing sensitive files

if git diff --cached --name-only | grep -q "config/api_keys.yaml"; then
    echo "❌ Error: Attempting to commit config/api_keys.yaml"
    echo "This file contains sensitive API keys and should not be committed."
    echo "Please remove it from staging: git reset HEAD config/api_keys.yaml"
    exit 1
fi

# Check for hardcoded API keys in code
if git diff --cached | grep -i "api.*key.*=.*['\"][a-zA-Z0-9]\{20,\}['\"]"; then
    echo "❌ Error: Potential hardcoded API key detected"
    echo "Please use environment variables or config files for API keys."
    exit 1
fi
EOF
    
    chmod +x .git/hooks/pre-commit
    print_success "Git pre-commit hook installed"
else
    print_warning "Not a Git repository - skipping Git hooks setup"
fi

# Setup Python virtual environment (if Python is available)
if [ -n "$PYTHON_CMD" ]; then
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        print_success "Python virtual environment created"
        
        # Activate virtual environment and install dependencies
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
            if [ -f "requirements.txt" ]; then
                pip install --upgrade pip
                pip install -r requirements.txt
                print_success "Python dependencies installed"
            fi
            deactivate
        fi
    else
        print_success "Python virtual environment already exists"
    fi
fi

# Setup Docker environment
print_status "Setting up Docker environment..."

# Pull required Docker images
print_status "Pulling Docker images (this may take a few minutes)..."
$DOCKER_COMPOSE_CMD pull

# Build custom images
print_status "Building custom Docker images..."
$DOCKER_COMPOSE_CMD build

print_success "Docker environment setup complete"

# Create team member configuration
print_status "Creating team member configuration..."

# Create team member config file
cat > config/team_member_config.yaml << EOF
# Team Member Configuration
team_member:
  setup_date: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  setup_version: "1.0"
  environment: "development"

# Development preferences
development:
  auto_start_services: true
  enable_debug_logging: true
  jupyter_password: "soccer_intelligence"
  
# Team collaboration settings
collaboration:
  git_hooks_enabled: true
  pre_commit_checks: true
  shared_notebooks: true
EOF

print_success "Team member configuration created"

# Setup development environment files
print_status "Setting up development environment..."

# Create .env file for development
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Development Environment Variables
ENVIRONMENT=development
DEBUG=true

# Database Configuration
POSTGRES_DB=soccer_intelligence
POSTGRES_USER=soccerapp
POSTGRES_PASSWORD=soccerpass123

# Jupyter Configuration
JUPYTER_PASSWORD=soccer_intelligence

# API Configuration (edit config/api_keys.yaml instead)
# API keys should be configured in config/api_keys.yaml
EOF
    print_success "Development environment file created"
fi

# Make scripts executable
print_status "Setting up script permissions..."
find scripts -name "*.sh" -type f -exec chmod +x {} \;
chmod +x run_sql_with_logs.sh
chmod +x show_database_structure.sh
print_success "Script permissions set"

# Final setup verification
print_status "Running setup verification..."

# Test Docker Compose configuration
if $DOCKER_COMPOSE_CMD config >/dev/null 2>&1; then
    print_success "Docker Compose configuration is valid"
else
    print_error "Docker Compose configuration has errors"
    exit 1
fi

# Create setup completion marker
echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" > .setup_complete

print_success "Setup verification complete"

echo ""
echo "=========================================="
echo "🎉 Team Member Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. 📝 Edit config/api_keys.yaml with your API keys"
echo "2. 🚀 Start the system: $DOCKER_COMPOSE_CMD up -d"
echo "3. ✅ Verify setup: ./scripts/setup/verify_setup.sh"
echo "4. 📚 Read the documentation in docs/"
echo ""
echo "Access points after starting:"
echo "📊 Database: localhost:5432"
echo "🔍 pgAdmin: http://localhost:8080"
echo "📓 Jupyter: http://localhost:8888"
echo "📈 Streamlit: http://localhost:8501"
echo ""
echo "For help, see docs/setup/TEAM_MEMBER_ONBOARDING.md"
echo "or create an issue on GitHub."
echo ""
print_success "Welcome to the ADS599 Capstone team! 🚀"

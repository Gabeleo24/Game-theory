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

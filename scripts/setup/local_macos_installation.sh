#!/bin/bash

# ADS599 Capstone - macOS Local Installation Script
# This script sets up the Soccer Intelligence System on macOS for local development
# Updated: 2025-07-07

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${PURPLE}=========================================="
    echo -e "$1"
    echo -e "==========================================${NC}"
}

print_step() {
    echo -e "${CYAN}[STEP] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS"
    print_status "For GitHub Codespaces, use: bash scripts/setup/codespace_installation.sh"
    print_status "For Linux, use: bash scripts/setup/linux_installation.sh"
    exit 1
fi

echo ""
print_header "🚀 ADS599 Capstone - macOS Local Installation"
echo ""
print_status "Setting up Soccer Intelligence System for local macOS development..."
echo ""

# Step 1: Check and install Homebrew
print_step "1/8 Checking Homebrew"

if ! command -v brew &> /dev/null; then
    print_status "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    
    print_success "Homebrew installed"
else
    print_success "Homebrew already installed"
fi

# Step 2: Install Docker Desktop
print_step "2/8 Checking Docker Desktop"

if ! command -v docker &> /dev/null; then
    print_status "Installing Docker Desktop..."
    brew install --cask docker
    print_success "Docker Desktop installed"
    print_warning "Please start Docker Desktop manually and return to continue"
    read -p "Press Enter after Docker Desktop is running..."
else
    print_success "Docker already installed"
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running"
    print_status "Please start Docker Desktop and try again"
    exit 1
fi

# Set Docker Compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
    print_success "Using 'docker compose' command"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
    print_success "Using 'docker-compose' command"
else
    print_error "Docker Compose not available"
    exit 1
fi

# Step 3: Install Python dependencies
print_step "3/8 Installing Python Dependencies"

# Check Python
if command -v python3 &> /dev/null; then
    print_success "Python3 is available"
else
    print_status "Installing Python..."
    brew install python
fi

# Check pip
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    print_error "pip not found"
    exit 1
fi

# Install required Python packages
print_status "Installing Python packages..."
$PIP_CMD install --user --quiet nbstripout jupyter jupyterlab pandas numpy matplotlib seaborn plotly sqlalchemy psycopg2-binary redis python-dotenv

print_success "Python dependencies installed"

# Step 4: Set up project directories
print_step "4/8 Setting Up Project Structure"

# Set notebooks directory
NOTEBOOKS_DIR="notebooks"

# Create necessary directories
mkdir -p {data/{cache,analysis,backups},logs,backups/{database,notebooks}}

# Create notebooks directory structure
mkdir -p "$NOTEBOOKS_DIR"/{shared,personal,research,archive}
mkdir -p "$NOTEBOOKS_DIR"/shared/{templates,data_exploration,team_analysis,reports,tutorials}
mkdir -p "$NOTEBOOKS_DIR"/personal/{analyst_workspace,developer_workspace,researcher_workspace}
mkdir -p "$NOTEBOOKS_DIR"/research/{methodology,literature_review,statistical_analysis,publications}
mkdir -p "$NOTEBOOKS_DIR"/archive/{completed_projects,deprecated_analyses,backup_notebooks}

print_success "Project directories created"

# Step 5: Configure API keys
print_step "5/8 Setting Up API Configuration"

if [ ! -f "config/api_keys.yaml" ]; then
    if [ -f "config/api_keys_template.yaml" ]; then
        cp config/api_keys_template.yaml config/api_keys.yaml
        print_success "API keys template created"
        print_warning "⚠️  IMPORTANT: Edit config/api_keys.yaml and add your SportMonks API key"
    fi
else
    print_success "API keys configuration already exists"
fi

# Step 6: Configure environment for local development
print_step "6/8 Configuring Local Environment"

# Create local environment file
cat > .env.local << EOF
# Local macOS Environment Configuration
# ADS599 Capstone Soccer Intelligence System

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=soccer_intelligence
POSTGRES_USER=soccerapp
POSTGRES_PASSWORD=soccerpass123

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# API Configuration
SPORTMONKS_API_KEY=your_api_key_here

# Environment
ENVIRONMENT=development
DEBUG=true

# Jupyter Configuration
JUPYTER_PORT=8888
JUPYTER_TOKEN=local_secure_token_2024

# Performance Configuration
WORKERS=2
TIMEOUT=300
KEEP_ALIVE=2
MAX_REQUESTS=1000
EOF

print_success "Local environment configured"

# Step 7: Create Docker Compose override for local development
print_step "7/8 Configuring Docker for Local Development"

# Create local Docker Compose override
cat > docker-compose.local.yml << EOF
version: '3.8'

services:
  postgres:
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_HOST_AUTH_METHOD=trust
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Local Jupyter environment
  jupyter-local:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    container_name: jupyter-local
    restart: unless-stopped
    depends_on:
      - postgres
      - redis
    environment:
      - POSTGRES_HOST=postgres
      - REDIS_HOST=redis
      - JUPYTER_ENABLE_LAB=yes
      - JUPYTER_TOKEN=local_secure_token_2024
      - SPORTMONKS_API_KEY=\${SPORTMONKS_API_KEY}
    ports:
      - "8888:8888"
    volumes:
      - .:/workspace
      - jupyter_data:/home/jovyan/.jupyter

  # pgAdmin for database management
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: pgadmin-local
    restart: unless-stopped
    depends_on:
      - postgres
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: admin
      PGADMIN_CONFIG_SERVER_MODE: 'False'
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    ports:
      - "8080:80"

volumes:
  postgres_data:
  redis_data:
  jupyter_data:
  pgadmin_data:

networks:
  default:
    name: soccer-intelligence-local
EOF

print_success "Docker configuration updated for local development"

# Step 8: Create management scripts
print_step "8/8 Creating Management Scripts"

# Create local startup script
cat > start_local.sh << EOF
#!/bin/bash

# ADS599 Capstone - Local Startup Script

echo "🚀 Starting ADS599 Capstone Soccer Intelligence System locally..."

# Start all services
$DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.local.yml up -d

echo ""
echo "✅ Services started! Access points:"
echo ""
echo "📊 Jupyter Lab: http://localhost:8888"
echo "   Token: local_secure_token_2024"
echo ""
echo "🗄️ pgAdmin: http://localhost:8080"
echo "   Email: admin@admin.com"
echo "   Password: admin"
echo ""
echo "📓 Notebooks: ./notebooks/"
echo ""
echo "🔧 Management commands:"
echo "   ./start_local.sh          # Start all services"
echo "   ./stop_local.sh           # Stop all services"
echo "   ./status_local.sh         # Check service status"
echo ""
EOF

# Create stop script
cat > stop_local.sh << EOF
#!/bin/bash
echo "🛑 Stopping ADS599 Capstone services..."
$DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.local.yml down
echo "✅ All services stopped"
EOF

# Create status script
cat > status_local.sh << EOF
#!/bin/bash
echo "📊 ADS599 Capstone Service Status:"
echo ""
$DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.local.yml ps
echo ""
echo "🔗 Access URLs:"
echo "📊 Jupyter Lab: http://localhost:8888"
echo "🗄️ pgAdmin: http://localhost:8080"
EOF

# Make scripts executable
chmod +x start_local.sh stop_local.sh status_local.sh

print_success "Local management scripts created"

# Set up Git configuration
git config --global user.name "$(git config user.name || echo 'Local User')"
git config --global user.email "$(git config user.email || echo 'user@local.dev')"

# Install nbstripout for notebook handling
if command -v nbstripout &> /dev/null; then
    nbstripout --install --attributes .gitattributes 2>/dev/null || true
    print_success "Git hooks configured for notebook handling"
fi

# Final success message
echo ""
print_header "🎉 Installation Complete!"
echo ""
print_success "ADS599 Capstone Soccer Intelligence System is ready for local development!"
echo ""
echo "🚀 Quick Start:"
echo ""
echo "1. 🔑 Set API Key:"
echo "   Edit config/api_keys.yaml and add your SportMonks API key"
echo ""
echo "2. 🚀 Start Services:"
echo "   ./start_local.sh"
echo ""
echo "3. 📊 Access Jupyter Lab:"
echo "   http://localhost:8888"
echo "   Token: local_secure_token_2024"
echo ""
echo "4. 🗄️ Access pgAdmin:"
echo "   http://localhost:8080"
echo "   Email: admin@admin.com / Password: admin"
echo ""
echo "📚 What's Available:"
echo "  ✅ Complete UEFA Champions League dataset (67 teams, 8,080+ players)"
echo "  ✅ PostgreSQL database with optimized queries"
echo "  ✅ Redis cache for high-performance data access"
echo "  ✅ Jupyter Lab with all analysis libraries"
echo "  ✅ Local development environment"
echo "  ✅ Advanced analytics including Shapley value analysis"
echo ""
echo "🛠️ Management Commands:"
echo "  ./start_local.sh    # Start all services"
echo "  ./stop_local.sh     # Stop all services"
echo "  ./status_local.sh   # Check service status"
echo ""
echo "📓 Notebooks Location: ./notebooks/"
echo ""
print_success "Ready for soccer intelligence analysis! ⚽📊"

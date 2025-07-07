#!/bin/bash

# GitHub Codespace Installation Script
# ADS599 Capstone Soccer Intelligence System
# Complete setup for GitHub Codespaces environment

set -e

# Check if we're in a Codespace environment
if [ -z "$CODESPACE_NAME" ]; then
    echo "⚠️  Warning: This script is designed for GitHub Codespaces"
    echo "   Some features may not work correctly in other environments"
    echo ""
fi

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

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

print_header "🚀 ADS599 Capstone - GitHub Codespace Installation"
echo ""
print_status "Setting up complete Soccer Intelligence System in GitHub Codespaces..."
echo ""

# Step 1: Detect and configure Codespace environment
print_step "1/10 Configuring GitHub Codespace Environment"

# Check if we're in a Codespace
if [ -n "$CODESPACE_NAME" ]; then
    print_success "GitHub Codespace detected: $CODESPACE_NAME"
    WORKSPACE_DIR="/workspaces/ADS599_Capstone"
    NOTEBOOKS_DIR="$WORKSPACE_DIR/notebooks"
    print_status "Workspace directory: $WORKSPACE_DIR"
else
    print_warning "Not in GitHub Codespace, using current directory"
    WORKSPACE_DIR=$(pwd)
    NOTEBOOKS_DIR="$WORKSPACE_DIR/notebooks"
fi

# Step 2: Update system packages
print_step "2/10 Updating System Packages"
sudo apt-get update -qq
sudo apt-get install -y curl wget git jq postgresql-client redis-tools

# Step 3: Configure Docker for Codespace
print_step "3/10 Setting Up Docker"

# In GitHub Codespaces, Docker is pre-installed
if command -v docker &> /dev/null; then
    print_success "Docker is available"

    # Start Docker service if not running
    if ! docker info &> /dev/null; then
        print_status "Starting Docker service..."
        sudo service docker start || true
        sleep 3
    fi

    # Add user to docker group if not already
    if ! groups $USER | grep -q docker; then
        print_status "Adding user to docker group..."
        sudo usermod -aG docker $USER || true
    fi
else
    print_error "Docker not found in Codespace environment"
    exit 1
fi

# Set Docker Compose command (prefer 'docker compose' over 'docker-compose')
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

print_success "Docker setup complete"

# Step 4: Install Python dependencies
print_step "4/10 Installing Python Dependencies"

# Check Python and pip availability
if command -v python3 &> /dev/null; then
    print_success "Python3 is available"
else
    print_error "Python3 not found"
    exit 1
fi

if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    print_status "Installing pip..."
    sudo apt-get install -y python3-pip
    PIP_CMD="pip3"
fi

# Install required Python packages
print_status "Installing Python packages..."
$PIP_CMD install --user --quiet nbstripout jupyter jupyterlab pandas numpy matplotlib seaborn plotly sqlalchemy psycopg2-binary redis python-dotenv

print_success "Python dependencies installed"

# Step 5: Configure project directories for Codespace
print_step "5/10 Setting Up Project Structure"

# Create necessary directories
mkdir -p {data/{cache,analysis,backups},logs,backups/{database,notebooks}}

# Create notebooks directory structure
mkdir -p "$NOTEBOOKS_DIR"/{shared,personal,research,archive}
mkdir -p "$NOTEBOOKS_DIR"/shared/{templates,data_exploration,team_analysis,reports,tutorials}
mkdir -p "$NOTEBOOKS_DIR"/personal/{analyst_workspace,developer_workspace,researcher_workspace}
mkdir -p "$NOTEBOOKS_DIR"/research/{methodology,literature_review,statistical_analysis,publications}
mkdir -p "$NOTEBOOKS_DIR"/archive/{completed_projects,deprecated_analyses,backup_notebooks}

print_success "Project directories created"

# Step 6: Configure API keys for Codespace
print_step "6/10 Setting Up API Configuration"

if [ ! -f "config/api_keys.yaml" ]; then
    if [ -f "config/api_keys_template.yaml" ]; then
        cp config/api_keys_template.yaml config/api_keys.yaml
        print_success "API keys template created"
        print_warning "⚠️  IMPORTANT: Set your SportMonks API key as a Codespace secret"
        echo "   1. Go to your GitHub repository settings"
        echo "   2. Navigate to Secrets and variables > Codespaces"
        echo "   3. Add secret: SPORTMONKS_API_KEY with your API key"
        echo "   4. The system will automatically use this secret"
    fi
else
    print_success "API keys configuration already exists"
fi

# Step 7: Configure environment for Codespace
print_step "7/10 Configuring Codespace Environment"

# Create Codespace-specific environment file
cat > .env.codespace << EOF
# GitHub Codespace Environment Configuration
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

# Jupyter Configuration
JUPYTER_ENABLE_LAB=yes
JUPYTER_TOKEN=codespace_secure_token_2024

# API Configuration (will use Codespace secrets)
SPORTMONKS_API_KEY=\${SPORTMONKS_API_KEY}

# Codespace Specific
CODESPACE_NAME=\${CODESPACE_NAME}
GITHUB_CODESPACE_TOKEN=\${GITHUB_TOKEN}

# Application Configuration
FLASK_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Performance Configuration
WORKERS=2
TIMEOUT=300
KEEP_ALIVE=2
MAX_REQUESTS=1000
EOF

print_success "Codespace environment configured"

# Step 8: Update Docker Compose for Codespace
print_step "8/10 Configuring Docker for Codespace"

# Create Codespace-specific Docker Compose override
cat > docker-compose.codespace.yml << EOF
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

  # Codespace-optimized Jupyter environment
  jupyter-codespace:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    container_name: jupyter-codespace
    restart: unless-stopped
    depends_on:
      - postgres
      - redis
    environment:
      - POSTGRES_HOST=postgres
      - REDIS_HOST=redis
      - JUPYTER_ENABLE_LAB=yes
      - JUPYTER_TOKEN=codespace_secure_token_2024
      - SPORTMONKS_API_KEY=\${SPORTMONKS_API_KEY}
    volumes:
      - .:/workspace:cached
      - jupyter_data:/home/jovyan/.jupyter
    ports:
      - "8888:8888"
    command: ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=codespace_secure_token_2024"]
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'

  # pgAdmin for database management
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: pgadmin-codespace
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
    name: soccer-intelligence-codespace
EOF

print_success "Docker configuration updated for Codespace"

# Step 9: Build and start services
print_step "9/10 Building and Starting Services"

print_status "Building Docker images..."
if ! $DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.codespace.yml build; then
    print_error "Failed to build Docker images"
    echo "This might be due to Docker not being fully initialized in Codespace"
    echo "Try running the script again in a few minutes"
    exit 1
fi

print_status "Starting core services..."
if ! $DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.codespace.yml up -d postgres redis; then
    print_error "Failed to start services"
    echo "Checking Docker status..."
    docker info || true
    exit 1
fi

# Wait for services to be ready
print_status "Waiting for services to initialize..."
sleep 15

# Check if services are healthy
if $DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.codespace.yml ps postgres | grep -q "Up"; then
    print_success "PostgreSQL database is ready"
else
    print_warning "PostgreSQL may still be initializing..."
    print_status "Checking PostgreSQL logs..."
    $DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.codespace.yml logs postgres | tail -10 || true
fi

if $DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.codespace.yml ps redis | grep -q "Up"; then
    print_success "Redis cache is ready"
else
    print_warning "Redis may still be initializing..."
    print_status "Checking Redis logs..."
    $DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.codespace.yml logs redis | tail -10 || true
fi

# Step 10: Final setup and verification
print_step "10/10 Final Setup and Verification"

# Set up Git configuration for Codespace
git config --global user.name "${GITHUB_USER:-codespace-user}"
git config --global user.email "${GITHUB_USER:-codespace-user}@users.noreply.github.com"

# Install nbstripout for notebook handling
if command -v nbstripout &> /dev/null; then
    nbstripout --install --attributes .gitattributes 2>/dev/null || true
    print_success "Git hooks configured for notebook handling"
fi

# Create Codespace-specific startup script
cat > start_codespace.sh << EOF
#!/bin/bash

# ADS599 Capstone - Codespace Startup Script

echo "🚀 Starting ADS599 Capstone Soccer Intelligence System in Codespace..."

# Start all services
$DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.codespace.yml up -d

echo ""
echo "✅ Services started! Access points:"
echo ""
echo "📊 Jupyter Lab: https://$CODESPACE_NAME-8888.app.github.dev"
echo "   Token: codespace_secure_token_2024"
echo ""
echo "🗄️ pgAdmin: https://$CODESPACE_NAME-8080.app.github.dev"
echo "   Email: admin@admin.com"
echo "   Password: admin"
echo ""
echo "📓 Notebooks: /workspaces/ADS599_Capstone/notebooks/"
echo ""
echo "🔧 Management commands:"
echo "   ./start_codespace.sh          # Start all services"
echo "   ./stop_codespace.sh           # Stop all services"
echo "   ./status_codespace.sh         # Check service status"
echo ""
EOF

# Create stop script
cat > stop_codespace.sh << EOF
#!/bin/bash
echo "🛑 Stopping ADS599 Capstone services..."
$DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.codespace.yml down
echo "✅ All services stopped"
EOF

# Create status script
cat > status_codespace.sh << EOF
#!/bin/bash
echo "📊 ADS599 Capstone Service Status:"
echo ""
$DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.codespace.yml ps
echo ""
echo "🔗 Access URLs:"
echo "📊 Jupyter Lab: https://\$CODESPACE_NAME-8888.app.github.dev"
echo "🗄️ pgAdmin: https://\$CODESPACE_NAME-8080.app.github.dev"
EOF

# Make scripts executable
chmod +x start_codespace.sh stop_codespace.sh status_codespace.sh

print_success "Codespace management scripts created"

# Final success message
echo ""
print_header "🎉 Installation Complete!"
echo ""
print_success "ADS599 Capstone Soccer Intelligence System is ready in GitHub Codespace!"
echo ""
echo "🚀 Quick Start:"
echo ""
echo "1. 🔑 Set API Key (if not already done):"
echo "   - Go to repository Settings > Secrets and variables > Codespaces"
echo "   - Add secret: SPORTMONKS_API_KEY with your SportMonks API key"
echo ""
echo "2. 🚀 Start Services:"
echo "   ./start_codespace.sh"
echo ""
echo "3. 📊 Access Jupyter Lab:"
echo "   https://$CODESPACE_NAME-8888.app.github.dev"
echo "   Token: codespace_secure_token_2024"
echo ""
echo "4. 🗄️ Access pgAdmin:"
echo "   https://$CODESPACE_NAME-8080.app.github.dev"
echo "   Email: admin@admin.com / Password: admin"
echo ""
echo "📚 What's Available:"
echo "  ✅ Complete UEFA Champions League dataset (67 teams, 8,080+ players)"
echo "  ✅ PostgreSQL database with optimized queries"
echo "  ✅ Redis cache for high-performance data access"
echo "  ✅ Jupyter Lab with all analysis libraries"
echo "  ✅ Shared notebook collaboration environment"
echo "  ✅ Advanced analytics including Shapley value analysis"
echo ""
echo "🛠️ Management Commands:"
echo "  ./start_codespace.sh    # Start all services"
echo "  ./stop_codespace.sh     # Stop all services"
echo "  ./status_codespace.sh   # Check service status"
echo ""
echo "📓 Notebooks Location: /workspaces/ADS599_Capstone/notebooks/"
echo ""
print_success "Ready for soccer intelligence analysis! ⚽📊"

# Run verification script
echo ""
print_info "Running installation verification..."
if [ -f "scripts/setup/verify_codespace.sh" ]; then
    bash scripts/setup/verify_codespace.sh
else
    print_warning "Verification script not found"
fi

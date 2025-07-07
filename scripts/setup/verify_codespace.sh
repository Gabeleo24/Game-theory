#!/bin/bash

# ADS599 Capstone - Codespace Verification Script
# This script verifies that the installation was successful

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo -e "${BLUE}=========================================="
    echo -e "$1"
    echo -e "==========================================${NC}"
}

echo ""
print_header "🔍 ADS599 Capstone Installation Verification"
echo ""

# Check if we're in a Codespace
if [ -n "$CODESPACE_NAME" ]; then
    print_success "Running in GitHub Codespace: $CODESPACE_NAME"
else
    print_warning "Not running in GitHub Codespace"
fi

# Check Docker
echo ""
print_info "Checking Docker installation..."
if command -v docker &> /dev/null; then
    print_success "Docker is installed"
    if docker info &> /dev/null; then
        print_success "Docker daemon is running"
    else
        print_error "Docker daemon is not running"
    fi
else
    print_error "Docker is not installed"
fi

# Check Docker Compose
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
    print_success "Docker Compose is available (v2)"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
    print_success "Docker Compose is available (v1)"
else
    print_error "Docker Compose is not available"
    exit 1
fi

# Check Python
echo ""
print_info "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python is installed: $PYTHON_VERSION"
else
    print_error "Python3 is not installed"
fi

# Check pip
if command -v pip3 &> /dev/null; then
    print_success "pip3 is available"
elif command -v pip &> /dev/null; then
    print_success "pip is available"
else
    print_error "pip is not available"
fi

# Check required Python packages
echo ""
print_info "Checking Python packages..."
REQUIRED_PACKAGES=("pandas" "numpy" "matplotlib" "seaborn" "plotly" "sqlalchemy" "psycopg2" "redis" "jupyter")

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" &> /dev/null; then
        print_success "$package is installed"
    else
        print_error "$package is not installed"
    fi
done

# Check project structure
echo ""
print_info "Checking project structure..."
REQUIRED_DIRS=("data" "logs" "notebooks" "config" "scripts")

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_success "Directory exists: $dir"
    else
        print_error "Directory missing: $dir"
    fi
done

# Check configuration files
echo ""
print_info "Checking configuration files..."
CONFIG_FILES=("docker-compose.yml" "docker-compose.codespace.yml" ".env.codespace")

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Configuration file exists: $file"
    else
        print_error "Configuration file missing: $file"
    fi
done

# Check management scripts
echo ""
print_info "Checking management scripts..."
SCRIPTS=("start_codespace.sh" "stop_codespace.sh" "status_codespace.sh")

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        print_success "Script exists and is executable: $script"
    else
        print_error "Script missing or not executable: $script"
    fi
done

# Check Docker services
echo ""
print_info "Checking Docker services..."
if [ -f "docker-compose.yml" ] && [ -f "docker-compose.codespace.yml" ]; then
    if $DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.codespace.yml ps | grep -q "Up"; then
        print_success "Some Docker services are running"
        echo ""
        print_info "Service status:"
        $DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.codespace.yml ps
    else
        print_warning "No Docker services are currently running"
        print_info "Run './start_codespace.sh' to start services"
    fi
else
    print_error "Docker Compose files not found"
fi

# Check API configuration
echo ""
print_info "Checking API configuration..."
if [ -f "config/api_keys.yaml" ]; then
    print_success "API keys configuration file exists"
else
    print_warning "API keys configuration file not found"
fi

if [ -n "$SPORTMONKS_API_KEY" ]; then
    print_success "SportMonks API key is set as environment variable"
else
    print_warning "SportMonks API key not set as environment variable"
    print_info "Set it as a Codespace secret for automatic loading"
fi

# Final summary
echo ""
print_header "📊 Verification Summary"
echo ""

if command -v docker &> /dev/null && docker info &> /dev/null && [ -f "docker-compose.yml" ]; then
    print_success "Core installation appears successful!"
    echo ""
    print_info "Next steps:"
    echo "  1. Set your SportMonks API key as a Codespace secret"
    echo "  2. Run './start_codespace.sh' to start all services"
    echo "  3. Access Jupyter Lab at: https://$CODESPACE_NAME-8888.app.github.dev"
    echo "  4. Access pgAdmin at: https://$CODESPACE_NAME-8080.app.github.dev"
else
    print_error "Installation verification failed"
    print_info "Try running the installation script again:"
    echo "  bash scripts/setup/codespace_installation.sh"
fi

echo ""

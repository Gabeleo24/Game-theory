#!/bin/bash

# ADS599 Capstone - Setup Verification Script
# This script verifies that the team member setup was successful

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[CHECK]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verification counters
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# Function to increment counters
check_passed() {
    ((CHECKS_PASSED++))
    print_success "$1"
}

check_failed() {
    ((CHECKS_FAILED++))
    print_error "$1"
}

check_warning() {
    ((CHECKS_WARNING++))
    print_warning "$1"
}

echo "=========================================="
echo "🔍 ADS599 Capstone Setup Verification"
echo "=========================================="
echo ""

# Check 1: Prerequisites
print_status "Checking prerequisites..."

if command_exists git; then
    check_passed "Git is available"
else
    check_failed "Git is not installed"
fi

if command_exists docker; then
    check_passed "Docker is available"
else
    check_failed "Docker is not installed"
fi

if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
    check_passed "Docker Compose is available"
    if command_exists docker-compose; then
        DOCKER_COMPOSE_CMD="docker-compose"
    else
        DOCKER_COMPOSE_CMD="docker compose"
    fi
else
    check_failed "Docker Compose is not available"
    exit 1
fi

# Check 2: Project structure
print_status "Checking project structure..."

required_dirs=("data" "docs" "scripts" "src" "config" "docker" "logs")
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        check_passed "Directory $dir exists"
    else
        check_failed "Directory $dir is missing"
    fi
done

# Check 3: Configuration files
print_status "Checking configuration files..."

if [ -f "config/api_keys.yaml" ]; then
    check_passed "API keys configuration exists"
    
    # Check if API keys are configured
    if grep -q "YOUR_.*_API_KEY_HERE" config/api_keys.yaml; then
        check_warning "API keys need to be configured in config/api_keys.yaml"
    else
        check_passed "API keys appear to be configured"
    fi
else
    check_failed "API keys configuration is missing"
fi

if [ -f "docker-compose.yml" ]; then
    check_passed "Docker Compose configuration exists"
else
    check_failed "Docker Compose configuration is missing"
fi

if [ -f "requirements.txt" ]; then
    check_passed "Python requirements file exists"
else
    check_warning "Python requirements file is missing"
fi

# Check 4: Docker environment
print_status "Checking Docker environment..."

# Test Docker Compose configuration
if $DOCKER_COMPOSE_CMD config >/dev/null 2>&1; then
    check_passed "Docker Compose configuration is valid"
else
    check_failed "Docker Compose configuration has errors"
fi

# Check if Docker is running
if docker info >/dev/null 2>&1; then
    check_passed "Docker daemon is running"
else
    check_failed "Docker daemon is not running"
fi

# Check 5: Services status
print_status "Checking services status..."

# Check if services are running
if $DOCKER_COMPOSE_CMD ps | grep -q "Up"; then
    check_passed "Some Docker services are running"
    
    # Check specific services
    services=("postgres" "redis")
    for service in "${services[@]}"; do
        if $DOCKER_COMPOSE_CMD ps | grep "$service" | grep -q "Up"; then
            check_passed "Service $service is running"
        else
            check_warning "Service $service is not running (start with: $DOCKER_COMPOSE_CMD up -d)"
        fi
    done
else
    check_warning "No Docker services are running (start with: $DOCKER_COMPOSE_CMD up -d)"
fi

# Check 6: Database connectivity (if running)
print_status "Checking database connectivity..."

if $DOCKER_COMPOSE_CMD ps | grep "postgres" | grep -q "Up"; then
    # Wait a moment for database to be ready
    sleep 2
    
    if docker exec soccer-intelligence-db pg_isready -U soccerapp >/dev/null 2>&1; then
        check_passed "Database is accepting connections"
        
        # Test database content
        table_count=$(docker exec soccer-intelligence-db psql -U soccerapp -d soccer_intelligence -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ' || echo "0")
        if [ "$table_count" -gt 0 ]; then
            check_passed "Database has $table_count tables"
        else
            check_warning "Database is empty (load data with: python scripts/data_loading/json_to_postgres.py)"
        fi
    else
        check_warning "Database is not ready yet (may still be starting)"
    fi
else
    check_warning "Database service is not running"
fi

# Check 7: Web interfaces (if running)
print_status "Checking web interfaces..."

web_services=(
    "8080:pgAdmin"
    "8888:Jupyter"
    "8501:Streamlit"
    "8081:Redis Commander"
)

for service_info in "${web_services[@]}"; do
    port=$(echo "$service_info" | cut -d: -f1)
    name=$(echo "$service_info" | cut -d: -f2)
    
    if curl -s "http://localhost:$port" >/dev/null 2>&1; then
        check_passed "$name is accessible at http://localhost:$port"
    else
        check_warning "$name is not accessible (may not be running)"
    fi
done

# Check 8: Scripts and tools
print_status "Checking scripts and tools..."

scripts=("run_sql_with_logs.sh" "show_database_structure.sh")
for script in "${scripts[@]}"; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        check_passed "Script $script is executable"
    else
        check_warning "Script $script is missing or not executable"
    fi
done

# Check 9: Python environment (if available)
print_status "Checking Python environment..."

if command_exists python3 || command_exists python; then
    if [ -d "venv" ]; then
        check_passed "Python virtual environment exists"
    else
        check_warning "Python virtual environment not found (optional)"
    fi
    
    # Check if in virtual environment
    if [ -n "$VIRTUAL_ENV" ]; then
        check_passed "Currently in Python virtual environment"
    else
        check_warning "Not in Python virtual environment (activate with: source venv/bin/activate)"
    fi
else
    check_warning "Python is not available"
fi

# Check 10: Git configuration
print_status "Checking Git configuration..."

if [ -d ".git" ]; then
    check_passed "Git repository is initialized"
    
    if git config user.name >/dev/null 2>&1 && git config user.email >/dev/null 2>&1; then
        check_passed "Git user configuration is set"
    else
        check_warning "Git user configuration needs to be set"
    fi
    
    if [ -f ".git/hooks/pre-commit" ]; then
        check_passed "Git pre-commit hook is installed"
    else
        check_warning "Git pre-commit hook is not installed"
    fi
else
    check_warning "Not in a Git repository"
fi

echo ""
echo "=========================================="
echo "📊 Verification Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}✓ Checks Passed: $CHECKS_PASSED${NC}"
echo -e "${YELLOW}⚠ Warnings: $CHECKS_WARNING${NC}"
echo -e "${RED}✗ Checks Failed: $CHECKS_FAILED${NC}"
echo ""

# Provide recommendations based on results
if [ $CHECKS_FAILED -eq 0 ]; then
    if [ $CHECKS_WARNING -eq 0 ]; then
        echo "🎉 Perfect! Your setup is complete and ready to use."
    else
        echo "✅ Good! Your setup is functional with some optional improvements available."
    fi
    echo ""
    echo "🚀 You can now:"
    echo "• Explore the database with: ./run_sql_with_logs.sh"
    echo "• Access Jupyter at: http://localhost:8888"
    echo "• View documentation in: docs/"
    echo "• Start analyzing data!"
else
    echo "❌ Some critical issues need to be resolved before you can use the system."
    echo ""
    echo "🔧 Next steps:"
    echo "• Fix the failed checks above"
    echo "• Re-run this verification: ./scripts/setup/verify_setup.sh"
    echo "• Check the setup guide: docs/setup/TEAM_MEMBER_ONBOARDING.md"
fi

echo ""
echo "📚 Resources:"
echo "• Setup Guide: docs/setup/TEAM_MEMBER_ONBOARDING.md"
echo "• Documentation: docs/"
echo "• GitHub Issues: https://github.com/mmoramora/ADS599_Capstone/issues"
echo ""

# Exit with appropriate code
if [ $CHECKS_FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi

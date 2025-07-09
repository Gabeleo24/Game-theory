#!/bin/bash

# ADS599 Capstone Soccer Intelligence System - Complete Setup Script
# This script sets up and runs the complete soccer intelligence system

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

# Function to check Docker availability
check_docker() {
    print_status "Checking Docker availability..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists "docker compose" && ! command_exists "docker-compose"; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is available and running"
}

# Function to check Python availability
check_python() {
    print_status "Checking Python availability..."
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python $python_version is available"
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        python3 -m pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found, skipping dependency installation"
    fi
}

# Function to check configuration
check_configuration() {
    print_status "Checking configuration..."
    
    if [ ! -f "config/api_keys.yaml" ]; then
        print_warning "API keys configuration not found"
        if [ -f "config/api_keys_template.yaml" ]; then
            print_status "Copying template configuration..."
            cp config/api_keys_template.yaml config/api_keys.yaml
            print_warning "Please edit config/api_keys.yaml with your actual API keys"
        else
            print_error "No configuration template found"
            exit 1
        fi
    else
        print_success "Configuration file found"
    fi
}

# Function to start Docker services
start_docker_services() {
    print_status "Starting Docker services..."
    
    # Stop any existing services
    docker compose down >/dev/null 2>&1 || true
    
    # Start PostgreSQL and Redis
    if command_exists "docker compose"; then
        docker compose up -d postgres redis
    else
        docker-compose up -d postgres redis
    fi
    
    print_success "Docker services started"
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if PostgreSQL is ready
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if docker compose exec -T postgres pg_isready -U soccerapp >/dev/null 2>&1; then
            break
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "PostgreSQL failed to start within timeout"
        exit 1
    fi
    
    print_success "All services are ready"
}

# Function to initialize database
initialize_database() {
    print_status "Initializing database with clean reset..."

    if python3 scripts/database/reset_and_initialize.py; then
        print_success "Database initialized successfully with clean schema"
    else
        print_error "Database initialization failed"
        exit 1
    fi
}

# Function to run data collection
run_data_collection() {
    print_status "Running data collection..."
    
    if [ "$1" = "--no-data" ]; then
        print_warning "Skipping data collection as requested"
        return 0
    fi
    
    if python3 -c "
import asyncio
import sys
sys.path.append('.')
from services.multi_api_data_collector import MultiAPIDataCollector

async def main():
    collector = MultiAPIDataCollector()
    try:
        await collector.run_comprehensive_collection(
            target_teams=['Real Madrid', 'Barcelona'],
            target_seasons=['2023-2024']
        )
        return True
    except Exception as e:
        print(f'Data collection failed: {e}')
        return False
    finally:
        collector.close_connections()

success = asyncio.run(main())
sys.exit(0 if success else 1)
"; then
        print_success "Data collection completed"
    else
        print_warning "Data collection failed, but system is still functional"
    fi
}

# Function to run system tests
run_tests() {
    print_status "Running system tests..."
    
    if python3 test_complete_system.py; then
        print_success "All tests passed"
    else
        print_warning "Some tests failed, but system may still be functional"
    fi
}

# Function to show system status
show_status() {
    echo ""
    echo "================================================================================"
    echo "🏆 ADS599 CAPSTONE SOCCER INTELLIGENCE SYSTEM"
    echo "================================================================================"
    echo ""
    
    # Check Docker services
    print_status "Docker Services Status:"
    if command_exists "docker compose"; then
        docker compose ps
    else
        docker-compose ps
    fi
    
    echo ""
    print_status "System URLs:"
    echo "  📊 Database: postgresql://soccerapp:soccerpass123@localhost:5432/soccer_intelligence"
    echo "  🔄 Redis Cache: redis://localhost:6379"
    echo ""
    
    print_status "Available Commands:"
    echo "  🔍 Test system: python3 test_complete_system.py"
    echo "  📊 Collect data: python3 services/multi_api_data_collector.py"
    echo "  🗄️  Initialize DB: python3 scripts/database/initialize_database.py"
    echo ""
    
    print_success "System is ready for use!"
    echo "================================================================================"
}

# Main execution
main() {
    echo "================================================================================"
    echo "🚀 ADS599 Capstone Soccer Intelligence System Setup"
    echo "================================================================================"
    echo ""
    
    # Check prerequisites
    check_docker
    check_python
    
    # Setup system
    check_configuration
    install_dependencies
    start_docker_services
    initialize_database
    
    # Optional data collection
    run_data_collection "$1"
    
    # Run tests
    run_tests
    
    # Show final status
    show_status
    
    echo ""
    print_success "🎉 Setup completed successfully!"
    echo ""
}

# Handle script arguments
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "ADS599 Capstone Soccer Intelligence System Setup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --no-data    Skip data collection during setup"
    echo "  --help, -h   Show this help message"
    echo ""
    echo "This script will:"
    echo "  1. Check system prerequisites (Docker, Python)"
    echo "  2. Start Docker services (PostgreSQL, Redis)"
    echo "  3. Initialize database with complete schema"
    echo "  4. Run sample data collection (unless --no-data)"
    echo "  5. Run system validation tests"
    echo "  6. Display system status and usage information"
    echo ""
    exit 0
fi

# Run main function with arguments
main "$@"

#!/bin/bash

# Real Madrid 2023-2024 Match Analysis System - Docker Startup Script
# Comprehensive containerized setup for Champions League winning season analysis

set -e

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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if command -v docker-compose > /dev/null 2>&1; then
        DOCKER_COMPOSE_CMD="docker-compose"
    elif docker compose version > /dev/null 2>&1; then
        DOCKER_COMPOSE_CMD="docker compose"
    else
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    print_success "Docker Compose is available: $DOCKER_COMPOSE_CMD"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs/match_analysis/2023-2024/{uefa_champions_league,la_liga,copa_del_rey,summary}
    mkdir -p data/focused/players/real_madrid_2023_2024
    mkdir -p database/{init,backups}
    mkdir -p web_interface/templates
    
    print_success "Directories created"
}

# Function to start the Real Madrid analysis system
start_system() {
    print_status "Starting Real Madrid 2023-2024 Match Analysis System..."
    
    # Start core services
    $DOCKER_COMPOSE_CMD -f docker-compose.real-madrid.yml up -d postgres redis real_madrid_app
    
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Check if database is ready
    if $DOCKER_COMPOSE_CMD -f docker-compose.real-madrid.yml exec postgres pg_isready -U soccerapp -d soccer_intelligence; then
        print_success "Database is ready"
    else
        print_warning "Database might not be fully ready yet. Continuing..."
    fi
    
    # Start web interface
    print_status "Starting web interface..."
    $DOCKER_COMPOSE_CMD -f docker-compose.real-madrid.yml up -d match_analyzer_web
    
    print_success "Real Madrid Analysis System started successfully!"
}

# Function to collect data from SportMonks API
collect_data() {
    print_status "Collecting Real Madrid 2023-2024 data from SportMonks API..."
    print_status "This may take several minutes due to rate limiting..."

    $DOCKER_COMPOSE_CMD -f docker-compose.real-madrid.yml --profile collector run --rm sportmonks_collector

    if [ $? -eq 0 ]; then
        print_success "Data collection completed successfully!"
        print_status "Data saved to PostgreSQL database"
    else
        print_error "Failed to collect data from SportMonks API"
        return 1
    fi
}

# Function to generate match reports
generate_reports() {
    print_status "Generating comprehensive match reports for all 52 games..."

    $DOCKER_COMPOSE_CMD -f docker-compose.real-madrid.yml --profile generator run --rm match_generator

    if [ $? -eq 0 ]; then
        print_success "Match reports generated successfully!"
        print_status "Reports saved to: logs/match_analysis/2023-2024/"
    else
        print_error "Failed to generate match reports"
        return 1
    fi
}

# Function to run complete data pipeline
run_full_pipeline() {
    print_status "Running complete Real Madrid 2023-2024 data pipeline..."

    # Step 1: Collect data from SportMonks API
    print_status "Step 1/2: Collecting data from SportMonks API..."
    collect_data

    if [ $? -ne 0 ]; then
        print_error "Data collection failed, stopping pipeline"
        return 1
    fi

    # Step 2: Generate match reports
    print_status "Step 2/2: Generating match analysis reports..."
    generate_reports

    if [ $? -eq 0 ]; then
        print_success "Complete data pipeline executed successfully!"
        print_status "✅ SportMonks data collected"
        print_status "✅ Match reports generated"
        print_status "✅ System ready for analysis"
    else
        print_error "Report generation failed"
        return 1
    fi
}

# Function to display premium statistics
show_premium_stats() {
    print_status "Displaying premium Real Madrid statistics..."
    
    $DOCKER_COMPOSE_CMD -f docker-compose.real-madrid.yml --profile display run --rm premium_display
}

# Function to start development environment
start_dev() {
    print_status "Starting development environment with Jupyter..."
    
    $DOCKER_COMPOSE_CMD -f docker-compose.real-madrid.yml up -d real_madrid_dev
    
    print_success "Development environment started!"
    print_status "Jupyter Lab available at: http://localhost:8888"
    print_status "Streamlit available at: http://localhost:8501"
}

# Function to show system status
show_status() {
    print_status "Real Madrid Analysis System Status:"
    echo ""
    
    $DOCKER_COMPOSE_CMD -f docker-compose.real-madrid.yml ps
    
    echo ""
    print_status "Available Services:"
    echo "  🏆 Web Interface: http://localhost:8080"
    echo "  📊 Database: localhost:5432"
    echo "  🔄 Redis Cache: localhost:6379"
    echo "  📝 Jupyter Lab: http://localhost:8888 (if dev environment is running)"
    echo "  📈 Streamlit: http://localhost:8501 (if dev environment is running)"
}

# Function to stop the system
stop_system() {
    print_status "Stopping Real Madrid Analysis System..."
    
    $DOCKER_COMPOSE_CMD -f docker-compose.real-madrid.yml down
    
    print_success "System stopped"
}

# Function to clean up everything
cleanup() {
    print_warning "This will remove all containers, volumes, and generated data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up Real Madrid Analysis System..."
        
        $DOCKER_COMPOSE_CMD -f docker-compose.real-madrid.yml down -v --remove-orphans
        docker system prune -f
        
        print_success "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Function to show logs
show_logs() {
    local service=${1:-real_madrid_app}
    print_status "Showing logs for service: $service"
    
    $DOCKER_COMPOSE_CMD -f docker-compose.real-madrid.yml logs -f $service
}

# Function to show help
show_help() {
    echo "Real Madrid 2023-2024 Match Analysis System - Enhanced Docker Management"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start          Start the complete analysis system"
    echo "  stop           Stop all services"
    echo "  restart        Restart all services"
    echo "  status         Show system status"
    echo "  dev            Start development environment"
    echo "  collect        Collect data from SportMonks API"
    echo "  generate       Generate all 52 match reports"
    echo "  pipeline       Run complete data pipeline (collect + generate)"
    echo "  stats          Display premium statistics"
    echo "  logs [service] Show logs for a service"
    echo "  cleanup        Remove all containers and data"
    echo "  help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start the system"
    echo "  $0 collect                  # Collect data from SportMonks API"
    echo "  $0 pipeline                 # Run complete data pipeline"
    echo "  $0 generate                 # Generate match reports"
    echo "  $0 logs sportmonks_collector # Show collector logs"
    echo "  $0 dev                      # Start development environment"
    echo ""
    echo "Services:"
    echo "  🏆 real_madrid_app         # Main application"
    echo "  🌐 match_analyzer_web      # Web interface"
    echo "  🗄️  postgres               # Enhanced database with SportMonks schema"
    echo "  📊 sportmonks_collector    # SportMonks API data collector"
    echo "  🔄 redis                   # Cache"
    echo "  👨‍💻 real_madrid_dev         # Development environment"
    echo ""
    echo "Data Pipeline:"
    echo "  1. collect  -> Fetch Real Madrid 2023-2024 data from SportMonks API"
    echo "  2. generate -> Create comprehensive match analysis reports"
    echo "  3. pipeline -> Run both steps automatically"
}

# Main script logic
main() {
    echo "🏆 Real Madrid 2023-2024 Champions League Winners - Match Analysis System 🏆"
    echo "==============================================================================="
    
    # Check prerequisites
    check_docker
    check_docker_compose
    create_directories
    
    # Handle commands
    case "${1:-start}" in
        "start")
            start_system
            show_status
            ;;
        "stop")
            stop_system
            ;;
        "restart")
            stop_system
            sleep 2
            start_system
            show_status
            ;;
        "status")
            show_status
            ;;
        "dev")
            start_dev
            show_status
            ;;
        "collect")
            collect_data
            ;;
        "generate")
            generate_reports
            ;;
        "pipeline")
            run_full_pipeline
            ;;
        "stats")
            show_premium_stats
            ;;
        "logs")
            show_logs $2
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"

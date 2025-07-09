#!/bin/bash

# Comprehensive Data Infrastructure Startup Script
# ADS599 Capstone - Soccer Intelligence Project
# Enhanced Real Madrid Data Collection with Redis Caching

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.real-madrid.yml"
PROJECT_NAME="real-madrid-analysis"
LOG_DIR="./logs"
DATA_DIR="./data"

# Detect Docker Compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v "docker-compose" &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose.${NC}"
    exit 1
fi

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "============================================================================"
    echo "🏆 ADS599 Capstone - Real Madrid Soccer Intelligence System"
    echo "🚀 Comprehensive Data Infrastructure with Redis Caching"
    echo "============================================================================"
    echo -e "${NC}"
}

print_separator() {
    echo -e "${BLUE}────────────────────────────────────────────────────────────────────────────${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check API key
    if ! grep -q "TmPuKHKnA7OJdHxp8zGzF5oevN0mgyqOOOaqgWMOr7KrhpaZeg9xB2ajoq2p" config/api_keys.yaml; then
        log_error "SportMonks API key not found or incorrect in config/api_keys.yaml"
        exit 1
    fi
    
    # Create required directories
    mkdir -p "$LOG_DIR/data_collection"
    mkdir -p "$LOG_DIR/match_analysis"
    mkdir -p "$LOG_DIR/performance"
    mkdir -p "$DATA_DIR/cache"
    mkdir -p "$DATA_DIR/exports"
    
    log_success "Prerequisites check completed"
}

# Clean up previous containers
cleanup_containers() {
    log_info "Cleaning up previous containers..."
    
    $DOCKER_COMPOSE_CMD -f $COMPOSE_FILE down --remove-orphans 2>/dev/null || true
    
    # Remove any dangling volumes if requested
    if [[ "$1" == "--clean-volumes" ]]; then
        log_warning "Removing all data volumes..."
        docker volume prune -f 2>/dev/null || true
    fi
    
    log_success "Container cleanup completed"
}

# Start infrastructure services
start_infrastructure() {
    log_info "Starting infrastructure services..."
    print_separator
    
    # Start PostgreSQL and Redis first
    log_info "🗄️  Starting PostgreSQL database..."
    $DOCKER_COMPOSE_CMD -f $COMPOSE_FILE up -d postgres
    
    log_info "🔄 Starting Redis cache..."
    $DOCKER_COMPOSE_CMD -f $COMPOSE_FILE up -d redis
    
    # Wait for services to be healthy
    log_info "⏳ Waiting for database to be ready..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if $DOCKER_COMPOSE_CMD -f $COMPOSE_FILE exec postgres pg_isready -U soccerapp -d soccer_intelligence >/dev/null 2>&1; then
            break
        fi
        sleep 2
        timeout=$((timeout-2))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "Database failed to start within 60 seconds"
        exit 1
    fi
    
    log_info "⏳ Waiting for Redis to be ready..."
    timeout=30
    while [ $timeout -gt 0 ]; do
        if $DOCKER_COMPOSE_CMD -f $COMPOSE_FILE exec redis redis-cli --no-auth-warning -a redispass123 ping >/dev/null 2>&1; then
            break
        fi
        sleep 2
        timeout=$((timeout-2))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "Redis failed to start within 30 seconds"
        exit 1
    fi
    
    log_success "Infrastructure services started successfully"
}

# Run comprehensive data collection
run_data_collection() {
    log_info "Starting comprehensive data collection..."
    print_separator
    
    log_info "🔄 Running enhanced SportMonks data collector..."
    log_info "📊 This will collect data for Real Madrid across multiple seasons (2019-2024)"
    log_info "⏱️  Estimated time: 15-30 minutes depending on API rate limits"
    
    # Run the enhanced collector
    $DOCKER_COMPOSE_CMD -f $COMPOSE_FILE --profile collector run --rm sportmonks_collector python enhanced_collector.py
    
    if [ $? -eq 0 ]; then
        log_success "Data collection completed successfully!"
        
        # Show collection summary
        log_info "📈 Generating collection summary..."
        $DOCKER_COMPOSE_CMD -f $COMPOSE_FILE exec postgres psql -U soccerapp -d soccer_intelligence -c "
            SELECT 
                collection_type,
                records_collected,
                collection_status,
                collection_duration_seconds,
                collection_timestamp
            FROM api_collection_metadata 
            ORDER BY collection_timestamp DESC 
            LIMIT 10;
        " 2>/dev/null || log_warning "Could not generate collection summary"
        
    else
        log_error "Data collection failed!"
        return 1
    fi
}

# Start analysis services
start_analysis_services() {
    log_info "Starting analysis services..."
    print_separator
    
    # Start the main application
    log_info "🚀 Starting Real Madrid analysis application..."
    $DOCKER_COMPOSE_CMD -f $COMPOSE_FILE up -d real_madrid_app
    
    # Start web interface
    log_info "🌐 Starting web interface..."
    $DOCKER_COMPOSE_CMD -f $COMPOSE_FILE up -d match_analyzer_web
    
    log_success "Analysis services started successfully!"
}

# Show system status
show_status() {
    log_info "System Status:"
    print_separator
    
    echo -e "${BLUE}🐳 Container Status:${NC}"
    $DOCKER_COMPOSE_CMD -f $COMPOSE_FILE ps
    
    echo -e "\n${BLUE}📊 Database Status:${NC}"
    $DOCKER_COMPOSE_CMD -f $COMPOSE_FILE exec postgres psql -U soccerapp -d soccer_intelligence -c "
        SELECT 
            'Teams' as table_name, COUNT(*) as records 
        FROM enhanced_teams
        UNION ALL
        SELECT 
            'Matches' as table_name, COUNT(*) as records 
        FROM enhanced_matches
        UNION ALL
        SELECT 
            'Player Statistics' as table_name, COUNT(*) as records 
        FROM enhanced_player_statistics;
    " 2>/dev/null || log_warning "Could not retrieve database status"
    
    echo -e "\n${BLUE}🔄 Redis Status:${NC}"
    redis_info=$($DOCKER_COMPOSE_CMD -f $COMPOSE_FILE exec redis redis-cli --no-auth-warning -a redispass123 info memory 2>/dev/null | grep used_memory_human || echo "Redis info unavailable")
    echo "Memory usage: $redis_info"
    
    echo -e "\n${BLUE}🌐 Access URLs:${NC}"
    echo "• Web Interface: http://localhost:8501"
    echo "• Database: localhost:5432 (soccer_intelligence)"
    echo "• Redis: localhost:6379"
    
    echo -e "\n${BLUE}📁 Log Files:${NC}"
    echo "• Data Collection: $LOG_DIR/data_collection/"
    echo "• Match Analysis: $LOG_DIR/match_analysis/"
    echo "• Performance: $LOG_DIR/performance/"
}

# Main execution
main() {
    print_header
    
    case "${1:-start}" in
        "start")
            check_prerequisites
            cleanup_containers
            start_infrastructure
            run_data_collection
            start_analysis_services
            show_status
            log_success "🎉 Real Madrid Soccer Intelligence System is ready!"
            ;;
        "collect-only")
            check_prerequisites
            cleanup_containers
            start_infrastructure
            run_data_collection
            ;;
        "infrastructure-only")
            check_prerequisites
            cleanup_containers
            start_infrastructure
            show_status
            ;;
        "status")
            show_status
            ;;
        "stop")
            log_info "Stopping all services..."
            $DOCKER_COMPOSE_CMD -f $COMPOSE_FILE down
            log_success "All services stopped"
            ;;
        "clean")
            log_warning "Stopping services and removing volumes..."
            cleanup_containers --clean-volumes
            log_success "System cleaned"
            ;;
        *)
            echo "Usage: $0 {start|collect-only|infrastructure-only|status|stop|clean}"
            echo ""
            echo "Commands:"
            echo "  start              - Full system startup with data collection"
            echo "  collect-only       - Start infrastructure and run data collection only"
            echo "  infrastructure-only - Start only PostgreSQL and Redis"
            echo "  status             - Show system status"
            echo "  stop               - Stop all services"
            echo "  clean              - Stop services and remove all data"
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"

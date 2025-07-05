#!/bin/bash
# Docker Entrypoint Script for ADS599 Capstone Soccer Intelligence System
# Handles initialization, configuration validation, and service startup

set -e

# ============================================================================
# Environment Variables and Defaults
# ============================================================================

# Set default values
export PYTHONPATH="${PYTHONPATH:-/app/src}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export ENVIRONMENT="${ENVIRONMENT:-production}"

# ============================================================================
# Logging Functions
# ============================================================================

log_info() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_warn() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [WARN] $1"
}

log_error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR] $1"
}

# ============================================================================
# Configuration Validation
# ============================================================================

validate_api_keys() {
    log_info "Validating API configuration..."
    
    # Check if API keys file exists
    if [ ! -f "/app/config/api_keys.yaml" ]; then
        log_warn "API keys file not found, creating from template..."
        cp /app/config/api_keys_template.yaml /app/config/api_keys.yaml
        
        # Replace template values with environment variables
        if [ -n "$API_FOOTBALL_KEY" ]; then
            sed -i "s/your_api_football_key_here/$API_FOOTBALL_KEY/g" /app/config/api_keys.yaml
        fi
        
        if [ -n "$OPENAI_API_KEY" ]; then
            sed -i "s/your_openai_api_key_here/$OPENAI_API_KEY/g" /app/config/api_keys.yaml
        fi
        
        if [ -n "$TWITTER_BEARER_TOKEN" ]; then
            sed -i "s/your_twitter_bearer_token_here/$TWITTER_BEARER_TOKEN/g" /app/config/api_keys.yaml
        fi
        
        if [ -n "$SPORTMONKS_API_KEY" ]; then
            sed -i "s/your_sportmonks_api_key_here/$SPORTMONKS_API_KEY/g" /app/config/api_keys.yaml
        fi
    fi
    
    log_info "API configuration validated"
}

validate_directories() {
    log_info "Validating directory structure..."
    
    # Create required directories if they don't exist
    mkdir -p /app/data/focused/players
    mkdir -p /app/data/focused/teams
    mkdir -p /app/data/cache
    mkdir -p /app/data/analysis
    mkdir -p /app/data/reports
    mkdir -p /app/logs/player_collection
    mkdir -p /app/logs/team_collection
    mkdir -p /app/logs/analysis
    
    # Set proper permissions
    chown -R soccerapp:soccerapp /app/data /app/logs
    
    log_info "Directory structure validated"
}

validate_python_environment() {
    log_info "Validating Python environment..."
    
    # Test core imports
    python -c "
import sys
sys.path.append('/app/src')
try:
    from soccer_intelligence.utils.config import Config
    from soccer_intelligence.data_collection.api_football import APIFootballClient
    print('Core modules imported successfully')
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)
"
    
    log_info "Python environment validated"
}

# ============================================================================
# Database Connection Validation
# ============================================================================

wait_for_postgres() {
    if [ -n "$POSTGRES_HOST" ]; then
        log_info "Waiting for PostgreSQL to be ready..."
        
        until python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'postgres'),
        port=os.environ.get('POSTGRES_PORT', '5432'),
        database=os.environ.get('POSTGRES_DB', 'soccer_intelligence'),
        user=os.environ.get('POSTGRES_USER', 'soccerapp'),
        password=os.environ.get('POSTGRES_PASSWORD', 'soccerpass123')
    )
    conn.close()
    print('PostgreSQL is ready')
except Exception as e:
    print(f'PostgreSQL not ready: {e}')
    exit(1)
"; do
            log_info "PostgreSQL is unavailable - sleeping"
            sleep 2
        done
        
        log_info "PostgreSQL is ready"
    fi
}

wait_for_redis() {
    if [ -n "$REDIS_HOST" ]; then
        log_info "Waiting for Redis to be ready..."
        
        until python -c "
import redis
import os
try:
    r = redis.Redis(
        host=os.environ.get('REDIS_HOST', 'redis'),
        port=int(os.environ.get('REDIS_PORT', '6379')),
        password=os.environ.get('REDIS_PASSWORD', 'redispass123'),
        db=int(os.environ.get('REDIS_DB', '0'))
    )
    r.ping()
    print('Redis is ready')
except Exception as e:
    print(f'Redis not ready: {e}')
    exit(1)
"; do
            log_info "Redis is unavailable - sleeping"
            sleep 2
        done
        
        log_info "Redis is ready"
    fi
}

# ============================================================================
# Application Initialization
# ============================================================================

initialize_application() {
    log_info "Initializing Soccer Intelligence System..."
    
    # Validate configuration
    validate_api_keys
    validate_directories
    validate_python_environment
    
    # Wait for dependencies
    wait_for_postgres
    wait_for_redis
    
    log_info "Application initialized successfully"
}

# ============================================================================
# Service Management
# ============================================================================

start_data_collection() {
    log_info "Starting data collection service..."
    exec python scripts/data_collection/comprehensive_player_collection.py "$@"
}

start_team_collection() {
    log_info "Starting team statistics collection..."
    exec python scripts/data_collection/comprehensive_team_statistics_collector.py "$@"
}

start_analysis() {
    log_info "Starting analysis service..."
    exec python scripts/analysis/simple_shapley_analysis.py "$@"
}

start_validation() {
    log_info "Starting validation service..."
    exec python scripts/analysis/player_statistics_validator.py "$@"
}

start_jupyter() {
    log_info "Starting Jupyter notebook server..."
    exec jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token="${JUPYTER_TOKEN:-}" --NotebookApp.password="${JUPYTER_PASSWORD:-}"
}

start_streamlit() {
    log_info "Starting Streamlit dashboard..."
    exec streamlit run scripts/dashboard/streamlit_app.py --server.address=0.0.0.0 --server.port=8501
}

# ============================================================================
# Main Execution Logic
# ============================================================================

main() {
    log_info "Starting Soccer Intelligence System Docker Container"
    log_info "Environment: $ENVIRONMENT"
    log_info "Log Level: $LOG_LEVEL"
    
    # Initialize application
    initialize_application
    
    # Determine service to start based on arguments
    case "${1:-default}" in
        "data-collection")
            shift
            start_data_collection "$@"
            ;;
        "team-collection")
            shift
            start_team_collection "$@"
            ;;
        "analysis")
            shift
            start_analysis "$@"
            ;;
        "validation")
            shift
            start_validation "$@"
            ;;
        "jupyter")
            start_jupyter
            ;;
        "streamlit")
            start_streamlit
            ;;
        "bash"|"shell")
            log_info "Starting interactive shell..."
            exec bash
            ;;
        "default"|*)
            log_info "Starting default service (validation)..."
            start_validation "$@"
            ;;
    esac
}

# Execute main function with all arguments
main "$@"

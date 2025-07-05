#!/bin/bash
# Workflow Execution Script for ADS599 Capstone Soccer Intelligence System
# Orchestrates data collection, analysis, and validation workflows in containers

set -e

# ============================================================================
# Configuration Variables
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Default workflow parameters
WORKFLOW_TYPE="${1:-full}"
MAX_TEAMS="${MAX_TEAMS:-10}"
SEASONS="${SEASONS:-2022,2023,2024}"
PARALLEL_WORKERS="${PARALLEL_WORKERS:-2}"

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
# Docker Compose Helper Functions
# ============================================================================

ensure_containers_running() {
    log_info "Ensuring required containers are running..."
    
    # Start core services
    docker-compose up -d postgres redis
    
    # Wait for services to be ready
    log_info "Waiting for database services to be ready..."
    docker-compose exec postgres pg_isready -U soccerapp -d soccer_intelligence || {
        log_error "PostgreSQL is not ready"
        exit 1
    }
    
    docker-compose exec redis redis-cli ping || {
        log_error "Redis is not ready"
        exit 1
    }
    
    log_info "Database services are ready"
}

run_container_command() {
    local service="$1"
    local command="$2"
    shift 2
    
    log_info "Running command in $service: $command"
    docker-compose run --rm "$service" $command "$@"
}

# ============================================================================
# Data Collection Workflows
# ============================================================================

run_player_data_collection() {
    log_info "Starting player data collection workflow..."
    
    local seasons_array=(${SEASONS//,/ })
    
    for season in "${seasons_array[@]}"; do
        log_info "Collecting player data for season $season..."
        
        run_container_command soccer-intelligence \
            "python scripts/data_collection/comprehensive_player_collection.py" \
            --mode basic_only \
            --seasons "$season" \
            --max-teams "$MAX_TEAMS"
        
        if [ $? -eq 0 ]; then
            log_info "Player data collection completed for season $season"
        else
            log_error "Player data collection failed for season $season"
            return 1
        fi
    done
    
    log_info "Player data collection workflow completed"
}

run_team_data_collection() {
    log_info "Starting team data collection workflow..."
    
    run_container_command soccer-intelligence \
        "python scripts/data_collection/comprehensive_team_statistics_collector.py" \
        --max-teams "$MAX_TEAMS" \
        --seasons "$SEASONS"
    
    if [ $? -eq 0 ]; then
        log_info "Team data collection workflow completed"
    else
        log_error "Team data collection workflow failed"
        return 1
    fi
}

run_competition_data_collection() {
    log_info "Starting competition-specific data collection..."
    
    run_container_command soccer-intelligence \
        "python scripts/data_collection/comprehensive_player_collection.py" \
        --mode competition_only \
        --comp-seasons "$SEASONS"
    
    if [ $? -eq 0 ]; then
        log_info "Competition data collection workflow completed"
    else
        log_error "Competition data collection workflow failed"
        return 1
    fi
}

# ============================================================================
# Analysis Workflows
# ============================================================================

run_shapley_analysis() {
    log_info "Starting Shapley value analysis workflow..."
    
    # Run Shapley analysis for key teams
    run_container_command soccer-intelligence \
        "python scripts/analysis/simple_shapley_analysis.py"
    
    if [ $? -eq 0 ]; then
        log_info "Shapley analysis workflow completed"
    else
        log_error "Shapley analysis workflow failed"
        return 1
    fi
}

run_multi_season_analysis() {
    log_info "Starting multi-season comparative analysis..."
    
    run_container_command soccer-intelligence \
        "python scripts/analysis/multi_season_comparative_analysis.py"
    
    if [ $? -eq 0 ]; then
        log_info "Multi-season analysis workflow completed"
    else
        log_error "Multi-season analysis workflow failed"
        return 1
    fi
}

run_performance_analysis() {
    log_info "Starting performance metrics analysis..."
    
    # Run comprehensive performance analysis
    run_container_command soccer-intelligence \
        "python -c \"
import sys
sys.path.append('src')
from soccer_intelligence.analysis.performance_metrics import PerformanceMetrics
from soccer_intelligence.data_processing.data_integrator import DataIntegrator

# Initialize components
metrics = PerformanceMetrics()
integrator = DataIntegrator()

# Run analysis
print('Running performance analysis...')
# Add your performance analysis logic here
print('Performance analysis completed')
\""
    
    if [ $? -eq 0 ]; then
        log_info "Performance analysis workflow completed"
    else
        log_error "Performance analysis workflow failed"
        return 1
    fi
}

# ============================================================================
# Validation Workflows
# ============================================================================

run_data_validation() {
    log_info "Starting data validation workflow..."
    
    # Run player statistics validation
    run_container_command soccer-intelligence \
        "python scripts/analysis/player_statistics_validator.py"
    
    if [ $? -ne 0 ]; then
        log_error "Player statistics validation failed"
        return 1
    fi
    
    # Run team statistics validation
    run_container_command soccer-intelligence \
        "python scripts/analysis/team_statistics_validator.py"
    
    if [ $? -ne 0 ]; then
        log_error "Team statistics validation failed"
        return 1
    fi
    
    log_info "Data validation workflow completed"
}

run_integration_validation() {
    log_info "Starting integration validation..."
    
    run_container_command soccer-intelligence \
        "python scripts/analysis/player_statistics_validator.py" \
        --mode integration_only
    
    if [ $? -eq 0 ]; then
        log_info "Integration validation workflow completed"
    else
        log_error "Integration validation workflow failed"
        return 1
    fi
}

# ============================================================================
# Parallel Workflow Execution
# ============================================================================

run_parallel_collection() {
    log_info "Starting parallel data collection workflow..."
    
    # Start multiple collection workers
    for i in $(seq 1 "$PARALLEL_WORKERS"); do
        log_info "Starting collection worker $i..."
        
        docker-compose up -d --scale data-collector="$PARALLEL_WORKERS" data-collector
    done
    
    # Wait for all workers to complete
    log_info "Waiting for parallel collection to complete..."
    docker-compose logs -f data-collector
    
    log_info "Parallel collection workflow completed"
}

run_parallel_analysis() {
    log_info "Starting parallel analysis workflow..."
    
    # Start multiple analysis workers
    for i in $(seq 1 "$PARALLEL_WORKERS"); do
        log_info "Starting analysis worker $i..."
        
        docker-compose up -d --scale analysis-worker="$PARALLEL_WORKERS" analysis-worker
    done
    
    # Wait for all workers to complete
    log_info "Waiting for parallel analysis to complete..."
    docker-compose logs -f analysis-worker
    
    log_info "Parallel analysis workflow completed"
}

# ============================================================================
# Complete Workflow Orchestration
# ============================================================================

run_full_workflow() {
    log_info "Starting complete Soccer Intelligence workflow..."
    
    # Phase 1: Data Collection
    log_info "Phase 1: Data Collection"
    run_player_data_collection || return 1
    run_team_data_collection || return 1
    run_competition_data_collection || return 1
    
    # Phase 2: Data Validation
    log_info "Phase 2: Data Validation"
    run_data_validation || return 1
    
    # Phase 3: Analysis
    log_info "Phase 3: Analysis"
    run_shapley_analysis || return 1
    run_multi_season_analysis || return 1
    run_performance_analysis || return 1
    
    # Phase 4: Integration Validation
    log_info "Phase 4: Integration Validation"
    run_integration_validation || return 1
    
    log_info "Complete workflow finished successfully!"
}

run_quick_workflow() {
    log_info "Starting quick validation workflow..."
    
    # Quick data collection with limited scope
    MAX_TEAMS=5 run_player_data_collection || return 1
    
    # Quick validation
    run_data_validation || return 1
    
    # Quick analysis
    run_shapley_analysis || return 1
    
    log_info "Quick workflow completed successfully!"
}

# ============================================================================
# Main Execution Logic
# ============================================================================

show_usage() {
    echo "Usage: $0 [WORKFLOW_TYPE]"
    echo ""
    echo "Available workflow types:"
    echo "  full              - Complete data collection and analysis workflow"
    echo "  quick             - Quick validation workflow with limited scope"
    echo "  collection        - Data collection workflows only"
    echo "  analysis          - Analysis workflows only"
    echo "  validation        - Validation workflows only"
    echo "  parallel          - Parallel execution workflows"
    echo "  player-collection - Player data collection only"
    echo "  team-collection   - Team data collection only"
    echo "  shapley           - Shapley analysis only"
    echo "  multi-season      - Multi-season analysis only"
    echo ""
    echo "Environment variables:"
    echo "  MAX_TEAMS         - Maximum number of teams to process (default: 10)"
    echo "  SEASONS           - Comma-separated list of seasons (default: 2022,2023,2024)"
    echo "  PARALLEL_WORKERS  - Number of parallel workers (default: 2)"
}

main() {
    log_info "Starting Soccer Intelligence workflow execution"
    log_info "Workflow type: $WORKFLOW_TYPE"
    log_info "Max teams: $MAX_TEAMS"
    log_info "Seasons: $SEASONS"
    log_info "Parallel workers: $PARALLEL_WORKERS"
    
    # Ensure containers are running
    ensure_containers_running
    
    # Execute workflow based on type
    case "$WORKFLOW_TYPE" in
        "full")
            run_full_workflow
            ;;
        "quick")
            run_quick_workflow
            ;;
        "collection")
            run_player_data_collection
            run_team_data_collection
            run_competition_data_collection
            ;;
        "analysis")
            run_shapley_analysis
            run_multi_season_analysis
            run_performance_analysis
            ;;
        "validation")
            run_data_validation
            run_integration_validation
            ;;
        "parallel")
            run_parallel_collection
            run_parallel_analysis
            ;;
        "player-collection")
            run_player_data_collection
            ;;
        "team-collection")
            run_team_data_collection
            ;;
        "shapley")
            run_shapley_analysis
            ;;
        "multi-season")
            run_multi_season_analysis
            ;;
        "help"|"-h"|"--help")
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown workflow type: $WORKFLOW_TYPE"
            show_usage
            exit 1
            ;;
    esac
    
    log_info "Workflow execution completed successfully!"
}

# Execute main function with all arguments
main "$@"

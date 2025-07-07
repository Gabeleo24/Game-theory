#!/bin/bash

# Jupyter Notebook Management Script
# ADS599 Capstone Soccer Intelligence System

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

# Check if Docker Compose command exists
if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    print_error "Docker Compose is not available"
    exit 1
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start-jupyter [role]     Start Jupyter environment for specific role"
    echo "  stop-jupyter [role]      Stop Jupyter environment for specific role"
    echo "  status                   Show status of all Jupyter environments"
    echo "  backup                   Backup all notebooks"
    echo "  restore [backup_file]    Restore notebooks from backup"
    echo "  clean-outputs           Clean all notebook outputs"
    echo "  sync                    Sync notebooks with Git"
    echo "  create-notebook [name]   Create new notebook from template"
    echo "  list-notebooks          List all notebooks by category"
    echo "  help                    Show this help message"
    echo ""
    echo "Roles: analyst, developer, researcher, all"
    echo ""
    echo "Examples:"
    echo "  $0 start-jupyter analyst           # Start analyst Jupyter environment"
    echo "  $0 create-notebook team_analysis   # Create new team analysis notebook"
    echo "  $0 backup                         # Backup all notebooks"
    echo "  $0 clean-outputs                  # Clean all notebook outputs"
}

# Function to start Jupyter environment
start_jupyter() {
    local role="$1"
    
    case "$role" in
        analyst)
            print_status "Starting Jupyter environment for analysts..."
            $DOCKER_COMPOSE_CMD --profile analyst up jupyter-analyst -d
            print_success "Analyst Jupyter environment started!"
            echo "Access at: http://localhost:8888"
            echo "Token: analyst_secure_token_2024"
            ;;
        developer)
            print_status "Starting Jupyter environment for developers..."
            $DOCKER_COMPOSE_CMD --profile developer up jupyter-developer -d
            print_success "Developer Jupyter environment started!"
            echo "Access at: http://localhost:8889"
            echo "Token: developer_secure_token_2024"
            ;;
        researcher)
            print_status "Starting Jupyter environment for researchers..."
            $DOCKER_COMPOSE_CMD --profile researcher up jupyter-researcher -d
            print_success "Researcher Jupyter environment started!"
            echo "Access at: http://localhost:8890"
            echo "Token: researcher_secure_token_2024"
            ;;
        all)
            print_status "Starting all Jupyter environments..."
            $DOCKER_COMPOSE_CMD --profile jupyter up -d
            print_success "All Jupyter environments started!"
            echo ""
            echo "Access points:"
            echo "  Analyst:    http://localhost:8888 (token: analyst_secure_token_2024)"
            echo "  Developer:  http://localhost:8889 (token: developer_secure_token_2024)"
            echo "  Researcher: http://localhost:8890 (token: researcher_secure_token_2024)"
            ;;
        *)
            print_error "Invalid role: $role"
            echo "Valid roles: analyst, developer, researcher, all"
            exit 1
            ;;
    esac
}

# Function to stop Jupyter environment
stop_jupyter() {
    local role="$1"
    
    case "$role" in
        analyst)
            print_status "Stopping analyst Jupyter environment..."
            $DOCKER_COMPOSE_CMD stop jupyter-analyst
            print_success "Analyst Jupyter environment stopped"
            ;;
        developer)
            print_status "Stopping developer Jupyter environment..."
            $DOCKER_COMPOSE_CMD stop jupyter-developer
            print_success "Developer Jupyter environment stopped"
            ;;
        researcher)
            print_status "Stopping researcher Jupyter environment..."
            $DOCKER_COMPOSE_CMD stop jupyter-researcher
            print_success "Researcher Jupyter environment stopped"
            ;;
        all)
            print_status "Stopping all Jupyter environments..."
            $DOCKER_COMPOSE_CMD stop jupyter-analyst jupyter-developer jupyter-researcher
            print_success "All Jupyter environments stopped"
            ;;
        *)
            print_error "Invalid role: $role"
            echo "Valid roles: analyst, developer, researcher, all"
            exit 1
            ;;
    esac
}

# Function to show Jupyter status
show_status() {
    print_status "Jupyter Environment Status:"
    echo ""
    
    # Check if any Jupyter services are running
    if $DOCKER_COMPOSE_CMD ps | grep "jupyter" | grep -q "Up"; then
        echo "🟢 Running Jupyter Services:"
        $DOCKER_COMPOSE_CMD ps | grep "jupyter" | while read line; do
            service=$(echo "$line" | awk '{print $1}')
            status=$(echo "$line" | awk '{print $3}')
            ports=$(echo "$line" | grep -o '[0-9]*:888[0-9]' | cut -d: -f1)
            
            if [[ "$service" == *"analyst"* ]]; then
                echo "  📊 Analyst:    http://localhost:$ports (token: analyst_secure_token_2024)"
            elif [[ "$service" == *"developer"* ]]; then
                echo "  💻 Developer:  http://localhost:$ports (token: developer_secure_token_2024)"
            elif [[ "$service" == *"researcher"* ]]; then
                echo "  📚 Researcher: http://localhost:$ports (token: researcher_secure_token_2024)"
            fi
        done
        echo ""
    else
        echo "🔴 No Jupyter services are currently running."
        echo ""
        echo "Start environments with:"
        echo "  $0 start-jupyter analyst     # For data analysts"
        echo "  $0 start-jupyter developer   # For developers"
        echo "  $0 start-jupyter researcher  # For researchers"
        echo "  $0 start-jupyter all         # For all roles"
    fi
    
    # Show notebook statistics
    if [ -d "notebooks" ]; then
        echo "📓 Notebook Statistics:"
        echo "  Shared notebooks:    $(find notebooks/shared -name "*.ipynb" 2>/dev/null | wc -l)"
        echo "  Personal notebooks:  $(find notebooks/personal -name "*.ipynb" 2>/dev/null | wc -l)"
        echo "  Research notebooks:  $(find notebooks/research -name "*.ipynb" 2>/dev/null | wc -l)"
        echo "  Archived notebooks:  $(find notebooks/archive -name "*.ipynb" 2>/dev/null | wc -l)"
        echo ""
    fi
}

# Function to backup notebooks
backup_notebooks() {
    print_status "Creating notebook backup..."

    local notebooks_dir="/Users/home/Documents/GitHub/ADS599_Capstone/notebooks"
    local backup_dir="/Users/home/Documents/GitHub/ADS599_Capstone/backups/notebooks"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$backup_dir/notebook_backup_$timestamp.tar.gz"

    # Create backup directory if it doesn't exist
    mkdir -p "$backup_dir"

    # Create backup
    if [ -d "$notebooks_dir" ]; then
        tar -czf "$backup_file" -C "/Users/home/Documents/GitHub/ADS599_Capstone" notebooks/
        print_success "Notebooks backed up to: $backup_file"

        # Keep only last 10 backups
        ls -t "$backup_dir"/notebook_backup_*.tar.gz | tail -n +11 | xargs -r rm
        print_status "Cleaned old backups (keeping last 10)"
    else
        print_warning "No notebooks directory found at: $notebooks_dir"
    fi
}

# Function to restore notebooks
restore_notebooks() {
    local backup_file="$1"
    local notebooks_dir="/Users/home/Documents/GitHub/ADS599_Capstone/notebooks"
    local backup_dir="/Users/home/Documents/GitHub/ADS599_Capstone/backups/notebooks"

    if [ -z "$backup_file" ]; then
        print_error "Usage: $0 restore <backup_file>"
        echo ""
        echo "Available backups:"
        ls -la "$backup_dir"/notebook_backup_*.tar.gz 2>/dev/null || echo "No backups found"
        exit 1
    fi

    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi

    print_status "Restoring notebooks from: $backup_file"

    # Create backup of current notebooks
    if [ -d "$notebooks_dir" ]; then
        local current_backup="$backup_dir/current_backup_$(date +"%Y%m%d_%H%M%S").tar.gz"
        tar -czf "$current_backup" -C "/Users/home/Documents/GitHub/ADS599_Capstone" notebooks/
        print_status "Current notebooks backed up to: $current_backup"
    fi

    # Restore from backup
    tar -xzf "$backup_file" -C "/Users/home/Documents/GitHub/ADS599_Capstone"
    print_success "Notebooks restored successfully to: $notebooks_dir"
}

# Function to clean notebook outputs
clean_outputs() {
    print_status "Cleaning notebook outputs..."

    local notebooks_dir="/Users/home/Documents/GitHub/ADS599_Capstone/notebooks"

    if command -v nbstripout >/dev/null 2>&1; then
        find "$notebooks_dir" -name "*.ipynb" -exec nbstripout {} \;
        print_success "All notebook outputs cleaned"
    else
        print_warning "nbstripout not found. Installing..."
        pip install nbstripout
        find "$notebooks_dir" -name "*.ipynb" -exec nbstripout {} \;
        print_success "All notebook outputs cleaned"
    fi
}

# Function to sync notebooks with Git
sync_notebooks() {
    print_status "Syncing notebooks with Git..."

    local notebooks_dir="/Users/home/Documents/GitHub/ADS599_Capstone/notebooks"

    # Clean outputs before committing
    clean_outputs

    # Change to project directory for Git operations
    cd "/Users/home/Documents/GitHub/ADS599_Capstone"

    # Check Git status
    if git status --porcelain notebooks/ | grep -q .; then
        print_status "Changes detected in notebooks directory"

        # Add notebook changes
        git add notebooks/

        # Commit with timestamp
        local commit_msg="docs: Update notebooks - $(date '+%Y-%m-%d %H:%M:%S')"
        git commit -m "$commit_msg"

        print_success "Notebooks synced with Git"
        print_status "Commit message: $commit_msg"
    else
        print_status "No changes detected in notebooks"
    fi
}

# Function to create new notebook
create_notebook() {
    local name="$1"

    if [ -z "$name" ]; then
        print_error "Usage: $0 create-notebook <name>"
        echo "Example: $0 create-notebook team_analysis"
        exit 1
    fi

    local notebooks_dir="/Users/home/Documents/GitHub/ADS599_Capstone/notebooks"
    local author=$(git config user.name 2>/dev/null || echo "Unknown")
    local date=$(date +"%Y-%m-%d")
    local filename="${date}_${author}_${name}_v1.ipynb"
    local filepath="$notebooks_dir/shared/$filename"
    local template_path="$notebooks_dir/shared/templates/data_analysis_template.ipynb"

    print_status "Creating new notebook: $filename"

    # Check if template exists
    if [ -f "$template_path" ]; then
        cp "$template_path" "$filepath"

        # Update notebook metadata (if jq is available)
        if command -v jq >/dev/null 2>&1; then
            # Update first cell with actual information
            jq --arg author "$author" --arg date "$date" --arg name "$name" \
               '.cells[0].source[1] = "**Author:** " + $author + "  " |
                .cells[0].source[2] = "**Date:** " + $date + "  " |
                .cells[0].source[3] = "**Purpose:** " + $name + "  "' \
               "$filepath" > "${filepath}.tmp" && mv "${filepath}.tmp" "$filepath"
        fi

        print_success "Notebook created: $filepath"
        echo ""
        echo "📝 Next steps:"
        echo "  1. Open the notebook in Jupyter"
        echo "  2. Update the purpose and team role in the first cell"
        echo "  3. Follow the template structure for your analysis"
        echo "  4. Save and commit when ready to share"
    else
        print_error "Template not found at: $template_path"
        echo "Run setup first: ./scripts/jupyter/setup_jupyter_collaboration.sh"
        exit 1
    fi
}

# Function to list notebooks
list_notebooks() {
    print_status "Notebook Inventory:"
    echo ""

    local notebooks_dir="/Users/home/Documents/GitHub/ADS599_Capstone/notebooks"

    if [ -d "$notebooks_dir" ]; then
        echo "📁 Shared Notebooks:"
        find "$notebooks_dir/shared" -name "*.ipynb" -not -path "*/templates/*" 2>/dev/null | sort | while read nb; do
            echo "  📓 $(basename "$nb")"
        done
        echo ""

        echo "👤 Personal Notebooks:"
        find "$notebooks_dir/personal" -name "*.ipynb" 2>/dev/null | sort | while read nb; do
            echo "  📓 $(basename "$nb")"
        done
        echo ""

        echo "🔬 Research Notebooks:"
        find "$notebooks_dir/research" -name "*.ipynb" 2>/dev/null | sort | while read nb; do
            echo "  📓 $(basename "$nb")"
        done
        echo ""

        echo "📦 Archived Notebooks:"
        find "$notebooks_dir/archive" -name "*.ipynb" 2>/dev/null | sort | while read nb; do
            echo "  📓 $(basename "$nb")"
        done
        echo ""

        echo "📋 Templates:"
        find "$notebooks_dir/shared/templates" -name "*.ipynb" 2>/dev/null | sort | while read nb; do
            echo "  📄 $(basename "$nb")"
        done
    else
        print_warning "No notebooks directory found at: $notebooks_dir"
        echo "Run setup first: ./scripts/jupyter/setup_jupyter_collaboration.sh"
    fi
}

# Main script logic
case "${1:-help}" in
    start-jupyter)
        start_jupyter "${2:-all}"
        ;;
    stop-jupyter)
        stop_jupyter "${2:-all}"
        ;;
    status)
        show_status
        ;;
    backup)
        backup_notebooks
        ;;
    restore)
        restore_notebooks "$2"
        ;;
    clean-outputs)
        clean_outputs
        ;;
    sync)
        sync_notebooks
        ;;
    create-notebook)
        create_notebook "$2"
        ;;
    list-notebooks)
        list_notebooks
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac

#!/bin/bash

# ADS599 Capstone - Team Access Management Script
# This script manages team member access and environments

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
    echo "  start-analyst      Start analyst environment"
    echo "  start-developer    Start developer environment"
    echo "  start-researcher   Start researcher environment"
    echo "  start-team         Start full team environment"
    echo "  stop-all          Stop all team environments"
    echo "  status            Show status of all environments"
    echo "  add-member        Add a new team member"
    echo "  remove-member     Remove a team member"
    echo "  list-members      List all team members"
    echo "  help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start-analyst                    # Start analyst environment"
    echo "  $0 start-developer                  # Start developer environment"
    echo "  $0 add-member john analyst          # Add John as analyst"
    echo "  $0 status                          # Show environment status"
}

# Function to start analyst environment
start_analyst() {
    print_status "Starting analyst environment..."
    
    $DOCKER_COMPOSE_CMD --profile analyst up -d
    
    print_success "Analyst environment started!"
    echo ""
    echo "Access points:"
    echo "📊 Database: localhost:5432 (read-only)"
    echo "📓 Jupyter: http://localhost:8888"
    echo "📈 Streamlit: http://localhost:8501"
    echo ""
    echo "Login credentials:"
    echo "Database: analyst_user / analyst_pass"
    echo "Jupyter: soccer_intelligence"
}

# Function to start developer environment
start_developer() {
    print_status "Starting developer environment..."
    
    $DOCKER_COMPOSE_CMD --profile development up -d
    
    print_success "Developer environment started!"
    echo ""
    echo "Access points:"
    echo "📊 Database: localhost:5432 (full access)"
    echo "📓 Jupyter: http://localhost:8889"
    echo "📈 Streamlit: http://localhost:8502"
    echo "🔍 pgAdmin: http://localhost:8080"
    echo "🔧 Redis Commander: http://localhost:8081"
    echo ""
    echo "Login credentials:"
    echo "Database: soccerapp / soccerpass123"
    echo "pgAdmin: admin@admin.com / admin"
}

# Function to start researcher environment
start_researcher() {
    print_status "Starting researcher environment..."
    
    $DOCKER_COMPOSE_CMD --profile research up -d
    
    print_success "Researcher environment started!"
    echo ""
    echo "Access points:"
    echo "📊 Database: localhost:5432 (read-only)"
    echo "📓 Jupyter: http://localhost:8890"
    echo ""
    echo "Login credentials:"
    echo "Database: research_user / research_pass"
    echo "Jupyter: soccer_intelligence"
}

# Function to start full team environment
start_team() {
    print_status "Starting full team environment..."
    
    $DOCKER_COMPOSE_CMD --profile team up -d
    
    print_success "Full team environment started!"
    echo ""
    echo "All team environments are now running."
    echo "Use '$0 status' to see detailed access information."
}

# Function to stop all environments
stop_all() {
    print_status "Stopping all team environments..."
    
    $DOCKER_COMPOSE_CMD down
    
    print_success "All environments stopped!"
}

# Function to show environment status
show_status() {
    print_status "Team Environment Status:"
    echo ""
    
    # Check if any services are running
    if $DOCKER_COMPOSE_CMD ps | grep -q "Up"; then
        echo "🟢 Running Services:"
        $DOCKER_COMPOSE_CMD ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        
        # Show access points for running services
        if $DOCKER_COMPOSE_CMD ps | grep "jupyter" | grep -q "Up"; then
            echo "📓 Jupyter Access:"
            $DOCKER_COMPOSE_CMD ps | grep "jupyter" | while read line; do
                service=$(echo "$line" | awk '{print $1}')
                ports=$(echo "$line" | grep -o '[0-9]*:8888' | cut -d: -f1)
                if [ -n "$ports" ]; then
                    echo "  - $service: http://localhost:$ports"
                fi
            done
            echo ""
        fi
        
        if $DOCKER_COMPOSE_CMD ps | grep "postgres" | grep -q "Up"; then
            echo "📊 Database Access: localhost:5432"
            echo ""
        fi
        
        if $DOCKER_COMPOSE_CMD ps | grep "pgadmin" | grep -q "Up"; then
            echo "🔍 pgAdmin: http://localhost:8080"
            echo ""
        fi
        
    else
        echo "🔴 No services are currently running."
        echo ""
        echo "Start an environment with:"
        echo "  $0 start-analyst     # For data analysts"
        echo "  $0 start-developer   # For developers"
        echo "  $0 start-researcher  # For researchers"
        echo "  $0 start-team        # For full team"
    fi
}

# Function to add a team member
add_member() {
    local name="$1"
    local role="$2"
    
    if [ -z "$name" ] || [ -z "$role" ]; then
        print_error "Usage: $0 add-member <name> <role>"
        echo "Roles: analyst, developer, researcher"
        exit 1
    fi
    
    # Validate role
    case "$role" in
        analyst|developer|researcher)
            ;;
        *)
            print_error "Invalid role: $role"
            echo "Valid roles: analyst, developer, researcher"
            exit 1
            ;;
    esac
    
    print_status "Adding team member: $name as $role"
    
    # Create team member directory
    mkdir -p "team_members/$name"
    
    # Create member configuration
    cat > "team_members/$name/config.yaml" << EOF
name: "$name"
role: "$role"
added_date: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
access_level: "$role"
environment: "$role"

# Member-specific settings
settings:
  jupyter_password: "soccer_intelligence"
  preferred_environment: "$role"
  
# Access permissions based on role
permissions:
$(case "$role" in
    analyst)
        echo "  database: read"
        echo "  data_files: read"
        echo "  notebooks: read_write"
        ;;
    developer)
        echo "  database: read_write"
        echo "  data_files: read_write"
        echo "  notebooks: read_write"
        echo "  source_code: read_write"
        ;;
    researcher)
        echo "  database: read"
        echo "  data_files: read"
        echo "  notebooks: read_write"
        echo "  documentation: read_write"
        ;;
esac)
EOF
    
    # Add to team members list
    if [ ! -f "team_members/members.txt" ]; then
        echo "# ADS599 Capstone Team Members" > "team_members/members.txt"
        echo "# Format: name,role,added_date" >> "team_members/members.txt"
    fi
    
    echo "$name,$role,$(date -u +"%Y-%m-%d")" >> "team_members/members.txt"
    
    print_success "Team member $name added as $role"
    echo ""
    echo "Next steps for $name:"
    echo "1. Run the team setup script: ./scripts/setup/team_member_setup.sh"
    echo "2. Configure API keys in config/api_keys.yaml"
    echo "3. Start their environment: $0 start-$role"
    echo "4. Access their tools and begin collaboration"
}

# Function to remove a team member
remove_member() {
    local name="$1"
    
    if [ -z "$name" ]; then
        print_error "Usage: $0 remove-member <name>"
        exit 1
    fi
    
    if [ ! -d "team_members/$name" ]; then
        print_error "Team member $name not found"
        exit 1
    fi
    
    print_status "Removing team member: $name"
    
    # Remove member directory
    rm -rf "team_members/$name"
    
    # Remove from members list
    if [ -f "team_members/members.txt" ]; then
        grep -v "^$name," "team_members/members.txt" > "team_members/members.txt.tmp"
        mv "team_members/members.txt.tmp" "team_members/members.txt"
    fi
    
    print_success "Team member $name removed"
}

# Function to list team members
list_members() {
    print_status "ADS599 Capstone Team Members:"
    echo ""
    
    if [ -f "team_members/members.txt" ]; then
        echo "Name                Role                Added Date"
        echo "=================================================="
        grep -v "^#" "team_members/members.txt" | while IFS=',' read -r name role date; do
            printf "%-18s %-18s %s\n" "$name" "$role" "$date"
        done
    else
        echo "No team members found."
        echo "Add members with: $0 add-member <name> <role>"
    fi
    echo ""
}

# Main script logic
case "${1:-help}" in
    start-analyst)
        start_analyst
        ;;
    start-developer)
        start_developer
        ;;
    start-researcher)
        start_researcher
        ;;
    start-team)
        start_team
        ;;
    stop-all)
        stop_all
        ;;
    status)
        show_status
        ;;
    add-member)
        add_member "$2" "$3"
        ;;
    remove-member)
        remove_member "$2"
        ;;
    list-members)
        list_members
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

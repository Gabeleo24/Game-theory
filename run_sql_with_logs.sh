#!/bin/bash
# SQL Query Runner with Automatic Logging
# Simple script to run SQL queries and automatically save logs

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== SQL Query Runner with Automatic Logging ===${NC}"
echo ""

# Check if logs directory exists
if [ ! -d "logs/sql_logs" ]; then
    echo -e "${YELLOW}Creating logs directory...${NC}"
    mkdir -p logs/sql_logs
fi

# Function to run pre-built analyses
run_analysis() {
    case $1 in
        "overview")
            echo -e "${GREEN}Running Database Overview Analysis...${NC}"
            python scripts/sql_logging/common_queries_with_logging.py overview
            ;;
        "cards")
            echo -e "${GREEN}Running Player Cards Analysis...${NC}"
            python scripts/sql_logging/common_queries_with_logging.py cards
            ;;
        "matches")
            echo -e "${GREEN}Running Match Analysis...${NC}"
            python scripts/sql_logging/common_queries_with_logging.py matches
            ;;
        "teams")
            echo -e "${GREEN}Running Team Performance Analysis...${NC}"
            python scripts/sql_logging/common_queries_with_logging.py teams
            ;;
        "all")
            echo -e "${GREEN}Running All Analyses...${NC}"
            python scripts/sql_logging/common_queries_with_logging.py all
            ;;
        *)
            echo -e "${RED}Unknown analysis type: $1${NC}"
            echo "Available analyses: overview, cards, matches, teams, all"
            return 1
            ;;
    esac
}

# Function to run custom query
run_custom_query() {
    local query="$1"
    local description="$2"
    
    if [ -z "$description" ]; then
        description="Custom SQL Query"
    fi
    
    echo -e "${GREEN}Running custom query with logging...${NC}"
    python scripts/sql_logging/run_query_with_logging.py --query "$query" --description "$description"
}

# Function to run query from file
run_query_file() {
    local file="$1"
    local description="$2"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}Error: File $file not found${NC}"
        return 1
    fi
    
    if [ -z "$description" ]; then
        description="Query from file: $file"
    fi
    
    echo -e "${GREEN}Running query from file with logging...${NC}"
    python scripts/sql_logging/run_query_with_logging.py --file "$file" --description "$description"
}

# Function to show recent logs
show_logs() {
    echo -e "${BLUE}Recent SQL logs:${NC}"
    echo ""
    ls -lt logs/sql_logs/ | head -10
    echo ""
    echo -e "${YELLOW}To view a specific log file:${NC}"
    echo "cat logs/sql_logs/[filename]"
}

# Main menu
if [ $# -eq 0 ]; then
    echo "Usage: $0 [command] [options]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  analysis [type]     - Run pre-built analysis (overview|cards|matches|teams|all)"
    echo "  query \"SQL\"         - Run custom SQL query with logging"
    echo "  file [path]         - Run SQL query from file with logging"
    echo "  logs                - Show recent log files"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 analysis cards"
    echo "  $0 query \"SELECT * FROM teams LIMIT 5\" \"Sample teams query\""
    echo "  $0 file my_query.sql \"My custom analysis\""
    echo "  $0 logs"
    exit 0
fi

# Parse command line arguments
case $1 in
    "analysis")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Analysis type required${NC}"
            echo "Available types: overview, cards, matches, teams, all"
            exit 1
        fi
        run_analysis "$2"
        ;;
    "query")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: SQL query required${NC}"
            exit 1
        fi
        run_custom_query "$2" "$3"
        ;;
    "file")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: File path required${NC}"
            exit 1
        fi
        run_query_file "$2" "$3"
        ;;
    "logs")
        show_logs
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo "Run '$0' without arguments to see usage"
        exit 1
        ;;
esac

# Show completion message
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Process completed successfully!${NC}"
    echo -e "${YELLOW}Check logs in: logs/sql_logs/${NC}"
    echo ""
    echo -e "${BLUE}Recent log files:${NC}"
    ls -t logs/sql_logs/*.sql | head -3
fi

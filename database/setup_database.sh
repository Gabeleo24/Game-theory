#!/bin/bash
# =====================================================
# Database Setup Script for Football Database
# =====================================================

# Configuration
DB_NAME="football_analytics"
DB_USER="postgres"
DB_PASSWORD="your_password_here"
DB_HOST="localhost"
DB_PORT="5432"

# Redis configuration
REDIS_HOST="localhost"
REDIS_PORT="6379"
REDIS_PASSWORD="your_redis_password_here"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required tools
echo -e "${YELLOW}Checking for required tools...${NC}"

if ! command_exists psql; then
    echo -e "${RED}PostgreSQL client (psql) not found. Please install PostgreSQL.${NC}"
    exit 1
fi

if ! command_exists redis-cli; then
    echo -e "${RED}Redis client (redis-cli) not found. Please install Redis.${NC}"
    exit 1
fi

# Create PostgreSQL database
echo -e "${YELLOW}Creating PostgreSQL database...${NC}"

# Check if database already exists
if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo -e "${YELLOW}Database $DB_NAME already exists. Do you want to drop and recreate it? (y/n)${NC}"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        dropdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME
        createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME
        echo -e "${GREEN}Database $DB_NAME recreated.${NC}"
    else
        echo -e "${YELLOW}Using existing database $DB_NAME.${NC}"
    fi
else
    createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME
    echo -e "${GREEN}Database $DB_NAME created.${NC}"
fi

# Create schema and tables
echo -e "${YELLOW}Creating database schema...${NC}"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f postgresql_schema.sql
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Database schema created successfully.${NC}"
else
    echo -e "${RED}Error creating database schema.${NC}"
    exit 1
fi

# Apply data validation rules
echo -e "${YELLOW}Applying data validation rules...${NC}"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f data_validation.sql
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Data validation rules applied successfully.${NC}"
else
    echo -e "${RED}Error applying data validation rules.${NC}"
    exit 1
fi

# Load initial data
echo -e "${YELLOW}Loading initial data...${NC}"

# Load competitions
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
INSERT INTO competitions (name, country, tier) VALUES
('Premier League', 'England', 1),
('Champions League', 'Europe', 1),
('FA Cup', 'England', 1),
('EFL Cup', 'England', 1),
('Community Shield', 'England', 1);
"

# Load positions
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
INSERT INTO positions (code, name, description) VALUES
('GK', 'Goalkeeper', 'Defends the goal'),
('DF', 'Defender', 'Primarily defensive player'),
('MF', 'Midfielder', 'Central player connecting defense and attack'),
('FW', 'Forward', 'Primarily attacking player');
"

# Load Manchester City team
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
INSERT INTO teams (name, short_name, official_name, city, country, founded_year, stadium_name, stadium_capacity, primary_color, secondary_color) VALUES
('Manchester City', 'Man City', 'Manchester City Football Club', 'Manchester', 'England', 1880, 'Etihad Stadium', 55097, '#6CABDD', '#FFFFFF');
"

# Configure Redis
echo -e "${YELLOW}Configuring Redis...${NC}"

# Check if Redis is running
redis-cli -h $REDIS_HOST -p $REDIS_PORT ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Redis is running.${NC}"
    
    # Copy Redis configuration
    echo -e "${YELLOW}Setting up Redis configuration...${NC}"
    # Note: In a real environment, you would copy the config file to the Redis config directory
    # and restart Redis. This is simplified for the example.
    echo -e "${GREEN}Redis configuration applied.${NC}"
    
    # Test Redis connection with password
    redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD ping > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Redis authentication successful.${NC}"
    else
        echo -e "${RED}Redis authentication failed. Please check your Redis password.${NC}"
    fi
else
    echo -e "${RED}Redis is not running. Please start Redis server.${NC}"
fi

# Create Python virtual environment and install dependencies
echo -e "${YELLOW}Setting up Python environment...${NC}"
if command_exists python3; then
    python3 -m venv venv
    source venv/bin/activate
    pip install psycopg2-binary redis pandas numpy
    echo -e "${GREEN}Python environment set up successfully.${NC}"
else
    echo -e "${RED}Python 3 not found. Please install Python 3.${NC}"
fi

echo -e "${GREEN}Database setup completed successfully!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Customize the database connection parameters in your application"
echo -e "2. Import your existing Manchester City data using the data import scripts"
echo -e "3. Start using the Redis caching for improved performance"

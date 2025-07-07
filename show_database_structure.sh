#!/bin/bash
# Show Database Structure and Relationships
# Quick visual overview of how tables connect

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== DATABASE REVERSE ENGINEERING OVERVIEW ===${NC}"
echo ""

echo -e "${CYAN}DATABASE STRUCTURE MAP${NC}"
echo -e "${CYAN}=====================${NC}"
echo ""

echo -e "${GREEN}ROOT TABLES (Foundation - No Dependencies)${NC}"
echo -e "├── ${YELLOW}teams${NC} (67 records) - Core team entities"
echo -e "│   ├── Referenced by: matches (home_team_id, away_team_id)"
echo -e "│   ├── Referenced by: player_statistics (team_id)"
echo -e "│   ├── Referenced by: team_statistics (team_id)"
echo -e "│   └── Referenced by: shapley_analysis (team_id)"
echo -e "│"
echo -e "└── ${YELLOW}competitions${NC} (1 record) - Competition definitions"
echo -e "    ├── Referenced by: matches (competition_id)"
echo -e "    ├── Referenced by: player_statistics (competition_id)"
echo -e "    └── Referenced by: team_statistics (competition_id)"
echo ""

echo -e "${GREEN}JUNCTION TABLES (Connect Multiple Tables)${NC}"
echo -e "├── ${YELLOW}matches${NC} (98 records) - Game records"
echo -e "│   ├── Depends on: teams (home_team_id → teams.team_id)"
echo -e "│   ├── Depends on: teams (away_team_id → teams.team_id)"
echo -e "│   ├── Depends on: competitions (competition_id → competitions.competition_id)"
echo -e "│   └── Referenced by: player_statistics (match_id)"
echo -e "│"
echo -e "├── ${YELLOW}player_statistics${NC} (8,080 records) - Player performance data"
echo -e "│   ├── Depends on: players (player_id → players.player_id)"
echo -e "│   ├── Depends on: teams (team_id → teams.team_id)"
echo -e "│   ├── Depends on: competitions (competition_id → competitions.competition_id)"
echo -e "│   └── Depends on: matches (match_id → matches.match_id)"
echo -e "│"
echo -e "└── ${YELLOW}team_statistics${NC} (0 records) - Team performance data"
echo -e "    ├── Depends on: teams (team_id → teams.team_id)"
echo -e "    └── Depends on: competitions (competition_id → competitions.competition_id)"
echo ""

echo -e "${GREEN}LEAF TABLES (Reference Others, Not Referenced)${NC}"
echo -e "└── ${YELLOW}shapley_analysis${NC} (0 records) - Advanced player analysis"
echo -e "    ├── Depends on: players (player_id → players.player_id)"
echo -e "    └── Depends on: teams (team_id → teams.team_id)"
echo ""

echo -e "${GREEN}STANDALONE TABLES (No Foreign Key Relationships)${NC}"
echo -e "├── ${YELLOW}players${NC} (3,980 records) - Individual player profiles"
echo -e "├── ${YELLOW}seasons${NC} (0 records) - Season definitions"
echo -e "└── ${YELLOW}collection_logs${NC} (0 records) - Data collection tracking"
echo ""

echo -e "${CYAN}OPERATION ORDER${NC}"
echo -e "${CYAN}===============${NC}"
echo ""

echo -e "${GREEN}INSERT ORDER (Dependencies First):${NC}"
echo -e "1. ${YELLOW}teams${NC} (ROOT - no dependencies)"
echo -e "2. ${YELLOW}competitions${NC} (ROOT - no dependencies)"
echo -e "3. ${YELLOW}players${NC} (STANDALONE - no dependencies)"
echo -e "4. ${YELLOW}matches${NC} (depends on teams + competitions)"
echo -e "5. ${YELLOW}player_statistics${NC} (depends on players + teams + competitions + matches)"
echo -e "6. ${YELLOW}team_statistics${NC} (depends on teams + competitions)"
echo -e "7. ${YELLOW}shapley_analysis${NC} (depends on players + teams)"
echo ""

echo -e "${RED}DELETE ORDER (Reverse Dependencies):${NC}"
echo -e "1. ${YELLOW}player_statistics${NC} (remove dependent data first)"
echo -e "2. ${YELLOW}team_statistics${NC} (remove dependent data)"
echo -e "3. ${YELLOW}shapley_analysis${NC} (remove dependent data)"
echo -e "4. ${YELLOW}matches${NC} (remove match records)"
echo -e "5. ${YELLOW}players${NC} (remove player records)"
echo -e "6. ${YELLOW}teams${NC} (remove root records)"
echo -e "7. ${YELLOW}competitions${NC} (remove root records)"
echo ""

echo -e "${CYAN}KEY RELATIONSHIPS${NC}"
echo -e "${CYAN}=================${NC}"
echo ""

echo -e "${GREEN}Active Data Connections:${NC}"
echo -e "• ${YELLOW}teams → matches${NC}: 67 teams connected to 98 matches"
echo -e "• ${YELLOW}players → player_statistics${NC}: 3,980 players with 8,080 stat records"
echo -e "• ${YELLOW}teams → player_statistics${NC}: All 67 teams have player statistics"
echo -e "• ${YELLOW}matches → player_statistics${NC}: Match-level player performance data"
echo ""

echo -e "${RED}Empty Tables (Ready for Data):${NC}"
echo -e "• ${YELLOW}team_statistics${NC}: Team performance metrics"
echo -e "• ${YELLOW}shapley_analysis${NC}: Advanced player value analysis"
echo -e "• ${YELLOW}seasons${NC}: Season definitions"
echo -e "• ${YELLOW}collection_logs${NC}: Data collection tracking"
echo ""

echo -e "${CYAN}QUICK COMMANDS${NC}"
echo -e "${CYAN}==============${NC}"
echo ""

echo -e "${GREEN}View complete analysis:${NC}"
echo -e "cat data/analysis/database_reverse_engineering_complete.md"
echo ""

echo -e "${GREEN}Run relationship analysis with logging:${NC}"
echo -e "./run_sql_with_logs.sh query \"SELECT tc.table_name, kcu.column_name, ccu.table_name, ccu.column_name FROM information_schema.table_constraints tc JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public' ORDER BY tc.table_name;\" \"Foreign Key Analysis\""
echo ""

echo -e "${GREEN}Check table sizes:${NC}"
echo -e "./run_sql_with_logs.sh analysis overview"
echo ""

echo -e "${BLUE}Database structure analysis complete!${NC}"
echo -e "${YELLOW}All relationships mapped and operation order determined.${NC}"

#!/usr/bin/env python3
"""
SportMonks Database Schema Explorer
Explore working endpoints and map data structure for database design
"""

import requests
import yaml
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SportMonksDatabaseExplorer:
    """Explore SportMonks API for database schema design."""
    
    def __init__(self):
        """Initialize with API configuration."""
        self.load_config()
        self.session = requests.Session()
        self.base_url = "https://api.sportmonks.com/v3/football"
        
        # Manchester City team ID (confirmed working)
        self.man_city_id = 9
        
        # Working season IDs
        self.seasons = {
            "2023-2024": 21646,
            "2022-2023": 19734,
            "2021-2022": 19686
        }
        
    def load_config(self):
        """Load SportMonks API configuration."""
        try:
            with open('config/api_keys.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            self.api_token = config.get('sportmonks', {}).get('api_key')
            
            if self.api_token:
                logger.info("✅ SportMonks API token loaded successfully")
            else:
                logger.error("❌ SportMonks API token not found")
                raise ValueError("SportMonks API token required")
                
        except FileNotFoundError:
            logger.error("❌ Config file not found: config/api_keys.yaml")
            raise
    
    def make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with error handling."""
        if params is None:
            params = {}
        
        params['api_token'] = self.api_token
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            logger.info(f"🔍 Testing: {endpoint}")
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Success: {endpoint}")
                return data
            else:
                logger.error(f"❌ Failed: {endpoint} - Status: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Exception for {endpoint}: {e}")
            return {}
    
    def analyze_data_structure(self, data: Any, path: str = "") -> Dict:
        """Analyze data structure for database schema design."""
        analysis = {
            'type': type(data).__name__,
            'fields': {},
            'sample_values': {},
            'nullable_fields': set(),
            'data_types': {}
        }
        
        if isinstance(data, dict):
            for key, value in data.items():
                field_path = f"{path}.{key}" if path else key
                analysis['fields'][key] = type(value).__name__
                analysis['data_types'][key] = self.get_sql_type(value)
                
                if value is None:
                    analysis['nullable_fields'].add(key)
                elif isinstance(value, (dict, list)) and len(str(value)) < 200:
                    analysis['sample_values'][key] = value
                elif not isinstance(value, (dict, list)):
                    analysis['sample_values'][key] = value
                    
        elif isinstance(data, list) and data:
            # Analyze first item in list
            analysis = self.analyze_data_structure(data[0], path)
            analysis['is_array'] = True
            analysis['array_length'] = len(data)
            
        return analysis
    
    def get_sql_type(self, value: Any) -> str:
        """Map Python types to SQL types."""
        if value is None:
            return "TEXT"
        elif isinstance(value, bool):
            return "BOOLEAN"
        elif isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "DECIMAL"
        elif isinstance(value, str):
            if len(value) > 255:
                return "TEXT"
            else:
                return "VARCHAR(255)"
        elif isinstance(value, dict):
            return "JSONB"
        elif isinstance(value, list):
            return "JSONB"
        else:
            return "TEXT"
    
    def explore_teams_data(self) -> Dict:
        """Explore teams data structure."""
        logger.info("🏟️ Exploring Teams Data Structure")
        
        results = {}
        
        # Basic team info
        team_data = self.make_request(f"teams/{self.man_city_id}")
        if team_data and 'data' in team_data:
            results['teams_basic'] = {
                'endpoint': f"teams/{self.man_city_id}",
                'structure': self.analyze_data_structure(team_data['data']),
                'description': 'Basic team information - core teams table'
            }
        
        # Team squad/players
        squad_data = self.make_request(f"squads/seasons/{self.seasons['2023-2024']}/teams/{self.man_city_id}")
        if squad_data and 'data' in squad_data:
            results['team_squads'] = {
                'endpoint': f"squads/seasons/{self.seasons['2023-2024']}/teams/{self.man_city_id}",
                'structure': self.analyze_data_structure(squad_data['data']),
                'description': 'Team squad data - players table with team relationships'
            }
        
        return results
    
    def explore_seasons_data(self) -> Dict:
        """Explore seasons and competitions data."""
        logger.info("🏆 Exploring Seasons Data Structure")
        
        results = {}
        
        # Seasons list
        seasons_data = self.make_request("seasons")
        if seasons_data and 'data' in seasons_data:
            results['seasons'] = {
                'endpoint': 'seasons',
                'structure': self.analyze_data_structure(seasons_data['data']),
                'description': 'Seasons data - seasons table'
            }
        
        return results
    
    def explore_fixtures_data(self) -> Dict:
        """Explore fixtures/matches data."""
        logger.info("⚽ Exploring Fixtures Data Structure")
        
        results = {}
        
        # Try different fixture endpoints
        endpoints_to_try = [
            ("fixtures", {}),
            ("fixtures", {"filters": f"teamIds:{self.man_city_id}"}),
            (f"teams/{self.man_city_id}/fixtures", {}),
        ]
        
        for endpoint, params in endpoints_to_try:
            fixtures_data = self.make_request(endpoint, params)
            if fixtures_data and 'data' in fixtures_data and fixtures_data['data']:
                results['fixtures'] = {
                    'endpoint': endpoint,
                    'params': params,
                    'structure': self.analyze_data_structure(fixtures_data['data']),
                    'description': 'Fixtures/matches data - matches table'
                }
                break
        
        return results
    
    def explore_players_data(self) -> Dict:
        """Explore individual player data."""
        logger.info("👤 Exploring Players Data Structure")
        
        results = {}
        
        # Get player ID from squad
        squad_data = self.make_request(f"squads/seasons/{self.seasons['2023-2024']}/teams/{self.man_city_id}")
        
        if squad_data and 'data' in squad_data and squad_data['data']:
            player_id = squad_data['data'][0].get('player_id')
            
            if player_id:
                # Individual player data
                player_data = self.make_request(f"players/{player_id}")
                if player_data and 'data' in player_data:
                    results['players'] = {
                        'endpoint': f"players/{player_id}",
                        'structure': self.analyze_data_structure(player_data['data']),
                        'description': 'Individual player data - players table'
                    }
        
        return results
    
    def generate_database_schema(self, exploration_results: Dict) -> str:
        """Generate SQL database schema from exploration results."""
        schema_sql = "-- SportMonks Database Schema\n"
        schema_sql += "-- Generated from API exploration\n\n"
        
        for category, endpoints in exploration_results.items():
            if category in ['timestamp', 'api_base_url', 'test_team']:
                continue

            schema_sql += f"-- {category.upper()} TABLES\n"

            if isinstance(endpoints, dict):
                for endpoint_name, endpoint_data in endpoints.items():
                    if 'structure' in endpoint_data:
                        structure = endpoint_data['structure']
                        table_name = endpoint_name.lower()

                        schema_sql += f"\nCREATE TABLE {table_name} (\n"
                        schema_sql += "    id SERIAL PRIMARY KEY,\n"

                        for field, data_type in structure.get('data_types', {}).items():
                            nullable = "NULL" if field in structure.get('nullable_fields', set()) else "NOT NULL"
                            schema_sql += f"    {field} {data_type} {nullable},\n"

                        schema_sql += "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n"
                        schema_sql += "    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n"
                        schema_sql += ");\n"

                        schema_sql += f"-- {endpoint_data.get('description', 'No description')}\n\n"
        
        return schema_sql
    
    def run_exploration(self) -> Dict:
        """Run complete database schema exploration."""
        logger.info("🚀 Starting SportMonks Database Schema Exploration")
        
        exploration_results = {
            'timestamp': datetime.now().isoformat(),
            'api_base_url': self.base_url,
            'test_team': f"Manchester City (ID: {self.man_city_id})",
            'teams': self.explore_teams_data(),
            'seasons': self.explore_seasons_data(),
            'fixtures': self.explore_fixtures_data(),
            'players': self.explore_players_data()
        }
        
        return exploration_results
    
    def save_results(self, results: Dict):
        """Save exploration results and generate schema."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_filename = f"logs/sportmonks_database_exploration_{timestamp}.json"
        with open(json_filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"✅ Results saved to: {json_filename}")
        
        # Generate and save SQL schema
        schema_sql = self.generate_database_schema(results)
        sql_filename = f"logs/sportmonks_database_schema_{timestamp}.sql"
        with open(sql_filename, 'w') as f:
            f.write(schema_sql)
        logger.info(f"✅ Database schema saved to: {sql_filename}")
        
        return json_filename, sql_filename

def main():
    """Main execution function."""
    explorer = SportMonksDatabaseExplorer()
    
    # Run exploration
    results = explorer.run_exploration()
    
    # Save results
    json_file, sql_file = explorer.save_results(results)
    
    # Print summary
    print("\n" + "="*80)
    print("🗄️ SPORTMONKS DATABASE SCHEMA EXPLORATION SUMMARY")
    print("="*80)
    
    for category, endpoints in results.items():
        if category not in ['timestamp', 'api_base_url', 'test_team']:
            print(f"\n📂 {category.upper()}:")
            for endpoint_name, endpoint_data in endpoints.items():
                print(f"  ✅ {endpoint_name}: {endpoint_data.get('description', 'No description')}")
    
    print(f"\n📄 Results saved to: {json_file}")
    print(f"🗄️ Database schema saved to: {sql_file}")
    print("="*80)

if __name__ == "__main__":
    main()

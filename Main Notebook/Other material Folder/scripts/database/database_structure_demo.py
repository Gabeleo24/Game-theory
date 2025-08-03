#!/usr/bin/env python3
"""
Database Structure Demonstration
Shows the structure of our soccer intelligence databases using available data
"""

import sqlite3
import pandas as pd
import os
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseStructureDemo:
    """Demonstrate database structures from available SQLite databases."""
    
    def __init__(self):
        """Initialize with available databases."""
        self.databases = self.find_available_databases()
        
    def find_available_databases(self) -> Dict[str, str]:
        """Find all available SQLite databases."""
        databases = {}
        
        # Check for various database files
        db_paths = [
            "data/final_advanced_stats/manchester_city_final_advanced_2023_24.db",
            "data/working_sportmonks_database/manchester_city_working_2023_24.db",
            "data/real_working_advanced_stats/manchester_city_real_working_2023_24.db"
        ]
        
        for db_path in db_paths:
            if os.path.exists(db_path):
                db_name = os.path.basename(db_path).replace('.db', '')
                databases[db_name] = db_path
                
        logger.info(f"✅ Found {len(databases)} available databases")
        return databases
    
    def show_database_overview(self):
        """Show overview of all available databases."""
        print("\n" + "="*100)
        print("🗄️ SOCCER INTELLIGENCE DATABASE STRUCTURE OVERVIEW")
        print("="*100)
        
        print(f"\n📊 AVAILABLE DATABASES ({len(self.databases)}):")
        
        for db_name, db_path in self.databases.items():
            print(f"\n🗄️ {db_name.upper()}:")
            print(f"   📍 Location: {db_path}")
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get table count
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                print(f"   📋 Tables: {len(tables)}")
                
                # Get total records
                total_records = 0
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    total_records += count
                
                print(f"   📊 Total Records: {total_records:,}")
                
                # Show table names
                table_names = [table[0] for table in tables]
                print(f"   📝 Table Names: {', '.join(table_names)}")
                
                conn.close()
                
            except Exception as e:
                print(f"   ❌ Error accessing database: {e}")
    
    def show_detailed_table_structure(self, db_name: str):
        """Show detailed structure for a specific database."""
        if db_name not in self.databases:
            print(f"❌ Database '{db_name}' not found")
            return
        
        db_path = self.databases[db_name]
        
        print(f"\n" + "="*100)
        print(f"📋 DETAILED TABLE STRUCTURE: {db_name.upper()}")
        print("="*100)
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]
            
            for table_name in tables:
                print(f"\n🗄️ TABLE: {table_name.upper()}")
                print("-" * 80)
                
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Get record count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                record_count = cursor.fetchone()[0]
                
                print(f"📊 Records: {record_count:,}")
                print(f"📝 Columns ({len(columns)}):")
                
                for col in columns:
                    col_id, name, data_type, not_null, default_val, pk = col
                    pk_indicator = " 🔑 PRIMARY KEY" if pk else ""
                    null_indicator = " NOT NULL" if not_null else " NULL"
                    default_indicator = f" DEFAULT {default_val}" if default_val else ""
                    
                    print(f"   • {name:<25} {data_type:<15}{null_indicator:<10}{pk_indicator}{default_indicator}")
                
                # Show sample data
                if record_count > 0:
                    print(f"\n📋 SAMPLE DATA (first 3 records):")
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    sample_data = cursor.fetchall()
                    
                    if sample_data:
                        # Get column names
                        column_names = [description[0] for description in cursor.description]
                        
                        # Create DataFrame for better display
                        df = pd.DataFrame(sample_data, columns=column_names)
                        
                        # Truncate long text for display
                        for col in df.columns:
                            if df[col].dtype == 'object':
                                df[col] = df[col].astype(str).str[:30]
                        
                        print(df.to_string(index=False))
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error accessing database: {e}")
    
    def show_postgresql_schema_design(self):
        """Show the PostgreSQL schema design that was created."""
        print("\n" + "="*100)
        print("🏗️ POSTGRESQL RELATIONAL DATABASE SCHEMA DESIGN")
        print("="*100)
        
        print(f"\n📊 COMPREHENSIVE RELATIONAL SCHEMA:")
        
        schema_tables = {
            "🏷️ REFERENCE TABLES": {
                "seasons": ["id", "season_name", "start_date", "end_date", "is_current", "sportmonks_id", "api_football_id"],
                "competitions": ["id", "name", "country", "type", "level", "sportmonks_id", "api_football_id", "logo_url"],
                "venues": ["id", "name", "city", "country", "capacity", "surface", "latitude", "longitude", "image_url"]
            },
            "👥 ENTITY TABLES": {
                "teams": ["id", "name", "short_name", "code", "country", "founded_year", "venue_id", "logo_url"],
                "players": ["id", "first_name", "last_name", "display_name", "date_of_birth", "nationality", "height", "weight", "position"]
            },
            "🔗 RELATIONSHIP TABLES": {
                "team_seasons": ["id", "team_id", "season_id", "competition_id", "position", "points", "matches_played"],
                "squad_members": ["id", "player_id", "team_id", "season_id", "jersey_number", "position", "is_captain"],
                "fixtures": ["id", "season_id", "competition_id", "home_team_id", "away_team_id", "venue_id", "match_date", "status"]
            },
            "📊 STATISTICS TABLES": {
                "team_match_statistics": ["id", "fixture_id", "team_id", "possession_percentage", "shots_total", "passes_total", "pass_accuracy"],
                "player_match_statistics": ["id", "fixture_id", "player_id", "team_id", "minutes_played", "goals", "assists", "rating"]
            },
            "⚽ MATCH DATA TABLES": {
                "lineups": ["id", "fixture_id", "player_id", "team_id", "position", "is_starter", "substituted_in_minute"],
                "match_events": ["id", "fixture_id", "team_id", "player_id", "minute", "event_type", "event_detail"]
            },
            "💼 BUSINESS TABLES": {
                "player_contracts": ["id", "player_id", "team_id", "start_date", "end_date", "salary_annual", "contract_type"],
                "player_transfers": ["id", "player_id", "from_team_id", "to_team_id", "transfer_date", "transfer_fee", "transfer_type"]
            }
        }
        
        for category, tables in schema_tables.items():
            print(f"\n{category}:")
            for table_name, columns in tables.items():
                print(f"   🗄️ {table_name}:")
                for col in columns[:5]:  # Show first 5 columns
                    print(f"      • {col}")
                if len(columns) > 5:
                    print(f"      • ... and {len(columns) - 5} more columns")
        
        print(f"\n🔗 KEY RELATIONSHIPS:")
        relationships = [
            "teams.venue_id → venues.id",
            "squad_members.player_id → players.id",
            "squad_members.team_id → teams.id",
            "fixtures.home_team_id → teams.id",
            "fixtures.away_team_id → teams.id",
            "player_match_statistics.fixture_id → fixtures.id",
            "player_match_statistics.player_id → players.id",
            "team_match_statistics.fixture_id → fixtures.id",
            "lineups.fixture_id → fixtures.id",
            "match_events.fixture_id → fixtures.id"
        ]
        
        for rel in relationships:
            print(f"   • {rel}")
        
        print(f"\n🎯 SCHEMA BENEFITS:")
        benefits = [
            "✅ Normalized structure eliminates data redundancy",
            "✅ Foreign key constraints ensure data integrity",
            "✅ Scalable design supports multiple seasons and competitions",
            "✅ Comprehensive statistics tracking at match and player level",
            "✅ Business intelligence support with contracts and transfers",
            "✅ Optimized for analytics and reporting queries",
            "✅ Dual API integration (SportAPI + SportMonks) support"
        ]
        
        for benefit in benefits:
            print(f"   {benefit}")
    
    def show_data_flow_architecture(self):
        """Show the data flow architecture."""
        print("\n" + "="*100)
        print("🔄 DATA FLOW ARCHITECTURE")
        print("="*100)
        
        print(f"\n📊 DATA COLLECTION PIPELINE:")
        
        pipeline_steps = [
            "1. 🌐 API Data Sources",
            "   • SportAPI (API-Football): Teams, players, fixtures, basic statistics",
            "   • SportMonks: Advanced statistics, detailed performance metrics",
            "",
            "2. 🔄 Data Processing Layer",
            "   • Rate limiting and error handling",
            "   • Data validation and cleaning",
            "   • Duplicate detection and merging",
            "   • Format standardization",
            "",
            "3. 🗄️ Storage Layer",
            "   • PostgreSQL: Relational database for structured data",
            "   • SQLite: Local development and testing",
            "   • Redis: Caching for API responses",
            "",
            "4. 📊 Analytics Layer",
            "   • Position-normalized performance algorithms",
            "   • Team contribution analysis",
            "   • Comparative league benchmarking",
            "   • Machine learning model training",
            "",
            "5. 🎯 Application Layer",
            "   • Team manager tools",
            "   • Player agent analytics",
            "   • Contract optimization",
            "   • Interactive dashboards"
        ]
        
        for step in pipeline_steps:
            print(step)
        
        print(f"\n🔗 INTEGRATION POINTS:")
        integrations = [
            "📡 Real-time API data collection with rate limiting",
            "🔄 Automated data synchronization between sources",
            "📊 Statistical calculation and aggregation pipelines",
            "🎯 Machine learning model training and inference",
            "📋 Business intelligence report generation",
            "🌐 Web interface for stakeholder access"
        ]
        
        for integration in integrations:
            print(f"   {integration}")
    
    def interactive_explorer(self):
        """Interactive database structure explorer."""
        while True:
            print("\n" + "="*80)
            print("🔍 DATABASE STRUCTURE EXPLORER")
            print("="*80)
            print("1. 📊 Database Overview")
            print("2. 📋 Detailed Table Structure")
            print("3. 🏗️ PostgreSQL Schema Design")
            print("4. 🔄 Data Flow Architecture")
            print("5. 🚪 Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                self.show_database_overview()
            elif choice == '2':
                if self.databases:
                    print(f"\nAvailable databases:")
                    for i, db_name in enumerate(self.databases.keys(), 1):
                        print(f"  {i}. {db_name}")
                    
                    try:
                        db_choice = int(input(f"\nSelect database (1-{len(self.databases)}): ")) - 1
                        db_name = list(self.databases.keys())[db_choice]
                        self.show_detailed_table_structure(db_name)
                    except (ValueError, IndexError):
                        print("❌ Invalid choice")
                else:
                    print("❌ No databases found")
            elif choice == '3':
                self.show_postgresql_schema_design()
            elif choice == '4':
                self.show_data_flow_architecture()
            elif choice == '5':
                print("\n🎉 Database structure exploration completed!")
                break
            else:
                print("❌ Invalid choice. Please select 1-5.")
            
            input("\nPress Enter to continue...")

def main():
    """Main execution function."""
    demo = DatabaseStructureDemo()
    
    if len(demo.databases) == 0:
        print("❌ No databases found. Please run data collection scripts first.")
        return
    
    # Show overview by default
    demo.show_database_overview()
    
    # Start interactive explorer
    demo.interactive_explorer()

if __name__ == "__main__":
    main()

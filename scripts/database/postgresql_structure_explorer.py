#!/usr/bin/env python3
"""
PostgreSQL Database Structure Explorer
Comprehensive tool to visualize and explore the database schema, relationships, and data
"""

import psycopg2
import psycopg2.extras
import pandas as pd
import yaml
import sys
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PostgreSQLStructureExplorer:
    """Comprehensive PostgreSQL database structure explorer."""
    
    def __init__(self):
        """Initialize database connection."""
        self.load_config()
        self.setup_connection()
    
    def load_config(self):
        """Load database configuration."""
        try:
            with open('config/api_keys.yaml', 'r') as f:
                config = yaml.safe_load(f)
            self.db_config = config['database']
            logger.info("✅ Configuration loaded")
        except FileNotFoundError:
            logger.error("❌ Config file not found")
            raise
    
    def setup_connection(self):
        """Setup PostgreSQL connection."""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['name'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            logger.info("✅ PostgreSQL connection established")
        except psycopg2.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def show_database_overview(self):
        """Show comprehensive database overview."""
        print("\n" + "="*100)
        print("🗄️ POSTGRESQL DATABASE STRUCTURE OVERVIEW")
        print("="*100)
        
        # Database information
        self.cursor.execute("""
            SELECT 
                current_database() as database_name,
                current_user as current_user,
                version() as postgresql_version
        """)
        db_info = self.cursor.fetchone()
        
        print(f"\n📊 DATABASE INFORMATION:")
        print(f"   • Database: {db_info['database_name']}")
        print(f"   • User: {db_info['current_user']}")
        print(f"   • PostgreSQL Version: {db_info['postgresql_version'].split(',')[0]}")
        
        # Get all tables
        self.cursor.execute("""
            SELECT 
                table_name,
                table_type
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = self.cursor.fetchall()
        
        print(f"\n📋 TABLES IN DATABASE ({len(tables)} total):")
        for table in tables:
            print(f"   • {table['table_name']} ({table['table_type']})")
    
    def show_table_schemas(self):
        """Show detailed schema for each table."""
        print("\n" + "="*100)
        print("📋 DETAILED TABLE SCHEMAS")
        print("="*100)
        
        # Get all user tables
        self.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row['table_name'] for row in self.cursor.fetchall()]
        
        for table_name in tables:
            print(f"\n🗄️ TABLE: {table_name.upper()}")
            print("-" * 80)
            
            # Get column information
            self.cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = %s 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """, (table_name,))
            
            columns = self.cursor.fetchall()
            
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                length = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                
                print(f"   • {col['column_name']:<25} {col['data_type']}{length:<15} {nullable:<10}{default}")
    
    def show_foreign_key_relationships(self):
        """Show foreign key relationships between tables."""
        print("\n" + "="*100)
        print("🔗 FOREIGN KEY RELATIONSHIPS")
        print("="*100)
        
        self.cursor.execute("""
            SELECT 
                tc.table_name as source_table,
                kcu.column_name as source_column,
                ccu.table_name as target_table,
                ccu.column_name as target_column,
                tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name
        """)
        
        relationships = self.cursor.fetchall()
        
        if relationships:
            print(f"\n📊 FOREIGN KEY RELATIONSHIPS ({len(relationships)} total):")
            for rel in relationships:
                print(f"   • {rel['source_table']}.{rel['source_column']} → {rel['target_table']}.{rel['target_column']}")
        else:
            print("\n❌ No foreign key relationships found")
    
    def show_table_sizes_and_counts(self):
        """Show table sizes and record counts."""
        print("\n" + "="*100)
        print("📊 TABLE SIZES AND RECORD COUNTS")
        print("="*100)
        
        # Get all user tables
        self.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row['table_name'] for row in self.cursor.fetchall()]
        
        table_stats = []
        
        for table_name in tables:
            # Get record count
            self.cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = self.cursor.fetchone()['count']
            
            # Get table size
            self.cursor.execute("""
                SELECT 
                    pg_size_pretty(pg_total_relation_size(%s)) as size,
                    pg_total_relation_size(%s) as size_bytes
            """, (table_name, table_name))
            size_info = self.cursor.fetchone()
            
            table_stats.append({
                'table': table_name,
                'records': count,
                'size': size_info['size'],
                'size_bytes': size_info['size_bytes']
            })
        
        # Sort by record count
        table_stats.sort(key=lambda x: x['records'], reverse=True)
        
        print(f"\n📋 TABLE STATISTICS:")
        print(f"{'Table Name':<25} {'Records':<10} {'Size':<10}")
        print("-" * 50)
        
        for stat in table_stats:
            print(f"{stat['table']:<25} {stat['records']:<10} {stat['size']:<10}")
        
        total_records = sum(stat['records'] for stat in table_stats)
        print(f"\n📊 TOTAL RECORDS ACROSS ALL TABLES: {total_records:,}")
    
    def show_sample_data(self, limit: int = 3):
        """Show sample data from each table."""
        print("\n" + "="*100)
        print(f"📋 SAMPLE DATA (First {limit} records from each table)")
        print("="*100)
        
        # Get all user tables with data
        self.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row['table_name'] for row in self.cursor.fetchall()]
        
        for table_name in tables:
            # Check if table has data
            self.cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = self.cursor.fetchone()['count']
            
            if count > 0:
                print(f"\n🗄️ {table_name.upper()} (showing {min(limit, count)} of {count} records):")
                print("-" * 80)
                
                # Get sample data
                self.cursor.execute(f"SELECT * FROM {table_name} LIMIT %s", (limit,))
                rows = self.cursor.fetchall()
                
                if rows:
                    # Convert to DataFrame for better display
                    df = pd.DataFrame([dict(row) for row in rows])
                    
                    # Truncate long text fields for display
                    for col in df.columns:
                        if df[col].dtype == 'object':
                            df[col] = df[col].astype(str).str[:50]
                    
                    print(df.to_string(index=False))
                else:
                    print("   No data found")
            else:
                print(f"\n🗄️ {table_name.upper()}: Empty table")
    
    def show_indexes_and_constraints(self):
        """Show indexes and constraints."""
        print("\n" + "="*100)
        print("🔍 INDEXES AND CONSTRAINTS")
        print("="*100)
        
        # Show indexes
        self.cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes 
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)
        indexes = self.cursor.fetchall()
        
        if indexes:
            print(f"\n📊 INDEXES ({len(indexes)} total):")
            current_table = None
            for idx in indexes:
                if idx['tablename'] != current_table:
                    current_table = idx['tablename']
                    print(f"\n   🗄️ {current_table}:")
                print(f"      • {idx['indexname']}")
        
        # Show constraints
        self.cursor.execute("""
            SELECT 
                table_name,
                constraint_name,
                constraint_type
            FROM information_schema.table_constraints
            WHERE table_schema = 'public'
            ORDER BY table_name, constraint_type
        """)
        constraints = self.cursor.fetchall()
        
        if constraints:
            print(f"\n🔒 CONSTRAINTS ({len(constraints)} total):")
            current_table = None
            for const in constraints:
                if const['table_name'] != current_table:
                    current_table = const['table_name']
                    print(f"\n   🗄️ {current_table}:")
                print(f"      • {const['constraint_name']} ({const['constraint_type']})")
    
    def generate_erd_description(self):
        """Generate Entity Relationship Diagram description."""
        print("\n" + "="*100)
        print("🎯 ENTITY RELATIONSHIP DIAGRAM (ERD) DESCRIPTION")
        print("="*100)
        
        print(f"\n📊 DATABASE RELATIONSHIP STRUCTURE:")
        
        # Core entities
        print(f"\n🏗️ CORE REFERENCE ENTITIES:")
        print(f"   • seasons ← (referenced by multiple tables)")
        print(f"   • competitions ← (referenced by fixtures, team_seasons)")
        print(f"   • venues ← (referenced by teams, fixtures)")
        print(f"   • teams ← (referenced by squad_members, fixtures)")
        print(f"   • players ← (referenced by squad_members, lineups, statistics)")
        
        # Relationship entities
        print(f"\n🔗 RELATIONSHIP ENTITIES:")
        print(f"   • team_seasons (teams ↔ seasons ↔ competitions)")
        print(f"   • squad_members (players ↔ teams ↔ seasons)")
        print(f"   • fixtures (teams ↔ competitions ↔ seasons ↔ venues)")
        
        # Transaction entities
        print(f"\n📊 TRANSACTION/EVENT ENTITIES:")
        print(f"   • lineups (fixtures ↔ players ↔ teams)")
        print(f"   • match_events (fixtures ↔ players ↔ teams)")
        print(f"   • team_match_statistics (fixtures ↔ teams)")
        print(f"   • player_match_statistics (fixtures ↔ players ↔ teams)")
        
        # Additional entities
        print(f"\n💼 ADDITIONAL ENTITIES:")
        print(f"   • player_contracts (players ↔ teams)")
        print(f"   • player_transfers (players ↔ teams)")
        
        print(f"\n🎯 KEY RELATIONSHIPS:")
        print(f"   • One season has many fixtures")
        print(f"   • One fixture involves two teams (home/away)")
        print(f"   • One fixture has many player statistics")
        print(f"   • One team has many squad members per season")
        print(f"   • One player can have statistics across multiple fixtures")
    
    def interactive_explorer(self):
        """Interactive database exploration menu."""
        while True:
            print("\n" + "="*80)
            print("🔍 POSTGRESQL DATABASE STRUCTURE EXPLORER")
            print("="*80)
            print("1. 📊 Database Overview")
            print("2. 📋 Table Schemas")
            print("3. 🔗 Foreign Key Relationships")
            print("4. 📊 Table Sizes & Record Counts")
            print("5. 📋 Sample Data")
            print("6. 🔍 Indexes & Constraints")
            print("7. 🎯 Entity Relationship Diagram")
            print("8. 🔍 Custom SQL Query")
            print("9. 🚪 Exit")
            
            choice = input("\nSelect option (1-9): ").strip()
            
            if choice == '1':
                self.show_database_overview()
            elif choice == '2':
                self.show_table_schemas()
            elif choice == '3':
                self.show_foreign_key_relationships()
            elif choice == '4':
                self.show_table_sizes_and_counts()
            elif choice == '5':
                self.show_sample_data()
            elif choice == '6':
                self.show_indexes_and_constraints()
            elif choice == '7':
                self.generate_erd_description()
            elif choice == '8':
                self.custom_sql_query()
            elif choice == '9':
                print("\n🎉 Database exploration completed!")
                break
            else:
                print("❌ Invalid choice. Please select 1-9.")
            
            input("\nPress Enter to continue...")
    
    def custom_sql_query(self):
        """Execute custom SQL query."""
        print("\n" + "="*60)
        print("🔍 CUSTOM SQL QUERY EXECUTOR")
        print("="*60)
        print("Enter your SQL query (or 'exit' to return):")
        
        while True:
            query = input("\nSQL> ").strip()
            
            if query.lower() == 'exit':
                break
            
            if query:
                try:
                    self.cursor.execute(query)
                    
                    if query.lower().startswith('select'):
                        results = self.cursor.fetchall()
                        if results:
                            df = pd.DataFrame([dict(row) for row in results])
                            print(df.to_string(index=False))
                            print(f"\n📊 {len(results)} rows returned")
                        else:
                            print("No results found.")
                    else:
                        print("✅ Query executed successfully")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
    
    def close_connection(self):
        """Close database connection."""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()
        logger.info("🔒 Database connection closed")

def main():
    """Main execution function."""
    explorer = PostgreSQLStructureExplorer()
    
    try:
        if len(sys.argv) > 1:
            option = sys.argv[1]
            if option == 'overview':
                explorer.show_database_overview()
            elif option == 'schemas':
                explorer.show_table_schemas()
            elif option == 'relationships':
                explorer.show_foreign_key_relationships()
            elif option == 'sizes':
                explorer.show_table_sizes_and_counts()
            elif option == 'sample':
                explorer.show_sample_data()
            elif option == 'erd':
                explorer.generate_erd_description()
            else:
                print("Available options: overview, schemas, relationships, sizes, sample, erd")
        else:
            explorer.interactive_explorer()
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        explorer.close_connection()

if __name__ == "__main__":
    main()

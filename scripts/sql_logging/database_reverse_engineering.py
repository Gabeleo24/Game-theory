#!/usr/bin/env python3
"""
Database Reverse Engineering Tool
Analyzes database structure, relationships, and connection order.
Shows how tables connect and the proper order for operations.
"""

import psycopg2
import json
from datetime import datetime
from pathlib import Path
from sql_logger import SQLLogger

class DatabaseReverseEngineer:
    """Reverse engineer database structure and relationships."""
    
    def __init__(self, log_dir: str = "logs/sql_logs"):
        """Initialize the reverse engineer."""
        self.logger = SQLLogger(log_dir)
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'soccer_intelligence',
            'user': 'soccerapp',
            'password': 'soccerpass123'
        }
        
        self.schema_info = {
            'tables': {},
            'relationships': [],
            'foreign_keys': [],
            'indexes': [],
            'constraints': []
        }
    
    def analyze_database_structure(self):
        """Complete database structure analysis with logging."""
        self.logger.log_process_start("Database Reverse Engineering", "Complete structure and relationship analysis")
        
        # 1. Get all tables and their columns
        self.get_table_structures()
        
        # 2. Get foreign key relationships
        self.get_foreign_key_relationships()
        
        # 3. Get indexes and constraints
        self.get_indexes_and_constraints()
        
        # 4. Analyze data relationships
        self.analyze_data_relationships()
        
        # 5. Determine operation order
        self.determine_operation_order()
        
        # 6. Create visual relationship map
        self.create_relationship_map()
        
        self.logger.log_process_end("Database Reverse Engineering", True)
    
    def get_table_structures(self):
        """Get detailed table structures."""
        # Get all tables
        tables_result = self.logger.execute_and_log("""
            SELECT 
                table_name,
                table_type,
                table_schema
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """, "Database Tables Overview")
        
        # Get detailed column information for each table
        for table in tables_result:
            table_name = table['table_name']
            
            columns_result = self.logger.execute_and_log(f"""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale,
                    ordinal_position
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = '{table_name}'
                ORDER BY ordinal_position;
            """, f"Table Structure: {table_name}")
            
            self.schema_info['tables'][table_name] = {
                'columns': columns_result,
                'row_count': 0,
                'relationships': []
            }
        
        # Get row counts for each table
        for table_name in self.schema_info['tables'].keys():
            count_result = self.logger.execute_and_log(f"""
                SELECT COUNT(*) as row_count FROM {table_name};
            """, f"Row Count: {table_name}")
            
            if count_result:
                self.schema_info['tables'][table_name]['row_count'] = count_result[0]['row_count']
    
    def get_foreign_key_relationships(self):
        """Get foreign key relationships between tables."""
        fk_result = self.logger.execute_and_log("""
            SELECT 
                tc.table_name as source_table,
                kcu.column_name as source_column,
                ccu.table_name as target_table,
                ccu.column_name as target_column,
                tc.constraint_name,
                tc.constraint_type
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name;
        """, "Foreign Key Relationships")
        
        self.schema_info['foreign_keys'] = fk_result
        
        # Build relationships list
        for fk in fk_result:
            relationship = {
                'from_table': fk['source_table'],
                'from_column': fk['source_column'],
                'to_table': fk['target_table'],
                'to_column': fk['target_column'],
                'constraint_name': fk['constraint_name']
            }
            self.schema_info['relationships'].append(relationship)
    
    def get_indexes_and_constraints(self):
        """Get indexes and constraints information."""
        # Get all constraints
        constraints_result = self.logger.execute_and_log("""
            SELECT 
                tc.table_name,
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name
            FROM information_schema.table_constraints tc
            LEFT JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_schema = 'public'
            ORDER BY tc.table_name, tc.constraint_type;
        """, "Table Constraints")
        
        self.schema_info['constraints'] = constraints_result
        
        # Get indexes
        indexes_result = self.logger.execute_and_log("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes 
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname;
        """, "Table Indexes")
        
        self.schema_info['indexes'] = indexes_result
    
    def analyze_data_relationships(self):
        """Analyze actual data relationships and connections."""
        # Check which foreign keys have actual data connections
        for relationship in self.schema_info['relationships']:
            from_table = relationship['from_table']
            from_column = relationship['from_column']
            to_table = relationship['to_table']
            to_column = relationship['to_column']
            
            # Count actual connections
            connection_result = self.logger.execute_and_log(f"""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT f.{from_column}) as unique_foreign_keys,
                    COUNT(DISTINCT t.{to_column}) as unique_primary_keys,
                    COUNT(CASE WHEN t.{to_column} IS NOT NULL THEN 1 END) as connected_records
                FROM {from_table} f
                LEFT JOIN {to_table} t ON f.{from_column} = t.{to_column};
            """, f"Data Connection Analysis: {from_table} -> {to_table}")
            
            if connection_result:
                relationship['data_stats'] = connection_result[0]
    
    def determine_operation_order(self):
        """Determine the proper order for database operations."""
        # Create dependency graph
        dependencies = {}
        
        for table_name in self.schema_info['tables'].keys():
            dependencies[table_name] = {
                'depends_on': [],
                'depended_by': [],
                'level': 0
            }
        
        # Build dependency relationships
        for relationship in self.schema_info['relationships']:
            from_table = relationship['from_table']
            to_table = relationship['to_table']
            
            dependencies[from_table]['depends_on'].append(to_table)
            dependencies[to_table]['depended_by'].append(from_table)
        
        # Calculate dependency levels (topological sort)
        levels = {}
        processed = set()
        
        def calculate_level(table):
            if table in processed:
                return levels.get(table, 0)
            
            processed.add(table)
            max_dependency_level = 0
            
            for dependency in dependencies[table]['depends_on']:
                dep_level = calculate_level(dependency)
                max_dependency_level = max(max_dependency_level, dep_level + 1)
            
            levels[table] = max_dependency_level
            dependencies[table]['level'] = max_dependency_level
            return max_dependency_level
        
        for table in dependencies.keys():
            calculate_level(table)
        
        self.schema_info['operation_order'] = dependencies
        
        # Create ordered lists
        ordered_tables = sorted(dependencies.items(), key=lambda x: x[1]['level'])
        
        self.schema_info['insert_order'] = [table for table, info in ordered_tables]
        self.schema_info['delete_order'] = [table for table, info in reversed(ordered_tables)]
    
    def create_relationship_map(self):
        """Create a visual representation of table relationships."""
        relationship_map = {
            'database_name': 'soccer_intelligence',
            'analysis_timestamp': datetime.now().isoformat(),
            'tables_summary': {},
            'relationship_chains': [],
            'operation_orders': {
                'insert_order': self.schema_info['insert_order'],
                'delete_order': self.schema_info['delete_order']
            }
        }
        
        # Summarize each table
        for table_name, table_info in self.schema_info['tables'].items():
            relationship_map['tables_summary'][table_name] = {
                'row_count': table_info['row_count'],
                'column_count': len(table_info['columns']),
                'primary_keys': [col['column_name'] for col in table_info['columns'] 
                               if col['column_name'].endswith('_id') or col['column_name'] == 'id'],
                'foreign_keys': [rel['from_column'] for rel in self.schema_info['relationships'] 
                               if rel['from_table'] == table_name],
                'referenced_by': [rel['from_table'] for rel in self.schema_info['relationships'] 
                                if rel['to_table'] == table_name]
            }
        
        # Create relationship chains
        for relationship in self.schema_info['relationships']:
            chain = {
                'connection': f"{relationship['from_table']}.{relationship['from_column']} -> {relationship['to_table']}.{relationship['to_column']}",
                'constraint': relationship['constraint_name'],
                'data_stats': relationship.get('data_stats', {})
            }
            relationship_map['relationship_chains'].append(chain)
        
        # Save to file
        map_file = Path("data/analysis/database_relationship_map.json")
        with open(map_file, 'w', encoding='utf-8') as f:
            json.dump(relationship_map, f, indent=2, default=str)
        
        self.logger.logger.info(f"Relationship map saved to: {map_file}")
        
        return relationship_map
    
    def generate_visual_diagram(self):
        """Generate a visual diagram of database relationships."""
        diagram_result = self.logger.execute_and_log("""
            -- Database Relationship Visual Map
            SELECT 
                'DATABASE STRUCTURE OVERVIEW' as section,
                '==============================' as separator;
            
            -- Table summary with relationships
            SELECT 
                t.table_name,
                (SELECT COUNT(*) FROM information_schema.columns 
                 WHERE table_name = t.table_name AND table_schema = 'public') as columns,
                COALESCE(fk_out.outgoing_fks, 0) as outgoing_foreign_keys,
                COALESCE(fk_in.incoming_fks, 0) as incoming_foreign_keys,
                CASE 
                    WHEN COALESCE(fk_out.outgoing_fks, 0) = 0 AND COALESCE(fk_in.incoming_fks, 0) > 0 THEN 'ROOT TABLE'
                    WHEN COALESCE(fk_out.outgoing_fks, 0) > 0 AND COALESCE(fk_in.incoming_fks, 0) = 0 THEN 'LEAF TABLE'
                    WHEN COALESCE(fk_out.outgoing_fks, 0) > 0 AND COALESCE(fk_in.incoming_fks, 0) > 0 THEN 'JUNCTION TABLE'
                    ELSE 'STANDALONE TABLE'
                END as table_type
            FROM information_schema.tables t
            LEFT JOIN (
                SELECT 
                    tc.table_name,
                    COUNT(*) as outgoing_fks
                FROM information_schema.table_constraints tc
                WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
                GROUP BY tc.table_name
            ) fk_out ON t.table_name = fk_out.table_name
            LEFT JOIN (
                SELECT 
                    ccu.table_name,
                    COUNT(*) as incoming_fks
                FROM information_schema.table_constraints tc
                JOIN information_schema.constraint_column_usage ccu 
                    ON tc.constraint_name = ccu.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
                GROUP BY ccu.table_name
            ) fk_in ON t.table_name = fk_in.table_name
            WHERE t.table_schema = 'public'
            ORDER BY 
                CASE 
                    WHEN COALESCE(fk_out.outgoing_fks, 0) = 0 AND COALESCE(fk_in.incoming_fks, 0) > 0 THEN 1
                    WHEN COALESCE(fk_out.outgoing_fks, 0) > 0 AND COALESCE(fk_in.incoming_fks, 0) > 0 THEN 2
                    WHEN COALESCE(fk_out.outgoing_fks, 0) > 0 AND COALESCE(fk_in.incoming_fks, 0) = 0 THEN 3
                    ELSE 4
                END,
                t.table_name;
        """, "Database Structure Overview with Table Types")
        
        return diagram_result

def main():
    """Main function to run database reverse engineering."""
    print("Starting Database Reverse Engineering Analysis...")
    print("=" * 60)
    
    engineer = DatabaseReverseEngineer()
    
    try:
        # Run complete analysis
        engineer.analyze_database_structure()
        
        # Generate visual diagram
        diagram = engineer.generate_visual_diagram()
        
        # Create relationship map
        relationship_map = engineer.create_relationship_map()
        
        print("\nReverse Engineering Analysis Completed!")
        print("=" * 60)
        print("Files Generated:")
        print("• Database relationship map: data/analysis/database_relationship_map.json")
        print("• Complete analysis logs: logs/sql_logs/")
        print("\nTable Operation Order:")
        print("• Insert Order:", " -> ".join(engineer.schema_info['insert_order']))
        print("• Delete Order:", " -> ".join(engineer.schema_info['delete_order']))
        
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    main()

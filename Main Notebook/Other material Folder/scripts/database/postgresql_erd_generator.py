#!/usr/bin/env python3
"""
PostgreSQL Entity Relationship Diagram Generator
Creates visual ERD diagrams and relationship maps for the soccer intelligence database
"""

import psycopg2
import psycopg2.extras
import yaml
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import networkx as nx
import pandas as pd
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PostgreSQLERDGenerator:
    """Generate Entity Relationship Diagrams for PostgreSQL database."""
    
    def __init__(self):
        """Initialize ERD generator."""
        self.load_config()
        self.setup_connection()
        self.tables_info = {}
        self.relationships = []
    
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
    
    def extract_database_schema(self):
        """Extract complete database schema information."""
        logger.info("📊 Extracting database schema...")
        
        # Get all tables
        self.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row['table_name'] for row in self.cursor.fetchall()]
        
        # Get detailed information for each table
        for table_name in tables:
            # Get columns
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
            
            # Get primary keys
            self.cursor.execute("""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = %s 
                AND tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_schema = 'public'
            """, (table_name,))
            primary_keys = [row['column_name'] for row in self.cursor.fetchall()]
            
            # Get record count
            self.cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            record_count = self.cursor.fetchone()['count']
            
            self.tables_info[table_name] = {
                'columns': columns,
                'primary_keys': primary_keys,
                'record_count': record_count
            }
        
        # Get foreign key relationships
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
        self.relationships = self.cursor.fetchall()
        
        logger.info(f"✅ Extracted schema for {len(tables)} tables with {len(self.relationships)} relationships")
    
    def create_network_erd(self):
        """Create network-style ERD using NetworkX."""
        logger.info("🎨 Creating network ERD...")
        
        # Create directed graph
        G = nx.DiGraph()
        
        # Add nodes (tables)
        for table_name, info in self.tables_info.items():
            G.add_node(table_name, 
                      record_count=info['record_count'],
                      column_count=len(info['columns']))
        
        # Add edges (relationships)
        for rel in self.relationships:
            G.add_edge(rel['target_table'], rel['source_table'],
                      relationship=f"{rel['target_column']} → {rel['source_column']}")
        
        # Create visualization
        plt.figure(figsize=(16, 12))
        
        # Use spring layout for better positioning
        pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
        
        # Draw nodes with different colors based on table type
        node_colors = []
        node_sizes = []
        
        for table in G.nodes():
            # Color coding based on table purpose
            if table in ['seasons', 'competitions', 'venues']:
                node_colors.append('#FF6B6B')  # Red for reference tables
                node_sizes.append(2000)
            elif table in ['teams', 'players']:
                node_colors.append('#4ECDC4')  # Teal for entity tables
                node_sizes.append(2500)
            elif 'statistics' in table:
                node_colors.append('#45B7D1')  # Blue for statistics tables
                node_sizes.append(1800)
            elif table in ['fixtures', 'lineups', 'match_events']:
                node_colors.append('#96CEB4')  # Green for match-related tables
                node_sizes.append(2200)
            else:
                node_colors.append('#FFEAA7')  # Yellow for other tables
                node_sizes.append(1500)
        
        # Draw the network
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20, alpha=0.6)
        
        plt.title("Soccer Intelligence Database - Entity Relationship Diagram", fontsize=16, fontweight='bold')
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF6B6B', markersize=10, label='Reference Tables'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4ECDC4', markersize=10, label='Core Entities'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#45B7D1', markersize=10, label='Statistics'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#96CEB4', markersize=10, label='Match Data'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFEAA7', markersize=10, label='Other')
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.axis('off')
        plt.tight_layout()
        
        # Save the diagram
        plt.savefig('docs/postgresql_erd_network.png', dpi=300, bbox_inches='tight')
        logger.info("✅ Network ERD saved as docs/postgresql_erd_network.png")
        
        return plt
    
    def create_detailed_table_diagram(self):
        """Create detailed table structure diagram."""
        logger.info("📋 Creating detailed table structure diagram...")
        
        # Calculate layout
        tables_per_row = 4
        rows_needed = (len(self.tables_info) + tables_per_row - 1) // tables_per_row
        
        fig, axes = plt.subplots(rows_needed, tables_per_row, figsize=(20, 5 * rows_needed))
        if rows_needed == 1:
            axes = [axes] if tables_per_row == 1 else axes
        else:
            axes = axes.flatten()
        
        # Hide unused subplots
        for i in range(len(self.tables_info), len(axes)):
            axes[i].set_visible(False)
        
        # Create table diagrams
        for idx, (table_name, info) in enumerate(self.tables_info.items()):
            ax = axes[idx]
            
            # Table header
            header_rect = FancyBboxPatch((0, 0.9), 1, 0.1, 
                                       boxstyle="round,pad=0.01",
                                       facecolor='#2C3E50', 
                                       edgecolor='black',
                                       linewidth=1)
            ax.add_patch(header_rect)
            ax.text(0.5, 0.95, table_name.upper(), ha='center', va='center', 
                   fontweight='bold', color='white', fontsize=10)
            
            # Record count
            ax.text(0.5, 0.85, f"({info['record_count']} records)", ha='center', va='center', 
                   fontsize=8, style='italic')
            
            # Columns
            y_pos = 0.8
            for col in info['columns'][:10]:  # Show first 10 columns
                # Determine column type indicator
                if col['column_name'] in info['primary_keys']:
                    indicator = "🔑"
                elif col['column_name'].endswith('_id'):
                    indicator = "🔗"
                else:
                    indicator = "📄"
                
                # Column text
                col_text = f"{indicator} {col['column_name']}"
                if len(col_text) > 25:
                    col_text = col_text[:22] + "..."
                
                ax.text(0.05, y_pos, col_text, ha='left', va='center', fontsize=8)
                ax.text(0.95, y_pos, col['data_type'], ha='right', va='center', 
                       fontsize=7, style='italic', color='gray')
                
                y_pos -= 0.08
                
                if y_pos < 0.1:
                    break
            
            # Show if there are more columns
            if len(info['columns']) > 10:
                ax.text(0.5, y_pos, f"... and {len(info['columns']) - 10} more columns", 
                       ha='center', va='center', fontsize=7, style='italic', color='gray')
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect('equal')
            ax.axis('off')
        
        plt.suptitle("PostgreSQL Database - Detailed Table Structures", fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Save the diagram
        plt.savefig('docs/postgresql_table_details.png', dpi=300, bbox_inches='tight')
        logger.info("✅ Detailed table diagram saved as docs/postgresql_table_details.png")
        
        return plt
    
    def generate_relationship_matrix(self):
        """Generate relationship matrix showing table connections."""
        logger.info("🔗 Creating relationship matrix...")
        
        tables = list(self.tables_info.keys())
        matrix = pd.DataFrame(0, index=tables, columns=tables)
        
        # Fill matrix with relationship counts
        for rel in self.relationships:
            source = rel['source_table']
            target = rel['target_table']
            if source in tables and target in tables:
                matrix.loc[source, target] += 1
        
        # Create heatmap
        plt.figure(figsize=(12, 10))
        
        # Create custom colormap
        import matplotlib.colors as mcolors
        colors = ['white', '#E8F4FD', '#B3D9F7', '#7EC8F0', '#4AB7EA', '#1E88E5']
        n_bins = len(colors)
        cmap = mcolors.LinearSegmentedColormap.from_list('custom', colors, N=n_bins)
        
        # Plot heatmap
        im = plt.imshow(matrix.values, cmap=cmap, aspect='auto')
        
        # Set ticks and labels
        plt.xticks(range(len(tables)), tables, rotation=45, ha='right')
        plt.yticks(range(len(tables)), tables)
        
        # Add text annotations
        for i in range(len(tables)):
            for j in range(len(tables)):
                if matrix.iloc[i, j] > 0:
                    plt.text(j, i, str(int(matrix.iloc[i, j])), 
                           ha='center', va='center', fontweight='bold')
        
        plt.title("Table Relationship Matrix\n(Rows reference Columns)", fontsize=14, fontweight='bold')
        plt.xlabel("Referenced Tables")
        plt.ylabel("Referencing Tables")
        
        # Add colorbar
        cbar = plt.colorbar(im)
        cbar.set_label('Number of Foreign Key Relationships')
        
        plt.tight_layout()
        
        # Save the matrix
        plt.savefig('docs/postgresql_relationship_matrix.png', dpi=300, bbox_inches='tight')
        logger.info("✅ Relationship matrix saved as docs/postgresql_relationship_matrix.png")
        
        return plt
    
    def generate_comprehensive_report(self):
        """Generate comprehensive database structure report."""
        logger.info("📋 Generating comprehensive database structure report...")
        
        print("\n" + "="*100)
        print("🗄️ POSTGRESQL DATABASE STRUCTURE COMPREHENSIVE REPORT")
        print("="*100)
        
        # Database overview
        total_tables = len(self.tables_info)
        total_relationships = len(self.relationships)
        total_records = sum(info['record_count'] for info in self.tables_info.values())
        
        print(f"\n📊 DATABASE OVERVIEW:")
        print(f"   • Total Tables: {total_tables}")
        print(f"   • Total Relationships: {total_relationships}")
        print(f"   • Total Records: {total_records:,}")
        
        # Table categories
        reference_tables = ['seasons', 'competitions', 'venues']
        entity_tables = ['teams', 'players']
        relationship_tables = ['team_seasons', 'squad_members', 'fixtures']
        statistics_tables = [t for t in self.tables_info.keys() if 'statistics' in t]
        
        print(f"\n🏗️ TABLE CATEGORIES:")
        print(f"   • Reference Tables: {len(reference_tables)} ({', '.join(reference_tables)})")
        print(f"   • Entity Tables: {len(entity_tables)} ({', '.join(entity_tables)})")
        print(f"   • Relationship Tables: {len(relationship_tables)} ({', '.join(relationship_tables)})")
        print(f"   • Statistics Tables: {len(statistics_tables)} ({', '.join(statistics_tables)})")
        
        # Largest tables
        sorted_tables = sorted(self.tables_info.items(), key=lambda x: x[1]['record_count'], reverse=True)
        
        print(f"\n📊 LARGEST TABLES BY RECORD COUNT:")
        for table_name, info in sorted_tables[:5]:
            print(f"   • {table_name}: {info['record_count']:,} records")
        
        # Relationship analysis
        print(f"\n🔗 RELATIONSHIP ANALYSIS:")
        source_counts = {}
        target_counts = {}
        
        for rel in self.relationships:
            source_counts[rel['source_table']] = source_counts.get(rel['source_table'], 0) + 1
            target_counts[rel['target_table']] = target_counts.get(rel['target_table'], 0) + 1
        
        # Most referenced tables
        most_referenced = sorted(target_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"   • Most Referenced Tables:")
        for table, count in most_referenced:
            print(f"     - {table}: referenced by {count} other tables")
        
        # Tables with most foreign keys
        most_referencing = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"   • Tables with Most Foreign Keys:")
        for table, count in most_referencing:
            print(f"     - {table}: references {count} other tables")
        
        print(f"\n🎯 VISUAL OUTPUTS GENERATED:")
        print(f"   • docs/postgresql_erd_network.png - Network ERD diagram")
        print(f"   • docs/postgresql_table_details.png - Detailed table structures")
        print(f"   • docs/postgresql_relationship_matrix.png - Relationship matrix")
        
        return {
            'total_tables': total_tables,
            'total_relationships': total_relationships,
            'total_records': total_records,
            'table_categories': {
                'reference': reference_tables,
                'entity': entity_tables,
                'relationship': relationship_tables,
                'statistics': statistics_tables
            },
            'largest_tables': sorted_tables[:5],
            'most_referenced': most_referenced,
            'most_referencing': most_referencing
        }
    
    def close_connection(self):
        """Close database connection."""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()
        logger.info("🔒 Database connection closed")

def main():
    """Main execution function."""
    erd_generator = PostgreSQLERDGenerator()
    
    try:
        # Extract database schema
        erd_generator.extract_database_schema()
        
        # Generate all visualizations
        erd_generator.create_network_erd()
        erd_generator.create_detailed_table_diagram()
        erd_generator.generate_relationship_matrix()
        
        # Generate comprehensive report
        report = erd_generator.generate_comprehensive_report()
        
        print("\n🎉 PostgreSQL database structure analysis completed!")
        print("📊 Visual diagrams saved in docs/ directory")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        erd_generator.close_connection()

if __name__ == "__main__":
    main()

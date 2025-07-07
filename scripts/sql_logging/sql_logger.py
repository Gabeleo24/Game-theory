#!/usr/bin/env python3
"""
SQL Query Logger
Automatically logs all SQL queries and results to timestamped files
for database process tracking and analysis.
"""

import os
import psycopg2
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

class SQLLogger:
    """Logger for SQL queries and results."""
    
    def __init__(self, log_dir: str = "logs/sql_logs"):
        """Initialize SQL logger."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'soccer_intelligence',
            'user': 'soccerapp',
            'password': 'soccerpass123'
        }
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"sql_session_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"SQL logging session started - Log file: {log_file}")
    
    def execute_and_log(self, query: str, description: str = "", save_results: bool = True) -> Optional[List[Dict[str, Any]]]:
        """Execute SQL query and log both query and results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        
        try:
            # Connect to database
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Log query start
            self.logger.info(f"EXECUTING QUERY: {description}")
            self.logger.info(f"SQL: {query}")
            
            # Execute query
            cursor.execute(query)
            
            # Get results if it's a SELECT query
            results = None
            if query.strip().upper().startswith('SELECT') or query.strip().upper().startswith('WITH'):
                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                
                # Convert to list of dictionaries
                results_dict = []
                for row in results:
                    results_dict.append(dict(zip(column_names, row)))
                
                self.logger.info(f"QUERY COMPLETED: {len(results)} rows returned")
                
                # Save results to file if requested
                if save_results:
                    self.save_results_to_file(query, description, results_dict, column_names, timestamp)
                
                return results_dict
            else:
                conn.commit()
                self.logger.info("QUERY COMPLETED: Non-SELECT query executed successfully")
                return None
                
        except Exception as e:
            self.logger.error(f"QUERY FAILED: {str(e)}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()
    
    def save_results_to_file(self, query: str, description: str, results: List[Dict[str, Any]], 
                           column_names: List[str], timestamp: str):
        """Save query results to a formatted file."""
        # Create filename
        safe_description = "".join(c for c in description if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_description = safe_description.replace(' ', '_')[:50]
        filename = f"query_{timestamp}_{safe_description}.sql"
        filepath = self.log_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"-- SQL Query Log\n")
            f.write(f"-- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Description: {description}\n")
            f.write(f"-- Results: {len(results)} rows\n")
            f.write(f"-- " + "="*60 + "\n\n")
            
            # Write original query
            f.write(f"-- ORIGINAL QUERY:\n")
            f.write(f"/*\n{query}\n*/\n\n")
            
            # Write results summary
            f.write(f"-- RESULTS SUMMARY:\n")
            f.write(f"-- Total rows: {len(results)}\n")
            f.write(f"-- Columns: {', '.join(column_names)}\n\n")
            
            # Write results as formatted table
            if results:
                f.write(f"-- RESULTS TABLE:\n")
                f.write(f"-- " + "-"*80 + "\n")
                
                # Write column headers
                header = " | ".join(f"{col:15}" for col in column_names)
                f.write(f"-- {header}\n")
                f.write(f"-- " + "-"*80 + "\n")
                
                # Write data rows (limit to first 100 for readability)
                for i, row in enumerate(results[:100]):
                    row_str = " | ".join(f"{str(row.get(col, ''))[:15]:15}" for col in column_names)
                    f.write(f"-- {row_str}\n")
                
                if len(results) > 100:
                    f.write(f"-- ... ({len(results) - 100} more rows)\n")
                
                f.write(f"-- " + "-"*80 + "\n")
            
            # Write results as INSERT statements (for backup/recreation)
            if results and len(results) <= 1000:  # Only for reasonable sized results
                f.write(f"\n-- RESULTS AS INSERT STATEMENTS:\n")
                f.write(f"-- (For backup/recreation purposes)\n\n")
                
                # Infer table name from query if possible
                table_name = "query_results"
                if "FROM" in query.upper():
                    try:
                        from_part = query.upper().split("FROM")[1].split()[0]
                        table_name = from_part.strip()
                    except:
                        pass
                
                for row in results:
                    values = []
                    for col in column_names:
                        val = row.get(col)
                        if val is None:
                            values.append("NULL")
                        elif isinstance(val, str):
                            values.append(f"'{val.replace(chr(39), chr(39)+chr(39))}'")  # Escape quotes
                        else:
                            values.append(str(val))
                    
                    f.write(f"-- INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({', '.join(values)});\n")
        
        self.logger.info(f"Results saved to: {filepath}")
    
    def log_process_start(self, process_name: str, description: str = ""):
        """Log the start of a database process."""
        self.logger.info(f"PROCESS START: {process_name}")
        if description:
            self.logger.info(f"DESCRIPTION: {description}")
        self.logger.info("-" * 60)
    
    def log_process_end(self, process_name: str, success: bool = True):
        """Log the end of a database process."""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"PROCESS END: {process_name} - {status}")
        self.logger.info("=" * 60)

# Convenience functions for easy use
def create_sql_logger(log_dir: str = "logs/sql_logs") -> SQLLogger:
    """Create and return a SQL logger instance."""
    return SQLLogger(log_dir)

def execute_and_log_query(query: str, description: str = "", log_dir: str = "logs/sql_logs"):
    """Execute a single query with logging."""
    logger = SQLLogger(log_dir)
    return logger.execute_and_log(query, description)

# Example usage functions
def log_player_cards_analysis():
    """Example: Log player cards analysis queries."""
    logger = create_sql_logger()
    
    logger.log_process_start("Player Cards Analysis", "Comprehensive analysis of player disciplinary records")
    
    # Query 1: Overview statistics
    logger.execute_and_log("""
        SELECT 
            COUNT(*) as total_player_statistics,
            SUM(yellow_cards) as total_yellow_cards,
            SUM(red_cards) as total_red_cards,
            COUNT(CASE WHEN yellow_cards > 0 THEN 1 END) as players_with_yellow_cards,
            COUNT(CASE WHEN red_cards > 0 THEN 1 END) as players_with_red_cards,
            ROUND(AVG(yellow_cards::numeric), 2) as avg_yellow_per_player,
            ROUND(AVG(red_cards::numeric), 2) as avg_red_per_player
        FROM player_statistics;
    """, "Player Cards Overview Statistics")
    
    # Query 2: Top players by yellow cards
    logger.execute_and_log("""
        SELECT 
            p.player_name,
            t.team_name,
            t.country,
            ps.season_year,
            ps.yellow_cards,
            ps.red_cards,
            ps.minutes_played,
            ps.goals,
            ps.assists,
            ps.position,
            CASE 
                WHEN ps.minutes_played > 0 
                THEN ROUND((ps.yellow_cards::numeric / ps.minutes_played * 90), 2)
                ELSE 0 
            END as yellow_cards_per_90min
        FROM player_statistics ps
        JOIN players p ON ps.player_id = p.player_id
        JOIN teams t ON ps.team_id = t.team_id
        WHERE ps.yellow_cards > 0
        ORDER BY ps.yellow_cards DESC, ps.red_cards DESC
        LIMIT 20;
    """, "Top 20 Players by Yellow Cards")
    
    # Query 3: Team disciplinary records
    logger.execute_and_log("""
        SELECT 
            t.team_name,
            t.country,
            ps.season_year,
            COUNT(*) as players_with_cards,
            SUM(ps.yellow_cards) as total_yellow_cards,
            SUM(ps.red_cards) as total_red_cards,
            ROUND(AVG(ps.yellow_cards::numeric), 2) as avg_yellow_per_player,
            ROUND(AVG(ps.red_cards::numeric), 2) as avg_red_per_player
        FROM player_statistics ps
        JOIN teams t ON ps.team_id = t.team_id
        WHERE ps.yellow_cards > 0 OR ps.red_cards > 0
        GROUP BY t.team_id, t.team_name, t.country, ps.season_year
        ORDER BY total_yellow_cards DESC, total_red_cards DESC
        LIMIT 20;
    """, "Team Disciplinary Records by Season")
    
    logger.log_process_end("Player Cards Analysis", True)

if __name__ == "__main__":
    # Example usage
    log_player_cards_analysis()

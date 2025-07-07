#!/usr/bin/env python3
"""
Run SQL Query with Automatic Logging
Simple script to execute any SQL query and automatically save logs.
"""

import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import sql_logger
sys.path.append(str(Path(__file__).parent))
from sql_logger import SQLLogger

def main():
    """Main function to run SQL queries with logging."""
    parser = argparse.ArgumentParser(description='Execute SQL query with automatic logging')
    parser.add_argument('--query', '-q', type=str, help='SQL query to execute')
    parser.add_argument('--file', '-f', type=str, help='File containing SQL query')
    parser.add_argument('--description', '-d', type=str, default='', help='Description of the query')
    parser.add_argument('--log-dir', '-l', type=str, default='logs/sql_logs', help='Directory to save logs')
    
    args = parser.parse_args()
    
    # Get query from argument or file
    query = None
    if args.query:
        query = args.query
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                query = f.read()
        except FileNotFoundError:
            print(f"Error: File {args.file} not found")
            return 1
    else:
        print("Error: Must provide either --query or --file")
        return 1
    
    # Create logger and execute query
    logger = SQLLogger(args.log_dir)
    
    description = args.description or "Manual SQL Query Execution"
    logger.log_process_start("Manual Query Execution", description)
    
    results = logger.execute_and_log(query, description)
    
    if results is not None:
        print(f"\nQuery executed successfully. {len(results)} rows returned.")
        print(f"Results logged to: {args.log_dir}")
        logger.log_process_end("Manual Query Execution", True)
        return 0
    else:
        print("Query execution failed or was a non-SELECT query.")
        logger.log_process_end("Manual Query Execution", False)
        return 1

if __name__ == "__main__":
    sys.exit(main())

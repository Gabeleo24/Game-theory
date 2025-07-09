#!/usr/bin/env python3
"""
Complete System Test and Validation Script for ADS599 Capstone Soccer Intelligence System
Comprehensive tests to ensure data collection, storage, and retrieval work correctly
"""

import os
import sys
import yaml
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import requests
import logging
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemValidator:
    """Comprehensive system validation and testing."""
    
    def __init__(self):
        """Initialize the system validator."""
        self.project_root = Path(__file__).parent
        self.load_configuration()
        self.test_results = {}
        
    def load_configuration(self):
        """Load system configuration."""
        try:
            with open(self.project_root / "config" / "api_keys.yaml", 'r') as f:
                self.config = yaml.safe_load(f)
            
            logger.info("✅ Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            raise
    
    def test_database_connection(self) -> Tuple[bool, str]:
        """Test database connectivity and basic operations."""
        try:
            db_config = self.config['database']
            
            # Test connection
            conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['name'],
                user=db_config['user'],
                password=db_config['password']
            )
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Test basic query
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            
            # Test table existence
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            table_count = cursor.fetchone()[0]
            
            conn.close()
            
            return True, f"Connected to PostgreSQL. Version: {version[:50]}..., Tables: {table_count}"
            
        except Exception as e:
            return False, f"Database connection failed: {str(e)}"
    
    def test_redis_connection(self) -> Tuple[bool, str]:
        """Test Redis connectivity and basic operations."""
        try:
            redis_config = self.config['redis']
            
            # Test connection
            client = redis.Redis(
                host=redis_config['host'],
                port=redis_config['port'],
                password=redis_config['password'],
                db=redis_config['db'],
                decode_responses=True
            )
            
            # Test basic operations
            test_key = "system_test_key"
            test_value = "system_test_value"
            
            client.set(test_key, test_value, ex=60)  # Expire in 60 seconds
            retrieved_value = client.get(test_key)
            client.delete(test_key)
            
            if retrieved_value == test_value:
                return True, "Redis connection and operations successful"
            else:
                return False, "Redis operations failed"
            
        except Exception as e:
            return False, f"Redis connection failed: {str(e)}"
    
    def test_api_connectivity(self) -> Dict[str, Tuple[bool, str]]:
        """Test connectivity to external APIs."""
        api_results = {}
        
        # Test SportMonks API
        try:
            sportmonks_config = self.config['sportmonks']
            url = f"{sportmonks_config['base_url']}/football/teams/53"  # Real Madrid
            params = {'api_token': sportmonks_config['api_key']}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    api_results['sportmonks'] = (True, "SportMonks API accessible")
                else:
                    api_results['sportmonks'] = (False, "SportMonks API returned unexpected format")
            else:
                api_results['sportmonks'] = (False, f"SportMonks API returned status {response.status_code}")
                
        except Exception as e:
            api_results['sportmonks'] = (False, f"SportMonks API error: {str(e)}")
        
        # Test API-Football
        try:
            api_football_config = self.config['api_football']
            url = f"{api_football_config['base_url']}/teams"
            headers = {
                'X-RapidAPI-Key': api_football_config['key'],
                'X-RapidAPI-Host': 'v3.football.api-sports.io'
            }
            params = {'id': 541}  # Real Madrid
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'response' in data:
                    api_results['api_football'] = (True, "API-Football accessible")
                else:
                    api_results['api_football'] = (False, "API-Football returned unexpected format")
            else:
                api_results['api_football'] = (False, f"API-Football returned status {response.status_code}")
                
        except Exception as e:
            api_results['api_football'] = (False, f"API-Football error: {str(e)}")
        
        return api_results
    
    def test_database_schema(self) -> Tuple[bool, str]:
        """Test database schema integrity."""
        try:
            db_config = self.config['database']
            conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['name'],
                user=db_config['user'],
                password=db_config['password']
            )
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Expected tables
            expected_tables = [
                'seasons', 'competitions', 'teams', 'players', 'matches',
                'player_statistics', 'team_statistics', 'match_events',
                'api_collection_metadata', 'data_quality_checks'
            ]
            
            # Check each table
            missing_tables = []
            table_info = {}
            
            for table in expected_tables:
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_name = %s AND table_schema = 'public'
                """, (table,))
                
                if cursor.fetchone()[0] == 0:
                    missing_tables.append(table)
                else:
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    row_count = cursor.fetchone()[0]
                    table_info[table] = row_count
            
            conn.close()
            
            if missing_tables:
                return False, f"Missing tables: {missing_tables}"
            else:
                summary = ", ".join([f"{table}: {count} rows" for table, count in table_info.items()])
                return True, f"All tables present. {summary}"
            
        except Exception as e:
            return False, f"Schema test failed: {str(e)}"
    
    def test_data_collection_functionality(self) -> Tuple[bool, str]:
        """Test data collection functionality."""
        try:
            # Import the data collector
            sys.path.append(str(self.project_root))
            from services.unified_data_collector import UnifiedDataCollector
            
            # Test basic collector initialization
            collector = UnifiedDataCollector()
            
            # Test configuration loading
            if not hasattr(collector, 'apis'):
                return False, "Data collector failed to load API configurations"
            
            if 'sportmonks' not in collector.apis or 'api_football' not in collector.apis:
                return False, "Data collector missing API configurations"
            
            # Test database connection
            if not hasattr(collector, 'db_conn'):
                return False, "Data collector failed to establish database connection"
            
            # Test cache connection
            if not hasattr(collector, 'redis_client'):
                return False, "Data collector failed to establish cache connection"
            
            collector.close_connections()
            
            return True, "Data collection functionality test passed"
            
        except Exception as e:
            return False, f"Data collection test failed: {str(e)}"
    
    def test_sample_data_insertion(self) -> Tuple[bool, str]:
        """Test sample data insertion and retrieval."""
        try:
            db_config = self.config['database']
            conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['name'],
                user=db_config['user'],
                password=db_config['password']
            )
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Insert test team
            test_team_name = f"Test Team {int(time.time())}"
            cursor.execute("""
                INSERT INTO teams (team_name, country, data_source)
                VALUES (%s, %s, %s)
                RETURNING team_id
            """, (test_team_name, "Test Country", "test"))
            
            team_id = cursor.fetchone()[0]
            
            # Insert test player
            test_player_name = f"Test Player {int(time.time())}"
            cursor.execute("""
                INSERT INTO players (player_name, current_team_id, data_source)
                VALUES (%s, %s, %s)
                RETURNING player_id
            """, (test_player_name, team_id, "test"))
            
            player_id = cursor.fetchone()[0]
            
            # Verify insertion
            cursor.execute("SELECT team_name FROM teams WHERE team_id = %s", (team_id,))
            retrieved_team = cursor.fetchone()
            
            cursor.execute("SELECT player_name FROM players WHERE player_id = %s", (player_id,))
            retrieved_player = cursor.fetchone()
            
            # Clean up test data
            cursor.execute("DELETE FROM players WHERE player_id = %s", (player_id,))
            cursor.execute("DELETE FROM teams WHERE team_id = %s", (team_id,))
            
            conn.commit()
            conn.close()
            
            if retrieved_team and retrieved_player:
                return True, "Sample data insertion and retrieval successful"
            else:
                return False, "Failed to retrieve inserted test data"
            
        except Exception as e:
            return False, f"Sample data test failed: {str(e)}"
    
    def run_comprehensive_tests(self) -> Dict[str, Tuple[bool, str]]:
        """Run all comprehensive system tests."""
        logger.info("🔄 Running comprehensive system tests...")
        
        tests = {
            'database_connection': self.test_database_connection,
            'redis_connection': self.test_redis_connection,
            'database_schema': self.test_database_schema,
            'sample_data_insertion': self.test_sample_data_insertion,
            'data_collection_functionality': self.test_data_collection_functionality,
        }
        
        results = {}
        
        for test_name, test_func in tests.items():
            logger.info(f"🔄 Running test: {test_name}")
            try:
                success, message = test_func()
                results[test_name] = (success, message)
                
                if success:
                    logger.info(f"✅ {test_name}: {message}")
                else:
                    logger.error(f"❌ {test_name}: {message}")
                    
            except Exception as e:
                error_msg = f"Test execution failed: {str(e)}"
                results[test_name] = (False, error_msg)
                logger.error(f"❌ {test_name}: {error_msg}")
        
        # Test API connectivity separately
        logger.info("🔄 Testing API connectivity...")
        api_results = self.test_api_connectivity()
        results.update(api_results)
        
        for api_name, (success, message) in api_results.items():
            if success:
                logger.info(f"✅ {api_name}_api: {message}")
            else:
                logger.error(f"❌ {api_name}_api: {message}")
        
        return results
    
    def print_test_summary(self, results: Dict[str, Tuple[bool, str]]):
        """Print comprehensive test summary."""
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE SYSTEM TEST RESULTS")
        print("="*80)
        
        passed_tests = sum(1 for success, _ in results.values() if success)
        total_tests = len(results)
        
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        
        for test_name, (success, message) in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
            print(f"    └─ {message}")
        
        print("\n" + "="*80)
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! System is fully functional.")
            print("✅ Ready for production data collection and analysis.")
        else:
            print("⚠️  Some tests failed. Please review and fix issues before proceeding.")
            print("📝 Check logs above for detailed error information.")
        
        print("="*80)
        
        return passed_tests == total_tests

def main():
    """Main function to run comprehensive system tests."""
    try:
        validator = SystemValidator()
        
        # Run all tests
        results = validator.run_comprehensive_tests()
        
        # Print summary
        all_passed = validator.print_test_summary(results)
        
        return all_passed
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

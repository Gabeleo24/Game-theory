#!/usr/bin/env python3
"""
Real Madrid System Validation and Testing Script
Comprehensive tests for Real Madrid 2023-2024 data collection system
"""

import os
import sys
import yaml
import psycopg2
from psycopg2.extras import RealDictCursor
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

class RealMadridSystemValidator:
    """Comprehensive validation for Real Madrid data collection system."""
    
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
        """Test database connectivity and Real Madrid schema."""
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
            
            # Check Real Madrid specific tables
            expected_tables = [
                'seasons', 'competitions', 'teams', 'players', 'matches',
                'player_match_statistics', 'match_events', 'data_collection_log'
            ]
            
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = set(expected_tables) - set(existing_tables)
            if missing_tables:
                conn.close()
                return False, f"Missing tables: {missing_tables}"
            
            # Check Real Madrid team exists
            cursor.execute("SELECT COUNT(*) FROM teams WHERE is_real_madrid = TRUE")
            real_madrid_count = cursor.fetchone()[0]
            
            # Check 2023-2024 season exists
            cursor.execute("SELECT COUNT(*) FROM seasons WHERE season_name = '2023-2024'")
            season_count = cursor.fetchone()[0]
            
            conn.close()
            
            return True, f"Database OK. Tables: {len(existing_tables)}, Real Madrid: {real_madrid_count}, Season: {season_count}"
            
        except Exception as e:
            return False, f"Database connection failed: {str(e)}"
    
    def test_sportmonks_api(self) -> Tuple[bool, str]:
        """Test SportMonks API connectivity."""
        try:
            sportmonks_config = self.config['sportmonks']
            url = f"{sportmonks_config['base_url']}/football/teams/53"  # Real Madrid
            params = {'api_token': sportmonks_config['api_key']}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data'].get('name') == 'Real Madrid':
                    return True, "SportMonks API accessible, Real Madrid data confirmed"
                else:
                    return False, "SportMonks API returned unexpected data format"
            else:
                return False, f"SportMonks API returned status {response.status_code}"
                
        except Exception as e:
            return False, f"SportMonks API error: {str(e)}"
    
    def test_data_collection_functionality(self) -> Tuple[bool, str]:
        """Test Real Madrid data collector functionality."""
        try:
            # Import the Real Madrid collector
            sys.path.append(str(self.project_root))
            from services.real_madrid_collector import RealMadridCollector
            
            # Test collector initialization
            collector = RealMadridCollector()
            
            # Test configuration loading
            if not hasattr(collector, 'api_token'):
                return False, "Collector failed to load SportMonks API configuration"
            
            if not hasattr(collector, 'db_conn'):
                return False, "Collector failed to establish database connection"
            
            # Test constants
            if collector.REAL_MADRID_TEAM_ID != 53:
                return False, "Incorrect Real Madrid team ID"
            
            if collector.SEASON_2023_2024_ID != 23087:
                return False, "Incorrect 2023-2024 season ID"
            
            collector.close_connections()
            
            return True, "Real Madrid collector functionality test passed"
            
        except Exception as e:
            return False, f"Collector test failed: {str(e)}"
    
    def test_database_schema_integrity(self) -> Tuple[bool, str]:
        """Test database schema integrity and constraints."""
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
            
            # Test unique constraints
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.table_constraints 
                WHERE constraint_type = 'UNIQUE' AND table_schema = 'public'
            """)
            unique_constraints = cursor.fetchone()[0]
            
            # Test foreign key constraints
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.table_constraints 
                WHERE constraint_type = 'FOREIGN KEY' AND table_schema = 'public'
            """)
            foreign_keys = cursor.fetchone()[0]
            
            # Test indexes
            cursor.execute("""
                SELECT COUNT(*) FROM pg_indexes 
                WHERE schemaname = 'public'
            """)
            indexes = cursor.fetchone()[0]
            
            # Test views
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.views 
                WHERE table_schema = 'public'
            """)
            views = cursor.fetchone()[0]
            
            # Test specific Real Madrid constraints
            cursor.execute("""
                SELECT column_name, is_nullable, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'player_match_statistics' 
                AND column_name IN ('match_id', 'player_id')
            """)
            key_columns = cursor.fetchall()
            
            conn.close()
            
            if len(key_columns) != 2:
                return False, "Missing key columns in player_match_statistics table"
            
            return True, f"Schema integrity OK. Constraints: {unique_constraints}, FKs: {foreign_keys}, Indexes: {indexes}, Views: {views}"
            
        except Exception as e:
            return False, f"Schema integrity test failed: {str(e)}"
    
    def test_data_quality(self) -> Tuple[bool, str]:
        """Test data quality and consistency."""
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
            
            quality_issues = []
            
            # Check for matches without Real Madrid involvement
            cursor.execute("""
                SELECT COUNT(*) FROM matches 
                WHERE real_madrid_home = FALSE AND real_madrid_away = FALSE
            """)
            non_real_madrid_matches = cursor.fetchone()[0]
            
            if non_real_madrid_matches > 0:
                quality_issues.append(f"{non_real_madrid_matches} matches without Real Madrid")
            
            # Check for players without team assignment
            cursor.execute("SELECT COUNT(*) FROM players WHERE team_id IS NULL")
            players_without_team = cursor.fetchone()[0]
            
            if players_without_team > 0:
                quality_issues.append(f"{players_without_team} players without team")
            
            # Check for statistics with impossible values
            cursor.execute("""
                SELECT COUNT(*) FROM player_match_statistics 
                WHERE minutes_played < 0 OR minutes_played > 120 
                OR goals < 0 OR assists < 0
            """)
            invalid_stats = cursor.fetchone()[0]
            
            if invalid_stats > 0:
                quality_issues.append(f"{invalid_stats} records with invalid statistics")
            
            # Check for duplicate player-match combinations
            cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT match_id, player_id, COUNT(*) 
                    FROM player_match_statistics 
                    GROUP BY match_id, player_id 
                    HAVING COUNT(*) > 1
                ) duplicates
            """)
            duplicate_stats = cursor.fetchone()[0]
            
            if duplicate_stats > 0:
                quality_issues.append(f"{duplicate_stats} duplicate player-match statistics")
            
            conn.close()
            
            if quality_issues:
                return False, f"Data quality issues: {'; '.join(quality_issues)}"
            else:
                return True, "Data quality validation passed"
            
        except Exception as e:
            return False, f"Data quality test failed: {str(e)}"
    
    def test_analysis_views(self) -> Tuple[bool, str]:
        """Test analysis views functionality."""
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
            
            # Test Real Madrid player summary view
            cursor.execute("SELECT COUNT(*) FROM real_madrid_player_summary")
            player_summary_count = cursor.fetchone()[0]
            
            # Test Real Madrid matches view
            cursor.execute("SELECT COUNT(*) FROM real_madrid_matches")
            matches_view_count = cursor.fetchone()[0]
            
            # Test view data quality
            if player_summary_count > 0:
                cursor.execute("""
                    SELECT player_name, matches_played, total_goals, avg_rating 
                    FROM real_madrid_player_summary 
                    LIMIT 1
                """)
                sample_player = cursor.fetchone()
                
                if not sample_player or not sample_player['player_name']:
                    conn.close()
                    return False, "Player summary view contains invalid data"
            
            conn.close()
            
            return True, f"Analysis views OK. Players: {player_summary_count}, Matches: {matches_view_count}"
            
        except Exception as e:
            return False, f"Analysis views test failed: {str(e)}"
    
    def run_comprehensive_tests(self) -> Dict[str, Tuple[bool, str]]:
        """Run all comprehensive system tests."""
        logger.info("🔄 Running comprehensive Real Madrid system tests...")
        
        tests = {
            'database_connection': self.test_database_connection,
            'sportmonks_api': self.test_sportmonks_api,
            'data_collection_functionality': self.test_data_collection_functionality,
            'database_schema_integrity': self.test_database_schema_integrity,
            'data_quality': self.test_data_quality,
            'analysis_views': self.test_analysis_views,
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
        
        return results
    
    def print_test_summary(self, results: Dict[str, Tuple[bool, str]]):
        """Print comprehensive test summary."""
        print("\n" + "="*80)
        print("🧪 REAL MADRID SYSTEM TEST RESULTS")
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
            print("🎉 ALL TESTS PASSED! Real Madrid system is fully functional.")
            print("✅ Ready for comprehensive data collection and analysis.")
            print("🚀 Run: python start_real_madrid_system.py")
        else:
            print("⚠️  Some tests failed. Please review and fix issues.")
            print("📝 Check logs above for detailed error information.")
        
        print("="*80)
        
        return passed_tests == total_tests

def main():
    """Main function to run comprehensive Real Madrid system tests."""
    try:
        validator = RealMadridSystemValidator()
        
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

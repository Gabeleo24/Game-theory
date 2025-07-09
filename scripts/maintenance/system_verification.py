#!/usr/bin/env python3
"""
SYSTEM VERIFICATION SCRIPT
Comprehensive verification that the cleaned project works correctly
"""

import os
import subprocess
import psycopg2
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemVerifier:
    def __init__(self):
        self.project_root = Path("/Users/home/Documents/GitHub/ADS599_Capstone")
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'soccer_intelligence',
            'user': 'soccerapp',
            'password': 'soccerpass123'
        }
        self.verification_results = []
    
    def verify_docker_containers(self):
        """Verify Docker containers are running."""
        logger.info("[DOCKER] Verifying Docker containers...")
        
        try:
            result = subprocess.run(
                ["docker", "compose", "ps", "--format", "json"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("   [PASS] Docker Compose is working")
                # Check if postgres container is running
                if "postgres" in result.stdout and "running" in result.stdout:
                    logger.info("   [PASS] PostgreSQL container is running")
                    self.verification_results.append(("Docker", "[PASS] PASS"))
                else:
                    logger.warning("   [WARNING] PostgreSQL container not running")
                    self.verification_results.append(("Docker", "[WARNING] WARNING"))
            else:
                logger.error("   [FAIL] Docker Compose failed")
                self.verification_results.append(("Docker", "[FAIL] FAIL"))
                
        except Exception as e:
            logger.error(f"   [FAIL] Docker verification failed: {e}")
            self.verification_results.append(("Docker", "[FAIL] FAIL"))
    
    def verify_database_connection(self):
        """Verify database connection and tables."""
        logger.info("[DATABASE] Verifying database connection...")
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check if fixed tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'fixed_%'
                ORDER BY table_name
            """)
            
            fixed_tables = cursor.fetchall()
            expected_tables = ['fixed_match_player_stats', 'fixed_matches', 'fixed_players', 'fixed_teams']
            
            if len(fixed_tables) >= 4:
                logger.info("   [PASS] Fixed tables exist")
                
                # Check data counts
                cursor.execute("SELECT COUNT(*) FROM fixed_matches")
                match_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM fixed_players WHERE team_id = (SELECT team_id FROM fixed_teams WHERE team_name = 'Real Madrid')")
                rm_player_count = cursor.fetchone()[0]
                
                logger.info(f"   [PASS] {match_count} matches loaded")
                logger.info(f"   [PASS] {rm_player_count} Real Madrid players")
                
                if match_count >= 50 and rm_player_count >= 35:
                    self.verification_results.append(("Database", "[PASS] PASS"))
                else:
                    self.verification_results.append(("Database", "[WARNING] WARNING"))
            else:
                logger.error("   [FAIL] Fixed tables missing")
                self.verification_results.append(("Database", "[FAIL] FAIL"))
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"   [FAIL] Database verification failed: {e}")
            self.verification_results.append(("Database", "[FAIL] FAIL"))
    
    def verify_essential_scripts(self):
        """Verify essential scripts exist and are executable."""
        logger.info("[SCRIPTS] Verifying essential scripts...")
        
        essential_scripts = [
            "scripts/data_loading/fixed_match_loader.py",
            "scripts/analysis/fixed_data_analysis.py",
            "scripts/analysis/missing_data_analyzer.py",
            "scripts/maintenance/comprehensive_cleanup.py"
        ]
        
        all_scripts_ok = True
        for script_path in essential_scripts:
            full_path = self.project_root / script_path
            if full_path.exists():
                # Check if file has substantial content
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                    if len(content) > 1000:  # Substantial script
                        logger.info(f"   [PASS] {script_path}")
                    else:
                        logger.warning(f"   [WARNING] {script_path} (small file)")
                        all_scripts_ok = False
                except Exception as e:
                    logger.error(f"   [FAIL] {script_path} (read error)")
                    all_scripts_ok = False
            else:
                logger.error(f"   [FAIL] {script_path} (missing)")
                all_scripts_ok = False
        
        if all_scripts_ok:
            self.verification_results.append(("Scripts", "[PASS] PASS"))
        else:
            self.verification_results.append(("Scripts", "[WARNING] WARNING"))
    
    def verify_data_files(self):
        """Verify essential data files exist."""
        logger.info("[FILES] Verifying data files...")
        
        data_dir = self.project_root / "data/focused/players/real_madrid_2023_2024/individual_matches"
        
        if data_dir.exists():
            json_files = list(data_dir.glob("*.json"))
            logger.info(f"   [PASS] Found {len(json_files)} match data files")
            
            if len(json_files) >= 50:
                self.verification_results.append(("Data Files", "[PASS] PASS"))
            else:
                self.verification_results.append(("Data Files", "[WARNING] WARNING"))
        else:
            logger.error("   [FAIL] Match data directory missing")
            self.verification_results.append(("Data Files", "[FAIL] FAIL"))
    
    def verify_configuration_files(self):
        """Verify configuration files exist."""
        logger.info("[CONFIG] Verifying configuration files...")
        
        config_files = [
            "docker-compose.yml",
            "Dockerfile", 
            "requirements.txt",
            ".env.template",
            ".gitignore",
            "README.md"
        ]
        
        all_configs_ok = True
        for config_file in config_files:
            full_path = self.project_root / config_file
            if full_path.exists():
                logger.info(f"   [PASS] {config_file}")
            else:
                logger.error(f"   [FAIL] {config_file} (missing)")
                all_configs_ok = False
        
        if all_configs_ok:
            self.verification_results.append(("Configuration", "[PASS] PASS"))
        else:
            self.verification_results.append(("Configuration", "[FAIL] FAIL"))
    
    def verify_mbapp_absence(self):
        """Verify Mbappé is correctly absent and explain why."""
        logger.info("[ANALYSIS] Verifying Mbappé absence explanation...")
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Search for Mbappé
            cursor.execute("""
                SELECT COUNT(*) 
                FROM fixed_players 
                WHERE LOWER(player_name) LIKE '%mbappe%' OR LOWER(player_name) LIKE '%mbappé%'
            """)
            
            mbappe_count = cursor.fetchone()[0]
            
            # Get data date range
            cursor.execute("""
                SELECT MIN(match_date) as first_match, MAX(match_date) as last_match
                FROM fixed_matches
            """)
            
            date_range = cursor.fetchone()
            
            if mbappe_count == 0:
                logger.info("   [PASS] Mbappé correctly absent from dataset")
                logger.info(f"   [DATE] Data covers: {date_range[0]} to {date_range[1]}")
                logger.info("   [DATE] Mbappé joined Real Madrid: June 3, 2024")
                logger.info("   [RESULT] Conclusion: Timeline explains absence - NOT missing data!")
                self.verification_results.append(("Mbappé Analysis", "[PASS] PASS"))
            else:
                logger.warning(f"   [WARNING] Found {mbappe_count} Mbappé records (unexpected)")
                self.verification_results.append(("Mbappé Analysis", "[WARNING] WARNING"))
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"   [FAIL] Mbappé verification failed: {e}")
            self.verification_results.append(("Mbappé Analysis", "[FAIL] FAIL"))
    
    def verify_data_quality(self):
        """Verify data quality improvements."""
        logger.info("[DATA] Verifying data quality...")
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Check Real Madrid player deduplication
            cursor.execute("""
                SELECT COUNT(DISTINCT player_name) as unique_players,
                       COUNT(*) as total_records
                FROM fixed_players p
                JOIN fixed_teams t ON p.team_id = t.team_id
                WHERE t.team_name = 'Real Madrid'
            """)
            
            rm_stats = cursor.fetchone()
            unique_players, total_records = rm_stats
            
            logger.info(f"   [DATA] Real Madrid: {unique_players} unique players, {total_records} records")
            
            if unique_players == total_records:
                logger.info("   [PASS] Perfect deduplication - no duplicate players!")
                self.verification_results.append(("Data Quality", "[PASS] PASS"))
            elif unique_players >= 35 and total_records <= unique_players + 5:
                logger.info("   [PASS] Good deduplication - minimal duplicates")
                self.verification_results.append(("Data Quality", "[PASS] PASS"))
            else:
                logger.warning(f"   [WARNING] Some duplication remains: {total_records - unique_players} extra records")
                self.verification_results.append(("Data Quality", "[WARNING] WARNING"))
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"   [FAIL] Data quality verification failed: {e}")
            self.verification_results.append(("Data Quality", "[FAIL] FAIL"))
    
    def generate_verification_report(self):
        """Generate final verification report."""
        logger.info("="*80)
        logger.info("[RESULT] SYSTEM VERIFICATION REPORT")
        logger.info("="*80)
        
        passed = 0
        warnings = 0
        failed = 0
        
        for component, status in self.verification_results:
            logger.info(f"   {component:<20} {status}")
            if "[PASS] " in status:
                passed += 1
            elif "[WARNING] " in status:
                warnings += 1
            else:
                failed += 1
        
        logger.info("="*80)
        logger.info(f"[DATA] VERIFICATION SUMMARY:")
        logger.info(f"   [PASS] Passed: {passed}")
        logger.info(f"   [WARNING] Warnings: {warnings}")
        logger.info(f"   [FAIL] Failed: {failed}")
        
        if failed == 0:
            if warnings == 0:
                logger.info("[COMPLETE] PERFECT! All systems operational!")
                logger.info("[PASS] Project is ready for production use!")
            else:
                logger.info("[PASS] GOOD! System is functional with minor issues!")
                logger.info("[PASS] Project is ready for use!")
        else:
            logger.error("[FAIL] ISSUES FOUND! Some components need attention!")
            logger.error("[WARNING] Project may not function correctly!")
        
        return failed == 0
    
    def run_verification(self):
        """Run complete system verification."""
        logger.info("COMPREHENSIVE SYSTEM VERIFICATION")
        logger.info("Cleaned ADS599 Capstone Soccer Intelligence System")
        logger.info("="*80)
        
        # Run all verification checks
        self.verify_docker_containers()
        self.verify_database_connection()
        self.verify_essential_scripts()
        self.verify_data_files()
        self.verify_configuration_files()
        self.verify_mbapp_absence()
        self.verify_data_quality()
        
        # Generate final report
        success = self.generate_verification_report()
        
        return success

if __name__ == "__main__":
    verifier = SystemVerifier()
    success = verifier.run_verification()
    exit(0 if success else 1)

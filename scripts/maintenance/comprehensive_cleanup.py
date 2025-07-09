#!/usr/bin/env python3
"""
COMPREHENSIVE PROJECT CLEANUP
Clean the entire codebase and organize everything properly
"""

import os
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProjectCleaner:
    def __init__(self):
        self.project_root = Path("/Users/home/Documents/GitHub/ADS599_Capstone")
        self.removed_files = []
        self.removed_dirs = []
        self.kept_files = []
        
    def clean_broken_scripts(self):
        """Remove broken/empty scripts that were manually cleared."""
        logger.info("🧹 Cleaning broken scripts...")
        
        broken_scripts = [
            "scripts/data_loading/match_level_player_stats_loader.py",
            "scripts/data_loading/load_real_madrid_match_stats.py", 
            "scripts/analysis/test_match_level_queries.py",
            "scripts/data_loading/load_real_madrid_with_players.py",
            "scripts/data_loading/simple_real_madrid_loader.py",
            "scripts/analysis/check_database_status.py",
            "scripts/data_loading/force_real_madrid_loader.py",
            "scripts/data_loading/final_real_madrid_loader.py",
            "scripts/analysis/check_match_level_data.py"
        ]
        
        for script_path in broken_scripts:
            full_path = self.project_root / script_path
            if full_path.exists():
                # Check if file is essentially empty (just contains placeholder)
                try:
                    with open(full_path, 'r') as f:
                        content = f.read().strip()
                    if len(content) < 50:  # Essentially empty
                        full_path.unlink()
                        self.removed_files.append(script_path)
                        logger.info(f"   [FAIL] Removed broken script: {script_path}")
                    else:
                        self.kept_files.append(script_path)
                        logger.info(f"   [PASS] Kept working script: {script_path}")
                except Exception as e:
                    logger.warning(f"   [WARNING] Could not process {script_path}: {e}")
    
    def clean_temporary_files(self):
        """Remove temporary and cache files."""
        logger.info("🧹 Cleaning temporary files...")
        
        temp_patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo", 
            "**/.DS_Store",
            "**/Thumbs.db",
            "**/*.tmp",
            "**/*.temp",
            "**/logs/sql_logs",
            "**/logs/*.log",
            "**/.pytest_cache"
        ]
        
        for pattern in temp_patterns:
            for path in self.project_root.glob(pattern):
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                        self.removed_dirs.append(str(path.relative_to(self.project_root)))
                        logger.info(f"   [FAIL] Removed directory: {path.relative_to(self.project_root)}")
                    else:
                        path.unlink()
                        self.removed_files.append(str(path.relative_to(self.project_root)))
                        logger.info(f"   [FAIL] Removed file: {path.relative_to(self.project_root)}")
                except Exception as e:
                    logger.warning(f"   [WARNING] Could not remove {path}: {e}")
    
    def organize_working_scripts(self):
        """Organize and verify working scripts."""
        logger.info("[FILES] Organizing working scripts...")
        
        # Key working scripts to verify
        working_scripts = {
            "scripts/data_loading/fixed_match_loader.py": "Fixed data loader with proper deduplication",
            "scripts/analysis/fixed_data_analysis.py": "Comprehensive analysis of fixed data",
            "scripts/analysis/missing_data_analyzer.py": "Missing data analysis tool",
            "scripts/analysis/comprehensive_player_roster.py": "Player roster analysis",
            "scripts/analysis/match_player_viewer.py": "Match-level player viewer",
            "scripts/data_loading/simple_match_loader.py": "Simple match data loader"
        }
        
        for script_path, description in working_scripts.items():
            full_path = self.project_root / script_path
            if full_path.exists():
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                    if len(content) > 100:  # Has substantial content
                        logger.info(f"   [PASS] Working: {script_path} - {description}")
                        self.kept_files.append(script_path)
                    else:
                        logger.warning(f"   [WARNING] Suspicious: {script_path} - Very small file")
                except Exception as e:
                    logger.warning(f"   [FAIL] Error reading {script_path}: {e}")
            else:
                logger.warning(f"   [FAIL] Missing: {script_path}")
    
    def clean_old_data_files(self):
        """Clean old/redundant data files while preserving essential ones."""
        logger.info("🗂️  Cleaning old data files...")
        
        # Preserve these essential data directories
        preserve_dirs = [
            "data/focused/players/real_madrid_2023_2024",
            "data/focused/teams",
            "config"
        ]
        
        # Check for old data that can be cleaned
        data_dir = self.project_root / "data"
        if data_dir.exists():
            for item in data_dir.rglob("*"):
                if item.is_file():
                    # Check if it's in a preserved directory
                    should_preserve = any(
                        str(item.relative_to(self.project_root)).startswith(preserve_dir)
                        for preserve_dir in preserve_dirs
                    )
                    
                    if should_preserve:
                        logger.info(f"   [PASS] Preserved: {item.relative_to(self.project_root)}")
                    else:
                        # Check file size and age to determine if it should be removed
                        if item.suffix in ['.json', '.csv'] and item.stat().st_size < 1000:
                            # Small data files that might be test/temp files
                            logger.info(f"   [WARNING] Small data file: {item.relative_to(self.project_root)}")
    
    def verify_essential_files(self):
        """Verify all essential files are present."""
        logger.info("[ANALYSIS] Verifying essential files...")
        
        essential_files = [
            "README.md",
            "docker-compose.yml", 
            "Dockerfile",
            "requirements.txt",
            ".env.template",
            ".gitignore",
            "scripts/data_loading/fixed_match_loader.py",
            "scripts/analysis/fixed_data_analysis.py"
        ]
        
        missing_files = []
        for file_path in essential_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                logger.info(f"   [PASS] Found: {file_path}")
            else:
                missing_files.append(file_path)
                logger.error(f"   [FAIL] Missing: {file_path}")
        
        return len(missing_files) == 0
    
    def create_cleanup_summary(self):
        """Create a summary of cleanup actions."""
        logger.info("[SUMMARY] Creating cleanup summary...")
        
        summary_path = self.project_root / "CLEANUP_SUMMARY.md"
        
        with open(summary_path, 'w') as f:
            f.write("# Project Cleanup Summary\n\n")
            f.write(f"**Cleanup Date**: {os.popen('date').read().strip()}\n\n")
            
            f.write("## Files Removed\n\n")
            if self.removed_files:
                for file_path in sorted(self.removed_files):
                    f.write(f"- [FAIL] {file_path}\n")
            else:
                f.write("- No files removed\n")
            
            f.write("\n## Directories Removed\n\n")
            if self.removed_dirs:
                for dir_path in sorted(self.removed_dirs):
                    f.write(f"- [FAIL] {dir_path}/\n")
            else:
                f.write("- No directories removed\n")
            
            f.write("\n## Key Working Files Verified\n\n")
            for file_path in sorted(self.kept_files):
                f.write(f"- [PASS] {file_path}\n")
            
            f.write("\n## Next Steps\n\n")
            f.write("1. Test the fixed data loader: `python scripts/data_loading/fixed_match_loader.py`\n")
            f.write("2. Run data analysis: `python scripts/analysis/fixed_data_analysis.py`\n")
            f.write("3. Verify database connectivity: `docker compose ps`\n")
            f.write("4. Check data quality with fixed tables\n")
        
        logger.info(f"   [DOCUMENT] Created cleanup summary: {summary_path}")
    
    def run_cleanup(self):
        """Run the complete cleanup process."""
        logger.info("STARTING COMPREHENSIVE PROJECT CLEANUP")
        logger.info("="*60)
        
        # Step 1: Clean broken scripts
        self.clean_broken_scripts()
        
        # Step 2: Clean temporary files
        self.clean_temporary_files()
        
        # Step 3: Organize working scripts
        self.organize_working_scripts()
        
        # Step 4: Clean old data files
        self.clean_old_data_files()
        
        # Step 5: Verify essential files
        all_essential_present = self.verify_essential_files()
        
        # Step 6: Create cleanup summary
        self.create_cleanup_summary()
        
        # Final summary
        logger.info("="*60)
        logger.info("[RESULT] CLEANUP COMPLETE!")
        logger.info(f"   Files removed: {len(self.removed_files)}")
        logger.info(f"   Directories removed: {len(self.removed_dirs)}")
        logger.info(f"   Working files verified: {len(self.kept_files)}")
        logger.info(f"   Essential files present: {'[PASS] Yes' if all_essential_present else '[FAIL] No'}")
        
        if all_essential_present:
            logger.info("[PASS] Project is ready for testing!")
        else:
            logger.error("[FAIL] Some essential files are missing - check logs above")
        
        return all_essential_present

if __name__ == "__main__":
    cleaner = ProjectCleaner()
    success = cleaner.run_cleanup()
    exit(0 if success else 1)

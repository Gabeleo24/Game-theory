#!/usr/bin/env python3
"""
Comprehensive Project Cleanup Script
Cleans and organizes the entire project folder while preserving essential data and functionality.
"""

import os
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectCleaner:
    """Comprehensive project cleanup and organization."""
    
    def __init__(self, project_root: str = "."):
        """Initialize the project cleaner."""
        self.project_root = Path(project_root).resolve()
        self.backup_dir = self.project_root / "backup_before_cleanup"
        
        # Statistics tracking
        self.stats = {
            'files_removed': 0,
            'directories_removed': 0,
            'files_moved': 0,
            'files_kept': 0,
            'space_freed_mb': 0
        }
        
        # Define what to keep vs remove
        self.essential_files = {
            # Core project files
            'README.md', 'requirements.txt', 'requirements_minimal.txt',
            'Dockerfile', 'docker-compose.yml', 'Makefile',
            'run_sql_with_logs.sh',
            
            # Essential data files
            'core_champions_league_teams.json',
            'team_league_mapping.json',
            'champions_league_focus_report.json',
            
            # Key analysis files
            'epic_matches_analysis.md',
            'player_cards_comprehensive_analysis.md',
            'README_SQL_LOGGING.md'
        }
        
        # Directories to keep (preserve structure)
        self.essential_dirs = {
            'src', 'scripts', 'config', 'docker', 'docs', 'tests',
            'data/focused/players', 'data/analysis', 'logs/sql_logs',
            'notebooks'
        }
        
        # File patterns to remove
        self.remove_patterns = {
            # Cache files
            '*.pyc', '__pycache__', '*.pyo', '*.pyd',
            '.pytest_cache', '.coverage', '.tox',
            
            # Temporary files
            '*.tmp', '*.temp', '*.bak', '*.swp', '*.swo',
            '.DS_Store', 'Thumbs.db',
            
            # Log files (except SQL logs)
            'collection_session_*.log',
            
            # Raw cache files
            'cache_*.json'
        }
        
        # Directories to clean completely
        self.clean_dirs = {
            'data/raw',
            'data/cache/player_statistics',
            'data/cache/team_statistics',
            'logs/player_collection'
        }
        
        # Redundant data directories (keep focused, remove processed duplicates)
        self.redundant_dirs = {
            'data/processed'  # Keep data/focused instead
        }
    
    def create_backup(self) -> None:
        """Create a backup of important files before cleanup."""
        logger.info("Creating backup of important files...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        self.backup_dir.mkdir(parents=True)
        
        # Backup key configuration and analysis files
        backup_files = [
            'config/focused_config.yaml',
            'data/analysis/epic_matches_analysis.md',
            'data/analysis/player_cards_comprehensive_analysis.md',
            'data/focused/core_champions_league_teams.json',
            'logs/README_SQL_LOGGING.md'
        ]
        
        for file_path in backup_files:
            src = self.project_root / file_path
            if src.exists():
                dst = self.backup_dir / file_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                logger.info(f"Backed up: {file_path}")
    
    def get_file_size_mb(self, path: Path) -> float:
        """Get file size in MB."""
        try:
            if path.is_file():
                return path.stat().st_size / (1024 * 1024)
            elif path.is_dir():
                total_size = 0
                for file_path in path.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                return total_size / (1024 * 1024)
        except:
            return 0
        return 0
    
    def should_keep_file(self, file_path: Path) -> bool:
        """Determine if a file should be kept."""
        # Keep essential files
        if file_path.name in self.essential_files:
            return True
        
        # Keep files in essential directories
        for essential_dir in self.essential_dirs:
            if str(file_path).startswith(str(self.project_root / essential_dir)):
                return True
        
        # Keep focused data files
        if 'data/focused' in str(file_path) and file_path.suffix == '.json':
            return True
        
        # Keep SQL logs
        if 'logs/sql_logs' in str(file_path):
            return True
        
        # Keep core scripts
        if file_path.suffix == '.py' and 'scripts' in str(file_path):
            return True
        
        # Keep documentation
        if file_path.suffix in {'.md', '.rst', '.txt'} and 'docs' in str(file_path):
            return True
        
        return False
    
    def clean_redundant_data(self) -> None:
        """Remove redundant data files and directories."""
        logger.info("Cleaning redundant data files...")
        
        # Remove redundant directories
        for dir_name in self.redundant_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                size_mb = self.get_file_size_mb(dir_path)
                shutil.rmtree(dir_path)
                self.stats['directories_removed'] += 1
                self.stats['space_freed_mb'] += size_mb
                logger.info(f"Removed redundant directory: {dir_name} ({size_mb:.1f} MB)")
        
        # Clean specific directories
        for dir_name in self.clean_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                size_mb = self.get_file_size_mb(dir_path)
                shutil.rmtree(dir_path)
                dir_path.mkdir(parents=True, exist_ok=True)
                self.stats['space_freed_mb'] += size_mb
                logger.info(f"Cleaned directory: {dir_name} ({size_mb:.1f} MB)")
    
    def remove_cache_and_temp_files(self) -> None:
        """Remove cache and temporary files."""
        logger.info("Removing cache and temporary files...")
        
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            
            # Remove cache directories
            for dir_name in dirs[:]:  # Use slice to avoid modification during iteration
                if dir_name in {'__pycache__', '.pytest_cache', '.tox', 'node_modules'}:
                    cache_dir = root_path / dir_name
                    size_mb = self.get_file_size_mb(cache_dir)
                    shutil.rmtree(cache_dir)
                    dirs.remove(dir_name)
                    self.stats['directories_removed'] += 1
                    self.stats['space_freed_mb'] += size_mb
                    logger.info(f"Removed cache directory: {cache_dir}")
            
            # Remove cache and temp files
            for file_name in files:
                file_path = root_path / file_name
                
                # Check against removal patterns
                should_remove = False
                for pattern in self.remove_patterns:
                    if pattern.startswith('*') and file_name.endswith(pattern[1:]):
                        should_remove = True
                        break
                    elif file_name == pattern:
                        should_remove = True
                        break
                
                if should_remove:
                    size_mb = self.get_file_size_mb(file_path)
                    file_path.unlink()
                    self.stats['files_removed'] += 1
                    self.stats['space_freed_mb'] += size_mb
                    logger.info(f"Removed cache/temp file: {file_path}")
    
    def organize_remaining_files(self) -> None:
        """Organize remaining files into proper structure."""
        logger.info("Organizing remaining files...")
        
        # Ensure essential directories exist
        essential_dirs = [
            'data/focused/players',
            'data/analysis',
            'logs/sql_logs',
            'scripts/analysis',
            'scripts/data_loading',
            'scripts/sql_logging',
            'config',
            'docs'
        ]
        
        for dir_path in essential_dirs:
            (self.project_root / dir_path).mkdir(parents=True, exist_ok=True)
    
    def create_cleanup_summary(self) -> None:
        """Create a summary of the cleanup process."""
        summary = {
            'cleanup_timestamp': datetime.now().isoformat(),
            'statistics': self.stats,
            'essential_files_preserved': list(self.essential_files),
            'essential_directories_preserved': list(self.essential_dirs),
            'directories_cleaned': list(self.clean_dirs),
            'redundant_directories_removed': list(self.redundant_dirs),
            'space_freed_mb': round(self.stats['space_freed_mb'], 2),
            'cleanup_actions': [
                'Removed redundant data/processed directory',
                'Cleaned cache and temporary files',
                'Removed old collection logs',
                'Preserved focused dataset and player statistics',
                'Kept SQL logging system intact',
                'Maintained core scripts and documentation'
            ]
        }
        
        summary_file = self.project_root / 'data/analysis/project_cleanup_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Cleanup summary saved to: {summary_file}")
    
    def run_cleanup(self) -> None:
        """Run the complete cleanup process."""
        logger.info("Starting comprehensive project cleanup...")
        logger.info(f"Project root: {self.project_root}")
        
        # Create backup
        self.create_backup()
        
        # Clean redundant data
        self.clean_redundant_data()
        
        # Remove cache and temp files
        self.remove_cache_and_temp_files()
        
        # Organize remaining files
        self.organize_remaining_files()
        
        # Create summary
        self.create_cleanup_summary()
        
        logger.info("Cleanup completed successfully!")
        self.print_summary()
    
    def print_summary(self) -> None:
        """Print cleanup summary."""
        logger.info("CLEANUP SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Files removed: {self.stats['files_removed']}")
        logger.info(f"Directories removed: {self.stats['directories_removed']}")
        logger.info(f"Space freed: {self.stats['space_freed_mb']:.1f} MB")
        logger.info(f"Backup created: {self.backup_dir}")
        logger.info("=" * 50)

def main():
    """Main function to run project cleanup."""
    cleaner = ProjectCleaner()
    
    # Confirm before proceeding
    print("This will clean up the entire project folder.")
    print("A backup will be created before cleanup.")
    print(f"Project root: {cleaner.project_root}")
    
    response = input("Do you want to proceed? (yes/no): ").lower().strip()
    if response in ['yes', 'y']:
        cleaner.run_cleanup()
    else:
        print("Cleanup cancelled.")

if __name__ == "__main__":
    main()

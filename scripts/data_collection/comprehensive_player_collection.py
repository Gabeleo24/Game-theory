#!/usr/bin/env python3
"""
Comprehensive Player Statistics Collection System
Main orchestration script for collecting detailed player statistics from all 67 core Champions League teams.
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
import argparse

# Add src to path for imports
sys.path.append('src')

# Import our collection modules
from player_statistics_collector import PlayerStatisticsCollector
from competition_specific_collector import CompetitionSpecificCollector

# Import validation module
sys.path.append('scripts/analysis')
from player_statistics_validator import PlayerStatisticsValidator

class ComprehensivePlayerCollectionSystem:
    """Orchestrates the complete player statistics collection process."""
    
    def __init__(self, collection_mode='full'):
        """
        Initialize the comprehensive collection system.
        
        Args:
            collection_mode: 'full', 'basic', 'competition_only', or 'validation_only'
        """
        self.collection_mode = collection_mode
        self.setup_logging()
        
        # Collection components
        self.player_collector = None
        self.competition_collector = None
        self.validator = None
        
        # Results tracking
        self.collection_results = {
            'start_time': datetime.now().isoformat(),
            'basic_collection': {},
            'competition_collection': {},
            'validation_results': {},
            'total_api_requests': 0,
            'total_players_collected': 0
        }
        
    def setup_logging(self):
        """Setup logging and output directories."""
        self.log_dir = Path('logs/player_collection')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_log = self.log_dir / f'collection_session_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        print(f"Comprehensive Player Collection System initialized")
        print(f"Collection mode: {self.collection_mode}")
        print(f"Session log: {self.session_log}")
    
    def log_message(self, message):
        """Log message to both console and file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        print(log_entry)
        
        with open(self.session_log, 'a') as f:
            f.write(log_entry + '\n')
    
    def run_basic_player_collection(self, seasons=[2019, 2020, 2021, 2022, 2023]):
        """Run basic player statistics collection for all teams."""
        if self.collection_mode == 'competition_only':
            self.log_message("Skipping basic collection (competition_only mode)")
            return
        
        self.log_message("=" * 60)
        self.log_message("STARTING BASIC PLAYER COLLECTION")
        self.log_message("=" * 60)
        
        try:
            self.player_collector = PlayerStatisticsCollector()
            
            self.log_message(f"Collecting players for {len(self.player_collector.core_teams)} teams")
            self.log_message(f"Seasons: {seasons}")
            
            # Run collection
            total_players = self.player_collector.collect_all_team_players(seasons)
            
            # Save mappings and generate reports
            mapping_data = self.player_collector.save_player_team_mappings()
            api_report = self.player_collector.save_api_usage_report()
            
            # Store results
            self.collection_results['basic_collection'] = {
                'status': 'completed',
                'total_players': total_players,
                'unique_players': mapping_data['total_players'],
                'api_requests': api_report['collection_session']['total_requests'],
                'seasons_processed': seasons,
                'teams_processed': len(self.player_collector.core_teams)
            }
            
            self.collection_results['total_api_requests'] += api_report['collection_session']['total_requests']
            self.collection_results['total_players_collected'] += total_players
            
            self.log_message(f"Basic collection completed successfully!")
            self.log_message(f"Total players collected: {total_players}")
            self.log_message(f"API requests used: {api_report['collection_session']['total_requests']}")
            
        except Exception as e:
            self.log_message(f"Error in basic player collection: {e}")
            self.collection_results['basic_collection'] = {
                'status': 'failed',
                'error': str(e)
            }
            raise
    
    def run_competition_specific_collection(self, seasons=[2022, 2023]):
        """Run competition-specific player statistics collection."""
        if self.collection_mode == 'basic_only':
            self.log_message("Skipping competition-specific collection (basic_only mode)")
            return
        
        self.log_message("=" * 60)
        self.log_message("STARTING COMPETITION-SPECIFIC COLLECTION")
        self.log_message("=" * 60)
        
        try:
            self.competition_collector = CompetitionSpecificCollector()
            
            self.log_message(f"Collecting competition-specific data for seasons: {seasons}")
            
            # Run collection
            total_players = self.competition_collector.collect_all_competitions(seasons)
            
            # Store results
            self.collection_results['competition_collection'] = {
                'status': 'completed',
                'total_players': total_players,
                'api_requests': self.competition_collector.request_count,
                'seasons_processed': seasons,
                'competitions_processed': len(self.competition_collector.competition_configs)
            }
            
            self.collection_results['total_api_requests'] += self.competition_collector.request_count
            self.collection_results['total_players_collected'] += total_players
            
            self.log_message(f"Competition-specific collection completed!")
            self.log_message(f"Total players collected: {total_players}")
            self.log_message(f"API requests used: {self.competition_collector.request_count}")
            
        except Exception as e:
            self.log_message(f"Error in competition-specific collection: {e}")
            self.collection_results['competition_collection'] = {
                'status': 'failed',
                'error': str(e)
            }
            raise
    
    def run_validation_and_integration(self):
        """Run validation and prepare data for Shapley integration."""
        self.log_message("=" * 60)
        self.log_message("STARTING VALIDATION AND INTEGRATION")
        self.log_message("=" * 60)
        
        try:
            self.validator = PlayerStatisticsValidator()
            
            # Run all validations
            self.log_message("Running data quality validation...")
            quality_results = self.validator.validate_data_quality()
            
            self.log_message("Running completeness validation...")
            completeness_results = self.validator.validate_completeness()
            
            self.log_message("Running consistency validation...")
            consistency_results = self.validator.validate_consistency()
            
            self.log_message("Preparing Shapley integration...")
            shapley_data = self.validator.prepare_shapley_integration()
            
            # Generate final validation report
            validation_report = self.validator.generate_validation_report()
            
            # Store results
            self.collection_results['validation_results'] = {
                'status': 'completed',
                'data_quality_score': quality_results.get('validation_rate', 0),
                'completeness_score': {
                    'team_coverage': completeness_results['teams_coverage']['coverage_percentage'],
                    'season_coverage': completeness_results['seasons_coverage']['coverage_percentage']
                },
                'consistency_score': consistency_results.get('consistency_score', 0),
                'shapley_ready_teams': shapley_data and len(shapley_data.get('players_by_team', {})),
                'recommendations_count': len(validation_report.get('recommendations', []))
            }
            
            self.log_message(f"Validation completed successfully!")
            self.log_message(f"Data quality score: {quality_results.get('validation_rate', 0):.2f}%")
            self.log_message(f"Team coverage: {completeness_results['teams_coverage']['coverage_percentage']:.2f}%")
            self.log_message(f"Consistency score: {consistency_results.get('consistency_score', 0):.2f}%")
            
        except Exception as e:
            self.log_message(f"Error in validation: {e}")
            self.collection_results['validation_results'] = {
                'status': 'failed',
                'error': str(e)
            }
            raise
    
    def generate_final_report(self):
        """Generate comprehensive final report."""
        self.log_message("=" * 60)
        self.log_message("GENERATING FINAL REPORT")
        self.log_message("=" * 60)
        
        # Complete collection results
        self.collection_results['end_time'] = datetime.now().isoformat()
        self.collection_results['total_duration'] = str(
            datetime.fromisoformat(self.collection_results['end_time']) - 
            datetime.fromisoformat(self.collection_results['start_time'])
        )
        
        # Calculate summary statistics
        summary = {
            'collection_mode': self.collection_mode,
            'total_api_requests': self.collection_results['total_api_requests'],
            'total_players_collected': self.collection_results['total_players_collected'],
            'collection_duration': self.collection_results['total_duration'],
            'success_rate': self.calculate_success_rate()
        }
        
        self.collection_results['summary'] = summary
        
        # Save final report
        report_file = Path('data/analysis/comprehensive_player_collection_report.json')
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(self.collection_results, f, indent=2, default=str)
        
        self.log_message(f"Final report saved to: {report_file}")
        
        # Print summary
        self.log_message("=" * 60)
        self.log_message("COLLECTION SUMMARY")
        self.log_message("=" * 60)
        self.log_message(f"Collection mode: {summary['collection_mode']}")
        self.log_message(f"Total API requests: {summary['total_api_requests']}")
        self.log_message(f"Total players collected: {summary['total_players_collected']}")
        self.log_message(f"Collection duration: {summary['collection_duration']}")
        self.log_message(f"Success rate: {summary['success_rate']:.2f}%")
        
        return self.collection_results
    
    def calculate_success_rate(self):
        """Calculate overall success rate of the collection process."""
        total_phases = 0
        successful_phases = 0
        
        if self.collection_mode in ['full', 'basic_only']:
            total_phases += 1
            if self.collection_results['basic_collection'].get('status') == 'completed':
                successful_phases += 1
        
        if self.collection_mode in ['full', 'competition_only']:
            total_phases += 1
            if self.collection_results['competition_collection'].get('status') == 'completed':
                successful_phases += 1
        
        if self.collection_mode in ['full', 'validation_only']:
            total_phases += 1
            if self.collection_results['validation_results'].get('status') == 'completed':
                successful_phases += 1
        
        return (successful_phases / total_phases * 100) if total_phases > 0 else 0
    
    def run_comprehensive_collection(self):
        """Run the complete player statistics collection process."""
        self.log_message("STARTING COMPREHENSIVE PLAYER STATISTICS COLLECTION")
        self.log_message(f"Mode: {self.collection_mode}")
        self.log_message(f"Start time: {self.collection_results['start_time']}")
        
        try:
            # Phase 1: Basic player collection
            if self.collection_mode in ['full', 'basic_only']:
                self.run_basic_player_collection()
                time.sleep(2)  # Brief pause between phases
            
            # Phase 2: Competition-specific collection
            if self.collection_mode in ['full', 'competition_only']:
                self.run_competition_specific_collection()
                time.sleep(2)  # Brief pause between phases
            
            # Phase 3: Validation and integration
            if self.collection_mode in ['full', 'validation_only']:
                self.run_validation_and_integration()
            
            # Generate final report
            final_report = self.generate_final_report()
            
            self.log_message("COMPREHENSIVE COLLECTION COMPLETED SUCCESSFULLY!")
            return final_report
            
        except Exception as e:
            self.log_message(f"COLLECTION FAILED: {e}")
            self.generate_final_report()  # Generate report even on failure
            raise

def main():
    """Main execution function with command line arguments."""
    parser = argparse.ArgumentParser(description='Comprehensive Player Statistics Collection System')
    parser.add_argument('--mode', choices=['full', 'basic_only', 'competition_only', 'validation_only'], 
                       default='full', help='Collection mode')
    parser.add_argument('--seasons', nargs='+', type=int, default=[2019, 2020, 2021, 2022, 2023],
                       help='Seasons to collect (for basic collection)')
    parser.add_argument('--comp-seasons', nargs='+', type=int, default=[2022, 2023],
                       help='Seasons for competition-specific collection')
    
    args = parser.parse_args()
    
    print("COMPREHENSIVE PLAYER STATISTICS COLLECTION SYSTEM")
    print("=" * 60)
    print(f"Mode: {args.mode}")
    print(f"Seasons: {args.seasons}")
    print(f"Competition seasons: {args.comp_seasons}")
    print("=" * 60)
    
    try:
        # Initialize and run collection system
        collection_system = ComprehensivePlayerCollectionSystem(collection_mode=args.mode)
        
        # Override seasons if provided
        if args.mode in ['full', 'basic_only']:
            collection_system.basic_seasons = args.seasons
        if args.mode in ['full', 'competition_only']:
            collection_system.competition_seasons = args.comp_seasons
        
        # Run collection
        results = collection_system.run_comprehensive_collection()
        
        print(f"\nCollection completed successfully!")
        print(f"Check the final report for detailed results.")
        
        return 0
        
    except Exception as e:
        print(f"Collection failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

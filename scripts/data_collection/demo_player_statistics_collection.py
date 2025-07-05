#!/usr/bin/env python3
"""
Demonstration Script for Player Statistics Collection System

This script demonstrates how to use the comprehensive player statistics
collection system for the ADS599 Capstone project.

Usage Examples:
1. Collect player data for a single team and season
2. Collect player data for multiple teams
3. Validate collected player data
4. Generate integrated reports
"""

import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import List
import sys

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent))

# Import our modules
from comprehensive_player_statistics_collector import ComprehensivePlayerStatisticsCollector
from player_team_data_integrator import PlayerTeamDataIntegrator
from player_statistics_validator import PlayerStatisticsValidator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_single_team_collection(team_id: int, season: int):
    """Demonstrate collecting player data for a single team and season."""
    logger.info(f"="*70)
    logger.info(f"DEMO: Single Team Player Data Collection")
    logger.info(f"Team ID: {team_id}, Season: {season}")
    logger.info(f"="*70)
    
    # Initialize collector
    collector = ComprehensivePlayerStatisticsCollector()
    
    try:
        # Collect data for the team/season
        logger.info(f"Collecting player data for team {team_id} season {season}...")
        season_data = collector.collect_team_season_player_data(team_id, season)
        
        if season_data:
            # Save the data
            collector.save_team_season_data(team_id, season, season_data)
            
            # Display summary
            match_count = len(season_data.get('match_statistics', []))
            player_count = len(season_data.get('player_season_stats', {}))
            
            logger.info(f"✓ Collection completed successfully!")
            logger.info(f"  Matches processed: {match_count}")
            logger.info(f"  Players tracked: {player_count}")
            
            # Show sample data structure
            if season_data.get('match_statistics'):
                sample_match = season_data['match_statistics'][0]
                player_performances = sample_match.get('player_performances', [])
                logger.info(f"  Sample match: {sample_match.get('fixture_id')}")
                logger.info(f"  Players in sample match: {len(player_performances)}")
                
                if player_performances:
                    sample_player = player_performances[0]
                    logger.info(f"  Sample player: {sample_player['player_info']['player_name']}")
                    logger.info(f"  Sample metrics: {list(sample_player['performance_metrics'].keys())}")
            
            return True
        else:
            logger.warning("No data collected")
            return False
            
    except Exception as e:
        logger.error(f"Collection failed: {e}")
        return False

def demo_multiple_teams_collection(team_ids: List[int], seasons: List[int], max_teams: int = 3):
    """Demonstrate collecting player data for multiple teams."""
    logger.info(f"="*70)
    logger.info(f"DEMO: Multiple Teams Player Data Collection")
    logger.info(f"Teams: {team_ids[:max_teams]}, Seasons: {seasons}")
    logger.info(f"="*70)
    
    # Initialize collector
    collector = ComprehensivePlayerStatisticsCollector()
    
    try:
        # Collect data for multiple teams (limited for demo)
        logger.info(f"Collecting player data for {min(len(team_ids), max_teams)} teams...")
        report = collector.collect_all_teams_player_data(seasons, max_teams)
        
        # Display summary
        logger.info(f"✓ Multi-team collection completed!")
        logger.info(f"  Teams processed: {report['collection_summary']['teams_processed']}")
        logger.info(f"  Seasons processed: {report['collection_summary']['seasons_processed']}")
        logger.info(f"  Matches processed: {report['collection_summary']['matches_processed']}")
        logger.info(f"  Players processed: {report['collection_summary']['players_processed']}")
        logger.info(f"  API requests made: {report['api_usage']['total_requests']}")
        logger.info(f"  Cache efficiency: {report['efficiency_metrics']['api_efficiency']:.1f}%")
        
        return True
        
    except Exception as e:
        logger.error(f"Multi-team collection failed: {e}")
        return False

def demo_data_validation(team_ids: List[int], seasons: List[int]):
    """Demonstrate player data validation."""
    logger.info(f"="*70)
    logger.info(f"DEMO: Player Data Validation")
    logger.info(f"="*70)
    
    # Initialize validator
    validator = PlayerStatisticsValidator()
    
    try:
        # Generate validation report
        logger.info("Generating comprehensive validation report...")
        validation_report = validator.generate_comprehensive_validation_report(
            teams=team_ids[:3],  # Limit for demo
            seasons=seasons
        )
        
        # Display validation summary
        summary = validation_report.get('summary_statistics', {})
        if summary.get('total_validations', 0) > 0:
            logger.info(f"✓ Validation completed!")
            logger.info(f"  Total validations: {summary['total_validations']}")
            logger.info(f"  Average quality score: {summary['average_quality_score']:.2f}")
            logger.info(f"  Quality range: {summary['min_quality_score']:.2f} - {summary['max_quality_score']:.2f}")
            
            # Show recommendations
            recommendations = validation_report.get('recommendations', [])
            if recommendations:
                logger.info(f"  Recommendations:")
                for rec in recommendations[:3]:  # Show first 3
                    logger.info(f"    - {rec}")
        else:
            logger.info("No data available for validation")
        
        return True
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return False

def demo_integration_analysis(team_id: int, season: int):
    """Demonstrate integration between team and player data."""
    logger.info(f"="*70)
    logger.info(f"DEMO: Team-Player Data Integration")
    logger.info(f"Team ID: {team_id}, Season: {season}")
    logger.info(f"="*70)
    
    # Initialize integrator
    integrator = PlayerTeamDataIntegrator()
    
    try:
        # Validate consistency
        logger.info("Validating team-player data consistency...")
        consistency_result = integrator.validate_team_player_consistency(team_id, season)
        
        if consistency_result.get('status') not in ['no_team_data', 'no_player_data']:
            logger.info(f"✓ Consistency validation completed!")
            logger.info(f"  Overall consistency score: {consistency_result['overall_consistency_score']:.2f}")
            logger.info(f"  Fixture consistency: {consistency_result['fixture_consistency']['consistency_score']:.2f}")
            logger.info(f"  Score consistency: {consistency_result['score_consistency']['consistency_score']:.2f}")
            logger.info(f"  Formation consistency: {consistency_result['formation_consistency']['consistency_score']:.2f}")
            
            # Try to generate integrated report for a specific match
            team_stats = integrator._load_team_statistics(team_id, season)
            if team_stats and team_stats.get('match_details'):
                sample_fixture_id = team_stats['match_details'][0].get('fixture_id')
                if sample_fixture_id:
                    logger.info(f"Generating integrated match report for fixture {sample_fixture_id}...")
                    integrated_report = integrator.generate_integrated_match_report(
                        team_id, season, sample_fixture_id
                    )
                    
                    if integrated_report and not integrated_report.get('error'):
                        logger.info(f"✓ Integrated report generated!")
                        logger.info(f"  Match date: {integrated_report['match_basic_info'].get('date', 'N/A')}")
                        logger.info(f"  Venue: {integrated_report['match_basic_info'].get('venue', {}).get('name', 'N/A')}")
                        
                        # Show integration analysis if available
                        analysis = integrated_report.get('integrated_analysis', {})
                        if analysis:
                            logger.info(f"  Integration analysis available: {list(analysis.keys())}")
        else:
            logger.info(f"Consistency validation skipped: {consistency_result.get('status')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Integration analysis failed: {e}")
        return False

def demo_data_structure_exploration():
    """Demonstrate exploring the player data structure."""
    logger.info(f"="*70)
    logger.info(f"DEMO: Player Data Structure Exploration")
    logger.info(f"="*70)
    
    # Look for existing player data
    player_data_dir = Path("data/focused/players")
    
    if not player_data_dir.exists():
        logger.info("No player data directory found")
        return False
    
    # Find available data
    available_teams = []
    available_seasons = set()
    
    for team_dir in player_data_dir.iterdir():
        if team_dir.is_dir() and team_dir.name.startswith('team_'):
            try:
                team_id = int(team_dir.name.replace('team_', ''))
                available_teams.append(team_id)
                
                for season_dir in team_dir.iterdir():
                    if season_dir.is_dir() and season_dir.name.isdigit():
                        available_seasons.add(int(season_dir.name))
            except ValueError:
                continue
    
    logger.info(f"Available player data:")
    logger.info(f"  Teams with data: {len(available_teams)}")
    logger.info(f"  Seasons with data: {sorted(list(available_seasons))}")
    
    if available_teams:
        # Show structure of first available team
        sample_team = available_teams[0]
        sample_season = max(available_seasons) if available_seasons else None
        
        if sample_season:
            sample_file = player_data_dir / f"team_{sample_team}" / str(sample_season) / f"team_{sample_team}_player_match_statistics_{sample_season}.json"
            
            if sample_file.exists():
                try:
                    with open(sample_file, 'r') as f:
                        sample_data = json.load(f)
                    
                    logger.info(f"Sample data structure (Team {sample_team}, Season {sample_season}):")
                    logger.info(f"  Root fields: {list(sample_data.keys())}")
                    
                    match_stats = sample_data.get('match_statistics', [])
                    if match_stats:
                        logger.info(f"  Total matches: {len(match_stats)}")
                        sample_match = match_stats[0]
                        logger.info(f"  Match fields: {list(sample_match.keys())}")
                        
                        player_perfs = sample_match.get('player_performances', [])
                        if player_perfs:
                            logger.info(f"  Players in sample match: {len(player_perfs)}")
                            sample_player = player_perfs[0]
                            logger.info(f"  Player performance fields: {list(sample_player.keys())}")
                            logger.info(f"  Performance metrics: {list(sample_player.get('performance_metrics', {}).keys())}")
                    
                    season_summary = sample_data.get('season_summary', {})
                    if season_summary:
                        logger.info(f"  Season summary fields: {list(season_summary.keys())}")
                    
                    player_season_stats = sample_data.get('player_season_stats', {})
                    logger.info(f"  Players with season stats: {len(player_season_stats)}")
                    
                except Exception as e:
                    logger.error(f"Error reading sample data: {e}")
    
    return True

def main():
    """Main demonstration function."""
    parser = argparse.ArgumentParser(description='Player Statistics Collection System Demo')
    parser.add_argument('--demo', choices=['single', 'multiple', 'validation', 'integration', 'structure', 'all'],
                       default='structure', help='Type of demonstration to run')
    parser.add_argument('--team-id', type=int, default=33, help='Team ID for single team demo')
    parser.add_argument('--season', type=int, default=2025, help='Season for demo')
    parser.add_argument('--max-teams', type=int, default=2, help='Maximum teams for multiple team demo')
    
    args = parser.parse_args()
    
    # Available teams (first few from our dataset)
    available_teams = [33, 34, 40, 42, 47, 49, 50]
    available_seasons = [2019, 2020, 2021, 2022, 2023, 2024]  # Full 2019-2024 range
    
    logger.info("="*70)
    logger.info("PLAYER STATISTICS COLLECTION SYSTEM - DEMONSTRATION")
    logger.info("="*70)
    
    success = True
    
    if args.demo == 'single' or args.demo == 'all':
        success &= demo_single_team_collection(args.team_id, args.season)
        if args.demo == 'all':
            logger.info("\n")
    
    if args.demo == 'multiple' or args.demo == 'all':
        success &= demo_multiple_teams_collection(available_teams, available_seasons, args.max_teams)
        if args.demo == 'all':
            logger.info("\n")
    
    if args.demo == 'validation' or args.demo == 'all':
        success &= demo_data_validation(available_teams, available_seasons)
        if args.demo == 'all':
            logger.info("\n")
    
    if args.demo == 'integration' or args.demo == 'all':
        success &= demo_integration_analysis(args.team_id, args.season)
        if args.demo == 'all':
            logger.info("\n")
    
    if args.demo == 'structure' or args.demo == 'all':
        success &= demo_data_structure_exploration()
    
    logger.info("\n" + "="*70)
    logger.info("DEMONSTRATION COMPLETED")
    logger.info("="*70)
    
    if success:
        logger.info("✓ All demonstrations completed successfully!")
        logger.info("\nNext Steps:")
        logger.info("1. Run full collection: python comprehensive_player_statistics_collector.py --seasons 2025")
        logger.info("2. Validate data: python player_statistics_validator.py")
        logger.info("3. Generate reports: python player_team_data_integrator.py")
    else:
        logger.warning("⚠ Some demonstrations encountered issues")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

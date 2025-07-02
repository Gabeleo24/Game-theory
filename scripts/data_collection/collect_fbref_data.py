#!/usr/bin/env python3
"""
FBref Data Collection for Soccer Intelligence System

Collects comprehensive football data from FBref.com for analysis including:
- League tables and standings
- Detailed player statistics (goals, assists, xG, xA, etc.)
- Team performance metrics
- Advanced statistics for Shapley value analysis

This script is designed to complement API-Football data with detailed statistical analysis.
"""

import sys
import os
from pathlib import Path
import argparse
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.soccer_intelligence.data_collection.fbref import FBrefCollector
import pandas as pd


class FBrefDataCollector:
    """Comprehensive FBref data collector for Soccer Intelligence System"""
    
    def __init__(self, cache_dir: str = "data/raw/fbref"):
        self.collector = FBrefCollector(cache_dir=cache_dir)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Major European leagues for comprehensive analysis
        self.major_leagues = {
            "Premier League": "/en/comps/9/Premier-League-Stats",
            "La Liga": "/en/comps/12/La-Liga-Stats", 
            "Serie A": "/en/comps/11/Serie-A-Stats",
            "Bundesliga": "/en/comps/20/Bundesliga-Stats",
            "Ligue 1": "/en/comps/13/Ligue-1-Stats"
        }
        
        # Statistics types for comprehensive analysis
        self.stat_types = {
            "standard": "stats",
            "shooting": "shooting", 
            "passing": "passing",
            "defense": "defense",
            "possession": "possession",
            "goalkeeping": "keepers",
            "advanced_goalkeeping": "keepersadv"
        }
    
    def collect_league_data(self, league_name: str, league_url: str, season: str = "2024-2025"):
        """
        Collect comprehensive data for a specific league
        
        Args:
            league_name: Name of the league
            league_url: FBref URL for the league
            season: Season string
        """
        print(f"\n=== Collecting {league_name} Data ===")
        
        # Create league-specific directory
        league_dir = self.cache_dir / league_name.lower().replace(" ", "_")
        league_dir.mkdir(exist_ok=True)
        
        # Collect league table
        print(f"Collecting {league_name} table...")
        table_df = self.collector.get_league_table(league_url, season)
        if table_df is not None:
            filename = f"{league_name.lower().replace(' ', '_')}_table_{season.replace('-', '_')}.csv"
            self.collector.save_data(table_df, filename)
            print(f"✓ League table saved: {len(table_df)} teams")
        else:
            print("✗ Failed to collect league table")
        
        # Collect player statistics
        for stat_name, stat_type in self.stat_types.items():
            print(f"Collecting {league_name} {stat_name} stats...")
            
            stats_df = self.collector.get_player_stats(league_url, stat_type)
            if stats_df is not None:
                filename = f"{league_name.lower().replace(' ', '_')}_{stat_name}_stats_{season.replace('-', '_')}.csv"
                self.collector.save_data(stats_df, filename)
                print(f"✓ {stat_name.capitalize()} stats saved: {len(stats_df)} players")
            else:
                print(f"✗ Failed to collect {stat_name} stats")
        
        # Collect team statistics
        print(f"Collecting {league_name} team stats...")
        team_stats = self.collector.get_team_stats(league_url, "stats")
        if team_stats is not None:
            filename = f"{league_name.lower().replace(' ', '_')}_team_stats_{season.replace('-', '_')}.csv"
            self.collector.save_data(team_stats, filename)
            print(f"✓ Team stats saved: {len(team_stats)} teams")
        else:
            print("✗ Failed to collect team stats")
    
    def collect_major_leagues_data(self, season: str = "2024-2025"):
        """Collect data for all major European leagues"""
        print("Collecting data for major European leagues...")
        print("This will take some time due to respectful rate limiting")
        
        for league_name, league_url in self.major_leagues.items():
            try:
                self.collect_league_data(league_name, league_url, season)
            except Exception as e:
                print(f"Error collecting {league_name} data: {e}")
                continue
    
    def collect_champions_league_data(self, season: str = "2024-2025"):
        """Collect UEFA Champions League data"""
        print("\n=== Collecting Champions League Data ===")
        
        champions_league_url = "/en/comps/8/Champions-League-Stats"
        
        try:
            # Collect group stage table
            print("Collecting Champions League group data...")
            table_df = self.collector.get_league_table(champions_league_url, season)
            if table_df is not None:
                filename = f"champions_league_table_{season.replace('-', '_')}.csv"
                self.collector.save_data(table_df, filename)
                print(f"✓ Champions League table saved: {len(table_df)} teams")
            
            # Collect player stats
            for stat_name, stat_type in self.stat_types.items():
                print(f"Collecting Champions League {stat_name} stats...")
                
                stats_df = self.collector.get_player_stats(champions_league_url, stat_type)
                if stats_df is not None:
                    filename = f"champions_league_{stat_name}_stats_{season.replace('-', '_')}.csv"
                    self.collector.save_data(stats_df, filename)
                    print(f"✓ {stat_name.capitalize()} stats saved: {len(stats_df)} players")
                    
        except Exception as e:
            print(f"Error collecting Champions League data: {e}")
    
    def generate_collection_summary(self):
        """Generate a summary of collected data"""
        print("\n=== Data Collection Summary ===")
        
        summary = {
            "collection_date": datetime.now().isoformat(),
            "files_collected": [],
            "total_files": 0,
            "leagues_covered": list(self.major_leagues.keys()) + ["Champions League"]
        }
        
        # Count collected files
        for file_path in self.cache_dir.glob("*.csv"):
            file_info = {
                "filename": file_path.name,
                "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            summary["files_collected"].append(file_info)
        
        summary["total_files"] = len(summary["files_collected"])
        
        # Save summary
        summary_file = self.cache_dir / "collection_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Total files collected: {summary['total_files']}")
        print(f"Summary saved to: {summary_file}")
        
        return summary
    
    def close(self):
        """Close the collector"""
        self.collector.close()


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Collect FBref data for Soccer Intelligence System")
    parser.add_argument("--league", type=str, help="Specific league to collect (e.g., 'Premier League')")
    parser.add_argument("--season", type=str, default="2024-2025", help="Season to collect (default: 2024-2025)")
    parser.add_argument("--champions-league", action="store_true", help="Collect Champions League data")
    parser.add_argument("--all", action="store_true", help="Collect all major leagues data")
    parser.add_argument("--cache-dir", type=str, default="data/raw/fbref", help="Cache directory")
    
    args = parser.parse_args()
    
    print("FBref Data Collection for Soccer Intelligence System")
    print("=" * 60)
    print(f"Season: {args.season}")
    print(f"Cache directory: {args.cache_dir}")
    print()
    
    collector = FBrefDataCollector(cache_dir=args.cache_dir)
    
    try:
        if args.league:
            # Collect specific league
            if args.league in collector.major_leagues:
                league_url = collector.major_leagues[args.league]
                collector.collect_league_data(args.league, league_url, args.season)
            else:
                print(f"League '{args.league}' not found in major leagues")
                print(f"Available leagues: {list(collector.major_leagues.keys())}")
                return
        
        elif args.champions_league:
            # Collect Champions League data
            collector.collect_champions_league_data(args.season)
        
        elif args.all:
            # Collect all major leagues
            collector.collect_major_leagues_data(args.season)
            collector.collect_champions_league_data(args.season)
        
        else:
            # Default: collect Premier League and La Liga (most relevant for your project)
            print("No specific collection specified. Collecting Premier League and La Liga data...")
            collector.collect_league_data("Premier League", collector.major_leagues["Premier League"], args.season)
            collector.collect_league_data("La Liga", collector.major_leagues["La Liga"], args.season)
        
        # Generate summary
        summary = collector.generate_collection_summary()
        
        print("\n" + "=" * 60)
        print("Data collection completed successfully!")
        print(f"Check {args.cache_dir} for collected data files")
        
    except KeyboardInterrupt:
        print("\nCollection interrupted by user")
    except Exception as e:
        print(f"\nCollection failed with error: {e}")
    finally:
        collector.close()


if __name__ == "__main__":
    main()

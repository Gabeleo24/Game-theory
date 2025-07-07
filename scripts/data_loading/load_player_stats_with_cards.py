#!/usr/bin/env python3
"""
Load Player Statistics with Cards Data
Simple script to load player statistics including yellow and red cards
directly into the database without complex constraints.
"""

import json
import psycopg2
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlayerStatsLoader:
    """Load player statistics with card data."""
    
    def __init__(self):
        """Initialize the loader."""
        self.db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'soccer_intelligence',
            'user': 'soccerapp',
            'password': 'soccerpass123'
        }
        self.players_dir = Path("data/focused/players")
        self.conn = None
        
        # Statistics tracking
        self.stats = {
            'player_stats_loaded': 0,
            'yellow_cards_total': 0,
            'red_cards_total': 0,
            'errors': 0
        }
    
    def connect_to_database(self):
        """Connect to PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.conn.autocommit = True  # Use autocommit to avoid transaction issues
            logger.info("Connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def load_player_season_stats(self, player_data: Dict[str, Any]) -> None:
        """Load player season statistics including cards."""
        try:
            team_context = player_data.get('team_context', {})
            team_id = team_context.get('team_id')
            season = team_context.get('season')
            
            player_info = player_data.get('player_info', {})
            player_id = player_info.get('id')
            
            if not team_id or not season or not player_id:
                return
            
            # Get aggregated statistics
            aggregated_stats = player_data.get('aggregated_stats', {})
            season_summary = player_data.get('season_summary', {})
            
            if not aggregated_stats:
                return
            
            # Extract card information
            yellow_cards = aggregated_stats.get('total_yellow_cards', 0)
            red_cards = aggregated_stats.get('total_red_cards', 0)
            
            # Extract other statistics
            minutes = aggregated_stats.get('total_minutes', 0)
            goals = aggregated_stats.get('total_goals', 0)
            assists = aggregated_stats.get('total_assists', 0)
            rating = aggregated_stats.get('average_rating', None)
            
            # Get position from season summary
            position = season_summary.get('primary_position', '') if season_summary else ''
            
            # Insert player statistics (simple insert without ON CONFLICT)
            cursor = self.conn.cursor()
            
            # First check if record exists
            cursor.execute("""
                SELECT COUNT(*) FROM player_statistics 
                WHERE player_id = %s AND team_id = %s AND season_year = %s
            """, (player_id, team_id, season))
            
            exists = cursor.fetchone()[0] > 0
            
            if not exists:
                cursor.execute("""
                    INSERT INTO player_statistics (
                        player_id, team_id, season_year, position,
                        minutes_played, goals, assists, yellow_cards, red_cards, rating
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    player_id, team_id, season, position,
                    minutes, goals, assists, yellow_cards, red_cards, rating
                ))
                
                self.stats['player_stats_loaded'] += 1
                self.stats['yellow_cards_total'] += yellow_cards
                self.stats['red_cards_total'] += red_cards
            
        except Exception as e:
            logger.error(f"Error loading player season stats: {e}")
            self.stats['errors'] += 1
    
    def load_all_player_stats(self) -> None:
        """Load all player statistics from JSON files."""
        logger.info("Starting to load player statistics with card information...")
        
        individual_stats_dir = self.players_dir / "individual_stats"
        
        if not individual_stats_dir.exists():
            logger.error(f"Individual stats directory not found: {individual_stats_dir}")
            return
        
        processed_count = 0
        
        # Process each team directory
        for team_dir in individual_stats_dir.iterdir():
            if not team_dir.is_dir():
                continue
                
            logger.info(f"Processing team directory: {team_dir.name}")
            
            # Process each season directory
            for season_dir in team_dir.iterdir():
                if not season_dir.is_dir():
                    continue
                    
                logger.info(f"  Processing season: {season_dir.name}")
                
                # Process each player file
                for player_file in season_dir.glob("*.json"):
                    try:
                        with open(player_file, 'r', encoding='utf-8') as f:
                            player_data = json.load(f)
                        
                        # Load player season statistics including cards
                        self.load_player_season_stats(player_data)
                        
                        processed_count += 1
                        
                        # Log progress every 100 players
                        if processed_count % 100 == 0:
                            logger.info(f"    Processed {processed_count} player files...")
                            
                    except Exception as e:
                        logger.error(f"Error processing file {player_file}: {e}")
                        self.stats['errors'] += 1
        
        logger.info("Player statistics loading completed!")
    
    def print_statistics(self) -> None:
        """Print loading statistics."""
        logger.info("PLAYER STATISTICS LOADING RESULTS")
        logger.info("=" * 45)
        logger.info(f"Player season statistics loaded: {self.stats['player_stats_loaded']}")
        logger.info(f"Total yellow cards: {self.stats['yellow_cards_total']}")
        logger.info(f"Total red cards: {self.stats['red_cards_total']}")
        logger.info(f"Errors encountered: {self.stats['errors']}")
    
    def close_connection(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

def main():
    """Main function to load player statistics with cards."""
    logger.info("Starting Player Statistics with Cards Loading...")
    
    loader = PlayerStatsLoader()
    
    try:
        # Connect to database
        if not loader.connect_to_database():
            return
        
        # Load all player statistics
        loader.load_all_player_stats()
        
        # Print statistics
        loader.print_statistics()
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
    finally:
        loader.close_connection()

if __name__ == "__main__":
    main()

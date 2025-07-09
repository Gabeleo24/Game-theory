#!/usr/bin/env python3
"""
SportMonks API Data Collector for Real Madrid 2023-2024 Season
Automated data collection service with rate limiting and error handling
"""

import os
import sys
import time
import logging
import requests
import psycopg2
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/sportmonks_collector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SportMonksCollector:
    """Automated SportMonks API data collector for Real Madrid 2023-2024 season."""
    
    def __init__(self):
        """Initialize collector with configuration."""
        self.api_token = os.getenv('SPORTMONKS_API_KEY')
        self.base_url = "https://api.sportmonks.com/v3/football"
        self.real_madrid_id = 53  # SportMonks team ID for Real Madrid
        self.season_2023_id = 21646  # 2023-2024 season ID
        
        # Rate limiting configuration
        self.rate_limit_delay = 1.0  # Seconds between requests
        self.max_retries = 3
        self.retry_delay = 5.0
        
        # Database connection
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'postgres'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'soccer_intelligence'),
            'user': os.getenv('POSTGRES_USER', 'soccerapp'),
            'password': os.getenv('POSTGRES_PASSWORD', 'soccerpass123')
        }
        
        # Collection statistics
        self.stats = {
            'teams_collected': 0,
            'players_collected': 0,
            'matches_collected': 0,
            'player_stats_collected': 0,
            'api_calls_made': 0,
            'errors_encountered': 0,
            'start_time': None,
            'collection_id': None
        }
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        self.session = requests.Session()
        self.conn = None
        self.cursor = None
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.cleanup()
        sys.exit(0)
    
    def connect_database(self) -> bool:
        """Connect to PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logger.info("✅ Database connected successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def start_collection_session(self) -> int:
        """Start a new collection session and return collection ID."""
        try:
            query = """
                INSERT INTO api_collection_metadata 
                (collection_type, api_source, collection_status, notes)
                VALUES (%s, %s, %s, %s)
                RETURNING collection_id
            """
            self.cursor.execute(query, (
                'REAL_MADRID_2023_2024_FULL_COLLECTION',
                'SportMonks',
                'IN_PROGRESS',
                'Automated collection of Real Madrid 2023-2024 season data'
            ))
            collection_id = self.cursor.fetchone()[0]
            self.conn.commit()
            
            self.stats['collection_id'] = collection_id
            self.stats['start_time'] = datetime.now()
            
            logger.info(f"🚀 Started collection session: {collection_id}")
            return collection_id
            
        except Exception as e:
            logger.error(f"❌ Failed to start collection session: {e}")
            return None
    
    def make_api_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make rate-limited API request with error handling."""
        if params is None:
            params = {}
        
        params['api_token'] = self.api_token
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
                response = self.session.get(url, params=params, timeout=30)
                self.stats['api_calls_made'] += 1
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check rate limit headers
                    if 'X-RateLimit-Remaining' in response.headers:
                        remaining = int(response.headers['X-RateLimit-Remaining'])
                        if remaining < 10:
                            logger.warning(f"⚠️ Low rate limit remaining: {remaining}")
                            time.sleep(5)  # Extra delay when approaching limit
                    
                    return data
                
                elif response.status_code == 429:
                    # Rate limit exceeded
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"⚠️ Rate limit exceeded, waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                
                else:
                    logger.error(f"❌ API request failed: {response.status_code} - {response.text}")
                    
            except Exception as e:
                logger.error(f"❌ API request error (attempt {attempt + 1}): {e}")
                
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (attempt + 1))
        
        self.stats['errors_encountered'] += 1
        return None
    
    def collect_team_data(self) -> bool:
        """Collect Real Madrid team information."""
        logger.info("📊 Collecting team data...")
        
        try:
            # Get Real Madrid team details
            data = self.make_api_request(f"teams/{self.real_madrid_id}")
            if not data or 'data' not in data:
                logger.error("❌ Failed to get team data")
                return False
            
            team_data = data['data']
            
            # Insert/update team data
            query = """
                INSERT INTO teams (
                    sportmonks_team_id, team_name, short_name, country,
                    founded_year, venue_name, venue_city, logo_url
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sportmonks_team_id) 
                DO UPDATE SET
                    team_name = EXCLUDED.team_name,
                    short_name = EXCLUDED.short_name,
                    country = EXCLUDED.country,
                    founded_year = EXCLUDED.founded_year,
                    venue_name = EXCLUDED.venue_name,
                    venue_city = EXCLUDED.venue_city,
                    logo_url = EXCLUDED.logo_url,
                    updated_at = CURRENT_TIMESTAMP
            """
            
            venue = team_data.get('venue', {}) or {}
            
            self.cursor.execute(query, (
                team_data.get('id'),
                team_data.get('name'),
                team_data.get('short_code'),
                team_data.get('country', {}).get('name') if team_data.get('country') else None,
                team_data.get('founded'),
                venue.get('name'),
                venue.get('city_name'),
                team_data.get('image_path')
            ))
            
            self.conn.commit()
            self.stats['teams_collected'] += 1
            
            logger.info(f"✅ Team data collected: {team_data.get('name')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error collecting team data: {e}")
            return False
    
    def collect_squad_data(self) -> bool:
        """Collect Real Madrid squad information."""
        logger.info("👥 Collecting squad data...")
        
        try:
            # Get squad for 2023-2024 season
            data = self.make_api_request(
                f"squads/seasons/{self.season_2023_id}/teams/{self.real_madrid_id}",
                {'include': 'player.person,player.position,player.nationality'}
            )
            
            if not data or 'data' not in data:
                logger.error("❌ Failed to get squad data")
                return False
            
            squad_data = data['data']
            players = squad_data.get('players', [])
            
            # Get team_id from database
            self.cursor.execute("SELECT team_id FROM teams WHERE sportmonks_team_id = %s", (self.real_madrid_id,))
            team_id = self.cursor.fetchone()[0]
            
            for player_data in players:
                player = player_data.get('player', {})
                person = player.get('person', {})
                position = player.get('position', {})
                nationality = player.get('nationality', {})
                
                # Insert/update player data
                query = """
                    INSERT INTO players (
                        sportmonks_player_id, player_name, display_name, first_name, last_name,
                        birth_date, nationality, height, weight, position, jersey_number, team_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (sportmonks_player_id)
                    DO UPDATE SET
                        player_name = EXCLUDED.player_name,
                        display_name = EXCLUDED.display_name,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        birth_date = EXCLUDED.birth_date,
                        nationality = EXCLUDED.nationality,
                        height = EXCLUDED.height,
                        weight = EXCLUDED.weight,
                        position = EXCLUDED.position,
                        jersey_number = EXCLUDED.jersey_number,
                        team_id = EXCLUDED.team_id,
                        updated_at = CURRENT_TIMESTAMP
                """
                
                # Parse birth date
                birth_date = None
                if person.get('date_of_birth'):
                    try:
                        birth_date = datetime.strptime(person['date_of_birth'], '%Y-%m-%d').date()
                    except:
                        pass
                
                self.cursor.execute(query, (
                    player.get('id'),
                    person.get('name'),
                    person.get('display_name'),
                    person.get('firstname'),
                    person.get('lastname'),
                    birth_date,
                    nationality.get('name'),
                    person.get('height'),
                    person.get('weight'),
                    position.get('name'),
                    player_data.get('jersey_number'),
                    team_id
                ))
                
                self.stats['players_collected'] += 1
            
            self.conn.commit()
            logger.info(f"✅ Squad data collected: {len(players)} players")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error collecting squad data: {e}")
            return False
    
    def collect_matches_data(self) -> List[int]:
        """Collect Real Madrid matches for 2023-2024 season."""
        logger.info("⚽ Collecting matches data...")
        
        try:
            # Get Real Madrid fixtures for 2023-2024 season
            data = self.make_api_request(
                "fixtures",
                {
                    'filters': f'teamIds:{self.real_madrid_id};seasonIds:{self.season_2023_id}',
                    'include': 'league,season,participants,venue,referee',
                    'per_page': 100
                }
            )
            
            if not data or 'data' not in data:
                logger.error("❌ Failed to get matches data")
                return []
            
            matches = data['data']
            match_ids = []
            
            for match in matches:
                try:
                    # Insert match data
                    match_id = self.insert_match_data(match)
                    if match_id:
                        match_ids.append(match_id)
                        self.stats['matches_collected'] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error processing match {match.get('id')}: {e}")
                    continue
            
            self.conn.commit()
            logger.info(f"✅ Matches data collected: {len(match_ids)} matches")
            return match_ids
            
        except Exception as e:
            logger.error(f"❌ Error collecting matches data: {e}")
            return []

    def insert_match_data(self, match: Dict) -> Optional[int]:
        """Insert match data into database."""
        try:
            league = match.get('league', {})
            season = match.get('season', {})
            participants = match.get('participants', [])
            venue = match.get('venue', {})
            referee = match.get('referee', {})

            # Get team IDs
            home_team_id = None
            away_team_id = None

            for participant in participants:
                if participant.get('meta', {}).get('location') == 'home':
                    home_team_id = participant.get('id')
                elif participant.get('meta', {}).get('location') == 'away':
                    away_team_id = participant.get('id')

            # Parse match date
            match_date = None
            if match.get('starting_at'):
                try:
                    match_date = datetime.fromisoformat(match['starting_at'].replace('Z', '+00:00'))
                except:
                    pass

            # Insert match
            query = """
                INSERT INTO matches (
                    sportmonks_match_id, season_id, home_team_id, away_team_id,
                    match_date, match_week, round_name, match_status,
                    venue_name, venue_city, referee_name, attendance
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sportmonks_match_id) DO NOTHING
                RETURNING match_id
            """

            self.cursor.execute(query, (
                match.get('id'),
                season.get('id'),
                home_team_id,
                away_team_id,
                match_date,
                match.get('round_id'),
                match.get('round', {}).get('name'),
                match.get('state', {}).get('short_name'),
                venue.get('name'),
                venue.get('city_name'),
                referee.get('common_name'),
                match.get('attendance')
            ))

            result = self.cursor.fetchone()
            return result[0] if result else None

        except Exception as e:
            logger.error(f"❌ Error inserting match data: {e}")
            return None

    def collect_all_player_stats(self, match_ids: List[int]) -> bool:
        """Collect player statistics for all matches."""
        logger.info(f"📈 Collecting player statistics for {len(match_ids)} matches...")

        success_count = 0

        for i, match_id in enumerate(match_ids):
            try:
                if self.collect_match_player_stats(match_id):
                    success_count += 1

                # Progress update every 10 matches
                if (i + 1) % 10 == 0:
                    logger.info(f"   Progress: {i + 1}/{len(match_ids)} matches processed")

                # Small delay between matches
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"❌ Error collecting stats for match {match_id}: {e}")
                continue

        logger.info(f"✅ Player statistics collected for {success_count}/{len(match_ids)} matches")
        return success_count > 0

    def collect_match_player_stats(self, sportmonks_match_id: int) -> bool:
        """Collect player statistics for a specific match."""
        try:
            # Get match statistics
            data = self.make_api_request(
                f"fixtures/{sportmonks_match_id}",
                {'include': 'statistics.player.person,statistics.type'}
            )

            if not data or 'data' not in data:
                return False

            match_data = data['data']
            statistics = match_data.get('statistics', [])

            # Get internal match_id
            self.cursor.execute(
                "SELECT match_id FROM matches WHERE sportmonks_match_id = %s",
                (sportmonks_match_id,)
            )
            result = self.cursor.fetchone()
            if not result:
                return False

            match_id = result[0]

            # Process player statistics
            player_stats = {}

            for stat in statistics:
                player = stat.get('player', {})
                stat_type = stat.get('type', {})

                player_id = player.get('id')
                stat_name = stat_type.get('name', '').lower().replace(' ', '_')
                stat_value = stat.get('value', 0)

                if player_id not in player_stats:
                    player_stats[player_id] = {
                        'player_id': player_id,
                        'team_id': stat.get('team_id'),
                        'position': stat.get('position'),
                        'jersey_number': stat.get('jersey_number')
                    }

                player_stats[player_id][stat_name] = stat_value

            # Insert player statistics
            for player_id, stats in player_stats.items():
                self.insert_player_match_stats(match_id, stats)
                self.stats['player_stats_collected'] += 1

            return True

        except Exception as e:
            logger.error(f"❌ Error collecting match player stats: {e}")
            return False

    def insert_player_match_stats(self, match_id: int, stats: Dict):
        """Insert player match statistics."""
        try:
            # Get internal player_id
            self.cursor.execute(
                "SELECT player_id FROM players WHERE sportmonks_player_id = %s",
                (stats['player_id'],)
            )
            result = self.cursor.fetchone()
            if not result:
                return

            player_id = result[0]

            query = """
                INSERT INTO match_player_stats (
                    match_id, player_id, team_id, position, jersey_number,
                    minutes_played, goals, assists, shots_total, shots_on_target,
                    passes_total, passes_completed, pass_accuracy, tackles_total,
                    interceptions, fouls_committed, fouls_drawn, yellow_cards,
                    red_cards, rating, expected_goals, expected_assists
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (match_id, player_id) DO UPDATE SET
                    minutes_played = EXCLUDED.minutes_played,
                    goals = EXCLUDED.goals,
                    assists = EXCLUDED.assists,
                    shots_total = EXCLUDED.shots_total,
                    shots_on_target = EXCLUDED.shots_on_target,
                    passes_total = EXCLUDED.passes_total,
                    passes_completed = EXCLUDED.passes_completed,
                    pass_accuracy = EXCLUDED.pass_accuracy,
                    tackles_total = EXCLUDED.tackles_total,
                    interceptions = EXCLUDED.interceptions,
                    fouls_committed = EXCLUDED.fouls_committed,
                    fouls_drawn = EXCLUDED.fouls_drawn,
                    yellow_cards = EXCLUDED.yellow_cards,
                    red_cards = EXCLUDED.red_cards,
                    rating = EXCLUDED.rating,
                    expected_goals = EXCLUDED.expected_goals,
                    expected_assists = EXCLUDED.expected_assists,
                    updated_at = CURRENT_TIMESTAMP
            """

            self.cursor.execute(query, (
                match_id,
                player_id,
                stats.get('team_id'),
                stats.get('position'),
                stats.get('jersey_number'),
                stats.get('minutes_played', 0),
                stats.get('goals', 0),
                stats.get('assists', 0),
                stats.get('shots_total', 0),
                stats.get('shots_on_target', 0),
                stats.get('passes_total', 0),
                stats.get('passes_completed', 0),
                stats.get('pass_accuracy', 0),
                stats.get('tackles_total', 0),
                stats.get('interceptions', 0),
                stats.get('fouls_committed', 0),
                stats.get('fouls_drawn', 0),
                stats.get('yellow_cards', 0),
                stats.get('red_cards', 0),
                stats.get('rating', 0),
                stats.get('expected_goals', 0),
                stats.get('expected_assists', 0)
            ))

        except Exception as e:
            logger.error(f"❌ Error inserting player stats: {e}")

    def finish_collection_session(self, success: bool, error_message: str = None):
        """Finish collection session and update metadata."""
        try:
            end_time = datetime.now()
            duration = (end_time - self.stats['start_time']).total_seconds()

            status = 'COMPLETED' if success else 'FAILED'

            query = """
                UPDATE api_collection_metadata SET
                    collection_status = %s,
                    records_collected = %s,
                    records_failed = %s,
                    collection_duration_seconds = %s,
                    error_messages = %s,
                    notes = %s
                WHERE collection_id = %s
            """

            notes = f"Teams: {self.stats['teams_collected']}, Players: {self.stats['players_collected']}, Matches: {self.stats['matches_collected']}, Player Stats: {self.stats['player_stats_collected']}, API Calls: {self.stats['api_calls_made']}"

            self.cursor.execute(query, (
                status,
                self.stats['teams_collected'] + self.stats['players_collected'] + self.stats['matches_collected'] + self.stats['player_stats_collected'],
                self.stats['errors_encountered'],
                int(duration),
                error_message,
                notes,
                self.stats['collection_id']
            ))

            self.conn.commit()
            logger.info(f"✅ Collection session finished: {status}")

        except Exception as e:
            logger.error(f"❌ Error finishing collection session: {e}")

    def display_collection_summary(self):
        """Display collection summary."""
        duration = (datetime.now() - self.stats['start_time']).total_seconds()

        print("\n" + "="*80)
        print("🏆 REAL MADRID 2023-2024 DATA COLLECTION SUMMARY 🏆")
        print("="*80)
        print(f"Collection ID: {self.stats['collection_id']}")
        print(f"Duration: {duration:.1f} seconds")
        print(f"API Calls Made: {self.stats['api_calls_made']}")
        print(f"Teams Collected: {self.stats['teams_collected']}")
        print(f"Players Collected: {self.stats['players_collected']}")
        print(f"Matches Collected: {self.stats['matches_collected']}")
        print(f"Player Statistics: {self.stats['player_stats_collected']}")
        print(f"Errors Encountered: {self.stats['errors_encountered']}")
        print("="*80)

    def cleanup(self):
        """Clean up resources."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        if self.session:
            self.session.close()
        logger.info("🧹 Cleanup completed")

def main():
    """Main collection process."""
    collector = SportMonksCollector()
    
    logger.info("🏆 Starting Real Madrid 2023-2024 data collection...")
    
    # Connect to database
    if not collector.connect_database():
        sys.exit(1)
    
    # Start collection session
    collection_id = collector.start_collection_session()
    if not collection_id:
        sys.exit(1)
    
    try:
        # Collect data in sequence
        success = True
        
        # 1. Collect team data
        if not collector.collect_team_data():
            success = False
        
        # 2. Collect squad data
        if not collector.collect_squad_data():
            success = False
        
        # 3. Collect matches data
        match_ids = collector.collect_matches_data()
        if not match_ids:
            success = False
        
        # 4. Collect player statistics for each match
        if match_ids:
            collector.collect_all_player_stats(match_ids)
        
        # Update collection status
        collector.finish_collection_session(success)
        
        # Display final statistics
        collector.display_collection_summary()
        
    except Exception as e:
        logger.error(f"❌ Collection failed: {e}")
        collector.finish_collection_session(False, str(e))
        sys.exit(1)
    
    finally:
        collector.cleanup()

if __name__ == "__main__":
    main()

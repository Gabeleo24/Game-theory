#!/usr/bin/env python3
"""
Real Madrid 2023-2024 Season Data Collector
Specialized collector using only SportMonks API for comprehensive match-level player statistics
Target: Real Madrid (SportMonks team ID: 53), Season: 2023-2024 (SportMonks season ID: 23087)
"""

import asyncio
import aiohttp
import yaml
import json
import logging
import time
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CollectionStats:
    """Track collection statistics."""
    matches_collected: int = 0
    players_collected: int = 0
    statistics_collected: int = 0
    api_requests: int = 0
    errors: int = 0
    start_time: datetime = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()

class RealMadridCollector:
    """Specialized collector for Real Madrid 2023-2024 season data."""
    
    # Constants
    REAL_MADRID_TEAM_ID = 53
    SEASON_2023_2024_ID = 23087
    SEASON_NAME = "2023-2024"
    
    def __init__(self, config_path: str = "config"):
        """Initialize the Real Madrid collector."""
        self.config_path = Path(config_path)
        self.load_configuration()
        self.setup_database_connection()
        self.stats = CollectionStats()
        self.api_call_times = []
        
    def load_configuration(self):
        """Load SportMonks API configuration."""
        try:
            config_file = self.config_path / "api_keys.yaml"
            if not config_file.exists():
                config_file = Path(__file__).parent.parent / "config" / "api_keys.yaml"
            
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            self.sportmonks_config = config['sportmonks']
            self.db_config = config['database']
            
            self.api_token = self.sportmonks_config['api_key']
            self.base_url = self.sportmonks_config['base_url']
            
            logger.info("✅ Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            raise
    
    def setup_database_connection(self):
        """Setup PostgreSQL database connection."""
        try:
            self.db_conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['name'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            self.db_conn.autocommit = False
            self.db_cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            
            logger.info("✅ Database connection established")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            raise
    
    def start_collection_session(self) -> int:
        """Start a new collection session."""
        try:
            query = """
                INSERT INTO data_collection_log 
                (collection_type, target_description, start_time, status)
                VALUES (%s, %s, %s, %s)
                RETURNING log_id
            """
            
            self.db_cursor.execute(query, (
                'REAL_MADRID_FULL_SEASON',
                f'Real Madrid 2023-2024 season - all matches and player statistics',
                datetime.now(),
                'IN_PROGRESS'
            ))
            
            log_id = self.db_cursor.fetchone()[0]
            self.db_conn.commit()
            
            logger.info(f"🚀 Started collection session: {log_id}")
            return log_id
            
        except Exception as e:
            logger.error(f"❌ Failed to start collection session: {e}")
            self.db_conn.rollback()
            raise
    
    async def check_rate_limit(self):
        """Check and enforce SportMonks rate limiting (3000 requests/hour)."""
        now = time.time()
        # Keep only requests from the last hour
        self.api_call_times = [t for t in self.api_call_times if now - t < 3600]
        
        if len(self.api_call_times) >= 2900:  # Leave some buffer
            wait_time = 3600 - (now - self.api_call_times[0])
            if wait_time > 0:
                logger.warning(f"⏳ Rate limit approaching, waiting {wait_time:.1f} seconds...")
                await asyncio.sleep(wait_time)
    
    async def make_sportmonks_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to SportMonks API with rate limiting."""
        await self.check_rate_limit()
        
        params = params or {}
        params['api_token'] = self.api_token
        
        url = f"{self.base_url}/football/{endpoint.lstrip('/')}"
        
        self.api_call_times.append(time.time())
        self.stats.api_requests += 1
        
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    elif response.status == 429:
                        logger.warning("Rate limited by SportMonks, waiting 60 seconds...")
                        await asyncio.sleep(60)
                        return await self.make_sportmonks_request(endpoint, params)
                    else:
                        logger.error(f"SportMonks API returned status {response.status} for {endpoint}")
                        self.stats.errors += 1
                        return None
                        
        except Exception as e:
            logger.error(f"Error making SportMonks request to {endpoint}: {e}")
            self.stats.errors += 1
            return None
    
    async def collect_real_madrid_matches(self) -> List[Dict]:
        """Collect all Real Madrid matches for 2023-2024 season."""
        logger.info("🔄 Collecting Real Madrid matches for 2023-2024 season...")
        
        matches = []
        
        # Get matches where Real Madrid is home team
        home_matches = await self.make_sportmonks_request(
            f'fixtures/seasons/{self.SEASON_2023_2024_ID}/teams/{self.REAL_MADRID_TEAM_ID}',
            {
                'include': 'league,round,venue,scores,participants',
                'filters': 'fixtureLeagues:8,271,75,76'  # Champions League, La Liga, Copa del Rey, Supercopa
            }
        )
        
        if home_matches and 'data' in home_matches:
            matches.extend(home_matches['data'])
        
        logger.info(f"✅ Collected {len(matches)} Real Madrid matches")
        self.stats.matches_collected = len(matches)
        
        return matches
    
    def save_match_to_database(self, match_data: Dict) -> Optional[int]:
        """Save match data to database."""
        try:
            # Extract match information
            match_info = {
                'sportmonks_match_id': match_data['id'],
                'match_date': match_data.get('starting_at'),
                'match_week': match_data.get('round', {}).get('name') if match_data.get('round') else None,
                'round_name': match_data.get('round', {}).get('name') if match_data.get('round') else None,
                'venue_name': match_data.get('venue', {}).get('name') if match_data.get('venue') else None,
                'venue_city': match_data.get('venue', {}).get('city_name') if match_data.get('venue') else None,
                'match_status': match_data.get('state', {}).get('short_name', 'finished'),
                'attendance': match_data.get('attendance')
            }
            
            # Get participants (teams)
            participants = match_data.get('participants', [])
            home_team = next((p for p in participants if p.get('meta', {}).get('location') == 'home'), None)
            away_team = next((p for p in participants if p.get('meta', {}).get('location') == 'away'), None)
            
            if not home_team or not away_team:
                logger.warning(f"Missing team data for match {match_data['id']}")
                return None
            
            # Determine Real Madrid involvement
            real_madrid_home = home_team['id'] == self.REAL_MADRID_TEAM_ID
            real_madrid_away = away_team['id'] == self.REAL_MADRID_TEAM_ID
            
            # Get or create teams
            home_team_id = self.get_or_create_team(home_team)
            away_team_id = self.get_or_create_team(away_team)
            
            # Get or create competition
            competition_id = self.get_or_create_competition(match_data.get('league', {}))
            
            # Get scores
            scores = match_data.get('scores', [])
            home_score = 0
            away_score = 0
            home_score_ht = 0
            away_score_ht = 0
            
            for score in scores:
                if score.get('description') == 'CURRENT':
                    if score.get('participant_id') == home_team['id']:
                        home_score = score.get('goals', 0)
                    else:
                        away_score = score.get('goals', 0)
                elif score.get('description') == 'HT':
                    if score.get('participant_id') == home_team['id']:
                        home_score_ht = score.get('goals', 0)
                    else:
                        away_score_ht = score.get('goals', 0)
            
            # Insert match
            query = """
                INSERT INTO matches (
                    sportmonks_match_id, competition_id, season_id, match_date, match_week, round_name,
                    home_team_id, away_team_id, home_score, away_score, home_score_ht, away_score_ht,
                    match_status, venue_name, venue_city, attendance, real_madrid_home, real_madrid_away
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sportmonks_match_id) 
                DO UPDATE SET 
                    home_score = EXCLUDED.home_score,
                    away_score = EXCLUDED.away_score,
                    home_score_ht = EXCLUDED.home_score_ht,
                    away_score_ht = EXCLUDED.away_score_ht,
                    match_status = EXCLUDED.match_status,
                    attendance = EXCLUDED.attendance
                RETURNING match_id
            """
            
            self.db_cursor.execute(query, (
                match_info['sportmonks_match_id'], competition_id, 1, match_info['match_date'],
                match_info['match_week'], match_info['round_name'], home_team_id, away_team_id,
                home_score, away_score, home_score_ht, away_score_ht, match_info['match_status'],
                match_info['venue_name'], match_info['venue_city'], match_info['attendance'],
                real_madrid_home, real_madrid_away
            ))
            
            result = self.db_cursor.fetchone()
            match_id = result[0] if result else None
            
            return match_id
            
        except Exception as e:
            logger.error(f"❌ Failed to save match {match_data.get('id', 'unknown')}: {e}")
            return None
    
    def get_or_create_team(self, team_data: Dict) -> Optional[int]:
        """Get existing team or create new one."""
        try:
            sportmonks_team_id = team_data['id']
            
            # Check if team exists
            self.db_cursor.execute(
                "SELECT team_id FROM teams WHERE sportmonks_team_id = %s",
                (sportmonks_team_id,)
            )
            result = self.db_cursor.fetchone()
            
            if result:
                return result[0]
            
            # Create new team
            is_real_madrid = sportmonks_team_id == self.REAL_MADRID_TEAM_ID
            
            query = """
                INSERT INTO teams (sportmonks_team_id, team_name, short_name, country, is_real_madrid)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING team_id
            """
            
            self.db_cursor.execute(query, (
                sportmonks_team_id,
                team_data.get('name', 'Unknown Team'),
                team_data.get('short_code', ''),
                team_data.get('country', {}).get('name') if team_data.get('country') else None,
                is_real_madrid
            ))
            
            result = self.db_cursor.fetchone()
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get/create team {team_data.get('id', 'unknown')}: {e}")
            return None
    
    def get_or_create_competition(self, competition_data: Dict) -> Optional[int]:
        """Get existing competition or create new one."""
        try:
            if not competition_data or 'id' not in competition_data:
                return None
                
            sportmonks_competition_id = competition_data['id']
            
            # Check if competition exists
            self.db_cursor.execute(
                "SELECT competition_id FROM competitions WHERE sportmonks_competition_id = %s",
                (sportmonks_competition_id,)
            )
            result = self.db_cursor.fetchone()
            
            if result:
                return result[0]
            
            # Create new competition
            query = """
                INSERT INTO competitions (sportmonks_competition_id, competition_name, competition_type, country, season_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING competition_id
            """
            
            self.db_cursor.execute(query, (
                sportmonks_competition_id,
                competition_data.get('name', 'Unknown Competition'),
                competition_data.get('type', 'Unknown'),
                competition_data.get('country', {}).get('name') if competition_data.get('country') else None,
                1  # 2023-2024 season
            ))
            
            result = self.db_cursor.fetchone()
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"❌ Failed to get/create competition {competition_data.get('id', 'unknown')}: {e}")
            return None
    
    async def collect_match_players_and_statistics(self, match_id: int, sportmonks_match_id: int) -> bool:
        """Collect players and their statistics for a specific match."""
        try:
            logger.info(f"🔄 Collecting player statistics for match {sportmonks_match_id}")
            
            # Get match lineups and player statistics
            match_details = await self.make_sportmonks_request(
                f'fixtures/{sportmonks_match_id}',
                {
                    'include': 'lineups.player,statistics.player,events.player'
                }
            )
            
            if not match_details or 'data' not in match_details:
                logger.warning(f"No match details found for {sportmonks_match_id}")
                return False
            
            match_data = match_details['data']
            players_processed = 0
            
            # Process lineups
            lineups = match_data.get('lineups', [])
            for lineup in lineups:
                team_id = self.get_team_id_by_sportmonks_id(lineup.get('participant_id'))
                if not team_id:
                    continue
                
                for player_lineup in lineup.get('lineups', []):
                    player_data = player_lineup.get('player')
                    if not player_data:
                        continue
                    
                    # Get or create player
                    player_id = self.get_or_create_player(player_data, team_id)
                    if not player_id:
                        continue
                    
                    # Create basic statistics record
                    self.create_player_match_statistics(
                        match_id, player_id, team_id, player_lineup, {}
                    )
                    players_processed += 1
            
            # Process detailed statistics
            statistics = match_data.get('statistics', [])
            for stat_group in statistics:
                player_data = stat_group.get('player')
                if not player_data:
                    continue
                
                player_id = self.get_player_id_by_sportmonks_id(player_data['id'])
                if not player_id:
                    continue
                
                # Update statistics
                self.update_player_match_statistics(match_id, player_id, stat_group)
            
            # Mark match as processed
            self.db_cursor.execute(
                "UPDATE matches SET players_collected = TRUE, statistics_collected = TRUE WHERE match_id = %s",
                (match_id,)
            )
            
            self.stats.statistics_collected += players_processed
            logger.info(f"✅ Processed {players_processed} player records for match {sportmonks_match_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to collect player statistics for match {sportmonks_match_id}: {e}")
            return False

    def get_or_create_player(self, player_data: Dict, team_id: int) -> Optional[int]:
        """Get existing player or create new one."""
        try:
            sportmonks_player_id = player_data['id']

            # Check if player exists
            self.db_cursor.execute(
                "SELECT player_id FROM players WHERE sportmonks_player_id = %s",
                (sportmonks_player_id,)
            )
            result = self.db_cursor.fetchone()

            if result:
                return result[0]

            # Create new player
            query = """
                INSERT INTO players (
                    sportmonks_player_id, player_name, display_name, first_name, last_name,
                    birth_date, nationality, height, weight, position, team_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING player_id
            """

            # Extract player details
            person = player_data.get('person', {}) if player_data.get('person') else {}
            position = player_data.get('position', {}) if player_data.get('position') else {}

            self.db_cursor.execute(query, (
                sportmonks_player_id,
                player_data.get('name', 'Unknown Player'),
                player_data.get('display_name', player_data.get('name', 'Unknown Player')),
                person.get('firstname'),
                person.get('lastname'),
                person.get('date_of_birth'),
                person.get('nationality'),
                person.get('height'),
                person.get('weight'),
                position.get('name'),
                team_id
            ))

            result = self.db_cursor.fetchone()
            player_id = result[0] if result else None

            if player_id:
                self.stats.players_collected += 1

            return player_id

        except Exception as e:
            logger.error(f"❌ Failed to get/create player {player_data.get('id', 'unknown')}: {e}")
            return None

    def get_team_id_by_sportmonks_id(self, sportmonks_team_id: int) -> Optional[int]:
        """Get team_id by SportMonks team ID."""
        try:
            self.db_cursor.execute(
                "SELECT team_id FROM teams WHERE sportmonks_team_id = %s",
                (sportmonks_team_id,)
            )
            result = self.db_cursor.fetchone()
            return result[0] if result else None
        except Exception:
            return None

    def get_player_id_by_sportmonks_id(self, sportmonks_player_id: int) -> Optional[int]:
        """Get player_id by SportMonks player ID."""
        try:
            self.db_cursor.execute(
                "SELECT player_id FROM players WHERE sportmonks_player_id = %s",
                (sportmonks_player_id,)
            )
            result = self.db_cursor.fetchone()
            return result[0] if result else None
        except Exception:
            return None

    def create_player_match_statistics(self, match_id: int, player_id: int, team_id: int,
                                     lineup_data: Dict, stats_data: Dict):
        """Create initial player match statistics record."""
        try:
            # Extract lineup information
            formation_position = lineup_data.get('formation_position')
            jersey_number = lineup_data.get('jersey_number')
            is_starter = lineup_data.get('type', {}).get('name') == 'starting-lineup'

            query = """
                INSERT INTO player_match_statistics (
                    match_id, player_id, team_id, position_played, jersey_number,
                    is_starter, is_substitute, minutes_played
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (match_id, player_id) DO NOTHING
            """

            self.db_cursor.execute(query, (
                match_id, player_id, team_id, formation_position, jersey_number,
                is_starter, not is_starter, 90 if is_starter else 0  # Default minutes
            ))

        except Exception as e:
            logger.error(f"❌ Failed to create player statistics record: {e}")

    def update_player_match_statistics(self, match_id: int, player_id: int, stats_data: Dict):
        """Update player match statistics with detailed data."""
        try:
            # Extract statistics from SportMonks data structure
            details = stats_data.get('details', [])
            stats_dict = {}

            # Convert details array to dictionary
            for detail in details:
                stat_type = detail.get('type', {}).get('name', '')
                value = detail.get('value', 0)
                stats_dict[stat_type] = value

            # Map SportMonks statistics to our database fields
            update_data = {
                'minutes_played': stats_dict.get('minutes_played', 0),
                'goals': stats_dict.get('goals', 0),
                'assists': stats_dict.get('assists', 0),
                'shots_total': stats_dict.get('shots_total', 0),
                'shots_on_target': stats_dict.get('shots_on_target', 0),
                'shots_off_target': stats_dict.get('shots_off_target', 0),
                'shots_blocked': stats_dict.get('shots_blocked', 0),
                'passes_total': stats_dict.get('passes_total', 0),
                'passes_completed': stats_dict.get('passes_completed', 0),
                'passes_accuracy': stats_dict.get('passes_accuracy', 0.0),
                'passes_key': stats_dict.get('passes_key', 0),
                'crosses_total': stats_dict.get('crosses_total', 0),
                'crosses_completed': stats_dict.get('crosses_completed', 0),
                'tackles_total': stats_dict.get('tackles_total', 0),
                'tackles_successful': stats_dict.get('tackles_successful', 0),
                'interceptions': stats_dict.get('interceptions', 0),
                'clearances': stats_dict.get('clearances', 0),
                'blocks': stats_dict.get('blocks', 0),
                'duels_total': stats_dict.get('duels_total', 0),
                'duels_won': stats_dict.get('duels_won', 0),
                'aerial_duels_total': stats_dict.get('aerial_duels_total', 0),
                'aerial_duels_won': stats_dict.get('aerial_duels_won', 0),
                'yellow_cards': stats_dict.get('yellow_cards', 0),
                'red_cards': stats_dict.get('red_cards', 0),
                'fouls_committed': stats_dict.get('fouls_committed', 0),
                'fouls_suffered': stats_dict.get('fouls_suffered', 0),
                'rating': stats_dict.get('rating', 0.0),
                'touches': stats_dict.get('touches', 0),
                'touches_penalty_area': stats_dict.get('touches_penalty_area', 0),
                'dribbles_attempted': stats_dict.get('dribbles_attempted', 0),
                'dribbles_successful': stats_dict.get('dribbles_successful', 0),
                'offsides': stats_dict.get('offsides', 0),
                'saves': stats_dict.get('saves', 0),
                'saves_inside_box': stats_dict.get('saves_inside_box', 0),
                'saves_outside_box': stats_dict.get('saves_outside_box', 0),
                'goals_conceded': stats_dict.get('goals_conceded', 0),
                'clean_sheet': stats_dict.get('clean_sheet', False)
            }

            # Build update query
            set_clauses = []
            values = []

            for field, value in update_data.items():
                if value is not None and value != 0:  # Only update non-zero values
                    set_clauses.append(f"{field} = %s")
                    values.append(value)

            if set_clauses:
                query = f"""
                    UPDATE player_match_statistics
                    SET {', '.join(set_clauses)}
                    WHERE match_id = %s AND player_id = %s
                """
                values.extend([match_id, player_id])

                self.db_cursor.execute(query, values)

        except Exception as e:
            logger.error(f"❌ Failed to update player statistics: {e}")

    async def run_complete_collection(self) -> bool:
        """Run complete Real Madrid data collection for 2023-2024 season."""
        try:
            logger.info("🚀 Starting Real Madrid 2023-2024 complete data collection...")

            # Start collection session
            session_id = self.start_collection_session()

            # Step 1: Collect all matches
            matches = await self.collect_real_madrid_matches()
            if not matches:
                logger.error("❌ No matches collected")
                return False

            # Step 2: Save matches to database
            logger.info("🔄 Saving matches to database...")
            match_ids = []

            for match_data in matches:
                match_id = self.save_match_to_database(match_data)
                if match_id:
                    match_ids.append((match_id, match_data['id']))

            self.db_conn.commit()
            logger.info(f"✅ Saved {len(match_ids)} matches to database")

            # Step 3: Collect player statistics for each match
            logger.info("🔄 Collecting player statistics for all matches...")

            successful_matches = 0
            for match_id, sportmonks_match_id in match_ids:
                try:
                    success = await self.collect_match_players_and_statistics(match_id, sportmonks_match_id)
                    if success:
                        successful_matches += 1
                        self.db_conn.commit()

                    # Small delay to respect rate limits
                    await asyncio.sleep(1)

                except Exception as e:
                    logger.error(f"❌ Failed to process match {sportmonks_match_id}: {e}")
                    self.db_conn.rollback()

            # End collection session
            self.end_collection_session(session_id, 'COMPLETED')

            # Print summary
            self.print_collection_summary(successful_matches, len(match_ids))

            return successful_matches > 0

        except Exception as e:
            logger.error(f"❌ Complete collection failed: {e}")
            logger.error(traceback.format_exc())
            return False

    def end_collection_session(self, session_id: int, status: str):
        """End the collection session with final statistics."""
        try:
            duration = (datetime.now() - self.stats.start_time).total_seconds()

            query = """
                UPDATE data_collection_log
                SET end_time = %s, status = %s, records_collected = %s,
                    records_failed = %s, api_requests = %s
                WHERE log_id = %s
            """

            self.db_cursor.execute(query, (
                datetime.now(), status,
                self.stats.matches_collected + self.stats.players_collected + self.stats.statistics_collected,
                self.stats.errors, self.stats.api_requests, session_id
            ))

            self.db_conn.commit()

        except Exception as e:
            logger.error(f"❌ Failed to end collection session: {e}")

    def print_collection_summary(self, successful_matches: int, total_matches: int):
        """Print collection summary."""
        duration = (datetime.now() - self.stats.start_time).total_seconds()

        print(f"\n{'='*80}")
        print("🏆 REAL MADRID 2023-2024 COLLECTION SUMMARY")
        print(f"{'='*80}")
        print(f"Matches collected: {self.stats.matches_collected}")
        print(f"Matches with player data: {successful_matches}/{total_matches}")
        print(f"Players collected: {self.stats.players_collected}")
        print(f"Player statistics records: {self.stats.statistics_collected}")
        print(f"API requests made: {self.stats.api_requests}")
        print(f"Errors encountered: {self.stats.errors}")
        print(f"Collection duration: {duration:.1f} seconds")
        print(f"{'='*80}")

    def close_connections(self):
        """Close database connections."""
        try:
            if self.db_cursor:
                self.db_cursor.close()
            if self.db_conn:
                self.db_conn.close()
            logger.info("✅ Database connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing connections: {e}")

async def main():
    """Main function to run Real Madrid data collection."""
    collector = RealMadridCollector()

    try:
        success = await collector.run_complete_collection()

        if success:
            print("\n🎉 Real Madrid data collection completed successfully!")
        else:
            print("\n❌ Real Madrid data collection failed!")

        return success

    except Exception as e:
        logger.error(f"❌ Collection failed: {e}")
        return False
    finally:
        collector.close_connections()

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

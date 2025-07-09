#!/usr/bin/env python3
"""
Multi-API Data Collector for ADS599 Capstone Soccer Intelligence System
Robust data collection service that fetches from both SportMonks and API-Football APIs
"""

import asyncio
import aiohttp
import yaml
import json
import logging
import time
import redis
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
from concurrent.futures import ThreadPoolExecutor
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CollectionSession:
    """Track a data collection session."""
    session_id: int
    start_time: datetime
    collection_type: str
    target_teams: List[str]
    target_seasons: List[str]
    status: str = "IN_PROGRESS"
    records_collected: int = 0
    records_failed: int = 0
    api_requests: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class MultiAPIDataCollector:
    """Multi-API data collector with robust error handling and data consistency."""
    
    def __init__(self, config_path: str = "config"):
        """Initialize the multi-API data collector."""
        self.config_path = Path(config_path)
        self.load_configurations()
        self.setup_connections()
        self.current_session: Optional[CollectionSession] = None
        
        # Rate limiting trackers
        self.api_call_times = {
            'sportmonks': [],
            'api_football': []
        }
        
    def load_configurations(self):
        """Load all configuration files."""
        try:
            # Load API keys
            with open(self.config_path / "api_keys.yaml", 'r') as f:
                self.api_config = yaml.safe_load(f)
            
            # Load data collection config
            with open(self.config_path / "data_collection_config.yaml", 'r') as f:
                self.collection_config = yaml.safe_load(f)
            
            logger.info("✅ Configurations loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load configurations: {e}")
            raise
    
    def setup_connections(self):
        """Setup database and cache connections."""
        try:
            # Setup PostgreSQL connection
            db_config = self.api_config['database']
            self.db_conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['name'],
                user=db_config['user'],
                password=db_config['password']
            )
            self.db_conn.autocommit = False
            self.db_cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            
            # Setup Redis connection
            redis_config = self.api_config['redis']
            self.redis_client = redis.Redis(
                host=redis_config['host'],
                port=redis_config['port'],
                password=redis_config['password'],
                db=redis_config['db'],
                decode_responses=True
            )
            
            # Test connections
            self.db_cursor.execute("SELECT 1")
            self.redis_client.ping()
            
            logger.info("✅ Database and cache connections established")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup connections: {e}")
            raise
    
    def start_collection_session(self, collection_type: str, target_teams: List[str], target_seasons: List[str]) -> int:
        """Start a new data collection session."""
        try:
            query = """
                INSERT INTO api_collection_metadata 
                (collection_type, api_source, collection_status, notes, collection_config)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING collection_id
            """
            
            config_json = {
                'target_teams': target_teams,
                'target_seasons': target_seasons,
                'collection_settings': self.collection_config.get('collection_settings', {})
            }
            
            self.db_cursor.execute(query, (
                collection_type,
                'unified',
                'IN_PROGRESS',
                f'Multi-API collection for {len(target_teams)} teams across {len(target_seasons)} seasons',
                json.dumps(config_json)
            ))
            
            session_id = self.db_cursor.fetchone()[0]
            self.db_conn.commit()
            
            self.current_session = CollectionSession(
                session_id=session_id,
                start_time=datetime.now(),
                collection_type=collection_type,
                target_teams=target_teams,
                target_seasons=target_seasons
            )
            
            logger.info(f"🚀 Started collection session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Failed to start collection session: {e}")
            self.db_conn.rollback()
            raise
    
    def end_collection_session(self, status: str = "COMPLETED"):
        """End the current collection session."""
        if not self.current_session:
            return
        
        try:
            duration = (datetime.now() - self.current_session.start_time).total_seconds()
            
            query = """
                UPDATE api_collection_metadata 
                SET collection_status = %s,
                    records_collected = %s,
                    records_failed = %s,
                    api_requests_made = %s,
                    collection_duration_seconds = %s,
                    error_messages = %s
                WHERE collection_id = %s
            """
            
            self.db_cursor.execute(query, (
                status,
                self.current_session.records_collected,
                self.current_session.records_failed,
                self.current_session.api_requests,
                int(duration),
                '\n'.join(self.current_session.errors) if self.current_session.errors else None,
                self.current_session.session_id
            ))
            
            self.db_conn.commit()
            
            logger.info(f"✅ Collection session {self.current_session.session_id} ended with status: {status}")
            logger.info(f"📊 Records collected: {self.current_session.records_collected}")
            logger.info(f"❌ Records failed: {self.current_session.records_failed}")
            logger.info(f"🕒 Duration: {duration:.2f} seconds")
            
            self.current_session = None
            
        except Exception as e:
            logger.error(f"❌ Failed to end collection session: {e}")
            self.db_conn.rollback()
    
    async def check_rate_limit(self, api_name: str) -> bool:
        """Check if we can make an API request without hitting rate limits."""
        now = time.time()
        api_times = self.api_call_times[api_name]
        
        # Clean old timestamps
        if api_name == 'sportmonks':
            # 50 requests per minute
            cutoff = now - 60
            self.api_call_times[api_name] = [t for t in api_times if t > cutoff]
            return len(self.api_call_times[api_name]) < 50
        else:  # api_football
            # 10 requests per minute
            cutoff = now - 60
            self.api_call_times[api_name] = [t for t in api_times if t > cutoff]
            return len(self.api_call_times[api_name]) < 10
    
    async def wait_for_rate_limit(self, api_name: str):
        """Wait if necessary to respect rate limits."""
        while not await self.check_rate_limit(api_name):
            wait_time = 2 if api_name == 'sportmonks' else 6
            logger.info(f"⏳ Rate limit reached for {api_name}, waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
    
    async def make_api_request(self, api_name: str, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make an API request with rate limiting and error handling."""
        await self.wait_for_rate_limit(api_name)
        
        params = params or {}
        api_config = self.api_config[api_name]
        
        # Record API call time
        self.api_call_times[api_name].append(time.time())
        
        if self.current_session:
            self.current_session.api_requests += 1
        
        # Prepare request
        if api_name == 'sportmonks':
            url = f"{api_config['base_url']}/football/{endpoint.lstrip('/')}"
            params['api_token'] = api_config['api_key']
            headers = {'Accept': 'application/json'}
        else:  # api_football
            url = f"{api_config['base_url']}/{endpoint.lstrip('/')}"
            headers = {
                'X-RapidAPI-Key': api_config['key'],
                'X-RapidAPI-Host': 'v3.football.api-sports.io'
            }
        
        # Make request with retries
        for attempt in range(api_config.get('retry_attempts', 3)):
            try:
                timeout = aiohttp.ClientTimeout(total=api_config.get('timeout', 30))
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data
                        elif response.status == 429:  # Rate limited
                            wait_time = 60 if api_name == 'sportmonks' else 300
                            logger.warning(f"Rate limited by {api_name}, waiting {wait_time} seconds...")
                            await asyncio.sleep(wait_time)
                        else:
                            logger.warning(f"API {api_name} returned status {response.status} for {endpoint}")
                            
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {api_name} {endpoint}: {e}")
                if attempt < api_config.get('retry_attempts', 3) - 1:
                    await asyncio.sleep(api_config.get('retry_delay', 2) * (2 ** attempt))
        
        # All attempts failed
        error_msg = f"Failed to fetch from {api_name} {endpoint} after all retries"
        logger.error(error_msg)
        
        if self.current_session:
            self.current_session.errors.append(error_msg)
            self.current_session.records_failed += 1
        
        return None
    
    async def collect_team_basic_info(self, team_config: Dict) -> Optional[Dict]:
        """Collect basic team information from both APIs."""
        team_data = {
            'name': team_config['name'],
            'sportmonks_data': None,
            'api_football_data': None
        }
        
        # Collect from SportMonks
        if 'sportmonks_id' in team_config:
            sportmonks_data = await self.make_api_request(
                'sportmonks',
                f'teams/{team_config["sportmonks_id"]}',
                {'include': 'venue,country'}
            )
            if sportmonks_data:
                team_data['sportmonks_data'] = sportmonks_data.get('data', {})
        
        # Collect from API-Football
        if 'api_football_id' in team_config:
            api_football_data = await self.make_api_request(
                'api_football',
                'teams',
                {'id': team_config['api_football_id']}
            )
            if api_football_data:
                team_data['api_football_data'] = api_football_data.get('response', [{}])[0]
        
        return team_data
    
    async def collect_team_players(self, team_config: Dict, season_config: Dict) -> Optional[List[Dict]]:
        """Collect team players for a specific season."""
        players_data = []
        
        # Collect from SportMonks
        if 'sportmonks_id' in team_config and 'sportmonks_id' in season_config:
            sportmonks_data = await self.make_api_request(
                'sportmonks',
                f'squads/seasons/{season_config["sportmonks_id"]}/teams/{team_config["sportmonks_id"]}',
                {'include': 'player.position,player.nationality,player.person'}
            )
            if sportmonks_data:
                squad_data = sportmonks_data.get('data', [])
                for player_info in squad_data:
                    player_data = player_info.get('player', {})
                    if player_data:
                        players_data.append({
                            'source': 'sportmonks',
                            'team_config': team_config,
                            'season_config': season_config,
                            'player_data': player_data
                        })
        
        # Collect from API-Football
        if 'api_football_id' in team_config and 'api_football_id' in season_config:
            api_football_data = await self.make_api_request(
                'api_football',
                'players/squads',
                {
                    'team': team_config['api_football_id'],
                    'season': season_config['api_football_id']
                }
            )
            if api_football_data:
                squad_data = api_football_data.get('response', [])
                for player_info in squad_data:
                    players_data.append({
                        'source': 'api_football',
                        'team_config': team_config,
                        'season_config': season_config,
                        'player_data': player_info
                    })
        
        return players_data
    
    def save_team_to_database(self, team_data: Dict) -> Optional[int]:
        """Save team data to database and return team_id."""
        try:
            sportmonks_data = team_data.get('sportmonks_data', {})
            api_football_data = team_data.get('api_football_data', {})
            
            # Prepare team information
            team_info = {
                'team_name': team_data['name'],
                'short_name': sportmonks_data.get('short_code') or api_football_data.get('team', {}).get('code'),
                'sportmonks_team_id': sportmonks_data.get('id'),
                'api_football_team_id': api_football_data.get('team', {}).get('id'),
                'country': sportmonks_data.get('country', {}).get('name') or api_football_data.get('team', {}).get('country'),
                'founded_year': sportmonks_data.get('founded') or api_football_data.get('team', {}).get('founded'),
                'venue_name': sportmonks_data.get('venue', {}).get('name') or api_football_data.get('venue', {}).get('name'),
                'venue_city': sportmonks_data.get('venue', {}).get('city_name') or api_football_data.get('venue', {}).get('city'),
                'venue_capacity': api_football_data.get('venue', {}).get('capacity'),
                'logo_url': sportmonks_data.get('image_path') or api_football_data.get('team', {}).get('logo'),
                'data_source': 'unified',
                'last_updated_sportmonks': datetime.now() if sportmonks_data else None,
                'last_updated_api_football': datetime.now() if api_football_data else None
            }
            
            # Insert or update team
            query = """
                INSERT INTO teams (team_name, short_name, sportmonks_team_id, api_football_team_id, 
                                 country, founded_year, venue_name, venue_city, venue_capacity, 
                                 logo_url, data_source, last_updated_sportmonks, last_updated_api_football)
                VALUES (%(team_name)s, %(short_name)s, %(sportmonks_team_id)s, %(api_football_team_id)s,
                        %(country)s, %(founded_year)s, %(venue_name)s, %(venue_city)s, %(venue_capacity)s,
                        %(logo_url)s, %(data_source)s, %(last_updated_sportmonks)s, %(last_updated_api_football)s)
                ON CONFLICT (sportmonks_team_id) 
                DO UPDATE SET 
                    team_name = EXCLUDED.team_name,
                    short_name = EXCLUDED.short_name,
                    api_football_team_id = EXCLUDED.api_football_team_id,
                    country = EXCLUDED.country,
                    founded_year = EXCLUDED.founded_year,
                    venue_name = EXCLUDED.venue_name,
                    venue_city = EXCLUDED.venue_city,
                    venue_capacity = EXCLUDED.venue_capacity,
                    logo_url = EXCLUDED.logo_url,
                    last_updated_sportmonks = EXCLUDED.last_updated_sportmonks,
                    last_updated_api_football = EXCLUDED.last_updated_api_football,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING team_id
            """
            
            self.db_cursor.execute(query, team_info)
            result = self.db_cursor.fetchone()
            team_id = result[0] if result else None
            
            if self.current_session:
                self.current_session.records_collected += 1
            
            return team_id
            
        except Exception as e:
            logger.error(f"❌ Failed to save team {team_data['name']}: {e}")
            if self.current_session:
                self.current_session.errors.append(f"Failed to save team {team_data['name']}: {str(e)}")
                self.current_session.records_failed += 1
            return None

    def save_players_to_database(self, players_data: List[Dict], team_id: int) -> int:
        """Save players data to database and return count of saved players."""
        saved_count = 0

        for player_info in players_data:
            try:
                source = player_info['source']
                player_data = player_info['player_data']

                if source == 'sportmonks':
                    player_info_dict = {
                        'player_name': player_data.get('display_name') or player_data.get('common_name'),
                        'first_name': player_data.get('firstname'),
                        'last_name': player_data.get('lastname'),
                        'sportmonks_player_id': player_data.get('id'),
                        'birth_date': player_data.get('date_of_birth'),
                        'nationality': player_data.get('nationality', {}).get('name'),
                        'height': player_data.get('height'),
                        'weight': player_data.get('weight'),
                        'position': player_data.get('position', {}).get('name'),
                        'current_team_id': team_id,
                        'data_source': 'sportmonks',
                        'last_updated_sportmonks': datetime.now()
                    }
                else:  # api_football
                    player_info_dict = {
                        'player_name': player_data.get('name'),
                        'first_name': player_data.get('firstname'),
                        'last_name': player_data.get('lastname'),
                        'api_football_player_id': player_data.get('id'),
                        'birth_date': player_data.get('birth', {}).get('date'),
                        'birth_place': player_data.get('birth', {}).get('place'),
                        'nationality': player_data.get('nationality'),
                        'height': player_data.get('height', '').replace('cm', '').strip() if player_data.get('height') else None,
                        'weight': player_data.get('weight', '').replace('kg', '').strip() if player_data.get('weight') else None,
                        'position': player_data.get('position'),
                        'current_team_id': team_id,
                        'data_source': 'api_football',
                        'last_updated_api_football': datetime.now()
                    }

                # Clean and convert numeric fields
                for field in ['height', 'weight']:
                    if player_info_dict.get(field):
                        try:
                            player_info_dict[field] = int(player_info_dict[field])
                        except (ValueError, TypeError):
                            player_info_dict[field] = None

                # Insert or update player
                query = """
                    INSERT INTO players (player_name, first_name, last_name, sportmonks_player_id,
                                       api_football_player_id, birth_date, birth_place, nationality,
                                       height, weight, position, current_team_id, data_source,
                                       last_updated_sportmonks, last_updated_api_football)
                    VALUES (%(player_name)s, %(first_name)s, %(last_name)s, %(sportmonks_player_id)s,
                            %(api_football_player_id)s, %(birth_date)s, %(birth_place)s, %(nationality)s,
                            %(height)s, %(weight)s, %(position)s, %(current_team_id)s, %(data_source)s,
                            %(last_updated_sportmonks)s, %(last_updated_api_football)s)
                    ON CONFLICT (sportmonks_player_id)
                    DO UPDATE SET
                        player_name = EXCLUDED.player_name,
                        api_football_player_id = EXCLUDED.api_football_player_id,
                        birth_date = EXCLUDED.birth_date,
                        birth_place = EXCLUDED.birth_place,
                        nationality = EXCLUDED.nationality,
                        height = EXCLUDED.height,
                        weight = EXCLUDED.weight,
                        position = EXCLUDED.position,
                        current_team_id = EXCLUDED.current_team_id,
                        last_updated_sportmonks = EXCLUDED.last_updated_sportmonks,
                        last_updated_api_football = EXCLUDED.last_updated_api_football,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING player_id
                """

                self.db_cursor.execute(query, player_info_dict)
                result = self.db_cursor.fetchone()
                if result:
                    saved_count += 1

            except Exception as e:
                logger.error(f"❌ Failed to save player {player_data.get('name', 'Unknown')}: {e}")
                if self.current_session:
                    self.current_session.errors.append(f"Failed to save player: {str(e)}")
                    self.current_session.records_failed += 1

        if self.current_session:
            self.current_session.records_collected += saved_count

        return saved_count

    async def collect_comprehensive_team_data(self, team_config: Dict, seasons: List[Dict]) -> Dict:
        """Collect comprehensive data for a team across multiple seasons."""
        logger.info(f"🔄 Collecting comprehensive data for {team_config['name']}")

        results = {
            'team_info': None,
            'team_id': None,
            'players_by_season': {},
            'matches_by_season': {},
            'errors': []
        }

        try:
            # Collect and save team basic information
            team_data = await self.collect_team_basic_info(team_config)
            if team_data:
                team_id = self.save_team_to_database(team_data)
                if team_id:
                    results['team_info'] = team_data
                    results['team_id'] = team_id
                    logger.info(f"✅ Saved team {team_config['name']} with ID: {team_id}")
                else:
                    error_msg = f"Failed to save team {team_config['name']} to database"
                    results['errors'].append(error_msg)
                    logger.error(error_msg)
                    return results
            else:
                error_msg = f"Failed to collect team data for {team_config['name']}"
                results['errors'].append(error_msg)
                logger.error(error_msg)
                return results

            # Collect players for each season
            for season_config in seasons:
                season_name = season_config['name']
                logger.info(f"🔄 Collecting players for {team_config['name']} - {season_name}")

                players_data = await self.collect_team_players(team_config, season_config)
                if players_data:
                    saved_players = self.save_players_to_database(players_data, team_id)
                    results['players_by_season'][season_name] = {
                        'total_collected': len(players_data),
                        'total_saved': saved_players
                    }
                    logger.info(f"✅ Saved {saved_players}/{len(players_data)} players for {team_config['name']} - {season_name}")
                else:
                    error_msg = f"No players data collected for {team_config['name']} - {season_name}"
                    results['errors'].append(error_msg)
                    logger.warning(error_msg)

            # Commit all changes for this team
            self.db_conn.commit()
            logger.info(f"✅ Committed all data for {team_config['name']}")

        except Exception as e:
            error_msg = f"Failed to collect comprehensive data for {team_config['name']}: {str(e)}"
            results['errors'].append(error_msg)
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.db_conn.rollback()

        return results

    async def run_comprehensive_collection(self, target_teams: List[str] = None, target_seasons: List[str] = None):
        """Run comprehensive data collection for specified teams and seasons."""
        # Use default teams and seasons if not specified
        if target_teams is None:
            target_teams = ['Real Madrid', 'Barcelona', 'Manchester City', 'Liverpool', 'Bayern Munich']

        if target_seasons is None:
            target_seasons = ['2023-2024', '2022-2023']

        # Get team configurations
        team_configs = []
        for league_teams in self.collection_config['target_teams'].values():
            for team_config in league_teams:
                if team_config['name'] in target_teams:
                    team_configs.append(team_config)

        # Get season configurations
        season_configs = [
            season for season in self.collection_config['seasons']
            if season['name'] in target_seasons
        ]

        if not team_configs:
            logger.error("❌ No valid team configurations found")
            return

        if not season_configs:
            logger.error("❌ No valid season configurations found")
            return

        # Start collection session
        session_id = self.start_collection_session(
            'COMPREHENSIVE_TEAM_DATA',
            target_teams,
            target_seasons
        )

        logger.info(f"🚀 Starting comprehensive collection for {len(team_configs)} teams across {len(season_configs)} seasons")

        try:
            collection_results = {}

            # Collect data for each team
            for team_config in team_configs:
                team_name = team_config['name']
                logger.info(f"\n{'='*60}")
                logger.info(f"🔄 Processing team: {team_name}")
                logger.info(f"{'='*60}")

                team_results = await self.collect_comprehensive_team_data(team_config, season_configs)
                collection_results[team_name] = team_results

                # Log progress
                if team_results['team_id']:
                    total_players = sum(
                        season_data['total_saved']
                        for season_data in team_results['players_by_season'].values()
                    )
                    logger.info(f"✅ Completed {team_name}: Team saved, {total_players} players saved")
                else:
                    logger.error(f"❌ Failed to process {team_name}")

                # Small delay between teams to be respectful to APIs
                await asyncio.sleep(2)

            # End collection session
            self.end_collection_session("COMPLETED")

            # Print final summary
            self.print_collection_summary(collection_results)

        except Exception as e:
            logger.error(f"❌ Collection failed: {e}")
            logger.error(traceback.format_exc())
            self.end_collection_session("FAILED")
            raise

    def print_collection_summary(self, results: Dict):
        """Print a summary of the collection results."""
        print(f"\n{'='*80}")
        print("📊 COLLECTION SUMMARY")
        print(f"{'='*80}")

        total_teams = len(results)
        successful_teams = sum(1 for r in results.values() if r['team_id'])
        total_players = sum(
            sum(season_data['total_saved'] for season_data in r['players_by_season'].values())
            for r in results.values()
        )

        print(f"Teams processed: {total_teams}")
        print(f"Teams successful: {successful_teams}")
        print(f"Total players saved: {total_players}")

        if self.current_session:
            print(f"API requests made: {self.current_session.api_requests}")
            print(f"Records collected: {self.current_session.records_collected}")
            print(f"Records failed: {self.current_session.records_failed}")

        print(f"\n📋 Team Details:")
        for team_name, team_results in results.items():
            status = "✅" if team_results['team_id'] else "❌"
            players_count = sum(
                season_data['total_saved']
                for season_data in team_results['players_by_season'].values()
            )
            print(f"  {status} {team_name}: {players_count} players")

            if team_results['errors']:
                for error in team_results['errors'][:3]:  # Show first 3 errors
                    print(f"    ⚠️  {error}")

        print(f"{'='*80}")

    def close_connections(self):
        """Close all connections."""
        try:
            if hasattr(self, 'db_conn'):
                self.db_conn.close()
            if hasattr(self, 'redis_client'):
                self.redis_client.close()
            logger.info("✅ Connections closed successfully")
        except Exception as e:
            logger.error(f"❌ Error closing connections: {e}")

async def main():
    """Main function for running the multi-API data collector."""
    collector = MultiAPIDataCollector()

    try:
        # Run comprehensive collection for key teams
        await collector.run_comprehensive_collection(
            target_teams=['Real Madrid', 'Barcelona', 'Manchester City', 'Liverpool'],
            target_seasons=['2023-2024', '2022-2023']
        )

    except Exception as e:
        logger.error(f"❌ Collection failed: {e}")
    finally:
        collector.close_connections()

if __name__ == "__main__":
    asyncio.run(main())

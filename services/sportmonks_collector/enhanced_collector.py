#!/usr/bin/env python3
"""
Enhanced SportMonks API Data Collector for Real Madrid
Comprehensive data collection with Redis caching and performance optimization
"""

import os
import sys
import json
import time
import logging
import requests
import psycopg2
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/enhanced_collector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CollectionConfig:
    """Configuration for data collection."""
    real_madrid_id: int = 53
    seasons: List[int] = None
    competitions: List[int] = None
    rate_limit_delay: float = 1.0
    max_retries: int = 3
    retry_delay: float = 5.0
    cache_ttl: int = 3600  # 1 hour cache TTL
    
    def __post_init__(self):
        if self.seasons is None:
            # SportMonks season IDs for 2019-2024
            self.seasons = [
                19686,  # 2019-2020
                19734,  # 2020-2021
                21646,  # 2021-2022
                21647,  # 2022-2023
                21648,  # 2023-2024
            ]
        
        if self.competitions is None:
            # Major competitions
            self.competitions = [
                8,    # UEFA Champions League
                271,  # La Liga
                75,   # Copa del Rey
                848,  # UEFA Super Cup
                955,  # FIFA Club World Cup
            ]

class EnhancedSportMonksCollector:
    """Enhanced SportMonks API collector with Redis caching and comprehensive data collection."""
    
    def __init__(self):
        """Initialize collector with configuration."""
        self.config = CollectionConfig()
        self.api_token = os.getenv('SPORTMONKS_API_KEY')
        self.base_url = "https://api.sportmonks.com/v3/football"
        
        # Initialize Redis connection
        self.redis_client = self._init_redis()
        
        # Initialize database connection
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'postgres'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'soccer_intelligence'),
            'user': os.getenv('POSTGRES_USER', 'soccerapp'),
            'password': os.getenv('POSTGRES_PASSWORD', 'soccerpass123')
        }
        
        # Session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Real-Madrid-Analysis/1.0',
            'Accept': 'application/json'
        })
        
        logger.info("Enhanced SportMonks Collector initialized")
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection."""
        try:
            redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'redis'),
                port=int(os.getenv('REDIS_PORT', '6379')),
                password=os.getenv('REDIS_PASSWORD', 'redispass123'),
                db=0,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            redis_client.ping()
            logger.info("✅ Redis connection established")
            return redis_client
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            logger.warning("Continuing without Redis caching")
            return None
    
    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate cache key for API request."""
        # Create a deterministic key from endpoint and params
        param_str = json.dumps(params, sort_keys=True)
        key_data = f"{endpoint}:{param_str}"
        return f"sportmonks:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """Get data from Redis cache."""
        if not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for key: {cache_key}")
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        
        return None
    
    def _set_cached_data(self, cache_key: str, data: Dict, ttl: int = None) -> None:
        """Store data in Redis cache."""
        if not self.redis_client:
            return
        
        try:
            ttl = ttl or self.config.cache_ttl
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(data, default=str)
            )
            logger.debug(f"Data cached with key: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    def _make_api_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with caching and rate limiting."""
        if params is None:
            params = {}
        
        # Add API token
        params['api_token'] = self.api_token
        
        # Check cache first
        cache_key = self._get_cache_key(endpoint, params)
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Make API request
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.config.max_retries):
            try:
                logger.debug(f"API request: {endpoint} (attempt {attempt + 1})")
                
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Cache successful response
                    self._set_cached_data(cache_key, data)
                    
                    # Rate limiting
                    time.sleep(self.config.rate_limit_delay)
                    
                    return data
                
                elif response.status_code == 429:
                    # Rate limit exceeded
                    wait_time = self.config.retry_delay * (2 ** attempt)
                    logger.warning(f"Rate limit exceeded. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                else:
                    logger.error(f"API error {response.status_code}: {response.text}")
                    break
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)
                    continue
                break
        
        return None
    
    def collect_team_information(self) -> Dict:
        """Collect comprehensive Real Madrid team information."""
        logger.info("🏆 Collecting Real Madrid team information...")
        
        endpoint = f"teams/{self.config.real_madrid_id}"
        params = {
            'include': 'country,venue,coach,players.person,players.position,statistics'
        }
        
        team_data = self._make_api_request(endpoint, params)
        
        if team_data and 'data' in team_data:
            logger.info("✅ Team information collected successfully")
            return team_data['data']
        
        logger.error("❌ Failed to collect team information")
        return {}
    
    def collect_season_data(self, season_id: int) -> Dict:
        """Collect data for a specific season."""
        logger.info(f"📅 Collecting season {season_id} data...")
        
        # Get season fixtures
        endpoint = f"fixtures/between/{season_id}/teams/{self.config.real_madrid_id}"
        params = {
            'include': 'participants,scores,statistics,lineups.player.person,lineups.player.position'
        }
        
        fixtures_data = self._make_api_request(endpoint, params)
        
        if fixtures_data and 'data' in fixtures_data:
            logger.info(f"✅ Season {season_id} fixtures collected: {len(fixtures_data['data'])} matches")
            return fixtures_data['data']
        
        logger.error(f"❌ Failed to collect season {season_id} data")
        return []

    def collect_player_statistics(self, season_id: int) -> List[Dict]:
        """Collect detailed player statistics for a season."""
        logger.info(f"👥 Collecting player statistics for season {season_id}...")

        endpoint = f"players/statistics/seasons/{season_id}/teams/{self.config.real_madrid_id}"
        params = {
            'include': 'player.person,player.position,details'
        }

        stats_data = self._make_api_request(endpoint, params)

        if stats_data and 'data' in stats_data:
            logger.info(f"✅ Player statistics collected: {len(stats_data['data'])} players")
            return stats_data['data']

        logger.error(f"❌ Failed to collect player statistics for season {season_id}")
        return []

    def collect_match_details(self, match_id: int) -> Dict:
        """Collect detailed match information including lineups and statistics."""
        logger.info(f"⚽ Collecting match details for match {match_id}...")

        endpoint = f"fixtures/{match_id}"
        params = {
            'include': 'participants,scores,statistics,lineups.player.person,' +
                      'lineups.player.position,lineups.statistics,events,substitutions'
        }

        match_data = self._make_api_request(endpoint, params)

        if match_data and 'data' in match_data:
            logger.info(f"✅ Match {match_id} details collected")
            return match_data['data']

        logger.error(f"❌ Failed to collect match {match_id} details")
        return {}

    def _get_db_connection(self):
        """Get database connection."""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def store_team_data(self, team_data: Dict) -> bool:
        """Store team data in database."""
        if not team_data:
            return False

        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            # Insert or update team data
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
                RETURNING team_id;
            """

            values = (
                team_data.get('id'),
                team_data.get('name'),
                team_data.get('short_code'),
                team_data.get('country', {}).get('name') if team_data.get('country') else None,
                team_data.get('founded'),
                team_data.get('venue', {}).get('name') if team_data.get('venue') else None,
                team_data.get('venue', {}).get('city_name') if team_data.get('venue') else None,
                team_data.get('image_path')
            )

            cursor.execute(query, values)
            team_id = cursor.fetchone()[0]

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"✅ Team data stored successfully (team_id: {team_id})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to store team data: {e}")
            return False

    def store_match_data(self, match_data: Dict) -> bool:
        """Store match data in database."""
        if not match_data:
            return False

        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            # Insert or update match data
            query = """
                INSERT INTO matches (
                    sportmonks_match_id, home_team_id, away_team_id, competition_id,
                    match_date, home_score, away_score, match_status, venue_name
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sportmonks_match_id)
                DO UPDATE SET
                    home_score = EXCLUDED.home_score,
                    away_score = EXCLUDED.away_score,
                    match_status = EXCLUDED.match_status,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING match_id;
            """

            # Extract scores
            scores = match_data.get('scores', [])
            home_score = away_score = 0

            for score in scores:
                if score.get('description') == 'CURRENT':
                    goals = score.get('score', {}).get('goals', {})
                    home_score = goals.get('home', 0)
                    away_score = goals.get('away', 0)
                    break

            values = (
                match_data.get('id'),
                match_data.get('participants', [{}])[0].get('id') if match_data.get('participants') else None,
                match_data.get('participants', [{}])[1].get('id') if len(match_data.get('participants', [])) > 1 else None,
                match_data.get('league_id'),
                match_data.get('starting_at'),
                home_score,
                away_score,
                match_data.get('state', {}).get('short_name'),
                match_data.get('venue', {}).get('name') if match_data.get('venue') else None
            )

            cursor.execute(query, values)
            match_id = cursor.fetchone()[0]

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"✅ Match data stored successfully (match_id: {match_id})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to store match data: {e}")
            return False

    def run_comprehensive_collection(self) -> bool:
        """Run comprehensive data collection for Real Madrid."""
        logger.info("🚀 Starting comprehensive Real Madrid data collection...")

        start_time = datetime.now()
        total_matches = 0
        total_players = 0

        try:
            # 1. Collect team information
            logger.info("📋 Step 1: Collecting team information...")
            team_data = self.collect_team_information()
            if team_data:
                self.store_team_data(team_data)

            # 2. Collect data for each season
            for season_id in self.config.seasons:
                logger.info(f"📅 Step 2: Processing season {season_id}...")

                # Collect season fixtures
                fixtures = self.collect_season_data(season_id)
                total_matches += len(fixtures)

                # Store each match
                for fixture in fixtures:
                    self.store_match_data(fixture)

                    # Collect detailed match data if needed
                    match_details = self.collect_match_details(fixture.get('id'))
                    if match_details:
                        # Process lineups and player statistics
                        self._process_match_lineups(match_details)

                # Collect player statistics for the season
                player_stats = self.collect_player_statistics(season_id)
                total_players += len(player_stats)

                # Store player statistics
                for player_stat in player_stats:
                    self._store_player_statistics(player_stat, season_id)

            # 3. Update collection metadata
            duration = (datetime.now() - start_time).total_seconds()
            self._log_collection_metadata(
                collection_type="COMPREHENSIVE_COLLECTION",
                records_collected=total_matches + total_players,
                duration=duration,
                status="COMPLETED"
            )

            logger.info(f"✅ Collection completed successfully!")
            logger.info(f"📊 Total matches: {total_matches}")
            logger.info(f"👥 Total player records: {total_players}")
            logger.info(f"⏱️ Duration: {duration:.2f} seconds")

            return True

        except Exception as e:
            logger.error(f"❌ Collection failed: {e}")
            self._log_collection_metadata(
                collection_type="COMPREHENSIVE_COLLECTION",
                records_collected=0,
                duration=(datetime.now() - start_time).total_seconds(),
                status="FAILED",
                error_message=str(e)
            )
            return False

    def _process_match_lineups(self, match_data: Dict) -> None:
        """Process match lineups and player statistics."""
        lineups = match_data.get('lineups', [])

        for lineup in lineups:
            team_id = lineup.get('team_id')
            if team_id == self.config.real_madrid_id:
                # Process Real Madrid players only
                for player_lineup in lineup.get('lineup', []):
                    self._store_match_player_stats(player_lineup, match_data.get('id'))

    def _store_player_statistics(self, player_stat: Dict, season_id: int) -> bool:
        """Store player statistics in database."""
        # Implementation for storing player statistics
        # This would include detailed player performance metrics
        pass

    def _store_match_player_stats(self, player_lineup: Dict, match_id: int) -> bool:
        """Store individual match player statistics."""
        # Implementation for storing match-level player statistics
        # This would include goals, assists, minutes played, etc.
        pass

    def _log_collection_metadata(self, collection_type: str, records_collected: int,
                                duration: float, status: str, error_message: str = None) -> None:
        """Log collection metadata to database."""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO api_collection_metadata (
                    collection_type, records_collected, collection_duration_seconds,
                    collection_status, error_messages
                ) VALUES (%s, %s, %s, %s, %s);
            """

            cursor.execute(query, (collection_type, records_collected, duration, status, error_message))
            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to log collection metadata: {e}")


def main():
    """Main entry point for the enhanced collector."""
    logger.info("🏆 Enhanced SportMonks Collector for Real Madrid")
    logger.info("=" * 60)

    try:
        collector = EnhancedSportMonksCollector()
        success = collector.run_comprehensive_collection()

        if success:
            logger.info("🎉 Data collection completed successfully!")
            sys.exit(0)
        else:
            logger.error("💥 Data collection failed!")
            sys.exit(1)

    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

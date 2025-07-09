#!/usr/bin/env python3
"""
Unified Data Collector for ADS599 Capstone Soccer Intelligence System
Integrates SportMonks and API-Football APIs with comprehensive error handling
"""

import asyncio
import aiohttp
import yaml
import json
import logging
import time
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """Configuration for API endpoints."""
    name: str
    base_url: str
    api_key: str
    rate_limit: int
    timeout: int
    retry_attempts: int
    retry_delay: float

@dataclass
class CollectionResult:
    """Result of a data collection operation."""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    api_source: str = ""
    collection_time: datetime = None
    records_count: int = 0

class UnifiedDataCollector:
    """Unified data collector for multiple soccer APIs."""
    
    def __init__(self, config_path: str = "config"):
        """Initialize the unified data collector."""
        self.config_path = Path(config_path)
        self.load_configurations()
        self.setup_connections()
        self.collection_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cached_responses': 0,
            'start_time': datetime.now()
        }
        
    def load_configurations(self):
        """Load all configuration files."""
        try:
            # Load API keys
            with open(self.config_path / "api_keys.yaml", 'r') as f:
                api_config = yaml.safe_load(f)
            
            # Load data collection config
            with open(self.config_path / "data_collection_config.yaml", 'r') as f:
                collection_config = yaml.safe_load(f)
            
            # Setup API configurations
            self.apis = {
                'sportmonks': APIConfig(
                    name='SportMonks',
                    base_url=api_config['sportmonks']['base_url'],
                    api_key=api_config['sportmonks']['api_key'],
                    rate_limit=api_config['sportmonks']['rate_limit'],
                    timeout=api_config['sportmonks']['timeout'],
                    retry_attempts=api_config['sportmonks']['retry_attempts'],
                    retry_delay=api_config['sportmonks']['retry_delay']
                ),
                'api_football': APIConfig(
                    name='API-Football',
                    base_url=api_config['api_football']['base_url'],
                    api_key=api_config['api_football']['key'],
                    rate_limit=api_config['api_football']['rate_limit'],
                    timeout=api_config['api_football']['timeout'],
                    retry_attempts=api_config['api_football']['retry_attempts'],
                    retry_delay=api_config['api_football']['retry_delay']
                )
            }
            
            # Store collection configuration
            self.collection_config = collection_config
            self.db_config = api_config['database']
            self.redis_config = api_config['redis']
            
            logger.info("✅ Configurations loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load configurations: {e}")
            raise
    
    def setup_connections(self):
        """Setup database and cache connections."""
        try:
            # Setup PostgreSQL connection
            self.db_conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['name'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            self.db_cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            
            # Setup Redis connection
            self.redis_client = redis.Redis(
                host=self.redis_config['host'],
                port=self.redis_config['port'],
                password=self.redis_config['password'],
                db=self.redis_config['db'],
                decode_responses=True
            )
            
            # Test connections
            self.db_cursor.execute("SELECT 1")
            self.redis_client.ping()
            
            logger.info("✅ Database and cache connections established")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup connections: {e}")
            raise
    
    def generate_cache_key(self, api_name: str, endpoint: str, params: Dict) -> str:
        """Generate a unique cache key for API requests."""
        key_data = f"{api_name}:{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached API response if available."""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                self.collection_stats['cached_responses'] += 1
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
            return None
    
    async def cache_response(self, cache_key: str, data: Dict, ttl_hours: int = 24):
        """Cache API response."""
        try:
            ttl_seconds = ttl_hours * 3600
            self.redis_client.setex(
                cache_key, 
                ttl_seconds, 
                json.dumps(data, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
    
    async def make_api_request(
        self, 
        api_name: str, 
        endpoint: str, 
        params: Dict = None,
        use_cache: bool = True
    ) -> CollectionResult:
        """Make an API request with caching and error handling."""
        api_config = self.apis[api_name]
        params = params or {}
        
        # Generate cache key
        cache_key = self.generate_cache_key(api_name, endpoint, params)
        
        # Check cache first
        if use_cache:
            cached_data = await self.get_cached_response(cache_key)
            if cached_data:
                return CollectionResult(
                    success=True,
                    data=cached_data,
                    api_source=api_name,
                    collection_time=datetime.now(),
                    records_count=len(cached_data.get('data', []))
                )
        
        # Prepare request
        url = f"{api_config.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers(api_name, api_config)
        
        # Add API key to params
        if api_name == 'sportmonks':
            params['api_token'] = api_config.api_key
        
        self.collection_stats['total_requests'] += 1
        
        # Make request with retries
        for attempt in range(api_config.retry_attempts):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=api_config.timeout)) as session:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Cache successful response
                            if use_cache:
                                await self.cache_response(cache_key, data)
                            
                            self.collection_stats['successful_requests'] += 1
                            
                            return CollectionResult(
                                success=True,
                                data=data,
                                api_source=api_name,
                                collection_time=datetime.now(),
                                records_count=len(data.get('data', []))
                            )
                        else:
                            logger.warning(f"API {api_name} returned status {response.status} for {endpoint}")
                            
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {api_name} {endpoint}: {e}")
                if attempt < api_config.retry_attempts - 1:
                    await asyncio.sleep(api_config.retry_delay * (2 ** attempt))
        
        # All attempts failed
        self.collection_stats['failed_requests'] += 1
        return CollectionResult(
            success=False,
            error=f"Failed after {api_config.retry_attempts} attempts",
            api_source=api_name,
            collection_time=datetime.now()
        )
    
    def _get_headers(self, api_name: str, api_config: APIConfig) -> Dict[str, str]:
        """Get appropriate headers for each API."""
        if api_name == 'api_football':
            return {
                'X-RapidAPI-Key': api_config.api_key,
                'X-RapidAPI-Host': 'v3.football.api-sports.io'
            }
        else:
            return {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
    
    async def collect_team_data(self, team_config: Dict) -> CollectionResult:
        """Collect comprehensive data for a specific team."""
        team_name = team_config['name']
        logger.info(f"🔄 Collecting data for {team_name}")
        
        results = {
            'team_info': None,
            'players': None,
            'matches': None,
            'statistics': None
        }
        
        try:
            # Collect from SportMonks
            if 'sportmonks_id' in team_config:
                sportmonks_results = await self._collect_sportmonks_team_data(team_config)
                results.update(sportmonks_results)
            
            # Collect from API-Football
            if 'api_football_id' in team_config:
                api_football_results = await self._collect_api_football_team_data(team_config)
                # Merge results intelligently
                results = self._merge_team_data(results, api_football_results)
            
            return CollectionResult(
                success=True,
                data=results,
                api_source="unified",
                collection_time=datetime.now(),
                records_count=sum(len(v) if isinstance(v, list) else 1 for v in results.values() if v)
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to collect data for {team_name}: {e}")
            return CollectionResult(
                success=False,
                error=str(e),
                api_source="unified",
                collection_time=datetime.now()
            )
    
    async def _collect_sportmonks_team_data(self, team_config: Dict) -> Dict:
        """Collect team data from SportMonks API."""
        team_id = team_config['sportmonks_id']
        results = {}
        
        # Team information
        team_result = await self.make_api_request(
            'sportmonks',
            f'/football/teams/{team_id}',
            {'include': 'venue,country'}
        )
        if team_result.success:
            results['team_info'] = team_result.data
        
        # Players
        players_result = await self.make_api_request(
            'sportmonks',
            f'/football/squads/seasons/{self.collection_config["seasons"][-1]["sportmonks_id"]}/teams/{team_id}',
            {'include': 'player.position,player.nationality'}
        )
        if players_result.success:
            results['players'] = players_result.data
        
        return results
    
    async def _collect_api_football_team_data(self, team_config: Dict) -> Dict:
        """Collect team data from API-Football."""
        team_id = team_config['api_football_id']
        results = {}
        
        # Team information
        team_result = await self.make_api_request(
            'api_football',
            '/teams',
            {'id': team_id}
        )
        if team_result.success:
            results['team_info_api'] = team_result.data
        
        return results
    
    def _merge_team_data(self, sportmonks_data: Dict, api_football_data: Dict) -> Dict:
        """Intelligently merge data from both APIs."""
        merged = sportmonks_data.copy()
        
        # Add API-Football data where SportMonks data is missing
        for key, value in api_football_data.items():
            if key not in merged or not merged[key]:
                merged[key] = value
        
        return merged
    
    def get_collection_stats(self) -> Dict:
        """Get current collection statistics."""
        runtime = datetime.now() - self.collection_stats['start_time']
        
        return {
            **self.collection_stats,
            'runtime_minutes': runtime.total_seconds() / 60,
            'success_rate': (
                self.collection_stats['successful_requests'] / 
                max(self.collection_stats['total_requests'], 1)
            ),
            'cache_hit_rate': (
                self.collection_stats['cached_responses'] / 
                max(self.collection_stats['total_requests'], 1)
            )
        }
    
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
    """Main function for testing the unified data collector."""
    collector = UnifiedDataCollector()
    
    try:
        # Test with Real Madrid
        real_madrid_config = {
            'name': 'Real Madrid',
            'sportmonks_id': 53,
            'api_football_id': 541
        }
        
        result = await collector.collect_team_data(real_madrid_config)
        
        if result.success:
            print(f"✅ Successfully collected data for Real Madrid")
            print(f"📊 Records collected: {result.records_count}")
            print(f"🕒 Collection time: {result.collection_time}")
        else:
            print(f"❌ Failed to collect data: {result.error}")
        
        # Print statistics
        stats = collector.get_collection_stats()
        print(f"\n📈 Collection Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    finally:
        collector.close_connections()

if __name__ == "__main__":
    asyncio.run(main())

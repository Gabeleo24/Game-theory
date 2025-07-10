"""
Redis Caching Strategy for Football Database
Implements caching patterns for optimal performance
"""

import redis
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pickle

class FootballRedisCache:
    """
    Redis caching implementation for football database
    Provides caching for player stats, match data, and analytics
    """
    
    def __init__(self, host='localhost', port=6379, password=None, db=0):
        """Initialize Redis connection with connection pooling"""
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            password=password,
            db=db,
            max_connections=20,
            retry_on_timeout=True
        )
        self.redis_client = redis.Redis(connection_pool=self.pool)
        
        # Cache TTL settings (in seconds)
        self.TTL_SETTINGS = {
            'player_stats': 3600,      # 1 hour
            'match_data': 1800,        # 30 minutes
            'season_stats': 7200,      # 2 hours
            'live_match': 30,          # 30 seconds
            'team_info': 86400,        # 24 hours
            'league_standings': 1800,   # 30 minutes
            'player_search': 600,      # 10 minutes
            'analytics': 3600          # 1 hour
        }
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate consistent cache keys"""
        key_parts = [prefix]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for Redis storage"""
        if isinstance(data, (dict, list)):
            return json.dumps(data, default=str).encode('utf-8')
        return pickle.dumps(data)
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data from Redis"""
        try:
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return pickle.loads(data)
    
    # =====================================================
    # PLAYER CACHING METHODS
    # =====================================================
    
    def cache_player_stats(self, player_id: str, season: str, stats: Dict) -> bool:
        """Cache player season statistics"""
        key = self._generate_cache_key("player_stats", player_id=player_id, season=season)
        data = self._serialize_data(stats)
        return self.redis_client.setex(key, self.TTL_SETTINGS['player_stats'], data)
    
    def get_player_stats(self, player_id: str, season: str) -> Optional[Dict]:
        """Retrieve cached player statistics"""
        key = self._generate_cache_key("player_stats", player_id=player_id, season=season)
        data = self.redis_client.get(key)
        return self._deserialize_data(data) if data else None
    
    def cache_player_match_performance(self, player_id: str, match_id: str, performance: Dict) -> bool:
        """Cache individual match performance"""
        key = self._generate_cache_key("player_match", player_id=player_id, match_id=match_id)
        data = self._serialize_data(performance)
        return self.redis_client.setex(key, self.TTL_SETTINGS['match_data'], data)
    
    def get_player_match_performance(self, player_id: str, match_id: str) -> Optional[Dict]:
        """Retrieve cached match performance"""
        key = self._generate_cache_key("player_match", player_id=player_id, match_id=match_id)
        data = self.redis_client.get(key)
        return self._deserialize_data(data) if data else None
    
    # =====================================================
    # MATCH CACHING METHODS
    # =====================================================
    
    def cache_match_data(self, match_id: str, match_data: Dict) -> bool:
        """Cache complete match information"""
        key = self._generate_cache_key("match", match_id=match_id)
        data = self._serialize_data(match_data)
        return self.redis_client.setex(key, self.TTL_SETTINGS['match_data'], data)
    
    def get_match_data(self, match_id: str) -> Optional[Dict]:
        """Retrieve cached match data"""
        key = self._generate_cache_key("match", match_id=match_id)
        data = self.redis_client.get(key)
        return self._deserialize_data(data) if data else None
    
    def cache_live_match_updates(self, match_id: str, live_data: Dict) -> bool:
        """Cache live match updates with short TTL"""
        key = self._generate_cache_key("live_match", match_id=match_id)
        data = self._serialize_data(live_data)
        return self.redis_client.setex(key, self.TTL_SETTINGS['live_match'], data)
    
    # =====================================================
    # TEAM CACHING METHODS
    # =====================================================
    
    def cache_team_squad(self, team_id: str, season: str, squad_data: List[Dict]) -> bool:
        """Cache team squad information"""
        key = self._generate_cache_key("team_squad", team_id=team_id, season=season)
        data = self._serialize_data(squad_data)
        return self.redis_client.setex(key, self.TTL_SETTINGS['team_info'], data)
    
    def get_team_squad(self, team_id: str, season: str) -> Optional[List[Dict]]:
        """Retrieve cached team squad"""
        key = self._generate_cache_key("team_squad", team_id=team_id, season=season)
        data = self.redis_client.get(key)
        return self._deserialize_data(data) if data else None
    
    def cache_manchester_city_key_players(self, key_players: List[Dict]) -> bool:
        """Cache Manchester City key players for validation"""
        key = "manchester_city:key_players"
        data = self._serialize_data(key_players)
        return self.redis_client.setex(key, self.TTL_SETTINGS['team_info'], data)
    
    # =====================================================
    # ANALYTICS CACHING METHODS
    # =====================================================
    
    def cache_player_analytics(self, player_id: str, analytics_type: str, data: Dict) -> bool:
        """Cache player analytics results"""
        key = self._generate_cache_key("analytics", player_id=player_id, type=analytics_type)
        serialized_data = self._serialize_data(data)
        return self.redis_client.setex(key, self.TTL_SETTINGS['analytics'], serialized_data)
    
    def get_player_analytics(self, player_id: str, analytics_type: str) -> Optional[Dict]:
        """Retrieve cached analytics"""
        key = self._generate_cache_key("analytics", player_id=player_id, type=analytics_type)
        data = self.redis_client.get(key)
        return self._deserialize_data(data) if data else None
    
    def cache_team_comparison(self, team1_id: str, team2_id: str, season: str, comparison_data: Dict) -> bool:
        """Cache team comparison analytics"""
        # Ensure consistent ordering for cache key
        teams = sorted([team1_id, team2_id])
        key = self._generate_cache_key("team_comparison", team1=teams[0], team2=teams[1], season=season)
        data = self._serialize_data(comparison_data)
        return self.redis_client.setex(key, self.TTL_SETTINGS['analytics'], data)
    
    # =====================================================
    # SEARCH AND LEADERBOARD CACHING
    # =====================================================
    
    def cache_player_search_results(self, search_query: str, results: List[Dict]) -> bool:
        """Cache player search results"""
        query_hash = hashlib.md5(search_query.lower().encode()).hexdigest()
        key = f"search:players:{query_hash}"
        data = self._serialize_data(results)
        return self.redis_client.setex(key, self.TTL_SETTINGS['player_search'], data)
    
    def get_player_search_results(self, search_query: str) -> Optional[List[Dict]]:
        """Retrieve cached search results"""
        query_hash = hashlib.md5(search_query.lower().encode()).hexdigest()
        key = f"search:players:{query_hash}"
        data = self.redis_client.get(key)
        return self._deserialize_data(data) if data else None
    
    def cache_leaderboard(self, stat_type: str, season: str, competition: str, leaderboard: List[Dict]) -> bool:
        """Cache statistical leaderboards"""
        key = self._generate_cache_key("leaderboard", stat=stat_type, season=season, competition=competition)
        data = self._serialize_data(leaderboard)
        return self.redis_client.setex(key, self.TTL_SETTINGS['analytics'], data)
    
    # =====================================================
    # UTILITY METHODS
    # =====================================================
    
    def invalidate_player_cache(self, player_id: str) -> int:
        """Invalidate all cache entries for a specific player"""
        pattern = f"*player*{player_id}*"
        keys = self.redis_client.keys(pattern)
        return self.redis_client.delete(*keys) if keys else 0
    
    def invalidate_match_cache(self, match_id: str) -> int:
        """Invalidate all cache entries for a specific match"""
        pattern = f"*match*{match_id}*"
        keys = self.redis_client.keys(pattern)
        return self.redis_client.delete(*keys) if keys else 0
    
    def get_cache_stats(self) -> Dict:
        """Get Redis cache statistics"""
        info = self.redis_client.info()
        return {
            'used_memory': info.get('used_memory_human'),
            'connected_clients': info.get('connected_clients'),
            'total_commands_processed': info.get('total_commands_processed'),
            'keyspace_hits': info.get('keyspace_hits'),
            'keyspace_misses': info.get('keyspace_misses'),
            'hit_rate': info.get('keyspace_hits', 0) / max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1)
        }
    
    def health_check(self) -> bool:
        """Check Redis connection health"""
        try:
            return self.redis_client.ping()
        except:
            return False

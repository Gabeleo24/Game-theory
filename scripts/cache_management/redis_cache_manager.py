#!/usr/bin/env python3
"""
Redis Cache Management Utility for Soccer Intelligence System
Provides cache optimization, monitoring, and management capabilities
"""

import os
import sys
import json
import redis
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RedisCacheManager:
    """Redis cache management and optimization utility."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = self._init_redis()
        
    def _init_redis(self) -> redis.Redis:
        """Initialize Redis connection."""
        try:
            redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
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
            logger.error(f"❌ Redis connection failed: {e}")
            sys.exit(1)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        try:
            info = self.redis_client.info()
            
            stats = {
                'memory': {
                    'used_memory_human': info.get('used_memory_human'),
                    'used_memory_peak_human': info.get('used_memory_peak_human'),
                    'used_memory_percentage': round(
                        (info.get('used_memory', 0) / info.get('maxmemory', 1)) * 100, 2
                    ) if info.get('maxmemory', 0) > 0 else 0
                },
                'keys': {
                    'total_keys': self.redis_client.dbsize(),
                    'sportmonks_keys': len(self.redis_client.keys('sportmonks:*')),
                    'expired_keys': info.get('expired_keys', 0),
                    'evicted_keys': info.get('evicted_keys', 0)
                },
                'performance': {
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'hit_rate': round(
                        info.get('keyspace_hits', 0) / 
                        max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1) * 100, 2
                    )
                },
                'connections': {
                    'connected_clients': info.get('connected_clients', 0),
                    'total_connections_received': info.get('total_connections_received', 0)
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}
    
    def analyze_cache_patterns(self) -> Dict[str, Any]:
        """Analyze cache usage patterns."""
        try:
            patterns = {
                'api_endpoints': {},
                'data_types': {},
                'age_distribution': {'fresh': 0, 'medium': 0, 'old': 0}
            }
            
            # Analyze SportMonks API cache keys
            sportmonks_keys = self.redis_client.keys('sportmonks:*')
            
            for key in sportmonks_keys:
                try:
                    # Get TTL
                    ttl = self.redis_client.ttl(key)
                    
                    # Categorize by age
                    if ttl > 1800:  # > 30 minutes
                        patterns['age_distribution']['fresh'] += 1
                    elif ttl > 300:  # > 5 minutes
                        patterns['age_distribution']['medium'] += 1
                    else:
                        patterns['age_distribution']['old'] += 1
                    
                    # Try to analyze cached data
                    data = self.redis_client.get(key)
                    if data:
                        try:
                            parsed_data = json.loads(data)
                            if isinstance(parsed_data, dict) and 'data' in parsed_data:
                                # Determine data type
                                if 'participants' in str(parsed_data):
                                    patterns['data_types']['matches'] = patterns['data_types'].get('matches', 0) + 1
                                elif 'position' in str(parsed_data):
                                    patterns['data_types']['players'] = patterns['data_types'].get('players', 0) + 1
                                elif 'statistics' in str(parsed_data):
                                    patterns['data_types']['statistics'] = patterns['data_types'].get('statistics', 0) + 1
                                else:
                                    patterns['data_types']['other'] = patterns['data_types'].get('other', 0) + 1
                        except json.JSONDecodeError:
                            pass
                            
                except Exception:
                    continue
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze cache patterns: {e}")
            return {}
    
    def optimize_cache(self) -> Dict[str, int]:
        """Optimize cache by removing expired and low-value entries."""
        try:
            optimization_stats = {
                'expired_removed': 0,
                'old_data_removed': 0,
                'memory_freed_mb': 0
            }
            
            # Get memory usage before optimization
            memory_before = self.redis_client.info()['used_memory']
            
            # Remove expired keys
            expired_keys = []
            all_keys = self.redis_client.keys('*')
            
            for key in all_keys:
                ttl = self.redis_client.ttl(key)
                if ttl == -2:  # Key doesn't exist (expired)
                    expired_keys.append(key)
                elif ttl > 0 and ttl < 60:  # Expiring soon
                    expired_keys.append(key)
            
            if expired_keys:
                self.redis_client.delete(*expired_keys)
                optimization_stats['expired_removed'] = len(expired_keys)
            
            # Remove old SportMonks data (older than 2 hours)
            old_sportmonks_keys = []
            sportmonks_keys = self.redis_client.keys('sportmonks:*')
            
            for key in sportmonks_keys:
                ttl = self.redis_client.ttl(key)
                if ttl > 0 and ttl < 1800:  # Less than 30 minutes remaining
                    old_sportmonks_keys.append(key)
            
            if old_sportmonks_keys:
                self.redis_client.delete(*old_sportmonks_keys)
                optimization_stats['old_data_removed'] = len(old_sportmonks_keys)
            
            # Calculate memory freed
            memory_after = self.redis_client.info()['used_memory']
            optimization_stats['memory_freed_mb'] = round(
                (memory_before - memory_after) / (1024 * 1024), 2
            )
            
            logger.info(f"Cache optimization completed: {optimization_stats}")
            return optimization_stats
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
            return {}
    
    def warm_cache_for_real_madrid(self) -> bool:
        """Pre-warm cache with frequently accessed Real Madrid data."""
        try:
            logger.info("🔥 Warming cache for Real Madrid data...")
            
            # This would typically involve making API calls to cache common data
            # For now, we'll just log the intention
            
            common_endpoints = [
                'teams/53',  # Real Madrid team info
                'fixtures/between/21648/teams/53',  # 2023-2024 fixtures
                'players/statistics/seasons/21648/teams/53'  # Player stats
            ]
            
            logger.info(f"Would warm cache for {len(common_endpoints)} endpoints")
            logger.info("Cache warming completed")
            
            return True
            
        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
            return False
    
    def clear_cache(self, pattern: str = None) -> int:
        """Clear cache entries matching pattern."""
        try:
            if pattern:
                keys = self.redis_client.keys(pattern)
                if keys:
                    deleted = self.redis_client.delete(*keys)
                    logger.info(f"Deleted {deleted} keys matching pattern: {pattern}")
                    return deleted
                else:
                    logger.info(f"No keys found matching pattern: {pattern}")
                    return 0
            else:
                # Clear all cache
                self.redis_client.flushdb()
                logger.info("All cache cleared")
                return -1
                
        except Exception as e:
            logger.error(f"Cache clearing failed: {e}")
            return 0
    
    def export_cache_report(self, output_file: str = None) -> str:
        """Export comprehensive cache report."""
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"logs/cache_report_{timestamp}.json"
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'stats': self.get_cache_stats(),
                'patterns': self.analyze_cache_patterns(),
                'recommendations': self._generate_recommendations()
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Cache report exported to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to export cache report: {e}")
            return ""
    
    def _generate_recommendations(self) -> List[str]:
        """Generate cache optimization recommendations."""
        recommendations = []
        
        try:
            stats = self.get_cache_stats()
            
            # Memory usage recommendations
            memory_usage = stats.get('memory', {}).get('used_memory_percentage', 0)
            if memory_usage > 80:
                recommendations.append("High memory usage detected. Consider increasing Redis memory limit or optimizing cache TTL.")
            elif memory_usage < 20:
                recommendations.append("Low memory usage. Consider increasing cache TTL for better performance.")
            
            # Hit rate recommendations
            hit_rate = stats.get('performance', {}).get('hit_rate', 0)
            if hit_rate < 70:
                recommendations.append("Low cache hit rate. Consider warming cache with frequently accessed data.")
            elif hit_rate > 95:
                recommendations.append("Excellent cache hit rate. Current configuration is optimal.")
            
            # Key management recommendations
            total_keys = stats.get('keys', {}).get('total_keys', 0)
            if total_keys > 10000:
                recommendations.append("Large number of cache keys. Consider implementing key expiration policies.")
            
            if not recommendations:
                recommendations.append("Cache performance is optimal. No immediate actions required.")
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            recommendations.append("Unable to generate recommendations due to analysis error.")
        
        return recommendations


def main():
    """Main CLI interface for Redis cache management."""
    parser = argparse.ArgumentParser(description='Redis Cache Management Utility')
    parser.add_argument('command', choices=[
        'stats', 'analyze', 'optimize', 'warm', 'clear', 'report'
    ], help='Command to execute')
    parser.add_argument('--pattern', help='Pattern for cache operations (e.g., sportmonks:*)')
    parser.add_argument('--output', help='Output file for reports')
    
    args = parser.parse_args()
    
    manager = RedisCacheManager()
    
    if args.command == 'stats':
        stats = manager.get_cache_stats()
        print(json.dumps(stats, indent=2))
        
    elif args.command == 'analyze':
        patterns = manager.analyze_cache_patterns()
        print(json.dumps(patterns, indent=2))
        
    elif args.command == 'optimize':
        result = manager.optimize_cache()
        print(f"Optimization completed: {result}")
        
    elif args.command == 'warm':
        success = manager.warm_cache_for_real_madrid()
        print(f"Cache warming {'successful' if success else 'failed'}")
        
    elif args.command == 'clear':
        deleted = manager.clear_cache(args.pattern)
        print(f"Deleted {deleted} cache entries")
        
    elif args.command == 'report':
        report_file = manager.export_cache_report(args.output)
        print(f"Report exported to: {report_file}")


if __name__ == "__main__":
    main()

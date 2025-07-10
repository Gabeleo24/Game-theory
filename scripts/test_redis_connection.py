#!/usr/bin/env python3
"""
Test Redis Connection
Simple script to test Redis connectivity and basic operations
"""

import redis
import yaml
import os
import sys
from datetime import datetime

def load_config():
    """Load Redis configuration from config file."""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'api_keys.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config['redis']
    except FileNotFoundError:
        print("❌ Config file not found. Using default localhost settings.")
        return {
            'host': 'localhost',
            'port': 6379,
            'password': 'redispass123',
            'db': 0
        }

def test_redis_connection():
    """Test Redis connection and basic operations."""
    print("🔄 Testing Redis Connection...")
    print("=" * 50)
    
    # Load configuration
    redis_config = load_config()
    print(f"📍 Connecting to Redis at {redis_config['host']}:{redis_config['port']}")
    
    try:
        # Create Redis connection
        r = redis.Redis(
            host=redis_config['host'],
            port=redis_config['port'],
            password=redis_config['password'],
            db=redis_config['db'],
            decode_responses=True
        )
        
        # Test connection
        print("🔍 Testing basic connectivity...")
        pong = r.ping()
        if pong:
            print("✅ Redis connection successful!")
        
        # Test basic operations
        print("\n🧪 Testing basic Redis operations...")
        
        # Set a test key
        test_key = f"test:connection:{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_value = "Hello from Manchester City Analytics!"
        
        r.set(test_key, test_value, ex=60)  # Expire in 60 seconds
        print(f"✅ SET operation successful: {test_key}")
        
        # Get the test key
        retrieved_value = r.get(test_key)
        if retrieved_value == test_value:
            print(f"✅ GET operation successful: {retrieved_value}")
        
        # Test hash operations (useful for caching player stats)
        hash_key = f"player:test:{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        player_data = {
            'name': 'Erling Haaland',
            'position': 'Forward',
            'goals': '36',
            'assists': '8'
        }
        
        r.hset(hash_key, mapping=player_data)
        print(f"✅ HSET operation successful: {hash_key}")
        
        # Retrieve hash data
        retrieved_player = r.hgetall(hash_key)
        if retrieved_player:
            print(f"✅ HGETALL operation successful: {retrieved_player}")
        
        # Test list operations (useful for match history)
        list_key = f"matches:test:{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        matches = ['vs Arsenal', 'vs Liverpool', 'vs Chelsea']
        
        for match in matches:
            r.lpush(list_key, match)
        print(f"✅ LIST operations successful: {list_key}")
        
        # Get list length
        list_length = r.llen(list_key)
        print(f"✅ List length: {list_length}")
        
        # Get Redis info
        print("\n📊 Redis Server Information:")
        info = r.info()
        print(f"   Redis Version: {info.get('redis_version', 'Unknown')}")
        print(f"   Used Memory: {info.get('used_memory_human', 'Unknown')}")
        print(f"   Connected Clients: {info.get('connected_clients', 'Unknown')}")
        print(f"   Total Commands Processed: {info.get('total_commands_processed', 'Unknown')}")
        
        # Clean up test keys
        r.delete(test_key, hash_key, list_key)
        print("\n🧹 Test keys cleaned up")
        
        print("\n" + "=" * 50)
        print("🎉 All Redis tests passed successfully!")
        print("🚀 Redis is ready for Manchester City analytics caching!")
        
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
        print("💡 Make sure Redis is running: docker compose up -d redis")
        return False
    except redis.AuthenticationError as e:
        print(f"❌ Redis authentication failed: {e}")
        print("💡 Check your Redis password in the config file")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_redis_usage_examples():
    """Show examples of how to use Redis for caching."""
    print("\n" + "=" * 50)
    print("📚 Redis Usage Examples for Soccer Analytics")
    print("=" * 50)
    
    examples = [
        {
            'title': 'Cache Player Statistics',
            'code': '''
# Cache player match statistics
player_stats = {
    'goals': 2,
    'assists': 1,
    'shots': 5,
    'rating': 8.5
}
redis_client.hset('player:haaland:match:123', mapping=player_stats)
'''
        },
        {
            'title': 'Cache API Responses',
            'code': '''
# Cache SportMonks API response for 1 hour
api_response = get_match_data_from_api(match_id)
redis_client.setex(f'api:match:{match_id}', 3600, json.dumps(api_response))
'''
        },
        {
            'title': 'Cache Query Results',
            'code': '''
# Cache expensive PostgreSQL query results
query_result = execute_complex_analytics_query()
redis_client.setex('analytics:top_performers:2023', 1800, json.dumps(query_result))
'''
        },
        {
            'title': 'Session Management',
            'code': '''
# Store user session data
session_data = {'user_id': 123, 'preferences': {'team': 'Manchester City'}}
redis_client.setex(f'session:{session_id}', 86400, json.dumps(session_data))
'''
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}:")
        print(example['code'])

if __name__ == "__main__":
    success = test_redis_connection()
    
    if success:
        show_redis_usage_examples()
    else:
        print("\n💡 Troubleshooting Tips:")
        print("1. Make sure Docker is running")
        print("2. Start Redis: docker compose up -d redis")
        print("3. Check Redis logs: docker compose logs redis")
        print("4. Verify port 6379 is not in use by another service")
        
    sys.exit(0 if success else 1)

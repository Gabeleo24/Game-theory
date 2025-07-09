#!/usr/bin/env python3
"""
TEST SPORTMONKS API ENDPOINTS
Test various SportMonks API endpoints to find working ones
"""

import requests
import json
import yaml
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SportMonksAPITester:
    """Test SportMonks API endpoints."""
    
    def __init__(self):
        """Initialize with API configuration."""
        self.load_config()
        self.session = requests.Session()
        self.base_url = "https://api.sportmonks.com/v3/football"
        
    def load_config(self):
        """Load SportMonks API configuration."""
        try:
            with open('config/api_keys.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            self.api_token = config.get('sportmonks', {}).get('api_key')
            
            if self.api_token:
                logger.info("✅ SportMonks API token loaded successfully")
            else:
                logger.error("❌ SportMonks API token not found")
                raise ValueError("SportMonks API token required")
                
        except FileNotFoundError:
            logger.error("❌ Config file not found: config/api_keys.yaml")
            raise
    
    def test_endpoint(self, endpoint: str, params: dict = None) -> dict:
        """Test a specific API endpoint."""
        try:
            if params is None:
                params = {'api_token': self.api_token}
            else:
                params['api_token'] = self.api_token
            
            response = self.session.get(endpoint, params=params, timeout=10)
            
            logger.info(f"Testing: {endpoint}")
            logger.info(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Success! Data keys: {list(data.keys())}")
                return data
            else:
                logger.error(f"❌ Failed: {response.text[:200]}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error testing {endpoint}: {e}")
            return {}
    
    def test_basic_endpoints(self):
        """Test basic API endpoints."""
        logger.info("🔍 Testing basic SportMonks API endpoints...")
        
        # Test basic endpoints
        endpoints = [
            f"{self.base_url}/teams",
            f"{self.base_url}/seasons",
            f"{self.base_url}/leagues",
            f"{self.base_url}/players"
        ]
        
        for endpoint in endpoints:
            self.test_endpoint(endpoint, {'per_page': 5})
            print("-" * 50)
    
    def test_real_madrid_endpoints(self):
        """Test Real Madrid specific endpoints."""
        logger.info("🔍 Testing Real Madrid specific endpoints...")
        
        # Test Real Madrid team ID 53
        real_madrid_endpoints = [
            f"{self.base_url}/teams/53",
            f"{self.base_url}/teams/search/Real Madrid",
            f"{self.base_url}/teams/53/players",
            f"{self.base_url}/teams/53/squad"
        ]
        
        for endpoint in real_madrid_endpoints:
            self.test_endpoint(endpoint)
            print("-" * 50)
    
    def test_season_endpoints(self):
        """Test season-related endpoints."""
        logger.info("🔍 Testing season endpoints...")
        
        # Test season endpoints
        season_endpoints = [
            f"{self.base_url}/seasons/21646",  # 2023-2024 season
            f"{self.base_url}/seasons/21646/teams",
            f"{self.base_url}/seasons/21646/teams/53"
        ]
        
        for endpoint in season_endpoints:
            self.test_endpoint(endpoint)
            print("-" * 50)
    
    def search_real_madrid(self):
        """Search for Real Madrid team."""
        logger.info("🔍 Searching for Real Madrid...")
        
        # Try different search methods
        search_endpoints = [
            f"{self.base_url}/teams",
            f"{self.base_url}/teams/search/Real",
            f"{self.base_url}/teams/search/Madrid"
        ]
        
        for endpoint in search_endpoints:
            params = {'per_page': 20}
            if 'search' not in endpoint:
                params['filters'] = 'name:Real Madrid'
            
            data = self.test_endpoint(endpoint, params)
            
            if data and 'data' in data:
                teams = data['data']
                for team in teams:
                    if isinstance(team, dict) and 'name' in team:
                        if 'Real Madrid' in team.get('name', ''):
                            logger.info(f"🎯 Found Real Madrid: ID={team.get('id')}, Name={team.get('name')}")
            
            print("-" * 50)
    
    def test_subscription_info(self):
        """Test subscription information."""
        logger.info("🔍 Testing subscription information...")
        
        # Test subscription endpoint
        subscription_endpoint = f"{self.base_url}/my/subscription"
        data = self.test_endpoint(subscription_endpoint)
        
        if data:
            print(json.dumps(data, indent=2))

def main():
    """Main function to test API endpoints."""
    try:
        tester = SportMonksAPITester()
        
        print("=" * 80)
        print("SPORTMONKS API ENDPOINT TESTING")
        print("=" * 80)
        
        # Test subscription first
        tester.test_subscription_info()
        print("\n" + "=" * 80)
        
        # Test basic endpoints
        tester.test_basic_endpoints()
        print("\n" + "=" * 80)
        
        # Search for Real Madrid
        tester.search_real_madrid()
        print("\n" + "=" * 80)
        
        # Test Real Madrid specific endpoints
        tester.test_real_madrid_endpoints()
        print("\n" + "=" * 80)
        
        # Test season endpoints
        tester.test_season_endpoints()
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Data Ingestion Pipeline for Dynamic Sports Performance Analytics Engine
Automated data collection, processing, and real-time updates
"""

import asyncio
import aiohttp
import sqlite3
import json
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import schedule
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.data_structures import PerformanceDataStructures, Player
from core.algorithms import PerformanceScoreAlgorithm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """Configuration for external API connections."""
    name: str
    base_url: str
    api_key: str
    rate_limit: int  # requests per minute
    timeout: int = 30

class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, max_requests: int, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        """Acquire permission to make a request."""
        now = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        # Check if we can make a request
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
                return await self.acquire()
        
        # Record this request
        self.requests.append(now)

class DataIngestionPipeline:
    """
    Main data ingestion pipeline with rate limiting, error handling, and real-time updates.
    """
    
    def __init__(self, data_structures: PerformanceDataStructures):
        self.data_structures = data_structures
        self.performance_algorithm = PerformanceScoreAlgorithm()
        self.api_configs = self._load_api_configs()
        self.rate_limiters = {
            config.name: RateLimiter(config.rate_limit) 
            for config in self.api_configs
        }
        self.session = None
        self.is_running = False
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'players_updated': 0,
            'last_update': None
        }
    
    def _load_api_configs(self) -> List[APIConfig]:
        """Load API configurations."""
        # In production, this would load from environment variables or config files
        return [
            APIConfig(
                name="sportapi",
                base_url="https://v3.football.api-sports.io",
                api_key="5ced20dec7f4b2226c8944c88c6d86aa",  # Your API key
                rate_limit=10  # 10 requests per minute for free tier
            ),
            APIConfig(
                name="sportmonks",
                base_url="https://api.sportmonks.com/v3/football",
                api_key="rhcvz5smy1FKTKqaEI1kbuhJlAZLADDHQvvDquOHbpDsjfHbwE6OxP5MMS4p",
                rate_limit=60  # 60 requests per minute
            )
        ]
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def make_api_request(self, api_name: str, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make rate-limited API request with error handling."""
        api_config = next((config for config in self.api_configs if config.name == api_name), None)
        if not api_config:
            logger.error(f"API configuration not found: {api_name}")
            return None
        
        # Apply rate limiting
        await self.rate_limiters[api_name].acquire()
        
        url = f"{api_config.base_url}/{endpoint}"
        headers = {}
        
        # Set API-specific headers
        if api_name == "sportapi":
            headers["X-RapidAPI-Key"] = api_config.api_key
            headers["X-RapidAPI-Host"] = "v3.football.api-sports.io"
        elif api_name == "sportmonks":
            if params is None:
                params = {}
            params["api_token"] = api_config.api_key
        
        try:
            self.stats['total_requests'] += 1
            
            async with self.session.get(
                url, 
                headers=headers, 
                params=params, 
                timeout=aiohttp.ClientTimeout(total=api_config.timeout)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    self.stats['successful_requests'] += 1
                    logger.debug(f"Successful request to {api_name}: {endpoint}")
                    return data
                else:
                    logger.error(f"API request failed: {response.status} - {await response.text()}")
                    self.stats['failed_requests'] += 1
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Request timeout for {api_name}: {endpoint}")
            self.stats['failed_requests'] += 1
            return None
        except Exception as e:
            logger.error(f"Request error for {api_name}: {endpoint} - {str(e)}")
            self.stats['failed_requests'] += 1
            return None
    
    async def fetch_team_players(self, team_id: int, season: int) -> List[Dict]:
        """Fetch players for a specific team and season."""
        players = []
        
        # Try SportAPI first
        sportapi_data = await self.make_api_request(
            "sportapi",
            f"players/squads",
            {"team": team_id, "season": season}
        )
        
        if sportapi_data and "response" in sportapi_data:
            for team_data in sportapi_data["response"]:
                if "players" in team_data:
                    for player_data in team_data["players"]:
                        player_info = self._parse_sportapi_player(player_data, team_id)
                        if player_info:
                            players.append(player_info)
        
        # Supplement with SportMonks data if needed
        if len(players) < 20:  # If we don't have enough players
            sportmonks_data = await self.make_api_request(
                "sportmonks",
                f"squads/seasons/{season}/teams/{team_id}",
                {"include": "player"}
            )
            
            if sportmonks_data and "data" in sportmonks_data:
                for squad_member in sportmonks_data["data"]:
                    if "player" in squad_member:
                        player_info = self._parse_sportmonks_player(squad_member["player"], team_id)
                        if player_info and not any(p["player_id"] == player_info["player_id"] for p in players):
                            players.append(player_info)
        
        return players
    
    def _parse_sportapi_player(self, player_data: Dict, team_id: int) -> Optional[Dict]:
        """Parse player data from SportAPI format."""
        try:
            player = player_data.get("player", {})
            statistics = player_data.get("statistics", [{}])[0] if player_data.get("statistics") else {}
            
            return {
                "player_id": player.get("id"),
                "name": player.get("name", "Unknown"),
                "position": self._normalize_position(player.get("position", "Unknown")),
                "team_id": team_id,
                "age": player.get("age", 25),
                "stats": {
                    "goals": statistics.get("goals", {}).get("total", 0) or 0,
                    "assists": statistics.get("goals", {}).get("assists", 0) or 0,
                    "pass_accuracy": statistics.get("passes", {}).get("accuracy", 0) or 0,
                    "shots_total": statistics.get("shots", {}).get("total", 0) or 0,
                    "tackles_won": statistics.get("tackles", {}).get("total", 0) or 0,
                    "interceptions": statistics.get("tackles", {}).get("interceptions", 0) or 0,
                    "key_passes": statistics.get("passes", {}).get("key", 0) or 0,
                    "minutes_played": statistics.get("games", {}).get("minutes", 0) or 0,
                    "average_rating": float(statistics.get("games", {}).get("rating", 0) or 0)
                }
            }
        except Exception as e:
            logger.error(f"Error parsing SportAPI player data: {e}")
            return None
    
    def _parse_sportmonks_player(self, player_data: Dict, team_id: int) -> Optional[Dict]:
        """Parse player data from SportMonks format."""
        try:
            return {
                "player_id": player_data.get("id"),
                "name": player_data.get("display_name", "Unknown"),
                "position": self._normalize_position(player_data.get("position", {}).get("name", "Unknown")),
                "team_id": team_id,
                "age": self._calculate_age(player_data.get("date_of_birth")),
                "stats": {
                    "goals": 0,  # Would need additional API calls for detailed stats
                    "assists": 0,
                    "pass_accuracy": 0,
                    "shots_total": 0,
                    "tackles_won": 0,
                    "interceptions": 0,
                    "key_passes": 0,
                    "minutes_played": 0,
                    "average_rating": 0
                }
            }
        except Exception as e:
            logger.error(f"Error parsing SportMonks player data: {e}")
            return None
    
    def _normalize_position(self, position: str) -> str:
        """Normalize position names to standard categories."""
        position = position.lower()
        
        if any(pos in position for pos in ["goalkeeper", "keeper", "gk"]):
            return "Goalkeeper"
        elif any(pos in position for pos in ["defender", "defence", "back", "cb", "lb", "rb"]):
            return "Defender"
        elif any(pos in position for pos in ["midfielder", "midfield", "cm", "dm", "am"]):
            return "Midfielder"
        elif any(pos in position for pos in ["forward", "attacker", "striker", "winger", "lw", "rw"]):
            return "Attacker"
        else:
            return "Unknown"
    
    def _calculate_age(self, date_of_birth: str) -> int:
        """Calculate age from date of birth."""
        if not date_of_birth:
            return 25  # Default age
        
        try:
            birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return max(16, min(45, age))  # Reasonable age bounds
        except:
            return 25
    
    async def update_player_data(self, player_data: Dict):
        """Update player data in the system."""
        try:
            # Calculate performance score
            stats = player_data["stats"]
            score = self.performance_algorithm.calculate_performance_score(stats, player_data["position"])
            
            # Create or update player
            player = Player(
                player_id=player_data["player_id"],
                name=player_data["name"],
                position=player_data["position"],
                team_id=player_data["team_id"],
                age=player_data["age"],
                performance_score=score,
                stats=stats,
                last_updated=datetime.now().timestamp()
            )
            
            # Add to data structures
            self.data_structures.add_player(player)
            self.stats['players_updated'] += 1
            
            logger.debug(f"Updated player: {player.name} (ID: {player.player_id}) - Score: {score:.2f}")
            
        except Exception as e:
            logger.error(f"Error updating player data: {e}")
    
    async def run_daily_update(self):
        """Run daily data update for all teams."""
        logger.info("Starting daily data update")
        start_time = time.time()
        
        # Manchester City team ID and current season
        team_id = 50  # Manchester City ID in SportAPI
        season = 2023
        
        try:
            # Fetch player data
            players = await self.fetch_team_players(team_id, season)
            
            # Update each player
            for player_data in players:
                await self.update_player_data(player_data)
            
            self.stats['last_update'] = datetime.now().isoformat()
            
            duration = time.time() - start_time
            logger.info(f"Daily update completed in {duration:.2f} seconds. Updated {len(players)} players.")
            
        except Exception as e:
            logger.error(f"Error in daily update: {e}")
    
    async def run_real_time_updates(self):
        """Run real-time updates for live match data."""
        logger.info("Starting real-time update monitoring")
        
        while self.is_running:
            try:
                # Check for live matches
                live_matches = await self.make_api_request(
                    "sportapi",
                    "fixtures",
                    {"live": "all", "team": 50}  # Manchester City
                )
                
                if live_matches and "response" in live_matches:
                    for match in live_matches["response"]:
                        await self.process_live_match(match)
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in real-time updates: {e}")
                await asyncio.sleep(60)
    
    async def process_live_match(self, match_data: Dict):
        """Process live match data for real-time updates."""
        # This would implement real-time player performance updates
        # For now, just log the match
        logger.info(f"Processing live match: {match_data.get('fixture', {}).get('id')}")
    
    def start_scheduled_updates(self):
        """Start scheduled data updates."""
        # Schedule daily updates
        schedule.every().day.at("02:00").do(lambda: asyncio.create_task(self.run_daily_update()))
        
        # Schedule hourly light updates
        schedule.every().hour.do(lambda: asyncio.create_task(self.run_light_update()))
        
        logger.info("Scheduled updates configured")
    
    async def run_light_update(self):
        """Run light update for recent changes."""
        logger.info("Running light update")
        # Implement light update logic here
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            **self.stats,
            'success_rate': (self.stats['successful_requests'] / max(1, self.stats['total_requests'])) * 100,
            'is_running': self.is_running
        }

async def main():
    """Main function for running the data pipeline."""
    # Initialize data structures
    data_structures = PerformanceDataStructures()
    
    # Create and run pipeline
    async with DataIngestionPipeline(data_structures) as pipeline:
        # Run initial data load
        await pipeline.run_daily_update()
        
        # Print statistics
        stats = pipeline.get_pipeline_stats()
        print(f"Pipeline completed. Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())

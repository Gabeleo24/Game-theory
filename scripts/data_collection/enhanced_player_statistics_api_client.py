#!/usr/bin/env python3
"""
Enhanced Player Statistics API Client for ADS599 Capstone Project

This module provides comprehensive player-level data collection capabilities,
including individual match performance, formations, and tactical analysis.

Features:
- Individual player match statistics
- Team formation data collection
- Match events and tactical changes
- Integration with existing team statistics
- Comprehensive caching and rate limiting
"""

import json
import time
import requests
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PlayerMatchPerformance:
    """Data class for individual player match performance."""
    player_id: int
    player_name: str
    team_id: int
    fixture_id: int
    minutes_played: int
    position: str
    rating: Optional[float]
    goals: int
    assists: int
    shots_total: int
    shots_on_target: int
    passes_total: int
    passes_completed: int
    pass_accuracy: float
    tackles: int
    interceptions: int
    fouls_committed: int
    fouls_drawn: int
    yellow_cards: int
    red_cards: int
    substitution_in: Optional[int]
    substitution_out: Optional[int]

@dataclass
class TeamFormation:
    """Data class for team formation data."""
    fixture_id: int
    team_id: int
    formation: str
    starting_eleven: List[Dict[str, Any]]
    substitutes: List[Dict[str, Any]]
    coach: Dict[str, Any]

class EnhancedPlayerStatisticsAPIClient:
    """Enhanced API client for comprehensive player statistics collection."""
    
    def __init__(self, config_path: str = "config/api_keys.yaml"):
        """
        Initialize the enhanced player statistics API client.
        
        Args:
            config_path: Path to API configuration file
        """
        self.config = self._load_config(config_path)
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = self._setup_headers()
        self.cache_dir = Path("data/cache/player_statistics")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting
        self.requests_made = 0
        self.last_request_time = 0
        self.min_request_interval = 0.6  # seconds between requests
        
        # Statistics tracking
        self.api_stats = {
            'total_requests': 0,
            'cached_requests': 0,
            'failed_requests': 0,
            'player_statistics_collected': 0,
            'formations_collected': 0,
            'match_events_collected': 0
        }
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load API configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logger.warning(f"Could not load config from {config_path}: {e}")
            return {}
    
    def _setup_headers(self) -> Dict[str, str]:
        """Setup API request headers."""
        api_key = self.config.get('api_football', {}).get('key')
        if not api_key:
            logger.warning("No API key found in configuration")
            return {}
        
        return {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'v3.football.api-sports.io'
        }
    
    def _rate_limit(self):
        """Implement rate limiting between API requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key for request."""
        params_str = "_".join([f"{k}_{v}" for k, v in sorted(params.items())])
        return f"{endpoint}_{params_str}"
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load data from cache if available."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Check if cache is recent (within 24 hours for player stats)
                cache_time = datetime.fromisoformat(cached_data.get('cache_timestamp', ''))
                if (datetime.now() - cache_time).total_seconds() < 86400:  # 24 hours
                    self.api_stats['cached_requests'] += 1
                    logger.info(f"Using cached data for {cache_key}")
                    return cached_data.get('data')
            except Exception as e:
                logger.warning(f"Error loading cache for {cache_key}: {e}")
        
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]):
        """Save data to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        cache_data = {
            'cache_timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Error saving cache for {cache_key}: {e}")
    
    def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make API request with caching and error handling.
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            
        Returns:
            API response data or None if failed
        """
        cache_key = self._get_cache_key(endpoint, params)
        
        # Try cache first
        cached_data = self._load_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Make API request
        if not self.headers:
            logger.error("No API headers configured")
            return None
        
        self._rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            self.api_stats['total_requests'] += 1
            
            # Save to cache
            self._save_to_cache(cache_key, data)
            
            logger.info(f"Successfully fetched data from {endpoint}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            self.api_stats['failed_requests'] += 1
            return None
    
    def get_match_player_statistics(self, fixture_id: int) -> List[PlayerMatchPerformance]:
        """
        Get detailed player statistics for a specific match.
        
        Args:
            fixture_id: Match fixture ID
            
        Returns:
            List of player performance data
        """
        params = {'fixture': fixture_id}
        response_data = self._make_api_request('fixtures/players', params)
        
        if not response_data:
            return []
        
        player_performances = []
        
        for team_data in response_data.get('response', []):
            team_id = team_data.get('team', {}).get('id')
            players = team_data.get('players', [])
            
            for player_data in players:
                player_info = player_data.get('player', {})
                statistics = player_data.get('statistics', [])
                
                if not statistics:
                    continue
                
                # Process player statistics (taking first statistics entry)
                stats = statistics[0]
                
                performance = PlayerMatchPerformance(
                    player_id=player_info.get('id', 0),
                    player_name=player_info.get('name', ''),
                    team_id=team_id,
                    fixture_id=fixture_id,
                    minutes_played=stats.get('games', {}).get('minutes', 0) or 0,
                    position=stats.get('games', {}).get('position', ''),
                    rating=self._safe_float(stats.get('games', {}).get('rating')),
                    goals=stats.get('goals', {}).get('total', 0) or 0,
                    assists=stats.get('goals', {}).get('assists', 0) or 0,
                    shots_total=stats.get('shots', {}).get('total', 0) or 0,
                    shots_on_target=stats.get('shots', {}).get('on', 0) or 0,
                    passes_total=stats.get('passes', {}).get('total', 0) or 0,
                    passes_completed=stats.get('passes', {}).get('accuracy', 0) or 0,
                    pass_accuracy=self._safe_float(stats.get('passes', {}).get('accuracy')),
                    tackles=stats.get('tackles', {}).get('total', 0) or 0,
                    interceptions=stats.get('tackles', {}).get('interceptions', 0) or 0,
                    fouls_committed=stats.get('fouls', {}).get('committed', 0) or 0,
                    fouls_drawn=stats.get('fouls', {}).get('drawn', 0) or 0,
                    yellow_cards=stats.get('cards', {}).get('yellow', 0) or 0,
                    red_cards=stats.get('cards', {}).get('red', 0) or 0,
                    substitution_in=self._safe_int(stats.get('games', {}).get('substitute')),
                    substitution_out=None  # Will be determined from events
                )
                
                player_performances.append(performance)
        
        self.api_stats['player_statistics_collected'] += len(player_performances)
        return player_performances
    
    def get_match_lineups(self, fixture_id: int) -> List[TeamFormation]:
        """
        Get team lineups and formation data for a specific match.
        
        Args:
            fixture_id: Match fixture ID
            
        Returns:
            List of team formation data
        """
        params = {'fixture': fixture_id}
        response_data = self._make_api_request('fixtures/lineups', params)
        
        if not response_data:
            return []
        
        formations = []
        
        for team_data in response_data.get('response', []):
            team_info = team_data.get('team', {})
            
            formation = TeamFormation(
                fixture_id=fixture_id,
                team_id=team_info.get('id', 0),
                formation=team_data.get('formation', ''),
                starting_eleven=team_data.get('startXI', []),
                substitutes=team_data.get('substitutes', []),
                coach=team_data.get('coach', {})
            )
            
            formations.append(formation)
        
        self.api_stats['formations_collected'] += len(formations)
        return formations
    
    def get_match_events(self, fixture_id: int) -> List[Dict[str, Any]]:
        """
        Get match events (goals, cards, substitutions) for a specific match.
        
        Args:
            fixture_id: Match fixture ID
            
        Returns:
            List of match events
        """
        params = {'fixture': fixture_id}
        response_data = self._make_api_request('fixtures/events', params)
        
        if not response_data:
            return []
        
        events = response_data.get('response', [])
        self.api_stats['match_events_collected'] += len(events)
        return events
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert value to float."""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert value to int."""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def get_api_statistics(self) -> Dict[str, Any]:
        """Get API usage statistics."""
        return self.api_stats.copy()
    
    def reset_statistics(self):
        """Reset API usage statistics."""
        self.api_stats = {
            'total_requests': 0,
            'cached_requests': 0,
            'failed_requests': 0,
            'player_statistics_collected': 0,
            'formations_collected': 0,
            'match_events_collected': 0
        }

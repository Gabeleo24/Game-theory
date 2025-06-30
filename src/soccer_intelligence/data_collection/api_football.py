"""
API-Football client for collecting soccer data with caching capabilities.
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

from ..utils.config import Config
from .cache_manager import CacheManager


class APIFootballClient:
    """Client for API-Football data collection with intelligent caching."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the API-Football client.
        
        Args:
            api_key: API key for API-Football. If None, loads from config.
        """
        self.config = Config()
        self.api_key = api_key or self.config.get('api_football.key')
        self.base_url = self.config.get('api_football.base_url', 'https://v3.football.api-sports.io')
        self.timeout = self.config.get('api_football.timeout', 30)
        self.rate_limit_delay = self.config.get('api_football.rate_limit_delay', 1.0)
        
        self.cache_manager = CacheManager()
        self.logger = logging.getLogger(__name__)
        
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'v3.football.api-sports.io'
        }
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request to the API-Football API with caching.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            API response data
        """
        # Check cache first
        cache_key = f"{endpoint}_{params or {}}"
        cached_data = self.cache_manager.get(cache_key)
        if cached_data:
            self.logger.info(f"Using cached data for {endpoint}")
            return cached_data
        
        # Make API request
        url = f"{self.base_url}/{endpoint}"
        
        try:
            time.sleep(self.rate_limit_delay)  # Rate limiting
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            self.cache_manager.set(cache_key, data)
            
            self.logger.info(f"Successfully fetched data from {endpoint}")
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching data from {endpoint}: {e}")
            raise
    
    def get_leagues(self, country: Optional[str] = None, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get available leagues.
        
        Args:
            country: Filter by country
            season: Filter by season
            
        Returns:
            List of league data
        """
        params = {}
        if country:
            params['country'] = country
        if season:
            params['season'] = season
            
        response = self._make_request('leagues', params)
        return response.get('response', [])
    
    def get_teams(self, league_id: int, season: int) -> List[Dict[str, Any]]:
        """
        Get teams for a specific league and season.
        
        Args:
            league_id: League ID
            season: Season year
            
        Returns:
            List of team data
        """
        params = {
            'league': league_id,
            'season': season
        }
        
        response = self._make_request('teams', params)
        return response.get('response', [])
    
    def get_matches(self, league_id: int, season: int, team_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get matches for a specific league and season.
        
        Args:
            league_id: League ID
            season: Season year
            team_id: Optional team ID filter
            
        Returns:
            List of match data
        """
        params = {
            'league': league_id,
            'season': season
        }
        
        if team_id:
            params['team'] = team_id
            
        response = self._make_request('fixtures', params)
        return response.get('response', [])
    
    def get_match_statistics(self, fixture_id: int) -> Dict[str, Any]:
        """
        Get detailed statistics for a specific match.
        
        Args:
            fixture_id: Match fixture ID
            
        Returns:
            Match statistics data
        """
        params = {'fixture': fixture_id}
        
        response = self._make_request('fixtures/statistics', params)
        return response.get('response', {})
    
    def get_player_statistics(self, player_id: int, season: int, league_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get player statistics for a season.
        
        Args:
            player_id: Player ID
            season: Season year
            league_id: Optional league ID filter
            
        Returns:
            Player statistics data
        """
        params = {
            'id': player_id,
            'season': season
        }
        
        if league_id:
            params['league'] = league_id
            
        response = self._make_request('players', params)
        return response.get('response', {})
    
    def get_team_statistics(self, team_id: int, league_id: int, season: int) -> Dict[str, Any]:
        """
        Get team statistics for a season.
        
        Args:
            team_id: Team ID
            league_id: League ID
            season: Season year
            
        Returns:
            Team statistics data
        """
        params = {
            'team': team_id,
            'league': league_id,
            'season': season
        }
        
        response = self._make_request('teams/statistics', params)
        return response.get('response', {})
    
    def get_standings(self, league_id: int, season: int) -> List[Dict[str, Any]]:
        """
        Get league standings.
        
        Args:
            league_id: League ID
            season: Season year
            
        Returns:
            League standings data
        """
        params = {
            'league': league_id,
            'season': season
        }
        
        response = self._make_request('standings', params)
        return response.get('response', [])
    
    def collect_comprehensive_data(self, league_id: int, season: int) -> Dict[str, Any]:
        """
        Collect comprehensive data for a league and season.
        
        Args:
            league_id: League ID
            season: Season year
            
        Returns:
            Comprehensive dataset
        """
        self.logger.info(f"Collecting comprehensive data for league {league_id}, season {season}")
        
        data = {
            'league_id': league_id,
            'season': season,
            'collected_at': datetime.now().isoformat(),
            'teams': [],
            'matches': [],
            'standings': [],
            'team_statistics': {}
        }
        
        # Get teams
        teams = self.get_teams(league_id, season)
        data['teams'] = teams
        
        # Get matches
        matches = self.get_matches(league_id, season)
        data['matches'] = matches
        
        # Get standings
        standings = self.get_standings(league_id, season)
        data['standings'] = standings
        
        # Get team statistics
        for team in teams:
            team_id = team['team']['id']
            team_stats = self.get_team_statistics(team_id, league_id, season)
            data['team_statistics'][team_id] = team_stats
            
            # Add delay to respect rate limits
            time.sleep(self.rate_limit_delay)
        
        self.logger.info(f"Comprehensive data collection completed for league {league_id}")
        return data

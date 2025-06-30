"""
Wikipedia data collection for historical context and player/team information.
"""

import wikipedia
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import re

from ..utils.config import Config
from .cache_manager import CacheManager


class WikipediaCollector:
    """Collects data from Wikipedia for historical context."""
    
    def __init__(self):
        """Initialize the Wikipedia collector."""
        self.config = Config()
        self.cache_manager = CacheManager()
        self.logger = logging.getLogger(__name__)
        
        # Set Wikipedia language
        wikipedia.set_lang("en")
    
    def search_page(self, query: str, auto_suggest: bool = True) -> Optional[str]:
        """
        Search for a Wikipedia page.
        
        Args:
            query: Search query
            auto_suggest: Whether to use auto-suggestion
            
        Returns:
            Page title if found, None otherwise
        """
        try:
            # Search for pages
            search_results = wikipedia.search(query, results=5)
            
            if not search_results:
                self.logger.warning(f"No Wikipedia pages found for query: {query}")
                return None
            
            # Return the first result
            return search_results[0]
            
        except wikipedia.exceptions.DisambiguationError as e:
            # Handle disambiguation pages
            self.logger.info(f"Disambiguation page found for {query}, using first option")
            return e.options[0] if e.options else None
            
        except Exception as e:
            self.logger.error(f"Error searching Wikipedia for {query}: {e}")
            return None
    
    def get_page_content(self, page_title: str) -> Optional[Dict[str, Any]]:
        """
        Get content from a Wikipedia page.
        
        Args:
            page_title: Wikipedia page title
            
        Returns:
            Page content data
        """
        # Check cache first
        cache_key = f"wikipedia_{page_title}"
        cached_data = self.cache_manager.get(cache_key)
        if cached_data:
            return cached_data.get('data')
        
        try:
            page = wikipedia.page(page_title)
            
            content_data = {
                'title': page.title,
                'url': page.url,
                'summary': page.summary,
                'content': page.content,
                'categories': page.categories,
                'links': page.links[:50],  # Limit links to avoid huge datasets
                'images': page.images[:10],  # Limit images
                'references': page.references[:20],  # Limit references
                'collected_at': datetime.now().isoformat()
            }
            
            # Cache the content
            self.cache_manager.set(cache_key, {'data': content_data})
            
            self.logger.info(f"Successfully collected Wikipedia content for: {page_title}")
            return content_data
            
        except wikipedia.exceptions.PageError:
            self.logger.warning(f"Wikipedia page not found: {page_title}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting Wikipedia content for {page_title}: {e}")
            return None
    
    def get_player_info(self, player_name: str, team_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get Wikipedia information for a player.
        
        Args:
            player_name: Player's name
            team_name: Optional team name for disambiguation
            
        Returns:
            Player information from Wikipedia
        """
        # Try different search variations
        search_queries = [
            player_name,
            f"{player_name} footballer",
            f"{player_name} soccer player"
        ]
        
        if team_name:
            search_queries.insert(1, f"{player_name} {team_name}")
        
        for query in search_queries:
            page_title = self.search_page(query)
            if page_title:
                content = self.get_page_content(page_title)
                if content and self._is_footballer_page(content):
                    return self._extract_player_info(content)
        
        self.logger.warning(f"Could not find Wikipedia page for player: {player_name}")
        return None
    
    def get_team_info(self, team_name: str) -> Optional[Dict[str, Any]]:
        """
        Get Wikipedia information for a team.
        
        Args:
            team_name: Team name
            
        Returns:
            Team information from Wikipedia
        """
        # Try different search variations
        search_queries = [
            team_name,
            f"{team_name} FC",
            f"{team_name} football club",
            f"{team_name} soccer club"
        ]
        
        for query in search_queries:
            page_title = self.search_page(query)
            if page_title:
                content = self.get_page_content(page_title)
                if content and self._is_football_club_page(content):
                    return self._extract_team_info(content)
        
        self.logger.warning(f"Could not find Wikipedia page for team: {team_name}")
        return None
    
    def get_league_info(self, league_name: str) -> Optional[Dict[str, Any]]:
        """
        Get Wikipedia information for a league.
        
        Args:
            league_name: League name
            
        Returns:
            League information from Wikipedia
        """
        page_title = self.search_page(league_name)
        if page_title:
            content = self.get_page_content(page_title)
            if content:
                return self._extract_league_info(content)
        
        self.logger.warning(f"Could not find Wikipedia page for league: {league_name}")
        return None
    
    def _is_footballer_page(self, content: Dict[str, Any]) -> bool:
        """Check if the page is about a footballer."""
        text = content.get('content', '').lower()
        categories = [cat.lower() for cat in content.get('categories', [])]
        
        # Check for footballer indicators
        footballer_keywords = ['footballer', 'soccer player', 'football player', 'midfielder', 'striker', 'defender', 'goalkeeper']
        footballer_categories = ['footballers', 'soccer players', 'association football']
        
        has_keywords = any(keyword in text for keyword in footballer_keywords)
        has_categories = any(any(cat_keyword in cat for cat_keyword in footballer_categories) for cat in categories)
        
        return has_keywords or has_categories
    
    def _is_football_club_page(self, content: Dict[str, Any]) -> bool:
        """Check if the page is about a football club."""
        text = content.get('content', '').lower()
        categories = [cat.lower() for cat in content.get('categories', [])]
        
        # Check for football club indicators
        club_keywords = ['football club', 'soccer club', 'fc', 'founded', 'stadium', 'league']
        club_categories = ['football clubs', 'soccer clubs', 'association football clubs']
        
        has_keywords = any(keyword in text for keyword in club_keywords)
        has_categories = any(any(cat_keyword in cat for cat_keyword in club_categories) for cat in categories)
        
        return has_keywords or has_categories
    
    def _extract_player_info(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured player information from Wikipedia content."""
        text = content.get('content', '')
        
        # Extract basic information using regex patterns
        birth_date_match = re.search(r'born[:\s]+(\d{1,2}\s+\w+\s+\d{4})', text, re.IGNORECASE)
        position_match = re.search(r'position[:\s]+(\w+)', text, re.IGNORECASE)
        nationality_match = re.search(r'nationality[:\s]+(\w+)', text, re.IGNORECASE)
        
        player_info = {
            'name': content.get('title'),
            'url': content.get('url'),
            'summary': content.get('summary'),
            'birth_date': birth_date_match.group(1) if birth_date_match else None,
            'position': position_match.group(1) if position_match else None,
            'nationality': nationality_match.group(1) if nationality_match else None,
            'categories': content.get('categories', []),
            'full_content': text[:2000],  # Truncate for storage
            'collected_at': content.get('collected_at')
        }
        
        return player_info
    
    def _extract_team_info(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured team information from Wikipedia content."""
        text = content.get('content', '')
        
        # Extract basic information using regex patterns
        founded_match = re.search(r'founded[:\s]+(\d{4})', text, re.IGNORECASE)
        stadium_match = re.search(r'stadium[:\s]+([^.]+)', text, re.IGNORECASE)
        league_match = re.search(r'league[:\s]+([^.]+)', text, re.IGNORECASE)
        
        team_info = {
            'name': content.get('title'),
            'url': content.get('url'),
            'summary': content.get('summary'),
            'founded': founded_match.group(1) if founded_match else None,
            'stadium': stadium_match.group(1).strip() if stadium_match else None,
            'league': league_match.group(1).strip() if league_match else None,
            'categories': content.get('categories', []),
            'full_content': text[:2000],  # Truncate for storage
            'collected_at': content.get('collected_at')
        }
        
        return team_info
    
    def _extract_league_info(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured league information from Wikipedia content."""
        text = content.get('content', '')
        
        # Extract basic information
        founded_match = re.search(r'founded[:\s]+(\d{4})', text, re.IGNORECASE)
        country_match = re.search(r'country[:\s]+(\w+)', text, re.IGNORECASE)
        
        league_info = {
            'name': content.get('title'),
            'url': content.get('url'),
            'summary': content.get('summary'),
            'founded': founded_match.group(1) if founded_match else None,
            'country': country_match.group(1) if country_match else None,
            'categories': content.get('categories', []),
            'full_content': text[:2000],  # Truncate for storage
            'collected_at': content.get('collected_at')
        }
        
        return league_info
    
    def collect_comprehensive_wikipedia_data(self, teams: List[str], players: List[str], 
                                           leagues: List[str]) -> Dict[str, Any]:
        """
        Collect comprehensive Wikipedia data for teams, players, and leagues.
        
        Args:
            teams: List of team names
            players: List of player names
            leagues: List of league names
            
        Returns:
            Comprehensive Wikipedia dataset
        """
        self.logger.info("Starting comprehensive Wikipedia data collection")
        
        data = {
            'collected_at': datetime.now().isoformat(),
            'teams': {},
            'players': {},
            'leagues': {},
            'summary': {}
        }
        
        # Collect team information
        for team in teams:
            team_info = self.get_team_info(team)
            if team_info:
                data['teams'][team] = team_info
                self.logger.info(f"Collected Wikipedia data for team: {team}")
        
        # Collect player information
        for player in players:
            player_info = self.get_player_info(player)
            if player_info:
                data['players'][player] = player_info
                self.logger.info(f"Collected Wikipedia data for player: {player}")
        
        # Collect league information
        for league in leagues:
            league_info = self.get_league_info(league)
            if league_info:
                data['leagues'][league] = league_info
                self.logger.info(f"Collected Wikipedia data for league: {league}")
        
        # Generate summary
        data['summary'] = {
            'total_teams_requested': len(teams),
            'total_players_requested': len(players),
            'total_leagues_requested': len(leagues),
            'teams_found': len(data['teams']),
            'players_found': len(data['players']),
            'leagues_found': len(data['leagues'])
        }
        
        self.logger.info("Comprehensive Wikipedia data collection completed")
        return data

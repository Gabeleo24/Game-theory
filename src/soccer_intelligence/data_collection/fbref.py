"""
FBref Data Collector

Collects football statistics and data from FBref.com
Provides detailed player statistics, team performance metrics, and match data
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import re
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse
import logging
from pathlib import Path

from ..utils.logger import get_logger
from .cache_manager import CacheManager


class FBrefCollector:
    """
    Collector for FBref.com football statistics
    
    Provides methods to scrape player statistics, team data, league tables,
    and match information from FBref.com with respectful rate limiting.
    """
    
    def __init__(self, cache_dir: str = "data/raw/fbref", delay: float = 2.0):
        """
        Initialize FBref collector
        
        Args:
            cache_dir: Directory to cache scraped data
            delay: Delay between requests in seconds (default 2.0 for respectful scraping)
        """
        self.base_url = "https://fbref.com"
        self.delay = delay
        self.cache_manager = CacheManager(cache_dir)
        self.logger = get_logger(__name__)
        
        # Session for connection pooling with comprehensive headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # Create cache directory
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        
    def _make_request(self, url: str, use_cache: bool = True) -> Optional[BeautifulSoup]:
        """
        Make HTTP request with caching and rate limiting
        
        Args:
            url: URL to request
            use_cache: Whether to use cached response if available
            
        Returns:
            BeautifulSoup object or None if request fails
        """
        # Check cache first
        if use_cache:
            cached_response = self.cache_manager.get(url)
            if cached_response and 'html_content' in cached_response:
                self.logger.info(f"Using cached data for {url}")
                return BeautifulSoup(cached_response['html_content'], 'html.parser')
        
        try:
            self.logger.info(f"Requesting: {url}")
            
            # Rate limiting
            time.sleep(self.delay)
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Cache the response
            if use_cache:
                cache_data = {
                    'html_content': response.text,
                    'status_code': response.status_code,
                    'url': url
                }
                self.cache_manager.set(url, cache_data)
            
            return BeautifulSoup(response.text, 'html.parser')
            
        except requests.RequestException as e:
            self.logger.error(f"Error requesting {url}: {e}")
            return None
    
    def get_league_table(self, league_url: str, season: str = "2024-2025") -> Optional[pd.DataFrame]:
        """
        Get league table for a specific competition
        
        Args:
            league_url: FBref league URL (e.g., "/en/comps/9/Premier-League-Stats")
            season: Season string (default "2024-2025")
            
        Returns:
            DataFrame with league table data
        """
        url = urljoin(self.base_url, league_url)
        soup = self._make_request(url)
        
        if not soup:
            return None
            
        try:
            # Find the league table
            table = soup.find('table', {'class': 'stats_table'})
            if not table:
                self.logger.warning(f"No league table found at {url}")
                return None
            
            # Extract table data
            headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]
            rows = []
            
            for tr in table.find('tbody').find_all('tr'):
                row_data = []
                for td in tr.find_all(['td', 'th']):
                    text = td.get_text(strip=True)
                    row_data.append(text)
                if row_data:
                    rows.append(row_data)
            
            df = pd.DataFrame(rows, columns=headers)
            df['season'] = season
            df['scraped_at'] = pd.Timestamp.now()
            
            self.logger.info(f"Successfully scraped league table with {len(df)} teams")
            return df
            
        except Exception as e:
            self.logger.error(f"Error parsing league table from {url}: {e}")
            return None
    
    def get_player_stats(self, league_url: str, stat_type: str = "stats") -> Optional[pd.DataFrame]:
        """
        Get player statistics for a league
        
        Args:
            league_url: FBref league URL
            stat_type: Type of stats ('stats', 'shooting', 'passing', 'defense', etc.)
            
        Returns:
            DataFrame with player statistics
        """
        # Construct stats URL
        base_league_url = league_url.rstrip('/')
        stats_url = f"{base_league_url}/{stat_type}/{base_league_url.split('/')[-1]}"
        url = urljoin(self.base_url, stats_url)
        
        soup = self._make_request(url)
        if not soup:
            return None
            
        try:
            # Find the stats table
            table = soup.find('table', {'id': f'stats_{stat_type}'})
            if not table:
                # Try alternative table ID
                table = soup.find('table', {'class': 'stats_table'})
                
            if not table:
                self.logger.warning(f"No {stat_type} table found at {url}")
                return None
            
            # Extract headers
            thead = table.find('thead')
            if not thead:
                return None
                
            # Handle multi-level headers
            header_rows = thead.find_all('tr')
            if len(header_rows) > 1:
                # Multi-level headers - combine them
                headers = []
                for i, th in enumerate(header_rows[-1].find_all('th')):
                    text = th.get_text(strip=True)
                    if not text and len(header_rows) > 1:
                        # Get text from parent header
                        parent_th = header_rows[0].find_all('th')[i] if i < len(header_rows[0].find_all('th')) else None
                        if parent_th:
                            text = parent_th.get_text(strip=True)
                    headers.append(text)
            else:
                headers = [th.get_text(strip=True) for th in header_rows[0].find_all('th')]
            
            # Extract data rows
            rows = []
            tbody = table.find('tbody')
            if tbody:
                for tr in tbody.find_all('tr'):
                    # Skip header rows within tbody
                    if tr.find('th', {'class': 'thead'}):
                        continue
                        
                    row_data = []
                    for td in tr.find_all(['td', 'th']):
                        text = td.get_text(strip=True)
                        row_data.append(text)
                    
                    if row_data and len(row_data) == len(headers):
                        rows.append(row_data)
            
            if not rows:
                self.logger.warning(f"No data rows found in {stat_type} table")
                return None
                
            df = pd.DataFrame(rows, columns=headers)
            df['stat_type'] = stat_type
            df['scraped_at'] = pd.Timestamp.now()
            
            self.logger.info(f"Successfully scraped {stat_type} stats for {len(df)} players")
            return df
            
        except Exception as e:
            self.logger.error(f"Error parsing {stat_type} stats from {url}: {e}")
            return None
    
    def get_team_stats(self, league_url: str, stat_type: str = "stats") -> Optional[pd.DataFrame]:
        """
        Get team statistics for a league
        
        Args:
            league_url: FBref league URL
            stat_type: Type of stats ('stats', 'shooting', 'passing', 'defense', etc.)
            
        Returns:
            DataFrame with team statistics
        """
        # Construct team stats URL
        base_league_url = league_url.rstrip('/')
        stats_url = f"{base_league_url}/squads/{stat_type}/{base_league_url.split('/')[-1]}"
        url = urljoin(self.base_url, stats_url)
        
        soup = self._make_request(url)
        if not soup:
            return None
            
        try:
            # Find the stats table
            table = soup.find('table', {'class': 'stats_table'})
            if not table:
                self.logger.warning(f"No team {stat_type} table found at {url}")
                return None
            
            # Extract table data similar to player stats
            headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]
            rows = []
            
            for tr in table.find('tbody').find_all('tr'):
                row_data = []
                for td in tr.find_all(['td', 'th']):
                    text = td.get_text(strip=True)
                    row_data.append(text)
                if row_data and len(row_data) == len(headers):
                    rows.append(row_data)
            
            df = pd.DataFrame(rows, columns=headers)
            df['stat_type'] = stat_type
            df['scraped_at'] = pd.Timestamp.now()
            
            self.logger.info(f"Successfully scraped team {stat_type} stats for {len(df)} teams")
            return df
            
        except Exception as e:
            self.logger.error(f"Error parsing team {stat_type} stats from {url}: {e}")
            return None
    
    def get_available_leagues(self) -> List[Dict[str, str]]:
        """
        Get list of available leagues from FBref
        
        Returns:
            List of dictionaries with league information
        """
        url = urljoin(self.base_url, "/en/comps/")
        soup = self._make_request(url)
        
        if not soup:
            return []
            
        leagues = []
        try:
            # Find competition links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/en/comps/' in href and href.count('/') >= 4:
                    text = link.get_text(strip=True)
                    if text and not any(skip in text.lower() for skip in ['stats', 'history', 'fixtures']):
                        leagues.append({
                            'name': text,
                            'url': href,
                            'full_url': urljoin(self.base_url, href)
                        })
            
            # Remove duplicates
            seen = set()
            unique_leagues = []
            for league in leagues:
                if league['url'] not in seen:
                    seen.add(league['url'])
                    unique_leagues.append(league)
            
            self.logger.info(f"Found {len(unique_leagues)} available leagues")
            return unique_leagues
            
        except Exception as e:
            self.logger.error(f"Error getting available leagues: {e}")
            return []
    
    def save_data(self, data: pd.DataFrame, filename: str) -> bool:
        """
        Save scraped data to file
        
        Args:
            data: DataFrame to save
            filename: Output filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = Path(self.cache_manager.cache_dir) / filename
            
            if filename.endswith('.json'):
                data.to_json(filepath, orient='records', indent=2)
            else:
                data.to_csv(filepath, index=False)
            
            self.logger.info(f"Saved data to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving data to {filename}: {e}")
            return False
    
    def close(self):
        """Close the session"""
        self.session.close()

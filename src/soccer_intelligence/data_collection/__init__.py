"""
Data Collection Module

Handles data collection from multiple sources:
- API-Football for match and player statistics
- FBref for detailed football statistics and analysis
- Social media data collection
- Wikipedia data extraction
"""

from .api_football import APIFootballClient
from .fbref import FBrefCollector
from .social_media import SocialMediaCollector
from .wikipedia import WikipediaCollector
from .cache_manager import CacheManager

__all__ = [
    'APIFootballClient',
    'FBrefCollector',
    'SocialMediaCollector',
    'WikipediaCollector',
    'CacheManager'
]

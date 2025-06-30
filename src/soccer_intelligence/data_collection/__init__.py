"""
Data Collection Module

Handles data collection from multiple sources:
- API-Football for match and player statistics
- Social media data collection
- Wikipedia data extraction
"""

from .api_football import APIFootballClient
from .social_media import SocialMediaCollector
from .wikipedia import WikipediaCollector
from .cache_manager import CacheManager

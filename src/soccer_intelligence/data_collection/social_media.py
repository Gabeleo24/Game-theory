"""
Social media data collection for player and team sentiment analysis.
"""

import tweepy
import requests
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from ..utils.config import Config
from .cache_manager import CacheManager


class SocialMediaCollector:
    """Collects social media data for sentiment analysis."""
    
    def __init__(self, twitter_bearer_token: Optional[str] = None):
        """
        Initialize the social media collector.
        
        Args:
            twitter_bearer_token: Twitter API bearer token
        """
        self.config = Config()
        self.bearer_token = twitter_bearer_token or self.config.get('twitter.bearer_token')
        self.cache_manager = CacheManager()
        self.logger = logging.getLogger(__name__)
        
        # Initialize Twitter API client
        if self.bearer_token:
            self.twitter_client = tweepy.Client(bearer_token=self.bearer_token)
        else:
            self.twitter_client = None
            self.logger.warning("Twitter bearer token not provided. Twitter functionality disabled.")
    
    def search_tweets(self, query: str, max_results: int = 100, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Search for tweets related to a query.
        
        Args:
            query: Search query
            max_results: Maximum number of tweets to return
            days_back: Number of days to look back
            
        Returns:
            List of tweet data
        """
        if not self.twitter_client:
            self.logger.error("Twitter client not initialized")
            return []
        
        # Check cache first
        cache_key = f"tweets_{query}_{max_results}_{days_back}"
        cached_data = self.cache_manager.get(cache_key)
        if cached_data:
            return cached_data.get('data', [])
        
        try:
            # Calculate start time
            start_time = datetime.now() - timedelta(days=days_back)
            
            # Search tweets
            tweets = tweepy.Paginator(
                self.twitter_client.search_recent_tweets,
                query=query,
                max_results=min(max_results, 100),  # API limit
                start_time=start_time,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations']
            ).flatten(limit=max_results)
            
            tweet_data = []
            for tweet in tweets:
                tweet_info = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                    'author_id': tweet.author_id,
                    'public_metrics': tweet.public_metrics,
                    'context_annotations': tweet.context_annotations
                }
                tweet_data.append(tweet_info)
            
            # Cache the results
            self.cache_manager.set(cache_key, {'data': tweet_data})
            
            self.logger.info(f"Collected {len(tweet_data)} tweets for query: {query}")
            return tweet_data
            
        except Exception as e:
            self.logger.error(f"Error searching tweets: {e}")
            return []
    
    def get_player_mentions(self, player_name: str, team_name: Optional[str] = None, 
                           max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Get social media mentions for a specific player.
        
        Args:
            player_name: Player's name
            team_name: Optional team name for more specific search
            max_results: Maximum number of mentions to return
            
        Returns:
            List of mention data
        """
        # Construct search query
        query = f'"{player_name}"'
        if team_name:
            query += f' "{team_name}"'
        
        # Add soccer-related keywords to filter relevant tweets
        query += ' (soccer OR football OR goal OR assist OR match)'
        
        return self.search_tweets(query, max_results)
    
    def get_team_mentions(self, team_name: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Get social media mentions for a specific team.
        
        Args:
            team_name: Team name
            max_results: Maximum number of mentions to return
            
        Returns:
            List of mention data
        """
        # Construct search query for team
        query = f'"{team_name}" (soccer OR football OR match OR game OR win OR loss)'
        
        return self.search_tweets(query, max_results)
    
    def get_match_sentiment(self, team1: str, team2: str, match_date: datetime) -> Dict[str, Any]:
        """
        Get social media sentiment around a specific match.
        
        Args:
            team1: First team name
            team2: Second team name
            match_date: Date of the match
            
        Returns:
            Match sentiment data
        """
        # Search for tweets about the match
        query = f'("{team1}" OR "{team2}") (vs OR against OR match)'
        
        # Search tweets from match day and day after
        tweets = []
        for days_back in [0, 1]:  # Match day and day after
            search_date = match_date + timedelta(days=days_back)
            daily_tweets = self.search_tweets(query, max_results=50, days_back=1)
            tweets.extend(daily_tweets)
        
        # Basic sentiment analysis (can be enhanced with proper NLP)
        sentiment_data = {
            'total_tweets': len(tweets),
            'match_date': match_date.isoformat(),
            'teams': [team1, team2],
            'tweets': tweets,
            'sentiment_summary': self._analyze_basic_sentiment(tweets)
        }
        
        return sentiment_data
    
    def _analyze_basic_sentiment(self, tweets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform basic sentiment analysis on tweets.
        
        Args:
            tweets: List of tweet data
            
        Returns:
            Basic sentiment analysis results
        """
        if not tweets:
            return {'positive': 0, 'negative': 0, 'neutral': 0}
        
        # Simple keyword-based sentiment analysis
        positive_keywords = ['win', 'victory', 'great', 'amazing', 'excellent', 'fantastic', 'goal']
        negative_keywords = ['loss', 'defeat', 'terrible', 'awful', 'bad', 'disappointing', 'miss']
        
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for tweet in tweets:
            text = tweet.get('text', '').lower()
            
            positive_score = sum(1 for keyword in positive_keywords if keyword in text)
            negative_score = sum(1 for keyword in negative_keywords if keyword in text)
            
            if positive_score > negative_score:
                sentiment_counts['positive'] += 1
            elif negative_score > positive_score:
                sentiment_counts['negative'] += 1
            else:
                sentiment_counts['neutral'] += 1
        
        # Calculate percentages
        total = len(tweets)
        sentiment_percentages = {
            'positive_pct': round((sentiment_counts['positive'] / total) * 100, 2),
            'negative_pct': round((sentiment_counts['negative'] / total) * 100, 2),
            'neutral_pct': round((sentiment_counts['neutral'] / total) * 100, 2)
        }
        
        return {**sentiment_counts, **sentiment_percentages}
    
    def collect_comprehensive_social_data(self, teams: List[str], players: List[str]) -> Dict[str, Any]:
        """
        Collect comprehensive social media data for teams and players.
        
        Args:
            teams: List of team names
            players: List of player names
            
        Returns:
            Comprehensive social media dataset
        """
        self.logger.info("Starting comprehensive social media data collection")
        
        data = {
            'collected_at': datetime.now().isoformat(),
            'team_mentions': {},
            'player_mentions': {},
            'summary': {}
        }
        
        # Collect team mentions
        for team in teams:
            team_data = self.get_team_mentions(team)
            data['team_mentions'][team] = team_data
            self.logger.info(f"Collected {len(team_data)} mentions for team: {team}")
        
        # Collect player mentions
        for player in players:
            player_data = self.get_player_mentions(player)
            data['player_mentions'][player] = player_data
            self.logger.info(f"Collected {len(player_data)} mentions for player: {player}")
        
        # Generate summary
        total_team_mentions = sum(len(mentions) for mentions in data['team_mentions'].values())
        total_player_mentions = sum(len(mentions) for mentions in data['player_mentions'].values())
        
        data['summary'] = {
            'total_teams': len(teams),
            'total_players': len(players),
            'total_team_mentions': total_team_mentions,
            'total_player_mentions': total_player_mentions,
            'total_mentions': total_team_mentions + total_player_mentions
        }
        
        self.logger.info("Comprehensive social media data collection completed")
        return data

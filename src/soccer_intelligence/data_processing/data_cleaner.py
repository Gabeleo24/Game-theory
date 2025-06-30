"""
Data cleaning module for soccer performance data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime

from ..utils.config import Config
from ..utils.helpers import clean_numeric_value, normalize_team_name, normalize_player_name


class DataCleaner:
    """Handles data cleaning and validation for soccer data."""
    
    def __init__(self):
        """Initialize the data cleaner."""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
    
    def clean_match_data(self, matches: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Clean and standardize match data.
        
        Args:
            matches: List of match data dictionaries
            
        Returns:
            Cleaned match data as DataFrame
        """
        self.logger.info(f"Cleaning {len(matches)} match records")
        
        cleaned_matches = []
        
        for match in matches:
            try:
                cleaned_match = self._clean_single_match(match)
                if cleaned_match:
                    cleaned_matches.append(cleaned_match)
            except Exception as e:
                self.logger.warning(f"Error cleaning match {match.get('fixture', {}).get('id', 'unknown')}: {e}")
        
        df = pd.DataFrame(cleaned_matches)
        
        if not df.empty:
            df = self._standardize_match_columns(df)
            df = self._validate_match_data(df)
        
        self.logger.info(f"Successfully cleaned {len(df)} match records")
        return df
    
    def _clean_single_match(self, match: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean a single match record."""
        fixture = match.get('fixture', {})
        teams = match.get('teams', {})
        goals = match.get('goals', {})
        score = match.get('score', {})
        
        # Extract basic match information
        cleaned = {
            'match_id': fixture.get('id'),
            'date': fixture.get('date'),
            'status': fixture.get('status', {}).get('long'),
            'venue': fixture.get('venue', {}).get('name'),
            'city': fixture.get('venue', {}).get('city'),
            'referee': fixture.get('referee'),
            
            # Home team
            'home_team_id': teams.get('home', {}).get('id'),
            'home_team_name': normalize_team_name(teams.get('home', {}).get('name', '')),
            'home_team_logo': teams.get('home', {}).get('logo'),
            
            # Away team
            'away_team_id': teams.get('away', {}).get('id'),
            'away_team_name': normalize_team_name(teams.get('away', {}).get('name', '')),
            'away_team_logo': teams.get('away', {}).get('logo'),
            
            # Goals
            'home_goals': clean_numeric_value(goals.get('home')),
            'away_goals': clean_numeric_value(goals.get('away')),
            
            # Score details
            'home_goals_halftime': clean_numeric_value(score.get('halftime', {}).get('home')),
            'away_goals_halftime': clean_numeric_value(score.get('halftime', {}).get('away')),
            'home_goals_fulltime': clean_numeric_value(score.get('fulltime', {}).get('home')),
            'away_goals_fulltime': clean_numeric_value(score.get('fulltime', {}).get('away')),
        }
        
        # Validate required fields
        if not all([cleaned['match_id'], cleaned['home_team_id'], cleaned['away_team_id']]):
            return None
        
        return cleaned
    
    def _standardize_match_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize match DataFrame columns."""
        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['year'] = df['date'].dt.year
            df['month'] = df['date'].dt.month
            df['day_of_week'] = df['date'].dt.day_name()
        
        # Calculate derived fields
        if 'home_goals' in df.columns and 'away_goals' in df.columns:
            df['total_goals'] = df['home_goals'] + df['away_goals']
            df['goal_difference'] = df['home_goals'] - df['away_goals']
            
            # Match result from home team perspective
            df['result'] = df['goal_difference'].apply(
                lambda x: 'Win' if x > 0 else ('Loss' if x < 0 else 'Draw')
            )
        
        return df
    
    def _validate_match_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and filter match data."""
        initial_count = len(df)
        
        # Remove matches with invalid data
        df = df.dropna(subset=['match_id', 'home_team_id', 'away_team_id'])
        
        # Remove duplicate matches
        df = df.drop_duplicates(subset=['match_id'])
        
        # Filter out matches with negative goals
        if 'home_goals' in df.columns and 'away_goals' in df.columns:
            df = df[(df['home_goals'] >= 0) & (df['away_goals'] >= 0)]
        
        final_count = len(df)
        if final_count < initial_count:
            self.logger.info(f"Filtered out {initial_count - final_count} invalid match records")
        
        return df
    
    def clean_player_data(self, players: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Clean and standardize player data.
        
        Args:
            players: List of player data dictionaries
            
        Returns:
            Cleaned player data as DataFrame
        """
        self.logger.info(f"Cleaning {len(players)} player records")
        
        cleaned_players = []
        
        for player_data in players:
            try:
                cleaned_player = self._clean_single_player(player_data)
                if cleaned_player:
                    cleaned_players.append(cleaned_player)
            except Exception as e:
                self.logger.warning(f"Error cleaning player data: {e}")
        
        df = pd.DataFrame(cleaned_players)
        
        if not df.empty:
            df = self._standardize_player_columns(df)
            df = self._validate_player_data(df)
        
        self.logger.info(f"Successfully cleaned {len(df)} player records")
        return df
    
    def _clean_single_player(self, player_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean a single player record."""
        player = player_data.get('player', {})
        statistics = player_data.get('statistics', [])
        
        if not statistics:
            return None
        
        # Take the first statistics entry (usually the main one)
        stats = statistics[0]
        team = stats.get('team', {})
        games = stats.get('games', {})
        goals = stats.get('goals', {})
        passes = stats.get('passes', {})
        tackles = stats.get('tackles', {})
        duels = stats.get('duels', {})
        
        cleaned = {
            'player_id': player.get('id'),
            'player_name': normalize_player_name(player.get('name', '')),
            'firstname': player.get('firstname'),
            'lastname': player.get('lastname'),
            'age': clean_numeric_value(player.get('age')),
            'birth_date': player.get('birth', {}).get('date'),
            'birth_place': player.get('birth', {}).get('place'),
            'birth_country': player.get('birth', {}).get('country'),
            'nationality': player.get('nationality'),
            'height': player.get('height'),
            'weight': player.get('weight'),
            'photo': player.get('photo'),
            
            # Team information
            'team_id': team.get('id'),
            'team_name': normalize_team_name(team.get('name', '')),
            
            # Game statistics
            'games_appearances': clean_numeric_value(games.get('appearences')),
            'games_lineups': clean_numeric_value(games.get('lineups')),
            'games_minutes': clean_numeric_value(games.get('minutes')),
            'games_position': games.get('position'),
            'games_rating': clean_numeric_value(games.get('rating')),
            'games_captain': games.get('captain'),
            
            # Goal statistics
            'goals_total': clean_numeric_value(goals.get('total')),
            'goals_conceded': clean_numeric_value(goals.get('conceded')),
            'goals_assists': clean_numeric_value(goals.get('assists')),
            'goals_saves': clean_numeric_value(goals.get('saves')),
            
            # Passing statistics
            'passes_total': clean_numeric_value(passes.get('total')),
            'passes_key': clean_numeric_value(passes.get('key')),
            'passes_accuracy': clean_numeric_value(passes.get('accuracy')),
            
            # Defensive statistics
            'tackles_total': clean_numeric_value(tackles.get('total')),
            'tackles_blocks': clean_numeric_value(tackles.get('blocks')),
            'tackles_interceptions': clean_numeric_value(tackles.get('interceptions')),
            
            # Duel statistics
            'duels_total': clean_numeric_value(duels.get('total')),
            'duels_won': clean_numeric_value(duels.get('won')),
        }
        
        # Validate required fields
        if not all([cleaned['player_id'], cleaned['player_name']]):
            return None
        
        return cleaned
    
    def _standardize_player_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize player DataFrame columns."""
        # Convert birth date
        if 'birth_date' in df.columns:
            df['birth_date'] = pd.to_datetime(df['birth_date'], errors='coerce')
        
        # Calculate derived metrics
        if 'games_minutes' in df.columns and 'games_appearances' in df.columns:
            df['minutes_per_game'] = df['games_minutes'] / df['games_appearances'].replace(0, np.nan)
        
        if 'goals_total' in df.columns and 'games_appearances' in df.columns:
            df['goals_per_game'] = df['goals_total'] / df['games_appearances'].replace(0, np.nan)
        
        if 'passes_total' in df.columns and 'passes_accuracy' in df.columns:
            df['passes_completed'] = (df['passes_total'] * df['passes_accuracy'] / 100).round()
        
        if 'duels_total' in df.columns and 'duels_won' in df.columns:
            df['duel_success_rate'] = (df['duels_won'] / df['duels_total'].replace(0, np.nan) * 100).round(2)
        
        return df
    
    def _validate_player_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and filter player data."""
        initial_count = len(df)
        
        # Remove players with invalid data
        df = df.dropna(subset=['player_id', 'player_name'])
        
        # Remove duplicate players
        df = df.drop_duplicates(subset=['player_id'])
        
        # Filter out players with negative statistics
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col.startswith(('goals_', 'games_', 'passes_', 'tackles_', 'duels_')):
                df = df[df[col] >= 0]
        
        final_count = len(df)
        if final_count < initial_count:
            self.logger.info(f"Filtered out {initial_count - final_count} invalid player records")
        
        return df
    
    def clean_team_data(self, teams: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Clean and standardize team data.
        
        Args:
            teams: List of team data dictionaries
            
        Returns:
            Cleaned team data as DataFrame
        """
        self.logger.info(f"Cleaning {len(teams)} team records")
        
        cleaned_teams = []
        
        for team_data in teams:
            try:
                cleaned_team = self._clean_single_team(team_data)
                if cleaned_team:
                    cleaned_teams.append(cleaned_team)
            except Exception as e:
                self.logger.warning(f"Error cleaning team data: {e}")
        
        df = pd.DataFrame(cleaned_teams)
        
        if not df.empty:
            df = self._validate_team_data(df)
        
        self.logger.info(f"Successfully cleaned {len(df)} team records")
        return df
    
    def _clean_single_team(self, team_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean a single team record."""
        team = team_data.get('team', {})
        venue = team_data.get('venue', {})
        
        cleaned = {
            'team_id': team.get('id'),
            'team_name': normalize_team_name(team.get('name', '')),
            'team_code': team.get('code'),
            'team_country': team.get('country'),
            'team_founded': clean_numeric_value(team.get('founded')),
            'team_national': team.get('national'),
            'team_logo': team.get('logo'),
            
            # Venue information
            'venue_id': venue.get('id'),
            'venue_name': venue.get('name'),
            'venue_address': venue.get('address'),
            'venue_city': venue.get('city'),
            'venue_capacity': clean_numeric_value(venue.get('capacity')),
            'venue_surface': venue.get('surface'),
            'venue_image': venue.get('image'),
        }
        
        # Validate required fields
        if not all([cleaned['team_id'], cleaned['team_name']]):
            return None
        
        return cleaned
    
    def _validate_team_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and filter team data."""
        initial_count = len(df)
        
        # Remove teams with invalid data
        df = df.dropna(subset=['team_id', 'team_name'])
        
        # Remove duplicate teams
        df = df.drop_duplicates(subset=['team_id'])
        
        final_count = len(df)
        if final_count < initial_count:
            self.logger.info(f"Filtered out {initial_count - final_count} invalid team records")
        
        return df

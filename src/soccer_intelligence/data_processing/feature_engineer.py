"""
Feature engineering module for creating advanced soccer analytics features.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta

from ..utils.config import Config
from ..utils.helpers import safe_divide, calculate_percentage


class FeatureEngineer:
    """Creates advanced features for soccer performance analysis."""
    
    def __init__(self):
        """Initialize the feature engineer."""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
    
    def create_player_features(self, player_df: pd.DataFrame, match_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create advanced features for player analysis.
        
        Args:
            player_df: Player statistics DataFrame
            match_df: Match data DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        self.logger.info("Creating player features")
        
        df = player_df.copy()
        
        # Performance efficiency metrics
        df = self._add_efficiency_metrics(df)
        
        # Consistency metrics
        df = self._add_consistency_metrics(df)
        
        # Impact metrics
        df = self._add_impact_metrics(df)
        
        # Position-specific features
        df = self._add_position_features(df)
        
        # Age and experience features
        df = self._add_age_experience_features(df)
        
        self.logger.info(f"Created features for {len(df)} players")
        return df
    
    def _add_efficiency_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add efficiency-based metrics."""
        # Goal efficiency
        if 'goals_total' in df.columns and 'games_minutes' in df.columns:
            df['goals_per_90min'] = (df['goals_total'] / df['games_minutes'] * 90).round(3)
        
        # Assist efficiency
        if 'goals_assists' in df.columns and 'games_minutes' in df.columns:
            df['assists_per_90min'] = (df['goals_assists'] / df['games_minutes'] * 90).round(3)
        
        # Pass efficiency
        if 'passes_total' in df.columns and 'passes_accuracy' in df.columns:
            df['pass_efficiency'] = df['passes_accuracy'] / 100
        
        # Tackle efficiency
        if 'tackles_total' in df.columns and 'duels_won' in df.columns:
            df['tackle_success_rate'] = safe_divide(df['duels_won'], df['tackles_total']) * 100
        
        # Overall contribution per minute
        if all(col in df.columns for col in ['goals_total', 'goals_assists', 'games_minutes']):
            df['goal_contributions_per_90min'] = (
                (df['goals_total'] + df['goals_assists']) / df['games_minutes'] * 90
            ).round(3)
        
        return df
    
    def _add_consistency_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add consistency-based metrics."""
        # Appearance consistency
        if 'games_appearances' in df.columns and 'games_lineups' in df.columns:
            df['lineup_percentage'] = calculate_percentage(df['games_lineups'], df['games_appearances'])
        
        # Minutes consistency
        if 'games_minutes' in df.columns and 'games_appearances' in df.columns:
            df['avg_minutes_per_appearance'] = safe_divide(df['games_minutes'], df['games_appearances'])
        
        # Performance consistency (based on rating if available)
        if 'games_rating' in df.columns:
            df['performance_tier'] = pd.cut(
                df['games_rating'], 
                bins=[0, 6.0, 7.0, 8.0, 10.0], 
                labels=['Below Average', 'Average', 'Good', 'Excellent'],
                include_lowest=True
            )
        
        return df
    
    def _add_impact_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add impact-based metrics."""
        # Offensive impact
        offensive_cols = ['goals_total', 'goals_assists', 'passes_key']
        if all(col in df.columns for col in offensive_cols):
            df['offensive_impact'] = (
                df['goals_total'] * 3 + 
                df['goals_assists'] * 2 + 
                df['passes_key'] * 0.5
            ).round(2)
        
        # Defensive impact
        defensive_cols = ['tackles_total', 'tackles_interceptions', 'tackles_blocks']
        if all(col in df.columns for col in defensive_cols):
            df['defensive_impact'] = (
                df['tackles_total'] * 1.5 + 
                df['tackles_interceptions'] * 2 + 
                df['tackles_blocks'] * 1.2
            ).round(2)
        
        # Overall impact score
        if 'offensive_impact' in df.columns and 'defensive_impact' in df.columns:
            df['overall_impact'] = (df['offensive_impact'] + df['defensive_impact']).round(2)
        
        return df
    
    def _add_position_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add position-specific features."""
        if 'games_position' not in df.columns:
            return df
        
        # Standardize position names
        position_mapping = {
            'Goalkeeper': 'GK',
            'Defender': 'DEF',
            'Midfielder': 'MID',
            'Attacker': 'ATT',
            'Forward': 'ATT'
        }
        
        df['position_category'] = df['games_position'].map(position_mapping).fillna('Unknown')
        
        # Position-specific efficiency metrics
        for position in ['GK', 'DEF', 'MID', 'ATT']:
            position_mask = df['position_category'] == position
            
            if position == 'GK' and 'goals_saves' in df.columns:
                df.loc[position_mask, 'gk_saves_per_game'] = safe_divide(
                    df.loc[position_mask, 'goals_saves'], 
                    df.loc[position_mask, 'games_appearances']
                )
            
            elif position == 'DEF' and 'defensive_impact' in df.columns:
                df.loc[position_mask, 'def_impact_per_game'] = safe_divide(
                    df.loc[position_mask, 'defensive_impact'], 
                    df.loc[position_mask, 'games_appearances']
                )
            
            elif position == 'ATT' and 'offensive_impact' in df.columns:
                df.loc[position_mask, 'att_impact_per_game'] = safe_divide(
                    df.loc[position_mask, 'offensive_impact'], 
                    df.loc[position_mask, 'games_appearances']
                )
        
        return df
    
    def _add_age_experience_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add age and experience-based features."""
        if 'age' in df.columns:
            # Age categories
            df['age_category'] = pd.cut(
                df['age'], 
                bins=[0, 21, 25, 30, 35, 50], 
                labels=['Young', 'Developing', 'Prime', 'Experienced', 'Veteran'],
                include_lowest=True
            )
            
            # Peak performance indicator (typically 25-30 for soccer)
            df['in_peak_age'] = ((df['age'] >= 25) & (df['age'] <= 30)).astype(int)
        
        # Experience level based on appearances
        if 'games_appearances' in df.columns:
            df['experience_level'] = pd.cut(
                df['games_appearances'], 
                bins=[0, 10, 25, 50, 100, 1000], 
                labels=['Rookie', 'Developing', 'Regular', 'Veteran', 'Legend'],
                include_lowest=True
            )
        
        return df
    
    def create_team_features(self, team_df: pd.DataFrame, match_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create advanced features for team analysis.
        
        Args:
            team_df: Team data DataFrame
            match_df: Match data DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        self.logger.info("Creating team features")
        
        df = team_df.copy()
        
        # Add match-based features
        if not match_df.empty:
            df = self._add_team_performance_features(df, match_df)
            df = self._add_team_form_features(df, match_df)
            df = self._add_team_style_features(df, match_df)
        
        self.logger.info(f"Created features for {len(df)} teams")
        return df
    
    def _add_team_performance_features(self, team_df: pd.DataFrame, match_df: pd.DataFrame) -> pd.DataFrame:
        """Add team performance features based on match data."""
        team_stats = []
        
        for _, team in team_df.iterrows():
            team_id = team['team_id']
            
            # Get matches for this team
            home_matches = match_df[match_df['home_team_id'] == team_id]
            away_matches = match_df[match_df['away_team_id'] == team_id]
            
            # Calculate statistics
            total_matches = len(home_matches) + len(away_matches)
            
            if total_matches > 0:
                # Goals
                goals_scored = (home_matches['home_goals'].sum() + away_matches['away_goals'].sum())
                goals_conceded = (home_matches['away_goals'].sum() + away_matches['home_goals'].sum())
                
                # Results
                home_wins = len(home_matches[home_matches['result'] == 'Win'])
                away_wins = len(away_matches[away_matches['result'] == 'Loss'])  # Away win is home loss
                total_wins = home_wins + away_wins
                
                home_draws = len(home_matches[home_matches['result'] == 'Draw'])
                away_draws = len(away_matches[away_matches['result'] == 'Draw'])
                total_draws = home_draws + away_draws
                
                total_losses = total_matches - total_wins - total_draws
                
                team_stats.append({
                    'team_id': team_id,
                    'total_matches': total_matches,
                    'wins': total_wins,
                    'draws': total_draws,
                    'losses': total_losses,
                    'goals_scored': goals_scored,
                    'goals_conceded': goals_conceded,
                    'goal_difference': goals_scored - goals_conceded,
                    'points': total_wins * 3 + total_draws,
                    'win_percentage': calculate_percentage(total_wins, total_matches),
                    'goals_per_game': safe_divide(goals_scored, total_matches),
                    'goals_conceded_per_game': safe_divide(goals_conceded, total_matches),
                    'home_matches': len(home_matches),
                    'away_matches': len(away_matches),
                    'home_wins': home_wins,
                    'away_wins': away_wins
                })
            else:
                team_stats.append({
                    'team_id': team_id,
                    'total_matches': 0
                })
        
        # Merge with team data
        stats_df = pd.DataFrame(team_stats)
        return team_df.merge(stats_df, on='team_id', how='left')
    
    def _add_team_form_features(self, team_df: pd.DataFrame, match_df: pd.DataFrame) -> pd.DataFrame:
        """Add team form features (recent performance)."""
        # This would require more complex logic to track recent matches
        # For now, we'll add placeholder columns that can be calculated with more detailed match data
        
        team_df['recent_form_5'] = np.nan  # Last 5 matches form
        team_df['recent_goals_scored_5'] = np.nan  # Goals in last 5 matches
        team_df['recent_goals_conceded_5'] = np.nan  # Goals conceded in last 5 matches
        
        return team_df
    
    def _add_team_style_features(self, team_df: pd.DataFrame, match_df: pd.DataFrame) -> pd.DataFrame:
        """Add team playing style features."""
        # Calculate style indicators based on match data
        for _, team in team_df.iterrows():
            team_id = team['team_id']
            
            # Get matches for this team
            team_matches = match_df[
                (match_df['home_team_id'] == team_id) | 
                (match_df['away_team_id'] == team_id)
            ]
            
            if len(team_matches) > 0:
                # High-scoring games indicator
                high_scoring_games = len(team_matches[team_matches['total_goals'] > 2.5])
                team_df.loc[team_df['team_id'] == team_id, 'high_scoring_percentage'] = \
                    calculate_percentage(high_scoring_games, len(team_matches))
                
                # Clean sheet percentage (when not conceding)
                home_clean_sheets = len(team_matches[
                    (team_matches['home_team_id'] == team_id) & 
                    (team_matches['away_goals'] == 0)
                ])
                away_clean_sheets = len(team_matches[
                    (team_matches['away_team_id'] == team_id) & 
                    (team_matches['home_goals'] == 0)
                ])
                total_clean_sheets = home_clean_sheets + away_clean_sheets
                
                team_df.loc[team_df['team_id'] == team_id, 'clean_sheet_percentage'] = \
                    calculate_percentage(total_clean_sheets, len(team_matches))
        
        return team_df
    
    def create_match_features(self, match_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create advanced features for match analysis.
        
        Args:
            match_df: Match data DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        self.logger.info("Creating match features")
        
        df = match_df.copy()
        
        # Match characteristics
        df = self._add_match_characteristics(df)
        
        # Temporal features
        df = self._add_temporal_features(df)
        
        # Competitive features
        df = self._add_competitive_features(df)
        
        self.logger.info(f"Created features for {len(df)} matches")
        return df
    
    def _add_match_characteristics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add match characteristic features."""
        # Goal-based characteristics
        if 'total_goals' in df.columns:
            df['high_scoring'] = (df['total_goals'] > 2.5).astype(int)
            df['low_scoring'] = (df['total_goals'] < 1.5).astype(int)
            df['very_high_scoring'] = (df['total_goals'] > 4.5).astype(int)
        
        # Result characteristics
        if 'goal_difference' in df.columns:
            df['close_match'] = (abs(df['goal_difference']) <= 1).astype(int)
            df['dominant_win'] = (abs(df['goal_difference']) >= 3).astype(int)
        
        # Clean sheet indicators
        if 'home_goals' in df.columns and 'away_goals' in df.columns:
            df['home_clean_sheet'] = (df['away_goals'] == 0).astype(int)
            df['away_clean_sheet'] = (df['home_goals'] == 0).astype(int)
            df['both_teams_scored'] = ((df['home_goals'] > 0) & (df['away_goals'] > 0)).astype(int)
        
        return df
    
    def _add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add temporal features."""
        if 'date' in df.columns:
            df['season'] = df['date'].dt.year  # Simplified season calculation
            df['month'] = df['date'].dt.month
            df['day_of_week'] = df['date'].dt.dayofweek
            df['is_weekend'] = (df['day_of_week'].isin([5, 6])).astype(int)  # Saturday, Sunday
            df['is_midweek'] = (df['day_of_week'].isin([1, 2, 3])).astype(int)  # Tue, Wed, Thu
        
        return df
    
    def _add_competitive_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add competitive balance features."""
        # This would require historical team strength data
        # For now, add placeholder columns
        df['expected_home_advantage'] = 0.5  # Placeholder
        df['competitive_balance'] = 0.5  # Placeholder
        
        return df

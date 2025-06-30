"""
Performance metrics calculation for soccer analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging

from ..utils.config import Config
from ..utils.helpers import safe_divide, calculate_percentage


class PerformanceMetrics:
    """Calculates various performance metrics for soccer analysis."""
    
    def __init__(self):
        """Initialize the performance metrics calculator."""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
    
    def calculate_player_metrics(self, player_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate comprehensive performance metrics for players.
        
        Args:
            player_data: Player statistics DataFrame
            
        Returns:
            DataFrame with calculated metrics
        """
        self.logger.info("Calculating player performance metrics")
        
        df = player_data.copy()
        
        # Basic efficiency metrics
        df['goals_per_game'] = safe_divide(df['goals_total'], df['games_appearances'])
        df['assists_per_game'] = safe_divide(df['goals_assists'], df['games_appearances'])
        df['minutes_per_game'] = safe_divide(df['games_minutes'], df['games_appearances'])
        
        # Advanced metrics
        df['goal_contributions'] = df['goals_total'] + df['goals_assists']
        df['goal_contributions_per_game'] = safe_divide(df['goal_contributions'], df['games_appearances'])
        
        # Defensive metrics
        if 'tackles_total' in df.columns and 'tackles_won' in df.columns:
            df['tackle_success_rate'] = calculate_percentage(df['tackles_won'], df['tackles_total'])
        
        # Passing metrics
        if 'passes_total' in df.columns and 'passes_accuracy' in df.columns:
            df['passes_completed'] = (df['passes_total'] * df['passes_accuracy'] / 100).round()
            df['passes_per_game'] = safe_divide(df['passes_total'], df['games_appearances'])
        
        # Performance rating
        df['performance_score'] = self._calculate_performance_score(df)
        
        return df
    
    def calculate_team_metrics(self, team_data: pd.DataFrame, match_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate team performance metrics.
        
        Args:
            team_data: Team data DataFrame
            match_data: Match data DataFrame
            
        Returns:
            DataFrame with team metrics
        """
        self.logger.info("Calculating team performance metrics")
        
        df = team_data.copy()
        
        # Basic metrics from existing data
        if 'total_matches' in df.columns:
            df['points_per_game'] = safe_divide(df['points'], df['total_matches'])
            df['goals_per_game'] = safe_divide(df['goals_scored'], df['total_matches'])
            df['goals_conceded_per_game'] = safe_divide(df['goals_conceded'], df['total_matches'])
        
        # Advanced team metrics
        df['goal_difference_per_game'] = df['goals_per_game'] - df['goals_conceded_per_game']
        df['clean_sheet_percentage'] = calculate_percentage(df.get('clean_sheets', 0), df.get('total_matches', 1))
        
        # Form and consistency metrics
        df['form_rating'] = self._calculate_team_form(df)
        df['consistency_score'] = self._calculate_team_consistency(df)
        
        return df
    
    def _calculate_performance_score(self, player_df: pd.DataFrame) -> pd.Series:
        """Calculate overall performance score for players."""
        # Normalize key metrics
        goals_norm = self._normalize_series(player_df['goals_per_game'])
        assists_norm = self._normalize_series(player_df['assists_per_game'])
        rating_norm = self._normalize_series(player_df.get('games_rating', pd.Series([0] * len(player_df))))
        
        # Weighted combination
        performance_score = (
            goals_norm * 0.4 +
            assists_norm * 0.3 +
            rating_norm * 0.3
        ) * 10  # Scale to 0-10
        
        return performance_score.round(2)
    
    def _calculate_team_form(self, team_df: pd.DataFrame) -> pd.Series:
        """Calculate team form rating."""
        # Simple form calculation based on win percentage and recent performance
        win_pct = team_df.get('win_percentage', 0)
        goals_ratio = safe_divide(team_df.get('goals_scored', 0), team_df.get('goals_conceded', 1))
        
        form_rating = (win_pct * 0.6 + np.minimum(goals_ratio * 20, 40) * 0.4) / 10
        return form_rating.round(2)
    
    def _calculate_team_consistency(self, team_df: pd.DataFrame) -> pd.Series:
        """Calculate team consistency score."""
        # Consistency based on goal difference variance and performance stability
        goal_diff = team_df.get('goal_difference', 0)
        matches = team_df.get('total_matches', 1)
        
        # Higher consistency for teams with stable performance
        consistency = np.minimum(100, 50 + goal_diff / matches * 10)
        return np.maximum(0, consistency).round(2)
    
    def _normalize_series(self, series: pd.Series) -> pd.Series:
        """Normalize a series to 0-1 range."""
        if series.std() == 0:
            return pd.Series([0.5] * len(series), index=series.index)
        
        return (series - series.min()) / (series.max() - series.min())
    
    def calculate_match_metrics(self, match_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate match-level performance metrics.
        
        Args:
            match_data: Match data DataFrame
            
        Returns:
            DataFrame with match metrics
        """
        self.logger.info("Calculating match performance metrics")
        
        df = match_data.copy()
        
        # Match intensity metrics
        df['goal_rate'] = df['total_goals'] / 90  # Goals per minute
        df['competitiveness'] = self._calculate_match_competitiveness(df)
        df['entertainment_value'] = self._calculate_entertainment_value(df)
        
        return df
    
    def _calculate_match_competitiveness(self, match_df: pd.DataFrame) -> pd.Series:
        """Calculate match competitiveness score."""
        goal_diff = abs(match_df['goal_difference'])
        total_goals = match_df['total_goals']
        
        # More competitive = smaller goal difference, reasonable number of goals
        competitiveness = (5 - goal_diff) * (1 + total_goals * 0.2)
        return np.maximum(0, np.minimum(10, competitiveness)).round(2)
    
    def _calculate_entertainment_value(self, match_df: pd.DataFrame) -> pd.Series:
        """Calculate entertainment value of matches."""
        total_goals = match_df['total_goals']
        close_match = (abs(match_df['goal_difference']) <= 1).astype(int)
        
        # Higher entertainment for more goals and close matches
        entertainment = total_goals * 2 + close_match * 3
        return np.minimum(10, entertainment).round(2)
    
    def generate_performance_report(self, player_data: pd.DataFrame, 
                                  team_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Args:
            player_data: Player statistics DataFrame
            team_data: Team data DataFrame
            
        Returns:
            Performance report dictionary
        """
        self.logger.info("Generating performance report")
        
        # Calculate metrics
        player_metrics = self.calculate_player_metrics(player_data)
        team_metrics = self.calculate_team_metrics(team_data, pd.DataFrame())
        
        # Top performers
        top_scorers = player_metrics.nlargest(5, 'goals_total')[
            ['player_name', 'team_name', 'goals_total', 'goals_per_game']
        ].to_dict('records')
        
        top_assisters = player_metrics.nlargest(5, 'goals_assists')[
            ['player_name', 'team_name', 'goals_assists', 'assists_per_game']
        ].to_dict('records')
        
        top_performers = player_metrics.nlargest(5, 'performance_score')[
            ['player_name', 'team_name', 'performance_score', 'goal_contributions']
        ].to_dict('records')
        
        # Team rankings
        top_teams = team_metrics.nlargest(5, 'points')[
            ['team_name', 'points', 'win_percentage', 'goal_difference']
        ].to_dict('records')
        
        report = {
            'summary': {
                'total_players': len(player_metrics),
                'total_teams': len(team_metrics),
                'avg_goals_per_player': player_metrics['goals_total'].mean(),
                'avg_team_points': team_metrics.get('points', pd.Series([0])).mean(),
            },
            'top_performers': {
                'scorers': top_scorers,
                'assisters': top_assisters,
                'overall': top_performers
            },
            'team_rankings': {
                'by_points': top_teams
            },
            'league_stats': {
                'highest_scorer': player_metrics.loc[player_metrics['goals_total'].idxmax(), 'player_name'] if not player_metrics.empty else 'N/A',
                'most_assists': player_metrics.loc[player_metrics['goals_assists'].idxmax(), 'player_name'] if not player_metrics.empty else 'N/A',
                'best_team': team_metrics.loc[team_metrics.get('points', pd.Series([0])).idxmax(), 'team_name'] if not team_metrics.empty else 'N/A'
            },
            'generated_at': pd.Timestamp.now().isoformat()
        }
        
        return report

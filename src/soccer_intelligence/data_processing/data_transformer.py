"""
Data transformation module for preparing soccer data for analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder

from ..utils.config import Config
from ..utils.helpers import safe_divide


class DataTransformer:
    """Transforms and prepares soccer data for analysis and modeling."""
    
    def __init__(self):
        """Initialize the data transformer."""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize scalers
        self.standard_scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
        self.label_encoders = {}
    
    def prepare_for_analysis(self, player_df: pd.DataFrame, team_df: pd.DataFrame, 
                           match_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Prepare all datasets for analysis.
        
        Args:
            player_df: Player data DataFrame
            team_df: Team data DataFrame
            match_df: Match data DataFrame
            
        Returns:
            Dictionary of prepared datasets
        """
        self.logger.info("Preparing datasets for analysis")
        
        prepared_data = {}
        
        # Transform player data
        if not player_df.empty:
            prepared_data['players'] = self.transform_player_data(player_df)
        
        # Transform team data
        if not team_df.empty:
            prepared_data['teams'] = self.transform_team_data(team_df)
        
        # Transform match data
        if not match_df.empty:
            prepared_data['matches'] = self.transform_match_data(match_df)
        
        # Create aggregated datasets
        if 'players' in prepared_data and 'teams' in prepared_data:
            prepared_data['team_player_summary'] = self.create_team_player_summary(
                prepared_data['players'], prepared_data['teams']
            )
        
        self.logger.info("Data preparation completed")
        return prepared_data
    
    def transform_player_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform player data for analysis."""
        self.logger.info("Transforming player data")
        
        transformed_df = df.copy()
        
        # Handle missing values
        transformed_df = self._handle_missing_values(transformed_df, 'player')
        
        # Normalize performance metrics
        performance_columns = [
            'goals_total', 'goals_assists', 'games_minutes', 'passes_total',
            'tackles_total', 'duels_total', 'games_rating'
        ]
        
        for col in performance_columns:
            if col in transformed_df.columns:
                transformed_df[f'{col}_normalized'] = self._normalize_column(transformed_df[col])
        
        # Create performance categories
        transformed_df = self._create_performance_categories(transformed_df)
        
        # Encode categorical variables
        categorical_columns = ['games_position', 'nationality', 'age_category']
        transformed_df = self._encode_categorical_variables(transformed_df, categorical_columns)
        
        return transformed_df
    
    def transform_team_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform team data for analysis."""
        self.logger.info("Transforming team data")
        
        transformed_df = df.copy()
        
        # Handle missing values
        transformed_df = self._handle_missing_values(transformed_df, 'team')
        
        # Normalize team performance metrics
        performance_columns = [
            'total_matches', 'wins', 'goals_scored', 'goals_conceded',
            'win_percentage', 'goals_per_game'
        ]
        
        for col in performance_columns:
            if col in transformed_df.columns:
                transformed_df[f'{col}_normalized'] = self._normalize_column(transformed_df[col])
        
        # Create team strength categories
        if 'win_percentage' in transformed_df.columns:
            transformed_df['team_strength'] = pd.cut(
                transformed_df['win_percentage'],
                bins=[0, 30, 50, 70, 100],
                labels=['Weak', 'Average', 'Strong', 'Elite'],
                include_lowest=True
            )
        
        return transformed_df
    
    def transform_match_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform match data for analysis."""
        self.logger.info("Transforming match data")
        
        transformed_df = df.copy()
        
        # Handle missing values
        transformed_df = self._handle_missing_values(transformed_df, 'match')
        
        # Create match outcome features
        if 'home_goals' in transformed_df.columns and 'away_goals' in transformed_df.columns:
            transformed_df['match_competitiveness'] = self._calculate_match_competitiveness(
                transformed_df['home_goals'], transformed_df['away_goals']
            )
        
        # Encode categorical variables
        categorical_columns = ['status', 'result', 'day_of_week']
        transformed_df = self._encode_categorical_variables(transformed_df, categorical_columns)
        
        return transformed_df
    
    def _handle_missing_values(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Handle missing values based on data type."""
        strategy = self.config.get('data_processing.feature_engineering.handle_missing_values', 'interpolate')
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if strategy == 'interpolate':
            for col in numeric_columns:
                df[col] = df[col].interpolate()
        elif strategy == 'mean':
            for col in numeric_columns:
                df[col] = df[col].fillna(df[col].mean())
        elif strategy == 'median':
            for col in numeric_columns:
                df[col] = df[col].fillna(df[col].median())
        else:  # forward fill
            df[numeric_columns] = df[numeric_columns].fillna(method='ffill')
        
        # Fill remaining NaN values with 0
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        # Fill categorical NaN values
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            df[col] = df[col].fillna('Unknown')
        
        return df
    
    def _normalize_column(self, series: pd.Series) -> pd.Series:
        """Normalize a column using MinMax scaling."""
        if series.std() == 0:  # No variance
            return pd.Series(np.zeros(len(series)), index=series.index)
        
        normalized = (series - series.min()) / (series.max() - series.min())
        return normalized.fillna(0)
    
    def _create_performance_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create performance categories for players."""
        # Goals per game categories
        if 'goals_per_game' in df.columns:
            df['goal_scorer_type'] = pd.cut(
                df['goals_per_game'],
                bins=[0, 0.1, 0.3, 0.5, 1.0, float('inf')],
                labels=['Non-scorer', 'Occasional', 'Regular', 'Prolific', 'Elite'],
                include_lowest=True
            )
        
        # Overall performance rating
        performance_cols = ['goals_total_normalized', 'goals_assists_normalized', 'games_rating_normalized']
        available_cols = [col for col in performance_cols if col in df.columns]
        
        if available_cols:
            df['overall_performance_score'] = df[available_cols].mean(axis=1)
            df['performance_tier'] = pd.cut(
                df['overall_performance_score'],
                bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                labels=['Poor', 'Below Average', 'Average', 'Good', 'Excellent'],
                include_lowest=True
            )
        
        return df
    
    def _encode_categorical_variables(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Encode categorical variables."""
        for col in columns:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                
                # Handle NaN values
                df[col] = df[col].fillna('Unknown')
                
                # Fit and transform
                try:
                    df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col])
                except Exception as e:
                    self.logger.warning(f"Error encoding {col}: {e}")
                    df[f'{col}_encoded'] = 0
        
        return df
    
    def _calculate_match_competitiveness(self, home_goals: pd.Series, away_goals: pd.Series) -> pd.Series:
        """Calculate match competitiveness score."""
        goal_difference = abs(home_goals - away_goals)
        total_goals = home_goals + away_goals
        
        # Competitiveness decreases with goal difference, increases with total goals
        competitiveness = (total_goals + 1) / (goal_difference + 1)
        
        # Normalize to 0-1 scale
        return (competitiveness - competitiveness.min()) / (competitiveness.max() - competitiveness.min())
    
    def create_team_player_summary(self, player_df: pd.DataFrame, team_df: pd.DataFrame) -> pd.DataFrame:
        """Create team-level summary from player data."""
        self.logger.info("Creating team-player summary")
        
        # Group players by team
        team_summary = player_df.groupby('team_id').agg({
            'player_id': 'count',
            'goals_total': ['sum', 'mean'],
            'goals_assists': ['sum', 'mean'],
            'games_minutes': ['sum', 'mean'],
            'games_rating': 'mean',
            'age': 'mean'
        }).round(2)
        
        # Flatten column names
        team_summary.columns = ['_'.join(col).strip() for col in team_summary.columns]
        team_summary = team_summary.reset_index()
        
        # Rename columns for clarity
        column_mapping = {
            'player_id_count': 'total_players',
            'goals_total_sum': 'team_total_goals',
            'goals_total_mean': 'avg_goals_per_player',
            'goals_assists_sum': 'team_total_assists',
            'goals_assists_mean': 'avg_assists_per_player',
            'games_minutes_sum': 'team_total_minutes',
            'games_minutes_mean': 'avg_minutes_per_player',
            'games_rating_mean': 'avg_team_rating',
            'age_mean': 'avg_team_age'
        }
        
        team_summary = team_summary.rename(columns=column_mapping)
        
        # Merge with team data
        if not team_df.empty:
            team_summary = team_summary.merge(
                team_df[['team_id', 'team_name', 'team_country', 'wins', 'total_matches']],
                on='team_id',
                how='left'
            )
        
        return team_summary
    
    def prepare_for_modeling(self, df: pd.DataFrame, target_column: str, 
                           feature_columns: Optional[List[str]] = None) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare data for machine learning modeling.
        
        Args:
            df: Input DataFrame
            target_column: Target variable column name
            feature_columns: List of feature columns to use
            
        Returns:
            Tuple of (features DataFrame, target Series)
        """
        self.logger.info("Preparing data for modeling")
        
        # Select features
        if feature_columns is None:
            # Use all numeric columns except target
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            feature_columns = [col for col in numeric_columns if col != target_column]
        
        # Filter available columns
        available_features = [col for col in feature_columns if col in df.columns]
        
        if not available_features:
            raise ValueError("No valid feature columns found")
        
        # Prepare features and target
        X = df[available_features].copy()
        y = df[target_column].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        y = y.fillna(y.mean())
        
        # Scale features
        if self.config.get('data_processing.feature_engineering.normalize_features', True):
            X_scaled = pd.DataFrame(
                self.standard_scaler.fit_transform(X),
                columns=X.columns,
                index=X.index
            )
            return X_scaled, y
        
        return X, y

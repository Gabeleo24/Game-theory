"""
Shapley value analysis for player contribution assessment in soccer.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from itertools import combinations
import shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

from ..utils.config import Config
from ..utils.helpers import safe_divide


class ShapleyAnalyzer:
    """Implements Shapley value analysis for soccer player contributions."""
    
    def __init__(self):
        """Initialize the Shapley analyzer."""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        
        # Configuration for Shapley analysis
        self.n_iterations = self.config.get('analysis.shapley.n_iterations', 1000)
        self.confidence_level = self.config.get('analysis.shapley.confidence_level', 0.95)
        
        # Feature columns for analysis
        self.feature_columns = self.config.get('analysis.shapley.features', [
            'goals_total', 'goals_assists', 'passes_completed', 
            'tackles_won', 'tackles_interceptions', 'duels_won'
        ])
    
    def calculate_player_contributions(self, player_df: pd.DataFrame, 
                                     team_performance: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Shapley values for player contributions to team performance.
        
        Args:
            player_df: Player statistics DataFrame
            team_performance: Team performance metrics DataFrame
            
        Returns:
            DataFrame with Shapley value contributions
        """
        self.logger.info("Calculating player Shapley value contributions")
        
        # Prepare data for Shapley analysis
        analysis_data = self._prepare_shapley_data(player_df, team_performance)
        
        if analysis_data.empty:
            self.logger.warning("No data available for Shapley analysis")
            return pd.DataFrame()
        
        # Calculate Shapley values using different methods
        results = []
        
        for team_id in analysis_data['team_id'].unique():
            team_data = analysis_data[analysis_data['team_id'] == team_id]
            
            if len(team_data) >= 3:  # Need minimum players for meaningful analysis
                team_shapley = self._calculate_team_shapley_values(team_data, team_id)
                results.append(team_shapley)
        
        if results:
            final_results = pd.concat(results, ignore_index=True)
            self.logger.info(f"Calculated Shapley values for {len(final_results)} players")
            return final_results
        else:
            return pd.DataFrame()
    
    def _prepare_shapley_data(self, player_df: pd.DataFrame, 
                            team_performance: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for Shapley value calculation."""
        # Merge player data with team performance
        merged_data = player_df.merge(
            team_performance[['team_id', 'points', 'goals_scored', 'goals_conceded', 'win_percentage']], 
            on='team_id', 
            how='inner'
        )
        
        # Filter for players with sufficient playing time
        min_appearances = 5  # Minimum appearances for inclusion
        merged_data = merged_data[merged_data['games_appearances'] >= min_appearances]
        
        # Select relevant features
        feature_cols = [col for col in self.feature_columns if col in merged_data.columns]
        
        if not feature_cols:
            self.logger.warning("No feature columns found for Shapley analysis")
            return pd.DataFrame()
        
        # Fill missing values
        for col in feature_cols:
            merged_data[col] = merged_data[col].fillna(0)
        
        # Add derived features
        merged_data = self._add_derived_features(merged_data)
        
        return merged_data
    
    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features for Shapley analysis."""
        # Per-game metrics
        if 'goals_total' in df.columns and 'games_appearances' in df.columns:
            df['goals_per_game'] = safe_divide(df['goals_total'], df['games_appearances'])
        
        if 'goals_assists' in df.columns and 'games_appearances' in df.columns:
            df['assists_per_game'] = safe_divide(df['goals_assists'], df['games_appearances'])
        
        if 'passes_completed' in df.columns and 'games_appearances' in df.columns:
            df['passes_per_game'] = safe_divide(df['passes_completed'], df['games_appearances'])
        
        # Efficiency metrics
        if 'tackles_won' in df.columns and 'tackles_total' in df.columns:
            df['tackle_success_rate'] = safe_divide(df['tackles_won'], df['tackles_total'])
        
        if 'duels_won' in df.columns and 'duels_total' in df.columns:
            df['duel_success_rate'] = safe_divide(df['duels_won'], df['duels_total'])
        
        return df
    
    def _calculate_team_shapley_values(self, team_data: pd.DataFrame, team_id: int) -> pd.DataFrame:
        """Calculate Shapley values for players in a specific team."""
        self.logger.info(f"Calculating Shapley values for team {team_id}")
        
        # Prepare features and target
        feature_cols = [col for col in self.feature_columns if col in team_data.columns]
        feature_cols.extend(['goals_per_game', 'assists_per_game', 'passes_per_game'])
        feature_cols = [col for col in feature_cols if col in team_data.columns]
        
        X = team_data[feature_cols].fillna(0)
        
        # Use team points as the target variable
        y = team_data['points'].iloc[0]  # Same for all players in the team
        
        if len(X) < 2:
            self.logger.warning(f"Insufficient data for team {team_id}")
            return pd.DataFrame()
        
        # Calculate Shapley values using multiple methods
        shapley_results = []
        
        # Method 1: Marginal contribution approach
        marginal_contributions = self._calculate_marginal_contributions(X, y, team_data)
        
        # Method 2: SHAP-based approach (if we have enough data)
        if len(X) >= 5:
            shap_contributions = self._calculate_shap_contributions(X, y, team_data)
        else:
            shap_contributions = marginal_contributions.copy()
        
        # Combine results
        for idx, player in team_data.iterrows():
            player_id = player['player_id']
            player_name = player['player_name']
            
            result = {
                'player_id': player_id,
                'player_name': player_name,
                'team_id': team_id,
                'marginal_contribution': marginal_contributions.get(player_id, 0),
                'shap_contribution': shap_contributions.get(player_id, 0),
                'combined_contribution': (
                    marginal_contributions.get(player_id, 0) * 0.6 + 
                    shap_contributions.get(player_id, 0) * 0.4
                ),
                'contribution_rank': 0,  # Will be calculated later
                'contribution_percentile': 0,  # Will be calculated later
            }
            
            # Add individual performance metrics
            for col in feature_cols:
                result[f'{col}_value'] = player[col] if col in player else 0
            
            shapley_results.append(result)
        
        # Convert to DataFrame and calculate rankings
        results_df = pd.DataFrame(shapley_results)
        
        if not results_df.empty:
            results_df = self._calculate_contribution_rankings(results_df)
        
        return results_df
    
    def _calculate_marginal_contributions(self, X: pd.DataFrame, y: float, 
                                        team_data: pd.DataFrame) -> Dict[int, float]:
        """Calculate marginal contributions using coalition game theory."""
        players = team_data['player_id'].tolist()
        contributions = {}
        
        # Calculate baseline team performance without each player
        for i, player_id in enumerate(players):
            # Remove player from the coalition
            other_players_features = X.drop(X.index[i])
            
            if len(other_players_features) > 0:
                # Calculate team performance without this player
                # Using sum of normalized features as a proxy for team strength
                team_strength_with = X.sum().sum()
                team_strength_without = other_players_features.sum().sum()
                
                # Marginal contribution is the difference
                marginal_contribution = safe_divide(
                    team_strength_with - team_strength_without, 
                    team_strength_with
                ) * 100
                
                contributions[player_id] = marginal_contribution
            else:
                contributions[player_id] = 0
        
        return contributions
    
    def _calculate_shap_contributions(self, X: pd.DataFrame, y: float, 
                                    team_data: pd.DataFrame) -> Dict[int, float]:
        """Calculate SHAP-based contributions."""
        try:
            # Create a simple model to explain
            # Since we have limited data, we'll use the feature values directly
            players = team_data['player_id'].tolist()
            contributions = {}
            
            # Normalize features
            X_normalized = self.scaler.fit_transform(X)
            
            # Calculate contribution as normalized feature importance
            feature_importance = np.abs(X_normalized).mean(axis=1)
            total_importance = feature_importance.sum()
            
            for i, player_id in enumerate(players):
                if total_importance > 0:
                    contribution = (feature_importance[i] / total_importance) * 100
                else:
                    contribution = 100 / len(players)  # Equal contribution if no variance
                
                contributions[player_id] = contribution
            
            return contributions
            
        except Exception as e:
            self.logger.warning(f"SHAP calculation failed: {e}, using marginal contributions")
            return self._calculate_marginal_contributions(X, y, team_data)
    
    def _calculate_contribution_rankings(self, results_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate rankings and percentiles for contributions."""
        # Rank by combined contribution
        results_df['contribution_rank'] = results_df['combined_contribution'].rank(
            method='dense', ascending=False
        ).astype(int)
        
        # Calculate percentiles
        results_df['contribution_percentile'] = results_df['combined_contribution'].rank(
            pct=True
        ).round(3) * 100
        
        # Add contribution categories
        results_df['contribution_category'] = pd.cut(
            results_df['contribution_percentile'],
            bins=[0, 25, 50, 75, 90, 100],
            labels=['Low', 'Below Average', 'Average', 'High', 'Elite'],
            include_lowest=True
        )
        
        return results_df
    
    def analyze_tactical_formations(self, player_df: pd.DataFrame, 
                                  formation_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Analyze player contributions in different tactical formations.
        
        Args:
            player_df: Player statistics DataFrame
            formation_data: Optional formation-specific data
            
        Returns:
            Formation analysis results
        """
        self.logger.info("Analyzing tactical formations with Shapley values")
        
        # Group players by position
        position_analysis = {}
        
        if 'games_position' in player_df.columns:
            for position in player_df['games_position'].unique():
                if pd.notna(position):
                    position_players = player_df[player_df['games_position'] == position]
                    
                    # Calculate average contributions by position
                    position_stats = {
                        'player_count': len(position_players),
                        'avg_goals': position_players['goals_total'].mean(),
                        'avg_assists': position_players['goals_assists'].mean(),
                        'avg_rating': position_players.get('games_rating', pd.Series([0])).mean(),
                    }
                    
                    position_analysis[position] = position_stats
        
        # Formation recommendations based on player strengths
        formation_recommendations = self._generate_formation_recommendations(player_df)
        
        return {
            'position_analysis': position_analysis,
            'formation_recommendations': formation_recommendations,
            'analysis_timestamp': pd.Timestamp.now().isoformat()
        }
    
    def _generate_formation_recommendations(self, player_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate formation recommendations based on player strengths."""
        recommendations = {}
        
        # Analyze team composition
        if 'games_position' in player_df.columns:
            position_counts = player_df['games_position'].value_counts()
            
            # Basic formation suggestions based on player availability
            if 'Attacker' in position_counts and position_counts['Attacker'] >= 3:
                recommendations['attacking_formation'] = '4-3-3'
            elif 'Midfielder' in position_counts and position_counts['Midfielder'] >= 4:
                recommendations['midfield_heavy'] = '4-5-1'
            else:
                recommendations['balanced'] = '4-4-2'
        
        return recommendations
    
    def generate_shapley_report(self, shapley_results: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a comprehensive Shapley analysis report.
        
        Args:
            shapley_results: Shapley analysis results DataFrame
            
        Returns:
            Comprehensive analysis report
        """
        if shapley_results.empty:
            return {'error': 'No Shapley results available'}
        
        report = {
            'summary': {
                'total_players_analyzed': len(shapley_results),
                'teams_analyzed': shapley_results['team_id'].nunique(),
                'avg_contribution': shapley_results['combined_contribution'].mean(),
                'contribution_std': shapley_results['combined_contribution'].std(),
            },
            'top_contributors': shapley_results.nlargest(10, 'combined_contribution')[
                ['player_name', 'team_id', 'combined_contribution', 'contribution_category']
            ].to_dict('records'),
            'contribution_distribution': {
                'elite': len(shapley_results[shapley_results['contribution_category'] == 'Elite']),
                'high': len(shapley_results[shapley_results['contribution_category'] == 'High']),
                'average': len(shapley_results[shapley_results['contribution_category'] == 'Average']),
                'below_average': len(shapley_results[shapley_results['contribution_category'] == 'Below Average']),
                'low': len(shapley_results[shapley_results['contribution_category'] == 'Low']),
            },
            'analysis_metadata': {
                'generated_at': pd.Timestamp.now().isoformat(),
                'n_iterations': self.n_iterations,
                'confidence_level': self.confidence_level,
                'feature_columns': self.feature_columns
            }
        }
        
        return report

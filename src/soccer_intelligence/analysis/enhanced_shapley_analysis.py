"""
Enhanced Shapley Value Analysis with FBref Metrics

Leverages detailed FBref statistics to provide more comprehensive
player contribution analysis using Shapley values.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from itertools import combinations
import shap
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

from ..utils.logger import get_logger
from ..data_processing.data_integrator import DataIntegrator


class EnhancedShapleyAnalyzer:
    """
    Enhanced Shapley value analysis using comprehensive FBref metrics
    """
    
    def __init__(self, cache_dir: str = "data/processed/shapley_enhanced"):
        """
        Initialize the enhanced Shapley analyzer
        
        Args:
            cache_dir: Directory to store analysis results
        """
        self.cache_dir = cache_dir
        self.logger = get_logger(__name__)
        self.scaler = StandardScaler()
        
        # Initialize data integrator
        self.data_integrator = DataIntegrator()
        
        # Enhanced feature sets using FBref metrics
        self.feature_sets = {
            'attacking': [
                'Gls_numeric', 'Ast_numeric', 'xG_numeric', 'xAG_numeric',
                'goal_contribution', 'expected_contribution'
            ],
            'defensive': [
                'Tkl', 'Int', 'Blocks', 'Clr', 'Err'  # FBref defensive stats
            ],
            'passing': [
                'Cmp', 'Att', 'Cmp%', 'TotDist', 'PrgDist'  # FBref passing stats
            ],
            'possession': [
                'Touches', 'Succ', 'Att', 'Succ%'  # FBref possession stats
            ],
            'advanced': [
                'xG_numeric', 'xAG_numeric', 'npxG', 'npxG+xAG'  # Advanced metrics
            ]
        }
        
        # Target variables for different analysis types
        self.target_variables = {
            'team_success': ['Pts', 'GD', 'xGD'],  # Team performance metrics
            'attacking_output': ['GF', 'xG'],      # Team attacking metrics
            'defensive_solidity': ['GA', 'xGA']    # Team defensive metrics
        }
    
    def analyze_player_contributions(self, league: str, season: int = 2024, 
                                   analysis_type: str = 'team_success') -> Dict[str, Any]:
        """
        Analyze player contributions using enhanced Shapley values
        
        Args:
            league: League name
            season: Season year
            analysis_type: Type of analysis ('team_success', 'attacking_output', 'defensive_solidity')
            
        Returns:
            Dictionary containing Shapley analysis results
        """
        self.logger.info(f"Analyzing player contributions for {league} {season}")
        
        # Get integrated data
        integrated_data = self.data_integrator.get_integrated_data(league, season)
        if not integrated_data:
            raise ValueError(f"No integrated data available for {league} {season}")
        
        if 'players' not in integrated_data or 'teams' not in integrated_data:
            raise ValueError("Missing player or team data for analysis")
        
        players_df = integrated_data['players']
        teams_df = integrated_data['teams']
        
        # Prepare data for analysis
        analysis_data = self._prepare_analysis_data(players_df, teams_df, analysis_type)
        
        # Perform Shapley analysis
        shapley_results = self._calculate_enhanced_shapley_values(analysis_data, analysis_type)
        
        # Add interpretation and insights
        shapley_results['interpretation'] = self._interpret_shapley_results(shapley_results, league)
        
        return shapley_results
    
    def _prepare_analysis_data(self, players_df: pd.DataFrame, teams_df: pd.DataFrame, 
                             analysis_type: str) -> Dict[str, pd.DataFrame]:
        """
        Prepare data for Shapley analysis
        """
        # Aggregate player stats by team
        team_player_stats = self._aggregate_team_player_stats(players_df)
        
        # Merge with team performance data
        analysis_df = teams_df.merge(team_player_stats, left_on='Squad', right_on='Squad', how='inner')
        
        # Select features and targets based on analysis type
        feature_columns = self._select_features_for_analysis(analysis_df, analysis_type)
        target_columns = self.target_variables.get(analysis_type, ['Pts'])
        
        # Clean and prepare data
        analysis_df = self._clean_analysis_data(analysis_df, feature_columns + target_columns)
        
        return {
            'full_data': analysis_df,
            'features': analysis_df[feature_columns],
            'targets': analysis_df[target_columns],
            'feature_names': feature_columns,
            'target_names': target_columns
        }
    
    def _aggregate_team_player_stats(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate individual player stats to team level
        """
        # Convert numeric columns
        numeric_columns = []
        for col in players_df.columns:
            if col.endswith('_numeric') or col in ['Gls', 'Ast', 'MP', 'Min']:
                try:
                    players_df[col] = pd.to_numeric(players_df[col], errors='coerce')
                    numeric_columns.append(col)
                except:
                    continue
        
        # Aggregate by team
        team_stats = players_df.groupby('Squad').agg({
            **{col: 'sum' for col in numeric_columns if col in players_df.columns},
            'Player': 'count'  # Number of players
        }).reset_index()
        
        # Rename player count column
        team_stats.rename(columns={'Player': 'total_players'}, inplace=True)
        
        # Calculate team-level derived metrics
        if 'Gls_numeric' in team_stats.columns and 'Ast_numeric' in team_stats.columns:
            team_stats['team_goal_contribution'] = team_stats['Gls_numeric'] + team_stats['Ast_numeric']
        
        if 'xG_numeric' in team_stats.columns and 'xAG_numeric' in team_stats.columns:
            team_stats['team_expected_contribution'] = team_stats['xG_numeric'] + team_stats['xAG_numeric']
        
        return team_stats
    
    def _select_features_for_analysis(self, df: pd.DataFrame, analysis_type: str) -> List[str]:
        """
        Select appropriate features based on analysis type
        """
        available_features = []
        
        if analysis_type == 'team_success':
            # Use all available feature sets for overall team success
            for feature_set in self.feature_sets.values():
                available_features.extend([f for f in feature_set if f in df.columns])
        
        elif analysis_type == 'attacking_output':
            # Focus on attacking features
            for feature_set in ['attacking', 'passing', 'advanced']:
                if feature_set in self.feature_sets:
                    available_features.extend([f for f in self.feature_sets[feature_set] if f in df.columns])
        
        elif analysis_type == 'defensive_solidity':
            # Focus on defensive features
            for feature_set in ['defensive', 'possession']:
                if feature_set in self.feature_sets:
                    available_features.extend([f for f in self.feature_sets[feature_set] if f in df.columns])
        
        # Remove duplicates and ensure we have features
        available_features = list(set(available_features))
        
        # Add basic team stats if available
        basic_stats = ['team_goal_contribution', 'team_expected_contribution', 'total_players']
        available_features.extend([f for f in basic_stats if f in df.columns])
        
        return available_features
    
    def _clean_analysis_data(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Clean and prepare data for analysis
        """
        # Select only available columns
        available_columns = [col for col in columns if col in df.columns]
        clean_df = df[available_columns].copy()
        
        # Handle missing values
        clean_df = clean_df.fillna(0)
        
        # Remove any infinite values
        clean_df = clean_df.replace([np.inf, -np.inf], 0)
        
        return clean_df
    
    def _calculate_enhanced_shapley_values(self, analysis_data: Dict, analysis_type: str) -> Dict[str, Any]:
        """
        Calculate Shapley values using enhanced FBref metrics
        """
        features = analysis_data['features']
        targets = analysis_data['targets']
        
        if features.empty or targets.empty:
            raise ValueError("Insufficient data for Shapley analysis")
        
        results = {}
        
        # For each target variable
        for target_col in analysis_data['target_names']:
            if target_col not in targets.columns:
                continue
                
            target = targets[target_col]
            
            # Split data for validation
            X_train, X_test, y_train, y_test = train_test_split(
                features, target, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Validate model
            y_pred = model.predict(X_test_scaled)
            r2 = r2_score(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            
            # Calculate SHAP values
            explainer = shap.Explainer(model, X_train_scaled)
            shap_values = explainer(X_train_scaled)
            
            # Store results
            results[target_col] = {
                'model_performance': {
                    'r2_score': r2,
                    'mse': mse,
                    'feature_importance': dict(zip(features.columns, model.feature_importances_))
                },
                'shapley_values': {
                    'values': shap_values.values,
                    'base_value': shap_values.base_values,
                    'data': shap_values.data,
                    'feature_names': list(features.columns)
                },
                'feature_contributions': self._calculate_feature_contributions(shap_values, features.columns),
                'top_contributors': self._identify_top_contributors(shap_values, features.columns)
            }
        
        # Add overall analysis summary
        results['summary'] = {
            'analysis_type': analysis_type,
            'total_features': len(features.columns),
            'total_teams': len(features),
            'feature_categories': self._categorize_features(features.columns)
        }
        
        return results
    
    def _calculate_feature_contributions(self, shap_values, feature_names: List[str]) -> Dict[str, float]:
        """
        Calculate average absolute contribution for each feature
        """
        contributions = {}
        for i, feature in enumerate(feature_names):
            contributions[feature] = np.mean(np.abs(shap_values.values[:, i]))
        
        return dict(sorted(contributions.items(), key=lambda x: x[1], reverse=True))
    
    def _identify_top_contributors(self, shap_values, feature_names: List[str], top_n: int = 5) -> List[Dict]:
        """
        Identify top contributing features
        """
        contributions = self._calculate_feature_contributions(shap_values, feature_names)
        
        top_contributors = []
        for i, (feature, contribution) in enumerate(list(contributions.items())[:top_n]):
            top_contributors.append({
                'rank': i + 1,
                'feature': feature,
                'contribution': contribution,
                'category': self._get_feature_category(feature)
            })
        
        return top_contributors
    
    def _categorize_features(self, feature_names: List[str]) -> Dict[str, List[str]]:
        """
        Categorize features by type
        """
        categories = {}
        for category, features in self.feature_sets.items():
            category_features = [f for f in feature_names if f in features]
            if category_features:
                categories[category] = category_features
        
        # Add uncategorized features
        categorized = set()
        for features in categories.values():
            categorized.update(features)
        
        uncategorized = [f for f in feature_names if f not in categorized]
        if uncategorized:
            categories['other'] = uncategorized
        
        return categories
    
    def _get_feature_category(self, feature: str) -> str:
        """
        Get category for a specific feature
        """
        for category, features in self.feature_sets.items():
            if feature in features:
                return category
        return 'other'
    
    def _interpret_shapley_results(self, results: Dict, league: str) -> Dict[str, Any]:
        """
        Provide interpretation and insights from Shapley analysis
        """
        interpretation = {
            'league': league,
            'key_insights': [],
            'tactical_implications': [],
            'player_value_insights': []
        }
        
        # Analyze results for each target
        for target, result in results.items():
            if target == 'summary':
                continue
                
            top_contributors = result.get('top_contributors', [])
            
            if top_contributors:
                top_feature = top_contributors[0]
                interpretation['key_insights'].append(
                    f"For {target}, {top_feature['feature']} ({top_feature['category']}) "
                    f"is the most important factor with contribution score {top_feature['contribution']:.3f}"
                )
                
                # Tactical implications
                if top_feature['category'] == 'attacking':
                    interpretation['tactical_implications'].append(
                        f"Attacking metrics are crucial for {target} - focus on goal-scoring and creativity"
                    )
                elif top_feature['category'] == 'defensive':
                    interpretation['tactical_implications'].append(
                        f"Defensive solidity drives {target} - prioritize defensive organization"
                    )
                elif top_feature['category'] == 'advanced':
                    interpretation['tactical_implications'].append(
                        f"Advanced metrics (xG/xA) are key for {target} - quality over quantity in chances"
                    )
        
        # Player value insights
        interpretation['player_value_insights'].append(
            "Players contributing to top Shapley features provide highest value to team success"
        )
        interpretation['player_value_insights'].append(
            "Expected metrics (xG, xA) help identify players creating quality chances vs lucky finishes"
        )
        
        return interpretation

    def save_analysis_results(self, results: Dict, league: str, season: int, analysis_type: str):
        """
        Save Shapley analysis results
        """
        try:
            import json
            from pathlib import Path

            output_dir = Path(self.cache_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Convert numpy arrays to lists for JSON serialization
            serializable_results = self._make_serializable(results)

            filename = f"{league.lower().replace(' ', '_')}_shapley_{analysis_type}_{season}.json"
            with open(output_dir / filename, 'w') as f:
                json.dump(serializable_results, f, indent=2)

            self.logger.info(f"Shapley analysis results saved to {filename}")

        except Exception as e:
            self.logger.error(f"Error saving analysis results: {e}")

    def _make_serializable(self, obj):
        """
        Convert numpy arrays and other non-serializable objects to JSON-compatible format
        """
        if isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        else:
            return obj

#!/usr/bin/env python3
"""
Core Algorithms for Dynamic Sports Performance Analytics Engine
Custom algorithms for performance scoring, player similarity, and predictive analytics
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

@dataclass
class PerformanceWeights:
    """Position-specific weights for performance calculation."""
    position: str
    weights: Dict[str, float]
    normalization_factors: Dict[str, Tuple[float, float]]  # (min, max) for each stat

class PerformanceScoreAlgorithm:
    """
    Custom weighted performance scoring algorithm with position-specific normalization.
    Implements domain expertise for fair cross-position comparisons.
    """
    
    def __init__(self):
        self.position_weights = self._initialize_position_weights()
        self.scaler = MinMaxScaler()
        self.is_fitted = False
    
    def _initialize_position_weights(self) -> Dict[str, PerformanceWeights]:
        """Initialize position-specific weights based on domain expertise."""
        return {
            'Goalkeeper': PerformanceWeights(
                position='Goalkeeper',
                weights={
                    'saves': 0.25,
                    'clean_sheets': 0.20,
                    'goals_conceded': -0.15,  # Negative weight (lower is better)
                    'pass_accuracy': 0.15,
                    'distribution_accuracy': 0.10,
                    'command_of_area': 0.10,
                    'minutes_played': 0.05
                },
                normalization_factors={
                    'saves': (0, 150),
                    'clean_sheets': (0, 25),
                    'goals_conceded': (0, 80),
                    'pass_accuracy': (50, 100),
                    'distribution_accuracy': (50, 100),
                    'command_of_area': (0, 100),
                    'minutes_played': (0, 3500)
                }
            ),
            'Defender': PerformanceWeights(
                position='Defender',
                weights={
                    'tackles_won': 0.20,
                    'interceptions': 0.15,
                    'clearances': 0.15,
                    'aerial_duels_won': 0.15,
                    'pass_accuracy': 0.10,
                    'goals_conceded_involvement': -0.10,
                    'clean_sheets': 0.10,
                    'minutes_played': 0.05
                },
                normalization_factors={
                    'tackles_won': (0, 100),
                    'interceptions': (0, 80),
                    'clearances': (0, 150),
                    'aerial_duels_won': (0, 100),
                    'pass_accuracy': (70, 100),
                    'goals_conceded_involvement': (0, 20),
                    'clean_sheets': (0, 25),
                    'minutes_played': (0, 3500)
                }
            ),
            'Midfielder': PerformanceWeights(
                position='Midfielder',
                weights={
                    'pass_accuracy': 0.20,
                    'key_passes': 0.15,
                    'assists': 0.15,
                    'tackles_won': 0.10,
                    'goals': 0.10,
                    'distance_covered': 0.10,
                    'possession_retention': 0.10,
                    'minutes_played': 0.05
                },
                normalization_factors={
                    'pass_accuracy': (70, 100),
                    'key_passes': (0, 100),
                    'assists': (0, 20),
                    'tackles_won': (0, 80),
                    'goals': (0, 15),
                    'distance_covered': (200, 400),
                    'possession_retention': (70, 100),
                    'minutes_played': (0, 3500)
                }
            ),
            'Attacker': PerformanceWeights(
                position='Attacker',
                weights={
                    'goals': 0.30,
                    'assists': 0.20,
                    'shots_on_target': 0.15,
                    'key_passes': 0.10,
                    'dribbles_successful': 0.10,
                    'conversion_rate': 0.10,
                    'minutes_played': 0.05
                },
                normalization_factors={
                    'goals': (0, 35),
                    'assists': (0, 20),
                    'shots_on_target': (0, 80),
                    'key_passes': (0, 80),
                    'dribbles_successful': (0, 100),
                    'conversion_rate': (0, 50),
                    'minutes_played': (0, 3500)
                }
            )
        }
    
    def normalize_stat(self, value: float, stat_name: str, position: str) -> float:
        """Normalize a single statistic to 0-1 scale using position-specific ranges."""
        if position not in self.position_weights:
            return 0.5  # Default neutral value
        
        normalization_factors = self.position_weights[position].normalization_factors
        if stat_name not in normalization_factors:
            return 0.5
        
        min_val, max_val = normalization_factors[stat_name]
        
        # Handle negative weights (lower is better)
        weights = self.position_weights[position].weights
        if weights.get(stat_name, 0) < 0:
            # Invert for negative weights
            normalized = 1 - ((value - min_val) / (max_val - min_val))
        else:
            normalized = (value - min_val) / (max_val - min_val)
        
        # Clamp to [0, 1] range
        return max(0, min(1, normalized))
    
    def calculate_performance_score(self, player_stats: Dict[str, float], position: str) -> float:
        """
        Calculate weighted performance score for a player.
        Returns score on 0-100 scale.
        """
        if position not in self.position_weights:
            return 50.0  # Default average score
        
        position_config = self.position_weights[position]
        total_score = 0.0
        total_weight = 0.0
        
        for stat_name, weight in position_config.weights.items():
            if stat_name in player_stats:
                normalized_value = self.normalize_stat(
                    player_stats[stat_name], stat_name, position
                )
                total_score += abs(weight) * normalized_value
                total_weight += abs(weight)
        
        if total_weight == 0:
            return 50.0
        
        # Scale to 0-100
        final_score = (total_score / total_weight) * 100
        return max(0, min(100, final_score))
    
    def batch_calculate_scores(self, players_data: List[Dict[str, Any]]) -> List[float]:
        """Calculate performance scores for multiple players efficiently."""
        scores = []
        for player_data in players_data:
            stats = player_data.get('stats', {})
            position = player_data.get('position', 'Unknown')
            score = self.calculate_performance_score(stats, position)
            scores.append(score)
        return scores

class PlayerSimilarityAlgorithm:
    """
    Advanced player similarity algorithm using multiple clustering techniques.
    Finds statistically similar players for scouting and analysis.
    """
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.scaler = StandardScaler()
        self.kmeans_model = None
        self.dbscan_model = None
        self.feature_matrix = None
        self.player_ids = None
        self.is_fitted = False
    
    def _extract_features(self, players_data: List[Dict[str, Any]]) -> np.ndarray:
        """Extract numerical features for similarity calculation."""
        features = []
        feature_names = [
            'goals', 'assists', 'pass_accuracy', 'shots_total', 'tackles_won',
            'interceptions', 'key_passes', 'minutes_played', 'average_rating'
        ]
        
        for player_data in players_data:
            stats = player_data.get('stats', {})
            player_features = []
            
            for feature in feature_names:
                value = stats.get(feature, 0)
                player_features.append(float(value))
            
            features.append(player_features)
        
        return np.array(features)
    
    def fit(self, players_data: List[Dict[str, Any]], n_clusters: int = 8):
        """Fit clustering models on player data."""
        self.player_ids = [player['player_id'] for player in players_data]
        
        # Extract and normalize features
        features = self._extract_features(players_data)
        self.feature_matrix = self.scaler.fit_transform(features)
        
        # Fit K-Means clustering
        self.kmeans_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.kmeans_model.fit(self.feature_matrix)
        
        # Fit DBSCAN clustering
        self.dbscan_model = DBSCAN(eps=0.5, min_samples=3)
        self.dbscan_model.fit(self.feature_matrix)
        
        self.is_fitted = True
    
    def find_similar_players(self, target_player_id: int, method: str = 'cosine', top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Find players similar to the target player.
        
        Args:
            target_player_id: ID of the player to find similarities for
            method: 'cosine', 'euclidean', or 'cluster'
            top_k: Number of similar players to return
        
        Returns:
            List of (player_id, similarity_score) tuples
        """
        if not self.is_fitted:
            raise ValueError("Algorithm must be fitted before finding similarities")
        
        try:
            target_index = self.player_ids.index(target_player_id)
        except ValueError:
            return []  # Player not found
        
        target_features = self.feature_matrix[target_index].reshape(1, -1)
        
        if method == 'cosine':
            similarities = cosine_similarity(target_features, self.feature_matrix)[0]
        elif method == 'euclidean':
            distances = euclidean_distances(target_features, self.feature_matrix)[0]
            # Convert distances to similarities (higher is more similar)
            max_distance = np.max(distances)
            similarities = 1 - (distances / max_distance)
        elif method == 'cluster':
            # Use cluster membership for similarity
            target_cluster = self.kmeans_model.labels_[target_index]
            similarities = (self.kmeans_model.labels_ == target_cluster).astype(float)
        else:
            raise ValueError(f"Unknown similarity method: {method}")
        
        # Get top-k similar players (excluding the target player)
        similar_indices = np.argsort(similarities)[::-1]
        result = []
        
        for idx in similar_indices:
            if idx != target_index and len(result) < top_k:
                player_id = self.player_ids[idx]
                similarity_score = similarities[idx]
                result.append((player_id, float(similarity_score)))
        
        return result
    
    def get_player_cluster(self, player_id: int) -> Optional[int]:
        """Get the cluster assignment for a specific player."""
        if not self.is_fitted:
            return None
        
        try:
            player_index = self.player_ids.index(player_id)
            return int(self.kmeans_model.labels_[player_index])
        except ValueError:
            return None
    
    def get_cluster_characteristics(self, cluster_id: int) -> Dict[str, float]:
        """Get the average characteristics of players in a cluster."""
        if not self.is_fitted:
            return {}
        
        cluster_mask = self.kmeans_model.labels_ == cluster_id
        if not np.any(cluster_mask):
            return {}
        
        cluster_features = self.feature_matrix[cluster_mask]
        avg_features = np.mean(cluster_features, axis=0)
        
        feature_names = [
            'goals', 'assists', 'pass_accuracy', 'shots_total', 'tackles_won',
            'interceptions', 'key_passes', 'minutes_played', 'average_rating'
        ]
        
        return dict(zip(feature_names, avg_features))

class PredictiveAlgorithm:
    """
    Time-series forecasting and regression algorithms for predicting player performance.
    Supports multiple prediction models and confidence intervals.
    """
    
    def __init__(self):
        self.models = {
            'linear_regression': LinearRegression(),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        self.fitted_models = {}
        self.feature_scaler = StandardScaler()
        self.target_scaler = StandardScaler()
    
    def prepare_time_series_features(self, historical_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features for time-series prediction.
        
        Args:
            historical_data: List of season data for a player
        
        Returns:
            Tuple of (features, targets) arrays
        """
        if len(historical_data) < 2:
            return np.array([]), np.array([])
        
        features = []
        targets = []
        
        for i in range(len(historical_data) - 1):
            current_season = historical_data[i]
            next_season = historical_data[i + 1]
            
            # Features: current season stats + age + trend
            feature_vector = [
                current_season.get('goals', 0),
                current_season.get('assists', 0),
                current_season.get('minutes_played', 0),
                current_season.get('average_rating', 0),
                current_season.get('age', 25),  # Default age
                i  # Season index as trend feature
            ]
            
            # Target: next season's performance score
            target = next_season.get('performance_score', 0)
            
            features.append(feature_vector)
            targets.append(target)
        
        return np.array(features), np.array(targets)
    
    def fit_prediction_models(self, training_data: Dict[int, List[Dict[str, Any]]]):
        """
        Fit prediction models on historical player data.
        
        Args:
            training_data: Dictionary mapping player_id to list of historical seasons
        """
        all_features = []
        all_targets = []
        
        # Collect training data from all players
        for player_id, historical_data in training_data.items():
            features, targets = self.prepare_time_series_features(historical_data)
            if len(features) > 0:
                all_features.extend(features)
                all_targets.extend(targets)
        
        if len(all_features) == 0:
            return
        
        X = np.array(all_features)
        y = np.array(all_targets)
        
        # Scale features and targets
        X_scaled = self.feature_scaler.fit_transform(X)
        y_scaled = self.target_scaler.fit_transform(y.reshape(-1, 1)).ravel()
        
        # Fit all models
        for model_name, model in self.models.items():
            model.fit(X_scaled, y_scaled)
            self.fitted_models[model_name] = model
    
    def predict_performance(self, player_current_stats: Dict[str, Any], model_name: str = 'random_forest') -> Dict[str, float]:
        """
        Predict next season performance for a player.
        
        Args:
            player_current_stats: Current season statistics
            model_name: Model to use for prediction
        
        Returns:
            Dictionary with prediction and confidence metrics
        """
        if model_name not in self.fitted_models:
            return {'prediction': 0.0, 'confidence': 0.0}
        
        # Prepare feature vector
        feature_vector = np.array([[
            player_current_stats.get('goals', 0),
            player_current_stats.get('assists', 0),
            player_current_stats.get('minutes_played', 0),
            player_current_stats.get('average_rating', 0),
            player_current_stats.get('age', 25),
            1  # Assume next season
        ]])
        
        # Scale features
        feature_vector_scaled = self.feature_scaler.transform(feature_vector)
        
        # Make prediction
        model = self.fitted_models[model_name]
        prediction_scaled = model.predict(feature_vector_scaled)[0]
        
        # Inverse transform prediction
        prediction = self.target_scaler.inverse_transform([[prediction_scaled]])[0][0]
        
        # Calculate confidence (simplified)
        if hasattr(model, 'estimators_'):
            # For ensemble models, use prediction variance as confidence measure
            predictions = [estimator.predict(feature_vector_scaled)[0] for estimator in model.estimators_]
            confidence = 1.0 / (1.0 + np.std(predictions))
        else:
            confidence = 0.8  # Default confidence for linear models
        
        return {
            'prediction': float(prediction),
            'confidence': float(confidence),
            'model_used': model_name
        }
    
    def predict_multiple_seasons(self, player_current_stats: Dict[str, Any], seasons_ahead: int = 3) -> List[Dict[str, float]]:
        """Predict performance for multiple seasons ahead."""
        predictions = []
        current_stats = player_current_stats.copy()
        
        for season in range(seasons_ahead):
            prediction = self.predict_performance(current_stats)
            predictions.append({
                'season_offset': season + 1,
                'predicted_score': prediction['prediction'],
                'confidence': prediction['confidence']
            })
            
            # Update stats for next iteration (simple aging model)
            current_stats['age'] = current_stats.get('age', 25) + 1
            # Slight performance decline with age (simplified)
            decline_factor = 0.98 if current_stats['age'] > 30 else 1.0
            for stat in ['goals', 'assists', 'average_rating']:
                if stat in current_stats:
                    current_stats[stat] *= decline_factor
        
        return predictions

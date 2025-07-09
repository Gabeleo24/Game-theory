#!/usr/bin/env python3
"""
KPI Algorithm Optimizer for Real Madrid Soccer Intelligence
Advanced machine learning system to find the best algorithms for soccer KPI prediction
Optimized for containerized deployment with comprehensive testing framework
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
import redis
import psycopg2
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from psycopg2.extras import RealDictCursor
import os
import sys
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AlgorithmResult:
    """Algorithm testing result."""
    algorithm_name: str
    kpi_type: str
    mse: float
    r2_score: float
    mae: float
    cv_score: float
    training_time: float
    prediction_accuracy: float
    feature_importance: Dict[str, float]
    hyperparameters: Dict[str, Any]

@dataclass
class KPIOptimizationResult:
    """KPI optimization result."""
    kpi_name: str
    best_algorithm: str
    best_score: float
    algorithm_rankings: List[AlgorithmResult]
    feature_rankings: Dict[str, float]
    optimization_timestamp: datetime

class KPIAlgorithmOptimizer:
    """Advanced algorithm optimizer for soccer KPI prediction."""
    
    def __init__(self):
        """Initialize the algorithm optimizer."""
        self.setup_connections()
        self.algorithms = self.initialize_algorithms()
        self.kpi_definitions = self.load_kpi_definitions()
        self.optimization_results = {}
        
    def setup_connections(self):
        """Setup database and cache connections."""
        try:
            # PostgreSQL connection
            self.db_conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=os.getenv('POSTGRES_PORT', 5432),
                database=os.getenv('POSTGRES_DB', 'soccer_intelligence'),
                user=os.getenv('POSTGRES_USER', 'soccerapp'),
                password=os.getenv('POSTGRES_PASSWORD', 'soccerpass123')
            )
            self.db_cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            
            # Redis connection
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                password=os.getenv('REDIS_PASSWORD', 'redispass123'),
                db=1,  # Use different DB for algorithm optimization
                decode_responses=True
            )
            
            # Test connections
            self.db_cursor.execute("SELECT 1")
            self.redis_client.ping()
            
            logger.info("✅ Database and Redis connections established")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup connections: {e}")
            raise
    
    def initialize_algorithms(self) -> Dict[str, Any]:
        """Initialize machine learning algorithms for testing."""
        return {
            'random_forest': {
                'model': RandomForestRegressor(random_state=42),
                'hyperparameters': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [5, 10, 15, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4]
                }
            },
            'gradient_boosting': {
                'model': GradientBoostingRegressor(random_state=42),
                'hyperparameters': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'max_depth': [3, 5, 7],
                    'subsample': [0.8, 0.9, 1.0]
                }
            },
            'linear_regression': {
                'model': LinearRegression(),
                'hyperparameters': {}
            },
            'ridge_regression': {
                'model': Ridge(random_state=42),
                'hyperparameters': {
                    'alpha': [0.1, 1.0, 10.0, 100.0]
                }
            },
            'lasso_regression': {
                'model': Lasso(random_state=42),
                'hyperparameters': {
                    'alpha': [0.01, 0.1, 1.0, 10.0]
                }
            },
            'svr': {
                'model': SVR(),
                'hyperparameters': {
                    'C': [0.1, 1, 10],
                    'gamma': ['scale', 'auto', 0.001, 0.01],
                    'kernel': ['rbf', 'linear', 'poly']
                }
            },
            'neural_network': {
                'model': MLPRegressor(random_state=42, max_iter=1000),
                'hyperparameters': {
                    'hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 50)],
                    'activation': ['relu', 'tanh'],
                    'alpha': [0.0001, 0.001, 0.01],
                    'learning_rate': ['constant', 'adaptive']
                }
            }
        }
    
    def load_kpi_definitions(self) -> Dict[str, Dict]:
        """Load KPI definitions and their target metrics."""
        return {
            'player_performance_rating': {
                'target_column': 'rating',
                'features': ['goals', 'assists', 'shots', 'shots_on_target', 'passes', 
                           'pass_accuracy', 'tackles', 'interceptions', 'minutes_played'],
                'description': 'Predict player match rating based on performance metrics'
            },
            'goal_scoring_probability': {
                'target_column': 'goals',
                'features': ['shots', 'shots_on_target', 'position_x', 'position_y', 
                           'minutes_played', 'pass_accuracy', 'key_passes'],
                'description': 'Predict goal scoring likelihood'
            },
            'assist_prediction': {
                'target_column': 'assists',
                'features': ['key_passes', 'crosses', 'through_balls', 'pass_accuracy',
                           'minutes_played', 'position', 'dribbles'],
                'description': 'Predict assist potential'
            },
            'defensive_impact': {
                'target_column': 'defensive_actions',
                'features': ['tackles', 'interceptions', 'clearances', 'blocks',
                           'aerial_duels_won', 'position', 'minutes_played'],
                'description': 'Predict defensive contribution'
            },
            'match_outcome_influence': {
                'target_column': 'match_impact_score',
                'features': ['rating', 'goals', 'assists', 'key_passes', 'tackles',
                           'interceptions', 'pass_accuracy', 'minutes_played'],
                'description': 'Predict player influence on match outcome'
            }
        }
    
    async def optimize_kpi_algorithms(self, kpi_name: str, season: str = "2023-2024") -> KPIOptimizationResult:
        """Optimize algorithms for a specific KPI."""
        logger.info(f"🔄 Optimizing algorithms for KPI: {kpi_name}")
        
        if kpi_name not in self.kpi_definitions:
            raise ValueError(f"Unknown KPI: {kpi_name}")
        
        kpi_config = self.kpi_definitions[kpi_name]
        
        # Load and prepare data
        data = await self.load_kpi_data(kpi_name, season)
        if data.empty:
            logger.warning(f"No data available for KPI: {kpi_name}")
            return None
        
        X, y = self.prepare_features_and_target(data, kpi_config)
        
        # Test all algorithms
        algorithm_results = []
        
        for algo_name, algo_config in self.algorithms.items():
            logger.info(f"  Testing algorithm: {algo_name}")
            
            try:
                result = await self.test_algorithm(
                    algo_name, algo_config, X, y, kpi_name
                )
                algorithm_results.append(result)
                
            except Exception as e:
                logger.warning(f"  Failed to test {algo_name}: {e}")
                continue
        
        # Rank algorithms by performance
        algorithm_results.sort(key=lambda x: x.cv_score, reverse=True)
        
        # Calculate feature importance rankings
        feature_rankings = self.calculate_feature_importance(algorithm_results, X.columns)
        
        # Create optimization result
        optimization_result = KPIOptimizationResult(
            kpi_name=kpi_name,
            best_algorithm=algorithm_results[0].algorithm_name if algorithm_results else None,
            best_score=algorithm_results[0].cv_score if algorithm_results else 0.0,
            algorithm_rankings=algorithm_results,
            feature_rankings=feature_rankings,
            optimization_timestamp=datetime.now()
        )
        
        # Cache results
        await self.cache_optimization_result(optimization_result)
        
        logger.info(f"✅ Algorithm optimization completed for {kpi_name}")
        return optimization_result
    
    async def load_kpi_data(self, kpi_name: str, season: str) -> pd.DataFrame:
        """Load data for KPI optimization."""
        # This is a simplified version - in practice, you'd have more complex queries
        query = """
        SELECT 
            ps.*,
            p.position,
            m.competition,
            m.match_date,
            CASE 
                WHEN (m.home_team_id = 53 AND m.home_score > m.away_score) OR 
                     (m.away_team_id = 53 AND m.away_score > m.home_score) THEN 1
                WHEN m.home_score = m.away_score THEN 0
                ELSE -1
            END as match_result,
            (ps.tackles + ps.interceptions + COALESCE(ps.clearances, 0) + COALESCE(ps.blocks, 0)) as defensive_actions,
            (ps.rating * ps.minutes_played / 90.0) as match_impact_score
        FROM player_statistics ps
        JOIN players p ON ps.player_id = p.player_id
        JOIN matches m ON ps.match_id = m.match_id
        WHERE m.season = %s AND p.team_id = 53 AND ps.minutes_played > 0
        ORDER BY m.match_date
        """
        
        self.db_cursor.execute(query, (season,))
        data = pd.DataFrame([dict(row) for row in self.db_cursor.fetchall()])
        
        # Handle missing values
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        data[numeric_columns] = data[numeric_columns].fillna(0)
        
        return data
    
    def prepare_features_and_target(self, data: pd.DataFrame, kpi_config: Dict) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features and target variable for machine learning."""
        # Select available features
        available_features = [col for col in kpi_config['features'] if col in data.columns]
        
        if not available_features:
            raise ValueError(f"No features available for KPI")
        
        X = data[available_features].copy()
        y = data[kpi_config['target_column']].copy()
        
        # Handle categorical variables (simple encoding)
        for col in X.columns:
            if X[col].dtype == 'object':
                X[col] = pd.Categorical(X[col]).codes
        
        # Remove rows with missing target values
        mask = ~y.isna()
        X = X[mask]
        y = y[mask]
        
        return X, y
    
    async def test_algorithm(
        self, 
        algo_name: str, 
        algo_config: Dict, 
        X: pd.DataFrame, 
        y: pd.Series, 
        kpi_name: str
    ) -> AlgorithmResult:
        """Test a specific algorithm on the KPI data."""
        start_time = datetime.now()
        
        # Scale features for algorithms that need it
        if algo_name in ['svr', 'neural_network']:
            scaler = StandardScaler()
            X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
        else:
            X_scaled = X
        
        # Use time series split for cross-validation
        tscv = TimeSeriesSplit(n_splits=5)
        
        # Get the model
        model = algo_config['model']
        
        # Perform cross-validation
        cv_scores = cross_val_score(model, X_scaled, y, cv=tscv, scoring='r2')
        
        # Fit the model for additional metrics
        model.fit(X_scaled, y)
        y_pred = model.predict(X_scaled)
        
        # Calculate metrics
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        cv_score = cv_scores.mean()
        
        # Calculate feature importance
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            for i, col in enumerate(X.columns):
                feature_importance[col] = float(model.feature_importances_[i])
        elif hasattr(model, 'coef_'):
            for i, col in enumerate(X.columns):
                feature_importance[col] = float(abs(model.coef_[i]))
        
        # Calculate prediction accuracy (percentage of predictions within acceptable range)
        accuracy_threshold = y.std() * 0.5  # Within 0.5 standard deviations
        prediction_accuracy = np.mean(np.abs(y - y_pred) <= accuracy_threshold) * 100
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        return AlgorithmResult(
            algorithm_name=algo_name,
            kpi_type=kpi_name,
            mse=float(mse),
            r2_score=float(r2),
            mae=float(mae),
            cv_score=float(cv_score),
            training_time=training_time,
            prediction_accuracy=float(prediction_accuracy),
            feature_importance=feature_importance,
            hyperparameters={}  # Would include optimized hyperparameters in full implementation
        )
    
    def calculate_feature_importance(self, algorithm_results: List[AlgorithmResult], features: List[str]) -> Dict[str, float]:
        """Calculate overall feature importance across all algorithms."""
        feature_scores = {feature: [] for feature in features}
        
        for result in algorithm_results:
            for feature, importance in result.feature_importance.items():
                if feature in feature_scores:
                    feature_scores[feature].append(importance)
        
        # Calculate average importance
        feature_rankings = {}
        for feature, scores in feature_scores.items():
            if scores:
                feature_rankings[feature] = np.mean(scores)
            else:
                feature_rankings[feature] = 0.0
        
        return dict(sorted(feature_rankings.items(), key=lambda x: x[1], reverse=True))
    
    async def cache_optimization_result(self, result: KPIOptimizationResult):
        """Cache optimization results in Redis."""
        cache_key = f"kpi_optimization_{result.kpi_name}"
        
        # Convert to serializable format
        result_dict = {
            'kpi_name': result.kpi_name,
            'best_algorithm': result.best_algorithm,
            'best_score': result.best_score,
            'algorithm_rankings': [
                {
                    'algorithm_name': r.algorithm_name,
                    'cv_score': r.cv_score,
                    'r2_score': r.r2_score,
                    'mae': r.mae,
                    'prediction_accuracy': r.prediction_accuracy,
                    'training_time': r.training_time
                } for r in result.algorithm_rankings
            ],
            'feature_rankings': result.feature_rankings,
            'optimization_timestamp': result.optimization_timestamp.isoformat()
        }
        
        self.redis_client.setex(
            cache_key,
            86400,  # 24 hours
            json.dumps(result_dict, default=str)
        )
    
    async def run_comprehensive_optimization(self, season: str = "2023-2024") -> Dict[str, KPIOptimizationResult]:
        """Run optimization for all KPIs."""
        logger.info("🚀 Starting comprehensive KPI algorithm optimization")
        
        results = {}
        
        for kpi_name in self.kpi_definitions.keys():
            try:
                result = await self.optimize_kpi_algorithms(kpi_name, season)
                if result:
                    results[kpi_name] = result
                    
            except Exception as e:
                logger.error(f"❌ Failed to optimize {kpi_name}: {e}")
                continue
        
        # Save comprehensive results
        await self.save_optimization_report(results)
        
        logger.info("✅ Comprehensive optimization completed")
        return results
    
    async def save_optimization_report(self, results: Dict[str, KPIOptimizationResult]):
        """Save comprehensive optimization report."""
        report = {
            'optimization_summary': {
                'total_kpis_optimized': len(results),
                'optimization_timestamp': datetime.now().isoformat(),
                'season': "2023-2024"
            },
            'kpi_results': {}
        }
        
        for kpi_name, result in results.items():
            report['kpi_results'][kpi_name] = {
                'best_algorithm': result.best_algorithm,
                'best_score': result.best_score,
                'top_3_algorithms': [
                    {
                        'name': r.algorithm_name,
                        'score': r.cv_score,
                        'accuracy': r.prediction_accuracy
                    } for r in result.algorithm_rankings[:3]
                ],
                'top_features': dict(list(result.feature_rankings.items())[:5])
            }
        
        # Save to file
        output_file = f"/app/data/algorithms/kpi_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📊 Optimization report saved to {output_file}")

async def main():
    """Main function to run the algorithm optimizer."""
    optimizer = KPIAlgorithmOptimizer()
    
    try:
        logger.info("🚀 Starting Real Madrid KPI Algorithm Optimization")
        
        # Run comprehensive optimization
        results = await optimizer.run_comprehensive_optimization("2023-2024")
        
        # Print summary
        print("\n" + "="*80)
        print("REAL MADRID KPI ALGORITHM OPTIMIZATION RESULTS")
        print("="*80)
        
        for kpi_name, result in results.items():
            print(f"\n{kpi_name.upper()}:")
            print(f"  Best Algorithm: {result.best_algorithm}")
            print(f"  Best Score (R²): {result.best_score:.4f}")
            print(f"  Top Features: {', '.join(list(result.feature_rankings.keys())[:3])}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"❌ Algorithm optimization failed: {e}")
        raise
    finally:
        if hasattr(optimizer, 'db_conn'):
            optimizer.db_conn.close()
        if hasattr(optimizer, 'redis_client'):
            optimizer.redis_client.close()

if __name__ == "__main__":
    asyncio.run(main())

"""
Optimized Shapley Value Analysis for ADS599 Capstone Soccer Intelligence System
Implements high-performance parallel Shapley computation with caching and memory optimization
for the 67 UEFA Champions League teams dataset (2019-2024 seasons).
"""

import pandas as pd
import numpy as np
import logging
import gc
import time
import pickle
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from functools import partial, lru_cache
import multiprocessing as mp
from pathlib import Path
import psutil
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Optimize imports
try:
    import shap
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import mean_squared_error, r2_score
    from sklearn.feature_selection import SelectKBest, f_regression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import scipy.sparse as sp
    from scipy.sparse import csr_matrix, csc_matrix
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

from ..utils.config import Config
from ..utils.logger import get_logger
from ..data_processing.data_integrator import DataIntegrator


@dataclass
class ShapleyMetrics:
    """Performance metrics for Shapley analysis operations."""
    computation_time: float
    memory_usage_gb: float
    samples_processed: int
    features_analyzed: int
    cache_hits: int
    cache_misses: int
    
    @property
    def samples_per_second(self) -> float:
        return self.samples_processed / max(self.computation_time, 0.001)
    
    @property
    def cache_hit_rate(self) -> float:
        total_requests = self.cache_hits + self.cache_misses
        return self.cache_hits / max(total_requests, 1)


class OptimizedShapleyAnalysis:
    """
    High-performance Shapley value analysis with parallel computation and caching.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the optimized Shapley analyzer."""
        self.config = config or Config()
        self.logger = get_logger(__name__)
        
        # Performance configuration
        self.perf_config = self.config.get('performance', {})
        self.shapley_config = self.perf_config.get('shapley_analysis', {})
        
        # Computation settings
        self.n_jobs = self.shapley_config.get('computation.n_jobs', 4)
        self.batch_size = self.shapley_config.get('computation.batch_size', 100)
        self.use_sparse = self.shapley_config.get('computation.use_sparse_matrices', True)
        self.memory_efficient = self.shapley_config.get('computation.memory_efficient_mode', True)
        
        # Sampling settings
        self.sampling_strategy = self.shapley_config.get('sampling.strategy', 'stratified')
        self.min_samples = self.shapley_config.get('sampling.min_samples', 1000)
        self.max_samples = self.shapley_config.get('sampling.max_samples', 10000)
        self.early_stopping = self.shapley_config.get('sampling.early_stopping', True)
        self.convergence_threshold = self.shapley_config.get('sampling.convergence_threshold', 0.001)
        
        # Caching settings
        self.cache_enabled = self.shapley_config.get('caching.cache_intermediate_results', True)
        self.cache_dir = Path(self.shapley_config.get('caching.cache_directory', '/app/data/cache/shapley'))
        self.cache_compression = self.shapley_config.get('caching.cache_compression', True)
        
        # Model settings
        self.model_config = self.shapley_config.get('model', {})
        
        # Initialize components
        self.data_integrator = DataIntegrator(config)
        self.scaler = StandardScaler()
        self.feature_selector = SelectKBest(f_regression, k='all') if SKLEARN_AVAILABLE else None
        
        # Cache management
        self.cache_hits = 0
        self.cache_misses = 0
        self._setup_cache()
        
        # Memory monitoring
        self.process = psutil.Process()
        
        self.logger.info(f"Initialized OptimizedShapleyAnalysis with n_jobs={self.n_jobs}, "
                        f"batch_size={self.batch_size}, cache_enabled={self.cache_enabled}")
    
    def _setup_cache(self) -> None:
        """Setup caching directory and mechanisms."""
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Cache directory setup: {self.cache_dir}")
    
    def _get_cache_key(self, data_hash: str, params: Dict[str, Any]) -> str:
        """Generate cache key for analysis parameters."""
        params_str = str(sorted(params.items()))
        combined = f"{data_hash}_{params_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_data_hash(self, df: pd.DataFrame) -> str:
        """Generate hash for DataFrame to use in caching."""
        return hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load results from cache."""
        if not self.cache_enabled:
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                if self.cache_compression and JOBLIB_AVAILABLE:
                    result = joblib.load(cache_file)
                else:
                    with open(cache_file, 'rb') as f:
                        result = pickle.load(f)
                
                self.cache_hits += 1
                self.logger.debug(f"Cache hit for key: {cache_key}")
                return result
            except Exception as e:
                self.logger.warning(f"Error loading from cache {cache_key}: {e}")
        
        self.cache_misses += 1
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Save results to cache."""
        if not self.cache_enabled:
            return
        
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        try:
            if self.cache_compression and JOBLIB_AVAILABLE:
                joblib.dump(data, cache_file, compress=3)
            else:
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
            
            self.logger.debug(f"Saved to cache: {cache_key}")
        except Exception as e:
            self.logger.warning(f"Error saving to cache {cache_key}: {e}")
    
    def _optimize_model_selection(self, X: pd.DataFrame, y: pd.Series) -> Any:
        """Select and optimize the best model for Shapley analysis."""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for model optimization")
        
        models = {
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=self.model_config.get('n_estimators', 100),
                max_depth=self.model_config.get('max_depth', 6),
                learning_rate=self.model_config.get('learning_rate', 0.1),
                subsample=self.model_config.get('subsample', 0.8),
                random_state=42,
                n_iter_no_change=10,
                validation_fraction=0.1
            ),
            'random_forest': RandomForestRegressor(
                n_estimators=self.model_config.get('n_estimators', 100),
                max_depth=self.model_config.get('max_depth', 6),
                max_features=self.model_config.get('max_features', 'sqrt'),
                random_state=42,
                n_jobs=self.n_jobs
            )
        }
        
        best_model = None
        best_score = -np.inf
        
        # Quick model selection with cross-validation
        for name, model in models.items():
            try:
                scores = cross_val_score(model, X, y, cv=3, scoring='r2', n_jobs=self.n_jobs)
                avg_score = np.mean(scores)
                
                self.logger.debug(f"Model {name} CV score: {avg_score:.4f}")
                
                if avg_score > best_score:
                    best_score = avg_score
                    best_model = model
                    
            except Exception as e:
                self.logger.warning(f"Error evaluating model {name}: {e}")
        
        if best_model is None:
            # Fallback to gradient boosting
            best_model = models['gradient_boosting']
        
        return best_model
    
    def _prepare_features(self, df: pd.DataFrame, target_column: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features for Shapley analysis with optimization."""
        # Separate features and target
        feature_columns = [col for col in df.columns if col != target_column and df[col].dtype in ['int64', 'float64']]
        
        if not feature_columns:
            raise ValueError("No numeric feature columns found")
        
        X = df[feature_columns].copy()
        y = df[target_column].copy()
        
        # Handle missing values
        X = X.fillna(X.median())
        y = y.fillna(y.median())
        
        # Feature selection for performance
        if self.feature_selector and len(feature_columns) > 20:
            k = min(20, len(feature_columns))  # Limit to top 20 features
            self.feature_selector.set_params(k=k)
            X_selected = self.feature_selector.fit_transform(X, y)
            selected_features = X.columns[self.feature_selector.get_support()].tolist()
            X = pd.DataFrame(X_selected, columns=selected_features, index=X.index)
            
            self.logger.info(f"Selected {len(selected_features)} features from {len(feature_columns)}")
        
        # Scale features
        X_scaled = pd.DataFrame(
            self.scaler.fit_transform(X),
            columns=X.columns,
            index=X.index
        )
        
        return X_scaled, y
    
    def _compute_shapley_batch(self, model: Any, X_batch: pd.DataFrame, 
                              explainer: Any) -> np.ndarray:
        """Compute Shapley values for a batch of samples."""
        try:
            if self.memory_efficient:
                # Process in smaller sub-batches to manage memory
                sub_batch_size = min(50, len(X_batch))
                shap_values_list = []
                
                for i in range(0, len(X_batch), sub_batch_size):
                    sub_batch = X_batch.iloc[i:i + sub_batch_size]
                    sub_shap_values = explainer.shap_values(sub_batch)
                    shap_values_list.append(sub_shap_values)
                    
                    # Memory cleanup
                    gc.collect()
                
                return np.vstack(shap_values_list)
            else:
                return explainer.shap_values(X_batch)
                
        except Exception as e:
            self.logger.error(f"Error computing Shapley values for batch: {e}")
            # Return zeros as fallback
            return np.zeros((len(X_batch), X_batch.shape[1]))
    
    def analyze_player_contributions(self, players_df: pd.DataFrame, 
                                   teams_df: pd.DataFrame,
                                   target_metric: str = 'Pts') -> Dict[str, Any]:
        """
        Analyze player contributions using optimized Shapley values.
        
        Args:
            players_df: Player statistics DataFrame
            teams_df: Team performance DataFrame
            target_metric: Target metric to analyze
            
        Returns:
            Dictionary containing Shapley analysis results
        """
        start_time = time.time()
        memory_before = self.process.memory_info().rss / (1024 ** 3)
        
        self.logger.info(f"Starting optimized Shapley analysis for {len(players_df)} players, "
                        f"target metric: {target_metric}")
        
        # Generate cache key
        data_hash = self._get_data_hash(pd.concat([players_df, teams_df]))
        cache_params = {
            'target_metric': target_metric,
            'n_jobs': self.n_jobs,
            'batch_size': self.batch_size,
            'max_samples': self.max_samples
        }
        cache_key = self._get_cache_key(data_hash, cache_params)
        
        # Check cache first
        cached_result = self._load_from_cache(cache_key)
        if cached_result is not None:
            self.logger.info("Returning cached Shapley analysis results")
            return cached_result
        
        try:
            # Prepare data
            analysis_df = self.data_integrator.integrate_player_team_data(players_df, teams_df)
            
            if analysis_df.empty or target_metric not in analysis_df.columns:
                raise ValueError(f"Target metric '{target_metric}' not found in integrated data")
            
            # Prepare features
            X, y = self._prepare_features(analysis_df, target_metric)
            
            # Sample data if too large
            if len(X) > self.max_samples:
                sample_indices = np.random.choice(len(X), self.max_samples, replace=False)
                X = X.iloc[sample_indices]
                y = y.iloc[sample_indices]
                self.logger.info(f"Sampled {self.max_samples} records from {len(analysis_df)}")
            
            # Select and train model
            model = self._optimize_model_selection(X, y)
            model.fit(X, y)
            
            # Create SHAP explainer
            if hasattr(shap, 'TreeExplainer'):
                explainer = shap.TreeExplainer(model)
            else:
                explainer = shap.Explainer(model, X.sample(min(100, len(X))))
            
            # Compute Shapley values in batches
            all_shap_values = []
            
            for i in range(0, len(X), self.batch_size):
                batch_end = min(i + self.batch_size, len(X))
                X_batch = X.iloc[i:batch_end]
                
                batch_shap_values = self._compute_shapley_batch(model, X_batch, explainer)
                all_shap_values.append(batch_shap_values)
                
                self.logger.debug(f"Processed batch {i//self.batch_size + 1}/{(len(X)-1)//self.batch_size + 1}")
                
                # Memory management
                if i % (self.batch_size * 5) == 0:
                    gc.collect()
            
            # Combine all Shapley values
            shap_values = np.vstack(all_shap_values)
            
            # Calculate feature importance
            feature_importance = np.abs(shap_values).mean(axis=0)
            feature_importance_df = pd.DataFrame({
                'feature': X.columns,
                'importance': feature_importance
            }).sort_values('importance', ascending=False)
            
            # Calculate player-level Shapley values
            player_shapley = pd.DataFrame(shap_values, columns=X.columns, index=X.index)
            player_shapley['total_contribution'] = player_shapley.sum(axis=1)
            
            # Model performance metrics
            y_pred = model.predict(X)
            model_r2 = r2_score(y, y_pred)
            model_mse = mean_squared_error(y, y_pred)
            
            # Compile results
            end_time = time.time()
            memory_after = self.process.memory_info().rss / (1024 ** 3)
            
            metrics = ShapleyMetrics(
                computation_time=end_time - start_time,
                memory_usage_gb=memory_after - memory_before,
                samples_processed=len(X),
                features_analyzed=len(X.columns),
                cache_hits=self.cache_hits,
                cache_misses=self.cache_misses
            )
            
            results = {
                'feature_importance': feature_importance_df,
                'player_shapley_values': player_shapley,
                'model_performance': {
                    'r2_score': model_r2,
                    'mse': model_mse,
                    'model_type': type(model).__name__
                },
                'analysis_metadata': {
                    'target_metric': target_metric,
                    'samples_analyzed': len(X),
                    'features_used': X.columns.tolist(),
                    'computation_time': metrics.computation_time,
                    'memory_usage_gb': metrics.memory_usage_gb,
                    'cache_hit_rate': metrics.cache_hit_rate
                }
            }
            
            # Save to cache
            self._save_to_cache(cache_key, results)
            
            self.logger.info(f"Shapley analysis completed: {metrics.samples_processed} samples in "
                           f"{metrics.computation_time:.2f}s ({metrics.samples_per_second:.0f} samples/s)")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in Shapley analysis: {e}")
            raise

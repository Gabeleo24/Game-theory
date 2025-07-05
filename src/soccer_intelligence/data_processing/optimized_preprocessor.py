"""
Optimized Data Preprocessing Pipeline for ADS599 Capstone Soccer Intelligence System
Implements high-performance data cleaning, transformation, and feature engineering
for the 67 UEFA Champions League teams dataset (2019-2024 seasons).
"""

import pandas as pd
import numpy as np
import gc
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from functools import partial
import multiprocessing as mp
from pathlib import Path
import psutil
import time
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Optimize pandas and numpy
pd.set_option('mode.copy_on_write', True)
pd.set_option('compute.use_bottleneck', True)
pd.set_option('compute.use_numexpr', True)

try:
    import numba
    from numba import jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    prange = range

from ..utils.config import Config
from ..utils.logger import get_logger


@dataclass
class ProcessingMetrics:
    """Performance metrics for data processing operations."""
    start_time: float
    end_time: float
    memory_before: float
    memory_after: float
    rows_processed: int
    chunk_count: int
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def memory_delta(self) -> float:
        return self.memory_after - self.memory_before
    
    @property
    def rows_per_second(self) -> float:
        return self.rows_processed / max(self.duration, 0.001)


class OptimizedPreprocessor:
    """
    High-performance data preprocessing pipeline optimized for soccer intelligence data.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the optimized preprocessor."""
        self.config = config or Config()
        self.logger = get_logger(__name__)
        
        # Performance configuration
        self.perf_config = self.config.get('performance', {})
        self.chunk_size = self.perf_config.get('data_processing.chunk_processing.chunk_size', 10000)
        self.max_workers = self.perf_config.get('parallel_processing.workers.max_workers', 4)
        self.memory_limit_gb = self.perf_config.get('data_processing.memory.max_memory_usage_gb', 6)
        self.use_numba = self.perf_config.get('data_processing.vectorization.use_numba_jit', True) and NUMBA_AVAILABLE
        
        # Memory monitoring
        self.process = psutil.Process()
        self.memory_threshold = self.memory_limit_gb * 0.8  # 80% threshold
        
        self.logger.info(f"Initialized OptimizedPreprocessor with chunk_size={self.chunk_size}, "
                        f"max_workers={self.max_workers}, numba_enabled={self.use_numba}")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in GB."""
        return self.process.memory_info().rss / (1024 ** 3)
    
    def _check_memory_usage(self) -> None:
        """Check memory usage and trigger garbage collection if needed."""
        current_memory = self._get_memory_usage()
        if current_memory > self.memory_threshold:
            self.logger.warning(f"Memory usage {current_memory:.2f}GB exceeds threshold {self.memory_threshold:.2f}GB")
            gc.collect()
            new_memory = self._get_memory_usage()
            self.logger.info(f"Garbage collection freed {current_memory - new_memory:.2f}GB")
    
    @jit(nopython=True, parallel=True)
    def _vectorized_normalize(self, data: np.ndarray) -> np.ndarray:
        """Vectorized normalization using numba for performance."""
        if not NUMBA_AVAILABLE:
            return (data - np.mean(data)) / (np.std(data) + 1e-8)
        
        mean_val = np.mean(data)
        std_val = np.std(data)
        result = np.empty_like(data)
        
        for i in prange(len(data)):
            result[i] = (data[i] - mean_val) / (std_val + 1e-8)
        
        return result
    
    @jit(nopython=True, parallel=True)
    def _vectorized_outlier_detection(self, data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """Vectorized outlier detection using z-score."""
        if not NUMBA_AVAILABLE:
            z_scores = np.abs((data - np.mean(data)) / (np.std(data) + 1e-8))
            return z_scores < threshold
        
        mean_val = np.mean(data)
        std_val = np.std(data)
        result = np.empty(len(data), dtype=np.bool_)
        
        for i in prange(len(data)):
            z_score = abs((data[i] - mean_val) / (std_val + 1e-8))
            result[i] = z_score < threshold
        
        return result
    
    def _process_chunk(self, chunk: pd.DataFrame, chunk_idx: int, 
                      processing_functions: List[callable]) -> Tuple[pd.DataFrame, ProcessingMetrics]:
        """Process a single chunk of data with performance monitoring."""
        start_time = time.time()
        memory_before = self._get_memory_usage()
        
        try:
            # Apply processing functions sequentially
            processed_chunk = chunk.copy()
            for func in processing_functions:
                processed_chunk = func(processed_chunk)
            
            # Memory cleanup
            del chunk
            gc.collect()
            
            end_time = time.time()
            memory_after = self._get_memory_usage()
            
            metrics = ProcessingMetrics(
                start_time=start_time,
                end_time=end_time,
                memory_before=memory_before,
                memory_after=memory_after,
                rows_processed=len(processed_chunk),
                chunk_count=1
            )
            
            self.logger.debug(f"Processed chunk {chunk_idx}: {len(processed_chunk)} rows in "
                            f"{metrics.duration:.2f}s ({metrics.rows_per_second:.0f} rows/s)")
            
            return processed_chunk, metrics
            
        except Exception as e:
            self.logger.error(f"Error processing chunk {chunk_idx}: {e}")
            raise
    
    def _chunked_processing(self, df: pd.DataFrame, 
                           processing_functions: List[callable],
                           parallel: bool = True) -> Tuple[pd.DataFrame, List[ProcessingMetrics]]:
        """Process DataFrame in chunks with optional parallelization."""
        chunks = [df[i:i + self.chunk_size] for i in range(0, len(df), self.chunk_size)]
        processed_chunks = []
        all_metrics = []
        
        self.logger.info(f"Processing {len(chunks)} chunks with chunk_size={self.chunk_size}, "
                        f"parallel={parallel}")
        
        if parallel and len(chunks) > 1 and self.max_workers > 1:
            # Parallel processing
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all chunks
                future_to_chunk = {
                    executor.submit(self._process_chunk, chunk, idx, processing_functions): idx
                    for idx, chunk in enumerate(chunks)
                }
                
                # Collect results
                for future in as_completed(future_to_chunk):
                    chunk_idx = future_to_chunk[future]
                    try:
                        processed_chunk, metrics = future.result()
                        processed_chunks.append((chunk_idx, processed_chunk))
                        all_metrics.append(metrics)
                        
                        # Memory check after each chunk
                        self._check_memory_usage()
                        
                    except Exception as e:
                        self.logger.error(f"Chunk {chunk_idx} processing failed: {e}")
                        raise
                
                # Sort by original chunk order
                processed_chunks.sort(key=lambda x: x[0])
                processed_chunks = [chunk for _, chunk in processed_chunks]
        else:
            # Sequential processing
            for idx, chunk in enumerate(chunks):
                processed_chunk, metrics = self._process_chunk(chunk, idx, processing_functions)
                processed_chunks.append(processed_chunk)
                all_metrics.append(metrics)
                
                # Memory check after each chunk
                self._check_memory_usage()
        
        # Combine all processed chunks
        result_df = pd.concat(processed_chunks, ignore_index=True)
        
        # Final memory cleanup
        del processed_chunks, chunks
        gc.collect()
        
        return result_df, all_metrics
    
    def clean_player_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimized player data cleaning with vectorized operations."""
        self.logger.info(f"Starting optimized player data cleaning for {len(df)} records")
        
        def _clean_chunk(chunk_df: pd.DataFrame) -> pd.DataFrame:
            """Clean a chunk of player data."""
            # Vectorized missing value handling
            numeric_columns = chunk_df.select_dtypes(include=[np.number]).columns
            chunk_df[numeric_columns] = chunk_df[numeric_columns].fillna(0)
            
            # Vectorized outlier detection and removal
            for col in numeric_columns:
                if col in ['goals_total', 'goals_assists', 'games_minutes']:
                    mask = self._vectorized_outlier_detection(chunk_df[col].values)
                    chunk_df = chunk_df[mask]
            
            # Vectorized data type optimization
            for col in numeric_columns:
                if chunk_df[col].dtype == 'float64':
                    chunk_df[col] = pd.to_numeric(chunk_df[col], downcast='float')
                elif chunk_df[col].dtype == 'int64':
                    chunk_df[col] = pd.to_numeric(chunk_df[col], downcast='integer')
            
            return chunk_df
        
        # Process in chunks
        cleaned_df, metrics = self._chunked_processing(df, [_clean_chunk])
        
        total_duration = sum(m.duration for m in metrics)
        total_rows = sum(m.rows_processed for m in metrics)
        
        self.logger.info(f"Player data cleaning completed: {total_rows} rows processed in "
                        f"{total_duration:.2f}s ({total_rows/total_duration:.0f} rows/s)")
        
        return cleaned_df

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimized feature engineering with vectorized operations."""
        self.logger.info(f"Starting optimized feature engineering for {len(df)} records")

        def _engineer_chunk(chunk_df: pd.DataFrame) -> pd.DataFrame:
            """Engineer features for a chunk of data."""
            # Vectorized efficiency metrics
            chunk_df['goals_per_game'] = np.where(
                chunk_df['games_appearances'] > 0,
                chunk_df['goals_total'] / chunk_df['games_appearances'],
                0
            )

            chunk_df['assists_per_game'] = np.where(
                chunk_df['games_appearances'] > 0,
                chunk_df['goals_assists'] / chunk_df['games_appearances'],
                0
            )

            chunk_df['minutes_per_game'] = np.where(
                chunk_df['games_appearances'] > 0,
                chunk_df['games_minutes'] / chunk_df['games_appearances'],
                0
            )

            # Vectorized composite metrics
            chunk_df['goal_contributions'] = chunk_df['goals_total'] + chunk_df['goals_assists']
            chunk_df['goal_contributions_per_game'] = np.where(
                chunk_df['games_appearances'] > 0,
                chunk_df['goal_contributions'] / chunk_df['games_appearances'],
                0
            )

            # Vectorized performance score calculation
            if self.use_numba:
                goals_norm = self._vectorized_normalize(chunk_df['goals_per_game'].values)
                assists_norm = self._vectorized_normalize(chunk_df['assists_per_game'].values)
                rating_norm = self._vectorized_normalize(chunk_df.get('games_rating', pd.Series([0] * len(chunk_df))).values)

                chunk_df['performance_score'] = (goals_norm * 0.4 + assists_norm * 0.3 + rating_norm * 0.3) * 10
            else:
                # Fallback to pandas operations
                goals_norm = (chunk_df['goals_per_game'] - chunk_df['goals_per_game'].mean()) / (chunk_df['goals_per_game'].std() + 1e-8)
                assists_norm = (chunk_df['assists_per_game'] - chunk_df['assists_per_game'].mean()) / (chunk_df['assists_per_game'].std() + 1e-8)
                rating_norm = (chunk_df.get('games_rating', 0) - chunk_df.get('games_rating', 0).mean()) / (chunk_df.get('games_rating', 0).std() + 1e-8)

                chunk_df['performance_score'] = (goals_norm * 0.4 + assists_norm * 0.3 + rating_norm * 0.3) * 10

            return chunk_df

        # Process in chunks
        engineered_df, metrics = self._chunked_processing(df, [_engineer_chunk])

        total_duration = sum(m.duration for m in metrics)
        total_rows = sum(m.rows_processed for m in metrics)

        self.logger.info(f"Feature engineering completed: {total_rows} rows processed in "
                        f"{total_duration:.2f}s ({total_rows/total_duration:.0f} rows/s)")

        return engineered_df

    def transform_team_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimized team data transformation."""
        self.logger.info(f"Starting optimized team data transformation for {len(df)} records")

        def _transform_chunk(chunk_df: pd.DataFrame) -> pd.DataFrame:
            """Transform a chunk of team data."""
            # Vectorized team performance metrics
            chunk_df['win_percentage'] = np.where(
                chunk_df['total_matches'] > 0,
                chunk_df['wins'] / chunk_df['total_matches'] * 100,
                0
            )

            chunk_df['goals_per_game'] = np.where(
                chunk_df['total_matches'] > 0,
                chunk_df['goals_scored'] / chunk_df['total_matches'],
                0
            )

            chunk_df['goals_conceded_per_game'] = np.where(
                chunk_df['total_matches'] > 0,
                chunk_df['goals_conceded'] / chunk_df['total_matches'],
                0
            )

            chunk_df['goal_difference'] = chunk_df['goals_scored'] - chunk_df['goals_conceded']
            chunk_df['goal_difference_per_game'] = np.where(
                chunk_df['total_matches'] > 0,
                chunk_df['goal_difference'] / chunk_df['total_matches'],
                0
            )

            # Vectorized defensive metrics
            chunk_df['clean_sheet_percentage'] = np.where(
                chunk_df['total_matches'] > 0,
                chunk_df.get('clean_sheets', 0) / chunk_df['total_matches'] * 100,
                0
            )

            return chunk_df

        # Process in chunks
        transformed_df, metrics = self._chunked_processing(df, [_transform_chunk])

        total_duration = sum(m.duration for m in metrics)
        total_rows = sum(m.rows_processed for m in metrics)

        self.logger.info(f"Team data transformation completed: {total_rows} rows processed in "
                        f"{total_duration:.2f}s ({total_rows/total_duration:.0f} rows/s)")

        return transformed_df

    def optimize_dataframe_memory(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame memory usage through data type optimization."""
        self.logger.info(f"Optimizing memory usage for DataFrame with {len(df)} rows")

        memory_before = df.memory_usage(deep=True).sum() / (1024 ** 2)  # MB

        # Optimize numeric columns
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')

        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')

        # Optimize object columns
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) < 0.5:  # If less than 50% unique values
                df[col] = df[col].astype('category')

        memory_after = df.memory_usage(deep=True).sum() / (1024 ** 2)  # MB
        memory_reduction = ((memory_before - memory_after) / memory_before) * 100

        self.logger.info(f"Memory optimization completed: {memory_before:.1f}MB -> {memory_after:.1f}MB "
                        f"({memory_reduction:.1f}% reduction)")

        return df

    def get_processing_summary(self, metrics_list: List[ProcessingMetrics]) -> Dict[str, Any]:
        """Generate a summary of processing performance metrics."""
        if not metrics_list:
            return {}

        total_duration = sum(m.duration for m in metrics_list)
        total_rows = sum(m.rows_processed for m in metrics_list)
        total_chunks = len(metrics_list)
        avg_memory_delta = sum(m.memory_delta for m in metrics_list) / total_chunks

        return {
            'total_duration_seconds': round(total_duration, 2),
            'total_rows_processed': total_rows,
            'total_chunks': total_chunks,
            'average_rows_per_second': round(total_rows / max(total_duration, 0.001), 0),
            'average_chunk_duration': round(total_duration / total_chunks, 2),
            'average_memory_delta_gb': round(avg_memory_delta, 3),
            'peak_memory_usage_gb': round(max(m.memory_after for m in metrics_list), 2)
        }

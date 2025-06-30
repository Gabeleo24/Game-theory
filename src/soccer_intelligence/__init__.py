"""
Soccer Performance Intelligence System

A comprehensive system for analyzing soccer performance using multi-source data,
Shapley values for tactical analysis, and RAG capabilities for player queries.
"""

__version__ = "1.0.0"
__author__ = "ADS599 Capstone Team"

# Import core modules (RAG system optional due to dependency issues)
from .data_collection import *
from .data_processing import *
from .analysis import *
from .utils import *

# Optional RAG system import
try:
    from .rag_system import *
except ImportError:
    print("Note: RAG system not available due to dependency issues. Core functionality still works.")

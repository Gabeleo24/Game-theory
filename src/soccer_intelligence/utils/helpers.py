"""
Helper functions and utilities for the Soccer Intelligence System.
"""

import json
import pickle
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import os
import hashlib


def save_json(data: Dict[str, Any], filepath: str, indent: int = 2) -> None:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        filepath: Path to save file
        indent: JSON indentation
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, default=str)


def load_json(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load data from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Loaded data or None if file doesn't exist
    """
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_pickle(data: Any, filepath: str) -> None:
    """
    Save data to pickle file.
    
    Args:
        data: Data to save
        filepath: Path to save file
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)


def load_pickle(filepath: str) -> Any:
    """
    Load data from pickle file.
    
    Args:
        filepath: Path to pickle file
        
    Returns:
        Loaded data or None if file doesn't exist
    """
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    except (pickle.PickleError, IOError):
        return None


def normalize_team_name(team_name: str) -> str:
    """
    Normalize team name for consistent matching.
    
    Args:
        team_name: Original team name
        
    Returns:
        Normalized team name
    """
    # Remove common suffixes and prefixes
    suffixes = ['FC', 'CF', 'Club', 'Football Club', 'Soccer Club']
    prefixes = ['Real', 'Club']
    
    normalized = team_name.strip()
    
    # Remove suffixes
    for suffix in suffixes:
        if normalized.endswith(f' {suffix}'):
            normalized = normalized[:-len(f' {suffix}')]
    
    # Remove prefixes (but keep Real Madrid as is)
    if not normalized.startswith('Real Madrid'):
        for prefix in prefixes:
            if normalized.startswith(f'{prefix} '):
                normalized = normalized[len(f'{prefix} '):]
    
    return normalized.strip()


def normalize_player_name(player_name: str) -> str:
    """
    Normalize player name for consistent matching.
    
    Args:
        player_name: Original player name
        
    Returns:
        Normalized player name
    """
    # Basic normalization
    normalized = player_name.strip()
    
    # Remove common suffixes like Jr., Sr.
    suffixes = [' Jr.', ' Sr.', ' III', ' II']
    for suffix in suffixes:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)]
    
    return normalized.strip()


def calculate_age(birth_date: Union[str, datetime], reference_date: Optional[datetime] = None) -> Optional[int]:
    """
    Calculate age from birth date.
    
    Args:
        birth_date: Birth date as string or datetime
        reference_date: Reference date for age calculation
        
    Returns:
        Age in years or None if calculation fails
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    try:
        if isinstance(birth_date, str):
            # Try different date formats
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']
            birth_dt = None
            
            for fmt in formats:
                try:
                    birth_dt = datetime.strptime(birth_date, fmt)
                    break
                except ValueError:
                    continue
            
            if birth_dt is None:
                return None
        else:
            birth_dt = birth_date
        
        age = reference_date.year - birth_dt.year
        
        # Adjust if birthday hasn't occurred this year
        if reference_date.month < birth_dt.month or \
           (reference_date.month == birth_dt.month and reference_date.day < birth_dt.day):
            age -= 1
        
        return age
    
    except (ValueError, TypeError):
        return None


def generate_hash(data: Any) -> str:
    """
    Generate MD5 hash for data.
    
    Args:
        data: Data to hash
        
    Returns:
        MD5 hash string
    """
    data_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(data_str.encode()).hexdigest()


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Flatten a nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
        
    Returns:
        Division result or default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def calculate_percentage(part: float, total: float, decimal_places: int = 2) -> float:
    """
    Calculate percentage with safe division.
    
    Args:
        part: Part value
        total: Total value
        decimal_places: Number of decimal places
        
    Returns:
        Percentage value
    """
    if total == 0:
        return 0.0
    
    percentage = (part / total) * 100
    return round(percentage, decimal_places)


def clean_numeric_value(value: Any) -> Optional[float]:
    """
    Clean and convert value to numeric.
    
    Args:
        value: Value to clean
        
    Returns:
        Numeric value or None if conversion fails
    """
    if value is None or value == '':
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remove common non-numeric characters
        cleaned = value.replace(',', '').replace('%', '').strip()
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    return None


def get_season_from_date(date: Union[str, datetime]) -> str:
    """
    Get season string from date (e.g., "2023-24").
    
    Args:
        date: Date as string or datetime
        
    Returns:
        Season string
    """
    if isinstance(date, str):
        try:
            date = datetime.strptime(date.split('T')[0], '%Y-%m-%d')
        except ValueError:
            return "Unknown"
    
    # European football season typically runs from August to May
    if date.month >= 8:  # August onwards is next season
        return f"{date.year}-{str(date.year + 1)[2:]}"
    else:  # January to July is current season
        return f"{date.year - 1}-{str(date.year)[2:]}"


def validate_data_completeness(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """
    Validate data completeness and return validation report.
    
    Args:
        data: Data to validate
        required_fields: List of required field names
        
    Returns:
        Validation report
    """
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif data[field] is None or data[field] == '':
            empty_fields.append(field)
    
    total_fields = len(required_fields)
    valid_fields = total_fields - len(missing_fields) - len(empty_fields)
    completeness_percentage = (valid_fields / total_fields) * 100 if total_fields > 0 else 0
    
    return {
        'is_valid': len(missing_fields) == 0 and len(empty_fields) == 0,
        'completeness_percentage': round(completeness_percentage, 2),
        'total_fields': total_fields,
        'valid_fields': valid_fields,
        'missing_fields': missing_fields,
        'empty_fields': empty_fields
    }

"""
Configuration management for the Soccer Intelligence System.
"""

import yaml
import os
from typing import Any, Dict, Optional
import logging


class Config:
    """Configuration manager for the application."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to configuration file. If None, uses default.
        """
        self.config_file = config_file or 'config/config.yaml'
        self.config_data = {}
        self.logger = logging.getLogger(__name__)
        
        self._load_config()
        self._load_api_keys()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f) or {}
                self.logger.info(f"Configuration loaded from {self.config_file}")
            else:
                # Try template file
                template_file = 'config/config_template.yaml'
                if os.path.exists(template_file):
                    with open(template_file, 'r', encoding='utf-8') as f:
                        self.config_data = yaml.safe_load(f) or {}
                    self.logger.warning(f"Using template configuration from {template_file}")
                else:
                    self.logger.warning("No configuration file found, using defaults")
                    self.config_data = self._get_default_config()
        
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.config_data = self._get_default_config()
    
    def _load_api_keys(self) -> None:
        """Load API keys from separate file."""
        api_keys_file = 'config/api_keys.yaml'
        
        try:
            if os.path.exists(api_keys_file):
                with open(api_keys_file, 'r', encoding='utf-8') as f:
                    api_keys = yaml.safe_load(f) or {}
                
                # Merge API keys into config
                self.config_data.update(api_keys)
                self.logger.info("API keys loaded successfully")
            else:
                self.logger.warning("API keys file not found")
        
        except Exception as e:
            self.logger.error(f"Error loading API keys: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            'api_football': {
                'base_url': 'https://v3.football.api-sports.io',
                'timeout': 30,
                'rate_limit_delay': 1.0,
                'cache_enabled': True,
                'cache_duration_hours': 24
            },
            'openai': {
                'model': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 1000,
                'embedding_model': 'text-embedding-ada-002'
            },
            'data_collection': {
                'cache_directory': 'data/raw',
                'max_requests_per_minute': 100
            },
            'data_processing': {
                'output_directory': 'data/processed'
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'api_football.timeout')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'api_football.timeout')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config_data
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def save(self, file_path: Optional[str] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            file_path: Path to save file. If None, uses original config file.
        """
        save_path = file_path or self.config_file
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to {save_path}")
        
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration data.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config_data.copy()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of updates to apply
        """
        def deep_update(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
            """Recursively update nested dictionaries."""
            for key, value in update_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_update(self.config_data, updates)
        self.logger.info("Configuration updated")
    
    def validate(self) -> bool:
        """
        Validate configuration for required fields.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        required_fields = [
            'api_football.base_url',
            'data_collection.cache_directory',
            'data_processing.output_directory'
        ]
        
        missing_fields = []
        for field in required_fields:
            if self.get(field) is None:
                missing_fields.append(field)
        
        if missing_fields:
            self.logger.error(f"Missing required configuration fields: {missing_fields}")
            return False
        
        return True

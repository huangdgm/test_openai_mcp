"""
Configuration Manager for loading and managing YAML-based configurations
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """
    Manages configuration loading from YAML files with environment-specific overrides.
    
    Supports:
    - Loading base configuration
    - Environment-specific overrides
    - Merging configurations
    - Easy access to nested configuration values
    """
    
    def __init__(self, config_dir: str = "config/environments"):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self._config: Dict[str, Any] = {}
        self._environment: Optional[str] = None
        
    def load_config(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration for the specified environment.
        
        Args:
            environment: Environment name (e.g., 'development', 'production')
                        If None, uses ENV environment variable or defaults to 'development'
        
        Returns:
            Merged configuration dictionary
        """
        if environment is None:
            environment = os.getenv("ENV", "development")
        
        self._environment = environment
        
        # Load base configuration
        base_config_path = self.config_dir / "base.yaml"
        if not base_config_path.exists():
            raise FileNotFoundError(f"Base configuration file not found: {base_config_path}")
        
        with open(base_config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        
        # Load environment-specific configuration if it exists
        env_config_path = self.config_dir / f"{environment}.yaml"
        if env_config_path.exists():
            with open(env_config_path, 'r') as f:
                env_config = yaml.safe_load(f)
                self._config = self._merge_configs(self._config, env_config)
        
        return self._config
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two configuration dictionaries.
        
        Args:
            base: Base configuration
            override: Override configuration
            
        Returns:
            Merged configuration
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the configuration value (e.g., 'azure_openai.model')
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    @property
    def environment(self) -> str:
        """Get current environment name."""
        return self._environment or "development"
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary."""
        return self._config.copy()


# Global configuration manager instance
config_manager = ConfigManager() 
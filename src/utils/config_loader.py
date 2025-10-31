"""
Configuration loader for Bible Study Finder Backend.
Handles environment variable substitution in YAML files.
"""

import os
import re
import yaml
from typing import Any, Dict, Optional
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ConfigLoader:
    """Loads configuration from YAML files with environment variable substitution."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the config loader.
        
        Args:
            config_path: Path to the config file (optional)
        """
        self.config_path = config_path or self._find_config_file()
        self._config_cache: Optional[Dict[str, Any]] = None
    
    def _find_config_file(self) -> str:
        """Find the config file in the project structure."""
        # Try different possible locations
        possible_paths = [
            "src/static/config.yaml",
            "config.yaml",
            "config/config.yaml",
            "src/config.yaml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.debug(f"Found config file at: {path}")
                return path
        
        logger.warning("No config file found, using default configuration")
        return "src/static/config.yaml"
    
    def _substitute_env_vars(self, value: Any) -> Any:
        """
        Recursively substitute environment variables in configuration values.
        
        Args:
            value: Configuration value (string, dict, list, etc.)
            
        Returns:
            Value with environment variables substituted
        """
        if isinstance(value, str):
            return self._substitute_string(value)
        elif isinstance(value, dict):
            return {k: self._substitute_env_vars(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._substitute_env_vars(item) for item in value]
        else:
            return value
    
    def _substitute_string(self, text: str) -> str:
        """
        Substitute environment variables in a string.
        
        Format: ${VAR_NAME:default_value} or ${VAR_NAME}
        
        Args:
            text: String that may contain environment variable references
            
        Returns:
            String with environment variables substituted
        """
        # Pattern to match ${VAR_NAME:default} or ${VAR_NAME}
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
        
        def replace_var(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ""
            
            # Get value from environment
            env_value = os.getenv(var_name)
            
            if env_value is not None:
                logger.debug(f"Substituted {var_name} from environment")
                return env_value
            elif default_value:
                logger.debug(f"Using default value for {var_name}")
                return default_value
            else:
                logger.warning(f"Environment variable {var_name} not found and no default provided")
                return f"${{{var_name}}}"
        
        return re.sub(pattern, replace_var, text)
    
    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load configuration from YAML file with environment variable substitution.
        
        Args:
            force_reload: Force reload from file instead of using cache
            
        Returns:
            Configuration dictionary
        """
        if self._config_cache is not None and not force_reload:
            return self._config_cache
        
        try:
            logger.info(f"Loading configuration from: {self.config_path}")
            
            if not os.path.exists(self.config_path):
                logger.warning(f"Config file not found: {self.config_path}")
                return self._get_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                raw_config = yaml.safe_load(file)
            
            if raw_config is None:
                logger.warning("Config file is empty or invalid")
                return self._get_default_config()
            
            # Substitute environment variables
            config = self._substitute_env_vars(raw_config)
            
            # Cache the result
            self._config_cache = config
            
            logger.info("Configuration loaded successfully")
            return config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when file loading fails."""
        logger.warning("Using default configuration")
        return {
            'apis': {
                'bible_api': 'https://api.scripture.api.bible/v1',
                'frontend_url': 'http://localhost:3000'
            },
            'keys': {
                'bible_api_key': os.getenv('BIBLE_API_KEY', ''),
                'jwt_secret': os.getenv('JWT_SECRET', ''),
                'encryption_key': os.getenv('ENCRYPTION_KEY', '')
            },
            'database': {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', '5432')),
                'name': os.getenv('DB_NAME', 'bible_study_finder'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', ''),
                'url': os.getenv('DATABASE_URL', '')
            },
            'logging': {
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'file_output': os.getenv('LOG_FILE_OUTPUT', 'true').lower() == 'true',
                'console_output': os.getenv('LOG_CONSOLE_OUTPUT', 'true').lower() == 'true',
                'log_file': os.getenv('LOG_FILE', 'logs/bible_study_backend.log')
            },
            'server': {
                'host': os.getenv('SERVER_HOST', '0.0.0.0'),
                'port': int(os.getenv('SERVER_PORT', '8000')),
                'debug': os.getenv('DEBUG', 'false').lower() == 'true',
                'environment': os.getenv('ENVIRONMENT', 'development')
            },
            'cors': {
                'allowed_origins': os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8080').split(','),
                'allowed_methods': os.getenv('CORS_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(','),
                'allowed_headers': os.getenv('CORS_HEADERS', '*').split(',')
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'apis.bible_api')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        config = self.load_config()
        
        # Navigate through nested keys
        keys = key.split('.')
        value = config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            logger.debug(f"Configuration key '{key}' not found, using default")
            return default
    
    def validate_required_keys(self, required_keys: list) -> bool:
        """
        Validate that required configuration keys are present and not empty.
        
        Args:
            required_keys: List of required keys (e.g., ['keys.bible_api_key'])
            
        Returns:
            True if all required keys are present and not empty
        """
        missing_keys = []
        
        for key in required_keys:
            value = self.get(key)
            if not value or (isinstance(value, str) and value.strip() == ''):
                missing_keys.append(key)
        
        if missing_keys:
            logger.error(f"Missing required configuration keys: {missing_keys}")
            return False
        
        logger.info("All required configuration keys are present")
        return True

# Global config instance
_config_loader = None

def get_config_loader() -> ConfigLoader:
    """Get the global configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader

def load_config() -> Dict[str, Any]:
    """Load configuration with environment variable substitution."""
    return get_config_loader().load_config()

def get_config_value(key: str, default: Any = None) -> Any:
    """Get a configuration value using dot notation."""
    return get_config_loader().get(key, default)

# Example usage and testing
if __name__ == "__main__":
    # Test the configuration loader
    config_loader = ConfigLoader()
    config = config_loader.load_config()
    
    print("Configuration loaded:")
    print(f"Bible API URL: {config_loader.get('apis.bible_api')}")
    print(f"Bible API Key: {config_loader.get('keys.bible_api_key', 'NOT_SET')[:10]}...")
    print(f"Debug Mode: {config_loader.get('server.debug')}")
    print(f"Log Level: {config_loader.get('logging.level')}")
    
    # Validate required keys
    required_keys = ['keys.bible_api_key']
    is_valid = config_loader.validate_required_keys(required_keys)
    print(f"Configuration valid: {is_valid}")

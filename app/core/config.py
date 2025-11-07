"""
Configuration management with validation and persistence
"""
import json
import os
import logging
from typing import Dict, List, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class Config:
    """Application configuration manager with validation"""
    
    DEFAULT_CONFIG = {
        "SPOTIFY_CLIENT_ID": "",
        "SPOTIFY_CLIENT_SECRET": "",
        "SPOTIFY_REDIRECT_URI": "http://localhost:5000/callback",
        "SPOTIFY_SCOPE": "user-read-currently-playing",
        "WLED_IPS": [],
        "REFRESH_INTERVAL": 30,
        "CACHE_DURATION": 5,  # Cache API responses for 5 seconds
        "MAX_RETRIES": 3,
        "RETRY_DELAY": 2,
    }
    
    def __init__(self, config_path: str = None):
        # Allow config path to be set via environment variable (for Docker/HA)
        if config_path is None:
            config_path = os.environ.get('CONFIG_PATH', 'config.json')
        
        self.config_path = Path(config_path)
        self.data = self.DEFAULT_CONFIG.copy()
        self.is_running = False
        self.load()
    
    def load(self) -> None:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    file_data = json.load(f)
                    self.data.update(file_data)
                logger.info(f"Configuration loaded from {self.config_path}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in config file: {e}")
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        else:
            logger.info("Config file not found, using defaults")
    
    def save(self) -> bool:
        """Save configuration to file"""
        try:
            # Don't save runtime state
            save_data = {k: v for k, v in self.data.items() 
                        if k not in ['IS_RUNNING']}
            
            with open(self.config_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate configuration
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check Spotify credentials
        if not self.data.get("SPOTIFY_CLIENT_ID"):
            errors.append("Spotify Client ID is required")
        if not self.data.get("SPOTIFY_CLIENT_SECRET"):
            errors.append("Spotify Client Secret is required")
        
        # Check WLED IPs
        if not self.data.get("WLED_IPS"):
            errors.append("At least one WLED IP address is required")
        
        # Validate refresh interval
        refresh = self.data.get("REFRESH_INTERVAL", 0)
        if not isinstance(refresh, int) or refresh < 1:
            errors.append("Refresh interval must be at least 1 second")
        
        return (len(errors) == 0, errors)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.data[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self.data.update(updates)
    
    def __getitem__(self, key: str) -> Any:
        return self.data[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value


# Global config instance
config = Config()

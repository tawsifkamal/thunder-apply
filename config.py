"""Configuration management for Thunder Apply automation tool."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class WebDriverSettings:
    """WebDriver configuration settings."""
    headless: bool = True
    implicit_wait: int = 5
    page_load_timeout: int = 30
    window_width: int = 1920
    window_height: int = 1080


@dataclass
class AutomationSettings:
    """Automation behavior settings."""
    max_retries: int = 3
    retry_delay: int = 2
    form_fill_delay: float = 0.5
    click_delay: float = 1.0
    page_load_wait: int = 2


@dataclass
class LoggingSettings:
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None


class Config:
    """Main configuration class for Thunder Apply."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration from file or defaults."""
        self.config_file = config_file or "config.json"
        self.webdriver = WebDriverSettings()
        self.automation = AutomationSettings()
        self.logging = LoggingSettings()
        
        # Load configuration if file exists
        if Path(self.config_file).exists():
            self.load_from_file()
    
    def load_from_file(self) -> None:
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Update settings from file
            if 'webdriver' in config_data:
                self.webdriver = WebDriverSettings(**config_data['webdriver'])
            
            if 'automation' in config_data:
                self.automation = AutomationSettings(**config_data['automation'])
            
            if 'logging' in config_data:
                self.logging = LoggingSettings(**config_data['logging'])
                
            logging.info(f"Configuration loaded from {self.config_file}")
            
        except Exception as e:
            logging.warning(f"Failed to load configuration from {self.config_file}: {e}")
            logging.info("Using default configuration")
    
    def save_to_file(self) -> None:
        """Save current configuration to JSON file."""
        try:
            config_data = {
                'webdriver': asdict(self.webdriver),
                'automation': asdict(self.automation),
                'logging': asdict(self.logging)
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logging.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            logging.error(f"Failed to save configuration to {self.config_file}: {e}")
    
    def setup_logging(self) -> None:
        """Configure logging based on settings."""
        logging.basicConfig(
            level=getattr(logging, self.logging.level.upper()),
            format=self.logging.format,
            filename=self.logging.file_path
        )
    
    def get_profile_data(self, profile_file: str = "profile.json") -> Dict[str, Any]:
        """Load user profile data from JSON file."""
        try:
            with open(profile_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load profile data from {profile_file}: {e}")
            return {}


# Global configuration instance
config = Config()


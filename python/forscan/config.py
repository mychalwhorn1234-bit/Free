"""
Configuration management for FORScan Python tools.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class AdapterConfig:
    """Adapter configuration."""
    type: str = "ELM327"
    port: str = "COM1"
    baudrate: int = 38400
    timeout: float = 2.0


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None


@dataclass
class FORScanConfig:
    """FORScan integration configuration."""
    executable_path: Optional[str] = None
    data_dir: str = "./data"
    config_dir: str = "./config"
    auto_connect: bool = False


class Config:
    """
    Configuration manager for FORScan Python tools.
    
    Handles loading, saving, and accessing configuration settings
    from YAML files and environment variables.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config_file = config_file or self._find_config_file()
        self.adapter = AdapterConfig()
        self.logging = LoggingConfig()
        self.forscan = FORScanConfig()
        
        # Load configuration
        self.load()
        self._apply_env_overrides()
    
    def _find_config_file(self) -> str:
        """Find configuration file in standard locations."""
        possible_paths = [
            "forscan_config.yaml",
            "config/forscan_config.yaml",
            os.path.expanduser("~/.forscan/config.yaml"),
            "/etc/forscan/config.yaml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return default path if none found
        return "forscan_config.yaml"
    
    def load(self) -> None:
        """Load configuration from file."""
        if not os.path.exists(self.config_file):
            logger.info(f"Config file {self.config_file} not found, using defaults")
            return
        
        try:
            with open(self.config_file, 'r') as f:
                data = yaml.safe_load(f)
            
            if not data:
                return
            
            # Load adapter config
            if 'adapter' in data:
                adapter_data = data['adapter']
                self.adapter = AdapterConfig(**adapter_data)
            
            # Load logging config
            if 'logging' in data:
                logging_data = data['logging']
                self.logging = LoggingConfig(**logging_data)
            
            # Load FORScan config
            if 'forscan' in data:
                forscan_data = data['forscan']
                self.forscan = FORScanConfig(**forscan_data)
            
            logger.info(f"Configuration loaded from {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            # Ensure config directory exists
            config_dir = os.path.dirname(self.config_file)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
            
            data = {
                'adapter': asdict(self.adapter),
                'logging': asdict(self.logging),
                'forscan': asdict(self.forscan)
            }
            
            with open(self.config_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        # Adapter overrides
        if os.getenv('FORSCAN_ADAPTER_TYPE'):
            self.adapter.type = os.getenv('FORSCAN_ADAPTER_TYPE')
        
        if os.getenv('FORSCAN_ADAPTER_PORT'):
            self.adapter.port = os.getenv('FORSCAN_ADAPTER_PORT')
        
        if os.getenv('FORSCAN_ADAPTER_BAUDRATE'):
            try:
                self.adapter.baudrate = int(os.getenv('FORSCAN_ADAPTER_BAUDRATE'))
            except ValueError:
                logger.warning("Invalid FORSCAN_ADAPTER_BAUDRATE value")
        
        # Logging overrides
        if os.getenv('FORSCAN_LOG_LEVEL'):
            self.logging.level = os.getenv('FORSCAN_LOG_LEVEL')
        
        if os.getenv('FORSCAN_LOG_FILE'):
            self.logging.file = os.getenv('FORSCAN_LOG_FILE')
        
        # FORScan overrides
        if os.getenv('FORSCAN_EXECUTABLE_PATH'):
            self.forscan.executable_path = os.getenv('FORSCAN_EXECUTABLE_PATH')
        
        if os.getenv('FORSCAN_DATA_DIR'):
            self.forscan.data_dir = os.getenv('FORSCAN_DATA_DIR')
        
        if os.getenv('FORSCAN_CONFIG_DIR'):
            self.forscan.config_dir = os.getenv('FORSCAN_CONFIG_DIR')
    
    def get_adapter_config(self) -> Dict[str, Any]:
        """Get adapter configuration as dictionary."""
        return asdict(self.adapter)
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration as dictionary."""
        return asdict(self.logging)
    
    def get_forscan_config(self) -> Dict[str, Any]:
        """Get FORScan configuration as dictionary."""
        return asdict(self.forscan)
    
    def update_adapter_config(self, **kwargs) -> None:
        """Update adapter configuration."""
        for key, value in kwargs.items():
            if hasattr(self.adapter, key):
                setattr(self.adapter, key, value)
    
    def update_logging_config(self, **kwargs) -> None:
        """Update logging configuration."""
        for key, value in kwargs.items():
            if hasattr(self.logging, key):
                setattr(self.logging, key, value)
    
    def update_forscan_config(self, **kwargs) -> None:
        """Update FORScan configuration."""
        for key, value in kwargs.items():
            if hasattr(self.forscan, key):
                setattr(self.forscan, key, value)
    
    def setup_logging(self) -> None:
        """Setup logging based on configuration."""
        log_level = getattr(logging, self.logging.level.upper(), logging.INFO)
        
        # Configure logging
        logging_config = {
            'level': log_level,
            'format': self.logging.format
        }
        
        if self.logging.file:
            # Ensure log directory exists
            log_dir = os.path.dirname(self.logging.file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            logging_config['filename'] = self.logging.file
        
        logging.basicConfig(**logging_config)
        logger.info("Logging configured")
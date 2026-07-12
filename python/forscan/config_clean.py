"""
Configuration management for FORScan Python tools.
"""

import os
import yaml
import logging
from dataclasses import dataclass, asdict
from typing import Any, Dict, Union, Optional


logger = logging.getLogger(__name__)

# Type alias for configuration data
ConfigData = Dict[str, Any]


@dataclass
class AdapterConfig:
    """Adapter configuration."""
    type: str = 'ELM327'
    port: str = 'COM1'
    baudrate: int = 38400
    timeout: float = 2.0


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = 'INFO'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file: Optional[str] = None


@dataclass
class FORScanConfig:
    """FORScan application configuration."""
    executable_path: Optional[str] = None
    data_dir: str = './data'
    config_dir: str = './config'
    auto_connect: bool = False


class Config:
    """Configuration manager."""
    
    def __init__(self, config_file: str = 'forscan_config.yaml'):
        """Initialize configuration with defaults."""
        self.config_file = config_file
        self.adapter = AdapterConfig()
        self.logging = LoggingConfig()
        self.forscan = FORScanConfig()
        
        # Load configuration if file exists
        self.load()
        
        # Apply environment variable overrides
        self._apply_env_overrides()
    
    def load(self) -> None:
        """Load configuration from file."""
        if not os.path.exists(self.config_file):
            logger.info(
                f"Config file {self.config_file} not found, using defaults"
            )
            return
        
        try:
            data = self._load_yaml_data()
            if not data:
                return
            
            self._load_adapter_config(data)
            self._load_logging_config(data)
            self._load_forscan_config(data)
            
            logger.info(f"Configuration loaded from {self.config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    def _load_yaml_data(self) -> ConfigData:
        """Load and validate YAML data from config file."""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            # Load raw YAML data as Any type first
            raw_data: Any = yaml.safe_load(f)
            # Ensure we have a valid nested dictionary structure
            if isinstance(raw_data, dict):
                return raw_data
            return {}
    
    def _load_adapter_config(self, data: ConfigData) -> None:
        """Load adapter configuration from data dict."""
        if 'adapter' in data:
            adapter_data = data['adapter']
            # Cast to exact types with explicit str() calls
            type_str = str(adapter_data.get('type') or 'ELM327')
            port_str = str(adapter_data.get('port') or 'COM1')
            baudrate_int = self._safe_int(
                adapter_data.get('baudrate'), 38400
            )
            timeout_float = self._safe_float(
                adapter_data.get('timeout'), 2.0
            )
            
            # Create adapter with fully validated types
            self.adapter = AdapterConfig(
                type=type_str,
                port=port_str,
                baudrate=baudrate_int,
                timeout=timeout_float
            )
    
    def _load_logging_config(self, data: ConfigData) -> None:
        """Load logging configuration from data dict."""
        if 'logging' in data:
            logging_data = data['logging']
            # Ensure proper string types for required fields
            default_format = (
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            level_val = str(logging_data.get('level') or 'INFO')
            format_val = str(logging_data.get('format') or default_format)
            file_val = (
                str(logging_data['file'])
                if logging_data.get('file') else None
            )
            
            # Create logging config with validated types
            self.logging = LoggingConfig(
                level=level_val,
                format=format_val,
                file=file_val
            )
    
    def _load_forscan_config(self, data: ConfigData) -> None:
        """Load FORScan configuration from data dict."""
        if 'forscan' in data:
            forscan_data = data['forscan']
            # Type cast all values with appropriate defaults
            executable_path_val = (
                str(forscan_data['executable_path'])
                if forscan_data.get('executable_path') else None
            )
            data_dir_val = str(
                forscan_data.get('data_dir') or './data'
            )
            config_dir_val = str(
                forscan_data.get('config_dir') or './config'
            )
            auto_connect_val = self._safe_bool(
                forscan_data.get('auto_connect'), False
            )
            
            # Create FORScan config with validated types
            self.forscan = FORScanConfig(
                executable_path=executable_path_val,
                data_dir=data_dir_val,
                config_dir=config_dir_val,
                auto_connect=auto_connect_val
            )
    
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
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        # Adapter overrides
        adapter_type = os.getenv('FORSCAN_ADAPTER_TYPE')
        if adapter_type:
            self.adapter.type = adapter_type
        
        adapter_port = os.getenv('FORSCAN_ADAPTER_PORT')
        if adapter_port:
            self.adapter.port = adapter_port
        
        adapter_baudrate = os.getenv('FORSCAN_ADAPTER_BAUDRATE')
        if adapter_baudrate:
            try:
                self.adapter.baudrate = int(adapter_baudrate)
            except ValueError:
                logger.warning(
                    f"Invalid FORSCAN_ADAPTER_BAUDRATE: {adapter_baudrate}"
                )
        
        # Logging overrides
        log_level = os.getenv('FORSCAN_LOG_LEVEL')
        if log_level:
            self.logging.level = log_level
        
        log_file = os.getenv('FORSCAN_LOG_FILE')
        if log_file:
            self.logging.file = log_file
        
        # FORScan overrides
        forscan_exe = os.getenv('FORSCAN_EXECUTABLE_PATH')
        if forscan_exe:
            self.forscan.executable_path = forscan_exe
        
        data_dir = os.getenv('FORSCAN_DATA_DIR')
        if data_dir:
            self.forscan.data_dir = data_dir
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Validate adapter configuration
        if not self.adapter.type:
            errors.append("Adapter type cannot be empty")
        
        if not self.adapter.port:
            errors.append("Adapter port cannot be empty")
        
        if self.adapter.baudrate <= 0:
            errors.append("Adapter baudrate must be positive")
        
        if self.adapter.timeout <= 0:
            errors.append("Adapter timeout must be positive")
        
        # Validate logging configuration
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.logging.level.upper() not in valid_levels:
            errors.append(
                f"Invalid log level: {self.logging.level}. "
                f"Valid levels: {', '.join(valid_levels)}"
            )
        
        # Validate FORScan configuration
        if self.forscan.executable_path:
            if not os.path.exists(self.forscan.executable_path):
                errors.append(
                    f"FORScan executable not found: "
                    f"{self.forscan.executable_path}"
                )
        
        return errors
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return {
            'adapter': asdict(self.adapter),
            'logging': asdict(self.logging),
            'forscan': asdict(self.forscan)
        }
    
    def _safe_int(
        self, value: Union[str, int, float, bool, None],
        default: int
    ) -> int:
        """Safely convert value to int with fallback."""
        try:
            if value is None:
                return default
            return int(float(value))  # Handle string numbers
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid int value {value}, using default {default}"
            )
            return default
    
    def _safe_float(
        self, value: Union[str, int, float, bool, None],
        default: float
    ) -> float:
        """Safely convert value to float with fallback."""
        try:
            if value is None:
                return default
            return float(value)
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid float value {value}, using default {default}"
            )
            return default
    
    def _safe_bool(
        self, value: Union[str, int, float, bool, None],
        default: bool
    ) -> bool:
        """Safely convert value to bool with fallback."""
        try:
            if value is None:
                return default
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid bool value {value}, using default {default}"
            )
            return default
    
    def setup_logging(self) -> None:
        """Setup logging based on configuration."""
        log_level = getattr(logging, self.logging.level.upper(), logging.INFO)
        
        # Build configuration with explicit types
        config_args: Dict[str, Union[str, int]] = {
            'level': log_level,
            'format': self.logging.format
        }
        
        if self.logging.file:
            # Ensure log directory exists
            log_dir = os.path.dirname(self.logging.file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            config_args['filename'] = self.logging.file
        
        # Type-safe logging configuration
        logging.basicConfig(
            level=config_args['level'],
            format=str(config_args['format']),
            filename=(
                str(config_args.get('filename'))
                if 'filename' in config_args else None
            )
        )
        logger.info("Logging configured")
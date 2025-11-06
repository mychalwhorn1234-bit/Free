"""
Configuration management for FORScan Python tools.
"""

import os
import yaml
import logging
from dataclasses import dataclass, asdict, fields


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
    file: str | None = None


@dataclass
class FORScanConfig:
    """FORScan integration configuration."""
    executable_path: str | None = None
    data_dir: str = "./data"
    config_dir: str = "./config"
    auto_connect: bool = False


class Config:
    """
    Configuration manager for FORScan Python tools.
    
    Handles loading, saving, and accessing configuration settings
    from YAML files and environment variables.
    """
    
    def __init__(self, config_file: str | None = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config_file: str = config_file or self._find_config_file()
        self.adapter: AdapterConfig = AdapterConfig()
        self.logging: LoggingConfig = LoggingConfig()
        self.forscan: FORScanConfig = FORScanConfig()
        
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
            logger.info(
                f"Config file {self.config_file} not found, using defaults"
            )
            return
        
        try:
            with open(self.config_file, 'r') as f:
                raw_data = yaml.safe_load(f)
                # Type cast YAML data safely
                data: dict[str, dict[str, str | int | float | bool | None]] = (
                    raw_data if isinstance(raw_data, dict) else {}
                )
            
            if not data:
                return
            
            # Load adapter config with safe type conversion
            if 'adapter' in data:
                adapter_data = data['adapter']
                # Use safe conversion methods to avoid type errors
                adapter_config = {
                    'type': str(adapter_data.get('type') or 'ELM327'),
                    'port': str(adapter_data.get('port') or 'COM1'),
                    'baudrate': self._safe_int(
                        adapter_data.get('baudrate'), 38400
                    ),
                    'timeout': self._safe_float(
                        adapter_data.get('timeout'), 2.0
                    )
                }
                self.adapter = AdapterConfig(**adapter_config)
            
            # Load logging config with safe conversion
            if 'logging' in data:
                logging_data = data['logging']
                # Ensure proper string types for required fields
                default_format = (
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                logging_config = {
                    'level': str(logging_data.get('level') or 'INFO'),
                    'format': str(
                        logging_data.get('format') or default_format
                    ),
                    'file': (
                        str(logging_data['file'])
                        if logging_data.get('file') else None
                    )
                }
                self.logging = LoggingConfig(**logging_config)
            
            # Load FORScan config with safe conversion
            if 'forscan' in data:
                forscan_data = data['forscan']
                # Ensure proper types with safe conversion
                forscan_config = {
                    'executable_path': (
                        str(forscan_data['executable_path'])
                        if forscan_data.get('executable_path') else None
                    ),
                    'data_dir': str(
                        forscan_data.get('data_dir') or './data'
                    ),
                    'config_dir': str(
                        forscan_data.get('config_dir') or './config'
                    ),
                    'auto_connect': self._safe_bool(
                        forscan_data.get('auto_connect'), False
                    )
                }
                self.forscan = FORScanConfig(**forscan_config)
            
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
        adapter_type = os.getenv('FORSCAN_ADAPTER_TYPE')
        if adapter_type:
            self.adapter.type = adapter_type
        
        adapter_port = os.getenv('FORSCAN_ADAPTER_PORT')
        if adapter_port:
            self.adapter.port = adapter_port
        
        if os.getenv('FORSCAN_ADAPTER_BAUDRATE'):
            try:
                baudrate_env = os.getenv('FORSCAN_ADAPTER_BAUDRATE')
                if baudrate_env:
                    self.adapter.baudrate = int(baudrate_env)
            except ValueError:
                logger.warning("Invalid FORSCAN_ADAPTER_BAUDRATE value")
        
        # Logging overrides
        log_level_env = os.getenv('FORSCAN_LOG_LEVEL')
        if log_level_env:
            self.logging.level = log_level_env
        
        log_file_env = os.getenv('FORSCAN_LOG_FILE')
        if log_file_env:
            self.logging.file = log_file_env
        
        # FORScan overrides
        exec_path_env = os.getenv('FORSCAN_EXECUTABLE_PATH')
        if exec_path_env:
            self.forscan.executable_path = exec_path_env
        
        data_dir_env = os.getenv('FORSCAN_DATA_DIR')
        if data_dir_env:
            self.forscan.data_dir = data_dir_env
        
        config_dir_env = os.getenv('FORSCAN_CONFIG_DIR')
        if config_dir_env:
            self.forscan.config_dir = config_dir_env
    
    def _update_config_section(
        self,
        section: AdapterConfig | LoggingConfig | FORScanConfig,
        values: dict[str, str | int | float | bool | None],
        section_name: str
    ) -> None:
        """Update dataclass section with filtered values and warn on extras."""
        allowed_fields = {field.name for field in fields(section)}
        filtered_values = {
            key: values[key] for key in values if key in allowed_fields
        }
        
        for key, value in filtered_values.items():
            setattr(section, key, value)
        
        unknown_keys = set(values) - allowed_fields
        if unknown_keys:
            logger.warning(
                "Ignoring unknown %s configuration keys: %s",
                section_name,
                ", ".join(sorted(unknown_keys))
            )
    
    def get_adapter_config(self) -> dict[str, str | int | float | bool]:
        """Get adapter configuration as dictionary."""
        return asdict(self.adapter)
    
    def get_logging_config(self) -> dict[str, str | None]:
        """Get logging configuration as dictionary."""
        return asdict(self.logging)
    
    def get_forscan_config(self) -> dict[str, str | bool | None]:
        """Get FORScan configuration as dictionary."""
        return asdict(self.forscan)
    
    def update_adapter_config(
        self, **kwargs: str | int | float | bool
    ) -> None:
        """Update adapter configuration."""
        for key, value in kwargs.items():
            if hasattr(self.adapter, key):
                setattr(self.adapter, key, value)
    
    def update_logging_config(self, **kwargs: str | None) -> None:
        """Update logging configuration."""
        for key, value in kwargs.items():
            if hasattr(self.logging, key):
                setattr(self.logging, key, value)
    
    def update_forscan_config(
        self, **kwargs: str | bool | None
    ) -> None:
        """Update FORScan configuration."""
        for key, value in kwargs.items():
            if hasattr(self.forscan, key):
                setattr(self.forscan, key, value)
    
    def _safe_int(
        self, value: str | int | float | bool | None, 
        default: int
    ) -> int:
        """Safely convert value to int with fallback."""
        try:
            if value is None:
                return default
            return int(value)
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid int value {value}, using default {default}"
            )
            return default
    
    def _safe_float(
        self, value: str | int | float | bool | None,
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
        self, value: str | int | float | bool | None,
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
        config_args: dict[str, str | int] = {
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
            filename=str(config_args.get('filename')) if 'filename' in config_args else None
        )
        logger.info("Logging configured")
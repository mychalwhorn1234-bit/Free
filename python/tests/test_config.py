"""
Tests for configuration management module.
"""

import yaml
from forscan.config import (
    Config,
    AdapterConfig,
    LoggingConfig,
    FORScanConfig,
)


class TestAdapterConfig:
    """Tests for AdapterConfig dataclass."""

    def test_default_values(self):
        """Test default adapter configuration values."""
        config = AdapterConfig()
        assert config.type == "ELM327"
        assert config.port == "COM1"
        assert config.baudrate == 38400
        assert config.timeout == 2.0

    def test_custom_values(self):
        """Test custom adapter configuration values."""
        config = AdapterConfig(type="J2534", port="COM3", baudrate=115200, timeout=5.0)
        assert config.type == "J2534"
        assert config.port == "COM3"
        assert config.baudrate == 115200
        assert config.timeout == 5.0


class TestLoggingConfig:
    """Tests for LoggingConfig dataclass."""

    def test_default_values(self):
        """Test default logging configuration values."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert config.file is None

    def test_custom_values(self):
        """Test custom logging configuration values."""
        config = LoggingConfig(level="DEBUG", format="%(message)s", file="test.log")
        assert config.level == "DEBUG"
        assert config.format == "%(message)s"
        assert config.file == "test.log"


class TestFORScanConfig:
    """Tests for FORScanConfig dataclass."""

    def test_default_values(self):
        """Test default FORScan configuration values."""
        config = FORScanConfig()
        assert config.executable_path is None
        assert config.data_dir == "./data"
        assert config.config_dir == "./config"
        assert config.auto_connect is False

    def test_custom_values(self):
        """Test custom FORScan configuration values."""
        config = FORScanConfig(
            executable_path="/path/to/forscan.exe",
            data_dir="/custom/data",
            config_dir="/custom/config",
            auto_connect=True,
        )
        assert config.executable_path == "/path/to/forscan.exe"
        assert config.data_dir == "/custom/data"
        assert config.config_dir == "/custom/config"
        assert config.auto_connect is True


class TestConfig:
    """Tests for Config manager class."""

    def test_init_without_config_file(self, tmp_path, monkeypatch):
        """Test Config initialization without a config file."""
        # Change to temp directory where config file doesn't exist
        monkeypatch.chdir(tmp_path)
        config = Config()
        assert config.adapter.type == "ELM327"
        assert config.logging.level == "INFO"
        assert config.forscan.data_dir == "./data"

    def test_load_from_yaml(self, tmp_path):
        """Test loading configuration from YAML file."""
        config_file = tmp_path / "test_config.yaml"
        config_data = {
            "adapter": {"type": "STN", "port": "COM2", "baudrate": 115200},
            "logging": {"level": "DEBUG", "file": "test.log"},
            "forscan": {"data_dir": "/custom/data", "auto_connect": True},
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = Config(str(config_file))
        assert config.adapter.type == "STN"
        assert config.adapter.port == "COM2"
        assert config.adapter.baudrate == 115200
        assert config.logging.level == "DEBUG"
        assert config.logging.file == "test.log"
        assert config.forscan.data_dir == "/custom/data"
        assert config.forscan.auto_connect is True

    def test_save_to_yaml(self, tmp_path):
        """Test saving configuration to YAML file."""
        config_file = tmp_path / "test_save.yaml"
        config = Config(str(config_file))
        config.adapter.type = "J2534"
        config.adapter.baudrate = 500000
        config.save()

        assert config_file.exists()
        with open(config_file, "r") as f:
            data = yaml.safe_load(f)
        assert data["adapter"]["type"] == "J2534"
        assert data["adapter"]["baudrate"] == 500000

    def test_env_overrides(self, tmp_path, monkeypatch):
        """Test environment variable overrides."""
        monkeypatch.setenv("FORSCAN_ADAPTER_TYPE", "J2534")
        monkeypatch.setenv("FORSCAN_ADAPTER_PORT", "COM5")
        monkeypatch.setenv("FORSCAN_ADAPTER_BAUDRATE", "115200")
        monkeypatch.setenv("FORSCAN_LOG_LEVEL", "DEBUG")

        monkeypatch.chdir(tmp_path)
        config = Config()
        assert config.adapter.type == "J2534"
        assert config.adapter.port == "COM5"
        assert config.adapter.baudrate == 115200
        assert config.logging.level == "DEBUG"

    def test_safe_int_conversion(self, tmp_path):
        """Test safe integer conversion."""
        config = Config()
        assert config._safe_int("123", 0) == 123
        assert config._safe_int(456, 0) == 456
        assert config._safe_int("invalid", 99) == 99
        assert config._safe_int(None, 88) == 88

    def test_safe_float_conversion(self, tmp_path):
        """Test safe float conversion."""
        config = Config()
        assert config._safe_float("1.5", 0.0) == 1.5
        assert config._safe_float(2.5, 0.0) == 2.5
        assert config._safe_float("invalid", 9.9) == 9.9
        assert config._safe_float(None, 8.8) == 8.8

    def test_safe_bool_conversion(self, tmp_path):
        """Test safe boolean conversion."""
        config = Config()
        assert config._safe_bool(True, False) is True
        assert config._safe_bool("true", False) is True
        assert config._safe_bool("1", False) is True
        assert config._safe_bool("yes", False) is True
        assert config._safe_bool("on", False) is True
        assert config._safe_bool("false", True) is False
        # Note: Invalid strings return False (not in the accepted list)
        assert config._safe_bool("invalid", True) is False
        assert config._safe_bool(None, False) is False
        assert config._safe_bool(None, True) is True  # None returns default

    def test_update_adapter_config(self, tmp_path, monkeypatch):
        """Test updating adapter configuration."""
        monkeypatch.chdir(tmp_path)
        config = Config()
        config.update_adapter_config(type="STN", baudrate=500000)
        assert config.adapter.type == "STN"
        assert config.adapter.baudrate == 500000

    def test_update_logging_config(self, tmp_path, monkeypatch):
        """Test updating logging configuration."""
        monkeypatch.chdir(tmp_path)
        config = Config()
        config.update_logging_config(level="ERROR", file="error.log")
        assert config.logging.level == "ERROR"
        assert config.logging.file == "error.log"

    def test_update_forscan_config(self, tmp_path, monkeypatch):
        """Test updating FORScan configuration."""
        monkeypatch.chdir(tmp_path)
        config = Config()
        config.update_forscan_config(data_dir="/new/data", auto_connect=True)
        assert config.forscan.data_dir == "/new/data"
        assert config.forscan.auto_connect is True

    def test_get_adapter_config(self, tmp_path, monkeypatch):
        """Test getting adapter configuration as dictionary."""
        monkeypatch.chdir(tmp_path)
        config = Config()
        adapter_dict = config.get_adapter_config()
        assert isinstance(adapter_dict, dict)
        assert adapter_dict["type"] == "ELM327"
        assert adapter_dict["port"] == "COM1"

    def test_get_logging_config(self, tmp_path, monkeypatch):
        """Test getting logging configuration as dictionary."""
        monkeypatch.chdir(tmp_path)
        config = Config()
        logging_dict = config.get_logging_config()
        assert isinstance(logging_dict, dict)
        assert logging_dict["level"] == "INFO"

    def test_get_forscan_config(self, tmp_path, monkeypatch):
        """Test getting FORScan configuration as dictionary."""
        monkeypatch.chdir(tmp_path)
        config = Config()
        forscan_dict = config.get_forscan_config()
        assert isinstance(forscan_dict, dict)
        assert forscan_dict["data_dir"] == "./data"

"""
Tests for adapter implementations.
"""

import pytest
from unittest.mock import Mock, patch
from forscan.adapters import (
    BaseAdapter, ELM327Adapter, J2534Adapter, STNAdapter
)


class TestBaseAdapter:
    """Test base adapter functionality."""
    
    def test_base_adapter_is_abstract(self) -> None:
        """Test that BaseAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            _ = BaseAdapter("COM1")


class TestELM327Adapter:
    """Test ELM327 adapter functionality."""
    
    def test_init(self):
        """Test ELM327 adapter initialization."""
        adapter = ELM327Adapter("COM1", 38400)
        
        assert adapter.port == "COM1"
        assert adapter.baudrate == 38400
        assert adapter.connection is None
        assert adapter.connected is False
        assert adapter.protocol == "AUTO"
    
    def test_init_default_baudrate(self):
        """Test ELM327 adapter with default baudrate."""
        adapter = ELM327Adapter("COM2")
        
        assert adapter.port == "COM2"
        assert adapter.baudrate == 38400
    
    @patch('forscan.adapters.serial.Serial')
    def test_connect_success(self, mock_serial: Mock) -> None:
        """Test successful ELM327 connection."""
        # Mock serial connection
        mock_connection = Mock()
        mock_serial.return_value = mock_connection
        
        adapter = ELM327Adapter("COM1")
        
        # Mock the initialization commands
        with patch.object(adapter, '_initialize_elm327'):
            result = adapter.connect()
        
        assert result is True
        assert adapter.connected is True
        assert adapter.connection == mock_connection
    
    @patch('forscan.adapters.serial.Serial')
    def test_connect_failure(self, mock_serial):
        """Test ELM327 connection failure."""
        # Mock serial connection failure
        mock_serial.side_effect = Exception("Port not found")
        
        adapter = ELM327Adapter("COM1")
        result = adapter.connect()
        
        assert result is False
        assert adapter.connected is False
    
    def test_disconnect(self):
        """Test ELM327 disconnection."""
        adapter = ELM327Adapter("COM1")
        
        # Mock connection
        mock_connection = Mock()
        mock_connection.is_open = True
        adapter.connection = mock_connection
        adapter.connected = True
        
        adapter.disconnect()
        
        mock_connection.close.assert_called_once()
        assert adapter.connected is False
    
    def test_send_command_not_connected(self):
        """Test sending command when not connected."""
        adapter = ELM327Adapter("COM1")
        
        with pytest.raises(ConnectionError):
            adapter.send_command("ATZ")
    
    def test_send_command_success(self):
        """Test successful command sending."""
        adapter = ELM327Adapter("COM1")
        
        # Mock connection
        mock_connection = Mock()
        mock_connection.read.side_effect = [b'O', b'K', b'\r', b'\r', b'>']
        adapter.connection = mock_connection
        adapter.connected = True
        
        result = adapter.send_command("ATZ")
        
        mock_connection.write.assert_called_once_with(b"ATZ\r")
        assert result == "OK"


class TestJ2534Adapter:
    """Test J2534 adapter functionality."""
    
    def test_init(self):
        """Test J2534 adapter initialization."""
        adapter = J2534Adapter("Test Device")
        
        assert adapter.device_name == "Test Device"
        assert adapter.device_id is None
        assert adapter.channel_id is None
        assert adapter.connected is False
    
    def test_connect_success(self):
        """Test successful J2534 connection."""
        adapter = J2534Adapter("Test Device")
        
        result = adapter.connect()
        
        # Placeholder implementation always succeeds
        assert result is True
        assert adapter.connected is True
        assert adapter.device_id == 1
        assert adapter.channel_id == 1
    
    def test_disconnect(self):
        """Test J2534 disconnection."""
        adapter = J2534Adapter("Test Device")
        adapter.connected = True
        adapter.device_id = 1
        adapter.channel_id = 1
        
        adapter.disconnect()
        
        assert adapter.connected is False
        assert adapter.device_id is None
        assert adapter.channel_id is None
    
    def test_send_command_not_connected(self):
        """Test sending command when not connected."""
        adapter = J2534Adapter("Test Device")
        
        with pytest.raises(ConnectionError):
            adapter.send_command("TEST")
    
    def test_send_command_success(self):
        """Test successful command sending."""
        adapter = J2534Adapter("Test Device")
        adapter.connected = True
        
        result = adapter.send_command("TEST")
        
        assert result == "OK"


class TestSTNAdapter:
    """Test STN adapter functionality."""
    
    def test_init(self):
        """Test STN adapter initialization."""
        adapter = STNAdapter("COM1", 115200)
        
        assert adapter.port == "COM1"
        assert adapter.baudrate == 115200
        assert adapter.connection is None
        assert adapter.connected is False
    
    def test_init_default_baudrate(self):
        """Test STN adapter with default baudrate."""
        adapter = STNAdapter("COM2")
        
        assert adapter.port == "COM2"
        assert adapter.baudrate == 115200
    
    @patch('forscan.adapters.serial.Serial')
    def test_connect_success(self, mock_serial):
        """Test successful STN connection."""
        # Mock serial connection
        mock_connection = Mock()
        mock_serial.return_value = mock_connection
        
        adapter = STNAdapter("COM1")
        
        # Mock the initialization commands
        with patch.object(adapter, '_initialize_stn'):
            result = adapter.connect()
        
        assert result is True
        assert adapter.connected is True
        assert adapter.connection == mock_connection
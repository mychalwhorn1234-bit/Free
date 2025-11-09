"""
Tests for FORScan core functionality.
"""

import pytest
from forscan.core import FORScanConnector, VehicleInfo


class TestFORScanConnector:
    """Test FORScan connector functionality."""
    
    def test_init_default(self):
        """Test connector initialization with defaults."""
        connector = FORScanConnector()
        
        assert connector.config == {}
        assert connector.connected is False
        assert connector.vehicle_info is None
    
    def test_init_with_config(self, sample_config):
        """Test connector initialization with configuration."""
        connector = FORScanConnector(sample_config)
        
        assert connector.config == sample_config
        assert connector.connected is False
    
    def test_connect_success(self):
        """Test successful connection."""
        connector = FORScanConnector()
        
        # Mock connection (placeholder implementation always returns True)
        result = connector.connect("ELM327", "COM1")
        
        assert result is True
        assert connector.connected is True
    
    def test_disconnect(self):
        """Test disconnection."""
        connector = FORScanConnector()
        connector.connected = True  # Simulate connected state
        
        connector.disconnect()
        
        assert connector.connected is False
    
    def test_get_vehicle_info_when_not_connected(self):
        """Test getting vehicle info when not connected."""
        connector = FORScanConnector()
        
        result = connector.get_vehicle_info()
        
        assert result is None
    
    def test_get_vehicle_info_when_connected(self):
        """Test getting vehicle info when connected."""
        connector = FORScanConnector()
        connector.connected = True
        
        result = connector.get_vehicle_info()
        
        assert result is not None
        assert isinstance(result, VehicleInfo)
        assert result.make == "Ford"
        assert result.model == "F-150"
        assert result.year == 2020
    
    def test_read_dtcs_when_not_connected(self):
        """Test reading DTCs when not connected."""
        connector = FORScanConnector()
        
        result = connector.read_dtcs()
        
        assert result == {}
    
    def test_read_dtcs_when_connected(self):
        """Test reading DTCs when connected."""
        connector = FORScanConnector()
        connector.connected = True
        
        result = connector.read_dtcs()
        
        assert "dtcs" in result
        assert "count" in result
        assert isinstance(result["dtcs"], list)
        assert result["count"] == len(result["dtcs"])
    
    def test_clear_dtcs_when_not_connected(self):
        """Test clearing DTCs when not connected."""
        connector = FORScanConnector()
        
        result = connector.clear_dtcs()
        
        assert result is False
    
    def test_clear_dtcs_when_connected(self):
        """Test clearing DTCs when connected."""
        connector = FORScanConnector()
        connector.connected = True
        
        result = connector.clear_dtcs()
        
        assert result is True


class TestVehicleInfo:
    """Test VehicleInfo dataclass."""
    
    def test_vehicle_info_creation(self):
        """Test creating VehicleInfo instance."""
        vehicle = VehicleInfo(
            make="Ford",
            model="Mustang",
            year=2023,
            vin="1FA6P8TH5J5123456",
            engine="5.0L V8"
        )
        
        assert vehicle.make == "Ford"
        assert vehicle.model == "Mustang"
        assert vehicle.year == 2023
        assert vehicle.vin == "1FA6P8TH5J5123456"
        assert vehicle.engine == "5.0L V8"
    
    def test_vehicle_info_optional_fields(self):
        """Test VehicleInfo with optional fields."""
        vehicle = VehicleInfo(
            make="Mazda",
            model="CX-5",
            year=2022
        )
        
        assert vehicle.make == "Mazda"
        assert vehicle.model == "CX-5"
        assert vehicle.year == 2022
        assert vehicle.vin is None
        assert vehicle.engine is None
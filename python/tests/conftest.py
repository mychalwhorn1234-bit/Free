"""
Test configuration for FORScan Python package.
"""

import pytest
import sys
import os

# Add the python directory to the path so we can import forscan
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        'adapter': {
            'type': 'ELM327',
            'port': 'COM1',
            'baudrate': 38400
        },
        'forscan': {
            'data_dir': './test_data',
            'config_dir': './test_config'
        }
    }
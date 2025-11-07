#!/usr/bin/env python3
"""
Quick test script to verify FORScan automation fixes.
"""

import sys
import os

# Add the FORScan Python library to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

def test_imports():
    """Test that all core imports work."""
    try:
        from python.forscan import Config, FORScanConnector, ELM327Adapter
        from python.forscan.diagnostics import DiagnosticSession
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test configuration creation."""
    try:
        from python.forscan.config import Config
        config = Config()
        print("✅ Configuration created successfully!")
        print(f"   - Adapter type: {config.adapter.type}")
        print(f"   - Port: {config.adapter.port}")
        print(f"   - Baudrate: {config.adapter.baudrate}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_adapter_creation():
    """Test adapter creation."""
    try:
        from python.forscan.adapters import ELM327Adapter
        from python.forscan.config import Config
        
        config = Config()
        adapter = ELM327Adapter(
            port=config.adapter.port,
            baudrate=config.adapter.baudrate
        )
        print("✅ Adapter created successfully!")
        print(f"   - Type: {type(adapter).__name__}")
        return True
    except Exception as e:
        print(f"❌ Adapter creation error: {e}")
        return False

def test_connector_creation():
    """Test connector creation."""
    try:
        from python.forscan.core import FORScanConnector
        connector = FORScanConnector()
        print("✅ Connector created successfully!")
        return True
    except Exception as e:
        print(f"❌ Connector creation error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("FORScan Automation Fix Verification")
    print("=" * 50)
    print()

    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Adapter Creation Test", test_adapter_creation),
        ("Connector Creation Test", test_connector_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Automation fixes are working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
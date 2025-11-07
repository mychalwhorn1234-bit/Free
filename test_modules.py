#!/usr/bin/env python3
"""
Quick test script for all FORScan modules
"""
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_module_imports():
    """Test importing all FORScan modules"""
    print("🔍 Testing FORScan Module Imports...")
    print("=" * 50)
    
    try:
        # Test config module
        print("📝 Testing config module...")
        from python.forscan.config import Config, AdapterConfig, LoggingConfig, FORScanConfig
        print("   ✅ Config classes imported successfully")
        
        # Test core module
        print("🔧 Testing core module...")
        from python.forscan.core import FORScanCore
        print("   ✅ Core module imported successfully")
        
        # Test adapters module
        print("🔌 Testing adapters module...")
        from python.forscan.adapters import BaseAdapter, ELM327Adapter, J2534Adapter
        print("   ✅ Adapter classes imported successfully")
        
        # Test diagnostics module
        print("🔍 Testing diagnostics module...")
        from python.forscan.diagnostics import DiagnosticsManager
        print("   ✅ Diagnostics module imported successfully")
        
        # Test CLI module
        print("💻 Testing CLI module...")
        from python.forscan.cli import main as cli_main
        print("   ✅ CLI module imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of key classes"""
    print("\n🧪 Testing Basic Functionality...")
    print("=" * 50)
    
    try:
        from python.forscan.config import Config, AdapterConfig, LoggingConfig, FORScanConfig
        
        # Test dataclass creation
        print("📋 Testing configuration classes...")
        adapter_config = AdapterConfig()
        print(f"   ✅ AdapterConfig: {adapter_config.type} on {adapter_config.port}")
        
        logging_config = LoggingConfig()
        print(f"   ✅ LoggingConfig: Level {logging_config.level}")
        
        forscan_config = FORScanConfig()
        print(f"   ✅ FORScanConfig: Data dir {forscan_config.data_dir}")
        
        # Test Config class
        print("⚙️ Testing main Config class...")
        config = Config()
        print(f"   ✅ Config loaded with adapter type: {config.adapter.type}")
        
        # Test validation
        print("🔍 Testing configuration validation...")
        errors = config.validate()
        if errors:
            print(f"   ⚠️  Validation found {len(errors)} issue(s):")
            for error in errors[:3]:  # Show first 3 errors
                print(f"      - {error}")
        else:
            print("   ✅ Configuration validation passed")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Functionality test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 FORScan Modules Test Suite")
    print("=" * 50)
    
    import_success = test_module_imports()
    functionality_success = test_basic_functionality()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY:")
    print("=" * 50)
    
    if import_success and functionality_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ All modules import successfully")
        print("✅ Basic functionality works correctly")
        print("✅ FORScan Python tools are ready to use")
        return 0
    else:
        print("⚠️  SOME ISSUES FOUND:")
        if not import_success:
            print("❌ Module import failures detected")
        if not functionality_success:
            print("❌ Basic functionality issues detected")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
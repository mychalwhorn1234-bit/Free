#!/usr/bin/env python3
"""
Test script to verify ENOENT fixes in config.py
"""
import sys
import os
import tempfile

# Add the current directory to Python path
sys.path.insert(0, '.')

from python.forscan.config import Config

def test_enoent_fixes():
    """Test that ENOENT errors are handled gracefully"""
    print("🧪 Testing ENOENT fixes...")
    
    # Test 1: Load with non-existent config file
    print("\n1. Testing non-existent config file...")
    try:
        config = Config("non_existent_config.yaml")
        print("   ✅ Config loaded without ENOENT exception")
    except FileNotFoundError:
        print("   ❌ ENOENT exception not caught")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected exception: {e}")
        return False
    
    # Test 2: Validate with bad executable path
    print("\n2. Testing validation with bad executable path...")
    try:
        config = Config()
        config.forscan.executable_path = "C:\\definitely\\does\\not\\exist\\forscan.exe"
        errors = config.validate()
        if any("not found or inaccessible" in err for err in errors):
            print("   ✅ Bad path handled gracefully in validation")
        else:
            print("   ⚠️  Expected validation error not found")
    except (FileNotFoundError, OSError):
        print("   ❌ ENOENT exception not caught in validation")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected validation exception: {e}")
        return False
    
    # Test 3: Save to read-only directory (simulate permission error)
    print("\n3. Testing save to inaccessible location...")
    try:
        config = Config()
        # Try to save to a location that likely doesn't exist or isn't writable
        config.config_file = "Z:\\nonexistent\\path\\config.yaml"
        config.save()  # Should not raise exception
        print("   ✅ Save to bad path handled gracefully")
    except (FileNotFoundError, OSError, PermissionError):
        print("   ❌ ENOENT/Permission exception not caught in save")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected save exception: {e}")
        return False
    
    print("\n🎉 All ENOENT fixes working correctly!")
    return True

if __name__ == "__main__":
    success = test_enoent_fixes()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Test script to verify the repo-summarizer package works correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_import():
    """Test that the package can be imported."""
    try:
        from repo_summarizer import main
        print("✅ Package import successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_main_function_exists():
    """Test that the main function exists."""
    try:
        from repo_summarizer.main import main
        print("✅ Main function exists")
        return True
    except ImportError as e:
        print(f"❌ Main function not found: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running tests...")

    success = True
    success &= test_import()
    success &= test_main_function_exists()

    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)
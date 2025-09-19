#!/usr/bin/env python3
"""
Test script to verify PDF Result Extractor installation
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError:
        print("❌ Flask import failed")
        return False
    
    try:
        import fitz
        print("✅ PyMuPDF (fitz) imported successfully")
    except ImportError:
        print("❌ PyMuPDF import failed")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError:
        print("❌ Requests import failed")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError:
        print("❌ Pandas import failed")
        return False
    
    try:
        import word2number
        print("✅ Word2Number imported successfully")
    except ImportError:
        print("❌ Word2Number import failed")
        return False
    
    return True

def test_directories():
    """Test if required directories exist"""
    print("\nTesting directories...")
    
    required_dirs = ['uploads', 'outputs', 'templates']
    all_exist = True
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Directory '{dir_name}' exists")
        else:
            print(f"❌ Directory '{dir_name}' missing")
            all_exist = False
    
    return all_exist

def test_files():
    """Test if required files exist"""
    print("\nTesting files...")
    
    required_files = ['app.py', 'requirements.txt', 'templates/index.html']
    all_exist = True
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"✅ File '{file_name}' exists")
        else:
            print(f"❌ File '{file_name}' missing")
            all_exist = False
    
    return all_exist

def test_flask_app():
    """Test if Flask app can be imported"""
    print("\nTesting Flask application...")
    
    try:
        from app import app
        print("✅ Flask app imported successfully")
        
        # Test if app has required routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        required_routes = ['/', '/upload', '/status/<task_id>', '/download/<filename>']
        
        for route in required_routes:
            if route in routes:
                print(f"✅ Route '{route}' found")
            else:
                print(f"❌ Route '{route}' missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Flask app import failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 PDF Result Extractor - Installation Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run all tests
    if not test_imports():
        all_tests_passed = False
    
    if not test_directories():
        all_tests_passed = False
    
    if not test_files():
        all_tests_passed = False
    
    if not test_flask_app():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All tests passed! Installation is ready.")
        print("Run 'python run.py' to start the application.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("Make sure to install dependencies: pip install -r requirements.txt")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

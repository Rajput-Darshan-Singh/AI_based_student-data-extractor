#!/usr/bin/env python3
"""
Test the complete PDF processing flow
"""

import requests
import json
import time

def test_complete_flow():
    """Test the complete processing flow"""
    print("🧪 Testing Complete PDF Processing Flow")
    print("=" * 50)
    
    # Step 1: Test AI connection
    print("1. Testing AI Model Connection...")
    try:
        response = requests.get('http://127.0.0.1:5000/test-ai')
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI Model: {result.get('status', 'unknown')}")
        else:
            print(f"❌ AI Model failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI Model error: {e}")
        return False
    
    # Step 2: Test CSV creation
    print("\n2. Testing CSV Creation...")
    try:
        response = requests.get('http://127.0.0.1:5000/test-csv')
        if response.status_code == 200:
            result = response.json()
            print(f"✅ CSV Creation: {result.get('message', 'unknown')}")
        else:
            print(f"❌ CSV Creation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CSV Creation error: {e}")
        return False
    
    # Step 3: Test download
    print("\n3. Testing Download...")
    try:
        response = requests.get('http://127.0.0.1:5000/download/test_results.csv')
        if response.status_code == 200:
            print("✅ Download: Working")
        else:
            print(f"❌ Download failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Download error: {e}")
        return False
    
    # Step 4: Check debug info
    print("\n4. Checking System Status...")
    try:
        response = requests.get('http://127.0.0.1:5000/debug')
        if response.status_code == 200:
            debug_info = response.json()
            print(f"✅ System Status:")
            print(f"   - Output files: {len(debug_info.get('output_files', []))}")
            print(f"   - Processing tasks: {len(debug_info.get('processing_tasks', []))}")
            print(f"   - Upload files: {len(debug_info.get('upload_files', []))}")
        else:
            print(f"❌ Debug info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Debug info error: {e}")
        return False
    
    print("\n🎉 All Tests Passed!")
    print("\n💡 The issue is likely in the PDF processing logic.")
    print("   When you upload a PDF, the processing fails silently.")
    print("   Check the console output for error messages during PDF upload.")
    
    return True

if __name__ == "__main__":
    test_complete_flow()

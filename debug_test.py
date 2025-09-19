#!/usr/bin/env python3
"""
Debug test script to help identify the download issue
"""

import os
import requests
import json
import time

def test_debug_endpoint():
    """Test the debug endpoint"""
    try:
        response = requests.get('http://localhost:5000/debug')
        if response.status_code == 200:
            debug_info = response.json()
            print("🔍 Debug Information:")
            print(f"Processing tasks: {debug_info.get('processing_tasks', [])}")
            print(f"Output files: {debug_info.get('output_files', [])}")
            print(f"Upload files: {debug_info.get('upload_files', [])}")
            print(f"Output folder: {debug_info.get('output_folder', '')}")
            print(f"Upload folder: {debug_info.get('upload_folder', '')}")
            return debug_info
        else:
            print(f"❌ Debug endpoint failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error accessing debug endpoint: {e}")
        return None

def test_download_endpoint(filename):
    """Test the download endpoint"""
    try:
        response = requests.get(f'http://localhost:5000/download/{filename}')
        if response.status_code == 200:
            print(f"✅ Download successful for {filename}")
            return True
        else:
            print(f"❌ Download failed for {filename}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing download: {e}")
        return False

def check_local_files():
    """Check local file system"""
    print("\n📁 Local File System Check:")
    
    # Check outputs directory
    outputs_dir = "outputs"
    if os.path.exists(outputs_dir):
        files = os.listdir(outputs_dir)
        print(f"Outputs directory ({outputs_dir}): {files}")
    else:
        print(f"❌ Outputs directory does not exist: {outputs_dir}")
    
    # Check uploads directory
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        files = os.listdir(uploads_dir)
        print(f"Uploads directory ({uploads_dir}): {files}")
    else:
        print(f"❌ Uploads directory does not exist: {uploads_dir}")

def main():
    print("🧪 PDF Result Extractor - Debug Test")
    print("=" * 50)
    
    # Check local files first
    check_local_files()
    
    # Test debug endpoint
    print("\n🌐 Testing Debug Endpoint:")
    debug_info = test_debug_endpoint()
    
    if debug_info and debug_info.get('output_files'):
        print("\n📥 Testing Download Endpoints:")
        for filename in debug_info['output_files']:
            test_download_endpoint(filename)
    else:
        print("\n⚠️  No output files found. This suggests:")
        print("   1. Processing failed")
        print("   2. Files were cleaned up")
        print("   3. Processing is still in progress")
        print("   4. There was an error during CSV creation")
    
    print("\n💡 Recommendations:")
    print("   1. Try uploading a new PDF file")
    print("   2. Check the terminal/console for error messages")
    print("   3. Make sure your AI model server is running")
    print("   4. Check the browser's developer console for errors")

if __name__ == "__main__":
    main()

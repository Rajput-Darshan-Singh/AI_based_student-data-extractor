#!/usr/bin/env python3
"""
Diagnostic tool to identify the PDF processing issue
"""

import requests
import json
import os

def check_system_status():
    """Check the current system status"""
    print("🔍 System Diagnostic")
    print("=" * 40)
    
    try:
        # Check debug info
        response = requests.get('http://127.0.0.1:5000/debug')
        if response.status_code == 200:
            debug_info = response.json()
            print(f"📊 Current Status:")
            print(f"   - Processing tasks: {len(debug_info.get('processing_tasks', []))}")
            print(f"   - Output files: {debug_info.get('output_files', [])}")
            print(f"   - Upload files: {debug_info.get('upload_files', [])}")
            
            if debug_info.get('processing_tasks'):
                print(f"   - Active tasks: {debug_info['processing_tasks']}")
            
            return debug_info
        else:
            print(f"❌ Failed to get debug info: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting debug info: {e}")
        return None

def check_file_system():
    """Check local file system"""
    print(f"\n📁 File System Check:")
    
    # Check outputs directory
    outputs_dir = "outputs"
    if os.path.exists(outputs_dir):
        files = os.listdir(outputs_dir)
        print(f"   - Outputs directory: {files}")
    else:
        print(f"   - ❌ Outputs directory missing")
    
    # Check uploads directory
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        files = os.listdir(uploads_dir)
        print(f"   - Uploads directory: {files}")
    else:
        print(f"   - ❌ Uploads directory missing")

def provide_solutions():
    """Provide solutions based on common issues"""
    print(f"\n💡 Solutions to Try:")
    print("1. **Upload a new PDF file** and watch the console for error messages")
    print("2. **Check if your PDF has selectable text** (not just scanned images)")
    print("3. **Ensure PDF is under 16MB**")
    print("4. **Try a different PDF file** to see if the issue is file-specific")
    print("5. **Check browser console** (F12) for any JavaScript errors")
    
    print(f"\n🔧 Debug Steps:")
    print("1. Open browser to http://127.0.0.1:5000")
    print("2. Upload your PDF file")
    print("3. Watch the terminal where Flask is running")
    print("4. Look for messages starting with:")
    print("   - 'Starting processing for task...'")
    print("   - 'PDF opened successfully...'")
    print("   - 'Processing page X/Y...'")
    print("   - Any error messages")

def main():
    debug_info = check_system_status()
    check_file_system()
    provide_solutions()
    
    if debug_info and not debug_info.get('processing_tasks'):
        print(f"\n⚠️  No active processing tasks found.")
        print("   This suggests the PDF processing failed or never started.")
        print("   Please try uploading a PDF and check the console output.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test script to debug the PDF processing issue
"""

import requests
import json
import time

def test_ai_model():
    """Test if AI model is working"""
    print("🤖 Testing AI Model...")
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": "Extract student information from this text: Student Name: John Doe, Registration: 12345, Total Marks: 85, SGPA: 8.5, Grade: A. Return JSON only.",
                "stream": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI Model Response: {result.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ AI Model failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI Model error: {e}")
        return False

def test_upload_and_process():
    """Test the upload and processing workflow"""
    print("\n📤 Testing Upload and Processing...")
    
    # Create a simple test file (we'll simulate this)
    print("Note: This test requires a real PDF file upload through the web interface")
    print("Please try uploading a PDF file through the web interface and check the console output")
    
    return True

def check_processing_status():
    """Check current processing status"""
    print("\n📊 Checking Processing Status...")
    try:
        response = requests.get('http://localhost:5000/debug')
        if response.status_code == 200:
            debug_info = response.json()
            print(f"Active tasks: {len(debug_info.get('processing_tasks', []))}")
            print(f"Output files: {len(debug_info.get('output_files', []))}")
            return debug_info
        else:
            print(f"❌ Failed to get debug info: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting debug info: {e}")
        return None

def main():
    print("🧪 PDF Processing Debug Test")
    print("=" * 50)
    
    # Test AI model
    ai_working = test_ai_model()
    
    if not ai_working:
        print("❌ AI model is not working. Please check Ollama installation.")
        return
    
    # Check processing status
    debug_info = check_processing_status()
    
    print("\n💡 Next Steps:")
    print("1. Open your browser and go to http://localhost:5000")
    print("2. Upload a PDF file")
    print("3. Watch the console output for any error messages")
    print("4. If processing fails, check the browser's developer console (F12)")
    print("5. Look for any error messages in the terminal where the app is running")
    
    print("\n🔍 Common Issues to Check:")
    print("- Make sure the PDF file is not corrupted")
    print("- Check if the PDF has selectable text (not just images)")
    print("- Verify the PDF is under 16MB")
    print("- Look for any error messages in the browser console")

if __name__ == "__main__":
    main()

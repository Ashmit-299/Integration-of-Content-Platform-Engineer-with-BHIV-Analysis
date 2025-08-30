#!/usr/bin/env python3
"""
Simple test script for BHIV platform
"""
import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

def test_upload():
    """Test file upload"""
    try:
        with open("sample/lesson.txt", "rb") as f:
            files = {"file": f}
            response = requests.post(f"{BASE_URL}/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            video_id = data.get("id")
            print(f"✅ Upload successful: {video_id}")
            return video_id
        else:
            print(f"❌ Upload failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def test_status():
    """Test BHIV status"""
    try:
        response = requests.get(f"{BASE_URL}/bhiv/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ BHIV Status: {data}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status error: {e}")
        return False

def main():
    """Run simple tests"""
    print("🧪 Running Simple BHIV Tests...")
    print()
    
    # Test 1: Health check
    if not test_health():
        print("💥 Server not running. Start with: python run.py")
        sys.exit(1)
    
    # Test 2: BHIV Status
    test_status()
    
    # Test 3: Upload (if sample file exists)
    try:
        video_id = test_upload()
        if video_id:
            print(f"🎬 Video generated with ID: {video_id}")
            print(f"🔗 Stream at: {BASE_URL}/stream/{video_id}")
    except:
        print("⚠️  Upload test skipped (sample file not found)")
    
    print()
    print("🎉 Basic tests completed!")
    print(f"🌐 Visit {BASE_URL}/docs for full API documentation")

if __name__ == "__main__":
    main()
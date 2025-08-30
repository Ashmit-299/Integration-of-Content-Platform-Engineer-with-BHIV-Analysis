# smoke_test.py (simple concurrency test)
import requests
import concurrent.futures
import time
import sys

BASE = "http://127.0.0.1:8000"

def upload_and_rate(i):
    """Upload script, stream video, and rate it"""
    try:
        # Upload file
        with open("sample/lesson.txt", "rb") as f:
            files = {"file": f}
            r = requests.post(BASE + "/upload", files=files, timeout=30)
        
        if r.status_code != 200:
            print(f"Upload {i} failed: {r.status_code}")
            return None
            
        vid = r.json().get("id")
        if not vid:
            print(f"No video ID returned for upload {i}")
            return None
        
        # Wait a bit for processing
        time.sleep(2)
        
        # Stream head (just check if accessible)
        s = requests.get(BASE + f"/stream/{vid}", stream=True, timeout=10)
        if s.status_code != 200:
            print(f"Stream {i} failed: {s.status_code}")
        
        # Rate the video
        rate_response = requests.post(
            BASE + f"/rate/{vid}", 
            data={"rating": 4, "comment": f"Test rating {i}"}, 
            timeout=10
        )
        
        if rate_response.status_code != 200:
            print(f"Rating {i} failed: {rate_response.status_code}")
        
        print(f"✅ Test {i} completed: {vid}")
        return vid
        
    except Exception as e:
        print(f"❌ Test {i} failed: {e}")
        return None

def test_health_endpoints():
    """Test health and status endpoints"""
    try:
        # Health check
        health = requests.get(BASE + "/health", timeout=5)
        assert health.status_code == 200
        print("✅ Health check passed")
        
        # Status check
        status = requests.get(BASE + "/status", timeout=5)
        assert status.status_code == 200
        print("✅ Status check passed")
        
        # BHIV status
        bhiv_status = requests.get(BASE + "/bhiv/status", timeout=5)
        assert bhiv_status.status_code == 200
        print("✅ BHIV status check passed")
        
        # Metrics
        metrics = requests.get(BASE + "/metrics", timeout=5)
        assert metrics.status_code == 200
        print("✅ Metrics check passed")
        
        return True
    except Exception as e:
        print(f"❌ Health checks failed: {e}")
        return False

def main():
    """Run smoke tests"""
    print("🚀 Starting BHIV Platform Smoke Tests...")
    
    # Test health endpoints first
    if not test_health_endpoints():
        print("💥 Health checks failed, aborting")
        sys.exit(1)
    
    # Run concurrent upload tests
    print(f"\n📊 Running concurrent upload tests...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(upload_and_rate, range(10)))
    
    successful = [r for r in results if r is not None]
    
    print(f"\n📈 Results:")
    print(f"  - Total tests: 10")
    print(f"  - Successful: {len(successful)}")
    print(f"  - Failed: {10 - len(successful)}")
    
    if len(successful) >= 8:  # 80% success rate
        print("🎉 Smoke tests PASSED!")
        sys.exit(0)
    else:
        print("💥 Smoke tests FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
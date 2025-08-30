#!/usr/bin/env python3
"""
BHIV-Integrated Gurukul Content Platform - Unified Deployment Runner
Single file deployment that starts frontend, backend, and all services together.
"""

import os
import sys
import subprocess
import threading
import time
import signal
import webbrowser
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def setup_environment():
    """Setup required directories and environment"""
    base_dir = Path(__file__).parent.parent
    
    # Create required directories
    dirs = ['bucket', 'bucket/logs', 'bucket/videos', 'bucket/scripts', 
            'bucket/storyboards', 'bucket/ratings', 'data', 'data/videos', 'data/storyboards']
    
    for dir_name in dirs:
        (base_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    # Set environment variables
    os.environ['BHIV_BUCKET_PATH'] = str(base_dir / 'bucket')
    os.environ['DATABASE_URL'] = f'sqlite:///{base_dir}/data/meta.db'
    
    return base_dir

def start_backend(base_dir):
    """Start FastAPI backend server"""
    print("🚀 Starting FastAPI Backend...")
    
    backend_cmd = [
        sys.executable, "-m", "uvicorn", 
        "backend.server:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ]
    
    return subprocess.Popen(
        backend_cmd, 
        cwd=base_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def start_frontend(base_dir):
    """Start Streamlit frontend"""
    print("🎨 Starting Streamlit Frontend...")
    
    frontend_cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ]
    
    return subprocess.Popen(
        frontend_cmd,
        cwd=base_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def wait_for_services():
    """Wait for services to be ready"""
    import requests
    
    print("⏳ Waiting for services to start...")
    
    # Wait for backend
    for i in range(30):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend ready!")
                break
        except:
            time.sleep(1)
    
    # Wait for frontend
    time.sleep(3)
    print("✅ Frontend ready!")

def open_browser():
    """Open browser to the application"""
    time.sleep(2)
    print("🌐 Opening browser...")
    webbrowser.open("http://localhost:8501")

def main():
    """Main deployment function"""
    print("=" * 60)
    print("🚀 BHIV-Integrated Gurukul Content Platform")
    print("   Unified Deployment Starting...")
    print("=" * 60)
    
    # Setup
    base_dir = setup_environment()
    processes = []
    
    try:
        # Start backend
        backend_process = start_backend(base_dir)
        processes.append(backend_process)
        
        # Start frontend
        frontend_process = start_frontend(base_dir)
        processes.append(frontend_process)
        
        # Wait for services
        wait_for_services()
        
        # Open browser
        threading.Thread(target=open_browser, daemon=True).start()
        
        print("\n" + "=" * 60)
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print("=" * 60)
        print("📱 Frontend:     http://localhost:8501")
        print("🔧 Backend:      http://localhost:8000")
        print("📚 API Docs:     http://localhost:8000/docs")
        print("💊 Health:       http://localhost:8000/health")
        print("🧠 BHIV Status:  http://localhost:8000/bhiv/status")
        print("=" * 60)
        print("Press Ctrl+C to stop all services")
        print("=" * 60)
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
    finally:
        # Cleanup
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()
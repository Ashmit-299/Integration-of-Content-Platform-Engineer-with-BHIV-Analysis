#!/usr/bin/env python3
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def setup():
    dirs = ["data", "data/videos", "temp"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

def start_api():
    print("🚀 Starting API server...")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "backend.server_minimal:app", 
        "--host", "127.0.0.1", 
        "--port", "8000"
    ])

def start_streamlit():
    print("🎨 Starting Streamlit frontend...")
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", 
        "streamlit_app.py",
        "--server.port", "8501",
        "--server.headless", "true"
    ])

def main():
    setup()
    
    api_process = start_api()
    time.sleep(3)
    
    streamlit_process = start_streamlit()
    time.sleep(3)
    
    print("\n✅ BHIV Platform Ready!")
    print("   • Frontend: http://127.0.0.1:8501")
    print("   • API: http://127.0.0.1:8000")
    
    try:
        webbrowser.open("http://127.0.0.1:8501")
    except:
        pass
    
    print("\n🎯 Press Ctrl+C to stop")
    
    try:
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        streamlit_process.terminate()
        api_process.terminate()
        print("✅ Stopped")

if __name__ == "__main__":
    main()
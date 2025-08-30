#!/usr/bin/env python3
"""
Simple runner for BHIV Platform
"""
import subprocess
import sys
from pathlib import Path

def setup_dirs():
    """Create directories"""
    dirs = ["bucket", "bucket/videos", "bucket/storyboards", "bucket/logs", "data", "temp"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("[OK] Directories created")

def main():
    print("[STARTING] BHIV Platform")
    
    setup_dirs()
    
    print("[INFO] Choose mode:")
    print("1. API Server (FastAPI)")
    print("2. Web App (Streamlit)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        print("[SERVER] Starting FastAPI on http://127.0.0.1:8000")
        print("[DOCS] API docs: http://127.0.0.1:8000/docs")
        
        try:
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "backend.server_minimal:app", 
                "--host", "127.0.0.1", 
                "--port", "8000", 
                "--reload"
            ])
        except KeyboardInterrupt:
            print("\n[STOPPED] Server stopped")
    
    elif choice == "2":
        print("[WEBAPP] Starting Streamlit on http://localhost:8501")
        
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.port", "8501"
            ])
        except KeyboardInterrupt:
            print("\n[STOPPED] Web app stopped")
    
    else:
        print("[ERROR] Invalid choice")

if __name__ == "__main__":
    main()
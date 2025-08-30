#!/usr/bin/env python3
"""
BHIV Platform Runner with Theme Selection
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
    print("=" * 50)
    print("🎥 BHIV Video Platform")
    print("=" * 50)
    
    setup_dirs()
    
    print("\n🎨 Choose Interface:")
    print("1. 🌟 Modern Gradient Theme (Recommended)")
    print("2. 🌙 Classic Dark Theme") 
    print("3. 🔧 API Server Only")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n[STARTING] Modern Gradient Theme")
        print("🌐 Access: http://localhost:8501")
        
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
                "--server.port", "8501",
                "--theme.base", "dark",
                "--theme.primaryColor", "#ff6b6b"
            ])
        except KeyboardInterrupt:
            print("\n[STOPPED] Application stopped")
    
    elif choice == "2":
        print("\n[STARTING] Classic Dark Theme")
        print("🌐 Access: http://localhost:8501")
        
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.port", "8501",
                "--theme.base", "dark"
            ])
        except KeyboardInterrupt:
            print("\n[STOPPED] Application stopped")
    
    elif choice == "3":
        print("\n[STARTING] API Server")
        print("🌐 API: http://127.0.0.1:8000")
        print("📖 Docs: http://127.0.0.1:8000/docs")
        
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
    
    else:
        print("[ERROR] Invalid choice")

if __name__ == "__main__":
    main()
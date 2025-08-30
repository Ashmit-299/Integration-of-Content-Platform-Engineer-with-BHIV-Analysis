#!/usr/bin/env python3
import subprocess
import sys
import webbrowser
import time
from pathlib import Path

def setup():
    Path("bucket").mkdir(exist_ok=True)
    Path("bucket/videos").mkdir(exist_ok=True)
    Path("bucket/storyboards").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    Path("temp").mkdir(exist_ok=True)

def main():
    print("🚀 Starting BHIV Platform...")
    setup()
    
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ])
        
        time.sleep(3)
        print("✅ Platform ready at: http://127.0.0.1:8501")
        
        try:
            webbrowser.open("http://127.0.0.1:8501")
        except:
            pass
        
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        process.terminate()
    except FileNotFoundError:
        print("❌ Streamlit not installed. Run: pip install streamlit")

if __name__ == "__main__":
    main()
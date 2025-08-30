#!/usr/bin/env python3
"""
Production deployment script for BHIV Platform
"""
import subprocess
import sys
import os
from pathlib import Path
import shutil

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found. Copy from .env.sample")
        return False
    
    # FFmpeg is handled by imageio[ffmpeg] package automatically
    
    print("✅ All requirements met")
    return True

def setup_environment():
    """Setup production environment"""
    print("🔧 Setting up environment...")
    
    # Create directories
    dirs = [
        "bucket", "bucket/scripts", "bucket/videos", 
        "bucket/storyboards", "bucket/logs",
        "data", "temp", "logs"
    ]
    
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    
    # Install dependencies
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    print("✅ Environment setup complete")

def run_tests():
    """Run test suite"""
    print("🧪 Running tests...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("❌ Tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("⚠️ pytest not found, skipping tests")
        return True

def deploy():
    """Deploy the application"""
    print("🚀 Deploying BHIV Platform...")
    
    # Start the application
    try:
        print("Starting Streamlit application...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Deployment stopped by user")
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False
    
    return True

def main():
    """Main deployment function"""
    print("🎥 BHIV Platform Deployment")
    print("=" * 40)
    
    if not check_requirements():
        sys.exit(1)
    
    setup_environment()
    
    if not run_tests():
        response = input("Tests failed. Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n🎯 Ready to deploy!")
    print("Access the platform at: http://localhost:8501")
    print("API documentation at: http://localhost:8000/docs (if running API server)")
    
    deploy()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Setup script for BHIV-Integrated Gurukul Content Platform
Installs dependencies and prepares environment
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing dependencies...")
    
    req_file = Path(__file__).parent / "requirements.txt"
    
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-r", str(req_file)
    ])
    
    print("✅ Dependencies installed!")

def setup_directories():
    """Create required directories"""
    print("📁 Setting up directories...")
    
    base_dir = Path(__file__).parent.parent
    dirs = [
        'bucket', 'bucket/logs', 'bucket/videos', 'bucket/scripts',
        'bucket/storyboards', 'bucket/ratings', 'data', 'data/videos', 
        'data/storyboards', 'temp', 'logs'
    ]
    
    for dir_name in dirs:
        (base_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created!")

def create_env_file():
    """Create .env file if it doesn't exist"""
    base_dir = Path(__file__).parent.parent
    env_file = base_dir / ".env"
    
    if not env_file.exists():
        print("🔧 Creating .env file...")
        
        env_content = """# BHIV Configuration
BHIV_BUCKET_PATH=bucket
BHIV_LM_URL=
BHIV_LM_API_KEY=

# Database
DATABASE_URL=sqlite:///./data/meta.db

# Optional S3 Configuration
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET_NAME=
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created!")

def main():
    """Main setup function"""
    print("=" * 50)
    print("🚀 BHIV Platform Setup")
    print("=" * 50)
    
    try:
        install_requirements()
        setup_directories()
        create_env_file()
        
        print("\n" + "=" * 50)
        print("✅ Setup Complete!")
        print("=" * 50)
        print("Run: python main_run.py")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
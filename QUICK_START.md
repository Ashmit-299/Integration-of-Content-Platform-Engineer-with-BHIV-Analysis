# Quick Start Guide

## Step 1: Activate Virtual Environment
```cmd
venv\Scripts\activate
```

## Step 2: Install Dependencies (if needed)
```cmd
pip install fastapi uvicorn streamlit PyJWT
```

## Step 3: Run the Platform
```cmd
python run_simple.py
```

## Step 4: Choose Mode
- **Option 1**: API Server (FastAPI) - For developers
- **Option 2**: Web App (Streamlit) - For users

## Access Points

### API Server Mode (Option 1)
- **API**: http://127.0.0.1:8000
- **Docs**: http://127.0.0.1:8000/docs
- **Health**: http://127.0.0.1:8000/health

### Web App Mode (Option 2)  
- **App**: http://localhost:8501

## Default Login
- **Username**: admin
- **Password**: admin123

## Features
- ✅ Auto-login detection
- ✅ File upload and processing
- ✅ User authentication
- ✅ Video generation
- ✅ Rating system
- ✅ Analytics dashboard

## Troubleshooting
1. Make sure virtual environment is activated
2. Check if all dependencies are installed
3. Ensure ports 8000/8501 are available
4. Check logs in `bucket/logs/` folder
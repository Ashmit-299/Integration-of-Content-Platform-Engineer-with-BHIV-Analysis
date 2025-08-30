# 🚀 BHIV Platform - Complete Deployment Guide

## Single Command Deployment

### Option 1: Windows Batch File (Easiest)
```cmd
run.bat
```

### Option 2: Python Commands
```cmd
# Setup (first time only)
python setup.py

# Run platform
python main_run.py
```

### Option 3: Manual Steps
```cmd
# Install dependencies
pip install -r requirements.txt

# Run unified platform
python main_run.py
```

## What This Deployment Includes

### ✅ Complete Stack
- **Frontend**: Streamlit UI (Port 8501)
- **Backend**: FastAPI server (Port 8000)
- **Video Generator**: AI-powered video creation
- **Analytics**: Advanced analytics engine
- **Authentication**: User login/register system
- **BHIV Core**: Bucket-Human-Intelligence-Video architecture

### ✅ Full User Journey
1. **User Registration/Login** → Secure authentication
2. **Script Upload** → Drag & drop interface
3. **Video Generation** → AI-powered processing
4. **Video Playback** → Professional video player
5. **Rating System** → User feedback with AI analysis
6. **Analytics Dashboard** → Real-time insights

### ✅ Enterprise Features
- Professional dark theme UI
- Real-time metrics and analytics
- Sentiment analysis of feedback
- Rating trends and insights
- Video gallery management
- Health monitoring endpoints

## Access Points After Deployment

- **Main Application**: http://localhost:8501
- **API Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **BHIV Status**: http://localhost:8000/bhiv/status

## File Structure

```
deployment/
├── main_run.py          # 🎯 MAIN DEPLOYMENT FILE
├── setup.py             # Environment setup
├── run.bat              # Windows quick start
├── app.py               # Streamlit frontend
├── requirements.txt     # Dependencies
├── backend/             # FastAPI server
├── video/               # Video generation
├── analytics/           # Analytics engine
├── security/            # Authentication
├── sample/              # Sample data
└── README.md            # Instructions
```

## Stopping the Platform

Press `Ctrl+C` in the terminal running `main_run.py`

## Troubleshooting

### Common Issues:
1. **Port conflicts**: Change ports in main_run.py
2. **Missing dependencies**: Run `python setup.py`
3. **Permission errors**: Run as administrator
4. **FFmpeg not found**: Install FFmpeg for video processing

### Logs Location:
- Backend logs: Console output
- Frontend logs: Console output
- Application logs: `bucket/logs/`

---

**🎯 One deployment folder, complete platform!**
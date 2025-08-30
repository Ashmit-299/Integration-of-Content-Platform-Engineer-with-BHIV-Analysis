# BHIV-Integrated Gurukul Content Platform

Production-ready AI platform that converts lesson scripts into videos with user authentication, rating system, and advanced analytics. Built with FastAPI backend, Streamlit frontend, and BHIV architecture for enterprise deployment.

## 🚀 Quick Start

### Local Production Deployment
```cmd
python deploy.py
```

### Cloud Deployment (Streamlit Community Cloud)
1. Push code to GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub and select repository
4. Set main file: `app.py`
5. Deploy

### Development Setup
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Start backend
uvicorn backend.server:app --reload

# Start frontend (new terminal)
streamlit run app.py
```

## 🧪 Testing

### Quick Test
```cmd
python test_simple.py
```

### Full Smoke Test
```cmd
python smoke_test.py
```

### Manual API Testing
```cmd
# Upload a script
curl -F "file=@sample/lesson.txt" http://127.0.0.1:8000/upload

# Check health
curl http://127.0.0.1:8000/health

# Check BHIV status
curl http://127.0.0.1:8000/bhiv/status
```

## 🌐 Access Points

- **Streamlit Frontend**: http://localhost:8501
- **FastAPI Backend**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health
- **Analytics Dashboard**: Built into Streamlit UI
- **BHIV Status**: http://127.0.0.1:8000/bhiv/status

## 🏗️ Enterprise Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   FastAPI        │    │   BHIV Core     │
│   Frontend      │◄──►│   Backend        │◄──►│   Orchestrator  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Analytics     │    │   Authentication │    │   AI Client     │
│   Dashboard     │    │   & Security     │    │   (LM)          │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📊 API Endpoints

### Core Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload script and generate video |
| `/stream/{vid}` | GET | Stream generated video |
| `/rate/{vid}` | POST | Rate video and trigger AI feedback |

### BHIV Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/bhiv/ingest` | POST | BHIV script ingestion |
| `/bhiv/feedback` | POST | AI feedback processing |
| `/bhiv/upload` | POST | Upload video to bucket |
| `/bhiv/status` | GET | BHIV system status |

### System Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/status` | GET | System status |
| `/metrics` | GET | Platform metrics |
| `/logs` | GET | System logs |

## 🔧 Configuration

### Environment Variables (.env)
```env
# BHIV Configuration
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
```

### File Structure
```
gurukul-content-platform/
├── app.py                   # Streamlit frontend
├── backend/
│   └── server.py            # FastAPI server
├── video/
│   ├── storyboard.py       # Script to storyboard conversion
│   ├── generator.py        # Video generation
│   └── feedback_adapter.py # Feedback processing
├── analytics/
│   └── advanced_analytics.py # Analytics engine
├── security/
│   └── config.py           # Security configuration
├── tests/
│   └── test_bhiv_core.py   # Unit tests
├── .github/workflows/
│   └── ci.yml              # CI/CD pipeline
├── bucket/                 # BHIV storage
├── bhiv_core.py           # Core orchestrator
├── bhiv_lm_client.py      # Robust AI client
├── deploy.py              # Production deployment
└── PRODUCTION_READY.md    # Enterprise docs
```

## 🎯 Usage

### Web Interface
1. **Login/Register**: Secure user authentication
2. **Upload Script**: Drag & drop lesson files
3. **Generate Video**: AI-powered video creation
4. **Rate & Review**: Feedback system with AI analysis
5. **Analytics**: Real-time performance metrics

### API Usage
```python
import requests

# Upload script
with open("lesson.txt", "rb") as f:
    response = requests.post(
        "http://127.0.0.1:8000/upload",
        files={"file": f}
    )

video_id = response.json()["id"]

# Rate video
requests.post(
    f"http://127.0.0.1:8000/rate/{video_id}",
    data={"rating": 5, "comment": "Great!"}
)
```

## 🐳 Docker Deployment

### Build and Run
```cmd
docker-compose up --build -d
```

### Deploy Script
```cmd
./deploy.sh
```

## 🧪 Testing & CI/CD

### Automated Testing
```cmd
# Unit tests
pytest tests/

# Integration tests
python smoke_test.py
```

### CI/CD Pipeline
- **GitHub Actions**: Automated testing on push
- **Security Scanning**: Dependency vulnerability checks
- **Code Quality**: Linting and formatting
- **Deployment**: Automated production deployment

### Prerequisites
- Python 3.8+
- FFmpeg (for video processing)
- Docker (optional)

## 🔍 Monitoring

### Health Checks
- **Health**: `/health` - Basic service health
- **Status**: `/status` - Detailed system status
- **BHIV Status**: `/bhiv/status` - BHIV component status
- **Metrics**: `/metrics` - Platform metrics

### Logs
- **System Logs**: `bucket/logs/`
- **Feedback Logs**: `bucket/logs/feedback_*.json`
- **Job Logs**: `bucket/logs/<job_id>.json`

## 🚀 Production Deployment

### Minimum Requirements
- 2 vCPUs, 4GB RAM
- 10GB storage
- Python 3.8+
- Docker (optional)

### Scaling Considerations
- Use external database (PostgreSQL)
- Configure S3 for bucket storage
- Add load balancer for multiple instances
- Monitor FFmpeg concurrency limits

## 🎉 Enterprise Features

### Frontend (Streamlit)
- ✅ Professional dark theme UI
- ✅ User authentication & authorization
- ✅ Real-time analytics dashboard
- ✅ Interactive video management
- ✅ Responsive design

### Backend (FastAPI)
- ✅ RESTful API with auto-documentation
- ✅ JWT-based security
- ✅ Async request handling
- ✅ Health monitoring endpoints
- ✅ SQLite database with migrations

### BHIV Architecture
- ✅ **Bucket**: Centralized storage with metadata
- ✅ **Human-in-the-loop**: Advanced feedback system
- ✅ **Intelligence**: AI-powered analysis with retry logic
- ✅ **Video**: Enhanced generation pipeline

### Production Ready
- ✅ CI/CD pipeline with GitHub Actions
- ✅ Comprehensive unit & integration tests
- ✅ Security configuration management
- ✅ Advanced analytics with sentiment analysis
- ✅ Automated deployment scripts
- ✅ Enterprise documentation

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feat/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feat/amazing-feature`)
5. Open Pull Request

## 📞 Support

For support and questions:
- Check `/docs` endpoint for API documentation
- Review logs in `bucket/logs/`
- Run health checks via `/health` endpoint

---

**🎯 Ready for Production | 🚀 BHIV-Powered | 🤖 AI-Enhanced**
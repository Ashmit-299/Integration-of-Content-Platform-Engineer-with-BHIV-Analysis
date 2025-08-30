# backend/server.py
from bhiv_core import get_orchestrator
from bhiv_bucket import save_script
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from video.feedback_adapter import adapt_storyboard
from video.bhiv_integration import BHIVClient
from security.auth import (
    auth_manager, get_current_active_user, require_admin, require_user,
    User, UserLogin, UserCreate, SecurityValidator
)
import uuid, shutil, json, sqlite3, os
from video.storyboard import generate_storyboard_from_file
import time
from datetime import datetime

app = FastAPI(
    title="BHIV-Integrated Gurukul Content Platform",
    description="Professional AI-enhanced video generation platform with BHIV integration",
    version="2.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Authentication endpoints
@app.post("/auth/login")
async def login(login_data: UserLogin):
    """User login endpoint"""
    return auth_manager.login(login_data)

@app.post("/auth/register")
async def register(user_data: UserCreate, current_user: User = Depends(require_admin)):
    """User registration (admin only)"""
    return auth_manager.create_user(user_data)

@app.post("/auth/refresh")
async def refresh_token(refresh_token: str = Form(...)):
    """Refresh access token"""
    return auth_manager.refresh_access_token(refresh_token)

@app.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@app.get("/health")
def health_check():
    """Health check endpoint for production"""
    return {"status": "healthy", "service": "bhiv-gurukul-platform"}

@app.get("/status")
def system_status():
    """System status with BHIV integration info"""
    bucket_exists = Path("bucket").exists()
    logs_exist = Path("bucket/logs").exists()
    
    return {
        "platform": "operational",
        "bhiv_integration": "active",
        "bucket_storage": "ready" if bucket_exists else "initializing",
        "ai_logging": "ready" if logs_exist else "initializing",
        "endpoints": ["/upload", "/bhiv/ingest", "/bhiv/feedback", "/bhiv/upload"]
    }

DATA = Path("data")
VIDEOS = DATA / "videos"
DBPATH = DATA / "meta.db"

def init_db():
    try:
        os.makedirs(DATA, exist_ok=True)
        os.makedirs(VIDEOS, exist_ok=True)
        
        with sqlite3.connect(DBPATH) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS videos
                         (id TEXT PRIMARY KEY, title TEXT, storyboard_path TEXT, video_path TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS ratings
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, video_id TEXT, rating INTEGER, comment TEXT)''')
            conn.commit()
    except Exception as e:
        print(f"Database initialization error: {e}")

init_db()

class UploadResponse(BaseModel):
    id: str
    message: str

@app.post("/upload", response_model=UploadResponse)
async def upload_script(
    file: UploadFile = File(...),
    current_user: User = Depends(require_user)
):
    """Upload script and process through BHIV Core"""
    if not file.filename or not file.filename.endswith((".txt", ".md")):
        raise HTTPException(status_code=400, detail="Only .txt or .md files accepted")

    temp_path = Path("temp") / file.filename
    temp_path.parent.mkdir(exist_ok=True)
    
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        from bhiv_core import process_script_upload
        result = process_script_upload(str(temp_path), current_user.id)
        
        with sqlite3.connect(DBPATH) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO videos (id, title, storyboard_path, video_path) VALUES (?,?,?,?)",
                      (result["id"], "Generated Video", result["storyboard"], result["video"]))
            conn.commit()
        
        return {"id": result["id"], "message": "Uploaded and processed via BHIV"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BHIV processing error: {e}")
    finally:
        if temp_path.exists():
            temp_path.unlink()

@app.get("/stream/{vid}")
def stream_video(vid: str):
    """Stream video with bucket support"""
    bucket_path = Path("bucket/videos") / f"{vid}.mp4"
    data_path = VIDEOS / f"{vid}.mp4"
    
    if bucket_path.exists():
        return FileResponse(bucket_path, media_type="video/mp4", filename=bucket_path.name)
    elif data_path.exists():
        return FileResponse(data_path, media_type="video/mp4", filename=data_path.name)
    else:
        raise HTTPException(status_code=404, detail="Video not found")

@app.post("/rate/{vid}")
async def rate_video(
    vid: str, 
    rating: int = Form(...), 
    comment: str = Form(""),
    current_user: User = Depends(get_current_active_user)
):
    """Rate video and trigger BHIV feedback loop"""
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="rating must be 1..5")
    
    with sqlite3.connect(DBPATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO ratings (video_id, rating, comment) VALUES (?,?,?)", (vid, rating, comment))
    
    # Sanitize comment input
    comment = SecurityValidator.sanitize_input(comment)
    
    try:
        from bhiv_core import notify_on_rate
        improvement = notify_on_rate(vid, rating, comment)
        return {"message": "Thanks for rating", "improvement_triggered": bool(improvement)}
    except Exception as e:
        return {"message": "Thanks for rating", "improvement_error": str(e)}

@app.get("/bhiv/status")
def bhiv_status(current_user: User = Depends(require_user)):
    """BHIV system status"""
    bucket_files = len(list(Path("bucket").glob("*"))) if Path("bucket").exists() else 0
    log_files = len(list(Path("bucket/logs").glob("*"))) if Path("bucket/logs").exists() else 0
    
    return {
        "bhiv_core": "operational",
        "bucket_files": bucket_files,
        "feedback_logs": log_files,
        "ai_client": "ready",
        "authenticated_user": current_user.username
    }

@app.get("/metrics")
def get_metrics(current_user: User = Depends(get_current_active_user)):
    """Get platform metrics"""
    with sqlite3.connect(DBPATH) as conn:
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM videos")
        video_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM ratings")
        rating_count = cur.fetchone()[0]
        
        cur.execute("SELECT AVG(rating) FROM ratings")
        avg_rating = cur.fetchone()[0] or 0
    
    bucket_files = len(list(Path("bucket").glob("**/*"))) if Path("bucket").exists() else 0
    
    return {
        "videos_generated": video_count,
        "total_ratings": rating_count,
        "average_rating": round(avg_rating, 2),
        "bucket_files": bucket_files,
        "system_status": "operational"
    }

@app.get("/admin/users")
async def list_users(current_user: User = Depends(require_admin)):
    """List all users (admin only)"""
    users = []
    for username, user_data in auth_manager.users_db.items():
        users.append({
            "id": user_data["id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "roles": user_data["roles"],
            "is_active": user_data["is_active"],
            "created_at": user_data["created_at"].isoformat(),
            "last_login": user_data["last_login"].isoformat() if user_data["last_login"] else None
        })
    return users

@app.get("/analytics/video/{vid}")
async def get_video_analytics(
    vid: str,
    current_user: User = Depends(require_user)
):
    """Get detailed video analytics"""
    try:
        from analytics.feedback_analyzer import get_feedback_analyzer
        analyzer = get_feedback_analyzer()
        analytics = analyzer.analyze_video_performance(vid)
        
        return {
            "video_id": analytics.video_id,
            "total_views": analytics.total_views,
            "average_rating": analytics.average_rating,
            "rating_distribution": analytics.rating_distribution,
            "engagement_score": analytics.engagement_score,
            "improvement_suggestions": analytics.improvement_suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {e}")

@app.get("/analytics/platform")
async def get_platform_analytics(
    days: int = 30,
    current_user: User = Depends(require_user)
):
    """Get platform-wide analytics"""
    try:
        from analytics.feedback_analyzer import get_feedback_analyzer
        analyzer = get_feedback_analyzer()
        return analyzer.get_platform_analytics(days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {e}")

@app.get("/")
async def serve_frontend():
    """Serve frontend application"""
    return FileResponse("frontend/index.html")
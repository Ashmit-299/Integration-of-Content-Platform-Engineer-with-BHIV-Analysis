# Minimal working server with auto-login
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Cookie, Header
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid, shutil, sqlite3, os
from auth_manager import auth_manager
from typing import Optional

app = FastAPI(title="BHIV Gurukul Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA = Path("data")
VIDEOS = DATA / "videos"
DBPATH = DATA / "meta.db"
os.makedirs(VIDEOS, exist_ok=True)
os.makedirs(DATA, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DBPATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (id TEXT PRIMARY KEY, title TEXT, storyboard_path TEXT, video_path TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ratings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, video_id TEXT, rating INTEGER, comment TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "bhiv-gurukul-platform"}

@app.get("/status")
def system_status():
    return {
        "platform": "operational",
        "bhiv_integration": "active",
        "bucket_storage": "ready",
        "endpoints": ["/upload", "/health", "/status"]
    }

# Authentication endpoints
@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Login endpoint"""
    result = auth_manager.login(username, password)
    if result["success"]:
        response = JSONResponse(content=result)
        response.set_cookie(
            key="session_id", 
            value=result["session_id"], 
            max_age=7*24*3600,  # 7 days
            httponly=True
        )
        return response
    else:
        raise HTTPException(status_code=401, detail=result["message"])

@app.post("/auth/register")
async def register(username: str = Form(...), password: str = Form(...)):
    """Register endpoint"""
    result = auth_manager.register(username, password)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@app.get("/auth/me")
async def get_current_user(
    session_id: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    """Get current user with auto-login"""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    
    user = auth_manager.auto_login(session_id=session_id, token=token)
    if user:
        return user
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")

@app.post("/auth/logout")
async def logout(session_id: Optional[str] = Cookie(None)):
    """Logout endpoint"""
    if session_id:
        result = auth_manager.logout(session_id)
        response = JSONResponse(content=result)
        response.delete_cookie("session_id")
        return response
    return {"success": True, "message": "Already logged out"}

# Helper function to get current user
async def get_current_user_optional(
    session_id: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
) -> Optional[dict]:
    """Get current user without raising exception"""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    
    return auth_manager.auto_login(session_id=session_id, token=token)

@app.post("/upload")
async def upload_script(
    file: UploadFile = File(...),
    session_id: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    """Upload with auto-login check"""
    user = await get_current_user_optional(session_id, authorization)
    
    if not file.filename.endswith((".txt", ".md")):
        raise HTTPException(status_code=400, detail="Only .txt or .md files accepted")

    vid = str(uuid.uuid4())
    temp_path = Path("temp") / file.filename
    temp_path.parent.mkdir(exist_ok=True)
    
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Simple processing - just save to database
    conn = sqlite3.connect(DBPATH)
    c = conn.cursor()
    c.execute("INSERT INTO videos (id, title, storyboard_path, video_path) VALUES (?,?,?,?)",
              (vid, file.filename, str(temp_path), ""))
    conn.commit()
    conn.close()
    
    message = f"File uploaded by {user['username']}" if user else "File uploaded (guest)"
    return {"id": vid, "message": message, "user": user}

@app.get("/")
async def root(
    session_id: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    """Root endpoint with auto-login detection"""
    user = await get_current_user_optional(session_id, authorization)
    
    if user:
        return {
            "message": f"Welcome back, {user['username']}!",
            "platform": "BHIV Gurukul Platform",
            "status": "authenticated",
            "docs": "/docs",
            "user": user
        }
    else:
        return {
            "message": "BHIV Gurukul Platform is running",
            "status": "guest",
            "docs": "/docs",
            "login": "/auth/login"
        }
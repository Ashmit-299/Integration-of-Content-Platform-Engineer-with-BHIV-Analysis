# backend/server.py (Full File - Paste Exactly)
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from video.feedback_adapter import adapt_storyboard
import uuid, shutil, json, sqlite3, os
from video.storyboard import generate_storyboard_from_file
import time
from datetime import datetime


app = FastAPI(title="Gurukul Content Platform MVP")


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


class UploadResponse(BaseModel):
    id: str
    message: str


@app.post("/upload", response_model=UploadResponse)
async def upload_script(file: UploadFile = File(...)):
    if not file.filename.endswith((".txt", ".md")):
        raise HTTPException(status_code=400, detail="Only .txt or .md files accepted")

    vid = str(uuid.uuid4())[:8]
    script_path = DATA / f"{vid}_script.txt"
    with open(script_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    storyboard_path = DATA / f"{vid}_storyboard.json"

    # Lazy import with detailed error handling
    try:
        from video.generator import render_video_from_storyboard
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cannot import 'render_video_from_storyboard' from 'video.generator'. Check for syntax errors or missing function in the file. Original error: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=("Server is missing the video backend (imageio) or generator import failed. "
                    "Install imageio and its dependencies: python -m pip install imageio[ffmpeg] pillow numpy. "
                    f"Import error: {e}")
        )

    start_time = time.time()
    try:
        sb = generate_storyboard_from_file(script_path, storyboard_path)
        video_path = render_video_from_storyboard(sb, out_path=str(VIDEOS / f"{vid}.mp4"))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {e}")

    conn = sqlite3.connect(DBPATH)
    c = conn.cursor()
    c.execute("INSERT INTO videos (id, title, storyboard_path, video_path) VALUES (?,?,?,?)",
              (vid, sb.get("title", ""), str(storyboard_path), str(video_path)))
    conn.commit()
    # After conn.commit() in /upload
    run_log = {
        "video_id": vid,
        "title": sb.get("title", ""),
        "generated_at": datetime.now().isoformat(),
        "scene_count": len(sb["scenes"]),
        "generation_time_secs": time.time() - start_time,  # Add start_time = time.time() before rendering
        "initial_ratings_summary": []  # Populated later via /rate
    }
    log_dir = Path("reports/runs")
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{vid}.json").write_text(json.dumps(run_log, indent=2))
    conn.close()
    return {"id": vid, "message": "Uploaded and processed"}


@app.get("/generate/{vid}")
def generate_by_id(vid: str):
    from video.generator import render_video_from_storyboard
    conn = sqlite3.connect(DBPATH)
    c = conn.cursor()
    c.execute("SELECT storyboard_path, video_path FROM videos WHERE id=?", (vid,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Video not found")
    storyboard_path, video_path = row
    
    # Load and adapt storyboard based on feedback
    import json
    from pathlib import Path
    storyboard = json.loads(Path(storyboard_path).read_text(encoding="utf-8"))
    storyboard = adapt_storyboard(storyboard, vid)
    
    try:
        new_video = render_video_from_storyboard(storyboard, out_path=video_path)
        return {"id": vid, "video": new_video}
    except Exception as e:
        raise HTTPException(500, f"Error generating video: {str(e)}")



@app.get("/stream/{vid}")
def stream_video(vid: str):
    path = VIDEOS / f"{vid}.mp4"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(path, media_type="video/mp4", filename=path.name)


@app.post("/rate/{vid}")
async def rate_video(vid: str, rating: int = Form(...), comment: str = Form("")):
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="rating must be 1..5")
    conn = sqlite3.connect(DBPATH)
    c = conn.cursor()
    c.execute("INSERT INTO ratings (video_id, rating, comment) VALUES (?,?,?)", (vid, rating, comment))
    conn.commit()
    # After conn.commit() in /rate
    log_path = Path(f"reports/runs/{vid}.json")
    if log_path.exists():
        log = json.loads(log_path.read_text())
        c.execute("SELECT AVG(rating) FROM ratings WHERE video_id=?", (vid,))
        log["initial_ratings_summary"] = {"average": c.fetchone() or 0}
        log_path.write_text(json.dumps(log, indent=2))
    conn.close()
    return {"message": "Thanks for rating"}



@app.get("/logs")
def get_logs():
    """
    Return both the plain-text daily log and a ratings summary
    aggregated from the SQLite DB.
    """
    # --- 1) Plain-text daily log ------------------------------------------
    log_file = Path("reports/daily_log.txt")
    daily_log_content = log_file.read_text() if log_file.exists() else ""


    # --- 2) Ratings summary -----------------------------------------------
    conn = sqlite3.connect(DBPATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title FROM videos")
    videos = cur.fetchall()


    ratings_summary = []
    for vid, title in videos:
        cur.execute("SELECT AVG(rating) FROM ratings WHERE video_id=?", (vid,))
        avg = cur.fetchone()
        ratings_summary.append(
            {
                "video_id": vid,
                "title": title,
                "average_rating": round(avg or 0, 2)  # 0 if None
            }
        )


    conn.close()


    # --- 3) Combined response ---------------------------------------------
    return {
        "daily_log": daily_log_content,
        "ratings_summary": ratings_summary
    }

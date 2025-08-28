# ── video/feedback_adapter.py ──────────────────────────────────────────
import sqlite3
from pathlib import Path
import json

DBPATH       = Path("data/meta.db")          # same DB your server uses
WEIGHTS_PATH = Path("data/weights.json")     # optional – stores last rating

def get_average_rating(video_id: str) -> float:
    """Return the mean rating (1-5). 3.0 if no ratings yet."""
    conn = sqlite3.connect(DBPATH)
    cur  = conn.cursor()
    cur.execute("SELECT AVG(rating) FROM ratings WHERE video_id=?", (video_id,))
    avg = cur.fetchone()[0] or 3.0      # None → 3.0
    conn.close()
    return avg

def adapt_storyboard(storyboard: dict, video_id: str) -> dict:
    """
    Primitive feedback loop:
    - If a video's average rating is <3, shorten every scene by 1 s (min 2 s).
    - Save the last average rating in data/weights.json for simple tracking.
    """
    avg_rating = get_average_rating(video_id)

    if avg_rating < 3:
        for scene in storyboard["scenes"]:
            scene["duration_secs"] = max(2, scene["duration_secs"] - 1)

    # (optional) persist simple metadata for future research
    WEIGHTS_PATH.write_text(json.dumps({"last_avg_rating": avg_rating}))

    return storyboard
# ───────────────────────────────────────────────────────────────────────

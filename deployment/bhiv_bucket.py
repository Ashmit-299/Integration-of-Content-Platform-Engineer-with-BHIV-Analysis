# bhiv_bucket.py
from pathlib import Path
import shutil
import os
import json
from typing import Optional

BUCKET_ROOT = Path(os.getenv("BHIV_BUCKET_PATH", "bucket"))

def init_bucket():
    for p in ["scripts","storyboards","videos","logs","ratings","tmp"]:
        (BUCKET_ROOT / p).mkdir(parents=True, exist_ok=True)

def save_script(local_path: str, dest_name: Optional[str]=None) -> str:
    init_bucket()
    dest_name = dest_name or Path(local_path).name
    dest = BUCKET_ROOT / "scripts" / dest_name
    shutil.copy(local_path, dest)
    return str(dest)

def save_storyboard(storyboard_dict, filename: str) -> str:
    init_bucket()
    out = BUCKET_ROOT / "storyboards" / filename
    out.write_text(json.dumps(storyboard_dict, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(out)

def save_video(local_video_path: str, filename: Optional[str]=None) -> str:
    init_bucket()
    filename = filename or Path(local_video_path).name
    dest = BUCKET_ROOT / "videos" / filename
    shutil.copy(local_video_path, dest)
    return str(dest)

def read_storyboard(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))
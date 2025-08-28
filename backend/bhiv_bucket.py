import os
from pathlib import Path

def init_bucket():
    """Initialize bucket directory"""
    bucket_path = Path("bucket")
    bucket_path.mkdir(exist_ok=True)
    return str(bucket_path)

def save_script(source_path, bucket_key):
    """Save script to bucket"""
    bucket_path = Path("bucket")
    bucket_path.mkdir(exist_ok=True)
    
    source = Path(source_path)
    dest = bucket_path / bucket_key
    
    if source.exists():
        dest.write_text(source.read_text())
        return str(dest)
    return None

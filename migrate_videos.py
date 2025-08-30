#!/usr/bin/env python3
"""
Script to migrate existing videos from file system to database and fix video display issues.
"""

import sqlite3
import os
import glob
from pathlib import Path
from datetime import datetime

def migrate_videos():
    """Migrate existing videos from file system to database"""
    
    # Database path
    db_path = "data/app.db"
    
    # Video directories to check
    video_dirs = [
        "data/videos",
        "bucket/videos"
    ]
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get existing video IDs from database
    c.execute("SELECT id FROM videos")
    existing_ids = {row[0] for row in c.fetchall()}
    
    print(f"Found {len(existing_ids)} videos in database")
    
    # Scan for video files
    video_files = []
    for video_dir in video_dirs:
        if os.path.exists(video_dir):
            pattern = os.path.join(video_dir, "*.mp4")
            files = glob.glob(pattern)
            video_files.extend(files)
            print(f"Found {len(files)} videos in {video_dir}")
    
    # Process each video file
    added_count = 0
    for video_file in video_files:
        # Extract video ID from filename
        filename = os.path.basename(video_file)
        video_id = filename.replace('.mp4', '')
        
        # Skip if already in database
        if video_id in existing_ids:
            continue
        
        # Look for corresponding script file
        script_content = ""
        script_paths = [
            f"data/{video_id}_script.txt",
            f"bucket/scripts/{video_id}_script.txt"
        ]
        
        for script_path in script_paths:
            if os.path.exists(script_path):
                with open(script_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                break
        
        # Generate title from script content or use video ID
        if script_content:
            lines = script_content.split('\n')
            title = lines[0].replace('Title:', '').strip() if lines and 'Title:' in lines[0] else f"Video {video_id}"
        else:
            title = f"Video {video_id}"
        
        # Look for storyboard file
        storyboard_path = ""
        storyboard_paths = [
            f"data/storyboards/{video_id}_storyboard.json",
            f"bucket/storyboards/{video_id}_storyboard.json"
        ]
        
        for path in storyboard_paths:
            if os.path.exists(path):
                storyboard_path = path
                break
        
        # Insert into database
        c.execute("""
            INSERT INTO videos (id, title, content, video_path, storyboard_path, created_at) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            video_id,
            title,
            script_content,
            video_file,
            storyboard_path,
            datetime.now().isoformat()
        ))
        
        added_count += 1
        print(f"Added video: {video_id} - {title}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"\nMigration complete! Added {added_count} new videos to database.")
    
    # Display summary
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM videos")
    total_videos = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ratings")
    total_ratings = c.fetchone()[0]
    conn.close()
    
    print(f"Total videos in database: {total_videos}")
    print(f"Total ratings in database: {total_ratings}")

if __name__ == "__main__":
    migrate_videos()
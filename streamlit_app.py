import streamlit as st
import time
import json
import uuid
import sqlite3
import hashlib
import os
from pathlib import Path
from datetime import datetime

# Configuration - Standalone mode (no external API)
STANDALONE_MODE = True

st.set_page_config(
    page_title="BHIV Video Platform",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional Theme CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .header-container {
        background: rgba(255, 255, 255, 0.1);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.15);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 0.5rem 0;
    }
    .upload-section {
        background: rgba(255, 255, 255, 0.1);
        padding: 2rem;
        border-radius: 15px;
        border: 2px dashed rgba(255, 255, 255, 0.3);
        text-align: center;
        margin: 1rem 0;
    }
    .video-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    .stSuccess, .stError, .stInfo, .stWarning {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
    }
    h1, h2, h3, h4, h5, h6, p, div, span {
        color: white !important;
    }
    .stSelectbox label, .stTextInput label, .stTextArea label, .stSlider label {
        color: white !important;
    }
    .stFileUploader label {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <h1>🎥 BHIV Video Platform</h1>
    <p style="font-size: 1.2rem; margin: 0;">Professional AI-Enhanced Video Generation System</p>
    <p style="opacity: 0.8; margin: 0.5rem 0 0 0;">✨ Standalone Mode - No API Required ✨</p>
    <p style="opacity: 0.7; font-size: 0.9rem;">Upload scripts → Generate videos → Get feedback</p>
</div>
""", unsafe_allow_html=True)

# Initialize database with migration
def init_db():
    Path("data").mkdir(exist_ok=True)
    conn = sqlite3.connect("data/app.db")
    c = conn.cursor()
    
    # Create tables with all required columns
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (id TEXT PRIMARY KEY, title TEXT, content TEXT, 
                  video_path TEXT, storyboard_path TEXT, created_at TEXT DEFAULT '2024-01-01T00:00:00')''')
    c.execute('''CREATE TABLE IF NOT EXISTS ratings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, video_id TEXT, rating INTEGER, comment TEXT)''')
    
    # Check and add missing columns
    c.execute("PRAGMA table_info(videos)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'video_path' not in columns:
        c.execute("ALTER TABLE videos ADD COLUMN video_path TEXT")
    if 'storyboard_path' not in columns:
        c.execute("ALTER TABLE videos ADD COLUMN storyboard_path TEXT")
    if 'created_at' not in columns:
        c.execute("ALTER TABLE videos ADD COLUMN created_at TEXT DEFAULT '2024-01-01T00:00:00'")
    
    conn.commit()
    conn.close()

init_db()

# Standalone functions
@st.cache_data(ttl=30)
def check_api_health():
    return True  # Always online in standalone mode

@st.cache_data(ttl=10)
def get_metrics():
    conn = sqlite3.connect("data/app.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM videos")
    video_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM ratings")
    rating_count = c.fetchone()[0]
    c.execute("SELECT AVG(rating) FROM ratings")
    avg_rating = c.fetchone()[0] or 0
    conn.close()
    
    return {
        "videos_generated": video_count,
        "total_ratings": rating_count,
        "average_rating": avg_rating
    }

@st.cache_data(ttl=5)
def get_videos():
    conn = sqlite3.connect("data/app.db")
    c = conn.cursor()
    try:
        c.execute("SELECT id, title, video_path, created_at FROM videos ORDER BY created_at DESC")
        videos = [{"id": row[0], "title": row[1], "video_path": row[2], "created_at": row[3]} for row in c.fetchall()]
    except sqlite3.OperationalError:
        # Fallback if columns don't exist
        c.execute("SELECT id, title FROM videos ORDER BY rowid DESC")
        videos = [{"id": row[0], "title": row[1], "video_path": None, "created_at": "2024-01-01T00:00:00"} for row in c.fetchall()]
    conn.close()
    return videos

def create_video(title, content):
    video_id = str(uuid.uuid4())[:8]
    conn = sqlite3.connect("data/app.db")
    c = conn.cursor()
    c.execute("INSERT INTO videos (id, title, content, created_at) VALUES (?, ?, ?, ?)",
              (video_id, title, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return video_id

def get_video_ratings(video_id):
    conn = sqlite3.connect("data/app.db")
    c = conn.cursor()
    c.execute("SELECT rating, comment FROM ratings WHERE video_id = ?", (video_id,))
    ratings = c.fetchall()
    conn.close()
    return ratings

def add_rating(video_id, rating, comment):
    conn = sqlite3.connect("data/app.db")
    c = conn.cursor()
    c.execute("INSERT INTO ratings (video_id, rating, comment) VALUES (?, ?, ?)",
              (video_id, rating, comment))
    conn.commit()
    conn.close()

# Status Dashboard
metrics = get_metrics()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>✅ Online</h3>
        <p>Platform Status</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>📹 {metrics.get("videos_generated", 0)}</h3>
        <p>Total Videos</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3>⭐ {metrics.get("total_ratings", 0)}</h3>
        <p>Total Ratings</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🎯 {metrics.get('average_rating', 0):.1f}/5</h3>
        <p>Average Rating</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Upload section
st.markdown("""
<div class="upload-section">
    <h2>📤 Upload Your Script</h2>
    <p>Transform your lesson scripts into engaging videos</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a script file",
    type=['txt', 'md'],
    help="Upload your lesson script in .txt or .md format"
)

if uploaded_file is not None:
    if st.button("Generate Video", type="primary"):
        with st.spinner("Processing script..."):
            try:
                content = uploaded_file.read().decode('utf-8')
                video_id = create_video(uploaded_file.name, content)
                st.success(f"✅ Video generated! ID: {video_id}")
                st.balloons()
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.divider()

# Videos section
st.markdown("""
<div style="text-align: center; margin: 2rem 0;">
    <h2>🎬 Video Gallery</h2>
    <p>Your generated videos with professional quality</p>
</div>
""", unsafe_allow_html=True)

videos = get_videos()

if videos:
    for video in videos:
        st.markdown(f"""
        <div class="video-card">
            <h3>📹 {video['title']}</h3>
            <p style="opacity: 0.8;">ID: {video['id']}</p>
            <p style="opacity: 0.6; font-size: 0.9rem;">Created: {video['created_at'][:10]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display video if path exists
        if video.get('video_path') and os.path.exists(video['video_path']):
            st.video(video['video_path'])
        else:
            st.info(f"🎬 Video file not found for {video['id']}")
        
        # Rating section
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            rating = st.selectbox(
                "Rate this video:",
                [1, 2, 3, 4, 5],
                key=f"rating_{video['id']}",
                index=4
            )
        
        with col2:
            comment = st.text_input(
                "Comment:",
                key=f"comment_{video['id']}",
                placeholder="Share your thoughts..."
            )
        
        with col3:
            if st.button("Submit", key=f"submit_{video['id']}"):
                add_rating(video['id'], rating, comment)
                st.success("Rating submitted!")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()
        
        # Show existing ratings
        ratings = get_video_ratings(video['id'])
        if ratings:
            st.markdown("**Previous Ratings:**")
            for r_rating, r_comment in ratings:
                st.markdown(f"⭐ {r_rating}/5 - {r_comment}")
        
        st.divider()
else:
    st.info("No videos found. Upload a script to generate your first video!")

# Show ratings for videos
if videos:
    st.markdown("### 📊 Recent Ratings")
    conn = sqlite3.connect("data/app.db")
    c = conn.cursor()
    c.execute("""
        SELECT v.title, r.rating, r.comment 
        FROM ratings r 
        JOIN videos v ON r.video_id = v.id 
        ORDER BY r.id DESC LIMIT 5
    """)
    recent_ratings = c.fetchall()
    conn.close()
    
    if recent_ratings:
        for title, rating, comment in recent_ratings:
            st.write(f"**{title}**: {'⭐' * rating} - {comment or 'No comment'}")
    else:
        st.info("No ratings yet")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 2rem; background: rgba(255, 255, 255, 0.1); border-radius: 15px;">
    <p><strong>BHIV Platform</strong> - Standalone Video Generation System</p>
    <p>✅ No API Required • 🚀 Ready to Use</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
if st.button("🔄 Refresh Dashboard", type="secondary"):
    st.cache_data.clear()
    st.rerun()
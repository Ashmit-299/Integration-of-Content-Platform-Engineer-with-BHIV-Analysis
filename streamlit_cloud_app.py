import streamlit as st
import sqlite3
import uuid
from pathlib import Path
import os
import json
import hashlib
import requests
from datetime import datetime

# Streamlit Cloud Configuration
st.set_page_config(
    page_title="BHIV Platform", 
    page_icon="🎥", 
    layout="wide"
)

# Initialize directories
@st.cache_resource
def init_app():
    dirs = ['bucket', 'bucket/videos', 'bucket/scripts', 'data']
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    db_path = Path("data/meta.db")
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS videos
                     (id TEXT PRIMARY KEY, title TEXT, created_at TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_ratings
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, video_id TEXT, 
                      rating INTEGER, comment TEXT, UNIQUE(user_id, video_id))''')
        conn.commit()

init_app()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(username, password):
    with sqlite3.connect("data/meta.db") as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", 
                  (username, hash_password(password)))
        result = c.fetchone()
        return result[0] if result else None

def register_user(username, password):
    user_id = str(uuid.uuid4())[:8]
    try:
        with sqlite3.connect("data/meta.db") as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (id, username, password_hash) VALUES (?,?,?)",
                      (user_id, username, hash_password(password)))
            conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None

def create_mock_video(video_id, title):
    """Create a mock video for demo purposes"""
    video_path = Path(f"bucket/videos/{video_id}.mp4")
    
    # Create a simple text file as placeholder
    with open(video_path, 'w') as f:
        f.write(f"Mock video content for: {title}\nVideo ID: {video_id}")
    
    # Save to database
    with sqlite3.connect("data/meta.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO videos (id, title, created_at) VALUES (?,?,?)",
                  (video_id, title, datetime.now().isoformat()))
        conn.commit()

# Modern UI Theme
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .main-header {
        background: rgba(255, 255, 255, 0.1);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.15);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        backdrop-filter: blur(10px);
        margin: 0.5rem 0;
    }
    .stButton > button {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
    h1, h2, h3, h4, h5, h6, p, div, span, label { color: white !important; }
</style>
""", unsafe_allow_html=True)

# Authentication
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

if not st.session_state.user_id:
    st.markdown("""
    <div class="main-header">
        <h1>🔐 Welcome to BHIV Platform</h1>
        <p>Professional AI-Enhanced Video Generation System</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user_id = login_user(username, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.success("Logged in!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("register"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            if st.form_submit_button("Register"):
                user_id = register_user(new_username, new_password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.session_state.username = new_username
                    st.success("Registered and logged in!")
                    st.rerun()
                else:
                    st.error("Username already exists")
    st.stop()

# Main App
st.markdown("""
<div class="main-header">
    <h1>🎥 BHIV Video Platform</h1>
    <p>Professional AI-Enhanced Video Generation System</p>
</div>
""", unsafe_allow_html=True)

# User controls
col1, col2 = st.columns([5, 1])
with col1:
    st.markdown("### 🚀 Transform Scripts into Professional Videos")
with col2:
    st.markdown(f'<span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 15px; color: white;">👤 {st.session_state.username}</span>', unsafe_allow_html=True)
    if st.button("🚪", help="Logout"):
        st.session_state.clear()
        st.rerun()

# Metrics
@st.cache_data(ttl=5)
def get_metrics():
    with sqlite3.connect("data/meta.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM videos")
        video_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM user_ratings")
        rating_count = cur.fetchone()[0]
        cur.execute("SELECT AVG(rating) FROM user_ratings")
        avg_rating = cur.fetchone()[0] or 0
    return video_count, rating_count, avg_rating

video_count, rating_count, avg_rating = get_metrics()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>📹 {video_count}</h3>
        <p>Total Videos</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>⭐ {rating_count}</h3>
        <p>Total Ratings</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🎯 {avg_rating:.1f}/5</h3>
        <p>Avg Rating</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Upload Section
st.markdown("""
<div style="background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 15px; text-align: center; margin: 1rem 0;">
    <h2>📤 Upload Your Script</h2>
    <p>Transform your lesson scripts into engaging videos</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose script file", type=['txt', 'md'])

if uploaded_file and st.button("Generate Video", type="primary"):
    video_id = str(uuid.uuid4())[:8]
    
    with st.spinner("Generating video..."):
        try:
            # Save script
            script_path = Path(f"bucket/scripts/{video_id}_script.txt")
            script_path.write_text(uploaded_file.read().decode())
            
            # Create mock video (in real app, this would be actual video generation)
            create_mock_video(video_id, uploaded_file.name)
            
            st.success(f"✅ Video generated! ID: {video_id}")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Video generation failed: {str(e)}")
    
    st.rerun()

st.divider()

# Video Gallery
st.markdown("""
<div style="text-align: center; margin: 2rem 0;">
    <h2>🎬 Video Gallery</h2>
    <p>Your generated videos with professional quality</p>
</div>
""", unsafe_allow_html=True)

with sqlite3.connect("data/meta.db") as conn:
    cur = conn.cursor()
    cur.execute("SELECT id, title, created_at FROM videos ORDER BY created_at DESC")
    videos = cur.fetchall()

if videos:
    for video_id, title, created_at in videos:
        with st.expander(f"📹 {title} (ID: {video_id})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.info("🎬 Video Preview (Demo Mode)")
                st.write(f"**Title:** {title}")
                st.write(f"**Created:** {created_at}")
                st.write(f"**Video ID:** {video_id}")
                
                # Show script content if available
                script_path = Path(f"bucket/scripts/{video_id}_script.txt")
                if script_path.exists():
                    with st.expander("📝 View Script"):
                        st.text(script_path.read_text()[:500] + "...")
            
            with col2:
                # Ratings
                with sqlite3.connect("data/meta.db") as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT rating, comment FROM user_ratings WHERE video_id = ?", (video_id,))
                    video_ratings = cur.fetchall()
                    
                    cur.execute("SELECT 1 FROM user_ratings WHERE user_id = ? AND video_id = ?", 
                               (st.session_state.user_id, video_id))
                    has_rated = cur.fetchone() is not None
                
                if video_ratings:
                    st.write(f"📊 **{len(video_ratings)} ratings:**")
                    for r, c in video_ratings[:3]:
                        st.write(f"⭐ {r}/5 - {c if c else 'No comment'}")
                else:
                    st.write("📊 No ratings yet")
                
                if has_rated:
                    st.info("✅ You have already rated this video")
                else:
                    st.markdown("#### ⭐ Rate This Video")
                    rating = st.select_slider(
                        "Your Rating", 
                        options=[1,2,3,4,5], 
                        value=3, 
                        key=f"rating_{video_id}",
                        format_func=lambda x: "⭐" * x
                    )
                    comment = st.text_area(
                        "Your Feedback", 
                        placeholder="Share your thoughts...", 
                        key=f"comment_{video_id}",
                        height=80
                    )
                    
                    if st.button("🚀 Submit Rating", key=f"submit_{video_id}", type="primary"):
                        try:
                            with sqlite3.connect("data/meta.db") as conn:
                                c = conn.cursor()
                                c.execute("INSERT INTO user_ratings (user_id, video_id, rating, comment) VALUES (?,?,?,?)",
                                          (st.session_state.user_id, video_id, rating, comment))
                                conn.commit()
                            
                            st.success("✅ Rating submitted successfully!")
                            st.balloons()
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to save rating: {str(e)}")
else:
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: rgba(255,255,255,0.1); border-radius: 10px;">
        <h3>🎬 No Videos Yet</h3>
        <p>Upload your first script to create professional videos</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 2rem; background: rgba(255,255,255,0.1); border-radius: 10px;">
    <p><strong>BHIV Platform</strong> - Professional Video Generation System</p>
    <p>Powered by AI • Built for Excellence • Demo Mode</p>
</div>
""", unsafe_allow_html=True)

if st.button("🔄 Refresh Dashboard", type="secondary"):
    st.cache_data.clear()
    st.rerun()
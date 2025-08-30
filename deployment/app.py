import streamlit as st
import sqlite3
import uuid
from pathlib import Path
import os
import json
import sys
import hashlib
import asyncio
# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from video.storyboard import generate_storyboard_from_file
    from video.generator import render_video_from_storyboard
    from bhiv_lm_client import get_lm_client
    from analytics.advanced_analytics import get_analytics
    from security.config import config
except ImportError as e:
    st.error(f"Import error: {e}. Please ensure all modules are available.")
    st.stop()

# Setup
BUCKET = Path("bucket")
VIDEOS = BUCKET / "videos"
STORYBOARDS = BUCKET / "storyboards"
DBPATH = Path("data") / "meta.db"

def init_db():
    os.makedirs(BUCKET, exist_ok=True)
    os.makedirs(VIDEOS, exist_ok=True)
    os.makedirs(STORYBOARDS, exist_ok=True)
    os.makedirs(Path("data"), exist_ok=True)
    
    with sqlite3.connect(DBPATH) as conn:
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in c.fetchall()]
        
        if 'users' not in tables:
            c.execute('''CREATE TABLE users
                         (id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)''')
        
        if 'user_ratings' not in tables:
            c.execute('''CREATE TABLE user_ratings
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, video_id TEXT, rating INTEGER, comment TEXT,
                          UNIQUE(user_id, video_id))''')
        conn.commit()

init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(username, password):
    with sqlite3.connect(DBPATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", 
                  (username, hash_password(password)))
        result = c.fetchone()
        return result[0] if result else None

def register_user(username, password):
    user_id = str(uuid.uuid4())[:8]
    try:
        with sqlite3.connect(DBPATH) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (id, username, password_hash) VALUES (?,?,?)",
                      (user_id, username, hash_password(password)))
            conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None

def has_user_rated(user_id, video_id):
    with sqlite3.connect(DBPATH) as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM user_ratings WHERE user_id = ? AND video_id = ?", (user_id, video_id))
        return c.fetchone() is not None

# Streamlit App
st.set_page_config(
    page_title="BHIV Platform", 
    page_icon="🎥", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Force dark theme
if 'dark_theme' not in st.session_state:
    st.session_state.dark_theme = True

# Professional Modern Theme
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-header {
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
    .user-badge {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        color: white;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        display: inline-block;
        backdrop-filter: blur(10px);
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
    .stButton > button[kind="primary"] {
        background: linear-gradient(45deg, #28a745, #20c997);
    }
    .stButton > button[kind="secondary"] {
        background: linear-gradient(45deg, #6c757d, #495057);
    }
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: white !important;
    }
    .stSelectbox label, .stTextInput label, .stTextArea label, .stSlider label {
        color: white !important;
    }
    .stFileUploader label {
        color: white !important;
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
    .stExpander {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
    }
    .stForm {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Authentication
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

# Check for saved login
if not st.session_state.user_id:
    saved_user = st.query_params.get('user_id')
    saved_username = st.query_params.get('username')
    if saved_user and saved_username:
        with sqlite3.connect(DBPATH) as conn:
            c = conn.cursor()
            c.execute("SELECT username FROM users WHERE id = ?", (saved_user,))
            result = c.fetchone()
            if result and result[0] == saved_username:
                st.session_state.user_id = saved_user
                st.session_state.username = saved_username

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
                    st.query_params.user_id = user_id
                    st.query_params.username = username
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
                    st.query_params.user_id = user_id
                    st.query_params.username = new_username
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

# Controls
col1, col2 = st.columns([5, 1])
with col1:
    st.markdown("### 🚀 Transform Scripts into Professional Videos")
with col2:
    st.markdown(f'<span class="user-badge">👤 {st.session_state.username}</span>', unsafe_allow_html=True)
    if st.button("🚪", help="Logout"):
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()

# Enhanced Metrics with Analytics
@st.cache_data(ttl=5)
def get_metrics():
    with sqlite3.connect(DBPATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM videos")
        video_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM user_ratings")
        rating_count = cur.fetchone()[0]
        cur.execute("SELECT AVG(rating) FROM user_ratings")
        avg_rating = cur.fetchone()[0] or 0
    
    # Get advanced analytics
    analytics = get_analytics()
    trends = analytics.get_rating_trends()
    sentiment = analytics.get_sentiment_analysis()
    
    return {
        'basic': (video_count, rating_count, avg_rating),
        'trends': trends,
        'sentiment': sentiment
    }

metrics_data = get_metrics()
video_count, rating_count, avg_rating = metrics_data['basic']
trends = metrics_data['trends']
sentiment = metrics_data['sentiment']

# Enhanced metrics display
col1, col2, col3, col4 = st.columns(4)
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
    trend_icon = "📈" if trends.get('trend') == 'improving' else "📉" if trends.get('trend') == 'declining' else "➡️"
    st.markdown(f"""
    <div class="metric-card">
        <h3>{trend_icon} {avg_rating:.1f}/5</h3>
        <p>Avg Rating ({trends.get('trend', 'stable')})</p>
    </div>
    """, unsafe_allow_html=True)
with col4:
    sentiment_total = sentiment.get('total_analyzed', 0)
    positive_pct = (sentiment.get('sentiment_distribution', {}).get('positive', 0) / max(sentiment_total, 1)) * 100
    st.markdown(f"""
    <div class="metric-card">
        <h3>😊 {positive_pct:.0f}%</h3>
        <p>Positive Sentiment</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Upload
st.markdown("""
<div class="upload-section">
    <h2>📤 Upload Your Script</h2>
    <p>Transform your lesson scripts into engaging videos</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose script file", 
    type=['txt', 'md'],
    help="Upload .txt or .md files containing your lesson content"
)

if uploaded_file and st.button("Generate Video", type="primary"):
    video_id = str(uuid.uuid4())[:8]
    content = uploaded_file.read().decode()
    
    with st.spinner("Generating video..."):
        try:
            script_path = Path("temp") / f"{video_id}_script.txt"
            script_path.parent.mkdir(exist_ok=True)
            script_path.write_text(content)
            
            storyboard_path = STORYBOARDS / f"{video_id}_storyboard.json"
            storyboard = generate_storyboard_from_file(script_path, storyboard_path)
            
            video_path = VIDEOS / f"{video_id}.mp4"
            render_video_from_storyboard(storyboard, str(video_path))
            
            with sqlite3.connect(DBPATH) as conn:
                c = conn.cursor()
                c.execute("PRAGMA table_info(videos)")
                columns = [col[1] for col in c.fetchall()]
                
                if 'storyboard_path' in columns and 'video_path' in columns:
                    c.execute("INSERT INTO videos (id, title, storyboard_path, video_path) VALUES (?,?,?,?)",
                              (video_id, uploaded_file.name, str(storyboard_path), str(video_path)))
                else:
                    c.execute("INSERT INTO videos (id, title) VALUES (?,?)",
                              (video_id, uploaded_file.name))
                conn.commit()
            
            st.success(f"✅ Video generated! ID: {video_id}")
            st.balloons()
            script_path.unlink()
            
        except Exception as e:
            st.error(f"❌ Video generation failed: {str(e)}")
    
    st.rerun()

st.divider()

# Videos
st.markdown("""
<div style="text-align: center; margin: 2rem 0;">
    <h2>🎬 Video Gallery</h2>
    <p>Your generated videos with professional quality</p>
</div>
""", unsafe_allow_html=True)

with sqlite3.connect(DBPATH) as conn:
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(videos)")
    columns = [col[1] for col in cur.fetchall()]
    
    if 'video_path' in columns and 'storyboard_path' in columns:
        cur.execute("SELECT id, title, video_path, storyboard_path FROM videos ORDER BY rowid DESC")
        videos = cur.fetchall()
    else:
        cur.execute("SELECT id, title FROM videos ORDER BY rowid DESC")
        video_data = cur.fetchall()
        videos = []
        for vid, title in video_data:
            vpath = VIDEOS / f"{vid}.mp4"
            spath = STORYBOARDS / f"{vid}_storyboard.json"
            videos.append((vid, title, str(vpath) if vpath.exists() else None, str(spath) if spath.exists() else None))

if videos:
    for video_data in videos:
        if len(video_data) == 4:
            video_id, title, video_path, storyboard_path = video_data
        else:
            video_id, title = video_data[:2]
            video_path = str(VIDEOS / f"{video_id}.mp4")
            storyboard_path = str(STORYBOARDS / f"{video_id}_storyboard.json")
        
        with st.expander(f"📹 {title} (ID: {video_id})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                if video_path and Path(video_path).exists():
                    st.video(video_path)
                else:
                    st.warning("⚠️ Video not found")
            
            with col2:
                if storyboard_path and Path(storyboard_path).exists():
                    try:
                        storyboard = json.loads(Path(storyboard_path).read_text())
                        st.info(f"🎨 Storyboard: {len(storyboard.get('scenes', []))} scenes")
                    except:
                        st.info("🎨 Storyboard available")
                
                with sqlite3.connect(DBPATH) as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT rating, comment FROM user_ratings WHERE video_id = ? ORDER BY id DESC", (video_id,))
                    video_ratings = cur.fetchall()
                
                if video_ratings:
                    st.write(f"📊 **{len(video_ratings)} ratings:**")
                    for r, c in video_ratings[:3]:
                        st.write(f"⭐ {r}/5 - {c if c else 'No comment'}")
                else:
                    st.write("📊 No ratings yet")
                
                if has_user_rated(st.session_state.user_id, video_id):
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
                        placeholder="Share your thoughts about this video...", 
                        key=f"comment_{video_id}",
                        height=80
                    )
                    
                    if st.button("🚀 Submit Rating", key=f"submit_{video_id}", type="primary"):
                        try:
                            # Save rating to database
                            with sqlite3.connect(DBPATH) as conn:
                                c = conn.cursor()
                                c.execute("INSERT INTO user_ratings (user_id, video_id, rating, comment) VALUES (?,?,?,?)",
                                          (st.session_state.user_id, video_id, rating, comment))
                                conn.commit()
                            
                            # Analyze feedback with LM client
                            if config['analytics_enabled']:
                                try:
                                    lm_client = get_lm_client()
                                    analysis = asyncio.run(lm_client.analyze_feedback(video_id, rating, comment))
                                    lm_client.log_feedback(video_id, rating, comment, analysis)
                                except Exception as e:
                                    print(f"Analytics error: {e}")
                            
                            st.success("✅ Rating submitted successfully!")
                            st.balloons()
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to save rating: {str(e)}")
else:
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: #21262d; border-radius: 10px; color: #f0f6fc;">
        <h3>🎬 No Videos Yet</h3>
        <p>Upload your first script to create professional videos</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 2rem; background: #30363d; border-radius: 10px; color: #f0f6fc;">
    <p><strong>BHIV Platform</strong> - Professional Video Generation System</p>
    <p>Powered by AI • Built for Excellence</p>
</div>
""", unsafe_allow_html=True)

# Analytics Dashboard
with st.expander("📊 Advanced Analytics"):
    if config['analytics_enabled']:
        analytics = get_analytics()
        insights = analytics.get_platform_insights()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Rating Trends")
            trend_data = insights['rating_trends']
            st.metric(
                "Trend Direction", 
                trend_data['trend'].title(),
                delta=f"{trend_data.get('improvement', 0):+.2f}"
            )
            
        with col2:
            st.subheader("🎯 Top Themes")
            themes = insights['sentiment_analysis'].get('top_themes', {})
            for theme, count in list(themes.items())[:3]:
                st.write(f"• {theme.title()}: {count} mentions")
        
        if insights['top_performing_videos']:
            st.subheader("🏆 Top Performing Videos")
            for video in insights['top_performing_videos'][:3]:
                st.write(f"• {video['title']}: {video['avg_rating']:.1f}⭐ ({video['rating_count']} ratings)")
    else:
        st.info("Analytics disabled. Enable in configuration to see detailed insights.")

if st.button("🔄 Refresh Dashboard", type="secondary"):
    st.cache_data.clear()
    st.rerun()
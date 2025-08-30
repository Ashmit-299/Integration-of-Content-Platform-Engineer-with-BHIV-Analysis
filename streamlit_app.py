import streamlit as st
import requests
import time
from pathlib import Path

# Configuration
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="BHIV Video Platform",
    page_icon="🎥",
    layout="wide"
)

# Title
st.title("🎥 BHIV Video Platform")
st.markdown("Upload scripts → Generate videos → Get feedback")

# Check API connection
@st.cache_data(ttl=30)
def check_api_health():
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# Get metrics
@st.cache_data(ttl=10)
def get_metrics():
    try:
        response = requests.get(f"{API_BASE}/metrics")
        return response.json() if response.status_code == 200 else {}
    except:
        return {}

# Get videos
@st.cache_data(ttl=5)
def get_videos():
    try:
        response = requests.get(f"{API_BASE}/videos")
        return response.json().get("videos", []) if response.status_code == 200 else []
    except:
        return []

# Status bar
col1, col2, col3, col4 = st.columns(4)

with col1:
    if check_api_health():
        st.success("✅ API Connected")
    else:
        st.error("❌ API Disconnected")

metrics = get_metrics()
with col2:
    st.metric("Videos", metrics.get("videos_generated", 0))

with col3:
    st.metric("Ratings", metrics.get("total_ratings", 0))

with col4:
    st.metric("Avg Rating", f"{metrics.get('average_rating', 0):.1f}/5")

st.divider()

# Upload section
st.header("📤 Upload Script")

uploaded_file = st.file_uploader(
    "Choose a script file",
    type=['txt', 'md'],
    help="Upload your lesson script in .txt or .md format"
)

if uploaded_file is not None:
    if st.button("Generate Video", type="primary"):
        with st.spinner("Processing script..."):
            try:
                files = {"file": uploaded_file}
                response = requests.post(f"{API_BASE}/upload", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Video generated! ID: {result['id']}")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Upload failed")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.divider()

# Videos section
st.header("🎬 Your Videos")

videos = get_videos()

if videos:
    for video in videos:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"**{video['title']}**")
            st.caption(f"ID: {video['id']}")
        
        with col2:
            if st.button("▶️ Play", key=f"play_{video['id']}"):
                st.info(f"Video URL: {API_BASE}/stream/{video['id']}")
        
        with col3:
            if st.button("⭐ Rate", key=f"rate_{video['id']}"):
                st.session_state[f"rating_modal_{video['id']}"] = True
        
        # Rating modal
        if st.session_state.get(f"rating_modal_{video['id']}", False):
            with st.form(f"rating_form_{video['id']}"):
                st.write(f"Rate: **{video['title']}**")
                rating = st.slider("Rating", 1, 5, 3)
                comment = st.text_area("Comment (optional)")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Submit Rating"):
                        try:
                            data = {"rating": rating, "comment": comment}
                            response = requests.post(f"{API_BASE}/rate/{video['id']}", data=data)
                            
                            if response.status_code == 200:
                                st.success("✅ Rating submitted!")
                                st.session_state[f"rating_modal_{video['id']}"] = False
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Rating failed")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"rating_modal_{video['id']}"] = False
                        st.rerun()
        
        st.divider()
else:
    st.info("No videos yet. Upload a script to get started!")

# Auto-refresh
if st.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()
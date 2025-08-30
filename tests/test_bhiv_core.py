import pytest
import tempfile
import sqlite3
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bhiv_lm_client import BHIVLMClient
from analytics.advanced_analytics import AdvancedAnalytics

class TestBHIVCore:
    
    def setup_method(self):
        """Setup test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE videos
                         (id TEXT PRIMARY KEY, title TEXT)''')
            c.execute('''CREATE TABLE user_ratings
                         (id INTEGER PRIMARY KEY, video_id TEXT, rating INTEGER, comment TEXT)''')
            
            # Insert test data
            c.execute("INSERT INTO videos VALUES ('test1', 'Test Video 1')")
            c.execute("INSERT INTO videos VALUES ('test2', 'Test Video 2')")
            c.execute("INSERT INTO user_ratings VALUES (1, 'test1', 5, 'Great video!')")
            c.execute("INSERT INTO user_ratings VALUES (2, 'test1', 4, 'Good content')")
            c.execute("INSERT INTO user_ratings VALUES (3, 'test2', 2, 'Too slow')")
            conn.commit()
    
    def teardown_method(self):
        """Cleanup test database"""
        os.unlink(self.db_path)
    
    def test_lm_client_feedback_analysis(self):
        """Test LM client feedback analysis"""
        client = BHIVLMClient()
        
        # Test positive feedback
        result = client._extract_themes("Great video with excellent quality!")
        assert "quality" in result
        
        # Test suggestions
        suggestions = client._generate_suggestions(2, "Too fast paced")
        assert any("pacing" in s.lower() for s in suggestions)
    
    def test_analytics_rating_trends(self):
        """Test analytics rating trends"""
        analytics = AdvancedAnalytics(self.db_path)
        trends = analytics.get_rating_trends()
        
        assert "trend" in trends
        assert "total_ratings" in trends
        assert trends["total_ratings"] == 3
    
    def test_analytics_video_performance(self):
        """Test video performance analytics"""
        analytics = AdvancedAnalytics(self.db_path)
        performance = analytics.get_video_performance("test1")
        
        assert performance["video_id"] == "test1"
        assert performance["average_rating"] == 4.5
        assert performance["total_ratings"] == 2
    
    def test_analytics_platform_insights(self):
        """Test platform insights"""
        analytics = AdvancedAnalytics(self.db_path)
        insights = analytics.get_platform_insights()
        
        assert "rating_trends" in insights
        assert "top_performing_videos" in insights
        assert len(insights["top_performing_videos"]) > 0

if __name__ == "__main__":
    pytest.main([__file__])
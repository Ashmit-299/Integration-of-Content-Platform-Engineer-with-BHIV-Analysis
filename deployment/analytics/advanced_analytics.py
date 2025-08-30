import sqlite3
from pathlib import Path

class Analytics:
    def __init__(self):
        self.db_path = Path("data/meta.db")
    
    def get_rating_trends(self):
        """Get rating trends"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT AVG(rating) FROM user_ratings")
                avg = cur.fetchone()[0] or 3.0
                return {"trend": "stable", "improvement": 0.0}
        except:
            return {"trend": "stable", "improvement": 0.0}
    
    def get_sentiment_analysis(self):
        """Get sentiment analysis"""
        return {
            "total_analyzed": 0,
            "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0}
        }
    
    def get_platform_insights(self):
        """Get platform insights"""
        return {
            "rating_trends": self.get_rating_trends(),
            "sentiment_analysis": {"top_themes": {}},
            "top_performing_videos": []
        }

def get_analytics():
    return Analytics()
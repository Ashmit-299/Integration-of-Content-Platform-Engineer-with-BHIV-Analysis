import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict
import statistics

class AdvancedAnalytics:
    def __init__(self, db_path: str = "data/meta.db"):
        self.db_path = db_path
        
    def get_rating_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze rating trends over time"""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT DATE(datetime('now', '-' || ? || ' days')) as date_threshold
            """, (days,))
            
            # Get ratings over time (simulated with row IDs as time proxy)
            cur.execute("""
                SELECT video_id, rating, comment, id
                FROM user_ratings 
                ORDER BY id DESC
                LIMIT 100
            """)
            
            ratings_data = cur.fetchall()
            
        if not ratings_data:
            return {"trend": "stable", "average": 0, "total_ratings": 0}
            
        # Analyze trends
        ratings = [r[1] for r in ratings_data]
        recent_ratings = ratings[:len(ratings)//2] if len(ratings) > 4 else ratings
        older_ratings = ratings[len(ratings)//2:] if len(ratings) > 4 else ratings
        
        recent_avg = statistics.mean(recent_ratings) if recent_ratings else 0
        older_avg = statistics.mean(older_ratings) if older_ratings else 0
        
        trend = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        
        return {
            "trend": trend,
            "recent_average": round(recent_avg, 2),
            "older_average": round(older_avg, 2),
            "total_ratings": len(ratings_data),
            "improvement": round(recent_avg - older_avg, 2)
        }
    
    def get_sentiment_analysis(self) -> Dict[str, Any]:
        """Analyze sentiment from feedback logs"""
        log_dir = Path("bucket/logs")
        if not log_dir.exists():
            return {"positive": 0, "neutral": 0, "negative": 0}
            
        sentiment_counts = defaultdict(int)
        themes = defaultdict(int)
        
        for log_file in log_dir.glob("feedback_*.json"):
            try:
                data = json.loads(log_file.read_text())
                analysis = data.get("analysis", {})
                
                sentiment = analysis.get("sentiment", "neutral")
                sentiment_counts[sentiment] += 1
                
                for theme in analysis.get("key_themes", []):
                    themes[theme] += 1
                    
            except Exception:
                continue
                
        return {
            "sentiment_distribution": dict(sentiment_counts),
            "top_themes": dict(sorted(themes.items(), key=lambda x: x[1], reverse=True)[:5]),
            "total_analyzed": sum(sentiment_counts.values())
        }
    
    def get_video_performance(self, video_id: str) -> Dict[str, Any]:
        """Get detailed performance metrics for a specific video"""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            
            # Get basic stats
            cur.execute("""
                SELECT AVG(rating), COUNT(*), MIN(rating), MAX(rating)
                FROM user_ratings 
                WHERE video_id = ?
            """, (video_id,))
            
            stats = cur.fetchone()
            avg_rating, count, min_rating, max_rating = stats if stats[0] else (0, 0, 0, 0)
            
            # Get rating distribution
            cur.execute("""
                SELECT rating, COUNT(*) 
                FROM user_ratings 
                WHERE video_id = ?
                GROUP BY rating
                ORDER BY rating
            """, (video_id,))
            
            distribution = dict(cur.fetchall())
            
        return {
            "video_id": video_id,
            "average_rating": round(avg_rating, 2) if avg_rating else 0,
            "total_ratings": count,
            "rating_range": {"min": min_rating, "max": max_rating},
            "rating_distribution": distribution,
            "engagement_score": min(100, (count * avg_rating * 20)) if avg_rating else 0
        }
    
    def get_platform_insights(self) -> Dict[str, Any]:
        """Get comprehensive platform insights"""
        rating_trends = self.get_rating_trends()
        sentiment_data = self.get_sentiment_analysis()
        
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            
            # Get top performing videos
            cur.execute("""
                SELECT v.id, v.title, AVG(ur.rating) as avg_rating, COUNT(ur.rating) as rating_count
                FROM videos v
                LEFT JOIN user_ratings ur ON v.id = ur.video_id
                GROUP BY v.id, v.title
                HAVING rating_count > 0
                ORDER BY avg_rating DESC, rating_count DESC
                LIMIT 5
            """)
            
            top_videos = [
                {
                    "id": row[0], 
                    "title": row[1], 
                    "avg_rating": round(row[2], 2), 
                    "rating_count": row[3]
                } 
                for row in cur.fetchall()
            ]
            
        return {
            "rating_trends": rating_trends,
            "sentiment_analysis": sentiment_data,
            "top_performing_videos": top_videos,
            "generated_at": datetime.now().isoformat()
        }

def get_analytics() -> AdvancedAnalytics:
    return AdvancedAnalytics()
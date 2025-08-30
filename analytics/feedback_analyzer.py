# analytics/feedback_analyzer.py - Advanced Feedback Analytics
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import statistics
import logging

logger = logging.getLogger(__name__)

@dataclass
class FeedbackTrend:
    period: str
    average_rating: float
    total_feedback: int
    sentiment_distribution: Dict[str, float]
    improvement_areas: List[str]
    user_satisfaction_score: float

@dataclass
class VideoAnalytics:
    video_id: str
    total_views: int
    average_rating: float
    rating_distribution: Dict[int, int]
    sentiment_trends: List[FeedbackTrend]
    engagement_score: float
    improvement_suggestions: List[str]

class FeedbackAnalyzer:
    """Advanced feedback analytics with trend analysis and RLHF insights"""
    
    def __init__(self, db_path: str = "data/meta.db", bucket_path: str = "bucket"):
        self.db_path = Path(db_path)
        self.bucket_path = Path(bucket_path)
        self.logs_path = self.bucket_path / "logs"
    
    def analyze_video_performance(self, video_id: str) -> VideoAnalytics:
        """Comprehensive video performance analysis"""
        try:
            # Get basic rating data from database
            rating_data = self._get_video_ratings(video_id)
            
            # Get advanced feedback from logs
            feedback_logs = self._get_feedback_logs(video_id)
            
            # Calculate metrics
            total_views = len(rating_data)
            average_rating = statistics.mean([r['rating'] for r in rating_data]) if rating_data else 0
            
            rating_distribution = defaultdict(int)
            for rating in rating_data:
                rating_distribution[rating['rating']] += 1
            
            # Analyze sentiment trends
            sentiment_trends = self._analyze_sentiment_trends(feedback_logs)
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(rating_data, feedback_logs)
            
            # Generate improvement suggestions
            improvement_suggestions = self._generate_improvement_suggestions(
                rating_data, feedback_logs, average_rating
            )
            
            return VideoAnalytics(
                video_id=video_id,
                total_views=total_views,
                average_rating=average_rating,
                rating_distribution=dict(rating_distribution),
                sentiment_trends=sentiment_trends,
                engagement_score=engagement_score,
                improvement_suggestions=improvement_suggestions
            )
            
        except Exception as e:
            logger.error(f"Video analysis failed for {video_id}: {e}")
            return self._empty_analytics(video_id)
    
    def get_platform_analytics(self, days: int = 30) -> Dict:
        """Get comprehensive platform analytics"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get all videos and their performance
            all_videos = self._get_all_videos()
            video_analytics = []
            
            for video in all_videos:
                analytics = self.analyze_video_performance(video['id'])
                video_analytics.append(analytics)
            
            # Calculate platform-wide metrics
            total_videos = len(all_videos)
            total_ratings = sum(va.total_views for va in video_analytics)
            average_platform_rating = statistics.mean([va.average_rating for va in video_analytics if va.average_rating > 0])
            
            # Sentiment analysis across platform
            sentiment_summary = self._analyze_platform_sentiment(video_analytics)
            
            # Top performing videos
            top_videos = sorted(video_analytics, key=lambda x: x.engagement_score, reverse=True)[:5]
            
            # Common improvement areas
            all_improvements = []
            for va in video_analytics:
                all_improvements.extend(va.improvement_suggestions)
            
            improvement_frequency = defaultdict(int)
            for improvement in all_improvements:
                improvement_frequency[improvement] += 1
            
            common_improvements = sorted(improvement_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "period_days": days,
                "total_videos": total_videos,
                "total_ratings": total_ratings,
                "average_platform_rating": round(average_platform_rating, 2) if video_analytics else 0,
                "sentiment_summary": sentiment_summary,
                "top_performing_videos": [
                    {"video_id": va.video_id, "engagement_score": va.engagement_score, "rating": va.average_rating}
                    for va in top_videos
                ],
                "common_improvement_areas": [{"area": area, "frequency": freq} for area, freq in common_improvements],
                "user_satisfaction_trend": self._calculate_satisfaction_trend(days),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Platform analytics failed: {e}")
            return {"error": str(e), "generated_at": datetime.now().isoformat()}
    
    def generate_rlhf_insights(self, video_id: str) -> Dict:
        """Generate Reinforcement Learning from Human Feedback insights"""
        try:
            analytics = self.analyze_video_performance(video_id)
            feedback_logs = self._get_feedback_logs(video_id)
            
            # RLHF-style analysis
            positive_feedback = [f for f in feedback_logs if f.get('sentiment', {}).get('sentiment') == 'positive']
            negative_feedback = [f for f in feedback_logs if f.get('sentiment', {}).get('sentiment') == 'negative']
            
            # Reward signal calculation
            reward_signal = self._calculate_reward_signal(analytics.average_rating, analytics.engagement_score)
            
            # Policy improvement suggestions
            policy_improvements = self._generate_policy_improvements(positive_feedback, negative_feedback)
            
            # Learning trajectory
            learning_trajectory = self._analyze_learning_trajectory(video_id)
            
            return {
                "video_id": video_id,
                "reward_signal": reward_signal,
                "policy_improvements": policy_improvements,
                "learning_trajectory": learning_trajectory,
                "positive_feedback_patterns": self._extract_patterns(positive_feedback),
                "negative_feedback_patterns": self._extract_patterns(negative_feedback),
                "recommended_actions": self._recommend_rlhf_actions(reward_signal, policy_improvements),
                "confidence_score": self._calculate_confidence_score(len(feedback_logs), analytics.average_rating)
            }
            
        except Exception as e:
            logger.error(f"RLHF insights failed for {video_id}: {e}")
            return {"error": str(e), "video_id": video_id}
    
    def _get_video_ratings(self, video_id: str) -> List[Dict]:
        """Get video ratings from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT rating, comment, id FROM ratings WHERE video_id = ?",
                (video_id,)
            )
            
            ratings = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return ratings
            
        except Exception as e:
            logger.error(f"Failed to get ratings for {video_id}: {e}")
            return []
    
    def _get_feedback_logs(self, video_id: str) -> List[Dict]:
        """Get advanced feedback logs from bucket"""
        try:
            feedback_file = self.logs_path / f"feedback_{video_id}.json"
            
            if feedback_file.exists():
                return json.loads(feedback_file.read_text())
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get feedback logs for {video_id}: {e}")
            return []
    
    def _get_all_videos(self) -> List[Dict]:
        """Get all videos from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, title FROM videos")
            videos = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return videos
            
        except Exception as e:
            logger.error(f"Failed to get all videos: {e}")
            return []
    
    def _analyze_sentiment_trends(self, feedback_logs: List[Dict]) -> List[FeedbackTrend]:
        """Analyze sentiment trends over time"""
        if not feedback_logs:
            return []
        
        # Group by time periods (daily)
        daily_feedback = defaultdict(list)
        
        for log in feedback_logs:
            timestamp = log.get('timestamp', datetime.now().isoformat())
            date = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).date()
            daily_feedback[str(date)].append(log)
        
        trends = []
        for date, logs in daily_feedback.items():
            ratings = [log.get('rating', 3) for log in logs]
            sentiments = [log.get('sentiment', {}).get('sentiment', 'neutral') for log in logs]
            
            sentiment_dist = defaultdict(int)
            for sentiment in sentiments:
                sentiment_dist[sentiment] += 1
            
            # Normalize sentiment distribution
            total = len(sentiments)
            sentiment_dist = {k: v/total for k, v in sentiment_dist.items()}
            
            trends.append(FeedbackTrend(
                period=date,
                average_rating=statistics.mean(ratings),
                total_feedback=len(logs),
                sentiment_distribution=dict(sentiment_dist),
                improvement_areas=[],  # Would extract from logs
                user_satisfaction_score=statistics.mean(ratings) / 5.0
            ))
        
        return trends
    
    def _calculate_engagement_score(self, rating_data: List[Dict], feedback_logs: List[Dict]) -> float:
        """Calculate engagement score based on ratings and feedback quality"""
        if not rating_data:
            return 0.0
        
        # Base score from ratings
        avg_rating = statistics.mean([r['rating'] for r in rating_data])
        rating_score = avg_rating / 5.0
        
        # Feedback quality score
        feedback_score = 0.0
        if feedback_logs:
            comment_lengths = [len(log.get('comment', '')) for log in feedback_logs]
            avg_comment_length = statistics.mean(comment_lengths)
            feedback_score = min(avg_comment_length / 100.0, 1.0)  # Normalize to 0-1
        
        # Combine scores
        engagement_score = (rating_score * 0.7) + (feedback_score * 0.3)
        
        return round(engagement_score, 3)
    
    def _generate_improvement_suggestions(self, rating_data: List[Dict], feedback_logs: List[Dict], avg_rating: float) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        if avg_rating < 3.0:
            suggestions.append("Consider major content restructuring")
        elif avg_rating < 4.0:
            suggestions.append("Focus on clarity and pacing improvements")
        
        # Analyze comments for specific issues
        all_comments = [r.get('comment', '') for r in rating_data] + [f.get('comment', '') for f in feedback_logs]
        comment_text = ' '.join(all_comments).lower()
        
        if 'slow' in comment_text:
            suggestions.append("Increase video pacing")
        if 'fast' in comment_text:
            suggestions.append("Slow down presentation")
        if 'unclear' in comment_text or 'confusing' in comment_text:
            suggestions.append("Improve explanation clarity")
        if 'boring' in comment_text:
            suggestions.append("Add more engaging elements")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def _analyze_platform_sentiment(self, video_analytics: List[VideoAnalytics]) -> Dict:
        """Analyze sentiment across the platform"""
        all_sentiments = []
        
        for va in video_analytics:
            for trend in va.sentiment_trends:
                for sentiment, count in trend.sentiment_distribution.items():
                    all_sentiments.extend([sentiment] * int(count * trend.total_feedback))
        
        if not all_sentiments:
            return {"positive": 0, "negative": 0, "neutral": 0}
        
        sentiment_counts = defaultdict(int)
        for sentiment in all_sentiments:
            sentiment_counts[sentiment] += 1
        
        total = len(all_sentiments)
        return {k: round(v/total, 3) for k, v in sentiment_counts.items()}
    
    def _calculate_satisfaction_trend(self, days: int) -> List[Dict]:
        """Calculate user satisfaction trend over time"""
        # This would analyze satisfaction over the specified period
        # For now, return a simple trend
        return [
            {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), "satisfaction": 0.75 + (i * 0.01)}
            for i in range(min(days, 30))
        ]
    
    def _calculate_reward_signal(self, avg_rating: float, engagement_score: float) -> float:
        """Calculate RLHF reward signal"""
        # Combine rating and engagement for reward
        rating_reward = (avg_rating - 3.0) / 2.0  # Normalize around neutral (3)
        engagement_reward = engagement_score
        
        return round((rating_reward * 0.6) + (engagement_reward * 0.4), 3)
    
    def _generate_policy_improvements(self, positive_feedback: List[Dict], negative_feedback: List[Dict]) -> List[str]:
        """Generate policy improvements based on feedback patterns"""
        improvements = []
        
        if len(positive_feedback) > len(negative_feedback):
            improvements.append("Reinforce current content style")
        else:
            improvements.append("Major content revision needed")
        
        # Analyze patterns in feedback
        if negative_feedback:
            improvements.append("Address common negative feedback patterns")
        
        if positive_feedback:
            improvements.append("Amplify successful content elements")
        
        return improvements
    
    def _analyze_learning_trajectory(self, video_id: str) -> Dict:
        """Analyze learning trajectory for RLHF"""
        # This would track how the video performance changes over time
        return {
            "initial_performance": 0.5,
            "current_performance": 0.7,
            "improvement_rate": 0.1,
            "learning_stability": 0.8
        }
    
    def _extract_patterns(self, feedback_list: List[Dict]) -> List[str]:
        """Extract common patterns from feedback"""
        if not feedback_list:
            return []
        
        # Simple pattern extraction
        patterns = []
        comments = [f.get('comment', '') for f in feedback_list]
        
        if any('clear' in c.lower() for c in comments):
            patterns.append("Users appreciate clarity")
        if any('example' in c.lower() for c in comments):
            patterns.append("Examples are valued")
        
        return patterns
    
    def _recommend_rlhf_actions(self, reward_signal: float, policy_improvements: List[str]) -> List[str]:
        """Recommend specific RLHF actions"""
        actions = []
        
        if reward_signal < 0:
            actions.append("Implement immediate content improvements")
        elif reward_signal > 0.5:
            actions.append("Continue current approach with minor optimizations")
        else:
            actions.append("Moderate improvements needed")
        
        actions.extend(policy_improvements[:3])
        
        return actions
    
    def _calculate_confidence_score(self, feedback_count: int, avg_rating: float) -> float:
        """Calculate confidence in the analysis"""
        # More feedback = higher confidence
        feedback_confidence = min(feedback_count / 10.0, 1.0)
        
        # Extreme ratings (very high or low) with little feedback = lower confidence
        rating_confidence = 1.0 - abs(avg_rating - 3.0) / 2.0 if feedback_count < 5 else 1.0
        
        return round(feedback_confidence * rating_confidence, 3)
    
    def _empty_analytics(self, video_id: str) -> VideoAnalytics:
        """Return empty analytics for error cases"""
        return VideoAnalytics(
            video_id=video_id,
            total_views=0,
            average_rating=0.0,
            rating_distribution={},
            sentiment_trends=[],
            engagement_score=0.0,
            improvement_suggestions=[]
        )

def get_feedback_analyzer() -> FeedbackAnalyzer:
    """Get feedback analyzer instance"""
    return FeedbackAnalyzer()
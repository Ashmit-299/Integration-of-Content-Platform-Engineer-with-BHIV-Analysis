import asyncio
import aiohttp
import backoff
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class BHIVLMClient:
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or "https://api.openai.com/v1"
        self.api_key = api_key or "demo-key"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=30
    )
    async def analyze_feedback(self, video_id: str, rating: int, comment: str) -> Dict[str, Any]:
        """Analyze user feedback with retry logic"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            # Simulate LM analysis (replace with actual API call)
            analysis = {
                "video_id": video_id,
                "sentiment": "positive" if rating >= 4 else "negative" if rating <= 2 else "neutral",
                "key_themes": self._extract_themes(comment),
                "improvement_suggestions": self._generate_suggestions(rating, comment),
                "confidence_score": 0.85,
                "timestamp": datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"LM analysis failed for video {video_id}: {e}")
            return {"error": str(e), "video_id": video_id}
    
    def _extract_themes(self, comment: str) -> list:
        """Extract key themes from comment"""
        themes = []
        keywords = {
            "quality": ["quality", "clear", "good", "excellent"],
            "content": ["content", "information", "topic", "subject"],
            "pacing": ["fast", "slow", "pace", "speed"],
            "engagement": ["boring", "interesting", "engaging", "captivating"]
        }
        
        comment_lower = comment.lower()
        for theme, words in keywords.items():
            if any(word in comment_lower for word in words):
                themes.append(theme)
        
        return themes or ["general"]
    
    def _generate_suggestions(self, rating: int, comment: str) -> list:
        """Generate improvement suggestions"""
        suggestions = []
        
        if rating <= 2:
            suggestions.append("Consider improving video quality and content clarity")
        if "fast" in comment.lower():
            suggestions.append("Reduce pacing for better comprehension")
        if "slow" in comment.lower():
            suggestions.append("Increase pacing to maintain engagement")
        if "boring" in comment.lower():
            suggestions.append("Add more interactive elements and visual variety")
            
        return suggestions or ["Continue current approach"]
    
    def log_feedback(self, video_id: str, rating: int, comment: str, analysis: Dict[str, Any]) -> Path:
        """Log feedback with analysis to file"""
        log_dir = Path("bucket/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "video_id": video_id,
            "rating": rating,
            "comment": comment,
            "analysis": analysis
        }
        
        log_file = log_dir / f"feedback_{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_file.write_text(json.dumps(log_entry, indent=2))
        
        return log_file

# Singleton instance
_lm_client = None

def get_lm_client() -> BHIVLMClient:
    global _lm_client
    if _lm_client is None:
        _lm_client = BHIVLMClient()
    return _lm_client
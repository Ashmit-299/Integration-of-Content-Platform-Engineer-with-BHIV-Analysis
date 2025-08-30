import json
from pathlib import Path

class BHIVLMClient:
    def __init__(self):
        self.logs_dir = Path("bucket/logs")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    async def analyze_feedback(self, video_id, rating, comment):
        """Simple feedback analysis"""
        return {
            "sentiment": "positive" if rating >= 4 else "negative" if rating <= 2 else "neutral",
            "suggestions": ["Improve pacing", "Add more examples"] if rating < 4 else ["Great work!"]
        }
    
    def log_feedback(self, video_id, rating, comment, analysis):
        """Log feedback analysis"""
        log_file = self.logs_dir / f"feedback_{video_id}.json"
        log_data = {
            "video_id": video_id,
            "rating": rating,
            "comment": comment,
            "analysis": analysis
        }
        log_file.write_text(json.dumps(log_data, indent=2))

def get_lm_client():
    return BHIVLMClient()
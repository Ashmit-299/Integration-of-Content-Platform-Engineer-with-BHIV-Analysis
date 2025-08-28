import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class BHIVLanguageModelClient:
    def __init__(self):
        self.logs_dir = Path("bucket/logs")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_feedback(self, video_id, rating, comment):
        suggestions = []
        if rating <= 2:
            suggestions.append("Shorten scenes")
        if "slow" in comment.lower():
            suggestions.append("Increase pacing")
        
        return {
            "suggestions": suggestions,
            "sentiment": "positive" if rating >= 4 else "negative"
        }
    
    def log_feedback(self, video_id, rating, comment, analysis):
        log_entry = {"video_id": video_id, "rating": rating, "analysis": analysis}
        log_file = self.logs_dir / f"feedback_{video_id}.json"
        log_file.write_text(json.dumps(log_entry, indent=2))
        return log_file

def get_lm_client():
    return BHIVLanguageModelClient()

from pathlib import Path
from bhiv_bucket import save_script, init_bucket
from video.bhiv_integration import BHIVClient
from bhiv_lm_client import get_lm_client
import json
import uuid

class BHIVOrchestrator:
    def __init__(self):
        self.client = BHIVClient()
        init_bucket()
    
    def ingest_script(self, script_path, metadata=None):
        """Ingest script into BHIV system"""
        script_id = str(uuid.uuid4())[:8]
        bucket_key = f"scripts/{script_id}.txt"
        
        # Save to bucket
        bucket_path = save_script(script_path, bucket_key)
        
        # Create metadata
        meta = {
            "script_id": script_id,
            "original_path": str(script_path),
            "bucket_path": bucket_path,
            "metadata": metadata or {}
        }
        
        # Save metadata
        meta_path = Path("bucket") / f"meta_{script_id}.json"
        meta_path.write_text(json.dumps(meta, indent=2))
        
        return script_id, bucket_path
    
    def process_webhook(self, script_id, action="process"):
        """Handle webhook for script processing"""
        meta_path = Path("bucket") / f"meta_{script_id}.json"
        if not meta_path.exists():
            return {"error": "Script not found"}
        
        meta = json.loads(meta_path.read_text())
        meta["status"] = "processing" if action == "process" else action
        meta_path.write_text(json.dumps(meta, indent=2))
        
        return {"script_id": script_id, "status": meta["status"]}
    
    def process_feedback(self, video_id, rating, comment):
        """Process user feedback with AI analysis"""
        lm_client = get_lm_client()
        analysis = lm_client.analyze_feedback(video_id, rating, comment)
        log_file = lm_client.log_feedback(video_id, rating, comment, analysis)
        return {"analysis": analysis, "log_file": str(log_file)}

def get_orchestrator():
    return BHIVOrchestrator()

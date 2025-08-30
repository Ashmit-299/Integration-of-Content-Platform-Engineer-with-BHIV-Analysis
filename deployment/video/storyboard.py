import json
from pathlib import Path

def generate_storyboard_from_file(script_path, output_path=None):
    """Generate storyboard from script file"""
    script_text = Path(script_path).read_text()
    
    # Simple storyboard generation
    lines = [line.strip() for line in script_text.split('\n') if line.strip()]
    scenes = []
    
    for i, line in enumerate(lines[:5]):  # Max 5 scenes
        scenes.append({
            "scene_id": i + 1,
            "text": line,
            "duration_secs": 4,
            "bg_color": "#FFFFFF",
            "visual_hint": f"Scene {i+1}"
        })
    
    storyboard = {
        "title": "Generated Video",
        "scenes": scenes
    }
    
    if output_path:
        Path(output_path).write_text(json.dumps(storyboard, indent=2))
    
    return storyboard
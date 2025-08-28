import json
from pathlib import Path

def split_into_scenes(script_text, max_sentences_per_scene=2):
    # Very simple sentence splitter based on periods and newlines
    lines = [ln.strip() for ln in script_text.splitlines() if ln.strip()]
    text = " ".join(lines)
    import re
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    scenes = []
    i = 0
    sid = 1
    while i < len(sentences):
        block = " ".join(sentences[i:i+max_sentences_per_scene])
        scenes.append({
            "scene_id": sid,
            "text": block,
            "duration_secs": max(3, len(block.split())//3)
        })
        i += max_sentences_per_scene
        sid += 1
        
    scene_types = {
        "example": ["example", "e.g."],
        "definition": ["define", "what is"],
        "summary": ["summary", "conclusion"]
    }
    for scene in scenes:
        text_lower = scene["text"].lower()
        scene["type"] = "standard"
        scene["bg_color"] = "#FFFFFF"  # Default white
        scene["visual_hint"] = ""
        for typ, keywords in scene_types.items():
            if any(kw in text_lower for kw in keywords):
                scene["type"] = typ
                if typ == "example":
                    scene["bg_color"] = "#E0F7FA"  # Light blue for emphasis
                    scene["visual_hint"] = "Insert illustrative diagram"
                elif typ == "definition":
                    scene["duration_secs"] += 2  # Extra time for absorption
                break
    return scenes

def generate_storyboard_from_file(input_path, output_path=None):
    input_path = Path(input_path)
    text = input_path.read_text(encoding="utf-8")
    scenes = split_into_scenes(text)
    storyboard = {
        "title": text.strip().splitlines()[0] if text.strip() else "untitled",
        "scenes": scenes
    }
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(storyboard, indent=2, ensure_ascii=False), encoding="utf-8")
    return storyboard

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python video/storyboard.py <script.txt> [output.json]")
        raise SystemExit(1)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "data/storyboard.json"
    sb = generate_storyboard_from_file(inp, out)
    print("Generated storyboard with %d scenes" % len(sb["scenes"]))

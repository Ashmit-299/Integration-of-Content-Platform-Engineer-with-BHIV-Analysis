import sys
from video.storyboard import generate_storyboard_from_file
from video.generator import render_video_from_storyboard

def run(script_path):
    sb = generate_storyboard_from_file(script_path, output_path="data/storyboards/sample_storyboard.json")
    print("Storyboard generated with %d scenes" % len(sb["scenes"]))
    video_path = render_video_from_storyboard(sb, out_path="data/videos/sample_video.mp4")
    print("Video generated:", video_path)

if __name__ == "__main__":
    script = sys.argv[1] if len(sys.argv)>1 else "sample/lesson.txt"
    run(script)

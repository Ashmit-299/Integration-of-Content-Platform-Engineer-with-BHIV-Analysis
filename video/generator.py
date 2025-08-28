# video/generator.py (Full File - Paste Exactly)
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
import uuid
import numpy as np
import textwrap
import imageio

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    return tuple(int(hex_color[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def _create_image_from_text(text, size=(1280,720), fontsize=36, bg="#FFFFFF", visual_hint=""):
    bg_rgb = hex_to_rgb(bg) if isinstance(bg, str) else bg
    img = Image.new("RGB", size, color=bg_rgb)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", fontsize)
    except Exception:
        font = ImageFont.load_default()

    lines = textwrap.wrap(text, width=60)
    y = 120
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            try:
                w, h = draw.textsize(line, font=font)
            except Exception:
                w, h = (len(line) * fontsize // 2, fontsize)  # approximate
        draw.text(((size[0] - w) / 2, y), line, fill=(0, 0, 0), font=font)
        y += h + 10

    if visual_hint:
        try:
            bbox = draw.textbbox((0, 0), visual_hint, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            w, h = (len(visual_hint) * fontsize // 2, fontsize)  # approximate
        draw.text((size[0] - w - 10, size[1] - h - 10), visual_hint, fill=(255, 0, 0), font=font)
    return img


def _save_scene_images(storyboard, tmpdir="data/tmp"):
    tmpdir = Path(tmpdir)
    tmpdir.mkdir(parents=True, exist_ok=True)
    image_paths = []
    durations = []

    default_colors = ["#FFFFFF", "#FFDDDD", "#DDFFDD", "#DDDDFF", "#FFFFDD"]

    for idx, sc in enumerate(storyboard.get("scenes", [])):
        txt = sc.get("text", "")
        dur = float(sc.get("duration_secs", 3))
        bg = sc.get("bg_color", default_colors[idx % len(default_colors)])
        visual_hint = sc.get("visual_hint", "")
        img = _create_image_from_text(txt, bg=bg, visual_hint=visual_hint)
        img_path = tmpdir / f"scene_{int(sc.get('scene_id', 0))}.png"
        img.save(img_path)
        image_paths.append(str(img_path))
        durations.append(dur)

    return image_paths, durations

def render_video_from_storyboard(storyboard, out_path=None, fps=24):
    if isinstance(storyboard, str):
        storyboard = json.loads(Path(storyboard).read_text(encoding="utf-8"))

    image_paths, durations = _save_scene_images(storyboard)
    if not image_paths:
        raise ValueError("No scenes found in storyboard")

    out_path = out_path or f"data/videos/{str(uuid.uuid4())[:8]}.mp4"
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    writer = imageio.get_writer(out_path, fps=fps, codec='libx264')

    try:
        prev_frame = None
        transition_frames = int(0.5 * fps)  # 0.5-second fade between scenes
        for img_path, dur in zip(image_paths, durations):
            pil_img = Image.open(img_path).convert("RGB")
            frame = np.array(pil_img)  # H x W x 3 uint8

            frames_to_write = max(1, int(round(dur * fps)))

            if prev_frame is not None:
                for t in range(transition_frames):
                    alpha = t / transition_frames
                    blended = ((1 - alpha) * prev_frame + alpha * frame).astype(np.uint8)
                    writer.append_data(blended)

            for _ in range(frames_to_write):
                writer.append_data(frame)

            prev_frame = frame

    finally:
        writer.close()

    return out_path

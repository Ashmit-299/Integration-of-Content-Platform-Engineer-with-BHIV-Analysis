# Gurukul Content Platform (MVP)

A minimal, ready-to-run MVP that converts lesson scripts into storyboard JSON, generates a simple video from the storyboard,
and exposes a small FastAPI backend to upload/stream and rate videos.

## What's included
- `video/storyboard.py` — converts a script text into storyboard JSON.
- `video/generator.py` — uses Pillow + moviepy to render frames and stitch an MP4.
- `backend/server.py` — FastAPI server: /upload, /generate/<id>, /stream/<id>, /rate/<id>.
- `run_pipeline.py` — local pipeline runner (script -> storyboard -> video).
- `requirements.txt` — Python packages required.
- `sample/lesson.txt` — sample lesson script.
- `reports/daily_log.txt` — sample daily log.
- `data/` — will contain generated videos and DB (created at runtime).

## How to run (local, development)
1. Create and activate a virtualenv:
   ```bash
   python -m venv venv
   source venv/bin/activate      # on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Run the API server:
   ```bash
   uvicorn backend.server:app --reload
   ```
   - Open `http://127.0.0.1:8000/docs` for the interactive API docs.

3. Or run the local pipeline to generate the sample video:
   ```bash
   python run_pipeline.py sample/lesson.txt
   ```
   Output will be saved to `data/videos/<id>.mp4`

## Notes
- This is a minimal MVP for the task PDF. It uses Pillow to render text into images and moviepy to create the MP4.
- For production or advanced styling, replace placeholder assets and improve the storyboard logic and RL feedback loop.

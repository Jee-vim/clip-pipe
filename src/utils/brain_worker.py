import json
import subprocess
import sys
import time
import random
import ollama
import re
from pathlib import Path
from pydantic import BaseModel, Field
from youtube_transcript_api import YouTubeTranscriptApi

class VideoClip(BaseModel):
    title: str = Field(..., min_length=10) 
    description: str = Field(..., min_length=20)
    start: str 
    end: str

BASE_DIR = Path(__file__).resolve().parent.parent.parent
JSON_FILE = BASE_DIR / "data" / "_jobs.json"
COOKIE_FILE = BASE_DIR / "data" / "_cookies.txt"

def get_video_data(url, rank=1):
    """Fetches video metadata using yt-dlp with cookies and jitter logic."""
    # Safety: Wait between 10 to 20 seconds before talking to YouTube
    wait_time = random.uniform(10, 20)
    time.sleep(wait_time)

    video_id = url.split("v=")[-1]
    
    # Base command with cookies
    cookie_args = ["--cookies", str(COOKIE_FILE)] if COOKIE_FILE.exists() else []

    # 1. Get real title
    cmd_title = ["yt-dlp", "--skip-download", "--get-title"] + cookie_args + [url]
    real_title = subprocess.run(cmd_title, capture_output=True, text=True).stdout.strip()
    
    # 2. Heatmap Jitter Logic
    cmd_json = ["yt-dlp", "--skip-download", "--dump-json"] + cookie_args + [url]
    try:
        res = subprocess.run(cmd_json, capture_output=True, text=True).stdout
        data = json.loads(res)
        heatmap = data.get('heatmap', [])
        sorted_peaks = sorted(heatmap, key=lambda x: x.get('value', 0), reverse=True)
    except:
        sorted_peaks = []
    
    selected_start = 15
    used_starts = []
    
    if sorted_peaks:
        found_count = 0
        for peak in sorted_peaks:
            p_start = peak.get('start_time', 0)
            # Ensure clips are at least 3 minutes apart
            if all(abs(p_start - existing) > 180 for existing in used_starts):
                found_count += 1
                used_starts.append(p_start)
                if found_count == rank:
                    selected_start = p_start
                    break
        
        if found_count < rank:
            selected_start = 15 + ((rank - 1) * 300)
    else:
        selected_start = 15 + ((rank - 1) * 300)

    v_start = time.strftime('%H:%M:%S', time.gmtime(selected_start))
    v_end = time.strftime('%H:%M:%S', time.gmtime(selected_start + 59))

    # 3. Get Transcript
    transcript_text = ""
    try:
        ts_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript = ts_list.find_transcript(['id'])
        except:
            transcript = ts_list.find_transcript(['en'])
        transcript_text = " ".join([t['text'] for t in transcript.fetch()[:40]])
    except:
        transcript_text = "None available"

    return transcript_text, v_start, v_end, real_title

def process_empty_jobs():
    if not JSON_FILE.exists():
        print(f"[ERROR] File not found: {JSON_FILE}", file=sys.stderr)
        return
    
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            schedule = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[FATAL] JSON Error: {e}", file=sys.stderr)
        return

    updated = False
    url_tracker = {}

    for slot in schedule:
        for item in slot.get("items", []):
            url = item.get("url")
            # Trigger only for empty slots
            if not item.get("title") or item.get("title") in ["CLIP", ""]:
                
                url_tracker[url] = url_tracker.get(url, 0) + 1
                rank = url_tracker[url]

                print(f"[BRAIN] Processing #{rank} for: {url}")
                transcript, v_start, v_end, real_title = get_video_data(url, rank=rank)

                prompt = f"""
                SOURCE VIDEO: {real_title}
                TRANSCRIPT: {transcript}
                CLIP VERSION: This is viral segment #{rank} from this video.

                MISSION: 
                You are a professional viral content creator. 
                Create a NEW, dramatic "Hook" title in Indonesian.
                DO NOT copy the source title. Make it unique for segment #{rank}.

                STRICT RULES:
                1. TITLE: Catchy Indonesian headline, UPPERCASE.
                2. DESCRIPTION: High-energy summary in Indonesian + 3-5 tags.
                3. START/END: You MUST use exactly '{v_start}' and '{v_end}'.
                4. LANGUAGE: Full Bahasa Indonesia.
                5. NO EMOJIS: Do not use any emojis or special symbols.
                """

                try:
                    response = ollama.chat(
                        model='llama3.2:3b',
                        messages=[{'role': 'user', 'content': prompt}],
                        format=VideoClip.model_json_schema(),
                        options={'temperature': 0.7} 
                    )
                    
                    ai_data = VideoClip.model_validate_json(response['message']['content'])
                    
                    f_start = ai_data.start if ":" in ai_data.start else v_start
                    f_end = ai_data.end if ":" in ai_data.end else v_end

                    item.update({
                        "title": ai_data.title.upper(),
                        "description": ai_data.description,
                        "start": f_start,
                        "end": f_end
                    })
                    print(f"[SUCCESS] {ai_data.title[:30]}...")
                    updated = True
                except Exception as e:
                    print(f"[ERROR] AI failed: {e}", file=sys.stderr)

    if updated:
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            # ensure_ascii=False saves text as-is (no \u unicode escapes)
            json.dump(schedule, f, indent=2, ensure_ascii=False)
        print("[INFO] Jobs updated")

if __name__ == "__main__":
    process_empty_jobs()t

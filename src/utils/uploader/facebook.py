import json
import time
import requests
from datetime import datetime
from pathlib import Path
from auth.meta import get_page_token
from utils.telegram import send_to_telegram

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

UPLOAD_LOG = DATA_DIR / "_upload_stats_fb.json"
MAX_DAILY_FB = 10

def can_upload_fb(account):
    if not UPLOAD_LOG.exists():
        return True
    
    with open(UPLOAD_LOG, 'r') as f:
        stats = json.load(f)
    
    today = datetime.now().strftime("%Y-%m-%d")
    acc_stats = stats.get(account, {})
    
    if acc_stats.get("date") == today:
        return acc_stats.get("count", 0) < MAX_DAILY_FB
    return True

def update_fb_count(account):
    stats = {}
    if UPLOAD_LOG.exists():
        with open(UPLOAD_LOG, 'r') as f:
            stats = json.load(f)
    
    today = datetime.now().strftime("%Y-%m-%d")
    if account not in stats or stats[account].get("date") != today:
        stats[account] = {"date": today, "count": 1}
    else:
        stats[account]["count"] += 1
        
    with open(UPLOAD_LOG, 'w') as f:
        json.dump(stats, f, indent=4)

def wait_for_fb_reels_ready(video_id, token):
    url = f"https://graph.facebook.com/v18.0/{video_id}"
    params = {
        "fields": "status",
        "access_token": token
    }
    
    for _ in range(30):
        res = requests.get(url, params=params).json()
        status = res.get("status", {}).get("video_status")
        
        if status == "ready":
            return True
        elif status == "failed":
            print(f"[ERROR] FB Processing failed: {res}")
            return False
            
        time.sleep(10)
    return False

def upload_facebook(video_path, title, description, account):
    if not can_upload_fb(account):
        print(f"[SKIP] Facebook {account} has reached daily limit.")
        return None

    page_id, token = get_page_token(account)
    
    try:
        start_url = f"https://graph.facebook.com/v18.0/{page_id}/video_reels"
        payload = {
            "upload_phase": "start",
            "access_token": token
        }
        start_res = requests.post(start_url, data=payload).json()
        video_id = start_res.get("video_id")

        if not video_id:
            print(f"[ERROR] Could not initialize FB Reel: {start_res}")
            return None

        upload_url = f"https://rupload.facebook.com/video-reels/{video_id}"
        with open(video_path, "rb") as f:
            upload_headers = {
                "Authorization": f"OAuth {token}",
                "offset": "0",
                "file_size": str(Path(video_path).stat().st_size),
                "Content-Type": "application/octet-stream"
            }
            requests.post(upload_url, data=f, headers=upload_headers).raise_for_status()

        publish_url = f"https://graph.facebook.com/v18.0/{page_id}/video_reels"
        publish_payload = {
            "upload_phase": "finish",
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": f"{title}\n\n{description}",
            "access_token": token
        }
        requests.post(publish_url, data=publish_payload).raise_for_status()

        print(f"[INFO] Waiting for Facebook to process Reel...")
        if wait_for_fb_reels_ready(video_id, token):
            print(f"[SUCCESS] Reel published on Facebook for {account}")
            update_fb_count(account)
            
            fb_link = f"https://www.facebook.com/reels/{video_id}"
            send_to_telegram(title=title, account=account, platform="Facebook", link=fb_link)
            return {"id": video_id}
            
    except Exception as e:
        print(f"[ERROR] Facebook upload failed for {account}: {e}")
        return None

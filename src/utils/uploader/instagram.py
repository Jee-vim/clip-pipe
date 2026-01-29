import json
import time
import requests
from datetime import datetime
from pathlib import Path
from auth.meta import get_ig_token
from utils.telegram import send_to_telegram

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

UPLOAD_LOG = DATA_DIR / "_upload_stats_ig.json"
MAX_DAILY_REELS = 10 

def can_upload_ig(account):
    if not UPLOAD_LOG.exists():
        return True
    
    with open(UPLOAD_LOG, 'r') as f:
        stats = json.load(f)
    
    today = datetime.now().strftime("%Y-%m-%d")
    acc_stats = stats.get(account, {})
    
    if acc_stats.get("date") == today:
        return acc_stats.get("count", 0) < MAX_DAILY_REELS
    return True

def update_ig_count(account):
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

def wait_for_media_ready(container_id, token):
    url = f"https://graph.facebook.com/v18.0/{container_id}"
    params = {"fields": "status_code", "access_token": token}
    
    for _ in range(30):
        res = requests.get(url, params=params).json()
        status = res.get("status_code")
        
        if status == "FINISHED":
            return True
        elif status == "ERROR":
            print(f"[ERROR] Meta processing failed: {res}")
            return False
            
        time.sleep(10)
    return False

def upload_instagram(video_url, title, description, account):
    if not can_upload_ig(account):
        print(f"[SKIP] Instagram {account} has reached daily Reels limit.")
        return None

    ig_user_id, token = get_ig_token(account)

    create_res = requests.post(
        f"https://graph.facebook.com/v18.0/{ig_user_id}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": f"{title}\n\n{description}",
            "access_token": token
        },
        timeout=60
    )
    
    create_data = create_res.json()
    if "id" not in create_data:
        print(f"[ERROR] Container creation failed: {create_data}")
        return None

    container_id = create_data["id"]

    print(f"[INFO] Uploading to IG {account}, waiting for processing...")
    if not wait_for_media_ready(container_id, token):
        print("[ERROR] Media processing timed out or failed.")
        return None

    publish = requests.post(
        f"https://graph.facebook.com/v18.0/{ig_user_id}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": token
        },
        timeout=60
    )

    if publish.status_code == 200:
        res_data = publish.json()
        print(f"[SUCCESS] Reels published on Instagram for {account}")
        update_ig_count(account)
        
        media_id = res_data.get("id")
        ig_link = f"https://www.instagram.com/reels/{media_id}/"

        send_to_telegram(
            title=title,
            account=account,
            platform="Instagram",
            link=ig_link
        )
        
        return res_data
    else:
        print(f"[ERROR] Publishing failed: {publish.text}")
        return None

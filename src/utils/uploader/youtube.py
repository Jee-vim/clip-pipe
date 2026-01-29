import json
from datetime import datetime
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from auth.youtube import get_credentials
from utils.telegram import send_to_telegram

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_LOG = DATA_DIR / "_upload_stats_yt.json"
MAX_DAILY_UPLOAD = 10 

def can_upload(account):
    if not UPLOAD_LOG.exists():
        return True
    
    with open(UPLOAD_LOG, 'r') as f:
        stats = json.load(f)
    
    today = datetime.now().strftime("%Y-%m-%d")
    acc_stats = stats.get(account, {})
    
    if acc_stats.get("date") == today:
        return acc_stats.get("count", 0) < MAX_DAILY_UPLOAD
    return True

def update_upload_count(account):
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

def upload_youtube(video_path, title, description, account):
    if not can_upload(account):
        print(f"[SKIP] Youtube {account} has reached the daily limit.")
        return None

    creds = get_credentials(account)
    youtube = build("youtube", "v3", credentials=creds)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["shorts"],
                "categoryId": "24"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True
        )
    )

    try:
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"[INFO] Uploading {int(status.progress() * 100)}%")
        
        video_id = response.get("id")
        video_link = f"https://youtu.be/{video_id}"
        
        update_upload_count(account)

        send_to_telegram(
            title=title,
            account=account,
            platform="YouTube",
            link=video_link
        )

        return response
    except Exception as e:
        print(f"[ERROR] Upload failed for {account}: {e}")
        return None

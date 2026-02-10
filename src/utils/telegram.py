import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_to_telegram(title, account, platform, link=None):
    """Send Telegram notification for video upload completion."""
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    if not TOKEN or not CHAT_ID:
        print("[WARNING] Telegram token or chat ID not configured")
        return False

    text = (
        f"<b>✅ Video Uploaded Successfully!</b>\n\n"
        f"<b>Title:</b> {title}\n"
        f"<b>Account:</b> {account}\n"
        f"<b>Platform:</b> {platform}"
    )
    
    if link:
        text += f"\n<b>🔗 Link:</b> {link}"
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID, 
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload, timeout=24)
        response.raise_for_status()
        print(f"\n[SUCCESS] Telegram notification sent for {platform}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Failed to send to Telegram: {e}")
        return False

def send_job_notification(title, account, status="completed", error_msg=None):
    """Send Telegram notification for job status."""
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    if not TOKEN or not CHAT_ID:
        return False
    
    if status == "completed":
        emoji = "✅"
        status_text = "Completed Successfully"
    elif status == "failed":
        emoji = "❌"
        status_text = f"Failed: {error_msg}" if error_msg else "Failed"
    else:
        emoji = "⏳"
        status_text = "In Progress"
    
    text = (
        f"<b>{emoji} Job {status_text}</b>\n\n"
        f"<b>Title:</b> {title}\n"
        f"<b>Account:</b> {account}"
    )
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID, 
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload, timeout=24)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Failed to send job notification: {e}")
        return False

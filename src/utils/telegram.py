import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_to_telegram(title, account, platform, link):
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    text = (
        f"<b>Title:</b> {title}\n"
        f"<b>Account:</b> {account}\n"
        f"<b>Platform:</b> {platform}\n"
        f"<b>Link:</b> {link}"
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
        print(f"\n[SUCCESS] Telegram notification sent for {platform}")
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Failed to send to Telegram: {e}")

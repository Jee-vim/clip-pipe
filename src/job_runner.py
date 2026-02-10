import json
import os
import sys
import time
import random
from datetime import datetime
from types import SimpleNamespace
from dotenv import load_dotenv
from pipeline import process_pipeline
from pathlib import Path

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

JSON_FILE = DATA_DIR / "_jobs.json"

# Load configuration from environment
MIN_DELAY = int(os.getenv("MIN_DELAY", "30"))          
MAX_DELAY = int(os.getenv("MAX_DELAY", "60"))         
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Proxy configuration
PROXIES_STR = os.getenv("PROXIES", "")
PROXIES = [p.strip() for p in PROXIES_STR.split(",") if p.strip()] if PROXIES_STR else []
USE_PROXY = len(PROXIES) > 0  # Auto-enable if proxies are configured
proxy_index = 0

# Telegram configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")

def load_jobs(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {path} not found.")
        return []

def save_jobs(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def print_daily_summary(schedule):
    os.system('cls' if os.name == 'nt' else 'clear')
    
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n[INFO] Current date: {today}")
    
    found_pending = False
    for slot in schedule:
        date_str = slot.get("date", "")
        status = slot.get("status", "pending")
        
        if "," in date_str:
            slot_date, slot_time = date_str.split(",")
            if slot_date == today and status == "pending":
                count = len(slot.get("items", []))
                print(f"[PENDING] {count} Task(s) on {slot_time}")
                found_pending = True
            
    if not found_pending:
        print("[INFO] No pending tasks remaining for today.")

def get_next_proxy():
    global proxy_index
    if not PROXIES:
        return None
    proxy = PROXIES[proxy_index]
    proxy_index = (proxy_index + 1) % len(PROXIES)
    return proxy

def normalize_job(job, proxy):
    return SimpleNamespace(
        url=job.get("url"),
        local=job.get("local"),
        start=job["start"],
        end=job["end"],
        position=job.get("position", "c"),
        title=job.get("title", ""),
        description=job.get("description", ""),
        account=job.get("account", "random"),
        model=job.get("model", "small"),
        subs=job.get("subs", True),
        crop=job.get("crop", True),
        tests=job.get("tests", False),
        brainrot=job.get("brainrot", False),
        proxy=proxy
    )

def send_telegram_notification(title, account, platform, link=None):
    """Send Telegram notification for job completion."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    try:
        import requests
        
        text = (
            f"<b>Title:</b> {title}\n"
            f"<b>Account:</b> {account}\n"
            f"<b>Platform:</b> {platform}"
        )
        
        if link:
            text += f"\n<b>Link:</b> {link}"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        
        payload = {
            "chat_id": TELEGRAM_CHAT_ID, 
            "text": text,
            "parse_mode": "HTML"
        }

        response = requests.post(url, data=payload, timeout=24)
        response.raise_for_status()
        print(f"\n[SUCCESS] Telegram notification sent for {platform}")
        return True
    except Exception as e:
        print(f"\n[ERROR] Failed to send to Telegram: {e}")
        return False

def main():
    last_reported_date = None
    if PROXIES:
        print(f"[INFO] Starting job runner with {len(PROXIES)} proxies")
    else:
        print("[INFO] Starting job runner without proxy (PROXIES not configured)")
    print(f"[INFO] Telegram notifications: {'Enabled' if TELEGRAM_TOKEN else 'Disabled'}")
    
    while True:
        current_today = datetime.now().strftime("%Y-%m-%d")
        schedule = load_jobs(JSON_FILE)
        if current_today != last_reported_date:
            print_daily_summary(schedule)
            last_reported_date = current_today
        if not schedule:
            time.sleep(CHECK_INTERVAL)
            continue
        now_str = datetime.now().strftime("%Y-%m-%d,%H:%M")
        updated = False
        for slot in schedule:
            slot_time = slot.get("date")
            status = slot.get("status", "pending")
            if slot_time <= now_str and status == "pending":
                print(f"\n[INFO] Executing Slot: {slot_time}")
                items = slot.get("items", [])
                total = len(items)
                for i, job in enumerate(items, 1):
                    print(f"\n--- Item {i}/{total} ---")
                    retry_count = 0
                    success = False
                    
                    while retry_count <= MAX_RETRIES and not success:
                        try:
                            current_proxy = get_next_proxy()
                            if current_proxy:
                                print(f"[PROXY] Using: {current_proxy}")
                            
                            args_obj = normalize_job(job, current_proxy)
                            process_pipeline(args_obj)
                            success = True
                            
                            # Send Telegram notification on success
                            job_title = job.get("title", "Unknown")
                            job_account = job.get("account", "Unknown")
                            send_telegram_notification(job_title, job_account, "Video Processing")
                            
                        except Exception as e:
                            retry_count += 1
                            print(f"[FAILED] Attempt {retry_count}/{MAX_RETRIES}: {e}")
                            if retry_count <= MAX_RETRIES:
                                wait_time = random.randint(5, 15)
                                print(f"Retrying in {wait_time}s...")
                                time.sleep(wait_time)
                    
                    if not success:
                        print(f"[FAILED] Job failed after {MAX_RETRIES} attempts")
                    
                    if i < total:
                        wait_time = random.randint(MIN_DELAY, MAX_DELAY)
                        print(f"Waiting {wait_time}s before next job...")
                        time.sleep(wait_time)
                        
                slot["status"] = "completed"
                updated = True
                print(f"\n[INFO] Slot {slot_time} Marked as COMPLETED")
        if updated:
            save_jobs(JSON_FILE, schedule)
            last_reported_date = None 
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Operation cancelled. Exiting...")
        sys.exit(0)

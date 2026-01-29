import json
import os
import sys
import time
import random
from datetime import datetime
from types import SimpleNamespace
from pipeline import process_pipeline
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

JSON_FILE = DATA_DIR / "_jobs.json"
MIN_DELAY = 30          
MAX_DELAY = 60         

USE_PROXY = False  
PROXIES = [
    "http://user:pass@p1.example.com:8080",
    "http://user:pass@p2.example.com:8080",
    "http://user:pass@p3.example.com:8080"
]
proxy_index = 0

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
    if not USE_PROXY or not PROXIES:
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

def main():
    last_reported_date = None
    while True:
        current_today = datetime.now().strftime("%Y-%m-%d")
        schedule = load_jobs(JSON_FILE)
        if current_today != last_reported_date:
            print_daily_summary(schedule)
            last_reported_date = current_today
        if not schedule:
            time.sleep(60)
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
                    try:
                        current_proxy = get_next_proxy()
                        if current_proxy:
                            print(f"[PROXY] Using: {current_proxy}")
                        
                        args_obj = normalize_job(job, current_proxy)
                        process_pipeline(args_obj)
                        if i < total:
                            wait_time = random.randint(MIN_DELAY, MAX_DELAY)
                            print(f"Waiting {wait_time}s...")
                            time.sleep(wait_time)
                    except Exception as e:
                        print(f"[FAILED] {e}")
                slot["status"] = "completed"
                updated = True
                print(f"\n[INFO] Slot {slot_time} Marked as COMPLETED")
        if updated:
            save_jobs(JSON_FILE, schedule)
            last_reported_date = None 
        time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Operation cancelled. Exiting...")
        sys.exit(0)

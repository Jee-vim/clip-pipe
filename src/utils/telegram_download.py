import os
import json
import asyncio
import random
from dotenv import load_dotenv
from telethon import TelegramClient
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MEDIA_DIR = BASE_DIR / "media"

LOCAL_DIR = MEDIA_DIR / "local"
JSON_FILE = DATA_DIR / "_telegram.json"

load_dotenv()

async def download_telegram_videos(entity, start_date_str, end_date_str):
    API_ID = os.getenv("TELEGRAM_API_ID")
    API_HASH = os.getenv("TELEGRAM_API_HASH")
    
    date_format = "%B %d, %Y"
    start_date = datetime.strptime(start_date_str, date_format)
    end_date = datetime.strptime(end_date_str, date_format)
    
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    
    download_count = 0
    
    async with TelegramClient('session_name', API_ID, API_HASH) as client:
        print(f"[INFO] Checking {entity}...")
        
        messages = []
        async for message in client.iter_messages(entity, offset_date=end_date):
            if message.date.replace(tzinfo=None) < start_date:
                break
            if message.video:
                messages.append(message)

        total_videos = len(messages)
        for i, message in enumerate(messages):
            print(f"[INFO] Downloading video {i+1}/{total_videos} from {message.date}...")
            path = await message.download_media(file=str(LOCAL_DIR))
            
            if path:
                download_count += 1
                
                if i == total_videos - 1:
                    continue
                
                if download_count % 5 == 0:
                    print("[WAIT] Downloaded 5 videos, sleeping for 10s...")
                    await asyncio.sleep(10)
                else:
                    await asyncio.sleep(2)

async def run_from_json(json_file):
    with open(json_file, 'r') as f:
        channels = json.load(f)
    
    total_channels = len(channels)
    for index, item in enumerate(channels):
        await download_telegram_videos(
            item['username'], 
            item['start'], 
            item['end']
        )
        
        if index < total_channels - 1:
            delay = random.randint(20, 60)
            print(f"[INFO] Waiting {delay}s before next channel...")
            await asyncio.sleep(delay)
        else:
            print("[INFO] All channels processed.")

if __name__ == "__main__":
    if JSON_FILE.exists():
        asyncio.run(run_from_json(JSON_FILE))
    else:
        print(f"[ERROR] {JSON_FILE} not found")

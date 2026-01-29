import json
import os
from datetime import datetime, timedelta

def generate_jobs():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(base_dir, "data", "_jobs.json")
    
    existing_data = []
    existing_dates = set()
    
    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            try:
                existing_data = json.load(f)
                existing_dates = {entry["date"] for entry in existing_data}
            except json.JSONDecodeError:
                existing_data = []

    start_date = datetime(2026, 1, 29)
    end_date = datetime(2026, 2, 28)
    times = ["06:00", "12:00", "17:00", "18:00", "19:00"]
    
    new_entries = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        for t in times:
            full_date_key = f"{date_str},{t}"
            if full_date_key not in existing_dates:
                entry = {
                    "date": full_date_key,
                    "status": "pending",
                    "items": [
                        {
                            "url": "",
                            "start": "00:00:00",
                            "end": "00:00:00",
                            "position": "c",
                            "account": "obrolan_clip",
                            "title": "",
                            "description": ""
                        }
                    ]
                }
                new_entries.append(entry)
        current_date += timedelta(days=1)
    
    final_data = existing_data + new_entries
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(final_data, f, indent=2)

if __name__ == "__main__":
    generate_jobs()

from pathlib import Path
from utils.uploader.all import upload_by_account

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "media"

test_video = DATA_DIR / "shorts" / "subs.mp4"

if not test_video.exists():
    raise RuntimeError(f"Test video not found at: {test_video}")

print(f"[START] Testing upload for account: dopamine_drop555")
try:
    upload_by_account(
        video_path=str(test_video),
        title="TEST UPLOAD",
        desc="Test run #shorts #test",
        source="LOCAL",
        account="dopamine_drop555"
    )
    print("[FINISHED] Process completed.")
except Exception as e:
    print(f"[CRITICAL ERROR] Test failed: {e}")

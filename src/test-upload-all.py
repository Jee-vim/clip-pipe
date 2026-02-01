from pathlib import Path
from utils.uploader.all import upload_by_account
from utils.uploader.facebook import upload_facebook

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "media"

test_video = DATA_DIR / "shorts" / "subs.mp4"

if not test_video.exists():
    raise RuntimeError(f"Test video not found at: {test_video}")

print(f"[START] Testing upload...")
try:
    # upload_by_account(
    #     video_path=str(test_video),
    #     title="TEST UPLOAD",
    #     desc="Test run #shorts #test",
    #     source="LOCAL",
    #     account="obrolan_clip"
    # )
    upload_facebook(str(test_video), "TEST", "Test run #shorts #test", "obrolan_clip")
    print("[FINISHED] Process completed.")
except Exception as e:
    print(f"[CRITICAL ERROR] Test failed: {e}")

        

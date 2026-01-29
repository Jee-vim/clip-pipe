from pathlib import Path
from dotenv import dotenv_values

SRC_ROOT = Path(__file__).resolve().parents[1]
ACCOUNTS_DIR = SRC_ROOT / "accounts"

def get_meta(account):
    env_file = ACCOUNTS_DIR / account / "meta.env"
    if not env_file.exists():
        raise RuntimeError(f"Meta account not available for {account}")
    return dotenv_values(env_file)

def get_page_token(account):
    meta = get_meta(account)
    page_id = meta.get("FB_PAGE_ID")
    token = meta.get("FB_PAGE_TOKEN")
    if not page_id or not token:
        raise RuntimeError("FB_PAGE_ID or FB_PAGE_TOKEN missing")
    return page_id, token

def get_ig_token(account):
    meta = get_meta(account)
    ig_user_id = meta.get("IG_USER_ID")
    token = meta.get("IG_TOKEN")
    if not ig_user_id or not token:
        raise RuntimeError("IG_USER_ID or IG_TOKEN missing")
    return ig_user_id, token

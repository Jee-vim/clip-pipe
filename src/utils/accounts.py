from pathlib import Path
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

REQUESTED_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
BASE_DIR = Path(__file__).resolve().parents[2]
ACCOUNT_DIR = BASE_DIR / "accounts" 

def has_account(account: str, platform: str) -> bool:
    """Check if account exists, auto-generate YT credentials if missing (using pickle)"""
    acc_dir = ACCOUNT_DIR / account

    if not acc_dir.is_dir():
        print(f"[{account}] [{platform}] Account directory not found")
        return False

    if platform == "youtube":
        pickle_file = acc_dir / "yt_token.pickle"
        client_secret = acc_dir / "client_secret.json"
        
        # If pickle exists and is valid, we're good
        if pickle_file.exists():
            try:
                with open(pickle_file, 'rb') as f:
                    creds = pickle.load(f)
                
                if creds and creds.valid:
                    return True
                elif creds and creds.expired and creds.refresh_token:
                    print(f"\n[{account}] YouTube token expired, refreshing...")
                    try:
                        creds.refresh(Request())
                        # Save refreshed token
                        with open(pickle_file, 'wb') as f:
                            pickle.dump(creds, f)
                        return True
                    except:
                        print(f"\n[{account}]  Failed to refresh token")
                        pickle_file.unlink()  # Delete invalid pickle
            except Exception as e:
                print(f"[{account}] Pickle file corrupt: {e}")
                pickle_file.unlink()  # Delete corrupt pickle
        
        # If we get here, we need to generate new credentials
        if client_secret.exists():
            print(f"\n[{account}] No valid YouTube credentials, starting OAuth...")
            return _generate_youtube_pickle(account, acc_dir, client_secret)
        else:
            print(f"\n[{account}] Missing client_secret.json for YouTube")
            return False

    # FB and IG tokens are both stored in meta.env
    elif platform in ["facebook", "instagram"]:
        meta_env = acc_dir / "meta.env"
        if meta_env.is_file():
            return True
        else:
            print(f"[{account}] No meta.env for {platform.upper()}")
            return False

    return False


def _generate_youtube_pickle(account: str, acc_dir: Path, client_secret: Path) -> bool:
    """Generate YouTube OAuth credentials and save as pickle"""
    try:
        print(f"\n[{account}] Opening browser for Google login...")
        print(f"[{account}] Please login to the correct Google account!")
        print("-" * 50)
        
        flow = InstalledAppFlow.from_client_secrets_file(
            str(client_secret),
            REQUESTED_SCOPES
        )
        
        # Get credentials - accept whatever scopes Google gives us
        creds = flow.run_local_server(
            port=0,
            access_type='offline',
            prompt='consent'
        )
        
        # Check if we got the required scope
        required_scope = "https://www.googleapis.com/auth/youtube.upload"
        if required_scope not in creds.scopes:
            print(f"[{account}] Warning: Did not get required scope: {required_scope}")
            print(f"[{account}] Got scopes: {creds.scopes}")
            # Check if we have at least some YouTube scope
            youtube_scopes = [s for s in creds.scopes if 'youtube' in s]
            if not youtube_scopes:
                print(f"[{account}] No YouTube scopes granted!")
                return False
            else:
                print(f"[{account}] Using available YouTube scopes: {youtube_scopes}")
        
        # Save as pickle
        pickle_file = acc_dir / "yt_token.pickle"
        with open(pickle_file, 'wb') as f:
            pickle.dump(creds, f)
        
        print(f"[{account}] YouTube credentials saved as pickle!")
        print(f"[{account}] File: {pickle_file}")
        print(f"[{account}] Scopes granted: {creds.scopes}")
        return True
        
    except Exception as e:
        print(f"[{account}] Failed to generate credentials: {e}")
        return False


def get_youtube_service(account: str):
    """Get YouTube service with auto-refresh (pickle version)"""

    acc_dir = ACCOUNT_DIR / account
    pickle_file = acc_dir / "yt_token.pickle"
    client_secret = acc_dir / "client_secret.json"
    
    creds = None
    
    # Load existing credentials
    if pickle_file.exists():
        try:
            with open(pickle_file, 'rb') as f:
                creds = pickle.load(f)
        except Exception as e:
            print(f"[{account}] Error loading pickle: {e}")
            creds = None
    
    # Check validity and refresh if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print(f"[{account}] Refreshing expired token...")
                creds.refresh(Request())
                # Save refreshed token
                with open(pickle_file, 'wb') as f:
                    pickle.dump(creds, f)
                print(f"[{account}] Token refreshed")
            except Exception as e:
                print(f"[{account}] Failed to refresh: {e}")
                creds = None
    
    # If still no valid credentials, get new ones
    if not creds or not creds.valid:
        if not client_secret.exists():
            print(f"[{account}] Missing client_secret.json")
            return None
        
        print(f"[{account}] Getting new credentials...")
        flow = InstalledAppFlow.from_client_secrets_file(
            str(client_secret),
            REQUESTED_SCOPES
        )
        
        creds = flow.run_local_server(
            port=0,
            access_type='offline',
            prompt='consent'
        )
        
        # Save new credentials
        with open(pickle_file, 'wb') as f:
            pickle.dump(creds, f)
        print(f"[{account}] New credentials saved")
    
    # Build and return YouTube service
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=creds)

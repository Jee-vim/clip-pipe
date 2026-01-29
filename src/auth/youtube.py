from pathlib import Path
import pickle
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
BASE_DIR = Path(__file__).resolve().parents[2]
ACCOUNT_DIR = BASE_DIR / "accounts" 

def get_credentials(account: str):
    acc_dir = ACCOUNT_DIR / account

    pickle_file = acc_dir / "yt_token.pickle"
    client_secret = acc_dir / "client_secret.json"
    
    if not acc_dir.exists():
        raise RuntimeError(f"Account directory not found: {acc_dir}")
    
    if not client_secret.exists():
        raise RuntimeError(f"Missing client_secret.json for account '{account}'")
    
    creds = None
    
    if pickle_file.exists():
        try:
            with open(pickle_file, 'rb') as f:
                creds = pickle.load(f)
        except Exception as e:
            print(f"[{account}] Could not load pickle: {e}")
            creds = None
    
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
        else:
            print(f"[{account}] Getting new credentials...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(client_secret),
                SCOPES
            )
            
            creds = flow.run_local_server(
                port=0,
                access_type='offline',
                prompt='consent'
            )
            
            with open(pickle_file, 'wb') as f:
                pickle.dump(creds, f)
            print(f"[{account}] New credentials saved")
    
    return creds

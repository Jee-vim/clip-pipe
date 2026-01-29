from utils.accounts import has_account
from utils.uploader.youtube import upload_youtube
from utils.uploader.facebook import upload_facebook
from utils.uploader.instagram import upload_instagram

def upload_by_account(video_path, title, desc, source, account):
    final_desc = f"""{desc}

Source:
{source}
"""

    print(f"\n[INFO] Processing account: {account}")
    
    if has_account(account, "youtube"):
        upload_youtube(video_path, title, final_desc, account)
    
    if has_account(account, "facebook"):
        upload_facebook(video_path, title, final_desc, account)
    
    if has_account(account, "instagram"):
        upload_instagram(video_path, title, final_desc, account)

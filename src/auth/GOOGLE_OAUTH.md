GOOGLE OAUTH SETUP FOR YOUTUBE UPLOAD BOT
========================================
https://console.cloud.google.com/welcome

This guide explains how to create client_secret.json
and fix Error 403: access_denied.


------------------------------------------------------
1. CREATE GOOGLE CLOUD PROJECT
------------------------------------------------------

1. Open:
   https://console.cloud.google.com/

2. Click:
   Select project → New project

3. Project name:
   short-maker

4. Create.


------------------------------------------------------
2. ENABLE YOUTUBE DATA API
------------------------------------------------------

1. Go to:
   APIs & Services → Library

2. Search:
   YouTube Data API v3

3. Click:
   Enable


------------------------------------------------------
3. CONFIGURE OAUTH CONSENT SCREEN
------------------------------------------------------

Open:
APIs & Services → OAuth consent screen


--- A. Branding tab ---

App name:
short-maker

User support email:
your_email@gmail.com

Developer contact email:
your_email@gmail.com

Save.


--- B. Audience tab ---

User type:
External

Scroll to:
Test users

Click:
Add users

Add:
your_email@gmail.com

Save.


--- C. Data Access tab ---

Click:
Add or remove scopes

Add this scope:

https://www.googleapis.com/auth/youtube.upload

Save.


------------------------------------------------------
4. CREATE OAUTH CLIENT ID
------------------------------------------------------

Go to:
APIs & Services → Credentials

Click:
Create credentials → OAuth client ID

Application type:
Desktop app

Name:
short-maker-local

Click:
Create


------------------------------------------------------
5. DOWNLOAD CLIENT SECRET
------------------------------------------------------

After creation:

Click the download icon ⬇️

Save file as:

client_secret.json

Place it in your project folder:

short-maker/
 ├─ main.py
 ├─ upload.py
 ├─ client_secret.json
 ├─ requirements.txt


IMPORTANT:
client_secret.json MUST NOT be empty.


------------------------------------------------------
6. FIRST AUTHENTICATION RUN
------------------------------------------------------

Run:

python upload.py -f video.mp4 -t "test" -d "test"


Browser will open.

If you see warning:

"This app isn't verified"

Click:
Advanced → Continue


Login using the SAME email added as test user.


------------------------------------------------------
7. SUCCESS OUTPUT
------------------------------------------------------

After successful login, this file appears:

yt_token.pickle

This file stores your login token.

From now on:
- No browser needed
- Fully automatic uploads
- Safe for cron / VPS / scripts


------------------------------------------------------
8. COMMON ERRORS
------------------------------------------------------

ERROR:
Access blocked: app has not completed verification

FIX:
OAuth consent screen → Audience → add your email
as Test User.


ERROR:
client_secrets.json empty

FIX:
Re-download credentials from Google Cloud Console.


ERROR:
redirect_uri_mismatch

FIX:
OAuth client must be "Desktop App", not Web.

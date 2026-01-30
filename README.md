# Clip Pipe

End-to-end automation pipeline for turning long videos into short-form content and distributing them across multiple platforms automatically.

This project handles downloading videos, clipping by timestamp, formatting for shorts, adding subtitles, scheduling uploads, managing multiple accounts, and sending upload notifications via Telegram.

Built for batch processing and unattended execution.

---

## Features

- Download videos from YouTube by URL
- Clip videos using start and end timestamps
- Auto-generate short-form vertical videos
- Subtitle embedding (auto or provided)
- Video cropping and positioning
- Multi-account support
- Upload automation:
  - YouTube 
  - Instagram 
  - Facebook 
- Upload scheduling
- Telegram success notifications per platform
- Telegram video downloader
- Generate `jobs.json` automatically using date ranges
- Fully JSON-driven workflow

---

## Installation (Nix)

This project uses **Nix shell** for dependency management.

All required system tools and Python packages are provided automatically.

### Requirements

- Linux or WSL2 (Windows, not tested yet) 
- Nix package manager

---

### Install Nix

#### Windows (WSL2)

```bash
wsl --install
```
```bash
curl -L https://nixos.org/nix/install | sh
```

#### Linux 

```bash
curl -L https://nixos.org/nix/install | sh
```

#### Linux (Nixos)
```bash
nix-shell
```

## Env Setup
```

# for send notif to telegram bot when successfully upload to a each platform
# create bot using this bot official telegram `@BotFather`
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=

# (optional)
# for pull video from telegram channel
# get the api id and hash from below link
# https://my.telegram.org/apps
TELEGRAM_API_ID=
TELEGRAM_API_HASH=
```

## Authentication Setup

Authentication is already documented in detail.
Follow these guides exactly:

### Google (YouTube Shorts)
```

/src/auth/GOOGLE_OAUTH.md
```


Covers:

- Google Cloud project creation
- OAuth consent screen
- Client ID setup
- Refresh token generation

### Meta (Instagram & Facebook Reels)
```
/src/auth/META_GRAPH.md
```

## Account Configuration

You need to create an `accounts/` folder in project `root`,
then make a folder based username or account name ex: `obrolan_clip/`
inside that folder username add `client_secret.json` and `meta.env`

Complete folders accounts

``` bash
accounts/
 └── obrolan_clip/
     ├── client_secret.json
     └── meta.env
 └── other_account/
```


## Full JSON Configuration
```json
[
  {
    "date": "2026-01-28,12:00", # date for scheduling 
    "status": "pending",        # if already executed will change to completed
    "items": [
      {
        "url": "",           # url youtube
        "start": "00:06:18", # time start clip
        "end": "00:07:18",   # end  time clip (result will be 01:00 minute shorts video)
        "position": "c",     # position crop (l,c,r)
        "crop": true,        # by default true, if set to false it will not crop, but still make the video vertical  
        "subs": true,        # by default true, if set to false will skip fast-whisper (auto generate subtitle)
        "brainrot": false,   # if true it  will added other video below the original shorts
        "tests": false,      # if true will skip upload to social media and only download and saved to media/shorts/ 
        "account": "other_username", # acccount name  based on folder inside accounts/
        "title": "",         # title video
        "description": ""    # description (pass tags is accepted)
      }
    ]
  }
]
```

## Generete _jobs.json
it also has script for auto generating `_jobs.json` based date range you provide the script inside `./src/utils/generate_jobs.py`
open the script and change the date range u wanna generate

## Run
Enter folder `./src`
then run 
```
python3 job_runner.py
```

## Additional Info
It also have proxy configuration (to reduce the risk of YouTube rate limiting), but i've never use it since i don't have yet

The proxy config inside `job_runner.py`

## Disclaimer

This project is intended for educational and automation purposes only.

You are responsible for:

- API usage
- Platform rate limits
- Content ownership
- Compliance with YouTube, Meta, and Telegram policies

## TODO
- Test all social media (instagram and facebook)

import subprocess
import os
import yt_dlp
import random
from pathlib import Path
from .helpers import sanitize_filename

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
BRAINROT_DIR = BASE_DIR / "media" / "brainrot"

COOKIE_FILE = DATA_DIR / "_cookies.txt"

def get_video_info(url, proxy=None):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
    }
    
    if proxy:
        ydl_opts['proxy'] = proxy

    if COOKIE_FILE.exists():
        ydl_opts['cookiefile'] = str(COOKIE_FILE)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return sanitize_filename(info.get('title', 'video')), info.get('url')
    except Exception as e:
        print(f"[ERROR] Extraction failed: {e}")
        return None, None

def process_video(args, video_source, final_output_path, ass_file=None):
    # Get proxy from args
    proxy = getattr(args, 'proxy', None)

    # 1. Source Setup
    if args.local:
        local_path = Path(args.local)
        video_title = sanitize_filename(local_path.stem)
        video_source = str(local_path)
    else:
        if not video_source:
            # Pass proxy to yt-dlp
            video_title, video_source = get_video_info(args.url, proxy=proxy)
        else:
            video_title = args.title or "video"

    # 2. Filter & Command Construction
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    
    # Network options for URL source
    if str(video_source).startswith("http"):
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        # Add proxy to FFmpeg if provided
        if proxy:
            cmd += ["-http_proxy", proxy]
            
        cmd += ["-reconnect", "1", "-reconnect_streamed", "1", "-reconnect_delay_max", "5", "-headers", f"User-Agent: {ua}\r\n"]

    target_h = 1350
    target_w = 760
    
    if getattr(args, 'brainrot', False):
        clip_files = list(BRAINROT_DIR.glob("*.mp4"))
        if not clip_files:
            raise FileNotFoundError(f"No brainrot clips found in: {BRAINROT_DIR.absolute()}")
        
        random_clip = str(random.choice(clip_files))
        bw, bh = 1080, 960 
        
        top_filter = f"scale={bw}:{bh}:force_original_aspect_ratio=increase,crop={bw}:{bh},setsar=1"
        if ass_file:
            abs_ass = Path(ass_file).absolute().as_posix().replace(":", "\\:")
            top_filter += f",subtitles='{abs_ass}'"
        
        bottom_filter = f"scale={bw}:{bh}:force_original_aspect_ratio=increase,crop={bw}:{bh},setsar=1"

        filter_complex = (
            f"[0:v]{top_filter}[top];"
            f"[1:v]{bottom_filter}[bottom];"
            f"[top][bottom]vstack=inputs=2,format=yuv420p"
        )

        cmd += [
            "-ss", str(args.start), "-to", str(args.end), "-i", str(video_source),
            "-stream_loop", "-1", "-i", random_clip,
            "-filter_complex", filter_complex,
            "-map", "0:a", "-shortest"
        ]
    else:
        crop_x_map = {"l": "0", "r": "iw/2", "c": "iw/4"}
        crop_x = crop_x_map.get(args.position, "iw/4")
        
        filters = ["format=yuv420p"]
        if args.crop:
            filters.insert(0, f"scale=-1:{target_h}")
            filters.append(f"crop='if(gt(iw,ih),iw/2,iw)':{target_h}:{crop_x}:0")
        else:
            filters.insert(0, f"scale={target_w}:-1")
            filters.append(f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2")

        if ass_file:
            abs_ass = Path(ass_file).absolute().as_posix().replace(":", "\\:")
            filters.append(f"subtitles='{abs_ass}'")

        cmd += [
            "-ss", str(args.start), "-to", str(args.end), "-i", str(video_source),
            "-vf", ",".join(filters)
        ]

    # 3. Common Encoding Settings
    cmd += [
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-avoid_negative_ts", "make_zero",
        str(final_output_path)
    ]

    subprocess.run(cmd, check=True)
    return video_title

import argparse
import subprocess
from pathlib import Path
from uuid import uuid4
from utils.helpers import run_with_spinner 
from utils.video import get_video_info, process_video
from utils.ai import load_whisper, transcribe, build_ass
from utils.uploader.all import upload_by_account

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"
SHORTS_DIR = MEDIA_DIR / "shorts"

def process_pipeline(args):
    SHORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get proxy from args (added via job_runner)
    proxy = getattr(args, 'proxy', None)

    # 1. Source Selection
    if args.local:
        src_path = Path(args.local).absolute()
        video_source = str(src_path)
        video_title = src_path.stem
    else:
        # Pass proxy to yt-dlp extractor
        video_title, video_source = run_with_spinner(
            "Extracting Stream URL", 
            lambda: get_video_info(args.url, proxy=proxy)
        )

    # 2. Extract Audio for AI
    temp_audio = SHORTS_DIR / f"temp_audio_{uuid4().hex[:8]}.wav"
    
    def extract_audio():
        cmd = ["ffmpeg", "-y", "-ss", args.start, "-to", args.end]
        
        # If using proxy for network stream
        if proxy and str(video_source).startswith("http"):
            cmd += ["-http_proxy", proxy]
            
        cmd += [
            "-i", video_source, 
            "-vn", "-ac", "1", "-ar", "16000", str(temp_audio)
        ]
        return subprocess.run(cmd, capture_output=True, check=True)

    run_with_spinner("Extracting Audio for AI", extract_audio)

    # 3. AI Transcription
    ass_file = None
    if args.subs:
        model = run_with_spinner("Loading AI", lambda: load_whisper(args.model))
        segments = run_with_spinner("Transcribing", lambda: transcribe(model, str(temp_audio)))
        ass_file = run_with_spinner(
            "Building Subtitles", 
            lambda: build_ass(segments, video_title, SHORTS_DIR, args.account)
        )

    # 4. Final Render
    out_name = args.title or video_title
    short_video = SHORTS_DIR / f"{out_name}.mp4"
    
    run_with_spinner(
        "Rendering Final Video",
        lambda: process_video(args, video_source, short_video, ass_file)
    )

    # 5. Delivery
    upload_success = False

    if not args.tests:
        try:
            run_with_spinner(
                "Uploading...",
                lambda: upload_by_account(
                    video_path=short_video,
                    title=out_name,
                    desc=args.description,
                    source=args.url or "Local",
                    account=args.account
                )
            )
            upload_success = True

        except Exception as e:
            print(f"\n[UPLOAD FAILED] {e}")
            print(f"[KEPT] Video saved at: {short_video}")

    # 6. Cleanup
    for f in [temp_audio, ass_file]:
        if f and f.exists():
            f.unlink()

    if not args.tests and upload_success and short_video.exists():
        short_video.unlink()

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", "--url")
    group.add_argument("-l", "--local")
    parser.add_argument("-s", "--start", required=True)
    parser.add_argument("-e", "--end", required=True)
    parser.add_argument("-p", "--position", choices=["c","l","r"], default="c")
    parser.add_argument("-t", "--title", required=True)
    parser.add_argument("-d", "--description", required=True)
    parser.add_argument("-a", "--account", default="obrolan_clip")
    parser.add_argument("-m", "--model", default="small")
    parser.add_argument("--no-subs", dest="subs", action="store_false")
    parser.set_defaults(subs=True)
    parser.add_argument("--no-crop", dest="crop", action="store_false")
    parser.set_defaults(crop=True)
    parser.add_argument("--tests", action="store_true")
    parser.add_argument("--brainrot", action="store_true")
    # Add proxy argument for CLI usage
    parser.add_argument("--proxy", default=None)

    args = parser.parse_args()
    try:
        process_pipeline(args)
        print("\n[DONE] Process Finished!")
    except Exception as e:
        print(f"\n[ERROR] {e}")

if __name__ == "__main__":
    main()

import random
import json
import os
from pathlib import Path
from faster_whisper import WhisperModel
from .helpers import sec_to_ass


def load_whisper(model_size):
    return WhisperModel(model_size, device="cpu", compute_type="int8")


def transcribe(model, video_path):
    segs, _ = model.transcribe(
        str(video_path),
        beam_size=5,
        word_timestamps=True
    )
    return list(segs)


def add_watermark(lines, text, duration, position="center"):
    positions = {
        "top-left": "{\\an7}",
        "top-right": "{\\an9}",
        "bottom-left": "{\\an1}",
        "bottom-right": "{\\an3}",
        "center": "{\\an5}",
    }

    align = positions.get(position, "{\\an3}")

    watermark = (
        f"Dialogue: 0,0:00:00.00,{duration},Default,,0,0,0,,"
        f"{align}{{\\fs40\\alpha&H80&}}{text}\n"
    )

    lines.append(watermark)


def build_ass(segments, video_title, output_dir, account_name):
    ass_file = output_dir / f"{video_title}.ass"

    colors = [
        "&H00FFFF&",
        "&H00D7FF&",
        "&H00FF00&",
        "&HFF00FF&",
        "&H00A5FF&"
    ]
    highlight = random.choice(colors)

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,70,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,4,0,2,40,40,400,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = [header]

    last_end = 0.0

    for seg in segments:
        if not seg.words:
            continue

        for w in seg.words:
            start = sec_to_ass(w.start)
            end = sec_to_ass(w.end)

            last_end = max(last_end, w.end)

            text = (
                f"{{\\c{highlight}\\fscx120\\fscy120}}"
                f"{w.word.strip()}"
                f"{{\\c&HFFFFFF&\\fscx100\\fscy100}}"
            )

            lines.append(
                f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"
            )

    # ✅ add watermark for full video duration
    if account_name:
        total_duration = sec_to_ass(last_end)
        add_watermark(
            lines,
            text=account_name,
            duration=total_duration,
            position="center"   # change if you want
        )

    ass_file.write_text("".join(lines), encoding="utf-8")
    return ass_file


def generate_content_automatically(video_path, transcript_text=""):
    """Generate Indonesian title, description, and hashtags for video content"""
    
    # For now, create simple content generation based on filename or transcript
    # In a real implementation, you would use OpenAI API or similar
    video_name = Path(video_path).stem
    
    # Extract keywords from video name or transcript
    keywords = extract_keywords(video_name, transcript_text)
    
    # Generate Indonesian title
    titles = [
        f"Video Keren: {keywords.get('topic', 'Menarik')}!",
        f"Intip {keywords.get('topic', 'Konten')} Yang Bikin Kaget",
        f"Wajib Tonton! {keywords.get('topic', 'Informasi')} Terbaru",
        f"Seru Banget! {keywords.get('topic', 'Hiburan')} Spesial",
        f"Mantul! {keywords.get('topic', 'Konten')} Kekinian"
    ]
    
    title = random.choice(titles)
    
    # Generate Indonesian description
    descriptions = [
        f"Halo guys! Kali ini kita bahas tentang {keywords.get('topic', 'sesuatu yang menarik')}. Simak ya sampai habis! Jangan lupa share ke teman-teman kalian ya 🎯 {generate_hashtags()}",
        f"Konten special untuk kalian semua! {keywords.get('topic', 'Topik menarik')} yang wajib kalian tonton. Like, comment, dan share ya! 🎉 {generate_hashtags()}",
        f"Video kali ini membahas {keywords.get('topic', 'informasi penting')} yang mungkin belum kalian ketahui. Yuk simak sampai selesai! 💡 {generate_hashtags()}",
        f"Wah seru banget {keywords.get('topic', 'konten ini')}! Buat kalian yang suka dengan hal-hal menarik, wajib nonton video ini! 🔥 {generate_hashtags()}"
    ]
    
    description = random.choice(descriptions)
    
    return {
        "title": title,
        "description": description
    }


def extract_keywords(video_name, transcript_text=""):
    """Extract keywords from video name and transcript"""
    # Simple keyword extraction - can be enhanced with NLP
    words = video_name.replace('_', ' ').replace('-', ' ').split()
    
    # Add some common Indonesian keywords
    common_topics = ["Tutorial", "Tips", "Info", "Berita", "Hiburan", "Edukasi", "Viral", "Trend", "Keren", "Seru", "Mantap"]
    
    # Find topic from video name or use random common topic
    topic = None
    for word in words:
        for common_topic in common_topics:
            if common_topic.lower() in word.lower():
                topic = common_topic
                break
        if topic:
            break
    
    if not topic:
        topic = random.choice(common_topics)
    
    return {
        "topic": topic,
        "words": words[:5]  # Limit to first 5 words
    }


def generate_hashtags():
    """Generate hashtags for social media"""
    base_hashtags = ["#clip #short #reels"]
    
    # Additional Indonesian hashtags
    extra_hashtags = [
        "#viralindonesia",
        "#trending", 
        "#fyp",
        "#explore",
        "#indonesia",
        "#videoviral",
        "#kontencreator",
        "#dagelan",
        "#videolucu",
        "#inspirasi"
    ]
    
    # Select 2-3 extra hashtags randomly
    selected = random.sample(extra_hashtags, random.randint(2, 3))
    return base_hashtags[0] + " " + " ".join(selected)


def auto_generate_jobs_from_media(media_dir, output_file="_jobs.json"):
    """Automatically generate _jobs.json from media files"""
    media_path = Path(media_dir)
    if not media_path.exists():
        print(f"Media directory {media_dir} not found")
        return
    
    # Find video files
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    video_files = []
    for ext in video_extensions:
        video_files.extend(media_path.glob(f"*{ext}"))
    
    if not video_files:
        print("No video files found")
        return
    
    jobs = []
    
    for video_file in video_files:
        # Generate content for this video
        content = generate_content_automatically(str(video_file))
        
        # Create job item
        job_item = {
            "url": str(video_file),
            "start": "00:00:00",  # Default start time
            "end": "00:01:00",    # Default 1 minute duration
            "position": "c",
            "crop": True,
            "subs": True,
            "brainrot": False,
            "tests": False,
            "account": "obrolan_clip",
            "title": content["title"],
            "description": content["description"]
        }
        
        jobs.append(job_item)
    
    # Create job structure
    from datetime import datetime
    now = datetime.now()
    date_str = f"{now.strftime('%Y-%m-%d')},{now.strftime('%H:%M')}"
    
    jobs_data = [{
        "date": date_str,
        "status": "pending",
        "items": jobs
    }]
    
    # Write to JSON file
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(jobs_data, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {len(jobs)} jobs in {output_path}")
    return jobs_data

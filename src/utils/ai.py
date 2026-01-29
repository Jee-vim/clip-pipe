import random
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

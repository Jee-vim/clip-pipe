import re
import sys
import time
import threading
import itertools

def normalize_time(t):
    if not t: return "00_00"
    if ":" in t:
        parts = t.split(":")
        if len(parts) == 2:
            m, s = parts
            total = int(m) * 60 + int(float(s))
        else:
            h, m, s = parts
            total = int(h) * 3600 + int(m) * 60 + int(float(s))
    else:
        total = int(float(t))
    return f"{total//60:02d}:{total%60:02d}"

def sanitize_filename(s):
    s = s.encode("ascii", "ignore").decode("ascii") 
    return re.sub(r"[^\w\s-]", "", s).strip().replace(" ", "_")

def sec_to_ass(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

stop_spinner = threading.Event()
def spinner(msg):
    chars = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    while not stop_spinner.is_set():
        sys.stderr.write(f"\r\033[K[INFO] {msg} {next(chars)}")
        sys.stderr.flush()
        time.sleep(0.1)
    sys.stderr.write("\r\033[K")
    sys.stderr.flush()

def run_with_spinner(msg, func):
    stop_spinner.clear()
    t = threading.Thread(target=spinner, args=(msg,), daemon=True)
    t.start()
    try:
        return func()
    except Exception as e:
        stop_spinner.set()
        t.join()
        raise e
    finally:
        stop_spinner.set()
        t.join()

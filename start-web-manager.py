#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Change to web-manager directory
script_dir = Path(__file__).parent
web_dir = script_dir / "web-manager"
os.chdir(web_dir)

# Import and run server
if __name__ == "__main__":
    import subprocess
    subprocess.run([sys.executable, "server.py"])

#!/usr/bin/env python3
"""
Simple test command for clip-pipes pipeline.
Usage: python3 simple_test.py
"""

import sys
import subprocess
from pathlib import Path

def main():
    print("🧪 Clip-Pipes Simple Test")
    print("=" * 40)
    
    # Check if test video exists
    test_video = Path("media/brainrot/brainrot_capucino.mp4")
    
    if not test_video.exists():
        print(f"❌ Test video not found: {test_video}")
        print("📁 Please make sure the video file exists")
        return False
    
    print(f"📁 Using test video: {test_video}")
    print("🧪 Running pipeline test...")
    print()
    
    # Build the command
    cmd = [
        sys.executable, "src/pipeline.py",
        "--local", str(test_video),
        "--start", "00:00:05",
        "--end", "00:00:15", 
        "--title", "Test Video - Brainrot Capucino",
        "--description", "Test video for pipeline validation",
        "--account", "test_account",
        "--tests",
        "--model", "tiny"
    ]
    
    try:
        # Run the pipeline
        result = subprocess.run(cmd, check=True)
        
        print()
        print("✅ Test completed successfully!")
        print("📁 Check the output in: media/shorts/")
        
        # Check if output file was created
        output_file = Path("media/shorts/Test Video - Brainrot Capucino.mp4")
        if output_file.exists():
            print(f"📹 Output file: {output_file}")
            print(f"📏 File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Test failed with exit code: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
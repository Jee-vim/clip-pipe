#!/usr/bin/env python3
"""
Test runner for clip-pipes pipeline.
Tests the pipeline without yt-dlp and platform uploads.
"""

import sys
import os
from pathlib import Path
from types import SimpleNamespace

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline import process_pipeline
print("✅ Successfully imported pipeline")

def test_local_video():
    """Test the pipeline with a local video file."""
    
    # Test configuration
    test_args = SimpleNamespace(
        local="/home/jee/Work/personal/cli/clip-pipes/media/brainrot/brainrot_capucino.mp4",
        start="00:00:05",
        end="00:00:15",
        position="c",
        account="test_account",
        title="Test Video - Brainrot Capucino",
        description="This is a test video for testing the pipeline without uploads",
        tests=True,  # This skips uploads!
        model="tiny",  # Use tiny model for faster testing
        subs=True,
        crop=True,
        brainrot=False,
        proxy=None
    )
    
    print("🧪 Testing pipeline with local video...")
    print(f"📁 Video: {test_args.local}")
    print(f"⏱️  Time: {test_args.start} - {test_args.end}")
    print(f"🎯 Test mode: {test_args.tests}")
    print(f"🤖 AI model: {test_args.model}")
    print()
    
    try:
        # Run the pipeline
        process_pipeline(test_args)
        print("\n✅ Test completed successfully!")
        print("📁 Check the output in: media/shorts/")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

def test_with_mock_video():
    """Test with a mock video (creates a simple test video)."""
    
    print("🧪 Creating test video...")
    
    # Create a simple test video using ffmpeg
    test_video = Path("media/test_video.mp4")
    test_video.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate a 10-second test video with color bars
    import subprocess
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "testsrc=duration=10:size=320x240:rate=30",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "23",
        str(test_video)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ Created test video: {test_video}")
        
        # Test with the created video
        test_args = SimpleNamespace(
            local=str(test_video),
            start="00:00:02",
            end="00:00:08",
            position="c",
            account="test_account",
            title="Generated Test Video",
            description="Auto-generated test video for pipeline testing",
            tests=True,
            model="tiny",
            subs=True,
            crop=True,
            brainrot=False,
            proxy=None
        )
        
        print("🧪 Testing pipeline with generated video...")
        process_pipeline(test_args)
        print("\n✅ Test completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create test video: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main test runner."""
    print("🚀 Clip-Pipes Test Runner")
    print("=" * 50)
    
    # Check if test video exists
    test_video = Path("/home/jee/Work/personal/cli/clip-pipes/media/brainrot/brainrot_capucino.mp4")
    
    if test_video.exists():
        print("📁 Found existing test video")
        success = test_local_video()
    else:
        print("📁 No test video found, creating one...")
        success = test_with_mock_video()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
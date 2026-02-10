#!/usr/bin/env bash

# Simple test script for clip-pipes
echo "🧪 Testing Clip-Pipes Pipeline..."

# Check if we're in nix-shell
if [ -z "$IN_NIX_SHELL" ]; then
    echo "📦 Entering nix-shell..."
    exec nix-shell --run "$0 $*"
fi

echo "✅ Nix environment loaded"

# Test with existing video
TEST_VIDEO="/home/jee/Work/personal/cli/clip-pipes/media/brainrot/brainrot_capucino.mp4"

if [ -f "$TEST_VIDEO" ]; then
    echo "📁 Found test video: $TEST_VIDEO"
    echo "🧪 Running pipeline test..."
    
    python src/pipeline.py \
        --local "$TEST_VIDEO" \
        --start "00:00:05" \
        --end "00:00:15" \
        --title "Test Video - Brainrot Capucino" \
        --description "Test video for pipeline validation" \
        --account "test_account" \
        --tests \
        --model tiny
    
    echo "✅ Test completed! Check media/shorts/ for output."
else
    echo "❌ Test video not found: $TEST_VIDEO"
    echo "📁 Please make sure the video file exists"
    exit 1
fi
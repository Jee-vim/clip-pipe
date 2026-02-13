#!/usr/bin/env python3
"""
Comprehensive upload test for clip-pipes pipeline.
Tests individual platform uploads to YouTube, Instagram, and Facebook.
Usage: python3 test_upload.py [platform] [account_name]
Examples:
  python3 test_upload.py youtube test_account
  python3 test_upload.py instagram test_account  
  python3 test_upload.py facebook test_account
  python3 test_upload.py all test_account
"""

import sys
import json
import os
import tempfile
import unittest.mock as mock
from pathlib import Path
from datetime import datetime

# Add src to path for direct imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import modules directly - this will work if we're in the right directory
try:
    from utils.uploader.all import upload_by_account
    from utils.uploader.youtube import upload_youtube, can_upload, update_upload_count
    from utils.uploader.instagram import upload_instagram, can_upload_ig, update_ig_count
    from utils.uploader.facebook import upload_facebook, can_upload_fb, update_fb_count
    from utils.accounts import has_account
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this test from the clip-pipes directory")
    sys.exit(1)

def create_test_video():
    """Create a temporary test video file"""
    temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    # Write some dummy video data
    temp_file.write(b"fake video content for testing")
    temp_file.close()
    return temp_file.name

def cleanup_test_file(filepath):
    """Clean up test file"""
    try:
        os.unlink(filepath)
    except:
        pass

class MockUploadTest:
    def __init__(self):
        self.test_results = []
        
    def log_test(self, platform, account, test_name, success, message=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'platform': platform,
            'account': account,
            'test': test_name,
            'success': success,
            'message': message
        })
        print(f"{status} [{platform}] [{account}] {test_name}")
        if message:
            print(f"    {message}")
    
    def mock_youtube_upload(self, video_path, title, description, account):
        """Mock YouTube upload for testing"""
        print(f"[MOCK] YouTube upload called for {account}")
        print(f"  Video: {video_path}")
        print(f"  Title: {title}")
        print(f"  Description: {description[:100]}...")
        return {"id": "mock_youtube_video_id_123"}
    
    def mock_instagram_upload(self, video_url, title, description, account):
        """Mock Instagram upload for testing"""
        print(f"[MOCK] Instagram upload called for {account}")
        print(f"  Video URL: {video_url}")
        print(f"  Title: {title}")
        print(f"  Description: {description[:100]}...")
        return {"id": "mock_ig_media_id_456"}
    
    def mock_facebook_upload(self, video_path, title, description, account):
        """Mock Facebook upload for testing"""
        print(f"[MOCK] Facebook upload called for {account}")
        print(f"  Video: {video_path}")
        print(f"  Title: {title}")
        print(f"  Description: {description[:100]}...")
        return {"id": "mock_fb_video_id_789"}

def test_single_platform_upload(platform, account_name, use_mock=True):
    """Test upload to a single platform"""
    print(f"\n🧪 Testing {platform.upper()} upload for account: {account_name}")
    print("=" * 60)
    
    test_instance = MockUploadTest()
    test_video_path = create_test_video()
    
    try:
        # Test account availability
        has_acc = has_account(account_name, platform)
        test_instance.log_test(platform, account_name, "Account Check", has_acc,
                             "Account credentials found" if has_acc else "Account credentials missing")
        
        if not has_acc and not use_mock:
            print(f"\n⚠️  No {platform} account found for '{account_name}'. Use --mock to test with mock data.")
            return False
        
        # Test rate limiting functionality
        if platform == "youtube":
            can_upload_before = can_upload(account_name)
            test_instance.log_test(platform, account_name, "Rate Limit Check (Before)", can_upload_before,
                                 "Can upload" if can_upload_before else "Rate limited")
        elif platform == "instagram":
            can_upload_before = can_upload_ig(account_name)
            test_instance.log_test(platform, account_name, "Rate Limit Check (Before)", can_upload_before,
                                 "Can upload" if can_upload_before else "Rate limited")
        elif platform == "facebook":
            can_upload_before = can_upload_fb(account_name)
            test_instance.log_test(platform, account_name, "Rate Limit Check (Before)", can_upload_before,
                                 "Can upload" if can_upload_before else "Rate limited")
        
        # Prepare upload parameters
        title = f"Test Video - {platform.upper()} - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        description = f"This is a test video for {platform} upload testing.\n\nAccount: {account_name}"
        source = f"Test Source - {platform}"
        
        # Initialize result
        result = None
        
        # Mock the upload functions if requested
        if use_mock:
            mock_instance = test_instance
            
            if platform == "youtube":
                with mock.patch('src.utils.uploader.youtube.upload_youtube', 
                              side_effect=mock_instance.mock_youtube_upload):
                    result = upload_youtube(test_video_path, title, description, account_name)
            elif platform == "instagram":
                with mock.patch('src.utils.uploader.instagram.upload_instagram',
                              side_effect=mock_instance.mock_instagram_upload):
                    result = upload_instagram(test_video_path, title, description, account_name)
            elif platform == "facebook":
                with mock.patch('src.utils.uploader.facebook.upload_facebook',
                              side_effect=mock_instance.mock_facebook_upload):
                    result = upload_facebook(test_video_path, title, description, account_name)
        else:
            # Real upload
            if platform == "youtube":
                result = upload_youtube(test_video_path, title, description, account_name)
            elif platform == "instagram":
                result = upload_instagram(test_video_path, title, description, account_name)
            elif platform == "facebook":
                result = upload_facebook(test_video_path, title, description, account_name)
        
        # Test upload result
        upload_success = result is not None
        test_instance.log_test(platform, account_name, "Upload Function", upload_success,
                             f"Result: {result}" if result else "Upload failed or returned None")
        
        # Test upload count tracking (only if upload was successful)
        if upload_success:
            if platform == "youtube":
                update_upload_count(account_name)
                test_instance.log_test(platform, account_name, "Upload Count Update", True,
                                     "YouTube upload count updated")
            elif platform == "instagram":
                update_ig_count(account_name)
                test_instance.log_test(platform, account_name, "Upload Count Update", True,
                                     "Instagram upload count updated")
            elif platform == "facebook":
                update_fb_count(account_name)
                test_instance.log_test(platform, account_name, "Upload Count Update", True,
                                     "Facebook upload count updated")
        
    except Exception as e:
        test_instance.log_test(platform, account_name, "Upload Test", False, f"Exception: {str(e)}")
    
    finally:
        cleanup_test_file(test_video_path)
    
    # Print summary
    print(f"\n📊 Test Summary for {platform.upper()}:")
    print("-" * 40)
    passed = sum(1 for r in test_instance.test_results if r['success'])
    total = len(test_instance.test_results)
    print(f"Tests Passed: {passed}/{total}")
    
    for result in test_instance.test_results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['test']}")
        if result['message']:
            print(f"   {result['message']}")
    
    return passed == total

def test_all_platforms(account_name, use_mock=True):
    """Test upload to all platforms for an account"""
    print(f"\n🧪 Testing ALL platforms for account: {account_name}")
    print("=" * 60)
    
    platforms = ["youtube", "instagram", "facebook"]
    results = {}
    
    for platform in platforms:
        print(f"\n--- Testing {platform.upper()} ---")
        try:
            results[platform] = test_single_platform_upload(platform, account_name, use_mock)
        except Exception as e:
            print(f"❌ {platform.upper()} test failed with exception: {e}")
            results[platform] = False
    
    # Overall summary
    print(f"\n🏁 Overall Test Summary:")
    print("=" * 40)
    passed_platforms = sum(1 for success in results.values() if success)
    total_platforms = len(platforms)
    
    print(f"Platforms Passed: {passed_platforms}/{total_platforms}")
    for platform, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {platform.upper()}")
    
    return passed_platforms == total_platforms

def test_upload_by_account(account_name, use_mock=True):
    """Test the upload_by_account function"""
    print(f"\n🧪 Testing upload_by_account for: {account_name}")
    print("=" * 60)
    
    test_instance = MockUploadTest()
    test_video_path = create_test_video()
    
    try:
        title = f"Test Video - All Platforms - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        description = f"This is a test video for all platforms.\n\nAccount: {account_name}"
        source = "Test Source - All Platforms"
        
        if use_mock:
            # Mock all upload functions
            with mock.patch('src.utils.uploader.youtube.upload_youtube',
                          side_effect=test_instance.mock_youtube_upload), \
                 mock.patch('src.utils.uploader.instagram.upload_instagram',
                          side_effect=test_instance.mock_instagram_upload), \
                 mock.patch('src.utils.uploader.facebook.upload_facebook',
                          side_effect=test_instance.mock_facebook_upload):
                
                upload_by_account(test_video_path, title, description, source, account_name)
        else:
            upload_by_account(test_video_path, title, description, source, account_name)
        
        test_instance.log_test("all", account_name, "upload_by_account Function", True,
                             "Function completed without errors")
        
    except Exception as e:
        test_instance.log_test("all", account_name, "upload_by_account Function", False,
                             f"Exception: {str(e)}")
    
    finally:
        cleanup_test_file(test_video_path)
    
    # Print results
    passed = sum(1 for r in test_instance.test_results if r['success'])
    total = len(test_instance.test_results)
    print(f"\n📊 upload_by_account Test Summary:")
    print(f"Tests Passed: {passed}/{total}")
    
    return passed == total

def print_usage():
    """Print usage instructions"""
    print("🧪 Clip-Pipes Upload Test")
    print("=" * 40)
    print("Usage:")
    print("  python3 test_upload.py [platform] [account_name] [options]")
    print()
    print("Platforms:")
    print("  youtube     Test YouTube upload")
    print("  instagram   Test Instagram upload")
    print("  facebook    Test Facebook upload")
    print("  all         Test all platforms")
    print("  combined    Test upload_by_account function")
    print()
    print("Account Name: Name of the account to test (must exist in accounts/ directory)")
    print()
    print("Options:")
    print("  --mock      Use mock functions (no real uploads)")
    print("  --real      Perform real uploads (requires valid credentials)")
    print()
    print("Examples:")
    print("  python3 test_upload.py youtube test_account --mock")
    print("  python3 test_upload.py all test_account --mock")
    print("  python3 test_upload.py combined test_account --mock")

def main():
    if len(sys.argv) < 3:
        print_usage()
        return False
    
    platform = sys.argv[1].lower()
    account_name = sys.argv[2]
    
    # Determine if using mock or real uploads
    use_mock = "--mock" in sys.argv or "--real" not in sys.argv
    
    print(f"🧪 Clip-Pipes Upload Test")
    print(f"Platform: {platform}")
    print(f"Account: {account_name}")
    print(f"Mode: {'MOCK' if use_mock else 'REAL'}")
    print("=" * 40)
    
    success = False
    
    try:
        if platform == "all":
            success = test_all_platforms(account_name, use_mock)
        elif platform == "combined":
            success = test_upload_by_account(account_name, use_mock)
        elif platform in ["youtube", "instagram", "facebook"]:
            success = test_single_platform_upload(platform, account_name, use_mock)
        else:
            print(f"❌ Unknown platform: {platform}")
            print_usage()
            return False
        
        if success:
            print(f"\n🎉 All tests passed!")
        else:
            print(f"\n❌ Some tests failed!")
        
        return success
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
"""Tests for video_downloader module."""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestURLPatterns:
    """Test URL pattern matching."""
    
    def test_youtube_video_url(self):
        """Test YouTube video URL pattern."""
        from video_downloader import YOUTUBE_VIDEO_PATTERN
        
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=abc123XYZ-_",
        ]
        
        for url in valid_urls:
            assert YOUTUBE_VIDEO_PATTERN.search(url), f"Should match: {url}"
    
    def test_youtube_playlist_url(self):
        """Test YouTube playlist URL pattern."""
        from video_downloader import YOUTUBE_PLAYLIST_PATTERN
        
        valid_urls = [
            "https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxxx",
            "https://youtube.com/playlist?list=PLtest123",
        ]
        
        for url in valid_urls:
            assert YOUTUBE_PLAYLIST_PATTERN.search(url), f"Should match: {url}"
    
    def test_bilibili_video_url(self):
        """Test Bilibili video URL pattern."""
        from video_downloader import BILIBILI_VIDEO_PATTERN
        
        valid_urls = [
            "https://www.bilibili.com/video/BV1xx411c7mD",
            "https://bilibili.com/video/BV1234567890",
        ]
        
        for url in valid_urls:
            assert BILIBILI_VIDEO_PATTERN.search(url), f"Should match: {url}"


class TestVersionInfo:
    """Test version information."""
    
    def test_app_version_exists(self):
        """Test APP_VERSION is defined."""
        from video_downloader import APP_VERSION
        
        assert APP_VERSION is not None
        assert APP_VERSION.startswith("v")
    
    def test_app_version_format(self):
        """Test APP_VERSION follows semver format."""
        from video_downloader import APP_VERSION
        import re
        
        # Should match v0.0.0 format
        pattern = r'^v\d+\.\d+\.\d+$'
        assert re.match(pattern, APP_VERSION), f"Version {APP_VERSION} should match semver format"


class TestDataClasses:
    """Test dataclass definitions."""
    
    def test_video_info_creation(self):
        """Test VideoInfo dataclass can be created."""
        from video_downloader import VideoInfo
        
        video = VideoInfo(
            title="Test Video",
            url="https://youtube.com/watch?v=test123",
            video_id="test123"
        )
        
        assert video.title == "Test Video"
        assert video.video_id == "test123"
        assert video.duration is None  # Optional field


class TestImports:
    """Test that all required modules can be imported."""
    
    def test_pyside6_available(self):
        """Test PySide6 is available."""
        try:
            from PySide6.QtWidgets import QApplication
            assert True
        except ImportError:
            pytest.skip("PySide6 not installed")
    
    def test_main_module_imports(self):
        """Test main module can be imported."""
        import video_downloader
        assert hasattr(video_downloader, 'APP_VERSION')
        assert hasattr(video_downloader, 'VideoDownloaderApp')

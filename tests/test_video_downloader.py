"""Tests for video_downloader module."""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestURLPatterns:
    """Test URL pattern matching."""
    
    def test_youtube_video_id_pattern(self):
        """Test YouTube video ID pattern."""
        from video_downloader import PATTERNS
        
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=abc123XYZ-_",
        ]
        
        for url in valid_urls:
            assert PATTERNS.YOUTUBE_VIDEO_ID.search(url), f"Should match: {url}"
    
    def test_youtube_playlist_pattern(self):
        """Test YouTube playlist URL pattern."""
        from video_downloader import PATTERNS
        
        valid_urls = [
            "https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxxx",
            "https://youtube.com/watch?v=xxx&list=PLtest123",
        ]
        
        for url in valid_urls:
            assert PATTERNS.YOUTUBE_PLAYLIST.search(url), f"Should match: {url}"
    
    def test_bilibili_video_pattern(self):
        """Test Bilibili video URL pattern."""
        from video_downloader import PATTERNS
        
        valid_urls = [
            "https://www.bilibili.com/video/BV1xx411c7mD",
            "https://bilibili.com/video/BV1234567890",
        ]
        
        for url in valid_urls:
            assert PATTERNS.BILIBILI_VIDEO.search(url), f"Should match: {url}"


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


class TestConstants:
    """Test constant definitions."""
    
    def test_constants_exists(self):
        """Test CONSTANTS is defined."""
        from video_downloader import CONSTANTS
        
        assert CONSTANTS is not None
        assert hasattr(CONSTANTS, 'VIDEO_EXTENSIONS')
        assert hasattr(CONSTANTS, 'QUALITY_OPTIONS')
    
    def test_quality_options(self):
        """Test quality options are defined."""
        from video_downloader import CONSTANTS
        
        assert 'best' in CONSTANTS.QUALITY_OPTIONS
        assert '1080p' in CONSTANTS.QUALITY_OPTIONS


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
        assert hasattr(video_downloader, 'MainWindow')
        assert hasattr(video_downloader, 'main')

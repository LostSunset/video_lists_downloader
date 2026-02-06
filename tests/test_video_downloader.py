"""Tests for video_downloader module."""

import os
import sys

import pytest

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
        import re

        from video_downloader import APP_VERSION

        # Should match v0.0.0 format
        pattern = r"^v\d+\.\d+\.\d+$"
        assert re.match(pattern, APP_VERSION), f"Version {APP_VERSION} should match semver format"


class TestConstants:
    """Test constant definitions."""

    def test_constants_exists(self):
        """Test CONSTANTS is defined."""
        from video_downloader import CONSTANTS

        assert CONSTANTS is not None
        assert hasattr(CONSTANTS, "VIDEO_EXTENSIONS")
        assert hasattr(CONSTANTS, "QUALITY_OPTIONS")

    def test_quality_options(self):
        """Test quality options are defined."""
        from video_downloader import CONSTANTS

        assert "best" in CONSTANTS.QUALITY_OPTIONS
        assert "1080p" in CONSTANTS.QUALITY_OPTIONS


class TestImports:
    """Test that all required modules can be imported."""

    def test_pyside6_available(self):
        """Test PySide6 is available."""
        try:
            from PySide6.QtWidgets import QApplication  # noqa: F401

            assert True
        except ImportError:
            pytest.skip("PySide6 not installed")

    def test_main_module_imports(self):
        """Test main module can be imported."""
        import video_downloader

        assert hasattr(video_downloader, "APP_VERSION")
        assert hasattr(video_downloader, "MainWindow")
        assert hasattr(video_downloader, "main")


# ==================== 新增測試 ====================


class TestPlatformUtils:
    """測試平台識別與工具函式"""

    def test_detect_platform_youtube(self):
        """測試各種 YouTube URL 格式的平台識別"""
        from video_downloader import PlatformUtils

        youtube_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/live/dQw4w9WgXcQ",
            "https://www.youtube.com/playlist?list=PLtest123",
            "https://YOUTUBE.COM/watch?v=test",
        ]
        for url in youtube_urls:
            assert PlatformUtils.detect_platform(url) == "youtube", f"應識別為 youtube: {url}"

    def test_detect_platform_bilibili(self):
        """測試各種 Bilibili URL 格式的平台識別"""
        from video_downloader import PlatformUtils

        bilibili_urls = [
            "https://www.bilibili.com/video/BV1xx411c7mD",
            "https://bilibili.com/video/av12345",
            "https://b23.tv/abcdef",
            "https://www.BILIBILI.COM/video/BV1234567890",
        ]
        for url in bilibili_urls:
            assert PlatformUtils.detect_platform(url) == "bilibili", f"應識別為 bilibili: {url}"

    def test_detect_platform_unknown(self):
        """測試未知 URL 的平台識別"""
        from video_downloader import PlatformUtils

        unknown_urls = [
            "https://www.google.com",
            "https://vimeo.com/12345",
            "https://twitter.com/user/status/123",
            "some random text",
            "",
        ]
        for url in unknown_urls:
            assert PlatformUtils.detect_platform(url) == "unknown", f"應識別為 unknown: {url}"

    def test_extract_video_id_youtube_watch(self):
        """測試 youtube.com/watch?v=xxx 格式的影片 ID 提取"""
        from video_downloader import PlatformUtils

        assert PlatformUtils.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        assert PlatformUtils.extract_video_id("https://youtube.com/watch?v=abc123XYZ-_") == "abc123XYZ-_"
        # 帶有額外參數
        assert PlatformUtils.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s") == "dQw4w9WgXcQ"

    def test_extract_video_id_youtube_short(self):
        """測試 youtu.be/xxx 短網址格式的影片 ID 提取"""
        from video_downloader import PlatformUtils

        assert PlatformUtils.extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        assert PlatformUtils.extract_video_id("https://youtu.be/abc123XYZ-_") == "abc123XYZ-_"

    def test_extract_video_id_youtube_shorts(self):
        """測試 youtube.com/shorts/xxx 格式的影片 ID 提取"""
        from video_downloader import PlatformUtils

        assert PlatformUtils.extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        assert PlatformUtils.extract_video_id("https://youtube.com/shorts/abc123XYZ-_") == "abc123XYZ-_"

    def test_extract_video_id_youtube_embed(self):
        """測試 youtube.com/embed/xxx 格式的影片 ID 提取"""
        from video_downloader import PlatformUtils

        assert PlatformUtils.extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_extract_video_id_youtube_live(self):
        """測試 youtube.com/live/xxx 格式的影片 ID 提取"""
        from video_downloader import PlatformUtils

        assert PlatformUtils.extract_video_id("https://www.youtube.com/live/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_extract_video_id_bilibili(self):
        """測試 bilibili.com/video/BVxxx 格式的影片 ID 提取"""
        from video_downloader import PlatformUtils

        result = PlatformUtils.extract_video_id("https://www.bilibili.com/video/BV1xx411c7mD")
        assert result.startswith("bili_")
        assert "BV1xx411c7mD" in result

        result_av = PlatformUtils.extract_video_id("https://www.bilibili.com/video/av12345678")
        assert result_av.startswith("bili_")
        assert "av12345678" in result_av

    def test_extract_playlist_id(self):
        """測試播放清單 ID 提取"""
        from video_downloader import PlatformUtils

        assert (
            PlatformUtils.extract_playlist_id("https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxxx")
            == "PLxxxxxxxxxxxxxxxx"
        )
        assert PlatformUtils.extract_playlist_id("https://youtube.com/watch?v=xxx&list=PLtest123") == "PLtest123"
        # 無播放清單 ID 時回傳原始 URL（已 strip）
        assert PlatformUtils.extract_playlist_id("https://www.youtube.com/watch?v=test") == (
            "https://www.youtube.com/watch?v=test"
        )


class TestDownloadStats:
    """測試下載統計資料類別"""

    def test_default_values(self):
        """測試預設值是否正確"""
        from video_downloader import DownloadStats

        stats = DownloadStats()
        assert stats.total_downloads == 0
        assert stats.successful_downloads == 0
        assert stats.failed_downloads == 0
        assert stats.skipped_downloads == 0
        assert stats.total_bytes_downloaded == 0
        assert stats.total_time_seconds == 0

    def test_to_dict(self):
        """測試序列化為字典"""
        from video_downloader import DownloadStats

        stats = DownloadStats(
            total_downloads=10,
            successful_downloads=8,
            failed_downloads=1,
            skipped_downloads=1,
            total_bytes_downloaded=1024000,
            total_time_seconds=3600,
        )
        result = stats.to_dict()
        assert result["total_downloads"] == 10
        assert result["successful_downloads"] == 8
        assert result["failed_downloads"] == 1
        assert result["skipped_downloads"] == 1
        assert result["total_bytes_downloaded"] == 1024000
        assert result["total_time_seconds"] == 3600

    def test_from_dict(self):
        """測試從字典反序列化"""
        from video_downloader import DownloadStats

        data = {
            "total_downloads": 5,
            "successful_downloads": 4,
            "failed_downloads": 1,
            "skipped_downloads": 0,
            "total_bytes_downloaded": 500000,
            "total_time_seconds": 120,
        }
        stats = DownloadStats.from_dict(data)
        assert stats.total_downloads == 5
        assert stats.successful_downloads == 4
        assert stats.failed_downloads == 1
        assert stats.skipped_downloads == 0
        assert stats.total_bytes_downloaded == 500000
        assert stats.total_time_seconds == 120

    def test_from_dict_with_missing_keys(self):
        """測試部分資料反序列化時使用預設值"""
        from video_downloader import DownloadStats

        # 空字典
        stats = DownloadStats.from_dict({})
        assert stats.total_downloads == 0
        assert stats.successful_downloads == 0
        assert stats.total_bytes_downloaded == 0

        # 只有部分欄位
        stats_partial = DownloadStats.from_dict({"total_downloads": 3, "failed_downloads": 2})
        assert stats_partial.total_downloads == 3
        assert stats_partial.failed_downloads == 2
        assert stats_partial.successful_downloads == 0
        assert stats_partial.skipped_downloads == 0

    def test_format_bytes(self):
        """測試各種大小格式化（B, KB, MB, GB）"""
        from video_downloader import DownloadStats

        stats = DownloadStats()

        # Bytes
        assert "B" in stats.format_bytes(500)
        assert "500.00 B" == stats.format_bytes(500)

        # KB
        result_kb = stats.format_bytes(1024)
        assert "KB" in result_kb
        assert "1.00 KB" == result_kb

        # MB
        result_mb = stats.format_bytes(1024 * 1024)
        assert "MB" in result_mb
        assert "1.00 MB" == result_mb

        # GB
        result_gb = stats.format_bytes(1024 * 1024 * 1024)
        assert "GB" in result_gb
        assert "1.00 GB" == result_gb

        # TB
        result_tb = stats.format_bytes(1024 * 1024 * 1024 * 1024)
        assert "TB" in result_tb
        assert "1.00 TB" == result_tb

        # 零
        assert "0.00 B" == stats.format_bytes(0)

    def test_get_summary(self):
        """測試統計摘要輸出"""
        from video_downloader import DownloadStats

        stats = DownloadStats(
            total_downloads=10,
            successful_downloads=8,
            failed_downloads=1,
            skipped_downloads=1,
            total_bytes_downloaded=1024 * 1024 * 100,  # 100 MB
            total_time_seconds=3661,  # 1小時1分1秒
        )
        summary = stats.get_summary()
        assert "總下載數: 10" in summary
        assert "成功: 8" in summary
        assert "80.0%" in summary
        assert "失敗: 1" in summary
        assert "跳過: 1" in summary
        assert "1時1分" in summary

    def test_get_summary_zero_downloads(self):
        """測試零下載時的摘要輸出（避免除以零）"""
        from video_downloader import DownloadStats

        stats = DownloadStats()
        summary = stats.get_summary()
        assert "總下載數: 0" in summary
        assert "0.0%" in summary


class TestCompiledPatterns:
    """測試預編譯正規表達式模式"""

    def test_progress_percent_pattern(self):
        """測試進度百分比解析"""
        from video_downloader import PATTERNS

        # 典型 yt-dlp 輸出行
        line = "[download]  45.2% of 100.00MiB at 5.00MiB/s ETA 00:11"
        match = PATTERNS.PROGRESS_PERCENT.search(line)
        assert match is not None
        assert match.group(1) == "45.2"

        # 100%
        line_100 = "[download] 100.0% of 100.00MiB"
        match_100 = PATTERNS.PROGRESS_PERCENT.search(line_100)
        assert match_100 is not None
        assert match_100.group(1) == "100.0"

        # 無百分比的行
        line_no = "[info] Downloading video #1"
        assert PATTERNS.PROGRESS_PERCENT.search(line_no) is None

    def test_progress_speed_pattern(self):
        """測試速度解析"""
        from video_downloader import PATTERNS

        line = "[download]  45.2% of 100.00MiB at 5.00MiB/s ETA 00:11"
        match = PATTERNS.PROGRESS_SPEED.search(line)
        assert match is not None
        assert "5.00MiB/s" in match.group(1)

        # KiB/s 速度
        line_kb = "[download]  10.0% of 50.00MiB at 512.00KiB/s ETA 01:30"
        match_kb = PATTERNS.PROGRESS_SPEED.search(line_kb)
        assert match_kb is not None

    def test_progress_eta_pattern(self):
        """測試 ETA 解析"""
        from video_downloader import PATTERNS

        line = "[download]  45.2% of 100.00MiB at 5.00MiB/s ETA 00:11"
        match = PATTERNS.PROGRESS_ETA.search(line)
        assert match is not None
        assert match.group(1) == "00:11"

        # 較長的 ETA
        line_long = "[download]  5.0% of 1.00GiB at 1.00MiB/s ETA 17:05"
        match_long = PATTERNS.PROGRESS_ETA.search(line_long)
        assert match_long is not None
        assert match_long.group(1) == "17:05"

    def test_file_size_pattern(self):
        """測試檔案大小解析"""
        from video_downloader import PATTERNS

        # MiB
        match_mb = PATTERNS.FILE_SIZE.search("100.50MiB")
        assert match_mb is not None
        assert match_mb.group(1) == "100.50"
        assert match_mb.group(2).lower() == "m"

        # GiB
        match_gb = PATTERNS.FILE_SIZE.search("1.50GiB")
        assert match_gb is not None
        assert match_gb.group(1) == "1.50"
        assert match_gb.group(2).lower() == "g"

        # KiB
        match_kb = PATTERNS.FILE_SIZE.search("512.00KiB")
        assert match_kb is not None
        assert match_kb.group(1) == "512.00"
        assert match_kb.group(2).lower() == "k"

        # 大寫 MB
        match_upper = PATTERNS.FILE_SIZE.search("100MB")
        assert match_upper is not None

    def test_bracket_id_pattern(self):
        """測試方括號 ID 解析"""
        from video_downloader import PATTERNS

        # 典型的影片檔名格式
        filename = "Some Video Title [dQw4w9WgXcQ].mp4"
        match = PATTERNS.BRACKET_ID.search(filename)
        assert match is not None
        assert match.group(1) == "dQw4w9WgXcQ"

        # 較長的 ID
        filename_long = "Video [abcdefghijklmnop].mp4"
        match_long = PATTERNS.BRACKET_ID.search(filename_long)
        assert match_long is not None
        assert match_long.group(1) == "abcdefghijklmnop"

        # 太短的 ID 不應匹配
        filename_short = "Video [abc].mp4"
        match_short = PATTERNS.BRACKET_ID.search(filename_short)
        assert match_short is None

    def test_download_speed_pattern(self):
        """測試下載速度正規表達式"""
        from video_downloader import PATTERNS

        line = "5.00 MiB/s"
        match = PATTERNS.DOWNLOAD_SPEED.search(line)
        assert match is not None
        assert match.group(1) == "5.00"

    def test_bilibili_bv_pattern(self):
        """測試 Bilibili BV 號正規表達式"""
        from video_downloader import PATTERNS

        url = "https://www.bilibili.com/video/BV1xx411c7mD"
        match = PATTERNS.BILIBILI_BV.search(url)
        assert match is not None
        assert match.group(1) == "BV1xx411c7mD"

    def test_bilibili_av_pattern(self):
        """測試 Bilibili AV 號正規表達式"""
        from video_downloader import PATTERNS

        url = "https://www.bilibili.com/video/av12345678"
        match = PATTERNS.BILIBILI_AV.search(url)
        assert match is not None
        assert match.group(1) == "av12345678"


class TestDownloadWorkerBuildCommand:
    """測試 DownloadWorker 的命令建構"""

    def test_basic_command(self):
        """測試基本命令建構"""
        from video_downloader import DownloadWorker

        worker = DownloadWorker(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            output_dir="/tmp/downloads",
        )
        cmd = worker._build_command("youtube")

        assert cmd[0] == "yt-dlp"
        assert "-o" in cmd
        assert "--no-playlist" in cmd
        assert "--progress" in cmd
        assert "--newline" in cmd
        assert cmd[-1] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        # 預設格式
        assert "-f" in cmd
        f_index = cmd.index("-f")
        assert "best" in cmd[f_index + 1]

    def test_command_with_cookies(self, tmp_path):
        """測試帶 cookie 的命令"""
        from video_downloader import DownloadWorker

        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text("# Netscape HTTP Cookie File\n.youtube.com\tTRUE\t/\tFALSE\t0\tSID\tvalue\n")

        worker = DownloadWorker(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            output_dir="/tmp/downloads",
            cookie_file=str(cookie_file),
        )
        cmd = worker._build_command("youtube")

        assert "--cookies" in cmd
        cookie_index = cmd.index("--cookies")
        assert cmd[cookie_index + 1] == str(cookie_file)

    def test_command_without_existing_cookie_file(self):
        """測試 cookie 檔案不存在時不加入 --cookies 參數"""
        from video_downloader import DownloadWorker

        worker = DownloadWorker(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            output_dir="/tmp/downloads",
            cookie_file="/nonexistent/cookies.txt",
        )
        cmd = worker._build_command("youtube")

        assert "--cookies" not in cmd

    def test_command_with_rate_limit(self):
        """測試帶速度限制的命令"""
        from video_downloader import DownloadWorker

        worker = DownloadWorker(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            output_dir="/tmp/downloads",
            rate_limit="5M",
        )
        cmd = worker._build_command("youtube")

        assert "--limit-rate" in cmd
        rate_index = cmd.index("--limit-rate")
        assert cmd[rate_index + 1] == "5M"

    def test_command_with_subtitles(self):
        """測試帶字幕的命令"""
        from video_downloader import DownloadWorker

        worker = DownloadWorker(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            output_dir="/tmp/downloads",
            include_subs=True,
            sub_langs="zh-TW,en",
        )
        cmd = worker._build_command("youtube")

        assert "--write-subs" in cmd
        assert "--write-auto-subs" in cmd
        assert "--sub-langs" in cmd
        lang_index = cmd.index("--sub-langs")
        assert cmd[lang_index + 1] == "zh-TW,en"
        assert "--embed-subs" in cmd
        assert "--convert-subs" in cmd

    def test_command_bilibili_platform(self):
        """測試 Bilibili 平台特定參數"""
        from video_downloader import DownloadWorker

        worker = DownloadWorker(
            url="https://www.bilibili.com/video/BV1xx411c7mD",
            output_dir="/tmp/downloads",
        )
        cmd = worker._build_command("bilibili")

        assert "--referer" in cmd
        referer_index = cmd.index("--referer")
        assert cmd[referer_index + 1] == "https://www.bilibili.com"
        assert "--add-header" in cmd

    def test_command_with_format_id(self):
        """測試指定格式 ID 的命令"""
        from video_downloader import DownloadWorker

        worker = DownloadWorker(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            output_dir="/tmp/downloads",
            format_id="137+140",
        )
        cmd = worker._build_command("youtube")

        f_index = cmd.index("-f")
        assert cmd[f_index + 1] == "137+140"

    def test_worker_default_attributes(self):
        """測試 DownloadWorker 預設屬性"""
        from video_downloader import CONSTANTS, DownloadWorker

        worker = DownloadWorker(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            output_dir="/tmp/downloads",
        )
        assert worker.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert worker.output_dir == "/tmp/downloads"
        assert worker.max_retries == CONSTANTS.DEFAULT_RETRY_COUNT
        assert worker.rate_limit is None
        assert worker.include_subs is False
        assert worker._is_cancelled is False

    def test_worker_custom_video_id(self):
        """測試自訂影片 ID"""
        from video_downloader import DownloadWorker

        worker = DownloadWorker(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            output_dir="/tmp/downloads",
            video_id="custom_id",
        )
        assert worker.video_id == "custom_id"

    def test_worker_auto_video_id(self):
        """測試自動提取影片 ID"""
        from video_downloader import DownloadWorker

        worker = DownloadWorker(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            output_dir="/tmp/downloads",
        )
        assert worker.video_id == "dQw4w9WgXcQ"


class TestBatchDownloadWorkerBuildCommand:
    """測試 BatchDownloadWorker 的命令建構"""

    def test_basic_ytdlp_command(self):
        """測試基本命令"""
        from video_downloader import BatchDownloadWorker

        settings = {"download_path": "/tmp/downloads", "quality": "best"}
        worker = BatchDownloadWorker(task_id=1, urls=["https://www.youtube.com/watch?v=test"], settings=settings)
        cmd = worker._build_ytdlp_command("https://www.youtube.com/watch?v=test", "youtube")

        assert cmd[0] == "yt-dlp"
        assert cmd[-1] == "https://www.youtube.com/watch?v=test"
        assert "--no-warnings" in cmd
        assert "--ignore-errors" in cmd
        assert "--retries" in cmd

    def test_command_with_quality_best(self):
        """測試 best 畫質設定"""
        from video_downloader import BatchDownloadWorker

        settings = {"download_path": "/tmp/downloads", "quality": "best"}
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)
        cmd = worker._build_ytdlp_command("https://www.youtube.com/watch?v=test", "youtube")

        f_index = cmd.index("-f")
        assert cmd[f_index + 1] == "bestvideo+bestaudio/best"

    def test_command_with_quality_1080p(self):
        """測試 1080p 畫質設定"""
        from video_downloader import BatchDownloadWorker

        settings = {"download_path": "/tmp/downloads", "quality": "1080p"}
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)
        cmd = worker._build_ytdlp_command("https://www.youtube.com/watch?v=test", "youtube")

        f_index = cmd.index("-f")
        format_str = cmd[f_index + 1]
        assert "1080" in format_str
        assert "bestvideo" in format_str

    def test_command_with_quality_worst(self):
        """測試 worst 畫質設定"""
        from video_downloader import BatchDownloadWorker

        settings = {"download_path": "/tmp/downloads", "quality": "worst"}
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)
        cmd = worker._build_ytdlp_command("https://www.youtube.com/watch?v=test", "youtube")

        f_index = cmd.index("-f")
        assert "worst" in cmd[f_index + 1]

    def test_command_with_subtitles(self):
        """測試字幕設定"""
        from video_downloader import BatchDownloadWorker

        settings = {
            "download_path": "/tmp/downloads",
            "quality": "best",
            "download_subtitle": True,
            "auto_subtitle": True,
            "subtitle_lang": "zh-TW,en",
        }
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)
        cmd = worker._build_ytdlp_command("https://www.youtube.com/watch?v=test", "youtube")

        assert "--write-subs" in cmd
        assert "--write-auto-subs" in cmd
        assert "--sub-langs" in cmd
        lang_index = cmd.index("--sub-langs")
        assert cmd[lang_index + 1] == "zh-TW,en"
        assert "--embed-subs" in cmd

    def test_command_with_subtitles_only(self):
        """測試僅下載字幕模式"""
        from video_downloader import BatchDownloadWorker

        settings = {
            "download_path": "/tmp/downloads",
            "quality": "best",
            "download_subtitle": True,
            "subtitle_only": True,
            "subtitle_lang": "zh-TW",
        }
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)
        cmd = worker._build_ytdlp_command("https://www.youtube.com/watch?v=test", "youtube")

        assert "--write-subs" in cmd
        assert "--skip-download" in cmd
        # subtitle_only 模式下不應嵌入字幕
        assert "--embed-subs" not in cmd

    def test_command_bilibili_headers(self):
        """測試 Bilibili headers 設定"""
        from video_downloader import BatchDownloadWorker

        settings = {"download_path": "/tmp/downloads", "quality": "best"}
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)
        cmd = worker._build_ytdlp_command("https://www.bilibili.com/video/BV1xx411c7mD", "bilibili")

        assert "--referer" in cmd
        referer_index = cmd.index("--referer")
        assert cmd[referer_index + 1] == "https://www.bilibili.com"
        assert "--user-agent" in cmd

    def test_command_with_cookies(self, tmp_path):
        """測試帶 cookie 的命令"""
        from video_downloader import BatchDownloadWorker

        cookie_file = tmp_path / "youtube_cookies.txt"
        cookie_file.write_text("# Netscape HTTP Cookie File\n")

        settings = {
            "download_path": "/tmp/downloads",
            "quality": "best",
            "use_cookies": True,
            "youtube_cookie_file": str(cookie_file),
        }
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)
        cmd = worker._build_ytdlp_command("https://www.youtube.com/watch?v=test", "youtube")

        assert "--cookies" in cmd
        cookie_index = cmd.index("--cookies")
        assert cmd[cookie_index + 1] == str(cookie_file)

    def test_command_with_output_template(self):
        """測試輸出模板設定"""
        from video_downloader import BatchDownloadWorker

        settings = {
            "download_path": "/tmp/downloads",
            "quality": "best",
        }
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)
        cmd = worker._build_ytdlp_command("https://www.youtube.com/watch?v=test", "youtube")

        assert "-o" in cmd
        o_index = cmd.index("-o")
        template = cmd[o_index + 1]
        assert "/tmp/downloads" in template.replace("\\", "/")
        assert "%(ext)s" in template

    def test_command_with_custom_filename_template(self):
        """測試自訂檔名模板"""
        from video_downloader import BatchDownloadWorker

        settings = {
            "download_path": "/tmp/downloads",
            "quality": "best",
            "use_custom_filename": True,
            "custom_filename_template": "%(title)s",
        }
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)
        cmd = worker._build_ytdlp_command("https://www.youtube.com/watch?v=test", "youtube")

        o_index = cmd.index("-o")
        template = cmd[o_index + 1]
        assert "%(title)s" in template
        # 應自動附加 %(ext)s
        assert "%(ext)s" in template

    def test_command_with_quality_as_custom_format(self):
        """測試自訂格式字串"""
        from video_downloader import BatchDownloadWorker

        settings = {
            "download_path": "/tmp/downloads",
            "quality": "137+140",
        }
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)
        cmd = worker._build_ytdlp_command("https://www.youtube.com/watch?v=test", "youtube")

        f_index = cmd.index("-f")
        assert cmd[f_index + 1] == "137+140"

    def test_command_with_trim_filename(self):
        """測試檔名裁切設定"""
        from video_downloader import BatchDownloadWorker

        settings = {
            "download_path": "/tmp/downloads",
            "quality": "best",
            "auto_trim_filename": True,
            "trim_filename_length": 80,
        }
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)
        cmd = worker._build_ytdlp_command("https://www.youtube.com/watch?v=test", "youtube")

        assert "--trim-filenames" in cmd
        trim_index = cmd.index("--trim-filenames")
        assert cmd[trim_index + 1] == "80"

    def test_batch_worker_default_stats(self):
        """測試 BatchDownloadWorker 預設統計"""
        from video_downloader import BatchDownloadWorker

        settings = {"download_path": "/tmp/downloads"}
        worker = BatchDownloadWorker(task_id=1, urls=["url1", "url2"], settings=settings)

        assert worker.stats == {"success": 0, "failed": 0, "skipped": 0}
        assert worker.task_id == 1
        assert len(worker.urls) == 2
        assert worker._is_running is True
        assert worker._is_paused is False


class TestMainWindowHelpers:
    """測試 MainWindow 的靜態輔助方法（使用 mock 避免需要 GUI）"""

    def test_normalize_path(self):
        """測試路徑標準化"""
        from video_downloader import MainWindow

        # 基本路徑標準化
        result = MainWindow.normalize_path("/tmp/downloads")
        assert result != ""
        assert os.path.isabs(result)

        # 路徑中有多餘的分隔符
        result_extra = MainWindow.normalize_path("/tmp//downloads///test")
        assert "//" not in result_extra.replace("\\\\", "")  # Windows 可能有 UNC path

        # 路徑中有 .. 應被解析
        result_dotdot = MainWindow.normalize_path("/tmp/downloads/../other")
        assert ".." not in result_dotdot

    def test_normalize_path_empty(self):
        """測試空路徑標準化"""
        from video_downloader import MainWindow

        assert MainWindow.normalize_path("") == ""
        assert MainWindow.normalize_path(None) == ""

    def test_normalize_path_consistency(self):
        """測試路徑標準化的一致性"""
        from video_downloader import MainWindow

        # 相同路徑的不同寫法應得到相同結果
        path1 = MainWindow.normalize_path("/tmp/downloads")
        path2 = MainWindow.normalize_path("/tmp/downloads/")
        path3 = MainWindow.normalize_path("/tmp/./downloads")
        assert path1 == path2
        assert path1 == path3


class TestStatusColors:
    """測試狀態顏色定義"""

    def test_status_colors_defined(self):
        """測試所有狀態顏色已定義"""
        from video_downloader import STATUS_COLORS

        assert STATUS_COLORS.SUCCESS == "#4CAF50"
        assert STATUS_COLORS.FAILED == "#F44336"
        assert STATUS_COLORS.SKIPPED == "#FFC107"
        assert STATUS_COLORS.PENDING == "#9E9E9E"
        assert STATUS_COLORS.RUNNING == "#2196F3"
        assert STATUS_COLORS.VALID == "#4CAF50"
        assert STATUS_COLORS.INVALID == "#F44336"
        assert STATUS_COLORS.UNKNOWN == "#FFC107"


class TestAppConstants:
    """測試應用程式常數"""

    def test_video_extensions(self):
        """測試影片副檔名列表"""
        from video_downloader import CONSTANTS

        assert ".mp4" in CONSTANTS.VIDEO_EXTENSIONS
        assert ".webm" in CONSTANTS.VIDEO_EXTENSIONS
        assert ".mkv" in CONSTANTS.VIDEO_EXTENSIONS

    def test_ignore_suffixes(self):
        """測試忽略的暫存檔副檔名"""
        from video_downloader import CONSTANTS

        assert ".part" in CONSTANTS.IGNORE_SUFFIXES
        assert ".ytdl" in CONSTANTS.IGNORE_SUFFIXES
        assert ".temp" in CONSTANTS.IGNORE_SUFFIXES

    def test_quality_caps(self):
        """測試畫質上限對照表"""
        from video_downloader import CONSTANTS

        assert CONSTANTS.QUALITY_CAPS["1080p"] == 1080
        assert CONSTANTS.QUALITY_CAPS["720p"] == 720
        assert CONSTANTS.QUALITY_CAPS["4320p"] == 4320
        assert CONSTANTS.QUALITY_CAPS["240p"] == 240

    def test_default_values(self):
        """測試預設常數值"""
        from video_downloader import CONSTANTS

        assert CONSTANTS.DEFAULT_TIMEOUT == 10800
        assert CONSTANTS.DEFAULT_RETRY_COUNT == 3
        assert CONSTANTS.DEFAULT_RATE_LIMIT == "0"
        assert CONSTANTS.RETRY_DELAY == 2
        assert CONSTANTS.COOKIE_UPDATE_INTERVAL == 600

    def test_youtube_key_cookies(self):
        """測試 YouTube 關鍵 Cookie 名稱"""
        from video_downloader import CONSTANTS

        assert "SAPISID" in CONSTANTS.YOUTUBE_KEY_COOKIES
        assert "HSID" in CONSTANTS.YOUTUBE_KEY_COOKIES

    def test_bilibili_key_cookies(self):
        """測試 Bilibili 關鍵 Cookie 名稱"""
        from video_downloader import CONSTANTS

        assert "SESSDATA" in CONSTANTS.BILIBILI_KEY_COOKIES
        assert "bili_jct" in CONSTANTS.BILIBILI_KEY_COOKIES
        assert "DedeUserID" in CONSTANTS.BILIBILI_KEY_COOKIES

    def test_height_priority(self):
        """測試畫質高度優先順序"""
        from video_downloader import CONSTANTS

        assert CONSTANTS.HEIGHT_PRIORITY == [4320, 2160, 1440, 1080, 720, 480, 360, 240]
        # 確認是由高到低排序
        for i in range(len(CONSTANTS.HEIGHT_PRIORITY) - 1):
            assert CONSTANTS.HEIGHT_PRIORITY[i] > CONSTANTS.HEIGHT_PRIORITY[i + 1]


class TestDownloadStatsRoundTrip:
    """測試 DownloadStats 序列化往返"""

    def test_round_trip(self):
        """測試 to_dict -> from_dict 往返一致性"""
        from video_downloader import DownloadStats

        original = DownloadStats(
            total_downloads=42,
            successful_downloads=38,
            failed_downloads=3,
            skipped_downloads=1,
            total_bytes_downloaded=9999999,
            total_time_seconds=7200,
        )
        restored = DownloadStats.from_dict(original.to_dict())

        assert restored.total_downloads == original.total_downloads
        assert restored.successful_downloads == original.successful_downloads
        assert restored.failed_downloads == original.failed_downloads
        assert restored.skipped_downloads == original.skipped_downloads
        assert restored.total_bytes_downloaded == original.total_bytes_downloaded
        assert restored.total_time_seconds == original.total_time_seconds


class TestBatchDownloadWorkerParseProgress:
    """測試 BatchDownloadWorker 的進度解析方法"""

    def test_parse_progress_with_percent(self):
        """測試解析包含百分比的進度行"""
        from video_downloader import BatchDownloadWorker

        settings = {"download_path": "/tmp"}
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)

        line = "[download]  45.2% of 100.00MiB at 5.00MiB/s ETA 00:11"
        result = worker._parse_progress(line)
        assert result != ""
        assert "45.2%" in result

    def test_parse_progress_no_percent(self):
        """測試解析不含百分比的行"""
        from video_downloader import BatchDownloadWorker

        settings = {"download_path": "/tmp"}
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)

        line = "[download] Destination: video.mp4"
        result = worker._parse_progress(line)
        assert result == ""

    def test_parse_progress_complete(self):
        """測試解析完成進度行"""
        from video_downloader import BatchDownloadWorker

        settings = {"download_path": "/tmp"}
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)

        line = "[download] 100.0% of 50.00MiB at 10.00MiB/s ETA 00:00"
        result = worker._parse_progress(line)
        assert "100.0%" in result


class TestDownloadWorkerCancel:
    """測試 DownloadWorker 取消功能"""

    def test_cancel_sets_flag(self):
        """測試取消操作設定旗標"""
        from video_downloader import DownloadWorker

        worker = DownloadWorker(
            url="https://www.youtube.com/watch?v=test",
            output_dir="/tmp",
        )
        assert worker._is_cancelled is False
        worker.cancel()
        assert worker._is_cancelled is True


class TestBatchDownloadWorkerControl:
    """測試 BatchDownloadWorker 控制方法"""

    def test_stop(self):
        """測試停止功能"""
        from video_downloader import BatchDownloadWorker

        settings = {"download_path": "/tmp"}
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)
        assert worker._is_running is True
        worker.stop()
        assert worker._is_running is False

    def test_pause_resume(self):
        """測試暫停與恢復功能"""
        from video_downloader import BatchDownloadWorker

        settings = {"download_path": "/tmp"}
        worker = BatchDownloadWorker(task_id=1, urls=[], settings=settings)
        assert worker._is_paused is False
        worker.pause()
        assert worker._is_paused is True
        worker.resume()
        assert worker._is_paused is False


class TestCookieManager:
    """測試 CookieManager 基本功能"""

    def test_init(self):
        """測試 CookieManager 初始化"""
        from video_downloader import CONSTANTS, CookieManager

        manager = CookieManager(parent_widget=None)
        assert manager.parent is None
        assert manager.last_update == 0
        assert manager.update_interval == CONSTANTS.COOKIE_UPDATE_INTERVAL

    def test_validate_youtube_cookies_missing_file(self):
        """測試 YouTube cookie 檔案不存在"""
        from video_downloader import CookieManager

        manager = CookieManager()
        success, msg = manager.validate_youtube_cookies("/nonexistent/cookies.txt")
        assert success is False
        assert "不存在" in msg

    def test_validate_bilibili_cookies_missing_file(self):
        """測試 Bilibili cookie 檔案不存在"""
        from video_downloader import CookieManager

        manager = CookieManager()
        success, result = manager.validate_bilibili_cookies("/nonexistent/cookies.txt")
        assert success is False
        assert "不存在" in result["error"]

    def test_validate_bilibili_cookies_valid_format(self, tmp_path):
        """測試 Bilibili cookie 檔案格式驗證"""
        from video_downloader import CookieManager

        cookie_file = tmp_path / "bilibili_cookies.txt"
        cookie_content = (
            "# Netscape HTTP Cookie File\n"
            ".bilibili.com\tTRUE\t/\tFALSE\t0\tSESSDATA\ttest_sessdata\n"
            ".bilibili.com\tTRUE\t/\tFALSE\t0\tbili_jct\ttest_bili_jct\n"
            ".bilibili.com\tTRUE\t/\tFALSE\t0\tDedeUserID\ttest_user_id\n"
        )
        cookie_file.write_text(cookie_content)

        manager = CookieManager()
        success, result = manager.validate_bilibili_cookies(str(cookie_file))
        assert success is True
        assert "正確" in result["message"]

    def test_validate_bilibili_cookies_missing_keys(self, tmp_path):
        """測試 Bilibili cookie 缺少關鍵欄位"""
        from video_downloader import CookieManager

        cookie_file = tmp_path / "bilibili_cookies.txt"
        cookie_content = "# Netscape HTTP Cookie File\n.bilibili.com\tTRUE\t/\tFALSE\t0\tSESSDATA\ttest_sessdata\n"
        cookie_file.write_text(cookie_content)

        manager = CookieManager()
        success, result = manager.validate_bilibili_cookies(str(cookie_file))
        assert success is False
        assert "缺少" in result["error"]

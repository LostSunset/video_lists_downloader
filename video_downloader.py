#!/usr/bin/env python3
"""
影片批量下載工具 (PySide6 版本)
支援 YouTube 與 Bilibili 平台
"""

from __future__ import annotations

import datetime
import glob
import json
import os
import re
import subprocess
import sys
import threading
import time
import traceback
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Any

from PySide6.QtCore import QObject, QSettings, QSize, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

import bin_manager

APP_VERSION = "v0.7.5"


# ==================== 狀態顏色定義 ====================
@dataclass
class StatusColors:
    """狀態顏色常數"""

    SUCCESS: str = "#4CAF50"  # 綠色 - 成功
    FAILED: str = "#F44336"  # 紅色 - 失敗
    SKIPPED: str = "#FFC107"  # 黃色 - 跳過
    PENDING: str = "#9E9E9E"  # 灰色 - 等待中
    RUNNING: str = "#2196F3"  # 藍色 - 進行中
    VALID: str = "#4CAF50"  # 綠色 - 有效
    INVALID: str = "#F44336"  # 紅色 - 無效
    UNKNOWN: str = "#FFC107"  # 黃色 - 未驗證


STATUS_COLORS = StatusColors()


# ==================== 常數定義 ====================
@dataclass
class AppConstants:
    """應用程式常數"""

    YOUTUBE_KEY_COOKIES: list[str] = field(default_factory=lambda: ["SAPISID", "HSID", "SSID", "APISID"])
    BILIBILI_KEY_COOKIES: list[str] = field(default_factory=lambda: ["SESSDATA", "bili_jct", "DedeUserID"])
    VIDEO_EXTENSIONS: tuple[str, ...] = (".mp4", ".webm", ".mkv", ".flv", ".avi", ".mov", ".m4a")
    IGNORE_SUFFIXES: tuple[str, ...] = (".part", ".ytdl", ".temp", ".aria2")
    QUALITY_OPTIONS: list[str] = field(
        default_factory=lambda: ["best", "4320p", "2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "worst"]
    )
    QUALITY_CAPS: dict[str, int] = field(
        default_factory=lambda: {
            "4320p": 4320,
            "2160p": 2160,
            "1440p": 1440,
            "1080p": 1080,
            "720p": 720,
            "480p": 480,
            "360p": 360,
            "240p": 240,
        }
    )
    HEIGHT_PRIORITY: list[int] = field(default_factory=lambda: [4320, 2160, 1440, 1080, 720, 480, 360, 240])
    DEFAULT_TIMEOUT: int = 10800
    DEFAULT_RETRY_COUNT: int = 3
    DEFAULT_RATE_LIMIT: str = "0"
    RETRY_DELAY: int = 2
    COOKIE_UPDATE_INTERVAL: int = 600


CONSTANTS = AppConstants()


# ==================== 預編譯正規表達式 ====================
class CompiledPatterns:
    """預編譯的正規表達式模式"""

    YOUTUBE_VIDEO_ID = re.compile(r"[?&]v=([A-Za-z0-9_-]{6,})")
    YOUTUBE_SHORT_URL = re.compile(r"youtu\.be/([A-Za-z0-9_-]{6,})")
    YOUTUBE_SHORTS = re.compile(r"/shorts/([A-Za-z0-9_-]{6,})")
    YOUTUBE_EMBED = re.compile(r"/embed/([A-Za-z0-9_-]{6,})")
    YOUTUBE_LIVE = re.compile(r"/live/([A-Za-z0-9_-]{6,})")
    YOUTUBE_PLAYLIST = re.compile(r"[?&]list=([A-Za-z0-9_-]+)")
    BILIBILI_BV = re.compile(r"/video/(BV[0-9A-Za-z]{10})")
    BILIBILI_AV = re.compile(r"/video/(av\d+)")
    BILIBILI_VIDEO = re.compile(r"bilibili\.com/video/(\w+)")
    PROGRESS_PERCENT = re.compile(r"(\d+\.\d+)%")
    PROGRESS_SIZE = re.compile(r"of\s+([\d.]+\s*[KMGT]?i?B)")
    PROGRESS_SPEED = re.compile(r"at\s+([\d.]+\s*[KMGT]?i?B/s)")
    PROGRESS_ETA = re.compile(r"ETA\s+(\d+:\d+)")
    DOWNLOAD_SPEED = re.compile(r"(\d+\.?\d*)\s*([KMGT]?i?B)/s")
    DOWNLOAD_ETA = re.compile(r"ETA\s*(\d+:\d+)")
    FILE_SIZE = re.compile(r"([\d.]+)(k|m|g|t)i?b", re.IGNORECASE)
    BRACKET_ID = re.compile(r"\[([A-Za-z0-9_-]{8,})\]")


PATTERNS = CompiledPatterns()


# ==================== 下載統計 ====================
@dataclass
class DownloadStats:
    """下載統計資料"""

    total_downloads: int = 0
    successful_downloads: int = 0
    failed_downloads: int = 0
    skipped_downloads: int = 0
    total_bytes_downloaded: int = 0
    total_time_seconds: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_downloads": self.total_downloads,
            "successful_downloads": self.successful_downloads,
            "failed_downloads": self.failed_downloads,
            "skipped_downloads": self.skipped_downloads,
            "total_bytes_downloaded": self.total_bytes_downloaded,
            "total_time_seconds": self.total_time_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DownloadStats:
        return cls(
            total_downloads=data.get("total_downloads", 0),
            successful_downloads=data.get("successful_downloads", 0),
            failed_downloads=data.get("failed_downloads", 0),
            skipped_downloads=data.get("skipped_downloads", 0),
            total_bytes_downloaded=data.get("total_bytes_downloaded", 0),
            total_time_seconds=data.get("total_time_seconds", 0),
        )

    def format_bytes(self, bytes_count: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_count < 1024:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024
        return f"{bytes_count:.2f} PB"

    def get_summary(self) -> str:
        success_rate = (self.successful_downloads / self.total_downloads * 100) if self.total_downloads > 0 else 0
        hours = self.total_time_seconds // 3600
        minutes = (self.total_time_seconds % 3600) // 60
        return (
            f" 下載統計\n"
            f"總下載數: {self.total_downloads}\n"
            f"成功: {self.successful_downloads} ({success_rate:.1f}%)\n"
            f"失敗: {self.failed_downloads}\n"
            f"跳過: {self.skipped_downloads}\n"
            f"總下載量: {self.format_bytes(self.total_bytes_downloaded)}\n"
            f"總耗時: {hours}時{minutes}分"
        )


# ==================== 平台識別與工具函式 ====================
class PlatformUtils:
    """平台相關工具函式"""

    @staticmethod
    def detect_platform(url: str) -> str:
        """自動識別網址平台類型"""
        url_lower = url.lower()
        if any(x in url_lower for x in ["youtube.com", "youtu.be"]):
            return "youtube"
        elif any(x in url_lower for x in ["bilibili.com", "b23.tv"]):
            return "bilibili"
        else:
            return "unknown"

    @staticmethod
    def extract_video_id(url: str) -> str:
        """提取影片 ID (支援 YouTube & Bilibili)"""
        platform = PlatformUtils.detect_platform(url)
        if platform == "youtube":
            for pattern in [
                PATTERNS.YOUTUBE_VIDEO_ID,
                PATTERNS.YOUTUBE_SHORT_URL,
                PATTERNS.YOUTUBE_SHORTS,
                PATTERNS.YOUTUBE_EMBED,
                PATTERNS.YOUTUBE_LIVE,
                PATTERNS.YOUTUBE_PLAYLIST,
            ]:
                match = pattern.search(url)
                if match:
                    return match.group(1)
        elif platform == "bilibili":
            for pattern in [PATTERNS.BILIBILI_BV, PATTERNS.BILIBILI_AV, PATTERNS.BILIBILI_VIDEO]:
                match = pattern.search(url)
                if match:
                    return f"bili_{match.group(1)}"
        return url.strip()

    @staticmethod
    def extract_playlist_id(url: str) -> str:
        """提取播放清單 ID"""
        match = PATTERNS.YOUTUBE_PLAYLIST.search(url)
        if match:
            return match.group(1)
        return url.strip()


# ==================== Cookie 管理器 ====================
class CookieManager:
    """Cookie 提取與管理"""

    def __init__(self, parent_widget=None):
        self.parent = parent_widget
        self.last_update = 0
        self.update_interval = CONSTANTS.COOKIE_UPDATE_INTERVAL

    def _extract_firefox_cookies(
        self,
        output_file: str,
        platform: str,
        test_urls: list[dict[str, list[str]]],
        key_cookies: list[str],
        fail_message: str,
    ) -> tuple[bool, str]:
        """從 Firefox 提取指定平台的 Cookies（共用邏輯）"""
        try:
            for method in test_urls:
                try:
                    result = subprocess.run(
                        bin_manager.get_base_ytdlp_cmd() + method["args"],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        timeout=45,
                        env=bin_manager.get_ytdlp_env(),
                    )
                    if result.returncode == 0 and os.path.exists(output_file):
                        file_size = os.path.getsize(output_file)
                        if file_size < 100:
                            continue
                        with open(output_file, encoding="utf-8") as f:
                            content = f.read()
                        found_keys = [k for k in key_cookies if k in content]
                        missing_keys = [k for k in key_cookies if k not in found_keys]
                        if platform == "youtube":
                            return (
                                True,
                                f"{method['name']}成功！\n檔案大小: {file_size} bytes\n"
                                f"找到關鍵 Cookie: {', '.join(found_keys) if found_keys else '無'}",
                            )
                        else:
                            if missing_keys:
                                return True, f"{method['name']}完成，但缺少關鍵 Cookie: {', '.join(missing_keys)}"
                            return True, f"{method['name']}成功！找到所有關鍵 Cookie"
                except (subprocess.TimeoutExpired, OSError):
                    continue
            return False, fail_message
        except (OSError, subprocess.SubprocessError) as e:
            return False, f"提取失敗: {str(e)}"

    def extract_firefox_cookies_youtube(self, output_file: str) -> tuple[bool, str]:
        """從 Firefox 提取 YouTube Cookies"""
        methods = [
            {
                "name": "增強提取",
                "args": [
                    "--cookies-from-browser",
                    "firefox",
                    "--cookies",
                    output_file,
                    "--print",
                    "webpage_url",
                    "--simulate",
                    "--no-warnings",
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                ],
            },
            {
                "name": "標準提取",
                "args": [
                    "--cookies-from-browser",
                    "firefox",
                    "--cookies",
                    output_file,
                    "--simulate",
                    "--quiet",
                    "https://www.youtube.com",
                ],
            },
        ]
        return self._extract_firefox_cookies(
            output_file,
            "youtube",
            methods,
            CONSTANTS.YOUTUBE_KEY_COOKIES,
            "所有提取方法都失敗。請確認:\n1. Firefox 已安裝並登入 YouTube\n2. 已關閉所有 Firefox 視窗",
        )

    def extract_firefox_cookies_bilibili(self, output_file: str) -> tuple[bool, str]:
        """從 Firefox 提取 Bilibili Cookies"""
        methods = [
            {
                "name": "增強提取",
                "args": [
                    "--cookies-from-browser",
                    "firefox",
                    "--cookies",
                    output_file,
                    "--print",
                    "webpage_url",
                    "--simulate",
                    "--no-warnings",
                    "https://www.bilibili.com/video/BV1xx411c7mD",
                ],
            },
            {
                "name": "標準提取",
                "args": [
                    "--cookies-from-browser",
                    "firefox",
                    "--cookies",
                    output_file,
                    "--simulate",
                    "--quiet",
                    "https://www.bilibili.com",
                ],
            },
        ]
        return self._extract_firefox_cookies(
            output_file,
            "bilibili",
            methods,
            CONSTANTS.BILIBILI_KEY_COOKIES,
            "所有提取方法都失敗。",
        )

    def validate_youtube_cookies(self, cookie_file: str) -> tuple[bool, str]:
        """驗證 YouTube Cookies 有效性"""
        if not os.path.exists(cookie_file):
            return False, "Cookie 檔案不存在"
        try:
            result = subprocess.run(
                bin_manager.get_base_ytdlp_cmd()
                + [
                    "--cookies",
                    cookie_file,
                    "--print",
                    "%(uploader)s",
                    "--simulate",
                    "--quiet",
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
                env=bin_manager.get_ytdlp_env(),
            )
            return (True, "Cookies 有效") if result.returncode == 0 else (False, "Cookies 無效或已過期")
        except subprocess.TimeoutExpired:
            return False, "測試超時"
        except (OSError, subprocess.SubprocessError) as e:
            return False, f"測試錯誤: {str(e)}"

    def validate_bilibili_cookies(self, cookie_file: str) -> tuple[bool, dict]:
        """驗證 Bilibili Cookies"""
        if not os.path.exists(cookie_file):
            return False, {"error": "Cookie 檔案不存在"}
        try:
            cookies = {}
            with open(cookie_file, encoding="utf-8") as f:
                for line in f:
                    if line.startswith("#") or not line.strip():
                        continue
                    parts = line.strip().split("\t")
                    if len(parts) >= 7:
                        cookies[parts[5]] = parts[6]
            missing = [c for c in CONSTANTS.BILIBILI_KEY_COOKIES if c not in cookies]
            if missing:
                return False, {"error": f"缺少關鍵 Cookie: {', '.join(missing)}"}
            return True, {"message": "Cookies 檔案格式正確"}
        except (OSError, ValueError) as e:
            return False, {"error": f"驗證錯誤: {str(e)}"}


# ==================== 通用非同步 Worker ====================
class AsyncWorker(QThread):
    """在背景執行緒中執行任意 callable，完成後發射信號回到主執行緒。"""

    finished = Signal(object)  # 回傳結果
    error = Signal(str)  # 錯誤訊息

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def run(self):
        try:
            result = self._fn(*self._args, **self._kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# ==================== 下載訊號類別 ====================
class DownloadSignals(QObject):
    """下載進度信號"""

    progress = Signal(str, float, str)  # video_id, progress, status
    finished = Signal(str, bool, str)  # video_id, success, message
    log = Signal(str)  # log message
    speed = Signal(str, str, str)  # video_id, speed, eta


# ==================== 下載工作執行緒 ====================
class DownloadWorker(QThread):
    """下載工作執行緒 - 支援重試與速度限制"""

    progress_update = Signal(str, float, str)
    download_finished = Signal(str, bool, str)
    log_message = Signal(str)
    speed_update = Signal(str, str, str)

    def __init__(
        self,
        url: str,
        output_dir: str,
        format_id: str = None,
        include_subs: bool = False,
        sub_langs: str = "en,zh-TW,zh-Hant",
        cookie_file: str = None,
        video_id: str = None,
        max_retries: int = None,
        rate_limit: str = None,
    ):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.format_id = format_id
        self.include_subs = include_subs
        self.sub_langs = sub_langs
        self.cookie_file = cookie_file
        self.video_id = video_id or PlatformUtils.extract_video_id(url)
        self.max_retries = max_retries or CONSTANTS.DEFAULT_RETRY_COUNT
        self.rate_limit = rate_limit
        self._is_cancelled = False
        self.process = None
        self.start_time = None
        self.downloaded_bytes = 0

    def cancel(self):
        """取消下載"""
        self._is_cancelled = True
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except OSError:
                try:
                    self.process.kill()
                except OSError:
                    pass

    def run(self):
        """執行下載 (含重試邏輯)"""
        self.start_time = time.time()
        for attempt in range(self.max_retries):
            if self._is_cancelled:
                self.download_finished.emit(self.video_id, False, "已取消")
                return
            if attempt > 0:
                self.log_message.emit(f"[{self.video_id}] 重試 {attempt}/{self.max_retries - 1}...")
                time.sleep(CONSTANTS.RETRY_DELAY * attempt)
            success, message = self._download_once()
            if success or self._is_cancelled:
                self.download_finished.emit(self.video_id, success, message)
                return
        self.download_finished.emit(self.video_id, False, f"下載失敗（已重試 {self.max_retries} 次）: {message}")

    def _download_once(self) -> tuple[bool, str]:
        """單次下載嘗試"""
        try:
            platform = PlatformUtils.detect_platform(self.url)
            cmd = self._build_command(platform)
            self.log_message.emit(f"[{self.video_id}] 開始下載...")
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo,
                bufsize=1,
                env=bin_manager.get_ytdlp_env(),
            )
            for line in iter(self.process.stdout.readline, ""):
                if self._is_cancelled:
                    self.process.terminate()
                    return False, "已取消"
                self._parse_progress(line)
            self.process.wait()
            if self.process.returncode == 0:
                elapsed = time.time() - self.start_time
                return True, f"下載完成 (耗時 {elapsed:.1f}s)"
            return False, f"下載失敗 (返回碼: {self.process.returncode})"
        except (OSError, subprocess.SubprocessError) as e:
            return False, f"錯誤: {str(e)}"

    def _build_command(self, platform: str) -> list[str]:
        """建立下載命令"""
        cmd = bin_manager.get_base_ytdlp_cmd() + [
            "-o",
            os.path.join(self.output_dir, "%(title)s.%(ext)s"),
            "--no-playlist",
            "--progress",
            "--newline",
        ]
        if self.rate_limit:
            cmd.extend(["--limit-rate", self.rate_limit])
        if self.cookie_file and os.path.exists(self.cookie_file):
            cmd.extend(["--cookies", self.cookie_file])
        else:
            cmd.extend(["--cookies-from-browser", "firefox"])
        if platform == "bilibili":
            cmd.extend(["--referer", "https://www.bilibili.com", "--add-header", "Origin:https://www.bilibili.com"])
        if self.format_id:
            cmd.extend(["-f", self.format_id])
        else:
            cmd.extend(["-f", "bestvideo+bestaudio/best"])
        cmd.extend(["--merge-output-format", "mp4"])
        if self.include_subs:
            cmd.extend(
                [
                    "--write-subs",
                    "--write-auto-subs",
                    "--sub-langs",
                    self.sub_langs,
                    "--embed-subs",
                    "--convert-subs",
                    "srt",
                ]
            )
        cmd.append(self.url)
        return cmd

    def _parse_progress(self, line: str):
        """解析進度輸出"""
        line = line.strip()
        if not line:
            return
        progress_match = PATTERNS.PROGRESS_PERCENT.search(line)
        if progress_match:
            try:
                percent = float(progress_match.group(1))
                self.progress_update.emit(self.video_id, percent, "下載中")
            except ValueError:
                pass
        speed_match = PATTERNS.DOWNLOAD_SPEED.search(line)
        eta_match = PATTERNS.DOWNLOAD_ETA.search(line)
        if speed_match:
            speed = speed_match.group(1)
            eta = eta_match.group(1) if eta_match else "--:--"
            self.speed_update.emit(self.video_id, speed, eta)
        if "[download]" in line or "[info]" in line:
            self.log_message.emit(f"[{self.video_id}] {line}")


# ==================== 批量下載 Worker ====================
class BatchDownloadWorker(QThread):
    """批量下載工作執行緒"""

    progress_update = Signal(int)
    status_change = Signal(str)
    download_progress = Signal(str)
    log_message = Signal(str)
    task_finished = Signal(dict)

    def __init__(self, task_id: int, urls: list[str], settings: dict, main_window=None):
        super().__init__()
        self.task_id = task_id
        self.urls = urls
        self.settings = settings
        self.main_window = main_window
        self._is_running = True
        self._is_paused = False
        self.stats = {"success": 0, "failed": 0, "skipped": 0}

    def run(self):
        """執行批量下載任務"""
        try:
            start_time = time.time()
            self.log_message.emit(f" 任務 #{self.task_id} 開始 ({len(self.urls)} 個項目)")

            for idx, url in enumerate(self.urls, 1):
                if not self._is_running:
                    break
                while self._is_paused and self._is_running:
                    self.msleep(100)
                if not self._is_running:
                    break

                self.status_change.emit(f"下載 {idx}/{len(self.urls)}")
                self.progress_update.emit(idx)

                platform = PlatformUtils.detect_platform(url)
                video_id = PlatformUtils.extract_video_id(url)
                self.log_message.emit(f"\n [{idx}/{len(self.urls)}] {url}")
                self.log_message.emit(f" 平台: {platform}, ID: {video_id}")

                # 檢查是否已下載
                download_path = self.settings.get("download_path", "")
                if self.main_window and download_path:
                    if self.main_window.is_downloaded(download_path, video_id):
                        self.stats["skipped"] += 1
                        self.log_message.emit(" 已下載過，跳過")
                        continue

                # 執行下載
                success = self._download_single(url, platform)

                if success:
                    self.stats["success"] += 1
                    self.log_message.emit(" 下載成功")
                    if self.main_window and download_path:
                        self.main_window.add_to_download_history(download_path, video_id, url, title=None)
                else:
                    self.stats["failed"] += 1
                    self.log_message.emit(" 下載失敗")

                if idx < len(self.urls) and self._is_running:
                    self.msleep(2000)

            duration = int(time.time() - start_time)
            self.log_message.emit("\n" + "=" * 50)
            self.log_message.emit(" 任務完成")
            self.log_message.emit(f" 成功: {self.stats['success']}")
            self.log_message.emit(f" 失敗: {self.stats['failed']}")
            self.log_message.emit(f" 跳過: {self.stats['skipped']}")
            self.log_message.emit(f" 耗時: {duration // 60}分{duration % 60}秒")

            self.task_finished.emit(self.stats)

        except (OSError, subprocess.SubprocessError) as e:
            self.log_message.emit(f" 任務錯誤: {str(e)}")
            traceback.print_exc()

    def _download_single(self, url: str, platform: str) -> bool:
        """下載單一影片"""
        try:
            cmd = self._build_ytdlp_command(url, platform)
            self.log_message.emit(f" 執行: {' '.join(cmd[:5])}...")

            timeout = self.settings.get("download_timeout", CONSTANTS.DEFAULT_TIMEOUT)

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=self.settings.get("download_path"),
                bufsize=1,
                env=bin_manager.get_ytdlp_env(),
            )

            last_progress = ""
            has_successful_download = False
            try:
                for line in iter(process.stdout.readline, ""):
                    if not self._is_running:
                        process.terminate()
                        break
                    line = line.strip()
                    if not line:
                        continue
                    if "[download]" in line:
                        progress_info = self._parse_progress(line)
                        if progress_info and progress_info != last_progress:
                            self.download_progress.emit(progress_info)
                            last_progress = progress_info
                        # 偵測下載完成的標記
                        if "has already been downloaded" in line or "100%" in line:
                            has_successful_download = True
                    elif "ERROR" in line or "WARNING" in line:
                        self.log_message.emit(f" {line}")
                    elif "[Merger]" in line or "Deleting original file" in line:
                        has_successful_download = True

                process.stdout.close()
                return_code = process.wait(timeout=timeout if timeout > 0 else None)
                # 播放清單中部分影片失敗（如被刪除）時 yt-dlp 回傳非零，
                # 但只要有任何影片成功下載就視為成功
                success = return_code == 0 or has_successful_download
                if not success:
                    self._cleanup_partial_files()
                return success

            except subprocess.TimeoutExpired:
                process.kill()
                self.log_message.emit(" 下載超時")
                self._cleanup_partial_files()
                return False

        except (OSError, subprocess.SubprocessError) as e:
            self.log_message.emit(f" 錯誤: {str(e)}")
            self._cleanup_partial_files()
            return False

    def _cleanup_partial_files(self):
        """清理下載失敗後殘留的不完整檔案（.part, .ytdl, .temp 等）"""
        download_path = self.settings.get("download_path")
        if not download_path or not os.path.isdir(download_path):
            return
        try:
            cleaned = 0
            for name in os.listdir(download_path):
                if name.endswith(CONSTANTS.IGNORE_SUFFIXES):
                    file_path = os.path.join(download_path, name)
                    try:
                        os.remove(file_path)
                        cleaned += 1
                    except OSError:
                        pass
            if cleaned:
                self.log_message.emit(f" 已清理 {cleaned} 個不完整檔案")
        except OSError:
            pass

    def _parse_progress(self, line: str) -> str:
        """解析進度輸出 (使用預編譯 regex)"""
        try:
            if "%" in line:
                parts = []
                percent_match = PATTERNS.PROGRESS_PERCENT.search(line)
                size_match = PATTERNS.PROGRESS_SIZE.search(line)
                speed_match = PATTERNS.PROGRESS_SPEED.search(line)
                eta_match = PATTERNS.PROGRESS_ETA.search(line)

                if percent_match:
                    parts.append(f" {percent_match.group(1)}%")
                if size_match:
                    parts.append(f" {size_match.group(1)}")
                if speed_match:
                    parts.append(f" {speed_match.group(1)}")
                if eta_match:
                    parts.append(f" {eta_match.group(1)}")

                if parts:
                    return " | ".join(parts)
        except (ValueError, AttributeError):
            pass
        return ""

    def _build_ytdlp_command(self, url: str, platform: str) -> list[str]:
        """建構 yt-dlp 指令"""
        cmd = bin_manager.get_base_ytdlp_cmd()

        if self.settings.get("use_cookies"):
            cookie_file = self.settings.get(f"{platform}_cookie_file")
            if cookie_file and os.path.exists(cookie_file):
                cmd.extend(["--cookies", cookie_file])
            else:
                cmd.extend(["--cookies-from-browser", "firefox"])

        if self.settings.get("download_path"):
            custom_template = None
            if self.settings.get("use_custom_filename"):
                template_text = (self.settings.get("custom_filename_template") or "").strip()
                if template_text:
                    custom_template = template_text

            base_template = custom_template or "%(uploader)s - %(title)s [%(id)s]"
            # 啟用檔名修剪時，將 [%(id)s] 放到前面，防止被截斷導致檔名碰撞
            if not custom_template and self.settings.get("auto_trim_filename"):
                base_template = "[%(id)s] %(uploader)s - %(title)s"
            if "%(ext" not in base_template:
                base_template = f"{base_template}.%(ext)s"

            output_template = os.path.join(self.settings["download_path"], base_template)
            cmd.extend(["-o", output_template])

        quality = (self.settings.get("quality") or "best").strip().lower()
        if quality == "best":
            cmd.extend(["-f", "bestvideo+bestaudio/best"])
        elif quality == "worst":
            cmd.extend(["-f", "worstvideo+worstaudio/worst"])
        elif quality in CONSTANTS.QUALITY_CAPS:
            height = CONSTANTS.QUALITY_CAPS[quality]
            cmd.extend(["-f", f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"])
        else:
            cmd.extend(["-f", quality])
        cmd.extend(["--merge-output-format", "mp4"])

        if self.settings.get("download_subtitle"):
            cmd.append("--write-subs")
            if self.settings.get("auto_subtitle"):
                cmd.append("--write-auto-subs")
            lang = self.settings.get("subtitle_lang", "zh-TW,zh,en")
            cmd.extend(["--sub-langs", lang])
            if not self.settings.get("subtitle_only"):
                cmd.append("--embed-subs")

        if self.settings.get("subtitle_only"):
            cmd.append("--skip-download")

        if self.settings.get("auto_trim_filename"):
            trim_length = self.settings.get("trim_filename_length", 120)
            cmd.extend(["--trim-filenames", str(trim_length)])

        cmd.extend(["--no-warnings", "--ignore-errors", "--retries", "3", "--fragment-retries", "10"])

        if platform == "bilibili":
            cmd.extend(
                [
                    "--referer",
                    "https://www.bilibili.com",
                    "--user-agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                ]
            )

        cmd.append(url)
        return cmd

    def stop(self):
        self._is_running = False

    def pause(self):
        self._is_paused = True

    def resume(self):
        self._is_paused = False


# ==================== 主視窗 ====================
class MainWindow(QMainWindow):
    """主應用程式視窗"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"影片批量下載工具 {APP_VERSION} - PySide6 版 (YouTube & Bilibili)")
        self.resize(1600, 900)

        self.workers = []
        self._async_workers = []
        self.global_seen_ids = set()
        self._seen_ids_lock = threading.Lock()
        self._history_lock = threading.Lock()
        self.cookie_manager = CookieManager(self)
        self.settings = QSettings("VideoDownloader", "PySide6App")

        self.download_history_file = "download_history.json"
        self.download_history = {}
        self.playlist_state_file = "playlist_state.json"
        self.playlist_states = {}
        self.playlist_updates_log_file = "playlist_updates_log.json"
        self.playlist_updates_log = []

        self.youtube_cookie_file = ""
        self.bilibili_cookie_file = ""

        self.init_ui()
        self.load_settings()
        self.load_download_history()
        self.load_playlist_states()
        self.load_playlist_updates_log()

        QTimer.singleShot(1000, self.check_dependencies)
        QTimer.singleShot(2000, self.auto_check_all_playlists_on_start)

    @staticmethod
    def normalize_path(path: str) -> str:
        if not path:
            return ""
        return os.path.normcase(os.path.abspath(os.path.normpath(path)))

    def init_ui(self):
        # 啟用拖放
        self.setAcceptDrops(True)

        self.create_toolbar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([600, 1000])
        self.statusBar().showMessage("就緒")
        self.apply_stylesheet()

        # 設定鍵盤快捷鍵
        self.setup_shortcuts()

        # 初始化最近路徑列表
        self.recent_paths: list[str] = []

    def setup_shortcuts(self):
        """設定鍵盤快捷鍵"""
        # Ctrl+Enter: 開始下載
        shortcut_start = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut_start.activated.connect(self.start_download)

        # Ctrl+V: 快速貼上 URL
        shortcut_paste = QShortcut(QKeySequence("Ctrl+Shift+V"), self)
        shortcut_paste.activated.connect(self.quick_paste_url)

        # F1: 顯示說明
        shortcut_help = QShortcut(QKeySequence("F1"), self)
        shortcut_help.activated.connect(self.show_help)

        # Ctrl+Q: 退出
        shortcut_quit = QShortcut(QKeySequence("Ctrl+Q"), self)
        shortcut_quit.activated.connect(self.close)

        # Ctrl+O: 選擇下載路徑
        shortcut_open = QShortcut(QKeySequence("Ctrl+O"), self)
        shortcut_open.activated.connect(self.browse_download_path)

    def quick_paste_url(self):
        """快速貼上 URL 到當前選中的輸入框"""
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            # 自動偵測並填入對應輸入框
            if "list=" in text or "playlist" in text.lower():
                self.playlist_url_edit.setText(text)
                self.playlist_radio.setChecked(True)
            else:
                self.single_url_edit.setText(text)
                self.single_radio.setChecked(True)
            self.log_to_overview(f"📋 已貼上 URL: {text[:50]}...")

    def dragEnterEvent(self, event: QDragEnterEvent):
        """處理拖入事件"""
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """處理放下事件"""
        mime_data = event.mimeData()

        if mime_data.hasUrls():
            urls = mime_data.urls()
            for url in urls:
                if url.isLocalFile():
                    # 本地檔案 (可能是 txt)
                    file_path = url.toLocalFile()
                    if file_path.endswith(".txt"):
                        self.file_path_edit.setText(file_path)
                        self.file_radio.setChecked(True)
                        self.log_to_overview(f"📁 已拖入檔案: {file_path}")
                else:
                    # 網址
                    url_str = url.toString()
                    self._handle_dropped_url(url_str)
        elif mime_data.hasText():
            text = mime_data.text().strip()
            self._handle_dropped_url(text)

    def _handle_dropped_url(self, url: str):
        """處理拖入的 URL"""
        if not url:
            return
        if "list=" in url or "playlist" in url.lower():
            self.playlist_url_edit.setText(url)
            self.playlist_radio.setChecked(True)
        else:
            self.single_url_edit.setText(url)
            self.single_radio.setChecked(True)
        self.log_to_overview(f"🔗 已拖入 URL: {url[:50]}...")

    def create_toolbar(self):
        toolbar = QToolBar("主工具列")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        start_action = QAction(" 開始下載", self)
        start_action.triggered.connect(self.start_download)
        toolbar.addAction(start_action)

        check_playlist_action = QAction(" 檢查目前清單", self)
        check_playlist_action.triggered.connect(self.manual_check_playlist_updates)
        toolbar.addAction(check_playlist_action)

        check_all_action = QAction(" 檢查所有清單", self)
        check_all_action.triggered.connect(self.manual_check_all_playlists)
        toolbar.addAction(check_all_action)

        toolbar.addSeparator()

        export_action = QAction("📊 匯出報告", self)
        export_action.triggered.connect(self.export_download_report)
        export_action.setToolTip("匯出下載歷史報告 (CSV/HTML)")
        toolbar.addAction(export_action)

        help_action = QAction("❓ 說明", self)
        help_action.triggered.connect(self.show_help)
        help_action.setToolTip("顯示使用說明 (F1)")
        toolbar.addAction(help_action)

    def create_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        scroll_layout.addWidget(self.create_platform_group())
        scroll_layout.addWidget(self.create_input_group())
        scroll_layout.addWidget(self.create_path_group())
        scroll_layout.addWidget(self.create_download_settings_group())
        scroll_layout.addWidget(self.create_cookie_group())
        scroll_layout.addWidget(self.create_subtitle_group())
        scroll_layout.addWidget(self.create_action_buttons())
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        return panel

    def create_platform_group(self) -> QGroupBox:
        group = QGroupBox("平台選擇")
        layout = QHBoxLayout()

        self.platform_buttons = QButtonGroup()

        youtube_btn = QRadioButton("YouTube")
        self.platform_buttons.addButton(youtube_btn, 0)
        layout.addWidget(youtube_btn)

        bilibili_btn = QRadioButton("Bilibili")
        self.platform_buttons.addButton(bilibili_btn, 1)
        layout.addWidget(bilibili_btn)

        auto_btn = QRadioButton("自動偵測")
        auto_btn.setChecked(True)
        self.platform_buttons.addButton(auto_btn, 2)
        layout.addWidget(auto_btn)

        group.setLayout(layout)
        return group

    def create_input_group(self) -> QGroupBox:
        group = QGroupBox("輸入模式")
        group.setToolTip("選擇輸入方式：單一影片、播放清單或網址清單檔案\n💡 提示：可直接拖放 URL 或 .txt 檔案到視窗")
        layout = QVBoxLayout()

        # 拖放提示
        drop_hint = QLabel("💡 支援拖放 URL 或 .txt 檔案")
        drop_hint.setStyleSheet("color: #888; font-size: 11px; margin-bottom: 5px;")
        layout.addWidget(drop_hint)

        self.single_radio = QRadioButton("單一影片")
        self.single_radio.setToolTip("下載單一影片")
        layout.addWidget(self.single_radio)

        self.single_url_edit = QLineEdit()
        self.single_url_edit.setPlaceholderText("輸入影片網址...")
        self.single_url_edit.setToolTip("可輸入 YouTube 或 Bilibili 影片網址")
        self.single_url_edit.textChanged.connect(self._on_single_url_changed)
        layout.addWidget(self.single_url_edit)

        self.playlist_radio = QRadioButton("播放清單")
        self.playlist_radio.setChecked(True)
        self.playlist_radio.setToolTip("下載整個播放清單")
        layout.addWidget(self.playlist_radio)

        self.playlist_url_edit = QLineEdit()
        self.playlist_url_edit.setPlaceholderText("輸入播放清單網址...")
        self.playlist_url_edit.setToolTip("輸入含有 list= 參數的 YouTube 播放清單網址")
        self.playlist_url_edit.textChanged.connect(self._on_playlist_url_changed)
        layout.addWidget(self.playlist_url_edit)

        self.remember_playlist_check = QCheckBox("記憶此播放清單")
        self.remember_playlist_check.setChecked(True)
        self.remember_playlist_check.setToolTip("勾選後會記錄此播放清單，可在「檢查所有清單」中追蹤更新")
        layout.addWidget(self.remember_playlist_check)

        self.file_radio = QRadioButton("網址清單檔案")
        self.file_radio.setToolTip("從 .txt 檔案載入多個網址")
        layout.addWidget(self.file_radio)

        file_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("選擇網址清單檔案...")
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setToolTip("每行一個 URL 的文字檔案")
        file_layout.addWidget(self.file_path_edit)

        browse_btn = QPushButton("瀏覽")
        browse_btn.clicked.connect(self.browse_url_file)
        browse_btn.setToolTip("選擇 .txt 檔案 (快捷鍵: Ctrl+O 選擇路徑)")
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)

        group.setLayout(layout)
        return group

    def _on_single_url_changed(self, text: str):
        """當單一影片 URL 變更時自動偵測類型"""
        if text.strip():
            self.single_radio.setChecked(True)
            # 如果是播放清單 URL，自動切換
            if "list=" in text:
                self.playlist_url_edit.setText(text)
                self.playlist_radio.setChecked(True)
                self.single_url_edit.clear()

    def _on_playlist_url_changed(self, text: str):
        """當播放清單 URL 變更時自動選擇"""
        if text.strip():
            self.playlist_radio.setChecked(True)

    def create_path_group(self) -> QGroupBox:
        group = QGroupBox("下載路徑")
        group.setToolTip("設定影片下載的目標資料夾")
        layout = QHBoxLayout()

        self.download_path_edit = QLineEdit()
        self.download_path_edit.setPlaceholderText("選擇下載資料夾...")
        self.download_path_edit.setReadOnly(True)
        self.download_path_edit.setToolTip("影片將下載至此資料夾\n快捷鍵: Ctrl+O")
        layout.addWidget(self.download_path_edit)

        browse_btn = QPushButton("瀏覽")
        browse_btn.clicked.connect(self.browse_download_path)
        browse_btn.setToolTip("選擇下載目標資料夾 (Ctrl+O)")
        layout.addWidget(browse_btn)

        group.setLayout(layout)
        return group

    def create_download_settings_group(self) -> QGroupBox:
        group = QGroupBox("下載設定")
        group.setToolTip("設定下載畫質、超時時間與檔名格式")
        layout = QFormLayout()

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(CONSTANTS.QUALITY_OPTIONS)
        self.quality_combo.setCurrentText("best")
        self.quality_combo.setToolTip("選擇下載畫質\nbest: 最高畫質\nworst: 最低畫質\n其他: 指定解析度上限")
        layout.addRow("畫質:", self.quality_combo)

        timeout_layout = QHBoxLayout()
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setMinimum(0)
        self.timeout_spin.setMaximum(36000)
        self.timeout_spin.setValue(CONSTANTS.DEFAULT_TIMEOUT)
        self.timeout_spin.setSuffix(" 秒")
        self.timeout_spin.setSpecialValueText("不限時")
        self.timeout_spin.setToolTip("設定單一影片下載超時時間\n0 表示不限時\n建議長影片設定較長時間")
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        layout.addRow("下載超時:", timeout_layout)

        self.debug_mode_check = QCheckBox("除錯模式")
        self.debug_mode_check.setToolTip("顯示詳細的下載資訊與錯誤訊息")
        layout.addRow("", self.debug_mode_check)

        self.custom_filename_check = QCheckBox("使用自訂檔名模板")
        self.custom_filename_check.setToolTip("啟用後可自訂下載檔案的命名規則")
        layout.addRow("", self.custom_filename_check)

        self.custom_filename_edit = QLineEdit("%(title)s [%(id)s]")
        self.custom_filename_edit.setToolTip(
            "檔名模板變數說明：\n"
            "%(title)s - 影片標題\n"
            "%(id)s - 影片 ID\n"
            "%(uploader)s - 上傳者名稱\n"
            "%(upload_date)s - 上傳日期\n"
            "%(duration)s - 影片長度\n"
            "%(resolution)s - 解析度"
        )
        layout.addRow("檔名模板:", self.custom_filename_edit)

        trim_layout = QHBoxLayout()
        self.auto_trim_filename_check = QCheckBox("自動縮短過長檔名")
        self.auto_trim_filename_check.setChecked(True)
        self.auto_trim_filename_check.setToolTip("自動截斷過長的檔案名稱\n避免因檔名過長導致的儲存錯誤")
        trim_layout.addWidget(self.auto_trim_filename_check)

        self.trim_filename_spin = QSpinBox()
        self.trim_filename_spin.setRange(20, 200)
        self.trim_filename_spin.setValue(120)
        self.trim_filename_spin.setSuffix(" 字元")
        self.trim_filename_spin.setToolTip("檔名最大長度限制")
        trim_layout.addWidget(self.trim_filename_spin)
        trim_layout.addStretch()

        self.auto_trim_filename_check.toggled.connect(self.trim_filename_spin.setEnabled)
        layout.addRow("長檔名處理:", trim_layout)

        group.setLayout(layout)
        return group

    def create_cookie_group(self) -> QGroupBox:
        group = QGroupBox("Cookie 設定")
        group.setToolTip("Cookie 用於下載會員限定影片\n需先在瀏覽器登入後提取")
        layout = QVBoxLayout()

        # YouTube Cookie
        youtube_layout = QHBoxLayout()
        self.youtube_status_label = QLabel("🟡")
        self.youtube_status_label.setToolTip("Cookie 狀態：未驗證")
        self.youtube_status_label.setFixedWidth(20)
        youtube_layout.addWidget(self.youtube_status_label)
        youtube_layout.addWidget(QLabel("YouTube:"))

        self.youtube_cookie_edit = QLineEdit()
        self.youtube_cookie_edit.setPlaceholderText("YouTube Cookie 檔案...")
        self.youtube_cookie_edit.setReadOnly(True)
        self.youtube_cookie_edit.setToolTip("從 Firefox 瀏覽器提取的 Cookie 檔案")
        youtube_layout.addWidget(self.youtube_cookie_edit)

        youtube_extract_btn = QPushButton("提取")
        youtube_extract_btn.clicked.connect(lambda: self.extract_cookies("youtube"))
        youtube_extract_btn.setToolTip("從 Firefox 自動提取登入 Cookie\n需先登入 YouTube")
        youtube_layout.addWidget(youtube_extract_btn)

        youtube_test_btn = QPushButton("測試")
        youtube_test_btn.clicked.connect(lambda: self.test_cookies("youtube"))
        youtube_test_btn.setToolTip("驗證 Cookie 是否有效")
        youtube_layout.addWidget(youtube_test_btn)
        layout.addLayout(youtube_layout)

        # Bilibili Cookie
        bilibili_layout = QHBoxLayout()
        self.bilibili_status_label = QLabel("🟡")
        self.bilibili_status_label.setToolTip("Cookie 狀態：未驗證")
        self.bilibili_status_label.setFixedWidth(20)
        bilibili_layout.addWidget(self.bilibili_status_label)
        bilibili_layout.addWidget(QLabel("Bilibili:"))

        self.bilibili_cookie_edit = QLineEdit()
        self.bilibili_cookie_edit.setPlaceholderText("Bilibili Cookie 檔案...")
        self.bilibili_cookie_edit.setReadOnly(True)
        self.bilibili_cookie_edit.setToolTip("從 Firefox 瀏覽器提取的 Cookie 檔案")
        bilibili_layout.addWidget(self.bilibili_cookie_edit)

        bilibili_extract_btn = QPushButton("提取")
        bilibili_extract_btn.clicked.connect(lambda: self.extract_cookies("bilibili"))
        bilibili_extract_btn.setToolTip("從 Firefox 自動提取登入 Cookie\n需先登入 Bilibili")
        bilibili_layout.addWidget(bilibili_extract_btn)

        bilibili_test_btn = QPushButton("測試")
        bilibili_test_btn.clicked.connect(lambda: self.test_cookies("bilibili"))
        bilibili_test_btn.setToolTip("驗證 Cookie 是否有效")
        bilibili_layout.addWidget(bilibili_test_btn)
        layout.addLayout(bilibili_layout)

        self.use_cookies_check = QCheckBox("啟用 Cookies (會員影片)")
        self.use_cookies_check.setChecked(True)
        self.use_cookies_check.setToolTip("啟用後可下載需要登入的會員限定影片")
        layout.addWidget(self.use_cookies_check)

        group.setLayout(layout)
        return group

    def update_cookie_status(self, platform: str, is_valid: bool | None):
        """更新 Cookie 狀態指示器"""
        if platform == "youtube":
            label = self.youtube_status_label
        else:
            label = self.bilibili_status_label

        if is_valid is None:
            label.setText("🟡")
            label.setToolTip("Cookie 狀態：未驗證")
        elif is_valid:
            label.setText("🟢")
            label.setToolTip("Cookie 狀態：有效")
        else:
            label.setText("🔴")
            label.setToolTip("Cookie 狀態：無效或已過期")

    def create_subtitle_group(self) -> QGroupBox:
        group = QGroupBox("字幕設定")
        group.setToolTip("設定字幕下載選項")
        layout = QVBoxLayout()

        self.download_subtitle_check = QCheckBox("下載字幕")
        self.download_subtitle_check.setChecked(True)
        self.download_subtitle_check.setToolTip("下載影片的字幕檔案 (若有提供)")
        layout.addWidget(self.download_subtitle_check)

        self.auto_subtitle_check = QCheckBox("下載自動生成字幕")
        self.auto_subtitle_check.setChecked(True)
        self.auto_subtitle_check.setToolTip("下載 YouTube 自動生成的字幕\n適用於沒有手動字幕的影片")
        layout.addWidget(self.auto_subtitle_check)

        self.subtitle_only_check = QCheckBox("僅下載字幕")
        self.subtitle_only_check.setToolTip("只下載字幕檔案，不下載影片")
        layout.addWidget(self.subtitle_only_check)

        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("語言:"))
        self.subtitle_lang_edit = QLineEdit("zh-TW,zh,en")
        self.subtitle_lang_edit.setToolTip("指定下載的字幕語言\n多個語言用逗號分隔\n例如: zh-TW,zh,en,ja")
        lang_layout.addWidget(self.subtitle_lang_edit)
        layout.addLayout(lang_layout)

        group.setLayout(layout)
        return group

    def create_action_buttons(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()

        self.start_btn = QPushButton(" 開始下載")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.start_btn.clicked.connect(self.start_download)
        layout.addWidget(self.start_btn)

        self.check_playlist_btn = QPushButton(" 檢查目前播放清單")
        self.check_playlist_btn.clicked.connect(self.manual_check_playlist_updates)
        layout.addWidget(self.check_playlist_btn)

        self.check_all_playlist_btn = QPushButton(" 檢查所有播放清單")
        self.check_all_playlist_btn.clicked.connect(self.manual_check_all_playlists)
        layout.addWidget(self.check_all_playlist_btn)

        widget.setLayout(layout)
        return widget

    def create_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        self.task_tabs = QTabWidget()
        self.task_tabs.setTabsClosable(True)
        self.task_tabs.tabCloseRequested.connect(self.close_task_tab)

        overview = self.create_overview_tab()
        self.task_tabs.addTab(overview, "總覽")

        layout.addWidget(self.task_tabs)
        return panel

    def create_overview_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.overview_log = QTextEdit()
        self.overview_log.setReadOnly(True)
        self.overview_log.setFont(QFont("Consolas", 9))

        welcome_msg = f""" 影片批量下載工具 {APP_VERSION} - PySide6 版本

 支援平台: YouTube & Bilibili
 Cookie 提取: Firefox 瀏覽器登入後提取
 核心改進:
    預編譯正規表達式提升效能
    自動重試機制
    增強的錯誤處理

等待您的操作...
"""
        self.overview_log.setPlainText(welcome_msg)
        layout.addWidget(self.overview_log)
        return widget

    def apply_stylesheet(self):
        style = """
        QMainWindow { background-color: #1e1e1e; color: #d4d4d4; }
        QGroupBox { font-weight: bold; border: 1px solid #3c3c3c; border-radius: 4px; margin-top: 8px; padding-top: 8px; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        QPushButton { background-color: #0e639c; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
        QPushButton:hover { background-color: #1177bb; }
        QPushButton:pressed { background-color: #0d5689; }
        QPushButton:disabled { background-color: #3c3c3c; color: #6e6e6e; }
        QLineEdit, QComboBox, QTextEdit { background-color: #3c3c3c; color: #d4d4d4; border: 1px solid #6e6e6e; border-radius: 2px; padding: 4px; }
        QLineEdit:focus, QComboBox:focus { border: 1px solid #0e639c; }
        QTextEdit { font-family: "Consolas", "Monaco", monospace; }
        QProgressBar { border: 1px solid #3c3c3c; border-radius: 4px; text-align: center; background-color: #2d2d30; }
        QProgressBar::chunk { background-color: #0e639c; border-radius: 3px; }
        QTabWidget::pane { border: 1px solid #3c3c3c; background-color: #252526; }
        QTabBar::tab { background-color: #2d2d30; color: #d4d4d4; padding: 8px 16px; border: 1px solid #3c3c3c; }
        QTabBar::tab:selected { background-color: #1e1e1e; border-bottom: 2px solid #0e639c; }
        QCheckBox, QRadioButton { color: #d4d4d4; }
        QLabel { color: #d4d4d4; }
        QToolBar { background-color: #2d2d30; border-bottom: 1px solid #3c3c3c; spacing: 5px; }
        QStatusBar { background-color: #007acc; color: white; }
        """
        self.setStyleSheet(style)

    def browse_url_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "選擇網址清單檔案", "", "文字檔案 (*.txt);;所有檔案 (*.*)")
        if file_path:
            self.file_path_edit.setText(file_path)
            self.file_radio.setChecked(True)

    def browse_download_path(self):
        dir_path = QFileDialog.getExistingDirectory(self, "選擇下載資料夾", "", QFileDialog.Option.ShowDirsOnly)
        if dir_path:
            self.download_path_edit.setText(dir_path)

    def extract_cookies(self, platform: str):
        self.log_to_overview(f" 開始提取 {platform.upper()} Cookies...")
        timestamp = int(time.time())
        output_file = f"{platform}_cookies_{timestamp}.txt"

        if platform == "youtube":
            fn = self.cookie_manager.extract_firefox_cookies_youtube
        elif platform == "bilibili":
            fn = self.cookie_manager.extract_firefox_cookies_bilibili
        else:
            return

        worker = AsyncWorker(fn, output_file)

        def on_done(result):
            success, message = result
            if platform == "youtube":
                if success:
                    self.youtube_cookie_file = os.path.abspath(output_file)
                    self.youtube_cookie_edit.setText(self.youtube_cookie_file)
                    self.log_to_overview(" YouTube Cookies 提取成功")
                    QMessageBox.information(self, "成功", f"YouTube Cookies 提取成功！\n\n{message}")
                else:
                    self.log_to_overview(f" YouTube Cookies 提取失敗: {message}")
                    QMessageBox.warning(self, "失敗", f"Cookie 提取失敗\n\n{message}")
            elif platform == "bilibili":
                if success:
                    self.bilibili_cookie_file = os.path.abspath(output_file)
                    self.bilibili_cookie_edit.setText(self.bilibili_cookie_file)
                    self.log_to_overview(" Bilibili Cookies 提取完成")
                    QMessageBox.information(self, "提取完成", f"Bilibili Cookies 已提取\n\n{message}")
                else:
                    self.log_to_overview(f" Bilibili Cookies 提取失敗: {message}")
                    QMessageBox.warning(self, "失敗", f"Cookie 提取失敗\n\n{message}")

        worker.finished.connect(on_done)
        worker.error.connect(lambda e: self.log_to_overview(f" Cookie 提取錯誤: {e}"))
        self._keep_worker_alive(worker)
        worker.start()

    def test_cookies(self, platform: str):
        self.log_to_overview(f"🔍 測試 {platform.upper()} Cookies...")
        if platform == "youtube":
            if not self.youtube_cookie_file:
                QMessageBox.warning(self, "警告", "請先提取 YouTube Cookies")
                self.update_cookie_status("youtube", None)
                return
            worker = AsyncWorker(self.cookie_manager.validate_youtube_cookies, self.youtube_cookie_file)

            def on_yt_done(result):
                valid, message = result
                self.update_cookie_status("youtube", valid)
                if valid:
                    self.log_to_overview("✅ YouTube Cookies 有效")
                    QMessageBox.information(self, "成功", "YouTube Cookies 有效且可用！")
                else:
                    self.log_to_overview(f"❌ YouTube Cookies 無效: {message}")
                    QMessageBox.warning(self, "失敗", f"YouTube Cookies 無效\n{message}")

            worker.finished.connect(on_yt_done)

        elif platform == "bilibili":
            if not self.bilibili_cookie_file:
                QMessageBox.warning(self, "警告", "請先提取 Bilibili Cookies")
                self.update_cookie_status("bilibili", None)
                return
            worker = AsyncWorker(self.cookie_manager.validate_bilibili_cookies, self.bilibili_cookie_file)

            def on_bili_done(result):
                valid, info = result
                self.update_cookie_status("bilibili", valid)
                if valid:
                    self.log_to_overview("✅ Bilibili Cookies 有效")
                    QMessageBox.information(self, "成功", "Bilibili Cookies 有效且可用！")
                else:
                    error = info.get("error", "未知錯誤")
                    self.log_to_overview(f"❌ Bilibili Cookies 無效: {error}")
                    QMessageBox.warning(self, "失敗", f"Bilibili Cookies 無效\n{error}")

            worker.finished.connect(on_bili_done)
        else:
            return

        worker.error.connect(lambda e: self.log_to_overview(f" Cookie 測試錯誤: {e}"))
        self._keep_worker_alive(worker)
        worker.start()

    def start_download(self):
        self.log_to_overview("=" * 50)
        self.log_to_overview(" 啟動下載流程...")

        download_path = self.download_path_edit.text()
        if not download_path:
            QMessageBox.warning(self, "警告", "請選擇下載路徑")
            return

        urls = self.get_urls()
        if not urls:
            QMessageBox.warning(self, "警告", "請輸入有效的影片網址")
            return

        if self.playlist_radio.isChecked() and len(urls) == 1:
            playlist_url = urls[0]
            remember = self.remember_playlist_check.isChecked()
            self.log_to_overview(" 取得播放清單資訊中...")
            self.statusBar().showMessage("取得播放清單資訊中...")

            def fetch_task():
                metadata = self.fetch_playlist_metadata(playlist_url)
                return {"metadata": metadata, "playlist_url": playlist_url, "download_path": download_path}

            worker = AsyncWorker(fetch_task)
            worker.finished.connect(lambda result: self._on_playlist_fetched_for_download(result, remember))
            worker.error.connect(lambda e: self.log_to_overview(f" 播放清單取得失敗: {e}"))
            self._keep_worker_alive(worker)
            worker.start()
            return

        self._proceed_download(urls, download_path)

    def _on_playlist_fetched_for_download(self, result: dict, remember: bool):
        """播放清單 metadata 取得完成後的 UI 邏輯（主執行緒）"""
        metadata = result["metadata"]
        playlist_url = result["playlist_url"]
        download_path = result["download_path"]
        self.statusBar().clearMessage()

        if not metadata:
            self.log_to_overview(" 無法取得播放清單資訊")
            QMessageBox.warning(self, "錯誤", "無法取得播放清單資訊")
            return

        detection = self._process_playlist_detection(
            playlist_url,
            download_path,
            metadata,
            prompt_user=True,
            offer_auto_download=False,
            remember=remember,
        )
        if detection.get("status") == "cancel":
            return

        video_ids = detection.get("video_ids", [])
        expanded, skipped = self._expand_playlist_urls_from_ids(
            playlist_url, video_ids=video_ids, download_path=download_path
        )
        if expanded:
            urls = expanded
            msg = f" 展開播放清單：{len(expanded)} 部影片待下載"
            if skipped:
                msg += f"（已跳過 {skipped} 部已下載）"
            self.log_to_overview(msg)
        elif skipped > 0:
            self.log_to_overview(f" 所有 {skipped} 部影片已下載過")
            QMessageBox.information(self, "提示", "所有影片已下載過，無需再次下載。")
            return
        else:
            urls = [playlist_url]

        self._proceed_download(urls, download_path)

    def _proceed_download(self, urls: list[str], download_path: str):
        """驗證設定後建立下載任務（UI 操作，主執行緒）"""
        self._finalize_download(urls, download_path)

    def _finalize_download(self, urls: list[str], download_path: str):
        """最終建立任務"""
        settings = self.build_download_settings(download_path)
        if not settings:
            return
        task_id = len(self.workers) + 1
        self.create_task(task_id, urls, settings)

    def build_download_settings(self, download_path: str) -> dict | None:
        normalized_path = self.normalize_path(download_path)
        if not os.path.isdir(normalized_path):
            QMessageBox.warning(self, "警告", f"下載路徑不存在:\n{download_path}")
            return None
        return {
            "download_path": normalized_path,
            "use_cookies": self.use_cookies_check.isChecked(),
            "youtube_cookie_file": self.youtube_cookie_file,
            "bilibili_cookie_file": self.bilibili_cookie_file,
            "quality": self.quality_combo.currentText(),
            "download_subtitle": self.download_subtitle_check.isChecked(),
            "auto_subtitle": self.auto_subtitle_check.isChecked(),
            "subtitle_only": self.subtitle_only_check.isChecked(),
            "subtitle_lang": self.subtitle_lang_edit.text(),
            "debug_mode": self.debug_mode_check.isChecked(),
            "download_timeout": self.timeout_spin.value(),
            "use_custom_filename": self.custom_filename_check.isChecked(),
            "custom_filename_template": self.custom_filename_edit.text(),
            "auto_trim_filename": self.auto_trim_filename_check.isChecked(),
            "trim_filename_length": self.trim_filename_spin.value(),
        }

    def get_urls(self) -> list[str]:
        if self.single_radio.isChecked():
            url = self.single_url_edit.text().strip()
            return [url] if url else []
        elif self.playlist_radio.isChecked():
            url = self.playlist_url_edit.text().strip()
            return [url] if url else []
        elif self.file_radio.isChecked():
            file_path = self.file_path_edit.text()
            if not os.path.exists(file_path):
                return []
            try:
                with open(file_path, encoding="utf-8") as f:
                    return [line.strip() for line in f if line.strip()]
            except (OSError, UnicodeDecodeError):
                return []
        return []

    def detect_platforms_from_urls(self, urls: list[str]) -> set:
        platforms = set()
        for url in urls:
            platform = PlatformUtils.detect_platform(url)
            if platform != "unknown":
                platforms.add(platform)
        return platforms

    def auto_extract_cookies_if_needed(self, urls: list[str]):
        """同步版本（已棄用，保留相容性）"""
        self._auto_extract_cookies_async(urls)

    def _auto_extract_cookies_async(self, urls: list[str], on_complete=None):
        """非同步提取所需的 Cookies，完成後呼叫 on_complete。"""
        platforms = self.detect_platforms_from_urls(urls)
        tasks = []

        if "youtube" in platforms and (not self.youtube_cookie_file or not os.path.exists(self.youtube_cookie_file)):
            timestamp = int(time.time())
            tasks.append(("youtube", f"youtube_cookies_{timestamp}.txt"))

        if "bilibili" in platforms and (not self.bilibili_cookie_file or not os.path.exists(self.bilibili_cookie_file)):
            timestamp = int(time.time())
            tasks.append(("bilibili", f"bilibili_cookies_{timestamp}.txt"))

        if not tasks:
            if on_complete:
                on_complete()
            return

        remaining = [len(tasks)]

        def make_handler(platform, output_file):
            def handler(result):
                success, _ = result
                if success:
                    if platform == "youtube":
                        self.youtube_cookie_file = os.path.abspath(output_file)
                        self.youtube_cookie_edit.setText(self.youtube_cookie_file)
                        self.log_to_overview(" YouTube Cookie 自動提取成功")
                    elif platform == "bilibili":
                        self.bilibili_cookie_file = os.path.abspath(output_file)
                        self.bilibili_cookie_edit.setText(self.bilibili_cookie_file)
                        self.log_to_overview(" Bilibili Cookie 自動提取成功")
                remaining[0] -= 1
                if remaining[0] <= 0 and on_complete:
                    on_complete()

            return handler

        for platform, output_file in tasks:
            self.log_to_overview(f" {platform.upper()} Cookie 未設定，自動提取...")
            if platform == "youtube":
                fn = self.cookie_manager.extract_firefox_cookies_youtube
            else:
                fn = self.cookie_manager.extract_firefox_cookies_bilibili
            worker = AsyncWorker(fn, output_file)
            worker.finished.connect(make_handler(platform, output_file))
            worker.error.connect(lambda e, p=platform: self.log_to_overview(f" {p} Cookie 提取錯誤: {e}"))
            self._keep_worker_alive(worker)
            worker.start()

    def fetch_playlist_metadata(self, playlist_url: str) -> dict | None:
        try:
            cmd = bin_manager.get_base_ytdlp_cmd() + ["-J", "--flat-playlist"]
            # 使用 cookie 檔案或直接從瀏覽器讀取
            platform = PlatformUtils.detect_platform(playlist_url)
            cookie_file = ""
            if platform == "youtube":
                cookie_file = self.youtube_cookie_file
            elif platform == "bilibili":
                cookie_file = self.bilibili_cookie_file
            if cookie_file and os.path.exists(cookie_file):
                cmd.extend(["--cookies", cookie_file])
            else:
                cmd.extend(["--cookies-from-browser", "firefox"])
            cmd.append(playlist_url)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
                env=bin_manager.get_ytdlp_env(),
            )
            if result.returncode != 0:
                return None
            return json.loads(result.stdout)
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
            return None

    def _keep_worker_alive(self, worker: AsyncWorker):
        """保持 worker 引用，防止被 GC 回收；完成後自動清除。"""
        self._async_workers = getattr(self, "_async_workers", [])
        self._async_workers.append(worker)
        worker.finished.connect(lambda: self._async_workers.remove(worker) if worker in self._async_workers else None)
        worker.error.connect(lambda: self._async_workers.remove(worker) if worker in self._async_workers else None)

    def detect_playlist_updates(
        self,
        playlist_url: str,
        download_path: str,
        prompt_user: bool = True,
        manual_trigger: bool = False,
        show_no_change_message: bool = True,
        offer_auto_download: bool = True,
        remember: bool = True,
    ) -> dict:
        """非同步版本 — 啟動背景取得 metadata，回傳 {"status": "async"}。"""
        if not playlist_url or not download_path:
            return {"status": "error"}

        self.log_to_overview(" 取得播放清單資訊中...")
        self.statusBar().showMessage("取得播放清單資訊中...")

        worker = AsyncWorker(self.fetch_playlist_metadata, playlist_url)

        def on_done(metadata):
            self.statusBar().clearMessage()
            self._process_playlist_detection(
                playlist_url,
                download_path,
                metadata,
                prompt_user=prompt_user,
                manual_trigger=manual_trigger,
                show_no_change_message=show_no_change_message,
                offer_auto_download=offer_auto_download,
                remember=remember,
            )
            # 如果是 offer_auto_download 流程，已在內部處理

        worker.finished.connect(on_done)
        worker.error.connect(lambda e: self.log_to_overview(f" 播放清單取得失敗: {e}"))
        self._keep_worker_alive(worker)
        worker.start()
        return {"status": "async"}

    def _process_playlist_detection(
        self,
        playlist_url: str,
        download_path: str,
        metadata: dict | None,
        prompt_user: bool = True,
        manual_trigger: bool = False,
        show_no_change_message: bool = True,
        offer_auto_download: bool = True,
        remember: bool = True,
    ) -> dict:
        """處理播放清單偵測邏輯（純 UI + 本地資料，在主執行緒呼叫）。"""
        if not metadata:
            return {"status": "error", "reason": "fetch-failed"}

        normalized_path = self.normalize_path(download_path)
        entries = metadata.get("entries") or []
        if not entries:
            return {"status": "error", "reason": "empty"}

        playlist_title = metadata.get("title", "")

        unavailable_titles = {"[deleted video]", "[private video]"}
        available_entries = [e for e in entries if (e.get("title") or "").strip().lower() not in unavailable_titles]

        playlist_id = metadata.get("id") or PlatformUtils.extract_playlist_id(playlist_url)
        current_ids = [e.get("id") or e.get("url") for e in available_entries if e.get("id") or e.get("url")]

        prev_state = self.playlist_states.get(normalized_path, {}).get(playlist_id, {})
        prev_ids = set(prev_state.get("video_ids", []))

        added_videos = [{"id": vid, "title": ""} for vid in current_ids if vid not in prev_ids]
        removed_ids = [vid for vid in prev_ids if vid not in current_ids]

        missing_videos = []
        for vid in current_ids:
            if vid in prev_ids and not self._has_local_file_for_video(normalized_path, vid):
                missing_videos.append({"id": vid, "title": ""})

        has_changes = bool(added_videos or removed_ids or missing_videos)

        title_prefix = f"【{playlist_title}】\n" if playlist_title else ""

        if not has_changes:
            if remember:
                self.update_playlist_state(
                    normalized_path, playlist_id, playlist_url, current_ids, playlist_title=playlist_title
                )
            if manual_trigger and show_no_change_message:
                QMessageBox.information(self, "偵測結果", f"{title_prefix}播放清單沒有新影片。")
            return {"status": "no-change", "video_ids": current_ids}

        msg_parts = []
        if added_videos:
            msg_parts.append(f"{len(added_videos)} 部新影片")
        if missing_videos:
            msg_parts.append(f"{len(missing_videos)} 部本地檔案缺失")
        summary = "、".join(msg_parts)

        if prompt_user:
            reply = QMessageBox.question(
                self,
                "播放清單有更新",
                f"{title_prefix}偵測到 {summary}，是否繼續?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return {"status": "cancel"}

        if remember:
            self.update_playlist_state(
                normalized_path, playlist_id, playlist_url, current_ids, playlist_title=playlist_title
            )

        if missing_videos:
            with self._history_lock:
                for vid_info in missing_videos:
                    vid = vid_info["id"]
                    if normalized_path in self.download_history and vid in self.download_history[normalized_path]:
                        del self.download_history[normalized_path][vid]
                if normalized_path in self.download_history and not self.download_history[normalized_path]:
                    del self.download_history[normalized_path]
                self.save_download_history()

        all_actionable = added_videos + missing_videos
        if offer_auto_download and all_actionable:
            auto_reply = QMessageBox.question(
                self,
                "自動下載",
                f"{title_prefix}偵測到 {summary}，是否立即下載?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if auto_reply == QMessageBox.StandardButton.Yes:
                self.auto_download_playlist(playlist_url, normalized_path)

        return {
            "status": "proceed" if not manual_trigger else "manual",
            "added_videos": added_videos,
            "missing_videos": missing_videos,
            "video_ids": current_ids,
        }

    def auto_download_playlist(self, playlist_url: str, download_path: str):
        settings = self.build_download_settings(download_path)
        if not settings:
            return

        def fetch_and_expand():
            metadata = self.fetch_playlist_metadata(playlist_url)
            if not metadata:
                return None
            entries = metadata.get("entries") or []
            unavailable_titles = {"[deleted video]", "[private video]"}
            video_ids = [
                e.get("id") or e.get("url")
                for e in entries
                if (e.get("id") or e.get("url")) and (e.get("title") or "").strip().lower() not in unavailable_titles
            ]
            return video_ids

        worker = AsyncWorker(fetch_and_expand)

        def on_done(video_ids):
            if video_ids:
                expanded, _ = self._expand_playlist_urls_from_ids(playlist_url, video_ids, download_path)
                urls = expanded if expanded else [playlist_url]
            else:
                urls = [playlist_url]
            task_id = len(self.workers) + 1
            self.create_task(task_id, urls, settings)

        worker.finished.connect(on_done)
        worker.error.connect(lambda e: self.log_to_overview(f" 播放清單展開失敗: {e}"))
        self._keep_worker_alive(worker)
        worker.start()

    def _expand_playlist_urls(
        self,
        playlist_url: str,
        video_ids: list[str] | None = None,
        download_path: str = "",
    ) -> tuple[list[str], int]:
        """將播放清單展開為個別影片 URL（可能阻塞，僅在背景執行緒使用）。"""
        if not video_ids:
            metadata = self.fetch_playlist_metadata(playlist_url)
            if not metadata:
                return [], 0
            entries = metadata.get("entries") or []
            unavailable_titles = {"[deleted video]", "[private video]"}
            video_ids = [
                e.get("id") or e.get("url")
                for e in entries
                if (e.get("id") or e.get("url")) and (e.get("title") or "").strip().lower() not in unavailable_titles
            ]

        return self._expand_playlist_urls_from_ids(playlist_url, video_ids, download_path)

    def _expand_playlist_urls_from_ids(
        self,
        playlist_url: str,
        video_ids: list[str],
        download_path: str = "",
    ) -> tuple[list[str], int]:
        """從已知 video_ids 展開為 URL 列表（純本地運算，不阻塞）。"""
        platform = PlatformUtils.detect_platform(playlist_url)
        normalized_path = self.normalize_path(download_path)
        expanded = []
        skipped = 0
        for vid in video_ids:
            if normalized_path and self.is_downloaded(normalized_path, vid):
                skipped += 1
                continue
            if platform == "bilibili":
                expanded.append(f"https://www.bilibili.com/video/{vid}")
            else:
                expanded.append(f"https://www.youtube.com/watch?v={vid}")
        return expanded, skipped

    def manual_check_playlist_updates(self):
        playlist_url = self.playlist_url_edit.text().strip()
        download_path = self.download_path_edit.text().strip()
        if not self.playlist_radio.isChecked():
            QMessageBox.information(self, "提示", "請先選擇播放清單模式並填入網址。")
            return
        self.detect_playlist_updates(
            playlist_url,
            download_path,
            prompt_user=True,
            manual_trigger=True,
            remember=self.remember_playlist_check.isChecked(),
        )

    def collect_known_playlists(self) -> list[dict[str, str]]:
        playlist_jobs = []
        for download_path, playlists in self.playlist_states.items():
            for playlist_id, info in playlists.items():
                url = info.get("playlist_url")
                if url:
                    playlist_jobs.append(
                        {
                            "download_path": download_path,
                            "playlist_id": playlist_id,
                            "playlist_url": url,
                            "playlist_title": info.get("playlist_title", ""),
                        }
                    )
        return playlist_jobs

    def check_all_playlists(self, manual_trigger: bool, show_no_change_message: bool):
        playlist_jobs = self.collect_known_playlists()
        if not playlist_jobs:
            if manual_trigger:
                QMessageBox.information(self, "播放清單檢查", "目前尚未建立任何播放清單記錄。")
            return

        self.log_to_overview(f" 開始批次檢查 {len(playlist_jobs)} 個播放清單...")
        self.statusBar().showMessage(f"批次檢查 {len(playlist_jobs)} 個播放清單中...")

        def fetch_all():
            results = []
            for job in playlist_jobs:
                metadata = self.fetch_playlist_metadata(job["playlist_url"])
                results.append((job, metadata))
            return results

        worker = AsyncWorker(fetch_all)

        def on_done(results):
            self.statusBar().clearMessage()
            updates_found = 0
            for job, metadata in results:
                job_title = job.get("playlist_title") or job["playlist_id"]
                self.log_to_overview(f"  處理中: {job_title}")
                result = self._process_playlist_detection(
                    job["playlist_url"],
                    job["download_path"],
                    metadata,
                    prompt_user=True,
                    manual_trigger=manual_trigger,
                    show_no_change_message=show_no_change_message,
                    remember=True,
                )
                if result.get("status") in ("proceed", "manual"):
                    updates_found += 1

            if manual_trigger:
                QMessageBox.information(
                    self, "播放清單檢查", f"批次檢查完成，共偵測到 {updates_found} 個播放清單有變動。"
                )

        worker.finished.connect(on_done)
        worker.error.connect(lambda e: self.log_to_overview(f" 批次檢查失敗: {e}"))
        self._keep_worker_alive(worker)
        worker.start()

    def manual_check_all_playlists(self):
        self.check_all_playlists(manual_trigger=True, show_no_change_message=False)

    def auto_check_all_playlists_on_start(self):
        """啟動時不自動檢查，避免阻塞 UI；使用者可手動點選檢查按鈕"""
        playlist_jobs = self.collect_known_playlists()
        if playlist_jobs:
            self.log_to_overview(f"📋 已載入 {len(playlist_jobs)} 個播放清單記錄，點選「檢查所有清單」可手動檢查更新")

    def create_task(self, task_id: int, urls: list[str], settings: dict):
        task_widget = QWidget()
        task_layout = QVBoxLayout(task_widget)

        info_label = QLabel(f"路徑: {settings['download_path']} | 項目: {len(urls)} 個")
        task_layout.addWidget(info_label)

        control_layout = QHBoxLayout()
        pause_btn = QPushButton(" 暫停")
        stop_btn = QPushButton(" 停止")
        control_layout.addWidget(pause_btn)
        control_layout.addWidget(stop_btn)
        control_layout.addStretch()
        task_layout.addLayout(control_layout)

        progress_bar = QProgressBar()
        progress_bar.setMaximum(len(urls))
        task_layout.addWidget(progress_bar)

        status_label = QLabel("等待開始...")
        task_layout.addWidget(status_label)

        progress_label = QLabel("")
        progress_label.setStyleSheet("color: #4CAF50; font-family: 'Consolas', monospace;")
        task_layout.addWidget(progress_label)

        log_text = QTextEdit()
        log_text.setReadOnly(True)
        log_text.setFont(QFont("Consolas", 9))
        task_layout.addWidget(log_text)

        self.task_tabs.addTab(task_widget, f"任務 {task_id}")
        self.task_tabs.setCurrentWidget(task_widget)

        worker = BatchDownloadWorker(task_id, urls, settings, main_window=self)
        worker.progress_update.connect(progress_bar.setValue)
        worker.status_change.connect(status_label.setText)
        worker.download_progress.connect(progress_label.setText)
        worker.log_message.connect(log_text.append)
        worker.log_message.connect(lambda msg: self.log_to_overview(f"[任務 {task_id}] {msg}"))
        worker.task_finished.connect(lambda stats: self.on_task_finished(task_id, stats))

        is_paused = False

        def toggle_pause():
            nonlocal is_paused
            if not is_paused:
                worker.pause()
                pause_btn.setText(" 恢復")
                is_paused = True
            else:
                worker.resume()
                pause_btn.setText(" 暫停")
                is_paused = False

        pause_btn.clicked.connect(toggle_pause)
        stop_btn.clicked.connect(worker.stop)

        self.workers.append(worker)
        worker.start()
        self.log_to_overview(f" 任務 {task_id} 已啟動")

    def close_task_tab(self, index: int):
        if index == 0:
            return
        self.task_tabs.removeTab(index)

    def on_task_finished(self, task_id: int, stats: dict):
        self.log_to_overview(f" 任務 {task_id} 完成")
        self.statusBar().showMessage(
            f"任務 {task_id} 完成 - 成功: {stats['success']}, 失敗: {stats['failed']}, 跳過: {stats['skipped']}"
        )
        QMessageBox.information(
            self,
            "任務完成",
            f"任務 {task_id} 已完成\n\n成功: {stats['success']}\n失敗: {stats['failed']}\n跳過: {stats['skipped']}",
        )

    def log_to_overview(self, message: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.overview_log.append(f"[{timestamp}] {message}")

    def check_dependencies(self):
        self.log_to_overview(" 檢查 yt-dlp / ffmpeg...")

        def check():
            bin_manager.check_and_update(log_cb=self.log_to_overview)

        threading.Thread(target=check, daemon=True).start()

    def show_help(self):
        help_text = f"""📺 影片批量下載工具 {APP_VERSION} - 使用說明

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 快速入門
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 選擇下載路徑 (Ctrl+O)
2. 輸入/貼上影片網址 (支援拖放)
3. 點擊「開始下載」(Ctrl+Enter)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⌨️ 鍵盤快捷鍵
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Ctrl+Enter    開始下載
• Ctrl+Shift+V  快速貼上 URL
• Ctrl+O        選擇下載路徑
• F1            顯示說明
• Ctrl+Q        退出程式

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 小技巧
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 可直接拖放 URL 或 .txt 檔案到視窗
• URL 會自動識別為單一影片或播放清單
• 滑鼠停留在選項上可查看詳細說明

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 常見問題
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Q: Cookie 提取失敗？
A: 請先在 Firefox 登入 YouTube/Bilibili，
   並關閉所有 Firefox 視窗後再試。

Q: 下載速度很慢？
A: 可能是網路問題或來源限制。

Q: 影片下載失敗？
A: 確認 URL 正確無誤，嘗試重新下載。
   會員影片需先提取 Cookie。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 支援平台: YouTube、Bilibili
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
        QMessageBox.information(self, "使用說明", help_text)

    def export_download_report(self):
        """匯出下載歷史報告"""
        if not self.download_history:
            QMessageBox.information(self, "提示", "目前沒有下載歷史記錄可匯出。")
            return

        # 讓使用者選擇格式和路徑
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "匯出下載報告",
            f"download_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "CSV 檔案 (*.csv);;HTML 檔案 (*.html)",
        )

        if not file_path:
            return

        try:
            if selected_filter == "CSV 檔案 (*.csv)" or file_path.endswith(".csv"):
                self._export_csv(file_path if file_path.endswith(".csv") else file_path + ".csv")
            else:
                self._export_html(file_path if file_path.endswith(".html") else file_path + ".html")

            self.log_to_overview(f"📊 報告已匯出: {file_path}")
            QMessageBox.information(self, "匯出成功", f"報告已匯出至:\n{file_path}")

        except OSError as e:
            self.log_to_overview(f"❌ 匯出失敗: {e}")
            QMessageBox.warning(self, "匯出失敗", f"無法匯出報告:\n{e}")

    def _export_csv(self, file_path: str):
        """匯出 CSV 格式報告"""
        import csv

        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["下載路徑", "影片 ID", "網址", "標題", "下載時間"])

            for path, videos in self.download_history.items():
                for video_id, info in videos.items():
                    writer.writerow(
                        [path, video_id, info.get("url", ""), info.get("title", ""), info.get("timestamp", "")]
                    )

    def _export_html(self, file_path: str):
        """匯出 HTML 格式報告"""
        total_count = sum(len(v) for v in self.download_history.values())

        html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>下載歷史報告</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #1e1e1e; color: #d4d4d4; }}
        h1 {{ color: #0e639c; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ padding: 10px; text-align: left; border: 1px solid #3c3c3c; }}
        th {{ background: #0e639c; color: white; }}
        tr:nth-child(even) {{ background: #2d2d30; }}
        tr:hover {{ background: #3c3c3c; }}
        a {{ color: #3794ff; }}
        .summary {{ background: #2d2d30; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h1>📊 下載歷史報告</h1>
    <div class="summary">
        <p>📅 產生時間: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p>📁 總路徑數: {len(self.download_history)}</p>
        <p>🎬 總影片數: {total_count}</p>
    </div>
    <table>
        <tr>
            <th>下載路徑</th>
            <th>影片 ID</th>
            <th>標題</th>
            <th>下載時間</th>
        </tr>
"""

        for path, videos in self.download_history.items():
            for video_id, info in videos.items():
                url = info.get("url", "")
                title = info.get("title", "") or video_id
                timestamp = info.get("timestamp", "")
                html_content += f"""        <tr>
            <td>{path}</td>
            <td><a href="{url}" target="_blank">{video_id}</a></td>
            <td>{title}</td>
            <td>{timestamp}</td>
        </tr>
"""

        html_content += """    </table>
</body>
</html>"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def load_download_history(self):
        try:
            if os.path.exists(self.download_history_file):
                with open(self.download_history_file, encoding="utf-8") as f:
                    self.download_history = json.load(f)
                self._normalize_download_history_keys()
                total = sum(len(v) for v in self.download_history.values())
                self.log_to_overview(f" 已載入下載歷史: {total} 個影片")
        except (OSError, json.JSONDecodeError) as e:
            self.download_history = {}
            self.log_to_overview(f" 載入下載歷史失敗: {e}")

    def load_playlist_states(self):
        try:
            if os.path.exists(self.playlist_state_file):
                with open(self.playlist_state_file, encoding="utf-8") as f:
                    self.playlist_states = json.load(f)
                self._normalize_playlist_state_keys()
        except (OSError, json.JSONDecodeError):
            self.playlist_states = {}

    def load_playlist_updates_log(self):
        try:
            if os.path.exists(self.playlist_updates_log_file):
                with open(self.playlist_updates_log_file, encoding="utf-8") as f:
                    self.playlist_updates_log = json.load(f)
        except (OSError, json.JSONDecodeError):
            self.playlist_updates_log = []

    def _normalize_download_history_keys(self):
        normalized = {}
        for path, videos in (self.download_history or {}).items():
            norm_path = self.normalize_path(path)
            if norm_path:
                normalized.setdefault(norm_path, {}).update(videos if isinstance(videos, dict) else {})
        self.download_history = normalized

    def _normalize_playlist_state_keys(self):
        normalized = {}
        for path, playlists in (self.playlist_states or {}).items():
            norm_path = self.normalize_path(path)
            if norm_path:
                normalized.setdefault(norm_path, {})
                for pid, info in (playlists if isinstance(playlists, dict) else {}).items():
                    normalized[norm_path][pid] = info
        self.playlist_states = normalized

    def save_download_history(self):
        try:
            with open(self.download_history_file, "w", encoding="utf-8") as f:
                json.dump(self.download_history, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def save_playlist_states(self):
        try:
            with open(self.playlist_state_file, "w", encoding="utf-8") as f:
                json.dump(self.playlist_states, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def update_playlist_state(
        self,
        download_path: str,
        playlist_id: str,
        playlist_url: str,
        video_ids: list[str],
        playlist_title: str = "",
    ):
        download_path = self.normalize_path(download_path)
        if not download_path or not playlist_id:
            return
        if download_path not in self.playlist_states:
            self.playlist_states[download_path] = {}
        state = {
            "playlist_url": playlist_url,
            "video_ids": video_ids,
            "last_checked": datetime.datetime.now().isoformat(),
        }
        if playlist_title:
            state["playlist_title"] = playlist_title
        self.playlist_states[download_path][playlist_id] = state
        self.save_playlist_states()

    def add_to_download_history(self, download_path: str, video_id: str, url: str, title: str = ""):
        download_path = self.normalize_path(download_path)
        with self._history_lock:
            if download_path not in self.download_history:
                self.download_history[download_path] = {}
            self.download_history[download_path][video_id] = {
                "url": url,
                "title": title,
                "timestamp": datetime.datetime.now().isoformat(),
            }
            self.save_download_history()

    def is_downloaded(self, download_path: str, video_id: str) -> bool:
        download_path = self.normalize_path(download_path)
        if self._has_local_file_for_video(download_path, video_id):
            return True
        with self._history_lock:
            if download_path in self.download_history and video_id in self.download_history[download_path]:
                # 歷史紀錄存在但本地檔案已被刪除，移除紀錄以允許重新下載
                del self.download_history[download_path][video_id]
                if not self.download_history[download_path]:
                    del self.download_history[download_path]
                self.save_download_history()
                return False
            return False

    def _has_local_file_for_video(self, download_path: str, video_id: str) -> bool:
        download_path = self.normalize_path(download_path)
        if not download_path or not os.path.isdir(download_path):
            return False
        video_id_clean = video_id.strip()
        try:
            for name in os.listdir(download_path):
                if not any(name.lower().endswith(ext) for ext in CONSTANTS.VIDEO_EXTENSIONS):
                    continue
                if name.endswith(CONSTANTS.IGNORE_SUFFIXES):
                    continue
                if f"[{video_id_clean}]" in name or video_id_clean in name:
                    return True
                bracket_match = PATTERNS.BRACKET_ID.search(name)
                if bracket_match:
                    file_id = bracket_match.group(1)
                    if file_id in video_id_clean or video_id_clean in file_id:
                        return True
                    if SequenceMatcher(None, file_id, video_id_clean).ratio() >= 0.75:
                        return True
        except OSError:
            pass
        return False

    def load_settings(self):
        self.download_path_edit.setText(self.settings.value("download_path", ""))
        self.subtitle_lang_edit.setText(self.settings.value("subtitle_lang", "zh-TW,zh,en"))
        quality = self.settings.value("quality", "best")
        idx = self.quality_combo.findText(quality)
        if idx >= 0:
            self.quality_combo.setCurrentIndex(idx)
        self.timeout_spin.setValue(int(self.settings.value("download_timeout", CONSTANTS.DEFAULT_TIMEOUT)))
        self.custom_filename_check.setChecked(
            str(self.settings.value("use_custom_filename", "false")).lower() == "true"
        )
        self.custom_filename_edit.setText(self.settings.value("custom_filename_template", "%(title)s [%(id)s]"))
        self.auto_trim_filename_check.setChecked(
            str(self.settings.value("auto_trim_filename", "true")).lower() == "true"
        )
        self.trim_filename_spin.setValue(int(self.settings.value("trim_filename_length", 120)))
        self.trim_filename_spin.setEnabled(self.auto_trim_filename_check.isChecked())
        self.remember_playlist_check.setChecked(str(self.settings.value("remember_playlist", "true")).lower() == "true")

    def save_settings(self):
        self.settings.setValue("download_path", self.download_path_edit.text())
        self.settings.setValue("quality", self.quality_combo.currentText())
        self.settings.setValue("subtitle_lang", self.subtitle_lang_edit.text())
        self.settings.setValue("download_timeout", self.timeout_spin.value())
        self.settings.setValue("use_custom_filename", self.custom_filename_check.isChecked())
        self.settings.setValue("custom_filename_template", self.custom_filename_edit.text())
        self.settings.setValue("auto_trim_filename", self.auto_trim_filename_check.isChecked())
        self.settings.setValue("trim_filename_length", self.trim_filename_spin.value())
        self.settings.setValue("remember_playlist", self.remember_playlist_check.isChecked())

    def closeEvent(self, event):
        for worker in self.workers:
            if worker.isRunning():
                worker.stop()
                worker.wait(1000)
        self.save_settings()
        self.save_download_history()
        self.save_playlist_states()
        self.cleanup_cookies()
        event.accept()

    def cleanup_cookies(self):
        try:
            for pattern in ["youtube_cookies_*.txt", "bilibili_cookies_*.txt"]:
                for cookie_file in glob.glob(pattern):
                    try:
                        os.remove(cookie_file)
                    except OSError:
                        pass
        except OSError:
            pass


# ==================== 主程式進入點 ====================
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("影片批量下載工具")
    app.setOrganizationName("VideoDownloader")
    app.setApplicationVersion(APP_VERSION)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

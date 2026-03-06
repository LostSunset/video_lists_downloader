"""
管理 yt-dlp 和 ffmpeg 的下載與更新。
將可執行檔存放在專案目錄下的 bin/ 資料夾。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

# bin 目錄位於專案根目錄下
BIN_DIR = Path(__file__).parent / "bin"
YTDLP_EXE = BIN_DIR / "yt-dlp.exe"
FFMPEG_DIR = BIN_DIR / "ffmpeg"
FFMPEG_EXE = FFMPEG_DIR / "ffmpeg.exe"
FFPROBE_EXE = FFMPEG_DIR / "ffprobe.exe"
VERSION_FILE = BIN_DIR / "versions.json"

YTDLP_RELEASE_URL = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
YTDLP_DOWNLOAD_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
FFMPEG_RELEASE_URL = "https://api.github.com/repos/BtbN/FFmpeg-Builds/releases/latest"


def _read_versions() -> dict:
    if VERSION_FILE.exists():
        return json.loads(VERSION_FILE.read_text(encoding="utf-8"))
    return {}


def _write_versions(data: dict):
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    VERSION_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _api_get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "video-downloader"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _download_file(url: str, dest: Path, progress_cb=None):
    """下載檔案，支援進度回呼 progress_cb(downloaded_bytes, total_bytes)"""
    req = urllib.request.Request(url, headers={"User-Agent": "video-downloader"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        dest.parent.mkdir(parents=True, exist_ok=True)
        downloaded = 0
        with open(dest, "wb") as f:
            while True:
                chunk = resp.read(1024 * 256)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if progress_cb:
                    progress_cb(downloaded, total)


def get_ytdlp_path() -> str:
    """回傳 yt-dlp 執行檔路徑。若本地 bin 存在就用，否則 fallback 到系統 PATH。"""
    if YTDLP_EXE.exists():
        return str(YTDLP_EXE)
    return "yt-dlp"


def get_ffmpeg_dir() -> str:
    """回傳 ffmpeg 所在目錄路徑（供 yt-dlp --ffmpeg-location 使用）。"""
    if FFMPEG_EXE.exists():
        return str(FFMPEG_DIR)
    return ""


def get_latest_ytdlp_version() -> str:
    """查詢 GitHub 上最新的 yt-dlp 版本號。"""
    data = _api_get_json(YTDLP_RELEASE_URL)
    return data.get("tag_name", "")


def get_local_ytdlp_version() -> str:
    """取得本地 yt-dlp 版本號。"""
    path = get_ytdlp_path()
    if path == "yt-dlp" and not shutil.which("yt-dlp"):
        return ""
    try:
        result = subprocess.run(
            [path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def download_ytdlp(progress_cb=None) -> str:
    """下載最新 yt-dlp.exe，回傳版本號。"""
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    _download_file(YTDLP_DOWNLOAD_URL, YTDLP_EXE, progress_cb)

    # 取得實際版本
    try:
        result = subprocess.run(
            [str(YTDLP_EXE), "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        version = result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        version = "unknown"

    versions = _read_versions()
    versions["yt-dlp"] = version
    _write_versions(versions)
    return version


def download_ffmpeg(progress_cb=None) -> str:
    """下載最新 ffmpeg（BtbN builds），回傳版本號。"""
    BIN_DIR.mkdir(parents=True, exist_ok=True)

    # 從 GitHub API 找到 win64-gpl 的 zip 資產
    data = _api_get_json(FFMPEG_RELEASE_URL)
    tag = data.get("tag_name", "unknown")
    asset_url = ""
    for asset in data.get("assets", []):
        name = asset["name"]
        if "win64" in name and "gpl" in name and name.endswith(".zip") and "shared" not in name:
            asset_url = asset["browser_download_url"]
            break

    if not asset_url:
        raise RuntimeError("找不到適合的 ffmpeg 下載連結")

    # 下載 zip 到暫存
    zip_path = BIN_DIR / "ffmpeg_tmp.zip"
    _download_file(asset_url, zip_path, progress_cb)

    # 解壓縮，只取 bin/ 下的 exe
    FFMPEG_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            basename = os.path.basename(info.filename)
            if basename in ("ffmpeg.exe", "ffprobe.exe"):
                with zf.open(info) as src, open(FFMPEG_DIR / basename, "wb") as dst:
                    shutil.copyfileobj(src, dst)

    zip_path.unlink(missing_ok=True)

    if not FFMPEG_EXE.exists():
        raise RuntimeError("解壓縮後找不到 ffmpeg.exe")

    versions = _read_versions()
    versions["ffmpeg"] = tag
    _write_versions(versions)
    return tag


def check_and_update(log_cb=None, progress_cb=None) -> dict:
    """
    檢查並更新 yt-dlp 和 ffmpeg。
    log_cb(message): 日誌回呼
    progress_cb(tool_name, downloaded, total): 進度回呼
    回傳 {"yt-dlp": version, "ffmpeg": version}
    """

    def log(msg):
        if log_cb:
            log_cb(msg)

    result = {}

    # --- yt-dlp ---
    log("檢查 yt-dlp 更新...")
    try:
        latest = get_latest_ytdlp_version()
        local = get_local_ytdlp_version()
        if local and local == latest:
            log(f"yt-dlp 已是最新版 ({local})")
            result["yt-dlp"] = local
        else:
            log(f"下載 yt-dlp {latest}..." + (f" (目前: {local})" if local else ""))
            ver = download_ytdlp(progress_cb=lambda d, t: progress_cb("yt-dlp", d, t) if progress_cb else None)
            log(f"yt-dlp 更新完成: {ver}")
            result["yt-dlp"] = ver
    except Exception as e:
        log(f"yt-dlp 更新失敗: {e}")
        result["yt-dlp"] = get_local_ytdlp_version() or "error"

    # --- ffmpeg ---
    log("檢查 ffmpeg...")
    if FFMPEG_EXE.exists():
        versions = _read_versions()
        log(f"ffmpeg 已存在 ({versions.get('ffmpeg', 'unknown')})")
        result["ffmpeg"] = versions.get("ffmpeg", "exists")
    else:
        log("下載 ffmpeg...")
        try:
            ver = download_ffmpeg(progress_cb=lambda d, t: progress_cb("ffmpeg", d, t) if progress_cb else None)
            log(f"ffmpeg 下載完成: {ver}")
            result["ffmpeg"] = ver
        except Exception as e:
            log(f"ffmpeg 下載失敗: {e}")
            result["ffmpeg"] = "error"

    return result

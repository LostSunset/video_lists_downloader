"""
管理 yt-dlp、ffmpeg 和 Node.js 的下載與更新。
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
NODEJS_DIR = BIN_DIR  # node.exe 放在 bin/ 根目錄，讓 yt-dlp.exe 能自動偵測到
NODEJS_EXE = BIN_DIR / "node.exe"
VERSION_FILE = BIN_DIR / "versions.json"

YTDLP_RELEASE_URL = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
YTDLP_DOWNLOAD_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
FFMPEG_RELEASE_URL = "https://api.github.com/repos/BtbN/FFmpeg-Builds/releases/latest"
NODEJS_RELEASE_URL = "https://nodejs.org/dist/index.json"


def _read_versions() -> dict:
    if VERSION_FILE.exists():
        return json.loads(VERSION_FILE.read_text(encoding="utf-8"))
    return {}


def _write_versions(data: dict):
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    VERSION_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _api_get_json(url: str) -> dict | list:
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


def get_nodejs_dir() -> str:
    """回傳 Node.js 所在目錄（供 PATH 注入使用）。"""
    if NODEJS_EXE.exists():
        return str(NODEJS_DIR)
    return ""


def get_ytdlp_env() -> dict:
    """取得執行 yt-dlp 時的環境變數，將 Node.js 加入 PATH。"""
    env = os.environ.copy()
    nodejs_dir = get_nodejs_dir()
    if nodejs_dir:
        env["PATH"] = nodejs_dir + os.pathsep + env.get("PATH", "")
    return env


def get_base_ytdlp_cmd() -> list[str]:
    """回傳 yt-dlp 基礎指令列表，包含 JS runtime 和 ffmpeg 設定。"""
    cmd = [get_ytdlp_path()]
    # 啟用 Node.js runtime 供 YouTube n-challenge solver 使用
    if NODEJS_EXE.exists() or shutil.which("node"):
        node_path = str(NODEJS_EXE) if NODEJS_EXE.exists() else ""
        if node_path:
            cmd.extend(["--js-runtimes", f"node:{node_path}"])
        else:
            cmd.extend(["--js-runtimes", "node"])
    cmd.extend(["--remote-components", "ejs:github"])
    ffmpeg_dir = get_ffmpeg_dir()
    if ffmpeg_dir:
        cmd.extend(["--ffmpeg-location", ffmpeg_dir])
    return cmd


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

    zip_path = BIN_DIR / "ffmpeg_tmp.zip"
    _download_file(asset_url, zip_path, progress_cb)

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


def download_nodejs(progress_cb=None) -> str:
    """下載 Node.js LTS（win-x64），供 yt-dlp 解算 YouTube n-challenge 使用。"""
    BIN_DIR.mkdir(parents=True, exist_ok=True)

    # 從 nodejs.org 取得最新 LTS 版本
    releases = _api_get_json(NODEJS_RELEASE_URL)
    lts_version = ""
    for rel in releases:
        if rel.get("lts"):
            lts_version = rel["version"]  # e.g. "v22.14.0"
            break

    if not lts_version:
        raise RuntimeError("找不到 Node.js LTS 版本")

    # 下載 win-x64 zip
    zip_name = f"node-{lts_version}-win-x64.zip"
    zip_url = f"https://nodejs.org/dist/{lts_version}/{zip_name}"

    zip_path = BIN_DIR / "node_tmp.zip"
    _download_file(zip_url, zip_path, progress_cb)

    # 解壓縮，只取 node.exe
    NODEJS_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            basename = os.path.basename(info.filename)
            if basename == "node.exe":
                with zf.open(info) as src, open(NODEJS_DIR / basename, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                break

    zip_path.unlink(missing_ok=True)

    if not NODEJS_EXE.exists():
        raise RuntimeError("解壓縮後找不到 node.exe")

    versions = _read_versions()
    versions["node"] = lts_version
    _write_versions(versions)
    return lts_version


def check_and_update(log_cb=None, progress_cb=None) -> dict:
    """
    檢查並更新 yt-dlp、ffmpeg 和 Node.js。
    log_cb(message): 日誌回呼
    progress_cb(tool_name, downloaded, total): 進度回呼
    回傳 {"yt-dlp": version, "ffmpeg": version, "node": version}
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

    # --- Node.js (yt-dlp n-challenge solver 需要) ---
    log("檢查 Node.js...")
    if NODEJS_EXE.exists():
        versions = _read_versions()
        log(f"Node.js 已存在 ({versions.get('node', 'unknown')})")
        result["node"] = versions.get("node", "exists")
    else:
        # 也檢查系統 PATH 是否已有 node
        if shutil.which("node"):
            log("Node.js 已在系統 PATH 中")
            result["node"] = "system"
        else:
            log("下載 Node.js (yt-dlp n-challenge 解碼需要)...")
            try:
                ver = download_nodejs(progress_cb=lambda d, t: progress_cb("node", d, t) if progress_cb else None)
                log(f"Node.js 下載完成: {ver}")
                result["node"] = ver
            except Exception as e:
                log(f"Node.js 下載失敗: {e}")
                result["node"] = "error"

    return result

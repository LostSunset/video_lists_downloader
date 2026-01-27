# Video Lists Downloader

[![CI](https://github.com/LostSunset/video_lists_downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/LostSunset/video_lists_downloader/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/LostSunset/video_lists_downloader?style=social)](https://github.com/LostSunset/video_lists_downloader/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/LostSunset/video_lists_downloader?style=social)](https://github.com/LostSunset/video_lists_downloader/network/members)
[![GitHub issues](https://img.shields.io/github/issues/LostSunset/video_lists_downloader)](https://github.com/LostSunset/video_lists_downloader/issues)

影片批量下載工具 - 支援 YouTube 與 Bilibili 平台

[English](#english) | [中文](#中文)

---

## 中文

### 功能特色

- 🎬 支援 YouTube 和 Bilibili 影片/播放清單下載
- 📊 下載進度追蹤與歷史記錄
- 🎨 深色/淺色主題切換
- 🔔 系統托盤與下載完成通知
- ⚡ 下載速度限制功能
- 🔄 自動重試機制
- 📈 下載統計功能
- 💾 設定匯出/匯入功能

### 截圖

<!-- TODO: 添加應用程式截圖 -->
<!-- ![主介面](docs/images/main.png) -->

### 環境需求

- Python 3.10+
- PySide6
- yt-dlp (用於下載)
- ffmpeg (用於合併影片，可選)

### 安裝

```bash
# 使用 pip
pip install PySide6 yt-dlp

# 或使用 uv (推薦)
uv sync
```

### 使用方式

```bash
python video_downloader.py
```

### 開發

```bash
# 安裝開發依賴
pip install -e ".[dev]"

# 執行測試
pytest

# 程式碼檢查
ruff check .
```

---

## English

### Features

- 🎬 Support YouTube and Bilibili video/playlist downloads
- 📊 Download progress tracking and history
- 🎨 Dark/Light theme switching
- 🔔 System tray and download completion notifications
- ⚡ Download speed limit
- 🔄 Auto-retry mechanism
- 📈 Download statistics
- 💾 Settings export/import

### Requirements

- Python 3.10+
- PySide6
- yt-dlp (for downloading)
- ffmpeg (for merging, optional)

### Installation

```bash
# Using pip
pip install PySide6 yt-dlp

# Or using uv (recommended)
uv sync
```

### Usage

```bash
python video_downloader.py
```

### Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .
```

---

## 版本歷史 | Changelog

See [CHANGELOG.md](CHANGELOG.md) for full history.

### v0.2.0 (2026-01-26)
- 新增下載速度限制、自動重試、系統托盤、主題切換等功能
- 從 PyQt6 遷移到 PySide6

## 貢獻 | Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## 授權 | License

[MIT License](LICENSE)

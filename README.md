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

### 🚀 快速入門

```bash
# 1. 安裝 (使用 uv 推薦)
uv sync
# 或 pip install PySide6 yt-dlp

# 2. 執行
python video_downloader.py
```

**三步驟開始下載：**
1. 選擇下載路徑 (`Ctrl+O`)
2. 貼上影片網址（支援拖放！）
3. 開始下載 (`Ctrl+Enter`)

### 功能特色

- 🎬 支援 YouTube 和 Bilibili 影片/播放清單下載
- 📊 下載進度追蹤與歷史記錄
- ⌨️ 鍵盤快捷鍵與拖放支援
- 🍪 Cookie 狀態指示（🟢有效 🟡未驗證 🔴無效）
- 🔄 自動重試機制
- 💡 完整的 Tooltip 說明

### ⌨️ 鍵盤快捷鍵

| 快捷鍵 | 功能 |
|--------|------|
| `Ctrl+Enter` | 開始下載 |
| `Ctrl+Shift+V` | 快速貼上 URL |
| `Ctrl+O` | 選擇下載路徑 |
| `F1` | 顯示說明 |
| `Ctrl+Q` | 退出程式 |

### 📖 文件

- [快速入門指南](docs/quick_start.md)
- [完整使用說明](docs/user_guide.md)
- [常見問題 (FAQ)](docs/faq.md)
- [疑難排解](docs/troubleshooting.md)

### 環境需求

- Python 3.10+
- PySide6
- yt-dlp (用於下載)
- ffmpeg (用於合併影片，可選)

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

### 🚀 Quick Start

```bash
# 1. Install (uv recommended)
uv sync
# or: pip install PySide6 yt-dlp

# 2. Run
python video_downloader.py
```

**Three steps to start downloading:**
1. Select download path (`Ctrl+O`)
2. Paste video URL (drag & drop supported!)
3. Start download (`Ctrl+Enter`)

### Features

- 🎬 YouTube and Bilibili video/playlist downloads
- 📊 Download progress tracking and history
- ⌨️ Keyboard shortcuts and drag-drop support
- 🍪 Cookie status indicators (🟢valid 🟡unverified 🔴invalid)
- 🔄 Auto-retry mechanism
- 💡 Comprehensive tooltips

### ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Start download |
| `Ctrl+Shift+V` | Quick paste URL |
| `Ctrl+O` | Select download path |
| `F1` | Show help |
| `Ctrl+Q` | Quit |

### 📖 Documentation

- [Quick Start Guide](docs/quick_start.md)
- [User Guide](docs/user_guide.md)
- [FAQ](docs/faq.md)
- [Troubleshooting](docs/troubleshooting.md)

### Requirements

- Python 3.10+
- PySide6
- yt-dlp (for downloading)
- ffmpeg (for merging, optional)

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

### v0.4.5 (2026-02-06)
- 🐛 修正 YouTube n-challenge 仍然失敗的問題：加入 `--remote-components ejs:github` 下載遠端 challenge solver 腳本
- 🔧 TV player variant + remote EJS solver 雙重修正，徹底解決 `Requested format is not available` 錯誤

### v0.4.4 (2026-02-06)
- 🐛 修正 YouTube n-challenge 解碼失敗導致 `Requested format is not available` 錯誤
- 🔧 YouTube 下載自動使用 `player_js_variant=tv` 繞過 player 4e51e895 的 EJS 相容性問題

### v0.4.3 (2026-02-06)
- 🐛 修正 Cookie 檔案不存在時自動 fallback 到 `--cookies-from-browser firefox`，解決 403 錯誤
- 🐛 下載失敗後自動清理 `.part`、`.ytdl`、`.temp` 等不完整檔案

### v0.4.2 (2026-02-06)
- 🐛 播放清單檢查自動排除被作者刪除/私人化的影片
- 🐛 修正播放清單部分影片失敗導致整個任務標記為失敗的問題
- 🔧 yt-dlp 的 ERROR/WARNING 訊息現在會顯示在日誌中

### v0.4.1 (2026-02-06)
- 🐛 修正播放清單檢查無法偵測本地檔案缺失的問題
- 🐛 檢查時自動掃描已知影片的本地檔案，缺失時清除歷史紀錄並提示重新下載

### v0.4.0 (2026-02-06)
- 🔧 例外處理改善：17 處 bare `except Exception:` 替換為具體例外類型
- 🔧 Cookie 提取程式碼重構，消除 ~40 行重複
- 🔧 新增執行緒安全機制（threading.Lock）防止競態條件
- 🐛 修正已刪除影片在播放清單檢查時不會重新下載的問題
- 🧪 測試擴充：從 9 個增加到 80 個單元測試

### v0.3.0 (2026-01-28)
- 🆕 鍵盤快捷鍵支援 (Ctrl+Enter, Ctrl+Shift+V, F1, Ctrl+O, Ctrl+Q)
- 🆕 拖放 URL 與檔案支援
- 🆕 自動 URL 類型偵測
- 🆕 Cookie 狀態指示燈 (🟢🟡🔴)
- 🆕 所有設定選項 Tooltip 說明
- 🆕 完整文件：快速入門、FAQ、疑難排解、使用指南
- 🆕 增強說明對話框

### v0.2.0 (2026-01-26)
- 新增下載速度限制、自動重試、系統托盤、主題切換等功能
- 從 PyQt6 遷移到 PySide6

## 貢獻 | Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=LostSunset/video_lists_downloader&type=Date)](https://star-history.com/#LostSunset/video_lists_downloader&Date)

## 授權 | License

[MIT License](LICENSE)


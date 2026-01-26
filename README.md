# Video Lists Downloader

影片批量下載工具 - 支援 YouTube 與 Bilibili 平台

## 功能特色

- 🎬 支援 YouTube 和 Bilibili 影片/播放清單下載
- 📊 下載進度追蹤與歷史記錄
- 🎨 深色/淺色主題切換
- 🔔 系統托盤與下載完成通知
- ⚡ 下載速度限制功能
- 🔄 自動重試機制
- 📈 下載統計功能
- 💾 設定匯出/匯入功能

## 環境需求

- Python 3.8+
- PySide6
- yt-dlp (用於下載)
- ffmpeg (用於合併影片)

## 安裝

```bash
pip install PySide6 yt-dlp
```

## 使用方式

```bash
python video_downloader_pyside6_v0.2.0.py
```

## 版本歷史

### v0.2.0 (2026-01-26)
- 移除未使用的 import 與空類別
- 預編譯正規表達式提升效能
- 新增下載速度限制功能
- 新增自動重試機制
- 新增系統托盤支援
- 新增下載完成通知
- 新增深色/淺色主題切換
- 新增下載統計功能
- 新增設定匯出/匯入功能

## 授權

MIT License

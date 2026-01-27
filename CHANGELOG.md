# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-01-27

### Added
- GitHub Actions CI/CD 自動測試和發布
- pytest 單元測試框架
- MIT LICENSE 授權檔案
- CONTRIBUTING.md 貢獻指南
- CHANGELOG.md 變更日誌
- 雙語 README（中文/英文）

### Changed
- 主程式重命名為 `video_downloader.py`
- 改進專案結構和文件
- 修復測試以匹配實際程式碼結構

## [0.2.0] - 2026-01-26

### Added
- 下載速度限制功能
- 自動重試機制
- 系統托盤支援
- 下載完成通知
- 深色/淺色主題切換
- 下載統計功能
- 設定匯出/匯入功能

### Changed
- 從 PyQt6 遷移到 PySide6
- 預編譯正規表達式提升效能

### Removed
- 移除未使用的 import 與空類別

## [0.1.9] - 2026-01-20

### Added
- Bilibili 平台支援
- 播放清單批量下載

## [0.1.0] - 2026-01-01

### Added
- 初始版本
- YouTube 影片下載
- 基本 GUI 介面

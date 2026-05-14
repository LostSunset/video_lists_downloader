# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.10.0] - 2026-05-14

### Added
- 新增「已記住播放清單」管理 UI，可查看已追蹤清單、載入清單、單獨檢查、開啟下載資料夾與移除追蹤記錄。
- 「檢查所有播放清單」新增進度列、目前檢查項目與取消檢查按鈕。
- 新增 helper 與回歸測試覆蓋已記住清單整理、移除、批次 metadata 抓取進度與取消摘要。

### Changed
- 批次檢查所有清單改用 `PlaylistBatchCheckWorker`，支援 cooperative cancellation 與逐項進度更新。
- 取消批次檢查時，尚未處理的清單會以 `cancel` 狀態進入彙總摘要。

## [0.9.3] - 2026-05-14

### Fixed
- 實際下載使用 Firefox/browser cookie 失敗時，會自動改用無 cookie 指令重試。
- 平台單選 UI 現在會傳入下載 worker，手動選擇 YouTube 或 Bilibili 時不再被 URL 自動偵測覆蓋。
- 批次檢查所有清單時，不再用目前 UI 路徑逐一觸發舊清單的路徑變更提示。
- 播放清單路徑遷移現在只搬移指定 playlist 與對應下載歷史，避免誤搬同路徑其他清單。
- HTML 匯出報告會 escape 路徑、標題與網址，避免特殊字元破版或插入 HTML。

### Changed
- `download_history.json` 與 `playlist_state.json` 改用 atomic write，降低中斷時寫壞狀態檔的風險。
- 批次檢查所有清單改為彙總結果訊息，減少逐一彈窗造成的操作干擾。
- 新增回歸測試覆蓋 cookie fallback、平台選擇、批次檢查摘要、路徑遷移、atomic JSON 與 HTML escaping。

## [0.9.2] - 2026-05-14

### Added
- 新增 `docs/developer_log.md`，建立 Codex/Claude Code 共用開發日誌規則。
- 新增 `docs/sessions/` SESSION 範本與本次維護紀錄。
- 新增 `docs/research_log.md`，記錄研究目標、流程決策與驗證方式。

### Changed
- 同步 `AGENTS.md` 與 `CLAUDE.md`，加入 repository identity、branch protection policy、automatic push rules、versioning rules 與 log/session 規範。
- 更新 `.agent/workflows/release.md`，將版本判斷、文件更新、開發日誌、SESSION、研究日誌與 branch protection 驗證納入 release workflow。
- 將 README 開發指令調整為 `uv` 工作流。
- 將 `uv.lock` 的本機 package 版本對齊 `0.9.2`。

## [0.9.1] - 2026-03-24

### Fixed
- 修正批次檢查時路徑變更對話框不出現的問題。
- 修正 cookie 不可用時播放清單偵測全部失敗的問題。
- 修正批次檢查未比較儲存路徑與 UI 路徑的問題。

### Changed
- 提取 `_migrate_playlist_path` 共用方法，統一路徑遷移邏輯。

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

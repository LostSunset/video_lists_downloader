# SESSION: 2026-05-14-playlist-reliability-fixes

## 基本資訊

- 日期：2026-05-14
- 作者/工具：Codex
- 關聯版本：v0.9.3
- 關聯 issue/PR：N/A

## 目標

- 分析並修正播放清單批次檢查、cookie fallback、平台選擇與狀態儲存中最影響使用者體驗的問題。

## 操作摘要

- 新增 TDD 回歸測試，先覆蓋已知問題與安全邊界。
- 實際下載 browser cookie 失敗時會自動無 cookie 重試。
- 平台單選設定會傳入下載 worker，手動選擇優先於 URL 自動偵測。
- 批次檢查所有清單改為彙總結果，避免每個清單逐一彈出路徑提示。
- 播放清單路徑遷移只搬移指定 playlist 與對應下載歷史。
- HTML 報告 escape 使用者資料，狀態 JSON 改用 atomic write。

## 變更檔案

- `video_downloader.py`
- `tests/test_video_downloader.py`
- `pyproject.toml`
- `uv.lock`
- `README.md`
- `CHANGELOG.md`
- `docs/developer_log.md`
- `docs/research_log.md`
- `docs/sessions/2026-05-14-playlist-reliability-fixes.md`

## 驗證

- `uv run ruff check .`
- `uv run python -m py_compile video_downloader.py bin_manager.py`
- `uv run pytest -q`，89 tests passed

## 後續事項

- 補上已記住播放清單管理 UI。
- 補上批次檢查進度顯示與取消控制。

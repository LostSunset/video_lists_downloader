# SESSION: 2026-05-14-playlist-management-ui

## 基本資訊

- 日期：2026-05-14
- 作者/工具：Codex
- 關聯版本：v0.10.0
- 關聯 issue/PR：N/A

## 目標

- 實作已記住播放清單管理 UI。
- 讓批次檢查所有清單可以顯示進度並支援取消。
- 完成測試、版本更新、commit、tag 與 push。

## 操作摘要

- 新增已記住播放清單 helper，整理清單顯示資料並支援移除追蹤記錄。
- 在左側面板新增「已記住播放清單」列表，提供載入、檢查、開啟資料夾、移除與重新整理。
- 新增 `PlaylistBatchCheckWorker`，讓批次檢查可以逐項回報進度並 cooperative cancel。
- 批次取消後，尚未處理的清單會以 `cancel` 狀態納入彙總摘要。
- 新增 4 個回歸測試覆蓋管理清單與批次取消行為。

## 變更檔案

- `video_downloader.py`
- `tests/test_video_downloader.py`
- `pyproject.toml`
- `uv.lock`
- `README.md`
- `CHANGELOG.md`
- `docs/developer_log.md`
- `docs/research_log.md`
- `docs/sessions/2026-05-14-playlist-management-ui.md`

## 驗證

- `uv run ruff check .`
- `uv run python -m py_compile video_downloader.py bin_manager.py`
- `uv run pytest -q`，93 tests passed
- PySide offscreen UI smoke check

## 後續事項

- 任務分頁關閉時可提示 worker 仍在執行。
- 下載完成彈窗可改為較不干擾的通知策略。

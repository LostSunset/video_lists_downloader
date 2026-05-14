# 開發者日誌 | Developer Log

本檔記錄專案層級的重要開發決策、版本變更、發布操作與維護規則。Claude Code、Codex 與其他開發者都應依照本檔格式補充日誌。

## 日誌規則

- 每次準備 commit 或 push 前，檢查本檔是否需要新增紀錄。
- 每筆紀錄使用 `YYYY-MM-DD` 日期、版本號、作者/工具、摘要、驗證結果與後續事項。
- 功能、修復、流程、文件、發布與研究目標變更都要記錄。
- 若本次工作有獨立脈絡，另於 `docs/sessions/` 新增 SESSION 檔。
- 若本次工作涉及調研、目標拆解或技術比較，同步更新 `docs/research_log.md`。
- 不記錄 token、金鑰、cookie、個人存取權杖或任何敏感資料。

## 版本紀錄

### 2026-05-14 - v0.9.2

- 作者/工具：Codex
- 類型：chore / docs
- 摘要：
  - 將本機資料夾初始化為 Git repository，並接上 `https://github.com/LostSunset/video_lists_downloader.git`。
  - 新增 Codex/Claude 共用開發日誌規則。
  - 新增 SESSION 範本與研究日誌，讓後續自動推送流程能追蹤決策脈絡。
  - 同步 `AGENTS.md` 與 `CLAUDE.md` 的工作規則。
- 驗證：
  - `uv run ruff check .` 通過。
  - `uv run python -m py_compile video_downloader.py bin_manager.py` 通過。
  - `uv run pytest -v` 通過，80 tests passed。
  - GitHub `main` branch protection 已啟用，required reviews = 1，enforce admins = false。
- 後續事項：
  - 若 repository 需要改為 private，需由 owner 明確確認後再修改 visibility。

# 研究目標與日誌 | Research Goals and Log

本檔記錄專案研究目標、技術取捨與尚待驗證的假設。當版本變更涉及架構、相依套件、下載策略、平台相容性或發布流程時，請同步更新。

## 使用規則

- 每個研究項目需包含目標、背景、目前結論、驗證方式與狀態。
- 若研究結果造成程式、文件或流程變更，於 `docs/developer_log.md` 加上對應版本紀錄。
- 若研究是在單次工作 session 中完成，也應於 `docs/sessions/` 留下 SESSION 紀錄。

## 目前研究目標

### R-2026-05-14-001 - 維護流程與分支保護

- 狀態：完成
- 目標：建立 Codex、Claude Code 與其他開發者都能遵守的共用維護流程。
- 背景：專案需要自動推送規則、版本判斷、文件更新規範、開發者日誌與 GitHub 分支保護。
- 目前結論：
  - `AGENTS.md` 與 `CLAUDE.md` 應保持同步，分別供 Codex 與 Claude Code 讀取。
  - 每次 push 必須依 Semantic Versioning 判斷是否 bump version。
  - `main` 應啟用 branch protection；admin/owner 可直接 push，其他開發者走 PR。
- 驗證方式：
  - 本機 lint/test 通過。
  - GitHub `main` branch protection API 回傳設定。
  - 遠端 commit、tag 與 release workflow 正常建立。
- 驗證結果：
  - `uv run ruff check .` 通過。
  - `uv run python -m py_compile video_downloader.py bin_manager.py` 通過。
  - `uv run pytest -v` 通過，80 tests passed。
  - `main` protected = true。
  - required approving reviews = 1。
  - enforce admins = false。

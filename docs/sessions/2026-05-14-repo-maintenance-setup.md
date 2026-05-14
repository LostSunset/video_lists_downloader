# SESSION: 2026-05-14-repo-maintenance-setup

## 基本資訊

- 日期：2026-05-14
- 作者/工具：Codex
- 關聯版本：v0.9.2
- 關聯 issue/PR：直接維護 main

## 目標

- 將目前本機資料夾初始化為 Git repository，並連接遠端 `LostSunset/video_lists_downloader`。
- 建立 Codex/Claude Code 共用的開發者日誌、SESSION 與研究日誌規則。
- 依專案規則 bump patch version 後直接推送。
- 設定 GitHub `main` 分支保護，讓非 admin 開發者必須透過 PR。

## 操作摘要

- 初始化 `.git` 並設定 `origin`。
- 以 `origin/main` 作為 index 基準，避免誤刪遠端既有 workflow。
- 保留遠端 `.agent/`、`.github/` 與 `.gitignore`。
- 新增維護文件並同步 `AGENTS.md`、`CLAUDE.md`。

## 驗證

- `uv run ruff check .` 通過。
- `uv run python -m py_compile video_downloader.py bin_manager.py` 通過。
- `uv run pytest -v` 通過，80 tests passed。
- GitHub branch protection API 回傳 `main` protected = true。
- required approving reviews = 1。
- enforce admins = false。

## 後續事項

- 若 repository 需要轉為 private，需由 owner 明確確認後再修改 visibility。

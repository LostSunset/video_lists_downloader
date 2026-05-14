# 研究目標與日誌 | Research Goals and Log

本檔記錄專案研究目標、技術取捨與尚待驗證的假設。當版本變更涉及架構、相依套件、下載策略、平台相容性或發布流程時，請同步更新。

## 使用規則

- 每個研究項目需包含目標、背景、目前結論、驗證方式與狀態。
- 若研究結果造成程式、文件或流程變更，於 `docs/developer_log.md` 加上對應版本紀錄。
- 若研究是在單次工作 session 中完成，也應於 `docs/sessions/` 留下 SESSION 紀錄。

## 目前研究目標

### R-2026-05-14-003 - 已記住清單管理與批次取消

- 狀態：完成
- 目標：讓使用者能直接管理已記住播放清單，並在批次檢查時看到進度與中途取消。
- 背景：v0.9.3 修正批次檢查的錯誤提示與路徑遷移問題後，仍缺少可視化管理入口；使用者無法知道目前追蹤哪些清單，也無法停止一輪較長的批次檢查。
- 目前結論：
  - 已記住清單應在左側主要工作區可見，並提供載入、檢查、開啟資料夾與移除追蹤記錄。
  - 移除追蹤記錄不應刪除下載歷史或本地檔案，避免破壞已下載狀態。
  - 批次檢查可採 cooperative cancellation：若目前 metadata 抓取已開始，會等目前項目完成後停止後續項目。
  - 取消後尚未處理的清單應進入摘要，讓使用者知道這輪沒有檢查完。
- 驗證方式：
  - 以 pytest 覆蓋清單整理、移除、批次 metadata 抓取進度與取消結果。
  - 執行 PySide offscreen 初始化 smoke check，確認新增 UI widget 可以建立並填入清單。
- 驗證結果：
  - `uv run ruff check .` 通過。
  - `uv run python -m py_compile video_downloader.py bin_manager.py` 通過。
  - `uv run pytest -q` 通過，93 tests passed。
  - PySide offscreen UI smoke check 通過。

### R-2026-05-14-002 - 播放清單批次檢查與下載可靠性

- 狀態：完成
- 目標：降低批次檢查所有清單與 cookie 下載流程中的錯誤率與 UI 干擾。
- 背景：使用者檢查所有清單時，既有邏輯會拿目前 UI 路徑與每個已記住清單路徑比較，可能連續跳出多個路徑變更提示；實際下載也缺少 browser cookie 失敗後的無 cookie fallback。
- 目前結論：
  - 單一播放清單手動檢查仍可提示路徑變更；批次檢查所有清單應使用各清單自己的記錄路徑並彙總結果。
  - 平台選擇應由下載設定傳入 worker，手動選擇優先於 URL 偵測。
  - 路徑遷移應以 playlist 為單位搬移狀態與下載歷史，避免同路徑其他清單受到影響。
  - 下載與匯出等本地狀態操作需要明確回歸測試，避免 UI-only regression。
- 驗證方式：
  - 新增 pytest 回歸測試覆蓋 cookie fallback、平台選擇、批次檢查提示條件、路徑遷移、atomic JSON 與 HTML escaping。
  - 執行 lint、語法檢查與完整測試。
- 驗證結果：
  - `uv run ruff check .` 通過。
  - `uv run python -m py_compile video_downloader.py bin_manager.py` 通過。
  - `uv run pytest -q` 通過，89 tests passed。

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

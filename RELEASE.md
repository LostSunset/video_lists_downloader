# 發布流程文檔

本專案使用 Copilot CLI 的 `release` agent 和 GitHub Actions 來自動執行發布流程。

## 自動發布 Agent

### 使用方式

在專案目錄中執行：

```bash
copilot @release
```

或帶版本號：

```bash
copilot @release v0.2.1
```

### Agent 功能

`release` agent 會自動執行以下步驟：

1. **執行測試** - 運行 pytest 和語法檢查
2. **同步版本號** - 自動同步 `video_downloader.py`、`pyproject.toml`、`CHANGELOG.md` 中的版本號
3. **更新 CHANGELOG** - 確保有對應版本的條目
4. **Lint 檢查** - 使用 ruff 檢查程式碼
5. **提交變更** - 自動 commit 所有變更
6. **標記版本** - 創建 Git tag
7. **推送到 GitHub** - 推送 commit 和 tag 到遠端

### 配置位置

Agent 配置檔案位於：
```
~/.copilot/agents/release.md
```

## GitHub Actions CI/CD

推送到 GitHub 後會自動觸發：

### CI 流程 (`.github/workflows/ci.yml`)
- 在 push 和 PR 時觸發
- 多平台測試 (Ubuntu, Windows, macOS)
- 多 Python 版本 (3.10, 3.11, 3.12)
- Lint 檢查和單元測試

### Release 流程 (`.github/workflows/release.yml`)
- 在推送 tag 時觸發
- 自動創建 GitHub Release
- 附加主程式和 LICENSE 檔案

## 手動發布流程

如果需要手動發布，請執行以下步驟：

```bash
# 1. 確保程式碼無語法錯誤並通過測試
python -m py_compile video_downloader.py
pytest tests/ -v

# 2. 更新版本號（確保以下檔案一致）
# - video_downloader.py: APP_VERSION = "v0.2.1"
# - pyproject.toml: version = "0.2.1"
# - CHANGELOG.md: 新增版本條目

# 3. 提交變更
git add .
git commit -m "Release v0.2.1"

# 4. 創建標籤
git tag -a v0.2.1 -m "Release v0.2.1"

# 5. 推送到 GitHub
git push origin main
git push origin v0.2.1
```

## 版本號規範

本專案遵循語義化版本 (SemVer)：

- **主版本號 (MAJOR)**: 不相容的 API 變更
- **次版本號 (MINOR)**: 新增功能（向下相容）
- **修訂號 (PATCH)**: Bug 修復（向下相容）

範例：`v0.2.0`

## 檔案結構

```
├── video_downloader.py      # 主程式（版本號在此）
├── pyproject.toml           # 專案配置（版本號需同步）
├── CHANGELOG.md             # 變更日誌（版本歷史）
├── tests/                   # 單元測試
│   └── test_video_downloader.py
└── .github/workflows/       # CI/CD 配置
    ├── ci.yml
    └── release.yml
```

# 發布流程文檔

本專案使用 Copilot CLI 的 `release` agent 來自動執行發布流程。

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

1. **執行測試** - 運行 Python 語法檢查和基本測試
2. **更新 README** - 自動從原始碼提取版本資訊更新 README.md
3. **提交變更** - 自動 commit 所有變更
4. **標記版本** - 創建 Git tag
5. **推送到 GitHub** - 推送 commit 和 tag 到遠端

### 配置位置

Agent 配置檔案位於：
```
~/.copilot/agents/release.md
```

## 手動發布流程

如果需要手動發布，請執行以下步驟：

```bash
# 1. 確保程式碼無語法錯誤
python -m py_compile video_downloader_pyside6_v0.2.0.py

# 2. 提交變更
git add .
git commit -m "Release v0.2.0"

# 3. 創建標籤
git tag -a v0.2.0 -m "Release v0.2.0"

# 4. 推送到 GitHub
git push origin main
git push origin v0.2.0
```

## 版本號規範

本專案遵循語義化版本：

- **主版本號 (MAJOR)**: 不相容的 API 變更
- **次版本號 (MINOR)**: 新增功能（向下相容）
- **修訂號 (PATCH)**: Bug 修復（向下相容）

範例：`v0.2.0`

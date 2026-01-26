# 貢獻指南 | Contributing Guide

感謝您有興趣為本專案做出貢獻！

## 如何貢獻

### 回報問題 (Bug Reports)

1. 確認問題尚未被回報過
2. 使用 [Issue 模板](https://github.com/LostSunset/video_lists_downloader/issues/new) 建立新 Issue
3. 提供詳細的重現步驟、環境資訊和錯誤訊息

### 功能建議 (Feature Requests)

1. 先搜尋是否已有類似建議
2. 清楚描述您希望的功能和使用場景
3. 如果可能，提供實作想法

### 提交程式碼 (Pull Requests)

1. Fork 本專案
2. 建立功能分支：`git checkout -b feature/your-feature`
3. 提交變更：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 開啟 Pull Request

## 開發環境設置

```bash
# 複製專案
git clone https://github.com/LostSunset/video_lists_downloader.git
cd video_lists_downloader

# 安裝依賴（使用 uv）
uv sync --all-extras

# 或使用 pip
pip install -e ".[dev]"
```

## 程式碼規範

- 使用 [Ruff](https://github.com/astral-sh/ruff) 進行程式碼檢查
- 遵循 PEP 8 風格指南
- 每行不超過 120 字元
- 使用有意義的變數和函數名稱

### 執行檢查

```bash
# Lint 檢查
ruff check .

# 格式化
ruff format .

# 類型檢查
mypy video_downloader.py

# 執行測試
pytest
```

## Commit 訊息規範

使用以下格式：

```
<type>: <description>

[optional body]
```

Type 類型：
- `feat`: 新功能
- `fix`: Bug 修復
- `docs`: 文件更新
- `style`: 程式碼格式（不影響功能）
- `refactor`: 重構
- `test`: 測試相關
- `chore`: 其他雜項

範例：
```
feat: 新增下載速度限制功能
fix: 修復 Bilibili 播放清單解析錯誤
docs: 更新 README 安裝說明
```

## 授權

貢獻的程式碼將採用與本專案相同的 [MIT License](LICENSE)。

# 疑難排解指南

## 錯誤訊息對照表

### 下載錯誤

| 錯誤訊息 | 可能原因 | 解決方案 |
|----------|----------|----------|
| `ERROR: Video unavailable` | 影片已刪除或設為私人 | 確認影片可正常觀看 |
| `ERROR: This video requires login` | 需要會員權限 | 提取並使用 Cookie |
| `ERROR: Incomplete YouTube ID` | URL 格式錯誤 | 檢查並修正 URL |
| `HTTP Error 429` | 請求太頻繁 | 等待一段時間後重試 |
| `HTTP Error 403` | 存取被拒絕 | 更新 Cookie 或 yt-dlp |
| `Download timeout` | 超時 | 增加超時時間設定 |

### Cookie 錯誤

| 錯誤訊息 | 可能原因 | 解決方案 |
|----------|----------|----------|
| Cookie 提取失敗 | Firefox 未關閉 | 完全關閉 Firefox |
| Cookies 無效 | Cookie 已過期 | 重新登入並提取 |
| 缺少關鍵 Cookie | 未完全登入 | 確認已登入帳號 |

---

## 常見問題解決步驟

### 問題：下載一直失敗

**步驟 1：確認 yt-dlp 是最新版本**
```bash
pip install --upgrade yt-dlp
```

**步驟 2：測試單一影片**
```bash
yt-dlp "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --simulate
```

**步驟 3：檢查網路連線**
- 確認可正常瀏覽該網站
- 暫時停用 VPN/代理（如有使用）

### 問題：程式無回應

**可能原因：**
- 正在處理大型播放清單
- 網路延遲過高

**解決方案：**
- 等待處理完成
- 將播放清單分批下載
- 重新啟動程式

### 問題：檔案名稱亂碼

**解決方案：**
- 確認系統語言設定正確
- 使用簡化檔名模板：`%(id)s`
- 啟用「自動縮短過長檔名」

---

## 進階診斷

### 開啟除錯模式

1. 勾選「除錯模式」選項
2. 重新執行下載
3. 查看日誌輸出中的詳細錯誤訊息

### 手動測試 yt-dlp

```bash
# 測試基本下載
yt-dlp "VIDEO_URL" -o "%(title)s.%(ext)s"

# 測試 Cookie
yt-dlp --cookies cookies.txt "VIDEO_URL" --simulate

# 查看可用格式
yt-dlp -F "VIDEO_URL"
```

---

## 取得支援

如果以上方法都無法解決問題：

1. 查看 [GitHub Issues](https://github.com/LostSunset/video_lists_downloader/issues)
2. 確認問題是否已被回報
3. 提交新的 Issue，請附上：
   - 錯誤訊息截圖
   - 使用的 URL（若方便提供）
   - 程式版本
   - 作業系統版本

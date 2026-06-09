# Demo Stability Baseline

本文件只保留 Demo 穩定性檢查清單。

目前狀態請以 `docs/CURRENT_STATUS.md` 為準。舊版 Step 0~3 補充內容已封存在 `docs/archive/demo_stability_baseline_舊版_2026-06-09.md`，後續實作紀錄請追加到 `docs/技術實作紀錄.md`。

## 目的

- 確認 Demo 主流程仍可穩定展示。
- 確認沒有 OpenAI、Gemini 或 PostgreSQL 時仍有 fallback。
- 在進入新功能前建立最小驗收基準。

## 檢查頻率

- Demo 前。
- 合併功能前。
- 修改 Dashboard、AI provider、API、資料流或資料庫相關程式後。

## 檢查項目

### Git 狀態

```powershell
git status
git branch --show-current
git log --oneline -5
```

### Frontend Build

```powershell
cd frontend
npm.cmd run build
```

通過標準：

- build 完成。
- 若受限 sandbox 因 `.next/trace` 寫入權限出現 `EPERM`，需在允許寫入的環境重跑確認。

### TypeScript

```powershell
cd frontend
npx.cmd tsc --noEmit
```

通過標準：

- 無 TypeScript error。

### Flask Smoke Test

```powershell
cd backend
python -c "import app; client=app.app.test_client(); print(client.get('/health').status_code); print(client.get('/api/topics').status_code); print(client.get('/api/user-settings').status_code); print(client.get('/api/favorites').status_code)"
```

通過標準：

- `/health` 回 200。
- `/api/topics` 回 200。
- `/api/user-settings` 回 200。
- `/api/favorites` 回 200。

### Demo 主流程

手動檢查：

- Dashboard 可正常顯示。
- 三個核心 topic 區塊可掃描。
- Topic detail 可開啟。
- AI summary、risk warning、content ideas 可顯示。
- 文案生成可執行，失敗時有 fallback。
- Favorites 與 User Settings 不阻擋主流程。
- Reddit live data 不可用時仍可使用 fallback data。

## Baseline 結論格式

每次檢查完成後，請將結果追加到 `docs/技術實作紀錄.md`：

```markdown
## YYYY-MM-DD Demo Stability Baseline Check

- Git branch:
- Frontend build:
- TypeScript:
- Flask smoke test:
- Demo main flow:
- Known limitations:
- Conclusion:
```

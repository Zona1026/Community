# Current Status

本文件是專案目前狀態的 Single Source of Truth。

其他文件若需要描述目前階段、完成項目、下一步、驗證指令或已知限制，請連回本文件，不重複維護同一份狀態。

## Current Phase

Phase 3 Lite：趨勢分析 UI 最小強化。

目前已完成 Demo Stability Baseline、TrendSignal 最小資料欄位、AI Copy Editor Modal MVP、AI Copy Tone Display、Regenerate Copy MVP、Multi-Version Output MVP、Export TXT MVP、Copy History MVP、Momentum Badge、Trend Chart Debug Text，以及 Trend Chart MVP。

## Completed

- Phase 1 Demo 主流程。
- OpenAI adapter 與 mock fallback 基礎架構。
- Gemini adapter 與 mock fallback 基礎架構。
- PostgreSQL 最小骨架與 `DATABASE_URL` 設定。
- Dashboard topics API 基礎串接。
- User Settings 最小儲存流程。
- Dashboard 強化。
- Favorites 收藏功能。
- Reddit 第二資料來源 fallback。
- Source Analysis。
- Demo Stability Baseline。
- Phase 3 Lite MVP:
  - Growth Rate。
  - Momentum。
  - Lifecycle Stage。
  - Trend Chart 資料準備：`scoreHistory`。
- AI Copy Editor Modal MVP。
- AI Copy Tone Display。
- Regenerate Copy MVP。
- Multi-Version Output MVP。
- Export TXT MVP。
- Copy History MVP。
- Momentum Badge。
- Trend Chart Debug Text。
- Trend Chart MVP。

## In Progress

- Phase 3 Lite 後續最小功能評估。
- 文件治理低優先級收尾。

## Next

建議下一個最小功能：

- Demo Stability Re-check。

MVP 範圍：

- 重新執行 build、TypeScript 與 Flask smoke test。
- 手動檢查 AI Copy Editor Modal 主流程。
- 確認 Copy / Regenerate / Versions / Export / History 不互相破壞。
- 不新增產品功能。

本功能暫不包含：

- 新功能。
- UI 美化。
- 資料庫 schema。
- 後端 API。

## Future Backlog

Export Backlog：

- Export Markdown。
- Export DOCX / PDF。

Documentation：

- 為 `docs/archive/` 內封存文件加入「封存勿維護」標頭。
- 此項為低優先級整理事項，不影響目前 Phase 3 Lite 開發工作。

Future AI Copy Backlog：

- 跨 Modal History 管理。
- History search。
- History category。

Phase 4：

- 更完整的跨平台來源分析。
- 長期資料保存策略。

Phase 5：

- Export：TXT / Markdown / DOCX / PDF。
- AI 趨勢顧問。

Phase 6：

- Login。
- Workspace。
- Team collaboration。
- SaaS subscription。
- Usage management。

## Validation Commands

Frontend:

```powershell
cd frontend
npm.cmd run build
npx.cmd tsc --noEmit
```

Flask smoke test:

```powershell
cd backend
python -c "import app; client=app.app.test_client(); print(client.get('/health').status_code); print(client.get('/api/topics').status_code); print(client.get('/api/user-settings').status_code); print(client.get('/api/favorites').status_code)"
```

## Known Limitations

- 真實 OpenAI 生成路徑需待有效 `OPENAI_API_KEY` 補測。
- Gemini 真實生成曾因 quota / rate limit 暫停，mock fallback 正常。
- PostgreSQL 寫入路徑需待有效 `DATABASE_URL` 補測。
- Demo 仍以固定資料與 fallback 穩定展示為優先。
- Trend Chart MVP 已使用既有 `scoreHistory` 與原生 SVG 完成最小圖表 UI。
- AI Copy Workflow 已完成 Modal MVP、Regenerate Copy MVP、Multi-Version Output MVP、Export TXT MVP 與 Copy History MVP，尚未實作雲端同步、搜尋、分類與進階匯出。
- `docs/技術實作紀錄.md` 維持 append-only 原則，保留歷史內容，不要求同步最新狀態。
- `docs/archive/` 內文件為封存用途，後續會低優先級補上「封存勿維護」標頭。
- 在受限 sandbox 中，Next.js build 可能因 `.next/trace` 寫入權限出現 `EPERM`；授權或允許寫入後可通過，屬環境限制。

# Trend Radar Phase 1 Demo

Trend Radar 是一個內容趨勢整理與靈感生成 Demo。Phase 1 目標是用固定展示資料跑完整主流程，讓 Demo 可以穩定呈現熱門話題、話題詳情、mock AI 分析與文案生成。

## 專案定位

本專案目前是結訓展示用的 Phase 1 MVP，不是正式上線版。重點放在：

- 整合 mockData 與 Threads / Dcard JSON sample
- 將資料轉成統一格式
- 建立熱門話題 Dashboard
- 顯示話題詳情、標籤、相關內容與靈感
- 使用 mock / rule-based AI 架構產生摘要、爭議提醒、內容靈感與文案

## 技術架構

- Frontend：Next.js / React / TypeScript
- Backend：Flask
- Database：PostgreSQL 規劃，連線統一使用 `DATABASE_URL`
- AI：Phase 1 僅使用 mock / rule-based 分析，尚未串接真實 AI API
- AI Provider：可透過 Next.js server route 使用 OpenAI adapter，預設仍為 mock fallback

## Phase 1 資料流

```text
mockData / Threads JSON / Dcard JSON
-> ContentItem
-> NormalizedContent
-> TopicCluster
-> TrendSignal
-> TrendReport
-> InspirationIdea
-> UI
```

## 前端啟動

```powershell
cd frontend
npm install
npm run dev
```

預設網址：

```text
http://localhost:3000
```

前端建置驗證：

```powershell
cd frontend
npm run build
```

## 後端啟動

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

Health check：

```text
GET http://127.0.0.1:5000/health
```

預期回應：

```json
{ "status": "ok" }
```

## DATABASE_URL

開發或部署時請使用環境變數管理 PostgreSQL 連線：

```text
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
```

Phase 1 尚未寫入資料庫；目前只保留 PostgreSQL / `DATABASE_URL` 設定骨架。

Step 2 已新增 PostgreSQL 最小落地骨架，包含 `topics`、`user_settings`、`generated_copies`。未設定 `DATABASE_URL` 時會安全略過資料庫初始化與測試寫入，Demo 仍使用 mockData / JSON sample fallback。

## Topics API

Step 3 已新增 Dashboard 主要資料 API。

Next.js API：

```text
GET /api/topics
GET /api/topics/{id}
```

Flask API：

```text
GET /api/topics
GET /api/topics/{topic_id}
```

前端 Dashboard 會優先呼叫 Next.js `/api/topics`。若 API 失敗，會保留初始 mockData / JSON sample fallback，不影響 Demo。

## AI Provider

前端 server route 支援 OpenAI adapter 與 mock fallback。

預設：

```text
AI_PROVIDER=mock
```

若要啟用 OpenAI：

```text
AI_PROVIDER=openai
OPENAI_API_KEY=你的金鑰
OPENAI_MODEL=gpt-4o-mini
```

未設定 `OPENAI_API_KEY` 或 OpenAI API 失敗時，Demo 會自動使用 mock / rule-based fallback。

## Demo 操作流程

1. 開啟首頁 Dashboard。
2. 檢查三個核心區塊：所有熱門話題、符合產業熱門話題、自訂關鍵字熱門話題。
3. 點擊任一話題卡片。
4. 在詳情彈窗查看 Score、Momentum、Summary、Insight、Source、Content Count。
5. 查看 Related Content、Inspiration Ideas、Platform Tags、Topic Tags。
6. 查看 mock AI 短摘要、完整摘要與爭議提醒。
7. 選擇語氣：專業、輕鬆、犀利。
8. 選擇發文角度：教學、觀點、懶人包。
9. 點擊產生文案，確認同一話題最多保留最新三版。
10. 關閉詳情彈窗，回到 Dashboard。

## Phase 1 限制

- 不接真實 AI API
- 不寫入資料庫
- 不做登入與權限
- 不新增 SaaS 付費功能
- 不做 Phase 2 以後的複雜趨勢生命週期或跨平台爆紅判斷

## 固定展示資料

- `frontend/src/data/mockData.ts`
- `frontend/src/data/importSamples/threads.sample.json`
- `frontend/src/data/importSamples/dcard.sample.json`

這些資料可重複操作，適合 Demo 使用。

## Step 4 User Settings

目前已新增使用者設定儲存的最小可用版本。

- 設定頁：`/settings`
- Next.js API：`GET /api/user-settings`
- Next.js API：`PUT /api/user-settings`
- Flask API：`GET /api/user-settings`
- Flask API：`PUT /api/user-settings`
- 設定項目：產業類別、常用語氣、自訂關鍵字
- 有 `DATABASE_URL` 且 `BACKEND_API_URL` 指向 Flask 時，可優先透過 PostgreSQL `user_settings` 儲存
- 無資料庫或 API 失敗時，前端使用 `localStorage` fallback，Demo 仍可展示

前端環境變數範例：

```text
BACKEND_API_URL=http://127.0.0.1:5000
```

# Trend Radar

Trend Radar 是一個內容趨勢整理與靈感生成 Demo，協助內容創作者、品牌與行銷團隊從多來源內容中整理熱門話題、檢視趨勢訊號，並產生內容靈感與文案。

目前專案狀態請以 `docs/CURRENT_STATUS.md` 為準。

## 專案定位

本專案以 Demo 穩定展示為優先，核心體驗包含：

- 整理 mockData、Threads / Dcard JSON sample 與 Reddit fallback data。
- 將來源資料轉成統一資料格式。
- 建立熱門話題 Dashboard。
- 顯示話題詳情、來源分析、標籤、相關內容與內容靈感。
- 透過 AI provider / fallback 架構產生摘要、爭議提醒與文案。

## 技術架構

- Frontend：Next.js / React / TypeScript
- Backend：Flask
- Database：PostgreSQL，連線統一使用 `DATABASE_URL`
- AI：Mock fallback、OpenAI adapter、Gemini adapter

技術選型與資源請見 `docs/技術資源與選型.md`。

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
npm.cmd run build
npx.cmd tsc --noEmit
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

## 環境變數

PostgreSQL：

```text
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
```

Backend API：

```text
BACKEND_API_URL=http://127.0.0.1:5000
```

AI Provider：

```text
AI_PROVIDER=mock
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
```

未設定真實 AI key 或外部服務失敗時，Demo 應保留 fallback。

## Demo 流程

1. 開啟首頁 Dashboard。
2. 檢查熱門話題、趨勢總覽、來源分析與收藏區塊。
3. 點擊任一話題卡片。
4. 在詳情彈窗查看 Score、Growth Rate、Momentum、Lifecycle Stage、Summary、Insight、Source、Content Count。
5. 查看 Related Content、Inspiration Ideas、Platform Tags、Topic Tags 與 Source Analysis。
6. 查看 AI 短摘要、完整摘要與爭議提醒。
7. 選擇語氣與發文角度。
8. 點擊產生文案。
9. 關閉詳情彈窗，回到 Dashboard。

## 權威文件

- 目前狀態：`docs/CURRENT_STATUS.md`
- 產品路線圖：`docs/產品路線圖.md`
- 開發路線圖：`docs/開發路線圖.md`
- Demo 穩定檢查：`docs/demo_stability_baseline.md`
- 技術資源與選型：`docs/技術資源與選型.md`
- 技術實作紀錄：`docs/技術實作紀錄.md`

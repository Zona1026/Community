# Trend Radar Frontend

Frontend 使用 Next.js / React / TypeScript，負責 Phase 1 Demo 的 Dashboard、話題詳情彈窗、AI 分析與文案生成。

## 啟動

```powershell
npm install
npm run dev
```

預設網址：

```text
http://localhost:3000
```

## 建置

```powershell
npm run build
```

## 主要畫面

- 首頁 Dashboard
- 所有熱門話題
- 符合產業熱門話題
- 自訂關鍵字熱門話題
- 話題詳情彈窗
- AI 分析與內容生成區塊

## Phase 1 資料來源

- `src/data/mockData.ts`
- `src/data/importSamples/threads.sample.json`
- `src/data/importSamples/dcard.sample.json`

## Phase 1 資料流

```text
ContentItem
-> NormalizedContent
-> TopicCluster
-> TrendSignal
-> TrendReport
-> InspirationIdea
-> UI
```

## AI Provider

目前支援：

- OpenAI adapter
- mock / rule-based fallback

預設仍使用 mock，避免 Demo 因 API Key 或外部服務不穩而中斷。

```text
AI_PROVIDER=mock
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

啟用 OpenAI：

```text
AI_PROVIDER=openai
OPENAI_API_KEY=你的金鑰
```

fallback 觸發條件：

- 未設定 `AI_PROVIDER=openai`
- 未設定 `OPENAI_API_KEY`
- OpenAI API 回傳錯誤
- 前端呼叫 `/api/ai-analysis` 失敗

# Demo 穩定基線紀錄

## 狀態

Step 0：Demo 穩定基線已完成。

目的：

- 在進入 OpenAI API、PostgreSQL、正式 API 串接之前，確認目前 Phase 1 Demo 仍可穩定展示。
- 確認目前 Demo 仍可在未設定 OpenAI API Key 的情況下正常運作。
- 建立可回復的驗收基準。

## 驗證日期

2026-06-05

## 驗證項目

### Demo 主流程

結果：通過。

目前主流程仍維持：

```text
mockData / JSON sample
→ ContentItem
→ NormalizedContent
→ TopicCluster
→ TrendSignal
→ TrendReport
→ InspirationIdea
→ Dashboard UI
→ 話題詳情
→ mock AI 分析
→ 文案生成
```

### 前端 build

指令：

```powershell
npm.cmd run build
```

結果：通過。

備註：

- 受限沙盒中第一次執行會因 `.next/trace` 寫入權限出現 EPERM。
- 授權後 build 正常通過。
- 此為環境權限問題，不是程式錯誤。

### TypeScript

指令：

```powershell
npm.cmd exec tsc -- --noEmit --incremental false
```

結果：通過。

### Flask health check

驗證方式：

```powershell
python -c "import sys; sys.path.insert(0, 'backend'); import app; client=app.app.test_client(); r=client.get('/health'); print(r.status_code, r.get_json())"
```

結果：

```text
200 {'status': 'ok'}
```

### JSON sample reader

驗證方式：

```powershell
python -c "import sys; sys.path.insert(0, 'backend'); import app; data=app.load_json_mock_data(); print(type(data).__name__, len(data))"
```

結果：

```text
list 2
```

### mock / rule-based AI

結果：通過。

確認內容：

- `frontend/src/lib/ai/createAiAnalysis.ts` 仍使用 mock / rule-based 分析。
- `frontend/src/components/TopicDashboard.tsx` 仍透過 `createAiAnalysis()` 顯示 AI 短摘要、完整摘要、爭議提醒、內容靈感與文案生成。
- 同一話題最新三版文案仍使用前端 state 保存。

### 未設定 OpenAI API Key

結果：通過。

確認內容：

- 目前 AI 模組沒有讀取 OpenAI / Gemini / API Key。
- 未設定 OpenAI API Key 不會影響 Demo。
- Demo 可繼續使用 mock / rule-based AI 展示。

## Step 0 結論

目前 Phase 1 Demo 穩定。

可以安全進入：

```text
Step 1：OpenAI API 基礎串接
```

但 Step 1 必須遵守：

- 不直接移除 mock AI
- 先新增 OpenAI adapter
- 保留 mock / rule-based fallback
- 未設定 API Key 時 Demo 仍可正常展示
- 每次修改後需重新通過 build、TypeScript、Flask health 與 Demo 主流程驗證

## Step 1 執行後補充

Step 1 已新增 OpenAI adapter 與 `/api/ai-analysis` route。

目前預設仍使用：

```text
AI_PROVIDER=mock
```

若要測試真實 OpenAI 路徑，需設定：

```text
AI_PROVIDER=openai
OPENAI_API_KEY=你的金鑰
```

若未設定 API Key 或 OpenAI API 失敗，Demo 會自動使用 mock fallback。

### Step 1 驗證結果

驗證項目：

- `npm.cmd run build` 通過
- `npm.cmd exec tsc -- --noEmit --incremental false` 通過
- Flask `/health` 回傳 `200 { "status": "ok" }`
- `/api/ai-analysis` route 已出現在 Next.js build 結果中
- 未設定 OpenAI API Key 時，AI route 回傳 `provider: mock`
- 未設定 OpenAI API Key 時，AI route 回傳 `isFallback: true`
- 未設定 OpenAI API Key 時，仍可產生文案

未驗證項目：

- 真實 OpenAI API Key 路徑尚未測試，因目前未提供 `OPENAI_API_KEY`

## Step 2 執行後補充

Step 2 已新增 PostgreSQL 最小可用骨架。

新增資料表：

- `topics`
- `user_settings`
- `generated_copies`

新增路由：

- `GET /db/status`
- `POST /db/init`
- `POST /db/smoke-test`

無 `DATABASE_URL` 時：

- `/db/status` 回傳 `configured: false`
- `/db/init` 回傳 `status: skipped`
- `/db/smoke-test` 回傳 `status: skipped`
- Demo 繼續使用 mockData / JSON sample fallback

待有效 PostgreSQL 連線後補測：

- `/db/init` 建表
- `/db/smoke-test` 寫入測試資料

## Step 3 執行後補充

Step 3 已新增正式 API 基礎串接。

新增 API：

- Next.js `GET /api/topics`
- Next.js `GET /api/topics/[id]`
- Flask `GET /api/topics`
- Flask `GET /api/topics/<topic_id>`

前端行為：

- Dashboard 初始顯示 fallback data
- 掛載後優先呼叫 `/api/topics`
- API 成功時切換為 API data
- API 失敗時保留 fallback data

驗證結果：

- `npm.cmd run build` 通過
- `npm.cmd exec tsc -- --noEmit --incremental false` 通過
- Flask `/health` 通過
- Flask topic routes 通過
- Next.js topic routes 通過
- 無 `DATABASE_URL` 時 Demo fallback 正常

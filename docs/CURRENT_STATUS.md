# Current Status

本文件是專案目前狀態的 Single Source of Truth。

其他文件若需要描述目前階段、完成項目、下一步、驗證指令或已知限制，請連回本文件，不重複維護同一份狀態。

## Current Phase

Phase 3 Lite：趨勢分析 UI 最小強化。

目前已完成 Demo Stability Baseline、Real Browser Demo Rehearsal、AI Copy Workflow 穩定性複查、TrendSignal 最小資料欄位、AI Copy Editor Modal MVP、AI Copy Tone Display、Regenerate Copy MVP、Multi-Version Output MVP、Copy History MVP、Momentum Badge、Trend Chart Debug Text，以及 Trend Chart MVP。

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
- 2026-06-10 Demo Stability Re-check。
- 2026-06-10 Real Browser Demo Rehearsal。
- Phase 3 Lite MVP:
  - Growth Rate。
  - Momentum。
  - Lifecycle Stage。
  - Trend Chart 資料準備：`scoreHistory`。
- AI Copy Editor Modal MVP。
- AI Copy Tone Display。
- Regenerate Copy MVP。
- Multi-Version Output MVP。
- Copy History MVP。
- Momentum Badge。
- Trend Chart Debug Text。
- Trend Chart MVP。

## In Progress

- 文件治理低優先級收尾。

## Next

建議下一步：

- Demo Freeze / commit 前整理。

MVP 範圍：

- 檢查 git diff 與變更範圍。
- 確認是否要提交目前成果。
- 準備 demo 說明或 commit message。
- 不新增產品功能。

本功能暫不包含：

- 新功能。
- UI 美化。
- 資料庫 schema。
- 後端 API。

## Future Backlog

Export Backlog：

- Export TXT。
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
- AI Copy Workflow 已完成 Modal MVP、Regenerate Copy MVP、Multi-Version Output MVP 與 Copy History MVP；目前 Modal action 保留「重新生成 / 保存 / 一鍵複製」，匯出功能列回後續規劃。
- `docs/技術實作紀錄.md` 維持 append-only 原則，保留歷史內容，不要求同步最新狀態。
- `docs/archive/` 內文件為封存用途，後續會低優先級補上「封存勿維護」標頭。
- 在受限 sandbox 中，Next.js build 可能因 `.next/trace` 寫入權限出現 `EPERM`；授權或允許寫入後可通過，屬環境限制。

## 2026-06-10 Status Note

- Completed: TrendSignal API Integration MVP.
- Current TrendSignal data flow: Browser -> Next `/api/topics` -> Flask `/api/topics` -> backend mock topics.
- Fallback data flow: Browser -> Next `/api/topics` -> frontend `buildDashboardData()` -> frontend mock/sample data.
- PostgreSQL status: not yet used as the source of TrendSignal / Dashboard topic data.
- Recommended next step: PostgreSQL read integration planning, then a minimal topics read endpoint backed by the `topics` table.

## 2026-06-10 Status Note - PostgreSQL Topics Read MVP

- Completed: PostgreSQL Topics Read MVP.
- Current `/api/topics` source priority: PostgreSQL topics table first, then `backend/mock_topics.py` fallback.
- DB topic shape: `topics.payload` stores the complete DashboardTopic / TrendSignal-compatible JSON payload.
- Fallback behavior: no `DATABASE_URL`, DB connection failure, or empty topics table returns `source=flask-mock-api`.
- Validation status: real Supabase PostgreSQL validation passed via pooler connection, Flask no-DB fallback smoke passed, DB branch simulation passed, `npx.cmd tsc --noEmit` passed, `npm.cmd run build` passed.
- Current verified `/api/topics` source: `postgresql`.
- Completed: Reddit Ingestion MVP Step 1, including `reddit_posts` staging table and DB smoke validation.
- Completed: Reddit Ingestion MVP Step 2, including Reddit env validation and OAuth token smoke test endpoint.
- Completed: RSS Ingestion MVP Step 1, including `rss_items` staging table and DB smoke validation.
- Completed: RSS Ingestion MVP Step 2, including `RSS_FEED_URL` env validation and RSS fetch smoke test endpoint.
- Remaining limitation: Reddit API credentials are not configured in the current local environment, so OAuth smoke currently returns `status=skipped`.
- Remaining limitation: `RSS_FEED_URL` is not configured in the current local environment, so RSS fetch smoke currently returns `status=skipped`.
- Remaining limitation: RSS parser and `rss_items` write flow have not started.
- Recommended next step: configure `RSS_FEED_URL`, then rerun `POST /rss/fetch-smoke-test` before implementing RSS parser or DB writes.

## 2026-06-10 Status Note - RSS Ingestion MVP Step 3

- Completed: RSS Ingestion MVP Step 3, RSS parser smoke test.
- New parser endpoint: `POST /rss/parser-smoke-test`.
- Parser scope: fetch `RSS_FEED_URL`, parse RSS/Atom XML, and return `item_count` plus sample `title`, `link`, and `guid` fields.
- Guid fallback rule: when RSS `guid` or Atom `id` is missing, use `link` as the fallback `guid`.
- Not implemented in this step: `rss_items` writes, upsert, topic generation, AI summary, scheduling, frontend UI, or ranking.
- Latest verified parser result: `item_count=30`.
- RSS fetch smoke test: passed.
- RSS parser smoke test: passed.
- DB smoke test: passed.
- Flask smoke test: passed.
- Frontend validation: `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed.
- Recommended next smallest step: implement a read-only normalized RSS item mapper or a dry-run ingestion summary before adding DB writes.

## 2026-06-10 Status Note - RSS Dry-run Ingestion Summary

- Completed: Read-only Normalized RSS Item Mapper / Dry-run Ingestion Summary.
- New dry-run endpoint: `POST /rss/dry-run-ingestion-summary`.
- Scope: fetch `RSS_FEED_URL`, parse RSS/Atom items, normalize valid items to the `rss_items` table shape, and return a summary without DB writes.
- Normalized item shape: `source_name`, `feed_url`, `item_guid`, `title`, `link`, `author`, `published_at`, `fetched_at`, `summary`, `raw_json`.
- Skipped rule: items missing `title` or `link` are skipped and reported; the flow does not crash.
- Guid fallback rule: when RSS `guid` or Atom `id` is missing, use `link` as fallback `item_guid`.
- Latest dry-run result: `total_parsed_items=30`, `valid_normalized_items=30`, `skipped_items_count=0`, `missing_guid_fallback_count=30`, `writes_to_database=False`.
- Validation status: dry-run ingestion summary passed; RSS parser smoke test passed; RSS fetch smoke test passed; DB smoke test passed; Flask smoke test passed; `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed.
- Recommended next smallest step: implement DB insert/upsert for `rss_items`, still behind an explicit smoke/dry-run style endpoint.

## 2026-06-10 Status Note - RSS Ingestion MVP Step 4

- Completed: RSS Ingestion MVP Step 4, DB Insert / Upsert Smoke Endpoint.
- New smoke endpoint: `POST /dev/rss-upsert-smoke`.
- Smoke item key: `item_guid=rss-smoke-test-guid`.
- Scope: verify `rss_items.item_guid` unique constraint, insert/update upsert behavior, `title` update, and `fetched_at` update.
- Not implemented in this step: formal RSS ingestion command, scheduling, topics generation, AI summary, frontend UI, or ranking.
- First smoke call result: `inserted=True`, `updated=True`, `final_row_id=13`, `final_item_guid=rss-smoke-test-guid`, `unique_row_count=1`, `unique_constraint_ok=True`, `fetched_at_updated=True`.
- Second smoke call result: `inserted=False`, `updated=True`, `final_row_id=13`, `final_item_guid=rss-smoke-test-guid`, `unique_row_count=1`, `unique_constraint_ok=True`, `fetched_at_updated=True`.
- Validation status: DB smoke test passed; RSS parser smoke test passed; RSS fetch smoke test passed; Flask smoke test passed; `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed.
- Recommended next smallest step: implement formal RSS ingestion MVP using the normalized mapper and the verified `rss_items` upsert path.

## 2026-06-11 Status Note - RSS Ingestion MVP Step 5

- Completed: RSS Ingestion MVP Step 5, Manual RSS Ingestion Endpoint.
- New manual endpoint: `POST /dev/rss-ingest`.
- Scope: read `RSS_FEED_URL`, fetch RSS XML, parse items, normalize items, and upsert valid items into `rss_items`.
- Upsert key: `rss_items.item_guid`.
- Upsert update fields: `source_name`, `feed_url`, `title`, `link`, `author`, `published_at`, `fetched_at`, `summary`, `raw_json`.
- Not implemented in this step: scheduling, topics auto-generation, TrendSignal ranking, AI summary, frontend UI, multi-source RSS management, or Reddit ingestion.
- First manual ingestion result: `total_parsed_items=30`, `valid_normalized_items=30`, `inserted_count=30`, `updated_count=0`, `skipped_count=0`, `error_count=0`, `source_name=Hacker News`.
- Second manual ingestion result: `total_parsed_items=30`, `valid_normalized_items=30`, `inserted_count=0`, `updated_count=30`, `skipped_count=0`, `error_count=0`, `source_name=Hacker News`.
- Validation status: manual `/dev/rss-ingest` write passed; rerun upsert passed without duplicate inserts; DB smoke test passed; RSS parser smoke test passed; Flask smoke test passed; `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed.
- Recommended next smallest step: add an RSS ingestion read/status endpoint for recently ingested `rss_items` before building topic generation.

## 2026-06-11 Status Note - RSS Read-only Status Endpoint

- Completed: Read-only RSS Ingestion Status / Recent Items Endpoint.
- New endpoint: `GET /dev/rss-status`.
- Scope: read recent `rss_items` from PostgreSQL and return counts, latest timestamps, and recent items without modifying data.
- Response summary fields: `total_count`, `recent_items_count`, `latest_fetched_at`, `latest_published_at`, `items`.
- Recent item fields: `id`, `source_name`, `feed_url`, `item_guid`, `title`, `link`, `author`, `published_at`, `fetched_at`.
- Empty behavior: returns `status=ok`, count fields as `0`, timestamp fields as `null`, and `items=[]`.
- DB unavailable behavior: returns `status=skipped` when `DATABASE_URL` is not configured, or `status=failed` with a clear reason if the database read fails.
- Latest verification result: `total_count=33`, `recent_items_count=10`, `latest_fetched_at=2026-06-11T00:58:59.823842+00:00`.
- Validation status: `/dev/rss-status` passed; `/dev/rss-ingest` still passed; DB smoke test passed; RSS parser smoke test passed; Flask smoke test passed; `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed.
- Recommended next smallest step: design a read-only RSS-to-topic candidate preview before writing generated topics.

## 2026-06-11 Status Note - RSS-to-Topic Candidate Preview

- Completed: Read-only RSS-to-Topic Candidate Preview.
- New endpoint: `GET /dev/rss-topic-candidates`.
- Query param: `limit`, default `10`, supports `?limit=20`; values are clamped to `0..50`.
- Scope: read recent `rss_items` and map them into candidate topic preview objects without writing `topics`.
- Candidate shape: `sourceItemId`, `sourceType`, `title`, `summary`, `sourceName`, `sourceUrl`, `publishedAt`, `candidateTopic`, `evidenceText`, `scoreBasis`.
- Mapping rules: `candidateTopic=title`; `evidenceText=summary` if present, otherwise `title`; `scoreBasis` includes `publishedAt`, `fetchedAt`, `sourceName`, `hasSummary`, `hasAuthor`, `itemGuid`, and `feedUrl`.
- Empty behavior: returns `status=ok`, `candidates_count=0`, and `candidates=[]`.
- DB unavailable behavior: returns `status=skipped` when `DATABASE_URL` is not configured, or `status=failed` with a clear reason if the DB read fails.
- Validation status: `/dev/rss-topic-candidates` passed; `/dev/rss-topic-candidates?limit=20` passed; empty candidates shape via `?limit=0` passed; `/dev/rss-ingest` still passed; DB smoke test passed; Flask smoke test passed; `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed.
- Recommended next smallest step: implement topic-candidate filtering / grouping preview, still read-only and without writing `topics`.

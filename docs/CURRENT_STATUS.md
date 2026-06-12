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

## 2026-06-11 Status Note - Grouped Topic Payload Preview

- Completed: Read-only Grouped Topic Payload Preview.
- New endpoint: `GET /dev/grouped-topic-payload-preview`.
- Query param: `limit`, default `10`; values are passed through the existing candidate grouping preview clamp.
- Scope: reuse RSS topic candidates and topic-candidate grouping preview, then map each group into a draft `topics.payload` shape without writing `topics`.
- Payload draft fields: `title`, `summary`, `score`, `growthRate`, `momentum`, `lifecycleStage`, `sourceType`, `sourceName`, `sourceUrl`, `evidenceCount`, `evidenceItems`, `rawGroupKey`.
- Default mapping values: `score=50`, `growthRate=0`, `momentum=weak`, `lifecycleStage=emerging`, `sourceType=rss`.
- Empty behavior: returns `status=ok`, `totalGroups=0`, `payloadCount=0`, `skippedGroups=0`, and `payloads=[]`.
- DB unavailable behavior: inherited from the grouping preview, returning `status=skipped` or `status=failed` with a clear reason.
- Validation status: `/dev/grouped-topic-payload-preview` passed; `/dev/grouped-topic-payload-preview?limit=20` passed; empty payload shape via `?limit=0` passed; `/dev/rss-ingest` still passed; DB smoke test passed; Flask smoke test passed; `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed.
- Recommended next smallest step: implement a write-disabled topics upsert dry-run plan that compares payload drafts against existing `topics.topic_key` candidates.

## 2026-06-11 Status Note - Topics Upsert Dry-run Plan

- Completed: Write-disabled Topics Upsert Dry-run Plan.
- New endpoint: `GET /dev/topics-upsert-dry-run`.
- Query param: `limit`, default `10`; values are passed through the existing grouped payload preview flow.
- Scope: reuse grouped RSS topic payload drafts, generate candidate `topicKey` values, compare against existing `topics.topic_key`, and return an insert/update/skipped/blocked plan without writing `topics`.
- Topic key support: `topics.topic_key` exists, so `missingTopicKeySupport=false`; no schema change is required for this read-only step.
- Topic key rule: lowercase title, trim, replace non-alphanumeric characters with hyphens, collapse duplicate hyphens, trim edge hyphens, cap length, and use a hash fallback when needed.
- Response includes `topicKeyRule`, `actionRules`, and `schemaSuggestion` so insert/update/skipped/blocked decisions can be inspected even when current data only triggers one action type.
- Latest dry-run result: `totalPayloads=10`, `plannedInserts=10`, `plannedUpdates=0`, `skipped=0`, `blocked=0`, `missingTopicKeySupport=false`.
- Empty behavior: `GET /dev/topics-upsert-dry-run?limit=0` returns `status=ok`, `totalPayloads=0`, and `plan=[]`.
- Validation status: `/dev/topics-upsert-dry-run` passed; `/dev/topics-upsert-dry-run?limit=20` passed; empty plan via `?limit=0` passed; `/dev/rss-ingest` still passed; DB smoke test passed; Flask smoke test passed; `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed.
- Recommended next smallest step: implement a still-explicit manual topics upsert smoke endpoint or add a write-disabled SQL preview for the exact insert/update statements before enabling topic writes.

## 2026-06-11 Status Note - Manual Topics Upsert Smoke Endpoint

- Completed: Manual Topics Upsert Smoke Endpoint.
- New endpoint: `POST /dev/topics-upsert-smoke`.
- Payload source: fixed dev smoke payload with `topic_key=topics-upsert-smoke-test`.
- Scope: verify real `topics.topic_key` insert/update behavior with `ON CONFLICT (topic_key) DO UPDATE`.
- Schema guard: endpoint checks that `topics.topic_key` exists and has a single-column unique or primary-key constraint before writing.
- First smoke call result: `insertedCount=1`, `updatedCount=0`, `finalTopicIds=[77]`, `topicKeys=["topics-upsert-smoke-test"]`, `duplicateTopicsCreated=false`.
- Second smoke call result: `insertedCount=0`, `updatedCount=1`, `finalTopicIds=[77]`, `topicKeys=["topics-upsert-smoke-test"]`, `duplicateTopicsCreated=false`.
- Not implemented in this step: formal RSS-to-topics ingestion, scheduling, TrendSignal ranking, AI summary, NLP/embedding, frontend UI, or multi-source integration.
- Validation status: `/dev/topics-upsert-smoke` insert/update passed; no duplicate topics created; DB smoke test passed; `/dev/rss-ingest` still passed; Flask smoke test passed; `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed.
- Recommended next smallest step: implement a manual RSS-to-topics ingestion preview/write endpoint behind `/dev/*`, using the existing grouped payload and verified topics upsert path.

## 2026-06-11 Status Note - Manual RSS-to-Topics Ingestion Endpoint

- Completed: Manual RSS-to-Topics Ingestion Endpoint.
- New endpoint: `POST /dev/rss-to-topics-ingest`.
- Query param: `limit`, default `3`, capped at `5`; `?limit=10` still processes at most 5 groups.
- Scope: read recent `rss_items`, generate RSS topic candidates, apply existing filtering/grouping, build grouped topic payload drafts, and upsert a limited batch into `topics`.
- Upsert key: generated `topics.topic_key` from grouped payload title.
- Upsert update fields: `title`, `summary`, `score`, `source`, `payload`, `updated_at`.
- First ingestion result with `?limit=3`: `totalGroups=3`, `processedGroups=3`, `insertedCount=3`, `updatedCount=0`, `skippedCount=0`, `sourceEvidenceCount=3`, `duplicateTopicsCreated=false`.
- Second ingestion result with `?limit=3`: `totalGroups=3`, `processedGroups=3`, `insertedCount=0`, `updatedCount=3`, `skippedCount=0`, `sourceEvidenceCount=3`, `duplicateTopicsCreated=false`.
- Topic keys verified: `vacuum-form-signage`, `notes-on-deepseek`, `klondike-solitaire-game-for-curses-in-5k-of-c`.
- `/api/topics` verification: returned `source=postgresql`; RSS-ingested topics are visible in `allTopics`.
- Not implemented in this step: scheduling, multi-source RSS management, TrendSignal ranking, AI summary, NLP/embedding, frontend UI, Reddit ingestion, or production ingestion.
- Validation status: `/dev/rss-to-topics-ingest` insert/update passed; no duplicate topics created; `/api/topics` can read the new topics; DB smoke test passed; `/dev/rss-ingest` still passed; Flask smoke test passed; `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed.
- Recommended next smallest step: add a read-only RSS-to-topics ingestion status endpoint that reports recent RSS-created topics and their evidence before building production ingestion controls.

## 2026-06-11 Status Note - RSS-to-Topics Status Endpoint

- Completed: Read-only RSS-to-Topics Ingestion Status Endpoint.
- New endpoint: `GET /dev/rss-topics-status`.
- Query param: `limit`, default `10`, capped at `10`; `?limit=50` returns `effectiveLimit=10`.
- Scope: read topics generated or updated by the RSS-to-topics ingestion flow without modifying `topics` or frontend UI.
- RSS-generated topic rule: `topics.payload` contains `rssIngestion` metadata.
- Response fields: `totalRssTopicsCount`, `recentTopicsCount`, `latestUpdatedAt`, `rssGeneratedTopicRule`, `schemaGap`, and `topics`.
- Recent topic fields: `id`, `topic_key`, `title`, `source_type`, `source_name`, `source_url`, `evidence_count`, `created_at`, `updated_at`.
- Latest status result: `totalRssTopicsCount=5`, `recentTopicsCount=5`, `effectiveLimit=10`, `latestUpdatedAt=2026-06-11T02:11:29.190728+00:00`.
- Empty recent behavior: `GET /dev/rss-topics-status?limit=0` returns `recentTopicsCount=0` and `topics=[]` while preserving total count.
- Schema note: no schema change was made; this MVP uses `topics.payload.rssIngestion`. A future production audit trail may benefit from a dedicated topic source/evidence table.
- Validation status: `/dev/rss-topics-status` passed; empty recent behavior via `?limit=0` passed; `/dev/rss-to-topics-ingest` still passed; `/api/topics` still passed; DB smoke test passed; Flask smoke test passed; `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed.
- Recommended next smallest step: add a read-only topic evidence detail endpoint for one `topic_key`, so each generated topic can expose the RSS items behind it before adding production controls.

## 2026-06-11 Status Note - Low-risk Real RSS Smoke Flow

- Completed: low-risk real RSS smoke flow for validating `RSS feed -> parse -> normalize -> grouping -> topic draft -> optional topics upsert`.
- New endpoints: `GET /dev/rss-preview`, `GET /dev/rss-topic-draft`, `POST /dev/rss-to-topics-smoke`, `POST /dev/rss-smoke-rollback`.
- Feed safety: fixed whitelist only; first allowed feed is `hacker-news` -> `https://news.ycombinator.com/rss`.
- Processing safety: at most 5 RSS items per request.
- Write safety: `POST /dev/rss-to-topics-smoke` defaults to `dry_run=true`; only `dry_run=false` writes to `topics`.
- Smoke write markers: `source='rss_smoke_test'`, `topic_key` prefix `rss-smoke-`, generated `batch_id`, and payload metadata `smokeBatchId`.
- Rollback: `POST /dev/rss-smoke-rollback` deletes only rows with `source='rss_smoke_test'` and matching `smokeBatchId`.
- Latest preview result: `feed_source=Hacker News`, `fetched_count=30`, `normalized_count=5`, `grouped_topic_count=0`, `skipped_count=0`, `dry_run=true`.
- Latest draft result: `feed_source=Hacker News`, `fetched_count=30`, `normalized_count=5`, `grouped_topic_count=5`, `skipped_count=0`, `dry_run=true`.
- Latest write smoke result: `inserted_count=5`, `updated_count=0`, `skipped_count=0`, `batch_id=rss-smoke-7d2291d0-b13a-4e7a-8023-9374567d434e`.
- Latest rollback result: `deleted_count=5` for the same batch id.
- Validation status: RSS preview passed; topic draft passed; dry-run smoke passed; `dry_run=false` write passed; rollback passed; DB smoke test passed; Flask smoke test passed; `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed.
- Recommended next smallest step: add a read-only smoke batch status endpoint for checking a `batch_id` before and after rollback, or keep using this flow manually while inspecting data quality.

## 2026-06-11 Status Note - RSS Smoke Acceptance Checks

- Completed: RSS smoke acceptance checks without production scheduler changes.
- New acceptance script: `python backend/dev_rss_smoke_acceptance.py`.
- Check 1: `dry_run=false` writes 5 RSS smoke topics, then `/api/topics` includes those topic ids.
- Check 2: frontend topic-list data contract is verified by confirming `TopicDashboard` fetches `/api/topics` and renders `topicsData.allTopics`.
- Check 3: rerunning the same smoke write uses `topic_key` upsert; second run updates 5 rows and creates no duplicates.
- Check 4: empty RSS, malformed RSS XML, timeout, and non-whitelisted feed return readable `reason` or `errors` without Flask crashing.
- Check 5: rollback by `batch_id` deletes 5 smoke rows, and `/api/topics` no longer includes that batch's topic ids.
- Latest acceptance result: `status=ok`; first batch `rss-smoke-76f9ab9e-3a61-4c07-be2d-56af2756f2c3`; second batch `rss-smoke-52803363-daa8-4049-b9b8-73bcc4891d69`; rollback completed.
- Validation status: acceptance script passed; `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed after build completed; Python compile passed.
- Note: no browser automation dependency was added; visual DOM verification can be added later with Playwright if needed.

## 2026-06-11 Status Note - Dcard Smoke Flow

- Completed: Dcard ingestion smoke test endpoints using the same safety posture as RSS smoke.
- New endpoints: `GET /dev/dcard-preview`, `GET /dev/dcard-topic-draft`, `POST /dev/dcard-to-topics-smoke`, `POST /dev/dcard-smoke-rollback`.
- Source: fixed Dcard popular posts API path, not arbitrary external URLs.
- Processing safety: at most 10 Dcard posts per request.
- Write safety: `POST /dev/dcard-to-topics-smoke` defaults to `dry_run=true`; only `dry_run=false` attempts to write.
- Smoke write markers: `source='dcard_smoke_test'`, `topic_key` prefix `dcard-smoke-`, generated `batch_id`, and payload metadata `smokeBatchId`.
- Rollback: `POST /dev/dcard-smoke-rollback` deletes only rows with `source='dcard_smoke_test'` and matching `smokeBatchId`.
- Live Dcard fetch verification: Dcard public API returned HTTP 403 even with browser-like headers. Endpoint returns readable `status=failed`, `reason=Dcard API returned an HTTP error.`, and does not write data.
- DB path verification: local Dcard smoke draft upsert inserted 1 row with `batch_id=dcard-smoke-0f001cf1-2897-41f8-83c4-c20577c70597`, then rollback deleted 1 row.
- Current blocker: real Dcard data cannot enter the pipeline until Dcard access is available or an approved alternative source is chosen. Do not assume API credentials or authorization exist.
- Validation status: Python compile passed; `/health`, `/api/topics`, `/db/status`, and DB smoke test passed; Dcard endpoints returned readable 403 failure without Flask crash; `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed.

## 2026-06-11 Status Note - Podcast RSS Smoke Flow

- Completed: Podcast RSS ingestion smoke test using the existing RSS parser/normalizer.
- New endpoints: `GET /dev/podcast-preview`, `GET /dev/podcast-topic-draft`, `POST /dev/podcast-to-topics-smoke`, `POST /dev/podcast-smoke-rollback`.
- Default feed: `planet-money`.
- Podcast whitelist: `planet-money`, `ted-radio-hour`, `bbc-global-news`, `lex-fridman`.
- Processing safety: at most 5 podcast episodes per request.
- Write safety: `POST /dev/podcast-to-topics-smoke` defaults to `dry_run=true`; only `dry_run=false` writes to `topics`.
- Smoke write markers: `source='podcast_smoke_test'`, `topic_key` prefix `podcast-smoke-`, generated `batch_id`, and payload metadata `smokeBatchId`.
- Rollback: `POST /dev/podcast-smoke-rollback` deletes only rows with `source='podcast_smoke_test'` and matching `smokeBatchId`.
- Latest preview result: `feed_source=NPR Planet Money`, `fetched_count=355`, `normalized_count=5`, `grouped_topic_count=0`, `skipped_count=2`, `dry_run=true`.
- Latest draft result: `feed_source=NPR Planet Money`, `fetched_count=355`, `normalized_count=5`, `grouped_topic_count=5`, `skipped_count=2`, `dry_run=true`.
- Latest write smoke result: `inserted_count=5`, `updated_count=0`, `skipped_count=0`, `batch_id=podcast-smoke-f114776c-8513-44d8-accf-d34f639d63ae`, then rollback deleted 5 rows.
- Upsert verification: first run inserted 5 rows, second run updated 5 rows, then rollback deleted 5 rows for `batch_id=podcast-smoke-d4137ba2-8829-4116-9587-b49c3b0b9da6`.
- Validation status: Python compile passed; podcast preview/draft/dry-run/write/rollback passed; non-whitelisted feed blocked; DB smoke test passed; Flask smoke test passed; `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed.

## 2026-06-11 Status Note - Podcast Smoke Acceptance Checks

- Completed: Podcast smoke acceptance script without production scheduler changes.
- New acceptance script: `python backend/dev_podcast_smoke_acceptance.py`.
- Check 1: `dry_run=false` writes 5 podcast smoke topics, then `/api/topics` includes those topic ids.
- Check 2: rerunning the same podcast smoke write uses `topic_key` upsert; second run updates 5 rows and creates no duplicates.
- Check 3: rollback by `batch_id` deletes 5 smoke rows, and `/api/topics` no longer includes that batch's topic ids.
- Check 4: verifies `batch_id`, `source='podcast_smoke_test'`, `topic_key` prefix `podcast-smoke-`, positive `evidence_count`, and non-empty `updated_at`.
- Latest acceptance result: `status=ok`; first batch `podcast-smoke-98d3dffe-8453-4a2d-b14f-42fd2571adcd`; second batch `podcast-smoke-ae51d4bc-7268-4a78-b386-db4e80e735ed`; rollback completed.
- Validation status: podcast acceptance script passed; DB smoke test passed; Flask smoke test passed; `/api/topics` passed; `npm.cmd run build` passed; `npx.cmd tsc --noEmit` passed after build completed; `python -m compileall backend` passed.
- Note: no production scheduler changes were made.

## 2026-06-11 Status Note - Ingestion Safety Boundary MVP

- Completed: Ingestion Safety Boundary MVP for current RSS, Podcast, and Dcard smoke ingestion endpoints.
- Dev endpoint guard: all `/dev/*` endpoints now require `ALLOW_DEV_ENDPOINTS=true`.
- Default behavior: when `ALLOW_DEV_ENDPOINTS` is missing or not `true`, `/dev/*` returns HTTP 403 with `status=blocked`.
- Production boundary: production should leave `ALLOW_DEV_ENDPOINTS=false` or unset; `/dev/*` is not a production ingestion control surface.
- Formal API safety: `/api/topics`, `/api/user-settings`, and `/api/favorites` are not affected by the dev endpoint guard.
- Smoke write metadata remains in the existing `topics` table; no schema or table was added.
- Smoke metadata rule: `topics.source` marks the smoke source, `topics.topic_key` uses a smoke prefix, and `topics.payload.smokeBatchId` stores the batch id.
- Rollback safety rule: RSS, Podcast, and Dcard rollback now require matching `source`, matching `payload.smokeBatchId`, and the expected `topic_key` prefix before deleting rows.
- Acceptance scripts explicitly enable `ALLOW_DEV_ENDPOINTS=true` for their own smoke flow validation.
- Not implemented: production scheduler, new ingestion source, new schema, auth, or production ingestion controls.

## 2026-06-11 Status Note - Production Deployment Checklist

- Added a minimum production deployment checklist focused on ingestion safety.
- Environment rule: `ALLOW_DEV_ENDPOINTS` must be `false` or unset in production.
- Database rule: `DATABASE_URL` must point to the correct production PostgreSQL database, not a local, smoke-test, staging, or personal DB.
- Dev endpoint rule: production must not use `/dev/*`; those endpoints should return HTTP 403 with `status=blocked`.
- Formal API rule: `/api/topics` must still return HTTP 200 after `/dev/*` is blocked.
- Ingestion rule: RSS and Podcast smoke flows are not production ingestion and must not be used as scheduled jobs.
- Scheduler status: no production scheduler is enabled yet.
- Rollback rule: smoke rollback is only for smoke topics and must match `source`, `payload.smokeBatchId`, and smoke `topic_key` prefix.
- Pre-deployment validation list: `/health`, `/db/status`, `/api/topics`, `python -m compileall backend`, `npm.cmd run build`, and `npx.cmd tsc --noEmit`.

## 2026-06-11 Status Note - Manual Scheduled Ingestion Runner MVP

- Completed: Manual Scheduled Ingestion Runner MVP.
- Scope: manual CLI trigger only; no timer, cron, background worker, or production scheduler was added.
- New table: `ingestion_runs`, used to record each ingestion run's source, status, timestamps, counts, dry-run flag, error message, and metadata.
- New CLI: `python backend/run_ingestion_once.py --source rss --feed hacker-news --limit 5`.
- Podcast CLI: `python backend/run_ingestion_once.py --source podcast --feed planet-money --limit 5`.
- Dry-run CLI: add `--dry-run`; topics are not written but `ingestion_runs` still records the run.
- New read-only status endpoint: `GET /admin/ingestion-runs/latest`.
- Runner path: does not call `/dev/*` endpoints.
- Source safety: reuses fixed RSS / Podcast whitelists; arbitrary feed URLs are not accepted.
- Formal topic source: runner does not write `rss_smoke_test` or `podcast_smoke_test`.
- Topic key rule: deterministic key from `source_type + source_key + title`; batch ids are not used for formal topic identity.
- Duplicate protection: batch-local duplicate topic keys are skipped, and `topics.topic_key UNIQUE` plus upsert remain the final DB guard.
- `/api/topics` remains the read path for frontend topics and is not an ingestion trigger.

## 2026-06-11 Status Note - Read-only Ingestion Run History Endpoint

- Completed: read-only ingestion run history endpoint.
- New endpoint: `GET /admin/ingestion-runs`.
- Scope: read `ingestion_runs` only; it does not trigger ingestion, update `topics`, or update `ingestion_runs`.
- Default behavior: returns the latest 20 runs ordered by `started_at DESC, id DESC`.
- Query params: `limit`, `source_type`, `source_key`, and `status`.
- Response run fields: `run_id`, `source_type`, `source_key`, `status`, `started_at`, `finished_at`, fetched/normalized/grouped/inserted/updated/skipped/error counts, `error_message`, and `dry_run`.
- Existing latest endpoint remains: `GET /admin/ingestion-runs/latest`.
- `/api/topics` remains unaffected.

## 2026-06-11 Status Note - Read-only Ingestion Run Detail Endpoint

- Completed: read-only ingestion run detail endpoint.
- New endpoint: `GET /admin/ingestion-runs/<run_id>`.
- Scope: reads one `ingestion_runs` row only; it does not trigger ingestion, update `topics`, or update `ingestion_runs`.
- Response includes all run summary fields plus full `metadata JSONB`.
- If `metadata` contains `topicKeys`, `finalTopicIds`, or per-topic `results`, they are returned unchanged.
- Not found behavior: missing `run_id` returns HTTP 404 with `status=not_found`.
- Existing history endpoint remains: `GET /admin/ingestion-runs`.
- Existing latest endpoint remains: `GET /admin/ingestion-runs/latest`.
- `/api/topics` remains unaffected.

## 2026-06-11 Status Note - Read-only Ingestion Health Summary Endpoint

- Completed: read-only admin ingestion health/status summary endpoint.
- New endpoint: `GET /admin/ingestion-health`.
- Scope: reads `ingestion_runs` only; it does not trigger ingestion, update `topics`, or update `ingestion_runs`.
- Response includes `latest_run`, `recent_failed_count`, `last_success_by_source_type.rss`, `last_success_by_source_type.podcast`, `last_failed_run`, and `status_summary`.
- Recent failure window: latest 20 `ingestion_runs`, ordered by `started_at DESC, id DESC`.
- `status_summary=no_runs`: there are no ingestion runs.
- `status_summary=healthy`: latest run is `success` and `recent_failed_count=0`.
- `status_summary=warning`: latest run failed, or `recent_failed_count>0`.
- Existing history/detail/latest endpoints remain unchanged.
- `/api/topics` remains unaffected.

## 2026-06-11 Status Note - Manual Ingestion Runbook

- Added a Manual Ingestion Runbook for the transition period before production scheduler work.
- Purpose: document how to operate the formal Manual Scheduled Ingestion Runner without using `/dev/*` smoke endpoints.
- Runner scope: formal CLI runner only; still not a timer, cron job, worker, or production scheduler.
- CLI examples documented:
  - `python backend/run_ingestion_once.py --source rss --feed hacker-news --limit 5`
  - `python backend/run_ingestion_once.py --source podcast --feed planet-money --limit 5`
  - dry-run examples for RSS and Podcast.
- Post-run check order documented: `/admin/ingestion-health`, `/admin/ingestion-runs/latest`, `/admin/ingestion-runs`, `/admin/ingestion-runs/<run_id>`, and `/api/topics`.
- Success criteria documented: CLI exit code 0, `ingestion_runs.status=success`, no new failed run in health, `/api/topics` remains HTTP 200, and reruns do not create duplicate topics.
- Failure handling documented: inspect detail metadata and `error_message`; do not use smoke rollback or manual topic deletion as the first response.
- Prohibited operations documented: do not use `/dev/*` smoke endpoints as formal ingestion, do not enable `ALLOW_DEV_ENDPOINTS=true` in production, do not use smoke rollback for formal topics, and do not use `batch_id` as formal topic identity.

## 2026-06-11 Status Note - Per-source Advisory Lock

- Completed: per-source PostgreSQL advisory lock for the Manual Scheduled Ingestion Runner.
- Scope: runner protection only; no scheduler, cron, worker, UI, or new table was added.
- Lock key rule: deterministic lock name `scheduled-ingestion:{source_type}:{source_key}`, converted to a signed 64-bit key with SHA-256.
- Same-source rule: the same `source_type + source_key` cannot run twice at the same time.
- Different-source rule: different sources can run independently because they use different advisory lock keys.
- Lock unavailable behavior: fetch, parse, and topic upsert are skipped.
- Lock unavailable run record: writes an `ingestion_runs` row with `status=skipped`, `error_count=1`, a clear `error_message`, and `metadata.advisoryLock.reason=lock_unavailable_already_running`.
- CLI behavior: lock unavailable exits with code 1 because the CLI only exits 0 for `status=success`.
- Safety: advisory lock is released in `finally`, including failed runs.

## 2026-06-11 Status Note - Host-level Scheduler Draft

- Added host-level scheduler draft documentation only.
- No real scheduler, cron job, Windows Task Scheduler task, worker, or HTTP trigger was enabled.
- Recommended trigger: host-level cron or Windows Task Scheduler directly executing `python backend/run_ingestion_once.py`.
- Scheduler must not call `/dev/*` endpoints.
- Recommended frequency: RSS every 1 hour; Podcast every 6 hours.
- Draft commands documented for RSS and Podcast runner.
- Windows Task Scheduler examples documented with `Program/script=python`, runner arguments, and project `Start in` path.
- Cron examples documented with hourly RSS and every-6-hours Podcast schedules.
- Prerequisites documented: correct `DATABASE_URL`, `ALLOW_DEV_ENDPOINTS=false` or unset, Manual Ingestion Runbook verified, per-source advisory lock enabled, and `/admin/ingestion-health` available.
- Post-run checks documented: `/admin/ingestion-health`, `/admin/ingestion-runs/latest`, `/admin/ingestion-runs`, and `/api/topics`.
- Explicitly out of scope: worker queue, GitHub Actions scheduler, hosted scheduler, retry, webhook, Slack, email alerts, and using `/dev/*` as scheduler.
- Next step after documentation: enable host-level scheduler in the deployment environment and observe 24-48 hours.

## 2026-06-11 Status Note - Render Production Readiness

- Completed: minimum Render backend production readiness gap.
- Backend dependency: `gunicorn` added to `backend/requirements.txt`.
- Recommended Render backend Web Service settings documented:
  - Root Directory: `backend`
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `gunicorn app:app`
- Added `ADMIN_API_TOKEN` to `backend/.env.example`.
- `/admin/*` endpoints now require a correct admin token.
- Accepted admin token formats:
  - `Authorization: Bearer <ADMIN_API_TOKEN>`
  - `X-Admin-API-Token: <ADMIN_API_TOKEN>`
- Missing or incorrect token returns HTTP 401 with `status=unauthorized`.
- `/health`, `/db/status`, and `/api/topics` do not require the admin token.
- `ALLOW_DEV_ENDPOINTS=false` remains the production default.
- Render Cron Job remains not enabled.

## 2026-06-12 Status Note - Render Manual Deployment Checklist

- Added Render Manual Deployment Checklist documentation only.
- No code was changed for this checklist step.
- No Render deployment was performed.
- No Render Cron Job was created or enabled.
- Backend Render Web Service settings documented:
  - Root Directory: `backend`
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `gunicorn app:app`
- Backend required env documented: `DATABASE_URL`, `ADMIN_API_TOKEN`, and `ALLOW_DEV_ENDPOINTS=false`.
- Backend acceptance order documented: `/health`, `/db/status`, `/api/topics`, `/admin/ingestion-health` without token expecting 401, and `/admin/ingestion-health` with token expecting 200.
- Frontend Render Web Service settings documented:
  - Root Directory: `frontend`
  - Build Command: `npm ci && npm run build`
  - Start Command: `npm run start`
- Frontend required env documented: `BACKEND_API_URL=<Render backend URL>`.
- Frontend acceptance notes documented: Dashboard opens, `/api/topics` can read backend topics, and backend cold-start fallback behavior is acceptable.
- Aiven PostgreSQL checks documented: `DATABASE_URL` points to Aiven, SSL is correct, Render backend can connect, and Render Free Postgres is not used as the long-term database.
- Render Cron Job remains a follow-up step for RSS and Podcast only.
- Deployment notes documented: Free Web Service may sleep, first request can be slower, `/admin/*` requires token, and `ALLOW_DEV_ENDPOINTS` must not be `true`.

## 2026-06-12 Status Note - Render psycopg Binary Build Fix

- Fixed Render backend build dependency issue.
- Previous requirement: `psycopg[binary]==3.2.3`.
- Render resolved the binary extra to `psycopg-binary==3.2.3`, but no matching distribution was available for the Render build environment.
- Updated requirement: `psycopg[binary]==3.2.13`.
- Kept Psycopg 3 because backend code imports `psycopg`; did not switch to `psycopg2-binary`.
- Before redeploying Render backend, commit and push the updated `backend/requirements.txt`, then trigger a fresh Render deploy.

## 2026-06-12 Status Note - HTML-to-text Summary Sanitizer

- Completed: minimum backend HTML-to-text sanitizer for RSS / Podcast topic summaries.
- New helper: `backend/text_utils.py`, function `clean_html_to_text(value, max_length=500)`.
- Sanitizer behavior: decodes HTML entities, converts common block tags to spacing, removes HTML tags, compresses whitespace, removes residual markup, and truncates long summaries.
- Ingestion path: RSS / Podcast normalized item `summary` is cleaned for future writes.
- Topic draft / payload path: topic summaries are cleaned again before topic upsert.
- API read fallback: `/api/topics` cleans summary before returning topics, so existing rows with old HTML summaries do not need manual deletion or rebuild.
- Frontend rendering remains plain text; `dangerouslySetInnerHTML` is not used.

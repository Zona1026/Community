# Backend

Phase 1 backend skeleton for the Trend Radar project.

## Tech

- Flask
- PostgreSQL
- `DATABASE_URL` for database connection settings

## Setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Set `DATABASE_URL` in `.env` or in your deployment platform environment variables when a PostgreSQL database is available.

## Run

```powershell
python app.py
```

Health check:

```text
GET http://127.0.0.1:5000/health
```

Expected response:

```json
{ "status": "ok" }
```

## JSON Mock Data

`load_json_mock_data()` can read JSON sample data from the frontend import sample folder.

## PostgreSQL

Step 2 adds a minimal PostgreSQL baseline. It is safe when `DATABASE_URL` is not configured.

Tables:

- `topics`
- `user_settings`
- `generated_copies`

Status:

```text
GET /db/status
```

Initialize tables:

```text
POST /db/init
```

Smoke test insert:

```text
POST /db/smoke-test
```

If `DATABASE_URL` is empty, `/db/init` and `/db/smoke-test` return `status: skipped` and the Phase 1 Demo can continue using mock fallback data.

## User Settings API

Step 4 adds a minimal single-demo-user settings API.

Endpoints:

```text
GET /api/user-settings
PUT /api/user-settings
POST /api/user-settings
```

Payload:

```json
{
  "industry": "AI",
  "tone": "專業",
  "keywords": ["AI", "創業"]
}
```

When `DATABASE_URL` is configured, settings are stored in the PostgreSQL `user_settings` table. When `DATABASE_URL` is not configured, the API returns a safe fallback response and does not break the Demo.

## Favorites API

Step 6 adds a minimal single-demo-user favorites API.

Endpoints:

```text
GET /api/favorites
POST /api/favorites/{topic_id}
DELETE /api/favorites/{topic_id}
```

Database table:

- `favorites`

When `DATABASE_URL` is configured, favorite topic IDs are stored in PostgreSQL. When `DATABASE_URL` is not configured, the API returns a safe fallback response and the frontend can keep favorites in `localStorage`.

## Reddit OAuth Smoke Test

Reddit ingestion is not implemented yet. Step 2 only validates Reddit API environment variables and confirms that an OAuth access token can be requested.

Required environment variables:

```text
REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET
REDDIT_USER_AGENT
```

Status:

```text
GET /reddit/status
```

OAuth token smoke test:

```text
POST /reddit/oauth-smoke-test
```

If the Reddit variables are missing, the smoke test returns `status: skipped` and does not affect the Flask app, `/api/topics`, or the PostgreSQL fallback flow.

## RSS Fetch Smoke Test

RSS ingestion is not implemented yet. This smoke test only validates `RSS_FEED_URL` and confirms that the feed URL can return XML-like content.

Required environment variable:

```text
RSS_FEED_URL
```

Optional environment variable:

```text
RSS_REQUEST_TIMEOUT_SECONDS
```

Status:

```text
GET /rss/status
```

Fetch smoke test:

```text
POST /rss/fetch-smoke-test
```

Parser smoke test:

```text
POST /rss/parser-smoke-test
```

The parser smoke test fetches `RSS_FEED_URL`, parses XML with Python stdlib `xml.etree.ElementTree`, and returns:

- `item_count`
- sample `items` with `title`, `link`, and `guid`
- `guid_fallback_rule`

If an RSS `guid` or Atom `id` is missing, the parser uses `link` as the fallback `guid`. This smoke test does not write to PostgreSQL, upsert `rss_items`, generate topics, call AI, schedule ingestion, or affect `/api/topics`.

If `RSS_FEED_URL` is missing, RSS smoke tests return `status: skipped`.

## RSS Dev Endpoints

Manual RSS ingestion:

```text
POST /dev/rss-ingest
```

Read-only RSS ingestion status:

```text
GET /dev/rss-status
```

`/dev/rss-status` reads recent `rss_items` only. It returns total count, recent item count, latest `fetched_at`, latest `published_at`, and recent RSS items. It does not write data, generate topics, call AI, schedule ingestion, or affect `/api/topics`.

Read-only RSS-to-topic candidate preview:

```text
GET /dev/rss-topic-candidates
GET /dev/rss-topic-candidates?limit=20
```

`/dev/rss-topic-candidates` maps recent `rss_items` into candidate topic preview objects. It does not write `topics`, merge duplicates, rank trends, call AI, schedule ingestion, or affect `/api/topics`.

Read-only grouped topic payload preview:

```text
GET /dev/grouped-topic-payload-preview
GET /dev/grouped-topic-payload-preview?limit=20
```

`/dev/grouped-topic-payload-preview` maps grouped RSS topic candidates into draft `topics.payload` objects. It does not write `topics`, upsert topics, rank trends, call AI, schedule ingestion, or affect `/api/topics`.

Write-disabled topics upsert dry-run plan:

```text
GET /dev/topics-upsert-dry-run
GET /dev/topics-upsert-dry-run?limit=20
```

`/dev/topics-upsert-dry-run` maps grouped topic payload drafts into an insert/update/skipped/blocked plan by comparing generated topic keys with existing `topics.topic_key` values. The response includes the topic key rule, action rules, and a schema suggestion when `topics.topic_key` is missing. It does not write `topics`, upsert topics, modify schema, rank trends, call AI, schedule ingestion, or affect `/api/topics`.

Manual topics upsert smoke test:

```text
POST /dev/topics-upsert-smoke
```

`/dev/topics-upsert-smoke` uses a fixed dev smoke payload to verify real `topics.topic_key` insert/update behavior. It checks that `topics.topic_key` exists and is uniquely constrained before writing. It does not run formal RSS-to-topics ingestion, rank trends, call AI, schedule ingestion, or affect the frontend UI.

Manual RSS-to-topics ingestion:

```text
POST /dev/rss-to-topics-ingest
POST /dev/rss-to-topics-ingest?limit=5
```

`/dev/rss-to-topics-ingest` reads recent `rss_items`, reuses the RSS topic candidate grouping and grouped payload draft mapper, limits processing to at most 5 groups, and upserts those drafts into `topics` with `topic_key` as the unique key. It does not schedule ingestion, call AI, run ranking, manage multiple sources, ingest Reddit, or modify the frontend UI.

Read-only RSS topics status:

```text
GET /dev/rss-topics-status
GET /dev/rss-topics-status?limit=10
```

`/dev/rss-topics-status` reads topics created or updated by the RSS-to-topics ingestion flow. It identifies RSS-generated topics by `topics.payload.rssIngestion`, returns counts, latest `updated_at`, and recent topic metadata. It is read-only and does not affect `/api/topics` or the frontend UI.

Low-risk real RSS smoke flow:

```text
GET /dev/rss-preview
GET /dev/rss-topic-draft
POST /dev/rss-to-topics-smoke
POST /dev/rss-to-topics-smoke?dry_run=false
POST /dev/rss-smoke-rollback
```

These endpoints fetch only fixed whitelisted RSS feeds, process at most 5 RSS items, default to `dry_run=true`, and write to `topics` only when `dry_run=false`. Smoke writes use `source='rss_smoke_test'`, a `rss-smoke-*` topic key prefix, and a generated `batch_id`; `/dev/rss-smoke-rollback` deletes smoke rows for that batch.

Acceptance check:

```text
python backend/dev_rss_smoke_acceptance.py
```

The acceptance script writes 5 RSS smoke topics, verifies `/api/topics` can read them, checks the frontend topic-list data contract, reruns the smoke write to confirm `topic_key` upsert behavior, verifies empty/malformed/timeout/non-whitelisted feed handling, and rolls the smoke batch back by `batch_id`.

Low-risk Dcard smoke flow:

```text
GET /dev/dcard-preview
GET /dev/dcard-topic-draft
POST /dev/dcard-to-topics-smoke
POST /dev/dcard-to-topics-smoke?dry_run=false
POST /dev/dcard-smoke-rollback
```

These endpoints use the fixed Dcard popular posts API path, process at most 10 posts, default to `dry_run=true`, and write to `topics` only when `dry_run=false`. Smoke writes use `source='dcard_smoke_test'`, a `dcard-smoke-*` topic key prefix, and a generated `batch_id`; `/dev/dcard-smoke-rollback` deletes Dcard smoke rows for that batch.

Current note: the Dcard public API returned HTTP 403 during local verification, so the live fetch endpoint currently returns a readable failure and does not write data. The DB upsert/rollback path was verified with a local smoke draft and rolled back.

Low-risk podcast RSS smoke flow:

```text
GET /dev/podcast-preview
GET /dev/podcast-topic-draft
POST /dev/podcast-to-topics-smoke
POST /dev/podcast-to-topics-smoke?dry_run=false
POST /dev/podcast-smoke-rollback
```

These endpoints reuse the existing RSS parser/normalizer for podcast RSS feeds, process at most 5 episodes, default to `dry_run=true`, and write to `topics` only when `dry_run=false`. Smoke writes use `source='podcast_smoke_test'`, a `podcast-smoke-*` topic key prefix, and a generated `batch_id`; `/dev/podcast-smoke-rollback` deletes podcast smoke rows for that batch.

Podcast whitelist:

- `planet-money`
- `ted-radio-hour`
- `bbc-global-news`
- `lex-fridman`

Podcast acceptance check:

```text
python backend/dev_podcast_smoke_acceptance.py
```

The acceptance script writes 5 podcast smoke topics, verifies `/api/topics` can read them, checks `batch_id`, `source='podcast_smoke_test'`, `topic_key`, `evidence_count`, and `updated_at`, reruns the smoke write to confirm `topic_key` upsert behavior, and rolls the smoke batch back by `batch_id`.

## Ingestion Safety Boundary MVP

`/dev/*` endpoints are development and smoke-test tools, not production ingestion controls. They are disabled by default unless the environment explicitly sets:

```text
ALLOW_DEV_ENDPOINTS=true
```

If `ALLOW_DEV_ENDPOINTS` is missing or any value other than `true`, every `/dev/*` endpoint returns HTTP 403 with `status=blocked`. Production environments should leave `ALLOW_DEV_ENDPOINTS=false` or unset. Formal APIs such as `/api/topics`, `/api/user-settings`, and `/api/favorites` are not affected by this guard.

Smoke write metadata uses the existing `topics` table and does not add new schema. Smoke topics must include:

- `topics.source`: `rss_smoke_test`, `podcast_smoke_test`, or `dcard_smoke_test`
- `topics.topic_key` prefix: `rss-smoke-`, `podcast-smoke-`, or `dcard-smoke-`
- `topics.payload.smokeBatchId`: generated `batch_id`
- source-specific payload metadata such as `rssIngestion`, `podcastSmokeTest`, or `dcardSmokeTest`

Rollback endpoints delete only rows that match all safety markers: expected `source`, matching `payload.smokeBatchId`, and the expected `topic_key` prefix. This prevents smoke rollback from deleting non-smoke topics even if payload metadata is malformed.

## Production Deployment Checklist

Before deploying, confirm the production environment keeps development ingestion tools disabled.

Environment variables:

- `ALLOW_DEV_ENDPOINTS` must be `false` or unset.
- `ADMIN_API_TOKEN` must be set before exposing `/admin/*` endpoints.
- `DATABASE_URL` must point to the correct production PostgreSQL database.
- Do not deploy with a local, smoke-test, staging, or personal database URL.

Dev endpoint safety:

- Production must not use `/dev/*` endpoints.
- `/dev/*` endpoints should return HTTP 403 with `status=blocked`.
- `/api/topics` must still return HTTP 200.

Ingestion status:

- RSS and Podcast smoke flows are not production ingestion.
- Do not use smoke endpoints as scheduled production jobs.
- No production scheduler is enabled yet.

Rollback and data safety:

- Smoke rollback endpoints are only for smoke topics.
- Rollback must match `source`, `payload.smokeBatchId`, and the smoke `topic_key` prefix.
- Formal production topics should not depend on smoke rollback.

Pre-deployment validation:

```text
GET /health
GET /db/status
GET /api/topics
python -m compileall backend
npm.cmd run build
cd frontend
npx.cmd tsc --noEmit
```

## Render Backend Web Service Readiness

The Flask backend can be deployed to Render as a Python Web Service.

Recommended Render backend settings:

```text
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

Required backend environment variables:

```text
DATABASE_URL=<production database URL>
ADMIN_API_TOKEN=<strong secret token>
ALLOW_DEV_ENDPOINTS=false
```

`/admin/*` endpoints are protected by `ADMIN_API_TOKEN`. Send either:

```text
Authorization: Bearer <ADMIN_API_TOKEN>
```

or:

```text
X-Admin-API-Token: <ADMIN_API_TOKEN>
```

If the token is missing or incorrect, `/admin/*` returns HTTP 401 with `status=unauthorized`.

Public health and product APIs do not require the admin token:

```text
GET /health
GET /db/status
GET /api/topics
```

Render Cron Job is not enabled yet. The backend Web Service readiness step only prepares production startup and read-only admin endpoint protection.

## Manual Scheduled Ingestion Runner MVP

The manual scheduled ingestion runner is the first non-smoke ingestion entrypoint. It does not use `/dev/*` endpoints, does not write `rss_smoke_test` or `podcast_smoke_test` topics, and does not enable a timer, cron job, or background worker yet.

It records every run in `ingestion_runs`, then writes topics through the existing `topics.topic_key` upsert path. Formal topic keys are deterministic and are generated from `source_type + source_key + title`, not from a random batch id.

The runner uses a per-source PostgreSQL advisory lock before fetching a feed. The lock name is derived from `scheduled-ingestion:{source_type}:{source_key}`. The same source cannot run twice at the same time, while different sources can run independently. If the lock is unavailable, the runner skips fetch/parse/upsert, writes an `ingestion_runs` row with `status=skipped`, stores lock metadata in `metadata.advisoryLock`, and the CLI exits with code `1`. The lock is released in a `finally` block, including failed runs.

CLI usage:

```text
python backend/run_ingestion_once.py --source rss --feed hacker-news --limit 5
python backend/run_ingestion_once.py --source podcast --feed planet-money --limit 5
python backend/run_ingestion_once.py --source rss --feed hacker-news --limit 5 --dry-run
```

Run status:

```text
GET /admin/ingestion-runs/latest
GET /admin/ingestion-runs
GET /admin/ingestion-runs?limit=5&source_type=rss&source_key=hacker-news&status=success
GET /admin/ingestion-runs/<run_id>
GET /admin/ingestion-health
```

`/admin/ingestion-runs/latest` is read-only and returns the latest `run_id`, source, status, timestamps, counts, error message, dry-run flag, and metadata. This endpoint is for observability only; it does not trigger ingestion.

`/admin/ingestion-runs` is a read-only history list. It returns the latest 20 runs by default, sorted by `started_at` newest first. Optional filters are `limit`, `source_type`, `source_key`, and `status`.

`/admin/ingestion-runs/<run_id>` is a read-only detail endpoint for one run. It returns the full run record, including `metadata` with topic keys and per-topic results when present. Missing run ids return HTTP 404 with `status=not_found`.

`/admin/ingestion-health` is a read-only diagnostic summary for scheduler readiness. It reads only `ingestion_runs`, returns the latest run, failed count in the latest 20 runs, last successful RSS and Podcast runs, the latest failed run, and a `status_summary`.

Health summary rules:

- `no_runs`: no `ingestion_runs` rows exist.
- `healthy`: latest run has `status=success` and failed count in the latest 20 runs is `0`.
- `warning`: latest run failed, or failed count in the latest 20 runs is greater than `0`.

`/admin/ingestion-health` does not trigger ingestion, does not update `topics`, and does not update `ingestion_runs`.

`ingestion_runs` stores run-level status that cannot be reliably inferred from `topics` alone, including failed fetches, skipped runs, counts, and error messages.

## Manual Ingestion Runbook

This runbook documents the temporary manual operation flow before a production scheduler exists. The Manual Scheduled Ingestion Runner is the formal runner path. It is not the `/dev/*` smoke flow, and it is not yet a timer, cron job, or background worker.

Manual execution:

```text
python backend/run_ingestion_once.py --source rss --feed hacker-news --limit 5
python backend/run_ingestion_once.py --source podcast --feed planet-money --limit 5
python backend/run_ingestion_once.py --source rss --feed hacker-news --limit 5 --dry-run
python backend/run_ingestion_once.py --source podcast --feed planet-money --limit 5 --dry-run
```

Post-run check order:

```text
GET /admin/ingestion-health
GET /admin/ingestion-runs/latest
GET /admin/ingestion-runs
GET /admin/ingestion-runs/<run_id>
GET /api/topics
```

Success criteria:

- CLI exit code is `0`.
- The new `ingestion_runs` row has `status=success`.
- `/admin/ingestion-health` does not show a new failed run.
- `/api/topics` still returns HTTP 200.
- Rerunning the same source should update or skip existing topics and should not create duplicate topic keys.

Failure handling:

- CLI exit code is `1`, or the new `ingestion_runs` row has `status=failed`.
- If `status=skipped` and `metadata.advisoryLock.reason=lock_unavailable_already_running`, another run for the same source is already active. Do not start a second copy; wait for the active run or inspect run history.
- Inspect `/admin/ingestion-runs/<run_id>` for `metadata` and `error_message`.
- Do not use `/dev/*` smoke rollback to handle formal runner topics.
- Do not manually delete formal topics as the first response; inspect the run record and source error first.

Prohibited operations:

- Do not use `/dev/*` smoke endpoints as formal ingestion.
- Do not set `ALLOW_DEV_ENDPOINTS=true` in production.
- Do not use smoke rollback endpoints for formal ingestion topics.
- Do not use `batch_id` as formal topic identity.

Once this manual runbook is stable, the next suitable phase is planning a production scheduler, cron job, or worker around the same runner and `ingestion_runs` observability path.

## Host-level Scheduler Draft

This is a draft only. Do not enable a real scheduler yet.

Scheduler MVP trigger:

- Use host-level cron or Windows Task Scheduler.
- Execute the existing CLI runner directly.
- Do not call `/dev/*` endpoints.
- Do not add an HTTP trigger.

Recommended frequency:

- RSS: every 1 hour. RSS/news feeds can change frequently, but hourly is enough for the MVP and avoids unnecessary load.
- Podcast: every 6 hours. Podcast feeds usually update less often, so a lower frequency is enough.

Runner commands:

```text
python backend/run_ingestion_once.py --source rss --feed hacker-news --limit 5
python backend/run_ingestion_once.py --source podcast --feed planet-money --limit 5
```

Windows Task Scheduler draft examples:

```text
Program/script:
python

Arguments:
backend/run_ingestion_once.py --source rss --feed hacker-news --limit 5

Start in:
D:\AI輔助全端設計班-23\專案作品
```

```text
Program/script:
python

Arguments:
backend/run_ingestion_once.py --source podcast --feed planet-money --limit 5

Start in:
D:\AI輔助全端設計班-23\專案作品
```

Cron draft examples:

```cron
0 * * * * cd /path/to/project && python backend/run_ingestion_once.py --source rss --feed hacker-news --limit 5 >> logs/ingestion-rss.log 2>&1
0 */6 * * * cd /path/to/project && python backend/run_ingestion_once.py --source podcast --feed planet-money --limit 5 >> logs/ingestion-podcast.log 2>&1
```

Prerequisites:

- `DATABASE_URL` points to the correct production database.
- `ALLOW_DEV_ENDPOINTS` is `false` or unset.
- Manual Ingestion Runbook has been verified.
- Per-source advisory lock is enabled.
- `GET /admin/ingestion-health` is available.

Post-run checks:

```text
GET /admin/ingestion-health
GET /admin/ingestion-runs/latest
GET /admin/ingestion-runs
GET /api/topics
```

Not included in this draft:

- Do not enable the scheduler yet.
- Do not add a worker queue.
- Do not add GitHub Actions scheduling.
- Do not add a hosted scheduler.
- Do not add retry, webhook, Slack, or email alerts.
- Do not use `/dev/*` as the scheduler.

Next step after this draft: enable the host-level scheduler in the deployment environment and observe it for 24-48 hours using `ingestion_runs` and `/admin/ingestion-health`.

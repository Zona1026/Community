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

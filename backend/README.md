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

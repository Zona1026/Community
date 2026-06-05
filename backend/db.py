import json
import os
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_database_url() -> str | None:
    value = os.getenv("DATABASE_URL")

    if not value or "username:password@host" in value:
        return None

    return value


def is_database_configured() -> bool:
    return get_database_url() is not None


def get_connection() -> Any:
    database_url = get_database_url()

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    try:
        import psycopg
    except ImportError as error:
        raise RuntimeError(
            "psycopg is not installed. Run `pip install -r requirements.txt`.",
        ) from error

    return psycopg.connect(database_url)


def initialize_database() -> dict[str, Any]:
    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
        }

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema_sql)
        connection.commit()

    return {"status": "ok"}


def insert_smoke_test_data() -> dict[str, Any]:
    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
        }

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO topics (topic_key, title, summary, score, source)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (topic_key)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    summary = EXCLUDED.summary,
                    score = EXCLUDED.score,
                    source = EXCLUDED.source,
                    updated_at = NOW()
                RETURNING id
                """,
                (
                    "step-2-smoke-topic",
                    "Step 2 Smoke Test Topic",
                    "PostgreSQL smoke test topic.",
                    1,
                    "backend",
                ),
            )
            topic_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO user_settings (user_key, industry, tone, keywords)
                VALUES (%s, %s, %s, %s::jsonb)
                ON CONFLICT (user_key)
                DO UPDATE SET
                    industry = EXCLUDED.industry,
                    tone = EXCLUDED.tone,
                    keywords = EXCLUDED.keywords,
                    updated_at = NOW()
                RETURNING id
                """,
                (
                    "step-2-smoke-user",
                    "AI",
                    "專業",
                    json.dumps(["AI", "創業"], ensure_ascii=False),
                ),
            )
            user_setting_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO generated_copies
                    (topic_id, tone, angle, content, provider)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    topic_id,
                    "專業",
                    "教學",
                    "Step 2 PostgreSQL smoke test generated copy.",
                    "smoke-test",
                ),
            )
            generated_copy_id = cursor.fetchone()[0]

        connection.commit()

    return {
        "status": "ok",
        "topic_id": topic_id,
        "user_setting_id": user_setting_id,
        "generated_copy_id": generated_copy_id,
    }

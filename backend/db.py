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

    from topic_repository import seed_mock_topics_for_smoke_test

    seeded_topic_count = seed_mock_topics_for_smoke_test()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO topics
                    (topic_key, title, summary, score, source, payload)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (topic_key)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    summary = EXCLUDED.summary,
                    score = EXCLUDED.score,
                    source = EXCLUDED.source,
                    payload = EXCLUDED.payload,
                    updated_at = NOW()
                RETURNING id
                """,
                (
                    "step-2-smoke-topic",
                    "Step 2 Smoke Test Topic",
                    "PostgreSQL smoke test topic.",
                    1,
                    "backend",
                    json.dumps(
                        {
                            "id": "step-2-smoke-topic",
                            "topic": "Step 2 Smoke Test Topic",
                            "score": 1,
                            "growthRate": 0,
                            "momentum": "weak",
                            "lifecycleStage": "emerging",
                            "scoreHistory": [],
                            "summary": "PostgreSQL smoke test topic.",
                            "insight": "Smoke test record for database connectivity.",
                            "source": "backend",
                            "contentCount": 1,
                            "relatedContent": [],
                            "inspirationIdeas": [],
                            "platformTags": ["backend"],
                            "topicTags": ["smoke-test"],
                            "searchText": "step 2 smoke test topic backend",
                        },
                        ensure_ascii=False,
                    ),
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

            cursor.execute(
                """
                INSERT INTO reddit_posts
                    (
                        subreddit,
                        reddit_post_id,
                        title,
                        url,
                        author,
                        score,
                        num_comments,
                        created_utc,
                        raw_json
                    )
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s::jsonb)
                ON CONFLICT (reddit_post_id)
                DO UPDATE SET
                    subreddit = EXCLUDED.subreddit,
                    title = EXCLUDED.title,
                    url = EXCLUDED.url,
                    author = EXCLUDED.author,
                    score = EXCLUDED.score,
                    num_comments = EXCLUDED.num_comments,
                    fetched_at = NOW(),
                    raw_json = EXCLUDED.raw_json
                RETURNING id
                """,
                (
                    "artificial",
                    "reddit-smoke-post",
                    "Reddit smoke test post",
                    "https://www.reddit.com/r/artificial/comments/reddit-smoke-post/",
                    "smoke-test-user",
                    10,
                    2,
                    json.dumps(
                        {
                            "id": "reddit-smoke-post",
                            "subreddit": "artificial",
                            "title": "Reddit smoke test post",
                        },
                        ensure_ascii=False,
                    ),
                ),
            )
            reddit_post_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO reddit_posts
                    (
                        subreddit,
                        reddit_post_id,
                        title,
                        url,
                        author,
                        score,
                        num_comments,
                        created_utc,
                        raw_json
                    )
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s::jsonb)
                ON CONFLICT (reddit_post_id)
                DO UPDATE SET
                    score = EXCLUDED.score,
                    num_comments = EXCLUDED.num_comments,
                    fetched_at = NOW(),
                    raw_json = EXCLUDED.raw_json
                RETURNING id, score, num_comments
                """,
                (
                    "artificial",
                    "reddit-smoke-post",
                    "Reddit smoke test post",
                    "https://www.reddit.com/r/artificial/comments/reddit-smoke-post/",
                    "smoke-test-user",
                    11,
                    3,
                    json.dumps(
                        {
                            "id": "reddit-smoke-post",
                            "subreddit": "artificial",
                            "title": "Reddit smoke test post",
                            "updated": True,
                        },
                        ensure_ascii=False,
                    ),
                ),
            )
            reddit_post_row = cursor.fetchone()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM reddit_posts
                WHERE reddit_post_id = %s
                """,
                ("reddit-smoke-post",),
            )
            reddit_post_count = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO rss_items
                    (
                        source_name,
                        feed_url,
                        item_guid,
                        title,
                        link,
                        author,
                        published_at,
                        summary,
                        raw_json
                    )
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s::jsonb)
                ON CONFLICT (item_guid)
                DO UPDATE SET
                    source_name = EXCLUDED.source_name,
                    feed_url = EXCLUDED.feed_url,
                    title = EXCLUDED.title,
                    link = EXCLUDED.link,
                    author = EXCLUDED.author,
                    published_at = EXCLUDED.published_at,
                    fetched_at = NOW(),
                    summary = EXCLUDED.summary,
                    raw_json = EXCLUDED.raw_json
                RETURNING id
                """,
                (
                    "Hacker News",
                    "https://news.ycombinator.com/rss",
                    "rss-smoke-item",
                    "RSS smoke test item",
                    "https://example.com/rss-smoke-item",
                    "smoke-test-author",
                    "Initial RSS smoke summary.",
                    json.dumps(
                        {
                            "guid": "rss-smoke-item",
                            "title": "RSS smoke test item",
                        },
                        ensure_ascii=False,
                    ),
                ),
            )
            rss_item_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO rss_items
                    (
                        source_name,
                        feed_url,
                        item_guid,
                        title,
                        link,
                        author,
                        published_at,
                        summary,
                        raw_json
                    )
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s::jsonb)
                ON CONFLICT (item_guid)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    link = EXCLUDED.link,
                    author = EXCLUDED.author,
                    published_at = EXCLUDED.published_at,
                    fetched_at = NOW(),
                    summary = EXCLUDED.summary,
                    raw_json = EXCLUDED.raw_json
                RETURNING id, summary
                """,
                (
                    "Hacker News",
                    "https://news.ycombinator.com/rss",
                    "rss-smoke-item",
                    "RSS smoke test item",
                    "https://example.com/rss-smoke-item",
                    "smoke-test-author",
                    "Updated RSS smoke summary.",
                    json.dumps(
                        {
                            "guid": "rss-smoke-item",
                            "title": "RSS smoke test item",
                            "updated": True,
                        },
                        ensure_ascii=False,
                    ),
                ),
            )
            rss_item_row = cursor.fetchone()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM rss_items
                WHERE item_guid = %s
                """,
                ("rss-smoke-item",),
            )
            rss_item_count = cursor.fetchone()[0]

        connection.commit()

    return {
        "status": "ok",
        "topic_id": topic_id,
        "user_setting_id": user_setting_id,
        "generated_copy_id": generated_copy_id,
        "seeded_topic_count": seeded_topic_count,
        "reddit_post_id": reddit_post_id,
        "reddit_post_unique_count": reddit_post_count,
        "reddit_post_score": reddit_post_row[1],
        "reddit_post_num_comments": reddit_post_row[2],
        "rss_item_id": rss_item_id,
        "rss_item_unique_count": rss_item_count,
        "rss_item_summary": rss_item_row[1],
    }


def run_rss_upsert_smoke_test() -> dict[str, Any]:
    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
        }

    smoke_item_guid = "rss-smoke-test-guid"

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, fetched_at
                FROM rss_items
                WHERE item_guid = %s
                """,
                (smoke_item_guid,),
            )
            previous_row = cursor.fetchone()

            cursor.execute(
                """
                INSERT INTO rss_items
                    (
                        source_name,
                        feed_url,
                        item_guid,
                        title,
                        link,
                        author,
                        published_at,
                        summary,
                        raw_json
                    )
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s::jsonb)
                ON CONFLICT (item_guid)
                DO NOTHING
                RETURNING id, item_guid, title, fetched_at
                """,
                (
                    "RSS Upsert Smoke",
                    "https://example.com/rss-upsert-smoke.xml",
                    smoke_item_guid,
                    "RSS upsert smoke inserted title",
                    "https://example.com/rss-upsert-smoke",
                    "smoke-test-author",
                    "Initial RSS upsert smoke summary.",
                    json.dumps(
                        {
                            "guid": smoke_item_guid,
                            "stage": "insert",
                        },
                        ensure_ascii=False,
                    ),
                ),
            )
            inserted_row = cursor.fetchone()

            cursor.execute(
                """
                INSERT INTO rss_items
                    (
                        source_name,
                        feed_url,
                        item_guid,
                        title,
                        link,
                        author,
                        published_at,
                        summary,
                        raw_json
                    )
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s::jsonb)
                ON CONFLICT (item_guid)
                DO UPDATE SET
                    source_name = EXCLUDED.source_name,
                    feed_url = EXCLUDED.feed_url,
                    title = EXCLUDED.title,
                    link = EXCLUDED.link,
                    author = EXCLUDED.author,
                    published_at = EXCLUDED.published_at,
                    fetched_at = clock_timestamp(),
                    summary = EXCLUDED.summary,
                    raw_json = EXCLUDED.raw_json
                RETURNING id, item_guid, title, fetched_at
                """,
                (
                    "RSS Upsert Smoke",
                    "https://example.com/rss-upsert-smoke.xml",
                    smoke_item_guid,
                    "RSS upsert smoke updated title",
                    "https://example.com/rss-upsert-smoke",
                    "smoke-test-author",
                    "Updated RSS upsert smoke summary.",
                    json.dumps(
                        {
                            "guid": smoke_item_guid,
                            "stage": "update",
                            "updated": True,
                        },
                        ensure_ascii=False,
                    ),
                ),
            )
            updated_row = cursor.fetchone()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM rss_items
                WHERE item_guid = %s
                """,
                (smoke_item_guid,),
            )
            unique_row_count = cursor.fetchone()[0]

        connection.commit()

    inserted = inserted_row is not None
    final_row_id = updated_row[0]
    final_item_guid = updated_row[1]
    final_title = updated_row[2]
    final_fetched_at = updated_row[3]
    previous_fetched_at = previous_row[2] if previous_row else (
        inserted_row[3] if inserted_row else None
    )
    fetched_at_updated = (
        previous_fetched_at is not None
        and final_fetched_at != previous_fetched_at
    )

    return {
        "status": "ok" if unique_row_count == 1 else "failed",
        "inserted": inserted,
        "updated": True,
        "final_row_id": final_row_id,
        "final_item_guid": final_item_guid,
        "final_title": final_title,
        "unique_row_count": unique_row_count,
        "unique_constraint_ok": unique_row_count == 1,
        "fetched_at_updated": fetched_at_updated,
        "reason": None if unique_row_count == 1 else "rss_items item_guid was duplicated.",
    }


def upsert_rss_items(normalized_items: list[dict[str, Any]]) -> dict[str, Any]:
    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
        }

    inserted_count = 0
    updated_count = 0
    error_count = 0
    errors: list[dict[str, Any]] = []

    with get_connection() as connection:
        with connection.cursor() as cursor:
            for index, item in enumerate(normalized_items):
                try:
                    cursor.execute(
                        """
                        INSERT INTO rss_items
                            (
                                source_name,
                                feed_url,
                                item_guid,
                                title,
                                link,
                                author,
                                published_at,
                                fetched_at,
                                summary,
                                raw_json
                            )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                        ON CONFLICT (item_guid)
                        DO NOTHING
                        RETURNING id
                        """,
                        (
                            item["source_name"],
                            item["feed_url"],
                            item["item_guid"],
                            item["title"],
                            item["link"],
                            item["author"],
                            item["published_at"],
                            item["fetched_at"],
                            item["summary"],
                            json.dumps(item["raw_json"], ensure_ascii=False),
                        ),
                    )
                    inserted_row = cursor.fetchone()

                    if inserted_row is not None:
                        inserted_count += 1
                        connection.commit()
                        continue

                    cursor.execute(
                        """
                        UPDATE rss_items
                        SET
                            source_name = %s,
                            feed_url = %s,
                            title = %s,
                            link = %s,
                            author = %s,
                            published_at = %s,
                            fetched_at = %s,
                            summary = %s,
                            raw_json = %s::jsonb
                        WHERE item_guid = %s
                        RETURNING id
                        """,
                        (
                            item["source_name"],
                            item["feed_url"],
                            item["title"],
                            item["link"],
                            item["author"],
                            item["published_at"],
                            item["fetched_at"],
                            item["summary"],
                            json.dumps(item["raw_json"], ensure_ascii=False),
                            item["item_guid"],
                        ),
                    )
                    updated_row = cursor.fetchone()

                    if updated_row is None:
                        raise RuntimeError("RSS item upsert did not return a row.")

                    updated_count += 1
                    connection.commit()
                except Exception as item_error:
                    connection.rollback()
                    error_count += 1

                    if len(errors) < 3:
                        errors.append(
                            {
                                "index": index,
                                "item_guid": item.get("item_guid", ""),
                                "error": str(item_error),
                            },
                        )

    return {
        "status": "ok" if error_count == 0 else "partial",
        "inserted_count": inserted_count,
        "updated_count": updated_count,
        "error_count": error_count,
        "errors": errors,
    }


def _serialize_datetime(value: Any) -> str | None:
    if value is None:
        return None

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return str(value)


def get_rss_ingestion_status(limit: int = 10) -> dict[str, Any]:
    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "total_count": 0,
            "recent_items_count": 0,
            "latest_fetched_at": None,
            "latest_published_at": None,
            "items": [],
        }

    safe_limit = min(max(1, limit), 10)

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM rss_items")
                total_count = cursor.fetchone()[0]

                cursor.execute(
                    """
                    SELECT MAX(fetched_at), MAX(published_at)
                    FROM rss_items
                    """,
                )
                latest_fetched_at, latest_published_at = cursor.fetchone()

                cursor.execute(
                    """
                    SELECT
                        id,
                        source_name,
                        feed_url,
                        item_guid,
                        title,
                        link,
                        author,
                        published_at,
                        fetched_at
                    FROM rss_items
                    ORDER BY fetched_at DESC, id DESC
                    LIMIT %s
                    """,
                    (safe_limit,),
                )
                rows = cursor.fetchall()
    except Exception as status_error:
        return {
            "status": "failed",
            "reason": "RSS ingestion status could not be read from the database.",
            "error": str(status_error),
            "total_count": 0,
            "recent_items_count": 0,
            "latest_fetched_at": None,
            "latest_published_at": None,
            "items": [],
        }

    items = [
        {
            "id": row[0],
            "source_name": row[1],
            "feed_url": row[2],
            "item_guid": row[3],
            "title": row[4],
            "link": row[5],
            "author": row[6],
            "published_at": _serialize_datetime(row[7]),
            "fetched_at": _serialize_datetime(row[8]),
        }
        for row in rows
    ]

    return {
        "status": "ok",
        "total_count": total_count,
        "recent_items_count": len(items),
        "latest_fetched_at": _serialize_datetime(latest_fetched_at),
        "latest_published_at": _serialize_datetime(latest_published_at),
        "items": items,
    }


def get_rss_topic_candidates(limit: int = 10) -> dict[str, Any]:
    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "total_count": 0,
            "requested_limit": limit,
            "candidates_count": 0,
            "candidates": [],
        }

    safe_limit = min(max(0, limit), 50)

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM rss_items")
                total_count = cursor.fetchone()[0]

                cursor.execute(
                    """
                    SELECT
                        id,
                        source_name,
                        feed_url,
                        item_guid,
                        title,
                        link,
                        author,
                        published_at,
                        fetched_at,
                        summary
                    FROM rss_items
                    ORDER BY fetched_at DESC, id DESC
                    LIMIT %s
                    """,
                    (safe_limit,),
                )
                rows = cursor.fetchall()
    except Exception as candidates_error:
        return {
            "status": "failed",
            "reason": "RSS topic candidates could not be read from the database.",
            "error": str(candidates_error),
            "total_count": 0,
            "requested_limit": safe_limit,
            "candidates_count": 0,
            "candidates": [],
        }

    candidates = []

    for row in rows:
        summary = row[9] or ""
        title = row[4] or ""
        evidence_text = summary.strip() or title

        candidates.append(
            {
                "sourceItemId": row[0],
                "sourceType": "rss",
                "title": title,
                "summary": summary,
                "sourceName": row[1],
                "sourceUrl": row[5],
                "publishedAt": _serialize_datetime(row[7]),
                "candidateTopic": title,
                "evidenceText": evidence_text,
                "scoreBasis": {
                    "publishedAt": _serialize_datetime(row[7]),
                    "fetchedAt": _serialize_datetime(row[8]),
                    "sourceName": row[1],
                    "hasSummary": bool(summary.strip()),
                    "hasAuthor": bool((row[6] or "").strip()),
                    "itemGuid": row[3],
                    "feedUrl": row[2],
                },
            },
        )

    return {
        "status": "ok",
        "total_count": total_count,
        "requested_limit": safe_limit,
        "candidates_count": len(candidates),
        "candidates": candidates,
    }

import hashlib
import json
import os
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from text_utils import clean_html_to_text


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


def _normalize_topic_group_key(title: str) -> str:
    return " ".join(title.strip().lower().split())


def get_topic_candidate_groups(limit: int = 10) -> dict[str, Any]:
    candidates_result = get_rss_topic_candidates(limit)

    if candidates_result["status"] != "ok":
        return {
            **candidates_result,
            "totalCandidates": 0,
            "filteredCount": 0,
            "groupCount": 0,
            "groups": [],
        }

    candidates = candidates_result["candidates"]
    seen_item_guids: set[str] = set()
    filtered_count = 0
    groups_by_key: dict[str, dict[str, Any]] = {}

    for candidate in candidates:
        title = candidate["title"].strip()
        link = candidate["sourceUrl"].strip()
        item_guid = candidate["scoreBasis"]["itemGuid"].strip()

        if not title or not link or item_guid in seen_item_guids:
            filtered_count += 1
            continue

        seen_item_guids.add(item_guid)
        group_key = _normalize_topic_group_key(title)

        if not group_key:
            filtered_count += 1
            continue

        if group_key not in groups_by_key:
            groups_by_key[group_key] = {
                "groupKey": group_key,
                "representativeTitle": title,
                "itemCount": 0,
                "items": [],
                "reason": "Grouped by normalized exact title match.",
            }

        groups_by_key[group_key]["items"].append(candidate)
        groups_by_key[group_key]["itemCount"] += 1

    groups = list(groups_by_key.values())

    return {
        "status": "ok",
        "total_count": candidates_result["total_count"],
        "requested_limit": candidates_result["requested_limit"],
        "totalCandidates": candidates_result["candidates_count"],
        "filteredCount": filtered_count,
        "groupCount": len(groups),
        "groups": groups,
    }


def get_grouped_topic_payload_preview(limit: int = 10) -> dict[str, Any]:
    groups_result = get_topic_candidate_groups(limit)

    if groups_result["status"] != "ok":
        return {
            **groups_result,
            "totalGroups": 0,
            "payloadCount": 0,
            "skippedGroups": 0,
            "payloads": [],
        }

    payloads: list[dict[str, Any]] = []
    skipped_groups = 0

    for group in groups_result["groups"]:
        items = group["items"]

        if not items:
            skipped_groups += 1
            continue

        representative_item = items[0]
        representative_title = group["representativeTitle"].strip()

        if not representative_title:
            skipped_groups += 1
            continue

        summary = (
            representative_item["summary"].strip()
            or representative_item["title"].strip()
        )

        payloads.append(
            {
                "title": representative_title,
                "summary": summary,
                "score": 50,
                "growthRate": 0,
                "momentum": "weak",
                "lifecycleStage": "emerging",
                "sourceType": "rss",
                "sourceName": representative_item["sourceName"],
                "sourceUrl": representative_item["sourceUrl"],
                "evidenceCount": group["itemCount"],
                "evidenceItems": items[:3],
                "rawGroupKey": group["groupKey"],
            },
        )

    return {
        "status": "ok",
        "requested_limit": groups_result["requested_limit"],
        "totalGroups": groups_result["groupCount"],
        "payloadCount": len(payloads),
        "skippedGroups": skipped_groups,
        "payloads": payloads,
    }


def _generate_topic_key(title: str, max_length: int = 80) -> str:
    title_hash = hashlib.sha1(title.encode("utf-8")).hexdigest()[:12]
    normalized_key = re.sub(r"[^a-z0-9]+", "-", title.strip().lower())
    normalized_key = re.sub(r"-+", "-", normalized_key).strip("-")

    if not normalized_key:
        return f"topic-{title_hash}"

    if len(normalized_key) <= max_length:
        return normalized_key

    prefix_length = max_length - len(title_hash) - 1
    return f"{normalized_key[:prefix_length].rstrip('-')}-{title_hash}"


def _safe_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _topics_table_has_topic_key(cursor: Any) -> bool:
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'topics'
            AND column_name = 'topic_key'
        )
        """,
    )

    return bool(cursor.fetchone()[0])


def _topics_table_has_unique_topic_key(cursor: Any) -> bool:
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.table_constraints AS table_constraints
            JOIN information_schema.key_column_usage AS key_columns
                ON table_constraints.constraint_name = key_columns.constraint_name
                AND table_constraints.table_schema = key_columns.table_schema
                AND table_constraints.table_name = key_columns.table_name
            WHERE table_constraints.table_name = 'topics'
            AND table_constraints.constraint_type IN ('UNIQUE', 'PRIMARY KEY')
            AND key_columns.column_name = 'topic_key'
            GROUP BY
                table_constraints.table_schema,
                table_constraints.table_name,
                table_constraints.constraint_name
            HAVING COUNT(*) = 1
        )
        """,
    )

    return bool(cursor.fetchone()[0])


def get_topics_upsert_dry_run(limit: int = 10) -> dict[str, Any]:
    payload_result = get_grouped_topic_payload_preview(limit)
    generated_at = datetime.now(UTC).isoformat()
    topic_key_rule = {
        "source": "payload.title",
        "normalization": [
            "lowercase",
            "trim",
            "replace non-alphanumeric characters with hyphen",
            "collapse repeated hyphens",
            "trim edge hyphens",
            "cap length at 80 characters",
            "fallback to topic-{sha1-prefix} when normalized title is empty",
        ],
    }
    action_rules = {
        "insert": "Generated topicKey does not match existing topics.",
        "update": "Generated topicKey matches an existing topic.",
        "skipped": "Payload title is empty or topicKey is duplicated within the dry-run batch.",
        "blocked": "A topicKey cannot be generated or required database metadata cannot be read.",
    }

    if payload_result["status"] != "ok":
        return {
            **payload_result,
            "generatedAt": generated_at,
            "topicKeyRule": topic_key_rule,
            "actionRules": action_rules,
            "totalPayloads": 0,
            "plannedInserts": 0,
            "plannedUpdates": 0,
            "skipped": 0,
            "blocked": 0,
            "missingTopicKeySupport": False,
            "schemaSuggestion": None,
            "plan": [],
        }

    payloads = payload_result["payloads"]

    if not payloads:
        return {
            "status": "ok",
            "generatedAt": generated_at,
            "requested_limit": payload_result["requested_limit"],
            "topicKeyRule": topic_key_rule,
            "actionRules": action_rules,
            "totalPayloads": 0,
            "plannedInserts": 0,
            "plannedUpdates": 0,
            "skipped": 0,
            "blocked": 0,
            "missingTopicKeySupport": False,
            "schemaSuggestion": None,
            "plan": [],
        }

    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "generatedAt": generated_at,
            "topicKeyRule": topic_key_rule,
            "actionRules": action_rules,
            "totalPayloads": len(payloads),
            "plannedInserts": 0,
            "plannedUpdates": 0,
            "skipped": 0,
            "blocked": len(payloads),
            "missingTopicKeySupport": False,
            "schemaSuggestion": None,
            "plan": [],
        }

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                has_topic_key = _topics_table_has_topic_key(cursor)

                if has_topic_key:
                    cursor.execute("SELECT id, topic_key, title FROM topics")
                else:
                    cursor.execute("SELECT id, NULL AS topic_key, title FROM topics")

                topic_rows = cursor.fetchall()
    except Exception as dry_run_error:
        return {
            "status": "failed",
            "reason": "Topics upsert dry-run could not read existing topics.",
            "error": str(dry_run_error),
            "generatedAt": generated_at,
            "topicKeyRule": topic_key_rule,
            "actionRules": action_rules,
            "totalPayloads": len(payloads),
            "plannedInserts": 0,
            "plannedUpdates": 0,
            "skipped": 0,
            "blocked": 0,
            "missingTopicKeySupport": False,
            "schemaSuggestion": None,
            "plan": [],
        }

    missing_topic_key_support = not has_topic_key
    schema_suggestion = (
        "Add a unique text column such as topics.topic_key TEXT NOT NULL UNIQUE, "
        "backfill existing rows with normalized title keys, then use topic_key as the upsert target."
        if missing_topic_key_support
        else None
    )
    existing_topics_by_key: dict[str, dict[str, Any]] = {}

    for row in topic_rows:
        existing_key = row[1] if has_topic_key else _generate_topic_key(row[2] or "")

        if not existing_key:
            continue

        existing_topics_by_key[existing_key] = {
            "id": row[0],
            "topic_key": existing_key,
            "title": row[2],
        }

    plan: list[dict[str, Any]] = []
    planned_inserts = 0
    planned_updates = 0
    skipped_count = 0
    blocked_count = 0
    seen_topic_keys: set[str] = set()

    for payload in payloads:
        title = payload["title"].strip()
        topic_key = _generate_topic_key(title)
        existing_topic = existing_topics_by_key.get(topic_key)

        if not title:
            action = "skipped"
            reason = "Payload title is empty."
            skipped_count += 1
        elif not topic_key:
            action = "blocked"
            reason = "Could not generate a topic key from payload title."
            blocked_count += 1
        elif topic_key in seen_topic_keys:
            action = "skipped"
            reason = "Duplicate topicKey within this dry-run payload batch."
            skipped_count += 1
        elif existing_topic is not None:
            action = "update"
            reason = "topicKey matches an existing topic."
            planned_updates += 1
        else:
            action = "insert"
            reason = "topicKey does not match existing topics."
            planned_inserts += 1

        seen_topic_keys.add(topic_key)

        plan.append(
            {
                "action": action,
                "topicKey": topic_key,
                "title": title,
                "reason": reason,
                "existingTopicId": existing_topic["id"] if existing_topic else None,
                "payloadPreview": payload,
                "sourceEvidenceCount": payload["evidenceCount"],
            },
        )

    return {
        "status": "ok",
        "generatedAt": generated_at,
        "requested_limit": payload_result["requested_limit"],
        "topicKeyRule": topic_key_rule,
        "actionRules": action_rules,
        "totalPayloads": len(payloads),
        "plannedInserts": planned_inserts,
        "plannedUpdates": planned_updates,
        "skipped": skipped_count,
        "blocked": blocked_count,
        "missingTopicKeySupport": missing_topic_key_support,
        "schemaSuggestion": schema_suggestion,
        "plan": plan,
    }


def run_topics_upsert_smoke_test() -> dict[str, Any]:
    executed_at = datetime.now(UTC).isoformat()
    schema_suggestion = (
        "Ensure topics has a unique text key, for example: "
        "ALTER TABLE topics ADD COLUMN IF NOT EXISTS topic_key TEXT; "
        "CREATE UNIQUE INDEX IF NOT EXISTS topics_topic_key_key ON topics(topic_key);"
    )
    test_payloads = [
        {
            "topic_key": "topics-upsert-smoke-test",
            "title": f"Topics upsert smoke test {executed_at}",
            "summary": "Manual topics upsert smoke endpoint test payload.",
            "score": 50,
            "source": "dev-smoke",
            "payload": {
                "sourceType": "dev-smoke",
                "sourceName": "Manual Topics Upsert Smoke",
                "sourceUrl": "https://example.com/dev/topics-upsert-smoke",
                "evidenceCount": 1,
                "executedAt": executed_at,
            },
        },
    ]

    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "executedAt": executed_at,
            "insertedCount": 0,
            "updatedCount": 0,
            "skippedCount": len(test_payloads),
            "finalTopicIds": [],
            "topicKeys": [payload["topic_key"] for payload in test_payloads],
            "schemaSuggestion": None,
        }

    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    final_topic_ids: list[int] = []
    topic_keys: list[str] = []
    results: list[dict[str, Any]] = []

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                has_topic_key = _topics_table_has_topic_key(cursor)
                has_unique_topic_key = _topics_table_has_unique_topic_key(cursor)

                if not has_topic_key or not has_unique_topic_key:
                    return {
                        "status": "blocked",
                        "reason": "topics.topic_key is missing or is not uniquely constrained.",
                        "executedAt": executed_at,
                        "insertedCount": 0,
                        "updatedCount": 0,
                        "skippedCount": len(test_payloads),
                        "finalTopicIds": [],
                        "topicKeys": [payload["topic_key"] for payload in test_payloads],
                        "topicKeyColumnExists": has_topic_key,
                        "topicKeyUniqueConstraintExists": has_unique_topic_key,
                        "schemaSuggestion": schema_suggestion,
                    }

                for payload in test_payloads:
                    topic_key = payload["topic_key"]
                    topic_keys.append(topic_key)

                    cursor.execute(
                        "SELECT id FROM topics WHERE topic_key = %s",
                        (topic_key,),
                    )
                    existing_row = cursor.fetchone()
                    action = "update" if existing_row else "insert"

                    cursor.execute(
                        """
                        INSERT INTO topics (
                            topic_key,
                            title,
                            summary,
                            score,
                            source,
                            payload,
                            updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s::jsonb, NOW())
                        ON CONFLICT (topic_key) DO UPDATE SET
                            title = EXCLUDED.title,
                            summary = EXCLUDED.summary,
                            score = EXCLUDED.score,
                            source = EXCLUDED.source,
                            payload = EXCLUDED.payload,
                            updated_at = NOW()
                        RETURNING id, topic_key, title
                        """,
                        (
                            topic_key,
                            payload["title"],
                            payload["summary"],
                            payload["score"],
                            payload["source"],
                            json.dumps(payload["payload"]),
                        ),
                    )
                    row = cursor.fetchone()
                    final_topic_ids.append(row[0])

                    if action == "insert":
                        inserted_count += 1
                    else:
                        updated_count += 1

                    cursor.execute(
                        "SELECT COUNT(*) FROM topics WHERE topic_key = %s",
                        (topic_key,),
                    )
                    row_count = cursor.fetchone()[0]

                    results.append(
                        {
                            "action": action,
                            "id": row[0],
                            "topicKey": row[1],
                            "title": row[2],
                            "rowCountForTopicKey": row_count,
                            "uniqueConstraintOk": row_count == 1,
                        },
                    )
    except Exception as smoke_error:
        return {
            "status": "failed",
            "reason": "Topics upsert smoke test failed.",
            "error": str(smoke_error),
            "executedAt": executed_at,
            "insertedCount": inserted_count,
            "updatedCount": updated_count,
            "skippedCount": skipped_count,
            "finalTopicIds": final_topic_ids,
            "topicKeys": topic_keys,
            "schemaSuggestion": schema_suggestion,
        }

    return {
        "status": "ok",
        "executedAt": executed_at,
        "payloadSource": "fixed dev smoke payload",
        "insertedCount": inserted_count,
        "updatedCount": updated_count,
        "skippedCount": skipped_count,
        "finalTopicIds": final_topic_ids,
        "topicKeys": topic_keys,
        "topicKeyColumnExists": True,
        "topicKeyUniqueConstraintExists": True,
        "duplicateTopicsCreated": any(
            result["rowCountForTopicKey"] != 1 for result in results
        ),
        "results": results,
    }


def _clamp_rss_to_topics_limit(limit: int) -> int:
    return max(0, min(limit, 5))


def _topic_payload_from_grouped_payload(
    grouped_payload: dict[str, Any],
    topic_key: str,
    executed_at: str,
) -> dict[str, Any]:
    source_name = grouped_payload.get("sourceName") or "RSS"
    source_url = grouped_payload.get("sourceUrl") or ""
    evidence_count = _safe_int(grouped_payload.get("evidenceCount"), 0)
    title = str(grouped_payload.get("title") or "")
    summary = clean_html_to_text(grouped_payload.get("summary")) or title

    return {
        "id": topic_key,
        "topic": title,
        "summary": summary,
        "score": _safe_int(grouped_payload.get("score"), 50),
        "growthRate": _safe_int(grouped_payload.get("growthRate"), 0),
        "momentum": grouped_payload.get("momentum") or "weak",
        "lifecycleStage": grouped_payload.get("lifecycleStage") or "emerging",
        "source": source_name,
        "contentCount": max(evidence_count, 1),
        "relatedContent": [
            {
                "title": grouped_payload.get("title", ""),
                "url": source_url,
                "source": source_name,
            },
        ]
        if source_url
        else [],
        "platformTags": ["rss", source_name],
        "topicTags": ["rss"],
        "searchText": " ".join(
            [
                title,
                summary,
                str(source_name),
            ],
        ).lower(),
        "rssIngestion": {
            "sourceType": grouped_payload.get("sourceType", "rss"),
            "sourceName": source_name,
            "sourceUrl": source_url,
            "evidenceCount": evidence_count,
            "evidenceItems": grouped_payload.get("evidenceItems", []),
            "rawGroupKey": grouped_payload.get("rawGroupKey"),
            "executedAt": executed_at,
        },
    }


def _scheduled_topic_key(
    source_type: str,
    source_key: str,
    title: str,
) -> str:
    return _generate_topic_key(f"{source_type} {source_key} {title}")


def _scheduled_source_label(source_type: str) -> str:
    if source_type == "podcast":
        return "Podcast"

    if source_type == "rss":
        return "RSS"

    return source_type


def _scheduled_error_message(message: Any) -> str:
    return str(message or "Scheduled ingestion failed.").replace(" smoke ", " ")


def _build_scheduled_topic_payload(
    grouped_payload: dict[str, Any],
    topic_key: str,
    run_id: str,
    source_type: str,
    source_key: str,
    executed_at: str,
) -> dict[str, Any]:
    topic_payload = _topic_payload_from_grouped_payload(
        grouped_payload,
        topic_key,
        executed_at,
    )
    source_name = str(grouped_payload.get("sourceName") or _scheduled_source_label(source_type))
    source_label = _scheduled_source_label(source_type)

    topic_payload["source"] = source_name
    topic_payload["platformTags"] = [source_type, source_label, source_name]
    topic_payload["topicTags"] = [source_type, "scheduled-ingestion"]
    topic_payload["scheduledIngestion"] = {
        "runId": run_id,
        "sourceType": source_type,
        "sourceKey": source_key,
        "sourceName": source_name,
        "sourceUrl": grouped_payload.get("sourceUrl") or "",
        "evidenceCount": _safe_int(grouped_payload.get("evidenceCount"), 0),
        "executedAt": executed_at,
    }

    return topic_payload


def _record_ingestion_run(result: dict[str, Any]) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingestion_runs (
                    run_id,
                    source_type,
                    source_key,
                    status,
                    started_at,
                    finished_at,
                    fetched_count,
                    normalized_count,
                    grouped_topic_count,
                    inserted_count,
                    updated_count,
                    skipped_count,
                    error_count,
                    error_message,
                    dry_run,
                    metadata
                )
                VALUES (
                    %s, %s, %s, %s, %s::timestamptz, %s::timestamptz,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb
                )
                ON CONFLICT (run_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    finished_at = EXCLUDED.finished_at,
                    fetched_count = EXCLUDED.fetched_count,
                    normalized_count = EXCLUDED.normalized_count,
                    grouped_topic_count = EXCLUDED.grouped_topic_count,
                    inserted_count = EXCLUDED.inserted_count,
                    updated_count = EXCLUDED.updated_count,
                    skipped_count = EXCLUDED.skipped_count,
                    error_count = EXCLUDED.error_count,
                    error_message = EXCLUDED.error_message,
                    dry_run = EXCLUDED.dry_run,
                    metadata = EXCLUDED.metadata
                """,
                (
                    result["run_id"],
                    result["source_type"],
                    result["source_key"],
                    result["status"],
                    result["started_at"],
                    result.get("finished_at"),
                    _safe_int(result.get("fetched_count"), 0),
                    _safe_int(result.get("normalized_count"), 0),
                    _safe_int(result.get("grouped_topic_count"), 0),
                    _safe_int(result.get("inserted_count"), 0),
                    _safe_int(result.get("updated_count"), 0),
                    _safe_int(result.get("skipped_count"), 0),
                    _safe_int(result.get("error_count"), 0),
                    str(result.get("error_message") or ""),
                    bool(result.get("dry_run")),
                    json.dumps(result.get("metadata", {}), ensure_ascii=False),
                ),
            )
        connection.commit()


def _ingestion_run_result(
    *,
    run_id: str,
    source_type: str,
    source_key: str,
    status: str,
    started_at: str,
    finished_at: str,
    dry_run: bool,
    fetched_count: int = 0,
    normalized_count: int = 0,
    grouped_topic_count: int = 0,
    inserted_count: int = 0,
    updated_count: int = 0,
    skipped_count: int = 0,
    error_count: int = 0,
    error_message: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "source_type": source_type,
        "source_key": source_key,
        "status": status,
        "started_at": started_at,
        "finished_at": finished_at,
        "fetched_count": fetched_count,
        "normalized_count": normalized_count,
        "grouped_topic_count": grouped_topic_count,
        "inserted_count": inserted_count,
        "updated_count": updated_count,
        "skipped_count": skipped_count,
        "error_count": error_count,
        "error_message": error_message,
        "dry_run": dry_run,
        "metadata": metadata or {},
    }


def _build_scheduled_topic_draft(
    source_type: str,
    source_key: str,
    limit: int,
) -> dict[str, Any]:
    from rss_feed import build_podcast_smoke_topic_draft, build_rss_smoke_topic_draft

    if source_type == "rss":
        return build_rss_smoke_topic_draft(source_key, limit)

    if source_type == "podcast":
        return build_podcast_smoke_topic_draft(source_key, limit)

    return {
        "status": "blocked",
        "reason": "Unsupported scheduled ingestion source_type.",
        "errors": [f"Unsupported source_type: {source_type}"],
        "fetched_count": 0,
        "normalized_count": 0,
        "grouped_topic_count": 0,
        "skipped_count": 0,
        "topic_drafts": [],
    }


def _scheduled_advisory_lock_key(source_type: str, source_key: str) -> int:
    raw_key = f"scheduled-ingestion:{source_type}:{source_key}".encode("utf-8")
    digest = hashlib.sha256(raw_key).digest()

    return int.from_bytes(digest[:8], byteorder="big", signed=True)


def _scheduled_advisory_lock_metadata(
    source_type: str,
    source_key: str,
) -> dict[str, Any]:
    return {
        "lockName": f"scheduled-ingestion:{source_type}:{source_key}",
        "lockKey": _scheduled_advisory_lock_key(source_type, source_key),
        "lockType": "postgres_advisory_lock",
        "scope": "per_source",
    }


def run_scheduled_ingestion(
    source_type: str,
    source_key: str,
    limit: int = 5,
    dry_run: bool = False,
) -> dict[str, Any]:
    normalized_source_type = source_type.strip().lower()
    normalized_source_key = source_key.strip().lower()
    requested_limit = limit
    effective_limit = max(0, min(limit, 5))
    run_id = f"ingestion-{uuid.uuid4()}"
    started_at = datetime.now(UTC).isoformat()

    if not is_database_configured():
        return _ingestion_run_result(
            run_id=run_id,
            source_type=normalized_source_type,
            source_key=normalized_source_key,
            status="skipped",
            started_at=started_at,
            finished_at=datetime.now(UTC).isoformat(),
            dry_run=dry_run,
            error_count=1,
            error_message="DATABASE_URL is not configured.",
            metadata={
                "requestedLimit": requested_limit,
                "effectiveLimit": effective_limit,
            },
        )

    try:
        initialize_database()
    except Exception as init_error:
        return _ingestion_run_result(
            run_id=run_id,
            source_type=normalized_source_type,
            source_key=normalized_source_key,
            status="failed",
            started_at=started_at,
            finished_at=datetime.now(UTC).isoformat(),
            dry_run=dry_run,
            error_count=1,
            error_message=f"Database initialization failed: {init_error}",
            metadata={
                "requestedLimit": requested_limit,
                "effectiveLimit": effective_limit,
            },
        )

    advisory_lock = _scheduled_advisory_lock_metadata(
        normalized_source_type,
        normalized_source_key,
    )
    lock_connection = None
    lock_acquired = False
    draft_result: dict[str, Any] = {}
    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    topic_keys: list[str] = []
    final_topic_ids: list[int] = []
    results: list[dict[str, Any]] = []

    try:
        lock_connection = get_connection()

        with lock_connection.cursor() as cursor:
            cursor.execute(
                "SELECT pg_try_advisory_lock(%s)",
                (advisory_lock["lockKey"],),
            )
            lock_acquired = bool(cursor.fetchone()[0])

        if not lock_acquired:
            result = _ingestion_run_result(
                run_id=run_id,
                source_type=normalized_source_type,
                source_key=normalized_source_key,
                status="skipped",
                started_at=started_at,
                finished_at=datetime.now(UTC).isoformat(),
                dry_run=dry_run,
                error_count=1,
                error_message=(
                    "Scheduled ingestion lock unavailable; another run is "
                    "already active for this source."
                ),
                metadata={
                    "requestedLimit": requested_limit,
                    "effectiveLimit": effective_limit,
                    "advisoryLock": {
                        **advisory_lock,
                        "acquired": False,
                        "reason": "lock_unavailable_already_running",
                    },
                },
            )
            _record_ingestion_run(result)
            return result

        draft_result = _build_scheduled_topic_draft(
            normalized_source_type,
            normalized_source_key,
            effective_limit,
        )

        if draft_result["status"] != "ok":
            result = _ingestion_run_result(
                run_id=run_id,
                source_type=normalized_source_type,
                source_key=normalized_source_key,
                status="failed",
                started_at=started_at,
                finished_at=datetime.now(UTC).isoformat(),
                dry_run=dry_run,
                fetched_count=_safe_int(draft_result.get("fetched_count"), 0),
                normalized_count=_safe_int(draft_result.get("normalized_count"), 0),
                grouped_topic_count=_safe_int(draft_result.get("grouped_topic_count"), 0),
                skipped_count=_safe_int(draft_result.get("skipped_count"), 0),
                error_count=max(1, len(draft_result.get("errors", []))),
                error_message=_scheduled_error_message(draft_result.get("reason")),
                metadata={
                    "requestedLimit": requested_limit,
                    "effectiveLimit": effective_limit,
                    "feedSource": draft_result.get("feed_source"),
                    "feedUrl": draft_result.get("feed_url"),
                    "errors": draft_result.get("errors", []),
                    "advisoryLock": {
                        **advisory_lock,
                        "acquired": True,
                    },
                },
            )
            _record_ingestion_run(result)
            return result

        topic_drafts = draft_result.get("topic_drafts", [])[:effective_limit]
        skipped_count = _safe_int(draft_result.get("skipped_count"), 0)
        seen_topic_keys: set[str] = set()
        executed_at = datetime.now(UTC).isoformat()

        with get_connection() as connection:
            with connection.cursor() as cursor:
                has_topic_key = _topics_table_has_topic_key(cursor)
                has_unique_topic_key = _topics_table_has_unique_topic_key(cursor)

                if not has_topic_key or not has_unique_topic_key:
                    result = _ingestion_run_result(
                        run_id=run_id,
                        source_type=normalized_source_type,
                        source_key=normalized_source_key,
                        status="blocked",
                        started_at=started_at,
                        finished_at=datetime.now(UTC).isoformat(),
                        dry_run=dry_run,
                        fetched_count=_safe_int(draft_result.get("fetched_count"), 0),
                        normalized_count=_safe_int(draft_result.get("normalized_count"), 0),
                        grouped_topic_count=_safe_int(draft_result.get("grouped_topic_count"), 0),
                        skipped_count=len(topic_drafts),
                        error_count=1,
                        error_message="topics.topic_key is missing or is not uniquely constrained.",
                        metadata={
                            "requestedLimit": requested_limit,
                            "effectiveLimit": effective_limit,
                            "topicKeyColumnExists": has_topic_key,
                            "topicKeyUniqueConstraintExists": has_unique_topic_key,
                            "advisoryLock": {
                                **advisory_lock,
                                "acquired": True,
                            },
                        },
                    )
                    _record_ingestion_run(result)
                    return result

                for draft in topic_drafts:
                    title = str(draft.get("title") or "").strip()
                    topic_key = _scheduled_topic_key(
                        normalized_source_type,
                        normalized_source_key,
                        title,
                    )
                    evidence_count = _safe_int(draft.get("evidenceCount"), 0)

                    if not title or not topic_key:
                        skipped_count += 1
                        results.append(
                            {
                                "action": "skipped",
                                "topicKey": topic_key,
                                "title": title,
                                "reason": "Draft title or generated topic key is empty.",
                                "sourceEvidenceCount": evidence_count,
                            },
                        )
                        continue

                    if topic_key in seen_topic_keys:
                        skipped_count += 1
                        results.append(
                            {
                                "action": "skipped",
                                "topicKey": topic_key,
                                "title": title,
                                "reason": "Duplicate topicKey within this ingestion run.",
                                "sourceEvidenceCount": evidence_count,
                            },
                        )
                        continue

                    seen_topic_keys.add(topic_key)
                    topic_keys.append(topic_key)

                    cursor.execute(
                        "SELECT id FROM topics WHERE topic_key = %s",
                        (topic_key,),
                    )
                    existing_row = cursor.fetchone()
                    action = "update" if existing_row else "insert"
                    topic_payload = _build_scheduled_topic_payload(
                        draft,
                        topic_key,
                        run_id,
                        normalized_source_type,
                        normalized_source_key,
                        executed_at,
                    )

                    if dry_run:
                        results.append(
                            {
                                "action": action,
                                "topicKey": topic_key,
                                "title": title,
                                "sourceEvidenceCount": evidence_count,
                                "wouldWrite": True,
                            },
                        )
                        continue

                    cursor.execute(
                        """
                        INSERT INTO topics (
                            topic_key,
                            title,
                            summary,
                            score,
                            source,
                            payload,
                            updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s::jsonb, NOW())
                        ON CONFLICT (topic_key) DO UPDATE SET
                            title = EXCLUDED.title,
                            summary = EXCLUDED.summary,
                            score = EXCLUDED.score,
                            source = EXCLUDED.source,
                            payload = EXCLUDED.payload,
                            updated_at = NOW()
                        RETURNING id, topic_key, title
                        """,
                        (
                            topic_key,
                            title,
                            clean_html_to_text(draft.get("summary")) or title,
                            _safe_int(draft.get("score"), 50),
                            str(draft.get("sourceName") or _scheduled_source_label(normalized_source_type)),
                            json.dumps(topic_payload, ensure_ascii=False),
                        ),
                    )
                    row = cursor.fetchone()
                    final_topic_ids.append(row[0])

                    if action == "insert":
                        inserted_count += 1
                    else:
                        updated_count += 1

                    cursor.execute(
                        "SELECT COUNT(*) FROM topics WHERE topic_key = %s",
                        (topic_key,),
                    )
                    row_count = cursor.fetchone()[0]

                    results.append(
                        {
                            "action": action,
                            "id": row[0],
                            "topicKey": row[1],
                            "title": row[2],
                            "sourceEvidenceCount": evidence_count,
                            "rowCountForTopicKey": row_count,
                            "uniqueConstraintOk": row_count == 1,
                        },
                    )

                connection.commit()

        result = _ingestion_run_result(
            run_id=run_id,
            source_type=normalized_source_type,
            source_key=normalized_source_key,
            status="success",
            started_at=started_at,
            finished_at=datetime.now(UTC).isoformat(),
            dry_run=dry_run,
            fetched_count=_safe_int(draft_result.get("fetched_count"), 0),
            normalized_count=_safe_int(draft_result.get("normalized_count"), 0),
            grouped_topic_count=_safe_int(draft_result.get("grouped_topic_count"), 0),
            inserted_count=inserted_count,
            updated_count=updated_count,
            skipped_count=skipped_count,
            error_count=len(draft_result.get("errors", [])),
            error_message="; ".join(draft_result.get("errors", [])),
            metadata={
                "requestedLimit": requested_limit,
                "effectiveLimit": effective_limit,
                "feedSource": draft_result.get("feed_source"),
                "feedUrl": draft_result.get("feed_url"),
                "topicKeys": topic_keys,
                "finalTopicIds": final_topic_ids,
                "duplicateTopicsCreated": any(
                    item.get("rowCountForTopicKey") != 1
                    for item in results
                    if item.get("action") in {"insert", "update"}
                ),
                "advisoryLock": {
                    **advisory_lock,
                    "acquired": True,
                },
                "results": results,
            },
        )
        _record_ingestion_run(result)

        return result
    except Exception as ingestion_error:
        result = _ingestion_run_result(
            run_id=run_id,
            source_type=normalized_source_type,
            source_key=normalized_source_key,
            status="failed",
            started_at=started_at,
            finished_at=datetime.now(UTC).isoformat(),
            dry_run=dry_run,
            fetched_count=_safe_int(draft_result.get("fetched_count"), 0),
            normalized_count=_safe_int(draft_result.get("normalized_count"), 0),
            grouped_topic_count=_safe_int(draft_result.get("grouped_topic_count"), 0),
            inserted_count=inserted_count,
            updated_count=updated_count,
            skipped_count=skipped_count,
            error_count=1,
            error_message=str(ingestion_error),
            metadata={
                "requestedLimit": requested_limit,
                "effectiveLimit": effective_limit,
                "feedSource": draft_result.get("feed_source"),
                "feedUrl": draft_result.get("feed_url"),
                "topicKeys": topic_keys,
                "finalTopicIds": final_topic_ids,
                "advisoryLock": {
                    **advisory_lock,
                    "acquired": lock_acquired,
                },
                "results": results,
            },
        )
        _record_ingestion_run(result)
        return result
    finally:
        if lock_connection is not None:
            try:
                if lock_acquired:
                    with lock_connection.cursor() as cursor:
                        cursor.execute(
                            "SELECT pg_advisory_unlock(%s)",
                            (advisory_lock["lockKey"],),
                        )
                    lock_connection.commit()
            finally:
                lock_connection.close()


def get_latest_ingestion_run() -> dict[str, Any]:
    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "run": None,
        }

    try:
        initialize_database()

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        run_id,
                        source_type,
                        source_key,
                        status,
                        started_at,
                        finished_at,
                        fetched_count,
                        normalized_count,
                        grouped_topic_count,
                        inserted_count,
                        updated_count,
                        skipped_count,
                        error_count,
                        error_message,
                        dry_run,
                        metadata
                    FROM ingestion_runs
                    ORDER BY started_at DESC, id DESC
                    LIMIT 1
                    """,
                )
                row = cursor.fetchone()
    except Exception as status_error:
        return {
            "status": "failed",
            "reason": "Latest ingestion run could not be read.",
            "error": str(status_error),
            "run": None,
        }

    if row is None:
        return {
            "status": "ok",
            "run": None,
        }

    return {
        "status": "ok",
        "run": {
            "run_id": row[0],
            "source_type": row[1],
            "source_key": row[2],
            "status": row[3],
            "started_at": _isoformat_or_none(row[4]),
            "finished_at": _isoformat_or_none(row[5]),
            "counts": {
                "fetched_count": row[6],
                "normalized_count": row[7],
                "grouped_topic_count": row[8],
                "inserted_count": row[9],
                "updated_count": row[10],
                "skipped_count": row[11],
                "error_count": row[12],
            },
            "error_message": row[13],
            "dry_run": row[14],
            "metadata": row[15],
        },
    }


def _clamp_ingestion_runs_limit(limit: int) -> int:
    return max(0, min(limit, 100))


def _ingestion_run_history_item(row: Any) -> dict[str, Any]:
    return {
        "run_id": row[0],
        "source_type": row[1],
        "source_key": row[2],
        "status": row[3],
        "started_at": _isoformat_or_none(row[4]),
        "finished_at": _isoformat_or_none(row[5]),
        "fetched_count": row[6],
        "normalized_count": row[7],
        "grouped_topic_count": row[8],
        "inserted_count": row[9],
        "updated_count": row[10],
        "skipped_count": row[11],
        "error_count": row[12],
        "error_message": row[13],
        "dry_run": row[14],
    }


def _ingestion_run_detail_item(row: Any) -> dict[str, Any]:
    return {
        **_ingestion_run_history_item(row),
        "metadata": row[15],
    }


def get_ingestion_run_history(
    limit: int = 20,
    source_type: str | None = None,
    source_key: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    requested_limit = limit
    effective_limit = _clamp_ingestion_runs_limit(limit)
    filters = {
        "source_type": (source_type or "").strip().lower(),
        "source_key": (source_key or "").strip().lower(),
        "status": (status or "").strip().lower(),
    }

    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "requested_limit": requested_limit,
            "effective_limit": effective_limit,
            "filters": filters,
            "runs_count": 0,
            "runs": [],
        }

    where_clauses: list[str] = []
    query_params: list[Any] = []

    for key, value in filters.items():
        if value:
            where_clauses.append(f"{key} = %s")
            query_params.append(value)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query_params.append(effective_limit)

    try:
        initialize_database()

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        run_id,
                        source_type,
                        source_key,
                        status,
                        started_at,
                        finished_at,
                        fetched_count,
                        normalized_count,
                        grouped_topic_count,
                        inserted_count,
                        updated_count,
                        skipped_count,
                        error_count,
                        error_message,
                        dry_run
                    FROM ingestion_runs
                    {where_sql}
                    ORDER BY started_at DESC, id DESC
                    LIMIT %s
                    """,
                    tuple(query_params),
                )
                rows = cursor.fetchall()
    except Exception as history_error:
        return {
            "status": "failed",
            "reason": "Ingestion run history could not be read.",
            "error": str(history_error),
            "requested_limit": requested_limit,
            "effective_limit": effective_limit,
            "filters": filters,
            "runs_count": 0,
            "runs": [],
        }

    runs = [_ingestion_run_history_item(row) for row in rows]

    return {
        "status": "ok",
        "requested_limit": requested_limit,
        "effective_limit": effective_limit,
        "filters": filters,
        "runs_count": len(runs),
        "runs": runs,
    }


def get_ingestion_run_detail(run_id: str) -> dict[str, Any]:
    normalized_run_id = run_id.strip()

    if not normalized_run_id:
        return {
            "status": "not_found",
            "reason": "run_id is required.",
            "run": None,
        }

    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "run": None,
        }

    try:
        initialize_database()

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        run_id,
                        source_type,
                        source_key,
                        status,
                        started_at,
                        finished_at,
                        fetched_count,
                        normalized_count,
                        grouped_topic_count,
                        inserted_count,
                        updated_count,
                        skipped_count,
                        error_count,
                        error_message,
                        dry_run,
                        metadata
                    FROM ingestion_runs
                    WHERE run_id = %s
                    LIMIT 1
                    """,
                    (normalized_run_id,),
                )
                row = cursor.fetchone()
    except Exception as detail_error:
        return {
            "status": "failed",
            "reason": "Ingestion run detail could not be read.",
            "error": str(detail_error),
            "run": None,
        }

    if row is None:
        return {
            "status": "not_found",
            "reason": "Ingestion run was not found.",
            "run_id": normalized_run_id,
            "run": None,
        }

    return {
        "status": "ok",
        "run": _ingestion_run_detail_item(row),
    }


def get_ingestion_health_summary() -> dict[str, Any]:
    recent_limit = 20

    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "latest_run": None,
            "recent_window": {"type": "latest_runs", "limit": recent_limit},
            "recent_failed_count": 0,
            "last_success_by_source_type": {
                "rss": None,
                "podcast": None,
            },
            "last_failed_run": None,
            "status_summary": "no_runs",
        }

    try:
        initialize_database()

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        run_id,
                        source_type,
                        source_key,
                        status,
                        started_at,
                        finished_at,
                        fetched_count,
                        normalized_count,
                        grouped_topic_count,
                        inserted_count,
                        updated_count,
                        skipped_count,
                        error_count,
                        error_message,
                        dry_run
                    FROM ingestion_runs
                    ORDER BY started_at DESC, id DESC
                    LIMIT %s
                    """,
                    (recent_limit,),
                )
                recent_rows = cursor.fetchall()

                cursor.execute(
                    """
                    SELECT
                        run_id,
                        source_type,
                        source_key,
                        status,
                        started_at,
                        finished_at,
                        fetched_count,
                        normalized_count,
                        grouped_topic_count,
                        inserted_count,
                        updated_count,
                        skipped_count,
                        error_count,
                        error_message,
                        dry_run
                    FROM ingestion_runs
                    WHERE status = 'failed'
                    ORDER BY started_at DESC, id DESC
                    LIMIT 1
                    """,
                )
                last_failed_row = cursor.fetchone()

                last_success_by_source_type: dict[str, dict[str, Any] | None] = {}

                for source_type in ("rss", "podcast"):
                    cursor.execute(
                        """
                        SELECT
                            run_id,
                            source_type,
                            source_key,
                            status,
                            started_at,
                            finished_at,
                            fetched_count,
                            normalized_count,
                            grouped_topic_count,
                            inserted_count,
                            updated_count,
                            skipped_count,
                            error_count,
                            error_message,
                            dry_run
                        FROM ingestion_runs
                        WHERE source_type = %s
                          AND status = 'success'
                        ORDER BY started_at DESC, id DESC
                        LIMIT 1
                        """,
                        (source_type,),
                    )
                    success_row = cursor.fetchone()
                    last_success_by_source_type[source_type] = (
                        _ingestion_run_history_item(success_row)
                        if success_row is not None
                        else None
                    )
    except Exception as health_error:
        return {
            "status": "failed",
            "reason": "Ingestion health summary could not be read.",
            "error": str(health_error),
            "latest_run": None,
            "recent_window": {"type": "latest_runs", "limit": recent_limit},
            "recent_failed_count": 0,
            "last_success_by_source_type": {
                "rss": None,
                "podcast": None,
            },
            "last_failed_run": None,
            "status_summary": "warning",
        }

    latest_run = (
        _ingestion_run_history_item(recent_rows[0])
        if recent_rows
        else None
    )
    recent_failed_count = sum(1 for row in recent_rows if row[3] == "failed")
    last_failed_run = (
        _ingestion_run_history_item(last_failed_row)
        if last_failed_row is not None
        else None
    )

    if latest_run is None:
        status_summary = "no_runs"
    elif latest_run["status"] == "success" and recent_failed_count == 0:
        status_summary = "healthy"
    else:
        status_summary = "warning"

    return {
        "status": "ok",
        "latest_run": latest_run,
        "recent_window": {"type": "latest_runs", "limit": recent_limit},
        "recent_failed_count": recent_failed_count,
        "last_success_by_source_type": last_success_by_source_type,
        "last_failed_run": last_failed_run,
        "status_summary": status_summary,
    }


def run_rss_to_topics_ingestion(limit: int = 3) -> dict[str, Any]:
    requested_limit = limit
    effective_limit = _clamp_rss_to_topics_limit(limit)
    executed_at = datetime.now(UTC).isoformat()
    schema_suggestion = (
        "Ensure topics.topic_key exists and has a unique constraint before enabling "
        "RSS-to-topics ingestion."
    )

    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "executedAt": executed_at,
            "requestedLimit": requested_limit,
            "effectiveLimit": effective_limit,
            "totalGroups": 0,
            "processedGroups": 0,
            "insertedCount": 0,
            "updatedCount": 0,
            "skippedCount": 0,
            "topicKeys": [],
            "sourceEvidenceCount": 0,
        }

    payload_result = get_grouped_topic_payload_preview(effective_limit)

    if payload_result["status"] != "ok":
        return {
            **payload_result,
            "executedAt": executed_at,
            "requestedLimit": requested_limit,
            "effectiveLimit": effective_limit,
            "processedGroups": 0,
            "insertedCount": 0,
            "updatedCount": 0,
            "skippedCount": 0,
            "topicKeys": [],
            "sourceEvidenceCount": 0,
        }

    payloads = payload_result["payloads"][:effective_limit]
    total_groups = payload_result["totalGroups"]

    if not payloads:
        return {
            "status": "ok",
            "reason": "No grouped RSS topic payloads are available. Run /dev/rss-ingest first if rss_items is empty.",
            "executedAt": executed_at,
            "requestedLimit": requested_limit,
            "effectiveLimit": effective_limit,
            "totalGroups": total_groups,
            "processedGroups": 0,
            "insertedCount": 0,
            "updatedCount": 0,
            "skippedCount": 0,
            "topicKeys": [],
            "sourceEvidenceCount": 0,
            "results": [],
        }

    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    processed_groups = 0
    source_evidence_count = 0
    topic_keys: list[str] = []
    final_topic_ids: list[int] = []
    results: list[dict[str, Any]] = []
    seen_topic_keys: set[str] = set()

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                has_topic_key = _topics_table_has_topic_key(cursor)
                has_unique_topic_key = _topics_table_has_unique_topic_key(cursor)

                if not has_topic_key or not has_unique_topic_key:
                    return {
                        "status": "blocked",
                        "reason": "topics.topic_key is missing or is not uniquely constrained.",
                        "executedAt": executed_at,
                        "requestedLimit": requested_limit,
                        "effectiveLimit": effective_limit,
                        "totalGroups": total_groups,
                        "processedGroups": 0,
                        "insertedCount": 0,
                        "updatedCount": 0,
                        "skippedCount": len(payloads),
                        "topicKeys": [],
                        "sourceEvidenceCount": 0,
                        "topicKeyColumnExists": has_topic_key,
                        "topicKeyUniqueConstraintExists": has_unique_topic_key,
                        "schemaSuggestion": schema_suggestion,
                    }

                for payload in payloads:
                    title = str(payload.get("title") or "").strip()
                    topic_key = _generate_topic_key(title)
                    evidence_count = _safe_int(payload.get("evidenceCount"), 0)

                    if not title or not topic_key:
                        skipped_count += 1
                        results.append(
                            {
                                "action": "skipped",
                                "topicKey": topic_key,
                                "title": title,
                                "reason": "Payload title or generated topic key is empty.",
                                "sourceEvidenceCount": evidence_count,
                            },
                        )
                        continue

                    if topic_key in seen_topic_keys:
                        skipped_count += 1
                        results.append(
                            {
                                "action": "skipped",
                                "topicKey": topic_key,
                                "title": title,
                                "reason": "Duplicate topicKey within this ingestion batch.",
                                "sourceEvidenceCount": evidence_count,
                            },
                        )
                        continue

                    seen_topic_keys.add(topic_key)
                    topic_keys.append(topic_key)

                    cursor.execute(
                        "SELECT id FROM topics WHERE topic_key = %s",
                        (topic_key,),
                    )
                    existing_row = cursor.fetchone()
                    action = "update" if existing_row else "insert"
                    topic_payload = _topic_payload_from_grouped_payload(
                        payload,
                        topic_key,
                        executed_at,
                    )

                    cursor.execute(
                        """
                        INSERT INTO topics (
                            topic_key,
                            title,
                            summary,
                            score,
                            source,
                            payload,
                            updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s::jsonb, NOW())
                        ON CONFLICT (topic_key) DO UPDATE SET
                            title = EXCLUDED.title,
                            summary = EXCLUDED.summary,
                            score = EXCLUDED.score,
                            source = EXCLUDED.source,
                            payload = EXCLUDED.payload,
                            updated_at = NOW()
                        RETURNING id, topic_key, title
                        """,
                        (
                            topic_key,
                            title,
                            clean_html_to_text(payload.get("summary"))
                            or str(payload.get("title") or ""),
                            _safe_int(payload.get("score"), 50),
                            str(payload.get("sourceName") or "RSS"),
                            json.dumps(topic_payload, ensure_ascii=False),
                        ),
                    )
                    row = cursor.fetchone()
                    final_topic_ids.append(row[0])
                    processed_groups += 1
                    source_evidence_count += evidence_count

                    if action == "insert":
                        inserted_count += 1
                    else:
                        updated_count += 1

                    cursor.execute(
                        "SELECT COUNT(*) FROM topics WHERE topic_key = %s",
                        (topic_key,),
                    )
                    row_count = cursor.fetchone()[0]

                    results.append(
                        {
                            "action": action,
                            "id": row[0],
                            "topicKey": row[1],
                            "title": row[2],
                            "sourceEvidenceCount": evidence_count,
                            "rowCountForTopicKey": row_count,
                            "uniqueConstraintOk": row_count == 1,
                        },
                    )
    except Exception as ingestion_error:
        return {
            "status": "failed",
            "reason": "RSS-to-topics ingestion failed.",
            "error": str(ingestion_error),
            "executedAt": executed_at,
            "requestedLimit": requested_limit,
            "effectiveLimit": effective_limit,
            "totalGroups": total_groups,
            "processedGroups": processed_groups,
            "insertedCount": inserted_count,
            "updatedCount": updated_count,
            "skippedCount": skipped_count,
            "topicKeys": topic_keys,
            "sourceEvidenceCount": source_evidence_count,
            "finalTopicIds": final_topic_ids,
            "results": results,
        }

    return {
        "status": "ok",
        "executedAt": executed_at,
        "requestedLimit": requested_limit,
        "effectiveLimit": effective_limit,
        "limitMax": 5,
        "totalGroups": total_groups,
        "processedGroups": processed_groups,
        "insertedCount": inserted_count,
        "updatedCount": updated_count,
        "skippedCount": skipped_count,
        "topicKeys": topic_keys,
        "sourceEvidenceCount": source_evidence_count,
        "finalTopicIds": final_topic_ids,
        "duplicateTopicsCreated": any(
            result.get("rowCountForTopicKey") != 1
            for result in results
            if result["action"] in {"insert", "update"}
        ),
        "results": results,
    }


def _clamp_rss_topics_status_limit(limit: int) -> int:
    return max(0, min(limit, 10))


def _isoformat_or_none(value: Any) -> str | None:
    if value is None:
        return None

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return str(value)


def get_rss_topics_status(limit: int = 10) -> dict[str, Any]:
    requested_limit = limit
    effective_limit = _clamp_rss_topics_status_limit(limit)

    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "requestedLimit": requested_limit,
            "effectiveLimit": effective_limit,
            "totalRssTopicsCount": 0,
            "recentTopicsCount": 0,
            "latestUpdatedAt": None,
            "rssGeneratedTopicRule": "topics.payload contains rssIngestion metadata.",
            "schemaGap": None,
            "topics": [],
        }

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                rss_topic_where = "payload ? 'rssIngestion'"

                cursor.execute(
                    f"""
                    SELECT COUNT(*), MAX(updated_at)
                    FROM topics
                    WHERE {rss_topic_where}
                    """,
                )
                total_count, latest_updated_at = cursor.fetchone()

                cursor.execute(
                    f"""
                    SELECT
                        id,
                        topic_key,
                        title,
                        payload -> 'rssIngestion' ->> 'sourceType' AS source_type,
                        payload -> 'rssIngestion' ->> 'sourceName' AS source_name,
                        payload -> 'rssIngestion' ->> 'sourceUrl' AS source_url,
                        payload -> 'rssIngestion' ->> 'evidenceCount' AS evidence_count,
                        created_at,
                        updated_at
                    FROM topics
                    WHERE {rss_topic_where}
                    ORDER BY updated_at DESC
                    LIMIT %s
                    """,
                    (effective_limit,),
                )
                rows = cursor.fetchall()
    except Exception as status_error:
        return {
            "status": "failed",
            "reason": "RSS topics status could not read topics.",
            "error": str(status_error),
            "requestedLimit": requested_limit,
            "effectiveLimit": effective_limit,
            "totalRssTopicsCount": 0,
            "recentTopicsCount": 0,
            "latestUpdatedAt": None,
            "rssGeneratedTopicRule": "topics.payload contains rssIngestion metadata.",
            "schemaGap": None,
            "topics": [],
        }

    topics = [
        {
            "id": row[0],
            "topic_key": row[1],
            "title": row[2],
            "source_type": row[3] or "rss",
            "source_name": row[4] or "",
            "source_url": row[5] or "",
            "evidence_count": _safe_int(row[6], 0),
            "created_at": _isoformat_or_none(row[7]),
            "updated_at": _isoformat_or_none(row[8]),
        }
        for row in rows
    ]

    return {
        "status": "ok",
        "requestedLimit": requested_limit,
        "effectiveLimit": effective_limit,
        "totalRssTopicsCount": total_count,
        "recentTopicsCount": len(topics),
        "latestUpdatedAt": _isoformat_or_none(latest_updated_at),
        "rssGeneratedTopicRule": "topics.payload contains rssIngestion metadata.",
        "schemaGap": (
            "No dedicated topics.source_type column or topic_sources table exists yet. "
            "The current read-only status uses topics.payload.rssIngestion, which is safe "
            "for topics created by the MVP RSS-to-topics ingestion endpoint."
        ),
        "topics": topics,
    }


def upsert_rss_smoke_topic_drafts(
    topic_drafts: list[dict[str, Any]],
    feed_source: str,
) -> dict[str, Any]:
    executed_at = datetime.now(UTC).isoformat()
    batch_id = f"rss-smoke-{uuid.uuid4()}"
    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    errors: list[str] = []
    topic_keys: list[str] = []
    final_topic_ids: list[int] = []
    source_evidence_count = 0
    results: list[dict[str, Any]] = []
    seen_topic_keys: set[str] = set()

    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "dry_run": False,
            "batch_id": None,
            "inserted_count": 0,
            "updated_count": 0,
            "skipped_count": len(topic_drafts),
            "errors": ["DATABASE_URL is not configured."],
            "topic_keys": [],
            "final_topic_ids": [],
            "sourceEvidenceCount": 0,
        }

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                has_topic_key = _topics_table_has_topic_key(cursor)
                has_unique_topic_key = _topics_table_has_unique_topic_key(cursor)

                if not has_topic_key or not has_unique_topic_key:
                    return {
                        "status": "blocked",
                        "reason": "topics.topic_key is missing or is not uniquely constrained.",
                        "dry_run": False,
                        "batch_id": None,
                        "inserted_count": 0,
                        "updated_count": 0,
                        "skipped_count": len(topic_drafts),
                        "errors": ["topics.topic_key is not ready for safe upsert."],
                        "topic_keys": [],
                        "final_topic_ids": [],
                        "sourceEvidenceCount": 0,
                        "topicKeyColumnExists": has_topic_key,
                        "topicKeyUniqueConstraintExists": has_unique_topic_key,
                    }

                for draft in topic_drafts:
                    title = str(draft.get("title") or "").strip()
                    base_key = _generate_topic_key(title)
                    topic_key = f"rss-smoke-{base_key}" if base_key else ""
                    evidence_count = _safe_int(draft.get("evidenceCount"), 0)

                    if not title or not topic_key:
                        skipped_count += 1
                        results.append(
                            {
                                "action": "skipped",
                                "topicKey": topic_key,
                                "title": title,
                                "reason": "Draft title or generated topic key is empty.",
                                "sourceEvidenceCount": evidence_count,
                            },
                        )
                        continue

                    if topic_key in seen_topic_keys:
                        skipped_count += 1
                        results.append(
                            {
                                "action": "skipped",
                                "topicKey": topic_key,
                                "title": title,
                                "reason": "Duplicate topicKey within this smoke batch.",
                                "sourceEvidenceCount": evidence_count,
                            },
                        )
                        continue

                    seen_topic_keys.add(topic_key)
                    topic_keys.append(topic_key)
                    source_evidence_count += evidence_count

                    cursor.execute(
                        "SELECT id FROM topics WHERE topic_key = %s",
                        (topic_key,),
                    )
                    existing_row = cursor.fetchone()
                    action = "update" if existing_row else "insert"
                    topic_payload = _topic_payload_from_grouped_payload(
                        draft,
                        topic_key,
                        executed_at,
                    )
                    topic_payload["source"] = "rss_smoke_test"
                    topic_payload["platformTags"] = ["rss", "rss_smoke_test", feed_source]
                    topic_payload["topicTags"] = ["rss", "smoke-test"]
                    topic_payload["smokeBatchId"] = batch_id
                    topic_payload["rssSmokeTest"] = {
                        "batchId": batch_id,
                        "feedSource": feed_source,
                        "executedAt": executed_at,
                        "dryRun": False,
                    }

                    cursor.execute(
                        """
                        INSERT INTO topics (
                            topic_key,
                            title,
                            summary,
                            score,
                            source,
                            payload,
                            updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s::jsonb, NOW())
                        ON CONFLICT (topic_key) DO UPDATE SET
                            title = EXCLUDED.title,
                            summary = EXCLUDED.summary,
                            score = EXCLUDED.score,
                            source = EXCLUDED.source,
                            payload = EXCLUDED.payload,
                            updated_at = NOW()
                        RETURNING id, topic_key, title
                        """,
                        (
                            topic_key,
                            title,
                            clean_html_to_text(draft.get("summary"))
                            or str(draft.get("title") or ""),
                            _safe_int(draft.get("score"), 50),
                            "rss_smoke_test",
                            json.dumps(topic_payload, ensure_ascii=False),
                        ),
                    )
                    row = cursor.fetchone()
                    final_topic_ids.append(row[0])

                    if action == "insert":
                        inserted_count += 1
                    else:
                        updated_count += 1

                    cursor.execute(
                        "SELECT COUNT(*) FROM topics WHERE topic_key = %s",
                        (topic_key,),
                    )
                    row_count = cursor.fetchone()[0]

                    results.append(
                        {
                            "action": action,
                            "id": row[0],
                            "topicKey": row[1],
                            "title": row[2],
                            "sourceEvidenceCount": evidence_count,
                            "rowCountForTopicKey": row_count,
                            "uniqueConstraintOk": row_count == 1,
                        },
                    )
    except Exception as upsert_error:
        return {
            "status": "failed",
            "reason": "RSS smoke topics upsert failed.",
            "error": str(upsert_error),
            "dry_run": False,
            "batch_id": batch_id,
            "inserted_count": inserted_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "errors": [str(upsert_error)],
            "topic_keys": topic_keys,
            "final_topic_ids": final_topic_ids,
            "sourceEvidenceCount": source_evidence_count,
            "results": results,
        }

    return {
        "status": "ok",
        "dry_run": False,
        "batch_id": batch_id,
        "inserted_count": inserted_count,
        "updated_count": updated_count,
        "skipped_count": skipped_count,
        "errors": errors,
        "topic_keys": topic_keys,
        "final_topic_ids": final_topic_ids,
        "sourceEvidenceCount": source_evidence_count,
        "duplicateTopicsCreated": any(
            result.get("rowCountForTopicKey") != 1
            for result in results
            if result["action"] in {"insert", "update"}
        ),
        "results": results,
    }


def rollback_rss_smoke_batch(batch_id: str) -> dict[str, Any]:
    normalized_batch_id = batch_id.strip()

    if not normalized_batch_id:
        return {
            "status": "failed",
            "reason": "batch_id is required.",
            "batch_id": None,
            "deleted_count": 0,
        }

    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "batch_id": normalized_batch_id,
            "deleted_count": 0,
        }

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM topics
                    WHERE source = 'rss_smoke_test'
                    AND payload ->> 'smokeBatchId' = %s
                    AND topic_key LIKE 'rss-smoke-%%'
                    RETURNING id, topic_key, title
                    """,
                    (normalized_batch_id,),
                )
                deleted_rows = cursor.fetchall()
    except Exception as rollback_error:
        return {
            "status": "failed",
            "reason": "RSS smoke rollback failed.",
            "error": str(rollback_error),
            "batch_id": normalized_batch_id,
            "deleted_count": 0,
        }

    return {
        "status": "ok",
        "batch_id": normalized_batch_id,
        "deleted_count": len(deleted_rows),
        "deleted_topics": [
            {
                "id": row[0],
                "topic_key": row[1],
                "title": row[2],
            }
            for row in deleted_rows
        ],
    }


def upsert_dcard_smoke_topic_drafts(
    topic_drafts: list[dict[str, Any]],
    feed_source: str,
) -> dict[str, Any]:
    executed_at = datetime.now(UTC).isoformat()
    batch_id = f"dcard-smoke-{uuid.uuid4()}"
    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    errors: list[str] = []
    topic_keys: list[str] = []
    final_topic_ids: list[int] = []
    source_evidence_count = 0
    results: list[dict[str, Any]] = []
    seen_topic_keys: set[str] = set()

    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "dry_run": False,
            "batch_id": None,
            "inserted_count": 0,
            "updated_count": 0,
            "skipped_count": len(topic_drafts),
            "errors": ["DATABASE_URL is not configured."],
            "topic_keys": [],
            "final_topic_ids": [],
            "sourceEvidenceCount": 0,
        }

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                has_topic_key = _topics_table_has_topic_key(cursor)
                has_unique_topic_key = _topics_table_has_unique_topic_key(cursor)

                if not has_topic_key or not has_unique_topic_key:
                    return {
                        "status": "blocked",
                        "reason": "topics.topic_key is missing or is not uniquely constrained.",
                        "dry_run": False,
                        "batch_id": None,
                        "inserted_count": 0,
                        "updated_count": 0,
                        "skipped_count": len(topic_drafts),
                        "errors": ["topics.topic_key is not ready for safe upsert."],
                        "topic_keys": [],
                        "final_topic_ids": [],
                        "sourceEvidenceCount": 0,
                        "topicKeyColumnExists": has_topic_key,
                        "topicKeyUniqueConstraintExists": has_unique_topic_key,
                    }

                for draft in topic_drafts:
                    title = str(draft.get("title") or "").strip()
                    base_key = _generate_topic_key(title)
                    topic_key = f"dcard-smoke-{base_key}" if base_key else ""
                    evidence_count = _safe_int(draft.get("evidenceCount"), 0)

                    if not title or not topic_key:
                        skipped_count += 1
                        results.append(
                            {
                                "action": "skipped",
                                "topicKey": topic_key,
                                "title": title,
                                "reason": "Draft title or generated topic key is empty.",
                                "sourceEvidenceCount": evidence_count,
                            },
                        )
                        continue

                    if topic_key in seen_topic_keys:
                        skipped_count += 1
                        results.append(
                            {
                                "action": "skipped",
                                "topicKey": topic_key,
                                "title": title,
                                "reason": "Duplicate topicKey within this smoke batch.",
                                "sourceEvidenceCount": evidence_count,
                            },
                        )
                        continue

                    seen_topic_keys.add(topic_key)
                    topic_keys.append(topic_key)
                    source_evidence_count += evidence_count

                    cursor.execute(
                        "SELECT id FROM topics WHERE topic_key = %s",
                        (topic_key,),
                    )
                    existing_row = cursor.fetchone()
                    action = "update" if existing_row else "insert"
                    topic_payload = _topic_payload_from_grouped_payload(
                        draft,
                        topic_key,
                        executed_at,
                    )
                    topic_payload["source"] = "dcard_smoke_test"
                    topic_payload["platformTags"] = [
                        "dcard",
                        "dcard_smoke_test",
                        feed_source,
                    ]
                    topic_payload["topicTags"] = ["dcard", "smoke-test"]
                    topic_payload["smokeBatchId"] = batch_id
                    topic_payload["dcardSmokeTest"] = {
                        "batchId": batch_id,
                        "feedSource": feed_source,
                        "executedAt": executed_at,
                        "dryRun": False,
                    }

                    cursor.execute(
                        """
                        INSERT INTO topics (
                            topic_key,
                            title,
                            summary,
                            score,
                            source,
                            payload,
                            updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s::jsonb, NOW())
                        ON CONFLICT (topic_key) DO UPDATE SET
                            title = EXCLUDED.title,
                            summary = EXCLUDED.summary,
                            score = EXCLUDED.score,
                            source = EXCLUDED.source,
                            payload = EXCLUDED.payload,
                            updated_at = NOW()
                        RETURNING id, topic_key, title
                        """,
                        (
                            topic_key,
                            title,
                            clean_html_to_text(draft.get("summary"))
                            or str(draft.get("title") or ""),
                            _safe_int(draft.get("score"), 50),
                            "dcard_smoke_test",
                            json.dumps(topic_payload, ensure_ascii=False),
                        ),
                    )
                    row = cursor.fetchone()
                    final_topic_ids.append(row[0])

                    if action == "insert":
                        inserted_count += 1
                    else:
                        updated_count += 1

                    cursor.execute(
                        "SELECT COUNT(*) FROM topics WHERE topic_key = %s",
                        (topic_key,),
                    )
                    row_count = cursor.fetchone()[0]

                    results.append(
                        {
                            "action": action,
                            "id": row[0],
                            "topicKey": row[1],
                            "title": row[2],
                            "sourceEvidenceCount": evidence_count,
                            "rowCountForTopicKey": row_count,
                            "uniqueConstraintOk": row_count == 1,
                        },
                    )
    except Exception as upsert_error:
        return {
            "status": "failed",
            "reason": "Dcard smoke topics upsert failed.",
            "error": str(upsert_error),
            "dry_run": False,
            "batch_id": batch_id,
            "inserted_count": inserted_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "errors": [str(upsert_error)],
            "topic_keys": topic_keys,
            "final_topic_ids": final_topic_ids,
            "sourceEvidenceCount": source_evidence_count,
            "results": results,
        }

    return {
        "status": "ok",
        "dry_run": False,
        "batch_id": batch_id,
        "inserted_count": inserted_count,
        "updated_count": updated_count,
        "skipped_count": skipped_count,
        "errors": errors,
        "topic_keys": topic_keys,
        "final_topic_ids": final_topic_ids,
        "sourceEvidenceCount": source_evidence_count,
        "duplicateTopicsCreated": any(
            result.get("rowCountForTopicKey") != 1
            for result in results
            if result["action"] in {"insert", "update"}
        ),
        "results": results,
    }


def rollback_dcard_smoke_batch(batch_id: str) -> dict[str, Any]:
    normalized_batch_id = batch_id.strip()

    if not normalized_batch_id:
        return {
            "status": "failed",
            "reason": "batch_id is required.",
            "batch_id": None,
            "deleted_count": 0,
        }

    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "batch_id": normalized_batch_id,
            "deleted_count": 0,
        }

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM topics
                    WHERE source = 'dcard_smoke_test'
                    AND payload ->> 'smokeBatchId' = %s
                    AND topic_key LIKE 'dcard-smoke-%%'
                    RETURNING id, topic_key, title
                    """,
                    (normalized_batch_id,),
                )
                deleted_rows = cursor.fetchall()
    except Exception as rollback_error:
        return {
            "status": "failed",
            "reason": "Dcard smoke rollback failed.",
            "error": str(rollback_error),
            "batch_id": normalized_batch_id,
            "deleted_count": 0,
        }

    return {
        "status": "ok",
        "batch_id": normalized_batch_id,
        "deleted_count": len(deleted_rows),
        "deleted_topics": [
            {
                "id": row[0],
                "topic_key": row[1],
                "title": row[2],
            }
            for row in deleted_rows
        ],
    }


def upsert_podcast_smoke_topic_drafts(
    topic_drafts: list[dict[str, Any]],
    feed_source: str,
) -> dict[str, Any]:
    executed_at = datetime.now(UTC).isoformat()
    batch_id = f"podcast-smoke-{uuid.uuid4()}"
    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    errors: list[str] = []
    topic_keys: list[str] = []
    final_topic_ids: list[int] = []
    source_evidence_count = 0
    results: list[dict[str, Any]] = []
    seen_topic_keys: set[str] = set()

    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "dry_run": False,
            "batch_id": None,
            "inserted_count": 0,
            "updated_count": 0,
            "skipped_count": len(topic_drafts),
            "errors": ["DATABASE_URL is not configured."],
            "topic_keys": [],
            "final_topic_ids": [],
            "sourceEvidenceCount": 0,
        }

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                has_topic_key = _topics_table_has_topic_key(cursor)
                has_unique_topic_key = _topics_table_has_unique_topic_key(cursor)

                if not has_topic_key or not has_unique_topic_key:
                    return {
                        "status": "blocked",
                        "reason": "topics.topic_key is missing or is not uniquely constrained.",
                        "dry_run": False,
                        "batch_id": None,
                        "inserted_count": 0,
                        "updated_count": 0,
                        "skipped_count": len(topic_drafts),
                        "errors": ["topics.topic_key is not ready for safe upsert."],
                        "topic_keys": [],
                        "final_topic_ids": [],
                        "sourceEvidenceCount": 0,
                        "topicKeyColumnExists": has_topic_key,
                        "topicKeyUniqueConstraintExists": has_unique_topic_key,
                    }

                for draft in topic_drafts:
                    title = str(draft.get("title") or "").strip()
                    base_key = _generate_topic_key(title)
                    topic_key = f"podcast-smoke-{base_key}" if base_key else ""
                    evidence_count = _safe_int(draft.get("evidenceCount"), 0)

                    if not title or not topic_key:
                        skipped_count += 1
                        results.append(
                            {
                                "action": "skipped",
                                "topicKey": topic_key,
                                "title": title,
                                "reason": "Draft title or generated topic key is empty.",
                                "sourceEvidenceCount": evidence_count,
                            },
                        )
                        continue

                    if topic_key in seen_topic_keys:
                        skipped_count += 1
                        results.append(
                            {
                                "action": "skipped",
                                "topicKey": topic_key,
                                "title": title,
                                "reason": "Duplicate topicKey within this smoke batch.",
                                "sourceEvidenceCount": evidence_count,
                            },
                        )
                        continue

                    seen_topic_keys.add(topic_key)
                    topic_keys.append(topic_key)
                    source_evidence_count += evidence_count

                    cursor.execute(
                        "SELECT id FROM topics WHERE topic_key = %s",
                        (topic_key,),
                    )
                    existing_row = cursor.fetchone()
                    action = "update" if existing_row else "insert"
                    topic_payload = _topic_payload_from_grouped_payload(
                        draft,
                        topic_key,
                        executed_at,
                    )
                    topic_payload["source"] = "podcast_smoke_test"
                    topic_payload["platformTags"] = [
                        "podcast",
                        "podcast_smoke_test",
                        feed_source,
                    ]
                    topic_payload["topicTags"] = ["podcast", "smoke-test"]
                    topic_payload["smokeBatchId"] = batch_id
                    topic_payload["podcastSmokeTest"] = {
                        "batchId": batch_id,
                        "feedSource": feed_source,
                        "executedAt": executed_at,
                        "dryRun": False,
                    }

                    cursor.execute(
                        """
                        INSERT INTO topics (
                            topic_key,
                            title,
                            summary,
                            score,
                            source,
                            payload,
                            updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s::jsonb, NOW())
                        ON CONFLICT (topic_key) DO UPDATE SET
                            title = EXCLUDED.title,
                            summary = EXCLUDED.summary,
                            score = EXCLUDED.score,
                            source = EXCLUDED.source,
                            payload = EXCLUDED.payload,
                            updated_at = NOW()
                        RETURNING id, topic_key, title
                        """,
                        (
                            topic_key,
                            title,
                            clean_html_to_text(draft.get("summary"))
                            or str(draft.get("title") or ""),
                            _safe_int(draft.get("score"), 50),
                            "podcast_smoke_test",
                            json.dumps(topic_payload, ensure_ascii=False),
                        ),
                    )
                    row = cursor.fetchone()
                    final_topic_ids.append(row[0])

                    if action == "insert":
                        inserted_count += 1
                    else:
                        updated_count += 1

                    cursor.execute(
                        "SELECT COUNT(*) FROM topics WHERE topic_key = %s",
                        (topic_key,),
                    )
                    row_count = cursor.fetchone()[0]

                    results.append(
                        {
                            "action": action,
                            "id": row[0],
                            "topicKey": row[1],
                            "title": row[2],
                            "sourceEvidenceCount": evidence_count,
                            "rowCountForTopicKey": row_count,
                            "uniqueConstraintOk": row_count == 1,
                        },
                    )
    except Exception as upsert_error:
        return {
            "status": "failed",
            "reason": "Podcast smoke topics upsert failed.",
            "error": str(upsert_error),
            "dry_run": False,
            "batch_id": batch_id,
            "inserted_count": inserted_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "errors": [str(upsert_error)],
            "topic_keys": topic_keys,
            "final_topic_ids": final_topic_ids,
            "sourceEvidenceCount": source_evidence_count,
            "results": results,
        }

    return {
        "status": "ok",
        "dry_run": False,
        "batch_id": batch_id,
        "inserted_count": inserted_count,
        "updated_count": updated_count,
        "skipped_count": skipped_count,
        "errors": errors,
        "topic_keys": topic_keys,
        "final_topic_ids": final_topic_ids,
        "sourceEvidenceCount": source_evidence_count,
        "duplicateTopicsCreated": any(
            result.get("rowCountForTopicKey") != 1
            for result in results
            if result["action"] in {"insert", "update"}
        ),
        "results": results,
    }


def rollback_podcast_smoke_batch(batch_id: str) -> dict[str, Any]:
    normalized_batch_id = batch_id.strip()

    if not normalized_batch_id:
        return {
            "status": "failed",
            "reason": "batch_id is required.",
            "batch_id": None,
            "deleted_count": 0,
        }

    if not is_database_configured():
        return {
            "status": "skipped",
            "reason": "DATABASE_URL is not configured.",
            "batch_id": normalized_batch_id,
            "deleted_count": 0,
        }

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM topics
                    WHERE source = 'podcast_smoke_test'
                    AND payload ->> 'smokeBatchId' = %s
                    AND topic_key LIKE 'podcast-smoke-%%'
                    RETURNING id, topic_key, title
                    """,
                    (normalized_batch_id,),
                )
                deleted_rows = cursor.fetchall()
    except Exception as rollback_error:
        return {
            "status": "failed",
            "reason": "Podcast smoke rollback failed.",
            "error": str(rollback_error),
            "batch_id": normalized_batch_id,
            "deleted_count": 0,
        }

    return {
        "status": "ok",
        "batch_id": normalized_batch_id,
        "deleted_count": len(deleted_rows),
        "deleted_topics": [
            {
                "id": row[0],
                "topic_key": row[1],
                "title": row[2],
            }
            for row in deleted_rows
        ],
    }

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from app import create_app
from db import get_connection, is_database_configured


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class AcceptanceFailure(RuntimeError):
    pass


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AcceptanceFailure(message)


def get_json(client: Any, path: str) -> tuple[int, dict[str, Any]]:
    response = client.get(path)
    return response.status_code, response.get_json() or {}


def post_json(
    client: Any,
    path: str,
    payload: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    response = client.post(path, json=payload)
    return response.status_code, response.get_json() or {}


def get_podcast_smoke_rows(topic_keys: list[str]) -> list[dict[str, Any]]:
    if not topic_keys:
        return []

    placeholders = ", ".join(["%s"] * len(topic_keys))

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                    topic_key,
                    source,
                    payload ->> 'smokeBatchId' AS batch_id,
                    payload -> 'rssIngestion' ->> 'evidenceCount' AS evidence_count,
                    updated_at
                FROM topics
                WHERE topic_key IN ({placeholders})
                ORDER BY topic_key
                """,
                tuple(topic_keys),
            )
            rows = cursor.fetchall()

    return [
        {
            "topic_key": row[0],
            "source": row[1],
            "batch_id": row[2],
            "evidence_count": int(row[3] or 0),
            "updated_at": row[4],
        }
        for row in rows
    ]


def assert_api_topics_contains_batch(client: Any, topic_keys: list[str]) -> None:
    status_code, api_topics = get_json(client, "/api/topics")
    assert_true(status_code == 200, "/api/topics did not return HTTP 200.")

    all_topics = api_topics.get("allTopics", [])
    visible_ids = {topic.get("id") for topic in all_topics}
    missing_ids = sorted(set(topic_keys) - visible_ids)

    assert_true(
        not missing_ids,
        f"/api/topics did not include podcast smoke topic ids: {missing_ids}",
    )


def assert_api_topics_excludes_batch(client: Any, topic_keys: list[str]) -> None:
    status_code, api_topics = get_json(client, "/api/topics")
    assert_true(status_code == 200, "/api/topics did not return HTTP 200.")

    all_topics = api_topics.get("allTopics", [])
    visible_ids = {topic.get("id") for topic in all_topics}
    remaining_ids = sorted(set(topic_keys) & visible_ids)

    assert_true(
        not remaining_ids,
        f"/api/topics still includes rolled-back podcast topics: {remaining_ids}",
    )


def assert_podcast_smoke_metadata(
    topic_keys: list[str],
    batch_id: str,
) -> None:
    rows = get_podcast_smoke_rows(topic_keys)

    assert_true(
        len(rows) == len(topic_keys),
        f"Expected {len(topic_keys)} podcast smoke rows, found {len(rows)}.",
    )

    for row in rows:
        assert_true(
            row["source"] == "podcast_smoke_test",
            f"Unexpected source for {row['topic_key']}: {row['source']}",
        )
        assert_true(
            row["batch_id"] == batch_id,
            f"Unexpected batch_id for {row['topic_key']}: {row['batch_id']}",
        )
        assert_true(
            row["topic_key"].startswith("podcast-smoke-"),
            f"topic_key does not use podcast-smoke prefix: {row['topic_key']}",
        )
        assert_true(
            row["evidence_count"] > 0,
            f"evidence_count is not positive for {row['topic_key']}.",
        )
        assert_true(
            row["updated_at"] is not None,
            f"updated_at is missing for {row['topic_key']}.",
        )


def run_acceptance() -> dict[str, Any]:
    if not is_database_configured():
        raise AcceptanceFailure("DATABASE_URL is required for podcast smoke acceptance.")

    os.environ.setdefault("FLASK_SKIP_DOTENV", "1")
    os.environ.setdefault("ALLOW_DEV_ENDPOINTS", "true")
    app = create_app()
    client = app.test_client()

    checks: list[str] = []

    first_status, first_write = post_json(
        client,
        "/dev/podcast-to-topics-smoke?dry_run=false",
    )
    assert_true(
        first_status == 200,
        "First podcast smoke write did not return HTTP 200.",
    )
    assert_true(first_write.get("status") == "ok", "First podcast smoke write failed.")
    assert_true(
        first_write.get("inserted_count") == 5,
        "First podcast smoke write did not insert 5 topics.",
    )

    first_topic_keys = first_write.get("topic_keys", [])
    first_batch_id = first_write.get("batch_id")
    assert_true(len(first_topic_keys) == 5, "First podcast smoke write returned wrong topic count.")
    assert_true(bool(first_batch_id), "First podcast smoke write did not return batch_id.")
    assert_api_topics_contains_batch(client, first_topic_keys)
    assert_podcast_smoke_metadata(first_topic_keys, first_batch_id)
    checks.append("/api/topics contains first podcast smoke batch.")
    checks.append("First podcast batch metadata is valid.")

    second_status, second_write = post_json(
        client,
        "/dev/podcast-to-topics-smoke?dry_run=false",
    )
    assert_true(
        second_status == 200,
        "Second podcast smoke write did not return HTTP 200.",
    )
    assert_true(second_write.get("status") == "ok", "Second podcast smoke write failed.")
    assert_true(
        second_write.get("inserted_count") == 0,
        "Second podcast smoke write inserted rows; expected upsert updates.",
    )
    assert_true(
        second_write.get("updated_count") == 5,
        "Second podcast smoke write did not update 5 existing topics.",
    )
    assert_true(
        not second_write.get("duplicateTopicsCreated"),
        "Second podcast smoke write reported duplicate topics.",
    )

    second_topic_keys = second_write.get("topic_keys", [])
    second_batch_id = second_write.get("batch_id")
    assert_true(len(second_topic_keys) == 5, "Second podcast smoke write returned wrong topic count.")
    assert_true(bool(second_batch_id), "Second podcast smoke write did not return batch_id.")
    assert_api_topics_contains_batch(client, second_topic_keys)
    assert_podcast_smoke_metadata(second_topic_keys, second_batch_id)
    checks.append("Rerun uses topic_key upsert without duplicates.")
    checks.append("Second podcast batch metadata is valid.")

    rollback_status, rollback = post_json(
        client,
        "/dev/podcast-smoke-rollback",
        {"batch_id": second_batch_id},
    )
    assert_true(rollback_status == 200, "Podcast rollback did not return HTTP 200.")
    assert_true(rollback.get("status") == "ok", "Podcast rollback failed.")
    assert_true(
        rollback.get("deleted_count") == 5,
        "Podcast rollback did not delete 5 topics.",
    )

    assert_api_topics_excludes_batch(client, second_topic_keys)
    checks.append("Rollback removes the podcast smoke batch from /api/topics.")

    return {
        "status": "ok",
        "checks": checks,
        "first_batch_id": first_batch_id,
        "second_batch_id": second_batch_id,
        "topic_keys": second_topic_keys,
    }


if __name__ == "__main__":
    result = run_acceptance()
    print(result)

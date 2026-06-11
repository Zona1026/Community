from __future__ import annotations

import os
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import rss_feed
from app import create_app
from db import get_connection, is_database_configured


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_TOPIC_DASHBOARD = (
    PROJECT_ROOT / "frontend" / "src" / "components" / "TopicDashboard.tsx"
)


class AcceptanceFailure(RuntimeError):
    pass


class FakeRssResponse:
    def __init__(
        self,
        body: bytes,
        status: int = 200,
        content_type: str = "application/rss+xml",
    ) -> None:
        self._body = body
        self.status = status
        self.headers = {"Content-Type": content_type}

    def __enter__(self) -> "FakeRssResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self, _size: int = -1) -> bytes:
        return self._body


@contextmanager
def patched_urlopen(fake_urlopen: Callable[..., Any]):
    original_urlopen = rss_feed.request.urlopen
    rss_feed.request.urlopen = fake_urlopen

    try:
        yield
    finally:
        rss_feed.request.urlopen = original_urlopen


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


def count_topics_by_keys(topic_keys: list[str]) -> int:
    if not topic_keys:
        return 0

    placeholders = ", ".join(["%s"] * len(topic_keys))

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT COUNT(*) FROM topics WHERE topic_key IN ({placeholders})",
                tuple(topic_keys),
            )
            return int(cursor.fetchone()[0])


def assert_api_topics_contains_batch(client: Any, topic_keys: list[str]) -> None:
    status_code, api_topics = get_json(client, "/api/topics")
    assert_true(status_code == 200, "/api/topics did not return HTTP 200.")

    all_topics = api_topics.get("allTopics", [])
    visible_ids = {topic.get("id") for topic in all_topics}
    missing_ids = sorted(set(topic_keys) - visible_ids)

    assert_true(
        not missing_ids,
        f"/api/topics did not include smoke topic ids: {missing_ids}",
    )


def assert_frontend_topic_list_contract() -> None:
    source = FRONTEND_TOPIC_DASHBOARD.read_text(encoding="utf-8")

    assert_true(
        "fetchDashboardTopics()" in source,
        "TopicDashboard does not fetch frontend /api/topics data.",
    )
    assert_true(
        "topics={topicsData.allTopics}" in source,
        "TopicDashboard topic list is not wired to topicsData.allTopics.",
    )


def assert_error_case(
    client: Any,
    label: str,
    fake_urlopen: Callable[..., Any],
    expected_status: str,
) -> None:
    with patched_urlopen(fake_urlopen):
        status_code, payload = get_json(client, "/dev/rss-preview")

    assert_true(status_code in {200, 502}, f"{label} returned HTTP {status_code}.")
    assert_true(
        payload.get("status") == expected_status,
        f"{label} returned status={payload.get('status')}, expected {expected_status}.",
    )
    assert_true(
        bool(payload.get("reason") or payload.get("errors")),
        f"{label} did not return a readable reason or errors.",
    )


def run_acceptance() -> dict[str, Any]:
    if not is_database_configured():
        raise AcceptanceFailure("DATABASE_URL is required for RSS smoke acceptance.")

    os.environ.setdefault("FLASK_SKIP_DOTENV", "1")
    os.environ.setdefault("ALLOW_DEV_ENDPOINTS", "true")
    app = create_app()
    client = app.test_client()

    checks: list[str] = []

    first_status, first_write = post_json(
        client,
        "/dev/rss-to-topics-smoke?dry_run=false",
    )
    assert_true(first_status == 200, "First RSS smoke write did not return HTTP 200.")
    assert_true(first_write.get("status") == "ok", "First RSS smoke write failed.")

    first_topic_keys = first_write.get("topic_keys", [])
    assert_true(len(first_topic_keys) == 5, "First RSS smoke write did not process 5 topics.")
    assert_api_topics_contains_batch(client, first_topic_keys)
    checks.append("/api/topics contains first RSS smoke batch.")

    assert_frontend_topic_list_contract()
    checks.append("Frontend topic list is wired to /api/topics allTopics data.")

    second_status, second_write = post_json(
        client,
        "/dev/rss-to-topics-smoke?dry_run=false",
    )
    assert_true(second_status == 200, "Second RSS smoke write did not return HTTP 200.")
    assert_true(second_write.get("status") == "ok", "Second RSS smoke write failed.")
    assert_true(
        second_write.get("inserted_count") == 0,
        "Second RSS smoke write inserted rows; expected upsert updates.",
    )
    assert_true(
        second_write.get("updated_count") == 5,
        "Second RSS smoke write did not update 5 existing topics.",
    )

    second_topic_keys = second_write.get("topic_keys", [])
    assert_true(
        count_topics_by_keys(second_topic_keys) == len(second_topic_keys),
        "Duplicate topics were created for smoke topic keys.",
    )
    checks.append("Rerun uses topic_key upsert without duplicates.")

    empty_feed = (
        b"<?xml version='1.0' encoding='UTF-8'?>"
        b"<rss><channel><title>Empty Feed</title></channel></rss>"
    )
    assert_error_case(
        client,
        "empty RSS",
        lambda *_args, **_kwargs: FakeRssResponse(empty_feed),
        "ok",
    )
    assert_error_case(
        client,
        "bad RSS XML",
        lambda *_args, **_kwargs: FakeRssResponse(b"<rss><channel>"),
        "failed",
    )
    assert_error_case(
        client,
        "timeout RSS",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(TimeoutError()),
        "failed",
    )

    non_whitelist_status, non_whitelist = get_json(
        client,
        "/dev/rss-preview?feed=not-allowed",
    )
    assert_true(non_whitelist_status == 200, "Non-whitelist feed did not return HTTP 200.")
    assert_true(
        non_whitelist.get("status") == "blocked",
        "Non-whitelist feed was not blocked.",
    )
    assert_true(
        bool(non_whitelist.get("reason")),
        "Non-whitelist feed did not return a readable reason.",
    )
    checks.append("Empty, malformed, timeout, and non-whitelist feeds are readable.")

    batch_id = second_write.get("batch_id")
    assert_true(bool(batch_id), "Second RSS smoke write did not return batch_id.")

    rollback_status, rollback = post_json(
        client,
        "/dev/rss-smoke-rollback",
        {"batch_id": batch_id},
    )
    assert_true(rollback_status == 200, "Rollback did not return HTTP 200.")
    assert_true(rollback.get("status") == "ok", "Rollback failed.")
    assert_true(rollback.get("deleted_count") == 5, "Rollback did not delete 5 topics.")

    status_code, api_topics_after_rollback = get_json(client, "/api/topics")
    assert_true(status_code == 200, "/api/topics failed after rollback.")
    all_topics = api_topics_after_rollback.get("allTopics", [])
    visible_ids = {topic.get("id") for topic in all_topics}
    remaining_ids = sorted(set(second_topic_keys) & visible_ids)
    assert_true(
        not remaining_ids,
        f"/api/topics still includes rolled-back batch topics: {remaining_ids}",
    )
    checks.append("Rollback removes the smoke batch from /api/topics.")

    return {
        "status": "ok",
        "checks": checks,
        "first_batch_id": first_write.get("batch_id"),
        "second_batch_id": batch_id,
        "topic_keys": second_topic_keys,
    }


if __name__ == "__main__":
    result = run_acceptance()
    print(result)

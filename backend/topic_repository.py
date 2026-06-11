from __future__ import annotations

import json
from typing import Any

from db import get_connection, initialize_database, is_database_configured
from mock_topics import get_mock_topics


def _safe_int(value: Any, fallback: int = 0) -> int:
    if isinstance(value, bool):
        return fallback

    if isinstance(value, int):
        return value

    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _decode_payload(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return {}

        return decoded if isinstance(decoded, dict) else {}

    return {}


def _topic_from_row(row: Any) -> dict[str, Any]:
    topic_key, title, summary, score, source, payload = row
    topic_payload = _decode_payload(payload)

    return {
        "id": str(topic_payload.get("id") or topic_key),
        "topic": str(topic_payload.get("topic") or title),
        "score": _safe_int(topic_payload.get("score"), _safe_int(score)),
        "growthRate": _safe_int(topic_payload.get("growthRate")),
        "momentum": topic_payload.get("momentum")
        if topic_payload.get("momentum") in {"rising", "stable", "weak"}
        else "weak",
        "lifecycleStage": topic_payload.get("lifecycleStage")
        if topic_payload.get("lifecycleStage")
        in {"emerging", "growing", "mainstream", "declining"}
        else "emerging",
        "scoreHistory": _safe_list(topic_payload.get("scoreHistory")),
        "summary": str(topic_payload.get("summary") or summary),
        "insight": str(topic_payload.get("insight") or ""),
        "source": str(topic_payload.get("source") or source),
        "contentCount": _safe_int(topic_payload.get("contentCount"), 1),
        "relatedContent": _safe_list(topic_payload.get("relatedContent")),
        "inspirationIdeas": _safe_list(topic_payload.get("inspirationIdeas")),
        "platformTags": _safe_list(topic_payload.get("platformTags")) or [str(source)],
        "topicTags": _safe_list(topic_payload.get("topicTags")),
        "searchText": str(
            topic_payload.get("searchText")
            or f"{title} {summary} {source}".lower()
        ),
    }


def get_topics_from_database() -> list[dict[str, Any]]:
    if not is_database_configured():
        return []

    try:
        initialize_database()

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT topic_key, title, summary, score, source, payload
                    FROM topics
                    ORDER BY score DESC, updated_at DESC
                    """,
                )
                rows = cursor.fetchall()
    except Exception:
        return []

    return [_topic_from_row(row) for row in rows]


def find_topic_from_database(topic_id: str) -> dict[str, Any] | None:
    if not is_database_configured():
        return None

    try:
        initialize_database()

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT topic_key, title, summary, score, source, payload
                    FROM topics
                    WHERE topic_key = %s OR payload ->> 'id' = %s
                    LIMIT 1
                    """,
                    (topic_id, topic_id),
                )
                row = cursor.fetchone()
    except Exception:
        return None

    return _topic_from_row(row) if row else None


def seed_mock_topics_for_smoke_test() -> int:
    if not is_database_configured():
        return 0

    mock_topics = get_mock_topics()

    initialize_database()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            for topic in mock_topics:
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
                    """,
                    (
                        topic["id"],
                        topic["topic"],
                        topic.get("summary", ""),
                        _safe_int(topic.get("score")),
                        topic.get("source", "backend-mock"),
                        json.dumps(topic, ensure_ascii=False),
                    ),
                )
        connection.commit()

    return len(mock_topics)

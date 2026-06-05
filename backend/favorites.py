from typing import Any

from db import get_connection, initialize_database, is_database_configured


DEFAULT_USER_KEY = "default-user"


def _fallback_response(topic_ids: list[str] | None = None) -> dict[str, Any]:
    return {
        "topicIds": topic_ids or [],
        "source": "fallback",
        "persisted": False,
    }


def _clean_topic_id(topic_id: str) -> str:
    return topic_id.strip()


def get_favorites(user_key: str = DEFAULT_USER_KEY) -> dict[str, Any]:
    if not is_database_configured():
        return _fallback_response()

    initialize_database()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT topic_id
                FROM favorites
                WHERE user_key = %s
                ORDER BY created_at DESC
                """,
                (user_key,),
            )
            rows = cursor.fetchall()

    return {
        "topicIds": [row[0] for row in rows],
        "source": "db",
        "persisted": True,
    }


def add_favorite(
    topic_id: str,
    user_key: str = DEFAULT_USER_KEY,
) -> dict[str, Any]:
    cleaned_topic_id = _clean_topic_id(topic_id)

    if not cleaned_topic_id:
        return _fallback_response()

    if not is_database_configured():
        return _fallback_response([cleaned_topic_id])

    initialize_database()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO favorites (user_key, topic_id)
                VALUES (%s, %s)
                ON CONFLICT (user_key, topic_id) DO NOTHING
                """,
                (user_key, cleaned_topic_id),
            )
        connection.commit()

    return get_favorites(user_key)


def remove_favorite(
    topic_id: str,
    user_key: str = DEFAULT_USER_KEY,
) -> dict[str, Any]:
    cleaned_topic_id = _clean_topic_id(topic_id)

    if not cleaned_topic_id:
        return _fallback_response()

    if not is_database_configured():
        return _fallback_response()

    initialize_database()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM favorites
                WHERE user_key = %s AND topic_id = %s
                """,
                (user_key, cleaned_topic_id),
            )
        connection.commit()

    return get_favorites(user_key)

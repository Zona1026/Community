import json
from typing import Any

from db import get_connection, initialize_database, is_database_configured


DEFAULT_USER_KEY = "default-user"
VALID_TONES = {"專業", "輕鬆", "犀利"}
DEFAULT_SETTINGS = {
    "industry": "AI",
    "tone": "專業",
    "keywords": ["AI", "創業"],
}


def _normalize_keywords(value: Any) -> list[str]:
    if not isinstance(value, list):
        return DEFAULT_SETTINGS["keywords"]

    keywords = []

    for item in value:
        if isinstance(item, str) and item.strip():
            keywords.append(item.strip())

    return list(dict.fromkeys(keywords))


def normalize_user_settings(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return DEFAULT_SETTINGS.copy()

    industry = payload.get("industry")
    tone = payload.get("tone")

    return {
        "industry": industry.strip()
        if isinstance(industry, str) and industry.strip()
        else DEFAULT_SETTINGS["industry"],
        "tone": tone if isinstance(tone, str) and tone in VALID_TONES else "專業",
        "keywords": _normalize_keywords(payload.get("keywords")),
    }


def _fallback_response(settings: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        **(settings or DEFAULT_SETTINGS),
        "source": "fallback",
        "persisted": False,
    }


def get_user_settings(user_key: str = DEFAULT_USER_KEY) -> dict[str, Any]:
    if not is_database_configured():
        return _fallback_response()

    initialize_database()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT industry, tone, keywords
                FROM user_settings
                WHERE user_key = %s
                """,
                (user_key,),
            )
            row = cursor.fetchone()

    if row is None:
        return {
            **DEFAULT_SETTINGS,
            "source": "db",
            "persisted": False,
        }

    keywords = row[2]

    if isinstance(keywords, str):
        keywords = json.loads(keywords)

    return {
        "industry": row[0],
        "tone": row[1],
        "keywords": _normalize_keywords(keywords),
        "source": "db",
        "persisted": True,
    }


def save_user_settings(
    payload: Any,
    user_key: str = DEFAULT_USER_KEY,
) -> dict[str, Any]:
    settings = normalize_user_settings(payload)

    if not is_database_configured():
        return _fallback_response(settings)

    initialize_database()

    with get_connection() as connection:
        with connection.cursor() as cursor:
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
                RETURNING industry, tone, keywords
                """,
                (
                    user_key,
                    settings["industry"],
                    settings["tone"],
                    json.dumps(settings["keywords"], ensure_ascii=False),
                ),
            )
            row = cursor.fetchone()
        connection.commit()

    keywords = row[2]

    if isinstance(keywords, str):
        keywords = json.loads(keywords)

    return {
        "industry": row[0],
        "tone": row[1],
        "keywords": _normalize_keywords(keywords),
        "source": "db",
        "persisted": True,
    }

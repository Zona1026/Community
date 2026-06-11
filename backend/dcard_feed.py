from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from urllib import error, parse, request


DCARD_API_BASE_URL = "https://www.dcard.tw/service/api/v2/posts"
DCARD_SMOKE_SOURCE = "Dcard Popular"
DEFAULT_DCARD_TIMEOUT_SECONDS = 10
MAX_DCARD_SMOKE_POSTS = 10
MAX_DCARD_RESPONSE_BYTES = 2_000_000


def _clamp_dcard_smoke_limit(limit: int) -> int:
    return max(0, min(limit, MAX_DCARD_SMOKE_POSTS))


def _build_dcard_smoke_url(limit: int) -> str:
    query = parse.urlencode(
        {
            "popular": "true",
            "limit": str(limit),
        },
    )
    return f"{DCARD_API_BASE_URL}?{query}"


def _build_dcard_request(limit: int) -> request.Request:
    return request.Request(
        _build_dcard_smoke_url(limit),
        method="GET",
        headers={
            "Accept": "application/json",
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
            "Origin": "https://www.dcard.tw",
            "Referer": "https://www.dcard.tw/f",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36 "
                "TrendRadarDcardSmokeTest/0.1"
            ),
        },
    )


def _normalize_datetime(value: str) -> str | None:
    if not value:
        return None

    try:
        parsed_datetime = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None

    if parsed_datetime.tzinfo is None:
        parsed_datetime = parsed_datetime.replace(tzinfo=UTC)

    return parsed_datetime.astimezone(UTC).isoformat()


def _normalize_title_key(title: str) -> str:
    return " ".join(title.strip().lower().split())


def _dcard_post_url(post: dict[str, Any]) -> str:
    post_id = post.get("id")
    forum_alias = post.get("forumAlias") or "all"

    if not post_id:
        return ""

    return f"https://www.dcard.tw/f/{forum_alias}/p/{post_id}"


def normalize_dcard_posts(posts: list[dict[str, Any]]) -> dict[str, Any]:
    fetched_at = datetime.now(UTC).isoformat()
    normalized_items: list[dict[str, Any]] = []
    skipped_items: list[dict[str, Any]] = []

    for index, post in enumerate(posts):
        post_id = post.get("id")
        title = str(post.get("title") or "").strip()
        link = _dcard_post_url(post)

        missing_required_fields = [
            field_name
            for field_name, field_value in {
                "id": post_id,
                "title": title,
                "link": link,
            }.items()
            if not field_value
        ]

        if missing_required_fields:
            skipped_items.append(
                {
                    "index": index,
                    "reason": "Missing required Dcard id, title, or link.",
                    "missing_fields": missing_required_fields,
                },
            )
            continue

        normalized_items.append(
            {
                "source_name": DCARD_SMOKE_SOURCE,
                "source_type": "dcard",
                "item_guid": str(post_id),
                "title": title,
                "link": link,
                "author": str(post.get("school") or post.get("department") or ""),
                "forum_name": str(post.get("forumName") or ""),
                "forum_alias": str(post.get("forumAlias") or ""),
                "published_at": _normalize_datetime(str(post.get("createdAt") or "")),
                "updated_at": _normalize_datetime(str(post.get("updatedAt") or "")),
                "fetched_at": fetched_at,
                "summary": str(post.get("excerpt") or ""),
                "like_count": post.get("likeCount", 0),
                "comment_count": post.get("commentCount", 0),
                "topics": post.get("topics") if isinstance(post.get("topics"), list) else [],
                "raw_json": post,
            },
        )

    return {
        "source_name": DCARD_SMOKE_SOURCE,
        "fetched_at": fetched_at,
        "fetched_count": len(posts),
        "normalized_count": len(normalized_items),
        "skipped_count": len(skipped_items),
        "items": normalized_items,
        "skipped_items": skipped_items[:3],
    }


def _group_dcard_normalized_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups_by_key: dict[str, dict[str, Any]] = {}

    for item in items:
        group_key = _normalize_title_key(str(item.get("title", "")))

        if not group_key:
            continue

        if group_key not in groups_by_key:
            groups_by_key[group_key] = {
                "groupKey": group_key,
                "representativeTitle": item["title"],
                "itemCount": 0,
                "items": [],
                "reason": "Grouped by normalized exact title match.",
            }

        groups_by_key[group_key]["items"].append(item)
        groups_by_key[group_key]["itemCount"] += 1

    return list(groups_by_key.values())


def _topic_drafts_from_dcard_groups(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    drafts: list[dict[str, Any]] = []

    for group in groups:
        items = group["items"]

        if not items:
            continue

        representative_item = items[0]
        title = str(group["representativeTitle"]).strip()

        if not title:
            continue

        forum_name = str(representative_item.get("forum_name") or "Dcard")
        source_url = str(representative_item.get("link") or "")
        summary = str(representative_item.get("summary") or title)

        drafts.append(
            {
                "title": title,
                "summary": summary,
                "score": 50,
                "growthRate": 0,
                "momentum": "weak",
                "lifecycleStage": "emerging",
                "sourceType": "dcard",
                "sourceName": forum_name,
                "sourceUrl": source_url,
                "evidenceCount": group["itemCount"],
                "evidenceItems": items[:3],
                "rawGroupKey": group["groupKey"],
            },
        )

    return drafts


def build_dcard_smoke_preview(limit: int = MAX_DCARD_SMOKE_POSTS) -> dict[str, Any]:
    effective_limit = _clamp_dcard_smoke_limit(limit)
    dcard_request = _build_dcard_request(effective_limit)

    try:
        with request.urlopen(
            dcard_request,
            timeout=DEFAULT_DCARD_TIMEOUT_SECONDS,
        ) as response:
            response_body = response.read(MAX_DCARD_RESPONSE_BYTES + 1)
            content_type = response.headers.get("Content-Type", "")
            status_code = response.status
    except error.HTTPError as dcard_error:
        return {
            "status": "failed",
            "reason": "Dcard API returned an HTTP error.",
            "http_status": dcard_error.code,
            "feed_source": DCARD_SMOKE_SOURCE,
            "fetched_count": 0,
            "normalized_count": 0,
            "grouped_topic_count": 0,
            "skipped_count": 0,
            "errors": [str(dcard_error)],
            "dry_run": True,
            "batch_id": None,
            "items": [],
        }
    except error.URLError as url_error:
        return {
            "status": "failed",
            "reason": "Dcard API could not be reached.",
            "error": str(url_error.reason),
            "feed_source": DCARD_SMOKE_SOURCE,
            "fetched_count": 0,
            "normalized_count": 0,
            "grouped_topic_count": 0,
            "skipped_count": 0,
            "errors": [str(url_error.reason)],
            "dry_run": True,
            "batch_id": None,
            "items": [],
        }
    except TimeoutError:
        return {
            "status": "failed",
            "reason": "Dcard API request timed out.",
            "feed_source": DCARD_SMOKE_SOURCE,
            "fetched_count": 0,
            "normalized_count": 0,
            "grouped_topic_count": 0,
            "skipped_count": 0,
            "errors": ["Dcard API request timed out."],
            "dry_run": True,
            "batch_id": None,
            "items": [],
        }

    if len(response_body) > MAX_DCARD_RESPONSE_BYTES:
        return {
            "status": "failed",
            "reason": "Dcard API response was too large.",
            "http_status": status_code,
            "content_type": content_type,
            "feed_source": DCARD_SMOKE_SOURCE,
            "fetched_count": 0,
            "normalized_count": 0,
            "grouped_topic_count": 0,
            "skipped_count": 0,
            "errors": ["Dcard API response was too large."],
            "dry_run": True,
            "batch_id": None,
            "items": [],
        }

    try:
        posts = json.loads(response_body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as parse_error:
        return {
            "status": "failed",
            "reason": "Dcard API JSON could not be parsed.",
            "error": str(parse_error),
            "http_status": status_code,
            "content_type": content_type,
            "feed_source": DCARD_SMOKE_SOURCE,
            "fetched_count": 0,
            "normalized_count": 0,
            "grouped_topic_count": 0,
            "skipped_count": 0,
            "errors": [str(parse_error)],
            "dry_run": True,
            "batch_id": None,
            "items": [],
        }

    if not isinstance(posts, list):
        return {
            "status": "failed",
            "reason": "Dcard API JSON response was not a list.",
            "http_status": status_code,
            "content_type": content_type,
            "feed_source": DCARD_SMOKE_SOURCE,
            "fetched_count": 0,
            "normalized_count": 0,
            "grouped_topic_count": 0,
            "skipped_count": 0,
            "errors": ["Dcard API JSON response was not a list."],
            "dry_run": True,
            "batch_id": None,
            "items": [],
        }

    normalized_summary = normalize_dcard_posts(posts[:effective_limit])

    return {
        "status": "ok",
        "feed_source": DCARD_SMOKE_SOURCE,
        "api_url": _build_dcard_smoke_url(effective_limit),
        "http_status": status_code,
        "content_type": content_type,
        "requested_limit": limit,
        "effective_limit": effective_limit,
        "max_items": MAX_DCARD_SMOKE_POSTS,
        "fetched_count": normalized_summary["fetched_count"],
        "normalized_count": normalized_summary["normalized_count"],
        "grouped_topic_count": 0,
        "skipped_count": normalized_summary["skipped_count"],
        "errors": [],
        "dry_run": True,
        "batch_id": None,
        "items": normalized_summary["items"],
        "skipped_items": normalized_summary["skipped_items"],
    }


def build_dcard_smoke_topic_draft(limit: int = MAX_DCARD_SMOKE_POSTS) -> dict[str, Any]:
    preview = build_dcard_smoke_preview(limit)

    if preview["status"] != "ok":
        return {
            **preview,
            "groups": [],
            "topic_drafts": [],
        }

    groups = _group_dcard_normalized_items(preview["items"])
    topic_drafts = _topic_drafts_from_dcard_groups(groups)

    return {
        **preview,
        "grouped_topic_count": len(groups),
        "groups": groups,
        "topic_drafts": topic_drafts,
    }

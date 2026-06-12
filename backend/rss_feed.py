from __future__ import annotations

import os
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any
from xml.etree import ElementTree
from urllib import error, request

from text_utils import clean_html_to_text


DEFAULT_RSS_TIMEOUT_SECONDS = 10
MAX_RSS_PARSE_BYTES = 2_000_000
MAX_PODCAST_PARSE_BYTES = 8_000_000
MAX_RSS_SMOKE_ITEMS = 5
REQUIRED_RSS_ENV_VARS = ["RSS_FEED_URL"]
RSS_SMOKE_FEED_WHITELIST = {
    "hacker-news": {
        "source": "Hacker News",
        "url": "https://news.ycombinator.com/rss",
    },
}
PODCAST_SMOKE_FEED_WHITELIST = {
    "planet-money": {
        "source": "NPR Planet Money",
        "url": "https://feeds.npr.org/510289/podcast.xml",
    },
    "ted-radio-hour": {
        "source": "TED Radio Hour",
        "url": "https://feeds.npr.org/510298/podcast.xml",
    },
    "bbc-global-news": {
        "source": "BBC Global News Podcast",
        "url": "https://podcasts.files.bbci.co.uk/p02nq0gn.rss",
    },
    "lex-fridman": {
        "source": "Lex Fridman Podcast",
        "url": "https://lexfridman.com/feed/podcast/",
    },
}


def validate_rss_env() -> dict[str, Any]:
    missing = [
        key for key in REQUIRED_RSS_ENV_VARS
        if not os.getenv(key, "").strip()
    ]

    if missing:
        return {
            "status": "skipped",
            "reason": "Missing RSS environment variables.",
            "missing": missing,
        }

    return {
        "status": "ok",
        "missing": [],
    }


def _get_timeout_seconds() -> int:
    raw_value = os.getenv("RSS_REQUEST_TIMEOUT_SECONDS", "").strip()

    if not raw_value:
        return DEFAULT_RSS_TIMEOUT_SECONDS

    try:
        return max(1, int(raw_value))
    except ValueError:
        return DEFAULT_RSS_TIMEOUT_SECONDS


def _build_rss_request(feed_url: str) -> request.Request:
    return request.Request(
        feed_url,
        method="GET",
        headers={
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
            "User-Agent": "TrendRadarRSSSmokeTest/0.1",
        },
    )


def _strip_namespace(tag_name: str) -> str:
    if "}" in tag_name:
        return tag_name.rsplit("}", 1)[1]

    return tag_name


def _find_child_text(element: ElementTree.Element, child_name: str) -> str:
    for child in list(element):
        if _strip_namespace(child.tag) == child_name and child.text:
            return child.text.strip()

    return ""


def _find_nested_child_text(element: ElementTree.Element, child_name: str) -> str:
    for child in element.iter():
        if child is element:
            continue

        if _strip_namespace(child.tag) == child_name and child.text:
            return child.text.strip()

    return ""


def _find_item_elements(root: ElementTree.Element) -> list[ElementTree.Element]:
    item_elements = [
        element for element in root.iter()
        if _strip_namespace(element.tag) == "item"
    ]

    if item_elements:
        return item_elements

    return [
        element for element in root.iter()
        if _strip_namespace(element.tag) == "entry"
    ]


def _find_rss_link(element: ElementTree.Element) -> str:
    link_text = _find_child_text(element, "link")

    if link_text:
        return link_text

    for child in list(element):
        if _strip_namespace(child.tag) != "link":
            continue

        href = child.attrib.get("href", "").strip()

        if href:
            return href

    return ""


def _find_source_name(root: ElementTree.Element) -> str:
    for element in root.iter():
        if _strip_namespace(element.tag) != "channel":
            continue

        channel_title = _find_child_text(element, "title")

        if channel_title:
            return channel_title

    return _find_child_text(root, "title")


def _normalize_datetime(value: str) -> str | None:
    if not value:
        return None

    try:
        parsed_datetime = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            parsed_datetime = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    if parsed_datetime.tzinfo is None:
        parsed_datetime = parsed_datetime.replace(tzinfo=UTC)

    return parsed_datetime.astimezone(UTC).isoformat()


def _parse_rss_item_element(item_element: ElementTree.Element) -> dict[str, Any]:
    title = _find_child_text(item_element, "title")
    link = _find_rss_link(item_element)
    guid = _find_child_text(item_element, "guid") or _find_child_text(
        item_element,
        "id",
    )
    author = (
        _find_child_text(item_element, "author")
        or _find_child_text(item_element, "creator")
        or _find_nested_child_text(item_element, "name")
    )
    published_raw = (
        _find_child_text(item_element, "pubDate")
        or _find_child_text(item_element, "published")
        or _find_child_text(item_element, "updated")
    )
    summary = (
        _find_child_text(item_element, "description")
        or _find_child_text(item_element, "summary")
        or _find_child_text(item_element, "content")
    )

    return {
        "title": title,
        "link": link,
        "guid": guid,
        "author": author,
        "published_raw": published_raw,
        "published_at": _normalize_datetime(published_raw),
        "summary": summary,
    }


def parse_rss_items(feed_xml: bytes | str) -> list[dict[str, str]]:
    root = ElementTree.fromstring(feed_xml)
    item_elements = _find_item_elements(root)
    items: list[dict[str, str]] = []

    for item_element in item_elements:
        parsed_item = _parse_rss_item_element(item_element)
        guid = parsed_item["guid"] or parsed_item["link"]

        items.append(
            {
                "title": parsed_item["title"],
                "link": parsed_item["link"],
                "guid": guid,
            },
        )

    return items


def normalize_rss_items(
    feed_xml: bytes | str,
    feed_url: str,
    fetched_at: str | None = None,
) -> dict[str, Any]:
    root = ElementTree.fromstring(feed_xml)
    item_elements = _find_item_elements(root)
    source_name = _find_source_name(root)
    normalized_fetched_at = fetched_at or datetime.now(UTC).isoformat()
    normalized_items: list[dict[str, Any]] = []
    skipped_items: list[dict[str, Any]] = []
    missing_guid_fallback_count = 0

    for index, item_element in enumerate(item_elements):
        parsed_item = _parse_rss_item_element(item_element)
        title = parsed_item["title"]
        link = parsed_item["link"]
        item_guid = parsed_item["guid"]
        raw_summary = parsed_item["summary"]
        clean_summary = clean_html_to_text(raw_summary) or title
        guid_was_fallback = False

        if not item_guid and link:
            item_guid = link
            guid_was_fallback = True

        missing_required_fields = [
            field_name for field_name, field_value in {
                "title": title,
                "link": link,
            }.items()
            if not field_value
        ]

        if missing_required_fields:
            skipped_items.append(
                {
                    "index": index,
                    "reason": "Missing required title or link.",
                    "missing_fields": missing_required_fields,
                    "raw_item": parsed_item,
                },
            )
            continue

        if guid_was_fallback:
            missing_guid_fallback_count += 1

        normalized_items.append(
            {
                "source_name": source_name,
                "feed_url": feed_url,
                "item_guid": item_guid,
                "title": title,
                "link": link,
                "author": parsed_item["author"],
                "published_at": parsed_item["published_at"],
                "fetched_at": normalized_fetched_at,
                "summary": clean_summary,
                "raw_json": {
                    "guid": parsed_item["guid"],
                    "guid_was_fallback": guid_was_fallback,
                    "published_raw": parsed_item["published_raw"],
                    "title": title,
                    "link": link,
                    "author": parsed_item["author"],
                    "summary": clean_summary,
                    "raw_summary": raw_summary,
                },
            },
        )

    return {
        "feed_url": feed_url,
        "source_name": source_name,
        "fetched_at": normalized_fetched_at,
        "total_parsed_items": len(item_elements),
        "valid_normalized_items": len(normalized_items),
        "skipped_items_count": len(skipped_items),
        "missing_guid_fallback_count": missing_guid_fallback_count,
        "items": normalized_items,
        "sample_items": normalized_items[:3],
        "skipped_items": skipped_items[:3],
    }


def _clamp_rss_smoke_limit(limit: int) -> int:
    return max(0, min(limit, MAX_RSS_SMOKE_ITEMS))


def _get_smoke_feed(feed_key: str | None = None) -> dict[str, str] | None:
    normalized_key = (feed_key or "hacker-news").strip().lower()
    return RSS_SMOKE_FEED_WHITELIST.get(normalized_key)


def _fetch_whitelisted_smoke_feed(feed_key: str | None = None) -> dict[str, Any]:
    feed = _get_smoke_feed(feed_key)

    if not feed:
        return {
            "status": "blocked",
            "reason": "RSS smoke feed is not in the fixed whitelist.",
            "allowedFeeds": sorted(RSS_SMOKE_FEED_WHITELIST.keys()),
        }

    feed_request = _build_rss_request(feed["url"])

    try:
        with request.urlopen(
            feed_request,
            timeout=_get_timeout_seconds(),
        ) as response:
            response_body = response.read(MAX_RSS_PARSE_BYTES + 1)
            content_type = response.headers.get("Content-Type", "")
            status_code = response.status
    except error.HTTPError as rss_error:
        return {
            "status": "failed",
            "reason": "RSS smoke feed returned an HTTP error.",
            "http_status": rss_error.code,
            "feed_source": feed["source"],
            "feed_url": feed["url"],
        }
    except error.URLError as url_error:
        return {
            "status": "failed",
            "reason": "RSS smoke feed could not be reached.",
            "error": str(url_error.reason),
            "feed_source": feed["source"],
            "feed_url": feed["url"],
        }
    except TimeoutError:
        return {
            "status": "failed",
            "reason": "RSS smoke feed request timed out.",
            "feed_source": feed["source"],
            "feed_url": feed["url"],
        }

    if len(response_body) > MAX_RSS_PARSE_BYTES:
        return {
            "status": "failed",
            "http_status": status_code,
            "content_type": content_type,
            "reason": "RSS smoke response was too large.",
            "max_bytes": MAX_RSS_PARSE_BYTES,
            "feed_source": feed["source"],
            "feed_url": feed["url"],
        }

    return {
        "status": "ok",
        "feed_source": feed["source"],
        "feed_url": feed["url"],
        "http_status": status_code,
        "content_type": content_type,
        "body": response_body,
    }


def _normalize_title_key(title: str) -> str:
    return " ".join(title.strip().lower().split())


def _group_smoke_normalized_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
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


def _topic_drafts_from_smoke_groups(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    drafts: list[dict[str, Any]] = []

    for group in groups:
        items = group["items"]

        if not items:
            continue

        representative_item = items[0]
        title = str(group["representativeTitle"]).strip()

        if not title:
            continue

        summary = clean_html_to_text(representative_item.get("summary")) or title
        source_name = str(representative_item.get("source_name") or "RSS")
        source_url = str(representative_item.get("link") or "")

        drafts.append(
            {
                "title": title,
                "summary": summary,
                "score": 50,
                "growthRate": 0,
                "momentum": "weak",
                "lifecycleStage": "emerging",
                "sourceType": "rss",
                "sourceName": source_name,
                "sourceUrl": source_url,
                "evidenceCount": group["itemCount"],
                "evidenceItems": items[:3],
                "rawGroupKey": group["groupKey"],
            },
        )

    return drafts


def build_rss_smoke_preview(
    feed_key: str | None = None,
    limit: int = MAX_RSS_SMOKE_ITEMS,
) -> dict[str, Any]:
    effective_limit = _clamp_rss_smoke_limit(limit)
    fetched = _fetch_whitelisted_smoke_feed(feed_key)

    if fetched["status"] != "ok":
        return {
            **fetched,
            "fetched_count": 0,
            "normalized_count": 0,
            "grouped_topic_count": 0,
            "skipped_count": 0,
            "errors": [fetched.get("reason", "RSS smoke fetch failed.")],
            "dry_run": True,
            "batch_id": None,
            "items": [],
        }

    try:
        normalized_summary = normalize_rss_items(fetched["body"], fetched["feed_url"])
    except ElementTree.ParseError as parse_error:
        return {
            "status": "failed",
            "reason": "RSS smoke XML could not be parsed.",
            "error": str(parse_error),
            "feed_source": fetched["feed_source"],
            "feed_url": fetched["feed_url"],
            "fetched_count": 0,
            "normalized_count": 0,
            "grouped_topic_count": 0,
            "skipped_count": 0,
            "errors": [str(parse_error)],
            "dry_run": True,
            "batch_id": None,
            "items": [],
        }

    limited_items = normalized_summary["items"][:effective_limit]
    errors = []
    reason = None

    if normalized_summary["total_parsed_items"] == 0:
        reason = "RSS smoke feed contained no items."
        errors.append(reason)

    result = {
        "status": "ok",
        "feed_source": fetched["feed_source"],
        "feed_url": fetched["feed_url"],
        "http_status": fetched["http_status"],
        "content_type": fetched["content_type"],
        "requested_limit": limit,
        "effective_limit": effective_limit,
        "max_items": MAX_RSS_SMOKE_ITEMS,
        "fetched_count": normalized_summary["total_parsed_items"],
        "normalized_count": len(limited_items),
        "grouped_topic_count": 0,
        "skipped_count": normalized_summary["skipped_items_count"],
        "errors": errors,
        "dry_run": True,
        "batch_id": None,
        "items": limited_items,
        "skipped_items": normalized_summary["skipped_items"],
    }

    if reason:
        result["reason"] = reason

    return result


def build_rss_smoke_topic_draft(
    feed_key: str | None = None,
    limit: int = MAX_RSS_SMOKE_ITEMS,
) -> dict[str, Any]:
    preview = build_rss_smoke_preview(feed_key, limit)

    if preview["status"] != "ok":
        return {
            **preview,
            "groups": [],
            "topic_drafts": [],
        }

    groups = _group_smoke_normalized_items(preview["items"])
    topic_drafts = _topic_drafts_from_smoke_groups(groups)

    return {
        **preview,
        "grouped_topic_count": len(groups),
        "groups": groups,
        "topic_drafts": topic_drafts,
    }


def _get_podcast_smoke_feed(feed_key: str | None = None) -> dict[str, str] | None:
    normalized_key = (feed_key or "planet-money").strip().lower()
    return PODCAST_SMOKE_FEED_WHITELIST.get(normalized_key)


def build_podcast_smoke_preview(
    feed_key: str | None = None,
    limit: int = MAX_RSS_SMOKE_ITEMS,
) -> dict[str, Any]:
    effective_limit = _clamp_rss_smoke_limit(limit)
    feed = _get_podcast_smoke_feed(feed_key)

    if not feed:
        return {
            "status": "blocked",
            "reason": "Podcast smoke feed is not in the fixed whitelist.",
            "allowedFeeds": sorted(PODCAST_SMOKE_FEED_WHITELIST.keys()),
            "feed_source": None,
            "fetched_count": 0,
            "normalized_count": 0,
            "grouped_topic_count": 0,
            "skipped_count": 0,
            "errors": ["Podcast smoke feed is not in the fixed whitelist."],
            "dry_run": True,
            "batch_id": None,
            "items": [],
        }

    feed_request = _build_rss_request(feed["url"])

    try:
        with request.urlopen(
            feed_request,
            timeout=_get_timeout_seconds(),
        ) as response:
            response_body = response.read(MAX_PODCAST_PARSE_BYTES + 1)
            content_type = response.headers.get("Content-Type", "")
            status_code = response.status
    except error.HTTPError as podcast_error:
        return {
            "status": "failed",
            "reason": "Podcast RSS feed returned an HTTP error.",
            "http_status": podcast_error.code,
            "feed_source": feed["source"],
            "feed_url": feed["url"],
            "fetched_count": 0,
            "normalized_count": 0,
            "grouped_topic_count": 0,
            "skipped_count": 0,
            "errors": [str(podcast_error)],
            "dry_run": True,
            "batch_id": None,
            "items": [],
        }
    except error.URLError as url_error:
        return {
            "status": "failed",
            "reason": "Podcast RSS feed could not be reached.",
            "error": str(url_error.reason),
            "feed_source": feed["source"],
            "feed_url": feed["url"],
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
            "reason": "Podcast RSS feed request timed out.",
            "feed_source": feed["source"],
            "feed_url": feed["url"],
            "fetched_count": 0,
            "normalized_count": 0,
            "grouped_topic_count": 0,
            "skipped_count": 0,
            "errors": ["Podcast RSS feed request timed out."],
            "dry_run": True,
            "batch_id": None,
            "items": [],
        }

    if len(response_body) > MAX_PODCAST_PARSE_BYTES:
        return {
            "status": "failed",
            "http_status": status_code,
            "content_type": content_type,
            "reason": "Podcast RSS response was too large.",
            "max_bytes": MAX_PODCAST_PARSE_BYTES,
            "feed_source": feed["source"],
            "feed_url": feed["url"],
            "fetched_count": 0,
            "normalized_count": 0,
            "grouped_topic_count": 0,
            "skipped_count": 0,
            "errors": ["Podcast RSS response was too large."],
            "dry_run": True,
            "batch_id": None,
            "items": [],
        }

    try:
        normalized_summary = normalize_rss_items(response_body, feed["url"])
    except ElementTree.ParseError as parse_error:
        return {
            "status": "failed",
            "reason": "Podcast RSS XML could not be parsed.",
            "error": str(parse_error),
            "feed_source": feed["source"],
            "feed_url": feed["url"],
            "fetched_count": 0,
            "normalized_count": 0,
            "grouped_topic_count": 0,
            "skipped_count": 0,
            "errors": [str(parse_error)],
            "dry_run": True,
            "batch_id": None,
            "items": [],
        }

    limited_items = normalized_summary["items"][:effective_limit]
    errors = []
    reason = None

    if normalized_summary["total_parsed_items"] == 0:
        reason = "Podcast RSS feed contained no episodes."
        errors.append(reason)

    result = {
        "status": "ok",
        "feed_source": feed["source"],
        "feed_url": feed["url"],
        "http_status": status_code,
        "content_type": content_type,
        "requested_limit": limit,
        "effective_limit": effective_limit,
        "max_items": MAX_RSS_SMOKE_ITEMS,
        "fetched_count": normalized_summary["total_parsed_items"],
        "normalized_count": len(limited_items),
        "grouped_topic_count": 0,
        "skipped_count": normalized_summary["skipped_items_count"],
        "errors": errors,
        "dry_run": True,
        "batch_id": None,
        "items": limited_items,
        "skipped_items": normalized_summary["skipped_items"],
    }

    if reason:
        result["reason"] = reason

    return result


def build_podcast_smoke_topic_draft(
    feed_key: str | None = None,
    limit: int = MAX_RSS_SMOKE_ITEMS,
) -> dict[str, Any]:
    preview = build_podcast_smoke_preview(feed_key, limit)

    if preview["status"] != "ok":
        return {
            **preview,
            "groups": [],
            "topic_drafts": [],
        }

    groups = _group_smoke_normalized_items(preview["items"])
    topic_drafts = _topic_drafts_from_smoke_groups(groups)

    for draft in topic_drafts:
        draft["sourceType"] = "podcast"
        draft["sourceName"] = preview["feed_source"]

    return {
        **preview,
        "grouped_topic_count": len(groups),
        "groups": groups,
        "topic_drafts": topic_drafts,
    }


def run_rss_dry_run_ingestion_summary() -> dict[str, Any]:
    env_status = validate_rss_env()

    if env_status["status"] != "ok":
        return env_status

    feed_url = os.environ["RSS_FEED_URL"].strip()
    feed_request = _build_rss_request(feed_url)

    try:
        with request.urlopen(
            feed_request,
            timeout=_get_timeout_seconds(),
        ) as response:
            response_body = response.read(MAX_RSS_PARSE_BYTES + 1)
            content_type = response.headers.get("Content-Type", "")
            status_code = response.status
    except error.HTTPError as rss_error:
        return {
            "status": "failed",
            "reason": "RSS feed returned an HTTP error.",
            "http_status": rss_error.code,
        }
    except error.URLError as url_error:
        return {
            "status": "failed",
            "reason": "RSS feed could not be reached.",
            "error": str(url_error.reason),
        }
    except TimeoutError:
        return {
            "status": "failed",
            "reason": "RSS feed request timed out.",
        }

    if len(response_body) > MAX_RSS_PARSE_BYTES:
        return {
            "status": "failed",
            "http_status": status_code,
            "content_type": content_type,
            "reason": "RSS response was too large for the dry-run ingestion summary.",
            "max_bytes": MAX_RSS_PARSE_BYTES,
        }

    try:
        summary = normalize_rss_items(response_body, feed_url)
    except ElementTree.ParseError as parse_error:
        return {
            "status": "failed",
            "http_status": status_code,
            "content_type": content_type,
            "reason": "RSS XML could not be parsed.",
            "error": str(parse_error),
        }

    return {
        "status": "ok",
        "http_status": status_code,
        "content_type": content_type,
        "total_parsed_items": summary["total_parsed_items"],
        "valid_normalized_items": summary["valid_normalized_items"],
        "skipped_items_count": summary["skipped_items_count"],
        "missing_guid_fallback_count": summary["missing_guid_fallback_count"],
        "sample_items": summary["sample_items"],
        "skipped_items": summary["skipped_items"],
        "writes_to_database": False,
    }


def run_rss_manual_ingestion() -> dict[str, Any]:
    env_status = validate_rss_env()

    if env_status["status"] != "ok":
        return {
            **env_status,
            "reason": "RSS_FEED_URL is required before manual RSS ingestion.",
        }

    feed_url = os.environ["RSS_FEED_URL"].strip()
    feed_request = _build_rss_request(feed_url)

    try:
        with request.urlopen(
            feed_request,
            timeout=_get_timeout_seconds(),
        ) as response:
            response_body = response.read(MAX_RSS_PARSE_BYTES + 1)
            content_type = response.headers.get("Content-Type", "")
            status_code = response.status
    except error.HTTPError as rss_error:
        return {
            "status": "failed",
            "reason": "RSS feed returned an HTTP error.",
            "http_status": rss_error.code,
        }
    except error.URLError as url_error:
        return {
            "status": "failed",
            "reason": "RSS feed could not be reached.",
            "error": str(url_error.reason),
        }
    except TimeoutError:
        return {
            "status": "failed",
            "reason": "RSS feed request timed out.",
        }

    if len(response_body) > MAX_RSS_PARSE_BYTES:
        return {
            "status": "failed",
            "http_status": status_code,
            "content_type": content_type,
            "reason": "RSS response was too large for manual ingestion.",
            "max_bytes": MAX_RSS_PARSE_BYTES,
        }

    try:
        normalized_summary = normalize_rss_items(response_body, feed_url)
    except ElementTree.ParseError as parse_error:
        return {
            "status": "failed",
            "http_status": status_code,
            "content_type": content_type,
            "reason": "RSS XML could not be parsed.",
            "error": str(parse_error),
        }

    from db import upsert_rss_items

    upsert_summary = upsert_rss_items(normalized_summary["items"])

    if upsert_summary["status"] == "skipped":
        return upsert_summary

    return {
        "status": upsert_summary["status"],
        "http_status": status_code,
        "content_type": content_type,
        "feed_url": normalized_summary["feed_url"],
        "source_name": normalized_summary["source_name"],
        "fetched_at": normalized_summary["fetched_at"],
        "total_parsed_items": normalized_summary["total_parsed_items"],
        "valid_normalized_items": normalized_summary["valid_normalized_items"],
        "inserted_count": upsert_summary["inserted_count"],
        "updated_count": upsert_summary["updated_count"],
        "skipped_count": normalized_summary["skipped_items_count"],
        "error_count": upsert_summary["error_count"],
        "errors": upsert_summary["errors"],
        "sample_items": normalized_summary["sample_items"],
        "writes_to_database": True,
    }


def run_rss_fetch_smoke_test() -> dict[str, Any]:
    env_status = validate_rss_env()

    if env_status["status"] != "ok":
        return env_status

    feed_url = os.environ["RSS_FEED_URL"].strip()
    feed_request = _build_rss_request(feed_url)

    try:
        with request.urlopen(
            feed_request,
            timeout=_get_timeout_seconds(),
        ) as response:
            response_body = response.read(4096)
            content_type = response.headers.get("Content-Type", "")
            status_code = response.status
    except error.HTTPError as rss_error:
        return {
            "status": "failed",
            "reason": "RSS feed returned an HTTP error.",
            "http_status": rss_error.code,
        }
    except error.URLError as url_error:
        return {
            "status": "failed",
            "reason": "RSS feed could not be reached.",
            "error": str(url_error.reason),
        }
    except TimeoutError:
        return {
            "status": "failed",
            "reason": "RSS feed request timed out.",
        }

    stripped_body = response_body.lstrip()
    looks_like_xml = stripped_body.startswith(b"<?xml") or stripped_body.startswith(
        b"<rss",
    ) or stripped_body.startswith(b"<feed")

    return {
        "status": "ok" if looks_like_xml else "failed",
        "http_status": status_code,
        "content_type": content_type,
        "bytes_checked": len(response_body),
        "looks_like_xml": looks_like_xml,
        "reason": None if looks_like_xml else "RSS response did not look like XML.",
    }


def run_rss_parser_smoke_test() -> dict[str, Any]:
    env_status = validate_rss_env()

    if env_status["status"] != "ok":
        return env_status

    feed_url = os.environ["RSS_FEED_URL"].strip()
    feed_request = _build_rss_request(feed_url)

    try:
        with request.urlopen(
            feed_request,
            timeout=_get_timeout_seconds(),
        ) as response:
            response_body = response.read(MAX_RSS_PARSE_BYTES + 1)
            content_type = response.headers.get("Content-Type", "")
            status_code = response.status
    except error.HTTPError as rss_error:
        return {
            "status": "failed",
            "reason": "RSS feed returned an HTTP error.",
            "http_status": rss_error.code,
        }
    except error.URLError as url_error:
        return {
            "status": "failed",
            "reason": "RSS feed could not be reached.",
            "error": str(url_error.reason),
        }
    except TimeoutError:
        return {
            "status": "failed",
            "reason": "RSS feed request timed out.",
        }

    if len(response_body) > MAX_RSS_PARSE_BYTES:
        return {
            "status": "failed",
            "http_status": status_code,
            "content_type": content_type,
            "reason": "RSS response was too large for the parser smoke test.",
            "max_bytes": MAX_RSS_PARSE_BYTES,
        }

    try:
        items = parse_rss_items(response_body)
    except ElementTree.ParseError as parse_error:
        return {
            "status": "failed",
            "http_status": status_code,
            "content_type": content_type,
            "reason": "RSS XML could not be parsed.",
            "error": str(parse_error),
        }

    item_count = len(items)

    return {
        "status": "ok" if item_count > 0 else "failed",
        "http_status": status_code,
        "content_type": content_type,
        "item_count": item_count,
        "items": items[:3],
        "guid_fallback_rule": "Use link as guid when guid/id is missing.",
        "reason": None if item_count > 0 else "RSS feed did not contain any item or entry elements.",
    }

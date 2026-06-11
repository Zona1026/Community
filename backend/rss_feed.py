from __future__ import annotations

import os
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any
from xml.etree import ElementTree
from urllib import error, request


DEFAULT_RSS_TIMEOUT_SECONDS = 10
MAX_RSS_PARSE_BYTES = 2_000_000
REQUIRED_RSS_ENV_VARS = ["RSS_FEED_URL"]


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
                "summary": parsed_item["summary"],
                "raw_json": {
                    "guid": parsed_item["guid"],
                    "guid_was_fallback": guid_was_fallback,
                    "published_raw": parsed_item["published_raw"],
                    "title": title,
                    "link": link,
                    "author": parsed_item["author"],
                    "summary": parsed_item["summary"],
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

import json
import os
from hmac import compare_digest
from pathlib import Path
from typing import Any

from flask import Flask, request

from dcard_feed import build_dcard_smoke_preview, build_dcard_smoke_topic_draft
from db import (
    get_grouped_topic_payload_preview,
    get_ingestion_health_summary,
    get_ingestion_run_history,
    get_ingestion_run_detail,
    get_latest_ingestion_run,
    get_rss_ingestion_status,
    get_rss_topic_candidates,
    get_rss_topics_status,
    get_topic_candidate_groups,
    get_topics_upsert_dry_run,
    get_database_url,
    initialize_database,
    insert_smoke_test_data,
    rollback_dcard_smoke_batch,
    rollback_podcast_smoke_batch,
    rollback_rss_smoke_batch,
    run_rss_to_topics_ingestion,
    run_rss_upsert_smoke_test,
    run_topics_upsert_smoke_test,
    upsert_rss_smoke_topic_drafts,
    upsert_dcard_smoke_topic_drafts,
    upsert_podcast_smoke_topic_drafts,
)
from favorites import add_favorite, get_favorites, remove_favorite
from mock_topics import find_mock_topic, get_mock_topics
from reddit_oauth import run_reddit_oauth_smoke_test, validate_reddit_env
from rss_feed import (
    build_podcast_smoke_preview,
    build_podcast_smoke_topic_draft,
    build_rss_smoke_preview,
    build_rss_smoke_topic_draft,
    run_rss_dry_run_ingestion_summary,
    run_rss_fetch_smoke_test,
    run_rss_manual_ingestion,
    run_rss_parser_smoke_test,
    validate_rss_env,
)
from topic_repository import find_topic_from_database, get_topics_from_database
from user_settings import get_user_settings, save_user_settings


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
ENV_FILE = BASE_DIR / ".env"
DEFAULT_SAMPLE_PATH = (
    PROJECT_ROOT
    / "frontend"
    / "src"
    / "data"
    / "importSamples"
    / "threads.sample.json"
)


def is_dev_endpoint_enabled() -> bool:
    return os.getenv("ALLOW_DEV_ENDPOINTS", "").strip().lower() == "true"


def dev_endpoint_blocked_response() -> tuple[dict[str, Any], int]:
    return {
        "status": "blocked",
        "reason": "Dev endpoints are disabled in this environment.",
        "required": "Set ALLOW_DEV_ENDPOINTS=true for local smoke testing.",
        "productionBoundary": "/dev/* endpoints are not production ingestion controls.",
    }, 403


def get_admin_api_token() -> str:
    return os.getenv("ADMIN_API_TOKEN", "").strip()


def get_request_admin_token() -> str:
    auth_header = request.headers.get("Authorization", "").strip()

    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()

    return request.headers.get("X-Admin-API-Token", "").strip()


def admin_endpoint_unauthorized_response() -> tuple[dict[str, Any], int]:
    return {
        "status": "unauthorized",
        "reason": "Admin API token is required for /admin/* endpoints.",
        "required": "Send Authorization: Bearer <ADMIN_API_TOKEN> or X-Admin-API-Token.",
    }, 401


def is_admin_request_authorized() -> bool:
    expected_token = get_admin_api_token()
    provided_token = get_request_admin_token()

    if not expected_token or not provided_token:
        return False

    return compare_digest(provided_token, expected_token)


def load_local_env() -> None:
    if not ENV_FILE.exists():
        return

    with ENV_FILE.open("r", encoding="utf-8") as env_file:
        for line in env_file:
            env_line = line.strip()

            if not env_line or env_line.startswith("#") or "=" not in env_line:
                continue

            key, value = env_line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def create_app() -> Flask:
    load_local_env()
    app = Flask(__name__)

    @app.before_request
    def guard_dev_endpoints() -> tuple[dict[str, Any], int] | None:
        if request.path.startswith("/dev/") and not is_dev_endpoint_enabled():
            return dev_endpoint_blocked_response()

        if request.path.startswith("/admin/") and not is_admin_request_authorized():
            return admin_endpoint_unauthorized_response()

        return None

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    @app.get("/db/status")
    def database_status() -> tuple[dict[str, str | bool], int]:
        return {
            "configured": get_database_url() is not None,
            "status": "configured" if get_database_url() else "fallback",
        }, 200

    @app.post("/db/init")
    def database_init() -> tuple[dict[str, Any], int]:
        result = initialize_database()
        return result, 200

    @app.post("/db/smoke-test")
    def database_smoke_test() -> tuple[dict[str, Any], int]:
        init_result = initialize_database()

        if init_result["status"] == "skipped":
            return init_result, 200

        result = insert_smoke_test_data()
        return result, 200

    @app.post("/dev/rss-upsert-smoke")
    def rss_upsert_smoke_test() -> tuple[dict[str, Any], int]:
        init_result = initialize_database()

        if init_result["status"] == "skipped":
            return init_result, 200

        result = run_rss_upsert_smoke_test()
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.post("/dev/rss-ingest")
    def rss_manual_ingest() -> tuple[dict[str, Any], int]:
        init_result = initialize_database()

        if init_result["status"] == "skipped":
            return init_result, 200

        result = run_rss_manual_ingestion()
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/dev/rss-status")
    def rss_ingestion_status() -> tuple[dict[str, Any], int]:
        result = get_rss_ingestion_status()
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/dev/rss-preview")
    def rss_smoke_preview() -> tuple[dict[str, Any], int]:
        raw_limit = request.args.get("limit", "5")
        feed_key = request.args.get("feed", "hacker-news")

        try:
            limit = int(raw_limit)
        except ValueError:
            limit = 5

        result = build_rss_smoke_preview(feed_key, limit)
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/dev/rss-topic-draft")
    def rss_smoke_topic_draft() -> tuple[dict[str, Any], int]:
        raw_limit = request.args.get("limit", "5")
        feed_key = request.args.get("feed", "hacker-news")

        try:
            limit = int(raw_limit)
        except ValueError:
            limit = 5

        result = build_rss_smoke_topic_draft(feed_key, limit)
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/dev/rss-topic-candidates")
    def rss_topic_candidates() -> tuple[dict[str, Any], int]:
        raw_limit = request.args.get("limit", "10")

        try:
            limit = int(raw_limit)
        except ValueError:
            limit = 10

        result = get_rss_topic_candidates(limit)
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/dev/topic-candidate-groups")
    def topic_candidate_groups() -> tuple[dict[str, Any], int]:
        raw_limit = request.args.get("limit", "10")

        try:
            limit = int(raw_limit)
        except ValueError:
            limit = 10

        result = get_topic_candidate_groups(limit)
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/dev/grouped-topic-payload-preview")
    def grouped_topic_payload_preview() -> tuple[dict[str, Any], int]:
        raw_limit = request.args.get("limit", "10")

        try:
            limit = int(raw_limit)
        except ValueError:
            limit = 10

        result = get_grouped_topic_payload_preview(limit)
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/dev/topics-upsert-dry-run")
    def topics_upsert_dry_run() -> tuple[dict[str, Any], int]:
        raw_limit = request.args.get("limit", "10")

        try:
            limit = int(raw_limit)
        except ValueError:
            limit = 10

        result = get_topics_upsert_dry_run(limit)
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.post("/dev/topics-upsert-smoke")
    def topics_upsert_smoke() -> tuple[dict[str, Any], int]:
        init_result = initialize_database()

        if init_result["status"] == "skipped":
            return init_result, 200

        result = run_topics_upsert_smoke_test()
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.post("/dev/rss-to-topics-ingest")
    def rss_to_topics_ingest() -> tuple[dict[str, Any], int]:
        init_result = initialize_database()

        if init_result["status"] == "skipped":
            return init_result, 200

        raw_limit = request.args.get("limit", "3")

        try:
            limit = int(raw_limit)
        except ValueError:
            limit = 3

        result = run_rss_to_topics_ingestion(limit)
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/dev/rss-topics-status")
    def rss_topics_status() -> tuple[dict[str, Any], int]:
        raw_limit = request.args.get("limit", "10")

        try:
            limit = int(raw_limit)
        except ValueError:
            limit = 10

        result = get_rss_topics_status(limit)
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.post("/dev/rss-to-topics-smoke")
    def rss_to_topics_smoke() -> tuple[dict[str, Any], int]:
        request_body = request.get_json(silent=True) or {}
        raw_limit = request.args.get("limit", request_body.get("limit", "5"))
        feed_key = request.args.get("feed", request_body.get("feed", "hacker-news"))
        raw_dry_run = request.args.get("dry_run", request_body.get("dry_run", True))

        try:
            limit = int(raw_limit)
        except (TypeError, ValueError):
            limit = 5

        dry_run = str(raw_dry_run).strip().lower() not in {"false", "0", "no"}
        draft_result = build_rss_smoke_topic_draft(feed_key, limit)

        if draft_result["status"] != "ok":
            status_code = 502 if draft_result["status"] == "failed" else 200
            return draft_result, status_code

        if dry_run:
            return {
                **draft_result,
                "dry_run": True,
                "batch_id": None,
                "inserted_count": 0,
                "updated_count": 0,
            }, 200

        init_result = initialize_database()

        if init_result["status"] == "skipped":
            return init_result, 200

        upsert_result = upsert_rss_smoke_topic_drafts(
            draft_result["topic_drafts"],
            draft_result["feed_source"],
        )
        status_code = 502 if upsert_result["status"] == "failed" else 200

        return {
            **draft_result,
            **upsert_result,
            "feed_source": draft_result["feed_source"],
            "fetched_count": draft_result["fetched_count"],
            "normalized_count": draft_result["normalized_count"],
            "grouped_topic_count": draft_result["grouped_topic_count"],
            "dry_run": False,
        }, status_code

    @app.post("/dev/rss-smoke-rollback")
    def rss_smoke_rollback() -> tuple[dict[str, Any], int]:
        request_body = request.get_json(silent=True) or {}
        batch_id = request.args.get("batch_id", request_body.get("batch_id", ""))
        result = rollback_rss_smoke_batch(str(batch_id))
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/dev/dcard-preview")
    def dcard_smoke_preview() -> tuple[dict[str, Any], int]:
        raw_limit = request.args.get("limit", "10")

        try:
            limit = int(raw_limit)
        except ValueError:
            limit = 10

        result = build_dcard_smoke_preview(limit)
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/dev/dcard-topic-draft")
    def dcard_smoke_topic_draft() -> tuple[dict[str, Any], int]:
        raw_limit = request.args.get("limit", "10")

        try:
            limit = int(raw_limit)
        except ValueError:
            limit = 10

        result = build_dcard_smoke_topic_draft(limit)
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.post("/dev/dcard-to-topics-smoke")
    def dcard_to_topics_smoke() -> tuple[dict[str, Any], int]:
        request_body = request.get_json(silent=True) or {}
        raw_limit = request.args.get("limit", request_body.get("limit", "10"))
        raw_dry_run = request.args.get("dry_run", request_body.get("dry_run", True))

        try:
            limit = int(raw_limit)
        except (TypeError, ValueError):
            limit = 10

        dry_run = str(raw_dry_run).strip().lower() not in {"false", "0", "no"}
        draft_result = build_dcard_smoke_topic_draft(limit)

        if draft_result["status"] != "ok":
            status_code = 502 if draft_result["status"] == "failed" else 200
            return draft_result, status_code

        if dry_run:
            return {
                **draft_result,
                "dry_run": True,
                "batch_id": None,
                "inserted_count": 0,
                "updated_count": 0,
            }, 200

        init_result = initialize_database()

        if init_result["status"] == "skipped":
            return init_result, 200

        upsert_result = upsert_dcard_smoke_topic_drafts(
            draft_result["topic_drafts"],
            draft_result["feed_source"],
        )
        status_code = 502 if upsert_result["status"] == "failed" else 200

        return {
            **draft_result,
            **upsert_result,
            "feed_source": draft_result["feed_source"],
            "fetched_count": draft_result["fetched_count"],
            "normalized_count": draft_result["normalized_count"],
            "grouped_topic_count": draft_result["grouped_topic_count"],
            "dry_run": False,
        }, status_code

    @app.post("/dev/dcard-smoke-rollback")
    def dcard_smoke_rollback() -> tuple[dict[str, Any], int]:
        request_body = request.get_json(silent=True) or {}
        batch_id = request.args.get("batch_id", request_body.get("batch_id", ""))
        result = rollback_dcard_smoke_batch(str(batch_id))
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/dev/podcast-preview")
    def podcast_smoke_preview() -> tuple[dict[str, Any], int]:
        raw_limit = request.args.get("limit", "5")
        feed_key = request.args.get("feed", "planet-money")

        try:
            limit = int(raw_limit)
        except ValueError:
            limit = 5

        result = build_podcast_smoke_preview(feed_key, limit)
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/dev/podcast-topic-draft")
    def podcast_smoke_topic_draft() -> tuple[dict[str, Any], int]:
        raw_limit = request.args.get("limit", "5")
        feed_key = request.args.get("feed", "planet-money")

        try:
            limit = int(raw_limit)
        except ValueError:
            limit = 5

        result = build_podcast_smoke_topic_draft(feed_key, limit)
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.post("/dev/podcast-to-topics-smoke")
    def podcast_to_topics_smoke() -> tuple[dict[str, Any], int]:
        request_body = request.get_json(silent=True) or {}
        raw_limit = request.args.get("limit", request_body.get("limit", "5"))
        feed_key = request.args.get(
            "feed",
            request_body.get("feed", "planet-money"),
        )
        raw_dry_run = request.args.get("dry_run", request_body.get("dry_run", True))

        try:
            limit = int(raw_limit)
        except (TypeError, ValueError):
            limit = 5

        dry_run = str(raw_dry_run).strip().lower() not in {"false", "0", "no"}
        draft_result = build_podcast_smoke_topic_draft(feed_key, limit)

        if draft_result["status"] != "ok":
            status_code = 502 if draft_result["status"] == "failed" else 200
            return draft_result, status_code

        if dry_run:
            return {
                **draft_result,
                "dry_run": True,
                "batch_id": None,
                "inserted_count": 0,
                "updated_count": 0,
            }, 200

        init_result = initialize_database()

        if init_result["status"] == "skipped":
            return init_result, 200

        upsert_result = upsert_podcast_smoke_topic_drafts(
            draft_result["topic_drafts"],
            draft_result["feed_source"],
        )
        status_code = 502 if upsert_result["status"] == "failed" else 200

        return {
            **draft_result,
            **upsert_result,
            "feed_source": draft_result["feed_source"],
            "fetched_count": draft_result["fetched_count"],
            "normalized_count": draft_result["normalized_count"],
            "grouped_topic_count": draft_result["grouped_topic_count"],
            "dry_run": False,
        }, status_code

    @app.post("/dev/podcast-smoke-rollback")
    def podcast_smoke_rollback() -> tuple[dict[str, Any], int]:
        request_body = request.get_json(silent=True) or {}
        batch_id = request.args.get("batch_id", request_body.get("batch_id", ""))
        result = rollback_podcast_smoke_batch(str(batch_id))
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/reddit/status")
    def reddit_status() -> tuple[dict[str, Any], int]:
        return validate_reddit_env(), 200

    @app.post("/reddit/oauth-smoke-test")
    def reddit_oauth_smoke_test() -> tuple[dict[str, Any], int]:
        result = run_reddit_oauth_smoke_test()
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/rss/status")
    def rss_status() -> tuple[dict[str, Any], int]:
        return validate_rss_env(), 200

    @app.get("/admin/ingestion-runs/latest")
    def latest_ingestion_run() -> tuple[dict[str, Any], int]:
        result = get_latest_ingestion_run()
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/admin/ingestion-runs")
    def ingestion_run_history() -> tuple[dict[str, Any], int]:
        raw_limit = request.args.get("limit", "20")

        try:
            limit = int(raw_limit)
        except ValueError:
            limit = 20

        result = get_ingestion_run_history(
            limit=limit,
            source_type=request.args.get("source_type"),
            source_key=request.args.get("source_key"),
            status=request.args.get("status"),
        )
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/admin/ingestion-runs/<run_id>")
    def ingestion_run_detail(run_id: str) -> tuple[dict[str, Any], int]:
        result = get_ingestion_run_detail(run_id)

        if result["status"] == "not_found":
            return result, 404

        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/admin/ingestion-health")
    def ingestion_health() -> tuple[dict[str, Any], int]:
        result = get_ingestion_health_summary()
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.post("/rss/fetch-smoke-test")
    def rss_fetch_smoke_test() -> tuple[dict[str, Any], int]:
        result = run_rss_fetch_smoke_test()
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.post("/rss/parser-smoke-test")
    def rss_parser_smoke_test() -> tuple[dict[str, Any], int]:
        result = run_rss_parser_smoke_test()
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.post("/rss/dry-run-ingestion-summary")
    def rss_dry_run_ingestion_summary() -> tuple[dict[str, Any], int]:
        result = run_rss_dry_run_ingestion_summary()
        status_code = 502 if result["status"] == "failed" else 200

        return result, status_code

    @app.get("/api/topics")
    def topics_index() -> tuple[dict[str, Any], int]:
        db_topics = get_topics_from_database()
        is_database_source = len(db_topics) > 0
        topics = db_topics if is_database_source else get_mock_topics()

        return {
            "allTopics": topics,
            "industryTopics": topics,
            "userKeywordTopics": topics,
            "source": "postgresql" if is_database_source else "flask-mock-api",
        }, 200

    @app.get("/api/topics/<topic_id>")
    def topics_show(topic_id: str) -> tuple[dict[str, Any], int]:
        topic = find_topic_from_database(topic_id) or find_mock_topic(topic_id)

        if topic is None:
            return {"error": "Topic not found."}, 404

        return topic, 200

    @app.get("/api/user-settings")
    def user_settings_show() -> tuple[dict[str, Any], int]:
        return get_user_settings(), 200

    @app.post("/api/user-settings")
    @app.put("/api/user-settings")
    def user_settings_update() -> tuple[dict[str, Any], int]:
        payload = request.get_json(silent=True) or {}

        return save_user_settings(payload), 200

    @app.get("/api/favorites")
    def favorites_index() -> tuple[dict[str, Any], int]:
        return get_favorites(), 200

    @app.post("/api/favorites/<topic_id>")
    def favorites_create(topic_id: str) -> tuple[dict[str, Any], int]:
        return add_favorite(topic_id), 200

    @app.delete("/api/favorites/<topic_id>")
    def favorites_delete(topic_id: str) -> tuple[dict[str, Any], int]:
        return remove_favorite(topic_id), 200

    return app


def load_json_mock_data(file_path: str | Path = DEFAULT_SAMPLE_PATH) -> Any:
    path = Path(file_path)

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    with path.open("r", encoding="utf-8") as json_file:
        return json.load(json_file)


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)

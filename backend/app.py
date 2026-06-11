import json
import os
from pathlib import Path
from typing import Any

from flask import Flask, request

from db import (
    get_rss_ingestion_status,
    get_rss_topic_candidates,
    get_database_url,
    initialize_database,
    insert_smoke_test_data,
    run_rss_upsert_smoke_test,
)
from favorites import add_favorite, get_favorites, remove_favorite
from mock_topics import find_mock_topic, get_mock_topics
from reddit_oauth import run_reddit_oauth_smoke_test, validate_reddit_env
from rss_feed import (
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

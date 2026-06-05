import json
import os
from pathlib import Path
from typing import Any

from flask import Flask, request

from db import get_database_url, initialize_database, insert_smoke_test_data
from favorites import add_favorite, get_favorites, remove_favorite
from topics import build_topics_from_json_sample, find_topic
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

    @app.get("/api/topics")
    def topics_index() -> tuple[dict[str, Any], int]:
        topics = build_topics_from_json_sample(load_json_mock_data())

        return {
            "allTopics": topics,
            "industryTopics": topics,
            "userKeywordTopics": topics,
            "source": "flask-json-fallback",
        }, 200

    @app.get("/api/topics/<topic_id>")
    def topics_show(topic_id: str) -> tuple[dict[str, Any], int]:
        topics = build_topics_from_json_sample(load_json_mock_data())
        topic = find_topic(topics, topic_id)

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

from __future__ import annotations

import base64
import json
import os
from typing import Any
from urllib import error, parse, request


REDDIT_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
REQUIRED_REDDIT_ENV_VARS = [
    "REDDIT_CLIENT_ID",
    "REDDIT_CLIENT_SECRET",
    "REDDIT_USER_AGENT",
]


def validate_reddit_env() -> dict[str, Any]:
    missing = [
        key for key in REQUIRED_REDDIT_ENV_VARS
        if not os.getenv(key, "").strip()
    ]

    if missing:
        return {
            "status": "skipped",
            "reason": "Missing Reddit API environment variables.",
            "missing": missing,
        }

    return {
        "status": "ok",
        "missing": [],
    }


def run_reddit_oauth_smoke_test(timeout_seconds: int = 10) -> dict[str, Any]:
    env_status = validate_reddit_env()

    if env_status["status"] != "ok":
        return env_status

    client_id = os.environ["REDDIT_CLIENT_ID"].strip()
    client_secret = os.environ["REDDIT_CLIENT_SECRET"].strip()
    user_agent = os.environ["REDDIT_USER_AGENT"].strip()
    credentials = f"{client_id}:{client_secret}".encode("utf-8")
    encoded_credentials = base64.b64encode(credentials).decode("ascii")
    payload = parse.urlencode({"grant_type": "client_credentials"}).encode(
        "utf-8",
    )
    token_request = request.Request(
        REDDIT_TOKEN_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": user_agent,
            "Accept": "application/json",
        },
    )

    try:
        with request.urlopen(token_request, timeout=timeout_seconds) as response:
            token_data = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as reddit_error:
        response_body = reddit_error.read().decode("utf-8", errors="replace")

        return {
            "status": "failed",
            "reason": "Reddit OAuth request failed.",
            "http_status": reddit_error.code,
            "error": response_body[:500],
        }
    except error.URLError as url_error:
        return {
            "status": "failed",
            "reason": "Reddit OAuth request could not reach Reddit.",
            "error": str(url_error.reason),
        }
    except TimeoutError:
        return {
            "status": "failed",
            "reason": "Reddit OAuth request timed out.",
        }
    except (json.JSONDecodeError, KeyError) as parse_error:
        return {
            "status": "failed",
            "reason": "Reddit OAuth response was invalid.",
            "error": str(parse_error),
        }

    return {
        "status": "ok",
        "has_access_token": bool(token_data.get("access_token")),
        "token_type": token_data.get("token_type"),
        "expires_in": token_data.get("expires_in"),
        "scope": token_data.get("scope"),
    }

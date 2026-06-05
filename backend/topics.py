from __future__ import annotations

from typing import Any


REDDIT_FALLBACK_TOPIC = {
    "id": "reddit-artificial",
    "topic": "Reddit r/artificial 熱門話題",
    "score": 310,
    "momentum": "stable",
    "summary": "Reddit fallback 資料整合 AI agents、open source models 與 AI search 討論。",
    "insight": "Reddit 可作為第二資料來源，驗證多來源資料整合能力。",
    "source": "Reddit r/artificial",
    "contentCount": 3,
    "relatedContent": [
        {
            "id": "reddit-fallback-ai-agents",
            "title": "AI agents are becoming more common in daily workflows",
            "source": "Reddit r/artificial",
            "text": "People are discussing how AI agents can summarize research, plan tasks, and automate repetitive work.",
        },
        {
            "id": "reddit-fallback-open-source-models",
            "title": "Open source AI models are getting more attention",
            "source": "Reddit r/artificial",
            "text": "The community is comparing open source models with commercial AI tools.",
        },
        {
            "id": "reddit-fallback-ai-search",
            "title": "AI search tools may change how people browse the web",
            "source": "Reddit r/artificial",
            "text": "Users are debating whether AI summaries can replace traditional search result pages.",
        },
    ],
    "inspirationIdeas": [
        "整理 Reddit AI 社群正在討論的三個重點。",
        "比較 Reddit 與 Threads / Dcard 對 AI 工具的討論角度。",
    ],
    "platformTags": ["Reddit r/artificial"],
    "topicTags": ["Reddit", "AI", "第二資料來源"],
    "searchText": "reddit artificial ai agents open source models ai search second source",
}


def _safe_int(value: Any, fallback: int = 0) -> int:
    if isinstance(value, bool):
        return fallback

    if isinstance(value, int):
        return value

    return fallback


def _get_items(json_data: Any) -> list[dict[str, Any]]:
    if isinstance(json_data, dict) and isinstance(json_data.get("items"), list):
        return [
            item for item in json_data["items"]
            if isinstance(item, dict)
        ]

    if isinstance(json_data, list):
        return [item for item in json_data if isinstance(item, dict)]

    return []


def build_topics_from_json_sample(json_data: Any) -> list[dict[str, Any]]:
    topics: list[dict[str, Any]] = []

    for index, item in enumerate(_get_items(json_data)):
        topic_id = str(item.get("id") or f"sample-topic-{index + 1}")
        platform = str(item.get("platform") or item.get("source") or "sample")
        title = str(item.get("title") or "未命名話題")
        content = str(item.get("content") or item.get("text") or "")
        like_count = _safe_int(item.get("likeCount"))
        comment_count = _safe_int(item.get("commentCount"))
        score = like_count + comment_count * 2

        topics.append(
            {
                "id": topic_id,
                "topic": title,
                "score": score,
                "momentum": "stable" if score >= 40 else "weak",
                "summary": content[:120] or title,
                "insight": "此資料由後端 JSON sample fallback 產生。",
                "source": platform,
                "contentCount": 1,
                "relatedContent": [
                    {
                        "id": topic_id,
                        "title": title,
                        "source": platform,
                        "text": content,
                    },
                ],
                "inspirationIdeas": [
                    f"用「{title}」整理一篇社群觀察。",
                    f"分析 {platform} 使用者對此話題的討論角度。",
                ],
                "platformTags": [platform],
                "topicTags": item.get("hotTags")
                if isinstance(item.get("hotTags"), list)
                else [],
                "searchText": f"{title} {content} {platform}".lower(),
            },
        )

    return [*topics, REDDIT_FALLBACK_TOPIC]


def find_topic(topics: list[dict[str, Any]], topic_id: str) -> dict[str, Any] | None:
    return next((topic for topic in topics if topic["id"] == topic_id), None)

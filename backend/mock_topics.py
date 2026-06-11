from __future__ import annotations

import copy
from typing import Any


MOCK_TOPICS: list[dict[str, Any]] = [
    {
        "id": "ai-search",
        "topic": "AI Search Workflow",
        "score": 5560,
        "growthRate": 42,
        "momentum": "rising",
        "lifecycleStage": "growing",
        "scoreHistory": [
            {"label": "Week 1", "score": 48},
            {"label": "Week 2", "score": 64},
            {"label": "Week 3", "score": 82},
            {"label": "Week 4", "score": 100},
        ],
        "summary": "Creators are comparing AI search tools with traditional search workflows.",
        "insight": "The topic is gaining attention because AI summaries can shorten research and content planning time.",
        "source": "Flask Mock API",
        "contentCount": 3,
        "relatedContent": [
            {
                "id": "ai-search-threads",
                "title": "AI search is changing research habits",
                "source": "Threads",
                "text": "Users discuss replacing keyword search with AI-assisted summaries.",
            },
            {
                "id": "ai-search-dcard",
                "title": "How students use AI search for reports",
                "source": "Dcard",
                "text": "Students compare AI search tools for finding references faster.",
            },
        ],
        "inspirationIdeas": [
            "Compare AI search and traditional search in a short carousel.",
            "Share a checklist for validating AI-generated search summaries.",
        ],
        "platformTags": ["Threads", "Dcard"],
        "topicTags": ["AI", "Search", "Workflow"],
        "searchText": "ai search workflow threads dcard research summaries",
    },
    {
        "id": "ai-video-tools",
        "topic": "AI Video Tools",
        "score": 3420,
        "growthRate": 28,
        "momentum": "stable",
        "lifecycleStage": "mainstream",
        "scoreHistory": [
            {"label": "Week 1", "score": 52},
            {"label": "Week 2", "score": 61},
            {"label": "Week 3", "score": 69},
            {"label": "Week 4", "score": 74},
        ],
        "summary": "Short-form creators are testing AI video editing, captions, and repurposing tools.",
        "insight": "The discussion is mature enough for practical tutorials and comparison content.",
        "source": "Flask Mock API",
        "contentCount": 2,
        "relatedContent": [
            {
                "id": "ai-video-dcard",
                "title": "AI video editors for beginners",
                "source": "Dcard",
                "text": "Creators compare editing speed, caption quality, and templates.",
            }
        ],
        "inspirationIdeas": [
            "Create a beginner guide for choosing an AI video editor.",
            "Turn a single blog post into a video workflow demo.",
        ],
        "platformTags": ["Dcard"],
        "topicTags": ["AI", "Video", "Creator Tools"],
        "searchText": "ai video tools creator editing captions templates",
    },
    {
        "id": "ai-workflow",
        "topic": "AI Workflow Automation",
        "score": 4140,
        "growthRate": 36,
        "momentum": "rising",
        "lifecycleStage": "growing",
        "scoreHistory": [
            {"label": "Week 1", "score": 46},
            {"label": "Week 2", "score": 58},
            {"label": "Week 3", "score": 77},
            {"label": "Week 4", "score": 92},
        ],
        "summary": "Teams are exploring AI agents and automation for recurring content tasks.",
        "insight": "The topic works well for operational playbooks because users want concrete workflows.",
        "source": "Flask Mock API",
        "contentCount": 3,
        "relatedContent": [
            {
                "id": "ai-workflow-threads",
                "title": "AI agents for daily workflows",
                "source": "Threads",
                "text": "People share task planning, summarization, and automation examples.",
            }
        ],
        "inspirationIdeas": [
            "Publish a simple AI workflow map for marketers.",
            "Share a before-and-after example of automating a repeated task.",
        ],
        "platformTags": ["Threads"],
        "topicTags": ["AI", "Automation", "Agents"],
        "searchText": "ai workflow automation agents marketing operations",
    },
]


def get_mock_topics() -> list[dict[str, Any]]:
    return copy.deepcopy(MOCK_TOPICS)


def find_mock_topic(topic_id: str) -> dict[str, Any] | None:
    return next(
        (topic for topic in get_mock_topics() if topic["id"] == topic_id),
        None,
    )

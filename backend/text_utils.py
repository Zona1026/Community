from __future__ import annotations

import html
import re
from typing import Any


BLOCK_BREAK_RE = re.compile(
    r"(?i)<\s*(br|/p|/div|/li|/ul|/ol|/h[1-6]|/section|/article)\s*/?\s*>",
)
SCRIPT_STYLE_RE = re.compile(
    r"(?is)<\s*(script|style)[^>]*>.*?<\s*/\s*\1\s*>",
)
HTML_TAG_RE = re.compile(r"(?s)<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")
RESIDUAL_MARKUP_RE = re.compile(r"(?i)</?[a-z][^<>\s]{0,20}[^<>]*>")


def clean_html_to_text(value: Any, max_length: int = 500) -> str:
    text = html.unescape(str(value or ""))

    if not text:
        return ""

    text = SCRIPT_STYLE_RE.sub(" ", text)
    text = BLOCK_BREAK_RE.sub(" ", text)
    text = HTML_TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = RESIDUAL_MARKUP_RE.sub(" ", text)
    text = WHITESPACE_RE.sub(" ", text).strip()

    if max_length > 0 and len(text) > max_length:
        trimmed = text[:max_length].rstrip()
        last_space = trimmed.rfind(" ")

        if last_space >= max_length // 2:
            trimmed = trimmed[:last_space].rstrip()

        text = f"{trimmed}..."

    return text

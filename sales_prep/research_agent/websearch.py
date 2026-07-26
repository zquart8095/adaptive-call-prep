"""Shared web_search_tool_result extraction. Factored out so both the chat
agent (sales_prep/chat/agent.py) and this flow's gather_section handle the
same real Anthropic response shape identically — including the case where
.content is a WebSearchToolResultError object, not a list of results."""

from typing import Any


def extract_web_search_hits(response) -> list[dict[str, Any]]:
    hits = []
    for block in response.content:
        if getattr(block, "type", None) != "web_search_tool_result":
            continue
        content = block.content
        if not isinstance(content, list):
            continue  # a WebSearchToolResultError, not results — skip
        for item in content:
            hits.append(
                {
                    "title": getattr(item, "title", ""),
                    "url": getattr(item, "url", ""),
                    "page_age": getattr(item, "page_age", None),
                }
            )
    return hits

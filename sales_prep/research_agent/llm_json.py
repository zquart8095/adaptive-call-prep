"""Shared JSON-object parsing for the plan/critique/compose LLM calls, with
a single retry-once-on-malformed-JSON pass. These nodes have no templated
fallback (a template literally can't propose a plan or critique
sufficiency) — unlike sales_prep/synthesis/, which falls back to
TemplateSynthesizer on any LLM hiccup, a clean retry matters more here."""

import json
import re
from typing import Any

_MODEL = "claude-sonnet-5"


def extract_text(content_blocks: list) -> str:
    """claude-sonnet-5 can return a ThinkingBlock before the TextBlock —
    same real bug found and fixed in synthesis/llm_synthesizer.py."""
    for block in content_blocks:
        if getattr(block, "type", None) == "text":
            return block.text
    raise ValueError("No text block in response content")


def _parse_json_object(content: str) -> dict[str, Any]:
    stripped = content.strip()
    match = re.match(r"^```(?:json)?\s*\n?(.*)\n?```$", stripped, re.DOTALL)
    if match:
        stripped = match.group(1).strip()
    return json.loads(stripped)


def call_for_json(client, *, system: str, user: str, max_tokens: int = 1536) -> dict[str, Any]:
    """Calls the model, parses JSON from its text response, and retries
    once (with a corrective follow-up message) if parsing fails. Raises if
    the retry also fails — no silent fallback for this flow."""
    messages: list[dict] = [{"role": "user", "content": user}]

    response = client.messages.create(model=_MODEL, max_tokens=max_tokens, system=system, messages=messages)
    try:
        return _parse_json_object(extract_text(response.content))
    except (ValueError, json.JSONDecodeError):
        pass

    messages.append({"role": "assistant", "content": response.content})
    messages.append(
        {
            "role": "user",
            "content": "Your last response wasn't valid JSON. Respond with ONLY the raw JSON object, no other text.",
        }
    )
    retry_response = client.messages.create(model=_MODEL, max_tokens=max_tokens, system=system, messages=messages)
    return _parse_json_object(extract_text(retry_response.content))

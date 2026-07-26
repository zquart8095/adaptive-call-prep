"""Shared fake-Anthropic-response building blocks — used by test_chat_agent.py
and the research_agent test suite so both can drive real control-flow logic
(tool dispatch/resume, JSON-returning calls, web_search result indexing)
without any real API calls."""

from types import SimpleNamespace


def text_block(text: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=text)


def tool_use_block(block_id: str, name: str, tool_input: dict) -> SimpleNamespace:
    return SimpleNamespace(type="tool_use", id=block_id, name=name, input=tool_input)


def web_search_result_block(results: list[SimpleNamespace]) -> SimpleNamespace:
    return SimpleNamespace(type="web_search_tool_result", content=results)


def response(content: list, stop_reason: str = "end_turn") -> SimpleNamespace:
    return SimpleNamespace(content=content, stop_reason=stop_reason)


def json_response(payload_json: str, stop_reason: str = "end_turn") -> SimpleNamespace:
    """A response whose only content block is JSON text — the common case
    for the research_agent's plan/critique/compose nodes, which all expect
    a single JSON object back."""
    return response([text_block(payload_json)], stop_reason=stop_reason)


class FakeMessages:
    def __init__(self, responses: list):
        self._responses = list(responses)
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self._responses.pop(0)


class FakeAnthropicClient:
    def __init__(self, responses: list):
        self.messages = FakeMessages(responses)

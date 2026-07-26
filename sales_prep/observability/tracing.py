"""LangSmith tracing — off by default, zero setup required to run the demo.

Once enabled, every pipeline node (each research branch's steps, the join,
the review gate) shows up as its own span in the trace tree automatically —
that's LangGraph's native behavior, no code changes needed for it. What
this module adds on top: wrapping the Anthropic client so LLM calls show
up as nested spans with full prompt/response, and tagging each graph
invocation with metadata (company, stage, synthesizer_version) so runs are
filterable in the LangSmith UI.
"""

import os
from typing import Any
from uuid import UUID


def is_tracing_enabled() -> bool:
    """Both vars are required — the API key alone does NOT turn tracing on.
    A real, documented LangSmith gotcha, not specific to this repo."""
    return bool(os.environ.get("LANGSMITH_API_KEY")) and os.environ.get(
        "LANGSMITH_TRACING", ""
    ).lower() == "true"


def wrap_anthropic_if_enabled(client: Any) -> Any:
    if not is_tracing_enabled():
        return client
    from langsmith.wrappers import wrap_anthropic

    return wrap_anthropic(client)


def traced_run_config(
    *,
    run_name: str,
    thread_id: str,
    run_id: UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Builds a RunnableConfig. Safe to pass run_name/metadata/run_id even
    when tracing is disabled — LangGraph just ignores them; no branching
    needed here."""
    config: dict[str, Any] = {
        "configurable": {"thread_id": thread_id},
        "run_name": run_name,
        "metadata": metadata or {},
    }
    if run_id is not None:
        config["run_id"] = run_id
    return config

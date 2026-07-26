"""Full-graph tests via build_graph(anthropic_client=FakeAnthropicClient([...])),
mirroring test_pipeline_smoke.py's approach: drive the real compiled graph
through .invoke()/Command(resume=...), no monkeypatching."""

import json
from types import SimpleNamespace

from langgraph.types import Command

from sales_prep.research_agent.graph import build_graph

from .conftest import make_call_context
from .fakes import FakeAnthropicClient, json_response, response, text_block, web_search_result_block

_GOAL_1 = {
    "goal_id": "goal-1",
    "title": "Map the buying committee",
    "description": "Understand who's involved in the decision.",
    "skill_hints": ["company_snapshot"],
    "why_it_matters_for_this_call": "Discovery calls need to identify the champion.",
}

_COMPOSE_JSON = json.dumps(
    {
        "executive_summary": "Alderleaf Robotics is a strong fit for Vantage Ops Suite.",
        "sections": [{"section_id": "goal-1", "narrative_with_markers": "Found via [cite-1]."}],
        "call_action_plan": {
            "suggested_opener": "Hi Jordan, congrats on the VP role and the Ohio expansion.",
            "discovery_questions": ["What's driving the shift-handoff pain point?"],
            "anticipated_objections": [{"objection": "Budget concerns", "suggested_response": "Focus on ROI."}],
        },
    }
)

_SUFFICIENT_CRITIQUE = json.dumps({"sufficient": True, "gaps": [], "focus_for_next_search": None})


def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def test_plan_approved_first_try_produces_report():
    plan_json = json.dumps({"goals": [_GOAL_1]})

    client = FakeAnthropicClient(
        [
            json_response(plan_json),
            json_response(_SUFFICIENT_CRITIQUE),
            json_response(_COMPOSE_JSON),
        ]
    )
    graph = build_graph(anthropic_client=client)
    config = _config("approve-first-try")

    result = graph.invoke({"context": make_call_context().model_dump(mode="json")}, config)
    assert "__interrupt__" in result
    payload = result["__interrupt__"][0].value
    assert payload["research_plan"][0]["goal_id"] == "goal-1"
    assert payload["plan_revision"] == 1

    final_result = graph.invoke(Command(resume={"decision": "approved"}), config)
    report = final_result["final_report"]

    assert report["company"] == "Alderleaf Robotics"
    assert len(report["sections"]) == 1
    assert report["sections"][0]["citation_ids"] == ["cite-1"]
    assert report["call_action_plan"]["suggested_opener"]
    assert len(report["citations"]) == 1
    assert report["citations"][0]["url"] is None  # fixture-derived, never fabricated


def test_plan_revision_loop():
    plan_v1 = json.dumps({"goals": [_GOAL_1]})
    plan_v2 = json.dumps(
        {"goals": [{**_GOAL_1, "description": "Revised: also check stakeholder buy-in specifically."}]}
    )

    client = FakeAnthropicClient(
        [
            json_response(plan_v1),
            json_response(plan_v2),
            json_response(_SUFFICIENT_CRITIQUE),
            json_response(_COMPOSE_JSON),
        ]
    )
    graph = build_graph(anthropic_client=client)
    config = _config("revision-loop")

    first = graph.invoke({"context": make_call_context().model_dump(mode="json")}, config)
    assert first["__interrupt__"][0].value["plan_revision"] == 1

    second = graph.invoke(Command(resume={"decision": "revise", "feedback": "add stakeholder buy-in"}), config)
    second_payload = second["__interrupt__"][0].value
    assert second_payload["plan_revision"] == 2
    assert "stakeholder buy-in" in second_payload["research_plan"][0]["description"]

    final_result = graph.invoke(Command(resume={"decision": "approved"}), config)
    assert final_result["final_report"]["company"] == "Alderleaf Robotics"


def test_critique_reflect_loop_triggers_real_followup_gather():
    plan_json = json.dumps({"goals": [_GOAL_1]})
    insufficient_critique = json.dumps(
        {"sufficient": False, "gaps": ["no funding signal"], "focus_for_next_search": "recent funding news"}
    )
    followup_response = response(
        [
            text_block("Additional research found Alderleaf recently opened a new manufacturing facility."),
            web_search_result_block(
                [SimpleNamespace(title="Alderleaf News", url="https://example.com/news", page_age="1 week ago")]
            ),
        ],
        "end_turn",
    )

    client = FakeAnthropicClient(
        [
            json_response(plan_json),
            json_response(insufficient_critique),
            followup_response,
            json_response(_SUFFICIENT_CRITIQUE),
            json_response(_COMPOSE_JSON),
        ]
    )
    graph = build_graph(anthropic_client=client)
    config = _config("reflect-loop")

    graph.invoke({"context": make_call_context().model_dump(mode="json")}, config)
    final_result = graph.invoke(Command(resume={"decision": "approved"}), config)

    section = final_result["sections"]["goal-1"]
    assert section["iteration"] == 2
    kinds = [f["kind"] for f in section["raw_findings"]]
    assert kinds == ["fixture", "web_search_followup"]

    report = final_result["final_report"]
    citation_kinds = {c["source_kind"] for c in report["citations"]}
    assert citation_kinds == {"fixture", "web_search"}


def test_critique_loop_bounded_by_max_iterations():
    plan_json = json.dumps({"goals": [_GOAL_1]})
    insufficient_critique = json.dumps(
        {"sufficient": False, "gaps": ["still thin"], "focus_for_next_search": "more info"}
    )
    followup_response = response([text_block("Found a little more.")], "end_turn")

    client = FakeAnthropicClient(
        [
            json_response(plan_json),
            json_response(insufficient_critique),  # after fixture gather (iteration 1)
            followup_response,  # gather iteration 2
            json_response(insufficient_critique),  # after iteration 2
            followup_response,  # gather iteration 3
            json_response(insufficient_critique),  # after iteration 3 -> hits max, advances
            json_response(_COMPOSE_JSON),
        ]
    )
    graph = build_graph(anthropic_client=client)
    config = _config("bounded-loop")

    graph.invoke({"context": make_call_context().model_dump(mode="json")}, config)
    final_result = graph.invoke(Command(resume={"decision": "approved"}), config)

    # No infinite loop, no crash — composition still proceeded.
    assert final_result["sections"]["goal-1"]["iteration"] == 3
    assert final_result["final_report"]["company"] == "Alderleaf Robotics"


def test_malformed_json_then_valid_retry_recovers():
    malformed = response([text_block("Sorry, I can't help with that.")], "end_turn")
    plan_json = json.dumps({"goals": [_GOAL_1]})

    client = FakeAnthropicClient(
        [
            malformed,
            json_response(plan_json),
            json_response(_SUFFICIENT_CRITIQUE),
            json_response(_COMPOSE_JSON),
        ]
    )
    graph = build_graph(anthropic_client=client)
    config = _config("retry-recovery")

    result = graph.invoke({"context": make_call_context().model_dump(mode="json")}, config)
    # Two client.create() calls happened inside generate_research_plan alone
    # (malformed + retry) before the interrupt — confirms retry-once works.
    assert client.messages.calls
    payload = result["__interrupt__"][0].value
    assert payload["research_plan"][0]["goal_id"] == "goal-1"

    final_result = graph.invoke(Command(resume={"decision": "approved"}), config)
    assert final_result["final_report"]["company"] == "Alderleaf Robotics"

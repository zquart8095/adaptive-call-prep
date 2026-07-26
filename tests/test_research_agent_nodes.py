from sales_prep.research_agent.nodes.advance import advance_section, route_after_advance
from sales_prep.research_agent.nodes.critique import route_after_critique
from sales_prep.research_agent.nodes.gather import make_gather_section
from sales_prep.research_agent.nodes.outline import build_outline
from sales_prep.research_agent.nodes.plan_gate import route_after_plan_approval

from .conftest import make_call_context
from .fakes import FakeAnthropicClient

_PLAN = [
    {
        "goal_id": "goal-1",
        "title": "Map the buying committee",
        "description": "Understand who's involved in the decision.",
        "skill_hints": ["stakeholders"],
        "why_it_matters_for_this_call": "Discovery calls need to identify the champion.",
    },
    {
        "goal_id": "goal-2",
        "title": "Assess competitive displacement risk",
        "description": "Understand what they already use.",
        "skill_hints": ["tech_competitive"],
        "why_it_matters_for_this_call": "Positioning depends on what they'd be replacing.",
    },
]


def test_route_after_plan_approval_approved():
    state = {"plan_decision": {"decision": "approved"}}
    assert route_after_plan_approval(state) == "build_outline"


def test_route_after_plan_approval_revise():
    state = {"plan_decision": {"decision": "revise"}}
    assert route_after_plan_approval(state) == "generate_research_plan"


def test_build_outline_from_canned_plan():
    state = {"research_plan": _PLAN}
    result = build_outline(state)

    assert result["section_order"] == ["goal-1", "goal-2"]
    assert result["current_section_index"] == 0
    assert set(result["sections"]) == {"goal-1", "goal-2"}
    assert result["sections"]["goal-1"]["goal"] == _PLAN[0]
    assert result["sections"]["goal-1"]["iteration"] == 0
    assert result["sections"]["goal-1"]["raw_findings"] == []


def test_route_after_critique_sufficient_advances():
    state = {
        "section_order": ["goal-1"],
        "current_section_index": 0,
        "max_iterations_per_section": 3,
        "sections": {"goal-1": {"critique": {"sufficient": True}, "iteration": 1}},
    }
    assert route_after_critique(state) == "advance_section"


def test_route_after_critique_insufficient_but_under_max_loops_back():
    state = {
        "section_order": ["goal-1"],
        "current_section_index": 0,
        "max_iterations_per_section": 3,
        "sections": {"goal-1": {"critique": {"sufficient": False}, "iteration": 1}},
    }
    assert route_after_critique(state) == "gather_section"


def test_route_after_critique_stops_at_max_iterations_even_if_insufficient():
    state = {
        "section_order": ["goal-1"],
        "current_section_index": 0,
        "max_iterations_per_section": 3,
        "sections": {"goal-1": {"critique": {"sufficient": False}, "iteration": 3}},
    }
    assert route_after_critique(state) == "advance_section"


def test_advance_section_increments_index():
    assert advance_section({"current_section_index": 0}) == {"current_section_index": 1}


def test_route_after_advance_more_sections():
    state = {"section_order": ["goal-1", "goal-2"], "current_section_index": 1}
    assert route_after_advance(state) == "gather_section"


def test_route_after_advance_done():
    state = {"section_order": ["goal-1", "goal-2"], "current_section_index": 2}
    assert route_after_advance(state) == "compose_report"


def test_gather_section_iteration_zero_never_touches_llm_client():
    """First pass is fixture-only — no LLM call at all. A client with zero
    scripted responses will raise IndexError the moment .create() is
    called, which is exactly the assertion: it must never be called."""
    client_that_must_not_be_used = FakeAnthropicClient([])
    gather_section = make_gather_section(client_that_must_not_be_used)

    state = {
        "context": make_call_context().model_dump(mode="json"),
        "section_order": ["goal-1"],
        "current_section_index": 0,
        "sections": {
            "goal-1": {
                "goal": _PLAN[0],  # skill_hints: ["stakeholders"]
                "raw_findings": [],
                "iteration": 0,
                "critique": None,
                "is_demo_fallback": False,
            }
        },
    }

    result = gather_section(state)  # would raise IndexError if the client were touched

    updated_section = result["sections"]["goal-1"]
    assert updated_section["iteration"] == 1
    assert len(updated_section["raw_findings"]) == 1
    assert updated_section["raw_findings"][0]["kind"] == "fixture"
    assert updated_section["raw_findings"][0]["skill"] == "stakeholders"

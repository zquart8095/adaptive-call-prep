from langgraph.types import interrupt

from sales_prep.research_agent.state import ResearchState


def plan_approval_gate(state: ResearchState) -> dict:
    """Human-in-the-loop pause — mirrors pipeline/nodes/review_gate.py's
    interrupt()/resume pattern, but runs *before* research instead of
    after. This human-gated loop is intentionally unbounded (a person
    controls the pace); the machine-driven critique loop later is bounded
    by max_iterations_per_section."""
    payload = interrupt(
        {
            "run_id": state["run_id"],
            "company": state["context"]["prospect_company"],
            "research_plan": state["research_plan"],
            "plan_revision": state["plan_revision"],
        }
    )

    decision = payload.get("decision")
    result: dict = {"plan_decision": {"decision": decision, "feedback": payload.get("feedback")}}
    if decision == "revise":
        result["plan_feedback"] = payload.get("feedback")
    return result


def route_after_plan_approval(state: ResearchState) -> str:
    return "build_outline" if state["plan_decision"]["decision"] == "approved" else "generate_research_plan"

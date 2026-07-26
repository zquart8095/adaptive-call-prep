from sales_prep.research_agent.state import ResearchState


def build_outline(state: ResearchState) -> dict:
    """Converts the approved plan into an ordered section list. No LLM
    call needed — the plan step already assigned skill_hints per goal."""
    plan = state["research_plan"]
    section_order = [goal["goal_id"] for goal in plan]
    sections = {
        goal["goal_id"]: {
            "goal": goal,
            "raw_findings": [],
            "iteration": 0,
            "critique": None,
            "is_demo_fallback": False,
        }
        for goal in plan
    }
    return {"section_order": section_order, "sections": sections, "current_section_index": 0}

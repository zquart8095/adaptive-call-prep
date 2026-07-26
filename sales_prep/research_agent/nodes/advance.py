from sales_prep.research_agent.state import ResearchState


def advance_section(state: ResearchState) -> dict:
    return {"current_section_index": state["current_section_index"] + 1}


def route_after_advance(state: ResearchState) -> str:
    if state["current_section_index"] >= len(state["section_order"]):
        return "compose_report"
    return "gather_section"

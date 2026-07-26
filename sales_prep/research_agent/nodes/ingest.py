import uuid

from sales_prep.research_agent.state import ResearchState


def ingest_research_context(state: ResearchState) -> dict:
    return {
        "run_id": state.get("run_id") or uuid.uuid4().hex[:8],
        "plan_revision": 0,
        "max_iterations_per_section": state.get("max_iterations_per_section") or 3,
    }

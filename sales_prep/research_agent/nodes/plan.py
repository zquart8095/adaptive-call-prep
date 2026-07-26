import anthropic

from sales_prep.config import CallContext
from sales_prep.observability.tracing import wrap_anthropic_if_enabled
from sales_prep.research_agent.llm_json import call_for_json
from sales_prep.research_agent.prompts import build_plan_prompt
from sales_prep.research_agent.state import ResearchState


def make_generate_research_plan(client=None):
    """client injectable for testing (mirrors ChatSession's constructor-
    injection pattern) — real client construction stays lazy, inside the
    returned node function, so importing this module (e.g. for
    langgraph.json) never requires ANTHROPIC_API_KEY."""

    def generate_research_plan(state: ResearchState) -> dict:
        c = client if client is not None else wrap_anthropic_if_enabled(anthropic.Anthropic())
        context = CallContext(**state["context"])
        is_revision = state.get("plan_revision", 0) > 0

        system, user = build_plan_prompt(
            context,
            research_focus=state.get("research_focus"),
            prior_plan=state.get("research_plan") if is_revision else None,
            feedback=state.get("plan_feedback") if is_revision else None,
        )
        parsed = call_for_json(c, system=system, user=user)
        return {
            "research_plan": parsed.get("goals", []),
            "plan_revision": state.get("plan_revision", 0) + 1,
        }

    return generate_research_plan

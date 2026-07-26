import anthropic

from sales_prep.config import CallContext
from sales_prep.observability.tracing import wrap_anthropic_if_enabled
from sales_prep.research_agent.llm_json import call_for_json
from sales_prep.research_agent.prompts import build_critique_prompt
from sales_prep.research_agent.state import ResearchState


def make_critique_section(client=None):
    def critique_section(state: ResearchState) -> dict:
        c = client if client is not None else wrap_anthropic_if_enabled(anthropic.Anthropic())
        context = CallContext(**state["context"])
        section_id = state["section_order"][state["current_section_index"]]
        section = dict(state["sections"][section_id])

        system, user = build_critique_prompt(context, section["goal"], section["raw_findings"])
        section["critique"] = call_for_json(c, system=system, user=user)

        sections = dict(state["sections"])
        sections[section_id] = section
        return {"sections": sections}

    return critique_section


def route_after_critique(state: ResearchState) -> str:
    section_id = state["section_order"][state["current_section_index"]]
    section = state["sections"][section_id]
    critique = section["critique"] or {}
    if critique.get("sufficient") or section["iteration"] >= state["max_iterations_per_section"]:
        return "advance_section"
    return "gather_section"

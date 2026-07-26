import anthropic

from sales_prep.config import CallContext
from sales_prep.observability.tracing import wrap_anthropic_if_enabled
from sales_prep.research_agent.prompts import build_followup_search_instruction
from sales_prep.research_agent.skills import SKILL_FETCHERS, is_fallback_result
from sales_prep.research_agent.state import ResearchState
from sales_prep.research_agent.websearch import extract_web_search_hits

_MODEL = "claude-sonnet-5"
_WEB_SEARCH_TOOL = {"type": "web_search_20260318", "name": "web_search", "max_uses": 3}


def make_gather_section(client=None):
    def gather_section(state: ResearchState) -> dict:
        c = client if client is not None else wrap_anthropic_if_enabled(anthropic.Anthropic())
        context = CallContext(**state["context"])
        section_id = state["section_order"][state["current_section_index"]]
        section = dict(state["sections"][section_id])
        goal = section["goal"]

        if section["iteration"] == 0:
            # First pass: the same fixture providers the fixed pipeline uses,
            # limited to whichever skills this specific goal called for.
            findings = list(section.get("raw_findings", []))
            is_fallback = section.get("is_demo_fallback", False)
            for skill_name in goal.get("skill_hints", []):
                fetcher = SKILL_FETCHERS.get(skill_name)
                if fetcher is None:
                    continue
                raw = fetcher(context)
                findings.append({"kind": "fixture", "skill": skill_name, "payload": raw})
                is_fallback = is_fallback or is_fallback_result(raw)
            section["raw_findings"] = findings
            section["is_demo_fallback"] = is_fallback
        else:
            # Follow-up after critique found a gap: real web search targeted
            # at the critique's focus, not a re-query of the same fixtures.
            critique = section.get("critique") or {}
            focus = critique.get("focus_for_next_search") or goal["description"]
            instruction = build_followup_search_instruction(context, goal, focus)
            response = c.messages.create(
                model=_MODEL,
                max_tokens=1024,
                tools=[_WEB_SEARCH_TOOL],
                messages=[{"role": "user", "content": instruction}],
            )
            summary = "\n".join(
                block.text for block in response.content if getattr(block, "type", None) == "text"
            ).strip()
            findings = list(section.get("raw_findings", []))
            findings.append(
                {
                    "kind": "web_search_followup",
                    "summary": summary,
                    "citations": extract_web_search_hits(response),
                }
            )
            section["raw_findings"] = findings

        section["iteration"] = section["iteration"] + 1
        sections = dict(state["sections"])
        sections[section_id] = section
        return {"sections": sections}

    return gather_section

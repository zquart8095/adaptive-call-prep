from datetime import datetime, timezone

import anthropic

from sales_prep.config import CallContext
from sales_prep.observability.tracing import wrap_anthropic_if_enabled
from sales_prep.research_agent.llm_json import call_for_json
from sales_prep.research_agent.models import (
    AnticipatedObjection,
    CallActionPlan,
    Citation,
    ReportSection,
    ResearchReport,
)
from sales_prep.research_agent.prompts import build_compose_prompt
from sales_prep.research_agent.state import ResearchState


def _fixture_label(skill: str, item: dict) -> str:
    if skill == "signals":
        return f"Recent Signal — {item.get('source', 'unknown source')}"
    if skill == "stakeholders":
        return f"Stakeholder Profile — {item.get('name', 'unknown')}"
    if skill == "tech_competitive":
        return "Competitive Landscape"
    return "Company Snapshot"


def _build_citation_registry(sections: dict) -> list[dict]:
    """Assigns stable cite-N ids across all findings. Fixture-derived
    citations never get a fabricated URL (url=None) — only real
    web_search citations carry one. The LLM composing the report only
    ever sees this registry, never raw source material, so it can't
    invent a citation that isn't backed by something real."""
    registry: list[dict] = []
    counter = 1

    for section in sections.values():
        for finding in section.get("raw_findings", []):
            if finding["kind"] == "fixture":
                payload = finding["payload"]
                items = payload if isinstance(payload, list) else [payload]
                for item in items:
                    registry.append(
                        {
                            "citation_id": f"cite-{counter}",
                            "label": _fixture_label(finding["skill"], item),
                            "url": None,
                            "source_kind": "fixture",
                        }
                    )
                    counter += 1
            elif finding["kind"] == "web_search_followup":
                for cite in finding.get("citations", []):
                    registry.append(
                        {
                            "citation_id": f"cite-{counter}",
                            "label": f"Web: {cite.get('title', 'untitled')}",
                            "url": cite.get("url"),
                            "source_kind": "web_search",
                        }
                    )
                    counter += 1
    return registry


def make_compose_report(client=None):
    def compose_report(state: ResearchState) -> dict:
        c = client if client is not None else wrap_anthropic_if_enabled(anthropic.Anthropic())
        context = CallContext(**state["context"])
        sections = state["sections"]

        citation_registry = _build_citation_registry(sections)
        valid_citation_ids = {entry["citation_id"] for entry in citation_registry}

        sections_payload = [
            {
                "section_id": goal_id,
                "title": sections[goal_id]["goal"]["title"],
                "why_it_matters_for_this_call": sections[goal_id]["goal"]["why_it_matters_for_this_call"],
                "findings": sections[goal_id]["raw_findings"],
            }
            for goal_id in state["section_order"]
        ]

        system, user = build_compose_prompt(context, sections_payload, citation_registry)
        # The default max_tokens (1536) truncated mid-JSON here for real —
        # composing N sections' narrative + a full action plan is a much
        # bigger generation than plan/critique. Found via two real runs:
        # a 5-section plan produced an "Unterminated string" JSONDecodeError
        # on both the initial call and the retry, even at 4096. Paired with
        # the prompt now explicitly asking for concise (2-4 sentence)
        # section narrative, both to reduce truncation risk and because a
        # scannable pre-call brief is the actual design goal.
        parsed = call_for_json(c, system=system, user=user, max_tokens=8192)

        report_sections = []
        for s in parsed.get("sections", []):
            section_id = s["section_id"]
            narrative = s.get("narrative_with_markers", "")
            used_ids = [cid for cid in valid_citation_ids if f"[{cid}]" in narrative]
            goal = sections.get(section_id, {}).get("goal", {})
            report_sections.append(
                ReportSection(
                    section_id=section_id,
                    title=goal.get("title", section_id),
                    narrative=narrative,
                    citation_ids=used_ids,
                    why_it_matters_for_this_call=goal.get("why_it_matters_for_this_call", ""),
                )
            )

        action_plan_data = parsed.get("call_action_plan", {})
        call_action_plan = CallActionPlan(
            suggested_opener=action_plan_data.get("suggested_opener", ""),
            discovery_questions=action_plan_data.get("discovery_questions", []),
            anticipated_objections=[
                AnticipatedObjection(**obj) for obj in action_plan_data.get("anticipated_objections", [])
            ],
        )

        is_demo_fallback = any(
            sections[goal_id].get("is_demo_fallback", False) for goal_id in state["section_order"]
        )

        report = ResearchReport(
            run_id=state["run_id"],
            company=context.prospect_company,
            generated_at=datetime.now(timezone.utc).isoformat(),
            executive_summary=parsed.get("executive_summary", ""),
            sections=report_sections,
            citations=[Citation(**entry) for entry in citation_registry],
            call_action_plan=call_action_plan,
            is_demo_fallback=is_demo_fallback,
        )
        return {"final_report": report.model_dump()}

    return compose_report

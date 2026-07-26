"""Sales-specific prompt builders. Deliberately NOT generic "deep research"
prompts — each one reasons about deal_stage/meeting_type/vendor context so
the plan, critique, and final output are shaped by what a sales rep
actually needs, not a generic research report about the same company."""

import json

from sales_prep.config import CallContext

_PLAN_SYSTEM = (
    "You are helping a B2B sales rep prepare for an upcoming call by proposing a "
    "research plan — NOT a generic research report outline. Each goal must be "
    "framed as a real sales-prep need (e.g. mapping the buying committee, "
    "assessing fit/pain points, gauging competitive displacement risk, "
    "anticipating objections, finding a warm opener/rapport angle), and you must "
    "reason about the deal_stage and meeting_type to decide which of the four "
    "available research skills actually matter for THIS call — don't propose "
    "using all four skills reflexively; a cold_outbound call needs different prep "
    "than a negotiation-stage call. Available skill hints: company_snapshot, "
    "signals, stakeholders, tech_competitive.\n\n"
    'Respond with raw JSON only: {"goals": [{"goal_id": str, "title": str, '
    '"description": str, "skill_hints": [str, ...], '
    '"why_it_matters_for_this_call": str}, ...]}'
)


def build_plan_prompt(
    context: CallContext,
    *,
    research_focus: str | None = None,
    prior_plan: list[dict] | None = None,
    feedback: str | None = None,
) -> tuple[str, str]:
    payload: dict = {"call_context": context.model_dump(mode="json"), "research_focus": research_focus}
    if prior_plan is not None:
        payload["prior_plan"] = prior_plan
        payload["rep_feedback_on_prior_plan"] = feedback
    return _PLAN_SYSTEM, json.dumps(payload, default=str)


def build_critique_prompt(context: CallContext, goal: dict, raw_findings: list[dict]) -> tuple[str, str]:
    system = (
        "You are evaluating whether enough has been found to prepare a sales rep "
        "for a specific goal ahead of their call. The question is NOT \"is this "
        "factually complete\" in a general research sense — it's: would "
        f"{context.salesperson_name} feel ready to run a {context.meeting_type} at "
        f"the {context.deal_stage.value} stage with what's been found for this "
        "goal? Frame any gaps as concrete sales blind spots (e.g. \"no signal on "
        "who holds budget authority\", \"haven't confirmed if they've evaluated a "
        "direct competitor\"), not generic research thinness.\n\n"
        'Respond with raw JSON only: {"sufficient": bool, "gaps": [str, ...], '
        '"focus_for_next_search": str | null}'
    )
    user = json.dumps({"goal": goal, "findings_so_far": raw_findings}, default=str)
    return system, user


def build_followup_search_instruction(context: CallContext, goal: dict, focus: str) -> str:
    return (
        f'For the sales-prep goal "{goal["title"]}" ahead of a call with '
        f"{context.prospect_company}, search the web for: {focus}. Summarize what "
        "you find in a few sentences grounded in real search results — don't "
        "speculate beyond what the search actually returns."
    )


def build_compose_prompt(
    context: CallContext, sections_payload: list[dict], citation_registry: list[dict]
) -> tuple[str, str]:
    system = (
        "You are composing the final call-prep deliverable for a sales rep, not a "
        "generic research report. Keep every section's narrative to 2-4 concise "
        "sentences — this needs to be scannable in the couple of minutes before a "
        "call, not a report to read cover to cover. Write per-section narrative "
        "referencing sources by their citation id in [cite-N] form — use ONLY the "
        "ids given in the citation registry below, never invent a URL or a fact not "
        "present in the findings. Also produce a concrete call action plan: a "
        "suggested opener tailored to this specific prospect and deal stage "
        f"({context.deal_stage.value}), a ranked list of discovery questions, and "
        "anticipated objections with suggested responses grounded in what was "
        "actually found.\n\n"
        'Respond with raw JSON only: {"executive_summary": str, "sections": '
        '[{"section_id": str, "narrative_with_markers": str}, ...], '
        '"call_action_plan": {"suggested_opener": str, "discovery_questions": '
        '[str, ...], "anticipated_objections": [{"objection": str, '
        '"suggested_response": str}, ...]}}'
    )
    user = json.dumps(
        {
            "call_context": context.model_dump(mode="json"),
            "sections": sections_payload,
            "citation_registry": citation_registry,
        },
        default=str,
    )
    return system, user

from typing import Any, Literal, TypedDict


class ResearchGoal(TypedDict):
    goal_id: str
    title: str
    description: str
    skill_hints: list[str]  # subset of {"company_snapshot","signals","stakeholders","tech_competitive"}
    why_it_matters_for_this_call: str


class FixtureFinding(TypedDict):
    kind: Literal["fixture"]
    skill: str
    payload: Any


class WebSearchFollowUp(TypedDict):
    """A follow-up research iteration, triggered when critique_section found a
    gap the four fixed fixtures can't fill — uses Anthropic's hosted
    web_search tool rather than re-querying the same static fixtures with
    cosmetic param tweaks."""

    kind: Literal["web_search_followup"]
    summary: str
    citations: list[dict[str, Any]]  # [{"title", "url", "page_age"}]


class SectionState(TypedDict, total=False):
    goal: ResearchGoal
    raw_findings: list[dict[str, Any]]  # FixtureFinding | WebSearchFollowUp
    iteration: int
    critique: dict[str, Any] | None  # {"sufficient": bool, "gaps": [...], "focus_for_next_search": str|None}
    is_demo_fallback: bool


class ResearchState(TypedDict, total=False):
    context: dict[str, Any]
    research_focus: str | None
    run_id: str
    max_iterations_per_section: int

    plan_revision: int
    plan_feedback: str | None
    research_plan: list[ResearchGoal]
    plan_decision: dict[str, Any]

    section_order: list[str]
    sections: dict[str, SectionState]
    current_section_index: int

    final_report: dict[str, Any]

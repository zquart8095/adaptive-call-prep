from pydantic import BaseModel


class Citation(BaseModel):
    citation_id: str  # "cite-1", "cite-2", ...
    label: str  # e.g. "Recent Signal — TechWire Daily" or "Web: <title>"
    url: str | None = None  # None for fixture-derived (fictional) sources — never fabricated
    source_kind: str  # "fixture" | "web_search"


class ReportSection(BaseModel):
    section_id: str
    title: str
    narrative: str  # prose containing [cite-N] markers, already resolved to plain text + citation list
    citation_ids: list[str]
    why_it_matters_for_this_call: str


class AnticipatedObjection(BaseModel):
    objection: str
    suggested_response: str


class CallActionPlan(BaseModel):
    """The concrete, sales-specific deliverable — what a rep actually opens
    before the call. Distinct from a generic research report's table of
    contents; this is what differentiates this flow's output from the
    fixed pipeline's talking_points/suggested_open_questions sections."""

    suggested_opener: str
    discovery_questions: list[str]
    anticipated_objections: list[AnticipatedObjection]


class ResearchReport(BaseModel):
    run_id: str
    company: str
    generated_at: str
    executive_summary: str
    sections: list[ReportSection]
    citations: list[Citation]
    call_action_plan: CallActionPlan
    is_demo_fallback: bool = False

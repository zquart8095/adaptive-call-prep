// Hand-kept TS mirrors of the Python models in sales_prep/research_agent/
// (models.py, state.py, config.py) and the interrupt payload built in
// nodes/plan_gate.py. No schema codegen — acceptable duplication at this
// demo's scope, but keep these in sync if the Python side changes shape.

export type DealStage = 'cold_outbound' | 'discovery' | 'demo_scheduled' | 'negotiation'

export interface CallContext {
  prospect_company: string
  prospect_domain: string
  salesperson_name: string
  vendor_product_name: string
  vendor_product_one_liner: string
  deal_stage: DealStage
  meeting_type: string
  call_datetime: string
  sdr_notes: string
  target_stakeholders: string[]
}

export interface ResearchGoal {
  goal_id: string
  title: string
  description: string
  skill_hints: string[]
  why_it_matters_for_this_call: string
}

export interface PlanApprovalPayload {
  run_id: string
  company: string
  research_plan: ResearchGoal[]
  plan_revision: number
}

export interface Citation {
  citation_id: string
  label: string
  url: string | null
  source_kind: 'fixture' | 'web_search'
}

export interface AnticipatedObjection {
  objection: string
  suggested_response: string
}

export interface CallActionPlan {
  suggested_opener: string
  discovery_questions: string[]
  anticipated_objections: AnticipatedObjection[]
}

export interface ReportSection {
  section_id: string
  title: string
  narrative: string
  citation_ids: string[]
  why_it_matters_for_this_call: string
}

export interface ResearchReport {
  run_id: string
  company: string
  generated_at: string
  executive_summary: string
  sections: ReportSection[]
  citations: Citation[]
  call_action_plan: CallActionPlan
  is_demo_fallback: boolean
}

// The research_agent graph's full state shape (subset actually read by the
// frontend) — mirrors sales_prep/research_agent/state.py::ResearchState.
export interface ResearchState {
  context?: CallContext
  research_focus?: string | null
  run_id?: string
  research_plan?: ResearchGoal[]
  plan_revision?: number
  section_order?: string[]
  current_section_index?: number
  sections?: Record<
    string,
    {
      goal: ResearchGoal
      iteration: number
      critique: { sufficient: boolean; gaps: string[]; focus_for_next_search: string | null } | null
    }
  >
  final_report?: ResearchReport
}

export interface TimelineEntry {
  id: string
  label: string
  detail?: string
}

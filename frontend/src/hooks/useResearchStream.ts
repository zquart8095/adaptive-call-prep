import { useCallback, useEffect, useRef, useState } from 'react'
import { useStream } from '@langchain/langgraph-sdk/react'

import { ASSISTANT_ID, LANGGRAPH_API_URL } from '@/lib/langgraph'
import type {
  CallContext,
  PlanApprovalPayload,
  ResearchReport,
  ResearchState,
  TimelineEntry,
} from '@/types/research'

export type Phase = 'input' | 'planning' | 'plan_review' | 'researching' | 'done' | 'error'

// node name -> human label, per the graph in sales_prep/research_agent/graph.py
const NODE_LABELS: Record<string, string> = {
  ingest_research_context: 'Setting up',
  generate_research_plan: 'Generating research plan',
  build_outline: 'Building research outline',
  gather_section: 'Researching',
  critique_section: 'Reflecting on findings',
  advance_section: 'Moving to next goal',
  compose_report: 'Composing final report',
}

function describeUpdate(nodeName: string, update: Record<string, unknown>): { label: string; detail?: string } {
  const baseLabel = NODE_LABELS[nodeName] ?? nodeName

  if (nodeName === 'gather_section' || nodeName === 'critique_section') {
    const sections = update.sections as ResearchState['sections'] | undefined
    const entries = sections ? Object.values(sections) : []
    const current = entries[entries.length - 1]
    if (current) {
      let label = `${baseLabel}: ${current.goal.title}`
      if (nodeName === 'gather_section' && current.iteration > 1) {
        label += ` (follow-up search #${current.iteration - 1})`
      }
      const detail =
        nodeName === 'critique_section' && current.critique
          ? current.critique.sufficient
            ? 'Sufficient — moving on'
            : `Gap found: ${current.critique.gaps.join('; ')}`
          : undefined
      return { label, detail }
    }
  }

  return { label: baseLabel }
}

function clock(totalSeconds: number): string {
  const m = Math.floor(totalSeconds / 60)
  const s = totalSeconds % 60
  return `${m}:${s < 10 ? '0' : ''}${s}`
}

interface Session {
  company: string
  domain: string
  stakeholderCount: number
}

export function useResearchStream() {
  const [timeline, setTimeline] = useState<TimelineEntry[]>([])
  const [phase, setPhase] = useState<Phase>('input')
  const [session, setSession] = useState<Session | undefined>()
  const [revisionCount, setRevisionCount] = useState(0)
  const [elapsed, setElapsed] = useState(0)

  const tickRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const stopClock = useCallback(() => {
    if (tickRef.current) {
      clearInterval(tickRef.current)
      tickRef.current = null
    }
  }, [])

  const startClock = useCallback(() => {
    stopClock()
    setElapsed(0)
    tickRef.current = setInterval(() => setElapsed((s) => s + 1), 1000)
  }, [stopClock])

  useEffect(() => stopClock, [stopClock])

  const thread = useStream<ResearchState>({
    apiUrl: LANGGRAPH_API_URL,
    assistantId: ASSISTANT_ID,
    onUpdateEvent: (data) => {
      setTimeline((prev) => {
        const additions: TimelineEntry[] = []
        for (const [nodeName, update] of Object.entries(data ?? {})) {
          if (!(nodeName in NODE_LABELS)) continue
          const { label, detail } = describeUpdate(nodeName, update as Record<string, unknown>)
          additions.push({ id: `${nodeName}-${prev.length + additions.length}`, label, detail })
        }
        return [...prev, ...additions]
      })
    },
    onError: () => {
      stopClock()
      setPhase('error')
    },
  })

  const start = useCallback(
    (context: CallContext, researchFocus: string | undefined) => {
      setTimeline([])
      setRevisionCount(0)
      setSession({
        company: context.prospect_company,
        domain: context.prospect_domain,
        stakeholderCount: context.target_stakeholders.length,
      })
      setPhase('planning')
      startClock()
      thread.submit({ context, research_focus: researchFocus ?? null })
    },
    [thread, startClock],
  )

  const approvePlan = useCallback(() => {
    setPhase('researching')
    startClock()
    thread.submit(undefined, { command: { resume: { decision: 'approved' } } })
  }, [thread, startClock])

  const revisePlan = useCallback(
    (feedback: string) => {
      setRevisionCount((n) => n + 1)
      setPhase('planning')
      startClock()
      thread.submit(undefined, { command: { resume: { decision: 'revise', feedback } } })
    },
    [thread, startClock],
  )

  const interruptPayload = thread.interrupt?.value as PlanApprovalPayload | undefined
  const report = thread.values?.final_report as ResearchReport | undefined
  const derivedPhase: Phase = report ? 'done' : interruptPayload ? 'plan_review' : phase

  useEffect(() => {
    if (!thread.isLoading) stopClock()
  }, [thread.isLoading, stopClock])

  const workStatus =
    derivedPhase === 'planning'
      ? {
          kicker: 'Planning',
          label: revisionCount > 0 ? 'Reworking the research plan…' : 'Thinking through the research plan…',
        }
      : derivedPhase === 'plan_review'
        ? { kicker: 'Paused for you', label: 'Plan ready — waiting on your call' }
        : derivedPhase === 'researching'
          ? { kicker: 'Researching', label: 'Researching and reflecting — this runs unattended' }
          : { kicker: '', label: '' }

  const workMeta = `${clock(elapsed)} elapsed · ${timeline.length} step${timeline.length === 1 ? '' : 's'} completed`

  return {
    start,
    approvePlan,
    revisePlan,
    timeline,
    interruptPayload,
    report,
    phase: derivedPhase,
    isLoading: thread.isLoading,
    error: thread.error,
    session,
    workStatus,
    workMeta,
  }
}

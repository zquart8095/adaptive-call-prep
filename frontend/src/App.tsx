import { useEffect, useState } from 'react'

import { ActivityTimeline } from '@/components/ActivityTimeline'
import { ContextForm } from '@/components/ContextForm'
import { PlanReviewCard } from '@/components/PlanReviewCard'
import { ReportView } from '@/components/ReportView'
import { Stepper } from '@/components/Stepper'
import { Button } from '@/components/ui/button'
import { useResearchStream } from '@/hooks/useResearchStream'
import type { CallContext } from '@/types/research'

function useTheme() {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const stored = localStorage.getItem('theme')
    if (stored === 'light' || stored === 'dark') return stored
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
    localStorage.setItem('theme', theme)
  }, [theme])

  return { theme, toggleTheme: () => setTheme((t) => (t === 'light' ? 'dark' : 'light')) }
}

export default function App() {
  const {
    start,
    approvePlan,
    revisePlan,
    timeline,
    interruptPayload,
    report,
    phase,
    isLoading,
    error,
    session,
    workStatus,
    workMeta,
  } = useResearchStream()
  const { theme, toggleTheme } = useTheme()

  function handleStart(context: CallContext, researchFocus: string | undefined) {
    start(context, researchFocus)
  }

  const runMeta = session
    ? `${session.company} · ${session.domain} · ${session.stakeholderCount} stakeholder${session.stakeholderCount === 1 ? '' : 's'}`
    : ''

  return (
    <div className="min-h-screen bg-page text-foreground">
      <header className="sticky top-0 z-30 border-b border-hairline bg-page">
        <div className="mx-auto flex max-w-5xl items-center gap-4 px-6 py-3.5">
          <span className="font-mono text-[11px] font-medium tracking-[0.13em] uppercase">Adaptive Call Prep</span>
          <div className="flex-1" />
          <span className="truncate font-mono text-[11px] text-muted-foreground">{runMeta}</span>
          <Button variant="outline" size="sm" onClick={() => window.location.reload()} className="font-mono text-[10.5px] uppercase">
            Reset
          </Button>
          <Button variant="outline" size="sm" onClick={toggleTheme} className="font-mono text-[10.5px] uppercase">
            {theme === 'light' ? 'Light' : 'Dark'}
          </Button>
        </div>
      </header>

      <div className="mx-auto max-w-5xl px-6 py-6.5 pb-24">
        <Stepper phase={phase} />

        {phase === 'input' && <ContextForm onStart={handleStart} disabled={isLoading} />}

        {(phase === 'planning' || phase === 'plan_review' || phase === 'researching') && (
          <div className="animate-phase-in grid items-start gap-5.5 lg:grid-cols-2">
            <ActivityTimeline
              entries={timeline}
              isLoading={isLoading}
              statusKicker={workStatus.kicker}
              statusLabel={workStatus.label}
              statusMeta={workMeta}
            />
            {phase === 'plan_review' && interruptPayload && (
              <PlanReviewCard payload={interruptPayload} onApprove={approvePlan} onRevise={revisePlan} disabled={isLoading} />
            )}
          </div>
        )}

        {phase === 'error' && (
          <div className="border-destructive/50 bg-destructive/10 rounded-md border p-3 text-sm">
            Something went wrong: {String(error)}
          </div>
        )}

        {phase === 'done' && report && <ReportView report={report} />}
      </div>
    </div>
  )
}

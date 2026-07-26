import { useState } from 'react'

import { ChatBox } from '@/components/ChatBox'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import type { PlanApprovalPayload } from '@/types/research'

interface PlanReviewCardProps {
  payload: PlanApprovalPayload
  onApprove: () => void
  onRevise: (feedback: string) => void
  disabled?: boolean
}

export function PlanReviewCard({ payload, onApprove, onRevise, disabled }: PlanReviewCardProps) {
  const [revising, setRevising] = useState(false)

  function handleRevise(feedback: string) {
    setRevising(false)
    onRevise(feedback)
  }

  return (
    <Card className="animate-phase-in gap-0 py-0">
      <div className="border-b border-hairline p-5 pb-4.5">
        <div className="mb-2 flex items-center gap-2">
          <span className="font-mono text-[10.5px] tracking-[0.12em] text-muted-foreground uppercase">
            Awaiting your approval
          </span>
          <Badge variant="outline" className="font-mono text-[10.5px]">
            Revision {payload.plan_revision}
          </Badge>
        </div>
        <h2 className="mb-1.5 text-[22px] leading-tight font-semibold tracking-[-0.02em]">
          Research plan for {payload.company}
        </h2>
        <p className="text-[13.5px] text-muted-foreground">
          {payload.research_plan.length} research goals — approve as-is, or tell the agent what to change.
        </p>
      </div>

      <ol className="list-none">
        {payload.research_plan.map((goal, i) => (
          <li key={goal.goal_id} className="grid grid-cols-[26px_minmax(0,1fr)] gap-x-3.5 border-b border-hairline p-5">
            <span className="pt-0.5 font-mono text-[11.5px] text-muted-foreground">
              {String(i + 1).padStart(2, '0')}
            </span>
            <div className="grid min-w-0 gap-1.5">
              <div className="text-[15px] font-medium tracking-[-0.01em]">{goal.title}</div>
              <div className="text-[13.5px] text-muted-foreground">{goal.why_it_matters_for_this_call}</div>
              <div className="mt-0.5 flex flex-wrap gap-1.5">
                {goal.skill_hints.map((skill) => (
                  <Badge key={skill} variant="secondary" className="font-mono text-[10.5px]">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
          </li>
        ))}
      </ol>

      <div className="grid gap-3.5 bg-muted p-5">
        <div className="flex flex-wrap items-center gap-2.5">
          <Button onClick={onApprove} disabled={disabled}>
            Approve &amp; start research
          </Button>
          <Button variant="outline" onClick={() => setRevising((r) => !r)} disabled={disabled}>
            {revising ? 'Cancel revision' : 'Revise with feedback'}
          </Button>
        </div>
        {revising && (
          <div className="animate-row-in">
            <ChatBox
              placeholder="What should change? e.g. focus more on competitive risk, drop the funding history goal"
              submitLabel="Revise plan"
              onSubmit={handleRevise}
              disabled={disabled}
            />
          </div>
        )}
      </div>
    </Card>
  )
}

import { useState, type ReactNode } from 'react'

import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { cn } from '@/lib/utils'
import type { CallContext, DealStage } from '@/types/research'

// Mirrors data/call_contexts/alderleaf_robotics.json at the repo root —
// kept in sync by hand (small, static fixture, not worth a build step).
const ALDERLEAF_DEMO: CallContext = {
  prospect_company: 'Alderleaf Robotics',
  prospect_domain: 'alderleaf-robotics.example',
  salesperson_name: 'Priya Nakamura',
  vendor_product_name: 'Vantage Ops Suite',
  vendor_product_one_liner: 'Unified observability and workflow automation for industrial operations teams',
  deal_stage: 'discovery',
  meeting_type: '30-min discovery call',
  call_datetime: '2026-07-29T15:00:00-07:00',
  sdr_notes: 'Champion is VP Ops; mentioned pain around manual shift-handoff reporting.',
  target_stakeholders: ['Jordan Ellery', 'Sam Okafor'],
}

const DEAL_STAGES: DealStage[] = ['cold_outbound', 'discovery', 'demo_scheduled', 'negotiation']

function SectionKicker({ children }: { children: ReactNode }) {
  return (
    <div className="col-span-full flex items-baseline gap-2.5">
      <span className="font-mono text-[10.5px] tracking-[0.12em] text-muted-foreground uppercase">{children}</span>
      <span className="h-px flex-1 bg-hairline" />
    </div>
  )
}

function Field({ label, className, children }: { label: string; className?: string; children: ReactNode }) {
  return (
    <div className={cn('grid gap-1.5', className)}>
      <Label className="text-[12.5px] font-medium text-muted-foreground">{label}</Label>
      {children}
    </div>
  )
}

interface ContextFormProps {
  onStart: (context: CallContext, researchFocus: string | undefined) => void
  disabled?: boolean
}

export function ContextForm({ onStart, disabled }: ContextFormProps) {
  const [context, setContext] = useState<CallContext>(ALDERLEAF_DEMO)
  const [stakeholdersText, setStakeholdersText] = useState(ALDERLEAF_DEMO.target_stakeholders.join(', '))
  const [researchFocus, setResearchFocus] = useState('')

  function update<K extends keyof CallContext>(key: K, value: CallContext[K]) {
    setContext((prev) => ({ ...prev, [key]: value }))
  }

  function loadDemo() {
    setContext(ALDERLEAF_DEMO)
    setStakeholdersText(ALDERLEAF_DEMO.target_stakeholders.join(', '))
  }

  function handleSubmit() {
    const finalContext: CallContext = {
      ...context,
      target_stakeholders: stakeholdersText
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
    }
    onStart(finalContext, researchFocus.trim() || undefined)
  }

  return (
    <div>
      <div className="mb-6 max-w-[660px]">
        <h1 className="mb-2 text-[29px] leading-[1.12] font-semibold tracking-[-0.025em]">Set the call context</h1>
        <p className="text-[15px] text-muted-foreground">
          The agent proposes a research plan from this context. You review and revise it before any research
          runs — inspired by Google's Deep Search / Gemini Fullstack pattern, adapted for sales call prep (see
          the README for the trade-off writeup).
        </p>
      </div>

      <Card className="gap-0 py-0">
        <div className="flex items-center justify-between gap-4 border-b border-hairline bg-muted px-5 py-3.5">
          <span className="font-mono text-[10.5px] tracking-[0.12em] text-muted-foreground uppercase">
            Session context
          </span>
          <Button variant="outline" size="sm" onClick={loadDemo} disabled={disabled}>
            Load Alderleaf demo
          </Button>
        </div>

        <section className="grid grid-cols-1 gap-x-5 gap-y-4 border-b border-hairline p-5 sm:grid-cols-2">
          <SectionKicker>01 / Who you're calling</SectionKicker>
          <Field label="Prospect company">
            <Input value={context.prospect_company} onChange={(e) => update('prospect_company', e.target.value)} disabled={disabled} />
          </Field>
          <Field label="Prospect domain">
            <Input
              className="font-mono text-[13px]"
              value={context.prospect_domain}
              onChange={(e) => update('prospect_domain', e.target.value)}
              disabled={disabled}
            />
          </Field>
          <Field label="Target stakeholders">
            <Input
              placeholder="Comma-separated"
              value={stakeholdersText}
              onChange={(e) => setStakeholdersText(e.target.value)}
              disabled={disabled}
            />
          </Field>
          <Field label="Meeting type">
            <Input value={context.meeting_type} onChange={(e) => update('meeting_type', e.target.value)} disabled={disabled} />
          </Field>
          <div className="col-span-full grid gap-2">
            <Label className="text-[12.5px] font-medium text-muted-foreground">Deal stage</Label>
            <div className="flex flex-wrap gap-1.5">
              {DEAL_STAGES.map((stage) => (
                <button
                  key={stage}
                  type="button"
                  onClick={() => update('deal_stage', stage)}
                  disabled={disabled}
                  className={cn(
                    'rounded-lg border px-3 py-1.5 font-mono text-[11.5px] transition-colors',
                    context.deal_stage === stage
                      ? 'border-transparent bg-primary text-primary-foreground'
                      : 'border-border text-muted-foreground hover:border-strong',
                  )}
                >
                  {stage.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          </div>
        </section>

        <section className="grid grid-cols-1 gap-x-5 gap-y-4 border-b border-hairline p-5 sm:grid-cols-2">
          <SectionKicker>02 / What you're selling</SectionKicker>
          <Field label="Vendor product">
            <Input value={context.vendor_product_name} onChange={(e) => update('vendor_product_name', e.target.value)} disabled={disabled} />
          </Field>
          <Field label="Salesperson">
            <Input value={context.salesperson_name} onChange={(e) => update('salesperson_name', e.target.value)} disabled={disabled} />
          </Field>
          <Field label="One-liner" className="col-span-full">
            <Input
              value={context.vendor_product_one_liner}
              onChange={(e) => update('vendor_product_one_liner', e.target.value)}
              disabled={disabled}
            />
          </Field>
        </section>

        <section className="grid gap-4 p-5">
          <SectionKicker>03 / Steer the research</SectionKicker>
          <div className="grid grid-cols-1 gap-x-5 gap-y-4 sm:grid-cols-2">
            <Field label="SDR notes">
              <Textarea rows={3} value={context.sdr_notes} onChange={(e) => update('sdr_notes', e.target.value)} disabled={disabled} />
            </Field>
            <Field label="Research focus — optional">
              <Textarea
                rows={3}
                placeholder="e.g. Focus more on stakeholder buy-in, less on general company background"
                value={researchFocus}
                onChange={(e) => setResearchFocus(e.target.value)}
                disabled={disabled}
              />
            </Field>
          </div>
        </section>

        <div className="flex flex-wrap items-center justify-between gap-3.5 border-t border-hairline bg-muted px-5 py-4">
          <span className="text-[12.5px] text-muted-foreground">Nothing runs until you approve the plan.</span>
          <Button onClick={handleSubmit} disabled={disabled}>
            Propose research plan
          </Button>
        </div>
      </Card>
    </div>
  )
}

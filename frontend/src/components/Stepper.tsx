import { cn } from '@/lib/utils'
import type { Phase } from '@/hooks/useResearchStream'

const STEPS: { num: string; label: string; phases: Phase[] }[] = [
  { num: '01', label: 'Context', phases: ['input'] },
  { num: '02', label: 'Plan review', phases: ['planning', 'plan_review'] },
  { num: '03', label: 'Research', phases: ['researching'] },
  { num: '04', label: 'Report', phases: ['done'] },
]

export function Stepper({ phase }: { phase: Phase }) {
  const activeIdx = STEPS.findIndex((s) => s.phases.includes(phase))

  return (
    <nav className="mb-8 flex flex-wrap gap-x-0 gap-y-1.5">
      {STEPS.map((step, i) => {
        const done = i < activeIdx
        const active = i === activeIdx
        return (
          <div key={step.num} className="flex min-w-0 flex-1 basis-[190px] items-center gap-2.5">
            <div
              className={cn(
                'flex min-w-0 items-center gap-2.5 transition-opacity duration-300',
                active ? 'opacity-100' : done ? 'opacity-60' : 'opacity-35',
              )}
            >
              <span
                className={cn(
                  'flex h-[21px] w-[21px] flex-none items-center justify-center rounded-md border font-mono text-[10.5px] font-medium transition-colors duration-300',
                  active
                    ? 'border-transparent bg-primary text-primary-foreground'
                    : 'border-border text-muted-foreground',
                )}
              >
                {done ? '✓' : step.num}
              </span>
              <span className={cn('truncate text-[13px]', active ? 'font-medium' : 'font-normal')}>
                {step.label}
              </span>
            </div>
            <div
              className={cn(
                'h-px min-w-3.5 flex-1 transition-colors duration-300',
                i <= activeIdx ? 'bg-strong' : 'bg-hairline',
              )}
            />
          </div>
        )
      })}
    </nav>
  )
}

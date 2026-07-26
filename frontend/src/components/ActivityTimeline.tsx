import { TimelineEntry } from '@/components/TimelineEntry'
import { Card } from '@/components/ui/card'
import { LumaSpin } from '@/components/ui/luma-spin'
import { cn } from '@/lib/utils'
import type { TimelineEntry as TimelineEntryType } from '@/types/research'

interface ActivityTimelineProps {
  entries: TimelineEntryType[]
  isLoading: boolean
  statusKicker: string
  statusLabel: string
  statusMeta: string
}

export function ActivityTimeline({ entries, isLoading, statusKicker, statusLabel, statusMeta }: ActivityTimelineProps) {
  return (
    <Card className="animate-phase-in min-w-0 gap-0 py-0">
      <div className="flex items-center gap-4.5 border-b border-hairline bg-muted p-5">
        {isLoading ? (
          <LumaSpin />
        ) : (
          <div className="flex h-[65px] w-[65px] flex-none items-center justify-center">
            <div className="flex h-[34px] w-[34px] items-center justify-center rounded-[11px] border-[1.5px] border-strong">
              <div className="h-[11px] w-[11px] rounded-[4px] bg-foreground" />
            </div>
          </div>
        )}
        <div className="grid min-w-0 gap-1">
          <div className="flex items-center gap-2">
            <span className={cn('h-1.5 w-1.5 rounded-sm bg-foreground', isLoading && 'animate-live-pulse')} />
            <span className="font-mono text-[10.5px] tracking-[0.12em] text-muted-foreground uppercase">
              {statusKicker}
            </span>
          </div>
          <div className="text-[17px] leading-tight font-medium tracking-[-0.015em]">{statusLabel}</div>
          <div className="font-mono text-[11.5px] text-muted-foreground">{statusMeta}</div>
        </div>
      </div>

      <div className="max-h-[420px] overflow-y-auto px-5 pt-1.5 pb-5">
        {entries.length === 0 ? (
          <div className={cn('py-5.5 text-[13px] text-muted-foreground', isLoading && 'animate-breathe')}>
            Waiting for the first step…
          </div>
        ) : (
          <div>
            {entries.map((entry, i) => (
              <TimelineEntry key={entry.id} entry={entry} live={isLoading && i === entries.length - 1} />
            ))}
          </div>
        )}
      </div>
    </Card>
  )
}

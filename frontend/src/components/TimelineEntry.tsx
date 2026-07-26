import { cn } from '@/lib/utils'
import type { TimelineEntry as TimelineEntryType } from '@/types/research'

export function TimelineEntry({ entry, live }: { entry: TimelineEntryType; live?: boolean }) {
  return (
    <div className="animate-row-in grid grid-cols-[20px_minmax(0,1fr)] gap-x-3.5">
      <div className="grid grid-rows-[18px_1fr] justify-items-center">
        <div
          className={cn(
            'h-[11px] w-[11px] self-center rounded-[4px] border-[1.5px]',
            live ? 'animate-live-pulse border-strong bg-transparent' : 'border-foreground bg-foreground',
          )}
        />
        <div className={cn('animate-rail-grow w-px origin-top bg-hairline', live && 'opacity-0')} />
      </div>
      <div className="min-w-0 py-3 pb-3.5">
        <div className="text-sm leading-snug font-medium">{entry.label}</div>
        {entry.detail && (
          <div className="mt-1 border-l border-hairline pl-2.5 text-[12.5px] text-muted-foreground">
            {entry.detail}
          </div>
        )}
      </div>
    </div>
  )
}

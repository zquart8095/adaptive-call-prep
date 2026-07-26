import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import type { Citation, ResearchReport } from '@/types/research'

const CITATION_MARKER = /(\[cite-\d+\])/g

function renderNarrative(narrative: string, citationMap: Record<string, Citation>) {
  return narrative.split(CITATION_MARKER).map((part, i) => {
    const match = part.match(/^\[(cite-\d+)\]$/)
    if (!match) return <span key={i}>{part}</span>

    const citation = citationMap[match[1]]
    if (!citation) return <span key={i}>{part}</span>

    const linkClasses =
      'inline whitespace-nowrap font-mono text-[0.72em] align-[0.15em] text-muted-foreground underline decoration-dotted underline-offset-[3px] transition-colors hover:text-foreground'

    return citation.url ? (
      <a key={i} href={citation.url} target="_blank" rel="noreferrer" title={citation.label} className={linkClasses}>
        [{match[1]}]
      </a>
    ) : (
      <span key={i} title={citation.label} className={linkClasses}>
        [{match[1]}]
      </span>
    )
  })
}

export function ReportView({ report }: { report: ResearchReport }) {
  const citationMap = Object.fromEntries(report.citations.map((c) => [c.citation_id, c]))
  const plan = report.call_action_plan

  return (
    <div className="animate-phase-in">
      {report.is_demo_fallback && (
        <div className="mb-5 rounded-md border border-yellow-500/50 bg-yellow-500/10 p-3 text-sm">
          Demo fallback data — this company wasn't in the bundled fixtures, so parts of this report use
          placeholder content.
        </div>
      )}

      <div className="mb-6.5 flex flex-wrap items-end justify-between gap-4.5 border-b border-hairline pb-5">
        <div className="min-w-0">
          <div className="mb-2 font-mono text-[10.5px] tracking-[0.12em] text-muted-foreground uppercase">
            Call prep report
          </div>
          <h1 className="text-[34px] leading-[1.08] font-semibold tracking-[-0.03em]">{report.company}</h1>
        </div>
        <div className="flex gap-6.5 font-mono text-[11.5px] text-muted-foreground">
          <div className="grid gap-0.5">
            <span className="opacity-75">Generated</span>
            <span className="text-foreground">{report.generated_at}</span>
          </div>
          <div className="grid gap-0.5">
            <span className="opacity-75">Sources</span>
            <span className="text-foreground">{report.citations.length}</span>
          </div>
          <div className="grid gap-0.5">
            <span className="opacity-75">Sections</span>
            <span className="text-foreground">{report.sections.length}</span>
          </div>
        </div>
      </div>

      <div className="grid items-start gap-6.5 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="grid min-w-0 gap-6.5">
          <Card className="p-6">
            <div className="mb-3 font-mono text-[10.5px] tracking-[0.12em] text-muted-foreground uppercase">
              Executive summary
            </div>
            <p className="text-[17px] leading-[1.55] tracking-[-0.012em]">
              {renderNarrative(report.executive_summary, citationMap)}
            </p>
          </Card>

          {report.sections.map((section, i) => (
            <section key={section.section_id} className="min-w-0">
              <div className="mb-2.5 flex items-baseline gap-3">
                <span className="font-mono text-[11.5px] text-muted-foreground">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <h3 className="text-[19px] leading-tight font-semibold tracking-[-0.018em]">{section.title}</h3>
              </div>
              <p className="mb-3 border-l border-hairline pl-6 text-[13px] text-muted-foreground">
                {section.why_it_matters_for_this_call}
              </p>
              <p className="pl-[25px] text-[15px] leading-[1.65]">{renderNarrative(section.narrative, citationMap)}</p>
            </section>
          ))}
        </div>

        <aside className="sticky top-22 grid min-w-0 gap-5.5">
          <Card className="gap-0 py-0">
            <div className="flex items-center gap-2 border-b border-hairline bg-muted px-5 py-3.5">
              <span className="h-1.5 w-1.5 rounded-sm bg-foreground" />
              <span className="font-mono text-[10.5px] tracking-[0.12em] uppercase">Call action plan</span>
            </div>

            <div className="border-b border-hairline p-5">
              <div className="mb-2 text-[12.5px] font-medium text-muted-foreground">Suggested opener</div>
              <p className="text-[14.5px] leading-[1.6]">{plan.suggested_opener}</p>
            </div>

            <div className="border-b border-hairline p-5">
              <div className="mb-2.5 text-[12.5px] font-medium text-muted-foreground">Discovery questions</div>
              <div className="grid gap-2.5">
                {plan.discovery_questions.map((q, i) => (
                  <div key={i} className="grid grid-cols-[20px_minmax(0,1fr)] gap-x-2.5">
                    <span className="pt-0.5 font-mono text-[11px] text-muted-foreground">
                      {String(i + 1).padStart(2, '0')}
                    </span>
                    <span className="text-sm leading-normal">{q}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-5">
              <div className="mb-2.5 text-[12.5px] font-medium text-muted-foreground">Anticipated objections</div>
              <div className="grid gap-3">
                {plan.anticipated_objections.map((o, i) => (
                  <div key={i} className="grid gap-1.5 rounded-[10px] bg-muted p-3">
                    <div className="text-[13.5px] font-medium">{o.objection}</div>
                    <div className="grid grid-cols-[14px_minmax(0,1fr)] gap-x-1.5 text-[13px] text-muted-foreground">
                      <span className="font-mono">→</span>
                      <span>{o.suggested_response}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          <Card className="gap-0 py-0">
            <div className="border-b border-hairline px-5 py-3.5 font-mono text-[10.5px] tracking-[0.12em] text-muted-foreground uppercase">
              Citations · {report.citations.length}
            </div>
            <div>
              {report.citations.map((citation) => (
                <a
                  key={citation.citation_id}
                  href={citation.url ?? undefined}
                  target={citation.url ? '_blank' : undefined}
                  rel="noreferrer"
                  className="grid grid-cols-[54px_minmax(0,1fr)] gap-x-3 border-b border-hairline px-5 py-3 text-inherit no-underline transition-colors last:border-b-0 hover:bg-muted"
                >
                  <span className="pt-0.5 font-mono text-[10.5px] text-muted-foreground">{citation.citation_id}</span>
                  <span className="grid min-w-0 gap-0.5">
                    <span className="text-[13.5px] leading-snug">{citation.label}</span>
                    <span className="font-mono text-[10.5px] text-muted-foreground">{citation.source_kind}</span>
                  </span>
                </a>
              ))}
            </div>
          </Card>

          <Button variant="outline" onClick={() => window.location.reload()} className="justify-self-start">
            Start a new session
          </Button>
        </aside>
      </div>
    </div>
  )
}

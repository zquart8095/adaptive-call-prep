# Adaptive Call Prep

An AI agent that preps a salesperson for an upcoming call: propose a research plan
scoped to the deal, let a human approve or revise it, then research autonomously —
reflecting on its own findings and looping back for more when it finds a real gap —
before composing a call-ready action plan (suggested opener, ranked discovery
questions, anticipated objections with responses), fully cited.

![Adaptive Call Prep running end to end: setting the call context, reviewing the proposed research plan, watching the autonomous research stream, and reading the finished cited report](docs/demo.gif)

**This is a from-scratch portfolio demo.** The company, scenario, and data are entirely
fictional ("Alderleaf Robotics," a made-up industrial robotics company). It exists to
demonstrate a set of engineering patterns I use in production agent work — LangGraph
`interrupt()`-based human-in-the-loop, a bounded reflect-and-refine research loop, and a
real streaming React frontend — without exposing any actual client code or data.

## Key Features

| Feature | Description |
|---|---|
| **Human-gated planning** | The agent proposes research goals scoped to the deal, then stops. Nothing runs until a person approves or sends feedback — LangGraph `interrupt()` / `Command(resume=...)`, with revisions looping back into plan generation. |
| **Bounded reflect-and-refine research** | Every section is critiqued against a sales-specific bar. A real gap triggers a targeted follow-up `web_search`; the loop is capped by `max_iterations_per_section` so it can't spin. |
| **Cited, call-ready output** | Not a research report — a suggested opener, ranked discovery questions, and anticipated objections with responses. The citation registry is assembled in Python before the model is called, so it can't invent a source. |
| **Real streaming frontend** | React + Vite + Tailwind + shadcn/ui driven by `@langchain/langgraph-sdk`'s `useStream` — a live Activity Timeline and the plan-approval interrupt surfaced as real UI, not a mock. |

## Setup and Installation

### Prerequisites

- Python 3.10+
- An Anthropic API key — get one at [console.anthropic.com](https://console.anthropic.com/settings/keys).
  There's no free/offline fallback for this repo; every path below needs it.
- Node.js 20+ / npm — **only** if you want the frontend, not the CLI

### 1. Clone and install

```bash
git clone https://github.com/zquart8095/adaptive-call-prep.git
cd adaptive-call-prep
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. Add your API key

Create a `.env` file in the repo root:
```bash
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env
```
This one `.env` powers both paths below — the CLI loads it directly, and
`langgraph.json` points `langgraph dev` at the same file, so the frontend picks it up
too. Nothing else needs configuring.

### 3. Run it — CLI (fastest, no Node needed)

```bash
.venv/bin/python -m sales_prep.cli research
```
Prints the proposed plan, prompts `[a]pprove` or type feedback to revise, then streams
progress to stdout through the autonomous phase and prints the full report + action
plan + citations at the end.

Try an unlisted company to see the graceful fixture-fallback path (no crash, clearly
labeled placeholder content):
```bash
.venv/bin/python -m sales_prep.cli research --context data/call_contexts/unlisted_prospect.json
```

### 3 (alternative) — Run it with the real frontend

```bash
# terminal 1 — serves the graph with real streaming, via LangGraph's own dev server
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/langgraph dev --port 2024

# terminal 2
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` — there's a "Load Alderleaf demo" button to prefill a
sample call context. `langgraph.json` (repo root) points at
`sales_prep/research_agent/graph.py:graph` — the frontend talks to it via
`@langchain/langgraph-sdk`'s `useStream` hook, which drives the live Activity Timeline
and surfaces the plan-approval interrupt.

`langgraph-cli[inmem]` is kept in a separate `requirements-dev.txt`, not folded into
`requirements.txt` — it pulls in a real server stack (uvicorn, etc.) that only matters
for the frontend-serving path.

### 4. Confirm everything's wired up

```bash
.venv/bin/python -m pytest tests/
```
All tests run offline against fake LLM clients — no API key spent, no network calls.
See **Testing** below for what each file covers.

## Agent Details

| Attribute | Detail |
|---|---|
| **Interaction type** | Human-in-the-loop gate, then fully autonomous |
| **Complexity** | Intermediate |
| **Agent type** | Single LangGraph `StateGraph`, eight nodes, three conditional edges |
| **Components** | `interrupt()` approval gate, bounded critique loop, Anthropic hosted `web_search`, `Protocol`-shaped fixture providers, streaming React frontend |
| **Model** | `claude-sonnet-5` for every LLM call (plan, critique, compose) |
| **Vertical** | Sales / GTM |

## How the Agent Thinks: A Two-Phase Workflow

![Adaptive Call Prep architecture: a human-gated planning loop feeding an autonomous, bounded reflect-and-refine research loop that ends in a composed call action plan](docs/architecture.png)

Every node name and routing condition in that diagram comes straight from
`sales_prep/research_agent/graph.py`.

### Phase 1: Plan & Refine (Human-in-the-Loop)

`ingest_research_context` seeds the run, then `generate_research_plan` asks
`claude-sonnet-5` for a set of goals scoped to this specific deal. `plan_approval_gate`
calls `interrupt()` and the graph stops there.

Approving routes to `build_outline`. Sending feedback routes back to
`generate_research_plan` with the prior plan *and* the feedback in the prompt, and
increments `plan_revision`. This loop is deliberately **unbounded** — a person controls
the pace, so there's nothing to cap.

### Phase 2: Execute Autonomous Research

`build_outline` converts the approved plan into an ordered section list — no LLM call
needed, since plan generation already assigned `skill_hints` per goal. Then, per section:

1. **`gather_section`** — on iteration 0, pulls from the fixture providers named by that
   goal's `skill_hints`.
2. **`critique_section`** — asks `claude-sonnet-5` a sales-specific question, not a
   generic-completeness one: *would this rep feel ready to run this meeting at this deal
   stage with what's been found?*
3. **Route.** A gap under the cap loops back to `gather_section`, which this time runs
   Anthropic's hosted `web_search` aimed at the exact `focus_for_next_search` the
   critique named. Sufficient, or `max_iterations_per_section` reached, falls through to
   `advance_section`.
4. **`advance_section`** — next section, or `compose_report` when they're all done.

Unlike Phase 1, this loop **is** bounded — it's machine-driven, so it gets a cap.

## Why this shape

Inspired by Google's ["Deep Search" ADK sample](https://github.com/google/adk-samples/tree/main/python/agents/deep-search)
and its predecessor, the LangGraph-native
[Gemini Fullstack Quickstart](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart)
— both share a two-phase shape (propose a plan → human approves/revises it →
autonomous research with a reflect-and-refine loop → cited report), and the latter maps
directly onto a LangGraph backend.

**This isn't a reskin of that pattern with sales fixture data plugged into generic
slots.** The plan, the critique, and the final output are all reasoned about through a
sales lens, not a generic-research one:

- **Plan generation reasons about `deal_stage`.** A `cold_outbound` call gets a
  different plan than a `negotiation`-stage one — goals are framed as real sales-prep
  needs (mapping the buying committee, assessing fit/pain, gauging competitive
  displacement risk, finding a warm opener), and each goal carries an explicit
  `why_it_matters_for_this_call` field, not just a research topic.
- **The critique step's "is this enough" question is sales-specific**, not generic
  completeness: *"would {salesperson} feel ready to run this {meeting_type} at the
  {deal_stage} stage with what's been found?"* — gaps read as sales blind spots ("no
  signal on who holds budget authority"), not research thinness.
- **The output is a call-ready action plan, not a research report**: a suggested
  opener, ranked discovery questions, and anticipated objections with suggested
  responses — the concrete artifact a rep actually opens before the call, built by an
  adaptive process that went and closed real gaps first, not a fixed synthesis pass
  over static data.

### Orchestration engine: LangGraph vs. Google ADK

Built on **LangGraph** (`StateGraph`, `interrupt()`), but I've also built the equivalent
topology on **Google's Agent Development Kit** (its graph-based `Workflow` API —
`nodes`/`edges`/`JoinNode`/`RequestInput`) in production client work. The two are a real
trade-off, not just a coin flip:

| | LangGraph | Google ADK (Workflow API) |
|---|---|---|
| Setup to run locally | `pip install langgraph` | GCP project, `agents-cli` scaffolding |
| HITL primitive | `interrupt()` / `Command(resume=...)` | `RequestInput` / `ctx.resume_inputs` |
| Ecosystem recognition | Broad, framework-agnostic | Newer, Google-specific |
| Natural deploy target | Anywhere (Docker, Lambda, etc.) | Vertex AI Agent Runtime, Cloud Run, GKE |

LangGraph was the right choice here specifically because `langgraph dev`'s local
in-memory server is exactly what a real streaming frontend needs, with no cloud project
required. ADK's Workflow API is the better choice when a Google-Cloud-native deploy
target is already part of the plan.

## Design decisions

`sales_prep/research_agent/` reuses fixture providers (`sales_prep/providers/` — four
`Protocol`-shaped adapters over bundled JSON, with a clearly-labeled `is_demo_fallback`
path for unlisted companies) for the initial pass over each research goal, plus
Anthropic's hosted `web_search` tool for the reflect-loop's follow-up research — the
one place this flow reaches beyond the fixtures, so "reflect and refine" is genuinely
doing something rather than re-querying static data with cosmetic param tweaks.

- **Sequential per-section, not LangGraph `Send`-based fan-out.** A `Send` fan-out
  would need an `Annotated` reducer for concurrent writes to `sections`, and would
  interleave the Activity Timeline nondeterministically — actively working against the
  frontend's core visual (a readable, ordered stream of what the agent is doing). The
  state (`sections` keyed by `goal_id`) is shaped so this could migrate to `Send` later
  without a redesign.
- **Purpose-built `ResearchReport`/`Citation`/`CallActionPlan` models.** `compose_report`
  builds the citation registry in Python *before* calling the LLM (fixture-derived
  citations get `url=None`, real web citations get a real URL) — the model only ever
  sees the registry, so it can't invent a URL or a fact not present in the findings.
  This one call runs at `max_tokens=8192` rather than `call_for_json`'s 1536 default: a
  five-goal plan has to fit every section's narrative *and* a complete action plan into
  a single response, and the prompt asks for 2-4 sentence sections so the brief stays
  scannable at that length instead of merely fitting.
- **Citation markers resolve everywhere the model can emit them.** Nothing in the prompt
  restricts citing to per-section narrative, and the composer reasonably cites in the
  executive summary too — so `ReportView` routes both through the same `[cite-N]`
  resolution pass (`renderNarrative`). A marker that leaks through as literal
  `[cite-1]` text is worse than no citation at all: it reads as a bug in exactly the
  place the report is asking to be trusted.
- **Testability via constructor injection.** Every LLM-calling node is a factory
  (`make_generate_research_plan(client=None)`), and `build_graph(anthropic_client=None)`
  threads one injected client through all of them — tests drive the **whole compiled
  graph** via `.invoke()`/`Command(resume=...)` with a fake Anthropic client
  (`tests/fakes.py`), no monkeypatching.
- **Raw `anthropic` SDK, no LangChain model wrapper.** Every LLM call goes through
  `client.messages.create(...)` directly (see `llm_json.py::call_for_json`) — kept
  consistent across every LLM-calling node in this repo rather than mixing in
  `langchain-anthropic` for some paths.

### Optional LangSmith tracing

Set `LANGSMITH_API_KEY` **and** `LANGSMITH_TRACING=true` in `.env` (both required — the
key alone doesn't turn tracing on, a real LangSmith gotcha) and every node in the graph
shows up as its own span automatically (native LangGraph behavior), plus
`sales_prep/observability/tracing.py::wrap_anthropic_if_enabled` wraps the Anthropic
client so LLM calls show up as nested spans with full prompt/response — a no-op
passthrough when tracing is off, verified in `tests/test_observability.py` against the
real gating logic (key-without-flag stays off, `wrap_anthropic_if_enabled` is a true
no-op when disabled).

## Testing

```bash
.venv/bin/python -m pytest tests/
```

- `test_providers_fixtures.py` — known-domain and unknown-domain (fallback) paths for
  all four fixture providers
- `test_observability.py` — LangSmith tracing graceful degradation (off by default,
  key-without-flag stays off, `wrap_anthropic_if_enabled` is a true no-op when disabled)
- `test_research_agent_graph.py` — the **full graph** through `Command(resume=...)`, via
  a fake Anthropic client (`tests/fakes.py`): plan approved first try, the
  plan-revision loop (a second interrupt with an incremented `plan_revision`), the
  reflect-loop actually triggering a follow-up `gather_section` call, the loop
  correctly bounded by `max_iterations_per_section` even when critique never says
  "sufficient," and the malformed-JSON-then-valid retry path recovering
- `test_research_agent_nodes.py` — pure router functions and `build_outline` in
  isolation; asserts `gather_section`'s first pass never touches the injected LLM
  client (a client with zero scripted responses would raise if it were)
- `test_research_agent_compose.py` — citation-registry assembly: stable `cite-N` ids,
  fixture citations never get a fabricated URL

## Repo layout

```
adaptive-call-prep/
├── README.md
├── langgraph.json                 # serves research_agent via `langgraph dev`
├── requirements-dev.txt           # requirements.txt + langgraph-cli[inmem]
├── docs/                          # demo gif, architecture diagram + its generator
├── data/call_contexts/            # fictional call-context inputs
├── sales_prep/
│   ├── config.py                  # CallContext
│   ├── cli.py                     # `research` subcommand
│   ├── providers/                 # 4 Protocols + fixture implementations
│   ├── observability/             # optional LangSmith tracing (tracing.py)
│   └── research_agent/            # plan/gate/outline/gather/critique/compose + graph.py
├── frontend/                      # React + Vite + Tailwind + Shadcn UI
└── tests/
```

## Technologies Used

### Backend

- **Python 3.10+**
- **LangGraph** — `StateGraph`, `interrupt()` / `Command(resume=...)`, `MemorySaver`
- **Anthropic Python SDK** — raw `client.messages.create(...)`, no LangChain model wrapper
- **Anthropic hosted `web_search` tool** — the reflect-loop's follow-up research
- **Pydantic** — `ResearchReport` / `Citation` / `CallActionPlan`
- **pytest** — full-graph tests against a fake client, fully offline
- **LangSmith** *(optional)* — per-node and per-LLM-call tracing

### Frontend

- **React + TypeScript + Vite**
- **Tailwind CSS + shadcn/ui**
- **`@langchain/langgraph-sdk`** — the `useStream` hook driving the Activity Timeline
  and the plan-approval interrupt

## What this intentionally omits

- **No real vendor integrations** — fixture data only, by design (see Design decisions
  above). Swapping in a real company-data API, news API, or people-search API is
  exactly the seam `providers/` exists for.
- **No dual orchestration-engine implementation.** I've built the ADK equivalent in
  production client work (see the trade-off table above), but building both here would
  be scope creep for a single portfolio repo.
- **No persistence across process restarts** — `MemorySaver` checkpointer only for the
  CLI; the frontend's `langgraph dev` server is dev-only, in-memory state. A real
  deployment would use a durable checkpointer (Postgres, SQLite) so a paused
  plan-review survives a restart.
- **No `Send`-based parallel fan-out** for research sections (see Design decisions
  above) — sequential, bounded, and deliberately keeps the Activity Timeline readable.
- **Fictional prospect names make the live `web_search` pass noisy.** "Jordan Ellery" and
  "Sam Okafor" are invented, so follow-up searches surface real, unrelated people who
  happen to share those names. The composer handles this the right way unprompted — it
  caveats that public search couldn't corroborate org-chart or authority specifics and
  marks them unverified rather than presenting the hits as fact — but the noise is
  inherent to demo data and disappears entirely against a real prospect.

## License

MIT

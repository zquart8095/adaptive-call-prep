from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

# Absolute imports, not relative — required because `langgraph dev` loads
# this file via direct module exec (langgraph_api's _graph_from_spec), not
# through the normal sales_prep package hierarchy, so relative imports
# fail with "attempted relative import with no known parent package".
# Verified directly: this is exactly the error a naive `from .state import
# ...` produces under `langgraph dev`.
from sales_prep.research_agent.nodes.advance import advance_section, route_after_advance
from sales_prep.research_agent.nodes.compose import make_compose_report
from sales_prep.research_agent.nodes.critique import make_critique_section, route_after_critique
from sales_prep.research_agent.nodes.gather import make_gather_section
from sales_prep.research_agent.nodes.ingest import ingest_research_context
from sales_prep.research_agent.nodes.outline import build_outline
from sales_prep.research_agent.nodes.plan import make_generate_research_plan
from sales_prep.research_agent.nodes.plan_gate import plan_approval_gate, route_after_plan_approval
from sales_prep.research_agent.state import ResearchState


def build_graph(anthropic_client=None, *, use_memory_checkpointer: bool = True):
    """anthropic_client injectable for testing (see tests/fakes.py) — real
    client construction stays lazy inside each node, so building/importing
    this graph never requires ANTHROPIC_API_KEY on its own; only actually
    running it does.

    use_memory_checkpointer=False for the module-level `graph` object below
    (what langgraph.json/`langgraph dev` loads) — the platform manages
    persistence itself and refuses to start if a custom checkpointer is
    passed to .compile(), confirmed directly: `langgraph dev` raised
    GraphLoadError over exactly this. CLI/tests call build_graph() with the
    default True, since standalone .invoke()/Command(resume=...) needs its
    own checkpointer for the interrupt/resume dance to work at all."""
    graph = StateGraph(ResearchState)

    graph.add_node("ingest_research_context", ingest_research_context)
    graph.add_node("generate_research_plan", make_generate_research_plan(anthropic_client))
    graph.add_node("plan_approval_gate", plan_approval_gate)
    graph.add_node("build_outline", build_outline)
    graph.add_node("gather_section", make_gather_section(anthropic_client))
    graph.add_node("critique_section", make_critique_section(anthropic_client))
    graph.add_node("advance_section", advance_section)
    graph.add_node("compose_report", make_compose_report(anthropic_client))

    graph.add_edge(START, "ingest_research_context")
    graph.add_edge("ingest_research_context", "generate_research_plan")
    graph.add_edge("generate_research_plan", "plan_approval_gate")
    graph.add_conditional_edges(
        "plan_approval_gate",
        route_after_plan_approval,
        {"build_outline": "build_outline", "generate_research_plan": "generate_research_plan"},
    )
    graph.add_edge("build_outline", "gather_section")
    graph.add_edge("gather_section", "critique_section")
    graph.add_conditional_edges(
        "critique_section",
        route_after_critique,
        {"gather_section": "gather_section", "advance_section": "advance_section"},
    )
    graph.add_conditional_edges(
        "advance_section",
        route_after_advance,
        {"gather_section": "gather_section", "compose_report": "compose_report"},
    )
    graph.add_edge("compose_report", END)

    if use_memory_checkpointer:
        return graph.compile(checkpointer=MemorySaver())
    return graph.compile()


graph = build_graph(use_memory_checkpointer=False)

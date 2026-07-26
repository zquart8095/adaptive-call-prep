import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langgraph.types import Command

load_dotenv()

from sales_prep.config import CallContext  # noqa: E402

_CONTEXT_DIR = Path(__file__).resolve().parent.parent / "data" / "call_contexts"


def research(context_path: str, research_focus: str | None) -> None:
    """CLI equivalent of the frontend's plan-approve-then-autonomous-research
    flow — no Node/npm needed. The plan-approval loop can repeat multiple
    times (a person controls the pace) before the autonomous
    research-and-critique phase runs."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ANTHROPIC_API_KEY is required for `sales-prep research` — plan generation, "
            "critique, and report composition all need a real model call, and there's "
            "no deterministic template fallback for this flow. Set it in .env, then "
            "try again."
        )
        return

    from sales_prep.research_agent.graph import build_graph as build_research_graph

    context = CallContext(**json.loads(Path(context_path).read_text()))
    graph = build_research_graph()
    config = {"configurable": {"thread_id": f"research-{context.prospect_domain}"}}

    result = graph.invoke(
        {"context": context.model_dump(mode="json"), "research_focus": research_focus}, config
    )

    while "__interrupt__" in result:
        payload = result["__interrupt__"][0].value
        print(f"\nResearch plan (revision {payload['plan_revision']}) for {payload['company']}:")
        for i, goal in enumerate(payload["research_plan"], 1):
            print(f"  {i}. {goal['title']}")
            print(f"     why: {goal['why_it_matters_for_this_call']}")
            print(f"     skills: {', '.join(goal['skill_hints'])}")

        decision = ""
        while not decision:
            decision = input("\nType 'a' to approve, or feedback to revise the plan: ").strip()

        if decision.lower() == "a":
            resume_payload = {"decision": "approved"}
        else:
            resume_payload = {"decision": "revise", "feedback": decision}
        result = graph.invoke(Command(resume=resume_payload), config)

    report_data = result["final_report"]
    print(f"\n=== Call Prep Report: {report_data['company']} ===\n")
    print(report_data["executive_summary"])

    print("\n--- Sections ---")
    for section in report_data["sections"]:
        print(f"\n{section['title']}")
        print(section["narrative"])

    action_plan = report_data["call_action_plan"]
    print("\n--- Call Action Plan ---")
    print(f"Suggested opener: {action_plan['suggested_opener']}")
    print("Discovery questions:")
    for question in action_plan["discovery_questions"]:
        print(f"  - {question}")
    print("Anticipated objections:")
    for objection in action_plan["anticipated_objections"]:
        print(f"  - {objection['objection']}")
        print(f"    -> {objection['suggested_response']}")

    print(f"\n--- Citations ({len(report_data['citations'])}) ---")
    for citation in report_data["citations"]:
        url_note = f" ({citation['url']})" if citation["url"] else ""
        print(f"  [{citation['citation_id']}] {citation['label']}{url_note}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="sales-prep")
    sub = parser.add_subparsers(dest="command", required=True)

    research_parser = sub.add_parser(
        "research", help="Adaptive call prep: propose a plan, approve/revise it, then autonomous research"
    )
    research_parser.add_argument(
        "--context",
        default=str(_CONTEXT_DIR / "alderleaf_robotics.json"),
        help="Path to a call context JSON file",
    )
    research_parser.add_argument(
        "--focus", default=None, help="Optional freeform note to steer the initial research plan"
    )

    args = parser.parse_args()
    if args.command == "research":
        research(args.context, args.focus)


if __name__ == "__main__":
    main()

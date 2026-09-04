from __future__ import annotations
from ripple.golden import build_golden
from ripple.orchestration.agent import GoldenChangeInterpreter, RippleAgent
from ripple.orchestration.session import RippleSession
from ripple.evaluation.rubric import collect_evidence


def run_demo():
    _, _, planner, executor, _ = build_golden()
    agent = RippleAgent(GoldenChangeInterpreter(), planner)
    session = RippleSession(agent, executor)
    utterance = "Our flight home was cancelled. We'll land tomorrow at 18:00."
    context = {
        "old_arrival_at": "2026-09-10T21:00:00",
        "new_arrival_at": "2026-09-11T18:00:00",
    }
    proposal = session.propose(utterance, context)
    print("USER:", utterance)
    print("RIPPLE:", proposal.spoken_summary)
    print("PLAN:")
    for action in proposal.plan.actions:
        print(f"- {action.tool}.{action.operation} -> {action.target_id} | +${action.added_cost:.0f} | avoids ${action.avoidable_loss:.0f}")
    result = session.approve_and_execute(proposal, max_total_cost=42, external_people_notified=3)
    print("EXECUTION:", [r.status for r in result.receipts])
    evidence = collect_evidence(proposal.plan, result.receipts)
    print("JUDGE EVIDENCE:")
    for field, items in evidence.__dict__.items():
        print(field.upper())
        for item in items:
            print("  -", item)


if __name__ == "__main__":
    run_demo()

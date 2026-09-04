from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

from ripple.evaluation.matrix import run_matrix
from ripple.presentation import build_repair_card
from ripple.webapp import DemoController


def collect_release_evidence() -> Dict[str, Any]:
    matrix = run_matrix()
    controller = DemoController()
    proposal = controller.propose("Our flight home was cancelled. We'll land tomorrow at 18:00.")
    card = build_repair_card(controller.proposal.plan)
    executed = controller.approve(proposal["approval_disclosure"])
    replay = controller.replay()

    checks = {
        "scenario_matrix": all(row.passed for row in matrix),
        "golden_impacts": proposal["plan"]["impact_count"] == 5,
        "zero_writes_before_approval": proposal["writes_before_approval"] == 0,
        "financial_summary": (
            proposal["plan"]["total_added_cost"] == 42
            and proposal["plan"]["total_avoidable_loss"] == 116
            and proposal["plan"]["net_direct_cash_preserved"] == 74
        ),
        "repair_card_money_first": (
            card["display_hint"] == "inline"
            and [m["value"] for m in card["metrics"]] == ["$116", "$42", "$74"]
            and card["decision"]["label"] == "Approve $42 repair"
        ),
        "exact_approval_disclosure": (
            proposal["approval_disclosure"]["snapshot_hash"] == proposal["plan"]["snapshot_hash"]
            and proposal["approval_disclosure"]["external_people_notified"] == 3
        ),
        "bounded_execution": executed["plan_status"] == "executed" and executed["receipt_count"] == 5,
        "idempotent_replay": replay["deduplicated"] == 5 and replay["external_write_count"] == 5,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "scenario_matrix": [asdict(row) for row in matrix],
        "golden": {
            "impacts": proposal["plan"]["impact_count"],
            "actions": proposal["plan"]["action_count"],
            "added_cost": proposal["plan"]["total_added_cost"],
            "avoidable_loss": proposal["plan"]["total_avoidable_loss"],
            "net_preserved": proposal["plan"]["net_direct_cash_preserved"],
            "writes_before_approval": proposal["writes_before_approval"],
            "execution_receipts": executed["receipt_count"],
            "unique_external_writes": executed["external_write_count"],
            "replay_deduplicated": replay["deduplicated"],
        },
    }


def render_markdown(evidence: Dict[str, Any]) -> str:
    checks = evidence["checks"]
    golden = evidence["golden"]
    lines = [
        "# Ripple — Release Gate v1.4",
        "",
        f"**Overall: {'PASS' if evidence['passed'] else 'FAIL'}**",
        "",
        "## Deterministic release checks",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    lines += [f"| `{name}` | {'PASS' if passed else 'FAIL'} |" for name, passed in checks.items()]
    lines += [
        "",
        "## Golden proof",
        "",
        f"- downstream impacts: **{golden['impacts']}**",
        f"- bounded actions: **{golden['actions']}**",
        f"- writes before approval: **{golden['writes_before_approval']}**",
        f"- added recovery cost: **${golden['added_cost']:.0f}**",
        f"- direct loss avoided: **${golden['avoidable_loss']:.0f}**",
        f"- net direct cash preserved: **${golden['net_preserved']:.0f}**",
        f"- authoritative execution receipts: **{golden['execution_receipts']}**",
        f"- unique external writes: **{golden['unique_external_writes']}**",
        f"- exact-plan replay deduplicated: **{golden['replay_deduplicated']}/5**",
        "",
        "## Adversarial matrix",
        "",
    ]
    for row in evidence["scenario_matrix"]:
        lines.append(f"- **{'PASS' if row['passed'] else 'FAIL'}** `{row['scenario']}` — {row['invariant']}")
    lines += [
        "",
        "This deterministic gate does not claim a live Alexa+ client, live AWS runtime, or real external-service integrations. Ripple v1.4 adds a structured money-first Repair Card and executable restart-durability contract while keeping the publicly verified MCP Streamable HTTP transport separate from the deterministic repair engine. The DynamoDB adapter exists, but live AWS persistence is not claimed until provisioned and exercised.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    evidence = collect_release_evidence()
    root = Path(__file__).resolve().parents[3]
    out = root / "docs" / "VALIDATION_REPORT.md"
    out.write_text(render_markdown(evidence), encoding="utf-8")
    print(render_markdown(evidence))
    if not evidence["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

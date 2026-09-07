from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ModelRate:
    name: str
    input_per_million_usd: float
    output_per_million_usd: float


@dataclass(frozen=True)
class ModelCostRow:
    name: str
    input_tokens: int
    output_tokens: int
    cost_per_change_usd: float
    cost_10k_changes_usd: float
    cost_100k_changes_usd: float


@dataclass(frozen=True)
class InfraCostRow:
    name: str
    modeled_monthly_usd: float
    billing_floor_usd: float
    effective_monthly_floor_usd: float
    basis: str


# Pricing snapshot used only for a reproducible planning comparison. These
# values must be reviewed against provider pricing before a future submission
# refresh; they are not evidence of the account's actual AWS bill.
NOVA_LITE = ModelRate("Amazon Nova Lite", 0.06, 0.24)
NOVA_2_LITE = ModelRate("Amazon Nova 2 Lite", 0.30, 2.50)

RAILWAY_CPU_PER_VCPU_MONTH_USD = 20.0
RAILWAY_RAM_PER_GB_MONTH_USD = 10.0
RAILWAY_HOBBY_MINIMUM_USD = 5.0

# Observed idle envelope already captured in docs/COST_MODEL.md.
RIPPLE_IDLE_CPU_VCPU = 0.0015677
RIPPLE_IDLE_RAM_GB = 0.0226319


def model_cost(rate: ModelRate, *, input_tokens: int = 2000, output_tokens: int = 256) -> ModelCostRow:
    per_change = (
        input_tokens * rate.input_per_million_usd / 1_000_000
        + output_tokens * rate.output_per_million_usd / 1_000_000
    )
    return ModelCostRow(
        name=rate.name,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_per_change_usd=per_change,
        cost_10k_changes_usd=per_change * 10_000,
        cost_100k_changes_usd=per_change * 100_000,
    )


def railway_idle_cost() -> InfraCostRow:
    modeled = (
        RIPPLE_IDLE_CPU_VCPU * RAILWAY_CPU_PER_VCPU_MONTH_USD
        + RIPPLE_IDLE_RAM_GB * RAILWAY_RAM_PER_GB_MONTH_USD
    )
    return InfraCostRow(
        name="Railway ripple-v12 idle envelope",
        modeled_monthly_usd=modeled,
        billing_floor_usd=RAILWAY_HOBBY_MINIMUM_USD,
        effective_monthly_floor_usd=max(modeled, RAILWAY_HOBBY_MINIMUM_USD),
        basis="observed idle CPU/RAM × published usage rates; excludes traffic/egress",
    )


def model_rows() -> list[ModelCostRow]:
    return [model_cost(NOVA_LITE), model_cost(NOVA_2_LITE)]


def render_markdown(rows: Iterable[ModelCostRow], infra: InfraCostRow) -> str:
    rows = list(rows)
    lines = [
        "# Ripple — Cost Benchmark (planning envelope)",
        "",
        "This benchmark is deterministic arithmetic over an explicit pricing snapshot. It is **not** an AWS invoice and does not claim that current month-to-date AWS spend is zero.",
        "",
        "## One-change model envelope",
        "",
        "Assumption: one normalization call per change, 2,000 input tokens + 256 output tokens. The production guard remains max 256 output tokens.",
        "",
        "| Model | Input $/1M | Output $/1M | Cost/change | 10k changes | 100k changes |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    rate_by_name = {NOVA_LITE.name: NOVA_LITE, NOVA_2_LITE.name: NOVA_2_LITE}
    for row in rows:
        rate = rate_by_name[row.name]
        lines.append(
            f"| {row.name} | ${rate.input_per_million_usd:.2f} | ${rate.output_per_million_usd:.2f} | "
            f"${row.cost_per_change_usd:.6f} | ${row.cost_10k_changes_usd:.2f} | ${row.cost_100k_changes_usd:.2f} |"
        )
    cheaper = min(rows, key=lambda row: row.cost_per_change_usd)
    lines += [
        "",
        f"Pure token-cost winner at this envelope: **{cheaper.name}**. Model lock still follows the separate accuracy-first Bedrock benchmark; price cannot override lower normalization accuracy.",
        "",
        "## Historical pre-AWS-cutover Railway idle envelope",
        "",
        f"Historical pre-AWS-cutover Railway idle resources model to **${infra.modeled_monthly_usd:.3f}/month** before traffic. "
        f"With the Hobby minimum/included-usage floor, the effective billing floor is **${infra.effective_monthly_floor_usd:.2f}/month** unless the workspace is on a different plan.",
        "",
        "## Economic scale check",
        "",
        "| Fixture | Repair cost | Net direct cash preserved | Net preserved / repair $ |",
        "|---|---:|---:|---:|",
        f"| Golden travel cascade | $42 | $74 | {74/42:.2f}× |",
        f"| Event operations cascade | $620 | $5,180 | {5180/620:.2f}× |",
        "",
        "The customer-economics ratios compare repair spend with direct cash preserved; they are not ROI claims about Ripple subscription pricing.",
        "",
        "## Guardrail state",
        "",
        "- The verified separate account-wide Ripple cost guard is $5/month; alerts/guardrails are not a hard service cutoff.",
        "- The CloudFormation template has its own configurable monthly budget parameter and must not be confused with the separate $5 guard.",
        "- Actual AWS month-to-date spend remains a separate observed metric; this benchmark deliberately does not infer it from modeled usage.",
        "",
        "## Pricing snapshot sources",
        "",
        "- Railway pricing: https://docs.railway.com/pricing and https://railway.com/pricing",
        "- Amazon Bedrock pricing: https://aws.amazon.com/bedrock/pricing/",
        "- Snapshot review date: 2026-09-06",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    rows = model_rows()
    infra = railway_idle_cost()
    payload = {
        "models": [asdict(row) for row in rows],
        "infra": asdict(infra),
        "actual_aws_spend_claimed": False,
    }
    print(json.dumps(payload, indent=2))
    repo_root = Path(__file__).resolve().parents[3]
    output = repo_root / "docs" / "COST_BENCHMARK_2026-09-06.md"
    output.write_text(render_markdown(rows, infra), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()

# Ripple — Cost Benchmark (planning envelope)

This benchmark is deterministic arithmetic over an explicit pricing snapshot. It is **not** an AWS invoice and does not claim that current month-to-date AWS spend is zero.

## One-change model envelope

Assumption: one normalization call per change, 2,000 input tokens + 256 output tokens. The production guard remains max 256 output tokens.

| Model | Input $/1M | Output $/1M | Cost/change | 10k changes | 100k changes |
|---|---:|---:|---:|---:|---:|
| Amazon Nova Lite | $0.06 | $0.24 | $0.000181 | $1.81 | $18.14 |
| Amazon Nova 2 Lite | $0.30 | $2.50 | $0.001240 | $12.40 | $124.00 |

Pure token-cost winner at this envelope: **Amazon Nova Lite**. Model lock still follows the separate accuracy-first Bedrock benchmark; price cannot override lower normalization accuracy.

## Historical pre-AWS-cutover Railway idle envelope

Historical pre-AWS-cutover Railway idle resources model to **$0.258/month** before traffic. With the Hobby minimum/included-usage floor, the effective billing floor is **$5.00/month** unless the workspace is on a different plan.

## Economic scale check

| Fixture | Repair cost | Net direct cash preserved | Net preserved / repair $ |
|---|---:|---:|---:|
| Golden travel cascade | $42 | $74 | 1.76× |
| Event operations cascade | $620 | $5,180 | 8.35× |

The customer-economics ratios compare repair spend with direct cash preserved; they are not ROI claims about Ripple subscription pricing.

## Guardrail state

- The verified separate account-wide Ripple cost guard is $5/month; alerts/guardrails are not a hard service cutoff.
- The CloudFormation template has its own configurable monthly budget parameter and must not be confused with the separate $5 guard.
- Actual AWS month-to-date spend remains a separate observed metric; this benchmark deliberately does not infer it from modeled usage.

## Pricing snapshot sources

- Railway pricing: https://docs.railway.com/pricing and https://railway.com/pricing
- Amazon Bedrock pricing: https://aws.amazon.com/bedrock/pricing/
- Snapshot review date: 2026-09-06

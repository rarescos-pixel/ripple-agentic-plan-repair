# Public production proof — 2026-09-05

An independent GitHub-hosted runner probed the deployed public Ripple service at:

`https://ripple-v12-production.up.railway.app`

GitHub Actions run:

`https://github.com/rarescos-pixel/ripple-agentic-plan-repair/actions/runs/33977293038`

## Observed result

```text
Ripple public runtime proof: PASS
base: https://ripple-v12-production.up.railway.app
source revision: unavailable
runtime mode: non-aws
structural AWS runtime: False
AWS components: []
Alexa Local Inspector JSON-only Accept reaches authentication: PASS
```

The probe also asserted that `/healthz` reports MCP protocol `2025-11-25` and that `/readyz` reports `status=ready`.

## Alexa Local Inspector compatibility evidence

The probe sent the documented Inspector-style unauthenticated MCP initialize request with:

- `Accept: application/json` only;
- client protocol example `2025-06-18`;
- no bearer credential.

The production service returned **401 Unauthorized**, which proves the JSON-only request passed transport/content negotiation and reached the authentication boundary. Before the compatibility fix, this request shape would have been rejected earlier with HTTP 406.

The full authenticated Local Inspector probe remains a separate evidence item because it requires the production service credential. This public proof does not pretend that an unauthenticated 401 proves authenticated tool/resource discovery.

## AWS claim boundary

The observed production readiness payload is explicitly:

- `runtime mode: non-aws`
- `structural AWS runtime: False`
- `AWS components: []`

Therefore this evidence **does not claim AWS LIVE**. It confirms the canonical service is still on the pre-cutover runtime, consistent with Ripple's AWS-ready/not-AWS-live disclosure.

## Source-attestation boundary

`source revision` was unavailable from the public readiness response for this deployment. The probe therefore does **not** claim that the public endpoint independently attests its Git SHA. Release/deployment identity must remain a control-plane evidence item until Railway supplies a runtime Git SHA for that deployment or Ripple exposes another trustworthy deployment identity signal.

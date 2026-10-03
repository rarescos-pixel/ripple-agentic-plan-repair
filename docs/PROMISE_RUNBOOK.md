# Reproduce continuous promise preservation

## First build gate

From a clean checkout of this branch, with Python 3.11 or newer:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e . pytest cfn-lint
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python scripts/promise_build_gate.py
```

The last command starts a separate loopback HTTP provider process, performs
conditional writes into its SQLite database, verifies via separate GET requests,
reconstructs the engine/worker and replays five times. It terminates the provider
and writes `docs/PROMISE_BUILD_EVIDENCE.json`. No AWS account, physical device,
message to another person, or remote service write is involved.

The contract and clock are explicit fixtures. The proof does not claim live
natural-language interpretation. Bedrock's constrained draft adapter has separate
contract tests and still needs its live gate.

## Interactive human review

```bash
PYTHONPATH=src python scripts/promise_local_demo.py
```

Open the review and scenario-control URLs printed by the process. Use the
ephemeral private review code in each tab. The code is never sent to a model.
All changes affect the digital twin; the clock is explicitly simulated.

1. Read the meaning, four promises, authority and expiry. Confirm meaning.
2. Use **Check again**, then approve the exact partial transition.
3. In scenario controls, choose **Mom goes out**. Return to review and approve
   the proposed empty-room repair. Let the worker perform the due change.
4. Choose **Departure moves later**. The worker predicts that the old scheduled
   plan would violate the timing promise. Review and approve the new plan.
5. Reach the old departure time: the common area remains home and security stays.
6. Reach the new departure time: effects still wait for actual departure evidence.
7. Choose **Family departure observed**, review the fresh binding, and approve.
8. After the verified transition, choose **Completion verified**. The contract
   reaches SATISFIED. Read-back and receipts remain available.

The engine does not infer that Mom's absence revokes her access. A schedule is
also not evidence that the family actually departed. These are independent facts.

## Enable the new MCP surface in an isolated runtime

Default: `RIPPLE_PROMISES_ENABLED=false`. The original five tools and deployed
baseline remain unchanged. Enabling selects the five promise tools and hides the
legacy workflow/card on that instance. The promise mode exposes no approval tool;
the default mode retains the original five tools and Repair Card.

Required settings:

| Setting | Meaning |
| --- | --- |
| `RIPPLE_PROMISES_ENABLED=true` | Explicitly enable this slice |
| `RIPPLE_PROMISE_OWNER` | Exact authenticated owner subject; current baseline auth uses `demo-user` |
| `RIPPLE_PROMISE_CATALOG_PATH` | Deployment-owned JSON catalogue, not model-generated tools |
| `RIPPLE_PROMISE_PROVIDER_URL` | Fixed HTTPS conditional-provider origin; HTTP only on loopback |
| `RIPPLE_PROMISE_PROVIDER_TOKEN` | Independent provider credential, at least 32 characters |
| `RIPPLE_PROMISE_HUMAN_TOKEN` | Different human-only credential, at least 32 characters |
| `RIPPLE_PROMISE_TIME_ZONE` | Explicit timezone for language normalization, default UTC |
| `RIPPLE_PROMISE_POLL_SECONDS` | 1–60 seconds, default 5 |
| `RIPPLE_STATE_BACKEND` | `sqlite` or `dynamodb`; memory is deliberately rejected |
| `RIPPLE_SQLITE_PATH` / `RIPPLE_DYNAMODB_TABLE` | Existing persistence substrate |
| `AWS_REGION`, `RIPPLE_BEDROCK_MODEL_ID` | Existing Bedrock Converse configuration |

Existing AWS profile, tracing and OAuth settings still apply. Promise keys use
the same table and existing GetItem/PutItem permissions. No infrastructure rewrite
or IAM expansion is needed. This is a bounded single-owner prototype; it does not
claim production multi-user human authentication.

MCP tools:

- `draft_promise_intent`: natural language → DRAFT; no authority.
- `clarify_promise_intent`: human clarification → new DRAFT version; cannot alter ACTIVE meaning.
- `get_promise`: durable state across conversational sessions.
- `reconcile_promise`: fresh observation and counterfactual proposal.
- `execute_promise`: only existing exact or confirmed reversible authority.

Human review: `/promises/review/{contract_id}`. The separate human API supports
review, confirm, approve, revise and revoke. MCP OAuth tokens cannot use it.
Meaning confirmation never grants consequential action approval. A new world
version invalidates approval even when the visible action list stays unchanged.

The watchlist is durable and limited to 32 active/draft contracts. Terminal
entries are retired from the watchlist; their ledger remains durable. The engine
limits predicates, expressions, search candidates, event history and aggregate
size. Capacity exhaustion blocks effects rather than dropping receipts.

## Provider contract and limits

A provider must atomically enforce expected world revision, a content-bound
idempotency key, expiry, invariant guards and deployment execution conditions.
It must supply an independent read and a durable operation receipt. Generic
HTTP success is insufficient. No physical adapter may be described as safe until
these properties have been independently verified for that adapter.

One provider represents one atomic consistency domain. There is no claim of
atomic transactions across different commercial providers or physical devices.
Projection is conditional on future execution prerequisites. An unobserved future
occupancy change is never treated as actual permission at execution time.

An UNSATISFIABLE result means no solution in the declared finite action space.
It is not a theorem about every possible action in the world. Missing data or an
exceeded search bound instead produces REQUEST_CLARIFICATION.

# Ripple durability contract

Ripple treats approval and idempotency as safety state, not conversational memory.

## Contract

Before an external write can occur:

1. the exact `Approval` is validated against plan id, version, cost/scope and snapshot hash;
2. that approval is persisted through the configured `StateStore`;
3. before every provider call, Ripple looks up the action idempotency key;
4. an authoritative prior `executed` receipt returns a synthetic `deduplicated` receipt without calling the provider again;
5. new receipts are persisted immediately after the provider returns.

## Backends

- `memory` — default compatibility mode for unit tests and ephemeral demos.
- `sqlite` — local durable backend used by executable restart tests.
- `dynamodb` — AWS deployment target; one table stores exact approvals and authoritative receipts.

Environment configuration:

```text
RIPPLE_STATE_BACKEND=memory|sqlite|dynamodb
RIPPLE_SQLITE_PATH=/path/to/ripple-state.sqlite3
RIPPLE_DYNAMODB_TABLE=ripple-state
AWS_REGION=eu-west-1
```

`boto3` is imported only when the DynamoDB backend is selected. Live AWS deployment therefore remains an explicit external gate rather than an implicit local dependency.

## Executable restart proof

`tests/test_persistence.py::test_sqlite_restart_resumes_without_duplicate_external_writes` interrupts the golden five-action plan after two writes, destroys the executor/tool objects, reopens the same durable store, restores the approval, and resumes with a new executor and provider registry.

Expected invariant:

```text
2 writes before restart
2 actions deduplicated after restart
3 new writes after restart
5 unique external writes total
```

This is the local proof for the same contract the DynamoDB backend is designed to enforce in AWS.

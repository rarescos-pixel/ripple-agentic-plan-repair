# Live Intent Contract normalization defect

## Root cause, established before editing

The preserved real response in `PROMISE_AWS_LIVE_EVIDENCE.json` (AWS run
36407918402, implementation `8b939542d5055f5c6c308cacdcd66667d71a0b68`)
contains `{"operator":[...]}`, a boolean comparison in `goal_at`, and
`{"approval_required":true,"control_name":"mode"}` as authority. It also
omits the requested temporal invariant. HTTP 200 and tool use proved inference,
not a valid Intent Contract.

The adapter supplied only `contract: {type: object}` to Bedrock. Its prose used
`operator` and `control_name` as placeholders without a nested schema explaining
their actual wire representation. The model emitted those placeholders literally.
`interpret()` then copied the tool input directly into `validate_contract()`;
there was no normalization stage converting it into another representation.
The deterministic validator correctly rejected `operator`. Changing that validator
to accept the response would also have admitted wrong temporal/authority semantics.

## Minimum fix

- Supply all canonical fields, required keys, bounds, predicate structure and
  context-specific fact/control names in the tool schema.
- Use actual operator-key JSON examples and distinguish integer `goal_at`, boolean
  goal/completion, mutable assumptions and continuing/temporal invariants.
- At the model boundary, reject ill-typed operands/predicates and incomplete tool
  responses. Never coerce or rewrite a model's malformed contract into acceptance.
- Retain confirmation, clarification and exact approval boundaries. The engine,
  deterministic evaluator/validator, persistence and execution code are unchanged.

The regression suite first reproduced 17 failures against the previous adapter.
After the fix, all 196 tests pass locally, including the existing adversarial
classes. The captured invalid live response still fails validation. The independent
HTTP-provider build gate also passes. These local checks are not a live Bedrock claim.

## Mandatory live closure

`scripts/promise_aws_live_proof.py` requires the exact checked-out implementation
SHA and fails the entire run on an invalid explicit-intent Bedrock response. It
checks two domains, using semantic truth tables rather than a preferred AST form.
Each raw model contract must equal the validated and persisted contract, with its
hash bound to the verified action receipt. It exercises changed assumptions,
counterfactual repair, stale/used approval rejection, duplicate/out-of-order events,
DynamoDB CAS, restart/replay and independent DynamoDB/CloudWatch hash read-back.
A separate actual inference must reject or request clarification for ambiguous intent.

Only the established main-branch live-proof workflow is updated to pin/run the new
implementation. Its OIDC role, session policy and AWS evidence resources remain
unchanged. Provider facts, clock and human approvals are explicitly test fixtures;
Bedrock, STS, DynamoDB and CloudWatch must be live. No production deployment or
physical Alexa/device claim is made. The live result is pending until read back.

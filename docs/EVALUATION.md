# Evaluation plan v1.0

## Hard gates before AWS integration
1. Golden contract passes deterministically.
2. Proposal phase performs zero writes.
3. Wrong-version/cost-drift approval performs zero writes.
4. Content drift after approval is detected by snapshot hash even without a version bump.
5. Replay produces zero duplicate writes.
6. Partial provider failure stays partial and names the unresolved action.
7. Provider ambiguity blocks the entire plan before the first write.
8. A missed repair deadline remains visible as unresolved; Ripple does not pretend it was saved.
9. Explicit hard user constraints are honored before cost optimization.
10. Interrupted execution can resume with zero duplicate external writes.
11. Natural-language facade can be replaced without touching execution policy.
12. Multi-step dependency paths remain preserved and unaffected commitments are not repaired.

## AWS gate
AWS/Bedrock is justified only after all local gates above are green. The cloud layer must not weaken any deterministic invariant.

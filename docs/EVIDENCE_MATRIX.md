# Ripple — Evidence Matrix v1.3

This report is generated from executable scenarios. It is evidence, not marketing copy.

| Scenario | Result | Invariant | Observed |
|---|---|---|---|
| `golden_flight_cascade` | PASS | one change repairs five bounded commitments | impacts=5; actions=5; added_cost=42; avoidable_loss=116; net_preserved=74; writes=5; snapshot_hash_prefix=b23a3a1d0690 |
| `missed_deadline` | PASS | expired repair windows remain visible; no fabricated save | impacts=1; actions=0; unresolved=['reservation:D1']; writes=0 |
| `ambiguous_provider` | PASS | ambiguous provider state blocks the whole plan before writes | blocked=True; writes=0 |
| `hard_preference` | PASS | explicit hard constraints filter options before cost optimization | selected_operation=reschedule_reservation; added_cost=25.0 |
| `event_operations_cascade` | PASS | generic changed-time graph chooses the repair bundle that preserves the most net cash | impacts=5; actions=5; added_cost=620.0; avoidable_loss=5800.0; net_preserved=5180.0; external_people=8; av_choice=move_av_delivery |
| `content_drift` | PASS | approval binds to exact content, not only a version integer | blocked=True; writes=0; hash_changed=True |
| `interruption_recovery` | PASS | resume after interruption produces zero duplicate external writes | persisted_receipts_before_resume=2; deduplicated_on_resume=2; new_writes_on_resume=3; unique_writes_total=5; final_status=executed |

**Summary: 7/7 scenarios PASS.**

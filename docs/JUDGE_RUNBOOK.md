# Judge Runbook — fastest path to the evidence

## 30 seconds: understand the idea
Read the README first.

**One changed fact → dependency graph → affected commitments → smallest safe repair plan → one exact approval → idempotent bounded execution.**

## 60 seconds: run the release proof
```bash
PYTHONPATH=src python -m ripple.evaluation.release_gate
```
Expected result: `Overall: PASS` and 6/6 adversarial scenarios PASS.


## 2 minutes: verify the real MCP server
Terminal A:
```bash
PYTHONPATH=src python -m ripple.mcp_server
```
Terminal B:
```bash
python scripts/mcp_smoke.py
```
Expected: `Ripple MCP smoke: PASS`, five tools discovered, preview with 5 impacts / 0 writes, approval with 0 writes, execution with 5 receipts, and replay with 5/5 deduplicated.

The MCP target is protocol `2025-11-25` over Streamable HTTP. See `docs/MCP_COMPLIANCE.md` and `docs/MCP_PROTOCOL_TEST_REPORT.md`.

## 2 minutes: use the simulated Alexa+ experience
```bash
PYTHONPATH=src python -m ripple.webapp
```
Open `http://127.0.0.1:8765` and keep the default utterance:

> Our flight home was cancelled. We'll land tomorrow at 18:00.

Verify visibly:
1. exactly 5 downstream impacts;
2. $42 recovery cost / $116 avoided loss / $74 net direct cash preserved;
3. 0 external writes before approval;
4. dependency paths from the changed flight to each affected commitment;
5. exact approval snapshot hash and side-effect disclosure;
6. 5 execution receipts after approval;
7. replay deduplicates 5/5 actions while unique writes remain 5.

## Adversarial evidence
The UI and `docs/EVIDENCE_MATRIX.md` show:
- missed deadline remains unresolved;
- ambiguous provider blocks before the first write;
- hard preference beats cheaper optimization;
- post-approval content drift requires re-approval;
- interrupted execution resumes with zero duplicate writes.

## Truthfulness
See `docs/TECHNOLOGY_DISCLOSURE.md` before evaluating integration claims.

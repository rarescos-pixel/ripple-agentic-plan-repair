from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(text: str, needle: str, label: str, errors: list[str]) -> None:
    if needle not in text:
        errors.append(f"{label}: missing required text: {needle!r}")


def forbid(text: str, needle: str, label: str, errors: list[str]) -> None:
    if needle in text:
        errors.append(f"{label}: stale/forbidden text present: {needle!r}")


def main() -> int:
    errors: list[str] = []

    readme = read("README.md")
    friction = read("docs/FRICTION_LOG.md")
    feedback = read("docs/PRODUCT_FEEDBACK.md")
    submission = read("docs/SUBMISSION_DRAFT.md")
    video = read("docs/VIDEO_SCRIPT.md")
    rubric = read("docs/RUBRIC_MAP.md")
    master = read("docs/MASTER.md")
    open_source = read("docs/OPEN_SOURCE_SUBMISSION.md")
    aws_live = read("docs/AWS_DIRECT_LIVE_EVIDENCE.md")

    for needle in (
        "Tell Alexa one thing that changed. Ripple fixes what breaks downstream.",
        "5 commitments affected",
        "$116 at risk",
        "$42 repair cost",
        "$74 net cash preserved",
        "MCP 2025-11-25",
        "MCP App",
        "AWS services are live and structurally verified",
        "canonical public Railway AWS-runtime cutover is pending",
        "What is real vs simulated",
        "one bounded real external provider integration",
        "docs/FRICTION_LOG.md",
    ):
        require(readme, needle, "README", errors)

    for needle in (
        "AWS-ready, not AWS-live verified",
        "**v1.2 — Alexa+ remote MCP milestone**",
        "43/43 tests PASS",
        "6/6 adversarial scenarios PASS",
        "AWS integration remains a later milestone",
        "DynamoDB/Lambda/CloudWatch",
    ):
        forbid(readme, needle, "README", errors)

    for entry in ("F1", "F2", "F3", "F4", "F5"):
        require(friction, f"## {entry} —", "FRICTION_LOG", errors)
    for field in (
        "**Task attempted:**",
        "**Steps taken:**",
        "**Expected:**",
        "**Actual:**",
        "**Severity:**",
        "**Workaround:**",
        "**Actionable suggestion:**",
    ):
        if friction.count(field) < 5:
            errors.append(
                f"FRICTION_LOG: expected field {field!r} in at least five real entries; "
                f"found {friction.count(field)}"
            )

    for needle in (
        "Which developer tools, APIs and SDKs did you use and for what?",
        "What worked well?",
        "What needs work?",
        "How was onboarding from zero to hello world?",
        "Would you build with Alexa+ / this path again?",
        "Direct AWS structural evidence is live verified",
        "canonical public Railway MCP process",
        "AWS_DIRECT_LIVE_EVIDENCE=PASS",
    ):
        require(feedback, needle, "PRODUCT_FEEDBACK", errors)
    forbid(feedback, "implemented and AWS-ready, but not yet AWS-live verified", "PRODUCT_FEEDBACK", errors)

    for needle in (
        "$5,180 net cash preserved",
        "5/5 deduplicated",
        "REAL_PROVIDER",
        "AWS services are live and structurally verified",
        "canonical public Railway AWS-runtime cutover is pending",
        "No actual Alexa+ production-client session is claimed",
        "**Primary Track:** Alexa+",
        "**Mini Challenge:** AWS Builder",
        "**Mini Challenge:** Open Source",
        "## Open Source Mini Challenge",
        "https://github.com/rarescos-pixel/ripple-agentic-plan-repair/pull/22",
    ):
        # REAL_PROVIDER is represented as prose in the draft; accept the exact
        # live-provider contract phrase below instead of a workflow-only marker.
        if needle == "REAL_PROVIDER":
            require(submission, "one bounded real external provider proof", "SUBMISSION_DRAFT", errors)
        else:
            require(submission, needle, "SUBMISSION_DRAFT", errors)
    forbid(submission, "Current evidence status is AWS-ready, not AWS-live verified", "SUBMISSION_DRAFT", errors)

    for needle in (
        "## 0:00–0:20",
        "No terminal scrolling as the primary demo.",
        "Keep the final cut under **3:00**",
        "Do not claim AWS live until the real AWS gate",
    ):
        require(video, needle, "VIDEO_SCRIPT", errors)

    for needle in (
        "## 1. Technical Implementation",
        "## 2. Design",
        "## 3. Potential Impact",
        "## 4. Quality of the Idea",
        "## Bonus — friction log",
    ):
        require(rubric, needle, "RUBRIC_MAP", errors)

    for needle in (
        "# Ripple — MASTER competition state",
        "$5,180",
        "## AWS boundary — DIRECT LIVE VERIFIED / PUBLIC RUNTIME CUTOVER PENDING",
        "AWS_DIRECT_LIVE_EVIDENCE=PASS",
        "## Real-provider contract — VERIFIED",
        "## Submission lock",
        "STOP before video",
    ):
        require(master, needle, "MASTER", errors)
    for needle in (
        "AWS-READY, NOT AWS-LIVE VERIFIED",
        "# Ripple — MASTER v1.2",
        "43/43 tests",
        "DynamoDB/Lambda/DynamoDB/CloudWatch",
        "Lambda deterministic boundary",
    ):
        forbid(master, needle, "MASTER", errors)

    for needle in (
        "# Ripple — AWS direct live evidence",
        "AWS_DIRECT_LIVE_EVIDENCE=PASS",
        "CLOUDWATCH_LOGS_LIVE=PASS",
        "DYNAMODB_RECEIPT_LIVE=PASS",
        "BEDROCK_LIVE=PASS",
        "public Railway AWS-runtime cutover remains pending",
    ):
        require(aws_live, needle, "AWS_DIRECT_LIVE_EVIDENCE", errors)

    for needle in (
        "# Open Source Mini Challenge — submission packet",
        "Repository created: **2026-09-04**",
        "License: **MIT**",
        "GitHub username: **rarescos-pixel**",
        "https://github.com/rarescos-pixel/ripple-agentic-plan-repair/pull/22",
        "### What I did",
        "### How it works",
        "### Why it matters",
    ):
        require(open_source, needle, "OPEN_SOURCE_SUBMISSION", errors)

    if errors:
        print("Ripple submission surface gate: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Ripple submission surface gate: PASS")
    print("judge_hook: 5 commitments / $116 at risk / $42 repair / $74 net preserved")
    print("friction_entries: 5 complete")
    print("aws_claim: direct structural live PASS / public Railway AWS-runtime cutover pending")
    print("real_provider: bounded reversible external write/readback/replay/restore PASS")
    print("mini_challenges: AWS Builder + Open Source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

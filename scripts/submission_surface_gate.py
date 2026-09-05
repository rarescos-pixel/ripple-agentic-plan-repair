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

    for needle in (
        "Tell Alexa one thing that changed. Ripple fixes what breaks downstream.",
        "5 commitments affected",
        "$116 at risk",
        "$42 repair cost",
        "$74 net cash preserved",
        "MCP 2025-11-25",
        "MCP App",
        "AWS-ready, not AWS-live verified",
        "What is real vs simulated",
        "docs/FRICTION_LOG.md",
    ):
        require(readme, needle, "README", errors)

    for needle in (
        "**v1.2 — Alexa+ remote MCP milestone**",
        "43/43 tests PASS",
        "6/6 adversarial scenarios PASS",
        "AWS integration remains a later milestone",
        "DynamoDB/Lambda/CloudWatch",
    ):
        forbid(readme, needle, "README", errors)

    for entry in ("F1", "F2", "F3", "F4"):
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
        if friction.count(field) < 4:
            errors.append(
                f"FRICTION_LOG: expected field {field!r} in at least four real entries; "
                f"found {friction.count(field)}"
            )

    for needle in (
        "Which developer tools, APIs and SDKs did you use and for what?",
        "What worked well?",
        "What needs work?",
        "How was onboarding from zero to hello world?",
        "Would you build with Alexa+ / this path again?",
        "AWS-ready, but not yet AWS-live verified",
    ):
        require(feedback, needle, "PRODUCT_FEEDBACK", errors)

    for needle in (
        "$5,180 net cash preserved",
        "5/5 deduplicated",
        "AWS-ready, not AWS-live verified",
        "No actual Alexa+ production-client session is claimed",
    ):
        require(submission, needle, "SUBMISSION_DRAFT", errors)

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
        "AWS-READY, NOT AWS-LIVE VERIFIED",
        "## Submission lock",
    ):
        require(master, needle, "MASTER", errors)
    for needle in (
        "# Ripple — MASTER v1.2",
        "43/43 tests",
        "DynamoDB/Lambda/DynamoDB/CloudWatch",
        "Lambda deterministic boundary",
    ):
        forbid(master, needle, "MASTER", errors)

    if errors:
        print("Ripple submission surface gate: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Ripple submission surface gate: PASS")
    print("judge_hook: 5 commitments / $116 at risk / $42 repair / $74 net preserved")
    print("friction_entries: 4 complete")
    print("aws_claim: AWS-ready / not AWS-live until live gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, got {count}")
    return text.replace(old, new, 1)


p = Path("src/ripple/promises/interpreter.py")
s = p.read_text()

s = replace_once(
    s,
    '"questions": {"type": "array", "maxItems": 16, "items": {"type": "string", "maxLength": 1000}},',
    '"questions": {"type": "array", "maxItems": 16, "items": {"type": "string", "maxLength": 1000},\n'
    '                      "description": "Optional advisory clarification text. It is retained only when confidence is below 0.85; it never grants or changes authority."},',
    "questions schema description",
)

s = replace_once(
    s,
    '    required = [key for key in properties if key not in {"expiry_when", "meaning"}]',
    '    required = [key for key in properties if key not in {"expiry_when", "meaning", "questions"}]',
    "questions optional schema",
)

s = replace_once(
    s,
    'If consequential meaning, expiry, lifetime completion or authority is genuinely unresolved, put the unresolved issue in questions. Never silently invent a preference.\n'
    'If the human explicitly supplied all current requirements, do not ask for a future value merely because a fact may change later; changing assumptions are handled by reconciliation.',
    'If consequential meaning, expiry, lifetime completion or authority is genuinely unresolved, set confidence below 0.85 and you may describe the unresolved issue in questions. Never silently invent a preference.\n'
    'Questions are advisory prose, not authority and not a semantic field. Ripple retains them only for low-confidence drafts; high-confidence drafts still require explicit human meaning confirmation before activation.\n'
    'If the human explicitly supplied all current requirements, do not ask for a future value merely because a fact may change later; changing assumptions are handled by reconciliation.',
    "questions guidance",
)

s = replace_once(
    s,
    '        "authority", "expiry_at", "evidence_source", "evidence_max_age_seconds",\n'
    '        "questions", "confidence",\n',
    '        "authority", "expiry_at", "evidence_source", "evidence_max_age_seconds",\n'
    '        "confidence",\n',
    "questions required set",
)

s = replace_once(
    s,
    '    allowed = required | {"expiry_when", "meaning"}',
    '    allowed = required | {"expiry_when", "meaning", "questions"}',
    "questions allowed set",
)

s = replace_once(
    s,
    '    questions = data["questions"]\n'
    '    if not isinstance(questions, list) or len(questions) > 16 or any(not isinstance(q, str) or len(q) > 1000 for q in questions):\n'
    '        raise ValueError("Invalid clarification questions")',
    '    questions = data.get("questions", [])\n'
    '    if not isinstance(questions, list) or len(questions) > 16 or any(not isinstance(q, str) or len(q) > 1000 for q in questions):\n'
    '        raise ValueError("Invalid clarification questions")',
    "questions default",
)

s = replace_once(
    s,
    '        "completion": _postfix(data["lifetime_completion"], context),\n'
    '        "questions": list(questions),\n',
    '        "completion": _postfix(data["lifetime_completion"], context),\n'
    '        "questions": list(questions) if confidence < .85 else [],\n',
    "confidence-gated questions",
)
p.write_text(s)

p = Path("tests/test_promise_interpreter.py")
s = p.read_text()

s = replace_once(
    s,
    '    assert "meaning" not in schema["required"]\n'
    '    assert "CONTRACT_SCHEMA=" not in model.request["system"][0]["text"]',
    '    assert "meaning" not in schema["required"]\n'
    '    assert "questions" not in schema["required"]\n'
    '    assert "CONTRACT_SCHEMA=" not in model.request["system"][0]["text"]',
    "questions optional schema assertion",
)

marker = '\n\ndef test_postfix_wire_round_trip_is_exact_representation_normalization(tmp_path):\n'
if s.count(marker) != 1:
    raise SystemExit(f"roundtrip marker count={s.count(marker)}")

tests = r'''


def test_high_confidence_advisory_question_cannot_override_structured_contract(tmp_path):
    engine, provider, clock, state = setup_engine(tmp_path)
    ctx = context(engine, provider, clock)
    data = contract_wire(state["contract"], confidence=.99)
    data["questions"] = ["May I act autonomously even though authority requires approval?"]
    spec, confidence = normalize_wire(data, ctx)
    assert confidence == .99
    assert spec["questions"] == []
    assert spec["authority"]["delivery_route"] == "APPROVAL_REQUIRED"
    assert spec["authority"]["budget_ok"] == "FORBIDDEN"


def test_missing_questions_is_valid_but_low_confidence_still_requires_clarification(tmp_path):
    engine, provider, clock, state = setup_engine(tmp_path)
    ctx = context(engine, provider, clock)
    data = contract_wire(state["contract"], confidence=.99)
    data.pop("questions", None)
    spec, confidence = normalize_wire(deepcopy(data), ctx)
    assert confidence == .99 and spec["questions"] == []

    class LowConfidenceNoQuestions(DraftModel):
        def converse(self, **kwargs):
            response = super().converse(**kwargs)
            wire = response["output"]["message"]["content"][0]["toolUse"]["input"]
            wire.pop("questions", None)
            wire["confidence"] = .2
            return response

    draft = BedrockIntentInterpreter(LowConfidenceNoQuestions(state["contract"]), "test").interpret(
        "Keep the specified promise", ctx
    )
    assert draft["questions"]
    assert "uncertain" in draft["questions"][-1].lower()


def test_malformed_advisory_questions_still_fail_closed(tmp_path):
    engine, provider, clock, state = setup_engine(tmp_path)
    data = contract_wire(state["contract"], confidence=.99)
    data["questions"] = [123]
    with pytest.raises(ValueError, match="clarification questions"):
        normalize_wire(data, context(engine, provider, clock))
'''
s = s.replace(marker, tests + marker, 1)
p.write_text(s)

from __future__ import annotations

import pytest

from ripple.mcp_server import McpRippleSession
from ripple.orchestration.executor import SimulatedInterruption


UTTERANCE = "Our flight home was cancelled. We'll land tomorrow at 18:00."
SUBJECT = "user:restart-proof"


def _new_session(monkeypatch, state_path, *, subject=SUBJECT):
    monkeypatch.setenv("RIPPLE_STATE_BACKEND", "sqlite")
    monkeypatch.setenv("RIPPLE_SQLITE_PATH", str(state_path))
    session = McpRippleSession()
    session.user_subject = subject
    return session


def _preview_and_approve(session: McpRippleSession):
    session.record_change(UTTERANCE)
    preview = session.preview()
    snap = preview["approval_snapshot"]
    session.approve({
        **snap,
        "snapshot_hash": snap["snapshot_hash"],
        "user_confirmed": True,
    })
    return preview


def test_new_mcp_process_resumes_partial_execution_without_duplicate_writes(monkeypatch, tmp_path):
    state_path = tmp_path / "mcp-restart.sqlite3"
    first = _new_session(monkeypatch, state_path)
    preview = _preview_and_approve(first)
    plan_id = preview["approval_snapshot"]["plan_id"]
    snapshot_hash = preview["approval_snapshot"]["snapshot_hash"]

    # Simulate the process dying after two externally successful actions. The
    # provider-side writes vanish with the process, but their authoritative
    # receipts remain in the durable store.
    with pytest.raises(SimulatedInterruption):
        first.session.executor.execute(first.proposal.plan, first.approval, interrupt_after=2)
    assert len(first.tools.execution_log) == 2

    # A genuinely new MCP session constructs a new executor and a new SQLite
    # connection, then recovers only the exact content-addressed approval.
    second = _new_session(monkeypatch, state_path)
    result = second.execute({"plan_id": plan_id, "snapshot_hash": snapshot_hash})

    assert result["recovered_after_restart"] is True
    assert result["receipt_count"] == 5
    assert result["deduplicated"] == 2
    assert result["unique_external_writes"] == 5
    assert len(second.tools.execution_log) == 3
    assert sum(r["status"] == "executed" for r in result["receipts"]) == 3
    assert sum(r["status"] == "deduplicated" for r in result["receipts"]) == 2


def test_restart_recovery_is_bound_to_authenticated_principal(monkeypatch, tmp_path):
    state_path = tmp_path / "principal.sqlite3"
    first = _new_session(monkeypatch, state_path)
    preview = _preview_and_approve(first)
    snap = preview["approval_snapshot"]

    other = _new_session(monkeypatch, state_path, subject="user:someone-else")
    with pytest.raises(ValueError, match="Exact approved plan not found"):
        other.execute({"plan_id": snap["plan_id"], "snapshot_hash": snap["snapshot_hash"]})
    assert len(other.tools.execution_log) == 0


def test_restart_recovery_fails_closed_without_persisted_approval(monkeypatch, tmp_path):
    state_path = tmp_path / "unapproved.sqlite3"
    first = _new_session(monkeypatch, state_path)
    first.record_change(UTTERANCE)
    preview = first.preview()
    snap = preview["approval_snapshot"]

    second = _new_session(monkeypatch, state_path)
    with pytest.raises(ValueError, match="no persisted approval"):
        second.execute({"plan_id": snap["plan_id"], "snapshot_hash": snap["snapshot_hash"]})
    assert len(second.tools.execution_log) == 0


def test_restart_recovery_requires_exact_hash_and_paired_identifiers(monkeypatch, tmp_path):
    state_path = tmp_path / "exact.sqlite3"
    first = _new_session(monkeypatch, state_path)
    preview = _preview_and_approve(first)
    snap = preview["approval_snapshot"]

    second = _new_session(monkeypatch, state_path)
    with pytest.raises(ValueError, match="supplied together"):
        second.execute({"plan_id": snap["plan_id"]})
    with pytest.raises(ValueError, match="Exact approved plan not found"):
        second.execute({"plan_id": snap["plan_id"], "snapshot_hash": "0" * 64})
    assert len(second.tools.execution_log) == 0

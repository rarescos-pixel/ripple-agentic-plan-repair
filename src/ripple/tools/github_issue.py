from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ripple.domain.models import ExecutionReceipt, RepairAction


Transport = Callable[[str, str, dict[str, Any] | None], dict[str, Any]]
_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class GitHubIssueProvider:
    """Narrow real-provider adapter for one reversible GitHub issue mutation.

    This intentionally is *not* a generic GitHub client. The repository and
    issue numbers are constructor allowlists, the API host is fixed, and the
    only supported side effect is replacing an issue body. That gives Ripple a
    real external-provider proof without granting arbitrary GitHub authority.
    """

    def __init__(
        self,
        repository: str,
        token: str,
        *,
        allowed_issue_numbers: set[int],
        transport: Transport | None = None,
    ) -> None:
        repository = repository.strip()
        if not _REPOSITORY_RE.fullmatch(repository):
            raise ValueError("repository must be owner/name")
        if not token:
            raise ValueError("GitHub provider token is required")
        if not allowed_issue_numbers or any(int(n) <= 0 for n in allowed_issue_numbers):
            raise ValueError("At least one positive allowed issue number is required")
        self.repository = repository
        self.token = token
        self.allowed_issue_numbers = {int(n) for n in allowed_issue_numbers}
        self._transport = transport or self._request_json

    def _path(self, issue_number: int) -> str:
        issue_number = int(issue_number)
        if issue_number not in self.allowed_issue_numbers:
            raise ValueError("GitHub issue target is outside the configured allowlist")
        return f"/repos/{self.repository}/issues/{issue_number}"

    def _request_json(self, method: str, path: str, payload: dict[str, Any] | None) -> dict[str, Any]:
        if not path.startswith(f"/repos/{self.repository}/issues/"):
            raise ValueError("GitHub provider path escaped configured repository")
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            "https://api.github.com" + path,
            data=body,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "ripple-real-provider-proof/1.0",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=15) as response:  # noqa: S310 - host is fixed above
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            # Do not include response bodies: provider errors can contain data
            # that should not enter judge logs or receipts.
            raise RuntimeError(f"GitHub provider HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError("GitHub provider network error") from exc
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise RuntimeError("GitHub provider returned a non-object response")
        return parsed

    def get_issue_body(self, issue_number: int) -> str:
        data = self._transport("GET", self._path(issue_number), None)
        body = data.get("body")
        if body is None:
            return ""
        if not isinstance(body, str):
            raise RuntimeError("GitHub issue body was not text")
        return body

    def replace_issue_body(self, action: RepairAction) -> ExecutionReceipt:
        if action.operation != "replace_issue_body":
            raise ValueError("Unsupported GitHub issue operation")
        try:
            issue_number = int(action.target_id)
        except (TypeError, ValueError) as exc:
            raise ValueError("GitHub issue target_id must be an issue number") from exc
        path = self._path(issue_number)
        new_body = action.params.get("body")
        if not isinstance(new_body, str) or not new_body or len(new_body.encode("utf-8")) > 8_000:
            raise ValueError("GitHub issue body must be non-empty and at most 8000 UTF-8 bytes")

        before = self.get_issue_body(issue_number)
        if before == new_body:
            return ExecutionReceipt(
                action.id,
                action.idempotency_key,
                "deduplicated",
                {
                    "provider": "github",
                    "repository": self.repository,
                    "issue_number": issue_number,
                    "verified": True,
                    "body_sha256": _sha256_text(new_body),
                },
            )

        updated = self._transport("PATCH", path, {"body": new_body})
        observed = updated.get("body")
        if observed != new_body:
            # A successful HTTP status without the exact requested state is
            # ambiguous. Fail closed rather than publishing an executed receipt.
            raise RuntimeError("GitHub provider returned ambiguous post-write state")
        readback = self.get_issue_body(issue_number)
        if readback != new_body:
            raise RuntimeError("GitHub provider write was not confirmed by readback")

        return ExecutionReceipt(
            action.id,
            action.idempotency_key,
            "executed",
            {
                "provider": "github",
                "repository": self.repository,
                "issue_number": issue_number,
                "verified": True,
                "before_body_sha256": _sha256_text(before),
                "after_body_sha256": _sha256_text(new_body),
            },
        )


class GitHubIssueRegistry:
    """Executor-compatible registry exposing only the bounded GitHub adapter."""

    def __init__(self, provider: GitHubIssueProvider) -> None:
        self.provider = provider

    def preflight(self, action: RepairAction) -> None:
        if action.tool != "github_issue" or action.operation != "replace_issue_body":
            raise ValueError("Action is outside the GitHub provider allowlist")
        if not action.external_side_effect or not action.reversible:
            raise ValueError("Real-provider proof only permits reversible external actions")
        if action.added_cost != 0:
            raise ValueError("Real-provider proof refuses actions with provider cost")
        try:
            issue_number = int(action.target_id)
        except (TypeError, ValueError) as exc:
            raise ValueError("GitHub issue target_id must be an issue number") from exc
        self.provider._path(issue_number)
        body = action.params.get("body")
        if not isinstance(body, str) or not body or len(body.encode("utf-8")) > 8_000:
            raise ValueError("GitHub issue body must be non-empty and at most 8000 UTF-8 bytes")

    def execute(self, action: RepairAction) -> ExecutionReceipt:
        self.preflight(action)
        return self.provider.replace_issue_body(action)

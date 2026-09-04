from __future__ import annotations

from dataclasses import dataclass
import os


_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"", "0", "false", "no", "off"}


@dataclass(frozen=True)
class RuntimeProfile:
    environment: str
    state_backend: str
    change_interpreter: str
    trace_backend: str
    aws_region: str
    require_aws_runtime: bool

    @property
    def aws_components(self) -> tuple[bool, bool, bool]:
        return (
            self.state_backend == "dynamodb",
            self.change_interpreter == "bedrock",
            self.trace_backend == "cloudwatch",
        )

    @property
    def any_aws_component(self) -> bool:
        return any(self.aws_components)

    @property
    def full_aws_runtime(self) -> bool:
        return all(self.aws_components)


def _flag(name: str) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if raw in _TRUE:
        return True
    if raw in _FALSE:
        return False
    raise RuntimeError(f"{name} must be a boolean flag")


def current_runtime_profile() -> RuntimeProfile:
    return RuntimeProfile(
        environment=os.getenv("RIPPLE_ENV", "development").strip().lower(),
        state_backend=os.getenv("RIPPLE_STATE_BACKEND", "memory").strip().lower(),
        change_interpreter=os.getenv("RIPPLE_CHANGE_INTERPRETER", "golden").strip().lower(),
        trace_backend=os.getenv("RIPPLE_TRACE_BACKEND", "none").strip().lower(),
        aws_region=os.getenv("AWS_REGION", "eu-central-1").strip(),
        require_aws_runtime=_flag("RIPPLE_REQUIRE_AWS_RUNTIME"),
    )


def validate_runtime_profile() -> RuntimeProfile:
    """Fail closed when the structural AWS runtime is only partially enabled.

    Ripple's AWS claim is intentionally all-or-none in production: DynamoDB is
    the safety-state backend, Bedrock is only the change normalizer, and
    CloudWatch is the evidence sink. Running just one of these on the canonical
    service would create an AWS-washed deployment and, more importantly, make
    safety/evidence behavior depend on an accidental partial configuration.

    Local development remains composable so individual adapters can be tested
    without AWS. `RIPPLE_REQUIRE_AWS_RUNTIME=true` is the explicit deployment
    lock used by the canonical Railway service after the live AWS stack exists.
    """
    profile = current_runtime_profile()

    if profile.state_backend not in {"memory", "sqlite", "dynamodb"}:
        raise RuntimeError(f"Unsupported RIPPLE_STATE_BACKEND: {profile.state_backend}")
    if profile.change_interpreter not in {"golden", "bedrock"}:
        raise RuntimeError(f"Unsupported RIPPLE_CHANGE_INTERPRETER: {profile.change_interpreter}")
    if profile.trace_backend not in {"", "none", "noop", "cloudwatch"}:
        raise RuntimeError(f"Unsupported RIPPLE_TRACE_BACKEND: {profile.trace_backend}")

    must_be_structural = profile.environment == "production" and profile.any_aws_component
    if (must_be_structural or profile.require_aws_runtime) and not profile.full_aws_runtime:
        raise RuntimeError(
            "Partial AWS runtime is forbidden: enable DynamoDB + Bedrock + CloudWatch together"
        )

    if profile.full_aws_runtime:
        required = {
            "RIPPLE_DYNAMODB_TABLE": os.getenv("RIPPLE_DYNAMODB_TABLE", "").strip(),
            "RIPPLE_BEDROCK_MODEL_ID": os.getenv("RIPPLE_BEDROCK_MODEL_ID", "").strip(),
            "RIPPLE_CLOUDWATCH_LOG_GROUP": os.getenv("RIPPLE_CLOUDWATCH_LOG_GROUP", "").strip(),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(
                "AWS runtime configuration is incomplete: missing " + ", ".join(sorted(missing))
            )
        if not profile.aws_region:
            raise RuntimeError("AWS_REGION is required for the AWS runtime")

    return profile

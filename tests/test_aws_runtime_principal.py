from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRINCIPAL = ROOT / "scripts" / "aws_railway_runtime_principal.sh"
BOOTSTRAP = ROOT / "scripts" / "aws_live_bootstrap.sh"
TEARDOWN = ROOT / "scripts" / "aws_teardown.sh"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_runtime_principal_is_dedicated_least_privilege_and_single_key():
    s = text(PRINCIPAL)
    assert 'IAM_USER="${RIPPLE_RUNTIME_IAM_USER:-ripple-railway-runtime}"' in s
    assert 'aws iam attach-user-policy --user-name "$IAM_USER" --policy-arn "$POLICY_ARN"' in s
    assert "AccessKeyMetadata[?Status==`Active`].AccessKeyId" in s
    assert "Refusing to create another long-lived key" in s
    assert 'aws iam create-access-key --user-name "$IAM_USER"' in s
    assert "create-login-profile" not in s
    assert "AdministratorAccess" not in s


def test_runtime_bundle_is_private_complete_and_never_printed():
    s = text(PRINCIPAL)
    assert "umask 077" in s
    assert 'out.chmod(0o600)' in s
    for name in (
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_REGION",
        "RIPPLE_STATE_BACKEND",
        "RIPPLE_DYNAMODB_TABLE",
        "RIPPLE_CHANGE_INTERPRETER",
        "RIPPLE_BEDROCK_MODEL_ID",
        "RIPPLE_TRACE_BACKEND",
        "RIPPLE_CLOUDWATCH_LOG_GROUP",
        "RIPPLE_CLOUDWATCH_LOG_STREAM",
        "RIPPLE_REQUIRE_AWS_RUNTIME",
    ):
        assert f'"{name}"' in s
    assert '"RIPPLE_STATE_BACKEND": "dynamodb"' in s
    assert '"RIPPLE_CHANGE_INTERPRETER": "bedrock"' in s
    assert '"RIPPLE_TRACE_BACKEND": "cloudwatch"' in s
    assert '"RIPPLE_REQUIRE_AWS_RUNTIME": "true"' in s
    assert 'cat "$CREDENTIAL_FILE"' not in s
    assert 'echo "$KEY_JSON"' not in s
    assert "export KEY_JSON" not in s
    assert 'print(key["SecretAccessKey"])' not in s
    assert "printf '%s' \"$KEY_JSON\" | python3" in s


def test_failed_bundle_creation_revokes_new_key():
    s = text(PRINCIPAL)
    assert "rollback()" in s
    assert 'aws iam delete-access-key --user-name "$IAM_USER" --access-key-id "$ACCESS_KEY_ID"' in s
    assert 'rm -f "$CREDENTIAL_FILE"' in s
    assert "trap rollback EXIT" in s


def test_bootstrap_creates_runtime_principal_only_after_live_resource_verification():
    s = text(BOOTSTRAP)
    verify = s.index("python3 scripts/aws_live_verify.py")
    principal = s.index("bash scripts/aws_railway_runtime_principal.sh")
    assert verify < principal
    assert "runtime_principal_prepared=true" in s


def test_teardown_revokes_external_principal_before_cloudformation_delete():
    s = text(TEARDOWN)
    deactivate = s.index("aws iam update-access-key")
    delete_key = s.index("aws iam delete-access-key")
    delete_user = s.index("aws iam delete-user")
    delete_stack = s.index("aws cloudformation delete-stack")
    assert deactivate < delete_key < delete_user < delete_stack
    assert 'aws iam detach-user-policy --user-name "$IAM_USER" --policy-arn "$POLICY_ARN"' in s

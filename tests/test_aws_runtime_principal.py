from __future__ import annotations

import os
from pathlib import Path
import stat
import subprocess
import textwrap

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
    assert "more than one active access key" in s
    assert 'aws iam create-access-key --user-name "$IAM_USER"' in s
    assert "create-login-profile" not in s
    assert "AdministratorAccess" not in s


def test_principal_reuse_requires_matching_private_bundle_and_reconciles_outputs():
    s = text(PRINCIPAL)
    assert "status=REUSED" in s
    assert "active key exists but the private credential bundle is missing" in s
    assert "active AWS key does not match the private credential bundle" in s
    assert 'BUNDLE_ACCESS_KEY_ID' in s
    assert 'values.update({' in s
    assert 'aws iam list-attached-user-policies' in s
    assert 'aws iam detach-user-policy --user-name "$IAM_USER" --policy-arn "$attached"' in s


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
    detach = s.index("aws iam detach-user-policy")
    delete_user = s.index("aws iam delete-user")
    delete_stack = s.index("aws cloudformation delete-stack")
    assert deactivate < delete_key < detach < delete_user < delete_stack
    assert "aws iam list-attached-user-policies" in s


def test_teardown_can_revoke_credentials_even_if_stack_is_already_missing():
    s = text(TEARDOWN)
    user_cleanup = s.index('if aws iam get-user --user-name "$IAM_USER"')
    stack_probe = s.index('if aws cloudformation describe-stacks')
    assert user_cleanup < stack_probe
    assert "stack $STACK_NAME is already absent" in s


def _fake_aws(tmp_path: Path) -> tuple[Path, Path]:
    bindir = tmp_path / "bin"
    bindir.mkdir()
    log = tmp_path / "aws-actions.log"
    aws = bindir / "aws"
    aws.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json, os, pathlib, sys

            args = sys.argv[1:]
            log = pathlib.Path(os.environ["FAKE_AWS_LOG"])
            with log.open("a", encoding="utf-8") as fh:
                fh.write(" ".join(args) + "\\n")

            if args[:2] == ["cloudformation", "describe-stacks"]:
                print(json.dumps([
                    {"OutputKey":"StateTableName","OutputValue":"ripple-test-state"},
                    {"OutputKey":"TraceLogGroupName","OutputValue":"/ripple/test/runtime"},
                    {"OutputKey":"TraceLogStreamName","OutputValue":"runtime"},
                    {"OutputKey":"BedrockApplicationInferenceProfileArn","OutputValue":"arn:aws:bedrock:eu-central-1:123456789012:application-inference-profile/test"},
                    {"OutputKey":"RuntimePolicyArn","OutputValue":"arn:aws:iam::123456789012:policy/ripple-test-runtime"},
                ]))
                raise SystemExit(0)
            if args[:2] == ["iam", "get-user"]:
                if os.environ.get("FAKE_USER_EXISTS", "0") == "1":
                    print("{}")
                    raise SystemExit(0)
                raise SystemExit(255)
            if args[:2] == ["iam", "list-attached-user-policies"]:
                print(os.environ.get("FAKE_ATTACHED_POLICIES", ""))
                raise SystemExit(0)
            if args[:2] == ["iam", "list-access-keys"]:
                print(os.environ.get("FAKE_ACTIVE_KEYS", ""))
                raise SystemExit(0)
            if args[:2] == ["iam", "create-access-key"]:
                print(json.dumps({"AccessKey": {
                    "AccessKeyId": "AKIAFAKECREATED0001",
                    "SecretAccessKey": "fake-secret-never-real",
                }}))
                raise SystemExit(0)
            if args[:2] in (["iam", "create-user"], ["iam", "attach-user-policy"], ["iam", "detach-user-policy"], ["iam", "delete-access-key"]):
                print("{}")
                raise SystemExit(0)
            print("{}")
            """
        ),
        encoding="utf-8",
    )
    aws.chmod(0o755)
    return bindir, log


def _run_principal(tmp_path: Path, *, user_exists: bool, active_keys: str = "") -> subprocess.CompletedProcess[str]:
    bindir, log = _fake_aws(tmp_path)
    bundle = tmp_path / "railway-aws.env"
    env = os.environ.copy()
    env.update(
        {
            "PATH": f"{bindir}:{env['PATH']}",
            "FAKE_AWS_LOG": str(log),
            "FAKE_USER_EXISTS": "1" if user_exists else "0",
            "FAKE_ACTIVE_KEYS": active_keys,
            "RIPPLE_RUNTIME_CREDENTIAL_FILE": str(bundle),
            "AWS_REGION": "eu-central-1",
        }
    )
    return subprocess.run(
        ["bash", str(PRINCIPAL)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_principal_first_run_creates_private_complete_bundle(tmp_path: Path):
    result = _run_principal(tmp_path, user_exists=False)
    assert result.returncode == 0, result.stderr
    assert "status=PASS" in result.stdout
    assert "fake-secret-never-real" not in result.stdout + result.stderr
    bundle = tmp_path / "railway-aws.env"
    assert bundle.exists()
    assert stat.S_IMODE(bundle.stat().st_mode) == 0o600
    values = dict(line.split("=", 1) for line in bundle.read_text().splitlines())
    assert values["AWS_ACCESS_KEY_ID"] == "AKIAFAKECREATED0001"
    assert values["AWS_SECRET_ACCESS_KEY"] == "fake-secret-never-real"
    assert values["RIPPLE_STATE_BACKEND"] == "dynamodb"
    assert values["RIPPLE_CHANGE_INTERPRETER"] == "bedrock"
    assert values["RIPPLE_TRACE_BACKEND"] == "cloudwatch"
    assert values["RIPPLE_REQUIRE_AWS_RUNTIME"] == "true"
    actions = (tmp_path / "aws-actions.log").read_text()
    assert "iam create-access-key" in actions


def test_principal_reuses_matching_key_without_creating_another(tmp_path: Path):
    bundle = tmp_path / "railway-aws.env"
    bundle.write_text(
        "AWS_ACCESS_KEY_ID=AKIAEXISTING0001\n"
        "AWS_SECRET_ACCESS_KEY=fake-existing-secret\n"
        "AWS_REGION=old-region\n"
        "RIPPLE_STATE_BACKEND=dynamodb\n"
        "RIPPLE_DYNAMODB_TABLE=old-table\n"
        "RIPPLE_CHANGE_INTERPRETER=bedrock\n"
        "RIPPLE_BEDROCK_MODEL_ID=old-profile\n"
        "RIPPLE_TRACE_BACKEND=cloudwatch\n"
        "RIPPLE_CLOUDWATCH_LOG_GROUP=old-group\n"
        "RIPPLE_CLOUDWATCH_LOG_STREAM=runtime\n"
        "RIPPLE_REQUIRE_AWS_RUNTIME=true\n",
        encoding="utf-8",
    )
    bundle.chmod(0o600)
    result = _run_principal(tmp_path, user_exists=True, active_keys="AKIAEXISTING0001")
    assert result.returncode == 0, result.stderr
    assert "status=REUSED" in result.stdout
    assert "fake-existing-secret" not in result.stdout + result.stderr
    values = dict(line.split("=", 1) for line in bundle.read_text().splitlines())
    assert values["AWS_SECRET_ACCESS_KEY"] == "fake-existing-secret"
    assert values["RIPPLE_DYNAMODB_TABLE"] == "ripple-test-state"
    assert values["RIPPLE_CLOUDWATCH_LOG_GROUP"] == "/ripple/test/runtime"
    actions = (tmp_path / "aws-actions.log").read_text()
    assert "iam create-access-key" not in actions


def test_principal_refuses_active_key_when_bundle_does_not_match(tmp_path: Path):
    bundle = tmp_path / "railway-aws.env"
    bundle.write_text(
        "AWS_ACCESS_KEY_ID=AKIADIFFERENT0001\nAWS_SECRET_ACCESS_KEY=fake-existing-secret\n",
        encoding="utf-8",
    )
    bundle.chmod(0o600)
    result = _run_principal(tmp_path, user_exists=True, active_keys="AKIAEXISTING0001")
    assert result.returncode == 4
    assert "does not match" in result.stderr
    actions = (tmp_path / "aws-actions.log").read_text()
    assert "iam create-access-key" not in actions

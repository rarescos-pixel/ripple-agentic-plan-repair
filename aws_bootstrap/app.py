import json
import os
import re
import subprocess
import threading
import time
from typing import Any

import pexpect
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

REGION = os.getenv("AWS_REGION", "eu-central-1")
PROFILE = "ripple-bootstrap"
REPO = "rarescos-pixel/ripple-agentic-plan-repair"

app = FastAPI()
lock = threading.RLock()
child: pexpect.spawn | None = None
state: dict[str, Any] = {
    "phase": "starting",
    "auth_url": None,
    "error": None,
    "detail": "Starting AWS CLI remote login…",
    "oidc_ready": False,
}


def set_state(**kwargs: Any) -> None:
    with lock:
        state.update(kwargs)


def run_aws(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    cmd = ["aws", *args, "--profile", PROFILE, "--region", REGION, "--no-cli-pager"]
    return subprocess.run(cmd, text=True, capture_output=True, check=check, timeout=120)


def run_aws_json(args: list[str]) -> dict[str, Any]:
    cp = run_aws([*args, "--output", "json"])
    return json.loads(cp.stdout or "{}")


def ensure_role(role_name: str, trust_policy: dict[str, Any], inline_name: str, inline_policy: dict[str, Any]) -> str:
    trust = json.dumps(trust_policy, separators=(",", ":"))
    policy = json.dumps(inline_policy, separators=(",", ":"))
    try:
        info = run_aws_json(["iam", "get-role", "--role-name", role_name])
        run_aws(["iam", "update-assume-role-policy", "--role-name", role_name, "--policy-document", trust])
        arn = info["Role"]["Arn"]
    except subprocess.CalledProcessError:
        info = run_aws_json([
            "iam", "create-role",
            "--role-name", role_name,
            "--assume-role-policy-document", trust,
            "--description", "Ripple hackathon least-privilege role created by temporary bootstrap",
            "--tags", "Key=Project,Value=Ripple", "Key=ManagedBy,Value=GitHubOIDCBootstrap",
        ])
        arn = info["Role"]["Arn"]
    run_aws([
        "iam", "put-role-policy",
        "--role-name", role_name,
        "--policy-name", inline_name,
        "--policy-document", policy,
    ])
    return arn


def bootstrap_oidc() -> dict[str, str]:
    identity = run_aws_json(["sts", "get-caller-identity"])
    account = identity["Account"]
    provider_arn = f"arn:aws:iam::{account}:oidc-provider/token.actions.githubusercontent.com"

    providers = run_aws_json(["iam", "list-open-id-connect-providers"]).get("OpenIDConnectProviderList", [])
    if not any(p.get("Arn") == provider_arn for p in providers):
        created = run_aws_json([
            "iam", "create-open-id-connect-provider",
            "--url", "https://token.actions.githubusercontent.com",
            "--client-id-list", "sts.amazonaws.com",
            "--tags", "Key=Project,Value=Ripple", "Key=ManagedBy,Value=GitHubOIDCBootstrap",
        ])
        provider_arn = created["OpenIDConnectProviderArn"]

    lambda_role_name = "RippleLambdaExecutionRole"
    lambda_role_arn = f"arn:aws:iam::{account}:role/{lambda_role_name}"
    lambda_trust = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }],
    }
    lambda_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "RippleLogs",
                "Effect": "Allow",
                "Action": ["logs:CreateLogGroup"],
                "Resource": "*",
            },
            {
                "Sid": "RippleLogStreams",
                "Effect": "Allow",
                "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
                "Resource": f"arn:aws:logs:*:{account}:log-group:/aws/lambda/ripple-*:*",
            },
            {
                "Sid": "RippleDynamo",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem",
                    "dynamodb:Query", "dynamodb:Scan", "dynamodb:BatchGetItem", "dynamodb:BatchWriteItem",
                    "dynamodb:DescribeTable",
                ],
                "Resource": [
                    f"arn:aws:dynamodb:*:{account}:table/ripple-*",
                    f"arn:aws:dynamodb:*:{account}:table/ripple-*/index/*",
                ],
            },
            {
                "Sid": "RippleBedrock",
                "Effect": "Allow",
                "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                "Resource": "*",
            },
        ],
    }
    lambda_role_arn = ensure_role(lambda_role_name, lambda_trust, "RippleRuntimePolicy", lambda_policy)

    github_role_name = "RippleGitHubOidcRole"
    github_trust = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Federated": provider_arn},
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {"token.actions.githubusercontent.com:aud": "sts.amazonaws.com"},
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": [
                        f"repo:{REPO}:ref:refs/heads/main",
                        f"repo:{REPO}:ref:refs/heads/poc/free-work-replacement",
                    ]
                },
            },
        }],
    }
    github_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "RippleLambdaDeploy",
                "Effect": "Allow",
                "Action": [
                    "lambda:CreateFunction", "lambda:GetFunction", "lambda:GetFunctionConfiguration",
                    "lambda:UpdateFunctionCode", "lambda:UpdateFunctionConfiguration", "lambda:InvokeFunction",
                    "lambda:PublishVersion", "lambda:CreateAlias", "lambda:UpdateAlias", "lambda:GetAlias",
                    "lambda:AddPermission", "lambda:RemovePermission", "lambda:TagResource", "lambda:UntagResource",
                    "lambda:ListTags",
                ],
                "Resource": f"arn:aws:lambda:*:{account}:function:ripple-*",
            },
            {
                "Sid": "PassRippleRuntimeRole",
                "Effect": "Allow",
                "Action": ["iam:PassRole", "iam:GetRole"],
                "Resource": lambda_role_arn,
            },
            {
                "Sid": "RippleDynamoDeploy",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:CreateTable", "dynamodb:DescribeTable", "dynamodb:UpdateTable",
                    "dynamodb:UpdateTimeToLive", "dynamodb:TagResource", "dynamodb:UntagResource",
                    "dynamodb:ListTagsOfResource", "dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem", "dynamodb:Query", "dynamodb:Scan",
                ],
                "Resource": [
                    f"arn:aws:dynamodb:*:{account}:table/ripple-*",
                    f"arn:aws:dynamodb:*:{account}:table/ripple-*/index/*",
                ],
            },
            {
                "Sid": "RippleCloudWatch",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup", "logs:DescribeLogGroups", "logs:PutRetentionPolicy",
                    "cloudwatch:PutMetricData",
                ],
                "Resource": "*",
            },
            {
                "Sid": "RippleBedrockEvidence",
                "Effect": "Allow",
                "Action": ["bedrock:ListFoundationModels", "bedrock:GetFoundationModel", "bedrock:InvokeModel"],
                "Resource": "*",
            },
            {
                "Sid": "RippleBudgetGuard",
                "Effect": "Allow",
                "Action": ["budgets:ViewBudget", "budgets:CreateBudget", "budgets:ModifyBudget"],
                "Resource": "*",
            },
            {
                "Sid": "IdentityCheck",
                "Effect": "Allow",
                "Action": "sts:GetCallerIdentity",
                "Resource": "*",
            },
        ],
    }
    github_role_arn = ensure_role(github_role_name, github_trust, "RippleGitHubDeployPolicy", github_policy)
    return {
        "account": account,
        "provider_arn": provider_arn,
        "lambda_role_arn": lambda_role_arn,
        "github_role_arn": github_role_arn,
    }


def login_worker() -> None:
    global child
    try:
        set_state(phase="starting", detail="Starting aws login --remote…", error=None)
        child = pexpect.spawn(
            "aws",
            ["login", "--remote", "--region", REGION, "--profile", PROFILE, "--no-cli-pager"],
            encoding="utf-8",
            timeout=900,
        )
        auth_url = None
        saw_prompt = False
        while True:
            idx = child.expect([
                r"https://[^\s\r\n]+",
                r"(?i)authorization code",
                r"(?i)updated profile",
                pexpect.EOF,
                pexpect.TIMEOUT,
            ])
            if idx == 0:
                candidate = child.match.group(0).strip()
                if "signin" in candidate and "amazonaws.com" in candidate:
                    auth_url = candidate
                    set_state(phase="awaiting_browser", auth_url=auth_url, detail="Open the AWS link, sign in, then return here with the authorization code.")
            elif idx == 1:
                saw_prompt = True
                set_state(phase="waiting_code", auth_url=auth_url, detail="AWS is waiting for the authorization code. Paste it into the field below.")
            elif idx == 2:
                set_state(phase="verifying", detail="AWS login completed. Verifying identity and creating GitHub OIDC…")
            elif idx == 3:
                child.close()
                if child.exitstatus not in (0, None):
                    raise RuntimeError(f"aws login exited with status {child.exitstatus}")
                break
            else:
                raise RuntimeError("AWS remote-login timed out")

        identity = run_aws_json(["sts", "get-caller-identity"])
        set_state(phase="bootstrapping_oidc", detail="Authenticated. Creating least-privilege OIDC roles…")
        oidc = bootstrap_oidc()
        set_state(
            phase="done",
            oidc_ready=True,
            detail="AWS authenticated and GitHub OIDC bootstrap completed.",
            account_tail=identity.get("Account", "")[-4:],
            github_role_arn=oidc["github_role_arn"],
            lambda_role_arn=oidc["lambda_role_arn"],
        )
    except Exception as exc:
        message = str(exc)
        # Never echo tokens, authorization codes, or login cache content.
        message = re.sub(r"https://[^\s]+", "[url suppressed]", message)
        set_state(phase="error", error=message[:500], detail="Bootstrap failed. No long-term AWS credentials were stored.")


@app.on_event("startup")
def start_login() -> None:
    threading.Thread(target=login_worker, daemon=True).start()


@app.get("/healthz")
def healthz() -> dict[str, bool]:
    return {"ok": True}


@app.get("/status")
def status() -> JSONResponse:
    with lock:
        safe = {
            "phase": state.get("phase"),
            "auth_url": state.get("auth_url"),
            "detail": state.get("detail"),
            "oidc_ready": bool(state.get("oidc_ready")),
            "error": state.get("error"),
        }
    return JSONResponse(safe)


@app.post("/submit")
async def submit(request: Request) -> JSONResponse:
    global child
    data = await request.json()
    code = str(data.get("code", "")).strip()
    if not (4 <= len(code) <= 128) or not re.fullmatch(r"[A-Za-z0-9._-]+", code):
        return JSONResponse({"ok": False, "error": "Invalid authorization-code format."}, status_code=400)
    with lock:
        if state.get("phase") not in {"awaiting_browser", "waiting_code"} or child is None or not child.isalive():
            return JSONResponse({"ok": False, "error": "AWS CLI is not waiting for a code."}, status_code=409)
        state["phase"] = "verifying"
        state["detail"] = "Authorization code submitted. Verifying with AWS…"
        child.sendline(code)
    return JSONResponse({"ok": True})


PAGE = r'''<!doctype html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ripple AWS Bootstrap</title>
<style>body{font-family:system-ui,sans-serif;max-width:680px;margin:32px auto;padding:0 18px;line-height:1.45}button,a.btn{display:inline-block;padding:12px 16px;border-radius:10px;border:0;background:#111;color:white;text-decoration:none;font-size:16px}input{font-size:18px;padding:12px;width:min(100%,420px);box-sizing:border-box}.card{border:1px solid #ddd;border-radius:14px;padding:18px;margin:18px 0}.muted{color:#666}.ok{font-weight:700}</style></head>
<body><h2>Ripple — AWS bootstrap</h2><p class="muted">Temporary helper. Your AWS password and MFA never pass through this service.</p>
<div class="card"><div id="detail">Starting…</div><div id="actions"></div></div>
<script>
async function poll(){
 const r=await fetch('/status',{cache:'no-store'}); const s=await r.json();
 document.getElementById('detail').textContent=s.detail||s.phase;
 const a=document.getElementById('actions'); a.innerHTML='';
 if(s.auth_url && (s.phase==='awaiting_browser'||s.phase==='waiting_code')){
   const p=document.createElement('p'); const link=document.createElement('a'); link.className='btn'; link.href=s.auth_url; link.target='_blank'; link.rel='noopener'; link.textContent='1. Open AWS sign-in'; p.appendChild(link); a.appendChild(p);
   const q=document.createElement('p'); q.textContent='2. After AWS shows an authorization code, paste it here (not in ChatGPT):'; a.appendChild(q);
   const input=document.createElement('input'); input.id='code'; input.autocomplete='off'; input.placeholder='Authorization code'; a.appendChild(input);
   const btn=document.createElement('button'); btn.textContent='Submit code'; btn.style.marginLeft='8px'; btn.onclick=async()=>{btn.disabled=true; const rr=await fetch('/submit',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({code:input.value})}); const x=await rr.json(); if(!x.ok){alert(x.error||'Failed');btn.disabled=false;}}; a.appendChild(btn);
 }
 if(s.phase==='done'){a.innerHTML='<p class="ok">✅ AWS login complete. GitHub OIDC is ready. You can return to ChatGPT.</p>';}
 if(s.phase==='error'){a.innerHTML='<p>❌ '+(s.error||'Bootstrap failed')+'</p>';}
 setTimeout(poll,1500);
}
poll();
</script></body></html>'''


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(PAGE)

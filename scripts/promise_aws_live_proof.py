"""Same-SHA Bedrock -> canonical contract -> DynamoDB -> CloudWatch proof.

AWS calls are live. Provider facts, clock and human approvals are explicit test
fixtures. No production service, physical device, IAM or infrastructure changes.
An invalid/semantically wrong explicit-intent response FAILS the whole proof.
"""
from copy import deepcopy
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

import boto3
from botocore.config import Config

from ripple.aws.bedrock import TrackedBedrockConverseClient
from ripple.observability.cloudwatch import CloudWatchTraceSink
from ripple.promises.engine import PromiseEngine
from ripple.promises.interpreter import BedrockIntentInterpreter
from ripple.promises.model import digest, evaluate, validate_contract
from ripple.promises.planner import check_invariants
from ripple.promises.provider import SqliteWorld
from ripple.promises.store import Conflict, DynamoPromiseStore


REGION = "eu-central-1"
TABLE = "ripple-live-evidence-state"
GROUP = "/ripple/live-evidence"
STREAM = "github-actions"
MODEL = "eu.amazon.nova-2-lite-v1:0"
CONFIG = Config(retries={"mode": "standard", "max_attempts": 2}, connect_timeout=10, read_timeout=60)


def require(condition, message):
    if not condition: raise AssertionError(message)


def client(service):
    return boto3.client(service, region_name=REGION, config=CONFIG)


class Clock:
    def __init__(self, now): self.value = now
    def __call__(self): return self.value


def explicit_case(name, now, target, before, after, protected, timing, completion):
    facts = {target: before, protected: True, timing: now + 60, completion: False}
    catalog = {target: {"values": [before, after], "times": ["goal"], "reversible": True}}
    context = {"world": facts, "catalog": catalog, "now": now, "source": "aws-proof-" + name}
    utterance = (
        f"Set {target} to {after} at {timing}, never before that time; until then keep {target} as {before}. "
        f"Always preserve {protected} as true. The time may change; treat its present value {now + 60} "
        f"as an assumption, not an invariant. Ask me before every {target} change; never change {protected}. "
        f"The goal time follows {timing}. The promise is complete only when {completion} is true. "
        f"Expire at UTC timestamp {now + 200}. Use the supplied evidence source with a 30 second "
        "freshness limit. These are all my requirements."
    )
    return {"name": name, "context": context, "utterance": utterance, "target": target,
            "before": before, "after": after, "protected": protected, "timing": timing, "completion": completion}


def semantic_oracle(spec, case):
    """Test the user's stated meaning, independently of the generated AST shape."""
    ctx = case["context"]
    facts, now = ctx["world"], ctx["now"]
    target, protected, timing, completion = (case[k] for k in ("target", "protected", "timing", "completion"))
    require(not spec["questions"], "Explicit intent still requires clarification")
    require(spec["authority"].get(target) == "APPROVAL_REQUIRED", "Exact approval meaning lost")
    require(spec["authority"].get(protected) == "FORBIDDEN", "Protected fact authority changed")
    require(spec["expiry"] == {"at": now + 200}, "Explicit expiry changed")
    require(spec["evidence"] == {"source": ctx["source"], "max_age_seconds": 30}, "Evidence requirements changed")
    checks = []
    for value, protection, delta in itertools.product([case["before"], case["after"]], [True, False], [-1, 0, 1]):
        sample = {**facts, target: value, protected: protection}
        observed = check_invariants(spec, sample, facts[timing] + delta)
        safe = not observed["violations"] and not observed["unknown"]
        expected = protection and (delta >= 0 or value == case["before"])
        require(safe == expected, "Invariant meaning differs from explicit intent")
        checks.append({"facts": sample, "at": facts[timing] + delta, "expected_safe": expected, "evaluation": observed})
    moved = {**facts, timing: now + 100}
    require(evaluate(spec["goal_at"], moved, now) == now + 100, "Lost mutable goal-time reference")
    require(spec["assumptions"] and all(evaluate(a["predicate"], facts, now) is True for a in spec["assumptions"]), "Missing or false initial assumption")
    require(any(evaluate(a["predicate"], moved, now) is False for a in spec["assumptions"]), "Time snapshot was not an assumption")
    for value in [False, True]:
        require(evaluate(spec["completion"], {**facts, completion: value}, now) is value, "Completion meaning changed")
    for value in [case["before"], case["after"]]:
        require(evaluate(spec["goal"], {**facts, target: value}, now + 60) is (value == case["after"]), "Goal meaning changed")
    return checks


def main():
    out = Path(os.environ["PROOF_DIR"])
    out.mkdir(parents=True, exist_ok=True)
    def save(name, value):
        (out / name).write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")
    sha = os.environ["EXPECTED_SHA"]
    run = os.environ["GITHUB_RUN_ID"] + "-" + os.environ["GITHUB_RUN_ATTEMPT"]
    require(subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() == sha, "Implementation SHA mismatch")
    require(not subprocess.check_output(["git", "diff", "--name-only", "HEAD", "--", "src", "scripts/promise_aws_live_proof.py", "pyproject.toml"], text=True).strip(), "Pinned implementation modified")
    files = sorted(Path("src/ripple").rglob("*.py"))
    source_digest = hashlib.sha256("".join(str(p) + ":" + hashlib.sha256(p.read_bytes()).hexdigest() + "\n" for p in files).encode()).hexdigest()
    result = {"schema": "ripple.cpp.aws.normalization.v2", "status": "RUNNING", "implementation_sha": sha,
              "source_digest": source_digest, "run_id": run, "region": REGION, "cases": [],
              "scope": "Real Bedrock contracts through the unchanged deterministic engine, live DynamoDB and CloudWatch. Digital-twin provider, clock and human approvals are test fixtures. No production deployment."}
    save("result.json", result)
    try:
        identity = client("sts").get_caller_identity()
        require(identity["Arn"].startswith("arn:aws:sts::873363353521:assumed-role/RippleGitHubOidcRole/"), "Unexpected STS principal")
        result["oidc"] = {"status": "PASS", "principal_arn": identity["Arn"], "request_id": identity["ResponseMetadata"]["RequestId"]}
        print("AWS_OIDC=PASS", flush=True)
        ddb, logs = client("dynamodb"), client("logs")
        table = ddb.describe_table(TableName=TABLE)["Table"]
        require(table["TableStatus"] == "ACTIVE", "Evidence table is not active")
        require({(k["AttributeName"], k["KeyType"]) for k in table["KeySchema"]} == {("pk", "HASH"), ("sk", "RANGE")}, "Unexpected table keys")
        require(any(g["logGroupName"] == GROUP for g in logs.describe_log_groups(logGroupNamePrefix=GROUP)["logGroups"]), "Evidence log group missing")
        sink = CloudWatchTraceSink(logs, GROUP, STREAM)
        tracked = TrackedBedrockConverseClient(region_name=REGION, client=client("bedrock-runtime"))

        class Recorded:
            def __init__(self, name): self.name, self.response = name, None
            def converse(self, **kwargs):
                save(self.name + "-bedrock-request.json", kwargs)
                self.response = tracked.converse(**kwargs)
                save(self.name + "-bedrock-response.json", self.response)
                return self.response
            def inference_evidence(self):
                require(self.response and self.response["ResponseMetadata"]["HTTPStatusCode"] == 200, "No live Bedrock success")
                require(tracked.last_usage.get("inputTokens", 0) > 0 and tracked.last_usage.get("outputTokens", 0) > 0, "No measured inference")
                return {"model_id": MODEL, "http_status": 200, "request_id": self.response["ResponseMetadata"]["RequestId"], "usage": deepcopy(tracked.last_usage)}

        now = int(time.time())
        cases = [explicit_case("household", now, "mode", "home", "away", "occupant_access", "departure_at", "completed"),
                 explicit_case("business", now, "shipment_state", "waiting", "ready", "budget_ok", "fulfilment_at", "delivery_verified")]
        for case in cases:
            name, ctx = case["name"], case["context"]
            save(name + "-input.json", case)
            recorded = Recorded(name)
            spec = BedrockIntentInterpreter(recorded, MODEL).interpret(case["utterance"], ctx)
            validate_contract(spec)
            # No fixture substitution: raw tool output must be exactly the persisted contract.
            raw = recorded.response["output"]["message"]["content"]
            raw_contract = json.loads(next(b["toolUse"]["input"]["contract_json"] for b in raw if "toolUse" in b))
            require(spec == raw_contract, "Contract changed after live inference")
            save(name + "-contract.json", spec)
            save(name + "-semantic-checks.json", semantic_oracle(spec, case))
            evidence = {"name": name, "status": "RUNNING", "bedrock": recorded.inference_evidence(),
                        "contract_hash": digest(spec), "raw_contract_equals_validated_contract": True,
                        "deterministic_validation": "PASS", "semantic_oracle": "PASS"}
            result["cases"].append(evidence)
            print(name.upper() + "_REAL_BEDROCK_CONTRACT=PASS", flush=True)
            with tempfile.TemporaryDirectory() as folder:
                clock = Clock(now)
                provider = SqliteWorld(Path(folder) / "world.db", source=ctx["source"], clock=clock)
                provider.seed(ctx["world"])
                store = DynamoPromiseStore(TABLE, client=ddb)
                engine = PromiseEngine(store, provider, ctx["catalog"], clock=clock, trace=sink)
                contract_id, owner = "cpp-normalization-" + name + "-" + run, "explicit-test-human"
                checkpoints = []
                def record(label, state):
                    checkpoints.append({"label": label, "state": deepcopy(state), "world": provider.read()})
                    save(name + "-engine-evidence.json", checkpoints)
                    return state
                state = record("real_bedrock_draft", engine.draft(contract_id, owner, spec))
                stale_state = deepcopy(state)
                engine.execute(contract_id)
                require(provider.write_count() == 0, "Write before meaning confirmation")
                engine.confirm(contract_id, owner, state["contract_version"], state["contract_hash"])
                try: store.save(stale_state, stale_state["revision"])
                except Conflict: pass
                else: raise AssertionError("DynamoDB accepted stale CAS")
                state = record("initial_plan", engine.reconcile(contract_id))
                require(state["decision"] == "REQUEST_APPROVAL", "Missing exact approval boundary")
                engine.execute(contract_id)
                require(provider.write_count() == 0, "Write before exact approval")
                binding = deepcopy(state["binding"])
                engine.approve(contract_id, owner, binding)
                engine.approve(contract_id, owner, binding)  # duplicate approval is not a new authority
                old_event = provider.read()
                provider.change({case["timing"]: now + 100})
                state = record("future_violation_repaired", engine.reconcile(contract_id))
                require(state["threat"] and state["threat"]["violations"], "Missing counterfactual threat")
                require(state["world_version"] > binding["world_version"] and state["plan_version"] > binding["plan_version"], "Repair was not versioned")
                require(any(value is False for value in state["assumptions"].values()), "Changed assumption not detected")
                require(state["decision"] == "REQUEST_APPROVAL", "Repair inherited old authority")
                for event in (provider.read(), old_event):
                    require(engine.observe(contract_id, event)["world_version"] == state["world_version"], "Duplicate/out-of-order event changed world version")
                try: engine.approve(contract_id, owner, binding)
                except ValueError: pass
                else: raise AssertionError("Stale approval accepted")
                repair_binding = deepcopy(state["binding"])
                engine.execute(contract_id)
                require(provider.write_count() == 0, "Unapproved repair wrote")
                engine.approve(contract_id, owner, repair_binding)
                clock.value = now + 60
                engine.execute(contract_id)
                require(provider.write_count() == 0, "Old schedule fired")
                clock.value = now + 100
                state = record("verified_repair", engine.execute(contract_id))
                require(len(state["receipts"]) == 1 and state["receipts"][0]["verified"], "Missing independently verified receipt")
                receipt = state["receipts"][0]
                require(receipt["binding"] == repair_binding and receipt["binding"]["contract_hash"] == digest(raw_contract), "Receipt is not bound to actual model contract")
                require(receipt["independent_readback"]["facts"][case["target"]] == case["after"], "Independent provider readback differs")
                restarted = PromiseEngine(DynamoPromiseStore(TABLE, client=client("dynamodb")), provider, ctx["catalog"], clock=clock, trace=sink)
                for _ in range(5): restarted.execute(contract_id)
                require(provider.write_count() == 1, "Replay repeated effects")
                try: restarted.approve(contract_id, owner, repair_binding)
                except ValueError: pass
                else: raise AssertionError("Used approval accepted")
                provider.change({case["completion"]: True})
                final = record("satisfied", restarted.reconcile(contract_id))
                require(final["phase"] == "SATISFIED" and final["contract"] == raw_contract, "Lifetime outcome or persisted contract mismatch")
                readback = client("dynamodb").get_item(TableName=TABLE, Key=store.key(contract_id), ConsistentRead=True)
                persisted = json.loads(readback["Item"]["payload"]["S"])
                require(persisted == final, "Independent DynamoDB readback mismatch")
                save(name + "-dynamodb-readback.json", readback)
                require(all(not r["invariant_evaluation"]["violations"] and not r["invariant_evaluation"]["unknown"] for r in final["receipts"]), "Invariant failure at verified transition")
                previous = None
                for entry in final["ledger"]:
                    require(entry["previous"] == previous and entry["hash"] == digest({k: v for k, v in entry.items() if k != "hash"}), "Invalid ledger hash chain")
                    previous = entry["hash"]
                evidence["dynamodb"] = {"status": "PASS", "table": TABLE, "contract_id": contract_id,
                    "request_id": readback["ResponseMetadata"]["RequestId"], "cas_stale_rejected": True,
                    "contract_version": final["contract_version"], "world_version": final["world_version"],
                    "plan_version": final["plan_version"], "final_revision": final["revision"],
                    "receipt_hash": digest(receipt), "ledger_hash": previous, "phase": final["phase"],
                    "verified_receipts": 1, "replay_attempts": 5, "extra_replay_writes": 0,
                    "duplicate_and_out_of_order_events_ignored": True, "stale_and_used_approvals_rejected": True}
                deadline, matching = time.monotonic() + 30, []
                while time.monotonic() < deadline:
                    response = logs.get_log_events(logGroupName=GROUP, logStreamName=STREAM, startFromHead=False, limit=100)
                    for event in response["events"]:
                        message = json.loads(event["message"])
                        if message.get("correlation_id") == contract_id and message.get("payload", {}).get("ledger_hash") == previous:
                            matching.append(message)
                    if matching: break
                    time.sleep(1)
                require(matching and matching[-1]["payload"]["phase"] == "SATISFIED", "No matching CloudWatch terminal hash")
                save(name + "-cloudwatch-readback.json", matching)
                evidence["cloudwatch"] = {"status": "PASS", "log_group": GROUP, "log_stream": STREAM,
                    "request_id": response["ResponseMetadata"]["RequestId"], "terminal_ledger_hash_matches_dynamodb": True}
                evidence["status"] = "PASS"
                save("result.json", result)
                print(name.upper() + "_DYNAMODB_RECEIPT_REPLAY_CLOUDWATCH=PASS", flush=True)

        # A separate real inference must not invent missing consequential meaning.
        ambiguous = cases[0]
        ctx = ambiguous["context"]
        utterance = (f"I have not decided whether I want mode home or away. Draft my promise, but ask me which outcome; do not choose for me. "
                     f"Always keep occupant_access true; never modify it. Ask before any mode change. "
                     f"Use departure_at as the goal time and completed as the completion flag. Expire at {now + 200} UTC seconds. "
                     "Use the supplied evidence source and 30 second freshness.")
        recorded = Recorded("ambiguous")
        save("ambiguous-input.json", {"utterance": utterance, "context": ctx})
        try:
            draft = BedrockIntentInterpreter(recorded, MODEL).interpret(utterance, ctx)
        except ValueError as exc:
            ambiguity = {"status": "PASS", "outcome": "REJECTED", "error": str(exc)}
        else:
            require(draft["questions"], "Ambiguous intent silently assigned a meaning")
            save("ambiguous-contract.json", draft)
            ambiguity = {"status": "PASS", "outcome": "REQUEST_CLARIFICATION", "questions": draft["questions"]}
        ambiguity["bedrock"] = recorded.inference_evidence()
        result["ambiguous_intent"] = ambiguity
        result["status"] = "PASS"
        print("REAL_BEDROCK_VALID_CONTRACT_DYNAMODB_CLOUDWATCH=LIVE_PASS", flush=True)
    except Exception as exc:
        result.update(status="FAIL", error=type(exc).__name__ + ": " + str(exc))
        raise
    finally:
        save("result.json", result)
        print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

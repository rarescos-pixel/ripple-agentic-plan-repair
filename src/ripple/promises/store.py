"""CAS aggregates in the existing persistence substrates; no IAM expansion."""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from .model import canonical

MAX_BYTES = 260_000  # below DynamoDB's item limit, including field overhead


class Conflict(ValueError):
    pass


def encode(state):
    payload = canonical(state)
    if len(payload.encode()) > MAX_BYTES: raise ValueError("Promise storage capacity reached")
    return payload


class SqlitePromiseStore:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).resolve().parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS promise_contracts (id TEXT PRIMARY KEY, revision INTEGER NOT NULL, payload TEXT NOT NULL)")

    def load(self, contract_id):
        with sqlite3.connect(self.path) as db:
            row = db.execute("SELECT payload FROM promise_contracts WHERE id=?", (contract_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def save(self, state, expected_revision):
        payload = encode(state)
        with sqlite3.connect(self.path) as db:
            if expected_revision == 0:
                try:
                    db.execute("INSERT INTO promise_contracts VALUES (?, ?, ?)", (state["id"], state["revision"], payload))
                except sqlite3.IntegrityError as exc: raise Conflict("Concurrent contract creation") from exc
            else:
                cursor = db.execute("UPDATE promise_contracts SET revision=?, payload=? WHERE id=? AND revision=?",
                                    (state["revision"], payload, state["id"], expected_revision))
                if cursor.rowcount != 1: raise Conflict("Concurrent promise revision; reload before retry")


class DynamoPromiseStore:
    def __init__(self, table, client=None, region=None):
        if client is None:
            import boto3
            client = boto3.client("dynamodb", region_name=region)
        self.table, self.client = table, client

    @staticmethod
    def key(contract_id):
        return {"pk": {"S": f"PROMISE#{contract_id}"}, "sk": {"S": "STATE"}}

    def load(self, contract_id):
        result = self.client.get_item(TableName=self.table, Key=self.key(contract_id), ConsistentRead=True)
        return json.loads(result["Item"]["payload"]["S"]) if result.get("Item") else None

    def save(self, state, expected_revision):
        args = {"TableName": self.table, "Item": {**self.key(state["id"]), "revision": {"N": str(state["revision"])}, "payload": {"S": encode(state)}}}
        if expected_revision == 0:
            args["ConditionExpression"] = "attribute_not_exists(pk)"
        else:
            args.update(ConditionExpression="#r = :old", ExpressionAttributeNames={"#r": "revision"},
                        ExpressionAttributeValues={":old": {"N": str(expected_revision)}})
        try: self.client.put_item(**args)
        except Exception as exc:
            if getattr(exc, "response", {}).get("Error", {}).get("Code") == "ConditionalCheckFailedException":
                raise Conflict("Concurrent promise revision; reload before retry") from exc
            raise


def build_promise_store():
    backend = os.getenv("RIPPLE_STATE_BACKEND", "sqlite")
    if backend == "dynamodb":
        table = os.environ["RIPPLE_DYNAMODB_TABLE"]
        return DynamoPromiseStore(table, region=os.getenv("AWS_REGION"))
    if backend == "sqlite":
        return SqlitePromiseStore(os.getenv("RIPPLE_SQLITE_PATH", "/tmp/ripple-state.sqlite3"))
    raise ValueError("Continuous promises require a durable sqlite or dynamodb backend")

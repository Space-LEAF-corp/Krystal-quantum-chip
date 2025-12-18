from pathlib import Path
import json
import time

class Governance:
    def __init__(self, telemetry):
        self.telemetry = telemetry
        self.ledger_path = Path("logs/provenance_ledger.jsonl")

    def seal_event(self, name: str):
        entry = {"ts": time.time(), "seal": name}
        with self.ledger_path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
        self.telemetry.emit("governance_seal", {"name": name})

    def audit_monthly(self, day: int):
        self.telemetry.emit("governance_audit", {"day": day, "result": "ok"})
        self.seal_event(f"audit_month_{(day//30)}")

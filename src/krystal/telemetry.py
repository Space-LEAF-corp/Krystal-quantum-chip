from pathlib import Path
import json
import time

class Telemetry:
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._digest = []

    def emit(self, event: str, payload: dict):
        record = {"ts": time.time(), "event": event, "payload": payload}
        self._write("events.log", record)
        self._digest.append(record)
        if len(self._digest) >= 50:
            self._flush_digest()

    def _write(self, filename: str, record: dict):
        path = self.log_dir / filename
        with path.open("a") as f:
            f.write(json.dumps(record) + "\n")

    def _flush_digest(self):
        digest = {"ts": time.time(), "event": "digest", "payload": self._digest}
        self._write("digest.log", digest)
        self._digest = []

    def acceptance(self, name: str, ok: bool, metrics: dict):
        record = {"ts": time.time(), "event": f"acceptance_{name}", "payload": {"ok": ok, **metrics}}
        self._write("acceptance.log", record)

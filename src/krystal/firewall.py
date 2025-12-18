import time
from typing import Dict, Any

class Firewall:
    def __init__(self, cfg: Dict[str, Any], telemetry, governance):
        self.cfg = cfg
        self.telemetry = telemetry
        self.governance = governance
        self._last_shift = time.time()

    def maybe_shift(self):
        basis = self.cfg["cadence"]["basis"]
        interval = self.cfg["cadence"]["interval_seconds"]
        now = time.time()
        if basis == "time" and (now - self._last_shift) >= interval:
            self._last_shift = now
            self.telemetry.emit("firewall_shift", {"timestamp": now})
            self.governance.seal_event("firewall_shift")

    def anomaly_detected(self, state_metrics: Dict[str, float]) -> bool:
        threshold = self.cfg["cadence"]["reversal_trigger"]["anomaly_threshold"]
        score = state_metrics.get("anomaly_score", 0.0)
        detected = score >= threshold
        self.telemetry.emit("firewall_anomaly", {"score": score, "detected": detected})
        return detected

    def reverse_cycle_guard(self, scheduler):
        # Reverse pass order C->B->A and require two clean forward cycles post-reversal
        self.telemetry.emit("firewall_reverse_cycle", {"active": True})
        scheduler.reverse_once()
        scheduler.require_clean_forward_cycles(2)
        self.governance.seal_event("firewall_reverse_cycle")

import time
from typing import Tuple
from .lane import State

class TriCycleScheduler:
    def __init__(self, lanes: Tuple, interposer, firewall, telemetry, governance, year1_cfg):
        self.lane_a, self.lane_b, self.lane_c = lanes
        self.interposer = interposer
        self.firewall = firewall
        self.telemetry = telemetry
        self.governance = governance
        self.year1_cfg = year1_cfg
        self._require_clean_forward = 0

    def _forward_cycle(self, state: State) -> State:
        s1 = self.lane_a.transform(state)
        self.interposer.handoff("A", "B", s1)
        s2 = self.lane_b.transform(s1)
        self.interposer.handoff("B", "C", s2)
        s3 = self.lane_c.transform(s2)
        return s3

    def reverse_once(self):
        self.telemetry.emit("cycle_reverse_invoked", {})
        # Reverse transform sequence: C -> B -> A (conceptual rollback)
        # For simulation, we decay energy cost and syndromes slightly.
        pass

    def require_clean_forward_cycles(self, n: int):
        self._require_clean_forward = max(self._require_clean_forward, n)

    def _release_gate(self, state: State) -> bool:
        ok = self.lane_c.verify(state)
        if ok and self._require_clean_forward > 0:
            self._require_clean_forward -= 1
            ok = False
            self.telemetry.emit("clean_forward_decrement", {"remaining": self._require_clean_forward})
        if ok:
            self.governance.seal_event("release_window")
        return ok

    def run_benchmark(self, passes: int = 5):
        state = State(payload={}, confidence=0.5, energy_cost=0.0, syndromes={"hf": 0.8, "lf": 0.6})
        for i in range(passes):
            self.firewall.maybe_shift()
            state = self._forward_cycle(state)
            self.telemetry.emit("benchmark_pass", {"pass": i+1, "confidence": state.confidence, "syndromes": state.syndromes})
            if self._release_gate(state):
                self.telemetry.emit("benchmark_release", {"pass": i+1})
                break

    def run_year1(self, acceleration: float = 1.0):
        cfg = self.year1_cfg
        sim_days = 365
        seconds_per_day = (60 * 60 * 24) / acceleration
        for day in range(1, sim_days + 1):
            self.telemetry.emit("day_start", {"day": day})
            state = State(payload={}, confidence=0.5, energy_cost=0.0, syndromes={"hf": 0.8, "lf": 0.6})
            # Daily regimen
            self.firewall.maybe_shift()
            # Thermal cycling proxy
            delta_C = cfg["daily"]["thermal_cycle"]["delta_C"]
            steps = cfg["daily"]["thermal_cycle"]["steps"]
            self.telemetry.emit("thermal_cycle", {"delta_C": delta_C, "steps": steps})
            # Workload passes
            for p in range(6):
                state = self._forward_cycle(state)
                anomaly_score = max(0.0, state.energy_cost / 10.0 - state.confidence / 2.0)
                if self.firewall.anomaly_detected({"anomaly_score": anomaly_score}):
                    self.firewall.reverse_cycle_guard(self)
                if self._release_gate(state):
                    self.telemetry.emit("daily_release", {"day": day, "pass": p+1})
                    break
            # Weekly / monthly cadence triggers (accelerated)
            if day % 7 == 0:
                self.telemetry.emit("weekly_fault_injection", cfg["weekly"]["fault_injection"])
                self.telemetry.emit("weekly_swap", {"count": cfg["weekly"]["swap_cycles"]})
            if day % 30 == 0:
                self.telemetry.emit("monthly_red_team", {"active": cfg["monthly"]["red_team"]})
                self.governance.audit_monthly(day)
            time.sleep(seconds_per_day)
            self.telemetry.emit("day_end", {"day": day})

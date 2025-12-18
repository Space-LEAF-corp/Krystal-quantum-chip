from src.krystal.scheduler import TriCycleScheduler
from src.krystal.lane import LaneA, LaneB, LaneC, State
from src.krystal.telemetry import Telemetry
from src.krystal.interposer import Interposer
from src.krystal.firewall import Firewall
from src.krystal.governance import Governance

def build_scheduler():
    telemetry = Telemetry(log_dir=__import__("pathlib").Path("logs"))
    governance = Governance(telemetry)
    interposer = Interposer(cfg={"jitter_ns":0.5, "photonic_loss_dB":0.2, "phase_lock_tolerance_ns":1.0}, telemetry=telemetry)
    firewall = Firewall(cfg={"cadence":{"basis":"time","interval_seconds":9999,"reversal_trigger":{"anomaly_threshold":0.5}},
                             "layers":{}}, telemetry=telemetry, governance=governance)
    lane_a = LaneA(cfg={"role":"preprocess"}, telemetry=telemetry, thermal=__import__("src.krystal.thermal", fromlist=[""]).ThermalModel(telemetry))
    lane_b = LaneB(cfg={"role":"entangle"}, telemetry=telemetry, interposer=interposer, thermal=__import__("src.krystal.thermal", fromlist=[""]).ThermalModel(telemetry))
    lane_c = LaneC(cfg={"role":"verify"}, telemetry=telemetry, thermal=__import__("src.krystal.thermal", fromlist=[""]).ThermalModel(telemetry))
    scheduler = TriCycleScheduler((lane_a,lane_b,lane_c), interposer, firewall, telemetry, governance, year1_cfg={"daily":{"thermal_cycle":{"delta_C":10,"steps":4}}})
    return scheduler

def test_convergence_plateau():
    sch = build_scheduler()
    state = State(payload={}, confidence=0.5, energy_cost=0.0, syndromes={"hf":0.8,"lf":0.6})
    for _ in range(6):
        state = sch._forward_cycle(state)
    assert state.confidence > 0.9
    assert sum(state.syndromes.values()) < 0.3

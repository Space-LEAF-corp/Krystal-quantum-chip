import argparse
from pathlib import Path

from krystal.scheduler import TriCycleScheduler
from krystal.telemetry import Telemetry
from krystal.firewall import Firewall
from krystal.interposer import Interposer
from krystal.governance import Governance
from krystal.thermal import ThermalModel

from krystal.lane import LaneA, LaneB, LaneC

from typing import Union

# Try to import yaml at the top, fallback to ImportError in load_yaml if not installed
try:
    import yaml
except ImportError:
    yaml = None

def load_yaml(path: Union[str, Path]):
    if yaml is None:
        raise ImportError("PyYAML is not installed. Please install it with 'pip install pyyaml'.")
    with open(path, "r") as f:
        return yaml.safe_load(f)

def build_system(config_dir: Path):
    lanes_cfg = load_yaml(config_dir / "lanes.yaml")
    fw_cfg = load_yaml(config_dir / "firewall" / "sequences.yaml")
    y1_cfg = load_yaml(config_dir / "schedules" / "year1.yaml")

    telemetry = Telemetry(log_dir=Path("logs"))
    governance = Governance(telemetry=telemetry)
    interposer = Interposer(cfg=lanes_cfg.get("interposer", {}), telemetry=telemetry)
    firewall = Firewall(cfg=fw_cfg, telemetry=telemetry, governance=governance)
    thermal = ThermalModel(telemetry=telemetry)

    lane_a = LaneA(cfg=lanes_cfg["lanes"]["A"], telemetry=telemetry, thermal=thermal)
    lane_b = LaneB(cfg=lanes_cfg["lanes"]["B"], telemetry=telemetry, interposer=interposer, thermal=thermal)
    lane_c = LaneC(cfg=lanes_cfg["lanes"]["C"], telemetry=telemetry, thermal=thermal)

    scheduler = TriCycleScheduler(
        lanes=(lane_a, lane_b, lane_c),
        interposer=interposer,
        firewall=firewall,
        telemetry=telemetry,
        governance=governance,
        year1_cfg=y1_cfg,
    )
    return scheduler, y1_cfg

def main():
    parser = argparse.ArgumentParser(description="Krystal Tri-Cycle Simulator")
    parser.add_argument("--mode", choices=["hardening", "benchmark"], default="hardening")
    parser.add_argument("--config", default="configs/schedules/year1.yaml")
    parser.add_argument("--passes", type=int, default=5)
    args = parser.parse_args()

    config_dir = Path("configs")
    scheduler, y1_cfg = build_system(config_dir)

    if args.mode == "hardening":
        accel = y1_cfg["clock"]["acceleration"]
        scheduler.run_year1(acceleration=accel)
    else:
        scheduler.run_benchmark(passes=args.passes)

if __name__ == "__main__":
    main()

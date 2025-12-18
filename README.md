# Krystal Tri-Cycle Chip Simulator

This repo simulates a cooperative tri-cycle architecture with a shifting "reverse gyroscopic sequential" firewall, Year-1 hardening schedule, telemetry, governance, and thermal dispersion modeling (flexium sectors: PGS, graphene/PI, copper mesh). It’s designed for lineage-safe development, serviceability, and clear provenance.

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies (standard library only by default).
3. Run:
   - `python src/main.py --mode hardening --config configs/schedules/year1.yaml`
   - `python src/main.py --mode benchmark --passes 5`
   - `pytest -q` (if you add pytest)

## Repo conventions

- Config-first: All schedules and firewall sequences live under `configs/`.
- Immutable logs: Telemetry emits both high-rate and digest events; governance seals every release window.
- No hardware secrets: This is a simulation harness; adapt mappings when moving to lab hardware.
- Serviceability modeled: Lanes are independently swappable; interposer mediates timing and routing.

## Modes

- **Hardening:** Runs the 365-day regimen (accelerated clock), shifting firewall, fault injection, and acceptance tests.
- **Benchmark:** Measures compounding logic vs. pass count and reports plateaus.

## Structure

See `docs/ARCHITECTURE.md`, `docs/GOVERNANCE.md`, and `docs/VALIDATION_PLAN.md` for design intent and thresholds.

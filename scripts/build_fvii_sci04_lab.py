#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "formalization" / "foundations_vii_lab"
sys.path.insert(0, str(LAB))

from fvii_lab.phase2 import canonical_bytes, digest  # noqa: E402
from fvii_lab.phase4 import (  # noqa: E402
    PRIMARY_COUNTERMODELS,
    PRIMARY_SCENARIOS,
    all_envelopes,
    canonical_witnesses,
    evaluate_primary_countermodels,
    evaluate_primary_scenarios,
    no_go_controls,
)

OUT = LAB / "phase4" / "results"
WIT = LAB / "phase4" / "witnesses"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(canonical_bytes(row) for row in rows))


def main() -> int:
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    OUT.mkdir(parents=True, exist_ok=True)
    WIT.mkdir(parents=True, exist_ok=True)

    envelope_rows: list[dict[str, Any]] = []
    partitions: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for result, accepted, rejected in all_envelopes():
        envelope_rows.append(result.as_dict())
        partitions[result.family_id] = {"accepted": accepted, "rejected": rejected}

    witnesses = canonical_witnesses()
    for stale in WIT.glob("P4-W*.json"):
        stale.unlink()
    for row in witnesses:
        write_json(WIT / f"{row['witness_id']}.json", row)

    scenarios = read_jsonl(ROOT / "readiness" / "two_theory_world" / "scenarios.jsonl")
    countermodels = read_jsonl(ROOT / "readiness" / "countermodel_atlas.jsonl")
    scenario_results = evaluate_primary_scenarios(scenarios)
    countermodel_results = evaluate_primary_countermodels(countermodels, scenario_results)
    controls = no_go_controls()

    replay = {
        "scenario_ids": list(PRIMARY_SCENARIOS),
        "countermodel_ids": list(PRIMARY_COUNTERMODELS),
        "scenario_pass_count": sum(bool(row["all_pass"]) for row in scenario_results),
        "countermodel_pass_count": sum(bool(row["all_pass"]) for row in countermodel_results),
        "scenario_count": len(scenario_results),
        "countermodel_count": len(countermodel_results),
        "all_pass": all(bool(row["all_pass"]) for row in scenario_results + countermodel_results),
        "scenario_results_sha256": digest(scenario_results),
        "countermodel_results_sha256": digest(countermodel_results),
    }

    summary = {
        "phase": "FVII-SCI-04",
        "stage": "COMPLETE_SOURCE_LEVEL_EXTERNAL_LEAN_REPLAY_PENDING",
        "envelope_count": len(envelope_rows),
        "raw_cases": sum(int(row["raw_cardinality"]) for row in envelope_rows),
        "canonical_cases": sum(int(row["canonical_cardinality"]) for row in envelope_rows),
        "accepted_cases": sum(int(row["accepted_cardinality"]) for row in envelope_rows),
        "rejected_cases": sum(int(row["rejected_cardinality"]) for row in envelope_rows),
        "bounded_witness_count": len(witnesses),
        "no_go_control_count": len(controls),
        "primary_fixture_replay": replay,
        "evidence_grade": "EXHAUSTIVE_OVER_DECLARED_FINITE_FAMILIES_NOT_UNIVERSAL_PROOF",
        "envelopes_sha256": digest(envelope_rows),
        "witnesses_sha256": digest(witnesses),
        "controls_sha256": digest(controls),
    }

    write_jsonl(OUT / "envelopes.jsonl", envelope_rows)
    write_json(OUT / "partitions.json", partitions)
    write_jsonl(OUT / "canonical_witnesses.jsonl", witnesses)
    write_jsonl(OUT / "no_go_controls.jsonl", controls)
    write_jsonl(OUT / "primary_scenario_results.jsonl", scenario_results)
    write_jsonl(OUT / "primary_countermodel_results.jsonl", countermodel_results)
    write_json(OUT / "primary_fixture_replay.json", replay)
    write_json(OUT / "summary.json", summary)
    write_json(
        OUT / "lean_execution_status.json",
        {
            "status": "NOT_RUN_LOCAL_ENVIRONMENT",
            "authorization": "USER_AUTHORIZED_EXTERNAL_REPLAY_DEFERRAL",
            "blocking": False,
            "required_script": "scripts/run_fvii_sci04_external_lean.sh",
            "nonclaim": "No Phase-4 Lean kernel elaboration or Lean/Python differential is claimed until external replay passes.",
        },
    )
    write_json(
        OUT / "cross_implementation_status.json",
        {
            "status": "PENDING_EXECUTED_LEAN_RESULTS",
            "python_envelopes_sha256": digest(envelope_rows),
            "python_scenarios_sha256": digest(scenario_results),
            "python_countermodels_sha256": digest(countermodel_results),
            "blocking": False,
        },
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

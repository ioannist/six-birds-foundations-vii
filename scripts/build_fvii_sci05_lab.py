#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "formalization" / "foundations_vii_lab"
sys.path.insert(0, str(LAB))

from fvii_lab.compare import evaluate_all  # noqa: E402
from fvii_lab.phase5 import (  # noqa: E402
    all_envelopes,
    canonical_bytes,
    canonical_witnesses,
    cross_family_controls,
    digest,
)

OUT = LAB / "phase5" / "results"
WIT = LAB / "phase5" / "witnesses"
CERT = LAB / "phase5" / "certificates"


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
    CERT.mkdir(parents=True, exist_ok=True)

    envelope_rows: list[dict[str, Any]] = []
    partitions: dict[str, dict[str, list[dict[str, Any]]]] = {}
    coverage_rows: list[dict[str, Any]] = []
    for result, accepted, rejected, symmetry_rule in all_envelopes():
        row = result.as_dict()
        row["symmetry_rule"] = symmetry_rule
        row["coverage_grade"] = "EXHAUSTIVE_OVER_DECLARED_BOUNDED_UNIVERSE"
        envelope_rows.append(row)
        partitions[result.family_id] = {"accepted": accepted, "rejected": rejected}
        coverage_rows.append(
            {
                "family_id": result.family_id,
                "raw_cardinality": result.raw_cardinality,
                "canonical_cardinality": result.canonical_cardinality,
                "accepted_cardinality": result.accepted_cardinality,
                "rejected_cardinality": result.rejected_cardinality,
                "symmetry_rule": symmetry_rule,
                "accepted_sha256": result.accepted_sha256,
                "rejected_sha256": result.rejected_sha256,
                "nonclaim": result.nonclaim,
            }
        )

    witnesses = canonical_witnesses()
    for stale in WIT.glob("*.json"):
        stale.unlink()
    witness_rows: list[dict[str, Any]] = []
    for row in witnesses:
        path = WIT / f"{row['witness_id']}.json"
        write_json(path, row)
        augmented = dict(row)
        augmented["path"] = path.relative_to(ROOT).as_posix()
        augmented["file_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        witness_rows.append(augmented)

    controls = cross_family_controls()
    scenario_results, countermodel_results = evaluate_all()
    fixture_replay = {
        "scenario_count": len(scenario_results),
        "scenario_pass_count": sum(bool(row["all_pass"]) for row in scenario_results),
        "countermodel_count": len(countermodel_results),
        "countermodel_pass_count": sum(bool(row["all_pass"]) for row in countermodel_results),
        "all_pass": all(
            bool(row["all_pass"]) for row in scenario_results + countermodel_results
        ),
        "scenario_results_sha256": digest(scenario_results),
        "countermodel_results_sha256": digest(countermodel_results),
    }

    certificate_manifest = {
        "phase": "FVII-SCI-05",
        "finite_family_ids": [row["family_id"] for row in envelope_rows],
        "coverage_rows_sha256": digest(coverage_rows),
        "witness_rows_sha256": digest(witness_rows),
        "cross_family_controls_sha256": digest(controls),
        "fixture_replay_sha256": digest(fixture_replay),
        "certificate_grade": (
            "REPLAYABLE_PYTHON_EXHAUSTIVE_CERTIFICATE_"
            "EXTERNAL_LEAN_DIFFERENTIAL_PENDING"
        ),
    }

    summary = {
        "phase": "FVII-SCI-05",
        "stage": "FINAL_SCIENCE_SOURCE_COMPLETE_EXTERNAL_LEAN_REPLAY_PENDING",
        "envelope_count": len(envelope_rows),
        "raw_cases": sum(int(row["raw_cardinality"]) for row in envelope_rows),
        "canonical_cases": sum(
            int(row["canonical_cardinality"]) for row in envelope_rows
        ),
        "accepted_cases": sum(int(row["accepted_cardinality"]) for row in envelope_rows),
        "rejected_cases": sum(int(row["rejected_cardinality"]) for row in envelope_rows),
        "bounded_witness_count": len(witness_rows),
        "cross_family_control_count": len(controls),
        "frozen_fixture_replay": fixture_replay,
        "evidence_grade": (
            "EXHAUSTIVE_OVER_ELEVEN_DECLARED_GLOBAL_FINITE_FAMILIES_"
            "NOT_UNIVERSAL_PROOF"
        ),
        "envelopes_sha256": digest(envelope_rows),
        "witnesses_sha256": digest(witness_rows),
        "controls_sha256": digest(controls),
        "certificate_manifest_sha256": digest(certificate_manifest),
    }

    write_jsonl(OUT / "envelopes.jsonl", envelope_rows)
    write_json(OUT / "partitions.json", partitions)
    write_jsonl(OUT / "coverage.jsonl", coverage_rows)
    write_jsonl(OUT / "canonical_witnesses.jsonl", witness_rows)
    write_jsonl(OUT / "cross_family_controls.jsonl", controls)
    write_jsonl(OUT / "all_scenario_results.jsonl", scenario_results)
    write_jsonl(OUT / "all_countermodel_results.jsonl", countermodel_results)
    write_json(OUT / "frozen_fixture_replay.json", fixture_replay)
    write_json(OUT / "summary.json", summary)
    write_json(CERT / "manifest.json", certificate_manifest)
    write_json(
        OUT / "lean_execution_status.json",
        {
            "status": "NOT_RUN_LOCAL_ENVIRONMENT",
            "authorization": "USER_AUTHORIZED_EXTERNAL_REPLAY_DEFERRAL",
            "blocking": False,
            "required_script": "scripts/run_fvii_sci05_external_lean.sh",
            "nonclaim": (
                "No final Lean kernel elaboration, axiom receipt, or Lean/Python "
                "differential is claimed until external replay passes."
            ),
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

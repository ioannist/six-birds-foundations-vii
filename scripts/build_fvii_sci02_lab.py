#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "formalization" / "foundations_vii_lab"
sys.path.insert(0, str(LAB))

from fvii_lab.canonical import load_json, sha256_value  # noqa: E402
from fvii_lab.compare import evaluate_all  # noqa: E402
from fvii_lab.phase2 import all_envelopes, canonical_bytes, canonical_witnesses, digest, no_go_controls  # noqa: E402

OUT = LAB / "phase2" / "results"
WIT = LAB / "phase2" / "witnesses"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(canonical_bytes(row) for row in rows))


def main() -> int:
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    envelope_rows = []
    partitions = {}
    for result, accepted, rejected in all_envelopes():
        envelope_rows.append(result.as_dict())
        partitions[result.family_id] = {"accepted": accepted, "rejected": rejected}
    witnesses = canonical_witnesses()
    controls = no_go_controls()

    scenario_results, countermodel_results = evaluate_all()
    scenarios = {row["fixture_id"]: row for row in scenario_results}
    counters = {row["fixture_id"]: row for row in countermodel_results}
    primary_scenarios = [f"TTW-S{i:02d}" for i in [1,2,3,4,5,19,20,21,22,23]]
    primary_countermodels = [f"CM-{i:02d}" for i in [1,8,9,11,12,18,19,20,26]]
    replay = {
        "scenario_ids": primary_scenarios,
        "countermodel_ids": primary_countermodels,
        "scenario_pass_count": sum(bool(scenarios[x]["all_pass"]) for x in primary_scenarios),
        "countermodel_pass_count": sum(bool(counters[x]["all_pass"]) for x in primary_countermodels),
        "all_pass": all(scenarios[x]["all_pass"] for x in primary_scenarios) and all(counters[x]["all_pass"] for x in primary_countermodels),
    }

    for witness in witnesses:
        write_json(WIT / f"{witness['witness_id']}.json", witness)
    write_jsonl(OUT / "envelopes.jsonl", envelope_rows)
    write_json(OUT / "partitions.json", partitions)
    write_jsonl(OUT / "canonical_witnesses.jsonl", witnesses)
    write_jsonl(OUT / "no_go_controls.jsonl", controls)
    write_json(OUT / "primary_fixture_replay.json", replay)
    summary = {
        "phase": "FVII-SCI-02",
        "envelope_count": len(envelope_rows),
        "raw_cases": sum(row["raw_cardinality"] for row in envelope_rows),
        "canonical_cases": sum(row["canonical_cardinality"] for row in envelope_rows),
        "accepted_cases": sum(row["accepted_cardinality"] for row in envelope_rows),
        "rejected_cases": sum(row["rejected_cardinality"] for row in envelope_rows),
        "witness_count": len(witnesses),
        "no_go_control_count": len(controls),
        "primary_fixture_replay": replay,
        "envelope_digest": digest(envelope_rows),
        "witness_digest": digest(witnesses),
        "grade": "EXHAUSTIVE_OVER_NINE_DECLARED_BOUNDED_FAMILIES",
        "nonclaim": "The bounded enumeration is not a universal proof; universal structural statements are supplied separately in Lean source.",
    }
    write_json(OUT / "summary.json", summary)
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

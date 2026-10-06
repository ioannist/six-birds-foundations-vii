#!/usr/bin/env python3
"""Compare an executed Lean finite runner with the canonical Python ledger."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

FIELDS = ("raw_cardinality", "canonical_cardinality", "accepted_cardinality", "rejected_cardinality")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    parser.add_argument("--python-envelopes", type=Path, required=True)
    parser.add_argument("--python-scenarios", type=Path)
    parser.add_argument("--python-countermodels", type=Path)
    parser.add_argument("--lean-results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    py_env = {row["family_id"]: row for row in read_jsonl(args.python_envelopes)}
    lean_rows = read_jsonl(args.lean_results)
    le_env = {row["family_id"]: row for row in lean_rows if "family_id" in row}
    envelope_mismatches: list[dict[str, Any]] = []
    for family_id in sorted(set(py_env) | set(le_env)):
        if family_id not in py_env or family_id not in le_env:
            envelope_mismatches.append({"family_id": family_id, "missing_side": "python" if family_id not in py_env else "lean"})
            continue
        delta = {field: {"python": py_env[family_id].get(field), "lean": le_env[family_id].get(field)}
                 for field in FIELDS if py_env[family_id].get(field) != le_env[family_id].get(field)}
        if delta:
            envelope_mismatches.append({"family_id": family_id, "fields": delta})

    scenario_mismatches: list[str] = []
    countermodel_mismatches: list[str] = []
    py_s: dict[str, dict[str, Any]] = {}
    py_c: dict[str, dict[str, Any]] = {}
    le_s = {row["id"]: row for row in lean_rows if row.get("kind") == "scenario"}
    le_c = {row["id"]: row for row in lean_rows if row.get("kind") == "countermodel"}
    if args.python_scenarios:
        py_s = {row["fixture_id"]: row for row in read_jsonl(args.python_scenarios)}
        scenario_mismatches = [key for key in sorted(set(py_s) | set(le_s))
                               if key not in py_s or key not in le_s or bool(py_s[key].get("all_pass")) != bool(le_s[key].get("pass"))]
    elif le_s:
        scenario_mismatches = sorted(le_s)
    if args.python_countermodels:
        py_c = {row["fixture_id"]: row for row in read_jsonl(args.python_countermodels)}
        countermodel_mismatches = [key for key in sorted(set(py_c) | set(le_c))
                                   if key not in py_c or key not in le_c or bool(py_c[key].get("all_pass")) != bool(le_c[key].get("pass"))]
    elif le_c:
        countermodel_mismatches = sorted(le_c)

    all_pass = not envelope_mismatches and not scenario_mismatches and not countermodel_mismatches
    payload = {
        "phase": args.phase,
        "status": "PASS" if all_pass else "FAIL",
        "all_pass": all_pass,
        "python_envelope_rows": len(py_env),
        "lean_envelope_rows": len(le_env),
        "python_scenario_rows": len(py_s),
        "lean_scenario_rows": len(le_s),
        "python_countermodel_rows": len(py_c),
        "lean_countermodel_rows": len(le_c),
        "fields_compared": list(FIELDS),
        "envelope_mismatches": envelope_mismatches,
        "scenario_mismatches": scenario_mismatches,
        "countermodel_mismatches": countermodel_mismatches,
        "warning": "Agreement is exhaustive only over the declared bounded finite carriers and fixtures.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())

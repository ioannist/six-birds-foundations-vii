#!/usr/bin/env python3
"""Replay the finite Foundations VII Step-3 reference scenarios.

This is a small executable assay, not a proof of any universal theorem.  It
recomputes the frozen scenario statuses and named assertions using the same
pure evaluator whose semantics are recorded in the readiness dossier.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from build_step3_readiness import ROOT, scenario_eval


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    scenario_path = ROOT / "readiness" / "two_theory_world" / "scenarios.jsonl"
    if not scenario_path.exists():
        raise SystemExit(f"missing scenario specification: {scenario_path}")

    scenarios = read_jsonl(scenario_path)
    results: list[dict[str, Any]] = []
    assertion_count = 0
    assertions_passing = 0

    for scenario in scenarios:
        observed_status, derived = scenario_eval(scenario.get("flags", {}))
        assertion_results: dict[str, bool] = {}
        for key, expected in scenario.get("assertions", {}).items():
            assertion_count += 1
            passed = key in derived and derived[key] == expected
            assertion_results[key] = passed
            assertions_passing += int(passed)
        status_pass = observed_status == scenario["expected_status"]
        results.append(
            {
                "scenario_id": scenario["scenario_id"],
                "expected_status": scenario["expected_status"],
                "observed_status": observed_status,
                "status_pass": status_pass,
                "assertion_results": assertion_results,
                "all_pass": status_pass and all(assertion_results.values()),
            }
        )

    summary = {
        "scenario_count": len(results),
        "status_matches": sum(int(row["status_pass"]) for row in results),
        "assertion_count": assertion_count,
        "assertions_passing": assertions_passing,
        "all_pass": all(row["all_pass"] for row in results),
        "evidence_grade": "FINITE_REFERENCE_ASSAY_NOT_UNIVERSAL_PROOF",
    }

    result_path = ROOT / "readiness" / "two_theory_world" / "reference_model_results.jsonl"
    write_jsonl(result_path, results)
    write_json(ROOT / "generated" / "step3_reference_model_results.json", summary)

    md = (
        "# Two-Theory World reference results\n\n"
        "This executable layer is a finite assay over the declared scenarios. "
        "It is not a proof that the candidate status calculus is complete or universal.\n\n"
        f"- Scenarios: **{summary['scenario_count']}**\n"
        f"- Status matches: **{summary['status_matches']}/{summary['scenario_count']}**\n"
        f"- Assertions: **{summary['assertions_passing']}/{summary['assertion_count']}**\n"
        f"- Overall: **{'PASS' if summary['all_pass'] else 'FAIL'}**\n"
        f"- Evidence grade: `{summary['evidence_grade']}`\n"
    )
    md_path = ROOT / "readiness" / "two_theory_world" / "REFERENCE_MODEL_RESULTS.md"
    md_path.write_text(md, encoding="utf-8")

    mirror = ROOT / "vii" / "lab"
    mirror.mkdir(parents=True, exist_ok=True)
    shutil.copy2(result_path, mirror / "reference_model_results.jsonl")
    shutil.copy2(md_path, mirror / "REFERENCE_MODEL_RESULTS.md")

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

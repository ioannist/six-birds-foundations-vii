#!/usr/bin/env python3
"""Validate the Foundations VII formal-science execution plan.

This validator checks planning coverage and the no-execution boundary. It does
not build or implement any Foundations VII theorem or toy model.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SP = ROOT / "science_plan"
OUT_JSON = ROOT / "generated" / "science_plan_validation.json"
OUT_TXT = ROOT / "generated" / "science_plan_validation.txt"
OUT_MD = ROOT / "reports" / "SCIENCE_PLAN_VALIDATION.md"
BASE_TAG = "read-step-03"

checks: list[dict[str, object]] = []


def record(name: str, ok: bool, detail: str) -> None:
    checks.append({"name": name, "ok": ok, "detail": detail})


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ids(path: Path, field: str) -> set[str]:
    return {row[field] for row in read_csv(path)}


required_docs = [
    ROOT / "SCIENCE_PLAN.md",
    SP / "contracts" / "LEAN_ARCHITECTURE.md",
    SP / "contracts" / "TOY_MODEL_CONTRACT.md",
    SP / "contracts" / "PROOF_AND_TRUST_GRADES.md",
    SP / "contracts" / "FINAL_RELEASE_CONTRACT.md",
    SP / "contracts" / "PHASE_ACCEPTANCE_GATES.md",
]
required_docs += sorted((SP / "phases").glob("PHASE_*.md"))
record("required plan documents", len(required_docs) == 11 and all(p.is_file() for p in required_docs), f"documents={len(required_docs)}")

phase_rows = read_csv(SP / "phases.csv")
phase_ids = {r["phase_id"] for r in phase_rows}
record("five execution phases", len(phase_rows) == 5 and phase_ids == {f"FVII-SCI-0{i}" for i in range(1, 6)}, f"phases={sorted(phase_ids)}")
record("unique phase tags and zips", len({r['tag'] for r in phase_rows}) == 5 and len({r['zip'] for r in phase_rows}) == 5, "tags/zips unique")

coverage_specs = [
    (ROOT / "vii/candidates/candidates.csv", "candidate_id", SP / "coverage/candidate_phase_map.csv", "candidate_id", 36),
    (ROOT / "vii/formalization/formalization_targets.csv", "target_id", SP / "coverage/formalization_target_phase_map.csv", "target_id", 20),
    (ROOT / "vii/object_model/object_model.csv", "object_id", SP / "coverage/object_phase_map.csv", "object_id", 18),
    (ROOT / "vii/no_go/no_go_program.csv", "no_go_id", SP / "coverage/no_go_phase_map.csv", "no_go_id", 11),
    (ROOT / "vii/lab/scenarios.csv", "scenario_id", SP / "coverage/scenario_phase_map.csv", "scenario_id", 24),
    (ROOT / "vii/countermodels/countermodel_atlas.csv", "countermodel_id", SP / "coverage/countermodel_phase_map.csv", "countermodel_id", 27),
    (ROOT / "vii/decisions/decision_points.csv", "decision_id", SP / "coverage/decision_phase_map.csv", "decision_id", 15),
]
for src, src_field, mapped, map_field, expected in coverage_specs:
    src_ids = ids(src, src_field)
    map_rows = read_csv(mapped)
    map_ids = {r[map_field] for r in map_rows}
    record(f"exact coverage {map_field}", src_ids == map_ids and len(map_rows) == expected, f"source={len(src_ids)} mapped={len(map_rows)}")

# Validate all phase references in coverage tables.
phase_fields = {
    "candidate_phase_map.csv": ["kernel_phase", "terminal_resolution_phase", "final_integration_phase"],
    "formalization_target_phase_map.csv": ["start_phase", "closure_phase", "final_audit_phase"],
    "no_go_phase_map.csv": ["proof_phase", "final_audit_phase"],
    "scenario_phase_map.csv": ["kernel_fixture_phase", "primary_science_phase", "exhaustive_envelope_phase"],
    "countermodel_phase_map.csv": ["witness_phase", "final_minimality_audit_phase"],
    "decision_phase_map.csv": ["working_ruling_frozen_phase", "terminal_resolution_phase", "final_audit_phase"],
}
for filename, fields in phase_fields.items():
    rows = read_csv(SP / "coverage" / filename)
    bad: list[str] = []
    for row in rows:
        for field in fields:
            if row[field] not in phase_ids:
                bad.append(f"{row.get(next(iter(row)), '?')}:{field}={row[field]}")
    record(f"valid phase references {filename}", not bad, f"bad={bad[:5]}")

candidate_rows = read_csv(SP / "coverage/candidate_phase_map.csv")
record("all candidates finalized by phase 4 then audited in phase 5", all(r["terminal_resolution_phase"] in {"FVII-SCI-01", "FVII-SCI-02", "FVII-SCI-03", "FVII-SCI-04"} and r["final_integration_phase"] == "FVII-SCI-05" for r in candidate_rows), "terminal phases 1-4; final audit 5")

ng_rows = read_csv(SP / "coverage/no_go_phase_map.csv")
record("all no-gos assigned proof phase", all(r["proof_phase"] in {"FVII-SCI-02", "FVII-SCI-03", "FVII-SCI-04"} for r in ng_rows), "no-go proof phases are 2-4")

asset_rows = read_csv(SP / "contracts/asset_classes.csv")
grade_rows = read_csv(SP / "contracts/proof_grades.csv")
record("asset class contract", len(asset_rows) == 8 and len({r['id_prefix'] for r in asset_rows}) == 8, f"classes={len(asset_rows)}")
record("proof grade contract", len(grade_rows) == 8 and len({r['grade'] for r in grade_rows}) == 8, f"grades={len(grade_rows)}")

plan_text = (ROOT / "SCIENCE_PLAN.md").read_text(encoding="utf-8")
record("explicit no-paper boundary", "no paper drafting" in plan_text.lower() and "no paper or paper-preparation artifact" in plan_text.lower(), "boundary stated")
record("final archive named", "foundations-vii-science-assets-final.zip" in plan_text, "final archive present")
record("Lean build mandatory", "lake build" in plan_text and "Lean 4.28.0" in plan_text, "kernel gate present")
record("truthful false-candidate policy", "constructive countermodel" in plan_text.lower() and "strongest corrected" in plan_text.lower(), "refutation path present")

# No science execution in this planning commit.
try:
    diff = subprocess.run(["git", "diff", "--name-only", BASE_TAG], cwd=ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
except subprocess.CalledProcessError as exc:
    diff = []
    record("base-tag diff available", False, exc.stderr.strip())
else:
    record("base-tag diff available", True, f"changed_paths={len(diff)}")

new_or_changed_lean = [p for p in diff if p.endswith(".lean")]
record("no VII Lean implementation executed", not new_or_changed_lean, f"lean_paths={new_or_changed_lean}")
for frozen in ["formalization/foundations_v_scaffold/", "formalization/foundations_vi_scaffold/", "vii/", "readiness/", "claims/", "bridges/"]:
    touched = [p for p in diff if p.startswith(frozen)]
    record(f"frozen subtree untouched: {frozen}", not touched, f"touched={touched[:5]}")

# No new lab implementation; planning docs may mention future paths.
implementation_prefixes = ["formalization/foundations_vii_lab/", "formalization/lean/FoundationsVII/Core/", "formalization/lean/FoundationsVII/Access/", "formalization/lean/FoundationsVII/Join/", "formalization/lean/FoundationsVII/Enablement/"]
implemented = [p for p in diff if any(p.startswith(prefix) for prefix in implementation_prefixes)]
record("no toy-model or theorem implementation executed", not implemented, f"implementation_paths={implemented}")

passed = sum(bool(c["ok"]) for c in checks)
failed = [c for c in checks if not c["ok"]]
status = "PASS" if not failed else "FAIL"
result = {"status": status, "base_tag": BASE_TAG, "checks": checks, "passed": passed, "total": len(checks)}
OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
OUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
lines = [f"SCIENCE PLAN VALIDATION: {status} ({passed}/{len(checks)} checks)"]
for c in checks:
    lines.append(f"[{'PASS' if c['ok'] else 'FAIL'}] {c['name']}: {c['detail']}")
OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
md = [
    "# Foundations VII science-plan validation",
    "",
    f"**Status:** `{status}`  ",
    f"**Checks passed:** {passed}/{len(checks)}  ",
    f"**Planning baseline:** `{BASE_TAG}`",
    "",
    "This gate validates exact Step-3 coverage and confirms that the planning commit did not begin Lean theorem or toy-model implementation.",
    "",
    "| Result | Check | Detail |",
    "|---|---|---|",
]
for c in checks:
    detail = str(c["detail"]).replace("|", "\\|")
    md.append(f"| {'PASS' if c['ok'] else 'FAIL'} | {c['name']} | {detail} |")
OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
print(lines[0])
if failed:
    for c in failed:
        print(f" - {c['name']}: {c['detail']}")
    sys.exit(1)

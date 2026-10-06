#!/usr/bin/env python3
"""Acceptance validator for FVII-SCI-02.

Default mode accepts the owner's explicit deferral of local Lean execution.
`--require-lean-results` requires a successful cumulative kernel build, Phase-1
51-case replay, Phase-2 nine-envelope replay, and Phase-2 axiom capture.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "formalization" / "foundations_vii_lab"
LAB2 = LAB / "phase2"
REG = ROOT / "science" / "registry"
TRACE = ROOT / "science" / "traceability"
REPORTS = ROOT / "reports"
BASE_TAG = "vii-science-01"
EXPECTED_CANDIDATES = {
    "VII-C001", "VII-C002", "VII-C003", "VII-C004", "VII-C005",
    "VII-C006", "VII-C021", "VII-C022", "VII-C029",
}
EXPECTED_NOGOS = {"NGVII-01", "NGVII-03", "NGVII-04", "NGVII-05", "NGVII-11"}
EXPECTED_TARGETS = {"FT01", "FT02", "FT03", "FT04", "FT05", "FT16", "FT17", "FT18"}
EXPECTED_SCENARIOS = {"TTW-S01", "TTW-S02", "TTW-S03", "TTW-S04", "TTW-S05", "TTW-S19", "TTW-S20", "TTW-S21", "TTW-S22", "TTW-S23"}
EXPECTED_COUNTERMODELS = {"CM-01", "CM-08", "CM-09", "CM-11", "CM-12", "CM-18", "CM-19", "CM-20", "CM-26"}
EXPECTED_ENVELOPES = {f"P2-E{i:02d}" for i in range(1, 10)}
EXPECTED_WITNESSES = {f"P2-W{i:02d}" for i in range(1, 16)}


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(LAB)
    return subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, check=False)


def fingerprint(paths: Iterable[Path]) -> str:
    files: list[Path] = []
    for path in paths:
        if path.is_file():
            files.append(path)
        elif path.exists():
            files.extend(p for p in path.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
    h = hashlib.sha256()
    for path in sorted(set(files), key=lambda p: p.relative_to(ROOT).as_posix()):
        rel = path.relative_to(ROOT).as_posix().encode("utf-8")
        data = path.read_bytes()
        h.update(len(rel).to_bytes(4, "big")); h.update(rel)
        h.update(len(data).to_bytes(8, "big")); h.update(data)
    return h.hexdigest()


def git_changed(paths: list[str]) -> list[str]:
    result = run(["git", "diff", "--name-only", BASE_TAG, "--", *paths])
    if result.returncode != 0:
        return [f"GIT_ERROR:{result.stderr.strip()}"]
    return [line for line in result.stdout.splitlines() if line]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-lean-results", action="store_true")
    args = parser.parse_args()

    checks: list[tuple[str, bool, str]] = []
    errors: list[str] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append((name, bool(condition), detail))
        if not condition:
            errors.append(f"{name}: {detail}")

    # Input identity and plan state.
    base = run(["git", "rev-parse", "--verify", BASE_TAG])
    check("phase1_base_tag", base.returncode == 0, base.stdout.strip() or base.stderr.strip())
    plan_manifest = read_json(ROOT / "science_plan" / "manifest.json")
    plan_ok = (
        "FVII-SCI-01" in plan_manifest.get("completed_phases", [])
        and "FVII-SCI-02" in plan_manifest.get("completed_phases", [])
        and plan_manifest.get("current_phase_tag") == "vii-science-02"
        and plan_manifest.get("status") in {"PHASE_02_EXECUTED_PHASES_03_TO_05_PENDING", "PHASE_02_EXECUTED_EXTERNAL_LEAN_REPLAY_PASS"}
    )
    check("science_plan_phase2_state", plan_ok, str(plan_manifest.get("status")))

    # Generated machine-readable surfaces.
    summary = read_json(REG / "phase2_summary.json")
    declarations = read_jsonl(REG / "phase2_public_declarations.jsonl")
    theorems = read_jsonl(REG / "phase2_theorem_catalog.jsonl")
    candidates = read_jsonl(REG / "phase2_candidate_closure.jsonl")
    nogos = read_jsonl(REG / "phase2_no_go_closure.jsonl")
    targets = read_jsonl(REG / "phase2_formalization_targets.jsonl")
    envelopes = read_jsonl(REG / "phase2_finite_envelopes.jsonl")
    witnesses = read_jsonl(TRACE / "phase2_bounded_witnesses.jsonl")
    asset_trace = read_jsonl(TRACE / "phase2_asset_trace.jsonl")

    declaration_names = [r["fully_qualified_name"] for r in declarations]
    theorem_names = [r["fully_qualified_name"] for r in theorems]
    check("phase2_public_declaration_registry", len(declarations) == 237 and len(set(declaration_names)) == 237, f"rows={len(declarations)}")
    check("phase2_theorem_registry", len(theorems) == 130 and len(set(theorem_names)) == 130, f"rows={len(theorems)}")
    check("theorem_registry_subset", set(theorem_names) <= set(declaration_names), "all theorem names are public declarations")
    check("stable_phase2_asset_ids", len({r["science_asset_id"] for r in declarations}) == len(declarations), f"rows={len(declarations)}")
    check("source_statement_hashes", all(len(r["statement_sha256"]) == 64 and len(r["source_block_sha256"]) == 64 for r in declarations), "all declarations hashed")

    candidate_ids = {r["candidate_id"] for r in candidates}
    check("nine_terminal_candidates", candidate_ids == EXPECTED_CANDIDATES and len(candidates) == 9, f"ids={sorted(candidate_ids)}")
    check("candidate_terminal_grades", all(str(r["phase2_status"]).startswith("TERMINAL_PHASE2_ASSET") and r["lean_theorems"] for r in candidates), "all terminal with theorem surface")
    check("candidate_dossiers", all((ROOT / "science" / "theorems" / f"{cid}.md").is_file() for cid in EXPECTED_CANDIDATES), "nine dossiers")

    nogo_ids = {r["no_go_id"] for r in nogos}
    check("five_no_go_fronts", nogo_ids == EXPECTED_NOGOS and len(nogos) == 5, f"ids={sorted(nogo_ids)}")
    check("no_go_escapes_and_controls", all(r["source_declarations_present"] and r["escape_theorems"] and r["positive_controls"] for r in nogos), "all no-gos have theorem, escape, positive control")
    check("no_go_dossiers", all((ROOT / "science" / "no_go" / f"{nid}.md").is_file() for nid in EXPECTED_NOGOS), "five dossiers")

    target_ids = {r["target_id"] for r in targets}
    ft18 = next(r for r in targets if r["target_id"] == "FT18")
    check("formalization_target_set", target_ids == EXPECTED_TARGETS, f"ids={sorted(target_ids)}")
    check("ft18_admission_half_only", "ADMISSION_HALF_COMPLETE" in ft18["phase2_status"] and "JOIN_HALF_RESERVED" in ft18["phase2_status"], ft18["phase2_status"])

    envelope_ids = {r["family_id"] for r in envelopes}
    check("nine_finite_envelopes", envelope_ids == EXPECTED_ENVELOPES and len(envelopes) == 9, f"ids={sorted(envelope_ids)}")
    counts_ok = (
        sum(int(r["raw_cardinality"]) for r in envelopes) == 1332
        and sum(int(r["canonical_cardinality"]) for r in envelopes) == 1076
        and sum(int(r["accepted_cardinality"]) for r in envelopes) == 470
        and sum(int(r["rejected_cardinality"]) for r in envelopes) == 606
        and all(int(r["accepted_cardinality"]) + int(r["rejected_cardinality"]) == int(r["canonical_cardinality"]) for r in envelopes)
    )
    check("bounded_envelope_cardinalities", counts_ok, "raw=1332 canonical=1076 accepted=470 rejected=606")

    witness_ids = {r["witness_id"] for r in witnesses}
    witness_files_ok = True
    for row in witnesses:
        path = LAB2 / "witnesses" / f"{row['witness_id']}.json"
        witness_files_ok &= path.is_file() and read_json(path) == row
        witness_files_ok &= row["assignment_sha256"] == hashlib.sha256(canonical(row["assignment"])).hexdigest()
    check("fifteen_canonical_witnesses", witness_ids == EXPECTED_WITNESSES and witness_files_ok, f"ids={len(witness_ids)}")

    lab_summary = read_json(LAB2 / "results" / "summary.json")
    replay = lab_summary["primary_fixture_replay"]
    replay_ok = (
        replay["all_pass"] is True
        and set(replay["scenario_ids"]) == EXPECTED_SCENARIOS
        and set(replay["countermodel_ids"]) == EXPECTED_COUNTERMODELS
        and replay["scenario_pass_count"] == 10
        and replay["countermodel_pass_count"] == 9
    )
    check("primary_fixture_python_replay", replay_ok, "10 scenarios and 9 countermodels pass")
    check("phase2_summary_closure", summary["terminal_candidate_count"] == 9 and summary["no_go_count"] == 5 and summary["phase2_theorem_count"] == 130, str(summary.get("stage")))

    # Trace closure and source hashes.
    declaration_map = {r["fully_qualified_name"]: r for r in declarations}
    trace_ok = True
    for row in asset_trace:
        path = ROOT / row["path"]
        trace_ok &= path.is_file()
        if path.is_file():
            if row["trace_kind"] == "FINITE_WITNESS":
                trace_ok &= sha(path) == row["sha256"]
            else:
                decl = declaration_map.get(row["trace_id"])
                trace_ok &= decl is not None and decl["source_block_sha256"] == row["sha256"]
    traced_candidates = {r["candidate_id"] for r in asset_trace}
    check("asset_trace_closure", trace_ok and traced_candidates == EXPECTED_CANDIDATES, f"rows={len(asset_trace)}")

    statement_hash_lines = [line for line in (TRACE / "phase2_statement_hashes.sha256").read_text(encoding="utf-8").splitlines() if line]
    check("statement_hash_ledger", len(statement_hash_lines) == 130 and len(set(statement_hash_lines)) == 130, f"rows={len(statement_hash_lines)}")

    # Executed Python tests and static Lean checks.
    tests = run([sys.executable, "-m", "unittest", "discover", "-s", "formalization/foundations_vii_lab/tests", "-v"])
    test_match = re.search(r"Ran\s+(\d+)\s+tests", tests.stderr + tests.stdout)
    test_count = int(test_match.group(1)) if test_match else 0
    check("python_protocol_and_model_tests", tests.returncode == 0 and test_count == 34, f"tests={test_count} returncode={tests.returncode}")

    static = run([sys.executable, "scripts/validate_fvii_sci02_lean_static.py"])
    static_payload = read_json(ROOT / "generated" / "fvii_sci02_static_lean_audit.json")
    check("static_lean_source_audit", static.returncode == 0 and static_payload["status"] == "PASS", static_payload["boundary"])

    py_compile = run([sys.executable, "-m", "py_compile",
        "scripts/build_fvii_sci02_lab.py", "scripts/build_fvii_sci02_registry.py",
        "scripts/validate_fvii_sci02.py", "scripts/validate_fvii_sci02_lean_static.py",
        "scripts/build_fvii_sci02_reports.py",
        "formalization/foundations_vii_lab/fvii_lab/phase2.py",
        "formalization/foundations_vii_lab/tests/test_phase2_admission.py"])
    check("python_source_compilation", py_compile.returncode == 0, py_compile.stderr.strip() or "seven source files")

    shell_files = [p for p in [ROOT / "scripts" / "run_fvii_sci02_external_lean.sh", ROOT / "scripts" / "rebuild_fvii_sci02.sh"] if p.exists()]
    shell_ok = all(run(["bash", "-n", str(p.relative_to(ROOT))]).returncode == 0 for p in shell_files)
    check("shell_syntax", shell_ok, f"files={len(shell_files)}")

    # Deterministic regeneration.
    generated_paths = [
        LAB2 / "results" / "envelopes.jsonl",
        LAB2 / "results" / "partitions.json",
        LAB2 / "results" / "canonical_witnesses.jsonl",
        LAB2 / "results" / "no_go_controls.jsonl",
        LAB2 / "results" / "primary_fixture_replay.json",
        LAB2 / "results" / "summary.json",
        LAB2 / "witnesses",
        REG / "phase2_public_declarations.jsonl",
        REG / "phase2_theorem_catalog.jsonl",
        REG / "phase2_candidate_closure.jsonl",
        REG / "phase2_no_go_closure.jsonl",
        REG / "phase2_formalization_targets.jsonl",
        REG / "phase2_finite_envelopes.jsonl",
        REG / "phase2_summary.json",
        TRACE / "phase2_bounded_witnesses.jsonl",
        TRACE / "phase2_asset_trace.jsonl",
        TRACE / "phase2_statement_hashes.sha256",
        ROOT / "science" / "theorems",
        ROOT / "science" / "no_go",
        ROOT / "formalization" / "lean" / "FoundationsVII" / "Trust" / "PrintAxiomsPhase2.lean",
    ]
    before = fingerprint(generated_paths)
    regen_lab = run([sys.executable, "scripts/build_fvii_sci02_lab.py"])
    regen_registry = run([sys.executable, "scripts/build_fvii_sci02_registry.py"])
    after = fingerprint(generated_paths)
    check("deterministic_phase2_regeneration", regen_lab.returncode == 0 and regen_registry.returncode == 0 and before == after, f"sha256={after}")

    # Scope and immutability.
    immutable_changes = git_changed([
        "formalization/foundations_v_scaffold", "formalization/foundations_vi_scaffold",
        "formalization/_provenance", "formalization/lean/FoundationsVII/Core",
        "formalization/lean/FoundationsVII/Prior",
        "formalization/lean/FoundationsVII/Models/Finite/Scenarios.lean",
        "formalization/lean/FoundationsVII/Models/Finite/Countermodels.lean",
        "formalization/lean/FoundationsVII/Models/Finite/Regression.lean",
        "formalization/foundations_vii_lab/fixtures",
    ])
    check("phase1_and_inherited_immutability", not immutable_changes, f"changed={immutable_changes[:10]}")
    tex_changes = [p for p in git_changed(["."]) if p.endswith(".tex") or p.endswith(".bib")]
    check("no_paper_work", not tex_changes, f"changed={tex_changes}")
    later = any((ROOT / "formalization" / "lean" / "FoundationsVII" / name).exists() for name in ("Join", "Dynamics", "Corollaries"))
    check("phases_3_4_5_not_executed", not later, "no later science directories")

    # Lean boundary: nonblocking default, strict when requested.
    build_status = read_json(ROOT / "formalization" / "lean" / "BUILD_STATUS_PHASE2.json")
    lean_status = read_json(LAB2 / "results" / "lean_execution_status.json")
    cross_status = read_json(LAB2 / "results" / "cross_implementation_status.json")
    if args.require_lean_results:
        phase1_cross_path = LAB / "results" / "cross_implementation.json"
        phase2_cross_path = LAB2 / "results" / "cross_implementation.json"
        phase1_cross = read_json(phase1_cross_path) if phase1_cross_path.exists() else {}
        phase2_cross = read_json(phase2_cross_path) if phase2_cross_path.exists() else {}
        axioms = LAB2 / "results" / "lean_axioms.txt"
        lean_ok = (
            build_status.get("kernel_build_status") == "PASS"
            and lean_status.get("status") == "LEAN_BUILD_AXIOM_AND_DIFFERENTIAL_REPLAY_PASS"
            and cross_status.get("status") == "PASS"
            and phase1_cross.get("all_pass") is True
            and phase2_cross.get("all_pass") is True
            and axioms.is_file() and axioms.stat().st_size > 0
        )
        check("lean_kernel_and_differential_replay", lean_ok, "strict cumulative Phase1+Phase2 replay")
    else:
        lean_ok = (
            (build_status.get("kernel_build_status") == "PASS" and cross_status.get("status") == "PASS")
            or (
                build_status.get("kernel_build_status") == "NOT_RUN_LOCAL_ENVIRONMENT"
                and lean_status.get("authorization") == "USER_AUTHORIZED_EXTERNAL_REPLAY_DEFERRAL"
                and lean_status.get("blocking") is False
                and cross_status.get("status") == "PENDING_EXECUTED_LEAN_RESULTS"
            )
        )
        check("lean_boundary_truthfully_recorded", lean_ok, str(build_status.get("kernel_build_status")))

    all_ok = all(ok for _, ok, _ in checks)
    payload = {
        "phase": "FVII-SCI-02",
        "status": "PASS" if all_ok else "FAIL",
        "strict_lean_required": args.require_lean_results,
        "check_count": len(checks),
        "pass_count": sum(ok for _, ok, _ in checks),
        "phase2_declaration_count": len(declarations),
        "phase2_theorem_count": len(theorems),
        "candidate_count": len(candidates),
        "no_go_count": len(nogos),
        "finite_envelope_count": len(envelopes),
        "bounded_witness_count": len(witnesses),
        "python_test_count": test_count,
        "lean_kernel_status": build_status.get("kernel_build_status"),
        "checks": [
            {"name": name, "status": "PASS" if ok else "FAIL", "detail": detail}
            for name, ok, detail in checks
        ],
        "errors": errors,
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "FVII_SCI_02_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    text = [f"FVII-SCI-02 VALIDATION: {payload['status']}", f"Checks: {payload['pass_count']}/{payload['check_count']}"]
    text.extend(f"{'PASS' if ok else 'FAIL'} {name}: {detail}" for name, ok, detail in checks)
    if errors:
        text += ["", "ERRORS:", *errors]
    (REPORTS / "FVII_SCI_02_VALIDATION.txt").write_text("\n".join(text) + "\n", encoding="utf-8")
    md = ["# FVII-SCI-02 validation", "", f"**Status:** `{payload['status']}`  ", f"**Checks:** {payload['pass_count']}/{payload['check_count']}  ", f"**Lean kernel status:** `{payload['lean_kernel_status']}`", "", "| Check | Status | Detail |", "|---|---:|---|"]
    md.extend(f"| `{name}` | {'PASS' if ok else 'FAIL'} | {detail.replace('|', '/')} |" for name, ok, detail in checks)
    if errors:
        md += ["", "## Errors", "", *[f"- {error}" for error in errors]]
    (REPORTS / "FVII_SCI_02_VALIDATION.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"FVII-SCI-02 VALIDATION: {payload['status']} ({payload['pass_count']}/{payload['check_count']})")
    for name, ok, detail in checks:
        print(f" - {'PASS' if ok else 'FAIL'} {name}: {detail}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

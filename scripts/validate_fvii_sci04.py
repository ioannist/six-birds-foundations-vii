#!/usr/bin/env python3
"""Acceptance validator for FVII-SCI-04.

By default the owner-authorized external Lean replay may remain pending.  Pass
``--require-lean-results`` after an external kernel replay to require build,
axiom, and Python/Lean differential receipts.
"""
from __future__ import annotations

import argparse
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
LAB4 = LAB / "phase4"
REG = ROOT / "science" / "registry"
TRACE = ROOT / "science" / "traceability"
REPORTS = ROOT / "reports"
LEAN = ROOT / "formalization" / "lean"
BASE_TAG = "vii-science-03"

EXPECTED_CANDIDATES = {
    "VII-C012", "VII-C013", "VII-C014", "VII-C015", "VII-C017",
    "VII-C018", "VII-C027", "VII-C028", "VII-C032", "VII-C034",
}
EXPECTED_NOGOS = {"NGVII-10"}
EXPECTED_TARGETS = {"FT11", "FT12", "FT13", "FT14", "FT15", "FT16", "FT19", "FT20"}
EXPECTED_DECISIONS = {"DP07", "DP08", "DP09", "DP11", "DP12"}
EXPECTED_ENVELOPES = {f"P4-E{i:02d}" for i in range(1, 13)}
EXPECTED_WITNESSES = {f"P4-W{i:02d}" for i in range(1, 33)}
EXPECTED_SCENARIOS = {"TTW-S02", "TTW-S03", "TTW-S06", "TTW-S16", "TTW-S17", "TTW-S18", "TTW-S20", "TTW-S21", "TTW-S24"}
EXPECTED_COUNTERMODELS = {"CM-06", "CM-07", "CM-10", "CM-17", "CM-22", "CM-23", "CM-24", "CM-25"}


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    merged["PYTHONDONTWRITEBYTECODE"] = "1"
    merged["PYTHONPATH"] = str(LAB)
    if env:
        merged.update(env)
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, env=merged)


def fingerprint(paths: Iterable[Path]) -> str:
    digest = hashlib.sha256()
    expanded: list[Path] = []
    for path in paths:
        if path.is_dir():
            expanded.extend(p for p in path.rglob("*") if p.is_file())
        elif path.is_file():
            expanded.append(path)
        else:
            digest.update(f"MISSING\0{path.relative_to(ROOT).as_posix()}\n".encode())
    for path in sorted(set(expanded)):
        rel = path.relative_to(ROOT).as_posix()
        digest.update(rel.encode() + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def git_changed(paths: list[str]) -> list[str]:
    diff = run(["git", "diff", "--name-only", BASE_TAG, "--", *paths])
    untracked = run(["git", "ls-files", "--others", "--exclude-standard", "--", *paths])
    if diff.returncode != 0 or untracked.returncode != 0:
        return [f"GIT_ERROR:{diff.stderr.strip()}:{untracked.stderr.strip()}"]
    return sorted(set(diff.stdout.splitlines()) | set(untracked.stdout.splitlines()))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-lean-results", action="store_true")
    args = parser.parse_args()

    checks: list[dict[str, str]] = []
    errors: list[str] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})
        if not condition:
            errors.append(f"{name}: {detail}")

    required_files = [
        ROOT / "FVII_SCI_04_REPORT.md",
        REPORTS / "FVII_SCI_04_FORMAL_ASSETS.md",
        REPORTS / "FVII_SCI_04_FINITE_EVIDENCE.md",
        REPORTS / "FVII_SCI_04_ACCEPTANCE.md",
        LEAN / "BUILD_STATUS_PHASE4.json",
        LEAN / "EXTERNAL_COMPILE_PHASE4.md",
        ROOT / "scripts" / "run_fvii_sci04_external_lean.sh",
        ROOT / "scripts" / "rebuild_fvii_sci04.sh",
        ROOT / "scripts" / "validate_fvii_sci04_lean_static.py",
        ROOT / "scripts" / "validate_fvii_sci04.py",
        ROOT / "scripts" / "build_fvii_sci04_lab.py",
        ROOT / "scripts" / "build_fvii_sci04_registry.py",
        ROOT / "scripts" / "build_fvii_sci04_reports.py",
        LEAN / "FoundationsVII" / "Trust" / "PrintAxiomsPhase4.lean",
    ]
    check("release_surface_present", all(path.is_file() for path in required_files),
          f"files={len(required_files)}")

    manifest = read_json(ROOT / "science_plan" / "manifest.json")
    manifest_ok = (
        manifest.get("current_phase_tag") == "vii-science-04"
        and manifest.get("completed_phases") == ["FVII-SCI-01", "FVII-SCI-02", "FVII-SCI-03", "FVII-SCI-04"]
        and manifest.get("pending_phases") == ["FVII-SCI-05"]
        and str(manifest.get("status", "")).startswith("PHASE_04_EXECUTED")
        and manifest.get("paper_work_allowed") is False
        and manifest.get("phase4_kernel_status") in {
            "PENDING_EXTERNAL_REPLAY_USER_AUTHORIZED_NONBLOCKING", "PASS_EXTERNAL_REPLAY"
        }
    )
    check("science_plan_manifest_advanced", manifest_ok, str(manifest.get("status")))

    declarations = read_jsonl(REG / "phase4_public_declarations.jsonl")
    theorems = read_jsonl(REG / "phase4_theorem_catalog.jsonl")
    candidates = read_jsonl(REG / "phase4_candidate_closure.jsonl")
    no_gos = read_jsonl(REG / "phase4_no_go_closure.jsonl")
    targets = read_jsonl(REG / "phase4_formalization_targets.jsonl")
    decisions = read_jsonl(REG / "phase4_decision_closure.jsonl")
    envelopes = read_jsonl(REG / "phase4_finite_envelopes.jsonl")
    witnesses = read_jsonl(TRACE / "phase4_bounded_witnesses.jsonl")
    asset_trace = read_jsonl(TRACE / "phase4_asset_trace.jsonl")
    summary = read_json(REG / "phase4_summary.json")

    declaration_names = {str(row["fully_qualified_name"]) for row in declarations}
    theorem_names = {str(row["fully_qualified_name"]) for row in theorems}
    check("phase4_declaration_census", len(declarations) == 268 and len(declaration_names) == 268,
          f"declarations={len(declarations)}")
    check("phase4_theorem_census", len(theorems) == 135 and len(theorem_names) == 135,
          f"theorems={len(theorems)}")
    check("theorem_catalog_subset", theorem_names <= declaration_names,
          f"subset={len(theorem_names & declaration_names)}/{len(theorem_names)}")

    candidate_ids = {str(row["candidate_id"]) for row in candidates}
    candidate_ok = (
        candidate_ids == EXPECTED_CANDIDATES and len(candidates) == 10
        and all(str(row["phase4_status"]).startswith("TERMINAL_PHASE4_ASSET") for row in candidates)
        and all(int(row["theorem_count"]) == len(row["lean_theorems"]) > 0 for row in candidates)
        and all(set(map(str, row["lean_theorems"])) <= theorem_names for row in candidates)
        and all(row["bounded_witnesses"] and row["finite_envelopes"] and row["nonclaim"] for row in candidates)
    )
    check("ten_terminal_candidate_assets", candidate_ok, f"ids={sorted(candidate_ids)}")
    dossier_ok = all((ROOT / "science" / "theorems" / f"{candidate_id}.md").is_file() for candidate_id in EXPECTED_CANDIDATES)
    check("candidate_dossiers", dossier_ok, "10 theorem dossiers")

    nogo_ids = {str(row["no_go_id"]) for row in no_gos}
    nogo_ok = (
        nogo_ids == EXPECTED_NOGOS and len(no_gos) == 1
        and all(row["source_declarations_present"] is True for row in no_gos)
        and all(str(row["theorem"]) in theorem_names for row in no_gos)
        and all(set(map(str, row["escape_theorems"])) <= theorem_names for row in no_gos)
        and all(set(map(str, row["control_theorems"])) <= theorem_names for row in no_gos)
        and all(row["failure_scenarios"] and row["positive_controls"] and row["nonclaim"] for row in no_gos)
    )
    check("ngvii10_terminal_asset", nogo_ok, f"ids={sorted(nogo_ids)}")
    check("no_go_dossier", (ROOT / "science" / "no_go" / "NGVII-10.md").is_file(), "NGVII-10 dossier")

    target_ids = {str(row["target_id"]) for row in targets}
    expected_kernel = (
        "PASS_EXTERNAL_REPLAY"
        if read_json(LEAN / "BUILD_STATUS_PHASE4.json").get("kernel_build_status") == "PASS"
        else "PENDING_EXTERNAL_LEAN_REPLAY"
    )
    target_ok = (
        target_ids == EXPECTED_TARGETS and len(targets) == 8
        and all("CLOSED" in str(row["phase4_status"]) for row in targets)
        and all(str(row["kernel_status"]) == expected_kernel for row in targets)
        and all(row["phase4_theorems"] and set(map(str, row["phase4_theorems"])) <= theorem_names for row in targets)
        and all(row["candidate_ids"] for row in targets)
    )
    check("formalization_target_closure", target_ok, f"ids={sorted(target_ids)}")

    decision_ids = {str(row["decision_id"]) for row in decisions}
    decision_ok = (
        decision_ids == EXPECTED_DECISIONS and len(decisions) == 5
        and all(row["terminal"] is True and row["evidence_present"] is True for row in decisions)
        and all(row["phase4_terminal_ruling"] for row in decisions)
        and all(set(map(str, row["evidence_declarations"])) <= theorem_names for row in decisions)
    )
    check("five_terminal_decisions", decision_ok, f"ids={sorted(decision_ids)}")
    decision_docs = [ROOT / "science" / "decisions" / f"{decision_id}.md" for decision_id in EXPECTED_DECISIONS]
    decision_docs += [ROOT / "science" / "decisions" / "FVII-SCI-04-TERMINAL-DECISIONS.md"]
    check("decision_dossiers", all(path.is_file() for path in decision_docs), f"files={len(decision_docs)}")

    envelope_ids = {str(row["family_id"]) for row in envelopes}
    envelope_counts_ok = (
        envelope_ids == EXPECTED_ENVELOPES and len(envelopes) == 12
        and sum(int(row["raw_cardinality"]) for row in envelopes) == 55168
        and sum(int(row["canonical_cardinality"]) for row in envelopes) == 55168
        and sum(int(row["accepted_cardinality"]) for row in envelopes) == 14832
        and sum(int(row["rejected_cardinality"]) for row in envelopes) == 40336
        and all(int(row["accepted_cardinality"]) + int(row["rejected_cardinality"]) == int(row["canonical_cardinality"]) for row in envelopes)
    )
    check("twelve_finite_envelopes", envelope_counts_ok,
          "raw=canonical=55168 accepted=14832 rejected=40336")
    finite_nonclaims = all(
        row["nonclaim"]
        and row["python_grade"] == "EXECUTED_EXHAUSTIVE_DECLARED_FINITE_FAMILY"
        and row["lean_grade"] in {"SOURCE_COMPLETE_EXTERNAL_REPLAY_PENDING", "KERNEL_VERIFIED", "KERNEL_VERIFIED_EXTERNAL_REPLAY"}
        for row in envelopes
    )
    check("finite_evidence_grades_and_nonclaims", finite_nonclaims, "bounded scopes retained")

    witness_ids = {str(row["witness_id"]) for row in witnesses}
    witness_candidates = {str(row["candidate_id"]) for row in witnesses}
    witness_files_ok = True
    for row in witnesses:
        path = ROOT / str(row["path"])
        source_row = {key: value for key, value in row.items() if key not in {"path", "file_sha256"}}
        witness_files_ok &= path.is_file()
        if path.is_file():
            witness_files_ok &= read_json(path) == source_row
            witness_files_ok &= sha(path) == row["file_sha256"]
        witness_files_ok &= row["assignment_sha256"] == hashlib.sha256(canonical(row["assignment"])).hexdigest()
    check("thirty_two_canonical_witnesses", witness_ids == EXPECTED_WITNESSES and witness_candidates == EXPECTED_CANDIDATES and witness_files_ok,
          f"witnesses={len(witness_ids)}")

    lab_summary = read_json(LAB4 / "results" / "summary.json")
    replay = lab_summary["primary_fixture_replay"]
    replay_ok = (
        replay["all_pass"] is True
        and set(replay["scenario_ids"]) == EXPECTED_SCENARIOS
        and set(replay["countermodel_ids"]) == EXPECTED_COUNTERMODELS
        and replay["scenario_pass_count"] == 9
        and replay["countermodel_pass_count"] == 8
    )
    check("primary_fixture_python_replay", replay_ok, "9 scenarios and 8 countermodels pass")
    lab_counts_ok = (
        lab_summary["envelope_count"] == 12
        and lab_summary["raw_cases"] == 55168
        and lab_summary["canonical_cases"] == 55168
        and lab_summary["accepted_cases"] == 14832
        and lab_summary["rejected_cases"] == 40336
        and lab_summary["bounded_witness_count"] == 32
        and lab_summary["no_go_control_count"] == 1
    )
    check("phase4_lab_summary", lab_counts_ok, str(lab_summary.get("stage")))

    controls = read_jsonl(LAB4 / "results" / "no_go_controls.jsonl")
    check("one_finite_no_go_control", len(controls) == 1 and {str(row["no_go_id"]) for row in controls} == EXPECTED_NOGOS,
          f"rows={len(controls)}")

    summary_ok = (
        summary["terminal_candidate_count"] == 10
        and summary["no_go_count"] == 1
        and summary["formalization_target_count"] == 8
        and summary["terminal_decision_count"] == 5
        and summary["phase4_declaration_count"] == 268
        and summary["phase4_theorem_count"] == 135
        and summary["finite_envelope_count"] == 12
        and summary["bounded_witness_count"] == 32
        and summary["no_paper_work"] is True
    )
    check("phase4_registry_summary", summary_ok, str(summary.get("stage")))

    declaration_map = {str(row["fully_qualified_name"]): row for row in declarations}
    trace_ok = True
    for row in asset_trace:
        path = ROOT / str(row["path"])
        trace_ok &= path.is_file()
        if not path.is_file():
            continue
        if row["trace_kind"] == "FINITE_WITNESS":
            trace_ok &= sha(path) == row["sha256"]
        else:
            declaration = declaration_map.get(str(row["trace_id"]))
            trace_ok &= declaration is not None and declaration["source_block_sha256"] == row["sha256"]
    traced_candidates = {str(row["candidate_id"]) for row in asset_trace}
    check("asset_trace_closure", trace_ok and traced_candidates == EXPECTED_CANDIDATES,
          f"rows={len(asset_trace)}")

    statement_hash_lines = [
        line for line in (TRACE / "phase4_statement_hashes.sha256").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    check("statement_hash_ledger", len(statement_hash_lines) == 135 and len(set(statement_hash_lines)) == 135,
          f"rows={len(statement_hash_lines)}")

    tests = run([sys.executable, "-m", "unittest", "discover", "-s", "formalization/foundations_vii_lab/tests", "-p", "test*.py", "-v"])
    match = re.search(r"Ran\s+(\d+)\s+tests", tests.stderr + tests.stdout)
    test_count = int(match.group(1)) if match else 0
    check("python_protocol_and_model_tests", tests.returncode == 0 and test_count == 62,
          f"tests={test_count} returncode={tests.returncode}")

    static = run([sys.executable, "scripts/validate_fvii_sci04_lean_static.py"])
    static_payload = read_json(ROOT / "generated" / "fvii_sci04_static_lean_audit.json")
    check("static_lean_source_audit", static.returncode == 0 and static_payload["status"] == "PASS",
          static_payload["boundary"])

    python_sources = [
        "scripts/build_fvii_sci04_lab.py",
        "scripts/build_fvii_sci04_registry.py",
        "scripts/build_fvii_sci04_reports.py",
        "scripts/validate_fvii_sci04.py",
        "scripts/validate_fvii_sci04_lean_static.py",
        "formalization/foundations_vii_lab/fvii_lab/phase4.py",
        "formalization/foundations_vii_lab/tests/test_phase4_dynamics.py",
    ]
    py_compile = run([sys.executable, "-m", "py_compile", *python_sources])
    check("python_source_compilation", py_compile.returncode == 0,
          py_compile.stderr.strip() or f"files={len(python_sources)}")

    shell_files = [
        ROOT / "scripts" / "run_fvii_sci04_external_lean.sh",
        ROOT / "scripts" / "rebuild_fvii_sci04.sh",
    ]
    shell_ok = all(path.is_file() and run(["bash", "-n", str(path.relative_to(ROOT))]).returncode == 0 for path in shell_files)
    check("shell_syntax", shell_ok, f"files={len(shell_files)}")

    generated_paths = [
        LAB4 / "results" / "envelopes.jsonl",
        LAB4 / "results" / "canonical_witnesses.jsonl",
        LAB4 / "results" / "no_go_controls.jsonl",
        LAB4 / "results" / "primary_fixture_replay.json",
        LAB4 / "results" / "primary_scenario_results.jsonl",
        LAB4 / "results" / "primary_countermodel_results.jsonl",
        LAB4 / "results" / "summary.json",
        LAB4 / "witnesses",
        REG / "phase4_public_declarations.jsonl",
        REG / "phase4_theorem_catalog.jsonl",
        REG / "phase4_candidate_closure.jsonl",
        REG / "phase4_no_go_closure.jsonl",
        REG / "phase4_formalization_targets.jsonl",
        REG / "phase4_decision_closure.jsonl",
        REG / "phase4_finite_envelopes.jsonl",
        REG / "phase4_summary.json",
        TRACE / "phase4_bounded_witnesses.jsonl",
        TRACE / "phase4_asset_trace.jsonl",
        TRACE / "phase4_statement_hashes.sha256",
        *[ROOT / "science" / "theorems" / f"{candidate_id}.md" for candidate_id in EXPECTED_CANDIDATES],
        ROOT / "science" / "no_go" / "NGVII-10.md",
        *decision_docs,
        LEAN / "FoundationsVII" / "Trust" / "PrintAxiomsPhase4.lean",
    ]
    before = fingerprint(generated_paths)
    regen_lab = run([sys.executable, "scripts/build_fvii_sci04_lab.py"])
    regen_registry = run([sys.executable, "scripts/build_fvii_sci04_registry.py"])
    after = fingerprint(generated_paths)
    check("deterministic_phase4_regeneration",
          regen_lab.returncode == 0 and regen_registry.returncode == 0 and before == after,
          f"sha256={after}")

    build = read_json(LEAN / "BUILD_STATUS_PHASE4.json")
    if args.require_lean_results:
        lean_cross_path = LAB4 / "results" / "cross_implementation_status.json"
        lean_results_path = LAB4 / "results" / "lean_results.jsonl"
        axiom_path = LAB4 / "results" / "lean_axioms.txt"
        strict_ok = (
            build.get("kernel_build_status") == "PASS"
            and build.get("lean_available") is True
            and build.get("lake_available") is True
            and lean_cross_path.is_file() and read_json(lean_cross_path).get("all_pass") is True
            and lean_results_path.is_file() and len([x for x in lean_results_path.read_text().splitlines() if x.strip()]) == 29
            and axiom_path.is_file() and axiom_path.stat().st_size > 0
        )
        check("required_external_lean_replay", strict_ok, str(build.get("kernel_build_status")))
    else:
        lean_boundary_ok = build.get("kernel_build_status") in {"NOT_RUN_LOCAL_ENVIRONMENT", "PASS"}
        if build.get("kernel_build_status") == "NOT_RUN_LOCAL_ENVIRONMENT":
            lean_boundary_ok &= build.get("lean_available") is False and build.get("lake_available") is False
            lean_boundary_ok &= build.get("cross_implementation_status") == "PENDING_ACTUAL_LEAN_EXECUTION"
        check("owner_authorized_lean_boundary", lean_boundary_ok, str(build.get("kernel_build_status")))

    immutable_changes = git_changed([
        "formalization/foundations_v_scaffold",
        "formalization/foundations_vi_scaffold",
        "formalization/_provenance",
        "formalization/lean/FoundationsVII/Core",
        "formalization/lean/FoundationsVII/Prior",
        "formalization/lean/FoundationsVII/Access",
        "formalization/lean/FoundationsVII/Contact",
        "formalization/lean/FoundationsVII/Join",
        "formalization/lean/FoundationsVII/Residuals",
        "formalization/lean/FoundationsVII/NoGo/Admission.lean",
        "formalization/lean/FoundationsVII/NoGo/Join.lean",
        "formalization/lean/FoundationsVII/Models/Finite/Phase2",
        "formalization/lean/FoundationsVII/Models/Finite/Phase3",
        "formalization/foundations_vii_lab/fixtures",
        "formalization/foundations_vii_lab/phase2",
        "formalization/foundations_vii_lab/phase3",
        "formalization/foundations_vii_lab/fvii_lab/phase2.py",
        "formalization/foundations_vii_lab/fvii_lab/phase3.py",
    ])
    check("prior_science_and_imported_scaffolds_immutable", not immutable_changes,
          f"changed={immutable_changes[:12]}")

    repo_changes = git_changed(["."])
    paper_changes = [p for p in repo_changes if p.endswith((".tex", ".bib")) or p.startswith(("source/papers/", "paper/", "papers/"))]
    check("no_paper_work", not paper_changes, f"changed={paper_changes}")
    phase5_paths = [p for p in repo_changes if "Phase5" in p or "/Corollaries/" in p or p.startswith("science/corollaries/")]
    check("phase5_not_started", not phase5_paths and not (LEAN / "FoundationsVII" / "Corollaries").exists(),
          f"paths={phase5_paths}")
    check("obsolete_duplicate_envelope_absent",
          not (LEAN / "FoundationsVII" / "Models" / "Finite" / "Phase4" / "EnablementDynamicsEnvelope.lean").exists(),
          "single Phase-4 finite-envelope source")

    all_ok = not errors
    payload = {
        "phase": "FVII-SCI-04",
        "status": "PASS" if all_ok else "FAIL",
        "strict_lean_required": args.require_lean_results,
        "check_count": len(checks),
        "pass_count": sum(item["status"] == "PASS" for item in checks),
        "failure_count": sum(item["status"] == "FAIL" for item in checks),
        "checks": checks,
        "errors": errors,
        "counts": {
            "declarations": len(declarations),
            "theorems": len(theorems),
            "candidates": len(candidates),
            "no_gos": len(no_gos),
            "targets": len(targets),
            "decisions": len(decisions),
            "finite_envelopes": len(envelopes),
            "bounded_witnesses": len(witnesses),
            "python_tests": test_count,
        },
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "FVII_SCI_04_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    generated = ROOT / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    (generated / "fvii_sci04_validation.json").write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    (generated / "fvii_sci04_validation.txt").write_text(
        "\n".join(f"{item['status']}\t{item['name']}\t{item['detail']}" for item in checks) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "phase": payload["phase"], "status": payload["status"],
        "pass_count": payload["pass_count"], "check_count": payload["check_count"],
        "failure_count": payload["failure_count"], "errors": errors,
    }, ensure_ascii=False, sort_keys=True))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

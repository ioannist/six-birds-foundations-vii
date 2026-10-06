#!/usr/bin/env python3
"""Acceptance validator for FVII-SCI-03.

Default mode accepts the owner's explicit deferral of local Lean execution.
`--require-lean-results` requires a successful cumulative kernel build, the
Phase-1/2/3 finite differentials, and executed Phase-3 axiom capture.
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
LAB3 = LAB / "phase3"
REG = ROOT / "science" / "registry"
TRACE = ROOT / "science" / "traceability"
REPORTS = ROOT / "reports"
BASE_TAG = "vii-science-02"

EXPECTED_CANDIDATES = {
    "VII-C007", "VII-C008", "VII-C009", "VII-C010", "VII-C011",
    "VII-C016", "VII-C019", "VII-C026", "VII-C030", "VII-C031",
    "VII-C033", "VII-C035", "VII-C036",
}
EXPECTED_NOGOS = {"NGVII-02", "NGVII-06", "NGVII-07", "NGVII-08", "NGVII-09"}
EXPECTED_TARGETS = {"FT05", "FT06", "FT07", "FT08", "FT09", "FT10", "FT16", "FT18", "FT19", "FT20"}
EXPECTED_DECISIONS = {"DP01", "DP02", "DP03", "DP04", "DP05", "DP06", "DP10", "DP15"}
EXPECTED_SCENARIOS = {
    "TTW-S05", "TTW-S06", "TTW-S07", "TTW-S08", "TTW-S09", "TTW-S10",
    "TTW-S11", "TTW-S12", "TTW-S13", "TTW-S14", "TTW-S15", "TTW-S24",
}
EXPECTED_COUNTERMODELS = {
    "CM-01", "CM-02", "CM-03", "CM-04", "CM-05", "CM-13", "CM-14",
    "CM-15", "CM-16", "CM-21", "CM-22", "CM-25", "CM-26", "CM-27",
}
EXPECTED_ENVELOPES = {f"P3-E{i:02d}" for i in range(1, 12)}
EXPECTED_WITNESSES = {f"P3-W{i:02d}" for i in range(1, 28)}


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
            files.extend(
                item for item in path.rglob("*")
                if item.is_file() and "__pycache__" not in item.parts and item.suffix not in {".pyc", ".pyo"}
            )
    digest = hashlib.sha256()
    for path in sorted(set(files), key=lambda item: item.relative_to(ROOT).as_posix()):
        rel = path.relative_to(ROOT).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(rel).to_bytes(4, "big")); digest.update(rel)
        digest.update(len(data).to_bytes(8, "big")); digest.update(data)
    return digest.hexdigest()


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

    # Input identity and phase state.
    base = run(["git", "rev-parse", "--verify", BASE_TAG])
    check("phase2_base_tag", base.returncode == 0, base.stdout.strip() or base.stderr.strip())
    manifest = read_json(ROOT / "science_plan" / "manifest.json")
    plan_ok = (
        all(phase in manifest.get("completed_phases", []) for phase in ("FVII-SCI-01", "FVII-SCI-02", "FVII-SCI-03"))
        and manifest.get("current_phase_tag") == "vii-science-03"
        and manifest.get("pending_phases") == ["FVII-SCI-04", "FVII-SCI-05"]
        and manifest.get("status") in {
            "PHASE_03_EXECUTED_PHASES_04_TO_05_PENDING",
            "PHASE_03_EXECUTED_EXTERNAL_LEAN_REPLAY_PASS",
        }
        and manifest.get("paper_work_allowed") is False
    )
    check("science_plan_phase3_state", plan_ok, str(manifest.get("status")))

    # Machine-readable science surfaces.
    summary = read_json(REG / "phase3_summary.json")
    declarations = read_jsonl(REG / "phase3_public_declarations.jsonl")
    theorems = read_jsonl(REG / "phase3_theorem_catalog.jsonl")
    candidates = read_jsonl(REG / "phase3_candidate_closure.jsonl")
    nogos = read_jsonl(REG / "phase3_no_go_closure.jsonl")
    targets = read_jsonl(REG / "phase3_formalization_targets.jsonl")
    decisions = read_jsonl(REG / "phase3_decision_closure.jsonl")
    envelopes = read_jsonl(REG / "phase3_finite_envelopes.jsonl")
    witnesses = read_jsonl(TRACE / "phase3_bounded_witnesses.jsonl")
    asset_trace = read_jsonl(TRACE / "phase3_asset_trace.jsonl")

    declaration_names = [str(row["fully_qualified_name"]) for row in declarations]
    theorem_names = [str(row["fully_qualified_name"]) for row in theorems]
    check(
        "phase3_public_declaration_registry",
        len(declarations) == 363 and len(set(declaration_names)) == 363,
        f"rows={len(declarations)}",
    )
    check(
        "phase3_theorem_registry",
        len(theorems) == 183 and len(set(theorem_names)) == 183,
        f"rows={len(theorems)}",
    )
    check("theorem_registry_subset", set(theorem_names) <= set(declaration_names), "all theorem names are public declarations")
    check("stable_phase3_asset_ids", len({row["science_asset_id"] for row in declarations}) == len(declarations), f"rows={len(declarations)}")
    check(
        "source_statement_hashes",
        all(len(str(row["statement_sha256"])) == 64 and len(str(row["source_block_sha256"])) == 64 for row in declarations),
        "every declaration has statement and source-block hashes",
    )

    trust_kinds = {str(row["kind"]) for row in declarations if str(row["kind"]) in {"axiom", "opaque"}}
    check("no_source_level_trust_shortcuts", not trust_kinds, f"kinds={sorted(trust_kinds)}")

    candidate_ids = {str(row["candidate_id"]) for row in candidates}
    check("thirteen_terminal_candidates", candidate_ids == EXPECTED_CANDIDATES and len(candidates) == 13, f"ids={sorted(candidate_ids)}")
    candidate_grade_ok = all(
        str(row["phase3_status"]).startswith("TERMINAL_PHASE3_ASSET")
        and int(row["theorem_count"]) > 0
        and row["lean_theorems"]
        and row["nonclaim"]
        for row in candidates
    )
    check("candidate_terminal_grades_and_boundaries", candidate_grade_ok, "all terminal with theorem surface and nonclaim")
    candidate_controls_ok = all(
        row["bounded_witnesses"] or row["positive_scenarios"] or row["countermodels"] or row["lean_theorems"]
        for row in candidates
    )
    check("candidate_finite_or_structural_controls", candidate_controls_ok, "every candidate has a formal or bounded control")
    candidate_source_ok = all(
        int(row["source_support_count"]) > 0
        or int(row["source_boundary_count"]) > 0
        or int(row["source_open_count"]) > 0
        or row["source_bridge_ids"]
        or row["source_law_or_no_go_ids"]
        for row in candidates
    )
    check("candidate_source_trace_counts", candidate_source_ok, "every candidate retains Step-3 source support or boundary provenance")
    check(
        "candidate_dossiers",
        all((ROOT / "science" / "theorems" / f"{candidate_id}.md").is_file() for candidate_id in EXPECTED_CANDIDATES),
        "thirteen terminal dossiers",
    )

    nogo_ids = {str(row["no_go_id"]) for row in nogos}
    no_go_ok = all(
        bool(row["source_declarations_present"])
        and row["escape_theorems"]
        and row["failure_scenarios"]
        and row["positive_controls"]
        and str(row["terminal_status"]).startswith("PROVED_AT_DECLARED_STRUCTURAL_SCOPE")
        for row in nogos
    )
    check("five_no_go_fronts", nogo_ids == EXPECTED_NOGOS and len(nogos) == 5 and no_go_ok, f"ids={sorted(nogo_ids)}")
    check(
        "no_go_dossiers",
        all((ROOT / "science" / "no_go" / f"{no_go_id}.md").is_file() for no_go_id in EXPECTED_NOGOS),
        "five scoped dossiers",
    )

    target_ids = {str(row["target_id"]) for row in targets}
    ft18 = next(row for row in targets if row["target_id"] == "FT18")
    ft19 = next(row for row in targets if row["target_id"] == "FT19")
    ft20 = next(row for row in targets if row["target_id"] == "FT20")
    expected_registry_kernel = (
        "PASS_EXTERNAL_REPLAY"
        if read_json(ROOT / "formalization" / "lean" / "BUILD_STATUS_PHASE3.json").get("kernel_build_status") == "PASS"
        else "PENDING_EXTERNAL_LEAN_REPLAY"
    )
    target_ok = (
        target_ids == EXPECTED_TARGETS
        and all(row["phase3_theorems"] for row in targets)
        and all(str(row["kernel_status"]) == expected_registry_kernel for row in targets)
        and "ADMISSION_AND_JOIN_HALVES_COMPLETE" in str(ft18["phase3_status"])
        and "PARENT_RETENTION_PORTION_COMPLETE" in str(ft19["phase3_status"])
        and "JOIN_RESIDUAL_PORTION_COMPLETE" in str(ft20["phase3_status"])
    )
    check("formalization_target_closure", target_ok, f"ids={sorted(target_ids)}")

    decision_ids = {str(row["decision_id"]) for row in decisions}
    decision_ok = all(
        row["terminal"] is True
        and row["phase3_terminal_ruling"]
        and row["evidence_present"] is True
        and row["evidence_declarations"]
        for row in decisions
    )
    check("eight_terminal_scope_decisions", decision_ids == EXPECTED_DECISIONS and len(decisions) == 8 and decision_ok, f"ids={sorted(decision_ids)}")
    check(
        "decision_dossier",
        (ROOT / "science" / "decisions" / "FVII-SCI-03-TERMINAL-DECISIONS.md").is_file(),
        "terminal rulings collected",
    )

    envelope_ids = {str(row["family_id"]) for row in envelopes}
    envelope_counts_ok = (
        envelope_ids == EXPECTED_ENVELOPES
        and len(envelopes) == 11
        and sum(int(row["raw_cardinality"]) for row in envelopes) == 141112
        and sum(int(row["canonical_cardinality"]) for row in envelopes) == 73528
        and sum(int(row["accepted_cardinality"]) for row in envelopes) == 34532
        and sum(int(row["rejected_cardinality"]) for row in envelopes) == 38996
        and all(
            int(row["accepted_cardinality"]) + int(row["rejected_cardinality"]) == int(row["canonical_cardinality"])
            for row in envelopes
        )
    )
    check(
        "eleven_finite_envelopes",
        envelope_counts_ok,
        "raw=141112 canonical=73528 accepted=34532 rejected=38996",
    )

    finite_nonclaims_ok = all(
        row["nonclaim"]
        and row["python_grade"] == "EXECUTED_EXHAUSTIVE_DECLARED_FINITE_FAMILY"
        and row["lean_grade"] == "SOURCE_COMPLETE_EXTERNAL_REPLAY_PENDING"
        for row in envelopes
    )
    check("finite_envelope_nonclaims", finite_nonclaims_ok, "bounded evidence grades and nonclaims retained")

    witness_ids = {str(row["witness_id"]) for row in witnesses}
    witness_files_ok = True
    for row in witnesses:
        path = LAB3 / "witnesses" / f"{row['witness_id']}.json"
        source_row = {key: value for key, value in row.items() if key not in {"path", "file_sha256"}}
        witness_files_ok &= path.is_file() and read_json(path) == source_row
        witness_files_ok &= row["path"] == path.relative_to(ROOT).as_posix()
        witness_files_ok &= row["assignment_sha256"] == hashlib.sha256(canonical(row["assignment"])).hexdigest()
        witness_files_ok &= row["file_sha256"] == sha(path)
    check("twenty_seven_canonical_witnesses", witness_ids == EXPECTED_WITNESSES and witness_files_ok, f"ids={len(witness_ids)}")

    lab_summary = read_json(LAB3 / "results" / "summary.json")
    replay = lab_summary["primary_fixture_replay"]
    replay_ok = (
        replay["all_pass"] is True
        and set(replay["scenario_ids"]) == EXPECTED_SCENARIOS
        and set(replay["countermodel_ids"]) == EXPECTED_COUNTERMODELS
        and replay["scenario_pass_count"] == 12
        and replay["countermodel_pass_count"] == 14
    )
    check("primary_fixture_python_replay", replay_ok, "12 scenarios and 14 countermodels pass")
    summary_ok = (
        summary["terminal_candidate_count"] == 13
        and summary["no_go_count"] == 5
        and summary["formalization_target_count"] == 10
        and summary["terminal_decision_count"] == 8
        and summary["phase3_theorem_count"] == 183
        and summary["finite_envelope_count"] == 11
        and summary["bounded_witness_count"] == 27
        and summary["no_paper_work"] is True
    )
    check("phase3_summary_closure", summary_ok, str(summary.get("stage")))

    sys.path.insert(0, str(LAB))
    from fvii_lab.phase3 import status_partitions  # imported only for deterministic finite census
    partition_counts = {name: len(rows) for name, rows in status_partitions().items()}
    expected_partition_counts = {
        "NO_EVIDENCED_CONTACT": 4,
        "EVIDENCED_CONTACT": 4,
        "COMMON_REFINEMENT": 8,
        "LAWFUL_COMPOSITE": 64,
        "STRICT_JOIN": 2,
        "OBSTRUCTED": 80,
        "CERTIFIED_NONINTERACTION": 8,
    }
    check("seven_status_partition_counts", partition_counts == expected_partition_counts, str(partition_counts))

    # Trace closure and hash receipts.
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
    check("asset_trace_closure", trace_ok and traced_candidates == EXPECTED_CANDIDATES, f"rows={len(asset_trace)}")

    statement_hash_lines = [
        line for line in (TRACE / "phase3_statement_hashes.sha256").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    check("statement_hash_ledger", len(statement_hash_lines) == 183 and len(set(statement_hash_lines)) == 183, f"rows={len(statement_hash_lines)}")

    controls = read_jsonl(LAB3 / "results" / "no_go_controls.jsonl")
    check(
        "five_finite_no_go_controls",
        len(controls) == 5 and {str(row["no_go_id"]) for row in controls} == EXPECTED_NOGOS,
        f"rows={len(controls)}",
    )

    # Executed Python and static Lean audits.
    tests = run([sys.executable, "-m", "unittest", "discover", "-s", "formalization/foundations_vii_lab/tests", "-v"])
    match = re.search(r"Ran\s+(\d+)\s+tests", tests.stderr + tests.stdout)
    test_count = int(match.group(1)) if match else 0
    check("python_protocol_and_model_tests", tests.returncode == 0 and test_count == 48, f"tests={test_count} returncode={tests.returncode}")

    static = run([sys.executable, "scripts/validate_fvii_sci03_lean_static.py"])
    static_payload = read_json(ROOT / "generated" / "fvii_sci03_static_lean_audit.json")
    check("static_lean_source_audit", static.returncode == 0 and static_payload["status"] == "PASS", static_payload["boundary"])

    python_sources = [
        "scripts/build_fvii_sci03_lab.py",
        "scripts/build_fvii_sci03_registry.py",
        "scripts/build_fvii_sci03_reports.py",
        "scripts/validate_fvii_sci03.py",
        "scripts/validate_fvii_sci03_lean_static.py",
        "formalization/foundations_vii_lab/fvii_lab/phase3.py",
        "formalization/foundations_vii_lab/tests/test_phase3_join.py",
    ]
    py_compile = run([sys.executable, "-m", "py_compile", *python_sources])
    check("python_source_compilation", py_compile.returncode == 0, py_compile.stderr.strip() or f"files={len(python_sources)}")

    shell_files = [
        ROOT / "scripts" / "run_fvii_sci03_external_lean.sh",
        ROOT / "scripts" / "rebuild_fvii_sci03.sh",
    ]
    shell_ok = all(path.is_file() and run(["bash", "-n", str(path.relative_to(ROOT))]).returncode == 0 for path in shell_files)
    check("shell_syntax", shell_ok, f"files={len(shell_files)}")

    # Deterministic regeneration of all primary Phase-3 machine products.
    generated_paths = [
        LAB3 / "results" / "envelopes.jsonl",
        LAB3 / "results" / "partitions.json",
        LAB3 / "results" / "canonical_witnesses.jsonl",
        LAB3 / "results" / "no_go_controls.jsonl",
        LAB3 / "results" / "primary_fixture_replay.json",
        LAB3 / "results" / "primary_scenario_results.jsonl",
        LAB3 / "results" / "primary_countermodel_results.jsonl",
        LAB3 / "results" / "summary.json",
        LAB3 / "witnesses",
        REG / "phase3_public_declarations.jsonl",
        REG / "phase3_theorem_catalog.jsonl",
        REG / "phase3_candidate_closure.jsonl",
        REG / "phase3_no_go_closure.jsonl",
        REG / "phase3_formalization_targets.jsonl",
        REG / "phase3_decision_closure.jsonl",
        REG / "phase3_finite_envelopes.jsonl",
        REG / "phase3_summary.json",
        TRACE / "phase3_bounded_witnesses.jsonl",
        TRACE / "phase3_asset_trace.jsonl",
        TRACE / "phase3_statement_hashes.sha256",
        ROOT / "science" / "theorems",
        ROOT / "science" / "no_go",
        ROOT / "science" / "decisions",
        ROOT / "formalization" / "lean" / "FoundationsVII" / "Trust" / "PrintAxiomsPhase3.lean",
    ]
    before = fingerprint(generated_paths)
    regen_lab = run([sys.executable, "scripts/build_fvii_sci03_lab.py"])
    regen_registry = run([sys.executable, "scripts/build_fvii_sci03_registry.py"])
    after = fingerprint(generated_paths)
    check(
        "deterministic_phase3_regeneration",
        regen_lab.returncode == 0 and regen_registry.returncode == 0 and before == after,
        f"sha256={after}",
    )

    # Scope, immutability, and absence of paper/later-phase work.
    immutable_changes = git_changed([
        "formalization/foundations_v_scaffold",
        "formalization/foundations_vi_scaffold",
        "formalization/_provenance",
        "formalization/lean/FoundationsVII/Core",
        "formalization/lean/FoundationsVII/Prior",
        "formalization/lean/FoundationsVII/Access",
        "formalization/lean/FoundationsVII/Models/Finite/Phase2",
        "formalization/foundations_vii_lab/fixtures",
        "formalization/foundations_vii_lab/fvii_lab/phase2.py",
    ])
    check("phase2_and_inherited_immutability", not immutable_changes, f"changed={immutable_changes[:10]}")
    tex_changes = [path for path in git_changed(["."]) if path.endswith(".tex") or path.endswith(".bib")]
    check("no_paper_work", not tex_changes, f"changed={tex_changes}")
    later = any((ROOT / "formalization" / "lean" / "FoundationsVII" / name).exists() for name in ("Enablement", "Dynamics", "Corollaries"))
    check("phases_4_and_5_not_executed", not later, "no later science directories")

    # Lean boundary: nonblocking by default, strict on demand.
    build_status = read_json(ROOT / "formalization" / "lean" / "BUILD_STATUS_PHASE3.json")
    lean_status = read_json(LAB3 / "results" / "lean_execution_status.json")
    cross_status = read_json(LAB3 / "results" / "cross_implementation_status.json")
    if args.require_lean_results:
        phase1_cross_path = LAB / "results" / "cross_implementation.json"
        phase2_cross_path = LAB / "phase2" / "results" / "cross_implementation.json"
        phase3_cross_path = LAB3 / "results" / "cross_implementation.json"
        phase1_cross = read_json(phase1_cross_path) if phase1_cross_path.exists() else {}
        phase2_cross = read_json(phase2_cross_path) if phase2_cross_path.exists() else {}
        phase3_cross = read_json(phase3_cross_path) if phase3_cross_path.exists() else {}
        axioms = LAB3 / "results" / "lean_axioms.txt"
        lean_ok = (
            build_status.get("kernel_build_status") == "PASS"
            and lean_status.get("status") == "LEAN_BUILD_AXIOM_AND_DIFFERENTIAL_REPLAY_PASS"
            and cross_status.get("status") == "PASS"
            and phase1_cross.get("all_pass") is True
            and phase2_cross.get("all_pass") is True
            and phase3_cross.get("all_pass") is True
            and axioms.is_file() and axioms.stat().st_size > 0
        )
        check("lean_kernel_and_differential_replay", lean_ok, "strict cumulative Phase1+Phase2+Phase3 replay")
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
        "phase": "FVII-SCI-03",
        "status": "PASS" if all_ok else "FAIL",
        "strict_lean_required": args.require_lean_results,
        "check_count": len(checks),
        "pass_count": sum(ok for _, ok, _ in checks),
        "phase3_declaration_count": len(declarations),
        "phase3_theorem_count": len(theorems),
        "candidate_count": len(candidates),
        "no_go_count": len(nogos),
        "formalization_target_count": len(targets),
        "terminal_decision_count": len(decisions),
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
    (REPORTS / "FVII_SCI_03_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    text = [
        f"FVII-SCI-03 VALIDATION: {payload['status']}",
        f"Checks: {payload['pass_count']}/{payload['check_count']}",
    ]
    text.extend(f"{'PASS' if ok else 'FAIL'} {name}: {detail}" for name, ok, detail in checks)
    if errors:
        text += ["", "ERRORS:", *errors]
    (REPORTS / "FVII_SCI_03_VALIDATION.txt").write_text("\n".join(text) + "\n", encoding="utf-8")

    markdown = [
        "# FVII-SCI-03 validation",
        "",
        f"- **Status:** `{payload['status']}`",
        f"- **Checks:** {payload['pass_count']}/{payload['check_count']}",
        f"- **Lean kernel status:** `{payload['lean_kernel_status']}`",
        "",
        "| Check | Status | Detail |",
        "|---|---:|---|",
    ]
    markdown.extend(
        f"| `{name}` | {'PASS' if ok else 'FAIL'} | {detail.replace('|', '/')} |"
        for name, ok, detail in checks
    )
    if errors:
        markdown += ["", "## Errors", "", *[f"- {error}" for error in errors]]
    (REPORTS / "FVII_SCI_03_VALIDATION.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")

    generated_dir = ROOT / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)
    (generated_dir / "fvii_sci03_validation.json").write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    (generated_dir / "fvii_sci03_validation.txt").write_text("\n".join(text) + "\n", encoding="utf-8")

    print(f"FVII-SCI-03 VALIDATION: {payload['status']} ({payload['pass_count']}/{payload['check_count']})")
    for name, ok, detail in checks:
        print(f" - {'PASS' if ok else 'FAIL'} {name}: {detail}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

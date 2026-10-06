#!/usr/bin/env python3
"""Acceptance validator for FVII-SCI-01.

Default mode accepts the user's explicit authorization to defer local Lean
execution when Lean/Lake are unavailable.  `--require-lean-results` upgrades
that environmental gate and requires a successful external kernel build,
`#print axioms` replay, and 51-row Python/Lean differential agreement.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "formalization" / "foundations_vii_lab"
REG = ROOT / "science" / "registry"
TRACE = ROOT / "science" / "traceability"
REPORT_TXT = ROOT / "reports" / "FVII_SCI_01_VALIDATION.txt"
REPORT_JSON = ROOT / "reports" / "FVII_SCI_01_VALIDATION.json"
REPORT_MD = ROOT / "reports" / "FVII_SCI_01_VALIDATION.md"
BASE_TAG = "vii-science-plan-v1"
TERMINAL = {"VII-C020", "VII-C023", "VII-C024", "VII-C025"}
EXPECTED_SECTIONS = {
    "domain_state", "admission_transition", "prospective_commitment",
    "source_ledger", "budget_ledger", "contact_surface", "contact_witness",
    "interaction_record", "join_candidate", "join_certificate",
    "join_obstruction", "noninteraction_certificate", "enablement_record",
    "reachability_witness", "observer_occupancy_record", "audit_record",
}


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def run(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    child_env = os.environ.copy()
    if env:
        child_env.update(env)
    child_env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(command, cwd=ROOT, env=child_env, text=True, capture_output=True, check=False)


def tree_fingerprint(paths: Iterable[Path]) -> str:
    h = hashlib.sha256()
    files: list[Path] = []
    for path in paths:
        if path.is_file():
            files.append(path)
        elif path.exists():
            files.extend(p for p in path.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
    for path in sorted(set(files), key=lambda p: p.relative_to(ROOT).as_posix()):
        rel = path.relative_to(ROOT).as_posix().encode("utf-8")
        h.update(len(rel).to_bytes(4, "big"))
        h.update(rel)
        data = path.read_bytes()
        h.update(len(data).to_bytes(8, "big"))
        h.update(data)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-lean-results", action="store_true")
    args = parser.parse_args()

    checks: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append((name, bool(condition), detail))

    # Machine-readable core registries.
    objects = read_jsonl(REG / "phase1_objects.jsonl")
    targets = read_jsonl(REG / "phase1_formalization_targets.jsonl")
    adapters = read_jsonl(REG / "inherited_adapter_ledger.jsonl")
    candidates = read_jsonl(REG / "phase1_candidate_closure.jsonl")
    decisions = read_jsonl(REG / "phase1_decision_rulings.jsonl")
    declarations = read_jsonl(REG / "phase1_public_declarations.jsonl")
    trust = read_jsonl(TRACE / "phase1_trust_surface.jsonl")

    check("object_registry", len(objects) == 18 and {r["object_id"] for r in objects} == {f"VII-O{i:02d}" for i in range(1, 19)}, f"rows={len(objects)}")
    check("fifteen_vii_owned_types", sum(r["step3_status"] != "INHERITED" for r in objects) == 15, "O04-O18")
    audit_object = next(r for r in objects if r["object_id"] == "VII-O03")
    check(
        "audit_anchor_and_local_representation",
        audit_object.get("lean_declaration") == "FoundationsVII.Prior.auditRecordAnchor"
        and audit_object.get("local_representation") == "FoundationsVII.AuditRecord",
        "inherited audit role anchored separately from the VII append-only representation",
    )
    check("formalization_target_registry", len(targets) == 20 and {r["target_id"] for r in targets} == {f"FT{i:02d}" for i in range(1, 21)}, f"rows={len(targets)}")
    check("adapter_ledger", len(adapters) == 30 and all(r["source_declaration_found"] for r in adapters), f"rows={len(adapters)}")
    check("adapter_target_coverage", {r["target_id"] for r in adapters} == {f"FT{i:02d}" for i in range(1, 21)}, "FT01-FT20")
    check("candidate_registry", len(candidates) == 36 and {r["candidate_id"] for r in candidates} == {f"VII-C{i:03d}" for i in range(1, 37)}, f"rows={len(candidates)}")
    terminal_rows = [r for r in candidates if r["candidate_id"] in TERMINAL]
    support_rows = [r for r in candidates if r["candidate_id"] not in TERMINAL]
    check("terminal_candidate_partition", len(terminal_rows) == 4 and all(r["phase1_terminal_status"].startswith("TERMINAL_PHASE1") for r in terminal_rows), "C020/C023/C024/C025")
    check("later_candidate_nonexecution", len(support_rows) == 32 and all("TYPED_SUPPORT_ONLY" in r["phase1_terminal_status"] for r in support_rows), f"support_rows={len(support_rows)}")
    check("terminal_declaration_trace", all(not r["missing_source_declarations"] for r in terminal_rows), "no missing terminal source declarations")
    protocols_text = (ROOT / "formalization" / "lean" / "FoundationsVII" / "Core" / "Protocols.lean").read_text(encoding="utf-8")
    detector_text = (ROOT / "formalization" / "lean" / "FoundationsVII" / "Models" / "Finite" / "Detector.lean").read_text(encoding="utf-8")
    protocol_tokens = [
        "decide (BridgeContract.WellFormed bridge)",
        "accepted_wellFormed_bridge_is_licensed",
        "incomplete_bridge_is_not_licensed",
        "point_null_does_not_license_unrestricted",
        "exhaustive_finite_does_not_license_unrestricted",
        "theorem_impossibility_licenses_under_unrestricted_declared_scope",
        "corollary_grade_requires_formal_declaration",
        "external_finite_evidence_does_not_upgrade_to_corollary",
        "lean_finite_evidence_does_not_upgrade_to_corollary",
        "falseNegativeCost < contract.falsePositiveCost",
        "listedInFrozen contract contract.sameSourceControls = true",
        "phase1_detector_false_positive_cost_exceeds_false_negative",
    ]
    missing_protocol_tokens = [token for token in protocol_tokens if token not in protocols_text + "\n" + detector_text]
    check("terminal_protocol_strength", not missing_protocol_tokens, f"missing={missing_protocol_tokens}")
    check("decision_registry", len(decisions) == 15 and all(r["working_ruling_status"] == "FROZEN_IN_PHASE1" for r in decisions), f"rows={len(decisions)}")
    check("decision_non_silent_resolution", all(r["terminal_resolution_phase"] for r in decisions), "all decisions retain a terminal phase")
    check("public_declaration_registry", len(declarations) >= 400 and len({r["fully_qualified_name"] for r in declarations}) == len(declarations), f"rows={len(declarations)}")
    asset_ids = [r.get("science_asset_id", "") for r in declarations]
    asset_id_ok = (
        len(set(asset_ids)) == len(asset_ids)
        and all(
            asset_id.startswith("FVII-THM-") if row["kind"] in {"theorem", "lemma", "corollary"}
            else asset_id.startswith("FVII-DEF-")
            for row, asset_id in zip(declarations, asset_ids)
        )
    )
    check("stable_science_asset_ids", asset_id_ok, f"unique={len(set(asset_ids))} rows={len(asset_ids)}")
    check("vii_owned_trust_surface", sum(r["ownership"] == "FVII_SCI_01" and str(r["status"]).startswith("FAIL") for r in trust) == 0, "no new VII axiom/opaque")
    check("inherited_trust_explicit", sum(r["ownership"] == "INHERITED" for r in trust) == 6, "one inherited axiom plus five opaque constants")

    # Fixtures and lossless migration from the Step-3 frozen inputs.
    scenario_source = {r["scenario_id"]: r for r in read_jsonl(ROOT / "readiness" / "two_theory_world" / "scenarios.jsonl")}
    counter_source = {r["countermodel_id"]: r for r in read_jsonl(ROOT / "readiness" / "countermodel_atlas.jsonl")}
    scenario_paths = sorted((LAB / "fixtures" / "scenarios").glob("*.json"))
    counter_paths = sorted((LAB / "fixtures" / "countermodels").glob("*.json"))
    scenarios = {p.stem: read_json(p) for p in scenario_paths}
    counters = {p.stem: read_json(p) for p in counter_paths}
    check("fixture_census", len(scenarios) == 24 and len(counters) == 27, f"scenarios={len(scenarios)} countermodels={len(counters)}")
    check("fixture_ids", set(scenarios) == {f"TTW-S{i:02d}" for i in range(1, 25)} and set(counters) == {f"CM-{i:02d}" for i in range(1, 28)}, "complete frozen IDs")
    migration_ok = True
    structural_ok = True
    canonical_ok = True
    for sid, fixture in scenarios.items():
        source = scenario_source[sid]
        migration_ok &= (
            fixture["name"] == source["name"]
            and fixture["expected_status"] == source["expected_status"]
            and fixture["assertions"] == {k: bool(v) for k, v in sorted(source["assertions"].items())}
            and fixture["candidate_ids"] == sorted(source["candidate_ids"])
            and fixture["falsifier"] == source["falsifier"]
            and all(fixture["flags"].get(k, False) == bool(source.get("flags", {}).get(k, False)) for k in fixture["flags"])
        )
        structural_ok &= set(fixture["structural_record"]) == EXPECTED_SECTIONS
        canonical_ok &= (LAB / "fixtures" / "scenarios" / f"{sid}.json").read_bytes() == canonical(fixture)
    for cid, fixture in counters.items():
        source = counter_source[cid]
        migration_ok &= (
            fixture["name"] == source["name"]
            and fixture["scenario_id"] == source["scenario_id"]
            and fixture["shows"] == source["shows"]
            and fixture["candidate_ids"] == sorted(source["candidate_ids"])
            and fixture["escape_route"] == source["escape_route"]
        )
        canonical_ok &= (LAB / "fixtures" / "countermodels" / f"{cid}.json").read_bytes() == canonical(fixture)
    check("lossless_step3_migration", migration_ok, "flags, expectations, assertions, traces")
    check("typed_fixture_sections", structural_ok, "15 VII-owned records plus append-only audit")
    check("canonical_fixture_bytes", canonical_ok, "sorted compact UTF-8 plus trailing newline")
    scenario_schema = read_json(LAB / "schemas" / "scenario.schema.json")
    countermodel_schema = read_json(LAB / "schemas" / "countermodel.schema.json")
    schema_closed = (
        scenario_schema.get("additionalProperties") is False
        and countermodel_schema.get("additionalProperties") is False
        and scenario_schema.get("properties", {}).get("structural_record", {}).get("additionalProperties") is False
        and scenario_schema.get("properties", {}).get("flags", {}).get("additionalProperties") is False
        and set(scenario_schema.get("properties", {}).get("flags", {}).get("required", []))
            == set(scenarios[next(iter(scenarios))]["flags"])
    )
    check("closed_fixture_schemas", schema_closed, "root, flags, structural records, and countermodels reject undeclared fields")

    manifest = read_json(LAB / "fixtures" / "manifest.json")
    manifest_hash_ok = all(sha(LAB / row["path"]) == row["sha256"] for row in manifest["fixtures"])
    check("fixture_manifest_hashes", manifest_hash_ok and len(manifest["fixtures"]) == 51, f"rows={len(manifest['fixtures'])}")
    scenario_hashes = {sid: sha(LAB / "fixtures" / "scenarios" / f"{sid}.json") for sid in scenarios}
    check("countermodel_scenario_hashes", all(fixture["scenario_sha256"] == scenario_hashes[fixture["scenario_id"]] for fixture in counters.values()), "27/27")

    # Runtime Python evidence.
    env = os.environ.copy()
    env["PYTHONPATH"] = str(LAB)
    tests = run([sys.executable, "-m", "unittest", "discover", "-s", str(LAB / "tests"), "-v"], env=env)
    test_output = tests.stderr + tests.stdout
    test_match = re.search(r"Ran (\d+) tests?", test_output)
    test_count = int(test_match.group(1)) if test_match else 0
    check("python_unit_tests", tests.returncode == 0 and test_count >= 25, f"{test_count} tests")
    evaluator = run([sys.executable, "-m", "fvii_lab.cli", "run", "--output", str(LAB / "results")], env=env)
    py_summary = read_json(LAB / "results" / "python_summary.json")
    check("python_reference_world", evaluator.returncode == 0 and py_summary["scenario_pass_count"] == 24 and py_summary["countermodel_pass_count"] == 27 and py_summary["all_pass"], "24/24 scenarios; 27/27 countermodels")
    statuses = {row["observed_status"] for row in read_jsonl(LAB / "results" / "python_scenario_results.jsonl")}
    check("twenty_four_reached_statuses", len(statuses) == 24, f"distinct={len(statuses)}")

    # Generated surfaces must rebuild byte-identically.
    generated_paths = [
        LAB / "fixtures", LAB / "schemas",
        ROOT / "formalization" / "lean" / "FoundationsVII" / "Models" / "Finite" / "Scenarios.lean",
        ROOT / "formalization" / "lean" / "FoundationsVII" / "Models" / "Finite" / "Countermodels.lean",
        ROOT / "formalization" / "lean" / "FoundationsVII" / "Prior",
        REG, TRACE, ROOT / "formalization" / "lean" / "FoundationsVII" / "Trust",
    ]
    before = tree_fingerprint(generated_paths)
    generators = [
        [sys.executable, "scripts/build_fvii_sci01_fixtures.py"],
        [sys.executable, "scripts/build_fvii_sci01_lean_fixtures.py"],
        [sys.executable, "scripts/build_fvii_sci01_adapters.py"],
        [sys.executable, "scripts/build_fvii_sci01_registry.py"],
    ]
    generator_ok = True
    for command in generators:
        result = run(command)
        generator_ok &= result.returncode == 0
    after = tree_fingerprint(generated_paths)
    check("deterministic_generators", generator_ok and before == after, f"fingerprint={after[:16]}")

    # Static Lean and source hygiene.
    static = run([sys.executable, "scripts/validate_fvii_sci01_lean_static.py"])
    check("lean_static_validation", static.returncode == 0, "imports, lexical structure, declarations, scope")
    python_sources = sorted((ROOT / "scripts").glob("*.py")) + sorted((LAB / "fvii_lab").glob("*.py")) + sorted((LAB / "tests").glob("*.py"))
    syntax_errors = []
    for source in python_sources:
        try:
            compile(source.read_text(encoding="utf-8"), str(source), "exec")
        except SyntaxError as exc:
            syntax_errors.append(f"{source.relative_to(ROOT)}:{exc.lineno}:{exc.msg}")
    check("python_syntax", not syntax_errors, f"files={len(python_sources)} errors={syntax_errors[:4]}")
    shell_files = ["scripts/rebuild_fvii_sci01.sh", "scripts/run_fvii_sci01_external_lean.sh"]
    shell_ok = all(run(["bash", "-n", path]).returncode == 0 for path in shell_files)
    check("shell_syntax", shell_ok, ", ".join(shell_files))

    immutable = run(["git", "diff", "--quiet", BASE_TAG, "--", "formalization/foundations_v_scaffold", "formalization/foundations_vi_scaffold"])
    check("imported_scaffolds_immutable", immutable.returncode == 0, "Foundations V/VI byte surfaces unchanged from plan tag")
    tex_diff = run(["git", "diff", "--name-only", BASE_TAG, "--", "*.tex"])
    untracked_tex = run(["git", "ls-files", "--others", "--exclude-standard", "--", "*.tex"])
    check(
        "no_paper_writing",
        tex_diff.returncode == 0 and untracked_tex.returncode == 0
        and not tex_diff.stdout.strip() and not untracked_tex.stdout.strip(),
        "no tracked or untracked TeX changed or added",
    )
    phase2_dirs = [ROOT / "formalization" / "lean" / "FoundationsVII" / name for name in ("Access", "Join", "Dynamics", "NoGo", "Corollaries")]
    check("no_later_phase_modules", not any(path.exists() for path in phase2_dirs), "Phase 2-4 science not executed")
    check("external_replay_instructions", (ROOT / "formalization" / "lean" / "EXTERNAL_COMPILE.md").exists() and (ROOT / "scripts" / "run_fvii_sci01_external_lean.sh").exists(), "directions and executable script")

    transient_paths: list[str] = []
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_dir() and path.name in {"__pycache__", ".lake"}:
            transient_paths.append(path.relative_to(ROOT).as_posix() + "/")
        elif path.is_file() and (path.suffix in {".pyc", ".olean", ".ilean"} or path.name.endswith(".trace")):
            transient_paths.append(path.relative_to(ROOT).as_posix())
    check("transient_artifacts_absent", not transient_paths, f"found={transient_paths[:8]}")

    # Lean execution gate: default is the explicit, nonblocking user-authorized deferral.
    lean_status = read_json(LAB / "results" / "lean_execution_status.json")
    if args.require_lean_results:
        lean_results_path = LAB / "results" / "lean_results.jsonl"
        cross_path = LAB / "results" / "cross_implementation.json"
        axiom_path = LAB / "results" / "lean_axioms.txt"
        strict_ok = (
            lean_status.get("status") == "LEAN_BUILD_AND_DIFFERENTIAL_REPLAY_PASS"
            and lean_results_path.exists()
            and len(read_jsonl(lean_results_path)) == 51
            and cross_path.exists()
            and read_json(cross_path).get("all_pass") is True
            and axiom_path.exists()
            and axiom_path.stat().st_size > 0
            and "error:" not in axiom_path.read_text(encoding="utf-8", errors="replace").lower()
            and "unknown constant" not in axiom_path.read_text(encoding="utf-8", errors="replace").lower()
        )
        check("lean_kernel_and_differential_replay", strict_ok, "strict external replay required")
    else:
        pending_ok = (
            lean_status.get("status") == "PENDING_EXTERNAL_LEAN_BUILD_AND_DIFFERENTIAL_REPLAY"
            and lean_status.get("blocking") is False
            and lean_status.get("authorization") == "USER_AUTHORIZED_EXTERNAL_REPLAY_DEFERRAL"
        )
        replayed_ok = (
            lean_status.get("status") == "LEAN_BUILD_AND_DIFFERENTIAL_REPLAY_PASS"
            and lean_status.get("blocking") is False
            and lean_status.get("authorization") == "EXTERNAL_REPLAY_EXECUTED"
        )
        check("lean_environment_override", pending_ok or replayed_ok, str(lean_status.get("status")))

    all_ok = all(ok for _, ok, _ in checks)
    mode = "REQUIRE_LEAN_RESULTS" if args.require_lean_results else "USER_AUTHORIZED_EXTERNAL_LEAN_REPLAY"
    informational: list[str] = []
    if not args.require_lean_results and lean_status.get("status") != "LEAN_BUILD_AND_DIFFERENTIAL_REPLAY_PASS":
        informational.append(
            "Lean kernel build, #print axioms replay, and 51-case Lean/Python differential remain pending external execution; this is nonblocking under the owner's explicit authorization."
        )
    pass_count = sum(ok for _, ok, _ in checks)
    fail_count = len(checks) - pass_count
    payload = {
        "phase": "FVII-SCI-01",
        "status": "PASS" if all_ok else "FAIL",
        "mode": mode,
        "checks": len(checks),
        "pass": pass_count,
        "info": len(informational),
        "fail": fail_count,
        "informational": informational,
        "results": [
            {"name": name, "status": "PASS" if ok else "FAIL", "detail": detail}
            for name, ok, detail in checks
        ],
    }
    lines = [
        f"FVII-SCI-01 VALIDATION: {payload['status']}",
        f"mode={mode}",
        f"checks={len(checks)}",
        f"pass={pass_count}",
        f"info={len(informational)}",
        f"fail={fail_count}",
    ]
    lines.extend(f"{'PASS' if ok else 'FAIL'}\t{name}\t{detail}" for name, ok, detail in checks)
    lines.extend(f"INFO\tlean_execution_boundary\t{message}" for message in informational)
    REPORT_TXT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    md_lines = [
        "# FVII-SCI-01 validation",
        "",
        f"**Status:** `{payload['status']}`",
        f"**Mode:** `{mode}`",
        f"**Acceptance checks:** {pass_count}/{len(checks)} pass",
        f"**Informational boundaries:** {len(informational)}",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for name, ok, detail in checks:
        safe_detail = detail.replace("|", "\\|").replace("\n", " ")
        md_lines.append(f"| `{name}` | {'PASS' if ok else 'FAIL'} | {safe_detail} |")
    if informational:
        md_lines += ["", "## Informational boundary", ""]
        md_lines.extend(f"- {message}" for message in informational)
    REPORT_MD.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    if not all_ok:
        print("\n--- static validator output ---\n" + static.stdout + static.stderr)
        print("\n--- unit test output ---\n" + tests.stdout + tests.stderr)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

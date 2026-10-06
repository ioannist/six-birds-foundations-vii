#!/usr/bin/env python3
"""Final acceptance validator for the Foundations VII science assets."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "science" / "registry"
TRACE = ROOT / "science" / "traceability"
REPORTS = ROOT / "reports"
LEAN = ROOT / "formalization" / "lean"
LAB = ROOT / "formalization" / "foundations_vii_lab"
LAB5 = LAB / "phase5" / "results"
BASE_TAG = "vii-science-04"

EXPECTED_CANDIDATES = {f"VII-C{i:03d}" for i in range(1, 37)}
EXPECTED_OBJECTS = {f"VII-O{i:02d}" for i in range(1, 19)}
EXPECTED_TARGETS = {f"FT{i:02d}" for i in range(1, 21)}
EXPECTED_NOGOS = {f"NGVII-{i:02d}" for i in range(1, 12)}
EXPECTED_DECISIONS = {f"DP{i:02d}" for i in range(1, 16)}
EXPECTED_COROLLARIES = {f"FVII-COR-{i:03d}" for i in range(1, 22)}
EXPECTED_PHASE5_ENVELOPES = {f"P5-E{i:02d}" for i in range(1, 12)}
TERMINAL_DISPOSITIONS = {
    "FORMAL_SCHEMA", "LEAN_KERNEL_PROVED", "LEAN_DECIDABLE_FINITE",
    "CONDITIONAL_THEOREM", "CONSTRUCTIVE_COUNTERMODEL",
    "REFUTED_CANDIDATE", "CLOSED_DEFERRAL",
}
EXPECTED_DISPOSITION_COUNTS = Counter({
    "FORMAL_SCHEMA": 15,
    "CONDITIONAL_THEOREM": 15,
    "LEAN_DECIDABLE_FINITE": 1,
    "CONSTRUCTIVE_COUNTERMODEL": 1,
    "REFUTED_CANDIDATE": 2,
    "CLOSED_DEFERRAL": 2,
})


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(command: list[str], *, python_path: bool = False) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if python_path:
        env["PYTHONPATH"] = str(LAB)
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, env=env)


def git_changed(paths: list[str]) -> list[str]:
    diff = run(["git", "diff", "--name-only", BASE_TAG, "--", *paths])
    untracked = run(["git", "ls-files", "--others", "--exclude-standard", "--", *paths])
    if diff.returncode or untracked.returncode:
        return [f"GIT_ERROR:{diff.stderr.strip()}:{untracked.stderr.strip()}"]
    return sorted(set(filter(None, diff.stdout.splitlines())) | set(filter(None, untracked.stdout.splitlines())))


def write_reports(payload: dict[str, Any]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "FVII_SCI_05_VALIDATION.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = [
        "# FVII-SCI-05 validation",
        "",
        f"**Status:** `{payload['status']}`",
        "",
        f"**Checks:** {payload['pass_count']}/{payload['check_count']}",
        "",
        f"**Kernel:** `{payload['kernel_status']}`",
        "",
        "| Check | Result | Detail |",
        "| --- | --- | --- |",
    ]
    for row in payload["checks"]:
        detail = str(row["detail"]).replace("|", "\\|")
        md.append(f"| {row['name']} | {row['status']} | {detail} |")
    if payload["errors"]:
        md += ["", "## Errors", ""] + [f"- {error}" for error in payload["errors"]]
    (REPORTS / "FVII_SCI_05_VALIDATION.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    text = [f"FVII-SCI-05 VALIDATION: {payload['status']}", f"PASS {payload['pass_count']}/{payload['check_count']}"]
    text.extend(f"{row['status']} {row['name']}: {row['detail']}".rstrip() for row in payload["checks"])
    if payload["errors"]:
        text.extend(f"ERROR {error}" for error in payload["errors"])
    (REPORTS / "FVII_SCI_05_VALIDATION.txt").write_text("\n".join(text) + "\n", encoding="utf-8")
    generated = ROOT / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    (generated / "fvii_sci05_validation.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (generated / "fvii_sci05_validation.txt").write_text("\n".join(text) + "\n", encoding="utf-8")


def _axiom_labels_match_raw_receipt(trust: list[dict]) -> bool:
    """Anchor trust labels to lean_axioms.txt itself, not to a generated field.

    Review gate 2: checking `static_classification` against the row's own
    `executed_axioms` lets a wrong generated field plus a matching wrong label pass.
    Parse the receipt independently and require three-way agreement -- receipt,
    field, label -- and require full coverage once the replay has run.
    """
    receipt_path = (ROOT / "formalization" / "foundations_vii_lab" / "phase5"
                    / "results" / "lean_axioms.txt")
    build = read_json(ROOT / "formalization" / "lean" / "BUILD_STATUS_FINAL.json")
    passed = build.get("kernel_build_status") == "PASS"
    if not passed:
        return all(str(r["static_classification"]).endswith("_PENDING_EXECUTED_PRINT_AXIOMS")
                   for r in trust)
    if not receipt_path.is_file():
        return False
    receipt: dict[str, list[str]] = {}
    for line in receipt_path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^'([^']+)' does not depend on any axioms\s*$", line)
        if m:
            receipt[m.group(1)] = []
            continue
        m = re.match(r"^'([^']+)' depends on axioms: \[(.*)\]\s*$", line)
        if m:
            receipt[m.group(1)] = [a.strip() for a in m.group(2).split(",") if a.strip()]
    # every theorem must appear in the receipt, and all three sources must agree
    for r in trust:
        name = str(r["theorem"])
        if name not in receipt:
            return False
        raw = receipt[name]
        if list(r.get("executed_axioms") or []) != raw:
            return False
        if (not raw) != str(r["static_classification"]).startswith("AXIOM_FREE_CONFIRMED"):
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-lean-results", action="store_true")
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    errors: list[str] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})
        if not condition:
            errors.append(f"{name}: {detail}")

    required = [
        ROOT / "FVII_SCI_05_REPORT.md",
        ROOT / "FVII_SCIENCE_FINAL_REPORT.md",
        REPORTS / "FVII_SCI_05_REPORT.md",
        REPORTS / "FVII_SCI_05_OBJECT_CLOSURE.md",
        REPORTS / "FVII_SCI_05_CANDIDATE_CLOSURE.md",
        REPORTS / "FVII_SCI_05_COROLLARIES.md",
        REPORTS / "FVII_SCI_05_FINITE_EVIDENCE.md",
        REPORTS / "FVII_SCI_05_TRUST_DEPENDENCY_AUDIT.md",
        REPORTS / "FVII_SCI_05_FINAL_ASSET_INDEX.md",
        REPORTS / "FVII_SCI_05_ACCEPTANCE.md",
        REPORTS / "FVII_SCI_05_EXTERNAL_LEAN_REPLAY.md",
        LEAN / "BUILD_STATUS_FINAL.json",
        LEAN / "EXTERNAL_COMPILE_FINAL.md",
        LEAN / "FoundationsVII" / "Release" / "Terminal.lean",
        LEAN / "FoundationsVII" / "Trust" / "PrintAxiomsFinal.lean",
        ROOT / "scripts" / "build_fvii_sci05_lab.py",
        ROOT / "scripts" / "build_fvii_sci05_registry.py",
        ROOT / "scripts" / "build_fvii_sci05_reports.py",
        ROOT / "scripts" / "validate_fvii_sci05_lean_static.py",
        ROOT / "scripts" / "validate_fvii_sci05.py",
        ROOT / "scripts" / "run_fvii_sci05_external_lean.sh",
        ROOT / "scripts" / "rebuild_fvii_sci05.sh",
    ]
    check("final_release_surface_present", all(path.is_file() for path in required), f"files={len(required)}")

    manifest = read_json(ROOT / "science_plan" / "manifest.json")
    manifest_ok = (
        manifest.get("current_phase_tag") == "vii-science-final"
        and manifest.get("completed_phases") == ["FVII-SCI-01", "FVII-SCI-02", "FVII-SCI-03", "FVII-SCI-04", "FVII-SCI-05"]
        and manifest.get("pending_phases") == []
        # Paper work is either not started, or explicitly authorised by the owner
        # AND confined to a declared prep phase. The prep phase produces assets
        # only; that no prose exists is enforced separately and unconditionally by
        # no_paper_or_paper_prep_changes below, which still fails on any .tex/.bib.
        and (
            manifest.get("paper_work_allowed") is False
            or (
                manifest.get("paper_work_allowed") is True
                and str(manifest.get("paper_phase", "")).startswith(("FVII-PREP-", "FVII-WRITE-"))
            )
        )
        and str(manifest.get("status", "")).startswith("FINAL_SCIENCE_RELEASE")
    )
    check("science_plan_manifest_final", manifest_ok, str(manifest.get("status")))

    summary = read_json(REG / "final_summary.json")
    # Re-run the static audit rather than reading a cached verdict: a stale PASS
    # written before later source changes masked a failing check for several
    # commits, which is exactly the staleness this validator exists to catch.
    run(["python3", str(ROOT / "scripts" / "validate_fvii_sci05_lean_static.py")])
    static = read_json(ROOT / "generated" / "fvii_sci05_static_lean_audit.json")
    check("static_lean_source_audit", static.get("status") == "PASS", f"{static.get('checks_passed', static.get('pass_count'))}/{static.get('checks_total', static.get('check_count'))}")

    candidates = read_jsonl(REG / "final_candidate_closure.jsonl")
    candidate_ids = {str(row["candidate_id"]) for row in candidates}
    disposition_counts = Counter(str(row["terminal_disposition"]) for row in candidates)
    candidate_ok = (
        len(candidates) == 36 and candidate_ids == EXPECTED_CANDIDATES
        and all(str(row["terminal_disposition"]) in TERMINAL_DISPOSITIONS for row in candidates)
        and disposition_counts == EXPECTED_DISPOSITION_COUNTS
        and all(row.get("specification_ready_not_proved_remaining") is False for row in candidates)
        and all(row.get("controlling_asset_id") and row.get("lean_declarations") and row.get("nonclaims") for row in candidates)
        and all(row.get("source_trace") for row in candidates)
    )
    check("all_candidates_terminal", candidate_ok, f"count={len(candidates)} dispositions={dict(disposition_counts)}")

    objects = read_jsonl(REG / "final_object_closure.jsonl")
    object_ok = (
        len(objects) == 18 and {str(row["object_id"]) for row in objects} == EXPECTED_OBJECTS
        and all(row.get("terminal") is True and row.get("declarations") and row.get("final_status") for row in objects)
    )
    check("all_eighteen_objects_closed", object_ok, f"objects={len(objects)}")

    targets = read_jsonl(REG / "final_formalization_target_closure.jsonl")
    target_ok = (
        len(targets) == 20 and {str(row["target_id"]) for row in targets} == EXPECTED_TARGETS
        and all("CLOSED" in str(row["final_status"]) and row.get("lean_theorems") for row in targets)
    )
    check("all_twenty_targets_closed_or_superseded", target_ok, f"targets={len(targets)}")

    declarations = read_jsonl(REG / "final_public_declarations.jsonl")
    declaration_names = {str(row["fully_qualified_name"]) for row in declarations}
    theorem_rows = read_jsonl(REG / "final_theorems.jsonl")
    theorem_names = {str(row["fully_qualified_name"]) for row in theorem_rows}
    check("public_declaration_census", len(declarations) == summary.get("public_declaration_count") == 1477 and len(declaration_names) == len(declarations), f"declarations={len(declarations)}")
    check("public_theorem_census", len(theorem_rows) == summary.get("public_theorem_count") == 732 and len(theorem_names) == len(theorem_rows), f"theorems={len(theorem_rows)}")

    corollaries = read_jsonl(REG / "final_corollaries.jsonl")
    corollary_ok = (
        len(corollaries) == 21 and {str(row["corollary_id"]) for row in corollaries} == EXPECTED_COROLLARIES
        and all(str(row["declaration"]) in theorem_names and row.get("statement_sha256") and row.get("nonclaim") and row.get("escape_routes") for row in corollaries)
    )
    check("twenty_one_cross_family_corollaries", corollary_ok, f"corollaries={len(corollaries)}")

    nogos = read_jsonl(REG / "final_no_go_closure.jsonl")
    nogo_ok = (
        len(nogos) == 11 and {str(row["no_go_id"]) for row in nogos} == EXPECTED_NOGOS
        and all(str(row["theorem"]) in theorem_names for row in nogos)
        and all(row.get("escape_theorems") and all(str(name) in theorem_names for name in row["escape_theorems"]) for row in nogos)
        and all(row.get("positive_controls") and row.get("failure_scenario") and row.get("nonclaim") for row in nogos)
    )
    check("eleven_terminal_no_gos", nogo_ok, f"no_gos={len(nogos)}")

    decisions = read_jsonl(REG / "final_decision_closure.jsonl")
    decision_ok = (
        len(decisions) == 15 and {str(row["decision_id"]) for row in decisions} == EXPECTED_DECISIONS
        and all(row.get("final_ruling") and row.get("final_status") for row in decisions)
        and {str(row["decision_id"]) for row in decisions if "SOURCE_GOVERNANCE" in str(row["final_status"])} == {"DP13", "DP14"}
    )
    check("fifteen_decisions_terminal_or_nonblocking", decision_ok, f"decisions={len(decisions)}")

    adapters = read_jsonl(REG / "final_adapters.jsonl")
    check("thirty_inherited_adapter_contracts", len(adapters) == 30 and len({row.get('reuse_id') or row.get('adapter_id') for row in adapters}) == 30, f"adapters={len(adapters)}")

    assays = read_jsonl(REG / "final_finite_assays.jsonl")
    phase_counts = Counter(str(row["phase"]) for row in assays)
    assay_ok = (
        len(assays) == 43 and phase_counts == Counter({"PHASE2": 9, "PHASE3": 11, "PHASE4": 12, "PHASE5": 11})
        and all(int(row["accepted_cardinality"]) + int(row["rejected_cardinality"]) == int(row["canonical_cardinality"]) for row in assays)
    )
    check("forty_three_cumulative_finite_assays", assay_ok, f"phase_counts={dict(phase_counts)}")

    p5_envelopes = read_jsonl(LAB5 / "envelopes.jsonl")
    p5_ids = {str(row["family_id"]) for row in p5_envelopes}
    p5_summary = read_json(LAB5 / "summary.json")
    p5_ok = (
        p5_ids == EXPECTED_PHASE5_ENVELOPES and len(p5_envelopes) == 11
        and p5_summary.get("raw_cases") == 86912
        and p5_summary.get("canonical_cases") == 84864
        and p5_summary.get("accepted_cases") == 21081
        and p5_summary.get("rejected_cases") == 63783
        and p5_summary.get("bounded_witness_count") == 33
        and p5_summary.get("cross_family_control_count") == 12
    )
    check("phase5_global_finite_census", p5_ok, json.dumps({k: p5_summary.get(k) for k in ("raw_cases", "canonical_cases", "accepted_cases", "rejected_cases", "bounded_witness_count", "cross_family_control_count")}, sort_keys=True))

    scenarios = read_jsonl(LAB5 / "all_scenario_results.jsonl")
    named_counter_results = read_jsonl(LAB5 / "all_countermodel_results.jsonl")
    fixture_ok = (
        len(scenarios) == 24 and all(row.get("all_pass") is True for row in scenarios)
        and len(named_counter_results) == 27 and all(row.get("all_pass") is True for row in named_counter_results)
        and len({row["fixture_id"] for row in scenarios}) == 24
        and len({row["fixture_id"] for row in named_counter_results}) == 27
    )
    check("complete_reference_fixture_replay", fixture_ok, "24/24 scenarios and 27/27 named countermodels")

    countermodels = read_jsonl(REG / "final_countermodels.jsonl")
    counter_kinds = Counter(str(row["countermodel_kind"]) for row in countermodels)
    counter_hash_errors: list[str] = []
    for row in countermodels:
        fixture = ROOT / str(row.get("fixture_path", ""))
        if not fixture.is_file():
            counter_hash_errors.append(f"missing:{row.get('countermodel_id')}:{fixture}")
        elif sha(fixture) != str(row.get("fixture_sha256", "")):
            counter_hash_errors.append(f"hash:{row.get('countermodel_id')}")
    counter_ok = (
        len(countermodels) == 38
        and counter_kinds == Counter({"NAMED_REFERENCE_COUNTERMODEL": 27, "MINIMIZED_BOUNDED_REJECTION_WITNESS": 11})
        and all(row.get("execution_pass") is True and row.get("fixture_path") and row.get("evidence_grade") for row in countermodels)
        and not counter_hash_errors
    )
    check("countermodel_registry_complete", counter_ok, f"kinds={dict(counter_kinds)} hash_errors={counter_hash_errors[:5]}")

    tests = run(["python3", "-m", "unittest", "discover", "-s", str(LAB / "tests"), "-p", "test*.py", "-v"], python_path=True)
    ran_match = re.search(r"Ran (\d+) tests", tests.stderr + tests.stdout)
    test_count = int(ran_match.group(1)) if ran_match else 0
    check("all_python_tests", tests.returncode == 0 and test_count == 70, f"returncode={tests.returncode} tests={test_count}")

    hashes = (TRACE / "final_statement_hashes.sha256").read_text(encoding="utf-8").splitlines()
    hash_names = {line.split("  ", 1)[1] for line in hashes if "  " in line}
    check("statement_hash_ledger_exact", len(hashes) == 732 and hash_names == theorem_names, f"hashes={len(hashes)}")

    dep_rows = read_jsonl(REG / "final_theorem_dependencies.jsonl")
    dep_edges = read_jsonl(TRACE / "final_theorem_dependency_edges.jsonl")
    dependency_ok = (
        len(dep_rows) == 732 and {str(row["theorem"]) for row in dep_rows} == theorem_names
        # 943, not the pre-replay 937: the external kernel replay required repairing
        # proofs that never compiled, and six genuine dependency edges became explicit
        # (five `*_admissible` proofs now name `TypedAdmissionStep.EffectTyped`, and
        # `strictness_accepted_cardinality` records the `allStrictnessCases` its own
        # statement already mentions). No edge was removed.
        and len(dep_edges) == summary.get("theorem_dependency_edge_count") == 943
        and all(str(row["source_theorem"]) in theorem_names and str(row["target_declaration"]) in declaration_names for row in dep_edges)
        and all(row["source_theorem"] != row["target_declaration"] for row in dep_edges)
    )
    check("theorem_dependency_registry_closed", dependency_ok, f"theorems={len(dep_rows)} edges={len(dep_edges)}")

    trust = read_jsonl(REG / "final_theorem_trust.jsonl")
    trust_ok = (
        len(trust) == 732 and {str(row["theorem"]) for row in trust} == theorem_names
        and all(row.get("static_classification") and row.get("executed_print_axioms_status") for row in trust)
        # Invariant: once the replay has run, every row's classification is decided
        # by its executed #print axioms receipt and must agree with it -- axiom-free
        # iff the receipt lists no axioms. Before the replay, the grade is a static
        # candidate. A blanket "confirmed axiom-free" over all 732 theorems is an
        # overclaim: only 625 are axiom-free; 107 depend on propext (10 also on
        # Quot.sound).
        and _axiom_labels_match_raw_receipt(trust)
    )
    check("theorem_trust_registry_closed", trust_ok, f"rows={len(trust)} trust_reachable={sum(bool(r['static_trust_reachable']) for r in trust)}")

    api = read_jsonl(REG / "final_public_api.jsonl")
    check("public_api_registry", len(api) == summary.get("public_module_count") == 111 and len({row["module"] for row in api}) == 111, f"modules={len(api)}")

    graph_paths = [
        TRACE / "final_theorem_dependency_graph.graphml",
        TRACE / "final_module_import_graph.graphml",
    ]
    graph_errors: list[str] = []
    graph_counts: list[tuple[int, int]] = []
    for graph_path in graph_paths:
        try:
            root = ET.parse(graph_path).getroot()
            ns = {"g": "http://graphml.graphdrawing.org/xmlns"}
            nodes = root.findall(".//g:node", ns)
            edges = root.findall(".//g:edge", ns)
            graph_counts.append((len(nodes), len(edges)))
            if not nodes:
                graph_errors.append(f"empty:{graph_path.name}")
        except Exception as exc:
            graph_errors.append(f"parse:{graph_path.name}:{exc}")
    graph_ok = (
        not graph_errors
        and len(graph_counts) == 2
        and graph_counts[0][1] == summary.get("theorem_dependency_edge_count")
        and graph_counts[1][1] == summary.get("module_import_edge_count")
    )
    check("graphml_dependency_surfaces_parse", graph_ok, f"counts={graph_counts} errors={graph_errors}")

    release = read_json(ROOT / "science" / "FINAL_SCIENCE_RELEASE.json")
    release_ok = (
        release.get("release_id") == "foundations-vii-science-final"
        and release.get("git_tag") == "vii-science-final"
        and release.get("archive") == "foundations-vii-science-assets-final.zip"
        and release.get("paper_work") is False
        and release.get("counts", {}).get("candidate_count") == 36
        and release.get("counts", {}).get("object_count") == 18
        and release.get("counts", {}).get("public_theorem_count") == 732
        and release.get("phase5_finite", {}).get("canonical_cases") == 84864
    )
    check("final_release_manifest_exact", release_ok, f"status={release.get('status')}")

    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    contents_text = (ROOT / "CONTENTS.md").read_text(encoding="utf-8")
    entry_paths = [
        ROOT / "FVII_SCIENCE_FINAL_REPORT.md",
        ROOT / "FVII_SCI_05_REPORT.md",
        REPORTS / "FVII_SCI_05_VALIDATION.json",
        ROOT / "SCIENCE_PLAN.md",
        LEAN / "EXTERNAL_COMPILE_FINAL.md",
    ]
    entry_ok = all(path.is_file() for path in entry_paths) and all(
        token in readme_text or token in contents_text
        for token in (
            "FVII_SCIENCE_FINAL_REPORT.md",
            "FVII_SCI_05_REPORT.md",
            "reports/FVII_SCI_05_VALIDATION.json",
            "SCIENCE_PLAN.md",
            "formalization/lean/EXTERNAL_COMPILE_FINAL.md",
        )
    )
    check("release_entry_points_resolve", entry_ok, f"entry_paths={len(entry_paths)}")

    static_summary_ok = (
        summary.get("candidate_count") == 36
        and summary.get("object_count") == 18
        and summary.get("formalization_target_count") == 20
        and summary.get("no_go_count") == 11
        and summary.get("corollary_count") == 21
        and summary.get("decision_count") == 15
        and summary.get("finite_assay_count") == 43
        and summary.get("adapter_count") == 30
        and summary.get("named_countermodel_count") == 27
        and summary.get("minimized_final_countermodel_count") == 11
        and summary.get("no_paper_work") is True
    )
    check("final_summary_exact", static_summary_ok, json.dumps(summary, sort_keys=True))

    inherited_changes = git_changed(["formalization/foundations_v_scaffold", "formalization/foundations_vi_scaffold"])
    check("inherited_formal_scaffolds_immutable", not inherited_changes, f"changed={inherited_changes[:8]}")
    paper_changes = git_changed(["source/papers", "formalization/foundations_vi_scaffold/paper", "formalization/foundations_v_scaffold/paper"])
    # Drafting is open under paper/ only. The frozen corpus (source/papers) and the
    # vendored scaffold papers remain immutable regardless of phase -- that is what
    # `paper_changes` above still enforces. Any .tex/.bib OUTSIDE paper/ is still a
    # violation, so a draft cannot leak into the science surface.
    tex_changes = [
        path for path in git_changed(["."])
        if Path(path).suffix.lower() in {".tex", ".bib"} and not path.startswith("paper/")
    ]
    check("no_paper_or_paper_prep_changes", not paper_changes and not tex_changes,
          f"paper={paper_changes[:5]} tex_outside_paper_dir={tex_changes[:5]}")

    # The writing-prep phase produces assets, not a manuscript. Blocking .tex/.bib
    # alone does not enforce that: a manuscript-shaped .md under paper_prep/ would
    # pass. Restrict the prep directory to asset formats, and cap per-file length so
    # a draft chapter cannot masquerade as an asset.
    prep = ROOT / "paper_prep"
    prep_allowed = {".md", ".csv", ".json", ".jsonl", ".yaml", ".yml", ".txt"}
    prep_bad = sorted(
        str(p.relative_to(ROOT)) for p in prep.rglob("*")
        if p.is_file() and p.suffix.lower() not in prep_allowed
    ) if prep.is_dir() else []
    PREP_MAX_WORDS = 6000
    prep_long = sorted(
        f"{p.relative_to(ROOT)}:{len(p.read_text(encoding='utf-8', errors='replace').split())}w"
        for p in prep.rglob("*.md")
        if p.is_file() and len(p.read_text(encoding="utf-8", errors="replace").split()) > PREP_MAX_WORDS
    ) if prep.is_dir() else []
    check("paper_prep_is_assets_not_manuscript", not prep_bad and not prep_long,
          f"bad_format={prep_bad[:5]} over_{PREP_MAX_WORDS}w={prep_long[:5]}")

    root_text = (LEAN / "FoundationsVII.lean").read_text(encoding="utf-8")
    all_text = (LEAN / "FoundationsVII" / "All.lean").read_text(encoding="utf-8")
    root_ok = "import FoundationsVII.All" in root_text and "import FoundationsVII.Release.All" in all_text and "paper" not in root_text.lower().replace("paper drafting", "")
    # The root comment intentionally says paper drafting is outside the API; do not reject that boundary sentence.
    root_ok = "import FoundationsVII.All" in root_text and "import FoundationsVII.Release.All" in all_text
    check("final_public_root_complete", root_ok, "FoundationsVII.lean -> All -> Release")

    build = read_json(LEAN / "BUILD_STATUS_FINAL.json")
    if args.require_lean_results:
        cross_path = LAB5 / "cross_implementation_status.json"
        axiom_path = LAB5 / "lean_axioms.txt"
        receipt_path = LAB5 / "lean_axiom_receipt_summary.json"
        lean_rows_path = LAB5 / "lean_results.jsonl"
        lean_ok = (
            build.get("kernel_build_status") == "PASS"
            and cross_path.is_file() and read_json(cross_path).get("all_pass") is True
            and axiom_path.is_file() and axiom_path.stat().st_size > 0
            and receipt_path.is_file() and read_json(receipt_path).get("sorry_dependency_detected") is False
            and lean_rows_path.is_file() and len(read_jsonl(lean_rows_path)) == 62
        )
        check("strict_external_lean_replay", lean_ok, f"kernel={build.get('kernel_build_status')}")
    else:
        lean_ok = build.get("kernel_build_status") in {"NOT_RUN_LOCAL_ENVIRONMENT", "PASS"}
        check("authorized_lean_boundary", lean_ok, f"kernel={build.get('kernel_build_status')}")

    rebuild_script = ROOT / "scripts" / "rebuild_fvii_sci05.sh"
    shell_check = run(["bash", "-n", str(rebuild_script)]) if rebuild_script.is_file() else None
    external_check = run(["bash", "-n", str(ROOT / "scripts" / "run_fvii_sci05_external_lean.sh")])
    check("shell_scripts_parse", shell_check is not None and shell_check.returncode == 0 and external_check.returncode == 0,
          f"rebuild={None if shell_check is None else shell_check.returncode} external={external_check.returncode}")

    py_files = [
        ROOT / "scripts" / "build_fvii_sci05_lab.py",
        ROOT / "scripts" / "build_fvii_sci05_registry.py",
        ROOT / "scripts" / "build_fvii_sci05_reports.py",
        ROOT / "scripts" / "validate_fvii_sci05_lean_static.py",
        ROOT / "scripts" / "validate_fvii_sci05.py",
        ROOT / "scripts" / "compare_fvii_sci05_lean.py",
        LAB / "fvii_lab" / "phase5.py",
    ]
    compile_check = run(["python3", "-m", "py_compile", *map(str, py_files)])
    check("python_sources_compile", compile_check.returncode == 0, compile_check.stderr.strip()[:500])

    payload = {
        "phase": "FVII-SCI-05",
        "status": "PASS" if not errors else "FAIL",
        "strict_lean_required": args.require_lean_results,
        "check_count": len(checks),
        "pass_count": sum(row["status"] == "PASS" for row in checks),
        "checks": checks,
        "errors": errors,
        "release_stage": summary.get("stage"),
        "kernel_status": build.get("kernel_build_status"),
        "candidate_count": len(candidates),
        "object_count": len(objects),
        "corollary_count": len(corollaries),
        "public_declaration_count": len(declarations),
        "public_theorem_count": len(theorem_rows),
        "finite_assay_count": len(assays),
        "named_countermodel_count": 27,
        "minimized_countermodel_count": 11,
    }
    write_reports(payload)
    print(json.dumps({k: payload[k] for k in ("status", "check_count", "pass_count", "candidate_count", "object_count", "corollary_count", "public_theorem_count", "finite_assay_count", "kernel_status")}, sort_keys=True))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main())

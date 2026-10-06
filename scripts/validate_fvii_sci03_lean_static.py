#!/usr/bin/env python3
"""Static source audit for FVII-SCI-03.

This is strictly weaker than Lean kernel elaboration.  It verifies the closed
Phase-3 source surface, import closure, declaration/registry parity, theorem
trust replay wiring, inherited immutability, phase boundaries, and the absence
of VII-owned proof shortcuts when Lean/Lake are unavailable.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from collections import Counter
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formalization" / "lean"
VII = LEAN / "FoundationsVII"
REG = ROOT / "science" / "registry"
GEN = ROOT / "generated"
BASE_TAG = "vii-science-02"

CANDIDATES = {
    "VII-C007", "VII-C008", "VII-C009", "VII-C010", "VII-C011",
    "VII-C016", "VII-C019", "VII-C026", "VII-C030", "VII-C031",
    "VII-C033", "VII-C035", "VII-C036",
}
NO_GOS = {"NGVII-02", "NGVII-06", "NGVII-07", "NGVII-08", "NGVII-09"}
TARGETS = {"FT05", "FT06", "FT07", "FT08", "FT09", "FT10", "FT16", "FT18", "FT19", "FT20"}
DECISIONS = {"DP01", "DP02", "DP03", "DP04", "DP05", "DP06", "DP10", "DP15"}
REQUIRED_THEOREMS = {
    "FoundationsVII.ContactProfile.compatibility_does_not_imply_evidenced_contact",
    "FoundationsVII.ContactProfile.evidenced_contact_does_not_imply_composite",
    "FoundationsVII.peer_contact_can_transport_without_join",
    "FoundationsVII.JoinEntryRecord.completed_has_witnessed_contact",
    "FoundationsVII.JoinEntryFieldProfile.weak_status_checker_has_source_false_positive",
    "FoundationsVII.JoinAssessment.strict_status_constructor",
    "FoundationsVII.JoinAssessment.contact_refinement_and_composite_axes_may_overlap",
    "FoundationsVII.CompositeClosureWitness.objecthood_from_fixed_point",
    "FoundationsVII.CompositeClosureWitness.certified_retains_both_parents",
    "FoundationsVII.finite_composite_objecthood_control",
    "FoundationsVII.AntiProductWitness.valid_is_nonfactorizing",
    "FoundationsVII.AntiProductWitness.relabel_only_fails",
    "FoundationsVII.AntiProductWitness.scheduling_only_fails",
    "FoundationsVII.AntiProductWitness.coarsening_only_fails",
    "FoundationsVII.StrictJoinEvidence.certified_has_objecthood",
    "FoundationsVII.StrictJoinEvidence.certified_retains_both_parents",
    "FoundationsVII.StrictJoinEvidence.certified_has_source_and_budget_gates",
    "FoundationsVII.StrictJoinEvidence.certified_does_not_supply_directionality",
    "FoundationsVII.StrictJoinProfile.anti_product_does_not_imply_objecthood",
    "FoundationsVII.StrictJoinProfile.strictness_does_not_imply_parent_retention",
    "FoundationsVII.SourceAncestry.same_lineage_excludes_independence",
    "FoundationsVII.SourceIndependenceGate.same_lineage_fails_independence_sensitive_credit",
    "FoundationsVII.SourceIndependenceGate.behavioral_nonfactorization_alone_is_insufficient",
    "FoundationsVII.JoinCostEntry.positive_cost_without_payment_or_zero_channel_is_not_credited",
    "FoundationsVII.JoinCostEntry.positive_observer_cost_cannot_be_hidden",
    "FoundationsVII.LiveJoinCapacity.finite_live_join_bound",
    "FoundationsVII.composite_formation_does_not_imply_parent_retention",
    "FoundationsVII.no_unconditional_join_monotonicity_under_refinement",
    "FoundationsVII.ResidualLedger.no_silent_residual_deletion_under_scope_change",
    "FoundationsVII.constructive_join_created_cross_term_needle",
    "FoundationsVII.joining_is_not_monotonically_obstruction_reducing",
    "FoundationsVII.ContactNullProfile.no_evidenced_contact_is_weaker_than_certified_noninteraction",
    "FoundationsVII.DeclaredContactCase.outside_family_is_an_explicit_escape",
    "FoundationsVII.mere_product_is_not_strict_join_credit",
    "FoundationsVII.special_case_categorical_representation_is_conditional",
    "FoundationsVII.unconditional_categorical_reduction_countermodel",
    "FoundationsVII.no_unqualified_contact_degree_from_bookkeeping_alone",
    "FoundationsVII.NoGo.NGVII_02_no_resemblance_only_independence_join",
    "FoundationsVII.NoGo.NGVII_06_no_join_from_contact_alone",
    "FoundationsVII.NoGo.NGVII_07_no_product_common_refinement_strictness_credit",
    "FoundationsVII.NoGo.NGVII_08_no_one_lineage_source_independence_credit",
    "FoundationsVII.NoGo.NGVII_09_no_positive_cost_join_credit_without_payment",
    "FoundationsVII.NoGo.no_self_bootstrapping_join_without_seed_or_bridge",
    "FoundationsVII.Models.Finite.Phase3.status_partition_complete",
    "FoundationsVII.Models.Finite.Phase3.directionless_strict_case_exists",
    "FoundationsVII.Models.Finite.Phase3.exactly_one_certified_noninteraction_profile",
    "FoundationsVII.Models.Finite.Phase3.strict_join_without_listed_universal_construction_exists",
    "FoundationsVII.Models.Finite.Phase3.all_phase3_scenarios_pass",
    "FoundationsVII.Models.Finite.Phase3.all_phase3_countermodels_pass",
}

DECL_RE = re.compile(
    r"^(?P<private>private\s+)?(?P<kind>structure|inductive|abbrev|def|theorem|lemma|corollary|axiom|opaque)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)"
)
NS_RE = re.compile(r"^namespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*$")
END_RE = re.compile(r"^end(?:\s+([A-Za-z_][A-Za-z0-9_.]*))?\s*$")


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def phase3_science_files() -> list[Path]:
    files: list[Path] = []
    for folder in ("Contact", "Join", "Residuals"):
        files.extend(p for p in sorted((VII / folder).glob("*.lean")) if p.name != "All.lean")
    files += [VII / "NoGo" / "Join.lean"]
    files += [
        VII / "Models" / "Finite" / "Phase3" / "ContactJoinEnvelope.lean",
        VII / "Models" / "Finite" / "Phase3" / "ScenarioChecks.lean",
    ]
    return files


def remove_comments_and_strings(text: str) -> tuple[str, list[str]]:
    out: list[str] = []
    errors: list[str] = []
    i = 0
    block_depth = 0
    in_string = False
    escaped = False
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if block_depth:
            if ch == "/" and nxt == "-":
                block_depth += 1; out.extend("  "); i += 2
            elif ch == "-" and nxt == "/":
                block_depth -= 1; out.extend("  "); i += 2
            else:
                out.append("\n" if ch == "\n" else " "); i += 1
            continue
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            out.append("\n" if ch == "\n" else " "); i += 1
            continue
        if ch == "/" and nxt == "-":
            block_depth = 1; out.extend("  "); i += 2; continue
        if ch == "-" and nxt == "-":
            while i < len(text) and text[i] != "\n":
                out.append(" "); i += 1
            continue
        if ch == '"':
            in_string = True; out.append(" "); i += 1; continue
        out.append(ch); i += 1
    if block_depth:
        errors.append(f"unterminated block comment depth={block_depth}")
    if in_string:
        errors.append("unterminated string literal")
    return "".join(out), errors


def delimiter_errors(code: str) -> list[str]:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[tuple[str, int]] = []
    errors: list[str] = []
    for pos, ch in enumerate(code):
        if ch in "([{":
            stack.append((ch, pos))
        elif ch in ")]}":
            if not stack or stack[-1][0] != pairs[ch]:
                errors.append(f"unmatched closing {ch} at offset {pos}")
            else:
                stack.pop()
    errors.extend(f"unclosed {ch} at offset {pos}" for ch, pos in stack)
    return errors


def library_roots() -> dict[str, Path]:
    data = tomllib.loads((LEAN / "lakefile.toml").read_text(encoding="utf-8"))
    roots: dict[str, Path] = {}
    for lib in data.get("lean_lib", []):
        roots[str(lib["name"])] = (LEAN / str(lib.get("srcDir", "."))).resolve()
    return roots


def resolve_import(name: str, roots: dict[str, Path]) -> Path | None:
    candidates = [LEAN / Path(*name.split(".")).with_suffix(".lean")]
    for lib_name, root in roots.items():
        if name == lib_name:
            candidates.append(root / f"{lib_name}.lean")
        elif name.startswith(lib_name + "."):
            candidates.append(root / Path(*name.split(".")).with_suffix(".lean"))
    return next((p for p in candidates if p.exists()), None)


def parse_public_declarations(files: Iterable[Path]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for path in files:
        skeleton, _ = remove_comments_and_strings(path.read_text(encoding="utf-8"))
        namespaces: list[str] = []
        for raw in skeleton.splitlines():
            stripped = raw.strip()
            ns = NS_RE.match(stripped)
            if ns:
                namespaces.extend(ns.group(1).split(".")); continue
            if END_RE.match(stripped):
                if namespaces:
                    namespaces.pop()
                continue
            match = DECL_RE.match(stripped)
            if not match or match.group("private"):
                continue
            name = match.group("name")
            fq = name if "." in name else ".".join((*namespaces, name))
            rows.append((fq, match.group("kind")))
    return rows


def git_changed(paths: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", BASE_TAG, "--", *paths],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    if result.returncode != 0:
        return [f"GIT_ERROR:{result.stderr.strip()}"]
    return [line for line in result.stdout.splitlines() if line]


def main() -> int:
    checks: list[tuple[str, bool, str]] = []
    errors: list[str] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append((name, bool(condition), detail))
        if not condition:
            errors.append(f"{name}: {detail}")

    all_files = sorted(VII.rglob("*.lean")) + [LEAN / "FoundationsVII.lean"]
    roots = library_roots()
    lexical_ok = import_ok = trust_ok = True
    import_count = 0
    for path in all_files:
        skeleton, lexical = remove_comments_and_strings(path.read_text(encoding="utf-8"))
        local_errors = lexical + delimiter_errors(skeleton)
        if local_errors:
            lexical_ok = False
            errors.extend(f"{path.relative_to(ROOT)}: {msg}" for msg in local_errors)
        forbidden: list[str] = []
        if re.search(r"\bsorry\b", skeleton):
            forbidden.append("sorry")
        if re.search(r"(?m)^\s*admit\b", skeleton):
            forbidden.append("admit-tactic")
        if re.search(r"(?m)^\s*(axiom|opaque|unsafe)\b", skeleton):
            forbidden.append("axiom/opaque/unsafe-declaration")
        if forbidden:
            trust_ok = False
            errors.append(f"{path.relative_to(ROOT)}: forbidden proof surface {forbidden}")
        for match in re.finditer(r"(?m)^\s*import\s+([A-Za-z0-9_.]+)\s*$", skeleton):
            import_count += 1
            if resolve_import(match.group(1), roots) is None:
                import_ok = False
                errors.append(f"{path.relative_to(ROOT)}: unresolved import {match.group(1)}")
    check("lexical_balance", lexical_ok, f"{len(all_files)} VII/root Lean files")
    check("import_closure", import_ok, f"{import_count} import statements")
    check("no_vii_owned_proof_shortcuts", trust_ok, "no sorry/admit/new axiom/opaque/unsafe")

    science_files = phase3_science_files()
    missing_sources = [str(p.relative_to(ROOT)) for p in science_files if not p.is_file()]
    check("phase3_source_surface_present", not missing_sources, f"files={len(science_files)} missing={missing_sources}")
    source_rows = parse_public_declarations(science_files)
    source_names = [name for name, _ in source_rows]
    duplicates = sorted(name for name, count in Counter(source_names).items() if count > 1)
    check("phase3_source_declaration_uniqueness", not duplicates, f"rows={len(source_rows)} duplicates={len(duplicates)}")

    registry_rows = read_jsonl(REG / "phase3_public_declarations.jsonl")
    registry_pairs = [(str(row["fully_qualified_name"]), str(row["kind"])) for row in registry_rows]
    parity = sorted(source_rows) == sorted(registry_pairs)
    check("phase3_registry_source_parity", parity, f"source={len(source_rows)} registry={len(registry_pairs)}")
    if not parity:
        source_set, registry_set = set(source_rows), set(registry_pairs)
        errors.append(f"registry delta source_only={sorted(source_set-registry_set)[:20]} registry_only={sorted(registry_set-source_set)[:20]}")

    theorem_names = {name for name, kind in source_rows if kind in {"theorem", "lemma", "corollary"}}
    check("required_phase3_theorems", REQUIRED_THEOREMS <= theorem_names,
          f"found={len(REQUIRED_THEOREMS & theorem_names)}/{len(REQUIRED_THEOREMS)}")
    if not REQUIRED_THEOREMS <= theorem_names:
        errors.append(f"missing required theorems: {sorted(REQUIRED_THEOREMS-theorem_names)}")

    print_path = VII / "Trust" / "PrintAxiomsPhase3.lean"
    print_axioms = re.findall(
        r"(?m)^#print axioms\s+([A-Za-z_][A-Za-z0-9_'.]*)\s*$",
        print_path.read_text(encoding="utf-8"),
    ) if print_path.is_file() else []
    print_ok = set(print_axioms) == theorem_names and len(print_axioms) == len(set(print_axioms))
    check("print_axioms_exact_phase3_surface", print_ok,
          f"printed={len(print_axioms)} theorems={len(theorem_names)}")

    build_status_path = LEAN / "BUILD_STATUS_PHASE3.json"
    build_status = json.loads(build_status_path.read_text(encoding="utf-8")) if build_status_path.is_file() else {}
    expected_kernel_status = (
        "PASS_EXTERNAL_REPLAY"
        if build_status.get("kernel_build_status") == "PASS"
        else "PENDING_EXTERNAL_LEAN_REPLAY"
    )

    candidates = read_jsonl(REG / "phase3_candidate_closure.jsonl")
    candidate_ids = {str(r["candidate_id"]) for r in candidates}
    candidate_ok = (
        candidate_ids == CANDIDATES
        and all(str(r["phase3_status"]).startswith("TERMINAL_PHASE3_ASSET") for r in candidates)
        and all(int(r["theorem_count"]) > 0 and r["lean_theorems"] for r in candidates)
    )
    check("thirteen_terminal_candidate_assets", candidate_ok, f"ids={sorted(candidate_ids)}")

    nogos = read_jsonl(REG / "phase3_no_go_closure.jsonl")
    nogo_ids = {str(r["no_go_id"]) for r in nogos}
    nogo_ok = (
        nogo_ids == NO_GOS
        and all(bool(r["source_declarations_present"]) for r in nogos)
        and all(str(r["theorem"]) in theorem_names for r in nogos)
        and all(
            all(str(name) in theorem_names for name in r["escape_theorems"])
            for r in nogos
        )
        and all(r["positive_controls"] and r["failure_scenarios"] for r in nogos)
        and all(str(r["terminal_status"]).startswith("PROVED_AT_DECLARED_STRUCTURAL_SCOPE") for r in nogos)
        and all(str(r["kernel_status"]) == expected_kernel_status for r in nogos)
    )
    check("five_no_go_fronts_with_escapes", nogo_ok, f"ids={sorted(nogo_ids)}")

    targets = read_jsonl(REG / "phase3_formalization_targets.jsonl")
    target_ids = {str(r["target_id"]) for r in targets}
    target_ok = (
        target_ids == TARGETS
        and all(
            ("COMPLETE" in str(r["phase3_status"]) or "PORTION_COMPLETE" in str(r["phase3_status"]))
            for r in targets
        )
        and all(str(r["kernel_status"]) == expected_kernel_status for r in targets)
        and all(r["phase3_theorems"] for r in targets)
    )
    check("formalization_target_closure", target_ok, f"targets={sorted(target_ids)}")

    decisions = read_jsonl(REG / "phase3_decision_closure.jsonl")
    decision_ids = {str(r["decision_id"]) for r in decisions}
    decision_ok = (
        decision_ids == DECISIONS
        and all(bool(r["terminal"]) and bool(r["phase3_terminal_ruling"]) for r in decisions)
        and all(bool(r["evidence_present"]) and r["evidence_declarations"] for r in decisions)
    )
    check("eight_terminal_scope_decisions", decision_ok, f"ids={sorted(decision_ids)}")

    root_imports = (VII / "All.lean").read_text(encoding="utf-8")
    finite_imports = (VII / "Models" / "Finite" / "All.lean").read_text(encoding="utf-8")
    nogo_imports = (VII / "NoGo" / "All.lean").read_text(encoding="utf-8")
    lakefile = (LEAN / "lakefile.toml").read_text(encoding="utf-8")
    wiring_ok = (
        "import FoundationsVII.Contact.All" in root_imports
        and "import FoundationsVII.Residuals.All" in root_imports
        and "import FoundationsVII.Join.All" in root_imports
        and "import FoundationsVII.NoGo.Join" in nogo_imports
        and "import FoundationsVII.Models.Finite.Phase3.All" in finite_imports
        and 'name = "fvii_phase3_envelopes"' in lakefile
        and 'root = "FoundationsVII.Models.Finite.Phase3.Runner"' in lakefile
    )
    check("phase3_public_and_executable_wiring", wiring_ok, "Contact/Join/Residuals/NoGo/finite runner")

    runner_text = (VII / "Models" / "Finite" / "Phase3" / "Runner.lean").read_text(encoding="utf-8")
    scenario_text = (VII / "Models" / "Finite" / "Phase3" / "ScenarioChecks.lean").read_text(encoding="utf-8")
    runner_ok = (
        all(f'"P3-E{i:02d}"' in runner_text for i in range(1, 12))
        and "phase3Scenarios" in runner_text and "phase3Countermodels" in runner_text
        and "phase3Scenarios.length = 12" in scenario_text
        and "phase3Countermodels.length = 14" in scenario_text
    )
    check("eleven_family_and_fixture_lean_runner", runner_ok, "P3-E01..P3-E11, 12 scenarios, 14 countermodels")

    later_dirs = [VII / name for name in ("Enablement", "Dynamics", "Corollaries")]
    check("later_science_not_executed", not any(path.exists() for path in later_dirs), "no Phase-4/5 implementation directories")

    immutable_paths = [
        "formalization/foundations_v_scaffold",
        "formalization/foundations_vi_scaffold",
        "formalization/_provenance",
        "formalization/lean/FoundationsVII/Core",
        "formalization/lean/FoundationsVII/Prior",
        "formalization/lean/FoundationsVII/Access",
        "formalization/lean/FoundationsVII/Models/Finite/Flags.lean",
        "formalization/lean/FoundationsVII/Models/Finite/Evaluator.lean",
        "formalization/lean/FoundationsVII/Models/Finite/Scenarios.lean",
        "formalization/lean/FoundationsVII/Models/Finite/Countermodels.lean",
        "formalization/lean/FoundationsVII/Models/Finite/Regression.lean",
        "formalization/lean/FoundationsVII/Models/Finite/Phase2",
        "formalization/foundations_vii_lab/fixtures",
        "formalization/foundations_vii_lab/fvii_lab/phase2.py",
    ]
    immutable_changes = git_changed(immutable_paths)
    check("phase2_and_inherited_surfaces_immutable", not immutable_changes, f"changed={immutable_changes[:10]}")

    tex_changes = [p for p in git_changed(["."]) if p.endswith(".tex") or p.endswith(".bib")]
    check("no_paper_or_bibliography_work", not tex_changes, f"changed={tex_changes}")

    risky_patterns = {
        "categorical_blind_decide": (VII / "Join" / "Categorical.lean", r"FinitePackageCategory\.WellFormed finitePackageCategoryWitness := by decide"),
        "retention_blind_decide": (VII / "Join" / "Retention.lean", r"JoinDescentCertificate\.Valid descentWitness := by decide"),
        "residual_blind_decide": (VII / "Residuals" / "Ledger.lean", r"ResidualTransition\.WellFormed residualTransitionWitness[\s\S]{0,200}:= by\s+decide"),
        "existential_blind_decide": (VII / "Models" / "Finite" / "Phase3" / "ContactJoinEnvelope.lean", r"∃ c ∈ [\s\S]{0,250}:= by decide"),
    }
    risky_hits = [name for name, (path, pattern) in risky_patterns.items() if re.search(pattern, path.read_text(encoding="utf-8"))]
    check("closed_quantifier_proofs_are_constructive", not risky_hits, f"hits={risky_hits}")

    all_ok = all(ok for _, ok, _ in checks)
    payload = {
        "phase": "FVII-SCI-03",
        "status": "PASS" if all_ok else "FAIL",
        "boundary": "STATIC_SOURCE_AUDIT_NOT_KERNEL_ELABORATION",
        "lean_file_count": len(all_files),
        "phase3_science_file_count": len(science_files),
        "phase3_declaration_count": len(source_rows),
        "phase3_theorem_count": len(theorem_names),
        "import_statement_count": import_count,
        "checks": [
            {"name": name, "status": "PASS" if ok else "FAIL", "detail": detail}
            for name, ok, detail in checks
        ],
        "errors": errors,
    }
    GEN.mkdir(parents=True, exist_ok=True)
    (GEN / "fvii_sci03_static_lean_audit.json").write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"FVII-SCI-03 LEAN STATIC VALIDATION: {payload['status']}")
    for name, ok, detail in checks:
        print(f" - {'PASS' if ok else 'FAIL'} {name}: {detail}")
    for error in errors:
        print("   ERROR", error)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

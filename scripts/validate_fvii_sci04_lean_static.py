#!/usr/bin/env python3
"""Static source audit for FVII-SCI-04.

This audit is intentionally weaker than Lean kernel elaboration.  It checks the
closed Phase-4 source surface, import closure, declaration/registry parity,
trust replay wiring, inherited/prior-phase immutability, finite runner wiring,
and the absence of VII-owned proof shortcuts when Lean/Lake are unavailable.
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
BASE_TAG = "vii-science-03"

CANDIDATES = {
    "VII-C012", "VII-C013", "VII-C014", "VII-C015", "VII-C017",
    "VII-C018", "VII-C027", "VII-C028", "VII-C032", "VII-C034",
}
NO_GOS = {"NGVII-10"}
TARGETS = {"FT11", "FT12", "FT13", "FT14", "FT15", "FT16", "FT19", "FT20"}
DECISIONS = {"DP07", "DP08", "DP09", "DP11", "DP12"}
ENVELOPES = {f"P4-E{i:02d}" for i in range(1, 13)}
SCENARIOS = {"TTW-S02", "TTW-S03", "TTW-S06", "TTW-S16", "TTW-S17", "TTW-S18", "TTW-S20", "TTW-S21", "TTW-S24"}
COUNTERMODELS = {"CM-06", "CM-07", "CM-10", "CM-17", "CM-22", "CM-23", "CM-24", "CM-25"}
REQUIRED_THEOREMS = {
    # Enablement attribution and endogeny.
    "FoundationsVII.AttributionEvidence.honest_refinement_preserves_source_root",
    "FoundationsVII.AttributedEnablement.hidden_execution_defeats_attribution",
    "FoundationsVII.attribution_does_not_imply_descent_sufficiency_causation_or_endogeny",
    "FoundationsVII.EndogenousEnablementProfile.eligible_iff_exact_criterion",
    "FoundationsVII.EndogenousEnablementProfile.hidden_theorist_execution_defeats_endogenous_credit",
    "FoundationsVII.EndogenousEnablementProfile.hidden_observer_execution_defeats_endogenous_credit",
    "FoundationsVII.constructive_endogenous_enablement_exists",
    "FoundationsVII.accounted_environmental_input_is_compatible_with_endogeny",
    # Birth and closure agency.
    "FoundationsVII.inherited_birth_class_signatures_are_injective",
    "FoundationsVII.every_inherited_birth_class_activates_packaging",
    "FoundationsVII.BirthRecord.participant_credit_requires_objecthood",
    "FoundationsVII.BirthRecord.participant_credit_requires_closure_survival",
    "FoundationsVII.contact_can_remain_relation_only",
    "FoundationsVII.closure_performed_and_closure_undergone_are_distinct",
    "FoundationsVII.inherited_activation_class_does_not_by_itself_create_participant",
    "FoundationsVII.participant_creation_is_conditional_not_automatic",
    # Transmission/descent and enablement separations.
    "FoundationsVII.TransmissionRecord.pure_downward_selection_preserves_present_lower_facts",
    "FoundationsVII.TransmissionRecord.pure_downward_selection_cannot_create_absent_lower_fact",
    "FoundationsVII.DescentSquare.fidelity_is_commuting_square",
    "FoundationsVII.structural_downward_selection_is_not_automatically_causal",
    "FoundationsVII.all_three_transmission_directions_have_positive_controls",
    "FoundationsVII.constructive_enablement_without_descent",
    "FoundationsVII.constructive_necessary_but_insufficient_enablement",
    "FoundationsVII.enablement_without_descent_need_not_be_causal",
    "FoundationsVII.necessary_enablement_does_not_imply_sufficiency",
    # Composition and residual accounting.
    "FoundationsVII.ResourceDelta.combine_assoc",
    "FoundationsVII.EnablementLink.compose_associative_data",
    "FoundationsVII.EnablementLink.composable_chain_associates",
    "FoundationsVII.EnablementLink.compose_accumulates_cost",
    "FoundationsVII.EnablementLink.compose_accumulates_residual_debt",
    "FoundationsVII.composed_enablement_without_transitive_causation_exists",
    "FoundationsVII.incompatible_order_blocks_composition_credit",
    "FoundationsVII.enablement_chain_can_be_order_sensitive",
    "FoundationsVII.ResidualFlow.accounted_balance",
    "FoundationsVII.ResidualFlow.composed_debt_accumulates",
    # Confluence and seed dependence.
    "FoundationsVII.CriticalPair.resolved_of_joinable_audit_equivalent",
    "FoundationsVII.FiniteAdmissionSystem.finite_critical_pair_criterion_iff_confluent",
    "FoundationsVII.finite_confluent_positive_model",
    "FoundationsVII.finite_nonconfluent_countermodel",
    "FoundationsVII.seed_partition_can_change_terminal_package",
    "FoundationsVII.presentation_difference_is_not_seed_dependence",
    "FoundationsVII.one_commuting_square_does_not_establish_global_confluence",
    # Holonomy, arrow, reversal, and cross-time contact.
    "FoundationsVII.constructive_interaction_holonomy",
    "FoundationsVII.holonomy_with_zero_arrow_witness",
    "FoundationsVII.driven_arrow_positive_control",
    "FoundationsVII.driven_arrow_requires_independent_drive_certificate",
    "FoundationsVII.reversal_null_and_driven_controls_are_distinct",
    "FoundationsVII.CrossTimeContact.valid_under_admissible_reparameterization",
    "FoundationsVII.synchronized_cross_time_contact_exists",
    "FoundationsVII.partial_order_cross_time_contact_exists",
    "FoundationsVII.synchronization_does_not_require_equal_local_clock_readings",
    "FoundationsVII.incommensurable_times_require_explicit_order_witness",
    # Primitive algebra decision.
    "FoundationsVII.current_full_primitive_algebra_is_not_ready",
    "FoundationsVII.full_algebra_reopen_condition_is_exact",
    "FoundationsVII.resource_delta_fragment_is_associative",
    "FoundationsVII.full_generators_relations_program_deferred_with_formal_reopen_condition",
    # No-go and finite controls.
    "FoundationsVII.NoGo.NGVII_10_no_arrow_from_holonomy_alone",
    "FoundationsVII.NoGo.NGVII_10_holonomy_zero_arrow_control",
    "FoundationsVII.NoGo.NGVII_10_escape_independent_driven_arrow",
    "FoundationsVII.Models.Finite.Phase4.finite_holonomy_zero_arrow_exists",
    "FoundationsVII.Models.Finite.Phase4.finite_driven_arrow_exists",
    "FoundationsVII.Models.Finite.Phase4.all_phase4_scenarios_pass",
    "FoundationsVII.Models.Finite.Phase4.all_phase4_countermodels_pass",
}

DECL_RE = re.compile(
    r"^(?P<private>private\s+)?(?P<kind>structure|inductive|abbrev|def|theorem|lemma|corollary|axiom|opaque)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)"
)
NS_RE = re.compile(r"^namespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*$")
END_RE = re.compile(r"^end(?:\s+([A-Za-z_][A-Za-z0-9_.]*))?\s*$")


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def phase4_science_files() -> list[Path]:
    files: list[Path] = []
    for folder in ("Enablement", "Dynamics"):
        files.extend(p for p in sorted((VII / folder).glob("*.lean")) if p.name != "All.lean")
    files += [VII / "NoGo" / "Dynamics.lean"]
    files += [
        VII / "Models" / "Finite" / "Phase4" / "DynamicsEnvelope.lean",
        VII / "Models" / "Finite" / "Phase4" / "ScenarioChecks.lean",
    ]
    return sorted(set(files))


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
            candidates.append(root / Path(*name.split(".")[1:]).with_suffix(".lean"))
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
                namespaces.append(ns.group(1)); continue
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
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "--", *paths],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    if result.returncode != 0 or untracked.returncode != 0:
        return [f"GIT_ERROR:{result.stderr.strip()}:{untracked.stderr.strip()}"]
    return sorted(set(result.stdout.splitlines()) | set(untracked.stdout.splitlines()))


def main() -> int:
    checks: list[tuple[str, bool, str]] = []
    errors: list[str] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append((name, bool(condition), detail))
        if not condition:
            errors.append(f"{name}: {detail}")

    all_files = sorted(VII.rglob("*.lean")) + [LEAN / "FoundationsVII.lean"]
    roots = library_roots()
    lexical_ok = True
    import_ok = True
    trust_ok = True
    import_count = 0
    for path in all_files:
        text = path.read_text(encoding="utf-8")
        skeleton, lexical_errors = remove_comments_and_strings(text)
        delims = delimiter_errors(skeleton)
        if lexical_errors or delims:
            lexical_ok = False
            errors.append(f"{path.relative_to(ROOT)}: {lexical_errors + delims}")
        shortcuts = []
        shortcuts += re.findall(r"(?m)^\s*(?:private\s+)?(axiom|opaque|unsafe)\b", skeleton)
        shortcuts += re.findall(r"(?m)^\s*(sorry|admit)\b", skeleton)
        if shortcuts:
            trust_ok = False
            errors.append(f"{path.relative_to(ROOT)}: prohibited VII-owned shortcut {shortcuts[:5]}")
        for match in re.finditer(r"(?m)^\s*import\s+([A-Za-z0-9_.]+)\s*$", skeleton):
            import_count += 1
            if resolve_import(match.group(1), roots) is None:
                import_ok = False
                errors.append(f"{path.relative_to(ROOT)}: unresolved import {match.group(1)}")
    check("lexical_balance", lexical_ok, f"{len(all_files)} VII/root Lean files")
    check("import_closure", import_ok, f"{import_count} import statements")
    check("no_vii_owned_proof_shortcuts", trust_ok, "no sorry/admit/new axiom/opaque/unsafe")

    science_files = phase4_science_files()
    missing_sources = [str(p.relative_to(ROOT)) for p in science_files if not p.is_file()]
    check("phase4_source_surface_present", not missing_sources and len(science_files) == 14,
          f"files={len(science_files)} missing={missing_sources}")
    source_rows = parse_public_declarations(science_files)
    source_names = [name for name, _ in source_rows]
    duplicates = sorted(name for name, count in Counter(source_names).items() if count > 1)
    check("phase4_source_declaration_uniqueness", not duplicates,
          f"rows={len(source_rows)} duplicates={len(duplicates)}")

    registry_rows = read_jsonl(REG / "phase4_public_declarations.jsonl")
    registry_pairs = [(str(row["fully_qualified_name"]), str(row["kind"])) for row in registry_rows]
    parity = sorted(source_rows) == sorted(registry_pairs)
    check("phase4_registry_source_parity", parity,
          f"source={len(source_rows)} registry={len(registry_pairs)}")
    if not parity:
        source_set, registry_set = set(source_rows), set(registry_pairs)
        errors.append(f"registry delta source_only={sorted(source_set-registry_set)[:20]} registry_only={sorted(registry_set-source_set)[:20]}")

    theorem_names = {name for name, kind in source_rows if kind in {"theorem", "lemma", "corollary"}}
    check("required_phase4_theorems", REQUIRED_THEOREMS <= theorem_names,
          f"found={len(REQUIRED_THEOREMS & theorem_names)}/{len(REQUIRED_THEOREMS)}")
    if not REQUIRED_THEOREMS <= theorem_names:
        errors.append(f"missing required theorems: {sorted(REQUIRED_THEOREMS-theorem_names)}")

    print_path = VII / "Trust" / "PrintAxiomsPhase4.lean"
    print_axioms = re.findall(
        r"(?m)^#print axioms\s+([A-Za-z_][A-Za-z0-9_'.]*)\s*$",
        print_path.read_text(encoding="utf-8") if print_path.is_file() else "",
    )
    print_ok = set(print_axioms) == theorem_names and len(print_axioms) == len(set(print_axioms))
    check("print_axioms_exact_phase4_surface", print_ok,
          f"printed={len(print_axioms)} theorems={len(theorem_names)}")

    build_status = read_json(LEAN / "BUILD_STATUS_PHASE4.json")
    expected_kernel = "PASS_EXTERNAL_REPLAY" if build_status.get("kernel_build_status") == "PASS" else "PENDING_EXTERNAL_LEAN_REPLAY"

    candidates = read_jsonl(REG / "phase4_candidate_closure.jsonl")
    candidate_ids = {str(r["candidate_id"]) for r in candidates}
    candidate_ok = (
        candidate_ids == CANDIDATES and len(candidates) == 10
        and all(str(r["phase4_status"]).startswith("TERMINAL_PHASE4_ASSET") for r in candidates)
        and all(int(r["theorem_count"]) > 0 and r["lean_theorems"] for r in candidates)
        and all(r["bounded_witnesses"] and r["finite_envelopes"] for r in candidates)
    )
    check("ten_terminal_candidate_assets", candidate_ok, f"ids={sorted(candidate_ids)}")

    nogos = read_jsonl(REG / "phase4_no_go_closure.jsonl")
    nogo_ids = {str(r["no_go_id"]) for r in nogos}
    nogo_ok = (
        nogo_ids == NO_GOS and len(nogos) == 1
        and all(bool(r["source_declarations_present"]) for r in nogos)
        and all(str(r["theorem"]) in theorem_names for r in nogos)
        and all(all(str(name) in theorem_names for name in r["escape_theorems"]) for r in nogos)
        and all(all(str(name) in theorem_names for name in r["control_theorems"]) for r in nogos)
        and all(r["positive_controls"] and r["failure_scenarios"] for r in nogos)
        and all(str(r["kernel_status"]) == expected_kernel for r in nogos)
    )
    check("ngvii10_with_control_and_escape", nogo_ok, f"ids={sorted(nogo_ids)}")

    targets = read_jsonl(REG / "phase4_formalization_targets.jsonl")
    target_ids = {str(r["target_id"]) for r in targets}
    target_ok = (
        target_ids == TARGETS and len(targets) == 8
        and all("CLOSED" in str(r["phase4_status"]) for r in targets)
        and all(str(r["kernel_status"]) == expected_kernel for r in targets)
        and all(r["phase4_theorems"] for r in targets)
        and all(r["candidate_ids"] for r in targets)
    )
    check("formalization_target_closure", target_ok, f"targets={sorted(target_ids)}")

    decisions = read_jsonl(REG / "phase4_decision_closure.jsonl")
    decision_ids = {str(r["decision_id"]) for r in decisions}
    decision_ok = (
        decision_ids == DECISIONS and len(decisions) == 5
        and all(bool(r["terminal"]) and bool(r["phase4_terminal_ruling"]) for r in decisions)
        and all(bool(r["evidence_present"]) and r["evidence_declarations"] for r in decisions)
        and all(all(str(name) in theorem_names for name in r["evidence_declarations"]) for r in decisions)
    )
    check("five_terminal_dynamic_decisions", decision_ok, f"ids={sorted(decision_ids)}")

    envelopes = read_jsonl(REG / "phase4_finite_envelopes.jsonl")
    envelope_ids = {str(r["family_id"]) for r in envelopes}
    envelope_ok = (
        envelope_ids == ENVELOPES and len(envelopes) == 12
        and sum(int(r["raw_cardinality"]) for r in envelopes) == 55168
        and sum(int(r["canonical_cardinality"]) for r in envelopes) == 55168
        and sum(int(r["accepted_cardinality"]) for r in envelopes) == 14832
        and sum(int(r["rejected_cardinality"]) for r in envelopes) == 40336
        and all(int(r["accepted_cardinality"]) + int(r["rejected_cardinality"]) == int(r["canonical_cardinality"]) for r in envelopes)
    )
    check("twelve_declared_finite_envelopes", envelope_ok, f"ids={sorted(envelope_ids)}")

    witnesses = read_jsonl(ROOT / "science" / "traceability" / "phase4_bounded_witnesses.jsonl")
    witness_ids = {str(r["witness_id"]) for r in witnesses}
    witness_candidates = {str(r["candidate_id"]) for r in witnesses}
    check("thirty_two_bounded_witnesses_cover_all_candidates",
          len(witnesses) == 32 and len(witness_ids) == 32 and witness_candidates == CANDIDATES,
          f"witnesses={len(witness_ids)} candidates={sorted(witness_candidates)}")

    replay = read_json(ROOT / "formalization" / "foundations_vii_lab" / "phase4" / "results" / "primary_fixture_replay.json")
    replay_ok = (
        replay.get("all_pass") is True
        and set(replay.get("scenario_ids", [])) == SCENARIOS
        and set(replay.get("countermodel_ids", [])) == COUNTERMODELS
        and replay.get("scenario_pass_count") == 9
        and replay.get("countermodel_pass_count") == 8
    )
    check("assigned_fixture_replay", replay_ok, "9 scenarios and 8 countermodels pass")

    root_imports = (VII / "All.lean").read_text(encoding="utf-8")
    finite_imports = (VII / "Models" / "Finite" / "All.lean").read_text(encoding="utf-8")
    nogo_imports = (VII / "NoGo" / "All.lean").read_text(encoding="utf-8")
    lakefile = (LEAN / "lakefile.toml").read_text(encoding="utf-8")
    wiring_ok = (
        "import FoundationsVII.Enablement.All" in root_imports
        and "import FoundationsVII.Dynamics.All" in root_imports
        and "import FoundationsVII.NoGo.Dynamics" in nogo_imports
        and "import FoundationsVII.Models.Finite.Phase4.All" in finite_imports
        and 'name = "fvii_phase4_envelopes"' in lakefile
        and 'root = "FoundationsVII.Models.Finite.Phase4.Runner"' in lakefile
    )
    check("phase4_public_and_executable_wiring", wiring_ok,
          "Enablement/Dynamics/NoGo/Phase4 runner")

    runner_text = (VII / "Models" / "Finite" / "Phase4" / "Runner.lean").read_text(encoding="utf-8")
    scenario_text = (VII / "Models" / "Finite" / "Phase4" / "ScenarioChecks.lean").read_text(encoding="utf-8")
    runner_ok = (
        all(f'"P4-E{i:02d}"' in runner_text for i in range(1, 13))
        and "phase4Scenarios" in runner_text and "phase4Countermodels" in runner_text
        and "phase4Scenarios.length = 9" in scenario_text
        and "phase4Countermodels.length = 8" in scenario_text
    )
    check("twelve_family_and_fixture_lean_runner", runner_ok,
          "P4-E01..P4-E12, 9 scenarios, 8 countermodels")

    check("obsolete_duplicate_phase4_envelope_absent",
          not (VII / "Models" / "Finite" / "Phase4" / "EnablementDynamicsEnvelope.lean").exists(),
          "single canonical DynamicsEnvelope module")
    check("phase5_not_executed", not (VII / "Corollaries").exists(),
          "no Phase-5 corollary/final-closure implementation")

    immutable_paths = [
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
    ]
    immutable_changes = git_changed(immutable_paths)
    check("prior_science_and_inherited_surfaces_immutable", not immutable_changes,
          f"changed={immutable_changes[:12]}")

    repo_changes = git_changed(["."])
    paper_changes = [p for p in repo_changes if p.endswith((".tex", ".bib")) or p.startswith(("source/papers/", "paper/", "papers/"))]
    check("no_paper_or_bibliography_work", not paper_changes, f"changed={paper_changes}")

    all_ok = all(ok for _, ok, _ in checks)
    payload = {
        "phase": "FVII-SCI-04",
        "status": "PASS" if all_ok else "FAIL",
        "boundary": "STATIC_SOURCE_AUDIT_NOT_KERNEL_ELABORATION",
        "lean_file_count": len(all_files),
        "phase4_science_file_count": len(science_files),
        "phase4_declaration_count": len(source_rows),
        "phase4_theorem_count": len(theorem_names),
        "import_statement_count": import_count,
        "checks": [
            {"name": name, "status": "PASS" if ok else "FAIL", "detail": detail}
            for name, ok, detail in checks
        ],
        "errors": errors,
    }
    GEN.mkdir(parents=True, exist_ok=True)
    (GEN / "fvii_sci04_static_lean_audit.json").write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

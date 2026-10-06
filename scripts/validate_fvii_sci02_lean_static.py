#!/usr/bin/env python3
"""Static source audit for FVII-SCI-02.

This is deliberately weaker than Lean kernel elaboration. It verifies the
closed source surface, imports, declaration/registry parity, trust hygiene,
phase boundaries, and replay wiring when Lean/Lake are unavailable.
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
BASE_TAG = "vii-science-01"

CANDIDATES = {
    "VII-C001", "VII-C002", "VII-C003", "VII-C004", "VII-C005",
    "VII-C006", "VII-C021", "VII-C022", "VII-C029",
}
NO_GOS = {"NGVII-01", "NGVII-03", "NGVII-04", "NGVII-05", "NGVII-11"}
TARGETS = {"FT01", "FT02", "FT03", "FT04", "FT05", "FT16", "FT17", "FT18"}
REQUIRED_THEOREMS = {
    "FoundationsVII.DomainState.normalForm_eq",
    "FoundationsVII.DomainState.normalForm_idempotent",
    "FoundationsVII.DomainState.recoverability_and_admissibility_are_incomparable",
    "FoundationsVII.DomainState.same_determination_can_have_different_exposure",
    "FoundationsVII.DomainState.ScopeChange.preserves_theory_and_interface",
    "FoundationsVII.DomainState.AuxiliaryRecoveryCertificate.valid_recovery_has_present_operation_and_adapter",
    "FoundationsVII.DomainState.AuxiliaryRecoveryCertificate.absent_operation_blocks_valid_recovery",
    "FoundationsVII.DomainState.AuxiliaryRecoveryCertificate.spurious_rigidity_is_not_a_recovery_certificate",
    "FoundationsVII.TypedAdmissionStep.Lawful.sourced_financed_and_audited",
    "FoundationsVII.TypedAdmissionStep.revocation_clears_current_admissibility_but_preserves_history",
    "FoundationsVII.TypedAdmissionStep.rollback_clears_current_admissibility_but_preserves_history",
    "FoundationsVII.AdmissionReplay.append",
    "FoundationsVII.ReachabilityWitness.operationallyCertified_is_wellFormed",
    "FoundationsVII.ReachabilityWitness.replay_transitions_are_wellFormed",
    "FoundationsVII.AdmissionRegime.no_first_extension_without_seed_or_reachable_generator",
    "FoundationsVII.AdmissionRegime.open_external_provision_authorizes_first_extension",
    "FoundationsVII.NeutralProvisioningCertificate.neutral_provisioning_authorizes_first_extension",
    "FoundationsVII.NeutralProvisioningCertificate.retrospective_stocking_cannot_earn_neutral_credit",
    "FoundationsVII.PackageAccess.common_origin_does_not_imply_shared_access",
    "FoundationsVII.PackageAccess.shared_access_does_not_imply_source_independence",
    "FoundationsVII.LensTransferCase.no_automatic_total_lens_transfer",
    "FoundationsVII.CommitmentUse.retrospective_predicate_cannot_discharge_prospective_certificate",
    "FoundationsVII.CommitmentUse.SameNeutralSeedClass.refl",
    "FoundationsVII.CommitmentUse.SameNeutralSeedClass.symm",
    "FoundationsVII.CommitmentUse.SameNeutralSeedClass.trans",
    "FoundationsVII.CommitmentUse.prospectively_certified_is_neutral_seed_equivalent",
    "FoundationsVII.OperationalProfile.no_occurrence_from_reachability_alone",
    "FoundationsVII.HorizonObservation.bounded_null_does_not_imply_unrestricted_nonoccurrence",
    "FoundationsVII.ObserverOccupancyRecord.unpriced_observer_invalidates_native_formation_credit",
    "FoundationsVII.BudgetEntry.failed_unused_admission_full_refund_is_conserved",
    "FoundationsVII.NoGo.NGVII_01_no_first_extension_without_seed_or_generator",
    "FoundationsVII.NoGo.NGVII_03_no_retrospective_self_certification",
    "FoundationsVII.NoGo.NGVII_04_no_automatic_total_lens_transfer",
    "FoundationsVII.NoGo.NGVII_05_no_unpriced_observer_native_credit",
    "FoundationsVII.NoGo.NGVII_11_no_occurrence_from_reachability_alone",
    "FoundationsVII.Models.Finite.Phase2.origin_raw_labelled_cardinality",
}

DECL_RE = re.compile(
    r"^(?P<private>private\s+)?(?P<kind>structure|inductive|abbrev|def|theorem|lemma|corollary|axiom|opaque)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)"
)
NS_RE = re.compile(r"^namespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*$")
END_RE = re.compile(r"^end(?:\s+([A-Za-z_][A-Za-z0-9_.]*))?\s*$")


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def phase2_science_files() -> list[Path]:
    files = [p for p in sorted((VII / "Access").glob("*.lean")) if p.name != "All.lean"]
    files += [p for p in sorted((VII / "NoGo").glob("*.lean")) if p.name != "All.lean"]
    files += [VII / "Models" / "Finite" / "Phase2" / "AdmissionEnvelope.lean"]
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
                block_depth += 1
                out.extend("  ")
                i += 2
            elif ch == "-" and nxt == "/":
                block_depth -= 1
                out.extend("  ")
                i += 2
            else:
                out.append("\n" if ch == "\n" else " ")
                i += 1
            continue
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            out.append("\n" if ch == "\n" else " ")
            i += 1
            continue
        if ch == "/" and nxt == "-":
            block_depth = 1
            out.extend("  ")
            i += 2
            continue
        if ch == "-" and nxt == "-":
            while i < len(text) and text[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(" ")
            i += 1
            continue
        out.append(ch)
        i += 1
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
        elif ch in ")]}" :
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
                namespaces.append(ns.group(1))
                continue
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
    command = ["git", "diff", "--name-only", BASE_TAG, "--", *paths]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return [f"GIT_ERROR:{result.stderr.strip()}"]
    return [line for line in result.stdout.splitlines() if line]


def main() -> int:
    checks: list[tuple[str, bool, str]] = []
    errors: list[str] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append((name, bool(condition), detail))

    all_files = sorted(VII.rglob("*.lean")) + [LEAN / "FoundationsVII.lean"]
    roots = library_roots()
    lexical_ok = True
    import_ok = True
    trust_ok = True
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
    check("no_vii_owned_proof_shortcuts", trust_ok, "no sorry/admit tactic/new axiom/opaque/unsafe")

    science_files = phase2_science_files()
    source_rows = parse_public_declarations(science_files)
    source_names = [name for name, _ in source_rows]
    source_counts = Counter(source_names)
    duplicates = sorted(name for name, count in source_counts.items() if count > 1)
    check("phase2_source_declaration_uniqueness", not duplicates, f"rows={len(source_rows)} duplicates={len(duplicates)}")
    if duplicates:
        errors.append(f"duplicate Phase-2 public declarations: {duplicates[:20]}")

    registry_rows = read_jsonl(REG / "phase2_public_declarations.jsonl")
    registry_pairs = [(str(row["fully_qualified_name"]), str(row["kind"])) for row in registry_rows]
    parity = sorted(source_rows) == sorted(registry_pairs)
    check("phase2_registry_source_parity", parity, f"source={len(source_rows)} registry={len(registry_pairs)}")
    if not parity:
        source_set, registry_set = set(source_rows), set(registry_pairs)
        errors.append(f"registry delta source_only={sorted(source_set-registry_set)[:20]} registry_only={sorted(registry_set-source_set)[:20]}")

    theorem_names = {name for name, kind in source_rows if kind in {"theorem", "lemma", "corollary"}}
    check("required_phase2_theorems", REQUIRED_THEOREMS <= theorem_names, f"found={len(REQUIRED_THEOREMS & theorem_names)}/{len(REQUIRED_THEOREMS)}")
    if not REQUIRED_THEOREMS <= theorem_names:
        errors.append(f"missing required theorems: {sorted(REQUIRED_THEOREMS-theorem_names)}")

    print_axioms = re.findall(
        r"(?m)^#print axioms\s+([A-Za-z_][A-Za-z0-9_'.]*)\s*$",
        (VII / "Trust" / "PrintAxiomsPhase2.lean").read_text(encoding="utf-8"),
    )
    print_ok = set(print_axioms) == theorem_names and len(print_axioms) == len(set(print_axioms))
    check("print_axioms_exact_phase2_surface", print_ok, f"printed={len(print_axioms)} theorems={len(theorem_names)}")
    if not print_ok:
        errors.append(f"PrintAxioms delta missing={sorted(theorem_names-set(print_axioms))[:20]} extra={sorted(set(print_axioms)-theorem_names)[:20]}")

    candidates = read_jsonl(REG / "phase2_candidate_closure.jsonl")
    candidate_ids = {str(r["candidate_id"]) for r in candidates}
    candidate_ok = (
        candidate_ids == CANDIDATES
        and all(str(r["phase2_status"]).startswith("TERMINAL_PHASE2_ASSET") for r in candidates)
        and all(int(r["theorem_count"]) > 0 for r in candidates)
        and all(r["lean_theorems"] for r in candidates)
    )
    check("nine_terminal_candidate_assets", candidate_ok, f"ids={len(candidate_ids)}")

    nogos = read_jsonl(REG / "phase2_no_go_closure.jsonl")
    nogo_ids = {str(r["no_go_id"]) for r in nogos}
    nogo_ok = (
        nogo_ids == NO_GOS
        and all(bool(r["source_declarations_present"]) for r in nogos)
        and all(r["escape_theorems"] for r in nogos)
        and all(r["positive_controls"] for r in nogos)
    )
    check("five_no_go_fronts_with_escapes", nogo_ok, f"ids={sorted(nogo_ids)}")

    targets = read_jsonl(REG / "phase2_formalization_targets.jsonl")
    target_ids = {str(r["target_id"]) for r in targets}
    ft18 = next((r for r in targets if r["target_id"] == "FT18"), None)
    target_ok = target_ids == TARGETS and ft18 is not None and "ADMISSION_HALF_COMPLETE" in str(ft18["phase2_status"])
    check("formalization_target_closure", target_ok, f"targets={sorted(target_ids)}")

    root_imports = (VII / "All.lean").read_text(encoding="utf-8")
    finite_imports = (VII / "Models" / "Finite" / "All.lean").read_text(encoding="utf-8")
    lakefile = (LEAN / "lakefile.toml").read_text(encoding="utf-8")
    wiring_ok = (
        "import FoundationsVII.Access.All" in root_imports
        and "import FoundationsVII.NoGo.All" in root_imports
        and "import FoundationsVII.Models.Finite.Phase2.All" in finite_imports
        and 'name = "fvii_phase2_envelopes"' in lakefile
        and 'root = "FoundationsVII.Models.Finite.Phase2.Runner"' in lakefile
    )
    check("phase2_public_and_executable_wiring", wiring_ok, "Access/NoGo/finite runner")

    later_dirs = [VII / name for name in ("Join", "Dynamics", "Corollaries")]
    later_absent = not any(path.exists() for path in later_dirs)
    check("later_science_not_executed", later_absent, "no Join/Dynamics/Corollaries implementation directories")

    immutable_paths = [
        "formalization/foundations_v_scaffold",
        "formalization/foundations_vi_scaffold",
        "formalization/_provenance",
        "formalization/lean/FoundationsVII/Core",
        "formalization/lean/FoundationsVII/Prior",
        "formalization/lean/FoundationsVII/Models/Finite/Scenarios.lean",
        "formalization/lean/FoundationsVII/Models/Finite/Countermodels.lean",
        "formalization/lean/FoundationsVII/Models/Finite/Regression.lean",
        "formalization/foundations_vii_lab/fixtures",
    ]
    immutable_changes = git_changed(immutable_paths)
    check("phase1_and_inherited_surfaces_immutable", not immutable_changes, f"changed={immutable_changes[:10]}")

    tex_changes = [p for p in git_changed(["."]) if p.endswith(".tex") or p.endswith(".bib")]
    check("no_paper_or_bibliography_work", not tex_changes, f"changed={tex_changes}")

    runner_text = (VII / "Models" / "Finite" / "Phase2" / "Runner.lean").read_text(encoding="utf-8")
    runner_ok = all(f'"P2-E{i:02d}"' in runner_text for i in range(1, 10)) and "canonical_cardinality" in runner_text
    check("nine_family_lean_runner", runner_ok, "P2-E01..P2-E09 with raw/canonical/accepted/rejected")

    all_ok = all(ok for _, ok, _ in checks)
    payload = {
        "phase": "FVII-SCI-02",
        "status": "PASS" if all_ok else "FAIL",
        "boundary": "STATIC_SOURCE_AUDIT_NOT_KERNEL_ELABORATION",
        "lean_file_count": len(all_files),
        "phase2_science_file_count": len(science_files),
        "phase2_declaration_count": len(source_rows),
        "phase2_theorem_count": len(theorem_names),
        "import_statement_count": import_count,
        "checks": [
            {"name": name, "status": "PASS" if ok else "FAIL", "detail": detail}
            for name, ok, detail in checks
        ],
        "errors": errors,
    }
    GEN.mkdir(parents=True, exist_ok=True)
    (GEN / "fvii_sci02_static_lean_audit.json").write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"FVII-SCI-02 LEAN STATIC VALIDATION: {payload['status']}")
    for name, ok, detail in checks:
        print(f" - {'PASS' if ok else 'FAIL'} {name}: {detail}")
    for error in errors:
        print("   ERROR", error)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

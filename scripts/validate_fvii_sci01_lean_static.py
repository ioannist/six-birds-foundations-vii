#!/usr/bin/env python3
"""Static integrity checks for the FVII-SCI-01 Lean source tree.

This validator is intentionally not a substitute for Lean elaboration.  It
checks the strongest source-level facts available when the requested toolchain
is absent: import closure, balanced lexical delimiters, exact phase ownership,
public object coverage, generated fixture census, adapter anchors, and absence
of forbidden proof shortcuts.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
LEAN_PROJECT = ROOT / "formalization" / "lean"
VII = LEAN_PROJECT / "FoundationsVII"
REG = ROOT / "science" / "registry"
GEN = ROOT / "generated"

EXPECTED_OBJECTS = {
    "DomainState",
    "AdmissionTransition",
    "ProspectiveCommitment",
    "SourceLedger",
    "BudgetLedger",
    "ContactSurface",
    "ContactWitness",
    "InteractionRecord",
    "JoinCandidate",
    "JoinCertificate",
    "JoinObstruction",
    "NonInteractionCertificate",
    "EnablementRecord",
    "ReachabilityWitness",
    "ObserverOccupancyRecord",
}
TERMINAL_CANDIDATES = {"VII-C020", "VII-C023", "VII-C024", "VII-C025"}
DECL_RE = re.compile(r"^(?P<private>private\s+)?(?P<kind>structure|inductive|abbrev|def|theorem|lemma|corollary|axiom|opaque)\s+(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)")
NS_RE = re.compile(r"^namespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*$")
END_RE = re.compile(r"^end(?:\s+([A-Za-z_][A-Za-z0-9_.]*))?\s*$")

EXPECTED_TERMINAL_DECLARATIONS = {
    "FoundationsVII.TransportAuthorization.citation_only_is_not_licensed",
    "FoundationsVII.TransportAuthorization.accepted_complete_bridge_is_licensed",
    "FoundationsVII.TransportAuthorization.accepted_bridge_is_licensed",
    "FoundationsVII.TransportAuthorization.incomplete_bridge_is_not_licensed",
    "FoundationsVII.TransportAuthorization.failed_bridge_is_not_licensed",
    "FoundationsVII.TransportAuthorization.withdrawn_bridge_is_not_licensed",
    "FoundationsVII.BridgeLedger.failed_bridge_not_silently_deleted",
    "FoundationsVII.BridgeLedger.withdrawn_bridge_not_silently_deleted",
    "FoundationsVII.BridgeLedger.withdrawn_entry_requires_sweeps",
    "FoundationsVII.NegativeEvidenceRecord.point_null_does_not_license_unrestricted",
    "FoundationsVII.NegativeEvidenceRecord.bounded_search_does_not_license_unrestricted",
    "FoundationsVII.NegativeEvidenceRecord.exhaustive_closed_finite_licenses_its_closed_family",
    "FoundationsVII.NegativeEvidenceRecord.exhaustive_finite_does_not_license_unrestricted",
    "FoundationsVII.NegativeEvidenceRecord.theorem_impossibility_licenses_under_unrestricted_declared_scope",
    "FoundationsVII.ScienceAssetRecord.theorem_grade_requires_formal_declaration",
    "FoundationsVII.ScienceAssetRecord.corollary_grade_requires_formal_declaration",
    "FoundationsVII.ScienceAssetRecord.external_finite_evidence_does_not_upgrade_to_theorem",
    "FoundationsVII.ScienceAssetRecord.external_finite_evidence_does_not_upgrade_to_corollary",
    "FoundationsVII.ScienceAssetRecord.lean_finite_evidence_does_not_upgrade_to_theorem",
    "FoundationsVII.ScienceAssetRecord.lean_finite_evidence_does_not_upgrade_to_corollary",
    "FoundationsVII.ScienceAssetRecord.normative_specification_requires_payload",
    "FoundationsVII.Models.Finite.phase1_detector_contract_wellFormed",
    "FoundationsVII.Models.Finite.phase1_detector_has_24_scenarios",
    "FoundationsVII.Models.Finite.phase1_detector_has_27_countermodels",
    "FoundationsVII.Models.Finite.phase1_detector_false_positive_cost_exceeds_false_negative",
    "FoundationsVII.Models.Finite.all_scenarios_pass",
    "FoundationsVII.Models.Finite.all_countermodels_pass",
}

DECL_RE = re.compile(
    r"^(?P<private>private\s+)?(?P<kind>structure|inductive|abbrev|def|theorem|lemma|corollary|axiom|opaque)\s+(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)"
)
NS_RE = re.compile(r"^namespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*$")
END_RE = re.compile(r"^end(?:\s+([A-Za-z_][A-Za-z0-9_.]*))?\s*$")


def load_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def remove_comments_and_strings(text: str) -> tuple[str, list[str]]:
    """Return code skeleton and lexical errors, respecting nested block comments."""
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
        elif ch in ")]}":
            if not stack or stack[-1][0] != pairs[ch]:
                errors.append(f"unmatched closing {ch} at offset {pos}")
            else:
                stack.pop()
    errors.extend(f"unclosed {ch} at offset {pos}" for ch, pos in stack)
    return errors


def library_roots() -> dict[str, Path]:
    data = tomllib.loads((LEAN_PROJECT / "lakefile.toml").read_text(encoding="utf-8"))
    roots: dict[str, Path] = {}
    for lib in data.get("lean_lib", []):
        roots[lib["name"]] = (LEAN_PROJECT / lib.get("srcDir", ".")).resolve()
    return roots


def resolve_import(name: str, roots: dict[str, Path]) -> Path | None:
    candidates: list[Path] = []
    for lib_name, root in roots.items():
        if name == lib_name:
            candidates.append(root / f"{lib_name}.lean")
        elif name.startswith(lib_name + "."):
            relative = Path(*name.split("."))
            candidates.append(root / relative.with_suffix(".lean"))
    # Lean can also import a project-local module not matching the library name
    candidates.append(LEAN_PROJECT / Path(*name.split(".")).with_suffix(".lean"))
    for path in candidates:
        if path.exists():
            return path
    return None


def direct_public_declaration_names(files: Iterable[Path]) -> list[str]:
    """Lexically enumerate VII-owned public declarations from source.

    This is deliberately independent of the generated declaration registry so a
    stale registry cannot hide duplicate declarations introduced in source.
    """
    names: list[str] = []
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
            if "." in name:
                names.append(name)
            else:
                prefix = ".".join(namespaces)
                names.append(f"{prefix}.{name}" if prefix else name)
    return names


def source_declarations() -> set[str]:
    path = REG / "phase1_public_declarations.jsonl"
    if not path.exists():
        return set()
    return {str(row["fully_qualified_name"]) for row in load_jsonl(path)}


def raw_public_declarations(files: list[Path]) -> list[str]:
    names: list[str] = []
    for path in files:
        namespaces: list[str] = []
        for raw in path.read_text(encoding="utf-8").splitlines():
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
            if "." in name:
                names.append(name)
            else:
                prefix = ".".join(namespaces)
                names.append(f"{prefix}.{name}" if prefix else name)
    return names


def main() -> int:
    checks: list[tuple[str, bool, str]] = []
    errors: list[str] = []
    files = sorted(VII.rglob("*.lean")) + [LEAN_PROJECT / "FoundationsVII.lean"]
    roots = library_roots()

    lexical_ok = True
    imports_ok = True
    forbidden_ok = True
    import_count = 0
    forbidden_pattern = re.compile(r"\b(sorry|admit|axiom|opaque|unsafe)\b")
    for path in files:
        text = path.read_text(encoding="utf-8")
        skeleton, lexical = remove_comments_and_strings(text)
        local_errors = lexical + delimiter_errors(skeleton)
        if local_errors:
            lexical_ok = False
            errors.extend(f"{path.relative_to(ROOT)}: {msg}" for msg in local_errors)
        forbidden = sorted(set(forbidden_pattern.findall(skeleton)))
        if forbidden:
            forbidden_ok = False
            errors.append(f"{path.relative_to(ROOT)}: forbidden tokens {forbidden}")
        for match in re.finditer(r"(?m)^\s*import\s+([A-Za-z0-9_.]+)\s*$", skeleton):
            import_count += 1
            name = match.group(1)
            if resolve_import(name, roots) is None:
                imports_ok = False
                errors.append(f"{path.relative_to(ROOT)}: unresolved import {name}")
    checks.append(("lexical_balance", lexical_ok, f"{len(files)} Lean files"))
    checks.append(("import_closure", imports_ok, f"{import_count} import statements"))
    checks.append(("no_forbidden_proof_shortcuts", forbidden_ok, "VII-owned source"))

    object_names: set[str] = set()
    for path in (VII / "Core").glob("*.lean"):
        skeleton, _ = remove_comments_and_strings(path.read_text(encoding="utf-8"))
        object_names.update(re.findall(r"(?m)^\s*structure\s+([A-Za-z_][A-Za-z0-9_']*)\b", skeleton))
    object_ok = EXPECTED_OBJECTS <= object_names
    checks.append(("fifteen_public_objects", object_ok, f"found={len(EXPECTED_OBJECTS & object_names)}/15"))
    if not object_ok:
        errors.append(f"missing Phase-1 object structures: {sorted(EXPECTED_OBJECTS - object_names)}")

    adapters = sorted((VII / "Prior").glob("FT[0-9][0-9].lean"))
    adapter_ids = {p.stem for p in adapters}
    expected_adapter_ids = {f"FT{i:02d}" for i in range(1, 21)}
    checks.append(("twenty_adapter_modules", adapter_ids == expected_adapter_ids, f"found={len(adapters)}"))
    if adapter_ids != expected_adapter_ids:
        errors.append(f"adapter module mismatch missing={sorted(expected_adapter_ids-adapter_ids)} extra={sorted(adapter_ids-expected_adapter_ids)}")

    scenario_text = (VII / "Models" / "Finite" / "Scenarios.lean").read_text(encoding="utf-8")
    counter_text = (VII / "Models" / "Finite" / "Countermodels.lean").read_text(encoding="utf-8")
    scenario_defs = len(re.findall(r"(?m)^def scenario\d{2}\b", scenario_text))
    scenario_proofs = len(re.findall(r"(?m)^theorem scenario\d{2}_passes\b", scenario_text))
    counter_defs = len(re.findall(r"(?m)^def countermodel\d{2}\b", counter_text))
    counter_proofs = len(re.findall(r"(?m)^theorem countermodel\d{2}_passes\b", counter_text))
    fixture_ok = (scenario_defs, scenario_proofs, counter_defs, counter_proofs) == (24, 24, 27, 27)
    checks.append(("lean_fixture_census", fixture_ok, f"scenario={scenario_defs}/{scenario_proofs} countermodel={counter_defs}/{counter_proofs}"))

    declarations = source_declarations()
    raw_names = raw_public_declarations(files)
    raw_counts: dict[str, int] = {}
    for name in raw_names:
        raw_counts[name] = raw_counts.get(name, 0) + 1
    raw_duplicates = sorted(name for name, count in raw_counts.items() if count > 1)
    checks.append(("source_declaration_uniqueness", not raw_duplicates, f"declarations={len(raw_names)} duplicates={len(raw_duplicates)}"))
    if raw_duplicates:
        errors.append(f"duplicate source declarations: {raw_duplicates[:20]}")
    registry_parity = set(raw_names) == declarations and len(raw_names) == len(declarations)
    checks.append(("source_registry_parity", registry_parity, f"source={len(raw_names)} registry={len(declarations)}"))
    if not registry_parity:
        errors.append(f"source/registry declaration delta: source_only={sorted(set(raw_names)-declarations)[:20]} registry_only={sorted(declarations-set(raw_names))[:20]}")

    terminal_ok = EXPECTED_TERMINAL_DECLARATIONS <= declarations
    checks.append(("terminal_candidate_declarations", terminal_ok, f"found={len(EXPECTED_TERMINAL_DECLARATIONS & declarations)}/{len(EXPECTED_TERMINAL_DECLARATIONS)}"))
    if not terminal_ok:
        errors.append(f"missing terminal declarations: {sorted(EXPECTED_TERMINAL_DECLARATIONS - declarations)}")

    direct_names = direct_public_declaration_names(files)
    direct_counts: dict[str, int] = {}
    for name in direct_names:
        direct_counts[name] = direct_counts.get(name, 0) + 1
    direct_duplicates = sorted(name for name, count in direct_counts.items() if count > 1)
    checks.append(("unique_direct_source_declarations", not direct_duplicates, f"duplicates={len(direct_duplicates)}"))
    if direct_duplicates:
        errors.append(f"duplicate declarations in VII source: {direct_duplicates[:20]}")

    registry_rows = load_jsonl(REG / "phase1_public_declarations.jsonl") if (REG / "phase1_public_declarations.jsonl").exists() else []
    registry_names = [str(row["fully_qualified_name"]) for row in registry_rows]
    registry_counts: dict[str, int] = {}
    for name in registry_names:
        registry_counts[name] = registry_counts.get(name, 0) + 1
    registry_duplicates = sorted(name for name, count in registry_counts.items() if count > 1)
    checks.append(("unique_public_declaration_names", not registry_duplicates, f"duplicates={len(registry_duplicates)}"))
    if registry_duplicates:
        errors.append(f"duplicate declaration names in registry: {registry_duplicates[:20]}")

    registry_sync = sorted(direct_names) == sorted(registry_names)
    checks.append(("declaration_registry_matches_source", registry_sync, f"source={len(direct_names)} registry={len(registry_names)}"))
    if not registry_sync:
        source_set, registry_set = set(direct_names), set(registry_names)
        errors.append(
            "declaration registry/source mismatch "
            f"missing={sorted(source_set-registry_set)[:10]} extra={sorted(registry_set-source_set)[:10]}"
        )

    theorem_names = sorted(
        str(row["fully_qualified_name"])
        for row in registry_rows
        if str(row.get("kind")) in {"theorem", "lemma", "corollary"}
    )
    print_axioms_path = VII / "Trust" / "PrintAxioms.lean"
    printed_names = []
    if print_axioms_path.exists():
        printed_names = re.findall(
            r"(?m)^#print axioms\s+([A-Za-z_][A-Za-z0-9_'.]*)\s*$",
            print_axioms_path.read_text(encoding="utf-8"),
        )
    print_axioms_exact = sorted(printed_names) == theorem_names and len(printed_names) == len(set(printed_names))
    checks.append(("print_axioms_covers_theorem_surface", print_axioms_exact, f"printed={len(printed_names)} theorems={len(theorem_names)}"))
    if not print_axioms_exact:
        errors.append("PrintAxioms theorem surface is stale, incomplete, or duplicated")

    root_text = (VII / "All.lean").read_text(encoding="utf-8")
    release_scope_ok = (
        "FoundationsVII.Core.All" in root_text
        and "FoundationsVII.Prior.All" in root_text
        and "FoundationsVII.Models.Finite.All" in root_text
        and "Trust" not in root_text
        and not any((VII / name).exists() for name in ("Access", "Join", "Dynamics", "NoGo", "Corollaries"))
    )
    checks.append(("phase1_release_scope", release_scope_ok, "no later-phase public modules"))

    generated_regression_import = "FoundationsVII.Models.Finite.Regression" in (VII / "Models" / "Finite" / "All.lean").read_text(encoding="utf-8")
    checks.append(("finite_regression_imported", generated_regression_import, "Models.Finite.All"))

    all_ok = all(ok for _, ok, _ in checks)
    payload = {
        "phase": "FVII-SCI-01",
        "status": "PASS" if all_ok else "FAIL",
        "lean_files": len(files),
        "import_statements": import_count,
        "checks": [
            {"name": name, "status": "PASS" if ok else "FAIL", "detail": detail}
            for name, ok, detail in checks
        ],
        "errors": errors,
        "boundary": "STATIC_SOURCE_AUDIT_NOT_KERNEL_ELABORATION",
    }
    GEN.mkdir(parents=True, exist_ok=True)
    (GEN / "fvii_sci01_static_lean_audit.json").write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print("FVII-SCI-01 LEAN STATIC VALIDATION:", payload["status"])
    for name, ok, detail in checks:
        print(f" - {'PASS' if ok else 'FAIL'} {name}: {detail}")
    for error in errors:
        print("   ERROR", error)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

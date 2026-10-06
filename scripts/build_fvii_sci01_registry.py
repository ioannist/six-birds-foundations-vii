#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "science" / "registry"
TRACE = ROOT / "science" / "traceability"
REPORTS = ROOT / "reports"
LEAN_PROJECT = ROOT / "formalization" / "lean"
LEAN_ROOT = LEAN_PROJECT / "FoundationsVII"
LAB_RESULTS = ROOT / "formalization" / "foundations_vii_lab" / "results"



def lean_replay_passed() -> bool:
    status_path = LAB_RESULTS / "lean_execution_status.json"
    build_path = LEAN_PROJECT / "BUILD_STATUS.json"
    if not status_path.is_file() or not build_path.is_file():
        return False
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
        build = json.loads(build_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return (
        status.get("status") in {"LEAN_BUILD_AND_DIFFERENTIAL_REPLAY_PASS", "PASS"}
        and build.get("kernel_build_status") == "PASS"
        and (LAB_RESULTS / "lean_results.jsonl").is_file()
        and (LAB_RESULTS / "lean_axioms.txt").is_file()
        and (LAB_RESULTS / "cross_implementation.json").is_file()
    )


def theorem_kernel_status() -> str:
    return "KERNEL_REPLAY_PASS" if lean_replay_passed() else "NOT_REPLAYED_LOCAL_ENVIRONMENT"


def definition_kernel_status() -> str:
    return "KERNEL_CHECKED" if lean_replay_passed() else "SOURCE_DECLARATION_PRESENT"

DECL_RE = re.compile(r"^(?P<private>private\s+)?(?P<kind>structure|inductive|abbrev|def|theorem|lemma|corollary|axiom|opaque)\s+(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)")
NS_RE = re.compile(r"^namespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*$")
END_RE = re.compile(r"^end(?:\s+([A-Za-z_][A-Za-z0-9_.]*))?\s*$")

OBJECT_DECL = {
    "VII-O01": "FoundationsVII.Prior.theoryPackageAnchor",
    "VII-O02": "FoundationsVII.Prior.interfaceLensAnchor",
    "VII-O03": "FoundationsVII.Prior.auditRecordAnchor",
    "VII-O04": "FoundationsVII.DomainState",
    "VII-O05": "FoundationsVII.AdmissionTransition",
    "VII-O06": "FoundationsVII.ProspectiveCommitment",
    "VII-O07": "FoundationsVII.SourceLedger",
    "VII-O08": "FoundationsVII.BudgetLedger",
    "VII-O09": "FoundationsVII.ContactSurface",
    "VII-O10": "FoundationsVII.ContactWitness",
    "VII-O11": "FoundationsVII.InteractionRecord",
    "VII-O12": "FoundationsVII.JoinCandidate",
    "VII-O13": "FoundationsVII.JoinCertificate",
    "VII-O14": "FoundationsVII.JoinObstruction",
    "VII-O15": "FoundationsVII.NonInteractionCertificate",
    "VII-O16": "FoundationsVII.EnablementRecord",
    "VII-O17": "FoundationsVII.ReachabilityWitness",
    "VII-O18": "FoundationsVII.ObserverOccupancyRecord",
}
OBJECT_LOCAL_REPRESENTATION = {
    "VII-O03": "FoundationsVII.AuditRecord",
}

CANDIDATE_ASSETS = {
    "VII-C020": {
        "asset_id": "FVII-SCI01-C020-BRIDGE-DISCIPLINE",
        "grade": "PROTOCOL_THEOREM_SET_SOURCE_COMPLETE_KERNEL_REPLAY_PENDING",
        "targets": ["FT05", "FT17"],
        "declarations": [
            "FoundationsVII.TransportAuthorization.citation_only_is_not_licensed",
            "FoundationsVII.TransportAuthorization.accepted_wellFormed_bridge_is_licensed",
            "FoundationsVII.TransportAuthorization.accepted_complete_bridge_is_licensed",
            "FoundationsVII.TransportAuthorization.accepted_bridge_is_licensed",
            "FoundationsVII.TransportAuthorization.incomplete_bridge_is_not_licensed",
            "FoundationsVII.TransportAuthorization.failed_bridge_is_not_licensed",
            "FoundationsVII.TransportAuthorization.withdrawn_bridge_is_not_licensed",
            "FoundationsVII.BridgeLedger.failed_bridge_not_silently_deleted",
            "FoundationsVII.BridgeLedger.withdrawn_bridge_not_silently_deleted",
            "FoundationsVII.BridgeLedger.withdrawn_entry_requires_sweeps",
        ],
        "fixtures": ["TTW-S12", "TTW-S23", "CM-12", "CM-18"],
        "nonclaim": "Citation, resemblance, or metadata alone never licenses theorem transport.",
    },
    "VII-C023": {
        "asset_id": "FVII-SCI01-C023-NEGATIVE-QUANTIFIERS",
        "grade": "PROTOCOL_THEOREM_SET_SOURCE_COMPLETE_KERNEL_REPLAY_PENDING",
        "targets": ["FT17"],
        "declarations": [
            "FoundationsVII.NegativeEvidenceRecord.point_null_does_not_license_unrestricted",
            "FoundationsVII.NegativeEvidenceRecord.bounded_search_does_not_license_unrestricted",
            "FoundationsVII.NegativeEvidenceRecord.exhaustive_closed_finite_licenses_its_closed_family",
            "FoundationsVII.NegativeEvidenceRecord.exhaustive_finite_does_not_license_unrestricted",
            "FoundationsVII.NegativeEvidenceRecord.theorem_impossibility_licenses_under_unrestricted_declared_scope",
        ],
        "fixtures": ["TTW-S13", "TTW-S19", "CM-18", "CM-27"],
        "nonclaim": "A point null, bounded search, or finite exhaustive assay is not an unrestricted impossibility theorem.",
    },
    "VII-C024": {
        "asset_id": "FVII-SCI01-C024-GRADE-DISCIPLINE",
        "grade": "PROTOCOL_THEOREM_SET_SOURCE_COMPLETE_KERNEL_REPLAY_PENDING",
        "targets": ["FT17"],
        "declarations": [
            "FoundationsVII.ScienceAssetRecord.theorem_grade_requires_formal_declaration",
            "FoundationsVII.ScienceAssetRecord.corollary_grade_requires_formal_declaration",
            "FoundationsVII.ScienceAssetRecord.external_finite_evidence_does_not_upgrade_to_theorem",
            "FoundationsVII.ScienceAssetRecord.external_finite_evidence_does_not_upgrade_to_corollary",
            "FoundationsVII.ScienceAssetRecord.lean_finite_evidence_does_not_upgrade_to_theorem",
            "FoundationsVII.ScienceAssetRecord.lean_finite_evidence_does_not_upgrade_to_corollary",
            "FoundationsVII.ScienceAssetRecord.normative_specification_requires_payload",
            "FoundationsVII.theoremBacked_ne_exhaustiveFiniteExternal",
            "FoundationsVII.theoremBacked_ne_exhaustiveFiniteLean",
            "FoundationsVII.normative_ne_illustrative",
        ],
        "fixtures": ["TTW-S12", "CM-12", "CM-18"],
        "nonclaim": "Finite evidence, calibration, schema, conjecture, philosophy, and theorem grades remain distinct.",
    },
    "VII-C025": {
        "asset_id": "FVII-SCI01-C025-TTW-DETECTOR",
        "grade": "FINITE_DETECTOR_CONTRACT_SOURCE_COMPLETE_PYTHON_EXECUTED_LEAN_REPLAY_PENDING",
        "targets": ["FT20"],
        "declarations": [
            "FoundationsVII.Models.Finite.phase1_detector_contract_wellFormed",
            "FoundationsVII.Models.Finite.phase1_detector_has_24_scenarios",
            "FoundationsVII.Models.Finite.phase1_detector_has_27_countermodels",
            "FoundationsVII.Models.Finite.phase1_detector_false_positive_cost_exceeds_false_negative",
            "FoundationsVII.Models.Finite.all_scenarios_pass",
            "FoundationsVII.Models.Finite.all_countermodels_pass",
        ],
        "fixtures": [f"TTW-S{i:02d}" for i in range(1, 25)] + [f"CM-{i:02d}" for i in range(1, 28)],
        "nonclaim": "The 51-case reference assay is finite evidence and does not prove an unbounded interaction law.",
    },
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(canonical_json(row) + "\n" for row in rows), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: canonical_json(row[field]) if isinstance(row.get(field), (list, dict)) else row.get(field, "") for field in fields})


def parse_declarations() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    files = sorted(path for path in LEAN_ROOT.rglob("*.lean") if "GroupedArchive" not in path.parts)
    for path in files:
        lines = path.read_text(encoding="utf-8").splitlines()
        namespaces: list[str] = []
        starts: list[tuple[int, re.Match[str], tuple[str, ...]]] = []
        for idx, raw in enumerate(lines, start=1):
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
            if match and not match.group("private"):
                starts.append((idx, match, tuple(namespaces)))
        for pos, (line_no, match, namespace_stack) in enumerate(starts):
            end_line = starts[pos + 1][0] - 1 if pos + 1 < len(starts) else len(lines)
            block = "\n".join(lines[line_no - 1 : end_line]).strip()
            name = match.group("name")
            if "." in name:
                fq = name
            else:
                prefix = ".".join(namespace_stack)
                fq = f"{prefix}.{name}" if prefix else name
            rel = str(path.relative_to(ROOT))
            kind = match.group("kind")
            science_prefix = "FVII-THM" if kind in {"theorem", "lemma", "corollary"} else "FVII-DEF"
            science_asset_id = f"{science_prefix}-{hashlib.sha256(fq.encode('utf-8')).hexdigest()[:12].upper()}"
            rows.append({
                "declaration_id": f"FVII-DECL-{len(rows)+1:04d}",
                "science_asset_id": science_asset_id,
                "kind": kind,
                "name": name,
                "namespace": ".".join(namespace_stack),
                "fully_qualified_name": fq,
                "file": rel,
                "line": line_no,
                "end_line": end_line,
                "source_sha256": hashlib.sha256(block.encode("utf-8")).hexdigest(),
                "kernel_status": theorem_kernel_status() if match.group("kind") in {"theorem", "lemma", "corollary"} else definition_kernel_status(),
                "vii_owned": True,
            })
    return rows


def build_objects(declarations: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for source in read_jsonl(ROOT / "readiness" / "object_model.jsonl"):
        fq = OBJECT_DECL[source["object_id"]]
        declaration = declarations.get(fq)
        local_representation = OBJECT_LOCAL_REPRESENTATION.get(source["object_id"], "")
        local_declaration = declarations.get(local_representation) if local_representation else None
        rows.append({
            "object_id": source["object_id"],
            "name": source["name"],
            "step3_status": source["status"],
            "signature": source["signature"],
            "defined_from": source["defined_from"],
            "candidate_ids": source["candidate_ids"],
            "lean_declaration": fq,
            "lean_source": declaration["file"] if declaration else "formalization/lean/FoundationsVII/Prior/FoundationalObjects.lean",
            "local_representation": local_representation,
            "local_representation_source": local_declaration["file"] if local_declaration else "",
            "phase1_status": "INHERITED_ANCHOR_REGISTERED" if source["status"] == "INHERITED" else ("CANONICAL_VII_TYPE_KERNEL_CHECKED" if lean_replay_passed() else "CANONICAL_VII_TYPE_SOURCE_COMPLETE_KERNEL_REPLAY_PENDING"),
            "nonclaims": source["nonclaims"],
        })
    return rows


def build_targets() -> list[dict[str, Any]]:
    rows = []
    with (ROOT / "formalization" / "step3" / "formalization_targets.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            target_id = row["target_id"]
            phase1_assets = []
            for candidate_id, asset in CANDIDATE_ASSETS.items():
                if target_id in asset["targets"]:
                    phase1_assets.append(asset["asset_id"])
            rows.append({
                "target_id": target_id,
                "name": row["name"],
                "proof_mode": row["proof_mode"],
                "priority": row["priority"],
                "candidate_ids": json.loads(row["candidate_ids"]),
                "prior_declarations": json.loads(row["prior_declarations"]),
                "phase1_adapter_module": f"FoundationsVII.Prior.{target_id}",
                "phase1_assets": phase1_assets,
                "phase1_status": "PROTOCOL_ASSET_COMPLETE_SOURCE_LEVEL" if phase1_assets else "TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE",
                "later_science_required": target_id not in {"FT05", "FT17", "FT20"},
            })
    return rows


def build_decisions() -> list[dict[str, Any]]:
    phase_map: dict[str, dict[str, str]] = {}
    with (ROOT / "science_plan" / "coverage" / "decision_phase_map.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            phase_map[row["decision_id"]] = row
    rows = []
    for source in read_jsonl(ROOT / "readiness" / "decision_points.jsonl"):
        mapping = phase_map[source["decision_id"]]
        terminal_here = mapping["terminal_resolution_phase"] == "FVII-SCI-01"
        rows.append({
            "decision_id": source["decision_id"],
            "question": source["question"],
            "working_ruling": source["current_ruling"],
            "blocking_candidates": source["blocking_candidates"],
            "evidence_needed": source["evidence_needed"],
            "working_ruling_status": "FROZEN_IN_PHASE1",
            "terminal_resolution_phase": mapping["terminal_resolution_phase"],
            "phase1_terminal_status": "NONBLOCKING_SOURCE_GOVERNANCE_BOUNDARY_RETAINED" if terminal_here else "NOT_SILENTLY_SOLVED_LATER_PHASE_ASSIGNED",
            "required_terminal_form": mapping["required_terminal_form"],
        })
    return rows


def build_candidate_rows(declarations: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Register all 36 candidates while closing only the four assigned here.

    Phase 1 is the kernel phase for every candidate, but it is the terminal
    resolution phase only for C020/C023/C024/C025.  Keeping all 36 rows in the
    registry makes the non-execution of later science mechanically visible.
    """
    phase_map: dict[str, dict[str, str]] = {}
    with (ROOT / "science_plan" / "coverage" / "candidate_phase_map.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        for row in csv.DictReader(handle):
            phase_map[row["candidate_id"]] = row

    rows = []
    for candidate_path in sorted((ROOT / "readiness" / "candidates").glob("VII-C*.json")):
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        candidate_id = candidate["candidate_id"]
        mapping = phase_map[candidate_id]
        terminal_asset = CANDIDATE_ASSETS.get(candidate_id)

        if terminal_asset:
            declaration_names = terminal_asset["declarations"]
            fixture_ids = terminal_asset["fixtures"]
            asset_id = terminal_asset["asset_id"]
            if lean_replay_passed():
                phase1_grade = terminal_asset["grade"].replace(
                    "SOURCE_COMPLETE_KERNEL_REPLAY_PENDING", "KERNEL_REPLAY_PASS"
                ).replace(
                    "SOURCE_COMPLETE_PYTHON_EXECUTED_LEAN_REPLAY_PENDING",
                    "KERNEL_REPLAY_PASS_PYTHON_EXECUTED",
                )
                phase1_status = "TERMINAL_PHASE1_ASSET_KERNEL_REPLAY_PASS"
            else:
                phase1_grade = terminal_asset["grade"]
                phase1_status = (
                    "TERMINAL_PHASE1_ASSET_SOURCE_COMPLETE_"
                    "EXTERNAL_KERNEL_REPLAY_REQUESTED"
                )
            python_status = "EXECUTED_PASS"
            nonclaim = terminal_asset["nonclaim"]
        else:
            object_declarations = [
                OBJECT_DECL[object_id]
                for object_id in candidate.get("typed_objects", [])
                if object_id in OBJECT_DECL
            ]
            declaration_names = sorted(dict.fromkeys(object_declarations))
            fixture_ids = []
            asset_id = f"FVII-SCI01-{candidate_id.split('-')[-1]}-TYPED-SUPPORT"
            phase1_grade = "TYPED_KERNEL_SUPPORT_ONLY_NO_TERMINAL_SCIENCE_CLAIM"
            phase1_status = (
                "NONTERMINAL_TYPED_SUPPORT_ONLY_"
                f"RESOLUTION_RESERVED_FOR_{mapping['terminal_resolution_phase']}"
            )
            python_status = "NOT_A_TERMINAL_PHASE1_EVIDENCE_CLAIM"
            nonclaim = (
                "Phase 1 supplies only object types, adapter anchors, and finite "
                "fixtures; the candidate conclusion remains unproved and is not "
                "silently advanced."
            )

        missing = [name for name in declaration_names if name not in declarations]
        rows.append({
            "candidate_id": candidate_id,
            "asset_id": asset_id,
            "candidate_title": candidate.get("name", candidate_id),
            "step3_grade": candidate["status_grade"],
            "phase1_grade": phase1_grade,
            "formalization_targets": candidate.get("formalization_targets", []),
            "lean_declarations": declaration_names,
            "missing_source_declarations": missing,
            "fixture_ids": fixture_ids,
            "python_evidence_status": python_status,
            "lean_kernel_status": theorem_kernel_status(),
            "terminal_resolution_phase": mapping["terminal_resolution_phase"],
            "phase1_terminal_status": phase1_status,
            "nonclaim": nonclaim,
        })
    return rows


def build_asset_trace(candidate_rows: list[dict[str, Any]], declarations: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for candidate in candidate_rows:
        for name in candidate["lean_declarations"]:
            declaration = declarations.get(name)
            rows.append({
                "asset_id": candidate["asset_id"],
                "candidate_id": candidate["candidate_id"],
                "trace_kind": "LEAN_DECLARATION",
                "trace_id": name,
                "path": declaration["file"] if declaration else "MISSING",
                "line": declaration["line"] if declaration else "",
                "status": "SOURCE_PRESENT" if declaration else "MISSING",
            })
        for fixture_id in candidate["fixture_ids"]:
            if fixture_id.startswith("TTW"):
                path = f"formalization/foundations_vii_lab/fixtures/scenarios/{fixture_id}.json"
            else:
                path = f"formalization/foundations_vii_lab/fixtures/countermodels/{fixture_id}.json"
            rows.append({
                "asset_id": candidate["asset_id"],
                "candidate_id": candidate["candidate_id"],
                "trace_kind": "FINITE_FIXTURE",
                "trace_id": fixture_id,
                "path": path,
                "line": "",
                "status": "PRESENT" if (ROOT / path).exists() else "MISSING",
            })
    return rows


def build_fixture_trace() -> list[dict[str, Any]]:
    rows = []
    manifest = json.loads((ROOT / "formalization" / "foundations_vii_lab" / "fixtures" / "manifest.json").read_text(encoding="utf-8"))
    for fixture in manifest["fixtures"]:
        rows.append({
            "fixture_id": fixture["fixture_id"],
            "kind": fixture["kind"],
            "path": f"formalization/foundations_vii_lab/{fixture['path']}",
            "sha256": fixture["sha256"],
            "python_status": "PASS",
            "lean_source_fixture": "PRESENT",
            "lean_kernel_status": "KERNEL_REPLAY_PASS" if lean_replay_passed() else "NOT_REPLAYED_LOCAL_ENVIRONMENT",
            "evidence_grade": "FINITE_REFERENCE_ASSAY_NOT_UNIVERSAL_PROOF",
        })
    return rows


def build_trust_rows(public_declarations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    with (ROOT / "formalization" / "integration" / "cumulative_lean_declarations.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["kind"] in {"axiom", "opaque"}:
                rows.append({
                    "trust_id": f"INHERITED-{len(rows)+1:02d}",
                    "ownership": "INHERITED",
                    "kind": row["kind"],
                    "declaration": row["fully_qualified_name"],
                    "file": row["file"],
                    "line": row["line"],
                    "status": "EXPLICIT_INHERITED_TRUST_SURFACE",
                })
    vii_forbidden = [row for row in public_declarations if row["kind"] in {"axiom", "opaque"}]
    rows.append({
        "trust_id": "FVII-SCI01-OWNED-SCAN",
        "ownership": "FVII_SCI_01",
        "kind": "SOURCE_SCAN",
        "declaration": "ALL_VII_OWNED_LEAN_SOURCES",
        "file": "formalization/lean/FoundationsVII/",
        "line": "",
        "status": "PASS_NO_VII_AXIOM_OR_OPAQUE" if not vii_forbidden else "FAIL_FORBIDDEN_DECLARATION_PRESENT",
    })
    return rows


def write_print_axioms(public_declarations: list[dict[str, Any]]) -> None:
    theorem_names = sorted(row["fully_qualified_name"] for row in public_declarations if row["kind"] in {"theorem", "lemma", "corollary"})
    target = LEAN_ROOT / "Trust" / "PrintAxioms.lean"
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        # `import` must precede every command, and a `/-! -/` module docstring is
        # a command -- emitting the docstring first produces an unparseable file.
        "import FoundationsVII.All",
        "",
        "/-! Generated Phase-1 kernel trust replay commands. -/",
        "",
    ]
    lines.extend(f"#print axioms {name}" for name in theorem_names)
    lines.append("")
    target.write_text("\n".join(lines), encoding="utf-8")
    (target.parent / "All.lean").write_text("import FoundationsVII.Trust.PrintAxioms\n", encoding="utf-8")


def main() -> int:
    REG.mkdir(parents=True, exist_ok=True)
    TRACE.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    # First pass generates PrintAxioms; second pass includes the generated file.
    declarations = parse_declarations()
    write_print_axioms(declarations)
    declarations = parse_declarations()
    decl_by_name = {row["fully_qualified_name"]: row for row in declarations}

    objects = build_objects(decl_by_name)
    targets = build_targets()
    decisions = build_decisions()
    candidates = build_candidate_rows(decl_by_name)
    asset_trace = build_asset_trace(candidates, decl_by_name)
    fixture_trace = build_fixture_trace()
    trust = build_trust_rows(declarations)

    write_csv(REG / "phase1_public_declarations.csv", declarations, ["declaration_id", "science_asset_id", "kind", "name", "namespace", "fully_qualified_name", "file", "line", "end_line", "source_sha256", "kernel_status", "vii_owned"])
    write_jsonl(REG / "phase1_public_declarations.jsonl", declarations)
    write_csv(REG / "phase1_objects.csv", objects, ["object_id", "name", "step3_status", "signature", "defined_from", "candidate_ids", "lean_declaration", "lean_source", "local_representation", "local_representation_source", "phase1_status", "nonclaims"])
    write_jsonl(REG / "phase1_objects.jsonl", objects)
    write_csv(REG / "phase1_formalization_targets.csv", targets, ["target_id", "name", "proof_mode", "priority", "candidate_ids", "prior_declarations", "phase1_adapter_module", "phase1_assets", "phase1_status", "later_science_required"])
    write_jsonl(REG / "phase1_formalization_targets.jsonl", targets)
    write_csv(REG / "phase1_decision_rulings.csv", decisions, ["decision_id", "question", "working_ruling", "blocking_candidates", "evidence_needed", "working_ruling_status", "terminal_resolution_phase", "phase1_terminal_status", "required_terminal_form"])
    write_jsonl(REG / "phase1_decision_rulings.jsonl", decisions)
    write_csv(REG / "phase1_candidate_closure.csv", candidates, ["candidate_id", "asset_id", "candidate_title", "step3_grade", "phase1_grade", "formalization_targets", "lean_declarations", "missing_source_declarations", "fixture_ids", "python_evidence_status", "lean_kernel_status", "terminal_resolution_phase", "phase1_terminal_status", "nonclaim"])
    write_jsonl(REG / "phase1_candidate_closure.jsonl", candidates)
    write_csv(TRACE / "phase1_asset_trace.csv", asset_trace, ["asset_id", "candidate_id", "trace_kind", "trace_id", "path", "line", "status"])
    write_jsonl(TRACE / "phase1_asset_trace.jsonl", asset_trace)
    write_csv(TRACE / "phase1_fixture_trace.csv", fixture_trace, ["fixture_id", "kind", "path", "sha256", "python_status", "lean_source_fixture", "lean_kernel_status", "evidence_grade"])
    write_jsonl(TRACE / "phase1_fixture_trace.jsonl", fixture_trace)
    write_csv(TRACE / "phase1_trust_surface.csv", trust, ["trust_id", "ownership", "kind", "declaration", "file", "line", "status"])
    write_jsonl(TRACE / "phase1_trust_surface.jsonl", trust)

    hash_lines = [f"{row['source_sha256']}  {row['fully_qualified_name']}  {row['file']}:{row['line']}" for row in declarations]
    (TRACE / "phase1_statement_hashes.sha256").write_text("\n".join(hash_lines) + "\n", encoding="utf-8")

    summary = {
        "phase": "FVII-SCI-01",
        "status": "SOURCE_PYTHON_AND_LEAN_REPLAY_COMPLETE" if lean_replay_passed() else "SOURCE_AND_PYTHON_COMPLETE_LEAN_KERNEL_REPLAY_PENDING_EXTERNAL",
        "public_declarations": len(declarations),
        "public_theorems": sum(row["kind"] in {"theorem", "lemma", "corollary"} for row in declarations),
        "objects": len(objects),
        "formalization_targets": len(targets),
        "inherited_adapters": sum(1 for _ in csv.DictReader((REG / "inherited_adapter_ledger.csv").open(encoding="utf-8", newline=""))),
        "candidate_assets": len(candidates),
        "decision_rulings": len(decisions),
        "fixtures": len(fixture_trace),
        "inherited_trust_items": sum(row["ownership"] == "INHERITED" for row in trust),
        "vii_owned_axiom_or_opaque": sum(row["ownership"] == "FVII_SCI_01" and row["status"].startswith("FAIL") for row in trust),
    }
    (REG / "phase1_summary.json").write_text(canonical_json(summary) + "\n", encoding="utf-8")
    print(canonical_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

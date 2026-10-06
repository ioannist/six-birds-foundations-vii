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
LEAN_ROOT = ROOT / "formalization" / "lean" / "FoundationsVII"
REG = ROOT / "science" / "registry"
TRACE = ROOT / "science" / "traceability"
THEOREMS = ROOT / "science" / "theorems"
NOGO = ROOT / "science" / "no_go"
LAB2 = ROOT / "formalization" / "foundations_vii_lab" / "phase2" / "results"

CANDIDATE_IDS = ["VII-C001", "VII-C002", "VII-C003", "VII-C004", "VII-C005", "VII-C006", "VII-C021", "VII-C022", "VII-C029"]
CANDIDATE_ASSET_IDS = {
    "VII-C001": "FVII-SCI02-C001-ACCESS-NORMAL-FORM",
    "VII-C002": "FVII-SCI02-C002-ADMISSION-TRANSITIONS",
    "VII-C003": "FVII-SCI02-C003-BOOTSTRAP-OBSTRUCTION",
    "VII-C004": "FVII-SCI02-C004-NEUTRAL-PROVISIONING",
    "VII-C005": "FVII-SCI02-C005-ORIGIN-ACCESS-NONTRANSFER",
    "VII-C006": "FVII-SCI02-C006-PROSPECTIVE-COMMITMENT",
    "VII-C021": "FVII-SCI02-C021-REACHABILITY-NEGATIVE-FORCE",
    "VII-C022": "FVII-SCI02-C022-ACCESS-RIGIDITY",
    "VII-C029": "FVII-SCI02-C029-OBSERVER-OCCUPANCY",
}
CANDIDATE_MODULES = {
    "VII-C001": ["Access/Domain.lean", "Models/Finite/Phase2/AdmissionEnvelope.lean"],
    "VII-C002": ["Access/Transitions.lean", "Access/Replay.lean", "Models/Finite/Phase2/AdmissionEnvelope.lean"],
    "VII-C003": ["Access/Bootstrap.lean", "NoGo/Admission.lean", "Models/Finite/Phase2/AdmissionEnvelope.lean"],
    "VII-C004": ["Access/Bootstrap.lean", "Access/Commitment.lean", "Models/Finite/Phase2/AdmissionEnvelope.lean"],
    "VII-C005": ["Access/Origin.lean", "NoGo/Admission.lean", "Models/Finite/Phase2/AdmissionEnvelope.lean"],
    "VII-C006": ["Access/Commitment.lean", "NoGo/Admission.lean", "Models/Finite/Phase2/AdmissionEnvelope.lean"],
    "VII-C021": ["Access/Reachability.lean", "Access/Replay.lean", "NoGo/Admission.lean", "Models/Finite/Phase2/AdmissionEnvelope.lean"],
    "VII-C022": ["Access/Domain.lean", "Models/Finite/Phase2/AdmissionEnvelope.lean"],
    "VII-C029": ["Access/Observer.lean", "NoGo/Admission.lean", "Models/Finite/Phase2/AdmissionEnvelope.lean"],
}
CANDIDATE_GRADE = {
    "VII-C001": "DEFINITION_AND_THEOREM_SET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C002": "TRANSITION_CALCULUS_AND_REPLAY_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C003": "NO_GO_AND_ESCAPE_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C004": "CERTIFICATE_SCHEMA_AND_ANTI_LAUNDERING_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C005": "NONTRANSFER_THEOREMS_AND_FINITE_COUNTERMODELS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C006": "RELATIONAL_PRECEDENCE_AND_SETTLEMENT_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C021": "REACHABILITY_SEPARATION_AND_NEGATIVE_FORCE_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C022": "ACCESS_SEPARATION_AND_RIGIDITY_CALCULUS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C029": "OBSERVER_OCCUPANCY_NO_GO_AND_LEDGER_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
}
CANDIDATE_NONCLAIM = {
    "VII-C001": "The Boolean normal form is a typed finite representation, not a universal claim that all access phenomena reduce to seven bits.",
    "VII-C002": "A well-typed transition calculus does not establish soundness of an undeclared domain-specific rule.",
    "VII-C003": "The bootstrap obstruction is scoped to a declared closed family and permits admitted seeds, reachable generators, and explicit external provision.",
    "VII-C004": "Neutral credit requires prospective, task-blind, outcome-independent provision; post-hoc stocking and system-generated laundering are excluded.",
    "VII-C005": "Common origin, carrier, or instrument does not establish shared access or source independence; adapter theorems remain necessary.",
    "VII-C006": "The precedence certificate does not assume or construct a universal global clock.",
    "VII-C021": "A bounded null remains horizon-qualified unless family closure and detector power are certified.",
    "VII-C022": "No total order among exposure, recoverability, and admissibility is asserted.",
    "VII-C029": "Observer costs are ledger-relative; omitted resources falsify native/endogenous or zero-cost credit.",
}
NO_GOS = {
    "NGVII-01": {
        "name": "No first extension without seed or reachable generator",
        "theorem": "FoundationsVII.NoGo.NGVII_01_no_first_extension_without_seed_or_generator",
        "escapes": ["FoundationsVII.NoGo.NGVII_01_escape_admitted_seed", "FoundationsVII.NoGo.NGVII_01_escape_reachable_generator", "FoundationsVII.NoGo.NGVII_01_escape_open_external_provision"],
        "failure": "TTW-S01", "controls": ["TTW-S02"], "candidates": ["VII-C003"],
        "scope": "Declared closed admission regime and declared permitted-first-extension family.",
    },
    "NGVII-03": {
        "name": "No retrospective self-certification",
        "theorem": "FoundationsVII.NoGo.NGVII_03_no_retrospective_self_certification",
        "escapes": ["FoundationsVII.NoGo.NGVII_03_escape_prospective_certificate"],
        "failure": "TTW-S04", "controls": ["TTW-S03"], "candidates": ["VII-C006"],
        "scope": "An explicit event-precedence relation; no global clock assumption.",
    },
    "NGVII-04": {
        "name": "No automatic total-lens transfer",
        "theorem": "FoundationsVII.NoGo.NGVII_04_no_automatic_total_lens_transfer",
        "escapes": ["FoundationsVII.NoGo.NGVII_04_escape_certified_adapter"],
        "failure": "TTW-S23", "controls": ["TTW-S08"], "candidates": ["VII-C005"],
        "scope": "Total source lens transported to a partial target without a certified adapter.",
    },
    "NGVII-05": {
        "name": "No unpriced observer-native formation credit",
        "theorem": "FoundationsVII.NoGo.NGVII_05_no_unpriced_observer_native_credit",
        "escapes": ["FoundationsVII.NoGo.NGVII_05_escape_external_observer", "FoundationsVII.NoGo.NGVII_05_escape_zero_occupancy"],
        "failure": "TTW-S22", "controls": ["TTW-S02"], "candidates": ["VII-C029"],
        "scope": "Native/endogenous credit with positive occupancy that exceeds charged occupancy.",
    },
    "NGVII-11": {
        "name": "No occurrence from reachability alone",
        "theorem": "FoundationsVII.NoGo.NGVII_11_no_occurrence_from_reachability_alone",
        "escapes": ["FoundationsVII.NoGo.NGVII_11_escape_fired_occurrence"],
        "failure": "TTW-S20", "controls": ["TTW-S21"], "candidates": ["VII-C021"],
        "scope": "Operational profiles satisfying the declared execution/reachability/firing implication spine.",
    },
}

DECL_RE = re.compile(r"^(?P<private>private\s+)?(?P<kind>structure|inductive|abbrev|def|theorem|lemma|corollary|axiom|opaque)\s+(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)")
NS_RE = re.compile(r"^namespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*$")
END_RE = re.compile(r"^end(?:\s+([A-Za-z_][A-Za-z0-9_.]*))?\s*$")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(canonical(row) + "\n" for row in rows), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: canonical(row[field]) if isinstance(row.get(field), (list, dict)) else row.get(field, "") for field in fields})


def source_files() -> list[Path]:
    files: list[Path] = []
    files.extend(path for path in sorted((LEAN_ROOT / "Access").glob("*.lean")) if path.name != "All.lean")
    files.extend(path for path in sorted((LEAN_ROOT / "NoGo").glob("*.lean")) if path.name != "All.lean")
    files.append(LEAN_ROOT / "Models" / "Finite" / "Phase2" / "AdmissionEnvelope.lean")
    return files


def parse_declarations() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in source_files():
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
            fq = name if "." in name else ".".join((*namespace_stack, name))
            kind = match.group("kind")
            rel = path.relative_to(LEAN_ROOT).as_posix()
            statement = block.split(":=", 1)[0].strip()
            asset_prefix = "FVII-SCI02-THM" if kind in {"theorem", "lemma", "corollary"} else "FVII-SCI02-DEF"
            rows.append({
                "declaration_id": f"FVII-SCI02-DECL-{len(rows)+1:04d}",
                "science_asset_id": f"{asset_prefix}-{hashlib.sha256(fq.encode()).hexdigest()[:12].upper()}",
                "kind": kind,
                "name": name,
                "fully_qualified_name": fq,
                "file": f"formalization/lean/FoundationsVII/{rel}",
                "line": line_no,
                "end_line": end_line,
                "statement_sha256": hashlib.sha256(statement.encode()).hexdigest(),
                "source_block_sha256": hashlib.sha256(block.encode()).hexdigest(),
                "kernel_status": "PENDING_EXTERNAL_LEAN_REPLAY" if kind in {"theorem", "lemma", "corollary"} else "SOURCE_DECLARATION_PRESENT",
                "trust_status": "NO_VII_OWNED_AXIOM_OR_OPAQUE_IN_SOURCE",
            })
    return rows


def declaration_candidates(row: dict[str, Any]) -> list[str]:
    rel = row["file"].split("FoundationsVII/", 1)[1]
    candidates = [cid for cid, modules in CANDIDATE_MODULES.items() if rel in modules]
    name = row["fully_qualified_name"]
    if "NGVII_01" in name:
        return ["VII-C003"]
    if "NGVII_03" in name:
        return ["VII-C006"]
    if "NGVII_04" in name:
        return ["VII-C005"]
    if "NGVII_05" in name:
        return ["VII-C029"]
    if "NGVII_11" in name:
        return ["VII-C021"]
    # Tighten finite-family assignments by declaration family.
    family_map = {
        "AccessCase": ["VII-C001", "VII-C022"], "access": ["VII-C001", "VII-C022"],
        "TransitionCase": ["VII-C002", "VII-C021"], "transition": ["VII-C002", "VII-C021"],
        "BootstrapCase": ["VII-C003"], "bootstrap": ["VII-C003"],
        "CommitmentCase": ["VII-C004", "VII-C006"], "commitment": ["VII-C004", "VII-C006"],
        "OriginCase": ["VII-C005"], "origin": ["VII-C005"],
        "TotalityCase": ["VII-C005"], "totality": ["VII-C005"],
        "HorizonCase": ["VII-C021"], "horizon": ["VII-C021"],
        "ObserverCase": ["VII-C029"], "observer": ["VII-C029"],
        "SettlementCase": ["VII-C029"], "settlement": ["VII-C029"],
    }
    if "Models.Finite.Phase2" in name:
        exact_finite = {
            "FoundationsVII.Models.Finite.Phase2.native_credit_requires_priced_occupancy": ["VII-C029"],
            "FoundationsVII.Models.Finite.Phase2.negative_force_requires_closed_powerful_complete_null": ["VII-C021"],
            "FoundationsVII.Models.Finite.Phase2.no_retrospective_self_certification_exhaustive": ["VII-C006"],
            "FoundationsVII.Models.Finite.Phase2.settled_failures_conserve_declared_budget": ["VII-C029"],
            "FoundationsVII.Models.Finite.Phase2.source_independence_is_complementary_to_same_origin_in_canonical_family": ["VII-C005"],
            "FoundationsVII.Models.Finite.Phase2.totality_transfer_requires_adapter_on_partial_targets": ["VII-C005"],
            "FoundationsVII.Models.Finite.Phase2.coherent_access_cases_respect_implication_spine": ["VII-C001", "VII-C022"],
            "FoundationsVII.Models.Finite.Phase2.coherent_transitions_respect_operational_spine": ["VII-C002", "VII-C021"],
            "FoundationsVII.Models.Finite.Phase2.bootstrap_law_exhaustive": ["VII-C003"],
        }
        if name in exact_finite:
            return exact_finite[name]
        for token, cids in family_map.items():
            if token in name:
                return cids
        return []
    return sorted(set(candidates))


def build_candidate_rows(declarations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_candidate: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for declaration in declarations:
        for cid in declaration_candidates(declaration):
            by_candidate[cid].append(declaration)
    rows = []
    for cid in CANDIDATE_IDS:
        dossier = json.loads((ROOT / "readiness" / "candidates" / f"{cid}.json").read_text(encoding="utf-8"))
        decls = sorted(by_candidate[cid], key=lambda r: r["fully_qualified_name"])
        theorem_decls = [r["fully_qualified_name"] for r in decls if r["kind"] in {"theorem", "lemma", "corollary"}]
        definition_decls = [r["fully_qualified_name"] for r in decls if r["kind"] not in {"theorem", "lemma", "corollary"}]
        trace = dossier["source_trace"]
        rows.append({
            "candidate_id": cid,
            "asset_id": CANDIDATE_ASSET_IDS[cid],
            "name": dossier["name"],
            "step3_status": dossier["proof_status"],
            "phase2_status": "TERMINAL_PHASE2_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
            "phase2_grade": CANDIDATE_GRADE[cid],
            "formalization_targets": dossier["formalization_targets"],
            "lean_theorems": theorem_decls,
            "lean_definitions": definition_decls,
            "theorem_count": len(theorem_decls),
            "definition_count": len(definition_decls),
            "positive_scenarios": dossier["positive_model"],
            "null_scenarios": dossier["null_models"],
            "countermodels": dossier["countermodels"],
            "bounded_witnesses": [r["witness_id"] for r in read_jsonl(LAB2 / "canonical_witnesses.jsonl") if r["candidate_id"] == cid],
            "source_support_count": len(trace["supporting_claim_ids"]),
            "source_boundary_count": len(trace["boundary_claim_ids"]),
            "source_open_count": len(trace["open_problem_ids"]),
            "source_bridge_ids": trace["bridge_ids"],
            "source_law_or_no_go_ids": trace["law_or_no_go_ids"],
            "nonclaim": CANDIDATE_NONCLAIM[cid],
        })
    return rows


def build_no_go_rows(declarations: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for no_go_id, spec in NO_GOS.items():
        names = [spec["theorem"], *spec["escapes"]]
        rows.append({
            "no_go_id": no_go_id,
            "asset_id": f"FVII-SCI02-{no_go_id}",
            "name": spec["name"],
            "scope": spec["scope"],
            "theorem": spec["theorem"],
            "escape_theorems": spec["escapes"],
            "failure_scenario": spec["failure"],
            "positive_controls": spec["controls"],
            "candidate_ids": spec["candidates"],
            "source_declarations_present": all(name in declarations for name in names),
            "kernel_status": "PENDING_EXTERNAL_LEAN_REPLAY",
            "terminal_status": "SOURCE_COMPLETE_WITH_EXACT_ESCAPE_THEOREM",
            "nonclaim": "The no-go has only the displayed typed hypotheses and does not license stronger transfer or universalization.",
        })
    return rows


def build_target_rows(candidate_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    target_specs = {
        "FT01": ("Finite access-status data model", "CLOSED_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"),
        "FT02": ("Admission reachability graph and occurrence separation", "CLOSED_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"),
        "FT03": ("Bootstrap obstruction", "CLOSED_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"),
        "FT04": ("Prospective commitment timestamp/budget record", "CLOSED_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"),
        "FT05": ("Source/provenance and transport discipline", "CLOSED_CUMULATIVE_PHASE1_PHASE2_SOURCE_COMPLETE"),
        "FT16": ("Budget and observer occupancy accounting", "CLOSED_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"),
        "FT17": ("Negative quantifier and claim-grade rules", "CLOSED_CUMULATIVE_PHASE1_PHASE2_SOURCE_COMPLETE"),
        "FT18": ("No-free-access/no-free-join lemmas", "ADMISSION_HALF_COMPLETE_JOIN_HALF_RESERVED_FOR_FVII_SCI_03"),
    }
    rows = []
    for target_id, (name, status) in target_specs.items():
        cands = [r["candidate_id"] for r in candidate_rows if target_id in r["formalization_targets"]]
        decls = sorted({d for r in candidate_rows if target_id in r["formalization_targets"] for d in r["lean_theorems"]})
        if target_id == "FT18":
            decls = sorted(set(decls) | {
                "FoundationsVII.TypedAdmissionStep.Lawful.sourced_financed_and_audited",
                "FoundationsVII.ObserverOccupancyRecord.unpriced_observer_invalidates_native_formation_credit",
            })
            cands = sorted(set(cands) | {"VII-C002", "VII-C029"})
        rows.append({
            "target_id": target_id,
            "name": name,
            "candidate_ids": cands,
            "phase2_theorems": decls,
            "phase2_status": status,
            "kernel_status": "PENDING_EXTERNAL_LEAN_REPLAY",
        })
    return rows


def write_candidate_dossiers(rows: list[dict[str, Any]]) -> None:
    THEOREMS.mkdir(parents=True, exist_ok=True)
    for row in rows:
        lines = [
            f"# {row['candidate_id']} — {row['name']}", "",
            f"**Phase-2 asset:** `{row['asset_id']}`  ",
            f"**Terminal status:** `{row['phase2_status']}`  ",
            f"**Grade:** `{row['phase2_grade']}`", "",
            "## Formal surface", "",
            f"- Definitions: {row['definition_count']}",
            f"- Theorems/lemmas/corollaries: {row['theorem_count']}",
            f"- Formalization targets: {', '.join(row['formalization_targets'])}",
            f"- Positive scenarios: {', '.join(row['positive_scenarios']) or 'none'}",
            f"- Null/control scenarios: {', '.join(row['null_scenarios']) or 'none'}",
            f"- Countermodels: {', '.join(row['countermodels']) or 'none'}",
            f"- New bounded witnesses: {', '.join(row['bounded_witnesses']) or 'none'}", "",
            "## Public theorem declarations", "",
        ]
        lines.extend(f"- `{name}`" for name in row["lean_theorems"])
        lines.extend(["", "## Scientific boundary", "", row["nonclaim"], "",
            "The source proof is complete at the Lean text level. Kernel elaboration and `#print axioms` replay remain an explicit external execution gate.", ""])
        (THEOREMS / f"{row['candidate_id']}.md").write_text("\n".join(lines), encoding="utf-8")


def write_no_go_dossiers(rows: list[dict[str, Any]]) -> None:
    NOGO.mkdir(parents=True, exist_ok=True)
    for row in rows:
        lines = [
            f"# {row['no_go_id']} — {row['name']}", "",
            f"**Asset:** `{row['asset_id']}`  ",
            f"**Status:** `{row['terminal_status']}`", "",
            "## Exact scope", "", row["scope"], "",
            "## Theorem", "", f"- `{row['theorem']}`", "",
            "## Escape/positive theorems", "",
        ]
        lines.extend(f"- `{name}`" for name in row["escape_theorems"])
        lines.extend(["", "## Finite controls", "",
            f"- Failure witness: `{row['failure_scenario']}`",
            f"- Positive controls: {', '.join(f'`{x}`' for x in row['positive_controls'])}", "",
            "## Nonclaim", "", row["nonclaim"], ""])
        (NOGO / f"{row['no_go_id']}.md").write_text("\n".join(lines), encoding="utf-8")


def write_print_axioms(theorems: list[dict[str, Any]]) -> None:
    path = LEAN_ROOT / "Trust" / "PrintAxiomsPhase2.lean"
    lines = ["import FoundationsVII.All", "",
             "/-! Generated FVII-SCI-02 trust replay surface. -/", ""]
    lines.extend(f"#print axioms {row['fully_qualified_name']}" for row in sorted(theorems, key=lambda r: r["fully_qualified_name"]))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    declarations = parse_declarations()
    for row in declarations:
        row["candidate_ids"] = declaration_candidates(row)
    declaration_map = {row["fully_qualified_name"]: row for row in declarations}
    candidates = build_candidate_rows(declarations)
    no_gos = build_no_go_rows(declaration_map)
    targets = build_target_rows(candidates)
    theorems = [row for row in declarations if row["kind"] in {"theorem", "lemma", "corollary"}]
    envelopes = read_jsonl(LAB2 / "envelopes.jsonl")
    witnesses = read_jsonl(LAB2 / "canonical_witnesses.jsonl")

    write_jsonl(REG / "phase2_public_declarations.jsonl", declarations)
    write_csv(REG / "phase2_public_declarations.csv", declarations, list(declarations[0]))
    write_jsonl(REG / "phase2_theorem_catalog.jsonl", theorems)
    write_csv(REG / "phase2_theorem_catalog.csv", theorems, list(theorems[0]))
    write_jsonl(REG / "phase2_candidate_closure.jsonl", candidates)
    write_csv(REG / "phase2_candidate_closure.csv", candidates, list(candidates[0]))
    write_jsonl(REG / "phase2_no_go_closure.jsonl", no_gos)
    write_csv(REG / "phase2_no_go_closure.csv", no_gos, list(no_gos[0]))
    write_jsonl(REG / "phase2_formalization_targets.jsonl", targets)
    write_csv(REG / "phase2_formalization_targets.csv", targets, list(targets[0]))
    write_jsonl(REG / "phase2_finite_envelopes.jsonl", envelopes)
    write_csv(REG / "phase2_finite_envelopes.csv", envelopes, list(envelopes[0]))
    write_jsonl(TRACE / "phase2_bounded_witnesses.jsonl", witnesses)
    write_csv(TRACE / "phase2_bounded_witnesses.csv", witnesses, list(witnesses[0]))

    trace_rows = []
    for candidate in candidates:
        for name in candidate["lean_theorems"] + candidate["lean_definitions"]:
            decl = declaration_map[name]
            trace_rows.append({
                "asset_id": candidate["asset_id"], "candidate_id": candidate["candidate_id"],
                "trace_kind": "LEAN_DECLARATION", "trace_id": name,
                "path": decl["file"], "line": decl["line"], "sha256": decl["source_block_sha256"],
            })
        for fixture_id in candidate["positive_scenarios"] + candidate["null_scenarios"] + candidate["countermodels"] + candidate["bounded_witnesses"]:
            if fixture_id.startswith("TTW"):
                path = f"formalization/foundations_vii_lab/fixtures/scenarios/{fixture_id}.json"
            elif fixture_id.startswith("CM"):
                path = f"formalization/foundations_vii_lab/fixtures/countermodels/{fixture_id}.json"
            else:
                path = f"formalization/foundations_vii_lab/phase2/witnesses/{fixture_id}.json"
            trace_rows.append({
                "asset_id": candidate["asset_id"], "candidate_id": candidate["candidate_id"],
                "trace_kind": "FINITE_WITNESS", "trace_id": fixture_id,
                "path": path, "line": "", "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
            })
    write_jsonl(TRACE / "phase2_asset_trace.jsonl", trace_rows)
    write_csv(TRACE / "phase2_asset_trace.csv", trace_rows, list(trace_rows[0]))

    hashes = [f"{row['statement_sha256']}  {row['fully_qualified_name']}" for row in theorems]
    (TRACE / "phase2_statement_hashes.sha256").write_text("\n".join(sorted(hashes)) + "\n", encoding="utf-8")
    write_print_axioms(theorems)
    write_candidate_dossiers(candidates)
    write_no_go_dossiers(no_gos)

    summary = {
        "phase": "FVII-SCI-02",
        "stage": "COMPLETE_SOURCE_LEVEL_EXTERNAL_LEAN_REPLAY_PENDING",
        "terminal_candidate_count": len(candidates),
        "no_go_count": len(no_gos),
        "formalization_target_count": len(targets),
        "phase2_declaration_count": len(declarations),
        "phase2_theorem_count": len(theorems),
        "finite_envelope_count": len(envelopes),
        "bounded_witness_count": len(witnesses),
        "python_summary": json.loads((LAB2 / "summary.json").read_text(encoding="utf-8")),
        "lean_kernel_status": "PENDING_EXTERNAL_LEAN_REPLAY_NONBLOCKING_BY_OWNER_AUTHORIZATION",
        "no_paper_work": True,
    }
    (REG / "phase2_summary.json").write_text(canonical(summary) + "\n", encoding="utf-8")
    print(canonical(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

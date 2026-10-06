#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "formalization" / "lean" / "FoundationsVII"
REG = ROOT / "science" / "registry"
TRACE = ROOT / "science" / "traceability"
THEOREMS = ROOT / "science" / "theorems"
NOGO = ROOT / "science" / "no_go"
DECISIONS = ROOT / "science" / "decisions"
LAB4 = ROOT / "formalization" / "foundations_vii_lab" / "phase4" / "results"

CANDIDATE_IDS = [
    "VII-C012", "VII-C013", "VII-C014", "VII-C015", "VII-C017",
    "VII-C018", "VII-C027", "VII-C028", "VII-C032", "VII-C034",
]

ASSET_IDS = {
    "VII-C012": "FVII-SCI04-C012-ENABLEMENT-ATTRIBUTION",
    "VII-C013": "FVII-SCI04-C013-ENDOGENOUS-CRITERION",
    "VII-C014": "FVII-SCI04-C014-BIRTH-PARTICIPANT-CLASSIFICATION",
    "VII-C015": "FVII-SCI04-C015-TRANSMISSION-DESCENT-FIDELITY",
    "VII-C017": "FVII-SCI04-C017-ORDER-RESIDUE-HOLONOMY",
    "VII-C018": "FVII-SCI04-C018-CONFLUENCE-SEED-DEPENDENCE",
    "VII-C027": "FVII-SCI04-C027-ENABLEMENT-COMPOSITION",
    "VII-C028": "FVII-SCI04-C028-PRIMITIVE-ALGEBRA-DECISION",
    "VII-C032": "FVII-SCI04-C032-ARROW-CROSS-TIME",
    "VII-C034": "FVII-SCI04-C034-ENABLEMENT-DESCENT-SEPARATION",
}

GRADES = {
    "VII-C012": "SOURCE_TYPED_ENABLEMENT_ATTRIBUTION_CALCULUS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C013": "EXACT_DECLARED_BOUNDARY_ENDOGENOUS_CRITERION_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C014": "BIRTH_RELATION_PARTICIPANT_CLASSIFICATION_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C015": "TYPED_TRANSMISSION_DESCENT_FIDELITY_AND_CAUSAL_SEPARATION_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C017": "ORDER_RESIDUE_AND_INTERACTION_HOLONOMY_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C018": "DECLARED_FINITE_CONFLUENCE_AND_SEED_DEPENDENCE_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C027": "CONDITIONAL_ENABLEMENT_COMPOSITION_AND_RESOURCE_DEBT_LAWS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C028": "FULL_PRIMITIVE_ALGEBRA_DEFERRED_SMALL_RESOURCE_FRAGMENT_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C032": "INDEPENDENT_DRIVE_ARROW_AND_CROSS_TIME_WITNESS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C034": "CONSTRUCTIVE_ENABLEMENT_WITHOUT_DESCENT_AND_NECESSARY_INSUFFICIENT_SEPARATIONS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
}

NONCLAIMS = {
    "VII-C012": "Attribution records provenance and execution responsibility; it does not by itself establish descent, sufficiency, causation, or endogeny.",
    "VII-C013": "Endogenous means carried, reachable, executed, audited, budgeted, and source-closed at the declared boundary; it does not mean uncaused or environmentally isolated.",
    "VII-C014": "Contact may remain relation-only. A newly credited participant requires closure survival and objecthood rather than contact alone.",
    "VII-C015": "Faithful downward structural selection is not automatically a top-down causal channel and cannot create an absent lower-carrier fact without an explicit insertion source.",
    "VII-C017": "Order residue and holonomy are route effects on one typed target; neither supplies directionality.",
    "VII-C018": "Confluence is proved only for the declared closed finite system, and seed dependence is separated from presentation-only differences.",
    "VII-C027": "Composable enablement accumulates cost and residual debt, but composed enablement does not imply transitive causation without a separate causal-chain certificate.",
    "VII-C028": "The full generators-and-relations program remains deferred. The landed resource-delta fragment does not establish a complete universal interaction algebra.",
    "VII-C032": "Holonomy alone carries zero arrow credit. Cross-time contact uses explicit synchronization or partial-order witnesses and assumes no universal simultaneity.",
    "VII-C034": "The constructive separations show possibility and non-implication; they do not deny that some enablement instances also descend or are sufficient.",
}

MODULES = {
    "VII-C012": ["Enablement/Attribution.lean"],
    "VII-C013": ["Enablement/Endogenous.lean"],
    "VII-C014": ["Enablement/Birth.lean"],
    "VII-C015": ["Dynamics/Transmission.lean", "Dynamics/ResidualFlow.lean"],
    "VII-C017": ["Dynamics/Holonomy.lean"],
    "VII-C018": ["Dynamics/Confluence.lean"],
    "VII-C027": ["Enablement/Composition.lean", "Dynamics/ResidualFlow.lean"],
    "VII-C028": ["Dynamics/PrimitiveAlgebra.lean"],
    "VII-C032": ["Dynamics/Holonomy.lean", "Dynamics/CrossTime.lean", "NoGo/Dynamics.lean"],
    "VII-C034": ["Enablement/Separation.lean"],
}

ENVELOPE_CANDIDATES = {
    "P4-E01": ["VII-C012"],
    "P4-E02": ["VII-C013"],
    "P4-E03": ["VII-C014"],
    "P4-E04": ["VII-C015"],
    "P4-E05": ["VII-C034"],
    "P4-E06": ["VII-C027"],
    "P4-E07": ["VII-C018"],
    "P4-E08": ["VII-C018"],
    "P4-E09": ["VII-C017"],
    "P4-E10": ["VII-C017", "VII-C032"],
    "P4-E11": ["VII-C032"],
    "P4-E12": ["VII-C028"],
}
CANDIDATE_ENVELOPES = {
    cid: sorted(fid for fid, cids in ENVELOPE_CANDIDATES.items() if cid in cids)
    for cid in CANDIDATE_IDS
}

FINITE_PREFIXES = {
    "VII-C012": ("Attribution", "attribution"),
    "VII-C013": ("Endogenous", "endogenous"),
    "VII-C014": ("Birth", "birth"),
    "VII-C015": ("Transmission", "transmission"),
    "VII-C017": ("Holonomy", "holonomy", "Arrow", "arrow", "finite_holonomy"),
    "VII-C018": ("Confluence", "confluence", "Seed", "seed"),
    "VII-C027": ("Composition", "composition"),
    "VII-C028": ("Algebra", "algebra"),
    "VII-C032": ("Arrow", "arrow", "CrossTime", "crossTime", "cross_time", "finite_driven", "finite_holonomy"),
    "VII-C034": ("Separation", "separation"),
}

NO_GOS = {
    "NGVII-10": {
        "name": "No arrow from holonomy alone",
        "theorem": "FoundationsVII.NoGo.NGVII_10_no_arrow_from_holonomy_alone",
        "escapes": ["FoundationsVII.NoGo.NGVII_10_escape_independent_driven_arrow"],
        "controls": ["FoundationsVII.NoGo.NGVII_10_holonomy_zero_arrow_control"],
        "failures": ["TTW-S17"],
        "positive_controls": ["TTW-S18"],
        "candidates": ["VII-C017", "VII-C032"],
        "scope": "The declared holonomy/drive/path-asymmetry/reversal/budget/audit profile.",
    }
}

TARGETS = {
    "FT11": ("Enablement record and composition", "CLOSED_ENABLEMENT_ATTRIBUTION_SEPARATION_AND_COMPOSITION_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"),
    "FT12": ("Endogenous generation and birth", "CLOSED_EXACT_ENDOGENOUS_AND_BIRTH_CLASSIFICATION_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"),
    "FT13": ("Transmission and descent fidelity", "CLOSED_TYPED_TRANSMISSION_DESCENT_AND_SEPARATION_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"),
    "FT14": ("Confluence, seed dependence, and algebra readiness", "CLOSED_FINITE_CONFLUENCE_AND_SEED_THEOREMS_FULL_ALGEBRA_TERMINALLY_DEFERRED"),
    "FT15": ("Holonomy, arrow, and cross-time contact", "CLOSED_HOLONOMY_ARROW_SEPARATION_AND_CROSS_TIME_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"),
    "FT16": ("Dynamic source and budget accounting", "CLOSED_CUMULATIVE_DYNAMIC_SOURCE_BUDGET_AND_OBSERVER_OBLIGATIONS_COMPLETE"),
    "FT19": ("Parent retention and descent", "CLOSED_CUMULATIVE_RETENTION_AND_DYNAMIC_DESCENT_PORTIONS_COMPLETE"),
    "FT20": ("Residual and needle semantics", "CLOSED_CUMULATIVE_JOIN_AND_DYNAMIC_RESIDUAL_PORTIONS_COMPLETE"),
}

TARGET_CANDIDATES = {
    "FT11": ["VII-C012", "VII-C014", "VII-C027", "VII-C034"],
    "FT12": ["VII-C013", "VII-C014"],
    "FT13": ["VII-C015", "VII-C034"],
    "FT14": ["VII-C017", "VII-C018", "VII-C028"],
    "FT15": ["VII-C017", "VII-C027", "VII-C032"],
    "FT16": ["VII-C013", "VII-C015", "VII-C027"],
    "FT19": ["VII-C015"],
    "FT20": ["VII-C015", "VII-C027"],
}

DECISION_ROWS = {
    "DP07": (
        "CROSS_TIME_CONTACT_REQUIRES_SYNCHRONIZATION_OR_PARTIAL_ORDER_WITNESS_NO_GLOBAL_CLOCK_ASSUMED",
        ["FoundationsVII.incommensurable_times_require_explicit_order_witness", "FoundationsVII.CrossTimeContact.valid_under_admissible_reparameterization"],
    ),
    "DP08": (
        "ENDOGENOUS_CREDIT_EXACTLY_CARRIED_REACHABLE_EXECUTED_AUDITED_BUDGETED_SOURCE_CLOSED_WITH_NO_HIDDEN_EXECUTOR",
        ["FoundationsVII.EndogenousEnablementProfile.eligible_iff_exact_criterion", "FoundationsVII.EndogenousEnablementProfile.hidden_theorist_execution_defeats_endogenous_credit", "FoundationsVII.EndogenousEnablementProfile.hidden_observer_execution_defeats_endogenous_credit"],
    ),
    "DP09": (
        "CONTACT_MAY_REMAIN_RELATION_ONLY_NEW_PARTICIPANT_REQUIRES_OBJECTHOOD_AND_CLOSURE_SURVIVAL",
        ["FoundationsVII.participant_creation_is_conditional_not_automatic", "FoundationsVII.BirthRecord.participant_credit_requires_objecthood", "FoundationsVII.BirthRecord.participant_credit_requires_closure_survival"],
    ),
    "DP11": (
        "HOLONOMY_DOES_NOT_IMPLY_ARROW_INDEPENDENT_DRIVE_PATH_ASYMMETRY_REVERSAL_BUDGET_AND_AUDIT_REQUIRED",
        ["FoundationsVII.holonomy_with_zero_arrow_witness", "FoundationsVII.driven_arrow_positive_control", "FoundationsVII.NoGo.NGVII_10_no_arrow_from_holonomy_alone", "FoundationsVII.reversal_null_and_driven_controls_are_distinct"],
    ),
    "DP12": (
        "FULL_PRIMITIVE_ALGEBRA_DEFERRED_SMALL_RESOURCE_DELTA_FRAGMENT_LANDED_WITH_EXACT_REOPEN_GATE",
        ["FoundationsVII.current_full_primitive_algebra_is_not_ready", "FoundationsVII.full_algebra_reopen_condition_is_exact", "FoundationsVII.resource_delta_fragment_is_associative", "FoundationsVII.full_generators_relations_program_deferred_with_formal_reopen_condition"],
    ),
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


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise AssertionError(f"cannot write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: canonical(value) if isinstance(value, (list, dict)) else value for key, value in row.items()})


def kernel_replay_passed() -> bool:
    path = ROOT / "formalization" / "lean" / "BUILD_STATUS_PHASE4.json"
    if not path.exists():
        return False
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("kernel_build_status") == "PASS"
    except (OSError, json.JSONDecodeError):
        return False


KERNEL_REPLAY_PASSED = kernel_replay_passed()
KERNEL_STATUS = "PASS_EXTERNAL_REPLAY" if KERNEL_REPLAY_PASSED else "PENDING_EXTERNAL_LEAN_REPLAY"
CANDIDATE_STATUS = "TERMINAL_PHASE4_ASSET_KERNEL_VERIFIED" if KERNEL_REPLAY_PASSED else "TERMINAL_PHASE4_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"


def resolved_grade(candidate_id: str) -> str:
    grade = GRADES[candidate_id]
    if KERNEL_REPLAY_PASSED and grade.endswith("_EXTERNAL_KERNEL_REPLAY_PENDING"):
        return grade.removesuffix("_EXTERNAL_KERNEL_REPLAY_PENDING") + "_KERNEL_VERIFIED"
    return grade


def source_files() -> list[Path]:
    files: list[Path] = []
    for dirname in ("Enablement", "Dynamics"):
        files.extend(p for p in sorted((LEAN_ROOT / dirname).glob("*.lean")) if p.name != "All.lean")
    files.extend([
        LEAN_ROOT / "NoGo" / "Dynamics.lean",
        LEAN_ROOT / "Models" / "Finite" / "Phase4" / "DynamicsEnvelope.lean",
        LEAN_ROOT / "Models" / "Finite" / "Phase4" / "ScenarioChecks.lean",
    ])
    return sorted(set(files))


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
            block = "\n".join(lines[line_no - 1:end_line]).strip()
            raw_name = match.group("name")
            fq = raw_name if "." in raw_name else ".".join((*namespace_stack, raw_name))
            kind = match.group("kind")
            statement = block.split(":=", 1)[0].strip()
            rel = path.relative_to(LEAN_ROOT).as_posix()
            rows.append({
                "declaration_id": "",
                "science_asset_id": "",
                "fully_qualified_name": fq,
                "short_name": raw_name,
                "kind": kind,
                "file": f"formalization/lean/FoundationsVII/{rel}",
                "line": line_no,
                "end_line": end_line,
                "statement_sha256": hashlib.sha256(statement.encode()).hexdigest(),
                "source_block_sha256": hashlib.sha256(block.encode()).hexdigest(),
                "kernel_status": KERNEL_STATUS,
            })
    rows.sort(key=lambda row: (row["file"], int(row["line"]), row["fully_qualified_name"]))
    for idx, row in enumerate(rows, start=1):
        row["declaration_id"] = f"FVII-SCI04-DECL-{idx:04d}"
        prefix = "FVII-SCI04-THM" if row["kind"] in {"theorem", "lemma", "corollary"} else "FVII-SCI04-DEF"
        row["science_asset_id"] = f"{prefix}-{idx:04d}"
    return rows


def candidate_ids_for_declaration(row: dict[str, Any]) -> list[str]:
    rel = str(Path(row["file"]).relative_to("formalization/lean/FoundationsVII"))
    name = str(row["short_name"])
    out = {cid for cid, modules in MODULES.items() if rel in modules}
    if rel == "Models/Finite/Phase4/DynamicsEnvelope.lean":
        out |= {cid for cid, prefixes in FINITE_PREFIXES.items() if name.startswith(prefixes)}
    elif rel == "Models/Finite/Phase4/ScenarioChecks.lean":
        out |= set(CANDIDATE_IDS)
    elif rel == "NoGo/Dynamics.lean":
        out |= {"VII-C017", "VII-C032"}
    return sorted(out)


def candidate_source(candidate_id: str) -> dict[str, Any]:
    return json.loads((ROOT / "readiness" / "candidates" / f"{candidate_id}.json").read_text(encoding="utf-8"))


def build_candidate_rows(declarations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    witnesses = read_jsonl(LAB4 / "canonical_witnesses.jsonl")
    rows: list[dict[str, Any]] = []
    for candidate_id in CANDIDATE_IDS:
        source = candidate_source(candidate_id)
        relevant = [row for row in declarations if candidate_id in row["candidate_ids"]]
        theorems = sorted(row["fully_qualified_name"] for row in relevant if row["kind"] in {"theorem", "lemma", "corollary"})
        definitions = sorted(row["fully_qualified_name"] for row in relevant if row["kind"] not in {"theorem", "lemma", "corollary"})
        bounded = sorted(row["witness_id"] for row in witnesses if row["candidate_id"] == candidate_id)
        trace = source.get("source_trace", {})
        rows.append({
            "candidate_id": candidate_id,
            "asset_id": ASSET_IDS[candidate_id],
            "name": source["name"],
            "kind": source.get("kind", "UNSPECIFIED_CANDIDATE_KIND"),
            "priority": source.get("priority", "UNSPECIFIED_PRIORITY"),
            "phase4_status": CANDIDATE_STATUS,
            "phase4_grade": resolved_grade(candidate_id),
            "lean_theorems": theorems,
            "lean_definitions": definitions,
            "theorem_count": len(theorems),
            "definition_count": len(definitions),
            "formalization_targets": source["formalization_targets"],
            "step3_positive_scenarios": source["positive_model"],
            "step3_null_scenarios": source["null_models"],
            "countermodels": source["countermodels"],
            "bounded_witnesses": bounded,
            "finite_envelopes": CANDIDATE_ENVELOPES[candidate_id],
            "source_support_count": len(trace.get("support_claim_ids", trace.get("supporting_claim_ids", trace.get("resolved_source_locations", [])))),
            "source_boundary_count": len(trace.get("boundary_claim_ids", [])),
            "source_open_count": len(trace.get("open_problem_ids", [])),
            "source_bridge_ids": trace.get("bridge_ids", []),
            "source_law_or_no_go_ids": trace.get("law_or_no_go_ids", []),
            "nonclaim": NONCLAIMS[candidate_id],
            "step3_prior_status": source.get("proof_status", "SPECIFICATION_READY_NOT_PROVED"),
        })
    return rows


def build_no_go_rows(declaration_names: set[str]) -> list[dict[str, Any]]:
    controls = {row["no_go_id"]: row for row in read_jsonl(LAB4 / "no_go_controls.jsonl")}
    rows = []
    for no_go_id, spec in NO_GOS.items():
        declarations = [spec["theorem"], *spec["escapes"], *spec["controls"]]
        rows.append({
            "no_go_id": no_go_id,
            "asset_id": f"FVII-SCI04-{no_go_id}",
            "name": spec["name"],
            "terminal_status": "PROVED_AT_DECLARED_STRUCTURAL_SCOPE_KERNEL_VERIFIED" if KERNEL_REPLAY_PASSED else "PROVED_AT_DECLARED_STRUCTURAL_SCOPE_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
            "theorem": spec["theorem"],
            "escape_theorems": spec["escapes"],
            "control_theorems": spec["controls"],
            "source_declarations_present": all(name in declaration_names for name in declarations),
            "failure_scenarios": spec["failures"],
            "positive_controls": spec["positive_controls"],
            "candidate_ids": spec["candidates"],
            "scope": spec["scope"],
            "finite_control_record": controls[no_go_id],
            "nonclaim": "The result blocks directionality credit from holonomy alone; a separately certified drive/path-asymmetry/reversal package is an explicit escape.",
            "kernel_status": KERNEL_STATUS,
        })
    return rows


def build_target_rows(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prior = {row["target_id"]: row for row in read_jsonl(REG / "phase3_formalization_targets.jsonl")}
    rows = []
    by_id = {row["candidate_id"]: row for row in candidates}
    for target_id, (name, status) in TARGETS.items():
        related = [by_id[candidate_id] for candidate_id in TARGET_CANDIDATES[target_id]]
        phase4_theorems = sorted({name for row in related for name in row["lean_theorems"]})
        rows.append({
            "target_id": target_id,
            "name": name,
            "candidate_ids": sorted(row["candidate_id"] for row in related),
            "prior_phase_status": prior.get(target_id, {}).get("phase3_status", "NOT_ASSIGNED_BEFORE_PHASE4"),
            "prior_phase_theorems": prior.get(target_id, {}).get("phase3_theorems", []),
            "phase4_theorems": phase4_theorems,
            "phase4_status": status,
            "kernel_status": KERNEL_STATUS,
        })
    return rows


def build_decision_rows(declaration_names: set[str]) -> list[dict[str, Any]]:
    readiness = {row["decision_id"]: row for row in read_jsonl(ROOT / "readiness" / "decision_points.jsonl")}
    rows = []
    for decision_id, (ruling, evidence) in DECISION_ROWS.items():
        base = readiness[decision_id]
        rows.append({
            "decision_id": decision_id,
            "question": base["question"],
            "prior_ruling": base["current_ruling"],
            "phase4_terminal_ruling": ruling,
            "terminal": True,
            "evidence_declarations": evidence,
            "evidence_present": all(name in declaration_names for name in evidence),
            "blocking_candidates": base["blocking_candidates"],
            "nonclaim": "This ruling is terminal for the current Foundations VII science program at its declared scope; stronger universal claims require new theorems.",
        })
    return rows


def write_candidate_dossiers(rows: list[dict[str, Any]]) -> None:
    THEOREMS.mkdir(parents=True, exist_ok=True)
    for row in rows:
        lines = [
            f"# {row['candidate_id']} — {row['name']}", "",
            f"- **Phase-4 asset:** `{row['asset_id']}`",
            f"- **Terminal status:** `{row['phase4_status']}`",
            f"- **Grade:** `{row['phase4_grade']}`", "",
            "## Formal surface", "",
            f"- Definitions: {row['definition_count']}",
            f"- Theorems/lemmas/corollaries: {row['theorem_count']}",
            f"- Formalization targets: {', '.join(row['formalization_targets'])}",
            f"- Step-3 scenario references: {', '.join(row['step3_positive_scenarios'] + row['step3_null_scenarios']) or 'none'}",
            f"- Countermodels: {', '.join(row['countermodels']) or 'none'}",
            f"- Phase-4 finite envelopes: {', '.join(row['finite_envelopes']) or 'none'}",
            f"- Phase-4 bounded witnesses: {', '.join(row['bounded_witnesses']) or 'none'}", "",
            "## Public theorem declarations", "",
        ]
        lines.extend(f"- `{name}`" for name in row["lean_theorems"])
        lines.extend(["", "## Scientific boundary", "", row["nonclaim"], "", "The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.", ""])
        (THEOREMS / f"{row['candidate_id']}.md").write_text("\n".join(lines), encoding="utf-8")


def write_no_go_dossiers(rows: list[dict[str, Any]]) -> None:
    NOGO.mkdir(parents=True, exist_ok=True)
    for row in rows:
        lines = [
            f"# {row['no_go_id']} — {row['name']}", "",
            f"- **Asset:** `{row['asset_id']}`",
            f"- **Status:** `{row['terminal_status']}`", "",
            "## Exact scope", "", row["scope"], "",
            "## Theorem", "", f"- `{row['theorem']}`", "",
            "## Control and escape theorems", "",
        ]
        lines.extend(f"- `{name}`" for name in row["control_theorems"] + row["escape_theorems"])
        lines.extend(["", "## Finite controls", "", f"- Failure scenarios: {', '.join(f'`{x}`' for x in row['failure_scenarios'])}", f"- Driven escapes: {', '.join(f'`{x}`' for x in row['positive_controls'])}", "", "## Nonclaim", "", row["nonclaim"], ""])
        (NOGO / f"{row['no_go_id']}.md").write_text("\n".join(lines), encoding="utf-8")


def write_decision_dossier(rows: list[dict[str, Any]]) -> None:
    DECISIONS.mkdir(parents=True, exist_ok=True)
    lines = ["# FVII-SCI-04 terminal science decisions", "", "These rulings close the Phase-4 dynamic and attribution decision load without claiming broader universal reductions.", ""]
    for row in rows:
        lines.extend([f"## {row['decision_id']} — {row['question']}", "", f"**Ruling:** `{row['phase4_terminal_ruling']}`", "", "Evidence:", ""])
        lines.extend(f"- `{name}`" for name in row["evidence_declarations"])
        lines.extend(["", "Blocking candidates from Step 3:", ""])
        lines.extend(f"- `{cid}`" for cid in row["blocking_candidates"])
        lines.extend(["", row["nonclaim"], ""])
        individual = [
            f"# {row['decision_id']} — {row['question']}", "",
            f"- **Prior ruling:** `{row['prior_ruling']}`",
            f"- **Phase-4 terminal ruling:** `{row['phase4_terminal_ruling']}`",
            f"- **Evidence present:** `{row['evidence_present']}`", "",
            "## Evidence declarations", "",
        ]
        individual.extend(f"- `{name}`" for name in row["evidence_declarations"])
        individual.extend(["", "## Blocking candidates", ""])
        individual.extend(f"- `{cid}`" for cid in row["blocking_candidates"])
        individual.extend(["", "## Boundary", "", row["nonclaim"], ""])
        (DECISIONS / f"{row['decision_id']}.md").write_text("\n".join(individual), encoding="utf-8")
    (DECISIONS / "FVII-SCI-04-TERMINAL-DECISIONS.md").write_text("\n".join(lines), encoding="utf-8")


def write_print_axioms(theorems: list[dict[str, Any]]) -> None:
    path = LEAN_ROOT / "Trust" / "PrintAxiomsPhase4.lean"
    lines = ["import FoundationsVII.All", "",
             "/-! Generated FVII-SCI-04 trust replay surface. -/", ""]
    lines.extend(f"#print axioms {row['fully_qualified_name']}" for row in sorted(theorems, key=lambda row: row["fully_qualified_name"]))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    declarations = parse_declarations()
    for row in declarations:
        row["candidate_ids"] = candidate_ids_for_declaration(row)
    declaration_map = {row["fully_qualified_name"]: row for row in declarations}
    names = set(declaration_map)
    theorems = [row for row in declarations if row["kind"] in {"theorem", "lemma", "corollary"}]
    candidates = build_candidate_rows(declarations)
    no_gos = build_no_go_rows(names)
    targets = build_target_rows(candidates)
    decisions = build_decision_rows(names)

    envelopes = []
    for row in read_jsonl(LAB4 / "envelopes.jsonl"):
        enriched = dict(row)
        enriched.update({
            "candidate_ids": ENVELOPE_CANDIDATES[row["family_id"]],
            "lean_module": "FoundationsVII.Models.Finite.Phase4.DynamicsEnvelope",
            "python_grade": "EXECUTED_EXHAUSTIVE_DECLARED_FINITE_FAMILY",
            "lean_grade": "SOURCE_COMPLETE_EXTERNAL_REPLAY_PENDING" if not KERNEL_REPLAY_PASSED else "KERNEL_VERIFIED",
        })
        envelopes.append(enriched)

    witnesses = []
    for row in read_jsonl(LAB4 / "canonical_witnesses.jsonl"):
        path = f"formalization/foundations_vii_lab/phase4/witnesses/{row['witness_id']}.json"
        full = ROOT / path
        enriched = dict(row)
        enriched.update({"path": path, "file_sha256": hashlib.sha256(full.read_bytes()).hexdigest()})
        witnesses.append(enriched)

    for stem, rows in (
        ("phase4_public_declarations", declarations),
        ("phase4_theorem_catalog", theorems),
        ("phase4_candidate_closure", candidates),
        ("phase4_no_go_closure", no_gos),
        ("phase4_formalization_targets", targets),
        ("phase4_decision_closure", decisions),
        ("phase4_finite_envelopes", envelopes),
    ):
        write_jsonl(REG / f"{stem}.jsonl", rows)
        write_csv(REG / f"{stem}.csv", rows)
    write_jsonl(TRACE / "phase4_bounded_witnesses.jsonl", witnesses)
    write_csv(TRACE / "phase4_bounded_witnesses.csv", witnesses)

    trace_rows: list[dict[str, Any]] = []
    for candidate in candidates:
        for name in candidate["lean_theorems"] + candidate["lean_definitions"]:
            decl = declaration_map[name]
            trace_rows.append({
                "asset_id": candidate["asset_id"], "candidate_id": candidate["candidate_id"],
                "trace_kind": "LEAN_DECLARATION", "trace_id": name,
                "path": decl["file"], "line": decl["line"], "sha256": decl["source_block_sha256"],
            })
        fixture_ids = candidate["step3_positive_scenarios"] + candidate["step3_null_scenarios"] + candidate["countermodels"] + candidate["bounded_witnesses"]
        for fixture_id in fixture_ids:
            if fixture_id.startswith("TTW"):
                path = f"formalization/foundations_vii_lab/fixtures/scenarios/{fixture_id}.json"
            elif fixture_id.startswith("CM"):
                path = f"formalization/foundations_vii_lab/fixtures/countermodels/{fixture_id}.json"
            else:
                path = f"formalization/foundations_vii_lab/phase4/witnesses/{fixture_id}.json"
            full = ROOT / path
            if not full.exists():
                raise AssertionError(f"missing trace fixture {fixture_id}: {path}")
            trace_rows.append({
                "asset_id": candidate["asset_id"], "candidate_id": candidate["candidate_id"],
                "trace_kind": "FINITE_WITNESS", "trace_id": fixture_id,
                "path": path, "line": "", "sha256": hashlib.sha256(full.read_bytes()).hexdigest(),
            })
    write_jsonl(TRACE / "phase4_asset_trace.jsonl", trace_rows)
    write_csv(TRACE / "phase4_asset_trace.csv", trace_rows)
    (TRACE / "phase4_statement_hashes.sha256").write_text("\n".join(sorted(f"{row['statement_sha256']}  {row['fully_qualified_name']}" for row in theorems)) + "\n", encoding="utf-8")

    write_print_axioms(theorems)
    write_candidate_dossiers(candidates)
    write_no_go_dossiers(no_gos)
    write_decision_dossier(decisions)

    summary = {
        "phase": "FVII-SCI-04",
        "stage": "COMPLETE_KERNEL_VERIFIED" if KERNEL_REPLAY_PASSED else "COMPLETE_SOURCE_LEVEL_EXTERNAL_LEAN_REPLAY_PENDING",
        "terminal_candidate_count": len(candidates),
        "no_go_count": len(no_gos),
        "formalization_target_count": len(targets),
        "terminal_decision_count": len(decisions),
        "phase4_declaration_count": len(declarations),
        "phase4_theorem_count": len(theorems),
        "finite_envelope_count": len(envelopes),
        "bounded_witness_count": len(witnesses),
        "python_summary": json.loads((LAB4 / "summary.json").read_text(encoding="utf-8")),
        "lean_kernel_status": "PASS_EXTERNAL_REPLAY" if KERNEL_REPLAY_PASSED else "PENDING_EXTERNAL_LEAN_REPLAY_NONBLOCKING_BY_OWNER_AUTHORIZATION",
        "no_paper_work": True,
    }
    (REG / "phase4_summary.json").write_text(canonical(summary) + "\n", encoding="utf-8")
    print(canonical(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

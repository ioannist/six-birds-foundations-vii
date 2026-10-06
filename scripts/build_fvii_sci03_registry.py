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
LAB3 = ROOT / "formalization" / "foundations_vii_lab" / "phase3" / "results"

CANDIDATE_IDS = [
    "VII-C007", "VII-C008", "VII-C009", "VII-C010", "VII-C011",
    "VII-C016", "VII-C019", "VII-C026", "VII-C030", "VII-C031",
    "VII-C033", "VII-C035", "VII-C036",
]

ASSET_IDS = {
    "VII-C007": "FVII-SCI03-C007-JOIN-ENTRY-NORMAL-FORM",
    "VII-C008": "FVII-SCI03-C008-JOIN-STATUS-CALCULUS",
    "VII-C009": "FVII-SCI03-C009-STRICT-JOIN-CERTIFICATE",
    "VII-C010": "FVII-SCI03-C010-SOURCE-INDEPENDENCE-GATE",
    "VII-C011": "FVII-SCI03-C011-JOIN-BUDGET-LEDGER",
    "VII-C016": "FVII-SCI03-C016-PEER-CONTACT-TRANSPORT",
    "VII-C019": "FVII-SCI03-C019-RESIDUAL-LEDGER",
    "VII-C026": "FVII-SCI03-C026-CATEGORICAL-DECISION",
    "VII-C030": "FVII-SCI03-C030-RETENTION-REFINEMENT",
    "VII-C031": "FVII-SCI03-C031-CONTACT-DEGREE-DECISION",
    "VII-C033": "FVII-SCI03-C033-CERTIFIED-NONINTERACTION",
    "VII-C035": "FVII-SCI03-C035-NO-FREE-JOIN-FAMILY",
    "VII-C036": "FVII-SCI03-C036-JOIN-CREATED-NEEDLE",
}

GRADES = {
    "VII-C007": "JOIN_ENTRY_NORMAL_FORM_AND_OMISSION_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C008": "SCOPED_JOIN_STATUS_CALCULUS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C009": "STRICT_JOIN_CERTIFICATE_AND_ANTI_PRODUCT_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C010": "SOURCE_INDEPENDENCE_GATE_AND_NO_GO_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C011": "TYPED_JOIN_BUDGET_AND_BOUNDEDNESS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C016": "PEER_CONTACT_TRANSPORT_WITHOUT_JOIN_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C019": "APPEND_ONLY_RESIDUAL_AND_DISSOLUTION_LEDGER_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C026": "UNCONDITIONAL_CATEGORICAL_REDUCTION_REJECTED_SPECIAL_CASE_THEOREMS_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C030": "RETENTION_REFINEMENT_AND_NONMONOTONICITY_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C031": "NATURAL_CONTACT_QUANTITIES_NONCONSERVATION_CONTROLS_SOURCE_COMPLETE_NO_UNIVERSAL_DEGREE_CERTIFIED",
    "VII-C033": "COVERAGE_QUALIFIED_NONINTERACTION_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C035": "NO_FREE_JOIN_FAMILY_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
    "VII-C036": "JOIN_CREATED_CROSS_TERM_NEEDLE_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
}



def kernel_replay_passed() -> bool:
    path = ROOT / "formalization" / "lean" / "BUILD_STATUS_PHASE3.json"
    if not path.is_file():
        return False
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("kernel_build_status") == "PASS"
    except (json.JSONDecodeError, OSError):
        return False


KERNEL_REPLAY_PASSED = kernel_replay_passed()
KERNEL_STATUS = "PASS_EXTERNAL_REPLAY" if KERNEL_REPLAY_PASSED else "PENDING_EXTERNAL_LEAN_REPLAY"
CANDIDATE_STATUS = (
    "TERMINAL_PHASE3_ASSET_KERNEL_VERIFIED"
    if KERNEL_REPLAY_PASSED
    else "TERMINAL_PHASE3_ASSET_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"
)

def resolved_grade(candidate_id: str) -> str:
    grade = GRADES[candidate_id]
    if not KERNEL_REPLAY_PASSED:
        return grade
    if grade.endswith("_EXTERNAL_KERNEL_REPLAY_PENDING"):
        return grade.removesuffix("_EXTERNAL_KERNEL_REPLAY_PENDING") + "_KERNEL_VERIFIED"
    return grade + "_KERNEL_VERIFIED"

NONCLAIMS = {
    "VII-C007": "A complete entry record makes a join attempt retrospectively auditable; it does not prove that contact, a composite, or strict join exists.",
    "VII-C008": "The status classifier is total only over the declared finite evidence family and is not a universal classification of every possible theory interaction.",
    "VII-C009": "Strictness remains separate from objecthood and directionality; anti-product evidence alone supplies neither.",
    "VII-C010": "Source independence is required only for independence-sensitive credit and is not equated with behavioral novelty or causal independence.",
    "VII-C011": "The typed ledger and finite capacity theorem do not identify a universal scalar currency or a domain-independent minimum cost.",
    "VII-C016": "Certified transport can make content available to a peer without forming a composite or strict joint theory.",
    "VII-C019": "Residual bookkeeping is scoped to declared ledgers and does not assert that all obstructions are additive or monotonically removed by joining.",
    "VII-C026": "No unconditional product, pullback, or pushout representation is claimed; only explicitly checked special cases receive categorical credit.",
    "VII-C030": "Parent refinement is not monotone for join evidence; preserving, strengthening, weakening, and destroying cases remain distinct.",
    "VII-C031": "No universal conserved contact degree is named. The tested natural bookkeeping quantities all have lawful nonconservation controls.",
    "VII-C033": "Certified non-interaction excludes contact only inside the exact declared family, detector, budget, and horizon; outside-family channels remain explicit escapes.",
    "VII-C035": "The five no-go fronts are separate scoped results, not one universal impossibility theorem.",
    "VII-C036": "A join-created needle requires an active sourced cross-term; relabeling alone does not count as a new obstruction.",
}

MODULES = {
    "VII-C007": ["Join/Entry.lean"],
    "VII-C008": ["Join/Status.lean", "Models/Finite/Phase3/ScenarioChecks.lean"],
    "VII-C009": ["Join/Objecthood.lean", "Join/Strictness.lean"],
    "VII-C010": ["Join/Source.lean"],
    "VII-C011": ["Join/Budget.lean"],
    "VII-C016": ["Contact/Transport.lean"],
    "VII-C019": ["Residuals/Ledger.lean"],
    "VII-C026": ["Join/Categorical.lean"],
    "VII-C030": ["Join/Retention.lean"],
    "VII-C031": ["Join/Degree.lean"],
    "VII-C033": ["Join/NonInteraction.lean"],
    "VII-C035": ["NoGo/Join.lean"],
    "VII-C036": ["Residuals/Ledger.lean"],
}

ENVELOPE_CANDIDATES = {
    "P3-E01": ["VII-C007", "VII-C016"],
    "P3-E02": ["VII-C007", "VII-C008"],
    "P3-E03": ["VII-C009"],
    "P3-E04": ["VII-C010"],
    "P3-E05": ["VII-C011", "VII-C035"],
    "P3-E06": ["VII-C011"],
    "P3-E07": ["VII-C030"],
    "P3-E08": ["VII-C019", "VII-C036"],
    "P3-E09": ["VII-C033"],
    "P3-E10": ["VII-C009", "VII-C026"],
    "P3-E11": ["VII-C031"],
}

CANDIDATE_ENVELOPES = {
    candidate_id: sorted(
        family_id
        for family_id, candidate_ids in ENVELOPE_CANDIDATES.items()
        if candidate_id in candidate_ids
    )
    for candidate_id in CANDIDATE_IDS
}

FINITE_PREFIXES = {
    "VII-C007": ("ContactTransport", "contactTransport", "contact_transport"),
    "VII-C008": ("JoinStatus", "joinStatus", "join_status", "FiniteJoinStatus", "classifyJoinStatus", "acceptedJoinStatusCases", "statusCount", "status_", "Phase3"),
    "VII-C009": ("Strictness", "strictness", "directionless_strict", "strict_join_status_count"),
    "VII-C010": ("SourceLineage", "sourceLineage", "source_lineage"),
    "VII-C011": ("Payment", "payment", "Capacity", "capacity", "finite_live_join"),
    "VII-C016": ("ContactTransport", "contactTransport", "contact_transport"),
    "VII-C019": ("Residual", "residual", "FiniteResidual"),
    "VII-C026": ("Categorical", "categorical", "strict_join_without_listed"),
    "VII-C030": ("Refinement", "refinement", "FiniteRetention", "FiniteRefinement", "retention"),
    "VII-C031": ("Measure", "measure", "FiniteMeasure", "hasLawful", "contacts_nonconservation", "live_joins_nonconservation", "paid_cost_nonconservation", "active_residuals_nonconservation", "retained_parents_nonconservation"),
    "VII-C033": ("Noninteraction", "noninteraction", "exactly_one_certified", "Phase3"),
    "VII-C035": ("Strictness", "strictness", "Payment", "payment", "Phase3"),
    "VII-C036": ("Residual", "residual", "FiniteResidual"),
}

NO_GOS = {
    "NGVII-02": {
        "name": "No resemblance-only independence-sensitive join",
        "theorem": "FoundationsVII.NoGo.NGVII_02_no_resemblance_only_independence_join",
        "escapes": ["FoundationsVII.NoGo.NGVII_02_escape_witnessed_independent_contact"],
        "failures": ["TTW-S05", "TTW-S15"], "controls": ["TTW-S08"],
        "candidates": ["VII-C010", "VII-C035"],
        "scope": "Independence-sensitive credit in the declared resemblance/contact/source profile.",
    },
    "NGVII-06": {
        "name": "No join from contact alone",
        "theorem": "FoundationsVII.NoGo.NGVII_06_no_join_from_contact_alone",
        "escapes": ["FoundationsVII.NoGo.NGVII_06_escape_complete_strict_join_certificate"],
        "failures": ["TTW-S06"], "controls": ["TTW-S08"],
        "candidates": ["VII-C007", "VII-C009", "VII-C035"],
        "scope": "A witnessed contact profile lacking a composite, retention, and anti-product novelty.",
    },
    "NGVII-07": {
        "name": "No product/common-refinement strictness credit",
        "theorem": "FoundationsVII.NoGo.NGVII_07_no_product_common_refinement_strictness_credit",
        "escapes": ["FoundationsVII.NoGo.NGVII_07_escape_anti_product_witness"],
        "failures": ["TTW-S07", "TTW-S14", "TTW-S15"], "controls": ["TTW-S08"],
        "candidates": ["VII-C009", "VII-C026", "VII-C035"],
        "scope": "The declared comparison baseline where mere product/common refinement still factors through the baseline.",
    },
    "NGVII-08": {
        "name": "No one-lineage source-independence credit",
        "theorem": "FoundationsVII.NoGo.NGVII_08_no_one_lineage_source_independence_credit",
        "escapes": ["FoundationsVII.NoGo.NGVII_08_escape_disjoint_root_certificate"],
        "failures": ["TTW-S05", "TTW-S11"], "controls": ["TTW-S08"],
        "candidates": ["VII-C010", "VII-C035"],
        "scope": "Independence-sensitive source claims with a single uncertified lineage.",
    },
    "NGVII-09": {
        "name": "No positive-cost join credit without payment or a certified zero-cost channel",
        "theorem": "FoundationsVII.NoGo.NGVII_09_no_positive_cost_join_credit_without_payment",
        "escapes": ["FoundationsVII.NoGo.NGVII_09_escape_paid_channel", "FoundationsVII.NoGo.NGVII_09_escape_certified_zero_cost_channel"],
        "failures": ["TTW-S10"], "controls": ["TTW-S08"],
        "candidates": ["VII-C011", "VII-C035"],
        "scope": "Positive-cost join credit in the declared payment and observer-pricing profile.",
    },
}

TARGETS = {
    "FT05": ("Source/provenance and transport discipline", "CLOSED_CUMULATIVE_SOURCE_TRANSPORT_DISCIPLINE_COMPLETE"),
    "FT06": ("Typed contact and join-entry records", "CLOSED_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"),
    "FT07": ("Composite objecthood, retention, and strict-join certificate", "CLOSED_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"),
    "FT08": ("Anti-product and no-fake-join witnesses", "CLOSED_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"),
    "FT09": ("Join status, budget, and obstruction calculus", "CLOSED_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"),
    "FT10": ("Coverage-qualified non-interaction", "CLOSED_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"),
    "FT16": ("Budget and observer occupancy accounting", "CLOSED_CUMULATIVE_ADMISSION_AND_JOIN_ACCOUNTING_COMPLETE"),
    "FT18": ("No-free-access/no-free-join lemmas", "CLOSED_CUMULATIVE_ADMISSION_AND_JOIN_HALVES_COMPLETE"),
    "FT19": ("Parent retention and descent", "PARENT_RETENTION_PORTION_COMPLETE_DYNAMICAL_DESCENT_RESERVED_FOR_FVII_SCI_04"),
    "FT20": ("Residual and needle semantics", "JOIN_RESIDUAL_PORTION_COMPLETE_DYNAMICAL_PORTION_RESERVED_FOR_FVII_SCI_04"),
}

DECISION_ROWS = {
    "DP01": ("CONTACT_SURFACE_RETAINED_AS_SCOPED_PRIMITIVE_RECORD", ["FoundationsVII.contact_surface_primitive_scoped_ruling"]),
    "DP02": ("JOIN_STATUS_LIST_TERMINAL_ONLY_FOR_DECLARED_FINITE_EVIDENCE_FAMILY", ["FoundationsVII.Models.Finite.Phase3.status_partition_complete"]),
    "DP03": ("SOURCE_INDEPENDENCE_REQUIRED_ONLY_FOR_INDEPENDENCE_SENSITIVE_CREDIT", ["FoundationsVII.SourceIndependenceGate.certified_gate_separates_source_and_behavior"]),
    "DP04": ("UNCONDITIONAL_CATEGORICAL_REDUCTION_REJECTED_SPECIAL_CASES_PERMITTED", ["FoundationsVII.unconditional_categorical_reduction_countermodel", "FoundationsVII.special_case_categorical_representation_is_conditional"]),
    "DP05": ("NO_SINGLE_SCALAR_JOIN_CURRENCY_TYPED_LEDGER_RETAINED", ["FoundationsVII.JoinPaymentLedger.typedCosts", "FoundationsVII.JoinCostEntry.positive_cost_without_payment_or_zero_channel_is_not_credited"]),
    "DP06": ("NO_CONSERVED_CONTACT_DEGREE_CERTIFIED_NATURAL_CANDIDATES_HAVE_NONCONSERVATION_CONTROLS", ["FoundationsVII.plausible_contact_quantities_disagree", "FoundationsVII.no_unqualified_contact_degree_from_bookkeeping_alone"]),
    "DP10": ("NO_UNCONDITIONAL_REFINEMENT_MONOTONICITY", ["FoundationsVII.no_unconditional_join_monotonicity_under_refinement"]),
    "DP15": ("NONINTERACTION_STRENGTH_EXACTLY_COVERAGE_QUALIFIED", ["FoundationsVII.ContactNullProfile.no_evidenced_contact_is_weaker_than_certified_noninteraction", "FoundationsVII.DeclaredContactCase.outside_family_is_an_explicit_escape"]),
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


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise AssertionError(f"cannot write empty CSV {path}")
    fields = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: canonical(row[field]) if isinstance(row.get(field), (list, dict)) else row.get(field, "") for field in fields})


def source_files() -> list[Path]:
    files: list[Path] = []
    for dirname in ("Contact", "Join", "Residuals"):
        files.extend(p for p in sorted((LEAN_ROOT / dirname).glob("*.lean")) if p.name != "All.lean")
    files.append(LEAN_ROOT / "NoGo" / "Join.lean")
    files.extend([
        LEAN_ROOT / "Models" / "Finite" / "Phase3" / "ContactJoinEnvelope.lean",
        LEAN_ROOT / "Models" / "Finite" / "Phase3" / "ScenarioChecks.lean",
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
            rel = path.relative_to(LEAN_ROOT).as_posix()
            statement = block.split(":=", 1)[0].strip()
            prefix = "FVII-SCI03-THM" if kind in {"theorem", "lemma", "corollary"} else "FVII-SCI03-DEF"
            rows.append({
                "declaration_id": f"FVII-SCI03-DECL-{len(rows)+1:04d}",
                "science_asset_id": f"{prefix}-{len(rows)+1:04d}",
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
    rows.sort(key=lambda r: (r["file"], int(r["line"]), r["fully_qualified_name"]))
    for idx, row in enumerate(rows, start=1):
        row["declaration_id"] = f"FVII-SCI03-DECL-{idx:04d}"
        row["science_asset_id"] = ("FVII-SCI03-THM" if row["kind"] in {"theorem", "lemma", "corollary"} else "FVII-SCI03-DEF") + f"-{idx:04d}"
    return rows


def candidate_ids_for_declaration(row: dict[str, Any]) -> list[str]:
    rel = str(Path(row["file"]).relative_to("formalization/lean/FoundationsVII"))
    name = str(row["short_name"])
    out = {cid for cid, modules in MODULES.items() if rel in modules}
    if rel == "Models/Finite/Phase3/ContactJoinEnvelope.lean":
        out |= {cid for cid, prefixes in FINITE_PREFIXES.items() if name.startswith(prefixes)}
    elif rel == "Models/Finite/Phase3/ScenarioChecks.lean":
        out |= {"VII-C008", "VII-C033", "VII-C035"}
    elif rel == "NoGo/Join.lean":
        out.add("VII-C035")
        if any(token in name for token in ("Resemblance", "Lineage", "NGVII_02", "NGVII_08", "resemblance", "lineage", "independent")):
            out.add("VII-C010")
        if any(token in name for token in ("ContactOnly", "ProductJoin", "NGVII_06", "NGVII_07", "strictJoin", "antiProduct")):
            out.add("VII-C009")
        if any(token in name for token in ("Payment", "NGVII_09", "paid", "zeroCost")):
            out.add("VII-C011")
    return sorted(out)


def candidate_source(candidate_id: str) -> dict[str, Any]:
    path = ROOT / "readiness" / "candidates" / f"{candidate_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def build_candidate_rows(declarations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    witnesses = read_jsonl(LAB3 / "canonical_witnesses.jsonl")
    rows: list[dict[str, Any]] = []
    for candidate_id in CANDIDATE_IDS:
        source = candidate_source(candidate_id)
        relevant = [r for r in declarations if candidate_id in r["candidate_ids"]]
        theorems = sorted(r["fully_qualified_name"] for r in relevant if r["kind"] in {"theorem", "lemma", "corollary"})
        definitions = sorted(r["fully_qualified_name"] for r in relevant if r["kind"] not in {"theorem", "lemma", "corollary"})
        bounded = sorted(r["witness_id"] for r in witnesses if r["candidate_id"] == candidate_id)
        if candidate_id == "VII-C019":
            bounded = sorted(set(bounded) | {"P3-W20", "P3-W21"})
        source_trace = source.get("source_trace", {})
        rows.append({
            "candidate_id": candidate_id,
            "asset_id": ASSET_IDS[candidate_id],
            "name": source["name"],
            "kind": source.get("kind", "UNSPECIFIED_CANDIDATE_KIND"),
            "priority": source.get("priority", "UNSPECIFIED_PRIORITY"),
            "phase3_status": CANDIDATE_STATUS,
            "phase3_grade": resolved_grade(candidate_id),
            "lean_theorems": theorems,
            "lean_definitions": definitions,
            "theorem_count": len(theorems),
            "definition_count": len(definitions),
            "formalization_targets": source["formalization_targets"],
            "positive_scenarios": source["positive_model"],
            "null_scenarios": source["null_models"],
            "countermodels": source["countermodels"],
            "bounded_witnesses": bounded,
            "finite_envelopes": CANDIDATE_ENVELOPES[candidate_id],
            "source_support_count": len(
                source_trace.get(
                    "support_claim_ids",
                    source_trace.get(
                        "supporting_claim_ids",
                        source_trace.get("resolved_source_locations", []),
                    ),
                )
            ),
            "source_boundary_count": len(source_trace.get("boundary_claim_ids", [])),
            "source_open_count": len(source_trace.get("open_problem_ids", [])),
            "source_bridge_ids": source_trace.get("bridge_ids", []),
            "source_law_or_no_go_ids": source_trace.get("law_or_no_go_ids", []),
            "nonclaim": NONCLAIMS[candidate_id],
            "step3_prior_status": source.get("proof_status", "SPECIFICATION_READY_NOT_PROVED"),
        })
    return rows


def build_no_go_rows(declaration_names: set[str]) -> list[dict[str, Any]]:
    controls = {r["no_go_id"]: r for r in read_jsonl(LAB3 / "no_go_controls.jsonl")}
    rows: list[dict[str, Any]] = []
    for no_go_id, spec in NO_GOS.items():
        rows.append({
            "no_go_id": no_go_id,
            "asset_id": f"FVII-SCI03-{no_go_id}",
            "name": spec["name"],
            "terminal_status": (
                "PROVED_AT_DECLARED_STRUCTURAL_SCOPE_KERNEL_VERIFIED"
                if KERNEL_REPLAY_PASSED
                else "PROVED_AT_DECLARED_STRUCTURAL_SCOPE_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"
            ),
            "theorem": spec["theorem"],
            "escape_theorems": spec["escapes"],
            "source_declarations_present": spec["theorem"] in declaration_names and all(x in declaration_names for x in spec["escapes"]),
            "failure_scenarios": spec["failures"],
            "positive_controls": spec["controls"],
            "candidate_ids": spec["candidates"],
            "scope": spec["scope"],
            "finite_control_record": controls[no_go_id],
            "nonclaim": "The result applies only to the declared typed profile; listed witness, source, payment, seed, bridge, or scope changes are explicit escapes.",
            "kernel_status": KERNEL_STATUS,
        })
    return rows


def build_target_rows(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prior = {r["target_id"]: r for r in read_jsonl(REG / "phase2_formalization_targets.jsonl")}
    rows: list[dict[str, Any]] = []
    for target_id, (name, status) in TARGETS.items():
        related = [r for r in candidates if target_id in r["formalization_targets"]]
        phase3_theorems = sorted({thm for r in related for thm in r["lean_theorems"]})
        rows.append({
            "target_id": target_id,
            "name": name,
            "candidate_ids": sorted(r["candidate_id"] for r in related),
            "prior_phase_status": prior.get(target_id, {}).get("phase2_status", "NOT_ASSIGNED_BEFORE_PHASE3"),
            "prior_phase_theorems": prior.get(target_id, {}).get("phase2_theorems", []),
            "phase3_theorems": phase3_theorems,
            "phase3_status": status,
            "kernel_status": KERNEL_STATUS,
        })
    return rows


def build_decision_rows(declaration_names: set[str]) -> list[dict[str, Any]]:
    readiness = {r["decision_id"]: r for r in read_jsonl(ROOT / "readiness" / "decision_points.jsonl")}
    rows = []
    for decision_id, (ruling, evidence) in DECISION_ROWS.items():
        base = readiness[decision_id]
        rows.append({
            "decision_id": decision_id,
            "question": base["question"],
            "prior_ruling": base["current_ruling"],
            "phase3_terminal_ruling": ruling,
            "terminal": True,
            "evidence_declarations": evidence,
            "evidence_present": all(x in declaration_names for x in evidence),
            "blocking_candidates": base["blocking_candidates"],
            "nonclaim": "This ruling is terminal for the current Foundations VII science program at its declared scope; stronger universal claims require new theorems.",
        })
    return rows


def write_candidate_dossiers(rows: list[dict[str, Any]]) -> None:
    THEOREMS.mkdir(parents=True, exist_ok=True)
    for row in rows:
        lines = [
            f"# {row['candidate_id']} — {row['name']}", "",
            f"- **Phase-3 asset:** `{row['asset_id']}`",
            f"- **Terminal status:** `{row['phase3_status']}`",
            f"- **Grade:** `{row['phase3_grade']}`", "",
            "## Formal surface", "",
            f"- Definitions: {row['definition_count']}",
            f"- Theorems/lemmas/corollaries: {row['theorem_count']}",
            f"- Formalization targets: {', '.join(row['formalization_targets'])}",
            f"- Positive scenarios: {', '.join(row['positive_scenarios']) or 'none'}",
            f"- Null/control scenarios: {', '.join(row['null_scenarios']) or 'none'}",
            f"- Countermodels: {', '.join(row['countermodels']) or 'none'}",
            f"- Phase-3 finite envelopes: {', '.join(row['finite_envelopes']) or 'none'}",
            f"- Phase-3 bounded witnesses: {', '.join(row['bounded_witnesses']) or 'none'}", "",
            "## Public theorem declarations", "",
        ]
        lines.extend(f"- `{name}`" for name in row["lean_theorems"])
        lines.extend(["", "## Scientific boundary", "", row["nonclaim"], "",
            "The Lean source is complete at text level. Kernel elaboration and executed `#print axioms` results remain the external replay gate.", ""])
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
            "## Escape/positive theorems", "",
        ]
        lines.extend(f"- `{name}`" for name in row["escape_theorems"])
        lines.extend(["", "## Finite controls", "",
            f"- Failure scenarios: {', '.join(f'`{x}`' for x in row['failure_scenarios'])}",
            f"- Positive controls: {', '.join(f'`{x}`' for x in row['positive_controls'])}", "",
            "## Nonclaim", "", row["nonclaim"], ""])
        (NOGO / f"{row['no_go_id']}.md").write_text("\n".join(lines), encoding="utf-8")


def write_decision_dossier(rows: list[dict[str, Any]]) -> None:
    DECISIONS.mkdir(parents=True, exist_ok=True)
    lines = ["# FVII-SCI-03 terminal science decisions", "",
        "These rulings close the Phase-3 decision load without claiming broader universal reductions.", ""]
    for row in rows:
        section = [
            f"## {row['decision_id']} — {row['question']}", "",
            f"**Ruling:** `{row['phase3_terminal_ruling']}`", "",
            "Evidence:", "",
        ]
        section.extend(f"- `{name}`" for name in row["evidence_declarations"])
        section.extend(["", "Blocking candidates from Step 3:", ""])
        section.extend(f"- `{candidate_id}`" for candidate_id in row["blocking_candidates"])
        section.extend(["", row["nonclaim"], ""])
        lines.extend(section)
        individual = [
            f"# {row['decision_id']} — {row['question']}", "",
            f"- **Prior ruling:** `{row['prior_ruling']}`",
            f"- **Phase-3 terminal ruling:** `{row['phase3_terminal_ruling']}`",
            f"- **Evidence present:** `{row['evidence_present']}`", "",
            "## Evidence declarations", "",
        ]
        individual.extend(f"- `{name}`" for name in row["evidence_declarations"])
        individual.extend(["", "## Blocking candidates", ""])
        individual.extend(f"- `{candidate_id}`" for candidate_id in row["blocking_candidates"])
        individual.extend(["", "## Boundary", "", row["nonclaim"], ""])
        (DECISIONS / f"{row['decision_id']}.md").write_text("\n".join(individual), encoding="utf-8")
    (DECISIONS / "FVII-SCI-03-TERMINAL-DECISIONS.md").write_text("\n".join(lines), encoding="utf-8")


def write_print_axioms(theorems: list[dict[str, Any]]) -> None:
    path = LEAN_ROOT / "Trust" / "PrintAxiomsPhase3.lean"
    lines = ["import FoundationsVII.All", "",
             "/-! Generated FVII-SCI-03 trust replay surface. -/", ""]
    lines.extend(f"#print axioms {row['fully_qualified_name']}" for row in sorted(theorems, key=lambda r: r["fully_qualified_name"]))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    declarations = parse_declarations()
    for row in declarations:
        row["candidate_ids"] = candidate_ids_for_declaration(row)
    names = {row["fully_qualified_name"] for row in declarations}
    declaration_map = {row["fully_qualified_name"]: row for row in declarations}
    theorems = [r for r in declarations if r["kind"] in {"theorem", "lemma", "corollary"}]
    candidates = build_candidate_rows(declarations)
    no_gos = build_no_go_rows(names)
    targets = build_target_rows(candidates)
    decisions = build_decision_rows(names)
    raw_envelopes = read_jsonl(LAB3 / "envelopes.jsonl")
    envelopes = []
    for row in raw_envelopes:
        enriched = dict(row)
        enriched.update({
            "candidate_ids": ENVELOPE_CANDIDATES[row["family_id"]],
            "lean_module": "FoundationsVII.Models.Finite.Phase3.ContactJoinEnvelope",
            "python_grade": "EXECUTED_EXHAUSTIVE_DECLARED_FINITE_FAMILY",
            "lean_grade": "SOURCE_COMPLETE_EXTERNAL_REPLAY_PENDING",
        })
        envelopes.append(enriched)

    raw_witnesses = read_jsonl(LAB3 / "canonical_witnesses.jsonl")
    witnesses = []
    for row in raw_witnesses:
        path = f"formalization/foundations_vii_lab/phase3/witnesses/{row['witness_id']}.json"
        full = ROOT / path
        enriched = dict(row)
        enriched.update({
            "path": path,
            "file_sha256": hashlib.sha256(full.read_bytes()).hexdigest(),
        })
        witnesses.append(enriched)

    for stem, rows in (
        ("phase3_public_declarations", declarations),
        ("phase3_theorem_catalog", theorems),
        ("phase3_candidate_closure", candidates),
        ("phase3_no_go_closure", no_gos),
        ("phase3_formalization_targets", targets),
        ("phase3_decision_closure", decisions),
        ("phase3_finite_envelopes", envelopes),
    ):
        write_jsonl(REG / f"{stem}.jsonl", rows)
        write_csv(REG / f"{stem}.csv", rows)
    write_jsonl(TRACE / "phase3_bounded_witnesses.jsonl", witnesses)
    write_csv(TRACE / "phase3_bounded_witnesses.csv", witnesses)

    trace_rows: list[dict[str, Any]] = []
    for candidate in candidates:
        for name in candidate["lean_theorems"] + candidate["lean_definitions"]:
            decl = declaration_map[name]
            trace_rows.append({
                "asset_id": candidate["asset_id"], "candidate_id": candidate["candidate_id"],
                "trace_kind": "LEAN_DECLARATION", "trace_id": name,
                "path": decl["file"], "line": decl["line"], "sha256": decl["source_block_sha256"],
            })
        fixture_ids = candidate["positive_scenarios"] + candidate["null_scenarios"] + candidate["countermodels"] + candidate["bounded_witnesses"]
        for fixture_id in fixture_ids:
            if fixture_id.startswith("TTW"):
                path = f"formalization/foundations_vii_lab/fixtures/scenarios/{fixture_id}.json"
            elif fixture_id.startswith("CM"):
                path = f"formalization/foundations_vii_lab/fixtures/countermodels/{fixture_id}.json"
            else:
                path = f"formalization/foundations_vii_lab/phase3/witnesses/{fixture_id}.json"
            full = ROOT / path
            if not full.exists():
                # Some candidate dossiers name Step-3 source scenarios or controls not
                # assigned to Phase 3.  The canonical fixture copy remains the source.
                raise AssertionError(f"missing trace fixture {fixture_id}: {path}")
            trace_rows.append({
                "asset_id": candidate["asset_id"], "candidate_id": candidate["candidate_id"],
                "trace_kind": "FINITE_WITNESS", "trace_id": fixture_id,
                "path": path, "line": "", "sha256": hashlib.sha256(full.read_bytes()).hexdigest(),
            })
    write_jsonl(TRACE / "phase3_asset_trace.jsonl", trace_rows)
    write_csv(TRACE / "phase3_asset_trace.csv", trace_rows)
    (TRACE / "phase3_statement_hashes.sha256").write_text(
        "\n".join(sorted(f"{r['statement_sha256']}  {r['fully_qualified_name']}" for r in theorems)) + "\n",
        encoding="utf-8",
    )

    write_print_axioms(theorems)
    write_candidate_dossiers(candidates)
    write_no_go_dossiers(no_gos)
    write_decision_dossier(decisions)

    summary = {
        "phase": "FVII-SCI-03",
        "stage": (
            "COMPLETE_KERNEL_VERIFIED"
            if KERNEL_REPLAY_PASSED
            else "COMPLETE_SOURCE_LEVEL_EXTERNAL_LEAN_REPLAY_PENDING"
        ),
        "terminal_candidate_count": len(candidates),
        "no_go_count": len(no_gos),
        "formalization_target_count": len(targets),
        "terminal_decision_count": len(decisions),
        "phase3_declaration_count": len(declarations),
        "phase3_theorem_count": len(theorems),
        "finite_envelope_count": len(envelopes),
        "bounded_witness_count": len(witnesses),
        "python_summary": json.loads((LAB3 / "summary.json").read_text(encoding="utf-8")),
        "lean_kernel_status": (
            "PASS_EXTERNAL_REPLAY"
            if KERNEL_REPLAY_PASSED
            else "PENDING_EXTERNAL_LEAN_REPLAY_NONBLOCKING_BY_OWNER_AUTHORIZATION"
        ),
        "no_paper_work": True,
    }
    (REG / "phase3_summary.json").write_text(canonical(summary) + "\n", encoding="utf-8")
    print(canonical(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

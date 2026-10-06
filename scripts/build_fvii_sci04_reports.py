#!/usr/bin/env python3
"""Build deterministic human-readable reports for FVII-SCI-04."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "science" / "registry"
TRACE = ROOT / "science" / "traceability"
REPORTS = ROOT / "reports"
LAB4 = ROOT / "formalization" / "foundations_vii_lab" / "phase4"
LEAN = ROOT / "formalization" / "lean"
DATE = "2026-07-26"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def esc(value: Any) -> str:
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value)
    return str(value).replace("|", "\\|").replace("\n", " ")


def table(headers: list[str], rows: Iterable[Iterable[Any]]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    out.extend("| " + " | ".join(esc(cell) for cell in row) + " |" for row in rows)
    return out


def write(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    declarations = read_jsonl(REG / "phase4_public_declarations.jsonl")
    theorems = read_jsonl(REG / "phase4_theorem_catalog.jsonl")
    candidates = read_jsonl(REG / "phase4_candidate_closure.jsonl")
    no_gos = read_jsonl(REG / "phase4_no_go_closure.jsonl")
    targets = read_jsonl(REG / "phase4_formalization_targets.jsonl")
    decisions = read_jsonl(REG / "phase4_decision_closure.jsonl")
    envelopes = read_jsonl(REG / "phase4_finite_envelopes.jsonl")
    witnesses = read_jsonl(TRACE / "phase4_bounded_witnesses.jsonl")
    lab = read_json(LAB4 / "results" / "summary.json")
    build = read_json(LEAN / "BUILD_STATUS_PHASE4.json")
    validation_path = REPORTS / "FVII_SCI_04_VALIDATION.json"
    validation = read_json(validation_path) if validation_path.exists() else {"status": "NOT_RUN", "pass_count": 0, "check_count": 0}
    lean_pass = build.get("kernel_build_status") == "PASS"
    stage = "FVII-SCI-04_COMPLETE_LEAN_REPLAY_PASS" if lean_pass else "FVII-SCI-04_COMPLETE_WITH_EXTERNAL_LEAN_REPLAY_PENDING"

    main_report = [
        "# FVII-SCI-04 — enablement, descent, dynamics, holonomy, and arrow", "",
        f"**Execution date:** {DATE}",
        f"**Stage:** `{stage}`",
        "**Paper or paper-preparation work:** none", "",
        "Phase 4 closes the dynamic and attribution half of the Foundations VII science program. It supplies source-typed enablement attribution, an exact declared-boundary criterion for endogeny, relation/layer/participant birth classification, typed transmission and descent fidelity, constructive enablement separations, conditional enablement-chain composition, finite confluence and seed-dependence results, interaction holonomy, a no-arrow-from-holonomy theorem with driven positive control, cross-time contact witnesses, and a terminal primitive-algebra decision.", "",
        "## Delivered formal surface", "",
        f"- {len(declarations)} public Phase-4 declarations, including {len(theorems)} theorem/lemma/corollary declarations.",
        f"- {len(candidates)} terminal candidate assets: {', '.join(row['candidate_id'] for row in candidates)}.",
        f"- {len(no_gos)} no-go front: {', '.join(row['no_go_id'] for row in no_gos)}.",
        f"- {len(targets)} formalization-target closure records.",
        f"- {len(decisions)} terminal decision records.",
        f"- {len(envelopes)} bounded exhaustive families: {lab['raw_cases']} raw/canonical cases, {lab['accepted_cases']} accepted, and {lab['rejected_cases']} rejected.",
        f"- {len(witnesses)} retained canonical bounded witnesses.",
        f"- {lab['primary_fixture_replay']['scenario_pass_count']}/{lab['primary_fixture_replay']['scenario_count']} assigned scenarios and {lab['primary_fixture_replay']['countermodel_pass_count']}/{lab['primary_fixture_replay']['countermodel_count']} assigned countermodels pass.", "",
        "## Scientific closure", "",
        "### Enablement and attribution", "",
        "Enablement provenance is represented independently of descent, sufficiency, causation, and endogeny. Source attribution covers theorist, carrier, peer, observer, environment, endogenous system, and mixed cases. Honest bridge refinement preserves the source root; hidden execution invalidates attribution credit.", "",
        "### Endogeny and birth", "",
        "Endogenous credit is exact at the declared boundary: carried, reachable, executed, audited, budgeted, source-closed, and free of hidden theorist or observer execution. Accounted environmental input remains compatible with endogeny. Contact may remain relation-only; participant creation requires closure survival and objecthood.", "",
        "### Transmission, descent, and composition", "",
        "Upward, downward, and peer transmissions carry payload, loss, ambiguity, source, budget, and audit records. A typed descent square states fidelity. Pure downward selection cannot manufacture an absent lower-carrier fact without explicit insertion, and structural selection is not automatically causal. Enablement chains compose only under source/budget/residual/audit compatibility; cost and residual debt accumulate, while transitive causation requires its own certificate.", "",
        "### Confluence, holonomy, arrow, and time", "",
        "Confluence is certified only for a declared closed finite system whose critical pairs are joinable and audit-equivalent. Seed dependence is separated from presentation-only differences. Holonomy records predictive route residue on one typed target but carries zero arrow credit by itself. Directionality additionally requires drive, path asymmetry, failed reversal, budget, and audit. Cross-time contact is licensed by synchronization or partial-order witnesses and remains invariant under admissible clock reparameterization.", "",
        "### Primitive algebra decision", "",
        "The full generators-and-relations program is not ready and is formally deferred. Its reopen gate requires declared generators, equivalence, composition domains, nonredundancy, semantics, and laws. A small associative resource-delta fragment with identity is landed independently.", "",
        "## Boundaries", "",
        "- No universal interaction algebra, global clock, universal simultaneity, transitive causal law, or arrow-from-holonomy implication is claimed.",
        "- Finite enumeration is exhaustive only over the twelve declared bounded families.",
        "- Kernel elaboration, executed axiom receipts, and Lean/Python differential agreement remain pending until the external replay succeeds." if not lean_pass else "- Kernel elaboration, axiom receipts, and Lean/Python differentials passed in the recorded external replay.", "",
        "## Validation", "",
        f"- Acceptance status: `{validation.get('status', 'NOT_RUN')}`.",
        f"- Checks passed: {validation.get('pass_count', 0)}/{validation.get('check_count', 0)}.",
        f"- Lean kernel status: `{build.get('kernel_build_status')}`.",
        f"- External replay directions: `{build.get('external_directions')}`.", "",
    ]
    write(ROOT / "FVII_SCI_04_REPORT.md", main_report)

    formal = ["# FVII-SCI-04 formal asset catalog", "", f"Generated: {DATE}", "", "## Candidate closure", ""]
    formal += table(["Candidate", "Asset", "Definitions", "Theorems", "Grade"], ((r["candidate_id"], r["asset_id"], r["definition_count"], r["theorem_count"], r["phase4_grade"]) for r in candidates))
    formal += ["", "## Formalization targets", ""]
    formal += table(["Target", "Candidates", "Status"], ((r["target_id"], r["candidate_ids"], r["phase4_status"]) for r in targets))
    formal += ["", "## Terminal decisions", ""]
    formal += table(["Decision", "Ruling", "Evidence present"], ((r["decision_id"], r["phase4_terminal_ruling"], r["evidence_present"]) for r in decisions))
    write(REPORTS / "FVII_SCI_04_FORMAL_ASSETS.md", formal)

    finite = ["# FVII-SCI-04 finite evidence", "", f"Evidence grade: `{lab['evidence_grade']}`", "", "## Exhaustive families", ""]
    finite += table(["Family", "Raw", "Canonical", "Accepted", "Rejected", "Candidates"], ((r["family_id"], r["raw_cardinality"], r["canonical_cardinality"], r["accepted_cardinality"], r["rejected_cardinality"], r["candidate_ids"]) for r in envelopes))
    finite += ["", "## Assigned fixture replay", "", f"- Scenarios: {lab['primary_fixture_replay']['scenario_pass_count']}/{lab['primary_fixture_replay']['scenario_count']} pass.", f"- Countermodels: {lab['primary_fixture_replay']['countermodel_pass_count']}/{lab['primary_fixture_replay']['countermodel_count']} pass.", f"- Canonical witnesses: {len(witnesses)}.", "", "These counts are exhaustive only over the declared finite carriers and are not universal proofs.", ""]
    write(REPORTS / "FVII_SCI_04_FINITE_EVIDENCE.md", finite)

    acceptance = ["# FVII-SCI-04 acceptance record", "", f"- Stage: `{stage}`", f"- Validation status: `{validation.get('status', 'NOT_RUN')}`", f"- Passed checks: {validation.get('pass_count', 0)}/{validation.get('check_count', 0)}", f"- Kernel status: `{build.get('kernel_build_status')}`", f"- Candidate assets: {len(candidates)}", f"- No-go fronts: {len(no_gos)}", f"- Decisions: {len(decisions)}", f"- Finite families: {len(envelopes)}", f"- Witnesses: {len(witnesses)}", "", "The owner-authorized nonblocking Lean boundary is truthful only while the build status remains `NOT_RUN_LOCAL_ENVIRONMENT`; a strict external replay must replace it before kernel verification is claimed.", ""]
    write(REPORTS / "FVII_SCI_04_ACCEPTANCE.md", acceptance)

    print(json.dumps({"stage": stage, "declarations": len(declarations), "theorems": len(theorems), "candidates": len(candidates), "envelopes": len(envelopes), "witnesses": len(witnesses)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

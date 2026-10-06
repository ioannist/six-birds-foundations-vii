#!/usr/bin/env python3
"""Build deterministic human-readable science reports for FVII-SCI-03."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "science" / "registry"
TRACE = ROOT / "science" / "traceability"
REPORTS = ROOT / "reports"
LAB3 = ROOT / "formalization" / "foundations_vii_lab" / "phase3"
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
    output = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    output.extend("| " + " | ".join(esc(cell) for cell in row) + " |" for row in rows)
    return output


def write(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    declarations = read_jsonl(REG / "phase3_public_declarations.jsonl")
    theorems = read_jsonl(REG / "phase3_theorem_catalog.jsonl")
    candidates = read_jsonl(REG / "phase3_candidate_closure.jsonl")
    no_gos = read_jsonl(REG / "phase3_no_go_closure.jsonl")
    targets = read_jsonl(REG / "phase3_formalization_targets.jsonl")
    decisions = read_jsonl(REG / "phase3_decision_closure.jsonl")
    envelopes = read_jsonl(REG / "phase3_finite_envelopes.jsonl")
    witnesses = read_jsonl(TRACE / "phase3_bounded_witnesses.jsonl")
    lab = read_json(LAB3 / "results" / "summary.json")
    build = read_json(LEAN / "BUILD_STATUS_PHASE3.json")
    validation_path = REPORTS / "FVII_SCI_03_VALIDATION.json"
    validation = read_json(validation_path) if validation_path.exists() else {
        "status": "NOT_RUN", "pass_count": 0, "check_count": 0,
    }
    lean_pass = build.get("kernel_build_status") == "PASS"
    stage = "FVII-SCI-03_COMPLETE_LEAN_REPLAY_PASS" if lean_pass else "FVII-SCI-03_COMPLETE_WITH_EXTERNAL_LEAN_REPLAY_PENDING"

    main_report = [
        "# FVII-SCI-03 — contact, strict join, obstruction, and certified non-interaction",
        "",
        f"**Execution date:** {DATE}",
        f"**Stage:** `{stage}`",
        "**Paper or paper-preparation work:** none",
        "",
        "Phase 3 closes the central Foundations VII contact/join science program. It supplies typed contact and transport, a declared-family join-status calculus, proof-carrying composite objecthood, anti-product novelty, source and budget gates, parent retention and refinement, residual/needle bookkeeping, coverage-qualified certified non-interaction, and terminal categorical/scalar decisions. Enablement, descent dynamics, confluence, holonomy, arrows, cross-time contact, and final cross-family corollaries remain reserved for later phases.",
        "",
        "## Delivered formal surface",
        "",
        f"- {len(declarations)} public Phase-3 declarations, including {len(theorems)} theorem/lemma/corollary declarations.",
        f"- {len(candidates)} terminal candidate assets: {', '.join(row['candidate_id'] for row in candidates)}.",
        f"- {len(no_gos)} no-go fronts with exact structural scope, finite failure controls, and named positive escapes.",
        f"- {len(targets)} formalization targets closed or explicitly partially closed; dynamical portions of FT19 and FT20 remain reserved for Phase 4.",
        f"- {len(decisions)} terminal scope decisions, each tied to source declarations.",
        f"- {len(envelopes)} bounded exhaustive families: {lab['raw_cases']} raw, {lab['canonical_cases']} canonical, {lab['accepted_cases']} accepted, and {lab['rejected_cases']} rejected cases.",
        f"- {len(witnesses)} retained canonical bounded witnesses.",
        f"- Primary fixture replay: {lab['primary_fixture_replay']['scenario_pass_count']}/12 scenarios and {lab['primary_fixture_replay']['countermodel_pass_count']}/14 countermodels pass.",
        f"- Acceptance gate: {validation['status']} ({validation.get('pass_count', 0)}/{validation.get('check_count', 0)} checks).",
        "",
        "## Terminal candidate assets",
        "",
    ]
    main_report += table(
        ["Candidate", "Asset", "Definitions", "Theorems", "Witnesses", "Kernel status"],
        (
            [
                row["candidate_id"], row["asset_id"], row["definition_count"],
                row["theorem_count"], row["bounded_witnesses"],
                "PASS" if lean_pass else "external replay pending",
            ]
            for row in candidates
        ),
    )
    main_report += ["", "## Five no-go fronts", ""]
    main_report += table(
        ["No-go", "Scope", "Failure scenarios", "Positive controls", "Escape theorem count"],
        (
            [
                row["no_go_id"], row["scope"], row["failure_scenarios"],
                row["positive_controls"], len(row["escape_theorems"]),
            ]
            for row in no_gos
        ),
    )
    main_report += [
        "",
        "## Scientific conclusions fixed by this phase",
        "",
        "- Compatibility, evidenced contact, transport, lawful composite formation, common refinement, strict join, typed obstruction, and certified non-interaction are distinct typed states.",
        "- Peer contact can transmit certified content while preserving destination ownership and provenance without forming a composite or join.",
        "- Strict-join credit requires separate objecthood, parent retention, anti-product novelty, source, and budget evidence. Directionality is not supplied by strictness.",
        "- Mere relabeling, scheduling, coarsening, product formation, common refinement, resemblance, or one-lineage re-expression cannot receive strict or independence-sensitive join credit under the stated hypotheses.",
        "- Positive-cost join credit requires actual payment or a certified zero-cost channel; positive observer cost cannot be hidden.",
        "- Finite live-join capacity is bounded only under the stated capacity ledger. No universal scalar join currency is inferred.",
        "- Parent refinement may preserve, strengthen, weaken, or destroy join evidence. There is no unconditional monotonicity theorem.",
        "- Residuals are sourced as inherited, dissolved, or newly created; an active sourced cross-term can create a join-specific needle, while relabeling alone cannot.",
        "- No observed contact is weaker than certified non-interaction. Certification requires exact declared family, detector, budget, horizon, and closure coverage, with outside-family channels remaining explicit escapes.",
        "- Unconditional product/pullback/pushout identification is rejected. Only explicitly checked special-case categorical representations receive credit.",
        "- The tested natural contact quantities have lawful nonconservation controls; no universal conserved contact degree is claimed.",
        "",
        "## Lean execution boundary",
        "",
        (
            "The cumulative library has passed the recorded kernel build, Phase-1/2/3 finite differentials, and generated axiom replay."
            if lean_pass else
            "Lean and Lake were unavailable locally. The repository therefore claims source-complete theorem assets, static import/trust closure, executed Python finite evidence, and deterministic source/registry traceability—but not kernel elaboration, executed `#print axioms`, or runtime Lean/Python agreement. The owner authorized this external replay boundary as nonblocking."
        ),
        "",
        "Run `bash scripts/run_fvii_sci03_external_lean.sh` in a Lean-capable environment. A compatible Lean 4 version may replace the current pin when that change is committed and the complete cumulative replay succeeds.",
        "",
        "## Boundaries retained",
        "",
        "- The eleven finite envelopes are exhaustive only over their declared bounded universes.",
        "- Static source validation is not a substitute for Lean kernel checking.",
        "- The join-status classifier is terminal only for its declared finite evidence family; it is not a universal ontology of all interactions.",
        "- Categorical special cases do not imply an unconditional categorical reduction.",
        "- Natural scalar nonconservation controls do not prove that no specialized invariant can exist under additional hypotheses.",
        "- Phase 3 does not implement enablement, descent, confluence, holonomy/arrow separation, cross-time contact, or final corollaries.",
        "- No paper text or paper-preparation artifact was created.",
        "",
        "## Authoritative surfaces",
        "",
        "- `science/registry/phase3_public_declarations.jsonl` and `phase3_theorem_catalog.jsonl`",
        "- `science/registry/phase3_candidate_closure.jsonl`",
        "- `science/registry/phase3_no_go_closure.jsonl`",
        "- `science/registry/phase3_formalization_targets.jsonl` and `phase3_decision_closure.jsonl`",
        "- `science/traceability/phase3_asset_trace.jsonl` and `phase3_statement_hashes.sha256`",
        "- `formalization/foundations_vii_lab/phase3/results/`",
        "- `reports/FVII_SCI_03_VALIDATION.md`",
    ]
    write(ROOT / "FVII_SCI_03_REPORT.md", main_report)
    write(REPORTS / "FVII_SCI_03_REPORT.md", main_report)

    lean_lines = [
        "# FVII-SCI-03 Lean assets and trust boundary",
        "",
        f"- Public Phase-3 declarations: {len(declarations)}",
        f"- Theorem/lemma/corollary declarations: {len(theorems)}",
        f"- Phase-3 public source modules: {len(set(row['file'] for row in declarations))}",
        "- VII-owned `sorry`, `admit`, new `axiom`, `opaque`, or `unsafe`: zero by static audit",
        f"- Requested/current toolchain: `{build['toolchain']}`",
        f"- Kernel status: `{build['kernel_build_status']}`",
        f"- Generated `#print axioms` commands: {len(theorems)}",
        "",
        "## Public declaration census",
        "",
    ]
    lean_lines += table(
        ["Asset", "Kind", "Declaration", "Source", "Statement hash", "Kernel status"],
        (
            [
                row["science_asset_id"], row["kind"], row["fully_qualified_name"],
                f"{row['file']}:{row['line']}", row["statement_sha256"], row["kernel_status"],
            ]
            for row in declarations
        ),
    )
    lean_lines += [
        "",
        "`formalization/lean/FoundationsVII/Trust/PrintAxiomsPhase3.lean` contains exactly one command per Phase-3 theorem. The external replay captures the result without silently upgrading any scientific grade.",
    ]
    write(REPORTS / "FVII_SCI_03_LEAN_ASSETS.md", lean_lines)

    finite_lines = [
        "# FVII-SCI-03 bounded contact/join laboratory",
        "",
        f"The independent Python enumerator executes {len(envelopes)} declared families and retains {len(witnesses)} canonical witnesses. The Lean runner independently defines matching cardinality and assigned-fixture surfaces; runtime differential replay is {'recorded as PASS' if lean_pass else 'pending external execution'}.",
        "",
    ]
    finite_lines += table(
        ["Family", "Description", "Raw", "Canonical", "Accepted", "Rejected", "Boundary"],
        (
            [
                row["family_id"], row["description"], row["raw_cardinality"],
                row["canonical_cardinality"], row["accepted_cardinality"],
                row["rejected_cardinality"], row["nonclaim"],
            ]
            for row in envelopes
        ),
    )
    finite_lines += ["", "## Canonical witnesses", ""]
    finite_lines += table(
        ["Witness", "Candidate", "Shows", "Assignment hash"],
        ([row["witness_id"], row["candidate_id"], row["shows"], row["assignment_sha256"]] for row in witnesses),
    )
    finite_lines += [
        "",
        "Minimality is only within each declared finite family and deterministic ordering. The witnesses expose omission attacks and calibrate hypotheses; they do not replace the structural theorem sources.",
    ]
    write(REPORTS / "FVII_SCI_03_FINITE_LAB.md", finite_lines)

    candidate_lines = [
        "# FVII-SCI-03 candidate closure",
        "",
        "All thirteen assigned candidates end with terminal source assets rather than readiness-only specifications. Kernel status remains separately recorded.",
        "",
    ]
    candidate_lines += table(
        ["Candidate", "Name", "Grade", "Targets", "Positive", "Null", "Countermodels", "Nonclaim"],
        (
            [
                row["candidate_id"], row["name"], row["phase3_grade"],
                row["formalization_targets"], row["positive_scenarios"],
                row["null_scenarios"], row["countermodels"], row["nonclaim"],
            ]
            for row in candidates
        ),
    )
    write(REPORTS / "FVII_SCI_03_CANDIDATE_CLOSURE.md", candidate_lines)

    nogo_lines = [
        "# FVII-SCI-03 no-go closure",
        "",
        "Each row has a structural statement only over its exact typed hypotheses, finite failure controls, and separately named escapes.",
        "",
    ]
    nogo_lines += table(
        ["No-go", "Theorem", "Escape theorems", "Failures", "Controls", "Scope", "Status"],
        (
            [
                row["no_go_id"], row["theorem"], row["escape_theorems"],
                row["failure_scenarios"], row["positive_controls"], row["scope"],
                row["terminal_status"],
            ]
            for row in no_gos
        ),
    )
    write(REPORTS / "FVII_SCI_03_NO_GOS.md", nogo_lines)

    decision_lines = [
        "# FVII-SCI-03 terminal decisions",
        "",
        "These eight rulings close the contact/join decision load at the declared scope while preserving stronger questions as future theorem obligations rather than rhetoric.",
        "",
    ]
    decision_lines += table(
        ["Decision", "Question", "Terminal ruling", "Evidence declarations", "Boundary"],
        (
            [
                row["decision_id"], row["question"], row["phase3_terminal_ruling"],
                row["evidence_declarations"], row["nonclaim"],
            ]
            for row in decisions
        ),
    )
    write(REPORTS / "FVII_SCI_03_DECISIONS.md", decision_lines)

    target_lines = [
        "# FVII-SCI-03 formalization-target closure",
        "",
        "Phase 3 closes the contact/join portions assigned by the science plan. FT19 and FT20 retain explicitly named dynamical portions for Phase 4.",
        "",
    ]
    target_lines += table(
        ["Target", "Name", "Candidates", "Prior status", "Phase-3 status", "Theorem count", "Kernel status"],
        (
            [
                row["target_id"], row["name"], row["candidate_ids"],
                row["prior_phase_status"], row["phase3_status"],
                len(row["phase3_theorems"]), row["kernel_status"],
            ]
            for row in targets
        ),
    )
    write(REPORTS / "FVII_SCI_03_TARGETS.md", target_lines)

    external_lines = [
        "# FVII-SCI-03 external Lean replay",
        "",
        f"Current repository pin: `{build['toolchain']}`. The owner permits a different compatible Lean 4 version when that is easier, provided the change is recorded and the complete cumulative replay passes.",
        "",
        "```bash",
        "bash scripts/run_fvii_sci03_external_lean.sh",
        "```",
        "",
        "The script rebuilds the cumulative library, executes the Phase-1 51-case runner, Phase-2 nine-envelope runner, and Phase-3 eleven-envelope plus assigned-fixture runner; captures all three axiom surfaces; compares Lean outputs to independent Python results; and invokes the strict Phase-3 validator.",
        "",
        "Until that script succeeds, `NOT_RUN_LOCAL_ENVIRONMENT` is the truthful kernel status.",
    ]
    write(REPORTS / "FVII_SCI_03_EXTERNAL_LEAN_REPLAY.md", external_lines)

    generated = {
        "date": DATE,
        "phase": "FVII-SCI-03",
        "status": stage,
        "public_declarations": len(declarations),
        "theorem_lemma_corollary_declarations": len(theorems),
        "terminal_candidates": len(candidates),
        "no_go_fronts": len(no_gos),
        "formalization_targets": len(targets),
        "terminal_decisions": len(decisions),
        "finite_envelopes": len(envelopes),
        "bounded_witnesses": len(witnesses),
        "raw_cases": lab["raw_cases"],
        "canonical_cases": lab["canonical_cases"],
        "accepted_cases": lab["accepted_cases"],
        "rejected_cases": lab["rejected_cases"],
        "primary_scenario_pass_count": lab["primary_fixture_replay"]["scenario_pass_count"],
        "primary_countermodel_pass_count": lab["primary_fixture_replay"]["countermodel_pass_count"],
        "lean_kernel_status": build["kernel_build_status"],
        "validation_status": validation["status"],
        "paper_assets_created": 0,
    }
    (ROOT / "generated" / "fvii_sci03_summary.json").write_text(
        json.dumps(generated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    toolchain = {
        "date": DATE,
        "requested": build["toolchain"],
        "lean_executable": shutil.which("lean"),
        "lake_executable": shutil.which("lake"),
        "elan_executable": shutil.which("elan"),
        "kernel_build_status": build["kernel_build_status"],
        "policy": "Compatible Lean 4 version permitted if committed and cumulative replay passes.",
    }
    (ROOT / "generated" / "fvii_sci03_toolchain_status.json").write_text(
        json.dumps(toolchain, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(generated, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

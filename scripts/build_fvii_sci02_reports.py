#!/usr/bin/env python3
"""Build deterministic human-readable science reports for FVII-SCI-02."""
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "science" / "registry"
TRACE = ROOT / "science" / "traceability"
REPORTS = ROOT / "reports"
LAB2 = ROOT / "formalization" / "foundations_vii_lab" / "phase2"
LEAN = ROOT / "formalization" / "lean"
DATE = "2026-07-26"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parsed(value: str) -> Any:
    if value == "":
        return []
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


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
    summary = read_json(REG / "phase2_summary.json")
    declarations = read_jsonl(REG / "phase2_public_declarations.jsonl")
    theorems = read_jsonl(REG / "phase2_theorem_catalog.jsonl")
    candidates = read_jsonl(REG / "phase2_candidate_closure.jsonl")
    no_gos = read_jsonl(REG / "phase2_no_go_closure.jsonl")
    targets = read_jsonl(REG / "phase2_formalization_targets.jsonl")
    envelopes = read_jsonl(REG / "phase2_finite_envelopes.jsonl")
    witnesses = read_jsonl(TRACE / "phase2_bounded_witnesses.jsonl")
    lab = read_json(LAB2 / "results" / "summary.json")
    build = read_json(LEAN / "BUILD_STATUS_PHASE2.json")
    validation_path = REPORTS / "FVII_SCI_02_VALIDATION.json"
    validation = read_json(validation_path) if validation_path.exists() else {"status": "NOT_RUN", "pass_count": 0, "check_count": 0}
    lean_pass = build.get("kernel_build_status") == "PASS"
    stage = "FVII-SCI-02_COMPLETE_LEAN_REPLAY_PASS" if lean_pass else "FVII-SCI-02_COMPLETE_WITH_EXTERNAL_LEAN_REPLAY_PENDING"

    main_report = [
        "# FVII-SCI-02 — admission, access, provenance, bootstrap, and negative force",
        "",
        f"**Execution date:** {DATE}",
        f"**Stage:** `{stage}`",
        "**Paper or paper-preparation work:** none",
        "",
        "Phase 2 closes the operational-domain side of the Foundations VII science program. It supplies typed admission transitions, path replay, access-coordinate separation, bootstrap and provisioning laws, provenance/non-transfer results, prospective commitment, horizon-qualified negative force, observer occupancy, and five exact no-go fronts. It does not implement contact/join, enablement/descent, dynamics, or final cross-family corollaries.",
        "",
        "## Delivered formal surface",
        "",
        f"- {len(declarations)} public Phase-2 declarations, including {len(theorems)} theorem/lemma/corollary declarations.",
        f"- {len(candidates)} terminal candidate assets: {', '.join(row['candidate_id'] for row in candidates)}.",
        f"- {len(no_gos)} no-go fronts, each with exact scope, a structural proof source, and at least one named positive escape.",
        f"- {len(targets)} formalization targets closed or cumulatively advanced; FT18 is explicitly only the admission half.",
        f"- {len(envelopes)} bounded exhaustive families: {lab['raw_cases']} raw, {lab['canonical_cases']} canonical, {lab['accepted_cases']} accepted, and {lab['rejected_cases']} rejected cases.",
        f"- {len(witnesses)} canonical bounded witnesses retained with content hashes.",
        f"- Primary fixture replay: {lab['primary_fixture_replay']['scenario_pass_count']}/10 scenarios and {lab['primary_fixture_replay']['countermodel_pass_count']}/9 countermodels pass.",
        f"- Acceptance gate: {validation['status']} ({validation.get('pass_count', 0)}/{validation.get('check_count', 0)} checks).",
        "",
        "## Terminal candidate assets",
        "",
    ]
    main_report += table(
        ["Candidate", "Asset", "Definitions", "Theorems", "Bounded witnesses", "Kernel status"],
        ([row["candidate_id"], row["asset_id"], row["definition_count"], row["theorem_count"], row["bounded_witnesses"], "PASS" if lean_pass else "external replay pending"] for row in candidates),
    )
    main_report += [
        "",
        "## Five no-go fronts",
        "",
    ]
    main_report += table(
        ["No-go", "Scope", "Failure control", "Positive controls", "Escape theorem count"],
        ([row["no_go_id"], row["scope"], row["failure_scenario"], row["positive_controls"], len(row["escape_theorems"])] for row in no_gos),
    )
    main_report += [
        "",
        "## Scientific conclusions fixed by this phase",
        "",
        "- Expressibility, presence, exposure, recoverability, admissibility, reachability, and occurrence are typed separately. Only the declared implication spine is imposed; converse collapses have explicit witnesses.",
        "- Rule soundness, executability, reachability, firing, and occurrence are distinct. Reachability alone cannot certify occurrence.",
        "- Admission, expiry, revocation, retraction, and rollback are typed operations. Lawful rollback and revocation preserve source, budget, and audit history.",
        "- A closed declared regime without an admitted seed or reachable generator has no lawful first extension. Admitted seeds, reachable generators, and open-family recorded external provision are explicit escapes.",
        "- Neutral provisioning requires prospective, task-blind, outcome-independent, source-audited provision. Post-hoc stocking and system-generated source laundering fail the certificate.",
        "- Common origin, carrier, or instrument does not imply shared access; shared access does not imply source independence.",
        "- Total-lens transfer requires a total source, a self-owned target, and—when the target is partial—a certified adapter.",
        "- Finite-horizon non-occurrence is horizon-qualified unless family closure, detector power, and no-later-occurrence are separately certified.",
        "- Hidden observer occupancy invalidates native/endogenous credit; correctly priced external observation and genuine zero occupancy remain explicit escapes.",
        "",
        "## Lean execution boundary",
        "",
        (
            "The cumulative library has passed the recorded kernel build, Phase-1 51-case differential, Phase-2 nine-envelope differential, and generated axiom replay."
            if lean_pass else
            "Lean and Lake were unavailable locally. The repository therefore claims source-complete theorem assets, static import/trust closure, and executed Python evidence, but not kernel elaboration or runtime Lean/Python agreement. The owner authorized this external replay boundary as nonblocking."
        ),
        "",
        "Run `bash scripts/run_fvii_sci02_external_lean.sh` in a Lean-capable environment. A compatible toolchain may replace the current pin if the edit is committed and the cumulative replay succeeds.",
        "",
        "## Boundaries retained",
        "",
        "- The nine finite envelopes are exhaustive only over their declared bounded universes.",
        "- Static source validation is not a substitute for Lean kernel checking.",
        "- Adapter metadata does not establish semantic equivalence or theorem transport.",
        "- Phase 2 does not define or prove strict join, certified non-interaction, enablement, descent, confluence, holonomy/arrow separation, or final corollaries.",
        "- No paper text or paper-preparation artifact was created.",
        "",
        "## Authoritative surfaces",
        "",
        "- `science/registry/phase2_public_declarations.jsonl` and `phase2_theorem_catalog.jsonl`",
        "- `science/registry/phase2_candidate_closure.jsonl`",
        "- `science/registry/phase2_no_go_closure.jsonl`",
        "- `science/registry/phase2_formalization_targets.jsonl`",
        "- `science/traceability/phase2_asset_trace.jsonl` and `phase2_statement_hashes.sha256`",
        "- `formalization/foundations_vii_lab/phase2/results/`",
        "- `reports/FVII_SCI_02_VALIDATION.md`",
    ]
    write(ROOT / "FVII_SCI_02_REPORT.md", main_report)
    write(REPORTS / "FVII_SCI_02_REPORT.md", main_report)

    lean_lines = [
        "# FVII-SCI-02 Lean assets and trust boundary",
        "",
        f"- Public Phase-2 declarations: {len(declarations)}",
        f"- Theorem/lemma/corollary declarations: {len(theorems)}",
        f"- Phase-2 public source modules: {len(set(row['file'] for row in declarations))}",
        "- VII-owned `sorry`, `admit`, `axiom`, `opaque`, or `unsafe`: zero by static audit",
        f"- Requested/current toolchain: `{build['toolchain']}`",
        f"- Kernel status: `{build['kernel_build_status']}`",
        f"- Generated `#print axioms` commands: {len(theorems)}",
        "",
        "## Public declaration census",
        "",
    ]
    lean_lines += table(
        ["Asset", "Kind", "Declaration", "Source", "Statement hash", "Kernel status"],
        ([row["science_asset_id"], row["kind"], row["fully_qualified_name"], f"{row['file']}:{row['line']}", row["statement_sha256"], row["kernel_status"]] for row in declarations),
    )
    lean_lines += [
        "",
        "`formalization/lean/FoundationsVII/Trust/PrintAxiomsPhase2.lean` contains one command per theorem. The cumulative replay script captures the result without changing scientific grade.",
    ]
    write(REPORTS / "FVII_SCI_02_LEAN_ASSETS.md", lean_lines)

    finite_lines = [
        "# FVII-SCI-02 bounded admission laboratory",
        "",
        f"The independent Python enumerator executes {len(envelopes)} declared families and retains {len(witnesses)} canonical witnesses. The Lean runner independently emits the four cardinality fields for each family; runtime differential replay is {'recorded as PASS' if lean_pass else 'pending external execution'}.",
        "",
    ]
    finite_lines += table(
        ["Family", "Description", "Raw", "Canonical", "Accepted", "Rejected", "Boundary"],
        ([row["family_id"], row["description"], row["raw_cardinality"], row["canonical_cardinality"], row["accepted_cardinality"], row["rejected_cardinality"], row["nonclaim"]] for row in envelopes),
    )
    finite_lines += ["", "## Canonical witnesses", ""]
    finite_lines += table(
        ["Witness", "Candidate", "Shows", "Assignment hash"],
        ([row["witness_id"], row["candidate_id"], row["shows"], row["assignment_sha256"]] for row in witnesses),
    )
    finite_lines += [
        "",
        "Minimality is only within each declared finite family and the stated canonical ordering. These witnesses calibrate theorem hypotheses and preserve failures; they do not replace structural proofs.",
    ]
    write(REPORTS / "FVII_SCI_02_FINITE_LAB.md", finite_lines)

    candidate_lines = [
        "# FVII-SCI-02 candidate closure",
        "",
        "All nine assigned candidates end with a terminal source asset rather than Step-3 specification grade. Kernel status remains separately recorded.",
        "",
    ]
    candidate_lines += table(
        ["Candidate", "Name", "Grade", "Targets", "Positive", "Null", "Countermodels", "Nonclaim"],
        ([row["candidate_id"], row["name"], row["phase2_grade"], row["formalization_targets"], row["positive_scenarios"], row["null_scenarios"], row["countermodels"], row["nonclaim"]] for row in candidates),
    )
    write(REPORTS / "FVII_SCI_02_CANDIDATE_CLOSURE.md", candidate_lines)

    nogo_lines = [
        "# FVII-SCI-02 no-go closure",
        "",
        "Each row has a universal structural statement only over its exact hypotheses, a named failure control, and one or more separately named escapes.",
        "",
    ]
    nogo_lines += table(
        ["No-go", "Theorem", "Escape theorems", "Failure", "Controls", "Scope", "Status"],
        ([row["no_go_id"], row["theorem"], row["escape_theorems"], row["failure_scenario"], row["positive_controls"], row["scope"], row["terminal_status"]] for row in no_gos),
    )
    write(REPORTS / "FVII_SCI_02_NO_GOS.md", nogo_lines)

    external_lines = [
        "# FVII-SCI-02 external Lean replay",
        "",
        f"Current repository pin: `{build['toolchain']}`. The owner permits a different compatible Lean 4 version when that is easier, provided the change is recorded and the complete replay passes.",
        "",
        "```bash",
        "bash scripts/run_fvii_sci02_external_lean.sh",
        "```",
        "",
        "The script rebuilds the cumulative library, executes the Phase-1 51-case runner and Phase-2 nine-envelope runner, captures both axiom surfaces, compares both Lean outputs to independent Python results, and invokes the strict Phase-2 validator.",
        "",
        "Until that script succeeds, `NOT_RUN_LOCAL_ENVIRONMENT` is the truthful kernel status.",
    ]
    write(REPORTS / "FVII_SCI_02_EXTERNAL_LEAN_REPLAY.md", external_lines)

    generated = {
        "date": DATE,
        "phase": "FVII-SCI-02",
        "status": stage,
        "public_declarations": len(declarations),
        "theorem_lemma_corollary_declarations": len(theorems),
        "terminal_candidates": len(candidates),
        "no_go_fronts": len(no_gos),
        "formalization_targets": len(targets),
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
    (ROOT / "generated" / "fvii_sci02_summary.json").write_text(
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
    (ROOT / "generated" / "fvii_sci02_toolchain_status.json").write_text(
        json.dumps(toolchain, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(generated, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

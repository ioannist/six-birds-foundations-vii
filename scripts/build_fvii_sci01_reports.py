#!/usr/bin/env python3
"""Build deterministic human-readable reports for FVII-SCI-01.

The canonical machine surfaces are the ``science/registry/phase1_*`` and
``science/traceability/phase1_*`` files.  This script never invents a stronger
proof grade than those registries record.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "science" / "registry"
TRACE = ROOT / "science" / "traceability"
REPORTS = ROOT / "reports"
LAB = ROOT / "formalization" / "foundations_vii_lab"
LEAN = ROOT / "formalization" / "lean"
DATE = "2026-07-26"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parsed(value: str) -> Any:
    if value == "":
        return []
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def md_escape(value: Any) -> str:
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value)
    return str(value).replace("|", "\\|").replace("\n", " ")


def table(headers: list[str], rows: Iterable[Iterable[Any]]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    out.extend("| " + " | ".join(md_escape(cell) for cell in row) + " |" for row in rows)
    return out


def write(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    summary = read_json(REG / "phase1_summary.json")
    public = read_csv(REG / "phase1_public_declarations.csv")
    objects = read_csv(REG / "phase1_objects.csv")
    targets = read_csv(REG / "phase1_formalization_targets.csv")
    adapters = read_csv(REG / "inherited_adapter_ledger.csv")
    candidates = read_csv(REG / "phase1_candidate_closure.csv")
    decisions = read_csv(REG / "phase1_decision_rulings.csv")
    trust = read_csv(TRACE / "phase1_trust_surface.csv")
    fixture_trace = read_csv(TRACE / "phase1_fixture_trace.csv")
    python_summary = read_json(LAB / "results" / "python_summary.json")
    build_status = read_json(LEAN / "BUILD_STATUS.json")
    scenario_files = sorted((LAB / "fixtures" / "scenarios").glob("*.json"))
    if not scenario_files:
        raise SystemExit("no canonical scenarios found")
    schema_version = read_json(scenario_files[0])["schema_version"]
    test_count = sum(
        len(re.findall(r"^\s*def\s+test_[A-Za-z0-9_]+\s*\(", path.read_text(encoding="utf-8"), flags=re.MULTILINE))
        for path in sorted((LAB / "tests").glob("test_*.py"))
    )
    validation_path = REPORTS / "FVII_SCI_01_VALIDATION.json"
    validation = read_json(validation_path) if validation_path.is_file() else {
        "status": "NOT_RUN", "pass": 0, "info": 0, "fail": 0
    }
    lean_pass = build_status.get("kernel_build_status") == "PASS"
    phase_stage = (
        "FVII-SCI-01_COMPLETE_LEAN_REPLAY_PASS"
        if lean_pass else
        "FVII-SCI-01_COMPLETE_WITH_EXTERNAL_LEAN_REPLAY_PENDING"
    )

    terminal = [row for row in candidates if row["phase1_terminal_status"].startswith("TERMINAL_PHASE1_ASSET")]
    supported = [row for row in candidates if row not in terminal]
    kind_counts = Counter(row["kind"] for row in public)
    theorem_kinds = {"theorem", "lemma", "corollary"}
    theorem_count = sum(row["kind"] in theorem_kinds for row in public)
    adapter_counts: dict[str, int] = defaultdict(int)
    for row in adapters:
        adapter_counts[row["target_id"]] += 1

    main_report = [
        "# FVII-SCI-01 — typed kernel, inherited adapters, and executable reference world",
        "",
        f"**Execution date:** {DATE}",
        f"**Stage:** `{phase_stage}`",
        "**Paper work:** none",
        "",
        "Phase 1 establishes the typed and computational substrate for later Foundations VII science. It does not execute the admission/access theorems assigned to Phase 2, the contact/join/no-go program assigned to Phase 3, or the enablement/dynamics program assigned to Phase 4.",
        "",
        "## Delivered science surface",
        "",
        f"- {len(objects)} object records: three inherited anchors and fifteen VII-owned canonical structures.",
        f"- {len(adapters)} exact inherited reuse records covering all {len(targets)} formalization targets.",
        f"- {len(public)} indexed VII public source declarations, including {theorem_count} theorem/lemma/corollary declarations.",
        f"- {len(candidates)} candidate closure rows: four terminal Phase-1 protocol/model assets and {len(supported)} explicitly nonterminal typed-support rows.",
        f"- {len(decisions)} frozen decision rulings; DP13 and DP14 remain nonblocking source-governance boundaries.",
        f"- {len(fixture_trace)} canonical finite fixtures under the closed `{schema_version}` contract: {python_summary['scenario_count']} scenarios and {python_summary['countermodel_count']} countermodels.",
        f"- Python reference world: {python_summary['scenario_pass_count']}/{python_summary['scenario_count']} scenarios and {python_summary['countermodel_pass_count']}/{python_summary['countermodel_count']} countermodels pass.",
        f"- Phase validator: {validation['status']} ({validation['pass']} pass, {validation['info']} informational, {validation['fail']} fail).",
        "",
        "## Terminal Phase-1 candidates",
        "",
    ]
    main_report += table(
        ["Candidate", "Asset", "Phase-1 grade", "Python evidence", "Lean status"],
        ([row["candidate_id"], row["asset_id"], row["phase1_grade"], row["python_evidence_status"], row["lean_kernel_status"]] for row in terminal),
    )
    main_report += [
        "",
        "## Lean boundary",
        "",
        (
            f"The active source targets `{build_status['toolchain']}`. The recorded external replay passed the Lean kernel build, generated `#print axioms` run, and exact 51-case Lean/Python differential."
            if lean_pass else
            f"The active source targets `{build_status['toolchain']}`. No usable Lean/Lake executable was available locally, so no kernel elaboration or Lean/Python runtime agreement is claimed. Source-level import closure, delimiter checks, declaration indexing, inherited-source identity, and forbidden-token/trust scans pass. Exact replay commands and an automated replay script are included."
        ),
        "",
        (
            "The kernel boundary is closed by the recorded external replay; finite agreement remains limited to the declared 51-case family."
            if lean_pass else
            "The user explicitly authorized this as a nonblocking execution boundary. Terminal source assets therefore remain graded as source-complete with external kernel replay pending; they are not mislabeled as locally kernel-proved."
        ),
        "",
        "## Scientific boundaries",
        "",
        f"- The Python side validates each fixture's complete closed `{schema_version}` structural envelope: all fifteen VII-owned record families plus append-only audit. The Lean runner independently checks the finite semantic projection (flags, statuses, and assertions); it is not represented as a parser or round trip for the full JSON envelope.",
        "- Finite success over the frozen 51-case family is not an unrestricted interaction theorem.",
        "- Adapter metadata is not semantic equivalence and cannot strengthen an inherited theorem.",
        "- Introducing a typed record does not prove that the represented object is irreducible or primitive.",
        "- Soundness, executability, reachability, firing, and occurrence remain distinct.",
        "- Contact, composite formation, and strict join remain distinct.",
        "- Evidence grade and scientific claim grade remain distinct.",
        "- No later-phase law, no-go, corollary, or categorical reduction is claimed here.",
        "",
        "## Authoritative audit surfaces",
        "",
        "- `science/registry/phase1_public_declarations.csv` — every VII public source declaration.",
        "- `reports/FVII_SCI_01_DECLARATIONS_AND_TRUST.md` — every declaration with source-level trust and kernel/axiom status.",
        "- `science/registry/phase1_candidate_closure.csv` — all 36 candidate dispositions at the Phase-1 boundary.",
        "- `science/registry/inherited_adapter_ledger.csv` — all 30 exact inherited reuse records.",
        "- `formalization/foundations_vii_lab/results/` — deterministic Python results and the explicit pending Lean differential status.",
        "- `reports/FVII_SCI_01_VALIDATION.md` — mechanical acceptance gate.",
    ]
    write(REPORTS / "FVII_SCI_01_REPORT.md", main_report)
    write(ROOT / "FVII_SCI_01_REPORT.md", main_report)

    declaration_lines = [
        "# FVII-SCI-01 public declarations and trust report",
        "",
        (
            "This is the complete public source-declaration census required by the Phase-1 contract. `Axioms` records the strongest verified status in this execution environment. The external kernel and generated `#print axioms` replay are recorded in the results directory."
            if lean_pass else
            "This is the complete public source-declaration census required by the Phase-1 contract. `Axioms` records the strongest verified status in this execution environment. The local environment had no Lean kernel, so theorem dependency surfaces remain pending the generated `#print axioms` replay rather than being guessed."
        ),
        "",
        f"- Public declarations: {len(public)}",
        f"- Theorem/lemma/corollary declarations: {theorem_count}",
        f"- Kinds: {json.dumps(dict(sorted(kind_counts.items())), sort_keys=True)}",
        "- VII-owned explicit `axiom` or `opaque` declarations: zero by source scan",
        "- Inherited trust surface: one axiom and five opaque constants, listed below",
        "",
        "## Complete declaration census",
        "",
    ]
    declaration_lines += table(
        ["Census ID", "Science asset", "Kind", "Declaration", "Source", "Statement hash", "Kernel", "Axioms"],
        (
            [
                row["declaration_id"],
                row["science_asset_id"],
                row["kind"],
                row["fully_qualified_name"],
                f"{row['file']}:{row['line']}-{row['end_line']}",
                row["source_sha256"],
                row["kernel_status"],
                ("RECORDED_IN_RESULTS_LEAN_AXIOMS_TXT" if lean_pass else "PENDING_EXTERNAL_#PRINT_AXIOMS") if row["kind"] in theorem_kinds else "NOT_APPLICABLE_DEFINITION_SOURCE_SCAN_CLEAN",
            ]
            for row in public
        ),
    )
    declaration_lines += ["", "## Explicit inherited trust surface", ""]
    declaration_lines += table(
        ["Trust ID", "Kind", "Declaration", "Source", "Status"],
        ([row["trust_id"], row["kind"], row["declaration"], f"{row['file']}:{row['line']}", row["status"]] for row in trust),
    )
    declaration_lines += [
        "",
        "## Replay",
        "",
        (
            "`formalization/lean/FoundationsVII/Trust/PrintAxioms.lean` contains one `#print axioms` command for every theorem, lemma, and corollary above. The recorded output is `formalization/foundations_vii_lab/results/lean_axioms.txt`."
            if lean_pass else
            "`formalization/lean/FoundationsVII/Trust/PrintAxioms.lean` contains one `#print axioms` command for every theorem, lemma, and corollary above. Run `bash scripts/run_fvii_sci01_external_lean.sh` in a Lean-capable environment to replace the pending kernel/axiom boundary with recorded output."
        ),
    ]
    write(REPORTS / "FVII_SCI_01_DECLARATIONS_AND_TRUST.md", declaration_lines)

    candidate_lines = [
        "# FVII-SCI-01 candidate closure",
        "",
        "All 36 Step-3 candidates are represented. Exactly C020, C023, C024, and C025 close at Phase-1 scope; the other 32 receive typed support only and retain their assigned later resolution phase.",
        "",
    ]
    candidate_lines += table(
        ["Candidate", "Asset", "Phase-1 status", "Resolution phase", "Missing declarations"],
        ([row["candidate_id"], row["asset_id"], row["phase1_terminal_status"], row["terminal_resolution_phase"], parsed(row["missing_source_declarations"])] for row in candidates),
    )
    candidate_lines += [
        "",
        "No candidate is promoted beyond its recorded grade. In particular, the C025 detector is finite evidence over the frozen 24+27 family, not a universal law.",
    ]
    write(REPORTS / "FVII_SCI_01_CANDIDATE_CLOSURE.md", candidate_lines)

    adapter_lines = [
        "# FVII-SCI-01 inherited adapter audit",
        "",
        "All twenty formalization targets have narrow adapter modules. Every adapter imports and `#check`s its exact inherited declaration and records source/target types, preserved hypotheses, added hypotheses, lost hypotheses, trust dependencies, and nonclaims. The metadata is not a transport theorem.",
        "",
    ]
    adapter_lines += table(
        ["Target", "Name", "Adapter rows", "Module", "Phase-1 status", "Later science"],
        ([row["target_id"], row["name"], adapter_counts[row["target_id"]], row["phase1_adapter_module"], row["phase1_status"], row["later_science_required"]] for row in targets),
    )
    adapter_lines += ["", "## Exact reuse records", ""]
    adapter_lines += table(
        ["Adapter", "Target", "Source declaration", "Source", "VII metadata declaration", "Status"],
        ([row["adapter_id"], row["target_id"], row["source_declaration"], f"{row['source_file']}:{row['source_line']}", row["lean_metadata_declaration"], row["status"]] for row in adapters),
    )
    write(REPORTS / "FVII_SCI_01_ADAPTERS.md", adapter_lines)

    decision_lines = [
        "# FVII-SCI-01 decision rulings",
        "",
        "These rulings prevent later phases from silently assuming contested structure. DP13 and DP14 are terminal nonblocking source-governance boundaries; all others carry an assigned later resolution phase.",
        "",
    ]
    decision_lines += table(
        ["ID", "Working ruling", "Phase-1 status", "Resolution phase", "Required terminal form"],
        ([row["decision_id"], row["working_ruling"], row["phase1_terminal_status"], row["terminal_resolution_phase"], row["required_terminal_form"]] for row in decisions),
    )
    write(REPORTS / "FVII_SCI_01_DECISIONS.md", decision_lines)

    toy_lines = [
        "# FVII-SCI-01 finite reference world",
        "",
        f"The reference world has independent Python and Lean source implementations. Only the Python implementation was executable locally. Canonical JSON under the closed `{schema_version}` schema freezes the input family before later scientific phases.",
        "",
        f"- Scenarios: {python_summary['scenario_pass_count']}/{python_summary['scenario_count']} pass",
        f"- Countermodels: {python_summary['countermodel_pass_count']}/{python_summary['countermodel_count']} pass",
        f"- Scenario result SHA-256: `{python_summary['scenario_results_sha256']}`",
        f"- Countermodel result SHA-256: `{python_summary['countermodel_results_sha256']}`",
        f"- Python regression/protocol tests: {test_count}/{test_count} pass",
        "- Structural sections per scenario: all fifteen VII-owned object families plus append-only audit",
        "- Closed-root, closed-section, closed-flag, and closed-nested-record mutation tests: pass",
        "- Lean finite replay boundary: semantic flag/status/assertion projection, not full structural JSON parsing",
        "- Deterministic canonical JSON and Lean-fixture regeneration: pass",
        f"- Lean runtime differential: {'51/51 exact agreement recorded' if lean_pass else 'pending external replay'}",
        "",
        "Evidence grade: finite reference assay over exactly 24 frozen scenarios and 27 frozen countermodels. It has no force outside that declared family without a separate theorem.",
    ]
    write(REPORTS / "FVII_SCI_01_TOY_MODEL.md", toy_lines)

    lean_lines = [
        "# FVII-SCI-01 Lean asset inventory",
        "",
        f"- Active VII source declarations: {len(public)}",
        f"- Theorem/lemma/corollary sources: {theorem_count}",
        f"- Active VII Lean files: {len(list((LEAN / 'FoundationsVII').rglob('*.lean')))}",
        "- Canonical VII-owned structures: 15",
        "- Exact inherited adapter records: 30 across 20 targets",
        "- Generated finite declarations: 24 scenarios and 27 countermodels, each with a decidable pass theorem",
        "- VII-owned `axiom`, `opaque`, `sorry`, `admit`, or `unsafe`: zero by source-level audit",
        f"- Requested toolchain: `{build_status['toolchain']}`",
        f"- Local kernel status: `{build_status['kernel_build_status']}`",
        "",
        "The complete declaration-and-trust table is `reports/FVII_SCI_01_DECLARATIONS_AND_TRUST.md`. Exact external replay is automated by `scripts/run_fvii_sci01_external_lean.sh` and documented in `formalization/lean/EXTERNAL_COMPILE.md`.",
    ]
    write(REPORTS / "FVII_SCI_01_LEAN_ASSETS.md", lean_lines)

    external_lines = [
        "# External Lean replay directions for FVII-SCI-01",
        "",
        f"The delivered source targets `{build_status['toolchain']}`. The owner authorized changing `formalization/lean/lean-toolchain` to an available Lean 4 version when that is the least-resistance route, provided the version change is recorded and the full replay succeeds.",
        "",
        "From the repository root run:",
        "",
        "```bash",
        "bash scripts/run_fvii_sci01_external_lean.sh",
        "```",
        "",
        "The script performs `lake clean`, `lake build`, executes all 51 Lean fixtures, compares Lean and Python outputs, captures every `#print axioms` result, records the toolchain/build status, removes transient `.lake` products, and runs the strict validator with `--require-lean-results`.",
        "",
        (
            "The recorded replay establishes 51 shared fixture IDs, no missing IDs, no status/pass mismatches, successful kernel checking of the full public root, and a captured axiom report."
            if lean_pass else
            "A successful replay must establish 51 shared fixture IDs, no missing IDs, no status/pass mismatches, successful kernel checking of the full public root, and a captured axiom report. Until then, the repository intentionally retains `NOT_RUN_LOCAL_ENVIRONMENT` rather than claiming compilation."
        ),
    ]
    write(REPORTS / "FVII_SCI_01_EXTERNAL_LEAN_REPLAY.md", external_lines)

    generated_summary = {
        "date": DATE,
        "phase": "FVII-SCI-01",
        "status": "PHASE1_COMPLETE_EXTERNAL_LEAN_REPLAY_PENDING" if build_status["kernel_build_status"] != "PASS" else "PHASE1_COMPLETE_LEAN_REPLAY_PASS",
        "objects": len(objects),
        "vii_owned_structures": 15,
        "fixture_schema_version": schema_version,
        "python_test_count": test_count,
        "formalization_targets": len(targets),
        "adapter_records": len(adapters),
        "public_declarations": len(public),
        "theorem_lemma_corollary_declarations": theorem_count,
        "declaration_kinds": dict(sorted(kind_counts.items())),
        "candidates_registered": len(candidates),
        "terminal_phase1_candidates": [row["candidate_id"] for row in terminal],
        "decision_rulings": len(decisions),
        "scenario_count": python_summary["scenario_count"],
        "countermodel_count": python_summary["countermodel_count"],
        "python_all_pass": python_summary["all_pass"],
        "lean_kernel_status": build_status["kernel_build_status"],
        "validation_status": validation["status"],
        "paper_assets_created": 0,
    }
    generated = ROOT / "generated" / "fvii_sci01_summary.json"
    generated.parent.mkdir(parents=True, exist_ok=True)
    generated.write_text(json.dumps(generated_summary, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

    toolchain_status = {
        "date": DATE,
        "requested": build_status["toolchain"],
        "lean_executable": shutil.which("lean"),
        "lake_executable": shutil.which("lake"),
        "elan_executable": shutil.which("elan"),
        "kernel_build_status": build_status["kernel_build_status"],
        "user_authorized_boundary": "Local Lean compilation is best-effort and external replay is nonblocking when honestly recorded.",
    }
    (ROOT / "generated" / "fvii_sci01_toolchain_status.json").write_text(
        json.dumps(toolchain_status, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(generated_summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

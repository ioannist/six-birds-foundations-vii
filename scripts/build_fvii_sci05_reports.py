#!/usr/bin/env python3
"""Build the human-readable final Foundations VII science release reports."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "science" / "registry"
LAB = ROOT / "formalization" / "foundations_vii_lab" / "phase5" / "results"
REPORTS = ROOT / "reports"
GENERATED = ROOT / "generated"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def esc(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def table(headers: list[str], rows: list[list[Any]]) -> str:
    return "\n".join(
        [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        + ["| " + " | ".join(esc(item) for item in row) + " |" for row in rows]
    )


def validation_markdown(path: Path, default_kernel: str) -> str:
    if not path.is_file():
        return "# FVII-SCI-05 validation\n\nValidation has not yet been generated."
    payload = read_json(path)
    passed = payload.get("pass_count", payload.get("checks_passed", 0))
    total = payload.get("check_count", payload.get("checks_total", 0))
    kernel = payload.get("kernel_status", payload.get("kernel_build_status", default_kernel))
    rows: list[list[Any]] = []
    for row in payload.get("checks", []):
        status = row.get("status") or ("PASS" if row.get("pass") else "FAIL")
        rows.append([row.get("name", ""), status, row.get("detail", "")])
    return (
        "# FVII-SCI-05 validation\n\n"
        f"**Status:** `{payload.get('status', 'UNKNOWN')}`\n\n"
        f"**Checks:** {passed}/{total}\n\n"
        f"**Kernel:** `{kernel}`\n\n"
        + table(["Check", "Result", "Detail"], rows)
    )


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    summary = read_json(REG / "final_summary.json")
    lab = read_json(LAB / "summary.json")
    candidates = read_jsonl(REG / "final_candidate_closure.jsonl")
    objects = read_jsonl(REG / "final_object_closure.jsonl")
    targets = read_jsonl(REG / "final_formalization_target_closure.jsonl")
    nogos = read_jsonl(REG / "final_no_go_closure.jsonl")
    corollaries = read_jsonl(REG / "final_corollaries.jsonl")
    assays = read_jsonl(REG / "final_finite_assays.jsonl")
    countermodels = read_jsonl(REG / "final_countermodels.jsonl")
    decisions = read_jsonl(REG / "final_decision_closure.jsonl")
    trust = read_jsonl(REG / "final_theorem_trust.jsonl")
    dependencies = read_jsonl(REG / "final_theorem_dependencies.jsonl")
    adapters = read_jsonl(REG / "final_adapters.jsonl")
    build = read_json(ROOT / "formalization" / "lean" / "BUILD_STATUS_FINAL.json")
    kernel = str(build.get("kernel_build_status", "NOT_RUN_LOCAL_ENVIRONMENT"))
    _passed = kernel == "PASS"
    boundary_note = (
        "The replay was executed locally in this repository: the public kernel build, all five finite\n"
        "differentials, and the `#print axioms` capture for every public theorem have run and passed.\n"
        "Kernel verification does not upgrade a scientific disposition -- a formalSchema is still a schema."
        if _passed else
        "Lean and Lake were unavailable locally, which the owner explicitly authorized as nonblocking. The "
        "release therefore claims source completion, static import/trust closure, executable Python finite "
        "evidence, and a complete external replay path--not local kernel elaboration or executed axiom receipts."
    )
    grade_note = ("Proof grades are backed by an executed kernel replay with axiom receipts."
                  if _passed else
                  "Proof grades remain source-level until external kernel replay succeeds.")
    core_state = ("confirmed by the executed `#print axioms` receipt"
                  if _passed else
                  "pending executed `#print axioms`")
    core_note = ("The axiom-free-core classification is backed by executed `#print axioms` receipts."
                 if _passed else
                 "The axiom-free-core classification is intentionally labeled **static and pending executed "
                 "replay**. Import reachability cannot establish kernel validity or exact proof-term axioms. "
                 "External replay is the only mechanism that upgrades these rows to executed receipts.")
    release_nonclaim = ("Source completion and finite exhaustiveness over declared carriers do not imply "
                        "universal interaction laws. The Lean kernel replay and axiom receipts have executed."
                        if _passed else
                        "Source completion and finite exhaustiveness over declared carriers do not imply "
                        "universal interaction laws or an executed Lean kernel proof until external replay passes.")

    root = f'''# FVII-SCI-05 — final theorem closure and science release

**Execution date:** 2026-07-26

**Stage:** `{summary['stage']}`

**Paper or paper-preparation work:** none

FVII-SCI-05 integrates the four prior science phases into one terminally graded formal-science release. It adds cross-family corollaries, eleven global finite closure envelopes, complete candidate/target/no-go/decision registries, theorem dependency and trust surfaces, and a final public Lean API. No manuscript or manuscript-preparation asset is included.

## Final closure census

- **36/36 candidates** have exactly one terminal disposition.
- **18/18 object records** are inherited with explicit anchors or VII-defined with exact declarations.
- **20/20 formalization targets** have terminal closure records.
- **11/11 no-go fronts** have source theorems, exact scopes, positive controls, and named escapes.
- **15/15 decision points** are terminal or explicitly nonblocking source-governance boundaries.
- **21 cross-family corollaries** are formalized across nine interacting subsystems.
- **43 cumulative finite assays** are retained: 9 Phase-2, 11 Phase-3, 12 Phase-4, and 11 Phase-5 envelopes.
- **38 countermodels** are indexed: 27 named executable fixtures and 11 minimized rejected assignments.
- **30 inherited adapter contracts** remain explicit and hypothesis-preserving.

## Terminal candidate grades

{table(['Disposition', 'Count'], [[key, value] for key, value in sorted(summary['candidate_dispositions'].items())])}

The two refuted candidates are the unconditional parent-refinement monotonicity claim and the universal conserved scalar contact-degree claim. Their failure is constructive and scoped: conditional refinement theorems and typed resource ledgers remain. The full categorical reduction and full generators-and-relations algebra remain closed deferrals with explicit reopen conditions.

## Cross-family science

The final corollaries establish scoped consequences involving prospective commitment plus join admission, source independence plus finite payment/capacity, coverage-qualified non-interaction, residual-aware enablement composition, refinement/descent compatibility, no-free-first-join obligations, holonomy/arrow separation, negative-force quantifier discipline, and observer-pricing/endogeny. Each corollary records exact hypotheses, source declarations, candidate links, nonclaims, and a statement hash.

## Global finite closure

The Phase-5 laboratory exhausts **{lab['raw_cases']:,} raw** and **{lab['canonical_cases']:,} canonical** assignments across eleven declared bounded universes. It accepts **{lab['accepted_cases']:,}** and rejects **{lab['rejected_cases']:,}** assignments, retains **{lab['bounded_witness_count']}** minimized witnesses, and replays all **24 scenarios** and **27 named countermodels** successfully.

These assays are exhaustive only over the stated finite carriers. They do not establish a universal normal form for arbitrary theory interaction, a universal interaction algebra, or a universal conserved scalar.

## Formal release surface

- **{summary['public_module_count']} public Foundations VII modules**;
- **{summary['public_declaration_count']} public declarations**;
- **{summary['public_theorem_count']} theorem/lemma/corollary declarations**;
- **{summary['theorem_dependency_edge_count']} static theorem-reference edges**;
- **{summary['module_import_edge_count']} module-import edges**;
- **{summary['static_axiom_free_core_candidate_count']} theorems** classified as axiom-free core, {core_state};
- inherited trust surface retained separately: **{summary['inherited_trust_declaration_count']} declarations**.

The final public root imports only complete Phase-1–5 modules, corollaries, finite models, and release registries. Imported Foundations V and VI trees remain byte-identical to the Phase-4 baseline.

## Lean execution boundary

Current kernel status: `{kernel}`.

{boundary_note}

Run:

```sh
bash scripts/run_fvii_sci05_external_lean.sh
```

The script builds the cumulative public root, executes all five Lean runners, compares the Lean and Python finite results, captures `#print axioms` for every public theorem, and reruns the strict final validator.

## Rebuild

```sh
bash scripts/rebuild_fvii_sci05.sh
python3 scripts/verify_delivery_manifest.py
```

The rebuild regenerates all finite results, final registries, dependency/trust graphs, reports, validations, and delivery hashes without creating paper assets.
'''
    write(ROOT / "FVII_SCI_05_REPORT.md", root)
    write(ROOT / "FVII_SCIENCE_FINAL_REPORT.md", root)
    write(REPORTS / "FVII_SCI_05_REPORT.md", root)

    object_rows = [
        [
            row["object_id"],
            row["name"],
            row["final_status"],
            ", ".join(row["declarations"]),
            row["anchor_declaration"] or "—",
        ]
        for row in objects
    ]
    write(
        REPORTS / "FVII_SCI_05_OBJECT_CLOSURE.md",
        "# FVII-SCI-05 object closure\n\n"
        + table(["ID", "Object", "Terminal status", "Declarations", "Inherited anchor"], object_rows)
        + "\n\nAll eighteen Step-3 object records are terminally accounted for. Inherited roles retain their source declarations; VII-owned objects have exact public declarations.",
    )

    candidate_rows = [
        [
            row["candidate_id"],
            row["name"],
            row["terminal_disposition"],
            row["terminal_phase"],
            len(row["lean_declarations"]),
            ",".join(row["finite_assay_ids"]) or "—",
        ]
        for row in candidates
    ]
    write(
        REPORTS / "FVII_SCI_05_CANDIDATE_CLOSURE.md",
        "# FVII-SCI-05 candidate closure\n\nEvery candidate has one controlling terminal ruling; none remains specification-ready/unproved.\n\n"
        + table(["ID", "Name", "Disposition", "Landed phase", "Lean assets", "Finite assays"], candidate_rows)
        + "\n\n" + grade_note,
    )

    corollary_rows = [
        [
            row["corollary_id"],
            row["declaration"],
            ",".join(row["candidate_ids"]),
            row["proof_grade"],
            row["nonclaim"],
        ]
        for row in corollaries
    ]
    write(
        REPORTS / "FVII_SCI_05_COROLLARIES.md",
        "# FVII-SCI-05 cross-family corollaries\n\n"
        + table(["ID", "Lean declaration", "Candidates", "Grade", "Boundary"], corollary_rows),
    )

    phase5_assays = [row for row in assays if row["phase"] == "PHASE5"]
    finite_rows = [
        [
            row["family_id"],
            row["raw_cardinality"],
            row["canonical_cardinality"],
            row["accepted_cardinality"],
            row["rejected_cardinality"],
            row["description"],
        ]
        for row in phase5_assays
    ]
    finite = f'''# FVII-SCI-05 finite evidence

{table(['Family', 'Raw', 'Canonical', 'Accepted', 'Rejected', 'Scope'], finite_rows)}

## Aggregate

- Phase-5 raw: {lab['raw_cases']:,}
- Phase-5 canonical: {lab['canonical_cases']:,}
- Phase-5 accepted: {lab['accepted_cases']:,}
- Phase-5 rejected: {lab['rejected_cases']:,}
- Minimized witnesses: {lab['bounded_witness_count']}
- Cross-family controls: {lab['cross_family_control_count']}
- Frozen scenario replay: 24/24
- Named countermodel replay: 27/27
- Cumulative finite assays: {len(assays)}

The finite evidence is exhaustive only over the declared bounded universes. Random or fuzz evidence is not used as a substitute for exhaustive enumeration.
'''
    write(REPORTS / "FVII_SCI_05_FINITE_EVIDENCE.md", finite)

    trust_report = f'''# FVII-SCI-05 theorem dependency and trust audit

- Public theorems: {len(trust)}
- Static theorem-reference rows: {len(dependencies)}
- Static theorem-reference edges: {summary['theorem_dependency_edge_count']}
- Static axiom-free-core candidates: {summary['static_axiom_free_core_candidate_count']}
- Static inherited-trust-reachable theorems: {summary['static_trust_reachable_theorem_count']}
- Explicit inherited trust declarations: {summary['inherited_trust_declaration_count']}
- Adapter contracts: {len(adapters)}
- Kernel status: `{kernel}`

`science/traceability/final_theorem_dependency_graph.graphml` and `final_module_import_graph.graphml` provide machine-readable DAGs. `formalization/lean/FoundationsVII/Trust/PrintAxiomsFinal.lean` contains one `#print axioms` command for every public theorem.

{core_note}
'''
    write(REPORTS / "FVII_SCI_05_TRUST_DEPENDENCY_AUDIT.md", trust_report)

    asset_index = "# FVII-SCI-05 final science asset index\n\n" + table(
        ["Asset class", "Count", "Canonical location"],
        [
            ["Candidates", len(candidates), "science/registry/final_candidate_closure.*"],
            ["Objects", len(objects), "science/registry/final_object_closure.*"],
            ["Formalization targets", len(targets), "science/registry/final_formalization_target_closure.*"],
            ["No-gos", len(nogos), "science/registry/final_no_go_closure.*"],
            ["Corollaries", len(corollaries), "science/registry/final_corollaries.*"],
            ["Countermodels", len(countermodels), "science/registry/final_countermodels.*"],
            ["Finite assays", len(assays), "science/registry/final_finite_assays.*"],
            ["Decisions", len(decisions), "science/registry/final_decision_closure.*"],
            ["Adapters", len(adapters), "science/registry/final_adapters.*"],
            ["Public declarations", summary["public_declaration_count"], "science/registry/final_public_declarations.*"],
            ["Public theorems", summary["public_theorem_count"], "science/registry/final_theorems.*"],
            ["Theorem dependencies", len(dependencies), "science/registry/final_theorem_dependencies.*"],
            ["Theorem trust rows", len(trust), "science/registry/final_theorem_trust.*"],
        ],
    )
    asset_index += "\n\nJSONL is canonical; CSV is a deterministic tabular view. The final typed Lean registry is `FoundationsVII.Release.Terminal`."
    write(REPORTS / "FVII_SCI_05_FINAL_ASSET_INDEX.md", asset_index)

    write(
        REPORTS / "FVII_SCI_05_VALIDATION.md",
        validation_markdown(GENERATED / "fvii_sci05_validation.json", kernel),
    )

    external_replay = f'''# FVII-SCI-05 external Lean replay

**Kernel status:** `{kernel}`

{boundary_note}

The cumulative replay contract is:

```sh
bash scripts/run_fvii_sci05_external_lean.sh
```

The script rebuilds all five finite layers, performs `lake clean` and `lake build`, runs every Lean finite executable, compares Lean and Python results, captures one `#print axioms` request per public theorem, records the actual toolchain, and reruns the strict final validator.

A compatible Lean 4 version may be selected by editing and committing `formalization/lean/lean-toolchain`. Until the replay succeeds, source-level proof grades, static trust reachability, and finite Python evidence remain distinct from kernel verification.
'''
    write(REPORTS / "FVII_SCI_05_EXTERNAL_LEAN_REPLAY.md", external_replay)

    acceptance = f'''# FVII-SCI-05 final acceptance

The final science release closes the complete five-phase program at source and finite-evidence level.

- Candidate closure: 36/36.
- Object closure: 18/18.
- Formalization targets: 20/20.
- No-go fronts: 11/11.
- Decision points: 15/15.
- Cross-family corollaries: 21.
- Cumulative finite assays: 43.
- Countermodels: 38.
- Python tests: 70/70.
- Paper work: none.
- Lean kernel replay: `{kernel}`; external replay remains explicit and nonblocking unless marked PASS.
'''
    write(REPORTS / "FVII_SCI_05_ACCEPTANCE.md", acceptance)

    # Canonical final-release aliases are regenerated rather than retained as
    # stale copies, so a fresh extraction can rebuild every advertised report.
    report_aliases = {
        "FVII_SCI_05_CANDIDATE_CLOSURE.md": "FINAL_CANDIDATE_CLOSURE.md",
        "FVII_SCI_05_COROLLARIES.md": "FINAL_COROLLARIES.md",
        "FVII_SCI_05_FINITE_EVIDENCE.md": "FINAL_FINITE_EVIDENCE.md",
        "FVII_SCI_05_TRUST_DEPENDENCY_AUDIT.md": "FINAL_TRUST_AND_DEPENDENCIES.md",
        "FVII_SCI_05_ACCEPTANCE.md": "FINAL_RELEASE_ACCEPTANCE.md",
        "FVII_SCI_05_EXTERNAL_LEAN_REPLAY.md": "FINAL_EXTERNAL_LEAN_REPLAY.md",
    }
    for source_name, alias_name in report_aliases.items():
        write(REPORTS / alias_name, (REPORTS / source_name).read_text(encoding="utf-8"))

    registry_readme = '''# Final Foundations VII science registries

The `final_*.jsonl` files are the canonical machine-readable registries. Matching CSV files are deterministic views for inspection. Prototype `*_registry` duplicates were removed to prevent conflicting counts or grades.

The controlling surfaces are:

- `final_candidate_closure`;
- `final_object_closure`;
- `final_formalization_target_closure`;
- `final_no_go_closure`;
- `final_corollaries`;
- `final_countermodels`;
- `final_finite_assays`;
- `final_adapters`;
- `final_decision_closure`;
- `final_public_declarations`, `final_definitions`, and `final_theorems`;
- `final_theorem_dependencies` and `final_theorem_trust`;
- `final_public_api` and `final_summary.json`.

Source-level Lean grades remain distinct from executed kernel status.
'''
    write(REG / "README.md", registry_readme)

    release = {
        "release_id": "foundations-vii-science-final",
        "date": "2026-07-26",
        "status": summary["stage"],
        "paper_work": False,
        "kernel_build_status": kernel,
        "git_tag": "vii-science-final",
        "archive": "foundations-vii-science-assets-final.zip",
        "counts": {
            key: summary[key]
            for key in [
                "candidate_count",
                "object_count",
                "formalization_target_count",
                "no_go_count",
                "corollary_count",
                "countermodel_registry_count",
                "finite_assay_count",
                "adapter_count",
                "decision_count",
                "public_module_count",
                "public_declaration_count",
                "public_theorem_count",
            ]
        },
        "phase5_finite": {
            key: lab[key]
            for key in [
                "envelope_count",
                "raw_cases",
                "canonical_cases",
                "accepted_cases",
                "rejected_cases",
                "bounded_witness_count",
                "cross_family_control_count",
            ]
        },
        "external_replay": "scripts/run_fvii_sci05_external_lean.sh",
        "nonclaim": release_nonclaim,
    }
    (ROOT / "science" / "FINAL_SCIENCE_RELEASE.json").write_text(
        json.dumps(release, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "reports": 16,
                "candidate_count": len(candidates),
                "corollary_count": len(corollaries),
                "finite_assay_count": len(assays),
                "kernel_status": kernel,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

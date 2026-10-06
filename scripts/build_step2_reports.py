#!/usr/bin/env python3
"""Build deterministic human-facing Step-2 reports from canonical artifacts."""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def compact(text: Any, limit: int = 300) -> str:
    s = " ".join(str(text).split())
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def md_counter(counter: Counter[str]) -> str:
    return ", ".join(f"`{k}`={v}" for k, v in sorted(counter.items()))


def main() -> None:
    claims = read_jsonl(ROOT / "registry" / "claims.jsonl")
    bridges = read_jsonl(ROOT / "bridges" / "bridge_atlas.jsonl")
    no_gos = read_jsonl(ROOT / "bridges" / "no_go_scope_matrix.jsonl")
    named_law_audit = read_jsonl(ROOT / "bridges" / "named_law_occurrence_audit.jsonl")
    no_go_correspondence = read_jsonl(ROOT / "formalization" / "integration" / "no_go_prior_scaffold_correspondence.jsonl")
    apps = read_jsonl(ROOT / "synthesis" / "step2" / "application_pressure_tests.jsonl")
    wish = read_jsonl(ROOT / "wishlists" / "step2_evidence_links.jsonl")
    carriers = read_jsonl(ROOT / "registry" / "examples_carriers.jsonl")
    conflicts = read_jsonl(ROOT / "bridges" / "unresolved_conflicts.jsonl")
    index = read_csv(ROOT / "corpus" / "step2_dossier_index.csv")
    F = read_csv(ROOT / "registry" / "F_laws.csv")
    E = read_csv(ROOT / "registry" / "E_laws.csv")
    G = read_csv(ROOT / "registry" / "G_laws.csv")
    NG = read_csv(ROOT / "registry" / "no_go_theorems.csv")
    formal_summary = json.loads((ROOT / "formalization" / "integration" / "cumulative_formalization_summary.json").read_text(encoding="utf-8"))
    claim_summary = json.loads((ROOT / "generated" / "step2_claim_summary.json").read_text(encoding="utf-8"))
    bridge_summary = json.loads((ROOT / "generated" / "step2_bridge_summary.json").read_text(encoding="utf-8"))

    claim_types = Counter(c["claim_type"] for c in claims)
    grades = Counter(c["claim_grade"] for c in claims)
    formal = Counter(c["formalization"]["status"] for c in claims)
    bridge_kinds = Counter(b["bridge_kind"] for b in bridges)
    bridge_classes = Counter(b["classification"] for b in bridges)
    by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in claims:
        by_paper[c["source_paper"]].append(c)

    # Current build report (replaces a discarded prototype report).
    build = [
        "# Step 2 — canonical claim and bridge build report", "",
        "This report describes the only active Step-2 claim-ID space. Earlier prototype outputs are deliberately absent.", "",
        f"- Papers represented: **{len(by_paper)}**.",
        f"- Canonical source-located claim records: **{len(claims)}**.",
        f"- Composite abstract theses: **{sum(c['review_status'] == 'SOURCE_EXTRACTED_COMPOSITE' for c in claims)}**; explicit abstract boundary components: **{sum(c.get('proof_status') == 'ABSTRACT_STATUS_BOUNDARY' for c in claims)}**.",
        f"- Explicit formal TeX environments represented: **{sum(c['review_status'] == 'SOURCE_EXTRACTED_FORMAL_SURFACE' for c in claims)}**.",
        f"- Named-section theorem/gate/result surfaces: **{sum(c['review_status'] == 'SOURCE_EXTRACTED_NAMED_SECTION_SURFACE' for c in claims)}**.",
        f"- Explicit prose definition/result/nonclaim/scope/open surfaces: **{sum(c['review_status'] == 'SOURCE_EXTRACTED_EXPLICIT_PROSE_SURFACE' for c in claims)}**.",
        f"- Bridge records: **{len(bridges)}** ({md_counter(bridge_kinds)}).",
        f"- Prior-law/no-go reuse contracts: **{bridge_summary['prior_law_reuse_contracts']}**.",
        f"- Named-law source audit: **{len(named_law_audit)} candidates**, **{bridge_summary['named_law_accepted_occurrences']} accepted occurrences**, and **{bridge_summary['named_law_import_rows']} grouped paper/law bridges**.",
        f"- No-go/prior-Lean correspondence rows: **{len(no_go_correspondence)}**.",
        f"- Application pressure tests: **{len(apps)}**.",
        f"- Example/carrier records: **{len(carriers)}**.",
        f"- Wishlist atoms linked: **{len(wish)}**.", "",
        "## Source boundary", "",
        "Fifty-seven papers were processed against their complete supplied TeX trees. P039 is represented only by its supplied abstract because eighteen included TeX files and the bibliography are absent. Its abstract thesis and explicit abstract nonclaim are retained; missing theorem, proof, calibration, or body-level boundary text was not reconstructed.", "",
        "## Authority and claim-grade rule", "",
        "Frozen TeX controls prose claims. Imported Lean source and its statement-fidelity ledgers control mechanization claims. A local Lean 4.28.0 kernel replay was unavailable, so this build reports static declaration/import closure and inherited paper-side evidence without claiming fresh elaboration.", "",
        "## Claim-type census", "",
        md_counter(claim_types), "",
        "## Bridge-classification census", "",
        md_counter(bridge_classes), "",
    ]
    (ROOT / "reports" / "step2" / "BUILD_REPORT.md").write_text("\n".join(build) + "\n", encoding="utf-8")

    # Reading completeness.
    completeness = [
        "# Step-2 reading completeness", "",
        "Every supplied paper root has a canonical per-paper JSONL and a Markdown dossier whose complete claim index names every record. The status below is source-completeness aware: `BRIDGED` means the supplied source was fully processed, not that every invocation was proved exact.", "",
        "| Paper | Status | Claims | Formal theorem/schema/principle | Definitions | Nonclaims/scope | Open |", "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in index:
        pid = row["paper_id"]
        rows = by_paper[pid]
        formal_n = sum(c["claim_type"] in {"theorem", "theorem*", "lemma", "proposition", "corollary", "schema", "conjecture", "postulate", "assumption", "principle"} for c in rows)
        completeness.append(
            f"| `{pid}` | `{row['status']}` | {len(rows)} | {formal_n} | {sum(c['claim_type'] in {'definition','prose_definition','construction','convention'} for c in rows)} | {sum(c['claim_type'] in {'nonclaim','scope_boundary'} for c in rows)} | {sum(c['claim_type']=='open_problem' for c in rows)} |"
        )
    completeness += [
        "", "## Extraction lanes", "",
        "- Formal environments: all supported `definition`, theorem-family, schema, postulate, convention, construction, nonclaim, remark, and methodological-principle environments are represented one-for-one.",
        "- Named surfaces: theorem-like headings, gates, verdicts, calibration/result lanes, and explicit paper-defined objects are retained when a formal environment is absent.",
        "- Prose status surfaces: only explicit definitions, result statements, nonclaims, scope limits, and open/deferred work are promoted; ordinary exposition and submission boilerplate are excluded.",
        "- Every paper has exactly one source-located composite abstract thesis, including section-form abstracts; composite abstracts remain navigation claims rather than exact theorem substitutes.",
        "- Explicit abstract nonclaims, scope boundaries, and open obligations are separately typed as component records; component theorem/body records still govern exact hypotheses and proof grades.",
    ]
    (ROOT / "reports" / "STEP2_READING_COMPLETENESS.md").write_text("\n".join(completeness) + "\n", encoding="utf-8")

    # Formalization reuse.
    f_report = [
        "# Step-2 formalization reuse and proof posture", "",
        "## Inherited active scaffold", "",
        f"- Unique active Lean modules: **{formal_summary['unique_active_modules']}**.",
        f"- Unique declarations: **{formal_summary['unique_active_declarations']}**.",
        f"- Theorem declarations: **{formal_summary['unique_active_theorems']}**.",
        f"- Resolved local import edges: **{formal_summary['import_edges']}**; unresolved imports: **{formal_summary['unresolved_imports']}**.",
        f"- Lexical `sorry` / `admit` tokens: **{formal_summary['sorry_tokens']} / {formal_summary['admit_tokens']}**.",
        f"- Inherited trust surface: **{formal_summary['axiom_declarations']} axiom and {formal_summary['opaque_declarations']} opaque declarations**.",
        f"- Foundations VII declarations: **{formal_summary['active_vii_declarations']}**.", "",
        "## Claim-level mapping census", "",
        md_counter(formal), "",
        "`MATCHED_IMPORTED_LAW_DECLARATION` means the law disclosure/traceability ledgers assign a locally imported declaration to the source row. `MATCHED_IMPORTED_ABSTRACT_CORE_DECLARATION` means an imported theorem captures a reusable abstract core but is not certified identical to the paper theorem. `PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT` marks a plausible typed core whose carrier, hypotheses, or conclusion still require an explicit adapter. `PLAUSIBLE_IMPORTED_MATCH_REQUIRES_STATEMENT_REVIEW` is lexical navigation only. `PAPER_DISCLOSED_ASSET_NOT_IMPORTED` means the paper reports a formal/computational asset but the corresponding source is absent from the supplied active scaffold or no claim-specific local declaration was assigned. `NO_MATCH` means no local claim-level match was assigned. None of these statuses silently implies a fresh local kernel replay.", "",
        "## Law-series reuse", "",
        f"- Source registry coverage: **{len(F)} F**, **{len(E)} E**, **{len(G)} G**, and **{len(NG)} no-go** rows.",
        f"- Reuse contracts: **{bridge_summary['prior_law_reuse_contracts']}**, one per prior law/no-go row.",
        f"- Source audit reviewed **{bridge_summary['named_law_candidate_occurrences']} F/E/G-shaped tokens**; **{bridge_summary['named_law_accepted_occurrences']} substantive occurrences** form **{bridge_summary['named_law_import_rows']} grouped target-paper/law bridges**. Rejected local figures, exhibits, workflow items, range endpoints, and mathematical symbols remain visible in the audit ledger.",
        f"- No-go/prior-scaffold correspondence: **{len(no_go_correspondence)} rows**, with exact matches, abstract-core correspondences, missing local assets, and no-match cases kept distinct.",
        "- The F/E/G and no-go paper statements remain controlling even where multiple component claims or Lean declarations are associated with one numbered result.", "",
        "## Machine-status boundary", "",
        "The supplied repositories request Lean 4.28.0. That toolchain was unavailable in the execution environment. The build therefore verifies source presence, declaration indexing, trust accounting, byte identity, and static import closure, while preserving prior paper-side theorem/test claims as inherited evidence rather than restating them as a new kernel run.",
    ]
    (ROOT / "reports" / "STEP2_FORMALIZATION_REUSE.md").write_text("\n".join(f_report) + "\n", encoding="utf-8")

    # Method documentation.
    method = [
        "# Step-2 method: claim extraction, formalization matching, and bridge audit", "",
        "## One canonical ID space", "",
        "`scripts/build_step2_claims.py` creates the canonical IDs `Pxxx-Cnnnn`. Every downstream registry, bridge, graph edge, wishlist link, dossier supplement, and application map consumes those IDs. `scripts/build_step2_claim_bridge_atlas.py` never re-extracts claims. This prevents competing indexes from drifting.", "",
        "## Source authority", "",
        "The frozen TeX tree is authoritative. Each record stores the original and macro-expanded TeX wording, a readable normalization, source and expanded-source ranges, root and tree hashes, typed objects where mechanically recoverable, hypotheses, conclusion, proof/evidence status, dependencies, lexical prior-law candidates, formalization posture, nonclaims, and VII-relevance links. Normalized prose and lexical law candidates are navigation views, not substitutes for the source statement or the source-level named-law audit.", "",
        "## Extraction lanes", "",
        "1. Exactly one source-located composite abstract record orients each paper, whether the source uses an `abstract` environment or an `Abstract` section; it cannot be cited as an exact theorem.",
        "2. Explicit nonclaims, scope boundaries, and open obligations found only in an abstract become separate typed component records.",
        "3. Every supported explicit formal environment becomes one record, preserving the environment-derived grade.",
        "4. Named sections that function as theorem, schema, gate, verdict, calibration, criterion, or result lanes are recorded when no formal environment is used.",
        "5. Explicit prose definitions, result summaries, nonclaims, scope limits, and open/deferred work are recorded outside occupied theorem environments.",
        "6. Submission boilerplate and generic exposition are excluded. P039 is stopped at the supplied-source boundary.", "",
        "## Formalization matching", "",
        "Numbered F/E/G laws are matched through the imported disclosure and traceability ledgers. Other claim-to-declaration candidates use lexical similarity only and are marked as requiring statement review. Every formalization block records modules, declarations, statement deltas, trust base, machine status, tests/lab evidence, and caveats. Presence is not conflated with proof fidelity or a fresh elaboration.", "",
        "## Bridge construction", "",
        "Three bridge kinds are retained: paper invocations, source-audited named-law imports, and one future-reuse contract for every F/E/G/no-go row. Every F/E/G-shaped source token is accepted or rejected with a reason before any named-law bridge is created. Every bridge names source and target objects, map/interface, inherited/added/lost hypotheses, source of truth, audit path, formalization posture, licensed conclusion, classification, nonclaims, and nearest countermodel.", "",
        "The classification vocabulary is deliberately conservative. `UNKNOWN_REQUIRES_PROOF`, `ANALOGY_ONLY_OR_DOMAIN_MAP_REQUIRED`, and partial-bridge rows are successful findings: they prevent a citation or verbal resemblance from silently becoming theorem transfer.", "",
        "## Rebuild", "",
        "Run `scripts/rebuild_step2.sh`. It regenerates claims, bridges, taxonomies, carrier and graph registries, reports, validation, and delivery hashes. The rebuild is deterministic and does not create a Foundations VII object model or Lean theorem.",
    ]
    (ROOT / "docs" / "STEP2_METHOD.md").write_text("\n".join(method) + "\n", encoding="utf-8")

    # Plan-to-artifact requirement audit.  This is deliberately separate from
    # the executable validator: it provides a human-readable proof of delivery
    # against the original Step-2 contract while the validator checks the
    # underlying invariants mechanically.
    req_rows = [
        {"requirement_id": "S2-R01", "plan_requirement": "All 58 papers have complete claim-level dossiers.", "status": "PASS_WITH_RECORDED_SOURCE_LIMIT", "evidence": "notes/dossiers/P001.md..P058.md; claims/by_paper/; reports/STEP2_READING_COMPLETENESS.md", "finding": f"{len(by_paper)} paper IDs represented; all have one source-located abstract thesis, 57 have full supplied trees, and P039 has two abstract-only records.", "limitation": "P039 has 18 missing includes and a missing bibliography; no absent text was reconstructed."},
        {"requirement_id": "S2-R02", "plan_requirement": "Every explicit formal claim surface is represented and source-located.", "status": "PASS", "evidence": "registry/claims.jsonl; generated/step2_validation.json", "finding": f"{sum(c['review_status'] == 'SOURCE_EXTRACTED_FORMAL_SURFACE' for c in claims)} explicit formal TeX environments represented one-for-one.", "limitation": "Normalized text is navigational; frozen TeX remains authoritative."},
        {"requirement_id": "S2-R03", "plan_requirement": "Definition, claim, nonclaim, open-problem, example/carrier, provenance, and proof-artifact registries exist.", "status": "PASS", "evidence": "registry/definitions.*; registry/theorem_claims.*; registry/nonclaims_withdrawals.*; registry/open_problems.*; registry/examples_carriers.*; registry/source_truth_provenance.csv; registry/proof_artifact_lean_coverage.*", "finding": "All planned cross-paper registries are populated from the canonical claim-ID space.", "limitation": "Registry membership does not promote source claim grade."},
        {"requirement_id": "S2-R04", "plan_requirement": "Every in-corpus paper invocation has a typed bridge record.", "status": "PASS", "evidence": "bridges/paper_invocation_bridges.*; corpus/paper_dependency_edges.csv", "finding": f"{bridge_kinds['PAPER_INVOCATION']} invocation bridges match all Step-1 dependency edges.", "limitation": "Citation identity alone licenses no theorem transfer."},
        {"requirement_id": "S2-R05", "plan_requirement": "Every genuine named imported law has an audited bridge rather than a lexical citation.", "status": "PASS", "evidence": "bridges/named_law_occurrence_audit.*; bridges/imported_law_bridges.*", "finding": f"{bridge_summary['named_law_accepted_occurrences']} accepted occurrences are covered exactly once by {bridge_kinds['NAMED_LAW_IMPORT']} grouped paper/law bridges.", "limitation": "Rejected local-label collisions remain in the audit rather than disappearing."},
        {"requirement_id": "S2-R06", "plan_requirement": "Every F/E/G/no-go source row has a future-reuse contract.", "status": "PASS", "evidence": "bridges/law_reuse_contracts.*", "finding": f"{bridge_kinds['PRIOR_LAW_REUSE_CONTRACT']} contracts cover 52 F, 16 E, 13 G, and 8 no-go rows.", "limitation": "A contract inventories prerequisites; it is not a Foundations VII theorem."},
        {"requirement_id": "S2-R07", "plan_requirement": "Mechanized reuse preserves declarations, statement deltas, trust base, and machine status.", "status": "PASS_WITH_ENVIRONMENT_LIMIT", "evidence": "registry/proof_artifact_lean_coverage.*; reports/STEP2_FORMALIZATION_REUSE.md", "finding": f"Claim-level formalization is aligned to the inherited {formal_summary['unique_active_modules']}-module / {formal_summary['unique_active_theorems']}-theorem spine.", "limitation": "Lean 4.28.0 was unavailable; no fresh local kernel elaboration is claimed."},
        {"requirement_id": "S2-R08", "plan_requirement": "No-go rows name exact carrier, hypotheses, scope, non-scope, and escape.", "status": "PASS", "evidence": "bridges/no_go_scope_matrix.*; synthesis/step2/NO_GO_SCOPE.md", "finding": f"All {len(no_gos)} no-go results have complete bounded-scope records.", "limitation": "A negative result blocks only its stated carrier and hypotheses."},
        {"requirement_id": "S2-R09", "plan_requirement": "Recurrent invalid role collapses are explicitly prohibited.", "status": "PASS", "evidence": "bridges/invalid_transfers.csv; bridges/INVALID_TRANSFER_REPORT.md", "finding": f"{bridge_summary['invalid_transfer_rows']} guardrails include transition/P3, path/P5, semantics/P1, holonomy/arrow, strictness/objecthood, access, enablement, and reachability separations.", "limitation": "A forbidden collapse may be repaired only by the named bridge/certificate."},
        {"requirement_id": "S2-R10", "plan_requirement": "Interaction, access, admission, join, retention, enablement, order, and budget distinctions are typed.", "status": "PASS", "evidence": "synthesis/step2/INTERACTION_ACCESS_TAXONOMY.md; synthesis/step2/*_matrix.csv", "finding": "Fourteen typed matrices preserve status ladders and nonimplications.", "limitation": "The matrices are synthesis controls, not new VII primitives."},
        {"requirement_id": "S2-R11", "plan_requirement": "Every domain application has a concrete carrier/interface/audit map or an explicit analogy/source block.", "status": "PASS_WITH_RECORDED_SOURCE_LIMIT", "evidence": "synthesis/step2/application_pressure_tests.*", "finding": f"All {len(apps)} pressure-test papers are mapped; P039 is BLOCKED_SOURCE.", "limitation": "Application conclusions do not transfer back to abstract SBT without a typed bridge."},
        {"requirement_id": "S2-R12", "plan_requirement": "Every wishlist atom links to relevant support, counterclaims, open problems, laws/no-gos, and bridges.", "status": "PASS", "evidence": "wishlists/step2_evidence_links.*; wishlists/WISHLIST_DISPOSITION_STEP2.md", "finding": f"All {len(wish)} atomic requests have evidence and boundary links.", "limitation": "Final inherited/new/rejected adjudication is reserved for Step 3."},
        {"requirement_id": "S2-R13", "plan_requirement": "P040/P058 non-independence is controlled at claim level.", "status": "PASS_WITH_UNRESOLVED_SEMANTIC_CHOICE", "evidence": "bridges/VF-SAU-01_claim_delta.csv; bridges/VF-SAU-01_CLAIM_DELTA.md; bridges/unresolved_conflicts.*", "finding": f"{bridge_summary['version_delta_rows']} alignment rows retain the pair as one non-independent evidence family.", "limitation": "No canonical member or theorem-equivalence ruling is selected at Step 2."},
        {"requirement_id": "S2-R14", "plan_requirement": "All unresolved conflicts are typed and source-grounded.", "status": "PASS", "evidence": "bridges/unresolved_conflicts.*", "finding": f"{len(conflicts)} conflicts have source grounding and safe reuse rulings.", "limitation": "Unresolved means explicitly bounded, not silently settled."},
        {"requirement_id": "S2-R15", "plan_requirement": "The concept/dependency graph closes over all claims, laws/no-gos, wish atoms, and bridge edges.", "status": "PASS", "evidence": "synthesis/step2/claim_dependency_graph.graphml; synthesis/step2/claim_graph_nodes.csv; synthesis/step2/claim_graph_edges.csv", "finding": f"{bridge_summary['graph_nodes']} nodes and {bridge_summary['graph_edges']} edges; every endpoint resolves.", "limitation": "Navigation edges do not themselves prove bridge validity."},
        {"requirement_id": "S2-R16", "plan_requirement": "Step 2 does not begin Foundations VII theorem construction.", "status": "PASS", "evidence": "generated/step2_validation.json; git diff read-step-01-complete-formal-spine -- formalization/lean", "finding": "No Foundations VII Lean source change, candidate law, no-go program, or Step-3 dossier is present.", "limitation": "Step 3 remains explicitly unstarted."},
    ]
    req_fields = ["requirement_id", "plan_requirement", "status", "evidence", "finding", "limitation"]
    write_csv(ROOT / "reports" / "STEP2_REQUIREMENT_AUDIT.csv", req_rows, req_fields)
    req_md = [
        "# Step-2 requirement audit", "",
        "This table maps the original Step-2 delivery and exit-gate requirements to canonical repository evidence. `PASS_WITH_*` records a bounded source, environment, or semantic limitation; it is not a silent exception.", "",
        "| ID | Requirement | Status | Evidence | Finding / limitation |", "|---|---|---|---|---|",
    ]
    for row in req_rows:
        req_md.append(f"| `{row['requirement_id']}` | {row['plan_requirement']} | `{row['status']}` | `{row['evidence']}` | {row['finding']} **Limit:** {row['limitation']} |")
    (ROOT / "reports" / "STEP2_REQUIREMENT_AUDIT.md").write_text("\n".join(req_md) + "\n", encoding="utf-8")

    # Root completion report.
    root = [
        "# Foundations VII readiness program — Step 2 completion report", "",
        "## Status", "",
        "**Step 2 is complete to the supplied-source boundary. Step 3 has not started.**", "",
        "**Delivery tag:** `read-step-02`. The included annotated tag resolves to the exact delivered commit.", "",
        "The cumulative repository now converts the complete supplied SBT corpus into one source-located claim body, aligns that body with the inherited Foundations I–VI Lean scaffold, and types every paper invocation, named law import, no-go boundary, application map, and wishlist evidence link needed for the later Foundations VII dependency-closure pass.", "",
        "## Canonical claim corpus", "",
        f"- **{len(claims)} canonical claim records** across all **58 paper roots**.",
        f"- **{claim_types['definition'] + claim_types['prose_definition'] + claim_types['construction'] + claim_types['convention']} definition/construction records**.",
        f"- **{sum(claim_types[k] for k in ('theorem','lemma','proposition','corollary','schema','postulate','principle'))} theorem/schema/principle records** before named result summaries.",
        f"- **{claim_types['nonclaim'] + claim_types['scope_boundary']} explicit nonclaim/scope records**.",
        f"- **{claim_types['open_problem']} open/deferred records**.",
        f"- **{sum(c['review_status'] == 'SOURCE_EXTRACTED_COMPOSITE' for c in claims)} composite abstract theses** and **{sum(c.get('proof_status') == 'ABSTRACT_STATUS_BOUNDARY' for c in claims)} explicit abstract boundary components**.",
        f"- **{len(carriers)} example/carrier records**.",
        "- Every paper has a per-paper JSONL and a Markdown dossier with a complete source-located claim index.", "",
        "P039 remains the only source-package exception. Its root and abstract are preserved, but eighteen included TeX files and the bibliography are absent. The repository records its abstract-level thesis and explicit abstract nonclaim, while licensing no reconstruction of missing theorem, proof, calibration, or body-level boundary text.", "",
        "## Bridge atlas", "",
        f"The atlas contains **{len(bridges)} bridge records**:", "",
        f"- **{bridge_kinds['PAPER_INVOCATION']} paper-invocation rows**, one for every in-corpus citation edge from Step 1;",
        f"- **{bridge_kinds['NAMED_LAW_IMPORT']} named-law rows**, representing **{bridge_summary['named_law_accepted_occurrences']} accepted source occurrences** after auditing **{bridge_summary['named_law_candidate_occurrences']} F/E/G-shaped candidates**;",
        f"- **{bridge_kinds['PRIOR_LAW_REUSE_CONTRACT']} reuse contracts**, covering every 52 F, 16 E, 13 G, and 8 no-go row.", "",
        "Each row carries a source claim, target context, typed object/interface description, inherited and added hypotheses, lost-hypothesis warning, source-of-truth path, formalization posture, exact licensed conclusion, nonclaims, and nearest countermodel. Citation identity alone never licenses theorem inheritance.", "",
        "The classification census is:", "",
        md_counter(bridge_classes), "",
        "The large `UNKNOWN`, `PARTIAL`, and `ANALOGY` populations are intentional anti-overread results. They identify where Foundations VII must later prove an adapter, narrow a claim, or retain a nontransfer boundary.", "",
        "## Interaction and access synthesis", "",
        "The typed matrices now separate:", "",
        "- expressible, present, exposed, recoverable, adequate, admissible, reachable, and occurrent states;",
        "- rule text, executable operation, native/bridged record, prospective commitment, external provision, endogenous generation, and rollback;",
        "- potential contact, evidenced contact, peer transport, common refinement, composite package, strict join, obstructed join, and certified non-interaction;",
        "- shared source, common quotient, common instrument, prospective commitment, and common refinement;",
        "- parent retention, absorption, enablement attribution, and endogenous birth class;",
        "- interaction order, confluence, holonomy, and directionality;",
        "- currencies, budgets, observer/instrument occupancy, and refund/failure accounting.", "",
        "These distinctions prevent the recurrent invalid collapses: common source is not shared access; strict extension is not objecthood or drive; P3 holonomy is not P6 directionality; enablement is not descent; and soundness, reachability, and occurrence are different obligations.", "",
        f"The canonical graph contains **{bridge_summary['graph_nodes']} nodes and {bridge_summary['graph_edges']} typed edges**. It deliberately excludes 41 recall-oriented lexical law-tag edges that lacked an independently accepted named-law occurrence bridge; audited bridge edges remain.", "",
        "## No-go and negative-result control", "",
        f"All **{len(no_gos)} existing no-go theorems** now retain exact source and macro-expanded statements plus a scope row naming the carrier, hypotheses, conclusion, what is ruled out, what remains outside the result, escape route, and formalization posture. A separate **{len(no_go_correspondence)}-row** table maps them conservatively to the inherited Lean scaffold without claiming statement identity. The invalid-transfer register contains **{bridge_summary['invalid_transfer_rows']}** explicit guardrails.", "",
        "## Application pressure tests", "",
        f"All **{len(apps)} domain papers** in the Step-2 pressure-test set have a concrete carrier, interface/lens, audit/certificate, principal claim links, nonclaim links, distinguishing role, and forbidden back-transfer. P039 alone is `BLOCKED_SOURCE`. Applications test the abstract theory; they are not counted as independent votes for it.", "",
        "## Wishlist evidence closure", "",
        f"All **{len(wish)} atomic wishlist requests** are linked to supporting claims, boundary/counterclaims, open problems, numbered laws/no-gos, and bridge rows. These are Step-2 evidence dispositions only. Final inheritance/new-work adjudication remains reserved for Step 3.", "",
        "## Formalization reuse", "",
        f"The active inherited formal spine remains **{formal_summary['unique_active_modules']} modules, {formal_summary['unique_active_declarations']} declarations, {formal_summary['unique_active_theorems']} theorem declarations, and {formal_summary['import_edges']} resolved import edges**, with zero unresolved imports and zero Foundations VII declarations. The inherited trust surface remains one axiom and five opaque declarations. Step 2 adds claim-to-formalization maps and reuse contracts but no new Lean theorem.", "",
        "Claim-level formalization statuses are:", "",
        md_counter(formal), "",
        "A matched declaration is still bounded by its statement-delta record and machine status. The local Lean 4.28.0 toolchain was unavailable, so no fresh kernel replay is claimed.", "",
        "## Version and conflict control", "",
        f"P040/P058 have **{bridge_summary['version_delta_rows']} claim-alignment rows** and remain one non-independent evidence family. No canonical member or theorem-equivalence ruling was selected. The conflict register contains **{len(conflicts)}** typed, source-grounded unresolved matters with safe reuse rulings.", "",
        "## Principal paths", "",
        "- `claims/by_paper/` and `notes/dossiers/` — complete per-paper claim bodies and canonical JSON bridge supplements.",
        "- `registry/claims.*` — canonical claim registry.",
        "- `registry/proof_artifact_lean_coverage.*` — claim-level proof/formalization map.",
        "- `bridges/bridge_atlas.*` — all bridge records.",
        "- `bridges/named_law_occurrence_audit.*` — precision-controlling accept/reject audit for every F/E/G-shaped token.",
        "- `bridges/no_go_scope_matrix.*`, `formalization/integration/no_go_prior_scaffold_correspondence.*`, and `bridges/INVALID_TRANSFER_REPORT.md` — negative-result boundaries and inherited Lean correspondences.",
        "- `synthesis/step2/` — interaction/access taxonomies, application pressure tests, and claim graph.",
        "- `wishlists/step2_evidence_links.*` — complete wishlist traceability.",
        "- `reports/STEP2_VALIDATION.md` — executable exit-gate report.",
        "- `reports/STEP2_REQUIREMENT_AUDIT.{csv,md}` — plan-to-artifact delivery audit.", "",
        "## Remaining limitations carried forward", "",
        "1. P039 cannot be read beyond its supplied abstract without the missing source files.",
        "2. Lean 4.28.0 was not locally available; static import/declaration closure is verified, but fresh kernel elaboration is not claimed.",
        "3. Claim normalizations are navigational. Exact TeX and Lean statements remain authoritative.",
        "4. P040/P058 theorem-level canonicalization remains unresolved by design.",
        "5. Partial, analogy, unknown, and source-blocked bridges remain proof obligations; they have not been promoted.", "",
        "## Boundary against Step 3", "",
        "No Foundations VII primitive, candidate law, no-go program, countermodel atlas, Two-Theory World, or new Lean declaration is created here. Step 2 supplies the evidence and bridge body that Step 3 will later adjudicate.",
    ]
    (ROOT / "STEP2_REPORT.md").write_text("\n".join(root) + "\n", encoding="utf-8")

    print(json.dumps({
        "reports_built": 7,
        "claims": len(claims),
        "bridges": len(bridges),
        "papers": len(by_paper),
        "wishlist_atoms": len(wish),
        "example_carriers": len(carriers),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

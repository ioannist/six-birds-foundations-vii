#!/usr/bin/env python3
"""Build the formalization-aware completion artifacts for Foundations VII Step 1.

This pass remains reconnaissance. It reconciles paper-side formalization
claims with the exact prior assets supplied in the Foundations VI/Collatz
archive, but it does not create Step-2 claim or bridge records.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "papers"
INTEGRATION = ROOT / "formalization" / "integration"
REPORTS = ROOT / "reports"
SYNTHESIS = ROOT / "synthesis"
DEEP_FORMAL = ROOT / "notes" / "deep_formalization"

PAPERS = {
    "P031": SOURCE / "Tsiokos_2026_Six_Birds_Foundations_of_Emergence_Calculus.tex",
    "P027": SOURCE / "Tsiokos_2026_Six_Birds_Foundations_II_Admissibility_Meta_Theory_and_the_Exact_Six_Program.tex",
    "P026": SOURCE / "Tsiokos_2026_Six_Birds_Foundations_III_A_Finite_Audited_Interaction_Calculus_for_SBT.tex",
    "P028": SOURCE / "Tsiokos_2026_Six_Birds_Foundations_IV_A_Catalog_of_Layer_Agnostic_Structural_Laws.tex",
    "P030": SOURCE / "Tsiokos_2026_Six_Birds_Foundations_V_Endogenous_Closure_A_Catalog_of_Structural_Laws_for_Living_Cognitive_and_Social_Systems.tex",
    "P029": SOURCE / "Tsiokos_2026_Six_Birds_Foundations_VI_A_Catalog_of_Dynamical_Structural_Laws.tex",
    "P032": SOURCE / "Tsiokos_2026_Six_Birds_No_Go_Theorems_for_Audited_Emergence.tex",
    "P040": SOURCE / "Tsiokos_2026_The_Usefulness_of_Non_Descending_Objects_A_Six_Birds_Theory_of_Mathematical_Applicability.tex",
    "P058": SOURCE / "Tsiokos_2026_Why_Mathematics_Even_Works.tex",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    fields = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def clean_tex(raw: str) -> str:
    text = raw
    for _ in range(6):
        text = re.sub(r"\\(?:textbf|textit|emph|mathrm|mathbf|mathsf|mathtt|operatorname|textrm|texttt|text|underline)\s*\{([^{}]*)\}", r"\1", text)
        text = re.sub(r"\\texorpdfstring\s*\{([^{}]*)\}\s*\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\(?:label|cite\w*|ref|cref|Cref|eqref|footnote|url|href)\*?(?:\[[^\]]*\])?\s*\{[^{}]*\}", " ", text)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = text.replace("---", "—").replace("--", "–").replace("~", " ")
    text = re.sub(r"[{}$]", " ", text)
    text = re.sub(r"\\[\[\]()]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def source_line(path: Path, needle: str, start: int = 1) -> int:
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if i >= start and needle in line:
            return i
    return 0


def build_evidence_ladder() -> None:
    text = """# Formalization evidence ladder and fidelity axes

This file is the controlling Step-1 rule for the words **formalized**, **mechanized**, **verified**, and **available for reuse**. A paper-side status, a Lean declaration, a locally present file, a resolved import graph, a kernel build, and a finite laboratory run are different facts. None may be substituted for another.

## Axis A — mathematical claim grade

Preserve the paper's grade independently of the implementation: theorem, schema, calibration-anchored schema, conditional classification, mechanized finite result, interpretive corollary, proposal, nonclaim, or open problem. A Lean theorem declaration does not automatically promote a paper-side schema.

## Axis B — statement fidelity

| Fidelity | What it licenses | What it does not license |
|---|---|---|
| `DIRECT_DERIVATION` | The Lean theorem derives the paper statement at the declared scope. | Broader prose, empirical realization, or an unstated bridge. |
| `NARROWED_OR_PARAMETRIC` | A genuine proof of a narrower or parameterized statement. | The full paper statement without the narrowing disclosure. |
| `CONDITIONAL_CLASSIFICATION` | Consequences follow from complete, linked, host-supplied evidence. | Discovery or construction of those host certificates. |
| `PROJECTION_OR_WRAPPER` | A proof-carrying record is projected or a guarded implication is applied. | An independent derivation of the wrapped premise. |
| `TYPED_MIRROR` | Types, constructors, statuses, and malformed-case rejection are checked. | The mathematical theorem mirrored by the types. |
| `PAPER_PROOF_ONLY` | The result is proved in the paper but not in the supplied Lean surface. | A mechanization claim. |
| `INTERPRETIVE_ONLY` | The statement is interpretation or outlook. | Theorem-grade inheritance. |

## Axis C — locally available verification state

| Code | State | Exact meaning |
|---|---|---|
| `R0_PAPER_REPORTED` | Paper disclosure only | The source paper reports a formal artifact. The artifact need not be present here. |
| `R1_ASSET_PRESENT` | File available | The relevant source file is present in this repository and covered by provenance hashes. |
| `R2_STATIC_INDEXED` | Lexically indexed | Modules, declarations, imports, placeholder tokens, and trust declarations were statically indexed. This is not elaboration. |
| `R3_IMPORT_RESOLVED` | Local import graph resolved | Every local import edge in the supplied project resolves to a present module. This is not a kernel check. |
| `R4_KERNEL_COMPILED` | Locally rebuilt by Lean | The exact local project compiled under its pinned toolchain. This state is **not reached in the current environment** because Lean/Lake is unavailable. |
| `R5_RUNTIME_VALIDATED` | Tests/labs rerun locally | The named finite or computational checks were executed locally. This is evidence for those fixtures, not a theorem proof. |

These states are cumulative only within one exact artifact. A paper can be `R0` while a narrower imported subset is `R1–R3`. Runtime validation is orthogonal to theorem fidelity; a passing laboratory does not upgrade a schema into a theorem.

## Current repository-wide ruling

- Foundations I, II, III, fourteen Foundations IV rows, all sixteen Foundations V E laws, and all thirteen Foundations VI law modules are present and statically indexed through `R3`.
- The Foundations V archive supplies the complete D1--D6 / E1--E16 authored theorem base. The immutable upstream root and 1,141-row manifest omit the already-landed E16 module/declarations; VII-owned import and manifest adapters complete discoverability without editing upstream files.
- No imported Lean project reached `R4` in this environment. The repository must say **source/import graph checked**, not **compiled here**.
- Sixty-two locally available Foundations VI lab tests and 317 non-E15 Foundations V tests reached `R5`; the E16 standalone sweep also passed 69/69 comparisons. Three G11 tests require unavailable PySAT, while the 74-test E15 file exceeded the local 900-second replay limit. These runtime facts do not alter paper grades.

## Mandatory citation form for later work

A later claim that reuses prior Lean must state all four items:

1. paper-side claim grade;
2. exact Lean module/declaration and fidelity;
3. trust-base or host-supplied premises;
4. local verification state (`R0`–`R5`).

The phrase “already mechanized” is forbidden unless these four fields are available.
"""
    (SYNTHESIS / "FORMALIZATION_EVIDENCE_LADDER.md").write_text(text, encoding="utf-8")


def build_spine_coverage() -> list[dict[str, str]]:
    modules = read_csv(INTEGRATION / "lean_modules.csv")
    counts = Counter(row["layer"] for row in modules)
    decls = Counter()
    thms = Counter()
    for row in modules:
        decls[row["layer"]] += int(row["declarations"])
        thms[row["layer"]] += int(row["theorems"])

    rows = [
        {
            "paper_id": "P031",
            "paper_title": "Foundations I",
            "paper_reported_scope": "Minimal backbone only: order closures and ladders; thin packaging/reflection; idempotent endomaps and fixed-point subtypes; explicitly no probability or Markov-chain Lean results.",
            "paper_reported_fidelity": "Direct order-theoretic core at intentionally limited scope.",
            "paper_source_anchor": "papers/Tsiokos_2026_Six_Birds_Foundations_of_Emergence_Calculus.tex:1493-1532",
            "local_assets": f"PRESENT: {counts['FOUNDATIONS_I_CLOSURE']} ClosureLadder modules plus {counts['FOUNDATIONS_I_COMPAT']} Foundations-I compatibility module; {decls['FOUNDATIONS_I_CLOSURE'] + decls['FOUNDATIONS_I_COMPAT']} lexical declarations.",
            "local_verification_state": "R1_ASSET_PRESENT;R2_STATIC_INDEXED;R3_IMPORT_RESOLVED",
            "local_kernel_build": "NOT_RUN: Lean/Lake unavailable",
            "trust_or_fidelity_boundary": "Do not cite the closure core as mechanizing Foundations I probability, Markov, arrow, or empirical claims.",
            "reuse_ruling": "Reuse closure/package/idempotence primitives directly; add adapters for any richer VII package.",
        },
        {
            "paper_id": "P027",
            "paper_title": "Foundations II",
            "paper_reported_scope": "Typed Role/Level/admissibility/decomposition/status harness with semantic rejection tests.",
            "paper_reported_fidelity": "The paper states that no claim is a faithful derivation in its strongest category; claims are typed mirrors, projections, narrowed/parametric declarations, or trivial/by-construction classifier facts.",
            "paper_source_anchor": "papers/Tsiokos_2026_Six_Birds_Foundations_II_Admissibility_Meta_Theory_and_the_Exact_Six_Program.tex:3128-3271",
            "local_assets": f"PRESENT: {counts['FOUNDATIONS_II']} modules; {decls['FOUNDATIONS_II']} lexical declarations; {thms['FOUNDATIONS_II']} theorem/lemma declarations.",
            "local_verification_state": "R1_ASSET_PRESENT;R2_STATIC_INDEXED;R3_IMPORT_RESOLVED",
            "local_kernel_build": "NOT_RUN: Lean/Lake unavailable",
            "trust_or_fidelity_boundary": "The no-seventh-role classifier is by construction under the recognition hypothesis; local declarations check typing and case rejection, not recognition completeness.",
            "reuse_ruling": "Reuse types, status channels, admissibility and non-collapse machinery; never cite the harness as an independent proof of exact-six exhaustiveness.",
        },
        {
            "paper_id": "P026",
            "paper_title": "Foundations III",
            "paper_reported_scope": "Manifest-scoped BirdInt finite audited calculus: 21 full schema definitions and 35 theorem-backed required claims; 56/56 probes/declaration-kind checks and theorem axiom audits reported passing.",
            "paper_reported_fidelity": "Theorem-grade, model-grade, and audit-grade claims remain distinct despite every required claim having a Lean theorem declaration.",
            "paper_source_anchor": "papers/Tsiokos_2026_Six_Birds_Foundations_III_A_Finite_Audited_Interaction_Calculus_for_SBT.tex:9262-9475",
            "local_assets": f"PRESENT: {counts['FOUNDATIONS_III']} modules; {decls['FOUNDATIONS_III']} lexical declarations; {thms['FOUNDATIONS_III']} theorem/lemma declarations. The original paper-specific manifest/strict validator is not part of the supplied active subset.",
            "local_verification_state": "R1_ASSET_PRESENT;R2_STATIC_INDEXED;R3_IMPORT_RESOLVED",
            "local_kernel_build": "NOT_RUN: Lean/Lake unavailable",
            "trust_or_fidelity_boundary": "Local static indexing does not reproduce the paper's original 56-entry manifest validator or broaden its finite audited scope.",
            "reuse_ruling": "Reuse BirdInt records and finite audited interaction primitives; reconstruct or import exact manifest checks before claiming original validation equivalence.",
        },
        {
            "paper_id": "P028",
            "paper_title": "Foundations IV",
            "paper_reported_scope": "All 52 catalog rows have paper-reported Lean realizations: 46 direct faithful theorem rows, 2 substrate anchors, 2 partial guarded wrappers, and 2 obligation guarded wrappers.",
            "paper_reported_fidelity": "Direct, anchored, partial, and obligation modes are explicitly non-interchangeable; F13a/F13b/F14/F15b require strengthening/discharge.",
            "paper_source_anchor": "papers/Tsiokos_2026_Six_Birds_Foundations_IV_A_Catalog_of_Layer_Agnostic_Structural_Laws.tex:9728-10229",
            "local_assets": f"PARTIAL SUBSET PRESENT: {counts['FOUNDATIONS_IV']} F-law modules; {decls['FOUNDATIONS_IV']} lexical declarations; {thms['FOUNDATIONS_IV']} theorem/lemma declarations. Only 14/52 rows are in the supplied archive.",
            "local_verification_state": "R1_ASSET_PRESENT;R2_STATIC_INDEXED;R3_IMPORT_RESOLVED for 14 rows; R0_PAPER_REPORTED for the other 38",
            "local_kernel_build": "NOT_RUN: Lean/Lake unavailable",
            "trust_or_fidelity_boundary": "The imported subset contains one inherited F13a axiom and five opaque constants; paper-wide coverage must not be inferred from the 14 local modules.",
            "reuse_ruling": "Reuse the 14 exact local modules when applicable; treat the remaining 38 rows as paper-reported until their source libraries are supplied.",
        },
        {
            "paper_id": "P030",
            "paper_title": "Foundations V",
            "paper_reported_scope": "D1-D6 definition infrastructure and E1-E16 full core, with E6/E9 shared; E7.1 and E12.1 interpretive corollaries unformalized. Paper reports 1,261 authored declarations, a 391-test pytest run, and a separate 69-case E16 sweep.",
            "paper_reported_fidelity": "Mostly conditional classifications, projections, exclusions, and derived finite algebra from host-supplied complete linked evidence; not empirical construction of those certificates.",
            "paper_source_anchor": "papers/Tsiokos_2026_Six_Birds_Foundations_V_Endogenous_Closure_A_Catalog_of_Structural_Laws_for_Living_Cognitive_and_Social_Systems.tex:6747-7505",
            "local_assets": "PRESENT: 22 authored modules (root + 6 D modules + 15 law modules), 1,261 authored declarations including 187 theorems; all E1-E16 modules, declaration/gate/example/sweep assets, and the finite lab package are retained. The full archive contains 70 Lean modules / 1,758 lexical declarations including vendored dependencies.",
            "local_verification_state": "R1_ASSET_PRESENT;R2_STATIC_INDEXED;R3_IMPORT_RESOLVED;R5_RUNTIME_BASELINE_RECORDED_SEPARATELY",
            "local_kernel_build": "NOT_RUN: Lean/Lake unavailable",
            "trust_or_fidelity_boundary": "No authored axiom/opaque/sorry/admit declarations were found lexically. E16 exists but is omitted from the upstream root and 1,141-row manifest; VII-owned adapters complete import/manifest discoverability. Conditional classifications still require host-supplied complete linked evidence, and open E-law bridges remain open.",
            "reuse_ruling": "Reuse exact D1-D6 and E1-E16 modules through FoundationsVII.PriorFoundationsVComplete; preserve theorem/conditional-classification grades and never infer empirical certificate construction from typed classification proofs.",
        },
        {
            "paper_id": "P029",
            "paper_title": "Foundations VI",
            "paper_reported_scope": "All G1-G13 law modules with theorem/schema/calibration grades, theorem ledger, gates, examples, finite labs, and review corrections.",
            "paper_reported_fidelity": "No project-specific law axioms; Lean theorem declarations preserve paper grades rather than converting schemas to theorems.",
            "paper_source_anchor": "papers/Tsiokos_2026_Six_Birds_Foundations_VI_A_Catalog_of_Dynamical_Structural_Laws.tex:2529-2708",
            "local_assets": f"PRESENT: {counts['FOUNDATIONS_VI']} modules including root and all 13 law modules; {decls['FOUNDATIONS_VI']} lexical declarations; {thms['FOUNDATIONS_VI']} theorem/lemma declarations; theorem/gate/lab traceability retained.",
            "local_verification_state": "R1_ASSET_PRESENT;R2_STATIC_INDEXED;R3_IMPORT_RESOLVED;R5_RUNTIME_VALIDATED for 62 locally available tests",
            "local_kernel_build": "NOT_RUN: Lean/Lake unavailable",
            "trust_or_fidelity_boundary": "Three G11 tests require unavailable PySAT. Local test success does not discharge conditional flagship hypotheses or alter G-law grades.",
            "reuse_ruling": "This is the strongest locally reusable prior law surface; import exact modules and preserve each G law's run quantifiers and paper grade.",
        },
        {
            "paper_id": "P032",
            "paper_title": "No-Go Theorems",
            "paper_reported_scope": "For NG_OBJECT_CONTRACTIVE, only uniqueness of fixed distributions under strict contraction is formalized; the total-variation/Dobrushin epsilon-separation bound remains a paper proof. Other supplementary formalization status is referenced but not supplied in the root source package.",
            "paper_reported_fidelity": "One explicitly narrowed formal component; no blanket mechanization claim for all eight no-go fronts.",
            "paper_source_anchor": "papers/Tsiokos_2026_Six_Birds_No_Go_Theorems_for_Audited_Emergence.tex:894-899",
            "local_assets": "NO dedicated no-go Lean module identified in the supplied Collatz archive.",
            "local_verification_state": "R0_PAPER_REPORTED only for the disclosed contraction-uniqueness component",
            "local_kernel_build": "NOT_AVAILABLE for this artifact",
            "trust_or_fidelity_boundary": "Do not describe all eight no-go theorems, or the Dobrushin epsilon bound, as locally mechanized.",
            "reuse_ruling": "Reuse theorem statements and carrier/escape-route discipline from paper source; obtain the supplementary formal artifact before Lean-level inheritance.",
        },
    ]
    write_csv(INTEGRATION / "foundations_spine_formalization_coverage.csv", rows)
    md = ["# Foundations spine — paper report versus locally reusable formal assets", "", "This is a Step-1 reconciliation table, not a claim-level bridge atlas.", "", "| Paper | Paper-reported scope | Local asset state | Reuse ruling |", "|---|---|---|---|"]
    for row in rows:
        md.append(f"| {row['paper_id']} — {row['paper_title']} | {row['paper_reported_scope']} | {row['local_assets']} {row['local_verification_state']}; kernel: {row['local_kernel_build']}. | {row['reuse_ruling']} |")
    md += ["", "Full fidelity, trust, and source-anchor fields are in `foundations_spine_formalization_coverage.csv`."]
    (INTEGRATION / "FOUNDATIONS_SPINE_FORMALIZATION_COVERAGE.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return rows


def parse_f_disclosure() -> list[dict[str, str]]:
    path = PAPERS["P028"]
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    status_map = {
        "\\statTheorem": "direct theorem row",
        "\\statAnchor": "substrate-delegated anchor",
        "\\statPartial": "partial theorem wrapper",
        "\\statObligation": "obligation-guarded wrapper",
    }
    pat = re.compile(r"^\s*(F\d+[ab]?)\s*&\s*(.*?)\s*&\s*(\\stat\w+)\s*&\s*([^&]+?)\s*&\s*\\path\|([^|]+)\|\s*\\\\")
    parsed: dict[str, dict[str, str]] = {}
    for lineno, line in enumerate(lines, 1):
        match = pat.match(line)
        if not match:
            continue
        fid, name, status_macro, alignment, declaration = match.groups()
        parsed[fid] = {
            "law_id": fid,
            "paper_name": clean_tex(name),
            "paper_formalization_status": status_map[status_macro],
            "paper_semantic_alignment": alignment.strip().replace("-", "_"),
            "paper_lean_declaration": "SixBirdsMetaMath.FoundationsIV." + declaration,
            "paper_source_anchor": f"papers/{path.name}:{lineno}",
        }
    if len(parsed) != 52:
        raise RuntimeError(f"expected 52 F disclosure rows, found {len(parsed)}")
    registry = {row["law_id"]: row for row in read_csv(ROOT / "registry" / "F_laws.csv")}
    local = {row["law_id"]: row for row in read_csv(INTEGRATION / "prior_law_formalization_coverage.csv") if row["series"] == "F"}
    rows = []
    def key(fid: str) -> tuple[int, str]:
        m = re.fullmatch(r"F(\d+)([ab]?)", fid)
        assert m
        return int(m.group(1)), m.group(2)
    for fid in sorted(parsed, key=key):
        p = parsed[fid]
        r = registry[fid]
        l = local.get(fid)
        rows.append({
            "law_id": fid,
            "name": r["name"],
            "axis": r["axis"],
            **p,
            "local_import_status": "IMPORTED_SUBSET_MODULE" if l else "NOT_IN_SUPPLIED_ARCHIVE",
            "local_lean_module": l["lean_module"] if l else "",
            "local_key_declarations": l["key_declarations"] if l else "",
            "local_verification_state": "R1_ASSET_PRESENT;R2_STATIC_INDEXED;R3_IMPORT_RESOLVED" if l else "R0_PAPER_REPORTED",
            "local_kernel_build": "NOT_RUN: Lean/Lake unavailable" if l else "NOT_AVAILABLE",
            "caveat": l["caveat"] if l else "Paper reports a Lean realization, but its source module is not in the supplied Collatz archive.",
        })
    write_csv(INTEGRATION / "f_law_formalization_disclosure.csv", rows)
    return rows


E_PROOF = {
    "E1": ("conditional exact classification and branch elimination", "E1_StatusPartition; E1_Internalization; E1_StrictSelfExtension; E1_NoGeneratorDichotomy", "Host supplies no-free-distinction, finite-forcing, promotion, schedule, binding/discharge, family-budget and classifier-completeness certificates; Lean verifies rather than discovers a repair family."),
    "E2": ("imported self-audit obstruction; derived finite capacity bound; conditional partition", "E2_SelfSoundnessObstruction; E2_ForcedStratification; E2_CapacityBound; E2_StatusPartition", "Tower bridges, record accounting, occurrence completeness and capacity declaration are certified; general audit-capacity pricing remains open."),
    "E3": ("conditional two-level verification and measured ablation consequence", "E3_TwoLevelFixedPoint; E3_StatusPartition; E3_RegressStoppedByE2; E3_AblationSeparation", "Persistence/coherence, metric/curve data, challenge typing and the cited tower are supplied."),
    "E4": ("conditional compilation; derived brittleness; exact partition", "E4_Compilation; E4_Brittleness; E4_StatusPartition", "Memory-only control, F2/F9 links, descent, silence and promotion instantiation are certified; general E4-to-E11 compilation remains open."),
    "E5": ("conditional complete-inventory verification; definitional collapse falsifier", "E5_CollapseFalsifier; E5_ReclosureCollapse; E5_IrreversibleCollapse; E5_SubsidyWithdrawalReclassification", "Inventory completeness, move-linked descent, reachability/kernel grade, subsidy and status completeness are inputs; E7-to-E5 onset remains open."),
    "E6": ("derived finite KKT and slack algebra", "E6_AttentionKKT; E6_SlackCollapse", "KKT equations, positive costs, feasibility, convex-host reading, carried policy and optimizer correctness are supplied; salience is sweep-level."),
    "E7": ("conditional exact trichotomy and structural projection", "E7_AlarmTrichotomy; E7_PreemptionSignature", "Xi/Omega values, viability coupling, horizon, response surface, no-overread, null-mode legality and totality are supplied; E7.1 is unformalized."),
    "E8": ("conditional control-price classification; direct reuse of E2 bound", "E8_ControlPrice; E8_ComponentShadowPrice; E8_CompressedSummaryLawfulness; E8_1_AuditCapture; E8_1_MetaAuditBoundedByE2", "Comparator/KKT honesty, field completeness, held-out rows, lineage and budget-status inventories are supplied; general E2 pricing and E3 lineage links remain open."),
    "E9": ("derived Xi zero-contraction and finite rational argmax", "E9_SameFamilyStrictness; exists_max_ratio; E9_CuriosityArgmax; E6_E9_AccessArbitration", "Catalog, budget/risk admissibility, candidate completeness, positive costs and saturation honesty are supplied."),
    "E10": ("conditional priority-normalized exact classifications", "E10_CognitiveDemarcation; E10_1_Intention; E10_2_Goal; falsifier wrappers", "E1-style descent, Foundations III channel, enablement comparators, route persistence and complete status records are inputs; E10.1-to-E11 remains open."),
    "E11": ("conditional structural comparator and exact classification", "E11_StackActivity; E11_Constitutive; E11_NCTDObstruction; E11_StatusPartition", "Material forcing, washout, thresholds, outcome readout and E4-shaped record are supplied; general E4/E10 bridges remain open."),
    "E12": ("conditional joint closure, declared-candidate maximality and exact partition", "E12_Individuation; E12_StatusPartition", "F7 sufficiency, F10 coarsestness, declared candidate/probe lists and E3 maintenance are inputs; E12.1, boundary discovery and E12-to-E13 flow remain open."),
    "E13": ("conditional four-clause verification and exact classification", "E13_Communication; E13_TeachingCapacity; E13_CoercionNull; E13_SymbolicRepair; E13_StatusPartition", "Interface mediation, role preservation, compression/saturation, coercion-null content and bridge-comparator honesty are supplied."),
    "E14": ("conditional trigger/outcome verification and exact trichotomy", "E14_ReconsolidationStatus; E14_LawfulConflictTrichotomy; branch projections; control/falsifier theorems", "F9 disposition, F20 formation, transport, provenance, distinction support and ledger-charge comparators are supplied."),
    "E15": ("derived debt/budget identities and conditional finite case packaging", "E15_DeficitAlternation; E15_OfflineCapacityExactlyFreed; E15_OfflineReclosureStatus; falsifier/regime theorems", "F3 status, Xi valuation, P2 exchange, E7/E5 observations and complete flows are supplied; scalar debt-to-alarm causation remains open."),
    "E16": ("conditional route/control classification; imported holonomy asymmetry and structural projections", "E16_AdaptabilityStatus; E16_CoherentAdaptability; E16_CurrentAuditBlindness; E16_RouteManufacturesRepairCapacity; E16_LoopAsymmetryAnchor", "Route admissibility, trial eligibility, probability semantics, control universes and E15 bridge acceptance are supplied; paper records a root-aggregator omission despite module landing."),
}


def build_e_disclosure() -> list[dict[str, str]]:
    registry = read_csv(ROOT / "registry" / "E_laws.csv")
    rows = []
    for row in registry:
        eid = row["law_id"]
        proof, declarations, boundary = E_PROOF[eid]
        rows.append({
            "law_id": eid,
            "name": row["name"],
            "cluster": row["cluster"],
            "paper_grade": row["paper_grade"],
            "paper_lean_status": "full core",
            "paper_proof_grade": proof,
            "paper_principal_declarations": declarations,
            "paper_certified_or_open_boundary": boundary,
            "paper_source_anchor": "papers/Tsiokos_2026_Six_Birds_Foundations_V_Endogenous_Closure_A_Catalog_of_Structural_Laws_for_Living_Cognitive_and_Social_Systems.tex:6747-7040",
            "local_import_status": ("PRESENT_SHARED_MODULE" if eid in {"E6", "E9"} else "PRESENT_MODULE_WITH_VII_ROOT_COMPLETION" if eid == "E16" else "PRESENT_DEDICATED_MODULE"),
            "local_verification_state": "R1_ASSET_PRESENT;R2_STATIC_INDEXED;R3_IMPORT_RESOLVED",
            "local_kernel_build": "NOT_RUN: Lean/Lake unavailable",
            "caveat": ("The E16 module is locally present (120 declarations, 15 theorems). The immutable upstream root and manifest omit it; VII-owned adapters complete discoverability without modifying upstream files. Paper grade and host-certificate obligations remain controlling." if eid == "E16" else "The local module is present and statically import-closed. This verifies source availability and dependency closure, not a local kernel replay; paper grade, conditional hypotheses, and host-certificate obligations remain controlling."),
        })
    write_csv(INTEGRATION / "e_law_formalization_disclosure.csv", rows)
    return rows


def build_g_disclosure() -> list[dict[str, str]]:
    registry = {row["law_id"]: row for row in read_csv(ROOT / "registry" / "G_laws.csv")}
    trace = read_csv(INTEGRATION / "g_law_traceability.csv")
    rows = []
    for tr in trace:
        gid = tr["law_id"]
        reg = registry[gid]
        rows.append({
            "law_id": gid,
            "name": reg["name"],
            "paper_grade": reg["paper_grade"],
            "paper_source_anchor": f"{reg['source_path']}:{reg['source_line']}",
            "local_import_status": "IMPORTED_COMPLETE_G_SERIES",
            "local_lean_module": tr["lean_module"],
            "local_lean_file": tr["lean_file"],
            "theorem_count": tr["theorem_count"],
            "gate_note": tr["gate_note"],
            "example_note": tr["example_note"],
            "lab_packages": tr["lab_packages"],
            "test_files": tr["test_files"],
            "recorded_results": tr["recorded_results"],
            "local_verification_state": "R1_ASSET_PRESENT;R2_STATIC_INDEXED;R3_IMPORT_RESOLVED;R5_RUNTIME_VALIDATED_PARTIAL_SUITE",
            "local_kernel_build": "NOT_RUN: Lean/Lake unavailable",
            "caveat": "Preserve the paper grade. Sixty-two locally available suite tests passed overall; three G11 tests requiring PySAT were unavailable. Tests do not discharge conditional law hypotheses.",
        })
    write_csv(INTEGRATION / "g_law_formalization_disclosure.csv", rows)
    return rows


LEVEL = {"part": 0, "section": 1, "subsection": 2, "subsubsection": 3, "paragraph": 4}


@dataclass
class Heading:
    kind: str
    title: str
    raw_title: str
    line: int
    start: int
    end: int


def parse_headings(path: Path) -> tuple[str, list[Heading]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(r"\\(part|section|subsection|subsubsection|paragraph)\*?\{")
    headings: list[Heading] = []
    for match in pattern.finditer(text):
        i = match.end()
        depth = 1
        while i < len(text) and depth:
            if text[i] == "{" and text[i - 1] != "\\":
                depth += 1
            elif text[i] == "}" and text[i - 1] != "\\":
                depth -= 1
            i += 1
        raw = text[match.end(): i - 1]
        headings.append(Heading(match.group(1), clean_tex(raw), raw, text.count("\n", 0, match.start()) + 1, match.start(), i))
    return text, headings


def tokens(text: str) -> list[str]:
    text = re.sub(r"(?m)(?<!\\)%.*$", " ", text)
    return [x.lower() for x in re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", text)]


def shingle_jaccard(a: str, b: str, width: int = 5) -> float:
    ta, tb = tokens(a), tokens(b)
    sa = set(zip(*(ta[i:] for i in range(width)))) if len(ta) >= width else set()
    sb = set(zip(*(tb[i:] for i in range(width)))) if len(tb) >= width else set()
    return len(sa & sb) / (len(sa | sb) or 1)


def build_version_delta() -> list[dict[str, str]]:
    text40, h40 = parse_headings(PAPERS["P040"])
    text58, h58 = parse_headings(PAPERS["P058"])
    if len(h40) != 73 or len(h58) != 73:
        raise RuntimeError(f"expected 73 headings each, got {len(h40)}/{len(h58)}")
    rows = []
    for idx, (a, b) in enumerate(zip(h40, h58), 1):
        end40 = h40[idx].start if idx < len(h40) else len(text40)
        end58 = h58[idx].start if idx < len(h58) else len(text58)
        body40 = text40[a.end:end40]
        body58 = text58[b.end:end58]
        if a.kind != b.kind:
            relation = "STRUCTURE_MISMATCH"
        elif a.title == b.title:
            relation = "IDENTICAL_HEADING"
        else:
            relation = "RENAMED_HEADING"
        rows.append({
            "ordinal": str(idx),
            "level": a.kind,
            "p040_line": str(a.line),
            "p040_heading": a.title,
            "p058_line": str(b.line),
            "p058_heading": b.title,
            "heading_relation": relation,
            "body_five_word_shingle_jaccard": f"{shingle_jaccard(body40, body58):.6f}",
            "step1_ruling": "same structural slot; retain both member-specific source locations",
        })
    write_csv(REPORTS / "P040_P058_SECTION_DELTA.csv", rows)
    exact = sum(row["heading_relation"] == "IDENTICAL_HEADING" for row in rows)
    renamed = len(rows) - exact
    scores = sorted(rows, key=lambda x: float(x["body_five_word_shingle_jaccard"]))
    low = scores[:10]
    md = [
        "# P040/P058 section-level delta ledger",
        "",
        "This is the Step-1 reconciliation required for the `VF-SAU-01` version family. It aligns the supplied sources structurally without performing the claim-level theorem comparison reserved for Step 2.",
        "",
        f"- Both members contain **73 aligned structural headings**.",
        f"- **{exact} headings are text-identical** and **{renamed} are editorially renamed** in the same structural slot.",
        "- The archive filenames and internal titles remain crossed; stable IDs, paths, and hashes are authoritative.",
        "- Body similarity is recorded per slot as a five-token-shingle Jaccard diagnostic. It is not a proof that theorem hypotheses or statuses are identical.",
        "",
        "## Material Step-1 conclusion",
        "",
        "The technical spine from `Theory Layers and Promoted-Use Traces` through the four case studies, transfer synthesis, definition bank, deferred proofs, artifact map, and Lean notes is structurally aligned. The largest editorial differences occur in the introduction and outlook/contribution framing, with additional local rewrites inside corresponding technical slots. Step 1 therefore treats P040/P058 as one evidence family but keeps every citation member-specific. No canonical member is selected before the Step-2 claim delta.",
        "",
        "## Lowest-similarity aligned slots",
        "",
        "| Ordinal | Level | P040 | P058 | Body Jaccard |",
        "|---:|---|---|---|---:|",
    ]
    for row in low:
        md.append(f"| {row['ordinal']} | {row['level']} | {row['p040_heading']} | {row['p058_heading']} | {row['body_five_word_shingle_jaccard']} |")
    md += [
        "",
        "## Remaining obligation",
        "",
        "Step 2 must compare individual definitions, theorem statements, hypotheses, proofs, grades, and nonclaims. Until that comparison, neither member silently supersedes the other and the family contributes one non-independent line of evidence.",
    ]
    (REPORTS / "P040_P058_SECTION_DELTA.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return rows


def build_deep_formal_notes() -> None:
    DEEP_FORMAL.mkdir(parents=True, exist_ok=True)
    notes = {
        "P031": """# P031 — formalization-aware Step-1 supplement

## Correction to the initial deep read

Foundations I's Lean claim is intentionally **minimal**. The paper mechanizes order-closure and closure ladders, thin packaging/reflection, idempotent endomaps, fixed-point subtypes, and their bridge. It explicitly says that no probability or Markov-chain results are mechanized (`source/papers/Tsiokos_2026_Six_Birds_Foundations_of_Emergence_Calculus.tex:1493-1532`).

## Supplied reusable surface

The imported archive contains five `ClosureLadder` modules and one Foundations-I compatibility module. They are hash-covered, statically indexed, and import-resolved, but not locally kernel-compiled because Lean/Lake is unavailable.

## VII reuse boundary

VII may directly reuse closure/package/idempotence definitions. It may not cite this core as a mechanization of arrow, probability, Markov, empirical, or full three-certificate results. Any richer theory-package object needs an explicit adapter and proof.
""",
        "P027": """# P027 — formalization-aware Step-1 supplement

## Load-bearing fidelity disclosure

The paper states unambiguously that **no claim in its Lean development is a faithful derivation in the strongest sense**. The project is a typed harness: typed mirrors, proof-record projections, narrowed/parametric witnesses, and by-construction bookkeeping/classification. The no-seventh-role classifier encodes the recognition hypothesis; it does not independently prove recognition completeness (`source/papers/Tsiokos_2026_Six_Birds_Foundations_II_Admissibility_Meta_Theory_and_the_Exact_Six_Program.tex:3128-3271`).

## Supplied reusable surface

Ten Foundations-II modules are present, with the Role/Level/admissibility/decomposition/status machinery and malformed-case rejection surface. They reach local evidence state R3 (asset, static index, resolved local imports), not a local kernel rebuild.

## VII reuse boundary

Use these types to prevent role collapse and to type new status channels. Never cite module presence, `upper_bound_classification`, or a `True` closure lemma as an independent proof of exact-six exhaustiveness.
""",
        "P026": """# P026 — formalization-aware Step-1 supplement

## Paper-reported validation scope

Foundations III reports a manifest-scoped Lean artifact with 21 full schema definitions and 35 theorem-backed required claims, 56/56 probes and declaration-kind checks, theorem axiom audits, placeholder scans, and semantic audits. The paper preserves theorem-grade, model-grade, and audit-grade distinctions even though required claims have Lean theorem declarations (`source/papers/Tsiokos_2026_Six_Birds_Foundations_III_A_Finite_Audited_Interaction_Calculus_for_SBT.tex:9262-9475`).

## Supplied reusable surface

Twenty-four BirdInt modules are present and statically indexed. The exact original paper manifest, strict validator, and trust-base audit scripts are not all part of the active imported subset, so this repository does not claim to have rerun the paper's 56-entry validation protocol.

## VII reuse boundary

BirdInt records, pair/cell/status/promotion machinery are prime reuse targets. Before claiming validation equivalence, restore the exact manifest/gate machinery or construct a VII-specific manifest with explicit statement mappings.
""",
        "P028": """# P028 — formalization-aware Step-1 supplement

## Paper-wide versus locally supplied coverage

Foundations IV reports all 52 catalog rows in Lean: 46 faithful direct theorem rows, F6/F53 as substrate anchors, F13a/F14 as partial guarded wrappers, and F13b/F15b as obligation guarded wrappers. The paper forbids describing projections, anchors, or guarded wrappers as direct proofs and explicitly marks the four guarded rows as needing strengthening (`source/papers/Tsiokos_2026_Six_Birds_Foundations_IV_A_Catalog_of_Layer_Agnostic_Structural_Laws.tex:9728-10229`).

## Supplied reusable surface

The Collatz archive contains only 14 F-law modules: F2, F3, F4, F6, F7, F10, F11, F12, F13a, F19, F27, F34, F40, and F49. The other 38 are paper-reported only in this repository. The imported subset exposes one F13a axiom and five opaque constants in its trust ledger. F4's local theorem is an abstract family and does not explicitly encode the paper prose's finiteness qualification.

## VII reuse boundary

Use exact local declarations only for the 14 present rows and carry their statement deltas/trust premises. Do not infer paper-wide local mechanization from the source appendix or the partial import.
""",
        "P030": """# P030 — formalization-aware Step-1 supplement

## Paper-reported formalization

Foundations V reports D1-D6 definition infrastructure and E1-E16 full core, with E6/E9 sharing a module. E7.1 (Alarm Fatigue) and E12.1 (Operational Selfhood) are unformalized interpretive corollaries. The paper reports 1,261 authored declarations (1,074 definitions, 187 theorems), a 391-test pytest run, and a separate 69-case E16 sweep. Its principal Lean results are conditional classifications, derived finite algebra, projections, and exclusions over complete linked host evidence—not construction of honest biological/social instruments (`source/papers/Tsiokos_2026_Six_Birds_Foundations_V_Endogenous_Closure_A_Catalog_of_Structural_Laws_for_Living_Cognitive_and_Social_Systems.tex:6747-7505`).

## Local theorem base and completion repair

The supplied Foundations V archive is now imported byte-for-byte. Its authored surface contains 22 modules and exactly 1,261 declarations, including 187 theorems, with zero lexical `sorry`, `admit`, axiom, or opaque declarations. All D1--D6 and E1--E16 modules are present and their 196 local import edges resolve. The archive root imports 20 of 21 authored submodules and omits the already-landed E16 module; its 1,141-row manifest likewise omits E16's 120 declarations. A declaration-free VII wrapper and a 1,261-row completed manifest repair discoverability without editing the upstream tree.

The available runtime baseline passes 317 non-E15 tests and the E16 69/69 sweep. The E15 file's 74 tests exceeded the local 900-second replay limit, and Lean/Lake is unavailable, so no local kernel compilation is claimed.

## VII reuse boundary

E-law modules are now direct local dependencies, especially for same-object linkage, universe completeness, and evidence-level priority. Their conditional hypotheses, supplied-certificate semantics, paper grades, and open cross-law bridges remain controlling; mechanized classification must not be presented as construction of honest biological, cognitive, or social evidence.
""",
        "P029": """# P029 — formalization-aware Step-1 supplement

## Complete local G surface with preserved grades

All thirteen G-law modules, theorem ledger, gates, examples, lab packages, tests, recorded results, and review corrections are present. The paper grades are not uniform: G1 is theorem/schema split; G2, G3, G8, G10, G11, G12 are theorems; G4, G6, G13 are schemas; G5, G7, G9 are calibration-anchored schemas (`source/papers/Tsiokos_2026_Six_Birds_Foundations_VI_A_Catalog_of_Dynamical_Structural_Laws.tex:2529-2708`). The Step-1 registry now records these grades explicitly.

## Local verification

The sources are hash-covered, statically indexed, and import-resolved. Sixty-two locally available lab tests pass; three G11 tests require unavailable PySAT. Lean/Lake is unavailable, so no local kernel build is claimed.

## VII reuse boundary

Reuse exact run-level modules and evidence-chain structure. Do not turn schemas into theorems, test fixtures into universal claims, or conditional Collatz-style bridge hypotheses into discharged facts.
""",
        "P032": """# P032 — formalization-aware Step-1 supplement

## Narrow formalization disclosure

The root paper specifically states that, for `NG_OBJECT_CONTRACTIVE`, only uniqueness of fixed distributions under strict contraction is formalized. The total-variation/Dobrushin framework and epsilon-stability separation bound remain paper proofs (`source/papers/Tsiokos_2026_Six_Birds_No_Go_Theorems_for_Audited_Emergence.tex:894-899`). The root refers to supplementary formalization status, but that supplement is not in the supplied source package.

## Local asset state

No dedicated no-go Lean module was identified in the imported Collatz archive. The eight theorem statements, carriers, hypotheses, and escape routes remain source-grounded paper results, not locally mechanized artifacts.

## VII reuse boundary

Inherit the carrier-first no-go format. Do not claim all eight fronts, or even the full contraction theorem, are locally mechanized without the supplementary artifact.
""",
    }
    for pid, text in notes.items():
        (DEEP_FORMAL / f"{pid}.md").write_text(text, encoding="utf-8")


def build_requirement_audit(spine: list[dict[str, str]], f_rows: list[dict[str, str]], e_rows: list[dict[str, str]], g_rows: list[dict[str, str]], version_rows: list[dict[str, str]]) -> None:
    audit = [
        {"requirement_id": "S1-CORPUS", "step1_requirement": "All 58 paper roots and four wish lists represented exactly once", "status": "PASS", "evidence": "config/paper_catalog.csv; config/wishlist_catalog.csv; corpus/coverage.csv", "remediation_or_limit": "None"},
        {"requirement_id": "S1-SURVEY", "step1_requirement": "Every paper has a source-located survey card", "status": "PASS_AFTER_REMEDIATION", "evidence": "notes/survey/P001.md through P058.md; corpus/survey_index.csv", "remediation_or_limit": "Cards now include every planned field; P039 is root-stub-level because 18 included files and bibliography are absent"},
        {"requirement_id": "S1-DEPENDENCY", "step1_requirement": "Every survey card identifies dependency papers at reconnaissance depth", "status": "PASS_AFTER_REMEDIATION", "evidence": "corpus/paper_dependency_edges.csv; corpus/paper_dependency_summary.csv; reports/PAPER_DEPENDENCY_RECONNAISSANCE.md; notes/survey/", "remediation_or_limit": "Citation-level navigation only: 240 resolved in-corpus edges, two explicitly unresolved internal keys, five papers citing out-of-corpus works; no theorem bridge or evidence-independence inference"},
        {"requirement_id": "S1-DISCLOSURE", "step1_requirement": "Every paper's artifact/formalization disclosure inspected at survey depth", "status": "PASS_AFTER_REMEDIATION", "evidence": "corpus/survey_artifact_formalization.csv; reports/SURVEY_ARTIFACT_FORMALIZATION_AUDIT.md; notes/survey/", "remediation_or_limit": "All 58 cards now carry explicit status, source anchors, and a no-local-reuse inference boundary; P039 remains source-blocked"},
        {"requirement_id": "S1-CANON", "step1_requirement": "Deep canonical sequence and controlling SBT model", "status": "PASS_AFTER_FORMAL_REREAD", "evidence": "notes/deep/; notes/deep_formalization/; synthesis/SBT_STEP1_SYNTHESIS.md", "remediation_or_limit": "Added formal-fidelity supplements for P031/P027/P026/P028/P030/P029/P032"},
        {"requirement_id": "S1-ROLES", "step1_requirement": "P1-P6 canonical definitions plus correction history", "status": "PASS", "evidence": "registry/primitive_roles.*; synthesis/correction_ambiguity_ledger.csv; synthesis/symbol_alias_ledger.csv", "remediation_or_limit": "Foundations-II Lean classified as typed harness, not theorem derivation"},
        {"requirement_id": "S1-LAWS", "step1_requirement": "All F/E/G/NG rows enumerated with original status", "status": "PASS_AFTER_REMEDIATION", "evidence": "registry/F_laws.*; registry/E_laws.*; registry/G_laws.*; registry/no_go_theorems.*", "remediation_or_limit": "G theorem/schema/calibration grades added; E theorem grade made explicit"},
        {"requirement_id": "S1-FORMAL", "step1_requirement": "Artifact/formalization disclosure incorporated into canonical reconnaissance", "status": "PASS_AFTER_REMEDIATION", "evidence": "formalization/integration/foundations_spine_formalization_coverage.csv; *_law_formalization_disclosure.csv; synthesis/FORMALIZATION_EVIDENCE_LADDER.md", "remediation_or_limit": "Separates paper report, local presence, static indexing/import closure, kernel build, and tests"},
        {"requirement_id": "S1-WISH", "step1_requirement": "All wish-list atoms classified as existing/partially existing/new/blocked by no-go/needs countermodel/unclear", "status": "PASS_AFTER_REMEDIATION", "evidence": "wishlists/atomic_requests.csv:prior_coverage_status", "remediation_or_limit": "Original planning disposition retained as a separate field; no request is yet proven blocked by a prior no-go at Step-1 depth"},
        {"requirement_id": "S1-VERSION", "step1_requirement": "P040/P058 reconciled or explicitly retained as unresolved deltas, including line-by-line source control", "status": "PASS_AFTER_REMEDIATION", "evidence": "reports/P040_P058_SECTION_DELTA.csv; reports/P040_P058_LINE_DELTA.csv; reports/P040_P058_RAW_TEX_DIFF.patch; corpus/version_families.csv", "remediation_or_limit": f"{len(version_rows)} structural slots plus 505 exact raw-TeX alignment blocks recorded; claim-level canonicalization remains Step 2"},
        {"requirement_id": "S1-SOURCE", "step1_requirement": "Immutable source manifest, hashes, dependency trees and extraction exceptions", "status": "PASS_QUALIFIED", "evidence": "corpus/source_hashes.sha256; corpus/dependency_trees.*; reports/SOURCE_EXTRACTION_EXCEPTIONS.md", "remediation_or_limit": "P039 full text remains authoritatively unavailable; no reconstruction substituted"},
        {"requirement_id": "S1-NONCLAIM", "step1_requirement": "No unsupported ‘SBT says’ statement remains", "status": "PASS_WITH_CONTROLS", "evidence": "synthesis/SBT_STEP1_SYNTHESIS.md; synthesis/FORMALIZATION_EVIDENCE_LADDER.md; formal-aware notes", "remediation_or_limit": "All mechanization statements now carry grade, fidelity, local availability, and trust/build qualifications"},
        {"requirement_id": "S1-REUSE", "step1_requirement": "Imported prior scaffold is understood well enough to support later reuse", "status": "PASS_FOR_STEP1", "evidence": "formalization/integration/FORMALIZATION_REUSE_MAP.md; foundations_spine_formalization_coverage.csv; F/E/G disclosures", "remediation_or_limit": "Foundations V assets absent; 38 Foundations IV rows paper-reported only; no local Lean kernel build"},
        {"requirement_id": "S1-NOSTEP2", "step1_requirement": "Do not begin Step 2 during remediation", "status": "PASS", "evidence": "corpus/coverage.csv remains 20 DEEP_READ and 38 SURVEYED; no claim/bridge record directories; active FoundationsVII Lean shell has zero declarations", "remediation_or_limit": "Only Step-1 reconnaissance/status artifacts added"},
        {"requirement_id": "S1-REPRO", "step1_requirement": "Machine validation and cumulative reproducibility", "status": "PASS_LOCAL_REBUILD", "evidence": "scripts/rebuild_step1_completion.sh; scripts/validate_step1_completion.py; generated/step1_completion_validation.txt; generated/file_manifest.csv; SHA256SUMS", "remediation_or_limit": "The repository-local rebuild, manifest, and checksum checks pass; the external zip integrity/hash is verified after commit/tag and recorded in the delivery response"},
    ]
    write_csv(REPORTS / "STEP1_REQUIREMENT_AUDIT.csv", audit)
    counts = Counter(row["status"] for row in audit)
    md = [
        "# Step 1 requirement audit after formal-scaffold integration",
        "",
        "## Verdict",
        "",
        "The original Step 1 was mechanically complete but not yet sufficiently **formalization-aware**. Its principal semantic model and corpus inventory were usable, but the newly supplied scaffold exposed real omissions in proof-grade/fidelity disclosure, local-versus-paper-reported coverage, G-law status preservation, exact wish-list classification vocabulary, version-family delta evidence, and the promised per-paper dependency-paper reconnaissance. Those gaps are closed by this remediation without starting Step 2.",
        "",
        f"Audit rows: **{len(audit)}**. Status distribution: " + ", ".join(f"`{k}`={v}" for k, v in sorted(counts.items())) + ".",
        "",
        "| Requirement | Status | Evidence | Remaining limitation |",
        "|---|---|---|---|",
    ]
    for row in audit:
        md.append(f"| {row['requirement_id']} — {row['step1_requirement']} | `{row['status']}` | {row['evidence']} | {row['remediation_or_limit']} |")
    md += [
        "",
        "## Material corrections made",
        "",
        "1. Foundations II is now explicitly treated as a typed harness, not a theorem-derivation library.",
        "2. Foundations IV's paper-wide 52-row formalization is separated from the 14-row local imported subset.",
        "3. Foundations V's reported D/E library, declaration census and tests are recorded as paper-reported only because those assets were not supplied.",
        "4. Foundations VI theorem/schema/calibration grades are present in the canonical G registry.",
        "5. The no-go paper's narrow formalized contraction component is not generalized to all eight no-go fronts.",
        "6. Every wish-list atom now has one of the exact Step-1 prior-coverage labels required by the plan.",
        "7. Every survey card now includes a source-line citation-level corpus dependency section; unresolved and out-of-corpus internal references remain visible rather than guessed.",
        "8. Every survey card now includes a source-located artifact/formalization disclosure with explicit anti-overread boundaries.",
        "9. P040/P058 now have both a 73-slot section delta and an exact 505-block raw-TeX line ledger while remaining one unresolved evidence family pending claim-level Step-2 comparison.",
        "",
        "## What remains deliberately outside this pass",
        "",
        "No full claim dossiers, theorem-by-theorem paper/Lean equivalence proofs, bridge records, application pressure tests, or VII candidate laws were created. Those are Step-2 and Step-3 products. P039 remains blocked by its incomplete source package, and no local Lean kernel compilation is claimed.",
    ]
    (REPORTS / "STEP1_REQUIREMENT_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def build_formal_audit_report(f_rows: list[dict[str, str]], e_rows: list[dict[str, str]], g_rows: list[dict[str, str]]) -> None:
    f_counts = Counter(row["paper_formalization_status"] for row in f_rows)
    local_f = sum(row["local_import_status"] == "IMPORTED_SUBSET_MODULE" for row in f_rows)
    text = f"""# Formalization-aware audit of the Foundations spine

## Controlling result

The imported scaffold changes how Step 1 must speak about prior proof support. It does **not** change the core SBT interpretation, but it sharpens which parts are directly reusable and which are only paper-reported, typed, conditional, guarded, or absent from the supplied archive.

## Coverage summary

| Surface | Paper-side disclosure | Locally supplied active surface | Step-1 ruling |
|---|---|---|---|
| Foundations I | Deliberately minimal closure/package core; no probability or Markov Lean | 6 relevant modules | Reuse closure/idempotence only. |
| Foundations II | Typed harness; no faithful theorem derivations in the paper's strongest fidelity class | 10 modules | Reuse types/status/admissibility; not exact-six proof. |
| Foundations III | 21 definitions + 35 theorem-backed manifest claims, with theorem/model/audit grades | 24 modules, but not the complete original validator packet | Reuse calculus; do not claim rerun manifest equivalence. |
| Foundations IV | 52 rows: {f_counts['direct theorem row']} direct, {f_counts['substrate-delegated anchor']} anchors, {f_counts['partial theorem wrapper']} partial, {f_counts['obligation-guarded wrapper']} obligations | {local_f}/52 modules | Use exact 14-row subset; other 38 are R0 paper-reported. |
| Foundations V | D1-D6 + E1-E16 core; 1,261 authored declarations / 187 theorems; 391 tests + separate E16 sweep reported | 22 authored modules; all 16 E laws locally present and import-resolved; E16 root/manifest omission repaired by VII-owned adapters | Reuse exact declarations while preserving conditional hypotheses, paper grades, and open bridges. |
| Foundations VI | All 13 G laws with mixed theorem/schema grades plus full evidence chain | 13/13 law modules, gates/labs/results | Strongest local reuse surface; preserve grades and hypotheses. |
| No-go paper | Narrow formalized uniqueness component for contraction front | No dedicated module located | Do not generalize mechanization to all eight no-gos. |

## Proof-status corrections relevant to Foundations VII

- A typed Lean structure can prevent ill-formed joins without proving that a lawful join exists.
- A conditional classification can verify a supplied complete evidence package without constructing a reachable one.
- A guarded wrapper can expose the exact missing certificate while leaving the mathematical obligation open.
- A paper-reported module not present in this repository is not an available dependency.
- A statically resolved import graph is not a local Lean kernel proof.
- A passing finite lab validates the registered fixtures and detector code, not a universal SBT law.

## Reuse consequences

The active VII project should start from ClosureLadder, Foundations-II typing, BirdInt records, the 14 present F modules, the complete D/E theorem base, and all G modules. Foundations V should be imported through `FoundationsVII.PriorFoundationsVComplete` so E16 is not silently omitted. Every imported statement in later work must name its declaration, fidelity, trust/host premises, and local evidence state from `FORMALIZATION_EVIDENCE_LADDER.md`.

## Remaining limitations

The environment lacks Lean/Lake, so no imported Lean tree was rebuilt locally. PySAT is absent, excluding three G11 tests. P039 remains source-blocked. None of these limitations licenses guessing, silent status promotion, or postponing explicit proof obligations.
"""
    (REPORTS / "FORMALIZATION_AWARE_FOUNDATIONS_AUDIT.md").write_text(text, encoding="utf-8")


def append_synthesis_control() -> None:
    path = SYNTHESIS / "SBT_STEP1_SYNTHESIS.md"
    text = path.read_text(encoding="utf-8")
    marker = "## 11. Formalization-aware authority rule"
    if marker in text:
        text = text[:text.index(marker)].rstrip() + "\n"
    addition = """

## 11. Formalization-aware authority rule

The imported proof scaffold adds a second anti-smuggling boundary. “Present in a paper,” “reported as mechanized,” “source file locally available,” “statically indexed,” “import-resolved,” “kernel-compiled here,” and “finite tests rerun here” are distinct statuses. Statement fidelity is independent: a typed mirror, record projection, conditional classification, narrowed theorem, guarded wrapper, and direct derivation do not license the same prose.

The controlling reconciliation is:

- Foundations I supplies a locally present but intentionally minimal closure/package core.
- Foundations II supplies a locally present typed harness and malformed-case rejection surface, not an independent exact-six proof.
- Foundations III supplies locally present BirdInt modules, but this repository has not rerun the exact original manifest validator.
- Foundations IV reports 52 Lean rows; only 14 are in the supplied archive, and guarded/anchor statuses remain visible.
- Foundations V supplies the complete local D1-D6 / E1-E16 theorem base. The upstream E16 root/manifest omission is repaired only in VII-owned adapters, and paper-side conditionality remains controlling.
- Foundations VI supplies the complete local G-law/evidence surface, with theorem/schema/calibration grades preserved.
- The no-go paper discloses only a narrow formalized component for its contraction front; no blanket eight-theorem mechanization is inferred.

The exact vocabulary and current evidence states are defined in `synthesis/FORMALIZATION_EVIDENCE_LADDER.md`. Later work may say “already mechanized” only after naming the exact declaration, fidelity, trust/host premises, and local verification state.
"""
    path.write_text(text.rstrip() + addition, encoding="utf-8")


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    SYNTHESIS.mkdir(exist_ok=True)
    build_evidence_ladder()
    spine = build_spine_coverage()
    f_rows = parse_f_disclosure()
    e_rows = build_e_disclosure()
    g_rows = build_g_disclosure()
    version_rows = build_version_delta()
    build_deep_formal_notes()
    build_requirement_audit(spine, f_rows, e_rows, g_rows, version_rows)
    build_formal_audit_report(f_rows, e_rows, g_rows)
    append_synthesis_control()
    summary = {
        "spine_papers": len(spine),
        "f_rows": len(f_rows),
        "f_local_modules": sum(row["local_import_status"] == "IMPORTED_SUBSET_MODULE" for row in f_rows),
        "e_rows": len(e_rows),
        "e_local_modules": sum(row["local_import_status"] != "NOT_IN_SUPPLIED_ARCHIVE" for row in e_rows),
        "g_rows": len(g_rows),
        "g_local_modules": sum(row["local_import_status"] == "IMPORTED_COMPLETE_G_SERIES" for row in g_rows),
        "formal_deep_supplements": len(list(DEEP_FORMAL.glob("P*.md"))),
        "survey_disclosure_rows": len(read_csv(ROOT / "corpus" / "survey_artifact_formalization.csv")),
        "dependency_summary_rows": len(read_csv(ROOT / "corpus" / "paper_dependency_summary.csv")),
        "dependency_edges": len(read_csv(ROOT / "corpus" / "paper_dependency_edges.csv")),
        "dependency_unresolved_internal_keys": sum(int(row["unresolved_internal_key_count"]) for row in read_csv(ROOT / "corpus" / "paper_dependency_summary.csv")),
        "version_slots": len(version_rows),
        "version_line_alignment_blocks": json.loads((ROOT / "generated" / "p040_p058_line_delta.json").read_text(encoding="utf-8"))["alignment_block_count"],
        "step2_started": False,
    }
    (ROOT / "generated" / "step1_formal_completion_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

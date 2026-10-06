# Step 1 requirement audit after formal-scaffold integration

## Verdict

The original Step 1 was mechanically complete but not yet sufficiently **formalization-aware**. Its principal semantic model and corpus inventory were usable, but the newly supplied scaffold exposed real omissions in proof-grade/fidelity disclosure, local-versus-paper-reported coverage, G-law status preservation, exact wish-list classification vocabulary, version-family delta evidence, and the promised per-paper dependency-paper reconnaissance. Those gaps are closed by this remediation without starting Step 2.

Audit rows: **15**. Status distribution: `PASS`=3, `PASS_AFTER_FORMAL_REREAD`=1, `PASS_AFTER_REMEDIATION`=7, `PASS_FOR_STEP1`=1, `PASS_LOCAL_REBUILD`=1, `PASS_QUALIFIED`=1, `PASS_WITH_CONTROLS`=1.

| Requirement | Status | Evidence | Remaining limitation |
|---|---|---|---|
| S1-CORPUS — All 58 paper roots and four wish lists represented exactly once | `PASS` | config/paper_catalog.csv; config/wishlist_catalog.csv; corpus/coverage.csv | None |
| S1-SURVEY — Every paper has a source-located survey card | `PASS_AFTER_REMEDIATION` | notes/survey/P001.md through P058.md; corpus/survey_index.csv | Cards now include every planned field; P039 is root-stub-level because 18 included files and bibliography are absent |
| S1-DEPENDENCY — Every survey card identifies dependency papers at reconnaissance depth | `PASS_AFTER_REMEDIATION` | corpus/paper_dependency_edges.csv; corpus/paper_dependency_summary.csv; reports/PAPER_DEPENDENCY_RECONNAISSANCE.md; notes/survey/ | Citation-level navigation only: 240 resolved in-corpus edges, two explicitly unresolved internal keys, five papers citing out-of-corpus works; no theorem bridge or evidence-independence inference |
| S1-DISCLOSURE — Every paper's artifact/formalization disclosure inspected at survey depth | `PASS_AFTER_REMEDIATION` | corpus/survey_artifact_formalization.csv; reports/SURVEY_ARTIFACT_FORMALIZATION_AUDIT.md; notes/survey/ | All 58 cards now carry explicit status, source anchors, and a no-local-reuse inference boundary; P039 remains source-blocked |
| S1-CANON — Deep canonical sequence and controlling SBT model | `PASS_AFTER_FORMAL_REREAD` | notes/deep/; notes/deep_formalization/; synthesis/SBT_STEP1_SYNTHESIS.md | Added formal-fidelity supplements for P031/P027/P026/P028/P030/P029/P032 |
| S1-ROLES — P1-P6 canonical definitions plus correction history | `PASS` | registry/primitive_roles.*; synthesis/correction_ambiguity_ledger.csv; synthesis/symbol_alias_ledger.csv | Foundations-II Lean classified as typed harness, not theorem derivation |
| S1-LAWS — All F/E/G/NG rows enumerated with original status | `PASS_AFTER_REMEDIATION` | registry/F_laws.*; registry/E_laws.*; registry/G_laws.*; registry/no_go_theorems.* | G theorem/schema/calibration grades added; E theorem grade made explicit |
| S1-FORMAL — Artifact/formalization disclosure incorporated into canonical reconnaissance | `PASS_AFTER_REMEDIATION` | formalization/integration/foundations_spine_formalization_coverage.csv; *_law_formalization_disclosure.csv; synthesis/FORMALIZATION_EVIDENCE_LADDER.md | Separates paper report, local presence, static indexing/import closure, kernel build, and tests |
| S1-WISH — All wish-list atoms classified as existing/partially existing/new/blocked by no-go/needs countermodel/unclear | `PASS_AFTER_REMEDIATION` | wishlists/atomic_requests.csv:prior_coverage_status | Original planning disposition retained as a separate field; no request is yet proven blocked by a prior no-go at Step-1 depth |
| S1-VERSION — P040/P058 reconciled or explicitly retained as unresolved deltas, including line-by-line source control | `PASS_AFTER_REMEDIATION` | reports/P040_P058_SECTION_DELTA.csv; reports/P040_P058_LINE_DELTA.csv; reports/P040_P058_RAW_TEX_DIFF.patch; corpus/version_families.csv | 73 structural slots plus 505 exact raw-TeX alignment blocks recorded; claim-level canonicalization remains Step 2 |
| S1-SOURCE — Immutable source manifest, hashes, dependency trees and extraction exceptions | `PASS_QUALIFIED` | corpus/source_hashes.sha256; corpus/dependency_trees.*; reports/SOURCE_EXTRACTION_EXCEPTIONS.md | P039 full text remains authoritatively unavailable; no reconstruction substituted |
| S1-NONCLAIM — No unsupported ‘SBT says’ statement remains | `PASS_WITH_CONTROLS` | synthesis/SBT_STEP1_SYNTHESIS.md; synthesis/FORMALIZATION_EVIDENCE_LADDER.md; formal-aware notes | All mechanization statements now carry grade, fidelity, local availability, and trust/build qualifications |
| S1-REUSE — Imported prior scaffold is understood well enough to support later reuse | `PASS_FOR_STEP1` | formalization/integration/FORMALIZATION_REUSE_MAP.md; foundations_spine_formalization_coverage.csv; F/E/G disclosures | Foundations V assets absent; 38 Foundations IV rows paper-reported only; no local Lean kernel build |
| S1-NOSTEP2 — Do not begin Step 2 during remediation | `PASS` | corpus/coverage.csv remains 20 DEEP_READ and 38 SURVEYED; no claim/bridge record directories; active FoundationsVII Lean shell has zero declarations | Only Step-1 reconnaissance/status artifacts added |
| S1-REPRO — Machine validation and cumulative reproducibility | `PASS_LOCAL_REBUILD` | scripts/rebuild_step1_completion.sh; scripts/validate_step1_completion.py; generated/step1_completion_validation.txt; generated/file_manifest.csv; SHA256SUMS | The repository-local rebuild, manifest, and checksum checks pass; the external zip integrity/hash is verified after commit/tag and recorded in the delivery response |

## Material corrections made

1. Foundations II is now explicitly treated as a typed harness, not a theorem-derivation library.
2. Foundations IV's paper-wide 52-row formalization is separated from the 14-row local imported subset.
3. Foundations V's reported D/E library, declaration census and tests are recorded as paper-reported only because those assets were not supplied.
4. Foundations VI theorem/schema/calibration grades are present in the canonical G registry.
5. The no-go paper's narrow formalized contraction component is not generalized to all eight no-go fronts.
6. Every wish-list atom now has one of the exact Step-1 prior-coverage labels required by the plan.
7. Every survey card now includes a source-line citation-level corpus dependency section; unresolved and out-of-corpus internal references remain visible rather than guessed.
8. Every survey card now includes a source-located artifact/formalization disclosure with explicit anti-overread boundaries.
9. P040/P058 now have both a 73-slot section delta and an exact 505-block raw-TeX line ledger while remaining one unresolved evidence family pending claim-level Step-2 comparison.

## What remains deliberately outside this pass

No full claim dossiers, theorem-by-theorem paper/Lean equivalence proofs, bridge records, application pressure tests, or VII candidate laws were created. Those are Step-2 and Step-3 products. P039 remains blocked by its incomplete source package, and no local Lean kernel compilation is claimed.

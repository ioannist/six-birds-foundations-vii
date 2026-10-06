# Changelog

## v2 stage 1 — semantic Lean results (2026-09-26)

- New stage `v2-semantics`, owned paths `formalization/lean/FoundationsVII/Semantics/` and `formalization/lean/SEMANTICS_REPORT.md`. Acceptance gates: the kernel build passes, the new code has no sorry, axiom, admit or native_decide, and an independent statement-fidelity review is CLEAN. The review took two rounds, recorded in six-birds-theory-extended `docs/plans/reviews/FVII_LEAN_S1_round{1,2}.md`.
- `Semantics/Rewriting.lean`: Newman's lemma (axiom-free), uniqueness of normal forms, a finite local-confluence decision procedure built from finite reachability, and the four-state counterexample showing that termination is needed.
- `Semantics/Admission.lean`: prerequisite admission as a terminating rewriting system. Commuting admissions reach a unique fixed point, and a disabling guard gives two distinct fixed points.
- `Semantics/Join.lean`: factorization on the reached image and the split-pair criterion. A strict observable factors through neither parent nor their pairing; the concrete example is the three-Boolean cube. A certificate bridge evaluates the `AntiProductWitness` flags from semantic predicates.
- No existing declaration was changed. `FoundationsVII/All.lean` only adds the three imports.

## Public-repository preparation — 2026-09-04

- Added a public-facing repository guide for the completed paper and FVII-SCI-05 release.
- Moved operational prompts, raw discovery material, build diagnostics, superseded templates, and
  original supplied archives out of Git tracking while retaining them locally.
- Kept curated imported scaffolds, archive digests, upstream identities, and file-level manifests.
- Updated CI and validation documentation to the final five-phase replay surface.

## vii-science-final — FVII-SCI-05 final science closure

- Closed all 18 object records, 36 candidates, 20 formalization targets, 11 no-go fronts, and 15 decision points.
- Added 21 nonredundant cross-family Lean corollaries and an executable terminal-release registry.
- Added eleven global bounded finite envelopes: 86,912 raw, 84,864 canonical, 21,081 accepted, and 63,783 rejected cases.
- Retained 33 minimized final witnesses and 12 cross-family controls; replayed all 24 scenarios and 27 named countermodels.
- Built canonical final registries for objects, definitions, theorems, no-gos, corollaries, countermodels, finite assays, adapters, decisions, dependencies, trust, candidates, and targets.
- Added the complete final `#print axioms` surface, external Lean replay script, static source audit, final validator, deterministic rebuild, and final release reports.
- Removed an obsolete unimported Phase-5 finite draft and restricted the public corollary layer to the 21 terminally registered consequences.
- Preserved the imported Foundations V/VI scaffolds byte-for-byte and performed no paper or paper-preparation work.
- Recorded the owner-authorized external Lean replay boundary without claiming kernel elaboration or axiom-free status.

## vii-science-04 — execute FVII-SCI-04 enablement, descent, dynamics, holonomy, and arrow

- Added source-typed enablement attribution with hidden-executor rejection and honest bridge-refinement stability.
- Added an exact declared-boundary endogeny criterion with theorist/observer anti-smuggling controls and accounted-environment positive control.
- Added relation/layer/participant birth classification, closure-agency separation, inherited four-class signatures, objecthood, closure-survival, and reachable-generator obligations.
- Added typed upward/downward/peer transmission, descent commuting squares, loss/ambiguity/source/budget fidelity, and the no-creation-by-pure-downward-selection law.
- Added constructive enablement-without-descent and necessary-but-insufficient enablement countermodels.
- Added conditional enablement-chain composition, associativity at the declared data level, accumulated cost and residual debt, order sensitivity, and a no-transitive-causation-without-certificate boundary.
- Added finite critical-pair confluence criteria, positive/nonconfluent controls, seed dependence, and a one-square-is-not-global-confluence result.
- Added interaction holonomy, zero-arrow and driven-arrow controls, reversal separation, cross-time synchronization/partial-order witnesses, and clock-reparameterization invariance.
- Closed NGVII-10: holonomy alone does not license an arrow; a separately certified driven path is an explicit escape.
- Terminally deferred the complete primitive algebra under an exact reopen gate while landing a small associative resource-delta fragment with identity.
- Closed ten candidates, eight formalization targets, and five dynamic representation decisions at their declared Phase-4 scope.
- Added twelve independently enumerated bounded families totaling 55,168 raw/canonical, 14,832 accepted, and 40,336 rejected cases, retaining 32 canonical witnesses.
- Replayed 9/9 assigned scenarios and 8/8 assigned countermodels; all 62 cumulative Python tests pass.
- Indexed 268 public Phase-4 declarations, including 135 theorem/lemma/corollary declarations, with exact source hashes, candidate traces, finite controls, and generated axiom commands.
- Added deterministic rebuild, static Lean audit, 31-check acceptance validation, cumulative external Lean replay automation, and complete formal/finite/decision reports.
- Preserved inherited scaffolds and Phase-1/2/3 science bodies unchanged; did not execute FVII-SCI-05 or create any paper asset.
- Recorded local Lean/Lake unavailability truthfully; kernel, axiom, and differential replay remain externally executable and nonblocking by owner authorization.

## vii-science-03 — execute FVII-SCI-03 contact, strict join, obstruction, and certified non-interaction

- Added witnessed contact and peer-transport machinery that preserves destination ownership and provenance without equating transport with composite formation or join.
- Added proof-carrying composite objecthood and parent-embedding witnesses, join-entry normal form, and an evidence-axis status calculus.
- Added strict-join certificates separating contact, objecthood, retention, anti-product novelty, source independence, payment/zero-cost certification, audit, and directionality.
- Added anti-product, relabeling, scheduling, and coarsening controls; strictness remains distinct from objecthood, retention, and directionality.
- Added source-lineage and honest-bridge discipline, typed join-cost ledgers, observer pricing, and a finite live-join capacity result.
- Added full/partial/erased parent retention, refinement preserve/strengthen/weaken/destroy cases, and a no-unconditional-monotonicity result.
- Rejected unconditional product/pullback/pushout reduction while retaining explicitly checked special-case categorical representation theorems.
- Rejected a universal conserved contact degree on the present evidence while retaining typed coordinate ledgers and scoped exact invariants.
- Added coverage-qualified certified non-interaction with explicit outside-family escapes.
- Added append-only residual transitions, dissolution records, join-created cross-term needles, and obstruction nonmonotonicity controls.
- Closed NGVII-02, NGVII-06, NGVII-07, NGVII-08, and NGVII-09 at source level with exact scopes, escape theorems, and finite controls.
- Closed 13 assigned candidates, 10 formalization-target rulings, and eight representation/governance decisions at their declared Phase-3 scope.
- Added eleven independent bounded families totaling 141,112 raw / 73,528 canonical / 34,532 accepted / 38,996 rejected cases and retained 27 canonical witnesses.
- Replayed 12/12 assigned scenarios and 14/14 assigned countermodels; all 48 cumulative Python tests pass.
- Indexed 363 public Phase-3 declarations, including 183 theorem/lemma/corollary declarations, with statement hashes, source traces, finite controls, and generated axiom commands.
- Added deterministic rebuild, 36-check acceptance validation, cumulative external Lean replay automation, and complete science/Lean/finite/decision reports.
- Preserved inherited scaffolds and Phase-1/2 science bodies unchanged; did not execute Phases 4–5 or create any paper asset.
- Recorded local Lean/Lake unavailability truthfully; kernel, axiom, and differential replay remain externally executable and nonblocking by owner authorization.

## vii-science-02 — execute FVII-SCI-02 admission, access, and provenance

- Added the Phase-2 accessible-domain normal form and explicit non-implication witnesses across expressibility, presence, exposure, recoverability, admissibility, reachability, and occurrence.
- Added typed admission, expiry, revocation, retraction, and rollback operations with source, budget, guard, audit, and append-only history obligations.
- Added lawful path composition and exact reachability-witness replay without collapsing soundness, executability, reachability, firing, or occurrence.
- Proved source-level bootstrap obstruction for closed declared regimes without an admitted seed or reachable generator, together with admitted-seed, reachable-generator, and open-family external-provision escapes.
- Added neutral provisioning, temporal-precedence, preregistration/task-blindness/outcome-independence, expiry, refund, anti-retrospective, and anti-source-laundering assets.
- Added common-origin/shared-access/source-independence separation and total-lens non-transfer to partial self-owned targets without a certified adapter.
- Added horizon-qualified negative-force and observer-occupancy/failed-admission settlement assets.
- Closed NGVII-01, NGVII-03, NGVII-04, NGVII-05, and NGVII-11 at source level with exact scopes and positive controls.
- Added nine independent bounded families totaling 1,332 raw / 1,076 canonical / 470 accepted / 606 rejected cases and retained 15 canonical witnesses.
- Replayed 10/10 assigned scenarios and 9/9 assigned countermodels; all 34 cumulative Python tests pass.
- Indexed 237 public Phase-2 declarations, including 130 theorem/lemma/corollary declarations, with statement hashes, asset IDs, candidate/no-go/target traces, and generated axiom commands.
- Added deterministic rebuild, 31-check acceptance validation, cumulative external Lean replay automation, and complete science/Lean/finite reports.
- Preserved inherited scaffolds and Phase-1 fixtures unchanged; did not execute Phases 3–5 or create any paper asset.
- Recorded local Lean/Lake unavailability truthfully; kernel and differential replay remain externally executable and nonblocking by owner authorization.

## vii-science-01 — execute FVII-SCI-01 typed kernel and reference world

- Added all fifteen VII-owned canonical Lean structures and the supporting identifier, grade, audit, ledger, protocol, and structural theorem surface.
- Added stable `FVII-DEF-*` and `FVII-THM-*` science asset IDs for every public VII declaration.
- Added twenty narrow formalization-target adapter modules and a thirty-row exact inherited-declaration ledger without modifying the imported Foundations V/VI trees.
- Closed the Phase-1 source assets for C020 bridge discipline, C023 negative-result quantifiers, C024 claim/evidence-grade discipline, and C025 finite detector contract.
- Migrated all 24 frozen scenarios and 27 countermodels to canonical JSON under the closed `FVII-SCI-01.3` schema and independent Lean/Python finite semantics.
- Added 25 Python protocol/regression and schema-mutation tests; all 24 scenario and 27 countermodel expectations pass.
- Added declaration/trust, candidate, fixture, decision, adapter, statement-hash, validation, and external replay reports.
- Removed five duplicate ledger declarations found during the pre-delivery source audit and added raw-source declaration uniqueness plus registry-parity checks.
- Preserved zero VII-owned `sorry`, `admit`, `axiom`, `opaque`, or `unsafe` declarations by source audit.
- Recorded the owner-authorized external Lean replay boundary; no local kernel build or Lean/Python runtime agreement is claimed.
- Added a deterministic Phase-1 rebuild and exact external Lean replay script.
- Did not execute FVII-SCI-02 through FVII-SCI-05 and created no paper asset.

## `vii-science-plan-v1` — plan the complete Foundations VII formal-science asset program

- Added a five-phase cumulative execution plan for the VII Lean kernel, dual finite reference model, admission/access theorem family, contact/join theorem family, enablement/dynamics theorem family, and final science closure release.
- Routed all 36 candidates, 20 formalization targets, 18 objects, 11 no-go fronts, 24 scenarios, 27 countermodels, and 15 decision points to exact phases.
- Added proof/trust grades, stable science asset classes, a narrow inherited-adapter architecture, toy-model evidence rules, per-phase acceptance gates, and a final release contract.
- Required actual Lean 4.28.0 kernel builds, zero new proof holes/axioms, theorem-level `#print axioms`, dual Python/Lean finite semantics, and deterministic fresh-extraction releases.
- Added a truthful closure policy for false, conditional, finite-only, and deferred candidates.
- Explicitly excluded manuscript drafting and all paper-writing preparation.
- Added a 33-check plan validator confirming exact Step-3 coverage and that no VII Lean or toy-model implementation was started.

## `read-step-03` — complete Foundations VII pre-authoring readiness dossier

- Re-read all 58 supplied papers against the VII dependency graph while preserving exact Step-2 claim IDs, source locations, grades, and P039/P040/P058 boundaries.
- Added 30 scope-inheritance rulings and final adjudication of all 130 atomic wish-list requests across seven explicit dispositions.
- Specified an 18-record minimal object model and 36 candidate definition/schema/theorem/no-go/decision dossiers, each with typing, proof obligations, detector/null/falsifier, finite controls, countermodels, nonclaims, and exact source traces.
- Established the scoped scientific center as a proof-carrying admission/contact calculus for partially accessible, source-typed theory packages rather than a universal interaction algebra.
- Added a 24-scenario Two-Theory World; the independent evaluator passes 24/24 expected statuses and 29/29 assertions while remaining explicitly finite and non-universal.
- Added 27 countermodels, 11 scoped candidate no-go fronts, a 12-node later chapter DAG, 30 red lines, and 15 evidence-gated decision points.
- Mapped 20 future formalization targets through 30 exact reuse records to 29 unique inherited Lean declarations without changing imported sources or introducing any Foundations VII declaration.
- Added 3,166 candidate-to-source trace rows and a closed 1,851-node / 5,969-edge dependency graph.
- Added Step-3 schemas, deterministic builders, finite replay, requirement audit, and executable exit validator.
- Canonicalized the packaged Git index from `HEAD`, making the cumulative archive byte-reproducible even after extraction under a different filesystem path.
- Preserved paper drafting, theorem proof, and new Lean implementation as later work; categorical reduction, a complete primitive algebra, and a conserved contact degree remain explicit deferrals.

## `read-step-02` — complete claim corpus and cross-paper bridge atlas

- Read all 58 supplied paper roots at claim/proof/nonclaim depth, subject to the recorded P039 missing-source boundary.
- Established one canonical `Pxxx-Cnnnn` claim-ID space with 2,821 source-located records and complete per-paper JSONL/Markdown dossiers.
- Closed abstract extraction across all 58 roots, including the section-form P023 abstract, and promoted 48 explicit abstract nonclaim/scope/open clauses into typed component records rather than hiding them inside composite summaries.
- Added cross-paper registries for definitions, theorem-family claims, nonclaims/scope boundaries, open problems, examples/carriers, source provenance, and proof/Lean coverage.
- Built 374 typed bridges: 240 paper invocations, 45 source-audited named-law imports covering 217 accepted occurrences, and 89 complete F/E/G/no-go reuse contracts.
- Added an occurrence-level audit of 2,022 candidate F/E/G references so local figure, experiment, workflow, table, and future-work labels cannot masquerade as imported laws.
- Added complete no-go scope/escape records, 20 invalid-transfer guardrails, six typed conflict records, and a 223-row P040/P058 claim delta under a non-independence ruling.
- Added 14 interaction/access/enablement matrices, 14 application pressure tests, and a closed 3,040-node / 35,276-edge typed graph. Forty-one recall-oriented lexical law-tag edges were deliberately excluded because they lacked an independently audited named-law bridge.
- Linked all 130 wish-list atoms to supporting claims, counterclaims/scope boundaries, open obligations, numbered laws/no-gos, and bridge records.
- Aligned the claim body to the inherited 123-module / 793-theorem Foundations I–VI Lean spine without changing imported Lean or introducing a Foundations VII declaration.
- Distinguished paper-reported declarations from locally imported matched declarations, correcting the 38 Foundations IV rows whose paper-side formal assets are not present in the supplied local scaffold.
- Added deterministic builders, a 16-row requirement audit, and a 42-check Step-2 exit validator.
- Preserved Step 3 as unstarted.

## read-step-01-complete-formal-spine — import Foundations V and close the prior-proof base

- Embedded the complete supplied Foundations V/cognition archive, its SHA-256, and upstream commit `d548b834481ffe9160194907df61e6e247defc8e`.
- Imported a curated 372-file, byte-exact Foundations V scaffold containing every Lean source plus theorem ledger, manifests, gates, examples, sweeps, labs, tests, traceability, and CI assets.
- Indexed 70 archive modules / 1,758 declarations and the exact 22-module authored surface / 1,261 declarations / 187 theorems, with zero unresolved imports, `sorry`, `admit`, axiom, or opaque declarations.
- Established local coverage for all D1–D6 definitions and E1–E16 laws; preserved the shared E6/E9 module and paper-side conditional/open boundaries.
- Reconciled the upstream 1,141-row declaration manifest against source and added the 120 already-landed E16 declarations to a VII-owned 1,261-row completed manifest.
- Added `PriorFoundationsVComplete`, a declaration-free import wrapper that repairs the upstream root's sole authored-module omission (E16) without modifying upstream source.
- Verified that the V and VI vendored Foundations III copies are byte-identical and built a deduplicated active index of 123 modules, 2,587 declarations, 793 theorem declarations, and 297 resolved imports.
- Replayed the available V runtime baseline: 202 Python files compile, 317 non-E15 tests pass, and the E16 sweep passes 69/69 comparisons; recorded the 74-test E15 file's 900-second replay limit separately.
- Updated the Step-1 synthesis, deep P030 supplement, F/E/G coverage, reuse map, cumulative Lake wiring, rebuild path, and validators.
- Added ADR-0009 and preserved the no-Step-2 boundary: the active VII shell still contains zero declarations.

## read-step-01-formal-aware-completion — audit and close Step 1 against the imported proof scaffold

- Re-audited the original Step-1 contract after importing the Foundations VI/Collatz theorem, Lean, gate, and lab scaffold.
- Added seven formalization-aware rereads for Foundations I–VI and the no-go paper.
- Added a three-axis formalization evidence ladder separating paper grade, statement fidelity, and local evidence state.
- Added complete F/E/G paper-versus-local disclosure matrices: 52 F rows with 14 local modules, 16 E rows with zero local modules, and all 13 graded G rows with local evidence chains.
- Corrected the G registry to preserve theorem, schema, split, and calibration-anchored grades; made E theorem grade explicit.
- Added a dedicated artifact/formalization disclosure section to all 58 survey cards and a 58-row audit index.
- Added source-located corpus-paper dependency reconnaissance to all 58 survey cards: 240 unique in-corpus citation edges, an auditable citation-key map, explicit unresolved/out-of-corpus references, and a strict citation-is-not-proof-dependency boundary.
- Reclassified all 130 wish-list atoms with the exact original Step-1 vocabulary and marked 17 countermodel obligations.
- Added a 73-slot P040/P058 structural delta plus an exact 505-block raw-TeX line alignment and 3,240-line unified diff, while retaining the family as unresolved pending Step-2 theorem/claim comparison.
- Added ADR-0008, a 15-row requirement audit, a 26-check completion validator, and a cumulative rebuild script.
- Preserved the no-Step-2 boundary: coverage remains 20 `DEEP_READ` / 38 `SURVEYED`, no claim or bridge corpus exists, and the VII Lean shell has zero declarations.

## read-prestep-02-formal-scaffold — ingest prior proof and lab infrastructure

- Embedded the complete supplied `six-birds-collatz_v19.zip`, its SHA-256, and upstream commit `220b45879d8e63f1a75573145e0be6bb3f52567c`.
- Imported a curated 282-file, byte-exact Foundations VI scaffold containing the theorem ledger, design/landing protocol, formalization notes and manifests, complete Lean and lab trees, paper source, CI recipe, and dependency audit.
- Preserved the imported subtree as immutable and recorded all exclusions and intended uses.
- Indexed 74 Lean modules, 1,106 lexical declarations, 125 resolved import edges, one inherited axiom, five opaque constants, and zero `sorry`/`admit`.
- Mapped 14 mechanized F-law modules, all 13 G-law modules, and the absence of a dedicated E-series library in this archive.
- Added a 13-row G-law traceability map connecting theorem prose, Lean, gates, examples, labs, tests/results, and paper source.
- Added an active Foundations VII Lake import shell over the prior libraries with zero VII declarations.
- Added reproducible import/index/baseline/validation scripts and a passing 13-check pre-Step-2 validator.
- Extended the claim and bridge templates/schemas with exact formalization, statement-delta, trust-base, adapter, elaboration, and lab-evidence fields for the later Step-2 pass.
- Recorded local environment limits: 62 tests pass; three PySAT tests and Lean 4.28.0 compilation could not be run here.
- Did not begin Step 2.

## read-step-01 — canonicalize and map

- Froze the supplied Foundations VII archive inside the persistent repository and recorded SHA-256 provenance.
- Inventoried 58 paper roots, 85 frozen source files, and all dependency closures.
- Created 58 source-located survey cards and 20 deep-read notes.
- Canonicalized P1–P6, the three-certificate architecture, BirdInt's controlling record, and the F/E/G/no-go strata.
- Added complete registries for 6 primitive roles, 52 F-laws, 16 E-laws, 13 G-laws, and 8 no-go theorems.
- Added a 44-term glossary, 10-entry alias ledger, 7-entry correction/ambiguity ledger, law architecture, concept graph, and Foundations-VII gap map.
- Atomized four wish lists into 130 source-located requests and organized them into 30 provenance-preserving convergence groups.
- Registered P040/P058 as unresolved version family `VF-SAU-01` without double-counting evidence.
- Recovered P020 plain text through a conservative TeX fallback after converter failure.
- Registered P039 as `BLOCKED_FULL_TEXT`: 18 declared includes and its bibliography are absent from the supplied package.
- Added reproducible build scripts and a passing Step-1 validation suite.
- Corrected the generated source-archive checksum path to its repository-local location; the archive digest and all supplied paper/wish-list bytes are unchanged (`ADR-0006`).
- Excluded transient Python bytecode caches from delivery manifests and added an explicit rebuild cleanup before checksum generation.

## plan-v1 — reading-program design

- Inventoried and classified all 58 paper roots and four wish lists at planning level.
- Recorded the cumulative three-pass reading and synthesis program.
- Added the repository contract, schemas, templates, and plan validation.

# Mechanical acceptance gates

## Coverage states

Every paper has exactly one row in `corpus/coverage.csv` and progresses through:

`INVENTORIED`, `SURVEYED`, `DEEP_READ`, `CLAIM_EXTRACTED`, `BRIDGED`, `VII_ADJUDICATED`, `CLOSED`.

`UNKNOWN`, `CONFLICT`, `BLOCKED`, and `NOT_APPLICABLE` require a reason and owner artifact. P039 is currently `BLOCKED` at full-text depth while retaining an abstract-level Step-2 record.

## Step 1 checks

- 58 unique paper IDs and four unique wish lists.
- Source file and hash recorded for every supplied paper root.
- Survey card for every paper with source-located dependency reconnaissance and artifact/formalization disclosure.
- Citation reconnaissance covers all 58 papers and preserves unresolved, out-of-corpus, and non-paper keys without treating citation as theorem inheritance.
- Exact registries for six primitive roles, 52 F laws, 16 E laws, 13 G laws, and eight no-go results.
- Canonical glossary, correction history, and version-family controls.
- P040/P058 structural and raw-source deltas retained without premature theorem equivalence.

## Prior-formalization ingestion checks

- Complete supplied Foundations V/cognition and Foundations VI/Collatz archives, checksums, and upstream commit identities retained.
- Curated imports verify byte-for-byte against per-file manifests.
- Prior module/declaration/theorem/import indexes contain no unresolved local imports.
- Trust-base axiom and opaque constants are explicit.
- Paper-side F/E/G coverage is kept separate from locally supplied Lean coverage.
- Foundations V E16 is made discoverable through a VII-owned wrapper and completed manifest without altering upstream files.
- Active Foundations VII Lake shell imports the prior surface and introduces zero VII declarations.
- Missing Lean/PySAT host tools are limitations, never counted as successful kernel/test checks.

## Step 2 checks

The executable gate is `scripts/validate_step2.py`. It currently performs **42 checks**, including:

- all required Step-2 products and all 58 paper IDs exist;
- exactly 2,821 unique canonical claims satisfy the claim schema;
- claim IDs are sequential within each paper and per-paper JSONL/dossiers exactly partition and index the canonical corpus;
- every source location, root/tree hash, and expanded-source range resolves;
- all 1,356 supported explicit TeX formal environments are represented one-for-one;
- the four extraction lanes are complete and exclude submission/checklist boilerplate;
- all 58 papers have exactly one source-located composite abstract thesis, including section-form abstracts;
- all 48 explicit abstract nonclaim/scope/open clauses have typed component records;
- P039 is the sole source-package blocker and remains abstract-only, with one thesis and one explicit nonclaim;
- coverage is 57 `BRIDGED` plus one `BLOCKED` paper;
- formalization statuses preserve statement-fidelity, local-asset, trust, and kernel boundaries;
- no imported Lean or Foundations VII Lean source changes occur;
- all 52 F, 16 E, 13 G, and eight no-go rows resolve to canonical source claims;
- exactly 374 bridge rows satisfy the bridge schema and reference valid claims/contexts;
- all 240 Step-1 in-corpus invocation edges have one bridge row;
- all 2,022 candidate named-law occurrences are source-audited, all 217 accepted occurrences are covered exactly once by 45 grouped bridges, and known local-label collisions are rejected;
- all 89 prior-law/no-go rows have a future-reuse contract;
- all eight no-go rows preserve exact statement, carrier, hypotheses, scope, non-scope, escape route, and conservative formal correspondence;
- all 20 recurrent invalid-transfer guardrails are present;
- all 14 interaction/access/enablement matrices have the expected rows;
- all 14 domain pressure tests have carrier/interface/audit/nontransfer maps or a source block;
- all 24 example/carrier rows are source-grounded;
- all 130 wishlist atoms link to claims, boundaries, open obligations, laws/no-gos, and bridges;
- the P040/P058 223-row claim delta and non-independence ruling are intact;
- all six unresolved conflicts are typed and source-grounded;
- the 3,040-node / 35,276-edge graph closes over all endpoints and excludes unaudited lexical law edges;
- generated summaries and the 16-row requirement audit agree with canonical artifacts;
- obsolete prototype outputs are absent;
- no Step-3 or candidate-Foundations-VII artifact exists.

A Step-2 delivery cannot close if any validator row is `FAIL`.

## Step 3 checks

- Every candidate VII claim has source dependencies, proof obligations, and a status grade.
- Every candidate has detector, null, falsifier, and positive/countermodel fields, or a documented exemption.
- Every wishlist atom has a final disposition.
- Scope inheritance identifies prior results and anti-duplication constraints.
- Red-line scan finds no forbidden inference without an explicit bridge.
- Readiness report has zero unresolved critical blockers; noncritical deferrals are named.

## Forbidden-inference scan

Automated and human review searches for unsupported transitions involving:

- generic transition → P3;
- generic path → P5 packaging;
- semantics → P1;
- common source → shared access;
- contact → strict join;
- P3 holonomy → P6 directionality;
- strictness → closure/objecthood/drive;
- soundness → reachability/occurrence;
- reachability → occurrence;
- structural selection → top-down causal channel;
- enablement → descent;
- theorist-triggered → endogenous;
- negative instance → universal no-go.

---

## Step 3 — readiness dossier exit gate

Step 3 passes only when `python scripts/validate_step3.py` exits successfully and all of the following hold:

1. All required readiness, method, report, schema, finite-lab, formalization, and governance products exist.
2. The 2,821-claim and 374-bridge Step-2 bodies remain complete and unchanged.
3. All 58 paper roots have source-local dependency rereads; P039 remains abstract-only and P040/P058 remain non-independent.
4. Exactly 30 scope rulings, 18 object records, 36 candidate dossiers, and 130 unique wish-list adjudications exist.
5. Candidate, object, countermodel, and wish-list records satisfy their JSON schemas.
6. Every candidate has typed objects, proof obligations, detector/null/falsifier, positive and null models, a countermodel, formalization targets, source trace, nonclaims, and one chapter assignment.
7. Every candidate reference closes over the canonical claim, bridge, law/no-go, object, scenario, countermodel, formalization, wish-list, group, and chapter registries.
8. The object graph and chapter graph are closed and acyclic.
9. The Two-Theory World contains 24 scenarios and the reference evaluator reproduces 24/24 statuses and 29/29 assertions.
10. The 27 countermodels cover the required source/access, contact/join, enablement/descent, soundness/reachability, reachability/occurrence, holonomy/arrow, observer-cost, and total/partial-domain separations.
11. All 11 candidate no-gos remain explicitly scoped and have a failure assay plus an escape/positive control.
12. Twenty formal targets resolve through 30 exact reuse records to 29 unique inherited Lean declarations.
13. No Lean or paper TeX file is added or modified; the cumulative index contains zero Foundations VII declarations.
14. The 30 red lines and 15 decision points contain the mandatory overclaim and deferral boundaries.
15. The 1,851-node / 5,969-edge candidate graph is closed and the 3,166 source-trace rows match exact Step-2 source locations and grades.
16. Coverage is 57 `CLOSED` papers plus P039 `BLOCKED` at body level.
17. The stage summary contains no critical blocker and declares `STEP3_READINESS_COMPLETE_NO_PAPER_DRAFT`.
18. Repository entry points explicitly state that Step 3 is neither a proof of new VII theorems nor a paper draft.

The finite reference assay is a coherence and falsification tool. It cannot by itself satisfy a theorem-proof gate.

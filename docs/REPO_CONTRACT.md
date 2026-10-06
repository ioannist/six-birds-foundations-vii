# Local repository and delivery contract

## Repository layout during execution

```text
foundations-vii-reading/
├── source/                         # immutable paper/wishlist snapshot
├── corpus/                         # manifests, hashes, versions, coverage, dependencies
├── claims/by_paper/                # canonical Step-2 per-paper claim partitions
├── notes/dossiers/                 # full Step-2 paper dossiers
├── registry/                       # laws, roles, claims, evidence and provenance
├── formalization/
│   ├── _provenance/                # supplied V/VI archives, commits and hashes
│   ├── foundations_v_scaffold/     # immutable D/E theorem, Lean and lab baseline
│   ├── foundations_vi_scaffold/    # immutable VI plus prior I–IV baseline
│   ├── integration/                # declaration/coverage/traceability indexes
│   └── lean/                       # Foundations VII extension project
├── bridges/                        # Step-2 bridge atlas and invalid transfers
├── wishlists/                      # atomic requests and evidence/final dispositions
├── synthesis/                      # canonical theory and cross-paper syntheses
├── vii/                            # reserved for Step-3 dependency-closure products
├── decisions/                      # append-only ADRs and withdrawals
├── scripts/                        # extraction, indexing, validation and packaging
├── generated/                      # validation and delivery manifests
└── reports/                        # stage reports and audits
```

## Source and formalization authority

- Original paper and wishlist source under `source/` is immutable.
- Imported prior formalization under both `formalization/foundations_v_scaffold/` and `formalization/foundations_vi_scaffold/` is immutable and verifies byte-for-byte against the retained upstream archives.
- Exact TeX is authoritative for paper claims. Canonical claim records are typed navigation and traceability artifacts, not replacements for source statements.
- Lean source plus kernel elaboration is authoritative for mechanized statements. Paper mathematical grade, statement fidelity, local source presence, static import closure, kernel replay, and runtime evidence are always reported separately.
- Foundations VII definitions and proofs live under `formalization/lean/FoundationsVII/`.
- A correction or specialization of an imported declaration must be a new wrapper or adapter with an ADR or bridge record; it may not overwrite imported files.
- Citation-key resolution, lexical law detection, normalized prose, and source-line deltas are navigation/provenance aids. They do not establish theorem dependency, bridge validity, claim equivalence, chronology, or evidentiary independence.
- A named-law transfer is licensed only by the occurrence audit and a typed bridge/reuse record, not by the recall-oriented `imported_laws` field alone.

## Git rules

- One repository persists across all three steps and the pre-Step-2 formalization gates.
- Stable tags are `read-step-01`, `read-prestep-02-formal-scaffold`, `read-step-01-formal-aware-completion`, `read-step-01-complete-formal-spine`, `read-step-02`, and `read-step-03`.
- Corrections are new commits; historical interpretations are not rewritten without a correction record.
- Candidate VII statements cannot overwrite source claims or imported theorem declarations.
- Step-2 builders own the sole canonical `Pxxx-Cnnnn` ID space; downstream products consume rather than recreate it.

## Zip rules

Each zip is cumulative, deterministic, and self-contained. It includes:

- original paper/wishlist and formalization archives;
- all prior-stage work and Git history;
- current claims, bridges, dossiers, syntheses, reports, schemas, decisions, and validation output;
- `CONTENTS.md`, `CHANGELOG.md`, `SHA256SUMS`, and a delivery manifest;
- imported recorded lab evidence as upstream source evidence rather than a transient run;
- no caches, build products, virtual environments, secrets, or locally generated transient test runs.

The root report states the stable delivery tag. The included annotated tag resolves to the exact delivered commit; the external SHA-256 sidecar and final delivery response state the ZIP digest and commit explicitly. This avoids a self-referential commit-hash field inside the commit whose hash it would change.

## Stage boundary

Step 2 may produce claim, bridge, taxonomy, pressure-test, wishlist-evidence, and formalization-reuse artifacts. It may not create a Foundations VII primitive, candidate law, no-go program, Two-Theory World, countermodel atlas, pre-authoring chapter DAG, or new VII Lean declaration. Those belong to Step 3.

---

## Step-3 readiness contract

As of tag `read-step-03`, the repository stage is `STEP3_READINESS_COMPLETE_NO_PAPER_DRAFT`.

### Canonical Step-3 surface

`readiness/` is the authoritative Step-3 delivery surface. `vii/` is a compact mirror for later planning tools. Where a difference appears, regenerate both with `scripts/build_step3_readiness.py`; do not manually edit the mirror.

### Ownership and immutability

- `registry/`, `claims/`, `bridges/`, `source/`, and `synthesis/step2/` are frozen Step-2 evidence bodies.
- `formalization/foundations_v_scaffold/`, `formalization/foundations_vi_scaffold/`, `formalization/integration/`, and the existing import shell are frozen prior-proof bodies.
- Step-3-owned generated records live under `readiness/`, `vii/`, `formalization/step3/`, and the Step-3 wishlist/report paths.
- Later paper prose and new Lean declarations must not be landed by editing Step-3 generated records. They require a new stage, explicit ownership paths, and new acceptance gates.

### Evidence grades

A Step-3 candidate, finite scenario, planned module, or candidate no-go is not a theorem. The exact source claim grade and the imported Lean declaration status remain controlling. No language in a generated Markdown view may promote a machine-readable record's grade.

### Required preservation rules

A valid rebuild must preserve:

- 2,821 canonical Step-2 claims and 374 typed bridges;
- all imported Foundations I–VI source and Lean bytes;
- source hashes and P039/P040/P058 boundary rulings;
- zero new Foundations VII Lean declarations;
- no added or modified paper TeX;
- an explicit no-draft/no-new-theorem boundary.

### Rebuild

The canonical Step-3 rebuild is:

```sh
bash scripts/rebuild_step3.sh
```

It regenerates the readiness surface, executes the finite reference evaluator, and runs the Step-3 validator. Delivery manifests and zip packaging are separate finalization operations.

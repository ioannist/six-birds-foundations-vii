# Formalization workspace

This directory is the formal proof and finite-model base for the Foundations VII program. It was completed **before Step 2** so later claim extraction and paper design can reuse the established Foundations I–VI theorem scaffold instead of reconstructing prior work from prose.

## Layout

- `foundations_v_scaffold/` — immutable, byte-exact curated import from `six-birds-cognition_v45_2.zip`. It preserves the Foundations V theorem ledger, all D1–D6/E1–E16 Lean sources, vendored dependencies, declaration manifest, gates, examples, sweeps, finite labs, tests, traceability, and CI assets.
- `foundations_vi_scaffold/` — immutable, byte-exact curated import from `six-birds-collatz_v19.zip`. It preserves the Foundations VI theorem ledger, prior Foundations I–IV Lean libraries, G1–G13 modules, gates, labs, paper source, dependency audit, and CI assets.
- `_provenance/` — upstream commit identities, archive digest records, selection policies, and per-file import hashes. Original ZIPs are retained locally and intentionally excluded from the public repository.
- `integration/` — generated V, VI, and cumulative indexes: module/declaration/theorem/import graphs, paper-versus-local law coverage, E/G traceability, the V completed manifest, dependency relocation records, and the VII reuse map.
- `lean/` — the active Foundations VII Lake project. It contains an import shell over the prior libraries and **zero Foundations VII declarations**.

## Immutability rule

Files under `foundations_v_scaffold/` and `foundations_vi_scaffold/` are upstream baseline assets. Do not edit them for VII. Maintainers with the original local archives may re-import them with:

```sh
python scripts/import_foundations_v_scaffold.py
python scripts/import_foundations_vi_scaffold.py
```

Foundations VII definitions and proofs belong under `formalization/lean/FoundationsVII/`. Any correction, statement adapter, or compatibility layer must live outside the immutable subtrees and must name the exact upstream statement it adapts.

## Current source and import baseline

### Foundations V archive

- 70 Lean modules and 1,758 lexically indexed declarations;
- 22 authored Foundations V modules containing exactly 1,261 declarations, including 187 theorems;
- all D1–D6 definitions and E1–E16 law modules present;
- 196 local import edges, all resolved;
- zero lexical `sorry`, `admit`, axiom, or opaque declarations in the imported V archive;
- upstream root imports 20 of 21 authored submodules and omits the already-landed E16 module;
- upstream 1,141-row declaration manifest omits E16's 120 declarations;
- `FoundationsVII.PriorFoundationsVComplete` and `foundations_v_completed_manifest.toml` complete discoverability without modifying upstream files.

### Foundations VI/prior archive

- 74 Lean modules and 1,106 lexically indexed declarations;
- 125 local import edges, all resolved;
- zero `sorry` and zero `admit` tokens;
- one inherited axiom and five inherited opaque constants, all confined to the F13a hiddenness substrate and listed in the upstream trust-base ledger;
- 14 locally supplied Foundations IV F-law modules and all 13 Foundations VI G-law modules.

### Deduplicated active graph

The two archives bundle byte-identical copies of 24 Foundations III modules. The active Lake project selects one copy while retaining both source trees for provenance. The cumulative index therefore contains:

- 123 unique active modules: 120 inherited plus three declaration-free VII shell modules;
- 2,587 unique active declarations, including 793 theorem declarations;
- 297 resolved imports and zero unresolved imports;
- one inherited axiom, five inherited opaque constants, and zero VII declarations.

## Runtime and build evidence

- Foundations VI dependency audit passes; 70 Python files compile; 62 locally available tests pass. Three G11 tests require unavailable PySAT.
- Foundations V has 202 Python files compiling; 317 tests outside the E15 file pass; the E16 standalone sweep passes 69/69 comparisons.
- The E15 test file contains 74 tests, but its full local replay exceeded the 900-second execution limit. This is recorded as a replay limitation, not a test failure or Lean proof failure.
- Lean/Lake 4.28.0 is unavailable in this environment. Source presence, lexical indexing, and import closure reached R1–R3; no local R4 kernel compilation is claimed.

The exact evidence is in `generated/formalization_baseline.{json,txt}` and the V/VI validators.

## Formalization-aware Step-1 ruling

Paper-wide formalization reports and locally available modules remain distinct. Foundations IV reports 52 rows but 14 are supplied here; Foundations V now supplies its complete authored D/E theorem base, with an upstream E16 discoverability defect repaired only by VII-owned adapters; Foundations VI supplies all 13 graded G modules. Module presence does not erase theorem/schema distinctions, host-supplied certificate assumptions, open bridges, empirical nonclaims, or trust-base obligations.

Any later reuse must name the paper grade, exact declaration and fidelity, host/trust premises, adapter if any, and local evidence state.

See `integration/FORMALIZATION_REUSE_MAP.md`, `integration/FOUNDATIONS_SPINE_FORMALIZATION_COVERAGE.md`, `synthesis/FORMALIZATION_EVIDENCE_LADDER.md`, `reports/FOUNDATIONS_V_INTEGRATION_REPORT.md`, and the root `STEP1_COMPLETION_REPORT.md` before beginning Step 2.

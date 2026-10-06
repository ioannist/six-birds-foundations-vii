# Foundations VI / Collatz scaffold import report

> **Current cumulative status:** This archive-specific report remains accurate for the Foundations VI/Collatz import. The repository-wide E-series gap it recorded has since been closed by the separate Foundations V/cognition import; see `FOUNDATIONS_V_INTEGRATION_REPORT.md` and the root `STEP1_COMPLETION_REPORT.md`.


**Stage:** pre-Step-2 formalization ingestion
**Step 2 status:** not started
**Supplied archive:** `six-birds-collatz_v19.zip`
**Archive SHA-256:** `a595687d1ebccac4407aa5131f6ee03df349131c0cace236f1ae91f6d6a86ad4`
**Upstream commit recorded in zip comment:** `220b45879d8e63f1a75573145e0be6bb3f52567c`

## Imported assets

The active scaffold contains 282 byte-exact files totaling 2,926,555 bytes:

- `THEOREMS.md`;
- all 15 design documents;
- all formalization inventories, manifests, gates, examples, and interaction notes;
- the complete 74-file Lean source tree, including vendored prior Foundations libraries;
- the complete Python lab, tests, fixtures, recorded runs, verdicts, SAT/CNF inputs, and package metadata;
- Foundations VI paper source and bibliography;
- the upstream CI workflow and `.gitignore`;
- the imported-foundations dependency-audit script.

The complete original archive is retained locally but is intentionally excluded from the public repository. Its digest and upstream identity remain recorded. The active scaffold excludes operational prompts, review-request history, freeform `ideas.md`/`collatz_idea.md`, and upstream packaging scripts because they are not required proof or evidence dependencies.

## Formal surface indexed

The generated index records:

- 74 Lean modules;
- 1,106 lexical declarations: 507 definitions, 465 theorems, 52 inductives, 49 structures, 27 abbreviations, one axiom, and five opaque constants;
- 125 local import edges and zero unresolved imports;
- 10 Foundations II modules;
- 24 Foundations III modules;
- 5 closure-ladder modules plus one Foundations-I compatibility module;
- 14 Foundations IV law modules;
- 6 shared meta-math modules;
- 14 Foundations VI modules, comprising the root plus G1–G13.

The declaration index is lexical and source-located. It assists navigation but does not replace Lean elaboration.

## Trust and scope findings

The imported law files contain zero `sorry` and zero `admit`. The only project-specific inherited trust items are in F13a Hiddenness Normal Form:

- one axiom: `hiddenness_pending`;
- five opaque Paper-7 substrate constants.

The supplied trust-base ledger names these explicitly. No dedicated Foundations V E-series Lean library is present in this archive. That fact is recorded as an import-scope gap only.

## Validation performed

- Archive checksum and upstream commit identity: pass.
- All 282 imported files against per-file SHA-256 manifest: pass.
- Lean local import closure: pass, zero unresolved edges.
- Imported Foundations IV dependency audit: pass, 10 entries and zero violations.
- Python syntax parse: pass, 70 files.
- Locally available lab tests: pass, 62 tests.
- Three G11 tests were not runnable because `python-sat`/PySAT is unavailable in this environment.
- Lean build was not rerun because Lean/Lake 4.28.0 is unavailable locally and external download is unavailable. This is recorded as `NOT_RUN_TOOLCHAIN_UNAVAILABLE`, not a successful proof check.

The supplied upstream materials state that the Lean tree and complete 65-test lab suite were previously run, but this report does not substitute that statement for an independent local build.

## VII extension shell

A new Lake project under `formalization/lean/` points to the imported prior source directories and defines a single `FoundationsVII.PriorScaffold` import surface. It imports the closure ladder, Foundations II, the full Foundations III root, the available Foundations IV normal forms, shared meta-math machinery, and all Foundations VI laws. It introduces zero VII declarations.

This establishes the proof dependency base without beginning Step 2 or prematurely defining the VII theory.

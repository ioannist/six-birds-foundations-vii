# Foundations V theorem-base integration — Step 1 completion

## Scope

This integration imports the supplied cognition/Foundations V repository into the cumulative Foundations VII preparation repository. It remains Step 1: no all-paper claim extraction, bridge adjudication, Foundations VII law design, or new VII theorem statement has begun.

## Imported proof surface

- Upstream archive commit: `d548b834481ffe9160194907df61e6e247defc8e`.
- Active curated import: 372 byte-exact files, including **all Lean sources** and all vendored Lean dependencies.
- Lean archive index: 70 modules, 1758 total lexical declarations, zero unresolved imports, zero `sorry`, zero `admit`, zero authored axioms, and zero opaque declarations.
- Foundations V authored surface: 22 modules and **1261 declarations**, including **187 theorems**. This exactly matches the paper-reported 1,261 authored declarations / 187 theorems.
- Definitions: D1--D6 are present. Laws: all E1--E16 are present; E6 and E9 share one module.

## Completion repairs kept outside the immutable upstream tree

The upstream root imports every authored submodule except the already-landed `SixBirdsFoundationsV.Laws.E16Adaptability`. Its declaration manifest likewise contains 1141 rows and omits the 120 E16 declarations. The repository therefore adds:

1. `formalization/lean/FoundationsVII/PriorFoundationsVComplete.lean`, which imports the upstream root and E16 explicitly;
2. `formalization/integration/foundations_v_completed_manifest.toml`, a 1261-row normalized manifest linked to exact Lean files and lines.

The original root and manifest remain byte-for-byte unchanged.

## Dependency and version control

- All imported Foundations V Lean imports resolve locally.
- The Foundations III vendor copy bundled with Foundations V is byte-identical to the copy bundled with Foundations VI: 27 files, no differences. The active Lake project therefore declares one SixBirdsIII library and retains both provenance copies.
- The historical imported-foundations inventory uses absolute local-checkout paths. In this self-contained repository, 46 of 51 entries have every identifier relocated exactly, 4 are partial, and 1 has no exact-string relocation. These are explicitly recorded as source-packaging/wording limitations, not silently marked verified.

## Deduplicated cumulative active graph

The V and VI archives overlap on 24 Foundations III module names. Their source copies are byte-identical and remain retained for provenance; the active Lake project selects one copy. The resulting graph contains **123 unique modules**, **2587 declarations**, including **793 theorem declarations**, and **297 resolved imports**, with zero VII declarations and zero unresolved imports. Machine-readable rows are in `cumulative_lean_modules.csv`, `cumulative_lean_declarations.csv`, `cumulative_lean_theorems.csv`, and `cumulative_lean_import_edges.csv`.

## Reuse rule

Foundations VII work may import `FoundationsVII.PriorScaffold` or the narrower `FoundationsVII.PriorFoundationsVComplete`. Paper-side theorem grades, conditional hypotheses, complete-evidence assumptions, and nonclaims remain controlling. A typed classification theorem is not evidence that a biological, cognitive, or social certificate was constructed honestly.

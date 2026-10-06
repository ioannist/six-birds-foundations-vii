# Formalization-aware audit of the Foundations spine

## Controlling result

The imported scaffold changes how Step 1 must speak about prior proof support. It does **not** change the core SBT interpretation, but it sharpens which parts are directly reusable and which are only paper-reported, typed, conditional, guarded, or absent from the supplied archive.

## Coverage summary

| Surface | Paper-side disclosure | Locally supplied active surface | Step-1 ruling |
|---|---|---|---|
| Foundations I | Deliberately minimal closure/package core; no probability or Markov Lean | 6 relevant modules | Reuse closure/idempotence only. |
| Foundations II | Typed harness; no faithful theorem derivations in the paper's strongest fidelity class | 10 modules | Reuse types/status/admissibility; not exact-six proof. |
| Foundations III | 21 definitions + 35 theorem-backed manifest claims, with theorem/model/audit grades | 24 modules, but not the complete original validator packet | Reuse calculus; do not claim rerun manifest equivalence. |
| Foundations IV | 52 rows: 46 direct, 2 anchors, 2 partial, 2 obligations | 14/52 modules | Use exact 14-row subset; other 38 are R0 paper-reported. |
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

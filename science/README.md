# Foundations VII final science assets

This directory contains the machine-readable scientific release through `FVII-SCI-05`. The
manuscript is maintained separately under `paper/`.

## Final registries

- `registry/final_*` records the terminal object, definition, theorem, no-go, corollary,
  countermodel, finite-assay, adapter, decision, dependency, trust, candidate, and target surfaces.
- `traceability/final_*` binds statements to source hashes, Lean declarations, imports, trust
  receipts, and bounded witnesses.
- `theorems/`, `no_go/`, and `decisions/` provide human-auditable dossiers for the terminal rulings.

## Cumulative phases

- Phase 1 supplies the typed kernel, inherited adapters, scenarios, countermodels, and reference
  evaluator.
- Phase 2 supplies admission/access definitions, five no-go fronts, and nine bounded families.
- Phase 3 supplies contact, join, residual, and certified-noninteraction machinery with eleven
  bounded families.
- Phase 4 supplies enablement, descent, confluence, holonomy, arrow, and residual-flow machinery
  with twelve bounded families.
- Phase 5 closes the cross-family corollaries and terminal registries and enumerates eleven global
  bounded families.

The final public surface contains 36 candidate dispositions, 20 formalization targets, 11 no-go
fronts, 21 cross-family corollaries, 24 scenarios, and 27 named countermodels.

## Verification boundary

The recorded Lean 4.28.0 replay passes the cumulative kernel build, all five Lean/Python
differentials, and the final `#print axioms` capture without a `sorry` dependency. Static completion,
kernel derivability, finite enumeration, and scientific interpretation remain distinct evidence
grades. Finite counts are exhaustive only over their declared carriers.

Run `bash scripts/rebuild_fvii_sci05.sh` from the repository root for the deterministic
source/Python rebuild, or `bash scripts/run_fvii_sci05_external_lean.sh` for the complete kernel and
differential replay.

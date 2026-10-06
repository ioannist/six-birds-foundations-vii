# Foundations VII science traceability

This directory records source, finite-evidence, statement-hash, and trust provenance for every executed science phase.

- `phase1_*` links kernel objects, inherited adapters, 24 scenarios, 27 countermodels, statements, and the inherited one-axiom/five-opaque trust surface.
- `phase2_*` links admission/access candidates and no-gos to Lean declarations, source blocks, nine finite families, primary fixtures, and 15 canonical witnesses.
- `phase3_*` links contact/join/obstruction candidates and no-gos to 363 declarations, 183 theorem statements, eleven finite families, primary fixtures, and 27 canonical witnesses.

`phase3_statement_hashes.sha256` freezes every Phase-3 theorem statement. `phase3_asset_trace.*` binds each candidate to exact source blocks and finite controls. `phase3_bounded_witnesses.*` records canonical assignments, file hashes, and assignment hashes.

Kernel-level dependencies and trust reports remain pending until the external cumulative `#print axioms` replay is executed; static traceability is not a substitute for elaboration.

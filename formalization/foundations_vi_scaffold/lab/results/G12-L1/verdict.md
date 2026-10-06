# G12-L1 Verdict - Heule 826 Finite Witness

## Hypothesis
The vendored Heule/Polymath16 826-vertex graph should be a real unit-distance graph and should be non-4-colorable.

## Outcome
PASS.
Parsed `826` vertices and `4273` undirected edges from the vendored data.
Exact symbolic unit-distance failures: `0`. 60-digit numeric failures: `0`.
Random non-edge sanity check: sampled `2000` non-edges with `0` exact unit-distance hits.
4-coloring CNF: `3304` variables, `22874` clauses, written to `results/G12-L1/heule_826_4color.cnf`.
SAT solve: `UNSAT` using `kissat404` in `308.335437` seconds.

## Certificate Scope
The coordinate and edge portions of `cert_4(W)` are checked here in exact algebraic arithmetic. The non-4-colorability portion is solver-verified by SAT, not independently proof-checked: this 826-vertex instance has no public DRAT/resolution certificate in Heule's `CNP-SAT` repository, and this lab does not produce or verify one. (Smaller graphs in the same repository, e.g. 517/529/553/610/633/803 vertices, do have public DRAT certificates; this lab does not consume or proof-check those either. See `data/PROVENANCE.md` for the corrected provenance record.)
This reproduces a known finite-witness lower-bound stream for the Hadwiger-Nelson problem. It is not a new chromatic-number result and does not claim to use the smallest known 509-vertex Parts graph, whose raw coordinates were not found publicly archived.

## Scope Note
The full SAT solve is intentionally not part of `pytest tests`; tests cover parsing, structural sanity, and exact unit-distance checks. Run this CLI without `--skip-sat` to reproduce the solver-verified UNSAT determination.

Traceability: this lab instantiates `SixBirdsFoundationsVI.Laws.G12FiniteWitnessRadiation.FiniteWitnessObstruction` for the concrete 826-vertex unit-distance graph at `k=4`. Combined with `SixBirdsFoundationsVI.Laws.G12FiniteWitnessRadiation.no_global_k_coloring`, the finite witness rules out a proper 4-coloring of the plane, modulo the solver-verified UNSAT caveat above.

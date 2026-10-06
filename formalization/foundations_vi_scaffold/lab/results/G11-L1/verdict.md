# G11-L1 Verdict - Periodic-Defect Certificates On Wang Sets

## Hypothesis
The monochromatic two-tile control set is periodic-admissible, while the Jeandel-Rao 11-tile set has no tiling on any tested small torus.

## Outcome
PASS. The control set was SAT on a `1x1` torus with assignment `[[0]]`.
PASS. The Jeandel-Rao sweep tested every `p1 x p2` torus with `1 <= p1,p2 <= 4` and every instance was UNSAT.
Jeandel-Rao instances: `1x1` UNSAT (11 vars, 230 clauses); `1x2` UNSAT (22 vars, 460 clauses); `1x3` UNSAT (33 vars, 690 clauses); `1x4` UNSAT (44 vars, 920 clauses); `2x1` UNSAT (22 vars, 460 clauses); `2x2` UNSAT (44 vars, 920 clauses); `2x3` UNSAT (66 vars, 1380 clauses); `2x4` UNSAT (88 vars, 1840 clauses); `3x1` UNSAT (33 vars, 690 clauses); `3x2` UNSAT (66 vars, 1380 clauses); `3x3` UNSAT (99 vars, 2070 clauses); `3x4` UNSAT (132 vars, 2760 clauses); `4x1` UNSAT (44 vars, 920 clauses); `4x2` UNSAT (88 vars, 1840 clauses); `4x3` UNSAT (132 vars, 2760 clauses); `4x4` UNSAT (176 vars, 3680 clauses).

## Surprise
None.

## Implication
The control instance supplies a case-(a) periodic-admissible witness. The Jeandel-Rao UNSAT sweep supplies bounded small-period defect certificates for case (b), consistent with the published aperiodicity theorem.

## Scope Note
This lab tests rectangular `p1 x p2` torus period lattices only: periods of the form `(p1,0)` and `(0,p2)` jointly realized as one rectangular fundamental domain. It does not test arbitrary non-axis-aligned period vectors `p=(a,b)` with both components nonzero as a single period.
This lab also records only the full-instance UNSAT result and commits the full DIMACS instance for each tested torus. It does not extract UNSAT cores or minimize finite defect regions, so `design/04_LABS.md`'s G11-L1 UNSAT-core/minimal-region refinement remains future work.

This result exercises G11's Case Enumeration cases (a) and (b), and the abstract `Hierarchy`/`ForcedBreaksPeriod` schema from `SixBirdsFoundationsVI.Laws.G11GlobalAntiSymmetry`, made concrete at bounded small-period SAT scale rather than as a specific Lean theorem.

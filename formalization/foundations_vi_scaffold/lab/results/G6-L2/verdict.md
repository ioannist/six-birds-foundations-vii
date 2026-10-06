# G6-L2 Verdict - Tunable Recaman Variants

## Hypothesis
Variant A with jump `2n` should visit only even values, making all odd positive integers permanent holes. Variant B with constant jump `1` should satisfy `a_n=n` and visit exactly `{0,...,n}` after step `n`.

## Outcome
PASS.
Variant A checked `1000000` steps: all-even=`True`, unique visited=`736749`, final=`4114328`, max=`11892252`, odd violations recorded=`0`.
Variant B checked `1000000` steps: identity holds=`True`, visited set exact=`True`, unique visited=`1000001`, final=`1000000`, max=`1000000`.

## Proof Artifacts
`lab/results/G6-L2-proofs.md` records the parity-invariant proof for Variant A and the exact visited-set induction proof for Variant B.

## Surprise
None.

## Scope Note
This is a genuine worked instantiation of both abstract G6 schemas for deliberately simplified tunable variants. It says nothing about the original Recaman sequence's open coverage question.
Variant A discharges `DominantObstruction visited_y 0` for every odd target `y`, because the parity invariant proves `visited_y(n)` is always false. This instantiates `hole_forming_schema`.
Variant B discharges `DominantPressure holes_M` for every finite window `W_M={1,...,M}`, because `holes_M(n)=max(M-n,0)` strictly decreases whenever positive. This instantiates `covering_schema`.

Traceability: Variant A is a concrete proof instance of `SixBirdsFoundationsVI.Laws.G6EndogenousNeedleGeneration.hole_forming_schema`; Variant B is a concrete proof instance of `SixBirdsFoundationsVI.Laws.G6EndogenousNeedleGeneration.covering_schema`. Neither variant is the original Recaman recurrence.

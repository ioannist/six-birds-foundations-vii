# G1-L4 Verdict - Aliquot Ledger Illustration

## Hypothesis
For starts `1 <= n <= 100000`, exact aliquot iteration `s(n)=sigma(n)-n` is tracked for up to `1000` steps, with values above `1000000000000` recorded as `escaped_cap`.

## Outcome
PASS as an illustrative exact-arithmetic exhibit. Checked `100000` starts in `7.627695` seconds.
Terminated at `0`: `82728`. Entered a cycle: `2085`. Escaped cap: `15187`. Step-cap unresolved: `0`.
Unique cycles found: `22`. Starts landing on fixed-point cycles: `801`. Unique fixed points: `(6, 28, 496, 8128)`.
Maximum observed steps before classification: `417` at start `62334`. Maximum value seen before stopping: `3110427560520`.
Factorized sigma was cross-checked against brute-force divisor sums for `1..1000`: `True`.

## Cycles and Open Cases
Representative unique cycles: `[(6,), (28,), (496,), (8128,), (220, 284), (1184, 1210), (2620, 2924), (5020, 5564), (6232, 6368), (10744, 10856), (12285, 14595), (17296, 18416), ... (22 total)]`.
Escaped-cap start sample: `(276, 306, 396, 552, 564, 660, 696, 702, 720, 780, 828, 840, 858, 888, 936, 966, 978, 990, 996, 1044, 1062, 1074, 1086, 1098, 1104, 1134, 1146, 1158, 1170, 1218, 1230, 1248, 1266, 1278, 1302, 1314, 1320, 1326, 1338, 1350, 1356, 1392, 1398, 1410, 1422, 1440, 1464, 1476, 1488, 1512)`. Step-cap start sample: `()`.

## Ledger Note
For each traced orbit step, the implementation can record `nu_2(sigma(n_k))` alongside `n_k`, `sigma(n_k)`, and `s(n_k)`. This is only one projection of the divisor-supply ledger: the relevant currency is the full factorization and divisor structure, not a one-dimensional scalar.

## Scope Note
This is an illustrative folded G1 instance only. Escaped-cap and step-cap cases are reported as open within this finite budget; they are not evidence that a sequence is unbounded and not evidence that it would terminate with more time.
The run makes no claim about the Catalan-Dickson boundedness/termination conjecture, the Guy-Selfridge unboundedness question, or the Collatz conjecture.

## Surprise
None.

This result is a G1 ledger-dimensionality illustration: it shows that a G1-style currency can be the non-scalar factorization/divisor-supply ledger. It does not instantiate `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.part_a_reduction`, `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.part_b_discharge`, `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.GhostConvergence`, or `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.NativeSeparation`.

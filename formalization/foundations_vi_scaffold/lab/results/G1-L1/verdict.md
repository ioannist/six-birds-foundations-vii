# G1-L1 Verdict - Collatz Affine Ledger Audit

## Hypothesis
For every checked odd `n`, the accelerated Collatz affine ledger `n_k = (3^k*n + B_k) / 2^A_k` holds exactly through first descent, and the descent certificate matches the integer inequality `2^A_k*n > 3^k*n + B_k`.

## Outcome
PASS. The sweep checked every positive odd `n < 1000000` with max step cap `1000` in `10.243299` seconds.
Tested odd starts: `500000`. Nonterminal starts: `499999`. Terminal fixed starts: `1`.
All `499999` nonterminal odd starts reached first descent before the cap; capped starts: `0`.
Total exact ledger checkpoints: `2241405`. Maximum first-descent step: `111` at `n=626331`.
Maximum accumulated valuation `A_k`: `176`; maximum `B_k` bit length: `178`; maximum checked orbit value bit length: `35`.

## Exact Checks
At every checked horizon the numerator `3^k*n + B_k` was exactly divisible by `2^A_k`, the quotient matched direct accelerated iteration, and `(n_k < n)` was equivalent to `2^A_k*n > 3^k*n + B_k` using integer arithmetic only.

## Scope Note
This lab validates the concrete Collatz setup formulas needed for future G1 instantiations. It does not directly instantiate `part_a_reduction` or `part_b_discharge`, because those Lean theorems are abstract statements about `Descends`, `BadTailMembrane`, `GhostConvergence`, and `NativeSeparation`, and do not contain the affine arithmetic ledger.
This packet does not prove Collatz and does not make progress on the Collatz conjecture. It is an exact bookkeeping audit over the declared finite range.

## Surprise
None.

## Implication
The affine ledger and descent-boundary certificate are internally consistent for every checked odd start. Any later Collatz-specific G1 membrane or ghost-shadowing lab can use these formulas as a tested calibration surface, while still needing separate evidence for the abstract liveness/discharge hypotheses.

This result validates the concrete G1 Setup formulas `T(n)=(3n+1)/2^a(n)`, `A_k=sum_{j<k} a_j`, `B_0=0`, `B_{j+1}=3B_j+2^A_j`, and `n_k=(3^k*n+B_k)/2^A_k` from `THEOREMS.md`. It is setup-formula validation for future use with `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.Descends` and `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.BadTailMembrane`, not a direct instantiation of `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.part_a_reduction` or `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.part_b_discharge`.

# G1-L2 Verdict - Bad-Tail Membrane Census

## Hypothesis
Every tested odd `n < 10^7` reaches first descent within the step cap, and the `2^L-1` ghost-shadowing family has exact `a_i=1` shadowing for `0 <= i < L-1` with predicted `k*(2^L-1)=L-1`.

## Outcome
SURPRISE / PARTIAL FAIL. The odd-start census checked every positive odd `n < 10000000` in `15.268460` seconds for the census phase and `15.280923` seconds total.
Nonterminal starts: `4999999`; descended before cap: `4999999`; capped: `0`; terminal fixed starts: `1`.
`k*` mean: `3.490310`; median: `2`; 90th percentile: `8`; 99th percentile: `27`; max: `155` at `n=8088063`.
Ghost family checked `L=2..80`. Shadow/closed-form failures: `0`. `k*=L-1` prediction failures: `79`.

## Membrane Census
| k | count with `k*=k` | membrane size `count(k*>k)` |
| ---: | ---: | ---: |
| 1 | 2499999 | 2500000 |
| 2 | 625000 | 1875000 |
| 3 | 625000 | 1250000 |
| 4 | 234375 | 1015625 |
| 5 | 273438 | 742187 |
| 6 | 117187 | 625000 |
| 7 | 73241 | 551759 |
| 8 | 103759 | 448000 |
| 9 | 52798 | 395202 |
| 10 | 72633 | 322569 |
| 11 | 36659 | 285910 |
| 12 | 25301 | 260609 |
| 13 | 38386 | 222223 |
| 14 | 21014 | 201209 |
| 15 | 30355 | 170854 |
| 155 | 1 | 0 |

The full `k*` histogram and membrane-size dictionary are recorded in `run.json`.

## Ghost-Shadowing Family
| L | shadow steps | all `a_i=1` | closed form | predicted k* | actual k* | match |
| ---: | ---: | --- | --- | ---: | ---: | --- |
| 2 | 1 | True | True | 1 | 2 | False |
| 3 | 2 | True | True | 2 | 4 | False |
| 4 | 3 | True | True | 3 | 4 | False |
| 5 | 4 | True | True | 4 | 35 | False |
| 6 | 5 | True | True | 5 | 34 | False |
| 7 | 6 | True | True | 6 | 9 | False |
| 8 | 7 | True | True | 7 | 8 | False |
| 9 | 8 | True | True | 8 | 11 | False |
| 10 | 9 | True | True | 9 | 11 | False |
| 20 | 19 | True | True | 19 | 34 | False |
| 30 | 29 | True | True | 29 | 76 | False |
| 40 | 39 | True | True | 39 | 75 | False |
| 50 | 49 | True | True | 49 | 90 | False |
| 60 | 59 | True | True | 59 | 129 | False |
| 70 | 69 | True | True | 69 | 185 | False |
| 80 | 79 | True | True | 79 | 141 | False |

## Surprise
The first tested ghost-family mismatch is `L=2`: the prediction was `k*=1`, but the exact run found `k*=2`.
The unconditional shadowing fact itself was confirmed: direct iteration matched `n_i = 3^i*2^(L-i)-1`, and all checked prefix valuations were `a_i=1` for `0 <= i < L-1`. What failed was the stronger packet prediction that this prefix makes the first descent occur exactly at `L-1`.

## Scope Note
The `2^L-1` ghost-shadowing family is evidence against fixed finite-depth proof strategies, not evidence for or against the Collatz conjecture. This lab is a native-integer bad-tail census and Proof-Spine formula check; it does not touch a completion `Xhat`, an embedding, ghost neighborhoods `U`, `GhostConvergence`, or `NativeSeparation`.
This packet does not prove Collatz and does not make progress on the Collatz conjecture.

## Implication
The census supplies exact finite-range membrane data, and the `2^L-1` family supplies verified arbitrarily long one-halving prefixes over the tested `L` range. The exact `k*=L-1` claim is not supported by this computation and should not be used as a paper claim without correction.

This result validates G1's native bad-tail census and the `2^L-1` shadowing formula from `THEOREMS.md` for the tested range. It is setup/proof-spine validation for future use with `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.BadTailMembrane` and `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.InfiniteBadThread`, not a direct instantiation of `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.part_a_reduction`, `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.part_b_discharge`, `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.GhostConvergence`, or `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.NativeSeparation`.

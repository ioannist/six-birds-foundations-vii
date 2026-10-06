# G7-L1 Verdict - Finite-Board Angel/Devil Search

## Hypothesis
Exact bounded-horizon minimax on small finite tori should show `p=1` trapped quickly and `p=2` surviving longer within the tested horizon, for devil budgets `b in {1,2}`.

## Outcome
QUALIFIED PASS. Full exact minimax was run for 8 parameter settings with total wall time 39.120220 seconds.
Across the four comparable `(N,b)` pairs, exactly one is a clean, unconfounded separation: `N=4,b=2`, where `p=1` traps within the tested horizon and `p=2` survives to horizon. Two pairs, `N=3,b=1` and `N=3,b=2`, are geometric degeneracies: on the `3 x 3` torus, `p=1` and `p=2` have identical legal-move sets, so separation is structurally impossible there. The remaining pair, `N=4,b=1`, is inconclusive within the tested horizon because both mobility values survive to horizon `8`.
This does not trigger the prediction's falsification condition: the degenerate rows cannot test mobility separation, and the one unconfounded `N=4,b=2` row shows the expected qualitative threshold behavior. It is nevertheless only a qualified finite-board calibration, not broad evidence across all tested rows.

| N | p | b | horizon | guaranteed turns | status | states | seconds |
| ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 3 | 1 | 1 | 9 | 8 | trapped within 9 | 4664 | 0.055466 |
| 3 | 1 | 2 | 9 | 4 | trapped within 5 | 3087 | 0.043261 |
| 3 | 2 | 1 | 9 | 8 | trapped within 9 | 4664 | 0.055309 |
| 3 | 2 | 2 | 9 | 4 | trapped within 5 | 3087 | 0.043153 |
| 4 | 1 | 1 | 8 | 8 | survived to horizon 8 | 147939 | 2.380535 |
| 4 | 1 | 2 | 8 | 5 | trapped within 6 | 460692 | 14.498064 |
| 4 | 2 | 1 | 8 | 8 | survived to horizon 8 | 148596 | 2.424476 |
| 4 | 2 | 2 | 8 | 8 | survived to horizon 8 | 572807 | 19.617532 |

## Board Geometry Check
Computed max torus-Chebyshev distance from cell `0`: `N=3` -> max torus-Chebyshev distance `1`; `N=4` -> max torus-Chebyshev distance `2`.
Thus `N=3` is too small to distinguish mobility powers `p=1` and `p=2`: every other cell is already within distance `1` by torus wraparound. On `N=4`, the maximum distance is `2`, so `p=2` genuinely reaches cells that `p=1` cannot reach in one move.

## Bounded-Horizon Scope
These are finite-board, bounded-horizon values. A finite torus is not the infinite angel-problem board: given enough turns, the devil can eventually delete all non-occupied cells. Therefore `survived to horizon` means only that the angel can force survival for the tested number of turns, not that the angel escapes forever.

## Tractability Scope
The aspirational design target was `N <= 7`; this packet runs full unrestricted devil responses on `N=3` with horizon `9` and `N=4` with horizon `8`. No devil move-set restriction was used. Larger boards/horizons were left for future packets because exact minimax grows combinatorially in the deleted-cell set and devil response subsets; a direct `N=5` probe at horizon `6+` exceeded the one-minute feasibility budget in this run.

## Wall-Rank Testbed
The concrete `p=1,b=1` finite-board confinement testbed uses an exhaustion/sweep-wall devil response rather than a classical infinite-plane wall proof: after the angel moves, delete the first available non-angel cell. The rank is the number of remaining deletable free cells, and it strictly decreases after every tested devil move.
start=0 turns=15 trapped=True; start=5 turns=15 trapped=True; start=10 turns=14 trapped=True.

## Surprise
Two prediction-relative surprises occurred and are resolved by the diagnostics above. First, `N=3` is a geometric degeneracy: `p=1` and `p=2` have identical legal-move sets because the maximum torus-Chebyshev distance is `1`. Second, `N=4,b=1` was inconclusive within the tested horizon: both mobility values survived to horizon `8` with no separation. These are scope explanations, not failures of the finite-board calibration.

## Implication
This is a bounded finite-board calibration for G7's certificate typing. The wall-rank testbed is structurally analogous to a concrete `ConfinementStrategy`; the `p=2` minimax rows are bounded-horizon evidence only and do not discharge an infinite `EscapeStrategy`.

This result exercises G7's Case Enumeration case (a), `Confined`, through a finite-board devil-side witness structurally analogous to `SixBirdsFoundationsVI.Laws.G7AdversarialMobilityConfinement.ConfinementStrategy` and `SixBirdsFoundationsVI.Laws.G7AdversarialMobilityConfinement.confinement_forces_trap`; the `p=2` rows are bounded-horizon evidence relevant to, but not a proof of, `SixBirdsFoundationsVI.Laws.G7AdversarialMobilityConfinement.EscapeStrategy` or `SixBirdsFoundationsVI.Laws.G7AdversarialMobilityConfinement.escape_never_stuck`.

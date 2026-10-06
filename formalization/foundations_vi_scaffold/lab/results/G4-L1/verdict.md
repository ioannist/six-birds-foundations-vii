# G4-L1 Verdict - Greedy Egyptian-Fraction Exhaustion

## Hypothesis
Every proper fraction `p/q` with `0 < p < q <= 500`, after reduction to lowest terms, terminates under the Fibonacci-Sylvester greedy algorithm with a strictly decreasing numerator budget and an exact unit-fraction certificate.

## Outcome
PASS. Swept `124750` raw proper fractions `p/q` with `0 < p < q <= 500`, representing `76115` distinct reduced fractions.
Failures: `0`. Step cap: `1000`. Maximum certificate length: `12`, attained by `221/398`, `36/457`.

## Certificate-Length Distribution
`1`: `2690`, `2`: `13077`, `3`: `32062`, `4`: `39042`, `5`: `25625`, `6`: `9615`, `7`: `2222`, `8`: `363`, `9`: `47`, `10`: `3`, `11`: `2`, `12`: `2`

## Target-Size Exhibit
| max denominator q | max certificate length among p/q with this q |
|---:|---:|
| 2 | 1 |
| 10 | 3 |
| 50 | 5 |
| 100 | 6 |
| 250 | 7 |
| 500 | 7 |

## Worked Example
`3/7 = 1/3 + 1/11 + 1/231` with denominator certificate `[3, 11, 231]` and numerator budget `[3, 2, 1, 0]`.

## Surprise
None.

## Scope Note
This lab calibrates G4's positive schema only: local arithmetic checks discharge patch soundness, and the strict positive-integer numerator descent discharges exhaustion for the tested greedy Egyptian-fraction instance.
It does not exercise `LanguageComplete` or `conditional_biconditional`, and it does not exercise `FixedLeak` or `fixed_package_no_go`. G4-L2 Erdos-Straus content is deliberately out of scope.

This result exercises `SixBirdsFoundationsVI.Laws.G4MovingCoverExhaustion.positive_schema` for the concrete Fibonacci-Sylvester greedy Egyptian-fraction calibration, with `Sound` represented by exact unit-subtraction checks and `Exhausted` represented by strict numerator descent.

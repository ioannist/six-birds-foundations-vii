# G6-L1 Verdict - Recaman Census

## Hypothesis
The exact Recaman recurrence should produce high but incomplete bounded-window coverage, a nonzero return-pressure proxy, and a visible smallest-missing trajectory over a `10^7`-step census.

## Outcome
PASS as a bounded census. Ran `10000000` exact Recaman steps with bytearray membership through `100000000` and exact high-value fallback count `0`.
Final value: `20438710`. Maximum value reached: `61998984`. Final smallest missing positive integer: `1355`.
Final return-pressure proxy `4999986/10000000` records the exact fraction of steps where the backward move was legal.

## Checkpoint Curve
| step | current | max | smallest missing | backward legal / steps | visited in [1,100000] | visited in [1,1000000] | visited in [1,10000000] |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1000000 | 2057164 | 5946126 | 1355 | 499988/1000000 | 97007/100000 | 466168/1000000 | 736748/10000000 |
| 2000000 | 5565082 | 11156073 | 1355 | 999987/2000000 | 98062/100000 | 659197/1000000 | 1461796/10000000 |
| 3000000 | 6384380 | 18043263 | 1355 | 1499987/3000000 | 98062/100000 | 807595/1000000 | 2126459/10000000 |
| 4000000 | 6399414 | 25641765 | 1355 | 1999987/4000000 | 98617/100000 | 824151/1000000 | 2656113/10000000 |
| 5000000 | 16199252 | 28123708 | 1355 | 2499986/5000000 | 98617/100000 | 824151/1000000 | 3085258/10000000 |
| 6000000 | 5572482 | 34704852 | 1355 | 2999987/6000000 | 99241/100000 | 913479/1000000 | 3490105/10000000 |
| 7000000 | 4564318 | 38142116 | 1355 | 3499987/7000000 | 99241/100000 | 913479/1000000 | 3869030/10000000 |
| 8000000 | 19390462 | 43296075 | 1355 | 3999986/8000000 | 99241/100000 | 913479/1000000 | 4208154/10000000 |
| 9000000 | 20176872 | 61998984 | 1355 | 4499986/9000000 | 99241/100000 | 913479/1000000 | 4518327/10000000 |
| 10000000 | 20438710 | 61998984 | 1355 | 4999986/10000000 | 99241/100000 | 933518/1000000 | 4675267/10000000 |

## Final Missing-Interval Sample
First missing intervals in `[1,1000000]`: `1355`, `1643`, `1814`, `[2405,2406]`, `2426`, `2520`, `2991`, `4202`, `8076`, `9168`, `11682`, `13548`, `13713`, `[14510,14511]`, `14568`, `14804`, `[16114,16115]`, `[18107,18108]`, `[18954,19113]`, `20577`.

## Surprise
None.

## Scope Note
This is a bounded exact-arithmetic census and System-case (S-c) uncertified exhibit for G6. It does not instantiate `covering_schema`, because it supplies no proof that all holes in a cofinal exhaustion are eventually covered.
It also does not instantiate `hole_forming_schema`, because it supplies no permanent-hole obstruction proof. The OEIS A005132 `852655` smallest-missing fact at computations as large as `10^612` terms is much stronger as a bounded computation than this `10^7`-step exhibit; this lab neither extends nor contradicts that record.

Traceability: this result is a bounded Recaman census for G6's case-enumeration System-case (S-c), illustrating the `gamma_n`/`rho_n` race. It is not a proof instance of `SixBirdsFoundationsVI.Laws.G6EndogenousNeedleGeneration.covering_schema` or `hole_forming_schema`.

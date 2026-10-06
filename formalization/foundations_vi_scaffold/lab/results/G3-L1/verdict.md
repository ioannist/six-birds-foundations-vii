# G3-L1 Verdict - Amortized Calibration Battery

## Hypothesis
Binary-counter increment has exact amortized cost `2`; dynamic-array insertion has amortized cost at most `3`, with exact cost `3` at resizing insertions; both satisfy the finite-prefix telescoping identity.

## Outcome
PASS. Binary counter seed 7301 ran 1000 increments from start value 44142 to 45142; every amortized cost was exactly `2` and telescoping held.
PASS. Dynamic array seed 7302 ran 1000 insertions after 3 warmup insertions; 8 resize step(s) were observed, every amortized cost was at most `3`, each resize had amortized cost exactly `3`, and telescoping held.

## Worked Checks
| check | before | after | actual | Phi before | Phi after | a_hat |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| binary carry | 0111 | 1000 | 4 | 3 | 1 | 2 |
| binary non-carry | 0100 | 0101 | 1 | 1 | 2 | 2 |
| dynamic resize | size=4,capacity=4 | size=5,capacity=8 | 5 | 4 | 2 | 3 |

## Credit-Ledger Preview
The JSON result includes the first five audited ledger rows for each calibration.

## Surprise
None.

## Implication
This is an exact-integer computational exhibit for G3's finite-prefix potential-currency theorem.

## Scope Note
Splay trees are not implemented in this lab packet. `THEOREMS.md` already cites Sleator-Tarjan's access lemma as the structural calibration; this run covers the binary-counter and dynamic-array arithmetic calibrations.

This result exercises `SixBirdsFoundationsVI.Laws.G3AmortizedCurrency.telescoping_identity` and `SixBirdsFoundationsVI.Laws.G3AmortizedCurrency.uniform_actual_cost_bound`, confirming exact finite-prefix amortized-cost accounting for the binary-counter and dynamic-array calibrations.

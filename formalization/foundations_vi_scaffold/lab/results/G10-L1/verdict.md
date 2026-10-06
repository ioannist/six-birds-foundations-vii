# G10-L1 Verdict - Ducci Collapse

## Hypothesis
Seeded Ducci tuples of power-of-two lengths `4`, `8`, and `16` collapse to zero, while the seeded non-power-of-two calibration tuples enter nonzero cycles. The GF(2) parity operator `L=I+S` satisfies `L^k=0` for `k=4,8,16`.

## Outcome
PASS. Seed 10100 swept `k=3..16` with max entry 1000000 and step budget 100000.
Power-of-two collapses: `k=4` zero at step `4`; `k=8` zero at step `18`; `k=16` zero at step `98`.
Non-power-of-two cycles: `k=3` period `3` at step `2889`; `k=5` period `15` at step `75`; `k=6` period `6` at step `62`; `k=7` period `7` at step `66`; `k=9` period `63` at step `158`; `k=10` period `30` at step `108`; `k=11` period `341` at step `449`; `k=12` period `12` at step `89`; `k=13` period `819` at step `915`; `k=14` period `14` at step `88`; `k=15` period `15` at step `99`.
Boundedness onset: after the first Ducci step, every observed coordinate stayed below the initial range bound for every tested `k`.
GF(2) matrix checks: `(I+S)^4=0` for `k=4`; `(I+S)^8=0` for `k=8`; `(I+S)^16=0` for `k=16`.

## Surprise
None.

## Implication
This is the mechanized lab witness for G10's Case Enumeration case (b), `Collapsing`: the Ducci parity structure is destroyed by the exact nilpotency certificate for power-of-two lengths, and the non-power-of-two seeded calibrations show eventual nonzero cycles.

This result exercises G10's `THEOREMS.md` Case Enumeration case (b) (`Collapsing`) and the Ducci GF(2) proof-spine claim `(I+S)^{2^m}=0`; Ducci was deliberately left as lab-only collapse content rather than a Lean theorem.

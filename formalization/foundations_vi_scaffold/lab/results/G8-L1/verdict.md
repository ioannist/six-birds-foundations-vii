# G8-L1 Verdict - Sandpile Odometer Invariance

## Hypothesis
Legal sandpile stabilization on finite grid graphs with sink is order-independent.

## Outcome
PASS. Seed 8601 tested sizes [10, 20, 30, 40, 50] with 1 initial configuration(s) per size and 100 random legal orders per configuration.
All 500 seeded random stabilizations matched the deterministic min-site and max-site baselines exactly in final configuration and odometer vector.

## Surprise
None.

## Implication
This supports G8 Part A on the tested sandpile calibration instances.

## Open Item
This packet did not implement the least-action / deliberately-wasteful-stabilization sub-experiment from `design/04_LABS.md`'s G8-L1 spec: comparing the true legal odometer against deliberately wasteful stabilizing scripts, "per Fey-Levine-Peres framing ⚑". This run covers only the order-independence half of G8-L1 (Part A). G8 Part B is already independently proved in Lean as `SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.least_action`; the missing item is the computational exhibit for the paper, not a gap in the law's Lean verification. Resolving the `⚑` remains future work and requires checking the actual Fey-Levine-Peres least-action construction against a citable source before implementing it.

This result exercises `SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.odometer_invariance`, confirming exact odometer invariance for the sandpile instantiation.

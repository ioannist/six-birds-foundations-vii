# G2-L1 Verdict - Goodstein Ordinal Escrow

## Hypothesis
Hereditary-base Goodstein rebasing preserves the ordinal escrow, and the Goodstein decrement strictly descends it.

## Outcome
PASS. Deterministic sweep checked starts 1..30 with step budget 4, for 116 verified Goodstein steps.
Terminated starts within budget: (1, 2). Max reached base: 6. Max integer bit length encountered: 120605.

## Worked Example
For `n=4`, base `2`, the runner reproduced `O_2(4)=omega^omega`, `rebase_{2->3}(4)=27`, `G_2(4)=26`, and `O_3(26)=omega^2*2 + omega*2 + 2 < omega^omega`.

## Surprise
None.

## Implication
This is a deterministic computational exhibit for G2's stage-coherent escrow descent mechanism.

## Scope / Runtime Note
`design/04_LABS.md`'s G2-L1 spec suggests a bounded prefix such as `10^4` steps, but Goodstein sequences grow explosively. In this exact hereditary-reconstruction implementation, even a step budget of `5` does not complete in reasonable time across all 30 starts. The shipped run uses budget `4` and already reaches integers up to `120605` bits, roughly 36306 decimal digits. This is a calibration exhibit of the per-step descent/invariance identities (116 independent checks across 30 starts), not a claim about full sequence termination length. Full termination is separately and unconditionally proved in Lean by `SixBirdsFoundationsVI.Laws.G2TransfiniteEscrow.no_infinite_nonterminal_run`, independent of how many steps a computational sweep can reach.

This result exercises `SixBirdsFoundationsVI.Laws.G2TransfiniteEscrow.no_infinite_nonterminal_run`, confirming the Goodstein ordinal escrow instantiation of stage-coherent descent.

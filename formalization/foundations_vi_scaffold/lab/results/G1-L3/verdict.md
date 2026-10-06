# G1-L3 Verdict - Finite Ghost Toy

## Hypothesis
The finite accelerated-Collatz residue system on odd residues modulo `2^16` should classify every native residue as descending, declared-ghost-bound, or non-ghost bad-cycle-bound, with zero unclassified residues.

## Outcome
PASS. Exhaustively classified `32768` odd residues modulo `65536` in `0.156657` seconds.
Terminal accepted residue: `1`. Nonterminal residues: `32767`. Descended: `32765`. Declared-ghost-bound: `2`. Genuine nonterminal bad-cycle starts: `0`. Unclassified: `0`.
Maximum descent step among separating residues: `37` at residue `27`.

## Gamma_m
The declared ghost residue is `21845`, the unique odd solution of `3*r+1 == 0 mod 2^16`. For this `m`, the closed form is `(2^16 - 1) / 3`.
The raw classifier also detects the fixed cycle `(1,)`. This is not a new toy-specific obstruction: it is the same accelerated Collatz terminal fixed point named in G1's Setup, where `3*1+1=4`, `nu_2(4)=2`, and therefore `T(1)=1`. Matching the abstract law's ordering, residue `1` is Case (a) terminal in `A={1}` and is excluded before bad-tail/Gamma bookkeeping.
With residue `1` excluded as terminal, corrected `Gamma_16` has `2` nonterminal starting residue(s): `[14563, 21845]`.
No genuine nonterminal non-ghost bad cycles were found.

## Hypothesis Checks
`NativeSeparation` finite analogue: `True`. Every nonterminal residue outside corrected `Gamma_16` has an explicit computed descent horizon `K=k*(r)`; residue `1` is discharged first as terminal.
`GhostConvergence` finite analogue: `True`. Every nonterminal residue in corrected `Gamma_16` reaches the declared ghost before any descent, and there are no genuine nonterminal bad cycles for `m=16`.

## Surprise
None remains after applying the abstract law's terminal-first ordering. The raw `(1,)` cycle is exactly the known `T(1)=1` accepted terminal fixed point, not a genuine nonterminal bad cycle or a new ghost obstruction.

## Scope Note
This is a finite toy model of G1's ghost machinery. It genuinely discharges the finite instance's `GhostConvergence` and `NativeSeparation` analogues, showing that the abstract hypotheses are checkable and non-vacuous in principle.
It does not discharge those hypotheses for the actual infinite Collatz system, does not construct the real `2`-adic completion, and does not prove or make progress on the Collatz conjecture.

This result instantiates `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.GhostConvergence` and `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.NativeSeparation` for the finite residue-ring toy model, and therefore exercises the conditional shape of `SixBirdsFoundationsVI.Laws.G1HiddenAmortizedSolvency.part_b_discharge` in a fully finite worked instance. It makes no claim that the real Collatz instance satisfies those hypotheses.

# G6-L2 Proofs - Tunable Recaman Variants

## Variant A: even-jump permanent holes

Define `a_0 = 0`. At step `n >= 1`, set `candidate = a_{n-1} - 2n`; if
`candidate > 0` and has not been visited, set `a_n = candidate`, otherwise set
`a_n = a_{n-1} + 2n`.

Claim: every `a_n` is even.

Proof: By induction on `n`. The base case is `a_0 = 0`, which is even. For the
inductive step, assume `a_{n-1}` is even. The jump `2n` is even, so both
`a_{n-1} - 2n` and `a_{n-1} + 2n` are even. The recurrence chooses one of these
two values, so `a_n` is even. Therefore every term is even.

Consequently no odd positive integer is ever visited. For any fixed odd target
`y`, define `visited_y(n)` to mean that `y` appears among `a_0,...,a_n`.
The parity invariant proves `¬ visited_y(n)` for every `n`; in particular
`¬ visited_y(0)`, and the implication `¬ visited_y(n) -> ¬ visited_y(n+1)` holds
for every `n`. Thus Variant A supplies `DominantObstruction visited_y 0`, and
G6's `hole_forming_schema` applies to every odd `y`.

## Variant B: constant-unit full coverage

Define `a_0 = 0`. At step `n >= 1`, set `candidate = a_{n-1} - 1`; if
`candidate > 0` and has not been visited, set `a_n = candidate`, otherwise set
`a_n = a_{n-1} + 1`.

Claim: for every `n >= 0`, `a_n = n`, and after step `n` the visited set is
exactly `{0,1,...,n}`.

Proof: Use induction on `n` with the invariant
`a_n = n` and `V_n = {0,1,...,n}`, where `V_n` is the set of values visited
through step `n`. The base case is `n=0`: `a_0=0` and `V_0={0}`. For the
inductive step, assume `a_n=n` and `V_n={0,1,...,n}`. At step `n+1`, the
candidate is `a_n - 1 = n - 1`. If `n=0`, this candidate is `-1`, not positive,
so the forward branch gives `a_1=1`. If `n>0`, then `n-1` is already in
`V_n`, so the backward branch is blocked. In all cases the recurrence takes the
forward branch and sets `a_{n+1}=a_n+1=n+1`. Therefore
`V_{n+1}=V_n ∪ {n+1}={0,1,...,n+1}`. The invariant holds for all `n`.

For any finite audit window `W_M={1,...,M}`, the hole count after step `n` is
`holes_M(n)=max(M-n,0)`. Whenever `holes_M(n)>0`, we have `n<M`, so
`holes_M(n+1)=holes_M(n)-1 < holes_M(n)`. This discharges
`DominantPressure holes_M`, and G6's `covering_schema` applies to every fixed
finite window.

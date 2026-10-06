# G5-L1 Verdict - Base-2 Reverse-and-Add Confinement

## Hypothesis
`22 = 10110_2` enters the four-phase target-free language `P0(r) -> P1(r) -> P2(r) -> P3(r) -> P0(r+1)` under `R(n)=n+rev_2(n)`, and no checked phase-family iterate is a palindrome.

## Outcome
PASS. Starting seed `22` followed the exact pre-entry segment `10110 -> 100011 -> 1010100 -> 1101001 -> 10110100` and then completed 20 full phase cycles.
The phase-family sweep checked `80` reverse-and-add transitions and `81` phase states, ending at `101111111111111111111111010000000000000000000000` (`P0(22)`).
Total reverse-and-add steps from the seed were `84`; the largest checked binary string had `48` bits.

## Worked First Cycle
`R(10110100)=11100001`; `R(11100001)=101101000`; `R(101101000)=110010101`; `R(110010101)=1011101000`.

## Surprise
None.

## Implication
This is an exact-integer computational exhibit for G5's closed-pattern confinement schema: after finite entry into `Pcal = P0 ∪ P1 ∪ P2 ∪ P3`, closure under `R_2` and target-freeness keep the orbit out of binary palindromes for every checked cycle.

## Scope Note
This is a finite exact-integer sweep of the four phase identities from one entry point over `20` checked cycles. It is not an independent proof that `R(P_i(r))` follows the claimed phase cycle for all `r`. The universal confinement theorem is the Lean-abstract `closed_pattern_confinement`, which takes `[H-G5-closed-pattern]` (`ClosedUnderR`/`TargetFree`) as a supplied hypothesis; this lab calibrates that hypothesis's concrete instance over a bounded run, rather than re-deriving it for unboundedly many `r`.

This packet does not explore base-10 Lychrel candidates such as `196`; G5's nonclaims keep that question open unless a closed target-free certificate is supplied.

This result exercises `SixBirdsFoundationsVI.Laws.G5CarryHorizonConfinement.closed_pattern_confinement` for the concrete instance `R = R_2`, `Target = Pal_2`, and `Pcal = P0 ∪ P1 ∪ P2 ∪ P3`.

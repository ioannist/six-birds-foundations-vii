# E4 Repair Compilation Law — Toy-Lab Predictions (Round A, pre-registration)

Written before any sweep implementation exists. Round B implements against this document; it does not
redesign the fixture after seeing results. All arithmetic is exact (`fractions.Fraction`); no
randomness. The carrier reuses `lab/sixbirds_foundations_v/worlds/repair_world.py`'s ring-kernel style
(as E3/E12 do). E4's own five-way status is evaluated per `(window, candidateOpt)` — a single shared
window with multiple candidates attached, mirroring how the Lean `CompleteCompilationStatus` is
parameterized.

## 1. Toy-Lab Configuration

### Post-registration additions (disclosed, step-5 methodology review)

The step-5 methodology review found three genuine gaps in the original registration, none fitting
predictions to observed results — each is forced by conditions this landing's own Lean/six-field stages
already settled:

1. **P2 support-gate compilation was never exercised.** Every original positive candidate used
   `RepairSort.P1`; the source text names P1 (operator rewrite) and P2 (support gate) as two distinct
   valid compilation forms, and only the negative (P3-rejection) side of that disjunction was tested.
   New candidate: **`cand_compiled_support_gate`** — identical to `cand_compiled` in every respect
   except `move.sort = P2`. Registered: `lawful=True`, `descent=True`, `silent=True`,
   `status=compiled`.
2. **No window genuinely failed the theorem's own scope hypotheses.** `window_main` is constructed to
   always satisfy `ObstructionReducingAcrossWindow`/`IdempotenceStableAcrossWindow`; only the
   structural `atLeastTwoInvocations` guard (`window_too_short`) was tested. `E4_Compilation`'s own
   Lean statement was fixed during mechanization review specifically to require these two facts as
   independent hypotheses — the toy-lab must demonstrate both can genuinely fail for a validly
   *constructed* (≥2-invocation) window. Two new windows:
   - **`window_no_obstruction_reduction`**: ≥2 valid invocations, idempotent payloads, but no strict
     obstruction shrink (a new post-invocation split pair is introduced). Registered:
     `CompilationCandidateWindow` constructible = True, `ObstructionReducingAcrossWindow` = False,
     `IdempotenceStableAcrossWindow` = True.
   - **`window_payload_drift`**: ≥2 valid invocations, genuine obstruction reduction, but payload
     distances between invocations exceed the declared threshold. Registered:
     `CompilationCandidateWindow` constructible = True, `ObstructionReducingAcrossWindow` = True,
     `IdempotenceStableAcrossWindow` = False.
3. **`SameFamilySaturated` was a disconnected flag.** `cand_compiling_same_family`'s saturation
   predicate ignored its own `(family, probe)` arguments and returned a hardcoded boolean — the same
   anti-pattern already caught and fixed for `Δ_bound` during E12's own toy-lab methodology review.
   Fix: the saturation predicate now genuinely computes "probe already in the active family's support
   with unchanged weight" from real `ActiveFamily` data — `cand_compiling_same_family`'s own repackaged
   payload is constructed to trigger this condition, while every other candidate's payload genuinely
   changes the support/weight and computes `False`.

### Ring carrier and shared window

`Z = {0, ..., 19}` (20 states), `supp_k(z, z') := z' == (z + 1) mod 20`, matching E3/E12's own
`ring_kernel` precedent. A single shared `window_main` is used across every candidate scenario below:
`episodeTimes = [0, 1, 2]` (3 invocation times, satisfying the structural `atLeastTwoInvocations`
non-vacuity guard), each invoking the *same* repair refinement `R_main`, with a genuine per-time
`EndogenousRepairOccurrence`-style witness (admissible source tag `committed_state`,
`generatedByS=True`, `inScope=True`, kernel-realized transition).

- **`ObstructionReducingAcrossWindow`**: at each invocation time, the split-pair set strictly shrinks —
  no new post-invocation obstruction, and at least one genuine pre-present/post-absent pair
  (`Delta` count: 3 at t=0's pre-state, 2 at t=1's pre-state, 1 at t=2's pre-state, 0 after t=2).
- **`IdempotenceStableAcrossWindow`**: all three invocations install payloads within
  `Fraction(1, 100)` of each other (well below a declared `threshold = Fraction(1, 10)`).

### FIII Promotion Python mirror (new — first use in this project's Python layer)

`lean/vendor/foundations/six-birds-foundations-iii/lean/full/SixBirdsIII/Promotion.lean` is mirrored
faithfully: `PromotionGateResults` (fields `suff`/`desc`/`stab`/`ctrl`/`nosmuggle`/`vis`/`audit`
as `GateStatus ∈ {pass, notRequired, fail}`, `strict` as `StrictGateStatus`), `PromotionBridgeData`
(`admissible: bool`, `gates: PromotionGateResults`), `required_core_gates_pass_bool` (the exact
`suff/ctrl/nosmuggle/vis/audit` all-`pass` plus `desc`/`stab` each `pass`-or-`notRequired` check),
`promotion_accepted_core_bool := admissible and required_core_gates_pass_bool(gates)`,
`promote` (returns `candidate`/`accepted`/`strict`/`nonStrict`), `accepted_promotion_family` (`True`
for `accepted`/`strict`/`nonStrict`, `False` for `candidate`).

### FIII TopDownChannel reuse (direct, matching E11's own precedent)

Reuses the exact fixture values E11's own sweep already established: `td_accepted_stack`-equivalent
(all nine gates `True`, genuinely accepted) and `td_structural_only`-equivalent (a real structural path
present but `interventionGate`/`effectGate` false, blocked claim status) are reused as the two channel
records tested below.

### Candidates attached to `window_main`

| candidate | lawful? | descent verified? | silent verified? | decompilation event? | out-of-class witness? | registered status |
| --- | --- | --- | --- | --- | --- | --- |
| (none — `candidateOpt = none`) | — | — | — | — | — | `exposed` |
| `cand_compiled` | True | True | True | False | False | `compiled` |
| `cand_mis_compiled` | True | True | True | False | True | `mis_compiled` |
| `cand_decompiled` | True | True | True | True | False | `decompiled` |
| `cand_compiling_blocked_channel` | False (channel blocked) | — | — | False | False | `compiling` |
| `cand_compiling_promotion_rejected` | False (promotion not accepted) | — | — | False | False | `compiling` |
| `cand_compiling_memory_only` | False (memory-only comparator fails) | — | — | False | False | `compiling` |
| `cand_compiling_same_family` | False (`SameFamilySaturated` holds) | — | — | False | False | `compiling` |
| `cand_compiling_unverified_descent` | True | False | — | False | False | `compiling` |
| `cand_statused_obstruction` | True | True | True | False | False (classified, not unstatused) | `compiled` |

`cand_compiled` and `cand_statused_obstruction` share an identical construction except for one thing:
`cand_statused_obstruction` has the *same* genuine out-of-class split-pair as `cand_mis_compiled`, but a
carried `ObstructionStatusRecord` classifies it (`assignedStatus = accepted_brittleness`) — so
`OutOfClassObstructionWitness`'s own `unstatused` conjunct is false, and the candidate is `compiled`,
not `mis_compiled`. This directly demonstrates `CarriedObstructionStatusFor`'s positive case, not just
its absence.

`cand_compiling_unverified_descent` demonstrates the exact gap the six-field review's round-5 finding
was about: `CompilationLawful` holds (all four certification conditions pass), but `CompiledDescent` is
NOT verified (a genuine residual in-class split pair still exists) — the candidate must land in
`compiling`, not `compiled`, confirming `E4_Compilation` genuinely requires descent as an independent,
checked hypothesis rather than something derivable from lawfulness alone.

### Priority-2 (decompiled) demonstration

`cand_decompiled` is deliberately built with the *exact same* lawful/descent/silent core as
`cand_compiled`, differing only by a genuine, carried `DecompilationEventRecord` tied to its own
`decompilationRecord`. This demonstrates the round-3 priority fix directly: a candidate that would
otherwise qualify as `compiled` correctly falls to `decompiled` once a genuine reversion event exists.

### Non-vacuity / structural controls

- **`window_too_short`**: an attempted window with only 1 invocation time — must fail to satisfy
  `atLeastTwoInvocations` (a construction-level rejection, not a runtime `False`).
- **`cand_wrong_sort`**: an attempted candidate whose `move.sort` is P3 (neither P1 nor P2) — must fail
  `sortIsRewriteOrGate` (construction-level rejection).
- **`cand_unattributed`**: a candidate genuinely constructed but carried under a *different* repair
  refinement / challenge class than `window_main`'s own `(C, R)` — must never be assigned any status
  for `window_main` (an attribution-linking control, mirroring E12's own arbitrary-fragment exclusion).

## 2. Registered Theorem-Facing Predictions

```text
candidateOpts = [none, cand_compiled, cand_compiled_support_gate, cand_mis_compiled,
                 cand_decompiled, cand_compiling_blocked_channel,
                 cand_compiling_promotion_rejected, cand_compiling_memory_only,
                 cand_compiling_same_family, cand_compiling_unverified_descent,
                 cand_statused_obstruction]
```

(`cand_compiled_support_gate` is the post-registration P2 addition from §1; listed here for
completeness now that it's a genuinely registered comparison, not just mentioned in the addendum.)

Each row's registered status matches §1's table exactly. `E4_StatusPartition`'s own claim (exactly one
of `Exposed`/`Decompiled`/`Compiled`/`MisCompiled`/`Compiling` holds per `(window, candidateOpt)`) is
checked for every row: exactly one status-boolean is `True`.

### `E4_Compilation` instance

```text
window = window_main
candidate = cand_compiled
```

| predicate | registered value |
| --- | --- |
| `CompiledOperatorRecordAttributedTo(window_main, cand_compiled)` | True |
| `CompilationLawful(cand_compiled)` | True |
| `CompiledDescent(cand_compiled)` | True |
| `HigherPackageGoesSilent(window_main, afterTime=2)` | True |
| `DecompilationEventRecord` exists | False |
| `OutOfClassObstructionWitness` exists | False |
| `CompiledHolds(window_main, cand_compiled)` | True |

### `E4_Brittleness` instance

Using `cand_mis_compiled`'s own compiled quotient (generated for the in-class family via
`minimalGeneratedQuotient`), tested against a declared out-of-class challenge `C_other ≠ C`: the
compiled quotient has a genuine split-pair for `C_other` (the same pair `OutOfClassObstructionWitness`
already witnesses), so `¬ descends(compiled_quotient, F(C_other), r)` — registered `True`. The
uncompiled, per-episode repair (re-deriving its own quotient fresh each episode) would not carry this
obstruction, since it never commits to a single fixed compiled quotient across classes.

## 3. Consolidation Instance: Habit/Institutionalization Reading

Per THEOREMS.md's own framing ("habits and institutionalization are one law"), `cand_compiled`'s
scenario reads at the cognitive scale as a skill becoming habitual (a repeatedly-practiced repair
compiled into a silent, low-audit-cost lower-layer operator) and at the social/economic scale as
routinization (repeated coordination repairs compiling into a standardized contract/convention).
`cand_mis_compiled` is the brittleness recognized instance at both scales (a habit failing
out-of-distribution; a standardized contract failing under an unanticipated dispute type) —
`cand_statused_obstruction` shows the same brittleness genuinely *managed* (the obstruction is
classified and accepted as a known, bounded cost) rather than silently accruing.

## 4. Null and Control Predictions

### Memory-only comparator control (`cand_compiling_memory_only`)

A control carrier supplied with the window's own history but genuinely lacking the repair structure
still reproduces the same in-class descent — `MemoryOnlyComparatorCertified.survivesControl = False`.
`CompilationLawful` fails condition (ii) specifically; every other condition ((i), (iii), (iv)) holds.
Registered: `compiling`, with condition (ii) isolated as the sole failure.

### Same-family-saturation control (`cand_compiling_same_family`)

The candidate's move payload is a pure relabeling of an already-carried repair with no genuine
structural change — `SameFamilySaturated(saturated, L, Mprobe) = True`, so
`¬ SameFamilySaturated = False`. `CompilationLawful` fails condition (iii) specifically; every other
condition holds. Registered: `compiling`.

### Blocked top-down channel control (`cand_compiling_blocked_channel`)

Reuses E11's own `td_structural_only`-equivalent channel record (a real structural path present, but
`interventionGate`/`effectGate` false). `TopDownChannelAcceptedBool = False`. `CompilationLawful` fails
condition (i)'s structural half. Registered: `compiling`.

### Promotion-bridge-rejected control (`cand_compiling_promotion_rejected`)

A `PromotionBridgeData` with `admissible = True` but `RequiredCoreGatesPass = False` (e.g. `ctrl =
fail`). `AcceptedPromotionFamily(Promote(...)) = False`. `CompilationLawful` fails condition (i)'s
promotion half specifically — every other sub-condition of (i) (the channel half) and conditions
(ii)–(iv) hold. Registered: `compiling`.

### Unverified-descent control (`cand_compiling_unverified_descent`)

See §1's own discussion above — isolates the round-5 six-field finding directly.

### Statused-obstruction control (`cand_statused_obstruction`)

See §1 — isolates `CarriedObstructionStatusFor`'s positive case, confirming a classified (not
unstatused) out-of-class obstruction does not block `compiled` status.

### Structural non-vacuity controls (`window_too_short`, `cand_wrong_sort`)

Both are construction-level rejections (the types themselves cannot be inhabited), not runtime `False`
values — registered as "cannot be constructed," matching the non-vacuity discipline established across
E1/E3/E11/E12's own landing history.

### Attribution-linking control (`cand_unattributed`)

`cand_unattributed` is carried under a distinct `(C', R')` pair, not `window_main`'s own `(C, R)`.
`CompiledOperatorRecordAttributedTo(window_main, cand_unattributed) = False` — the candidate is never
assigned any status for `window_main`.

## 5. Scope Note: Actual Carried Candidate vs. Existential Feasible Candidate

Following E1/E3/E11/E12's own precedent, every candidate above is a genuinely constructed, carried,
attributed dataclass instance — not an assumed/hypothetical one. `CompilationLawful`'s four conditions
are each checked against the candidate's *own* carried fields (channel record, promotion data,
memory-only witness, same-family witness), never a separately-supplied, unlinked witness — mirroring
the anti-unlinked-evidence fix from six-field review round 2.

## 6. Falsification Conditions

1. Falsified for `cand_compiled` if any of `CompilationLawful`/`CompiledDescent`/
   `HigherPackageGoesSilent` is computed `False`, if a `DecompilationEventRecord` or
   `OutOfClassObstructionWitness` is found for it, or if `CompiledHolds` is not the unique `...Holds`
   predicate reported true.
2. Falsified for `cand_mis_compiled` if the shared lawful/descent/silent core is not identical to
   `cand_compiled`'s own, if no genuine `OutOfClassObstructionWitness` is found, or if
   `MisCompiledHolds` is not the unique `...Holds` predicate reported true.
3. Falsified for `cand_decompiled` if the shared lawful/descent/silent core is not identical to
   `cand_compiled`'s own, if no genuine `DecompilationEventRecord` is found, or if it is classified
   anything other than `decompiled` (confirming priority-2 placement is load-bearing).
4. Falsified for `cand_compiling_blocked_channel`/`cand_compiling_promotion_rejected`/
   `cand_compiling_memory_only`/`cand_compiling_same_family` if `CompilationLawful` is computed `True`,
   or if the specific condition named for each is not the isolated point of failure (i.e. every other
   condition must independently hold).
5. Falsified for `cand_compiling_unverified_descent` if `CompilationLawful` is computed `False` (the
   control must isolate unverified descent, not lawfulness, as the reason for `compiling` status).
6. Falsified for `cand_statused_obstruction` if it is classified `mis_compiled` rather than `compiled`,
   or if its `OutOfClassObstructionWitness` existential is reported nonexistent rather than existing-
   but-classified (the control specifically tests the `unstatused` conjunct, not witness absence).
7. Falsified if `window_too_short` or `cand_wrong_sort` can be constructed at all (both must be
   structurally impossible, not merely falsy).
8. Falsified if `cand_unattributed` is ever assigned a status for `window_main`, or if
   `CompiledOperatorRecordAttributedTo` is satisfied by a witness not genuinely tied to `window_main`'s
   own `(C, R)`.
9. Falsified if the FIII Promotion Python mirror's `promote`/`accepted_promotion_family` disagrees with
   a hand-derived expectation for any registered candidate (spot-checked against the exact Lean gate
   logic in `Promotion.lean:6-68`).
10. **(post-registration addition)** Falsified for `cand_compiled_support_gate` if `lawful`/`descent`/
    `silent` are not all `True`, if its status is anything other than `compiled`, or if its `move.sort`
    is not genuinely `P2` (confirming P1 is not the only compilation form the sweep can classify
    `compiled`).
11. **(post-registration addition)** Falsified for `window_no_obstruction_reduction` if
    `ObstructionReducingAcrossWindow` is computed `True` despite the constructed new post-invocation
    split pair, or if `IdempotenceStableAcrossWindow` is computed `False` for it (the control must
    isolate obstruction-reduction failure specifically).
12. **(post-registration addition)** Falsified for `window_payload_drift` if
    `IdempotenceStableAcrossWindow` is computed `True` despite payload distances exceeding the declared
    threshold, or if `ObstructionReducingAcrossWindow` is computed `False` for it (the control must
    isolate idempotence-stability failure specifically).
13. **(post-registration addition)** Falsified if `cand_compiling_same_family`'s
    `SameFamilySaturated` value is computed from anything other than genuine `ActiveFamily` support/
    weight data — e.g. if the predicate ignores its own `(family, probe)` arguments — or if any
    non-same-family candidate's payload is computed `SameFamilySaturated = True` by the same genuine
    predicate (a false-positive would indicate the predicate is too permissive, not genuinely
    discriminating real structural change from relabeling).
14. Falsified if the total registered comparison count reported by the sweep does not match this
    document's own candidate count (10 original candidateOpt rows + 3 original structural/attribution
    controls + 3 post-registration additions = 16 total registered checks).

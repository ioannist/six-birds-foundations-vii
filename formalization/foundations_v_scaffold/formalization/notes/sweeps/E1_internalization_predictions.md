# E1 Internalization Predictions

This is the pre-registered prediction artifact for the E1 toy-laboratory
probe. It is intentionally written before any E1 sweep implementation exists.
Round B should implement the sweep against this document, not redesign the
configuration after seeing results.

No experiment has been run for this artifact. All quantities below are exact
and should be represented with `fractions.Fraction` where arithmetic is needed.
This E1 Round A instance is fully deterministic: no random seed, stochastic
simulation, or hash-audited float branch is required.

## 1. Toy-Lab Configuration

### Repair-World Carrier And Challenge Switch

The sweep specializes `lab/sixbirds_foundations_v/worlds/repair_world.py`.
It uses `RepairWorldState`, `RepairWorldConfig`, `RepairAction`,
`ChallengeClass`, and `ChallengeProcess` directly. The challenge switch is the
existing `ChallengeProcess.drift_schedule` mechanism:

```python
F = Fraction

C_base = ChallengeClass("baseline")
C_split = ChallengeClass("split_ab")

challenge_process = ChallengeProcess(
    recurrence_period=1,
    default_challenge=C_base,
    drift_schedule={2: C_split},
    binding_states=frozenset({0, 1, 2, 3, 4}),
)
```

Thus `challenge_at(t, y)` returns `baseline` at `t = 0,1` and
`split_ab` at `t = 2,3,4`. The matched enabled and ablated variants use the
same challenge process and the same starting state.

The carrier items are:

```text
X = {a,b,c,d}.
```

The initial quotient is:

| item | `Q0(item)` |
| --- | --- |
| `a` | `u` |
| `b` | `u` |
| `c` | `v` |
| `d` | `v` |

The baseline challenge has constant readout, so its split-pair obstruction is
empty. The switched challenge `split_ab` uses the readout:

| item | `r_split(F_split(item))` |
| --- | ---: |
| `a` | `0` |
| `b` | `1` |
| `c` | `0` |
| `d` | `0` |

The registered obstruction score is the unordered challenged-pair count:

```text
DeltaCount(Q, C_split) =
  number of unordered pairs {x,x'} with Q(x)=Q(x')
  and r_split(F_split(x)) != r_split(F_split(x')).
```

For `Q0`, the only challenged split pair is `{a,b}`, so:

```text
DeltaCount(Q0, C_split) = 1.
DeltaCount(Q0, C_base)  = 0.
```

The declared challenged fibers for E1's `StrictChallengeDescent` check are
exactly the unordered pair `{a,b}`.

### Repair Generator And Refinement

The generator-enabled variant has a reachable repair generator for the binding
defect:

```text
defect_split := "split_ab_defect"
S.R_S(defect_split) = move_split
move_split.payload = R_split
```

The installed refinement is:

| item | `R_split(item)` |
| --- | --- |
| `a` | `a_star` |
| `b` | `b_star` |
| `c` | `rest` |
| `d` | `rest` |

D1 repair join gives:

```text
Q1 = repair_join(Q0, R_split)
```

with fibers separating `a` and `b`, while leaving `c,d` together. Therefore:

```text
DeltaCount(Q1, C_split) = 0.
Discharge_split = DeltaCount(Q0, C_split) - DeltaCount(Q1, C_split) = 1.
```

The repair cost is:

```text
cost(rho_2) = 2
repair_budget = 3
```

so the enabled repair family has exact spend `2`, exact remaining budget `1`,
and is budget-feasible.

The generator-ablated variant has the same defect, same challenge schedule, and
same starting state, but `S.R_S` is unreachable for `defect_split`:

```text
NoReachableRepairGenerator(S_ablated, H, C_split, horizon) = True.
```

No `RepairAction` installing `R_split` is lawful in the ablated variant.

### External State And Viability Readout

The finite external coordinate `state.y` is only used to track stress and
collapse in the matched run:

| `state.y` | meaning | declared viability descends? |
| ---: | --- | --- |
| `0` | pre-switch safe state | yes |
| `1` | unresolved split obstruction, residual age 1 | yes |
| `2` | unresolved split obstruction, residual age 2 | yes |
| `3` | unresolved split obstruction, residual age 3 | no |
| `4` | repaired/recovered state | yes |

Without repair after the switch, the matched trajectory is:

```text
t=0: y=0
t=1: y=0
t=2: y=1
t=3: y=2
t=4: y=3
```

With the endogenous repair at `t=2`, the trajectory is:

```text
t=0: y=0
t=1: y=0
t=2: y=4
t=3: y=4
t=4: y=4
```

The carried residual level for the ablated run is:

| horizon | residual level |
| ---: | ---: |
| `0` | `0` |
| `1` | `0` |
| `2` | `1` |
| `3` | `2` |
| `4` | `3` |

`StatusedResidualAccrues` is registered as true exactly at residual levels
`1` and `2`. `CollapsingEvidence` is registered as true at residual level `3`,
where the declared viability probe fails to descend.

### Occurrence And Source-Class Conventions

The enabled repair occurrence is:

```text
rho_2 = RepairTypedAuditEntry.move(move_split.moveRecord, entryClass_2)
entryClass_2.sourceTag    = FineSourceTag.committed_state
entryClass_2.generatedByS = true
entryClass_2.inScope      = true
```

It is present in `H.repairAuditEntries`, passes
`RepairTypedAuditEntryCarried`, is realized by the kernel, and is tied to the
same `move_split` produced by `S.R_S(defect_split)`.

The exact source-tag guard list for `Delta_endo` is the Python
`FineSourceTag` list:

```text
fallback
unknown
contradictory
independent_pair_witness
simulation_trace
ablation_record
```

An entry with one of those tags, or with `generatedByS = false`, or with
`inScope = false`, or not carried, or off-kernel, or omitted from
`H.repairAuditEntries`, is predicted to be counted by `Delta_endo` if it
discharges the `split_ab` obstruction.

### Generator-Reachability Scope Note

The enabled/ablated comparison is not a generator-independent kernel
comparison. E1's status classification is relative to the actual `S.R_S`
reachability and carried repair-family evidence for the run. Round B may use
`repair_world_viability_kernel` as a sanity check on a variant-specific action
registry, but no policy-independent or generator-independent kernel value is
registered as the status classifier. This avoids the E7-style trap of replacing
a policy/run-relative claim with an existential action-set claim.

## 2. Registered Status Predictions

The registered horizons are `0,1,2,3,4`, using the cumulative history up to the
listed horizon. For the switched class `C_split`, binding begins at horizon `2`
because the `split_ab` challenge has recurred, the split-pair obstruction
`{a,b}` is nonempty, the obstruction is declared viability-relevant, and
`MeasuredObstructionSlackThroughout` is false from that point onward.

### Matched Enabled vs Ablated Status Table

| horizon | active challenge | `C_split` binding by horizon? | enabled status | enabled residual | enabled cumulative spend | ablated status | ablated residual |
| ---: | --- | --- | --- | ---: | ---: | --- | ---: |
| `0` | `baseline` | no | `slack` | `0` | `0` | `slack` | `0` |
| `1` | `baseline` | no | `slack` | `0` | `0` | `slack` | `0` |
| `2` | `split_ab` | yes | `endogenously_repairing` | `0` | `2` | `stressed` | `1` |
| `3` | `split_ab` | yes | `endogenously_repairing` | `0` | `2` | `stressed` | `2` |
| `4` | `split_ab` | yes | `endogenously_repairing` | `0` | `2` | `collapsing` | `3` |

Registered prediction: the ablated variant lands in `{stressed, collapsing}`
exactly at horizons `{2,3,4}`, which are exactly the horizons where the
`split_ab` challenge binds. It is `slack` before the challenge binds.

For the enabled variant, the set of `ChallengedEpisodeTime` values with a
`C_split` obstruction witness is exactly:

```text
{2}
```

The endogenous repair family must be defined at `t=2`, and the single defined
entry must satisfy `EndogenousRepairOccurrence`, `InstallsRepairJoin`, and
`StrictChallengeDescent`. There are no remaining obstruction-witness episodes
for `C_split` after the repair.

For the ablated variant, the obstruction persists, so:

```text
ChallengedEpisodeTime(C_split) = {2,3,4}
EndogenousRepairFamilyValid = False
NoReachableRepairGenerator = True
```

## 3. Delta-Discharge Predictions

### Enabled Variant

At the binding episode:

| time | pre-repair quotient | pre `DeltaCount` | repair | post quotient | post `DeltaCount` | discharge |
| ---: | --- | ---: | --- | --- | ---: | ---: |
| `2` | `Q0` | `1` | `R_split` | `Q1 = Q0 vee R_split` | `0` | `1` |

Total enabled discharge over the run is exactly:

```text
1.
```

### Ablated Variant

The ablated variant never installs a repair refinement:

| time | quotient | `DeltaCount(C_split)` | discharge |
| ---: | --- | ---: | ---: |
| `2` | `Q0` | `1` | `0` |
| `3` | `Q0` | `1` | `0` |
| `4` | `Q0` | `1` | `0` |

Total ablated discharge over the run is exactly:

```text
0.
```

The measured-discharge bridge used by the enabled branch is therefore:

```text
MeasuredObstructionDischarge = True
MeasuredDischargeExcludesResidualAccrual = True
StatusedResidualAccrues = False
```

For the ablated horizons `2` and `3`:

```text
MeasuredObstructionDischarge = False
StatusedResidualAccrues = True
```

For ablated horizon `4`:

```text
ViabilityProbesDescendAtH = False
CollapsingEvidence = True
```

## 4. Source-Class Census Predictions

### Genuine Enabled Repair

Across the enabled run, exactly one refinement is installed:

| count item | predicted count |
| --- | ---: |
| installed refinements | `1` |
| `FineSourceTag.committed_state` | `1` |
| `generatedByS = true` | `1` |
| `inScope = true` | `1` |
| carried by `RepairTypedAuditEntryCarried` | `1` |
| realized by `S.T.suppK` | `1` |
| present in `H.repairAuditEntries` | `1` |
| `Delta_endo` entries | `0` |

All bad-source counters are registered as zero:

```text
fallback = 0
unknown = 0
contradictory = 0
independent_pair_witness = 0
simulation_trace = 0
ablation_record = 0
generatedByS_false = 0
inScope_false = 0
not_carried = 0
off_kernel = 0
audit_omitted = 0
```

### Ablated Variant

The ablated variant installs no refinements:

```text
installed refinements = 0
committed_state repairs = 0
Delta_endo entries = 0
```

It is not externally subsidized in the registered main run; it is stressed or
collapsing because the binding obstruction remains undischarged.

### External-Subsidy Control

The external-subsidy control installs the same mathematical refinement
`R_split` at `t=2`, but with non-endogenous source evidence:

```text
sourceTag    = FineSourceTag.fallback
generatedByS = false
inScope      = true
```

Registered predictions:

| quantity | predicted value |
| --- | ---: |
| pre `DeltaCount` | `1` |
| post `DeltaCount` | `0` |
| discharge | `1` |
| `Delta_endo` count | `1` |
| `EndogenouslyRepairingHolds` | `False` |
| status | `externally_subsidized` |

This control checks E1's source-internality claim: a discharging repair with
fallback or generated-outside-`S` provenance is a subsidy, not endogenous
source-repair.

## 5. Budget Spend Predictions

The registered repair budget is:

```text
repair_budget = 3.
```

The enabled family has one repair entry at `t=2`:

| time | repair | cost | cumulative spend | budget feasible? |
| ---: | --- | ---: | ---: | --- |
| `0` | none | `0` | `0` | yes |
| `1` | none | `0` | `0` | yes |
| `2` | `rho_2` | `2` | `2` | yes |
| `3` | none | `0` | `2` | yes |
| `4` | none | `0` | `2` | yes |

Registered prediction:

```text
FamilyBudgetFeasibleInLambda = True
total_spend = 2
remaining_budget = 1
```

The ablated main run spends:

```text
total_spend = 0
```

and still fails to discharge the binding obstruction.

## 6. Null And Control Predictions

### Same-Family Saturation Null

The same-family fake repair is:

| item | `R_same(item)` |
| --- | --- |
| `a` | `u` |
| `b` | `u` |
| `c` | `v` |
| `d` | `v` |

This is only a reparameterization of the current quotient closure
`Sigma_Qt`. D1 join with `R_same` does not split the challenged pair:

```text
Q_same = repair_join(Q0, R_same)
DeltaCount(Q_same, C_split) = 1
discharge = 0
StrictChallengeDescent = False
StrictSelfExtension = False
EndogenousRepairFamilyValid = False
```

Registered status for the same-family-null run, with no genuine repair also
present, is:

```text
horizon 2: stressed
```

It must not be counted as `endogenously_repairing`.

### Schedule-Trap Null

The schedule-trap control directly switches the quotient from `Q0` to `Q1` at
`t=2` through an exogenous schedule variable rather than a carried
`RepairAction`. The support entry is explicitly marked as:

```text
sourceTag    = FineSourceTag.simulation_trace
generatedByS = false
inScope      = true
```

and is not listed as a genuine endogenous repair family entry.

Registered predictions:

| quantity | predicted value |
| --- | ---: |
| pre `DeltaCount` | `1` |
| post `DeltaCount` | `0` |
| measured discharge | `1` |
| `NoScheduleTrap` | `False` |
| `Delta_endo` count | `1` |
| `EndogenouslyRepairingHolds` | `False` |
| status | `externally_subsidized` |

This control is the schedule-trap falsifier: a scripted switch may discharge
the obstruction, but it is not an endogenous source-repair.

### Audit-Omission Control

The audit-omission control uses a mathematically correct `R_split` discharge
but omits the discharging occurrence from `H.repairAuditEntries`.

Registered predictions:

```text
discharge = 1
entry in H.repairAuditEntries = False
Delta_endo count = 1
EndogenouslyRepairingHolds = False
status = externally_subsidized
```

This control checks the D5 completeness side of E1: a repair that is not in the
complete repair audit history cannot be credited as endogenous.

## 7. Falsification Conditions

The following outcomes falsify the corresponding registered predictions.

1. Challenge switching is falsified if `challenge_at(t,y)` does not return
   `baseline` at `t=0,1` and `split_ab` at `t=2,3,4` for the registered
   binding states.

2. Split-pair measurement is falsified if `DeltaCount(Q0, C_split) != 1`, if
   `DeltaCount(Q1, C_split) != 0`, or if the baseline challenge has nonzero
   obstruction.

3. The enabled internalization prediction is falsified if the enabled run does
   not have status `endogenously_repairing` at horizons `2,3,4`, if its
   `ChallengedEpisodeTime(C_split)` set is not exactly `{2}`, or if its single
   family entry fails `EndogenousRepairOccurrence`, `InstallsRepairJoin`, or
   `StrictChallengeDescent`.

4. The ablated comparison is falsified if the ablated run is not `slack` at
   horizons `0,1`, not `stressed` at horizons `2,3`, or not `collapsing` at
   horizon `4`. It is also falsified if the ablated run is ever classified as
   `endogenously_repairing` or `externally_subsidized` in the main matched run.

5. THEOREMS.md's registered prediction is falsified for this instance if the
   ablated variant lands outside `{stressed, collapsing}` at any binding
   horizon in `{2,3,4}`, or if it lands inside `{stressed, collapsing}` before
   the challenge binds.

6. Delta-discharge is falsified if enabled discharge at `t=2` is not exactly
   `1`, if enabled total discharge is not exactly `1`, or if ablated total
   discharge is not exactly `0`.

7. Source-class census is falsified if the enabled repair has any source tag
   other than `committed_state`, if `generatedByS` or `inScope` is false, if
   the repair is not carried, if it is not kernel-realized, if it is omitted
   from `H.repairAuditEntries`, or if `Delta_endo` is nonempty for the enabled
   main run.

8. Budget feasibility is falsified if enabled total spend is not exactly `2`,
   if remaining budget is not exactly `1`, or if
   `FamilyBudgetFeasibleInLambda` is false for the enabled family.

9. The external-subsidy control is falsified if the fallback/generated-outside
   discharge is counted as `endogenously_repairing`, if `Delta_endo` does not
   count exactly one offending occurrence, or if the status is not
   `externally_subsidized`.

10. The same-family saturation null is falsified if `R_same` reduces
    `DeltaCount`, if `StrictChallengeDescent` is true, if
    `StrictSelfExtension` is true, or if the run is counted as
    `endogenously_repairing`.

11. The schedule-trap null is falsified if an exogenous quotient switch with
    `sourceTag = simulation_trace` and `generatedByS = false` is credited as
    endogenous repair, if `NoScheduleTrap` remains true, or if `Delta_endo`
    does not count exactly one offending occurrence.

12. The audit-omission control is falsified if a discharging occurrence omitted
    from `H.repairAuditEntries` is credited as endogenous repair, or if
    `Delta_endo` does not count exactly one audit-omitted occurrence.

13. The generator-reachability discipline is falsified if the Round B
    implementation classifies the enabled/ablated statuses by a
    generator-independent existential kernel rather than by the variant's
    actual `S.R_S` reachability and carried repair-family evidence.

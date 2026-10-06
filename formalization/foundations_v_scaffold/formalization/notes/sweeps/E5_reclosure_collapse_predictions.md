# E5 Reclosure Collapse Law - Toy-Lab Predictions (Round A, pre-registration)

This document pre-registers the toy-lab probe for E5 before any E5 sweep
implementation exists. It is grounded in the accepted six-field normal form
`formalization/notes/examples/E5.md` and the mechanized Lean module
`lean/SixBirdsFoundationsV/Laws/E5ReclosureCollapse.lean`.

The probe mirrors the Lean predicates, not a looser prose reading. In
particular, a collapse falsifier requires a declared self-scope rescue
candidate that is both admissible/in budget and credited for descent by the
candidate's own `CollapseMoveRecord`; collapse requires a complete declared
rescue inventory; subsidy is external-only; and irreversibility requires the
coherent reachability/kernel pair.

All quantities below are exact rationals, written as fractions. Round B must
use `fractions.Fraction` and no floating-point arithmetic or randomness.

### Post-registration addition (disclosed, step-5 methodology review)

The step-5 methodology review found that Case Enumeration item 2 ("Viable
apparatus reclosure") was not literally exercised. The original registration
had positive apparatus-reclosure coverage only under `scn_revived_new_lineage`,
whose top-priority `revived` branch deliberately masks the lower-priority
`ViableCase` path. This disclosed addition registers
`scn_viable_apparatus_reclosure`, a standalone E3 `MaintenanceReinstatementFor`
rescue with no prior collapsed/subsidized lineage witness and no residual
accrual, predicted `viable`. The outcome is forced by the already-landed E5
definitions; this is a coverage addition, not a fit-to-result change.

## 1. Toy-Lab Configuration

### Carrier, scope, and ledger

The carrier is the shared Repair-World ring fixture used by the existing
Foundation V sweeps:

```text
Z = {0, 1, ..., 17}
S.T.suppK(z, z') := z' = (z + 1) mod 18
```

The main collapse scope is:

```text
challengeClass = C_collapse
horizon = h0
horizon_after_withdrawal = h1
```

The toy ledger contains the exact entries named below:

```text
budget_1, budget_1_2, budget_1_4, spend_1_5, spend_1_4,
spend_1_3, spend_1_2, spend_3_2, spend_5_4,
repair_audit, boundary_audit, reclosure_audit, acquisition_audit,
status_audit, subsidy_audit, suspension_audit, lineage_audit
```

Every positive carried record uses one of the admissible source tags
`committed_state` or `audited_cell_records`, `generatedByS = true`, and
`inScope = true`. The fallback control intentionally violates this discipline.

### Declared viability probes and descent attribution

The declared probe-family record is `probe_family_collapse`. It contains two
finite readouts computed from the concrete fixture:

```text
delta_split_count : number of declared split pairs remaining under the current quotient
budget_margin     : budget - spend for the credited move
```

The descent readout for a rescue move is:

```text
DescentReadout(moveRecord, pre_delta, post_delta, spend, budget)
```

`RescueMoveCreditedForDescent(moveRecord, readout)` is computed, not asserted:

```text
readout.moveRecord = moveRecord
and readout.post_delta < readout.pre_delta
and readout.budget_margin = readout.budget - readout.spend
```

The global `ViabilityProbesDescendAtH.holds(S,H,C,horizon)` certificate is
therefore not sufficient by itself in the sweep. A candidate descends only when
its own move record is credited by its own readout. This is the toy-lab guard
against the proof-irrelevance/unlinked-descent bug fixed during E5's Lean setup
review.

### Move records

| move record | kind | source/target or payload | spend | budget | pre_delta | post_delta | credited descent |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `mv_repair_viable` | `repair` | E1 repair, `2 -> 3` | `1/4` | `1` | `2` | `0` | true |
| `mv_repair_stressed` | `repair` | E1 repair, `4 -> 5` | `1/3` | `1` | `2` | `0` | true |
| `mv_boundary_viable` | `boundary_update` | boundary `16 -> 17` | `1/5` | `1` | `2` | `0` | true |
| `mv_acquisition_viable` | `acquisition` | strict probe acquisition, `probe_stabilizer` | `1/4` | `1` | `2` | `0` | true |
| `mv_reclosure_viable` | `apparatus_reclosure` | E3 reclosure, `5 -> 6`, no prior lineage | `1/2` | `1` | `2` | `0` | true |
| `mv_self_sub_no_descent` | `repair` | E1 repair, `6 -> 7` | `1/4` | `1` | `1` | `1` | false |
| `mv_self_sub_over_budget` | `repair` | E1 repair, `7 -> 8` | `3/2` | `1` | `2` | `0` | true |
| `mv_external_subsidy` | `repair` (subsidizer scope) | external carrier, `S_ext`, `7 -> 8` | `1/2` | `1` | `2` | `0` | true |
| `mv_suspended_probe` | `repair` | not attempted; operations gated off | `0` | `0` | `0` | `0` | false |
| `mv_recover_no_descent` | `repair` | E1 repair, `8 -> 9` | `1/4` | `1` | `1` | `1` | false |
| `mv_recover_over_budget` | `repair` | E1 repair, `9 -> 10` | `5/4` | `1` | `2` | `0` | true |
| `mv_recover_off_kernel_boundary` | `boundary_update` | boundary `8 -> 10` | `1/4` | `1` | `2` | `0` | true |
| `mv_irrev_no_descent` | `repair` | E1 repair, `11 -> 12` | `1/4` | `1` | `1` | `1` | false |
| `mv_irrev_over_budget_acquisition` | `acquisition` | strict probe acquisition | `3/2` | `1` | `2` | `0` | true |
| `mv_reclosure_revived` | `apparatus_reclosure` | E3 reclosure, `10 -> 11`, new lineage | `1/2` | `1` | `2` | `0` | true |
| `mv_post_withdrawal_repair` | `repair` | E1 repair, `12 -> 13` | `1/4` | `1` | `2` | `0` | true |
| `mv_ctrl_over_budget` | `repair` | E1 repair, `13 -> 14` | `3/2` | `1` | `2` | `0` | true |
| `mv_ctrl_unlinked_candidate` | `repair` | E1 repair, `14 -> 15` | `1/4` | `1` | `2` | `0` | false |
| `mv_ctrl_unlinked_named` | `repair` | readout names this different record | `1/4` | `1` | `2` | `0` | true |
| `mv_ctrl_fallback` | `repair` | E1-shaped repair, `15 -> 16` | `1/4` | `1` | `2` | `0` | true but uncarried |

The boundary record for `mv_recover_off_kernel_boundary` has:

```text
preBoundary.sourceState = 8
postBoundary.targetState = 10
S.T.suppK(8, 10) = false
```

The legal ring successor of `8` is `9`, so the boundary candidate is rejected
because kernel realization fails, not because the descent readout is missing.
It never enters any scenario's `CompleteCollapseRescueInventory.declaredCandidates`
list because no `BoundaryUpdateCandidate` value exists for it.

The positive boundary row uses a separate legal boundary update:

```text
mv_boundary_viable.preBoundary.sourceState = 16
mv_boundary_viable.postBoundary.targetState = 17
S.T.suppK(16, 17) = true
```

This is the registered positive coverage for the boundary-update rescue family.

### Complete rescue inventories

Each scenario has a finite constructor universe and a declared inventory. The
Round B sweep must compute `CompleteCollapseRescueInventory.complete` by
comparing the generated constructible self-scope candidates for that scenario
against the declared list. It must not treat omission from the list as collapse
evidence.

| scope | declared self-scope candidates | complete inventory | collapse falsifier | collapsed core |
| --- | --- | --- | --- | --- |
| `scn_viable_self_repair` | `mv_repair_viable` | true | true | false |
| `scn_stressed_self_repair` | `mv_repair_stressed` | true | true | false |
| `scn_viable_boundary_update` | `mv_boundary_viable` | true | true | false |
| `scn_viable_acquisition` | `mv_acquisition_viable` | true | true | false |
| `scn_viable_apparatus_reclosure` | `mv_reclosure_viable` | true | true | false |
| `scn_subsidized_external_rescue` | `mv_self_sub_no_descent`, `mv_self_sub_over_budget` | true | false | true |
| `scn_suspended_gated_operations` | empty | true | false | not used by branch |
| `scn_collapsed_recoverable` | `mv_recover_no_descent`, `mv_recover_over_budget` | true | false | true |
| `scn_collapsed_irreversible` | `mv_irrev_no_descent`, `mv_irrev_over_budget_acquisition` | true | false | true |
| `scn_revived_new_lineage` | `mv_reclosure_revived` | true | true | false |
| `scn_post_withdrawal_reclassified` | `mv_post_withdrawal_repair` | true | true | false |
| `ctrl_incomplete_inventory_attempt` | empty, while `mv_repair_viable` is constructible | false | not creditable |

### Reachability and apparatus-kernel certificates

The reachability/kernel input is certified host data, but the toy-lab values
are computed from declared finite surfaces.

| record pair | unreachable | selfReachable | externallyReachableOnly | kernelEmpty | kernelNonempty | coherence | role |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `reach_recover`, `kernel_recover` | false | true | false | false | true | true | recoverable collapse |
| `reach_irrev`, `kernel_irrev` | true | false | false | true | false | true | irreversible collapse |
| `reach_inconsistent`, `kernel_nonempty_bad` | true | false | false | false | true | false | coherence control |

Coherence is the actual equivalence
`reach.unreachable <-> kernel.kernelEmpty`. The inconsistent row must be
structurally rejected for `IrreversibleCollapseInput`.

### Residual, suspension, subsidy, and lineage records

| record | exact values | scope | predicted use |
| --- | --- | --- | --- |
| `residual_stressed` | `residualSpend = 1/5`, `residualBudget = 1/2` | `(C_collapse, h0)` | statused residual for stressed |
| `residual_wrong_scope` | `residualSpend = 1/5`, `residualBudget = 1/2` | `(C_other, h0)` | ignored for viable/stressed split |
| `subsidy_ext_1` | external carrier `S_ext`, move `mv_external_subsidy` | `(C_collapse, h0)` | active subsidy |
| `withdraw_subsidy_ext_1` | prior subsidy `subsidy_ext_1` | transition `h0 -> h1` | subsidy withdrawal |
| `suspension_ops_gate` | apparatus intact, operations gated off, no binding challenge | `(C_collapse, h0)` | suspended |
| `lineage_revived` | old `lineage_subsidized_v1`, new `lineage_reclosed_v2` | `(C_collapse, h0)` | revived |

`operations_gated_off` is computed from a concrete operation schedule with no
enabled transitions in the operational gate list at `h0 = 3`:

| time | operation | enabled |
| ---: | --- | --- |
| `3` | `self_repair` | false |
| `3` | `boundary_update` | false |
| `3` | `apparatus_reclosure` | false |
| `3` | `acquisition` | false |

`apparatus_intact` is computed by reusing E3's `apparatus_distance` helper on
two concrete apparatus records:

| apparatus | gate_instrument | threshold_records | app_boundary | audit_data |
| --- | --- | --- | ---: | ---: |
| `app_suspend_baseline` | `gate_collapse` | `("theta_stay", "theta_budget")` | `6` | `4` |
| `app_suspend_current` | `gate_collapse` | `("theta_stay", "theta_budget")` | `6` | `4` |

The computed distance is `0/8`, so the apparatus is intact. The binding
challenge schedule is:

| time | challenge | binding |
| ---: | --- | --- |
| `2` | `C_collapse` | true |
| `3` | `C_collapse` | false |
| `3` | `C_background_noise` | false |

Thus `BindingOperationalChallengeActive(S,H,C_collapse,h0)` is false by
schedule lookup, not by an ignored boolean flag.

The collapsed-recoverable scenario also carries ordinary low-level activity
that is deliberately not a rescue candidate:

| time | activity | source | target | `S.T.suppK` | rescue move? |
| ---: | --- | ---: | ---: | --- | --- |
| `3` | `ordinary_tick` | `0` | `1` | true | false |

This row covers the active-collapsed-system case: ordinary lawful activity can
continue while `CollapseFalsifier` remains false.

### E3 and E6/E9 reuse points

`mv_reclosure_viable` is a standalone E3-style apparatus reclosure candidate:

```text
MaintenanceReinstatementRecord.source_state = 5
MaintenanceReinstatementRecord.target_state = 6
S.T.suppK(5, 6) = true
app_tplus1 = operator.apply(5)
reclosureMoveRef(record) = mv_reclosure_viable
prior collapsed/subsidized lineage witness = absent
```

This is the registered positive coverage for the lower-priority viable
apparatus-reclosure path.

`mv_reclosure_revived` is a separate E3-style apparatus reclosure candidate:

```text
MaintenanceReinstatementRecord.source_state = 10
MaintenanceReinstatementRecord.target_state = 11
S.T.suppK(10, 11) = true
app_tplus1 = operator.apply(10)
reclosureMoveRef(record) = mv_reclosure_revived
```

Acquisition rows use the E6/E9 probe-shop discipline:

```text
LawfulAcquisition = true only when pre/post active-family records are carried
CandidateAcquisition = true only when catalog membership, strictness,
BudgetFeasible, and risk admissibility all hold
BudgetFeasible = spend <= budget
```

For `mv_acquisition_viable`, the concrete acquisition fixture is:

```text
pre active family  = L_base = {probe_base: 1}
new probe          = probe_stabilizer
post active family = L_stabilized = {probe_base: 1, probe_stabilizer: 1/4}
probe_stabilizer in catalog = true
AcquisitionStrict(L_base, probe_stabilizer, L_stabilized) = true
BudgetFeasible = 1/4 <= 1
riskAdmissible(probe_stabilizer) = true
```

This is the registered positive coverage for the acquisition rescue family.

## 2. Registered Theorem-Facing Predictions

| theorem | concrete instantiation | registered prediction |
| --- | --- | --- |
| `E5_CollapseFalsifier` | `scn_viable_self_repair`, `mv_repair_viable` | `CollapseFalsifier = true`, `CollapsedCore = false` |
| `E5_CollapseFalsifier` | `scn_viable_boundary_update`, `mv_boundary_viable` | `CollapseFalsifier = true`, `CollapsedCore = false` |
| `E5_CollapseFalsifier` | `scn_viable_acquisition`, `mv_acquisition_viable` | `CollapseFalsifier = true`, `CollapsedCore = false` |
| `E5_CollapseFalsifier` | `scn_viable_apparatus_reclosure`, `mv_reclosure_viable` | `CollapseFalsifier = true`, `CollapsedCore = false` |
| `E5_CollapseFalsifier` | `ctrl_over_budget_descent`, `mv_ctrl_over_budget` | `CollapseRescueDescends = true`, `CollapseRescueAdmissibleInBudget = false`, `CollapseFalsifier = false` |
| `E5_ReclosureCollapse` | all registered status scenarios below | exactly one status holds for each scenario |
| `E5_IrreversibleCollapse` | `scn_collapsed_irreversible`, `reach_irrev`, `kernel_irrev` | `CollapsedIrreversibleHolds = true` |
| `E5_SubsidyWithdrawalReclassification` | `scn_subsidized_external_rescue @ h0` then `scn_post_withdrawal_reclassified @ h1` | `SubsidizedHolds(h1) = false`, post-withdrawal status is `viable` |

Positive rescue-family coverage is registered as follows:

| rescue family | positive row | status produced |
| --- | --- | --- |
| repair | `scn_viable_self_repair` | `viable` |
| boundary update | `scn_viable_boundary_update` | `viable` |
| apparatus reclosure | `scn_viable_apparatus_reclosure` | `viable` |
| acquisition | `scn_viable_acquisition` | `viable` |

`scn_revived_new_lineage` remains the separate priority-override check: it
uses apparatus reclosure plus a prior subsidized/collapsed lineage witness and
therefore must classify as `revived`, not `viable`.

## 3. Registered Status Scenarios

### `scn_viable_self_repair`

| field | predicted value |
| --- | --- |
| carried status record | `status_viable_self_repair`, status `viable` |
| declared rescue inventory complete | true |
| credited rescue move | `mv_repair_viable` |
| `CollapseRescueAdmissibleInBudget` | true (`1/4 <= 1`) |
| `CollapseRescueDescends` | true (`2 > 0`, readout names `mv_repair_viable`) |
| scoped statused residual exists | false |
| `CollapseFalsifier` | true |
| predicted status | `viable` |

### `scn_stressed_self_repair`

| field | predicted value |
| --- | --- |
| carried status record | `status_stressed_self_repair`, status `stressed` |
| declared rescue inventory complete | true |
| credited rescue move | `mv_repair_stressed` |
| `CollapseRescueAdmissibleInBudget` | true (`1/3 <= 1`) |
| `CollapseRescueDescends` | true (`2 > 0`, readout names `mv_repair_stressed`) |
| scoped statused residual exists | true (`1/5 <= 1/2`, scope `(C_collapse, h0)`) |
| `CollapseFalsifier` | true |
| predicted status | `stressed` |

### `scn_viable_boundary_update`

| field | predicted value |
| --- | --- |
| carried status record | `status_viable_boundary_update`, status `viable` |
| declared rescue inventory complete | true |
| credited rescue move | `mv_boundary_viable` |
| pre/post boundary states | `16 -> 17` |
| `S.T.suppK(16, 17)` | true |
| `BoundaryUpdateCandidate` constructible | true |
| `CollapseRescueAdmissibleInBudget` | true (`1/5 <= 1`) |
| `CollapseRescueDescends` | true (`2 > 0`, readout names `mv_boundary_viable`) |
| scoped statused residual exists | false |
| `CollapseFalsifier` | true |
| predicted status | `viable` |

### `scn_viable_acquisition`

| field | predicted value |
| --- | --- |
| carried status record | `status_viable_acquisition`, status `viable` |
| declared rescue inventory complete | true |
| credited rescue move | `mv_acquisition_viable` |
| `LawfulAcquisition` | true |
| `CandidateAcquisition` | true |
| `BudgetFeasible` | true (`1/4 <= 1`) |
| `AcquisitionStrict` | true (`probe_stabilizer` newly enters the active support) |
| `CollapseRescueDescends` | true (`2 > 0`, readout names `mv_acquisition_viable`) |
| scoped statused residual exists | false |
| `CollapseFalsifier` | true |
| predicted status | `viable` |

### `scn_viable_apparatus_reclosure`

| field | predicted value |
| --- | --- |
| carried status record | `status_viable_apparatus_reclosure`, status `viable` |
| declared rescue inventory complete | true |
| credited rescue move | `mv_reclosure_viable` |
| `MaintenanceReinstatementFor` | true |
| reinstatement source/target | `5 -> 6`, with `S.T.suppK(5, 6) = true` |
| `CollapseRescueAdmissibleInBudget` | true (`1/2 <= 1`) |
| `CollapseRescueDescends` | true (`2 > 0`, readout names `mv_reclosure_viable`) |
| prior collapsed/subsidized lineage witness | absent |
| `RevivedCase` | false |
| scoped statused residual exists | false |
| `CollapseFalsifier` | true |
| predicted status | `viable` |

This is the standalone viable apparatus-reclosure case. It deliberately has no
`RevivalWitness`, so the lower-priority `ViableCase` must be the branch that
classifies it.

### `scn_subsidized_external_rescue`

| field | predicted value |
| --- | --- |
| carried status record | `status_subsidized_external_rescue`, status `subsidized` |
| declared rescue inventory complete | true |
| self-scope in-budget descending move exists | false |
| external subsidy witness | `subsidy_ext_1` |
| external move descends | true (`mv_external_subsidy`, `2 > 0`) |
| external move budget feasible | true (`1/2 <= 1`) |
| `notSelfCarried` | true (`mv_external_subsidy` differs from every constructible self-scope move record) |
| predicted status | `subsidized` |

This is explicitly an external-only subsidy case. The self inventory contains a
non-descending self move and an over-budget descending self move, so no
self-scope falsifier exists.

### `scn_suspended_gated_operations`

| field | predicted value |
| --- | --- |
| carried status record | `status_suspended_gated_operations`, status `suspended` |
| apparatus intact | true |
| operations gated off | true |
| binding operational challenge active | false |
| revived/subsidized higher-priority branches | false |
| predicted status | `suspended` |

The fixture computes `operations_gated_off` from the operation gate schedule.
This row must not be implemented as a disconnected flag.

### `scn_collapsed_recoverable`

| field | predicted value |
| --- | --- |
| carried status record | `status_collapsed_recoverable`, status `collapsed_recoverable` |
| declared rescue inventory complete | true |
| in-budget descending self move exists | false |
| `CollapsedCore` | true |
| ordinary low-level activity present | true (`ordinary_tick`, `0 -> 1`, `S.T.suppK(0, 1) = true`) |
| ordinary activity is a rescue candidate | false |
| reachability input | `reach_recover.selfReachable = true`, `unreachable = false` |
| kernel input | `kernel_recover.kernelNonempty = true`, `kernelEmpty = false` |
| `IrreversibilityCoherence` | true (`false <-> false`) |
| `RecoverableCollapseInput` | true |
| predicted status | `collapsed_recoverable` |

### `scn_collapsed_irreversible`

| field | predicted value |
| --- | --- |
| carried status record | `status_collapsed_irreversible`, status `collapsed_irreversible` |
| declared rescue inventory complete | true |
| in-budget descending self move exists | false |
| `CollapsedCore` | true |
| reachability input | `reach_irrev.unreachable = true` |
| kernel input | `kernel_irrev.kernelEmpty = true`, `kernelNonempty = false` |
| `IrreversibilityCoherence` | true (`true <-> true`) |
| `IrreversibleCollapseInput` | true |
| predicted status | `collapsed_irreversible` |

### `scn_revived_new_lineage`

| field | predicted value |
| --- | --- |
| carried status record | `status_revived_new_lineage`, status `revived` |
| prior status reference | `prior_subsidized_or_collapsed_1` |
| prior status accepted by predicate | true (`subsidized` or collapsed prior record) |
| lineage changed | true (`lineage_subsidized_v1 != lineage_reclosed_v2`) |
| credited reclosure move | `mv_reclosure_revived` |
| `MaintenanceReinstatementFor` | true |
| `CollapseRescueAdmissibleInBudget` | true (`1/2 <= 1`) |
| `CollapseRescueDescends` | true (`2 > 0`, readout names `mv_reclosure_revived`) |
| predicted status | `revived` |

Revival has highest priority. Even though the fresh reclosure move is a
self-scope rescue, the row is classified as `revived`, not merely `viable`.

### `scn_post_withdrawal_reclassified`

| field | predicted value |
| --- | --- |
| before withdrawal | `SubsidizedHolds(scn_subsidized_external_rescue, h0) = true` |
| withdrawal event | `withdraw_subsidy_ext_1`, carried and linked to `subsidy_ext_1` |
| active external subsidy at `h1` | false |
| `NoActiveExternalSubsidyAt(h1)` | true |
| post-withdrawal self move | `mv_post_withdrawal_repair` |
| post-withdrawal self move budget/descent | true (`1/4 <= 1`, `2 > 0`) |
| `SubsidizedHolds(h1)` | false |
| predicted post-withdrawal status | `viable` |

This is the registered discontinuity instance for
`E5_SubsidyWithdrawalReclassification`. Withdrawal does not force irreversible
collapse; it forces recomputation under the post-withdrawal complete
classifier.

## 4. Null and Control Predictions

### `ctrl_over_budget_descent`

| field | predicted value |
| --- | --- |
| move | `mv_ctrl_over_budget` |
| `CollapseRescueDescends` | true (`2 > 0`, readout names `mv_ctrl_over_budget`) |
| `CollapseBudgetFeasible` | false (`3/2 <= 1` is false) |
| `CollapseRescueAdmissibleInBudget` | false |
| `CollapseFalsifier` | false |
| collapse defeated? | false |

### `ctrl_unlinked_descent_certificate`

| field | predicted value |
| --- | --- |
| candidate move | `mv_ctrl_unlinked_candidate` |
| descent readout move | `mv_ctrl_unlinked_named` |
| `moveRecordLinked` | false |
| `RescueMoveCreditedForDescent(mv_ctrl_unlinked_candidate, readout)` | false |
| `CollapseRescueCandidate` value exists | false |
| `CollapseRescueDescends` callable on this fixture object | no; there is no constructed candidate value |

This control targets the exact proof-irrelevance/unlinked-descent bug fixed in
Lean. A global descent-looking certificate for a different move must not credit
this fixture object, and the mismatched move/readout pair must fail before it
enters any declared candidate inventory.

### `ctrl_off_kernel_boundary`

| field | predicted value |
| --- | --- |
| move | `mv_recover_off_kernel_boundary` |
| pre source | `8` |
| post target | `10` |
| `S.T.suppK(8, 10)` | false |
| budget/descent readout | true (`1/4 <= 1`, `2 > 0`) |
| `BoundaryUpdateCandidate` constructible | false |
| collapse defeated? | false |

The candidate fails because the linked boundary records do not realize a kernel
step. The sweep must compute this from `ring_kernel(18)`. Because no
`BoundaryUpdateCandidate` value exists, this fixture object never appears in
any scenario's declared rescue inventory.

### `ctrl_fallback_uncarried`

| field | predicted value |
| --- | --- |
| move | `mv_ctrl_fallback` |
| source tag | `fallback` |
| generatedByS | false |
| inScope | false |
| budget/descent data | otherwise feasible and descending |
| carried occurrence accepted | false |
| collapse defeated? | false |

This verifies that an untrusted or out-of-scope repair-shaped object cannot
become a self-scope rescue candidate.

### `ctrl_inconsistent_irreversibility`

| field | predicted value |
| --- | --- |
| reach record | `reach_inconsistent.unreachable = true` |
| kernel record | `kernel_nonempty_bad.kernelEmpty = false`, `kernelNonempty = true` |
| `IrreversibilityCoherence` | false (`true <-> false` is false) |
| `IrreversibleCollapseInput` | false |
| `CollapsedIrreversibleHolds` | false |

This checks that the reachability/kernel equivalence is not decorative.

### `ctrl_wrong_scope_residual`

| field | predicted value |
| --- | --- |
| residual record | `residual_wrong_scope` |
| residual scope | `(C_other, h0)` |
| evaluated scope | `(C_collapse, h0)` |
| `StatusedResidualAccrual(S, C_collapse, h0)` | false |
| effect on `scn_viable_self_repair` | remains `viable`, not `stressed` |

This guards the scoped-residual fix from the six-field review. A residual in an
unrelated challenge class cannot reclassify the current E5 scope.

### `ctrl_incomplete_inventory_attempt`

| field | predicted value |
| --- | --- |
| declared candidates | empty |
| constructible self move omitted | `mv_repair_viable` |
| generated constructible candidate set equals declared list | false |
| `CompleteCollapseRescueInventory` | false |
| any `...Holds` wrapper may be concluded from this inventory | false |

This checks that collapse cannot be obtained by omitting a real rescue
candidate from the declared inventory.

## 5. Scope Note: Actual Carried Rescue Inventory vs. Existential Possible Move

The predictions are about the actual carried rescue candidates, subsidy
records, suspension records, lineage records, reachability records, kernel
records, and status records exposed by the finite toy-lab fixture. They are not
claims that some abstract move could be imagined.

Round B must compute:

```text
CollapseRescueAdmissibleInBudget
CollapseRescueDescends
CollapseFalsifier
CollapsedCore
BoundaryUpdateCandidate kernel realization
LawfulAcquisition
CandidateAcquisition
StatusedResidualAccrual
IrreversibilityCoherence
RecoverableCollapseInput
IrreversibleCollapseInput
SubsidizedEvidence notSelfCarried
SuspensionWitness
ordinary activity vs. rescue-candidate membership
RevivalWitness lineageChanged
CompleteReclosureCollapseStatus
```

from the fixture data. It must never hardcode a status label or a control
verdict from this document.

## 6. Falsification Conditions

1. `scn_viable_self_repair` is falsified if `mv_repair_viable` is not computed
   as an admissible in-budget descending self rescue, or if the status is not
   exactly `viable`.
2. `scn_stressed_self_repair` is falsified if the scoped residual
   `residual_stressed` is not what separates `stressed` from `viable`, or if
   the status is not exactly `stressed`.
3. `scn_viable_boundary_update` is falsified if `S.T.suppK(16, 17)` is not
   computed from the ring kernel, if the legal boundary update is not
   constructible, or if the status is not exactly `viable`.
4. `scn_viable_acquisition` is falsified if `LawfulAcquisition`,
   `CandidateAcquisition`, `AcquisitionStrict`, or exact `BudgetFeasible`
   fails for `mv_acquisition_viable`, or if the status is not exactly
   `viable`.
5. `scn_viable_apparatus_reclosure` is falsified if the E3
   `MaintenanceReinstatementFor` witness is not checked, if a prior
   collapsed/subsidized lineage witness is attached, if `RevivedCase` fires, or
   if the status is not exactly `viable`.
6. `scn_subsidized_external_rescue` is falsified if a self-scope rescue
   falsifier exists, if `mv_external_subsidy` matches a self move record, or if
   the status is not exactly `subsidized`.
7. `scn_suspended_gated_operations` is falsified if suspension is credited
   without all three facts: apparatus intact, operations gated off, and no
   binding operational challenge.
8. `scn_collapsed_recoverable` is falsified if any declared self candidate is
   both in budget and credited for descent, or if recoverability is accepted
   without coherent reachability/kernel evidence.
9. `scn_collapsed_recoverable` is also falsified if the presence of ordinary
   low-level activity `ordinary_tick(0, 1)` is treated as a collapse
   falsifier or rescue candidate.
10. `scn_collapsed_irreversible` is falsified if irreversibility is accepted
   without `unreachable = true`, `kernelEmpty = true`, and coherence
   `true <-> true`.
11. `scn_revived_new_lineage` is falsified if the new lineage is not genuinely
   distinct, if the E3 reclosure witness is not actually checked, or if the
   row is classified as merely `viable`.
12. The subsidy-withdrawal scenario is falsified if `SubsidizedHolds(h1)` remains
   true despite `NoActiveExternalSubsidyAt(h1)`, or if the post-withdrawal
   status is not recomputed as `viable` from `mv_post_withdrawal_repair`.
13. The over-budget control is falsified if a descending but over-budget move
   defeats collapse.
14. The unlinked descent control is falsified if a mismatched readout naming
    `mv_ctrl_unlinked_named` allows construction of a `CollapseRescueCandidate`
    for `mv_ctrl_unlinked_candidate`.
15. The off-kernel boundary control is falsified if `S.T.suppK(8, 10)` is
    ignored, if a `BoundaryUpdateCandidate` value is constructed, or if the
    boundary fixture object enters any declared inventory.
16. The fallback/uncarried control is falsified if an inadmissible source tag,
    `generatedByS = false`, or `inScope = false` can still produce a rescue
    candidate.
17. The inconsistent irreversibility control is falsified if
    `IrreversibleCollapseInput` accepts `unreachable = true` with
    `kernelEmpty = false`.
18. The wrong-scope residual control is falsified if a residual under
    `(C_other, h0)` changes the status for `(C_collapse, h0)`.
19. The incomplete-inventory control is falsified if collapse or any status
    wrapper is credited from an inventory that omits a constructible rescue
    candidate.
20. The future sweep is falsified if any status row is produced by a lookup
    table rather than by evaluating the finite carried records, kernel support,
    exact budgets, descent readouts, and priority-normalized status cases.

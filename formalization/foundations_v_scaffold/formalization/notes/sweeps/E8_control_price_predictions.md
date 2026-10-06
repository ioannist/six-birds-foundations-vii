# E8 Control-Price Law - Toy-Lab Predictions (Round A, pre-registration)

This document pre-registers the toy-lab probe for E8 before any E8 sweep
implementation exists. It is grounded in the accepted six-field normal form
`formalization/notes/examples/E8.md` and the mechanized Lean module
`lean/SixBirdsFoundationsV/Laws/E8ControlPrice.lean`.

The probe mirrors the Lean predicates, not a looser prose reading. In
particular, the main classifier is scoped by `ControlPriceClaimRef`, not by a
global system status; slack and proxy obstructions must be linked to the
component actually contained in the queried claim; the compressed-summary
comparators are a shared bundle; and the E8.1 classifier is scoped by
`BudgetAuditClaimRef = (budgetMoveRecord, lineageRecord?, healthRecord?)`, not
by the budget move alone.

All quantities below are exact rationals, written as fractions. Round B must
use `fractions.Fraction` and no floating-point arithmetic or randomness.

Methodology-review additions before Round B implementation: this version adds
three registered controls found during toy-lab methodology review. First,
`claim_summary_slack_obstructed` covers Case Enumeration item 8 after the
six-field/Lean `SlackObstructedCase` fix: a summary can be predictively
legitimate while failing slack collapse and must classify as
`slack_obstructed` through the summary-level disjunct. Second,
`ctrl_wrong_lineage_capture_claim` checks that capture detection rejects a
blind-spot audit carried for the wrong Omega lineage. Third,
`ctrl_disconnected_budget_inflation_flag` checks that budget inflation is
computed from exact `oldBudget < newBudget` data rather than accepted from a
stored metadata flag.

## 1. Toy-Lab Configuration

### Shared arithmetic and reuse points

The control-price fixture is a deterministic finite ledger over named records.
It reuses existing toy-lab machinery rather than introducing a separate solver:

```text
E6/E9 allocation substrate:
  use e6_e9_probe_shop.kll_dagger_alloc, marginal_ratios,
  allocation_argmax, and exact Fraction arithmetic for componentwise KKT rows.

E2 meta-audit capacity substrate:
  use e2_bounded_reflexivity_sweep.capacity_realizable_tower,
  tower_footprint, capacity_admissible, capacity_saturated, and
  capacity_bound_holds.

Xi blind-spot substrate:
  use E7's established scalar pattern for adequacyResidual/matSub/quad.
  E8's Lean `adequacyDefect` is exactly `adequacyResidual - Omega`.
```

Every positive carried record uses source tag `committed_state` or
`audited_cell_records`, `generatedByS = true`, and `inScope = true`.

### Declared constraints and component records

The declared control constraints are:

```text
c_cpu, c_mem, c_net, c_io, c_proxy, c_aux
```

The component table fixes the exact KKT and signal data. `spend = budget`
means `BindingExposureBudget`; `spend < budget` means `SlackExposureBudget`.

| component | constraint | spend | budget | `KKT.lambda` | carried `lambdaValue` | signal value | signal active | regime | registered role |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| `cmp_cpu_bind` | `c_cpu` | `1` | `1` | `3/2` | `3/2` | `3/2` | true | binding | component lawful |
| `cmp_mem_bind` | `c_mem` | `1` | `1` | `1` | `1` | `1` | true | binding | field component |
| `cmp_net_slack_zero` | `c_net` | `1/2` | `1` | `0` | `0` | `0` | false | slack | lawful slack component |
| `cmp_aux_slack_zero` | `c_aux` | `1/4` | `1` | `0` | `0` | `0` | false | slack | summary slack collapse |
| `cmp_io_slack_violation` | `c_io` | `1/2` | `1` | `0` | `0` | `1/4` | true | slack | slack obstruction |
| `cmp_proxy_bind` | `c_proxy` | `1` | `1` | `4/5` | `4/5` | `9/10` | true | binding | proxy obstruction |
| `cmp_unrelated_slack_violation` | `c_aux` | `1/3` | `1` | `0` | `0` | `1/3` | true | slack | unrelated-member control |

The E6-style marginal data for the binding components is exact:

| component | selected probe | marginal discharge | marginal cost | ratio |
| --- | --- | ---: | ---: | ---: |
| `cmp_cpu_bind` | `probe_cpu` | `3` | `2` | `3/2` |
| `cmp_mem_bind` | `probe_mem` | `1` | `1` | `1` |
| `cmp_proxy_bind` | `probe_proxy` | `4` | `5` | `4/5` |

Slack rows have `lambda = 0`, `mu = 0` on their selected support, and
`spend < budget`. Round B must compute the binding/slack predicates from the
budget witness, not from the status label.

### Component comparators and falsifier records

`ControlSignalReadoutCertified.value` is the exact `signal value` column above,
and `ControlSignalReadoutCertified.active` is the `signal active` column.

`SlackCollapseViolation(component)` is computed as:

```text
SlackExposureBudget(component.budgetData)
and (signal_value(component.signalRecord) != 0 or signal_active(component.signalRecord))
and no carried SlackResidualExplanationRecord linked to the same signal/component
```

Thus:

```text
SlackCollapseViolation(cmp_io_slack_violation) = true
SlackCollapseViolation(cmp_unrelated_slack_violation) = true
SlackCollapseViolation(cmp_net_slack_zero) = false
```

The proxy comparators are shared comparator objects, not per-instance flags:

```text
LedgerAlignmentComparator.aligned(signal, constraint, spend, budget)
  := signal.constraintRef = constraint
     and signal.value = component.lambdaValue
     and signal.ledgerSpend = spend
     and signal.ledgerBudget = budget

HeldOutPredictionComparator.predicts(signal, prediction)
  := prediction.expectedSignal = signal.value
     and prediction.hit = true

DualStabilityComparator.stable(signal, stability)
  := stability.maxPerturbation <= 1/10
     and stability.lambdaDrift <= 1/20
```

For `cmp_proxy_bind` the fixture registers:

```text
ledger alignment = false    (signal value 9/10 != lambda 4/5)
held-out prediction = false (prediction.hit = false)
dual stability = false      (lambdaDrift = 1/5 > 1/20)
ProxyFailure(cmp_proxy_bind) = true
```

### Fields and summaries

Fields are scoped by their own declared constraints.

| field | declared constraints | components | complete? | registered role |
| --- | --- | --- | --- | --- |
| `field_ops_lawful` | `c_cpu`, `c_mem`, `c_net` | `cmp_cpu_bind`, `cmp_mem_bind`, `cmp_net_slack_zero` | true | field lawful |
| `field_member_slack` | `c_cpu`, `c_io` | `cmp_cpu_bind`, `cmp_io_slack_violation` | true | member slack obstructs field |
| `field_unrelated_clean` | `c_cpu`, `c_mem` | `cmp_cpu_bind`, `cmp_mem_bind` | true | unrelated slack does not obstruct |
| `field_summary_slack` | `c_net`, `c_aux` | `cmp_net_slack_zero`, `cmp_aux_slack_zero` | true | summary slack collapse |
| `field_incomplete` | `c_cpu`, `c_mem`, `c_net` | `cmp_cpu_bind` | false | incomplete or unpriced |

The summary comparator bundle is fixed once for the whole fixture:

```text
sameExternalObservation(q, before, after)
  := before.externalObservationKey = q.key
     and after.externalObservationKey = q.key

summarySeparates(summary, before, after)
  := summary.value != 0
     and before.policySupport != after.policySupport

policySupportChanges(before, after)
  := before.policySupport != after.policySupport

heldOutPredicts(prediction, before, after)
  := prediction.expectedAddedSupport = after.policySupport - before.policySupport
     and prediction.hit = true

dualStableHeldOut(stability, summary, perturbations)
  := perturbations is nonempty
     and every |p| <= 1/10
     and stability.maxShadowDrift <= 1/20
     and stability.summaryRef = summary
```

The registered summaries are:

| summary | field | value | shadowComponent | slackBaseline | before support | after support | perturbations | predictive legitimacy | slack collapse |
| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |
| `summary_ops_lawful` | `field_summary_slack` | `1/2` | `0` | `0` | `{basic}` | `{basic, burst}` | `[-1/10, 1/10]` | true | true |
| `summary_slack_obstructed` | `field_summary_slack` | `1/2` | `1/8` | `0` | `{basic}` | `{basic, burst}` | `[-1/10, 1/10]` | true | false |
| `summary_redescription` | `field_summary_slack` | `1/2` | `0` | `0` | `{basic}` | `{basic}` | `[-1/10, 1/10]` | false | true |

`summary_redescription` may correlate with current behavior through
`summary.value = 1/2`, but it supplies no held-out support distinction beyond
the external-observation quotient. This is the shared-comparator control: a
trivially-true local predicate would incorrectly accept it, but the fixed
comparator bundle rejects it because `policySupportChanges = false` and
`heldOutPredicts = false`.

`summary_slack_obstructed` uses the same genuine held-out witness pair as
`summary_ops_lawful`: `sameExternalObservation`, `summarySeparates`,
`policySupportChanges`, `heldOutPredicts`, and `dualStableHeldOut` all compute
true. Its summary-field components are still slack, but `shadowComponent =
1/8` and `slackBaseline = 0`, so `SummarySlackCollapse` computes false. Since
there is no member component slack violation in `field_summary_slack`, this
row must be classified by the summary-level disjunct of `SlackObstructedCase`,
not by the component disjunct.

### Xi/Omega lineage and budget-setting moves

The E8.1 fixture uses the scalar Xi pattern already established by E7:

```text
Cxi = [[1]]
Lxi = [[0]]
KLLdagger = [[0]]
originalOmega = [[0]]
xiWitness = (1)
D(hazard) = [[hazard]]
adequacyDefect(Cxi,Lxi,D,KLLdagger,originalOmega) = [[hazard^2]]
quad(adequacyDefect, xiWitness) = hazard^2
OmegaLineageBlindSpot = hazard^2 > 0
```

Thus `hazard = 1` gives a persistent blind spot and `hazard = 0` gives no
blind spot.

Budget-setting moves are exact-rational ledger moves:

| budget move | old budget | new budget | budget inflates | registered use |
| --- | ---: | ---: | --- | --- |
| `bm_shared` | `10` | `15` | true | two independently-scoped claims |
| `bm_no_capture` | `10` | `12` | true | capture claim rejected |
| `bm_capacity` | `8` | `8` | false | E2 meta-audit capacity blocked |
| `bm_missing` | `5` | `5` | false | meta-audit missing |
| `bm_inflation_no_blind` | `10` | `20` | true | inflation without blind spot |
| `bm_wrong_lineage` | `10` | `14` | true | wrong-lineage capture control |
| `bm_equal_budget_metadata_inflated` | `12` | `12` | false | disconnected inflation-flag control |

`bm_equal_budget_metadata_inflated` also carries a metadata field
`reportedInflated = true`. This metadata is not part of
`EndogenousBudgetSettingMove.budgetInflates`; Round B must compute budget
inflation as `oldBudget < newBudget`, so `12 < 12` is false.

The scoped budget-audit claims are:

| claim | budget move | lineage | health | hazard | blind spot | residual before | residual after |
| --- | --- | --- | --- | ---: | --- | ---: | ---: |
| `claim_shared_discharge` | `bm_shared` | `lineage_shared_A` | none | `0` | false | `5` | `2` |
| `claim_shared_capture` | `bm_shared` | `lineage_shared_B` | `health_shared_B` | `1` | true | not used | not used |
| `claim_no_capture_rejected` | `bm_no_capture` | `lineage_no_capture` | `health_no_capture` | `0` | false | not used | not used |
| `claim_capacity_blocked` | `bm_capacity` | none | none | `0` | false | not used | not used |
| `claim_missing_meta_audit` | `bm_missing` | none | none | `0` | false | not used | not used |
| `claim_inflation_no_blind` | `bm_inflation_no_blind` | `lineage_no_blind` | none | `0` | false | `9` | `4` |
| `ctrl_wrong_lineage_capture_claim` | `bm_wrong_lineage` | `lineage_claim_actual` | `health_wrong_lineage` | `1` | true | not used | not used |
| `ctrl_disconnected_budget_inflation_flag` | `bm_equal_budget_metadata_inflated` | `lineage_flag_blind` | `health_flag_blind` | `1` | true | not used | not used |

For `ctrl_wrong_lineage_capture_claim`, the queried
`BudgetAuditClaimRef.lineageRecord` is `lineage_claim_actual`, but the carried
`BlindSpotAuditRecord`/`OmegaLineageAudit` is explicitly linked to
`lineage_wrong_source`. The blind-spot computation is positive (`hazard = 1`),
the budget move inflates (`10 < 14`), and reported health is present, but
`BudgetInflationAudit.linkedToOriginalLineage` must compute false because the
lineage records disagree.

For `ctrl_disconnected_budget_inflation_flag`, the queried lineage and health
records match, the blind spot is positive (`hazard = 1`), and
`reportedInflated = true` is present as metadata, but the exact budget data
compute `budgetInflates = false` because `oldBudget = newBudget = 12`.

Reported ledger health rows are:

```text
health_shared_B.reportsHealthy = true
health_no_capture.reportsHealthy = true
health_wrong_lineage.reportsHealthy = true
health_flag_blind.reportsHealthy = true
```

`LedgerLineageAgreementComparator.agrees(health, lineage)` is computed as:

```text
health.lineageRef = lineage
and health.reportsHealthy = true
and lineage.noCaptureCertificate = true
```

It is true for `claim_no_capture_rejected` and false for
`claim_shared_capture`.

### E2 capacity tower data

The `claim_capacity_blocked` row reuses E2's existing finite tower:

```text
levels = (LEVELS[0], LEVELS[1], LEVELS[2])
footprints = 2, 3, 3
tower_footprint(levels) = 8
capacity cap = 8
capacity_admissible(levels) = true
attempted next level footprint = 2
capacity_admissible(levels + attempted_next) = false
capacity_saturated(levels) = true
capacity_bound_holds(levels) = true
```

This is the registered `E2_CapacityBound` bridge control. The footprint is
computed from the level record sets; it must not be asserted as a stored
boolean.

## 2. Registered Theorem-Facing Predictions

Round B must report exactly 21 registered comparisons.

| theorem / apparatus | concrete instantiation | registered prediction |
| --- | --- | --- |
| `E8_ControlPrice` | `claim_component_cpu_lawful = component(cmp_cpu_bind.componentRecord)` | exactly one main status holds: `component_lawful` |
| `E8_ControlPrice` | `claim_field_ops_lawful = field(field_ops_lawful.fieldRecord)` | exactly one main status holds: `field_lawful` |
| `E8_ControlPrice` | `claim_summary_ops_lawful = summary(summary_ops_lawful.summaryRecord)` | exactly one main status holds: `summary_lawful` |
| `E8_ControlPrice` | `claim_summary_slack_obstructed = summary(summary_slack_obstructed.summaryRecord)` | exactly one main status holds: `slack_obstructed` via the summary-level slack disjunct |
| `E8_ControlPrice` | `claim_component_io_slack = component(cmp_io_slack_violation.componentRecord)` | exactly one main status holds: `slack_obstructed` |
| `E8_ControlPrice` | `claim_component_proxy = component(cmp_proxy_bind.componentRecord)` | exactly one main status holds: `proxy_obstructed` |
| `E8_ControlPrice` | `claim_summary_redescription = summary(summary_redescription.summaryRecord)` | exactly one main status holds: `summary_redescription` |
| `E8_ControlPrice` | `claim_field_incomplete = field(field_incomplete.fieldRecord)` | exactly one main status holds: `incomplete_or_unpriced` |
| `E8_1_AuditCapture` | `claim_shared_discharge` | exactly one budget-audit status holds: `residual_discharge_verified` |
| `E8_1_AuditCapture` | `claim_shared_capture` | exactly one budget-audit status holds: `capture_detected` |
| `E8_1_AuditCapture` | `claim_no_capture_rejected` | exactly one budget-audit status holds: `capture_claim_rejected` |
| `E8_1_AuditCapture` | `claim_capacity_blocked` | exactly one budget-audit status holds: `meta_audit_capacity_blocked` |
| `E8_1_AuditCapture` | `claim_missing_meta_audit` | exactly one budget-audit status holds: `meta_audit_missing` |
| `E8_1_CaptureFalsifier` | `claim_no_capture_rejected` | `CaptureClaimRejected = true`, `CaptureDetectedHolds = false` for the same `(budgetMove,lineage,health)` claim |
| `E8_1_MetaAuditBoundedByE2` | `claim_capacity_blocked` | `tower_footprint = 8`, `cap = 8`, `capacity_bound_holds = true`, `capacity_saturated = true` |
| `E8_1_AuditCapture` | `ctrl_wrong_lineage_capture_claim` | `CaptureDetectedCase = false` because the positive blind-spot audit is linked to `lineage_wrong_source`, not the claim lineage `lineage_claim_actual` |
| `E8_1_AuditCapture` | `ctrl_disconnected_budget_inflation_flag` | `EndogenousBudgetSettingMove.budgetInflates = false`, `BudgetInflationAudit = false`, and `CaptureDetectedCase = false` despite `reportedInflated = true` metadata |

## 3. Registered Main Control-Price Scenarios

### `claim_component_cpu_lawful`

| field | predicted value |
| --- | --- |
| claim ref | `ControlPriceClaimRef.component(cmp_cpu_bind.componentRecord)` |
| carried status record | `status_component_cpu_lawful`, status `component_lawful` |
| `BindingExposureBudget` | true (`1 = 1`) |
| `GenuineScarcity` | true (`probe_cpu` selected, marginal discharge `3 > 0`) |
| `ShadowPriceComponentIdentified` | true (`lambdaValue = KKT.lambda = 3/2`) |
| `SlackCollapseViolation` | false |
| `ProxyFailure` | false |
| predicted status | `component_lawful` |

### `claim_field_ops_lawful`

| field | predicted value |
| --- | --- |
| claim ref | `ControlPriceClaimRef.field(field_ops_lawful.fieldRecord)` |
| carried status record | `status_field_ops_lawful`, status `field_lawful` |
| declared constraints | `c_cpu`, `c_mem`, `c_net` |
| every declared constraint has linked component | true |
| every component is `ComponentShadowPriceLawful` | true |
| member slack/proxy obstruction exists | false |
| predicted status | `field_lawful` |

### `claim_summary_ops_lawful`

| field | predicted value |
| --- | --- |
| claim ref | `ControlPriceClaimRef.summary(summary_ops_lawful.summaryRecord)` |
| carried status record | `status_summary_ops_lawful`, status `summary_lawful` |
| `SummaryPredictiveLegitimacy` | true |
| `sameExternalObservation` | true (`obs_low` before and after) |
| `summarySeparates` | true (`summary.value = 1/2`, support changes) |
| `policySupportChanges` | true (`{basic} -> {basic, burst}`) |
| `heldOutPredicts` | true (`expectedAddedSupport = {burst}`, `hit = true`) |
| `dualStableHeldOut` | true (`maxShadowDrift = 1/40 <= 1/20`) |
| `SummarySlackCollapse` | true (all summary-field components are slack and `shadowComponent = slackBaseline = 0`) |
| predicted status | `summary_lawful` |

### `claim_summary_slack_obstructed`

| field | predicted value |
| --- | --- |
| claim ref | `ControlPriceClaimRef.summary(summary_slack_obstructed.summaryRecord)` |
| carried status record | `status_summary_slack_obstructed`, status `slack_obstructed` |
| `SummaryPredictiveLegitimacy` | true |
| `sameExternalObservation` | true (`obs_low` before and after) |
| `summarySeparates` | true (`summary.value = 1/2`, support changes) |
| `policySupportChanges` | true (`{basic} -> {basic, burst}`) |
| `heldOutPredicts` | true (`expectedAddedSupport = {burst}`, `hit = true`) |
| `dualStableHeldOut` | true (`maxShadowDrift = 1/40 <= 1/20`) |
| member component slack violation | false (`cmp_net_slack_zero` and `cmp_aux_slack_zero` both have zero inactive signals) |
| `SummarySlackCollapse` | false (`shadowComponent = 1/8`, `slackBaseline = 0`) |
| obstruction path | summary-level `SlackObstructedCase` disjunct |
| predicted status | `slack_obstructed` |

### `claim_component_io_slack`

| field | predicted value |
| --- | --- |
| claim ref | `ControlPriceClaimRef.component(cmp_io_slack_violation.componentRecord)` |
| carried status record | `status_component_io_slack`, status `slack_obstructed` |
| `SlackExposureBudget` | true (`1/2 < 1`) |
| persistent signal | true (`signal value = 1/4`, active) |
| linked residual/noise explanation exists | false |
| `SlackCollapseViolation` | true |
| predicted status | `slack_obstructed` |

### `claim_component_proxy`

| field | predicted value |
| --- | --- |
| claim ref | `ControlPriceClaimRef.component(cmp_proxy_bind.componentRecord)` |
| carried status record | `status_component_proxy`, status `proxy_obstructed` |
| higher slack obstruction for same claim | false |
| `LedgerAlignmentComparator.aligned` | false |
| `HeldOutPredictionComparator.predicts` | false |
| `DualStabilityComparator.stable` | false |
| `ProxyFailure` | true |
| predicted status | `proxy_obstructed` |

### `claim_summary_redescription`

| field | predicted value |
| --- | --- |
| claim ref | `ControlPriceClaimRef.summary(summary_redescription.summaryRecord)` |
| carried status record | `status_summary_redescription`, status `summary_redescription` |
| higher slack/proxy obstruction for same claim | false |
| `sameExternalObservation` | true |
| `summarySeparates` | false (`policySupport` is unchanged) |
| `policySupportChanges` | false (`{basic} -> {basic}`) |
| `heldOutPredicts` | false (`expectedAddedSupport = {burst}`, actual added support empty) |
| `dualStableHeldOut` | false (`maxShadowDrift = 1/8 > 1/20`) |
| `SummaryPredictiveLegitimacy` | false |
| predicted status | `summary_redescription` |

### `claim_field_incomplete`

| field | predicted value |
| --- | --- |
| claim ref | `ControlPriceClaimRef.field(field_incomplete.fieldRecord)` |
| carried status record | `status_field_incomplete`, status `incomplete_or_unpriced` |
| declared constraints | `c_cpu`, `c_mem`, `c_net` |
| linked components | `cmp_cpu_bind` only |
| `completeForDeclaredConstraints` | false (`c_mem`, `c_net` missing) |
| higher branches for same claim | false |
| predicted status | `incomplete_or_unpriced` |

## 4. Registered E8.1 Budget-Audit Scenarios

### `claim_shared_discharge`

| field | predicted value |
| --- | --- |
| claim ref | `(bm_shared, some lineage_shared_A, none)` |
| carried status record | `status_shared_discharge`, status `residual_discharge_verified` |
| residual before/after | `5 -> 2` |
| `ResidualDischargeAudit` | true (`2 < 5`) |
| `CaptureDetectedCase` for this claim | false (`healthRecord = none`, blind spot false) |
| predicted status | `residual_discharge_verified` |

### `claim_shared_capture`

| field | predicted value |
| --- | --- |
| claim ref | `(bm_shared, some lineage_shared_B, some health_shared_B)` |
| carried status record | `status_shared_capture`, status `capture_detected` |
| reported ledger health | true |
| budget inflation | true (`10 < 15`) |
| `OmegaLineageBlindSpot` | true (`hazard = 1`, `quad = 1`) |
| no-capture falsifier for same claim | false |
| predicted status | `capture_detected` |

`claim_shared_discharge` and `claim_shared_capture` use the same
`budgetMoveRecord = bm_shared` but different lineage/health records. This is
the registered scoping control for `BudgetAuditClaimRef`: neither claim is
allowed to overwrite the other's status.

### `claim_no_capture_rejected`

| field | predicted value |
| --- | --- |
| claim ref | `(bm_no_capture, some lineage_no_capture, some health_no_capture)` |
| carried status record | `status_no_capture_rejected`, status `capture_claim_rejected` |
| `OmegaLineageBlindSpot` | false (`hazard = 0`, `quad = 0`) |
| `NoCaptureLineageAudit.noOriginalBlindSpotPersists` | true |
| `LedgerLineageAgreementComparator.agrees` | true |
| `CaptureClaimRejected` | true |
| `CaptureDetectedHolds` for this exact claim | false |
| predicted status | `capture_claim_rejected` |

### `claim_capacity_blocked`

| field | predicted value |
| --- | --- |
| claim ref | `(bm_capacity, none, none)` |
| carried status record | `status_capacity_blocked`, status `meta_audit_capacity_blocked` |
| `capacity_realizable_tower(levels)` | true |
| `tower_footprint(levels)` | `8` |
| `capacity_admissible(levels, cap=8)` | true |
| `capacity_saturated(levels, cap=8)` | true |
| higher capture/rejection/residual branches | false |
| predicted status | `meta_audit_capacity_blocked` |

### `claim_missing_meta_audit`

| field | predicted value |
| --- | --- |
| claim ref | `(bm_missing, none, none)` |
| carried status record | `status_missing_meta_audit`, status `meta_audit_missing` |
| carried meta-audit record | absent |
| higher budget-audit branches | false |
| predicted status | `meta_audit_missing` |

### `claim_inflation_no_blind`

| field | predicted value |
| --- | --- |
| claim ref | `(bm_inflation_no_blind, some lineage_no_blind, none)` |
| carried status record | `status_inflation_no_blind`, status `residual_discharge_verified` |
| budget inflation | true (`10 < 20`) |
| residual before/after | `9 -> 4` |
| `ResidualDischargeAudit` | true (`4 < 9`) |
| `OmegaLineageBlindSpot` | false (`hazard = 0`, `quad = 0`) |
| `CaptureDetectedCase` | false despite budget inflation |
| predicted status | `residual_discharge_verified` |

This isolates the capture-detection conjuncts: inflation alone is not capture
when the original-lineage blind spot does not persist.

### `ctrl_wrong_lineage_capture_claim`

| field | predicted value |
| --- | --- |
| claim ref | `(bm_wrong_lineage, some lineage_claim_actual, some health_wrong_lineage)` |
| carried status record | `status_wrong_lineage_capture`, status `meta_audit_missing` |
| reported ledger health | true |
| budget inflation | true (`10 < 14`) |
| carried blind-spot audit lineage | `lineage_wrong_source` |
| queried claim lineage | `lineage_claim_actual` |
| `OmegaLineageBlindSpot` for carried audit | true (`hazard = 1`, `quad = 1`) |
| `BudgetInflationAudit.linkedToOriginalLineage` | false |
| `CaptureDetectedCase` | false because the audit lineage is not the claim lineage |

This control has all capture-looking ingredients present individually, but the
capture claim is rejected at the linkage step. Round B must not accept a
blind-spot audit for a different Omega lineage.

### `ctrl_disconnected_budget_inflation_flag`

| field | predicted value |
| --- | --- |
| claim ref | `(bm_equal_budget_metadata_inflated, some lineage_flag_blind, some health_flag_blind)` |
| carried status record | `status_disconnected_budget_flag`, status `meta_audit_missing` |
| metadata field | `reportedInflated = true` |
| exact budget data | `oldBudget = 12`, `newBudget = 12` |
| computed `EndogenousBudgetSettingMove.budgetInflates` | false (`12 < 12` is false) |
| `OmegaLineageBlindSpot` | true (`hazard = 1`, `quad = 1`) |
| reported ledger health | true |
| `BudgetInflationAudit` | false |
| `CaptureDetectedCase` | false because budget inflation is computed from exact budget values |

This control is falsified if Round B treats a disconnected metadata flag as the
budget-inflation fact instead of computing the exact rational comparison.

## 5. Null and Control Predictions

### `ctrl_budget_audit_claim_scoping`

| field | predicted value |
| --- | --- |
| shared budget move | `bm_shared` |
| first claim | `claim_shared_discharge -> residual_discharge_verified` |
| second claim | `claim_shared_capture -> capture_detected` |
| move-only uniqueness would pass? | false |
| `BudgetAuditClaimRef` scoped uniqueness | true |

This is falsified if the sweep keys `CompleteBudgetAuditStatus` only by
`budgetMoveRecord`.

### `ctrl_field_member_slack_obstruction`

| field | predicted value |
| --- | --- |
| claim ref | `ControlPriceClaimRef.field(field_member_slack.fieldRecord)` |
| member violating component | `cmp_io_slack_violation` |
| `cmp_io_slack_violation in field_member_slack.components` | true |
| `ControlClaimContainsComponent` | true |
| predicted status | `slack_obstructed` |

### `ctrl_unrelated_component_not_obstructing_field`

| field | predicted value |
| --- | --- |
| claim ref | `ControlPriceClaimRef.field(field_unrelated_clean.fieldRecord)` |
| unrelated violating component | `cmp_unrelated_slack_violation` |
| `cmp_unrelated_slack_violation in field_unrelated_clean.components` | false |
| `ControlClaimContainsComponent` for this claim/component | false |
| higher slack obstruction for this claim | false |
| predicted status | `field_lawful` |

This pair of field controls targets the claim-kind-aware obstruction fix. A
component violation obstructs a field only when the component is a member of
that field.

### `ctrl_summary_comparators_nontrivial`

| field | predicted value |
| --- | --- |
| summary | `summary_redescription` |
| current correlation present | true (`summary.value = 1/2`) |
| held-out support distinction | false |
| `SummaryPredictiveLegitimacy` | false |
| predicted status | `summary_redescription` |

This control is falsified if Round B implements the summary conditions with a
per-instance `lambda *_: True` comparator instead of the shared comparator
bundle.

### `ctrl_e2_capacity_bound_computed`

| field | predicted value |
| --- | --- |
| claim | `claim_capacity_blocked` |
| tower footprint | `8` |
| capacity cap | `8` |
| `capacity_bound_holds` | true |
| `capacity_saturated` | true |
| predicted status | `meta_audit_capacity_blocked` |

The footprint must be computed from the E2 level records. This control is
falsified if the bound is smuggled as a stored field.

### `ctrl_inflation_without_blindspot`

| field | predicted value |
| --- | --- |
| claim | `claim_inflation_no_blind` |
| budget inflation | true (`10 < 20`) |
| reported original-lineage blind spot | false |
| residual discharge | true (`4 < 9`) |
| `CaptureDetectedCase` | false |
| predicted status | `residual_discharge_verified` |

### `ctrl_wrong_lineage_capture_claim`

| field | predicted value |
| --- | --- |
| claim | `ctrl_wrong_lineage_capture_claim` |
| budget inflation | true (`10 < 14`) |
| reported health | true |
| positive blind-spot audit exists | true (`hazard = 1`, `quad = 1`) |
| audit lineage | `lineage_wrong_source` |
| claim lineage | `lineage_claim_actual` |
| lineage link check | false |
| `CaptureDetectedCase` | false |

The blind-spot fact is computed, but it is not credited to the queried claim
because it is carried for a different Omega lineage.

### `ctrl_disconnected_budget_inflation_flag`

| field | predicted value |
| --- | --- |
| claim | `ctrl_disconnected_budget_inflation_flag` |
| metadata field | `reportedInflated = true` |
| old/new budget | `12 -> 12` |
| computed `budgetInflates` | false |
| blind spot | true (`hazard = 1`, `quad = 1`) |
| reported health | true |
| `BudgetInflationAudit` | false |
| `CaptureDetectedCase` | false |

This is the disconnected-flag control: the budget-inflation predicate must read
the exact budget values, not the metadata flag.

## 6. Registered Comparison List

Round B must emit one `PASS`/`FAIL` row for each of these 21 comparisons:

| # | registered comparison | expected value |
| ---: | --- | --- |
| 1 | `claim_component_cpu_lawful.status` | `component_lawful` |
| 2 | `claim_field_ops_lawful.status` | `field_lawful` |
| 3 | `claim_summary_ops_lawful.status` | `summary_lawful` |
| 4 | `claim_summary_slack_obstructed.status` | `slack_obstructed` through the summary-level slack disjunct |
| 5 | `claim_component_io_slack.status` | `slack_obstructed` |
| 6 | `claim_component_proxy.status` | `proxy_obstructed` |
| 7 | `claim_summary_redescription.status` | `summary_redescription` |
| 8 | `claim_field_incomplete.status` | `incomplete_or_unpriced` |
| 9 | `claim_shared_discharge.status` | `residual_discharge_verified` |
| 10 | `claim_shared_capture.status` | `capture_detected` |
| 11 | `claim_no_capture_rejected.status` | `capture_claim_rejected` |
| 12 | `claim_capacity_blocked.status` | `meta_audit_capacity_blocked` |
| 13 | `claim_missing_meta_audit.status` | `meta_audit_missing` |
| 14 | `ctrl_budget_audit_claim_scoping` | `bm_shared` supports two independent claim statuses |
| 15 | `ctrl_field_member_slack_obstruction.status` | `slack_obstructed` |
| 16 | `ctrl_unrelated_component_not_obstructing_field.status` | `field_lawful` |
| 17 | `ctrl_summary_comparators_nontrivial.status` | `summary_redescription` |
| 18 | `ctrl_e2_capacity_bound_computed` | `footprint=8`, `cap=8`, `bound=true`, `saturated=true` |
| 19 | `ctrl_inflation_without_blindspot.status` | `residual_discharge_verified`, `capture_detected=false` |
| 20 | `ctrl_wrong_lineage_capture_claim` | `capture_detected=false` because the blind-spot audit lineage is not the claim lineage |
| 21 | `ctrl_disconnected_budget_inflation_flag` | `budgetInflates=false`, `BudgetInflationAudit=false`, `capture_detected=false` |

## 7. Falsification Conditions

1. `claim_component_cpu_lawful` is falsified if the binding component's
   multiplier is not computed from its own KKT witness, if `lambdaValue` does
   not equal `KKT.lambda = 3/2`, or if the status is not exactly
   `component_lawful`.
2. `claim_field_ops_lawful` is falsified if `completeForDeclaredConstraints`
   is not checked against `c_cpu`, `c_mem`, and `c_net`, if any member
   component is not `ComponentShadowPriceLawful`, or if the status is not
   exactly `field_lawful`.
3. `claim_summary_ops_lawful` is falsified if either source-text condition is
   missing: held-out predictive legitimacy beyond the observation quotient, or
   slack collapse. It is also falsified if the status is not exactly
   `summary_lawful`.
4. `claim_summary_slack_obstructed` is falsified if a predictively legitimate
   summary with all relevant components slack but `shadowComponent = 1/8 != 0`
   is not classified `slack_obstructed` through the summary-level
   `SlackObstructedCase` disjunct. It is also falsified if the row is accepted
   through a component slack violation, since no component in
   `field_summary_slack` has a persistent signal.
5. `claim_component_io_slack` is falsified if a slack component with persistent
   nonzero signal and no residual explanation is not classified
   `slack_obstructed`.
6. `claim_component_proxy` is falsified if proxy obstruction does not require
   all three failures: ledger alignment, held-out prediction, and dual
   stability.
7. `claim_summary_redescription` is falsified if a summary with no held-out
   policy-support distinction is accepted as lawful merely because it
   correlates with behavior.
8. `claim_field_incomplete` is falsified if an incomplete field is classified
   as field-lawful or if the catch-all branch is reached without checking the
   six higher-priority cases for the same claim.
9. `claim_shared_discharge` is falsified if a genuine residual decrease
   `5 -> 2` is not classified `residual_discharge_verified`.
10. `claim_shared_capture` is falsified if reported health, budget inflation,
   and a positive Xi blind-spot witness do not classify as `capture_detected`.
11. `claim_no_capture_rejected` is falsified if a no-capture lineage audit with
    no blind-spot persistence and reported-ledger agreement does not reject the
    capture claim for the same `(budgetMove,lineage,health)` key.
12. `claim_capacity_blocked` is falsified if a saturated E2 meta-audit tower is
    not classified `meta_audit_capacity_blocked`, or if the E2 footprint bound
    is asserted without computing `tower_footprint = 8`.
13. `claim_missing_meta_audit` is falsified if a budget-setting move with no
    carried meta-audit record is not classified `meta_audit_missing`.
14. The budget-audit scoping control is falsified if the two `bm_shared` claims
    cannot simultaneously have different statuses under different
    lineage/health keys.
15. The field-member obstruction control is falsified if a slack violation from
    a component in `field_member_slack.components` does not obstruct that field
    claim.
16. The unrelated-component control is falsified if a slack violation from a
    component outside `field_unrelated_clean.components` obstructs the field
    anyway.
17. The shared-summary-comparator control is falsified if
    `summary_redescription` can satisfy `SummaryPredictiveLegitimacy` by using
    per-instance trivially true predicates.
18. The E2 bridge control is falsified if `capacity_bound_holds`, footprint, or
    saturation are not computed by the E2 sweep machinery.
19. The inflation-without-blindspot control is falsified if budget inflation
    alone causes `capture_detected` when `OmegaLineageBlindSpot = false`.
20. The wrong-lineage capture control is falsified if reported health, budget
    inflation, and a positive blind-spot audit for `lineage_wrong_source`
    classify as `capture_detected` for the different claim lineage
    `lineage_claim_actual`.
21. The disconnected budget-inflation flag control is falsified if
    `reportedInflated = true` is accepted as budget inflation when the exact
    rational comparison computes `oldBudget = newBudget = 12`, so
    `oldBudget < newBudget` is false.
22. The future sweep is falsified if any registered row is produced by a status
    lookup table rather than by evaluating the finite carried records, exact
    budgets, KKT witnesses, comparator bundles, Xi matrices, E2 tower records,
    and priority-normalized case predicates.

## 8. Round B Implementation Guard

The Round B sweep must compute all certified boolean/Prop-mirroring facts from
fixture data:

```text
BindingExposureBudget
SlackExposureBudget
GenuineScarcity
ShadowPriceComponentIdentified
SlackCollapseViolation
ProxyFailure
ControlClaimContainsComponent
SummaryPredictiveLegitimacy
SummarySlackCollapse
BudgetAuditClaimRef matching
OmegaLineageBlindSpot
CaptureClaimRejected
ResidualDischargeAudit
BudgetInflationAudit
MetaAuditBoundedByE2 / capacity_saturated
CompleteControlPriceStatus
CompleteBudgetAuditStatus
```

No status in this document may be hardcoded as a lookup value. The registered
status labels are predictions about what the predicate mirror should compute
from the declared finite fixture.

# E15 Offline Reclosure Law - Toy-Lab Predictions (Round A, pre-registration)

This document pre-registers the toy-lab probe for E15 before any E15 sweep
implementation exists. It is grounded in the accepted six-field normal form
`formalization/notes/examples/E15.md`, the committed Lean module
`lean/SixBirdsFoundationsV/Laws/E15OfflineReclosure.lean`, and the E15 entry in
`THEOREMS.md`.

Round B must mirror the Lean predicates, not a looser prose reading. In
particular, closure debt is a complete, duplicate-safe sum of actual E14, F3,
and Xi debt witnesses; capacities are projections of one carried allocation
bound to a binding `ExposureBudgetWitness`; external exchange is computed from
a complete, sound, duplicate-free census; and priority exclusions inspect
record-independent `...EvidenceFor` predicates for the same full claim. A
status label, zero observed traffic, or fitted capacity is never substitute
evidence.

All E15 arithmetic must use exact `fractions.Fraction`. All other E15 data are
finite maps, finite sets, or finite lists. Round B must use no randomness and
no floating point anywhere in the E15 calculation path. Expected statuses may
not be stored on fixture records or selected from a lookup table.

Round B must report exactly **46 registered comparisons**.

## 1. Toy-Lab Configuration

### Repair-World carrier and carried-source convention

The sweep specializes
`lab/sixbirds_foundations_v/worlds/repair_world.py`, reusing its
`RepairWorldState`, carried ledger, `ESystem`, and D4 lawful-repair checker.
E15 is a single-`ESystem` law; no E13-style inter-carrier bridge is created.

Every positive carried occurrence has:

```text
sourceTag in {committed_state, audited_cell_records}
generatedByS = true
inScope = true
CarriedRecordAt = true under the record's declared policy
```

Round B must evaluate the full `E15Carried` conjunction at
`E15OfflineReclosure.lean:336-351`. The registered carriedness control mutates
`sourceTag`, `generatedByS`, and `inScope` independently; no stored
`carried = true` field is permitted.

### Debt scope, actual E14 residual, F3 residue, and Xi residual

Every fixture that declares a debt scope receives a deterministic
`fixtureIndex`. The reserved index ranges are:

```text
base exemplar: fixtureIndex = 0
ten status fixtures: fixtureIndex = tagIndex in 1..10
boundary fixtures at rates 7/2, 4, 5: fixtureIndex = 20, 21, 22
four ablation traces: fixtureIndex = 30, 31, 32, 33
control/mutation row r, variant v: fixtureIndex = 1000 + 100*r + v
  where v starts at 0 and follows the mutation order stated in Section 4

scope_<fixtureIndex>:
  debtClaimId = 1500 + fixtureIndex
  challengeClass = C_reclosure
  horizon.startTime = 0
  horizon.endTime = the selected schedule end
```

The last formula applies to every control that actually constructs a full
claim; controls over a raw inventory field alone do not fabricate an unused
scope. These index ranges are disjoint.

For every `fixtureIndex = i`, Round B must construct fresh, claim-linked clones
of all three base debt witnesses using these exact IDs:

```text
debtIdBase(i) = 100000 + 100*i

E14 clone:
  conflictId = debtIdBase(i) + 1
  residualId = debtIdBase(i) + 2
  registrationId = debtIdBase(i) + 3
  ledgerEntryId = debtIdBase(i) + 4
  homeContextId = debtIdBase(i) + 40
  shiftContextId = debtIdBase(i) + 41
  contextFamilyId = debtIdBase(i) + 42
  memoryRecordId = debtIdBase(i) + 43
  provenanceRootId = debtIdBase(i) + 44
  quotientRecordId = debtIdBase(i) + 45
  homeTransportId = debtIdBase(i) + 46
  shiftTransportId = debtIdBase(i) + 47
  currentFormationId = debtIdBase(i) + 48
  sourceFormationId = debtIdBase(i) + 49
  dispositionId = debtIdBase(i) + 50
  e14StatusRecordId = debtIdBase(i) + 51
  residual.conflictRecord.claimRecord.claimId = scope_i.debtClaimId
  claimRef = (memory record, context family, shift transport, shift context,
    memory claim)
  disposition = statused_unresolved, supportingMutation = none,
    supportingResidual = that exact residual
  e14 status record.status = statused_unresolved
  e14 status record.residualRecord = that exact residual
  StatusedUnresolvedCase holds for that claimRef/status record
  registration.residualRecord = that exact residual
  e14_outstanding_registry entries =
    (registrationId, t) for exactly those snapshot times t at which
    this full residual entry remains in the snapshot
  component key = (e14_reconsolidation, residualId)

F3 clone:
  residueId = debtIdBase(i) + 11
  ledgerEntryId = debtIdBase(i) + 12
  reconciliationClaimId = scope_i.debtClaimId
  f3_awaiting_registry entries =
    (residueId, t) for exactly those snapshot times t at which
    this full residue entry remains in the snapshot
  component key = (f3_route_residue, residueId)

Xi clone:
  residualId = debtIdBase(i) + 21
  valuationPolicyId = debtIdBase(i) + 22
  ledgerEntryId = debtIdBase(i) + 23
  reconciliationClaimId = scope_i.debtClaimId
  accepted policy entry = valuationPolicyId
  xi_awaiting_registry entries =
    (residualId, t) for exactly those snapshot times t at which
    this full Xi entry remains in the snapshot
  component key = (xi_adequacy_residual, residualId)
```

The cloned E14 conflict's actual memory claim ID also equals
`scope_i.debtClaimId`. All three cloned physical ledger entries are distinct
members of the one Repair-World `S.Lambda_S`. Thus every E14
`scopeClaimLinked`, F3 `claimLinked`, and Xi `claimLinked` field is literal
equality for that fixture; no claim-1500 witness is reused for claims
1501-1510 or for boundary, ablation, or mutation scopes.

The base exemplar (`i = 0`, claim ID `1500`) therefore contains these three
distinct physical ledger charges:

| entry | exact source | amount | component key |
| --- | --- | ---: | --- |
| `debt_e14_base` | actual concrete `StatusedUnresolvedEvidence` plus linked canonical `StatusedUnresolvedCase` named `e14_unresolved_base` | `Fraction(8)` | `(e14_reconsolidation, 100002)` |
| `debt_f3_base` | carried `route_residue_base`, accepted as awaiting reconciliation | `Fraction(8)` | `(f3_route_residue, 100011)` |
| `debt_xi_base` | carried `xi_residual_base` | `Fraction(4)` | `(xi_adequacy_residual, 100021)` |

Thus `ClosureDebt([debt_e14_base, debt_f3_base, debt_xi_base]) =
Fraction(20)`.

`e14_unresolved_base` is not an E14-shaped local label. It is the actual E14
interface over a carried memory record, declared context family, retrieval
trigger, `ReconsolidationResidualRecord(residualId = 100002,
residualAmount = Fraction(8))`, and a carried exact charge in `S.Lambda_S`.
Identity, claim, version, value, and provenance root are preserved, and the
residual points to that trigger's exact conflict. Its claim-linked carried E14
status record has ID `100051`, is canonically `statused_unresolved`, satisfies
`StatusedUnresolvedCase`, and names that same full residual record. This is the
complete two-layer input required by `E14ResidualDebtItem`, not merely its
concrete `StatusedUnresolvedEvidence` realization.

`route_residue_base` is a carried F3 record with reconciliation claim `1500`,
recorded at `0`, a real carried ledger entry, and a shared-registry certificate
that it awaits reconciliation. The Xi data use one-dimensional rational
matrices:

```text
C = [[1]], L = [[1]], D = [[2]], KLLdagger = [[0]]
adequacyResidual(C,L,D,KLLdagger) = [[4]]
valuation_policy_base.declaredAt = -1
xiResidualAmount(valuation_policy_base, [[4]]) = Fraction(4)
```

The valuation policy, Xi record, and physical ledger entry are carried. The
policy is preregistered, accepted by the shared context, and the Xi record is
in the awaiting-discharge registry. Each fixture's initial snapshot uses its
own clones with the same exact amounts `8`, `8`, and `4`, plus only the
explicit whole-entry discharge reserves listed below.

Additional online accrual batches are also claim-scoped. For fixture `i` and
one-based phase ordinal `j`, their IDs are:

```text
accrualIdBase(i,j) = 2000000 + 10000*i + 100*j
E14 residual/registration/ledger offsets = +2, +3, +4
F3 residue/ledger offsets = +11, +12
Xi residual/policy/ledger offsets = +21, +22, +23
```

Because `CompleteClosureDebtFlow.everyDischargeLinked` discharges whole entries
already present in the before snapshot, fixtures whose first required
discharge is not a subset sum of base amounts `[8,8,4]` receive carried,
claim-linked F3 reserve entries. Zero-based reserve `k` uses residue/ledger offsets
`+(31 + 2*k)` and `+(32 + 2*k)` from `debtIdBase(i)`, has
`reconciliationClaimId = scope_i.debtClaimId`, and is registered as awaiting
at exactly the snapshot times where it remains present. The exact reserves are:

| fixture/profile | reserve entry amounts |
| --- | --- |
| `claim_online_sufficient` | `[9]` |
| `claim_offline_optional` | `[9]` |
| `claim_decorative_exchange_active` | `[6]` |
| `claim_decorative_bad_reallocation` | `[5]` |
| `claim_duty_cycle_mismatch` | `[6,6]`, one for each offline discharge |
| `claim_zero_exchange_without_p2` | `[6]` |
| boundary rate `7/2` | `[21/2]` |
| boundary rate `5` | `[4]`; the first online discharge uses base `[8,8,4]` plus this reserve |
| gross-accrual-versus-net-change control | `[3]` |
| `ctrl_recurrence_uses_online_duration` | `[6]`; retained for the second genuine offline phase |
| capacity-bound persistent-deficit variant | `[10]` |
| capacity-bound bounded-counterexample variant | `[10,10]`, one per online phase |
| capacity-bound online-sufficient variant | `[10]` |

No other fixture has a reserve. Each reserve has its own component key and
physical ledger charge. These offsets stay below the next fixture's
`debtIdBase` and therefore preserve the existing no-collision invariant.

Every accrued clone has reconciliation/claim ID `scope_i.debtClaimId`. Its
outstanding/awaiting registry contains exactly the later snapshot times at
which that full entry remains present, beginning with its arrival phase end and
ending when its full discharge removes it. The registry is therefore computed
from the preregistered finite snapshot lists, not a single end-of-horizon flag.

Accrued entries are fixed per phase profile rather than reused from one
duration. Each online phase has exactly the following fresh list, using the
E14/F3/Xi ID offsets above:

| profile | fixtures | E14 amount | F3 amount | Xi amount | exact accrued sum |
| --- | --- | ---: | ---: | ---: | ---: |
| duration `3`, rate `6` | `claim_alternation_required` online phases | `6` | `6` | `6` | `18 = 3*6` |
| duration `2`, rate `6` | counterexample, duty mismatch, cascade, four ablation traces | `4` | `4` | `4` | `12 = 2*6` |
| duration `6`, rate `5` | rate-5 boundary online phases | `12` | `12` | `6` | `30 = 6*5` |
| duration `3`, rate `3` | online-sufficient and optional-online phases | `3` | `3` | `3` | `9 = 3*3` |
| duration `3`, rate `7/2` | lower boundary fixture | `7/2` | `7/2` | `7/2` | `21/2 = 3*(7/2)` |
| duration `3`, rate `4` | equality boundary fixture | `4` | `4` | `4` | `12 = 3*4` |
| duration `1`, rate `5` | gross-accrual-versus-net-change control | `2` | `2` | `1` | `5 = 1*5` |
| duration `4`, rate `6` | recurrence-bound isolation control | `10` | `8` | `6` | `24 = 4*6` |
| duration `2`, rate `3` | capacity-bound online-sufficient variant | `2` | `2` | `2` | `6 = 2*3` |
| any offline profile, rate `0` | every offline phase | no entries | no entries | no entries | `0` |

The Xi entry in each nonempty profile is literal `adequacyResidual` with
`C = [[1]]` and `L = [[1]]`:

| Xi amount | `D` | `KLLdagger` | computed one-cell residual |
| ---: | --- | --- | ---: |
| `6` | `[[3]]` | `[[1/3]]` | `9*(1-1/3) = 6` |
| `4` | `[[2]]` | `[[0]]` | `4*(1-0) = 4` |
| `3` | `[[2]]` | `[[1/4]]` | `4*(1-1/4) = 3` |
| `7/2` | `[[2]]` | `[[1/8]]` | `4*(1-1/8) = 7/2` |
| `2` | `[[2]]` | `[[1/2]]` | `4*(1-1/2) = 2` |
| `1` | `[[1]]` | `[[0]]` | `1*(1-0) = 1` |

The rate-5 profile deliberately uses Xi amount `6`; its two `12` entries make
the total `30`. No profile borrows the amount list of another duration. All
component keys and physical ledger entries are distinct. The `100000` and
`2000000` debt bands cannot collide with status records (`6001..6010`), phase,
exchange, gate, flow, snapshot, boundary, ablation, or mutation bands.

### Shared classifier context

One singleton `ctx_offline` supplies every comparator for every fixture:

```text
e14ResidualOutstanding(registration, asOf)
  := (registration.registrationId, asOf) is in e14_outstanding_registry

f3RouteResidueAwaitingReconciliation(residue, asOf)
  := (residue.residueId, asOf) is in f3_awaiting_registry

xiValuationPolicyAccepted(policy)
  := policy.valuationPolicyId is in accepted_xi_policy_ids

xiResidualAmount(policy, matrix)
  := sum of all rational entries in matrix under the registered policy

xiResidualAwaitingDischarge(residual, asOf)
  := (residual.residualId, asOf) is in xi_awaiting_registry

ledgerEntryChargesRouteResidue(entry, residue, amount)
  := entry.kind = route and entry.sourceId = residue.residueId
     and entry.amount = amount and amount > 0

ledgerEntryChargesXiResidual(entry, residual, amount)
  := entry.kind = xi and entry.sourceId = residual.residualId
     and entry.amount = amount and amount > 0

gateClosesExternalExchange(gate)
  := gate.gateRecordId is in accepted_external_gate_ids
     and external_channel_by_gate[gate.gateRecordId] = external_exchange

e7AlarmObservationAccepted(observation)
  := observation.observationId is in accepted_e7_alarm_ids
     and its carried E7 disposition record matches its stored kind/reason

e5StressObservationAccepted(observation)
  := observation.observationId is in accepted_e5_stress_ids
     and its carried E5 occurrence is tagged stressed
```

Every function reads all semantically relevant arguments. Section 4 registers
a concrete mutation that changes each comparator's result from true to false
while the same `ctx_offline` object is retained. No fixture may replace it with
a per-instance lambda.

### Binding budget geometry

Every positive claim owns a carried scope-linked clone of this allocation:

```text
budgetData_<tag>:
  spend = Fraction(6)
  budget = Fraction(6)
  spend and budget entries are distinct carried members of S.Lambda_S
  BindingExposureBudget = true

allocation_<tag>:
  declaredAt = -1
  onlineExternalAllocation = Fraction(2)
  onlineInternalDischargeAllocation = Fraction(4)
  offlineExternalAllocation = Fraction(0)
  offlineInternalDischargeAllocation = Fraction(6)
```

The projections are therefore computed, never stored independently:

```text
kappaOn = Fraction(4)
freedAllocation = Fraction(2)
kappaOff = Fraction(6)
kappaOff = kappaOn + freedAllocation
```

This instantiates `DerivedOfflineBudgetGeometry`
(`E15OfflineReclosure.lean:666-710`). The post-hoc geometry controls mutate
the carried allocation or declaration time; they do not supply alternative
capacity scalars.

### Exact phase, flow, exchange, and gate conventions

Schedules are finite, `Nodup`, scope-linked, ordered, contiguous, and cover
their declared horizon. The notation below is only a compact record listing:

```text
O[d; a; r; x] = online phase of duration d,
                 accrual rate a, discharge rate r, exchange amount x
F[d; a; r; x] = offline phase with the same fields
```

Amounts are recomputed as rate times positive `PhaseDuration`. Every flow has
carried complete before/after snapshots, duplicate-free accrual/discharge
lists, full coverage, and the exact balance equation. Every online flow used
by deficit, bounded-counterexample, or sufficient-capacity evidence satisfies
`dischargeRate <= kappaOn`; sufficient-capacity flows additionally satisfy
`accrualRate <= dischargeRate`.

Every schedule phase has at least one carried exchange record, including a
zero-valued record for an offline phase. This is required by
`CompleteExternalExchangeInventory.everyPhaseCovered`. The census is complete
over every `EligibleExternalExchange`, sound, `records.Nodup`, and
record-ID-Nodup. `ExchangeInPhase` is the exact sum of records selected by full
phase equality.

Each genuine offline phase additionally owns a carried `ExchangeGateRecord`
whose generated repair move is accepted by Repair-World's D4 checker, whose
sort is literally `SixBirdsIII.Primitive.P2`, whose phase link is exact, and
whose ID is accepted by the one shared `gateClosesExternalExchange`
comparator. Zero exchange and a P2 gate are separate checks.

### Preregistered status fixture families

Each row owns fresh scope, allocation, schedule, tolerance, recurrence bound,
status record, snapshots, flow IDs, exchange IDs, and gate IDs. Tolerances and
recurrence bounds are carried, scope-linked, and declared at `-1`.

The status tags have fixed indices in table order, `1..10`. Round B must assign
IDs deterministically from that index:

```text
horizonId = 1600 + tagIndex
allocationId = 2000 + tagIndex
scheduleId = 3000 + tagIndex
toleranceId = 4000 + tagIndex
recurrenceBoundId = 5000 + tagIndex
statusRecordId = 6000 + tagIndex
phaseId(tagIndex,j) = 10000 + 100*tagIndex + j
exchangeRecordId(tagIndex,j) = 20000 + 100*tagIndex + j
gateRecordId(tagIndex,j) = 30000 + 100*tagIndex + j
flowId(tagIndex,j) = 40000 + 100*tagIndex + j
snapshotId(tagIndex,j) = 50000 + 100*tagIndex + j
```

Boundary nondebt records use the `70000..72999` band, with `1000` IDs per
boundary fixture in table order; ablation nondebt records analogously use
`80000..83999`. Control/mutation nondebt records use
`1000000 + 10000*rowNumber + 100*variantOrdinal + typeOffset`, where
`typeOffset` is `1` scope/horizon, `2` allocation, `3` schedule, `4` tolerance,
`5` recurrence, `6` status, `10+j` phase, `30+j` exchange, `50+j` gate,
`70+j` flow, and `90+j` snapshot. These bands, the per-claim debt band, and
the `2000000 + 10000*i + 100*j` accrual band are disjoint for every registered
fixture. No ID is reused across bands.
`allocation_bad` has ID `2099` and is used only by the broken-reallocation
fixture.

| fixture | exact schedule/data | additional preregistered facts | expected status |
| --- | --- | --- | --- |
| `claim_alternation_required` | `[O[3;6;4;1], F[1;0;6;0], O[3;6;4;1], F[1;0;6;0]]` | `maximumOnlineRun = 3`; two lawful P2 offline phases; observed duty `2/8 = 1/4`; predicted duty `(6-4)/((6-4)+6) = 1/4`; tolerance `0` | `alternation_required` |
| `claim_online_sufficient` | `[O[3;3;3;1], O[3;3;3;1]]` | all online; each flow offsets accrual and remains below `kappaOn`; debt nonincreasing | `online_sufficient` |
| `claim_offline_optional` | `[O[3;3;3;1], F[1;0;6;0]]` | `3 <= kappaOn`; its one offline phase is fully genuine; universal offline check ranges over that exact singleton | `offline_optional` |
| `claim_deficit_online_counterexample` | five copies of `O[2;6;4;1]` | horizon length `10`; `maximumOnlineRun = 3`; bound `40` declared at `-1`; snapshots `20,24,28,32,36,40`; all online discharge rates equal `kappaOn` | `deficit_online_counterexample` |
| `claim_decorative_exchange_active` | `[F[1;0;6;1]]` | offline label but complete census sum is `1` | `decorative_offline` |
| `claim_decorative_no_discharge` | `[F[1;0;0;0]]` | lawful P2 gate and exact allocation, but discharged debt `0` and debt does not fall | `decorative_offline` |
| `claim_decorative_bad_reallocation` | `[F[1;0;5;0]]` | claim geometry is valid; carried phase instead names `allocation_bad` with offline external `1`, offline internal `5` | `decorative_offline` |
| `claim_duty_cycle_mismatch` | `[O[2;6;4;1], F[1;0;6;0], O[2;6;4;1], F[1;0;6;0]]` | observed duty `2/6 = 1/3`; prediction `1/4`; preregistered tolerance `1/24`; exact error `1/12 > 1/24` | `duty_cycle_mismatch` |
| `claim_skipped_offline_cascade` | three copies of `O[2;6;4;1]` | no debt-bound witness; debt grows; alarm at `1` in phase 1, stress at `5` in phase 3; both carried and accepted | `skipped_offline_cascade` |
| `claim_zero_exchange_without_p2` | `[F[1;0;6;0]]` | complete census genuinely sums to zero and flow is otherwise valid, but no phase-linked lawful P2 gate exists | `offline_reclosure_rejected` |

The load-bearing claim metadata are fixed before Round B:

| status fixture | `maximumOnlineRun` | tolerance |
| --- | ---: | ---: |
| `claim_alternation_required` | `3` | `0` |
| `claim_online_sufficient` | `3` | `0` |
| `claim_offline_optional` | `3` | `0` |
| `claim_deficit_online_counterexample` | `3` | `0` |
| `claim_decorative_exchange_active` | `1` | `0` |
| `claim_decorative_no_discharge` | `1` | `0` |
| `claim_decorative_bad_reallocation` | `1` | `0` |
| `claim_duty_cycle_mismatch` | `2` | `1/24` |
| `claim_skipped_offline_cascade` | `2` | `0` |
| `claim_zero_exchange_without_p2` | `1` | `0` |

Every value in this table is carried, scope-linked, and declared at `-1`. For
every other full claim in this document the exact default is
`maximumOnlineRun = 3`, `tolerance = 0`, both declared at `-1`, unless an
explicit override is listed below. The only overrides are:

```text
boundary rate 7/2: maximumOnlineRun = 3, tolerance = 0
boundary rate 4:   maximumOnlineRun = 3, tolerance = 0
boundary rate 5:   maximumOnlineRun = 6, tolerance = 0
ablation traces 1..4: maximumOnlineRun = 2, tolerance = 0
ctrl_recurrence_uses_online_duration: maximumOnlineRun = 3, tolerance = 0
ctrl_posthoc_tolerance_rejected: maximumOnlineRun = 2,
  tolerance = 1/24, tolerance.declaredAt mutated from -1 to 1
ctrl_claim_scoping online side: maximumOnlineRun = 3, tolerance = 0
ctrl_claim_scoping mismatch side: maximumOnlineRun = 2, tolerance = 1/24
cascade-derived controls: maximumOnlineRun = 2, tolerance = 0
zero-exchange/P2-derived controls: maximumOnlineRun = 1, tolerance = 0
```

Controls that mutate one of these fields begin from the listed baseline. No
recurrence bound or tolerance may be synthesized from an observed status.

The exact snapshot trajectories implied by those flows are preregistered here.
Each delta is `(duration*accrualRate) - (duration*dischargeRate)`:

| fixture | per-phase `(accrued, discharged, net)` | ordered snapshot totals |
| --- | --- | --- |
| `claim_alternation_required` | `(18,12,+6),(0,6,-6),(18,12,+6),(0,6,-6)` | `[20,26,20,26,20]` |
| `claim_online_sufficient` | `(9,9,0),(9,9,0)` | `[29,29,29]` |
| `claim_offline_optional` | `(9,9,0),(0,6,-6)` | `[29,29,23]` |
| `claim_deficit_online_counterexample` | five copies of `(12,8,+4)` | `[20,24,28,32,36,40]` |
| `claim_decorative_exchange_active` | `(0,6,-6)` | `[26,20]` |
| `claim_decorative_no_discharge` | `(0,0,0)` | `[20,20]` |
| `claim_decorative_bad_reallocation` | `(0,5,-5)` | `[25,20]` |
| `claim_duty_cycle_mismatch` | `(12,8,+4),(0,6,-6),(12,8,+4),(0,6,-6)` | `[32,36,30,34,28]` |
| `claim_skipped_offline_cascade` | three copies of `(12,8,+4)` | `[20,24,28,32]` |
| `claim_zero_exchange_without_p2` | `(0,6,-6)` | `[26,20]` |

For example, each duration-3 deficit online phase accrues `18`, discharges
`12`, and changes debt by `+6`; each duration-1 offline phase accrues `0`,
discharges `6`, and changes debt by `-6`. Each duration-2 cascade or bounded-
counterexample phase accrues `12`, discharges `8`, and changes debt by `+4`.
Every number is recomputed from the concrete entry and discharge lists; the
snapshot table is a prediction, not stored classifier input.

For `claim_alternation_required`, every online phase's own duration is `3 <=
maximumOnlineRun`; recurrence is not inferred from the zero gap to the next
contiguous phase. Every online phase has a later offline phase. External debt
accrual is assumed gated during each offline phase, so offline accrual is
exactly zero. This is the registered duty model and the explicit scope of
E15 Nonclaim 11.

### Deficit-boundary and offline-ablation families

The boundary sweep uses the same exact geometry (`kappaOn = 4`, `kappaOff =
6`) at three exact rates:

| accrual rate | schedule | `maximumOnlineRun` | tolerance | predicted regime/status |
| ---: | --- | ---: | ---: | --- |
| `7/2` | two copies of `O[3;7/2;7/2;1]` | `3` | `0` | `online_sufficient` |
| `4` | two copies of `O[3;4;4;1]` | `3` | `0` | `online_sufficient`; equality is not deficit |
| `5` | `[O[6;5;4;1], F[1;0;6;0], O[6;5;4;1], F[1;0;6;0]]` | `6` | `0` | `alternation_required`; observed and predicted duty both `2/14 = 1/7` |

The three boundary trajectories, recomputed from their exact profiles, are:

| accrual rate | per-phase `(accrued, discharged, net)` | ordered snapshot totals |
| ---: | --- | --- |
| `7/2` | two copies of `(21/2,21/2,0)` | `[61/2,61/2,61/2]` |
| `4` | two copies of `(12,12,0)` | `[20,20,20]` |
| `5` | `(30,24,+6),(0,6,-6),(30,24,+6),(0,6,-6)` | `[24,30,24,30,24]` |

The offline-ablation census contains four fresh all-online deficit traces,
each with three copies of `O[2;6;4;1]`, `maximumOnlineRun = 2`, and tolerance
`0`; both metadata records are declared at `-1`. In each trace, debt grows, the
carried E7 alarm precedes the carried E5 stress, both comparators accept the
observations, and each timestamp is within its named phase. Registered counts
are `alarm = 4`, `stress = 4`, valid chronology `= 4`.
Every ablation trace has three copies of `(12,8,+4)` and exact trajectory
`[20,24,28,32]`. Across four traces this is four independently recomputed
copies, not one trajectory selected by an ablation label.
Two traces may also reach an E5 collapse status as descriptive telemetry, but
no collapse count, rate, or comparison is an E15 registered claim, matching
Nonclaim 9.

## 2. Registered Theorem-Facing Predictions

Round B must report exactly **46 registered comparisons**.

| theorem | concrete instantiation | registered prediction |
| --- | --- | --- |
| `E15_OfflineReclosureStatus` | all ten status fixtures | exactly one of the eight Holds predicates is true for each full claim |
| `E15_DeficitAlternation` | `claim_alternation_required` | `AlternationRequiredHolds = true` from its supplied full case |
| `E15_OfflineCapacityExactlyFreed` | every valid geometry | `kappaOff = 6 = 4 + 2` and `kappaOn < kappaOff` |
| `E15_OnlineSufficientNoOfflineRequired` | `claim_online_sufficient` | `OnlineSufficientHolds = true` and `AlternationRequiredHolds = false` |
| `E15_OfflinePermittedOutsideDeficit` | `claim_offline_optional` | `OfflineOptionalHolds = true` |
| `E15_SkippedOfflineCascade` | `claim_skipped_offline_cascade` | `SkippedOfflineCascadeHolds = true` |
| `E15_DecorativeOfflineFalsifier` | all three primary decorative fixtures | `DecorativeOfflineHolds = true` and `AlternationRequiredHolds = false` |
| `E15_DutyCycleMismatchFalsifier` | `claim_duty_cycle_mismatch` | mismatch Holds true and alternation Holds false |
| `E15_DeficitOnlineFalsifiesNecessity` | `claim_deficit_online_counterexample` | counterexample Holds true and alternation Holds false |
| `E15_DeficitCounterexampleExcludesLowerPriority` | canonical complete counterexample claim; the adversarial tag is tested separately | all seven lower-priority Holds predicates are false because their cases negate the raw counterexample evidence |

## 3. Registered Eight-Status Scenarios

The first ten registered comparisons are the ten status fixtures in Section 1.
Their full claim key is always:

```text
(scope, allocationRecord, schedule, toleranceRecord, recurrenceBound)
```

The ten keys are pairwise distinct. Each status record matches all five
components, is fully carried, and is classified through the committed order:

```text
deficit_online_counterexample > decorative_offline > duty_cycle_mismatch >
skipped_offline_cascade > alternation_required > online_sufficient >
offline_optional > offline_reclosure_rejected
```

The three decorative fixtures share the same status but have distinct full
claim keys and isolate three different positive disjuncts of
`DecorativeOfflineEvidence`. The rejected fixture is not treated as positive
evidence of a causal failure: its registered diagnosis is specifically the
missing P2 gate.

## 4. Registered Controls and Mutation Fixtures

### Debt-source and inventory controls

- `ctrl_three_source_exact_aggregation` recomputes `8 + 8 + 4 = 20`, then
  removes each source in turn and predicts completeness failure.
- `ctrl_e14_direct_witness_required` copies its control claim's cloned
  residual ID `debtIdBase(fixtureIndex) + 2` and amount `8` into a local
  lookalike without the corresponding actual E14 unresolved witness; it predicts no
  `E14ResidualDebtItem` and zero credited E14 amount.
- `ctrl_f3_certificate_required` keeps a carried route-residue label but
  removes the F3 registry entry; the F3 comparator is false and the item is
  excluded.
- `ctrl_xi_posthoc_scalarization_rejected` moves the valuation declaration to
  time `1` and changes the stored amount from the shared matrix valuation. Both
  preregistration and amount linkage fail.
- `ctrl_xi_amount_without_matrix_rejected` supplies amount `4` but no source
  matrices or `residualComputed` equality.
- `ctrl_duplicate_physical_ledger_charge` reuses one carried ledger entry for
  F3 and Xi. Component keys differ, but `ledgerChargesNodup = false`.
- `ctrl_debt_and_flow_duplicate_safety` mutates, one at a time, debt component
  keys, accrued-entry keys, discharge IDs, and discharged full records. Its
  expected vector is four `Nodup = false` results.

### Geometry, rate, recurrence, and claim controls

- `ctrl_free_capacity_smuggling_rejected` supplies only the numbers `4` and
  `6`; without the carried allocation and binding budget witness, no geometry
  or positive E15 branch is constructible.
- `ctrl_capacity_gain_equation` recomputes `6 = 4 + 2`; mutating the carried
  allocation's `offlineInternalDischargeAllocation`, and hence projected
  `kappaOff`, to `11/2` or `13/2` makes the reallocation equation false.
- `ctrl_gross_accrual_not_net_change` begins at `23` because it owns the
  preregistered reserve entry `3`; over duration `1`, new debt is `5`,
  discharge is `3`, exact net change is `2`, and the trajectory is `[23,25]`.
  Expected rates are accrual `5` and discharge `3`, never accrual `2`.
- `sweep_deficit_boundary` is the exact three-rate table in Section 1.
- `ctrl_incomplete_phase_flow_inventory` removes the unique flow for one
  declared online phase. `everyPhaseCovered = false`; absent a higher positive
  obstruction, the status is `offline_reclosure_rejected`.
- `ctrl_recurrence_uses_online_duration` uses row 22, variant 0, hence
  `fixtureIndex = 3200`, `debtIdBase = 420000`, reserve residue/ledger IDs
  `420031/420032`, and accrued-entry bases `34000100` and `34000300`. It has
  the complete schedule
  `[O[4;6;4;1], F[1;0;6;0], O[2;6;4;1], F[1;0;6;0]]` under
  `maximumOnlineRun = 3` and tolerance `0`. Its initial entries are base
  `[8,8,4]` plus the deterministic reserve `[6]`. The duration-4 online phase
  accrues `[E14 10, F3 8, Xi 6] = 24`, discharges the two base entries
  `[8,8] = 16`, and moves `26 -> 34`. The first offline phase has its own
  lawful P2 gate, complete zero census, exact allocation, no accrual, and
  discharges the duration-4 Xi entry `6`, moving `34 -> 28`. The duration-2
  online phase accrues
  `[4,4,4] = 12`, discharges the prior F3 entry `8`, and moves `28 -> 32`.
  The second independently gated genuine offline phase discharges the reserve
  `6`, moving `32 -> 26`. Thus the exact trajectory is
  `[26,34,28,32,26]`, both online rates equal `6 > kappaOn`, both online
  discharge rates equal `4`, and observed duty `2/8 = 1/4` equals predicted
  duty. The schedule starts online, alternates, has two offline phases, and
  every online phase has a later offline phase. Only the first online phase's
  own check `4 <= maximumOnlineRun = 3` is false; the contiguous gap remains
  irrelevant.
- `ctrl_posthoc_tolerance_rejected` changes only `tolerance.declaredAt` from
  `-1` to `1`; both duty prediction and mismatch evidence reject it.
- `ctrl_claim_scoping` classifies one debt scope under two otherwise identical
  claims with different schedules/tolerances. One is `online_sufficient`, the
  other `duty_cycle_mismatch`; neither status record matches the other's key.
- `ctrl_evidence_priority_not_status_tag` attempts an alternation-tagged carried
  record for the counterexample claim. `AlternationRequiredCase = false`
  because raw `DeficitOnlineCounterexampleEvidenceFor` is true. If that record
  is retained alongside the canonical counterexample status occurrence,
  `CompleteOfflineReclosureStatus.statusUnique` also fails; the canonical
  complete fixture therefore contains only the counterexample status record.
- `ctrl_allocation_postdates_horizon` changes only `allocation.declaredAt` from
  `-1` to `1`; the allocation remains carried but geometry is false.
- `ctrl_online_discharge_capacity_bound` owns three complete variants, using
  row 41's control fixture indices `5100`, `5101`, and `5102` for variant
  ordinals `0`, `1`, and `2`. Their `debtIdBase` values are `610000`, `610100`,
  and `610200`; reserve residue/ledger IDs are respectively `610031/610032`,
  `610131/610132` plus `610133/610134`, and `610231/610232`. Their first
  accrued-entry bases are `53000100`, `53010100`, and `53020100`; bounded
  variant 1's second base is `53010200`. Every variant uses carried
  `maximumOnlineRun = 3` and tolerance `0`, both declared at `-1`:

| target consumer | exact schedule and before entries | exact flow arithmetic | all other target fields |
| --- | --- | --- | --- |
| persistent deficit | variant 0, `[O[2;6;5;1]]`, before `[8,8,4,10]` | accrued `[4,4,4] = 12`, whole-entry discharge `[10]`, trajectory `[30,32]`, rate `6 > 4` | carried complete schedule/flow, claim allocation, online existence, common rate, strict deficit all true; only `5 <= 4` false |
| bounded counterexample | variant 1, two copies of `O[2;6;5;1]`, before `[8,8,4,10,10]` | each phase accrues `[4,4,4] = 12` and discharges one reserve `10`; trajectory `[40,42,44]` | bound `44` and recurrence `3` declared at `-1`, horizon `4 > 3`, all-online, snapshots bounded, exchange positive; the sole concrete failure is `5 <= 4` |
| online sufficient | variant 2, `[O[2;3;5;1]]`, before `[8,8,4,10]` | accrued `[2,2,2] = 6`, whole-entry discharge `[10]`, trajectory `[30,26]` | all-online, positive exchange, `3 <= 5`, and debt nonincrease true; only `5 <= 4` false |

  In Lean, `DeficitOnlineBoundedCounterexample` contains a
  `PersistentDeficitEvidence` over the same single-valued phase-flow inventory,
  so variant 1's over-capacity data prevents that inherited substructure and
  also falsifies the counterexample's repeated local capacity field. These are
  not two independent fixture failures: both are the identical computed
  inequality `5 <= 4`, and every non-capacity field listed above passes.
- `ctrl_claim_match_key_mutations` mutates each of the five status-key fields
  separately. The expected vector is five
  `OfflineReclosureStatusRecordMatchesClaim = false` results.

### External-review-v42 canonical-status, flow-lineage, and timestamp controls

- `ctrl_e14_wrong_canonical_status_rejected` uses row 44, variant 0, hence
  `fixtureIndex = 5400`, `scope.debtClaimId = 6900`,
  `debtIdBase = 640000`, and control band base `1440000`. Its concrete E14
  unresolved layer is unchanged from the positive clone: conflict/residual/
  registration/ledger IDs are `640001/640002/640003/640004`, residual amount
  is `Fraction(8)`, the carried unchanged current record and exact
  `S.Lambda_S` charge are valid, and disposition `640050` still directly
  supports residual `640002`. Its E14 claim uses contexts `640040/640041`,
  family `640042`, memory/root/quotient `640043/640044/640045`, transports
  `640046/640047`, and formations `640048/640049`. The carried E14 status
  record is `640051`, but the same trigger also owns two complete lawful
  outcomes, so E14 canonically classifies it `outcome_collision`:
  repair package/mutation/formation/provenance IDs are
  `640060/640061/640062/640063`; coarsening mutation/formation/before-quotient/
  after-quotient/support-audit/provenance IDs are
  `640064/640065/640066/640067/640068/640069`. Both successor records preserve
  source record ID `640043`, claim `6900`, and provenance root `640044`, and
  advance version `1 -> 2`. The repair adds
  `({collision_left},{collision_right},{},{})` pointwise to the source record;
  the coarsening quotients map `(a,b,c,d)` to `(a,b,c,d)` before and
  `(ab,ab,c,d)` after, audit `640068` owns merged pair `(a,b)`, and both
  carried D4 moves/provenances are accepted for the exact trigger at
  `zBefore = 0`, with repair `zAfter = 2` and coarsening `zAfter = 3`. Thus
  status record `640051` names the exact source, family, shift transport,
  shift context, memory claim, and conflict `640001`; `OutcomeCollisionCase`
  and the complete E14 status occurrence are genuine,
  while E15's required `canonicalStatus = statused_unresolved` and
  `StatusedUnresolvedCase` are false. Expected: E14 debt item false and
  credited E14 amount `Fraction(0)`.

- `ctrl_offline_flow_off_inventory_rejected` uses row 45, variant 0, hence
  `fixtureIndex = 5500`, `scope.debtClaimId = 7000`,
  `debtIdBase = 650000`, and control band base `1450000`. Its one-phase
  schedule is `F[1;0;6;0]` over `[0,1]`, with horizon/allocation/schedule/
  tolerance/recurrence IDs `1450001..1450005`, phase ID `1450011`, zero
  exchange record `1450031`, and lawful P2 gate `1450051`. Initial debt is
  base `[8,8,4]` plus reserve `6` at residue/ledger IDs `650031/650032`.
  Canonical flow `1450071` is the sole member of
  `CompletePhaseFlowInventory.flows`; it uses snapshots `1450091/1450092`,
  discharge `57000171` at time `1`, no accrual, and trajectory `26 -> 20`.
  A carried complete phase-linked positive clone `1450072` uses those same
  snapshots/discharge but is not in the inventory. A second carried complete
  phase-linked decorative clone `1450073` uses before snapshot `1450091`, new
  snapshot `1450093` with unchanged debt `26`, and no discharge, so its
  concrete no-reduction defect is true; it too is absent from the inventory.
  Expected: `GenuineOfflinePhaseEvidence` for `1450072` is false and
  `DecorativeOfflineEvidence` for `1450073` is false, with `flowMember` the
  isolated failed field in each attempted construction.

- `ctrl_discharge_out_of_phase_rejected` uses row 46, variant 0, hence
  `fixtureIndex = 5600`, `scope.debtClaimId = 7100`,
  `debtIdBase = 660000`, and control band base `1460000`. It clones the same
  valid `F[1;0;6;0]` offline flow shape with horizon/allocation/schedule/
  tolerance/recurrence IDs `1460001..1460005`, phase `1460011`, zero exchange
  `1460031`, P2 gate `1460051`, flow `1460071`, snapshots
  `1460091/1460092`, and reserve residue/ledger `660031/660032`. Valid
  discharge `58000171` removes exactly that carried reserve amount `6` at
  `Fraction(1)`, giving `26 -> 20`. The registered mutation changes only
  `dischargedAt` to `Fraction(2)`, outside the phase interval `[0,1]`.
  Expected: `everyDischargeLinked = false` and
  `CompleteClosureDebtFlow = false`.

Rows 44-46 use E14 offsets only through `+69` and control-band offsets only
through `+93`; both remain below the next `+100` fixture/control band. Their
accrual/discharge IDs retain the global fixture-index/phase-ordinal formula, so
the existing no-ID-reuse invariant remains exact.

### Cascade and offline controls

- `ctrl_alarm_without_e7_acceptance` keeps the carried alarm tag but removes
  its observation ID from the shared E7 acceptance registry.
- `ctrl_stress_without_e5_acceptance` keeps the carried `stressed` tag but
  removes its ID from the shared E5 acceptance registry.
- `ctrl_cascade_chronology_lineage_mutations` independently puts the alarm
  after stress, moves each timestamp outside its named phase, changes the debt
  scope, and names a phase outside the schedule. Every mutation makes
  `SkippedOfflineCascadeEvidence = false`.
- `ctrl_e5_suspension_is_not_e15_offline` supplies valid E5 suspension evidence
  but omits the complete E15 exchange census, exact reallocation, and measured
  debt reduction. No E15 offline witness exists.
- `ctrl_offline_overcapacity_is_decorative` gives an optional schedule one
  valid offline phase and one carried offline phase with discharge rate `7 >
  kappaOff`. Universal genuineness fails; the over-capacity phase positively
  realizes `DecorativeOfflineEvidence`, so status is `decorative_offline`, not
  `offline_optional`.
- `census_offline_ablation_alarm_stress` reports the exact `4/4/4` alarm,
  stress, and chronology counts from Section 1. Collapse telemetry is excluded
  from the registered value.

### Exchange census, gate, carriedness, and shared-comparator controls

- `ctrl_exchange_census_omission` omits one positive eligible record while it
  remains in the fixture-wide eligible universe; `completeForSchedule = false`.
- `ctrl_exchange_census_record_duplicate` repeats one full record;
  `recordsNodup = false`.
- `ctrl_exchange_census_id_duplicate` uses two distinct carried eligible
  records with the same ID; `recordIdsNodup = false`.
- `ctrl_exchange_eligibility_soundness_matrix` separately mutates carriedness,
  phase membership, nonnegativity, and in-phase timing, places each bad record
  in the inventory, and removes all records from one declared phase. Expected:
  the four relevant `EligibleExternalExchange` fields are false,
  `soundForSchedule = false` for each inserted bad record, and
  `everyPhaseCovered = false` for the missing phase.
- `ctrl_shared_context_mutation_matrix` starts with all nine Prop-valued shared
  comparators true and the `xiResidualAmount` equality holding, then applies
  these concrete mutations while retaining `ctx_offline`:

| comparator | mutation | expected result |
| --- | --- | --- |
| `e14ResidualOutstanding` | unregistered `(registrationId, asOf)` | false |
| `f3RouteResidueAwaitingReconciliation` | unregistered `(residueId, asOf)` | false |
| `xiValuationPolicyAccepted` | unregistered policy ID | false |
| `xiResidualAmount` | change matrix entry while retaining stored amount | amount equality false |
| `xiResidualAwaitingDischarge` | mark residual discharged before `asOf` | false |
| `ledgerEntryChargesRouteResidue` | change source ID and amount | false |
| `ledgerEntryChargesXiResidual` | change source ID and amount | false |
| `gateClosesExternalExchange` | gate ID names another channel | false |
| `e7AlarmObservationAccepted` | unregistered observation ID | false |
| `e5StressObservationAccepted` | unregistered observation ID | false |

- `ctrl_carriedness_conjunction_mutations` mutates a positive record to
  fallback source tag, `generatedByS = false`, and `inScope = false`. Expected:
  `E15Carried = false` in all three variants. Round B must repeat this check for
  representative debt, allocation, phase, exchange, gate, flow, and status
  policies.
- `ctrl_p2_gate_component_mutations` independently makes the gate uncarried,
  links it to another phase, breaks repair-generator linkage, changes the sort
  to P1, makes the D4 step unlawful, and makes the shared channel comparator
  false. Every variant predicts `P2ExternalExchangeGateEvidence = false` even
  though the complete exchange census remains zero.

## 5. Case Enumeration Coverage Audit

| E15 case item | registered comparison |
| ---: | --- |
| 1 | `claim_alternation_required.status` |
| 2 | `claim_online_sufficient.status` |
| 3 | `claim_offline_optional.status` |
| 4 | `claim_deficit_online_counterexample.status` |
| 5 | `claim_decorative_exchange_active.status` |
| 6 | `claim_decorative_no_discharge.status` |
| 7 | `claim_decorative_bad_reallocation.status` |
| 8 | `claim_duty_cycle_mismatch.status` |
| 9 | `claim_skipped_offline_cascade.status` |
| 10 | `ctrl_three_source_exact_aggregation` |
| 11 | `ctrl_e14_direct_witness_required` |
| 12 | `ctrl_f3_certificate_required` |
| 13 | `ctrl_xi_posthoc_scalarization_rejected` |
| 14 | `ctrl_xi_amount_without_matrix_rejected` |
| 15 | `ctrl_duplicate_physical_ledger_charge` |
| 16 | `ctrl_free_capacity_smuggling_rejected` |
| 17 | `ctrl_capacity_gain_equation` |
| 18 | `ctrl_gross_accrual_not_net_change` |
| 19 | `sweep_deficit_boundary` |
| 20 | `ctrl_incomplete_phase_flow_inventory` |
| 21 | `ctrl_recurrence_uses_online_duration` |
| 22 | `ctrl_posthoc_tolerance_rejected` |
| 23 | `ctrl_claim_scoping` |
| 24 | `ctrl_evidence_priority_not_status_tag` |
| 25 | `ctrl_alarm_without_e7_acceptance` |
| 26 | `ctrl_stress_without_e5_acceptance` |
| 27 | `ctrl_cascade_chronology_lineage_mutations` |
| 28 | `ctrl_e5_suspension_is_not_e15_offline` |
| 29 | `ctrl_offline_overcapacity_is_decorative` |
| 30 | `ctrl_incomplete_phase_flow_inventory` |
| 31 | `ctrl_exchange_census_omission`, `ctrl_exchange_census_record_duplicate`, `ctrl_exchange_census_id_duplicate`, `ctrl_exchange_eligibility_soundness_matrix` |
| 32 | `claim_zero_exchange_without_p2.status`, `ctrl_p2_gate_component_mutations` |

## 6. Registered Comparison List

Round B must emit one `PASS`/`FAIL` row for each of these **46 comparisons**,
in this order:

| # | registered comparison | expected value | Lean grounding |
| ---: | --- | --- | --- |
| 1 | `claim_alternation_required.status` | `alternation_required`; observed/predicted duty `1/4` | `AlternationRequiredCase` consumes `DutyCyclePredictionEvidence` after all four higher raw-evidence exclusions. |
| 2 | `claim_online_sufficient.status` | `online_sufficient`; alternation false | `OnlineSufficientEvidence` requires all-online, actual offset, `dischargeRate <= kappaOn`, and nonincreasing debt. |
| 3 | `claim_offline_optional.status` | `offline_optional` | `OptionalOfflineOutsideDeficitEvidence.everyOfflineGenuine` universally covers its offline phases. |
| 4 | `claim_deficit_online_counterexample.status` | `deficit_online_counterexample`; all lower Holds false | `DeficitOnlineBoundedCounterexample` checks strict deficit, bounded snapshots, all-online exchange, recurrence horizon, and online capacity. |
| 5 | `claim_decorative_exchange_active.status` | `decorative_offline`; exchange sum `1` | `DecorativeOfflineEvidence.concreteFailure` consumes the complete census. |
| 6 | `claim_decorative_no_discharge.status` | `decorative_offline`; discharged debt `0` | Nonpositive discharge and absent strict debt reduction are positive decorative failures. |
| 7 | `claim_decorative_bad_reallocation.status` | `decorative_offline`; exact allocation link false | The carried phase cannot borrow the claim's valid geometry. |
| 8 | `claim_duty_cycle_mismatch.status` | `duty_cycle_mismatch`; exact error `1/12 > 1/24` | `DutyCycleMismatchEvidence` uses preregistered tolerance and exact duty computations. |
| 9 | `claim_skipped_offline_cascade.status` | `skipped_offline_cascade` | `SkippedOfflineCascadeEvidence` checks growing debt, accepted carried observations, in-phase timestamps, chronology, and lineage. |
| 10 | `claim_zero_exchange_without_p2.status` | `offline_reclosure_rejected`; census zero, gate false | `GenuineOfflinePhaseEvidence` requires both zero exchange and a lawful accepted P2 gate. |
| 11 | `ctrl_three_source_exact_aggregation` | total `20`; omitting any source makes coverage false | `CompleteClosureDebtInventory` supplies soundness, coverage, key uniqueness, and physical-charge uniqueness. |
| 12 | `ctrl_e14_direct_witness_required` | local lookalike credited amount `0`; E14 item false | `E14ResidualDebtItem` consumes actual E14 concrete evidence plus its linked canonical `StatusedUnresolvedCase`. |
| 13 | `ctrl_f3_certificate_required` | F3 item false | The shared F3 awaiting-reconciliation comparator is mandatory in addition to carriedness and label. |
| 14 | `ctrl_xi_posthoc_scalarization_rejected` | Xi item false; declaration and amount links false | Xi scalarization is one predeclared shared policy, not a per-record fit. |
| 15 | `ctrl_xi_amount_without_matrix_rejected` | Xi record/item false | `residualComputed` must be literal vendored `adequacyResidual`. |
| 16 | `ctrl_duplicate_physical_ledger_charge` | `ledgerChargesNodup = false` | One physical charge cannot count under two component tags. |
| 17 | `ctrl_free_capacity_smuggling_rejected` | geometry false; no positive capacity branch | `kappaOn`/`kappaOff` are projections, not fixture parameters. |
| 18 | `ctrl_capacity_gain_equation` | `6 = 4 + 2`; fitted `11/2` and `13/2` rejected | `offlineInternalIsReallocation` and `E15_OfflineCapacityExactlyFreed`. |
| 19 | `ctrl_gross_accrual_not_net_change` | accrual rate `5`, discharge rate `3`, net change `2` | `AccruedDebt` and `DischargedDebt` are separate exact sums. |
| 20 | `sweep_deficit_boundary` | rates `7/2,4,5` -> statuses `online_sufficient, online_sufficient, alternation_required` | `PersistentDeficitEvidence` uses strict `kappaOn < accrualRate`; equality is sufficient capacity. |
| 21 | `ctrl_incomplete_phase_flow_inventory` | `everyPhaseCovered = false`; status `offline_reclosure_rejected` | `CompletePhaseFlowInventory` requires one complete flow for every phase. |
| 22 | `ctrl_recurrence_uses_online_duration` | all alternation fields pass except duration `4 <= 3`; alternation false and fallback status `offline_reclosure_rejected` | Complete `[O4,F1,O2,F1]` substrate isolates `PhaseDuration phase <= maximumOnlineRun`, not contiguous gap length. |
| 23 | `ctrl_posthoc_tolerance_rejected` | prediction and mismatch evidence both false | Tolerance must predate horizon start. |
| 24 | `ctrl_claim_scoping` | same scope, distinct claims retain `online_sufficient` and `duty_cycle_mismatch` | Matching and uniqueness use all five claim-key records. |
| 25 | `ctrl_evidence_priority_not_status_tag` | alternation case false; coexistence makes `statusUnique` false; canonical status remains counterexample | Lower case negates raw `DeficitOnlineCounterexampleEvidenceFor`; completeness also rejects conflicting carried tags. |
| 26 | `ctrl_alarm_without_e7_acceptance` | cascade evidence false | Stored E7 enum is not acceptance evidence. |
| 27 | `ctrl_stress_without_e5_acceptance` | cascade evidence false | Stored `stressed` tag is not E5 acceptance evidence. |
| 28 | `ctrl_cascade_chronology_lineage_mutations` | every registered mutation makes cascade evidence false | E15 checks both in-phase timestamp bounds, chronology, scope, and schedule membership. |
| 29 | `ctrl_e5_suspension_is_not_e15_offline` | E5 suspension true; E15 genuine offline false | E15 additionally requires its census, P2 external-channel gate, reallocation, and debt discharge. |
| 30 | `ctrl_offline_overcapacity_is_decorative.status` | `decorative_offline`, not `offline_optional` | One over-capacity phase defeats universal genuineness and realizes the decorative disjunct. |
| 31 | `ctrl_exchange_census_omission` | `completeForSchedule = false` | Every eligible carried exchange must occur. |
| 32 | `ctrl_exchange_census_record_duplicate` | `recordsNodup = false` | Full-record duplicates are rejected. |
| 33 | `ctrl_exchange_census_id_duplicate` | `recordIdsNodup = false` | Distinct records cannot reuse one census ID. |
| 34 | `ctrl_exchange_eligibility_soundness_matrix` | eligibility failures `[carried, phase, nonnegative, timing]`; soundness false; phase coverage false | `EligibleExternalExchange` and every field of `CompleteExternalExchangeInventory`. |
| 35 | `ctrl_shared_context_mutation_matrix` | nine baseline predicates true and Xi amount equality holds; each listed mutation makes its predicate or equality false | One nontrivial `OfflineReclosureClassifierContext` is shared by every claim. |
| 36 | `ctrl_carriedness_conjunction_mutations` | fallback/generated-false/out-of-scope -> `[false,false,false]` for each representative policy | `E15Carried` is the full D3 conjunction. |
| 37 | `ctrl_allocation_postdates_horizon` | geometry false | A carried allocation declared after horizon start cannot define capacities. |
| 38 | `ctrl_p2_gate_component_mutations` | all six variants make P2 gate evidence false while exchange stays zero | P2 sort, D4 lawfulness, phase, generator, carriedness, and shared channel link are independent requirements. |
| 39 | `ctrl_claim_match_key_mutations` | five claim-match results all false | `OfflineReclosureStatusRecordMatchesClaim` compares scope, allocation, schedule, tolerance, and recurrence bound. |
| 40 | `ctrl_debt_and_flow_duplicate_safety` | four duplicate-safety fields all false under their named mutation | Debt and flow records cannot inflate rates or totals by repetition. |
| 41 | `ctrl_online_discharge_capacity_bound` | persistent, bounded, and sufficient variants all reject solely because `5 <= 4` is false | Three complete schedules use whole-entry reserve-10 discharges; measured online discharge is bounded by derived `kappaOn`. |
| 42 | `census_offline_ablation_alarm_stress` | exact counts alarm/stress/valid chronology `4/4/4`; no registered collapse comparison | E15's cascade bridge is carried and chronological but does not prove collapse rates. |
| 43 | `ctrl_eight_way_partition_and_top_exclusion` | each status fixture has exactly one Holds; counterexample excludes all seven lower Holds | `CompleteOfflineReclosureStatus`, `E15_OfflineReclosureStatus`, and the mandatory top-priority regression theorem. |
| 44 | `ctrl_e14_wrong_canonical_status_rejected` | E14 debt item false; credited E14 amount `0` | `E14ResidualDebtItem.canonicalStatus`, `statusCase`, and `classifiedResidualLinked` (`E15OfflineReclosure.lean:369-407`) require the same full residual to have canonical E14 `statused_unresolved` classification, not merely concrete realization. |
| 45 | `ctrl_offline_flow_off_inventory_rejected` | genuine offline false; decorative offline false | `GenuineOfflinePhaseEvidence.flowMember` and `DecorativeOfflineEvidence.flowMember` (`E15OfflineReclosure.lean:864-894,1121-1151`) require the attempted flow to belong to the claim's complete flow inventory; `E15_OffInventoryFlowCannotCertifyOffline` (`:2456`) exposes both exclusions. |
| 46 | `ctrl_discharge_out_of_phase_rejected` | `everyDischargeLinked = false`; `CompleteClosureDebtFlow = false` | `CompleteClosureDebtFlow.everyDischargeLinked` (`E15OfflineReclosure.lean:678-688`) bounds `dischargedAt` inside the linked phase interval. |

All eight `OfflineReclosureStatus` constructors occur in rows 1-10.

## 7. Falsification Conditions

1. Row 1 is falsified if any offline phase lacks its own lawful P2 gate,
   complete zero-exchange census, exact reallocation, positive bounded
   discharge, recurrence witness, or exact duty match.
2. Row 2 is falsified if capacity availability substitutes for actual
   discharge, if discharge exceeds `kappaOn`, or if debt increases.
3. Row 3 is falsified if the implementation checks only one favorable offline
   phase instead of every offline phase.
4. Row 4 is falsified if the horizon/bound was not preregistered, if the
   horizon is not longer than `maximumOnlineRun`, or if discharge exceeds
   `kappaOn`.
5. Rows 5-7 are falsified if the three decorative mechanisms do not
   independently produce `decorative_offline` or if any reaches alternation.
6. Row 8 is falsified by floating-point duty arithmetic, post-hoc tolerance,
   or failure to classify the exact `1/12` mismatch.
7. Row 9 is falsified if labels replace E7/E5 acceptance, timestamps are not
   phase-bounded, chronology is wrong, or observations are from another claim.
8. Row 10 is falsified if a zero census is treated as proof of P2 gating.
9. Rows 11-16 are falsified if labels, copied IDs, missing witnesses, post-hoc
   valuation, missing Xi matrices, or duplicate physical charges enter debt.
10. Rows 17-18 are falsified if capacities are independently supplied or the
    exact `6 = 4 + 2` equation is not structural.
11. Row 19 is falsified if net debt change `2` is substituted for gross accrual
    `5`.
12. Row 20 is falsified if equality at `4` is classified as deficit or onset
    occurs anywhere other than the strict side of the boundary.
13. Rows 21-23 are falsified if incomplete flows, one-off/overlong online runs,
    or post-hoc tolerances satisfy positive duty evidence.
14. Row 24 is falsified if uniqueness is widened beyond the full five-record
    claim key.
15. Row 25 is falsified if a status-tag mismatch discharges a higher-priority
    evidence exclusion.
16. Rows 26-28 are falsified if enum labels, wrong chronology, out-of-phase
    times, or foreign lineage can produce the cascade.
17. Row 29 is falsified if E5 suspension is aliased to E15 offline mode.
18. Row 30 is falsified if one genuine phase hides another over-capacity phase.
19. Rows 31-34 are falsified if omission, duplicate records, duplicate IDs,
    unsound entries, or missing phase coverage can establish a complete census.
20. Row 35 is falsified if any shared comparator ignores its registered input
    mutation or a fixture replaces the shared context.
21. Row 36 is falsified if any carriedness field flip is ignored.
22. Row 37 is falsified if an allocation declared after horizon start defines
    geometry.
23. Row 38 is falsified if inactivity substitutes for any P2/D4/channel-link
    requirement.
24. Row 39 is falsified if a status record matches after any claim-key field is
    changed.
25. Row 40 is falsified if duplicated debt/accrual/discharge records can alter
    a sum or rate while completeness remains true.
26. Row 41 is falsified if any online consumer accepts discharge `5` under
    `kappaOn = 4`.
27. Row 42 is falsified if the exact alarm/stress census differs from `4/4/4`,
    or if a collapse-rate claim is added to the registered result.
28. Row 43 is falsified if any claim has zero or multiple Holds branches, or if
    genuine counterexample evidence coexists with a lower-priority Holds.
29. Row 44 is falsified if concrete E14 residual realization is credited
    without the linked carried E14 status occurrence, canonical
    `statused_unresolved` tag, full `StatusedUnresolvedCase`, and exact full-
    residual equality.
30. Row 45 is falsified if either positive or decorative offline evidence can
    use a carried complete phase-linked flow absent from the claim's
    `CompletePhaseFlowInventory.flows`.
31. Row 46 is falsified if a discharge outside its phase interval still
    satisfies `everyDischargeLinked` or `CompleteClosureDebtFlow`.
32. The entire sweep is falsified if any expected value is read from this table
    instead of recomputing records, sums, rates, census membership, geometry,
    comparator results, case priority, and claim matching.

## 8. Round B Implementation Guard

Round B must compute every Prop-mirroring fact from the registered finite data:

```text
E15Carried
E14ResidualDebtItem / actual StatusedUnresolvedEvidence and linked canonical
  StatusedUnresolvedCase/status occurrence
F3RouteResidueDebtItem
XiAdequacyResidualDebtItem / adequacyResidual
CompleteClosureDebtInventory / ClosureDebt
CompleteClosureDebtSnapshot
CompleteClosureDebtFlow / in-phase discharge linkage
AccruedDebt / DischargedDebt / PhaseDuration
ClosureDebtAccrualRate / ClosureDebtDischargeRate
DerivedOfflineBudgetGeometry / kappaOn / freedAllocation / kappaOff
CompletePhaseFlowInventory
EligibleExternalExchange
CompleteExternalExchangeInventory / ExchangeInPhase
P2ExternalExchangeGateEvidence
PersistentDeficitEvidence
GenuineOfflinePhaseEvidence / flowMember
AlternatingOfflineSubstrate
DutyCyclePredictionEvidence / DutyCycleMismatchEvidence
OnlineSufficientEvidence
OptionalOfflineOutsideDeficitEvidence
DeficitOnlineBoundedCounterexample
DecorativeOfflineEvidence / flowMember
SkippedOfflineCascadeEvidence
OfflineReclosureStatusRecordMatchesClaim
OfflineReclosureStatusOccurrenceFor
all seven record-independent EvidenceFor predicates
all eight priority-normalized Case predicates
CompleteOfflineReclosureStatus
```

The classifier must execute the exact committed priority chain for the same
claim. Every lower case must negate raw record-independent EvidenceFor facts,
never sibling cases on the same status record. The implementation must emit
exactly 46 rows in the registered order above and may not contain a static
status map, expected-status field, hardcoded discipline flag, random branch, or
floating-point E15 calculation.

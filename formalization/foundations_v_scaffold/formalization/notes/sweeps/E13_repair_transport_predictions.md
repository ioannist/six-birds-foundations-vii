# E13 Repair Transport Law - Toy-Lab Predictions (Round A, pre-registration)

This document pre-registers the toy-lab probe for E13 before any E13 sweep
implementation exists. It is grounded in the accepted six-field normal form
`formalization/notes/examples/E13.md` and the mechanized Lean module
`lean/SixBirdsFoundationsV/Laws/E13RepairTransport.lean`.

The probe mirrors the Lean predicates, not a looser prose reading. In
particular, E13 is scoped by a concrete `TransportClaimRef`; credited positive
transport must pass through `InterCarrierBridge` with paid defects; receiver
repair credit uses the candidate's own `TargetRepairRecord` and
`TransportDeltaReduction`; scaffolding/forcing is computed by the shared
`RepairTransportClassifierContext.forceComparator`; and falsifier structures
must be linked to the same token/package/bridge/family named by the claim.

All quantities below are exact rationals, written as fractions. Round B must
use `fractions.Fraction` and no floating-point arithmetic or randomness.

Round B must report exactly 19 registered comparisons.

## 1. Toy-Lab Configuration

### Two carriers and bridge records

The fixture contains two deterministic finite E-system carriers:

```text
S_A.Z = {A0, A1, A2, A3}
S_B.Z = {B0, B1, ..., B7}
S_A.T.suppK(Ai, Aj) := j = (i + 1) mod 4
S_B.T.suppK(Bi, Bj) := j = (i + 1) mod 8
```

The primary bridge is:

```text
bridge_paid_ab:
  bridgeId = 10
  sourceCarrier = carrier_A
  targetCarrier = carrier_B
  channelRecord = channel_ab_main
```

The rejected bridge is:

```text
bridge_unpaid_ab:
  bridgeId = 11
  sourceCarrier = carrier_A
  targetCarrier = carrier_B
  channelRecord = channel_ab_unpaid
```

The flow-crossing control uses a separate bridge record that is named by the
status record but is not constructible as an E13 `InterCarrierBridge`:

```text
bridge_flow_unlinked_ab:
  bridgeId = 12
  sourceCarrier = carrier_A
  targetCarrier = carrier_B
  channelRecord = channel_boundary_flow_only
  carried bridge occurrence = absent
  bridge defect ledger evidence = absent
```

Bridge defects are paid by a shared `BridgeDischargeComparator`, not by a bare
flag:

```text
BridgeDischargeComparator.discharges(defect, sourceLedger, targetLedger)
  := sourceLedger.bridgeRef = defect.bridgeRef
     and targetLedger.bridgeRef = defect.bridgeRef
     and sourceLedger.amount + targetLedger.amount >= defect.cost
```

| defect | bridge | cost | source ledger | target ledger | computed discharge |
| --- | --- | ---: | ---: | ---: | --- |
| `def_paid_ab` | `bridge_paid_ab` | `1` | `3/5` | `2/5` | true |
| `def_unpaid_ab` | `bridge_unpaid_ab` | `1` | `1/5` | `1/5` | false |

Every positive carried record uses source tag `committed_state` or
`audited_cell_records`, `generatedByS = true`, and `inScope = true`.
Rejected uncarried controls intentionally omit this D3 occurrence data.

### Taxonomy, roles, and shared comparator context

The declared taxonomy is `taxonomy_transport_v1`:

| challenge class | taxonomy id | role |
| --- | ---: | --- |
| `C_navigation` | `1` | source class for the main package |
| `C_power` | `1` | different-class influence control |
| `C_language` | `1` | symbol context family |

`SameTransportChallengeClass(taxonomy, C, C')` is computed by exact challenge
id equality under the same taxonomy id. Thus:

```text
same(C_navigation, C_navigation) = true
same(C_navigation, C_power) = false
same(C_language, C_language) = true
```

The shared `RepairTransportClassifierContext ctx_main` contains:

```text
taxonomy = taxonomy_transport_v1
bridgeDischargeComparator = the comparator above
quotientInstall.installedBy(move, qAfter)
  := qAfter.installedMoveRecord = move.moveRecord
roleComparator.preserves(sourceRole, targetRole)
  := sourceRole.roleId = targetRole.roleId
     and sourceRole.challengeClass = targetRole.challengeClass
activationComparator.roleActiveAfter(postState, role, family)
  := role.roleId in postState.activeRoleIds[family.familyId]
forceComparator.classifies(schedule, opportunities, mode)
  := mode is computed from the force schedule and opportunity list:
     empty opportunities + forceLevel = 1 -> fully_forced_response
     aidPresent = true + forceLevel = 0 -> scaffolded_response
     cueOnly = true + forceLevel = 0 -> primed_response
     nonempty opportunities + no aid/cue/force -> observed_free_response
```

The comparator bundle is shared by every row. Round B must not install
per-scenario comparator lambdas.

### Tokens, source packages, target repairs, and Delta readouts

The navigation/source repair package schema is instantiated as distinct
token/package records for each registered claim. This avoids a false global
status conflict: `CompleteRepairTransportStatus.statusUnique` is scoped by
`TransportClaimRef`, so separate status scenarios must use separate claim refs
unless the row explicitly says it is a scoping control.

```text
pkg_nav_*:
  sourceChallenge = C_navigation
  roleRecord = role_nav_filter

tok_nav_*:
  sourceCarrier = carrier_A
  targetCarrier = carrier_B
  emittedFor = C_navigation
```

| row family | token | package |
| --- | --- | --- |
| clean communication | `tok_nav_comm` | `pkg_nav_comm` |
| teaching | `tok_nav_teach` | `pkg_nav_teach` |
| coercion-null | `tok_nav_force` | `pkg_nav_force` |
| scaffolding | `tok_nav_scaffold` | `pkg_nav_scaffold` |
| priming | `tok_nav_prime` | `pkg_nav_prime` |
| influence | `tok_nav_influence` | `pkg_nav_influence` |
| unpaid bridge rejection | `tok_nav_unpaid` | `pkg_nav_unpaid` |
| uncarried repair rejection | `tok_nav_uncarried` | `pkg_nav_uncarried` |
| role-preservation rejection | `tok_nav_role_drift` | `pkg_nav_role_drift` |
| parameter-channel rejection | `tok_nav_parameter` | `pkg_nav_parameter` |
| flow-crossing rejection | `tok_nav_flow` | `pkg_nav_flow` |

The symbol package schema is likewise instantiated per symbol claim:

```text
pkg_lang_*:
  sourceChallenge = C_language
  roleRecord = role_lang_handle

tok_symbol_*:
  sourceCarrier = carrier_A
  targetCarrier = carrier_B
  emittedFor = C_language
```

| row family | token | package |
| --- | --- | --- |
| stable symbol | `tok_symbol_stable` | `pkg_lang_stable` |
| context instability | `tok_symbol_instability` | `pkg_lang_instability` |
| role drift | `tok_symbol_role_drift` | `pkg_lang_role_drift` |
| saturation relabel | `tok_symbol_saturation` | `pkg_lang_saturation` |

Delta readouts are represented by exact split-pair sets:

```text
Delta(qBefore, F_C, r_B) = readout.preSplits
Delta(qAfter, F_C, r_B) = readout.postSplits
TransportDeltaReduction = postSplits proper-subset preSplits
  and qAfter.installedMoveRecord = targetRepair.inducedMove.moveRecord
```

| target repair | token | target class | move | target role | pre splits | post splits | carried? | lawful? | role preserved? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `repair_nav_clean` | `tok_nav_comm` | `C_navigation` | `mv_nav_clean` | `role_nav_filter` | `{p01,p02,p03}` | `{p01}` | true | true | true |
| `repair_nav_teach_initial` | `tok_nav_teach` | `C_navigation` | `mv_nav_teach_initial` | `role_nav_filter` | `{p04,p05,p06}` | `{p04,p05}` | true | true | true |
| `repair_nav_later_capacity` | `tok_nav_teach` | `C_navigation` | `mv_nav_later` | `role_nav_filter` | `{p04,p05}` | `{p04}` | true as `committed_state` | true | true |
| `repair_nav_scaffold_immediate` | `tok_nav_scaffold` | `C_navigation` | `mv_nav_scaffold` | `role_nav_filter` | `{p07,p08}` | `{p07}` | true while A present | true | true |
| `repair_nav_prime_immediate` | `tok_nav_prime` | `C_navigation` | `mv_nav_prime` | `role_nav_filter` | `{p09,p12}` | `{p09}` | true while A present | true | true |
| `repair_nav_unpaid` | `tok_nav_unpaid` | `C_navigation` | `mv_nav_unpaid` | `role_nav_filter` | `{p13,p14}` | `{p13}` | true | true | true |
| `repair_power_influence` | `tok_nav_influence` | `C_power` | `mv_power` | `role_power_filter` | `{p10,p11}` | `{p10}` | true | true | true within `C_power` |
| `repair_nav_uncarried` | `tok_nav_uncarried` | `C_navigation` | `mv_nav_uncarried` | `role_nav_filter` | `{p20,p21}` | `{p20}` | false | true | true |
| `repair_nav_role_drift` | `tok_nav_role_drift` | `C_navigation` | `mv_nav_drift` | `role_power_filter` | `{p30,p31}` | `{p30}` | true | true | false |
| `repair_symbol_ctx1` | `tok_symbol_stable` | `C_language` | `mv_symbol_c1` | `role_lang_handle` | `{s1,s2}` | `{s1}` | true | true | true |
| `repair_symbol_ctx2` | `tok_symbol_stable` | `C_language` | `mv_symbol_c2` | `role_lang_handle` | `{s3,s4}` | `{s3}` | true | true | true |
| `repair_symbol_ctx2_drift` | `tok_symbol_role_drift` | `C_language` | `mv_symbol_c2_drift` | `role_other_handle` | `{s3,s4}` | `{s3}` | true | true | false |

The uncarried row has genuine raw Delta reduction, but no
`CarriedRecordAt targetRepairPolicy repair_nav_uncarried ...` witness. It
therefore cannot satisfy `CommunicationTransportEvidence` or
`DifferentClassInfluenceEvidence`.

### Force schedules, opportunity censuses, and A-absence probes

The force/opportunity data is finite and computed by `ctx_main.forceComparator`.

| interaction | token | forceLevel | aidPresent | cueOnly | opportunities | computed mode |
| --- | --- | ---: | --- | --- | --- | --- |
| `force_full_nav` | `tok_nav_force` | `1` | false | false | `[]` | `fully_forced_response` |
| `force_scaffold_nav` | `tok_nav_scaffold` | `0` | true | false | `[free_choice_1]` | `scaffolded_response` |
| `force_prime_nav` | `tok_nav_prime` | `0` | false | true | `[free_choice_1]` | `primed_response` |
| `force_free_nav` | `tok_nav_teach` | `0` | false | false | `[free_choice_1, free_choice_2]` | `observed_free_response` |

The A-absence probe schedule for teaching is:

```text
schedule_A_absent_nav:
  challengeClass = C_navigation
  probeTimes = [5, 6]
  aCarrierPresentAt(5) = false
  bridgeOpenAt(5) = false
  aCarrierPresentAt(6) = false
  bridgeOpenAt(6) = false
```

`repair_nav_later_capacity` is carried by B at time `5` with
`sourceTag = committed_state`, `generatedByS = true`, and `inScope = true`.

The scaffolding and priming controls use the same token/package class but have
no later A-absent B-committed capacity witness.

### Symbol context family and current-structure guard

The declared context family is:

```text
family_language:
  familyId = 300
  contexts = [ctx_lang_prompt, ctx_lang_tool]
  atLeastTwoContexts = true
```

Stable symbol data:

```text
ctx_lang_prompt -> repair_symbol_ctx1
ctx_lang_tool   -> repair_symbol_ctx2
role ids both role_lang_handle
current structure before receipt does not carry role_lang_handle
activation after receipt carries role_lang_handle in family_language
```

Rejected symbol controls:

```text
reject_symbol_context_instability:
  ctx_lang_prompt reactivates, ctx_lang_tool has no reactivation

reject_symbol_role_drift:
  ctx_lang_prompt reactivates role_lang_handle
  ctx_lang_tool reactivates role_other_handle

reject_saturation_relabel:
  current structure already carries role_lang_handle before token receipt
  no genuine new package reactivation is credited
```

## 2. Registered Theorem-Facing Predictions

Round B must report exactly 19 registered comparisons.

| theorem / apparatus | concrete instantiation | registered prediction |
| --- | --- | --- |
| `E13_Communication` | `claim_comm_clean = communication(tok_nav_comm, pkg_nav_comm, bridge_paid_ab, C_navigation)` | `CommunicatedHolds = true`; partition status `communicated` |
| `E13_TeachingCapacity` | `claim_teach_absent_capacity = teaching(tok_nav_teach, pkg_nav_teach, bridge_paid_ab, C_navigation)` | `TaughtHolds = true`; partition status `taught` |
| `E13_CoercionNull` | `claim_force_null = communication(tok_nav_force, pkg_nav_force, bridge_paid_ab, C_navigation)` with `force_full_nav` | `CoercionNullHolds = true`; partition status `coercion_null` |
| `E13_SymbolicRepair` | `claim_symbol_stable = symbol(tok_symbol_stable, pkg_lang_stable, bridge_paid_ab, family_language)` | `SymbolicHolds = true`; partition status `symbolic` |
| `E13_StatusPartition` | every registered `claimRef` below | exactly one of the seven status predicates holds for that claim |

## 3. Registered Status Scenarios

### `claim_comm_clean`

| field | predicted value |
| --- | --- |
| claim ref | `communication(tok_nav_comm, pkg_nav_comm, bridge_paid_ab, C_navigation)` |
| carried status record | `status_comm_clean`, status `communicated` |
| bridge defects paid | true (`3/5 + 2/5 >= 1`) |
| interface mediation | true (`bridge_paid_ab` and `taxonomy_transport_v1` linked on both carriers) |
| target repair carried/lawful | true |
| `TransportDeltaReduction` | true (`{p01} proper-subset {p01,p02,p03}` and `qAfter.installedMoveRecord = mv_nav_clean`) |
| same challenge class | true (`C_navigation = C_navigation`) |
| role preservation | true (`role_nav_filter = role_nav_filter`) |
| predicted status | `communicated` |

### `claim_teach_absent_capacity`

| field | predicted value |
| --- | --- |
| claim ref | `teaching(tok_nav_teach, pkg_nav_teach, bridge_paid_ab, C_navigation)` |
| carried status record | `status_teach_absent_capacity`, status `taught` |
| communication witness for same token/package/bridge/class | true via `repair_nav_teach_initial` |
| A-absent probe schedule | true (`probeTimes = [5,6]`, A absent and bridge closed at both) |
| B committed repair in A absence | true (`repair_nav_later_capacity` carried as `committed_state` at time `5`) |
| later repair same class | true |
| predicted status | `taught` |

### `claim_force_null`

| field | predicted value |
| --- | --- |
| claim ref | `communication(tok_nav_force, pkg_nav_force, bridge_paid_ab, C_navigation)` |
| carried status record | `status_force_null`, status `coercion_null` |
| forcing record | `force_full_nav` |
| computed response mode | `fully_forced_response` |
| free-response opportunities | `[]` |
| B-committed transported repair exists | false |
| quotient refined by forced response | false (`Delta(qAfterForce) = Delta(qBeforeForce)`) |
| predicted status | `coercion_null` |

### `claim_symbol_stable`

| field | predicted value |
| --- | --- |
| claim ref | `symbol(tok_symbol_stable, pkg_lang_stable, bridge_paid_ab, family_language)` |
| carried status record | `status_symbol_stable`, status `symbolic` |
| family non-vacuity | true (`2` contexts) |
| bridge paid | true |
| every context reactivates | true |
| roles stable across contexts | true (`role_lang_handle` in both) |
| saturation strict | true (role was not already carried before receipt) |
| predicted status | `symbolic` |

### `claim_scaffolded_no_capacity`

| field | predicted value |
| --- | --- |
| claim ref | `teaching(tok_nav_scaffold, pkg_nav_scaffold, bridge_paid_ab, C_navigation)` |
| carried status record | `status_scaffolded_no_capacity`, status `scaffolded_or_primed` |
| forcing record | `force_scaffold_nav` |
| computed response mode | `scaffolded_response` |
| record forcing link | `record.forcingRecord = force_scaffold_nav` |
| immediate B improvement | true |
| later A-absent B-committed capacity | false |
| predicted status | `scaffolded_or_primed` |

### `claim_primed_no_capacity`

| field | predicted value |
| --- | --- |
| claim ref | `communication(tok_nav_prime, pkg_nav_prime, bridge_paid_ab, C_navigation)` |
| carried status record | `status_primed_no_capacity`, status `scaffolded_or_primed` |
| forcing record | `force_prime_nav` |
| computed response mode | `primed_response` |
| record forcing link | `record.forcingRecord = force_prime_nav` |
| later A-absent B-committed capacity | false |
| predicted status | `scaffolded_or_primed` |

### `claim_influence_different_class`

| field | predicted value |
| --- | --- |
| claim ref | `communication(tok_nav_influence, pkg_nav_influence, bridge_paid_ab, C_power)` |
| carried status record | `status_influence_different_class`, status `influence_only` |
| target repair | `repair_power_influence` |
| record/claim occurrence match | true (`repair_power_influence.targetChallenge = C_power`) |
| source package class | `pkg_nav_influence.sourceChallenge = C_navigation` |
| target repair carried/lawful | true |
| bridge linked and paid | true |
| `TransportDeltaReduction` | true (`{p10} proper-subset {p10,p11}`) |
| same challenge class | false between source package and target repair (`C_navigation != C_power`) |
| predicted status | `influence_only` |

## 4. Registered Rejection Scenarios

Each row below is predicted `transport_rejected`. Round B must distinguish the
reason, not only the final label.

### `reject_unpaid_bridge`

| field | predicted value |
| --- | --- |
| claim ref | `communication(tok_nav_unpaid, pkg_nav_unpaid, bridge_unpaid_ab, C_navigation)` |
| bridge discharge | false (`1/5 + 1/5 < 1`) |
| target repair | `repair_nav_unpaid` |
| `InterCarrierBridge` constructible | false |
| positive communication evidence | false |
| predicted status | `transport_rejected` |

### `reject_uncarried_target_repair`

| field | predicted value |
| --- | --- |
| claim ref | `communication(tok_nav_uncarried, pkg_nav_uncarried, bridge_paid_ab, C_navigation)` |
| target repair | `repair_nav_uncarried` |
| raw Delta reduction | true (`{p20} proper-subset {p20,p21}`) |
| target repair carried | false |
| communication / influence evidence constructible | false |
| predicted status | `transport_rejected` |

### `reject_role_preservation_failure`

| field | predicted value |
| --- | --- |
| claim ref | `communication(tok_nav_role_drift, pkg_nav_role_drift, bridge_paid_ab, C_navigation)` |
| target repair | `repair_nav_role_drift` |
| same-class Delta reduction | true |
| role preservation | false (`role_nav_filter != role_power_filter`) |
| communication evidence constructible | false |
| predicted status | `transport_rejected` |

### `reject_symbol_context_instability`

| field | predicted value |
| --- | --- |
| claim ref | `symbol(tok_symbol_instability, pkg_lang_instability, bridge_paid_ab, family_language)` |
| context family | `[ctx_lang_prompt, ctx_lang_tool]` |
| missing reactivation | `ctx_lang_tool` |
| `SymbolicRepairEvidence` constructible | false |
| predicted status | `transport_rejected` |

### `reject_symbol_role_drift`

| field | predicted value |
| --- | --- |
| claim ref | `symbol(tok_symbol_role_drift, pkg_lang_role_drift, bridge_paid_ab, family_language)` |
| reactivation in every context | true |
| roles stable | false (`role_lang_handle` vs `role_other_handle`) |
| `SymbolicRepairEvidence` constructible | false |
| predicted status | `transport_rejected` |

### `reject_saturation_relabel`

| field | predicted value |
| --- | --- |
| claim ref | `symbol(tok_symbol_saturation, pkg_lang_saturation, bridge_paid_ab, family_language)` |
| current structure already carries role | true |
| genuine new reactivation credited | false |
| `SymbolSaturationStrict` | false |
| predicted status | `transport_rejected` |

### `reject_parameter_channel_only`

| field | predicted value |
| --- | --- |
| claim ref | `communication(tok_nav_parameter, pkg_nav_parameter, bridge_paid_ab, C_navigation)` |
| channel changes B parameters | true |
| carried target repair record | absent |
| role-preserving repair package transport | false |
| predicted status | `transport_rejected` |

### `reject_flow_crossing_no_bridge`

| field | predicted value |
| --- | --- |
| claim ref | `communication(tok_nav_flow, pkg_nav_flow, bridge_flow_unlinked_ab, C_navigation)` |
| E12-style boundary/flow crossing record exists | true (`flow_boundary_crossing_1`) |
| referenced bridge record | `bridge_flow_unlinked_ab` |
| carried bridge occurrence / paid defect evidence | absent |
| `InterCarrierBridge` for crossing | false |
| predicted status | `transport_rejected` |

## 5. Null and Control Predictions

### `ctrl_shared_comparator_bundle_nontrivial`

| field | predicted value |
| --- | --- |
| shared context | `ctx_main` |
| force comparator accepts | `force_full_nav -> fully_forced_response`, `force_scaffold_nav -> scaffolded_response`, `force_prime_nav -> primed_response` |
| role comparator accepts | `role_nav_filter` to `role_nav_filter` |
| role comparator rejects | `role_nav_filter` to `role_power_filter` |
| bridge comparator accepts | `def_paid_ab` |
| bridge comparator rejects | `def_unpaid_ab` |
| registered prediction | one shared comparator bundle produces both true and false results from real data |

This is falsified if Round B installs per-row comparator functions that can be
chosen to make every row pass.

### `ctrl_transport_claim_kind_scoping`

| field | predicted value |
| --- | --- |
| status record | `status_comm_clean` |
| matches `claim_comm_clean` | true |
| matches `teaching(tok_nav_comm, pkg_nav_comm, bridge_paid_ab, C_navigation)` | false |
| matches `symbol(tok_nav_comm, pkg_nav_comm, bridge_paid_ab, family_language)` | false |
| registered prediction | `TransportStatusRecordMatchesClaim` is claim-kind-aware |

This is falsified if a communication-kind status record can satisfy a teaching
or symbol claim for the same token and bridge.

### `ctrl_claim_independence`

| field | predicted value |
| --- | --- |
| first claim | `claim_comm_clean -> communicated` |
| second claim | `symbol(tok_symbol_stable, pkg_lang_stable, bridge_paid_ab, family_language) -> symbolic` |
| token/package overlap | none (`tok_nav_comm/pkg_nav_comm` vs `tok_symbol_stable/pkg_lang_stable`) |
| status uniqueness scope | per `TransportClaimRef`, not global |
| registered prediction | both claims keep independent statuses |

This is falsified if `CompleteRepairTransportStatus.statusUnique` is applied
globally across all status records instead of per claim.

### `ctrl_falsifier_claim_linkage`

| field | predicted value |
| --- | --- |
| falsifier evidence token | `tok_symbol_stable` |
| falsified claim token | `tok_nav_comm` |
| falsifier evidence bridge | `bridge_unpaid_ab` |
| falsified claim bridge | `bridge_paid_ab` |
| `claimLinked` field satisfiable | false |
| registered prediction | mismatched-token/bridge falsifier cannot be constructed |

This directly targets the Lean status-apparatus review fixes that added
claim-linking fields to the falsifier structures.

## 6. Registered Comparison List

Round B must emit one `PASS`/`FAIL` row for each of these 19 comparisons:

| # | registered comparison | expected value |
| ---: | --- | --- |
| 1 | `claim_comm_clean.status` | `communicated` |
| 2 | `claim_teach_absent_capacity.status` | `taught` |
| 3 | `claim_force_null.status` | `coercion_null` |
| 4 | `claim_symbol_stable.status` | `symbolic` |
| 5 | `claim_scaffolded_no_capacity.status` | `scaffolded_or_primed` |
| 6 | `claim_primed_no_capacity.status` | `scaffolded_or_primed` |
| 7 | `claim_influence_different_class.status` | `influence_only` |
| 8 | `reject_unpaid_bridge.status` | `transport_rejected`; bridge discharge false |
| 9 | `reject_uncarried_target_repair.status` | `transport_rejected`; raw Delta reduction does not compensate for missing carried repair record |
| 10 | `reject_role_preservation_failure.status` | `transport_rejected`; role comparator false |
| 11 | `reject_symbol_context_instability.status` | `transport_rejected`; missing reactivation in one declared context |
| 12 | `reject_symbol_role_drift.status` | `transport_rejected`; unstable role across contexts |
| 13 | `reject_saturation_relabel.status` | `transport_rejected`; current structure already carries the role |
| 14 | `reject_parameter_channel_only.status` | `transport_rejected`; no carried target repair record |
| 15 | `reject_flow_crossing_no_bridge.status` | `transport_rejected`; no paid E13 bridge |
| 16 | `ctrl_shared_comparator_bundle_nontrivial` | shared `ctx_main` computes both accepting and rejecting comparator results |
| 17 | `ctrl_transport_claim_kind_scoping` | communication record matches only communication claim, not teaching/symbol claims |
| 18 | `ctrl_claim_independence` | distinct claims keep independent statuses |
| 19 | `ctrl_falsifier_claim_linkage` | mismatched-token/bridge falsifier linkage is false |

## 7. Falsification Conditions

1. `claim_comm_clean` is falsified if bridge paidness, interface mediation,
   same-class alignment, role preservation, target repair carriedness, or
   target-owned Delta reduction is skipped; it is also falsified if the status
   is not exactly `communicated`.
2. `claim_teach_absent_capacity` is falsified if teaching is credited without
   the same communication witness plus a later B-committed repair during an
   A-absent, bridge-closed probe.
3. `claim_force_null` is falsified if a fully forced interaction is accepted
   from a self-declared enum instead of the force/opportunity census, if a
   B-committed transported repair exists, or if the status is not
   `coercion_null`.
4. `claim_symbol_stable` is falsified if `family_language` has fewer than two
   contexts, if any context lacks role-preserving reactivation, if the role
   drifts, if saturation strictness is ignored, or if the status is not
   `symbolic`.
5. `claim_scaffolded_no_capacity` is falsified if the status record's
   `forcingRecord` is not linked to the witness's own
   `scaffoldedOrPrimed.interaction`, if A-absent capacity is credited anyway,
   or if the status is not `scaffolded_or_primed`.
6. `claim_primed_no_capacity` is falsified if the same shared force comparator
   does not compute `primed_response`, or if priming is misclassified as
   teaching/communication.
7. `claim_influence_different_class` is falsified if the claim target class
   does not match `repair_power_influence.targetChallenge = C_power`, if the
   source-package-vs-target-repair class comparison is skipped, if a carried
   lawful different-class repair is rejected as uncarried, or if it is
   incorrectly classified as `communicated`.
8. `reject_unpaid_bridge` is falsified if bridge discharge is accepted from a
   flag rather than computed from exact ledger values.
9. `reject_uncarried_target_repair` is falsified if raw Delta reduction alone
   can enter a positive transport branch without D3 carried target-repair
   occurrence.
10. `reject_role_preservation_failure` is falsified if same-class Delta
    reduction is enough for communication despite role comparator failure.
11. `reject_symbol_context_instability` is falsified if symbolic status is
    credited without reactivation in every declared context.
12. `reject_symbol_role_drift` is falsified if symbolic status ignores role
    instability across contexts.
13. `reject_saturation_relabel` is falsified if a pre-existing active role is
    accepted as symbolic repair reactivation.
14. `reject_parameter_channel_only` is falsified if parameter changes with no
    carried target repair are treated as E13 transport.
15. `reject_flow_crossing_no_bridge` is falsified if the bare
    `flow_boundary_crossing_1` record or the nonconstructible
    `bridge_flow_unlinked_ab` reference is treated as E13 repair transport
    without carried bridge occurrence and paid defect evidence.
16. `ctrl_shared_comparator_bundle_nontrivial` is falsified if any comparator is
    a per-instance trivially true predicate rather than the shared `ctx_main`
    computation over finite records.
17. `ctrl_transport_claim_kind_scoping` is falsified if
    `TransportStatusRecordMatchesClaim` ignores `TransportClaimKind` or allows
    a communication record to satisfy a teaching/symbol claim.
18. `ctrl_claim_independence` is falsified if status uniqueness is global across
    all status records instead of scoped by the queried `TransportClaimRef`.
19. `ctrl_falsifier_claim_linkage` is falsified if a falsifier whose evidence
    names a different token or bridge can refute the queried claim.
20. The future sweep is falsified if any registered row is produced by a lookup
    table instead of evaluating the carried records, exact ledger/discharge
    values, Delta split sets, shared comparator bundle, and priority-normalized
    case predicates.

## 8. Round B Implementation Guard

Round B must compute all certified boolean/Prop-mirroring facts from fixture
data:

```text
BridgeDischargeComparator.discharges
BridgeDefectsPaid
InterfaceMediationCertified
SameTransportChallengeClass
TransportDeltaReduction
InducedBRepair / target repair carriedness
RolePreservingTransportCertified
BCommittedRepairInAAbsence
FullyForcedInteraction
CoercionNullCertified
ScaffoldedOrPrimedInteraction
ScaffoldingOrPrimingWitness
ContextualRepairReactivation
SymbolSaturationStrict
SymbolicRepairEvidence
TransportStatusRecordMatchesClaim
CompleteRepairTransportStatus
```

No status in this document may be hardcoded as a lookup value. The registered
status labels are predictions about what the predicate mirror should compute
from the finite two-carrier fixture.

# E3 Self-Maintaining Reclosure Predictions

This is the pre-registered prediction artifact for the E3 toy-laboratory
probe. It is intentionally written before any E3 sweep implementation exists.
Round B should implement the sweep against this document, not redesign the
configuration after seeing results.

No experiment has been run for this artifact. All quantities below are exact
and should be represented with `fractions.Fraction` where arithmetic is
needed. This E3 Round A instance is fully deterministic: no random seed,
stochastic simulation, or hash-audited float branch is required.

## 1. Toy-Lab Configuration

### Repair-World Carrier And Closure Apparatus

The sweep specializes `lab/sixbirds_foundations_v/worlds/repair_world.py`.
It uses the same four-item carrier fixture as the E1 and E2 toy labs:

```text
X = {a,b,c,d}.
```

The object-level quotient starts from the E1/E2 base quotient:

| item | `Q0(item)` |
| --- | --- |
| `a` | `u` |
| `b` | `u` |
| `c` | `v` |
| `d` | `v` |

E3 uses the existing `RepairWorldState.A` field as the carrier hook for the
active apparatus:

```python
state.A = AuditState(instrument=I_gate, flags=AuditFlags(frozenset({0})))
```

Round B may extend the lawfulness checker behind `MaintenanceStubAction`, but
the registered predictions below are about concrete carried apparatus,
maintenance-operator, reinstatement, and status records. The future sweep must
derive statuses from those records and transitions.

The main apparatus records are:

| apparatus | time | `gateInstrument` | `thresholdRecords` | `AppBoundary` | `auditData` | `apparatusRecord` | ledger entries | audit records |
| --- | ---: | --- | --- | ---: | ---: | --- | --- | --- |
| `app_0` | `0` | `I_gate` | `[theta_gate, theta_budget]` | `10` | `100` | `app_rec_0` | `[led_app_0]` | `[aud_app_0]` |
| `app_1` | `1` | `I_gate` | `[theta_gate, theta_budget]` | `10` | `101` | `app_rec_1` | `[led_app_1]` | `[aud_app_1]` |
| `app_2_pre` | `2` | `I_gate` | `[theta_gate, theta_budget]` | `20` | `200` | `app_rec_2_pre` | `[led_app_2_pre]` | `[aud_app_2_pre]` |
| `app_2_post` | `3` | `I_gate` | `[theta_gate, theta_budget]` | `21` | `200` | `app_rec_2_post` | `[led_app_2_post]` | `[aud_app_2_post]` |
| `app_crystal_0` | `0` | `I_gate_crystal` | `[theta_crystal]` | `30` | `300` | `app_rec_crystal_0` | `[led_app_crystal]` | `[aud_app_crystal]` |
| `app_decay_0` | `0` | `I_gate_decay` | `[theta_decay]` | `40` | `400` | `app_rec_decay_0` | `[led_app_decay]` | `[aud_app_decay]` |
| `app_decay_1` | `1` | `I_gate_decay` | `[theta_decay_drifted]` | `44` | `404` | `app_rec_decay_1` | `[led_app_decay_1]` | `[aud_app_decay_1]` |

All listed ledger entries are in `S.Lambda_S.ledgerEntries`. All listed audit
records have `HasCarriedRecordEvidence(S.auditRecordPolicy, auditRecord)`.
All listed closure-apparatus records are carried under `appPolicy` with:

```text
sourceTag = committed_state
generatedByS = true
inScope = true
```

### Maintenance Operator And Full Reinstatement Equality

The maintained challenge-free instance uses:

```text
m_keep.operatorRecord = m_keep_record
m_keep.operatorLedgerEntries = [led_m_keep]
m_keep.operatorAuditRecords = [aud_m_keep]
m_keep.apply(z_app_0) = app_1
```

The reinstatement record is:

| field | value |
| --- | --- |
| `time` | `0` |
| `sourceState` | `z_app_0` |
| `targetState` | `z_app_1` |
| `operatorRecord` | `m_keep_record` |
| `preAppRecord` | `app_rec_0` |
| `postAppRecord` | `app_rec_1` |
| `outputRecord` | `app_rec_1` |
| `reinstatementLedgerEntry` | `led_rr_keep` |
| carried source tag | `committed_state` |
| `generatedByS` | `true` |
| `inScope` | `true` |
| `S.T.suppK(z_app_0,z_app_1)` | `true` |
| in complete audit history | `true` |

The full apparatus-structure equality required by
`MaintenanceReinstatementFor` is registered field by field:

| field | `app_1` | `m_keep.apply(z_app_0)` | equal? |
| --- | --- | --- | --- |
| `time` | `1` | `1` | yes |
| `gateInstrument` | `I_gate` | `I_gate` | yes |
| `thresholdRecords` | `[theta_gate, theta_budget]` | `[theta_gate, theta_budget]` | yes |
| `AppBoundary` | `10` | `10` | yes |
| `auditData` | `101` | `101` | yes |
| `apparatusRecord` | `app_rec_1` | `app_rec_1` | yes |
| `usedLedgerEntries` | `[led_app_1]` | `[led_app_1]` | yes |
| `usedAuditRecords` | `[aud_app_1]` | `[aud_app_1]` | yes |

Therefore:

```text
MaintenanceOperatorOccurrenceFor(S, 0, m_keep) = True.
MaintenanceReinstatementFor(S, H, 0, app_0, app_1, m_keep, rr_keep) = True.
```

The challenged maintained instance uses:

```text
m_repair.operatorRecord = m_repair_record
m_repair.apply(z_app_2_pre) = app_2_post
rr_repair.time = 2
rr_repair.sourceState = z_app_2_pre
rr_repair.targetState = z_app_2_post
rr_repair.operatorRecord = m_repair_record
rr_repair.preAppRecord = app_rec_2_pre
rr_repair.postAppRecord = app_rec_2_post
rr_repair.outputRecord = app_rec_2_post
```

Again the full apparatus-structure equality is registered:

```text
app_2_post = m_repair.apply(z_app_2_pre)
```

with equality in `gateInstrument`, `thresholdRecords`, `AppBoundary`,
`auditData`, `apparatusRecord`, `usedLedgerEntries`, and `usedAuditRecords`.

### Challenge Process And Apparatus Repair

The challenge process distinguishes challenge-free and apparatus-challenged
steps:

```python
C_app_base = ChallengeClass("apparatus_baseline")
C_app_boundary = ChallengeClass("apparatus_boundary_drift")

challenge_process = ChallengeProcess(
    recurrence_period=1,
    default_challenge=C_app_base,
    drift_schedule={2: C_app_boundary},
    binding_states=frozenset({0, 1, 2, 3, 4, 5}),
)
```

Registered challenge readings:

| time | challenge | E3 predicate |
| ---: | --- | --- |
| `0` | `apparatus_baseline` | `ChallengeFreeAt(H,0)` |
| `1` | `apparatus_baseline` | `ChallengeFreeAt(H,1)` |
| `2` | `apparatus_boundary_drift` | `ClosureApparatusChallengeAt(H,C_app_boundary,2)` |
| `3` | `apparatus_boundary_drift` | post-repair observation |
| `4` | `apparatus_boundary_drift` | perturbation measurement |
| `5` | `apparatus_boundary_drift` | perturbation measurement |

The apparatus-level repair episode at time `2` is:

| witness | value |
| --- | --- |
| `rho_t` | `rho_app_2` |
| `R_t` | `R_app_boundary` |
| `defect` | `defect_app_boundary` |
| `move` | `move_app_boundary = S.R_S(defect_app_boundary)` |
| `z` | `z_app_2_pre` |
| `z'` | `z_app_2_post` |
| `auditRecord` | `audit_app_boundary` |
| repair entry membership | `rho_app_2 in H.repairAuditEntries` |
| carried source tag | `committed_state` |
| `generatedByS` | `true` |
| `inScope` | `true` |
| `ESystem.RepairStep` | `true` |
| `CorePromotionGatesPass` | `true` |
| `R_t` target | `AppBoundary` |

Registered apparatus-level repair facts:

```text
EndogenousRepairOccurrenceWithWitnesses(... rho_app_2, R_app_boundary,
  z_app_2_pre, z_app_2_post, defect_app_boundary,
  move_app_boundary, audit_app_boundary) = True.

ApparatusLevelRepairOccurrenceWithWitnesses(... rr_repair,
  rho_app_2, R_app_boundary, z_app_2_pre, z_app_2_post,
  defect_app_boundary, move_app_boundary, audit_app_boundary) = True.

ApparatusLevelRepairOccurrence(S,H,C_app_boundary,2,
  app_2_pre, app_2_post, m_repair, rr_repair) = True.
```

### Apparatus Distance And Tolerances

The apparatus distance used by this toy lab is an exact registered function
over the named apparatus states. It counts weighted component changes and is
not inferred from string equality:

```text
distance(app', app) =
  (1/8) * changed_gateInstrument
  + (1/8) * changed_threshold_bundle
  + (1/8) * changed_AppBoundary
  + (1/8) * changed_auditData
```

Each changed component indicator is `0` or `1`. Therefore the maximum value in
this fixture is `1/2`.

The E3 tolerance is:

```text
epsilon_app = 1/4.
```

Registered distances:

| pair | changed components | distance |
| --- | --- | ---: |
| `app_1` vs `app_0` | audit-data refresh only | `1/8` |
| `app_2_post` vs `app_2_pre` after repair | boundary repair only | `1/8` |
| `app_decay_1` vs `app_decay_0` | threshold + boundary + audit-data drift | `3/8` |
| identical apparatus records | none | `0` |

Object-level F19/F20 content remains certified host input, matching E3's Lean
setup. The toy lab registers the following object tolerance and curve values:

```text
epsilon_obj = 1/4.
```

### E2 Tower Reused For Regress Stop

E3 reuses the exact E2 audit tower fixture from
`formalization/notes/sweeps/E2_bounded_reflexivity_predictions.md` section 1.
The tower auditing `m_keep` has:

```text
cap(z_cap) = 8
level footprints = 2, 3, 3
TowerFootprint(depth 0) = 0
TowerFootprint(depth 1) = 2
TowerFootprint(depth 2) = 5
TowerFootprint(depth 3) = 8
attempted depth 4 footprint = 10
```

E3 does not recompute new tower numbers. It registers that this same tower
appears in `MaintenanceOperatorAuditedByTower(S,H,C_app_boundary,2,horizon,
m_repair,tower_E2,3)`, with lower-stack audit citations to:

```text
m_repair.operatorRecord = m_repair_record
rr_repair
```

## 2. Registered Theorem-Facing Predictions

### Two-Level Fixed Point, Challenge-Free

The challenge-free theorem-facing instance is:

```text
t = 0
horizon = 5
C = C_app_base
app_t = app_0
app_tplus1 = app_1
m = m_keep
record = rr_keep
distance(app_1, app_0) = 1/8 <= epsilon_app = 1/4
```

Registered facts:

| predicate | registered value |
| --- | --- |
| `ObjectLevelFixedPointCertified(S,H,0,5)` | `True` |
| `ObjectRecordCoherenceCertified(S,H,0,5)` | `True` |
| `ClosureApparatusOccurrenceFor(S,0,app_0)` | `True` |
| `ClosureApparatusOccurrenceFor(S,1,app_1)` | `True` |
| `MaintenanceOperatorOccurrenceFor(S,0,m_keep)` | `True` |
| `MaintenanceReinstatementFor(S,H,0,app_0,app_1,m_keep,rr_keep)` | `True` |
| `ChallengeFreeAt(H,0)` | `True` |
| `ApproxApparatusFixedPoint(distance,epsilon_app,app_0,app_1)` | `True` |
| `ApparatusMaintainedStep(...)` | `True` |
| `DeltaMaintEmpty(S,H,0,app_0,app_1)` | `True` |
| in this challenge-free instance, no `SubsidizedReinstatementWitness` exists for any `bad_app_t`/`bad_app_tplus1`/`component` at `t=0` | `True` |
| `m_keep` audited by an E2 tower? | `False`; the tower-conditional in `MaintainedClosureEvidence` holds vacuously |
| `TwoLevelFixedPoint(S,H,C_app_base,distance,epsilon_app,0,5)` | `True` |
| `MaintainedClosureHolds(S,H,C_app_base,distance,epsilon_app,0,5)` | `True` |

The carried status-record witness is explicit:

| field | `msr_maint_free` value |
| --- | --- |
| `time` | `0` |
| `horizon` | `5` |
| `status` | `maintained_closure` |
| `objectFixedPointRecord` | `ofp_0_5` |
| `apparatusRecord` | `app_rec_1` |
| `maintenanceOperatorRecord` | `some m_keep_record` |
| `reinstatementRecord` | `some rr_keep` |
| `apparatusDistanceRecord` | `dist_app0_app1_1_over_8` |
| `supportingLedgerEntries` | `[led_status_maint_free]` |
| `supportingAuditRecords` | `[aud_status_maint_free]` |
| carried source tag | `committed_state` |
| `generatedByS` | `true` |
| `inScope` | `true` |

This carried status record is required. The toy lab must not infer
`MaintainedClosureHolds` from object fixedness and maintenance reinstatement
alone.

### Two-Level Fixed Point, Challenged Maintained

The challenged maintained instance is:

```text
t = 2
horizon = 5
C = C_app_boundary
app_t = app_2_pre
app_tplus1 = app_2_post
m = m_repair
record = rr_repair
```

Registered facts:

| predicate | registered value |
| --- | --- |
| `ObjectLevelFixedPointCertified(S,H,2,5)` | `True` |
| `ObjectRecordCoherenceCertified(S,H,2,5)` | `True` |
| `ClosureApparatusChallengeAt(H,C_app_boundary,2)` | `True` |
| `MaintenanceReinstatementFor(S,H,2,app_2_pre,app_2_post,m_repair,rr_repair)` | `True` |
| `ApparatusLevelRepairOccurrence(S,H,C_app_boundary,2,app_2_pre,app_2_post,m_repair,rr_repair)` | `True` |
| `ApparatusMaintainedStep(...)` | `True` |
| `DeltaMaintEmpty(S,H,2,app_2_pre,app_2_post)` | `True` |
| in this challenged maintained instance, no `SubsidizedReinstatementWitness` exists for any `bad_app_t`/`bad_app_tplus1`/`component` at `t=2` | `True` |
| `m_repair` audited by an E2 tower? | `True`; discharged non-vacuously by the E2 regress-stop bridge registered below |
| `TwoLevelFixedPoint(S,H,C_app_boundary,distance,epsilon_app,2,5)` | `True` |
| `MaintainedClosureHolds(S,H,C_app_boundary,distance,epsilon_app,2,5)` | `True` |

The carried status-record witness is:

| field | `msr_maint_challenged` value |
| --- | --- |
| `time` | `2` |
| `horizon` | `5` |
| `status` | `maintained_closure` |
| `objectFixedPointRecord` | `ofp_2_5` |
| `apparatusRecord` | `app_rec_2_post` |
| `maintenanceOperatorRecord` | `some m_repair_record` |
| `reinstatementRecord` | `some rr_repair` |
| `apparatusDistanceRecord` | `dist_app2pre_app2post_1_over_8` |
| `supportingLedgerEntries` | `[led_status_maint_challenged]` |
| `supportingAuditRecords` | `[aud_status_maint_challenged]` |

This is Case Enumeration case 2: maintenance under challenge through an
E1-style apparatus-level repair occurrence.

### Four-Way Maintenance Status Classification

The status table is over the actual carried status records at a fixed
`(S,H,C,t,horizon)`. It is not a tower-wide or list-wide default.

| row | time | horizon | key facts | carried status record | predicted status |
| --- | ---: | ---: | --- | --- | --- |
| `maintained_free` | `0` | `5` | valid `rr_keep`, `DeltaMaintEmpty`, distance `1/8 <= 1/4` | `msr_maint_free` | `maintained_closure` |
| `maintained_challenged` | `2` | `5` | valid `rr_repair`, E1 apparatus repair, `DeltaMaintEmpty` | `msr_maint_challenged` | `maintained_closure` |
| `crystal_stable` | `0` | `5` | object fixed, no valid or subsidized reinstatement, stable without maintenance | `msr_crystal` | `crystal_grade` |
| `subsidized_fallback` | `2` | `5` | object fixed, `SubsidizedReinstatementWitness` from fallback `rr_fallback` | `msr_subsidized_fallback` | `subsidized_closure` |
| `decaying_no_repair` | `0` | `5` | transient object persistence, no valid/subsidized reinstatement, apparatus distance `3/8 > 1/4` | `msr_decay` | `decaying_closure` |

Registered branch booleans:

| row | `crystal_grade` | `maintained_closure` | `subsidized_closure` | `decaying_closure` |
| --- | --- | --- | --- | --- |
| `maintained_free` | `False` | `True` | `False` | `False` |
| `maintained_challenged` | `False` | `True` | `False` | `False` |
| `crystal_stable` | `True` | `False` | `False` | `False` |
| `subsidized_fallback` | `False` | `False` | `True` | `False` |
| `decaying_no_repair` | `False` | `False` | `False` | `True` |

The `crystal_stable` row uses:

```text
ObjectLevelFixedPointCertified = True
ObjectRecordCoherenceCertified = True
no MaintenanceOperatorOccurrenceFor accounting for app_crystal_0
no MaintenanceReinstatementFor witness
no SubsidizedReinstatementWitness
ApparatusStableWithoutMaintenance = True
ApparatusDecayExceedsTolerance = False
record.reinstatementRecord = none
record.maintenanceOperatorRecord = none
```

The `decaying_no_repair` row uses:

```text
ObjectLevelTransientPersistence = True
NoValidMaintenanceReinstatement = True
ApparatusReinstatedByExternalCarrier = False
ApparatusDecayExceedsTolerance = True
ApparatusStableWithoutMaintenance = False
record.reinstatementRecord = none
record.maintenanceOperatorRecord = none
```

### E2 Regress Stop Bridge

The E3 maintenance operator `m_repair` is audited by the E2 tower from the
E2 pre-registration:

```text
t = 2
horizon = 5
n = 3
targetLevel = 2
TowerFootprint(tower_E2,3) = 8
cap(z_cap) = 8
```

Registered E3 bridge facts:

| predicate or value | registered value |
| --- | --- |
| `MaintenanceOperatorOccurrenceFor(S,2,m_repair)` | `True` |
| `MaintenanceOperatorAuditedByTower(S,H,C_app_boundary,2,5,m_repair,tower_E2,3)` | `True` |
| `CapacityRealizableTower(S,tower_E2,3)` | `True` |
| `CapacityAdmissible(S,measure_E2,tower_E2,3,z_cap)` | `True` |
| `TowerFootprint(S,measure_E2,tower_E2,3)` | `8` |
| `measure_E2.cap(z_cap)` | `8` |
| `TowerFootprint <= cap` | `True` |
| E2 status at `targetLevel = 2` | exactly `saturated` |
| same-level `Sound(I)` claim without shift bridge accepted? | `False` |
| `MaintenanceAuditRegressStoppedByE2(...)` | `True` |

This row cites E2's registered tower numbers directly:

```text
depth footprints = 0, 2, 5, 8
attempted depth 4 footprint = 10
depth 3 saturated under cap 8
claim_circular classified as undefinedCircular, accepted = False
```

The regress-stop prediction is not that the top level certifies itself. It is
that the audit tower is finite-capacity, exactly statused by E2, and blocks
same-level accepted self-soundness.

## 3. Ablation Separation Predictions

### Pass Case: Maintained Closure Separates Under Ablation

The pass case uses the maintained apparatus from section 2 and exposes it to
persistent perturbation over times `0..5`.

Registered predicates:

```text
PersistentPerturbationExposure(S,H,0,5) = True
MaintenanceChannelAblated(S,H,2,5) = True for the ablated run
epsilon_app = 1/4
epsilon_obj = 1/4
```

The maintained run keeps the apparatus within tolerance:

| time | maintained apparatus distance |
| ---: | ---: |
| `0` | `0` |
| `1` | `1/8` |
| `2` | `1/8` |
| `3` | `1/8` |
| `4` | `1/8` |
| `5` | `1/8` |

The ablated run removes `m` starting at time `2`:

| time | ablated apparatus distance | object-level distance |
| ---: | ---: | ---: |
| `0` | `0` | `0` |
| `1` | `1/8` | `1/16` |
| `2` | `3/8` | `1/16` |
| `3` | `1/2` | `1/8` |
| `4` | `5/8` | `3/16` |
| `5` | `3/4` | `5/16` |

Hand checks:

```text
At time 2:
  ablated apparatus distance = 3/8 > 1/4
  object-level distance = 1/16 <= 1/4

At time 3:
  ablated apparatus distance = 1/2 > 1/4
  object-level distance = 1/8 <= 1/4

At time 4:
  ablated apparatus distance = 5/8 > 1/4
  object-level distance = 3/16 <= 1/4
```

Registered prediction:

```text
CurvesSeparate(ApparatusDecayCurve, ObjectDecayCurve) = True.
first_separation_time = 2.
```

This is the ablation falsifier's pass case: cutting the maintenance channel
causes apparatus decay while object-level closure initially persists.

### Fail Control: Crystal-Grade Stability Does Not Separate

The fail control uses the crystal-grade row. It deliberately has no genuine
maintenance operator to cut.

Registered predicates:

```text
PersistentPerturbationExposure(S,H,0,5) = True
MaintenanceChannelAblated(S,H,2,5) = True
CrystalGradeHolds(S,H,C_app_base,distance,epsilon_app,0,5) = True
```

Registered curves:

| time | ablated apparatus distance | object-level distance |
| ---: | ---: | ---: |
| `0` | `0` | `0` |
| `1` | `1/8` | `1/16` |
| `2` | `1/8` | `1/16` |
| `3` | `1/8` | `1/8` |
| `4` | `1/8` | `1/8` |
| `5` | `1/8` | `1/8` |

Post-Round-B correction: the original `1/16` apparatus values at times 1-2
were not derivable from the section 1 apparatus-distance formula, which is
quantized in `1/8` component changes. The crystal-fail control is corrected
to use the same undamped `apparatus_distance` formula as the maintained and
ablated apparatus curves.

All apparatus values are `<= epsilon_app = 1/4`, so:

```text
CurvesSeparate(ApparatusDecayCurve, ObjectDecayCurve) = False.
```

This null prevents the ablation falsifier from being vacuous. Cutting an
absent or irrelevant maintenance channel does not automatically count as
evidence for maintained closure.

## 4. Null And Control Predictions

Each `Delta_maint` control is a one-field variant of the maintained
challenge-free instance unless stated otherwise. The component under test is:

```text
component = theta_budget
```

For each present-record defect, the record otherwise matches `rr_keep`'s
operator, source state, pre-app record, post-app record, output record, and
ledger entry.

`MaintenanceReinstatementFor` and `Delta_maint` deliberately check different
things. The fallback, off-kernel, out-of-scope, and non-carried controls fail
`MaintenanceReinstatementFor` directly. The audit-omission control is
different and more diagnostic: `rr_omitted` satisfies every field checked by
`MaintenanceReinstatementFor`, but it is omitted from the complete audit
history, so `Delta_maint` is nonempty through the separate
`historyMembership` disjunct and `DeltaMaintEmpty` fails.

| control | changed field | `maybeRR` | `Delta_maint` branch | expected `MaintenanceReinstatementFor` | expected status |
| --- | --- | --- | --- | --- | --- |
| `absent_record` | no carried reinstatement record accounts for `theta_budget` | `none` | absent record | `False` | `subsidized_closure` via absent obstruction |
| `fallback_source` | `sourceTag = fallback` | `some rr_fallback` | fallback source tag | `False` | `subsidized_closure` |
| `off_kernel` | `S.T.suppK(sourceState,targetState) = false` | `some rr_off_kernel` | off-kernel transition | `False` | `subsidized_closure` |
| `out_of_scope` | `inScope = false` | `some rr_out_scope` | out-of-scope record | `False` | `subsidized_closure` |
| `non_carried` | `generatedByS = false` | `some rr_non_carried` | non-carried/external generation | `False` | `subsidized_closure` |
| `audit_omission` | record omitted from complete audit history | `some rr_omitted` | omitted audit-history member | `True` | `subsidized_closure` because `DeltaMaintEmpty` fails |

Registered per-control booleans:

| control | `MaintenanceReinstatementFor`? | `Delta_maint` nonempty? | `SubsidizedReinstatementWitness`? | `MaintainedClosureHolds`? | `SubsidizedClosureHolds`? |
| --- | --- | --- | --- | --- | --- |
| `absent_record` | `False` | `True` | `True` with `maybeRR = none` | `False` | `True` |
| `fallback_source` | `False` | `True` | `True` with `maybeRR = some rr_fallback` | `False` | `True` |
| `off_kernel` | `False` | `True` | `True` with `maybeRR = some rr_off_kernel` | `False` | `True` |
| `out_of_scope` | `False` | `True` | `True` with `maybeRR = some rr_out_scope` | `False` | `True` |
| `non_carried` | `False` | `True` | `True` with `maybeRR = some rr_non_carried` | `False` | `True` |
| `audit_omission` | `True` | `True` via `not historyMembership.holds rr_omitted` | `True` with `maybeRR = some rr_omitted` | `False` | `True` |

The absent-record row is deliberately `Option`-shaped: no attempted
`MaintenanceReinstatementRecord` is fabricated for the missing-record case.

### Unlinked Output Evidence Control

The unlinked control uses a carried operator-shaped value and a carried
next-apparatus record, but breaks the full output equality:

```text
rr_unlinked.operatorRecord = m_keep_record
rr_unlinked.preAppRecord = app_rec_0
rr_unlinked.postAppRecord = app_rec_1
rr_unlinked.outputRecord = app_rec_wrong
m_keep.apply(rr_unlinked.sourceState) = app_wrong
app_1 != app_wrong
```

The mismatch is not only a tag mismatch. The concrete fields differ:

| field | `app_1` | `app_wrong` |
| --- | --- | --- |
| `gateInstrument` | `I_gate` | `I_gate_wrong` |
| `thresholdRecords` | `[theta_gate, theta_budget]` | `[theta_wrong]` |
| `AppBoundary` | `10` | `99` |
| `auditData` | `101` | `999` |
| `apparatusRecord` | `app_rec_1` | `app_rec_wrong` |

Registered predictions:

| quantity | predicted value |
| --- | --- |
| carried operator-shaped record exists | `True` |
| carried next apparatus record exists | `True` |
| `app_1 = m_keep.apply(rr_unlinked.sourceState)` | `False` |
| `MaintenanceReinstatementFor(S,H,0,app_0,app_1,m_keep,rr_unlinked)` | `False` |
| `ApparatusMaintainedStep(...)` using `rr_unlinked` | `False` |
| `MaintainedClosureHolds` witnessed by `rr_unlinked` | `False` |

This is Case Enumeration case 9: output evidence must be linked to the same
full apparatus produced by the same operator.

### Maintenance Regress Attempt Control

The regress attempt pairs `m_repair` with the E2 circular claim:

```text
claim_circular =
  { inClaimTypes = true,
    selfDependent = true,
    hasLevelShiftBridge = false }
```

Registered predictions, inherited from the E2 fixture:

| quantity | predicted value |
| --- | --- |
| `SameLevelSelfAuditClassify(claim_circular)` | `undefinedCircular` |
| classifier returns `accepted` | `False` |
| E2 tower depth | `3` |
| E2 status at target level `2` | `saturated` |
| `TowerFootprint <= cap` | `8 <= 8` |
| E3 regress guard accepts final self-certification? | `False` |
| `MaintenanceAuditRegressStoppedByE2` | `True` |

The correct outcome is finite, non-self-certifying audit control, not a final
same-level certificate for `m_repair`.

## 5. Scope Note: Actual Carried Apparatus vs Existential Maintenance

The registered predictions are about the actual carried closure apparatus,
maintenance operator, reinstatement records, audit records, ledger entries,
and maintenance status records exposed by the toy-lab state.

They are not about an existential claim that some apparatus/operator pair
could have maintained the closure. Round B may compute feasibility sanity
checks, but it must not use an existential feasible operator as the status
classifier.

The status rows above must be derived from:

```text
ActualCarriedMaintenance:
  ClosureApparatusOccurrenceFor
  MaintenanceOperatorOccurrenceFor
  MaintenanceReinstatementFor
  Delta_maint / DeltaMaintEmpty
  MaintenanceStatusOccurrenceFor
  carried status records
```

not from:

```text
ExistentialFeasibleMaintenance:
  some operator-shaped function that could have produced an apparatus
  some status tag listed in a registered table
```

This is E3's analogue of E1's generator-reachability guard and E2's
actual-carried-tower versus feasible-tower guard.

## 6. Falsification Conditions

The following outcomes falsify the corresponding registered predictions.

1. The fixture is falsified if the future sweep does not build the actual
   carried `ClosureApparatus`, `ClosureMaintenanceOperator`,
   `MaintenanceReinstatementRecord`, and `MaintenanceStatusRecord` objects
   listed above, or if it uses a different carrier than `X = {a,b,c,d}`
   without an explicit correction to this pre-registration.

2. The full reinstatement-equality guard is falsified if
   `MaintenanceReinstatementFor` accepts `rr_keep` or `rr_repair` without
   checking field-by-field equality between `app_tplus1` and
   `m.apply(record.sourceState)`.

3. The challenge-free two-level fixed-point prediction is falsified if
   `distance(app_1,app_0) != 1/8`, if `1/8 <= 1/4` is not used to derive
   `ApproxApparatusFixedPoint`, or if `MaintainedClosureHolds` is reported
   without the carried `msr_maint_free` status record.

4. The challenged maintained prediction is falsified if the time-2 row is
   classified as maintained without the E1-style apparatus-level repair
   witnesses `rho_app_2`, `R_app_boundary`, `defect_app_boundary`,
   `move_app_boundary`, and `audit_app_boundary`, or if any of those witnesses
   fail the registered carried/gate-passing checks.

5. The status-partition prediction is falsified if any row in the four-way
   status table has zero statuses or more than one status, or if any row's
   computed status differs from the registered table.

6. The E2 regress-stop bridge is falsified if E3 builds a new audit tower
   with different numbers instead of reusing E2's registered footprints
   `0,2,5,8,10`, if the depth-3 bridge does not satisfy `8 <= 8`, or if a
   same-level unshifted `Sound(I)` claim is accepted.

7. The ablation pass case is falsified if the maintained apparatus curve
   exceeds `1/4`, if the ablated apparatus curve does not first exceed `1/4`
   at time `2`, or if the object curve is already above `1/4` at the first
   separation time.

8. The ablation fail control is falsified if the crystal-grade ablated curve
   is reported as separated even though every apparatus and object value in
   that control is `<= 1/4`.

9. The absent-record control is falsified if the missing reinstatement record
   is represented as a fabricated `some rr`, if `Delta_maint` is empty, or if
   the row is classified as `maintained_closure`.

10. The fallback-source control is falsified if `sourceTag = fallback` passes
    as maintained closure instead of producing a nonempty `Delta_maint` and
    `subsidized_closure`.

11. The off-kernel control is falsified if
    `S.T.suppK(sourceState,targetState) = false` is ignored and the row passes
    as maintained closure.

12. The out-of-scope control is falsified if `inScope = false` is ignored and
    the row passes as maintained closure.

13. The non-carried control is falsified if `generatedByS = false` is ignored
    and the row passes as maintained closure.

14. The audit-omission control is falsified if `rr_omitted` fails
    `MaintenanceReinstatementFor` solely because of audit-history omission,
    or if that same omission is not caught by `Delta_maint` and the row is
    treated as `DeltaMaintEmpty`.

15. The unlinked output-evidence control is falsified if
    `MaintenanceReinstatementFor` accepts `rr_unlinked` even though
    `app_1 != m_keep.apply(rr_unlinked.sourceState)` as a full apparatus
    structure.

16. The actual-vs-existential scope discipline is falsified if the future
    sweep classifies a row using an operator or status record that is not
    actually carried in the toy-lab state.

17. The future sweep guard is falsified if Round B hardcodes the four
    statuses, `Delta_maint` pass/fail outcomes, ablation pass/fail outcomes,
    or E2 regress-stop rows from this document instead of computing them from
    carried records, transitions, curve values, and the shared E2 tower
    fixture.

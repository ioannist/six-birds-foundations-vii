# E14 Reconsolidation Law - Toy-Lab Predictions (Round A, pre-registration)

This document pre-registers the toy-lab probe for E14 before any E14 sweep
implementation exists. It is grounded in the accepted six-field normal form
`formalization/notes/examples/E14.md` and the committed Lean module
`lean/SixBirdsFoundationsV/Laws/E14Reconsolidation.lean`.

Round B must mirror the Lean predicates, not a looser prose reading. In
particular, retrieval transport is a complete, context-indexed, pointwise
single-valued inventory; conflict is literal E1 `Delta`; F9 dispositions name
their realizing records directly; coarsening uses D1 `Refines` plus the exact
pair owned by the support audit; and status uniqueness is scoped by the full
`ReconsolidationClaimRef`.

All arithmetic is exact `fractions.Fraction` arithmetic. All other computed
quantities are finite maps, finite sets, or finite lists. Round B must use no
randomness and introduce no floating-point E14 calculation. The imported
Repair-World carrier may retain its existing finite-kernel representation, but
the E14 mirror must consume only its finite support, D4 repair, carried-ledger,
and carried-record interfaces.

Round B must report exactly 21 registered comparisons.

## 1. Toy-Lab Configuration

### Repair-World carrier and carried-source convention

The sweep specializes
`lab/sixbirds_foundations_v/worlds/repair_world.py`, reusing
`RepairWorldState`, `RepairWorldConfig`, `RepairAction`, the D4 repair checker,
and the existing carried ledger. E14 is a single-`ESystem` law. It does not
construct an E13-style inter-carrier bridge.

The finite memory carrier is the same four-item carrier used by the E1 toy lab:

```text
X = {a, b, c, d}
state0.y = 0
```

The current quotient is:

| item | `q_current(item)` |
| --- | --- |
| `a` | `u` |
| `b` | `u` |
| `c` | `v` |
| `d` | `v` |

Every positive carried record uses one of:

```text
sourceTag = committed_state
sourceTag = audited_cell_records
generatedByS = true
inScope = true
```

Negative carriedness controls change exactly the stated field. No outcome may
be credited from a stored `carried = true` shortcut. Round B must evaluate the
same `CarriedRecordAt`/`CarriedSource` conjunction used throughout
`E14Reconsolidation.lean:241-299` and the outcome evidence structures.

### Source claim, source memory, and F20 formation

The main claim and source record are:

```text
claim_episode:
  claimId = 10
  demand(a,b,c,d) = (0,1,0,0)
  readout = identity

m_episode:
  recordId = 100
  version = 4
  claimRecord = claim_episode
  recordValue(a) = {door,left}
  recordValue(b) = {door,right}
  recordValue(c) = {hall}
  recordValue(d) = {key}
  provenanceRootId = 700

formation_episode:
  formationId = 1000
  memoryRecord = m_episode
  formedAt = 0
```

`m_episode`, `claim_episode`, and `formation_episode` are carried, and the
shared F20 comparator accepts `formation_episode`. This realizes
`F20CarriedMemoryRecord` exactly as mechanized at
`E14Reconsolidation.lean:241-267`.

An alternate claim used only by the wrong-claim control is:

```text
claim_other.claimId = 11
claim_other.demand(a,b,c,d) = (0,0,0,0)
claim_other.readout = identity

m_other:
  recordId = 101
  version = 4
  claimRecord = claim_other
  recordValue = m_episode.recordValue pointwise
  provenanceRootId = 701
```

`m_other` and its linked formation record `formation_other (formationId =
1001, formedAt = 0)` are carried and accepted by the same F20 registry.

### Context families and declared retrieval transports

The two context-dependent transport-map templates are:

| item | `T_home(m_episode)` | `T_shift(m_episode)` |
| --- | --- | --- |
| `a` | `episode_ab` | `episode_ab` |
| `b` | `episode_ab` | `episode_ab` |
| `c` | `home_c` | `shift_c` |
| `d` | `home_d` | `home_d` |

Every status scenario owns a dedicated family and two dedicated transports.
The selected and peer contexts in each row are distinct, and no family,
context, transport, or conflict record in this table is reused by another
status scenario:

| scenario tag | family `(id)` | selected context `(id)` | peer context `(id)` | selected transport `(id,map)` | peer transport `(id,map)` | conflict `(id)` |
| --- | --- | --- | --- | --- | --- | --- |
| repair | `family_repair (20)` | `c_repair_focus (101)` | `c_repair_peer (102)` | `t_repair_focus (200,T_home)` | `t_repair_peer (201,T_shift)` | `conflict_repair (700)` |
| coarsen | `family_coarsen (21)` | `c_coarsen_focus (103)` | `c_coarsen_peer (104)` | `t_coarsen_focus (202,T_shift)` | `t_coarsen_peer (203,T_home)` | `conflict_coarsen (701)` |
| unresolved | `family_unresolved (22)` | `c_unresolved_focus (105)` | `c_unresolved_peer (106)` | `t_unresolved_focus (204,T_shift)` | `t_unresolved_peer (205,T_home)` | `conflict_unresolved (702)` |
| collision | `family_collision (23)` | `c_collision_focus (107)` | `c_collision_peer (108)` | `t_collision_focus (206,T_home)` | `t_collision_peer (207,T_shift)` | `conflict_collision (703)` |
| unrealized | `family_unrealized (24)` | `c_unrealized_focus (109)` | `c_unrealized_peer (110)` | `t_unrealized_focus (208,T_home)` | `t_unrealized_peer (209,T_shift)` | `conflict_unrealized (704)` |
| silent | `family_silent (25)` | `c_silent_focus (111)` | `c_silent_peer (112)` | `t_silent_focus (210,T_home)` | `t_silent_peer (211,T_shift)` | `conflict_silent (705)` |
| provenance | `family_provenance (26)` | `c_provenance_focus (113)` | `c_provenance_peer (114)` | `t_provenance_focus (212,T_home)` | `t_provenance_peer (213,T_shift)` | `conflict_provenance (706)` |
| ordinary | `family_ordinary (27)` | `c_ordinary_focus (115)` | `c_ordinary_peer (116)` | `t_ordinary_focus (214,T_read)` | `t_ordinary_peer (215,T_read)` | none |
| unstatused | `family_unstatused (28)` | `c_unstatused_focus (117)` | `c_unstatused_peer (118)` | `t_unstatused_focus (216,T_home)` | `t_unstatused_peer (217,T_shift)` | `conflict_unstatused (707)` |
| scope control | `family_scope (29)` | `c_scope_home (119)` | `c_scope_shift (120)` | `t_scope_home (218,T_home)` | `t_scope_shift (219,T_shift)` | `conflict_scope_home (708)`, `conflict_scope_shift (709)` |

For each row, `family_<tag>.contexts = [selectedContext, peerContext]`, the
list is `Nodup`, and `inventory_<tag>.declaredTransports` is exactly the
selected/peer pair. Every transport names `m_episode`, uses `q_current`, is
carried, and is accepted by `ctx_recon.retrievalDeclared`. Its `retrievedAt`
is fixed by `transportId - 196`, so transport `200` is retrieved at `4`,
transport `201` at `5`, and so on. Every named conflict record has:

```text
sourceRecord = m_episode
transportRecord = the row's selected transport
claimRecord = claim_episode
```

The scope-control row has two conflict records, one for each transport.
Consequently, for every non-ordinary row:

```text
family_<tag>.contexts.Nodup = true
inventory_<tag>.everyContextCovered = true
inventory_<tag>.transportSingleValuedPerContext = true
ContextDependentRetrieval(inventory_<tag>) = true
```

For each conflict-bearing status row, `trigger_<tag>` is the concrete
`ReconsolidationTrigger` with:

```text
trigger_<tag>.inventory = inventory_<tag>
trigger_<tag>.contextDependent = the selected/peer T_home/T_shift witness
trigger_<tag>.conflict = conflict_<tag>
trigger_<tag>.conflictTransportDeclared = true
```

The scope row analogously defines `trigger_scope_home` and
`trigger_scope_shift` from `conflict_scope_home` and
`conflict_scope_shift`. Thus every trigger name used below resolves to one
specific transport and context.

The last fact is witnessed by distinct selected/peer contexts and
`T_home(c) != T_shift(c)`. These checks mirror
`DeclaredRetrievalContextFamily.contextsPairwiseDistinct`
(`E14Reconsolidation.lean:43-47`) and
`CompleteRetrievalTransportInventory.transportSingleValuedPerContext`
(`E14Reconsolidation.lean:301-337`).

`T_read = T_home` pointwise. The ordinary row is duplicate-free and
single-valued, but
`RetrievalWithoutTransportEvidence.contextInvariant = true` and
`ContextDependentRetrieval = false`, matching
`E14Reconsolidation.lean:339-375`.

The no-conflict and wrong-claim controls use otherwise-unused families:

| control | family | contexts | transports |
| --- | --- | --- | --- |
| no conflict | `family_clear (30)` | `c_clear_focus (121)`, `c_clear_peer (122)` | `t_clear_focus (220,T_clear_home)`, `t_clear_peer (221,T_clear_shift)` |
| other claim | `family_other (31)` | `c_other_focus (123)`, `c_other_peer (124)` | `t_other_focus (222,T_home)`, `t_other_peer (223,T_shift)` |

Every status-bearing negative control also has an otherwise-unused full key.
The final row reserves a separate family for the malformed-inventory control:

| control tag | family `(id)` | contexts `(ids)` | transports `(ids)` | conflict `(id)` |
| --- | --- | --- | --- | --- |
| pair mismatch | `family_pair_mismatch (32)` | `c_pair_focus (130)`, `c_pair_peer (131)` | `t_pair_focus (230)`, `t_pair_peer (231)` | `conflict_pair_mismatch (710)` |
| root drift | `family_root_drift (33)` | `c_root_focus (132)`, `c_root_peer (133)` | `t_root_focus (232)`, `t_root_peer (233)` | `conflict_root_drift (711)` |
| non-strict | `family_non_strict (34)` | `c_non_strict_focus (134)`, `c_non_strict_peer (135)` | `t_non_strict_focus (234)`, `t_non_strict_peer (235)` | `conflict_non_strict (712)` |
| wrong direction | `family_wrong_direction (35)` | `c_wrong_focus (136)`, `c_wrong_peer (137)` | `t_wrong_focus (236)`, `t_wrong_peer (237)` | `conflict_wrong_direction (713)` |
| uncarried successor | `family_uncarried (36)` | `c_uncarried_focus (138)`, `c_uncarried_peer (139)` | `t_uncarried_focus (238)`, `t_uncarried_peer (239)` | `conflict_uncarried (714)` |
| ledger label | `family_ledger_label (37)` | `c_ledger_focus (140)`, `c_ledger_peer (141)` | `t_ledger_focus (240)`, `t_ledger_peer (241)` | `conflict_ledger_label (715)` |
| unrelated mutation | `family_unrelated (38)` | `c_unrelated_focus (142)`, `c_unrelated_peer (143)` | `t_unrelated_focus (242)`, `t_unrelated_peer (243)` | `conflict_unrelated (716)` |
| same-context inventory | `family_bad_same_context (39)` | `c_bad_focus (144)`, `c_bad_peer (145)` | `t_bad_focus (224)`, `t_bad_focus_disagree (225)`, `t_bad_peer (226)` | none |

For the first seven rows, the focus transport uses `T_home`, the peer uses
`T_shift`, and the same completeness, carriedness, single-valuedness, and
literal-Delta facts stated for the primary conflict rows hold. The final row
is specified separately in its control section so exactly one completeness
field fails.

### Literal Delta conflict and no-conflict controls

Round B must enumerate unordered pairs directly. For every selected transport
in a conflict row:

```text
DeltaSet(q_current join T_context, claim_episode)
  = {{a,b}}
```

The joined quotient identifies `a,b` because both `q_current` and the selected
transport agree there, while `claim_episode.readout(demand(a)) = 0` and
`claim_episode.readout(demand(b)) = 1`. Each carried conflict record in the
registry points to its row's exact source, transport, and `claim_episode`.
This is the literal `Delta` witness required by
`RetrievalConflictEvidence` at `E14Reconsolidation.lean:377-402`.

For the no-conflict transport control:

| item | `T_clear_home` | `T_clear_shift` |
| --- | --- | --- |
| `a` | `seen_a` | `seen_a` |
| `b` | `seen_b` | `seen_b` |
| `c` | `home_c` | `shift_c` |
| `d` | `home_d` | `home_d` |

Context dependence remains true at `c`, but the join separates `a,b`, so the
computed `DeltaSet` is empty. Under `claim_other`, the computed set is also
empty even for `T_home`, because its readout is constant.

### Shared classifier context

One shared object `ctx_recon` supplies every comparator. No scenario may
install a per-instance predicate.

```text
ctx_recon.f20RecordFormed(formation)
  := formation is carried
     and formation_registry[formation.formationId] = formation.memoryRecord

ctx_recon.retrievalDeclared(transport)
  := declared_transport_registry.count(transport.transportId) = 1
     and declared_transport_registry[transport.transportId] = transport
     and transport.sourceRecord is carried

ctx_recon.repairMoveInstallsJoin(move, package, before, after)
  := move.payload = package
     and for every x, after.recordValue(x)
       = before.recordValue(x) union package.repairValue(x)

ctx_recon.recordUsesQuotient(record, quotient)
  := record_quotient_link[record.recordId, record.version]
       = quotient.quotientId

ctx_recon.coarseningMoveInstallsRecord(move, before, after, q0, q1)
  := move names before/after and the registered quotient transition q0 -> q1

ctx_recon.distinctionNoLongerSupportable(audit, claim)
  := audit.claimId = claim.claimId
     and unordered(audit.mergedLeft, audit.mergedRight)
       is in unsupported_pairs[audit.auditId]

ctx_recon.f9ClassifiesNativeConflict(conflict, disposition)
  := disposition.conflictRecord = conflict
     and f9_registry[conflict.conflictId] = disposition.dispositionId

ctx_recon.ledgerEntryChargesResidual(entry, residual, amount)
  := entry.residualId = residual.residualId
     and entry.amount = amount
     and amount > 0

ctx_recon.provenanceMatchesMutation(provenance)
  := provenance.declaredParent = provenance.mutationRecord.beforeRecord
     and provenance.declaredDerivedRecord =
       provenance.mutationRecord.afterRecord
     and provenance's retrieval/root lineage equals the mutation lineage
```

These are the exact shared fields exposed at
`E14Reconsolidation.lean:155-192`. Each result must be recomputed from the
records shown here. `f20RecordFormed` depends only on its `formation` argument,
and `retrievalDeclared` depends only on its `transport` argument. Family
membership remains the separate `DeclaredRetrievalTransport.contextMember`
check at `E14Reconsolidation.lean:278-280`.

### Lawful repair records

The positive repair package and successor are:

```text
repair_primary.repairId = 300
repair_primary.contextRecord = c_repair_focus
repair_primary.repairValue(a,b,c,d)
  = ({cue_left}, {cue_right}, {}, {})

m_repaired:
  recordId = 100
  version = 5
  claimRecord = claim_episode
  provenanceRootId = 700
  recordValue(x) = m_episode.recordValue(x) union repair_primary.repairValue(x)
```

`mutation_repair` has `mutationId = 400`, names `m_episode` and `m_repaired`,
uses transport `t_repair_focus (200)`, context `c_repair_focus`, and kind
`repair`.
`provenance_repair` names exactly that mutation, parent, and derived record.
All records are carried. Repair-World's D4 checker accepts `zBefore = 0`,
`zAfter = 1`, `defect_memory_repair`, `audit_memory_repair`, and the generated
move whose payload is `repair_primary`. This evidence is indexed by
`trigger_repair`, whose conflict is `conflict_repair`. Thus every field of
`RecordRepairEvidence`
(`E14Reconsolidation.lean:478-536`) is computed true.

### Lawful strict coarsening records

The quotient and support-audit data are:

| item | `q_before(item)` | `q_after(item)` |
| --- | --- | --- |
| `a` | `A` | `AB` |
| `b` | `B` | `AB` |
| `c` | `C` | `C` |
| `d` | `C` | `C` |

```text
Refines(q_before, q_after) = true
q_before(a) != q_before(b)
q_after(a) = q_after(b)

audit_merge_ab:
  auditId = 500
  beforeQuotient = q_before
  afterQuotient = q_after
  claimId = 10
  mergedLeft = a
  mergedRight = b
  unsupported_pairs[500] = {{a,b}}
```

`m_coarsened` retains record id `100`, claim, and root `700`, advances to
version `5`, and is linked to `q_after`. `mutation_coarsen` has id `401`, kind
`coarsening`, transport `t_coarsen_focus (202)`, and context
`c_coarsen_focus`.
`provenance_coarsen` is honest and carried. The D4 move is accepted and
`coarseningMoveInstallsRecord` computes true for `trigger_coarsen`, whose
conflict is `conflict_coarsen`. This realizes
`RecordCoarseningEvidence` at `E14Reconsolidation.lean:538-622`, including the
reviewed audit-owned pair linkage at lines 588-601.

### Dedicated same-trigger collision records

The collision scenario does not borrow either lawful scenario above. Both of
its evidence objects are indexed by the one exact `trigger_collision`, whose
selected retrieval is `t_collision_focus`, context is `c_collision_focus`, and
conflict is `conflict_collision`.

```text
repair_collision:
  repairId = 302
  contextRecord = c_collision_focus
  repairValue(a,b,c,d) = ({collision_left}, {collision_right}, {}, {})

m_collision_repaired:
  recordId = 100
  version = 5
  claimRecord = claim_episode
  provenanceRootId = 700
  recordValue(x) = m_episode.recordValue(x) union repair_collision.repairValue(x)

mutation_collision_repair:
  mutationId = 410
  beforeRecord = m_episode
  afterRecord = m_collision_repaired
  retrievalTransportId = 206
  contextRecord = c_collision_focus
  mutationKind = repair

provenance_collision_repair:
  provenanceId = 510
  mutationRecord = mutation_collision_repair
  declaredParent = m_episode
  declaredDerivedRecord = m_collision_repaired

formation_collision_repaired:
  formationId = 1010
  memoryRecord = m_collision_repaired
  formedAt = 6
```

The package, successor, formation, mutation, provenance, defect, and audit
records are carried; the formation registry accepts
`formation_collision_repaired`. Repair-World accepts the D4 step
`zBefore = 0`, `zAfter = 2`, `defect_collision_repair`, and
`audit_collision_repair`; its generated move payload is `repair_collision`,
and `repairMoveInstallsJoin = true`.

The coarsening side is independently complete:

```text
q_collision_before = q_before pointwise
q_collision_after = q_after pointwise

audit_collision_ab:
  auditId = 502
  beforeQuotient = q_collision_before
  afterQuotient = q_collision_after
  claimId = 10
  mergedLeft = a
  mergedRight = b
  unsupported_pairs[502] = {{a,b}}

m_collision_coarsened:
  recordId = 100
  version = 5
  claimRecord = claim_episode
  provenanceRootId = 700
  recordValue(a) = {door}
  recordValue(b) = {door}
  recordValue(c) = {hall}
  recordValue(d) = {key}
  linked quotient = q_collision_after

mutation_collision_coarsen:
  mutationId = 411
  beforeRecord = m_episode
  afterRecord = m_collision_coarsened
  retrievalTransportId = 206
  contextRecord = c_collision_focus
  mutationKind = coarsening

provenance_collision_coarsen:
  provenanceId = 511
  mutationRecord = mutation_collision_coarsen
  declaredParent = m_episode
  declaredDerivedRecord = m_collision_coarsened

formation_collision_coarsened:
  formationId = 1011
  memoryRecord = m_collision_coarsened
  formedAt = 6
```

The successor, formation, quotient, support-audit, mutation, provenance,
defect, and audit records are carried; the formation registry accepts
`formation_collision_coarsened`; both provenance comparators return true;
`Refines(q_collision_before,
q_collision_after) = true`; `(a,b)` is distinct before and merged after; the
shared support comparator accepts `audit_collision_ab`; and Repair-World
accepts `zBefore = 0`, `zAfter = 3`, `defect_collision_coarsen`, and
`audit_collision_coarsen`. Therefore both `RecordRepairEvidence` and
`RecordCoarseningEvidence` are genuinely constructible for the same
`trigger_collision`, satisfying the first disjunct of
`ReconsolidationOutcomeCollision`.

### Statused-unresolved records and Lambda_S

```text
m_current_at_status = m_episode exactly

residual_unresolved:
  residualId = 600
  conflictRecord = conflict_unresolved
  residualAmount = Fraction(1,3)

led_residual_unresolved:
  residualId = 600
  amount = Fraction(1,3)
```

`trigger_unresolved` owns `conflict_unresolved`, so
`StatusedUnresolvedEvidence.residualLinked` is literal record equality.
`led_residual_unresolved` is a real carried member of
`S.Lambda_S.ledgerEntries`. Identity, claim, version, value, and
`provenanceRootId = 700` are unchanged. The shared comparator accepts the
exact entry/residual/amount triple. This realizes every field of
`StatusedUnresolvedEvidence` at `E14Reconsolidation.lean:624-666`.

The label-only negative record `led_missing_label` stores the same text label
and a disconnected `charged = true` metadata value, but is absent from
`S.Lambda_S`; its amount is `Fraction(1,2)`, not `Fraction(1,3)`. Both real
membership and `ledgerEntryChargesResidual` therefore fail.

### F9 dispositions and complete concrete-outcome inventories

Each positive lawful disposition directly references the full realizing
record:

| disposition | conflict | tag | `supportingMutation` | `supportingResidual` | matching sound outcome inventory |
| --- | --- | --- | --- | --- | --- |
| `disp_repair` | `conflict_repair` | `record_repair` | `mutation_repair` | `none` | repair list `[mutation_repair]` |
| `disp_coarsen` | `conflict_coarsen` | `record_coarsening` | `mutation_coarsen` | `none` | coarsening list `[mutation_coarsen]` |
| `disp_unresolved` | `conflict_unresolved` | `statused_unresolved` | `none` | `residual_unresolved` | residual list `[residual_unresolved]` |

All are carried and accepted by the conflict-scoped F9 registry. The direct
record equality in `DispositionRealizedByInventory`
(`E14Reconsolidation.lean:730-760`) must be used, not numeric ID matching.

The reviewed ID-coincidence control uses:

```text
repair_reference:
  repairId = 303
  contextRecord = c_unrealized_focus
  repairValue(a,b,c,d) = ({ref_left}, {ref_right}, {}, {})

m_reference_realized:
  recordId = 100
  version = 5
  claimRecord = claim_episode
  provenanceRootId = 700
  recordValue(x) = m_episode.recordValue(x) union repair_reference.repairValue(x)

mutation_reference_realized.mutationId = 400
mutation_reference_realized.beforeRecord = m_episode
mutation_reference_realized.afterRecord = m_reference_realized
mutation_reference_realized.retrievalTransportId = 208
mutation_reference_realized.contextRecord = c_unrealized_focus

m_detached:
  recordId = 100
  version = 5
  claimRecord = claim_episode
  provenanceRootId = 700
  recordValue(d) = {key,detached}

mutation_detached.mutationId = 400
mutation_detached.beforeRecord = m_episode
mutation_detached.afterRecord = m_detached
mutation_detached.retrievalTransportId = 209
mutation_detached.contextRecord = c_unrealized_peer
disp_detached.conflictRecord = conflict_unrealized
disp_detached.supportingMutation = some mutation_detached
outcome_inventory_detached.repairMutationRecords = [mutation_reference_realized]
```

`mutation_reference_realized` has a carried, honest `RecordRepairEvidence` for
`trigger_unrealized`: its provenance names the exact parent/derived records,
and Repair-World accepts the generated `repair_reference` move from `0` to
`4`. The outcome inventory is therefore sound. The IDs coincide, but
the full records differ and `mutation_detached` is not in that inventory.
Hence `DispositionRealizedByInventory = false`.

### Provenance defects, silent rewrite, and root-only drift

`m_silent` retains record id and claim but changes
`recordValue(d)` from `{key}` to `{key,false-detail}`. Its complete F9,
outcome, and provenance inventories are empty. The linked provenance audit is
carried and has `beforeRecord = m_episode`, `afterRecord = m_silent`, and
`retrievalTransportId = 210`, exactly matching `trigger_silent`. This realizes
`SilentRewriteEvidence`
(`E14Reconsolidation.lean:833-871`).

`m_laundered` changes `recordValue(d)` in the same way.
`mutation_laundered` is carried with `beforeRecord = m_episode`,
`afterRecord = m_laundered`, `retrievalTransportId = 212`, and
`contextRecord = c_provenance_focus`. Its carried audit record names the same
before/after/transport triple. Meanwhile,
`provenance_laundered` purports to cover it but names root `999` instead of
`700`. Therefore `ctx_recon.provenanceMatchesMutation = false`, realizing
`LaunderedProvenanceDefect` (`E14Reconsolidation.lean:873-920`).

The root-only control is deliberately different:

```text
m_root_drift.recordId = 100
m_root_drift.version = 4
m_root_drift.claimRecord = claim_episode
m_root_drift.recordValue = m_episode.recordValue pointwise
m_root_drift.provenanceRootId = 701

residual_root_drift:
  residualId = 601
  conflictRecord = conflict_root_drift
  residualAmount = Fraction(1,3)

led_residual_root_drift:
  residualId = 601
  amount = Fraction(1,3)
  carried member of S.Lambda_S

disp_root_drift:
  conflictRecord = conflict_root_drift
  disposition = statused_unresolved
  supportingMutation = none
  supportingResidual = some residual_root_drift
```

It fails `StatusedUnresolvedEvidence.provenanceRootPreserved`
(`E14Reconsolidation.lean:638-647`). Because its `recordValue` is unchanged, it
also cannot satisfy the explicit `valueChanged` fields of either
`SilentRewriteEvidence` or `LaunderedProvenanceDefect`. With a carried F9
unresolved disposition directly naming `residual_root_drift`, but no sound
unresolved outcome record, the first constructible branch is therefore
`unrealized_disposition`. This is the committed Lean result; Round B must not
fabricate a value mutation to force a provenance branch.

### Status records and full claim keys

Every positive status record is carried and matches its full claim key:

```text
(sourceRecord, family, transportRecord, contextRecord, claimRecord)
```

`ReconsolidationStatusRecordMatchesClaim` checks every component
(`E14Reconsolidation.lean:1005-1017`), and
`ReconsolidationStatusOccurrenceFor` additionally checks carried occurrence
(`E14Reconsolidation.lean:1019-1032`). Complete status uniqueness is applied
only to that full key.

The nine keys listed in Section 3 are pairwise distinct by their family,
transport, and context records. The two `family_scope` keys are distinct from
one another and from all nine primary keys. Every status-bearing control key
uses its own family from the negative-control registry, so no complete status
record in this pre-registration assigns two statuses to one full key.

### Descriptive budget strata

Budget values are exact metadata for the descriptive probe, not inputs to any
E14 case predicate.

```text
loose stratum, 8 claims:
  exposureBudget = Fraction(3)
  exposureSpend = Fraction(1)
  residualBudget = Fraction(2)
  residualDemand = Fraction(1)

tight stratum, 8 matched claims:
  exposureBudget = Fraction(1)
  exposureSpend = Fraction(1)
  residualBudget = Fraction(1,4)
  residualDemand = Fraction(1)
```

Each indexed claim has its own source/transport/context status key and real
E14 evidence generated from the templates above:

| stratum | indexed outcomes |
| --- | --- |
| loose | `L1-L6 record_repaired`, `L7 record_coarsened`, `L8 statused_unresolved` |
| tight | `T1 record_repaired`, `T2-T7 record_coarsened`, `T8 statused_unresolved` |

The registered aggregate predictions are `6 > 1` for repair in loose versus
tight and `6 > 1` for coarsening in tight versus loose. No per-row classifier
may read the stratum label to choose its status.

## 2. Registered Theorem-Facing Predictions

Round B must report exactly 21 registered comparisons.

| theorem | concrete instantiation | registered prediction |
| --- | --- | --- |
| `E14_ReconsolidationStatus` | every status-bearing registered claim, both row-19 claims, and every stratum episode | exactly one of the nine `...Holds` predicates is true for the same full claim |
| `E14_LawfulConflictTrichotomy` | `claim_record_repaired`, `claim_record_coarsened`, `claim_statused_unresolved` | after the six stated exclusions, exactly one of the three lawful outcomes holds |
| `E14_RecordRepair` | `claim_record_repaired` | `RecordRepairedHolds = true` from the supplied full case |
| `E14_RecordCoarsening` | `claim_record_coarsened` | `RecordCoarsenedHolds = true` from the supplied full case |
| `E14_StatusedUnresolvedChargedToLambda` | `claim_statused_unresolved` | `StatusedUnresolvedHolds = true`, with exact charge to the existing `Lambda_S` entry |
| `E14_SilentRewriteFalsifier` | `claim_silent_rewrite` | all three lawful holds predicates are false for the same complete claim |
| `E14_RetrievalWithoutTransportControl` | `claim_ordinary_read` | `OrdinaryReadHolds = true`; all three lawful holds predicates are false |
| `E14_LaunderedProvenanceDefect` | `claim_provenance_defect` | `ProvenanceDefectHolds = true` |

## 3. Registered Nine-Status Scenarios

### `claim_record_repaired`

| field | predicted value |
| --- | --- |
| claim key | `(m_episode, family_repair, t_repair_focus, c_repair_focus, claim_episode)` |
| trigger | true; context-dependent inventory and `DeltaSet = {{a,b}}` |
| F9 disposition | `disp_repair`, directly referencing `mutation_repair` |
| repair evidence | true, including D4 step, join install, carried successor, and honest provenance |
| higher-priority cases | all false |
| predicted status | `record_repaired` |

### `claim_record_coarsened`

| field | predicted value |
| --- | --- |
| claim key | `(m_episode, family_coarsen, t_coarsen_focus, c_coarsen_focus, claim_episode)` |
| trigger | true; `DeltaSet = {{a,b}}` |
| F9 disposition | `disp_coarsen`, directly referencing `mutation_coarsen` |
| `Refines(q_before,q_after)` | true |
| strict audited pair | `(a,b)` is distinct before, merged after, and owned by `audit_merge_ab` |
| predicted status | `record_coarsened` |

### `claim_statused_unresolved`

| field | predicted value |
| --- | --- |
| claim key | `(m_episode, family_unresolved, t_unresolved_focus, c_unresolved_focus, claim_episode)` |
| trigger/conflict | `trigger_unresolved` / `conflict_unresolved` |
| current record | identity, claim, version, value, and provenance root unchanged |
| residual | carried `residual_unresolved = Fraction(1,3)`, linked to `conflict_unresolved` |
| ledger check | `led_residual_unresolved` carried, present in `S.Lambda_S`, exact comparator true |
| F9 disposition | direct residual reference realized by the sound inventory |
| predicted status | `statused_unresolved` |

### `claim_outcome_collision`

| field | predicted value |
| --- | --- |
| claim key | `(m_episode, family_collision, t_collision_focus, c_collision_focus, claim_episode)` |
| trigger | dedicated `trigger_collision` over `conflict_collision` |
| concrete outcomes | `mutation_collision_repair` and `mutation_collision_coarsen`, each with valid evidence indexed by `trigger_collision` |
| `ReconsolidationOutcomeCollision` | true by its first disjunct (`E14Reconsolidation.lean:780-800`) |
| higher-priority provenance/silent/ordinary cases | false |
| predicted status | `outcome_collision` |

### `claim_unrealized_direct_reference`

| field | predicted value |
| --- | --- |
| claim key | `(m_episode, family_unrealized, t_unrealized_focus, c_unrealized_focus, claim_episode)` |
| trigger | `trigger_unrealized` over `conflict_unrealized` |
| F9 disposition | carried `disp_detached`, tag `record_repair`, direct reference `mutation_detached` |
| comparison mutation | `mutation_reference_realized`, same `mutationId = 400` but a different full record |
| sound repair inventory | `[mutation_reference_realized]`; does not contain `mutation_detached` |
| `DispositionRealizedByInventory` | false despite numeric ID coincidence |
| predicted status | `unrealized_disposition` |

### `claim_silent_rewrite`

| field | predicted value |
| --- | --- |
| claim key | `(m_episode, family_silent, t_silent_focus, c_silent_focus, claim_episode)` |
| trigger/conflict | `trigger_silent` / `conflict_silent` |
| changed record | carried `m_silent`, same record id and claim, changed value at `d` |
| outcome inventory | all three lists empty |
| F9 disposition inventory | empty |
| mutation provenance inventory | empty and complete for this before/after/transport key |
| `SilentRewriteEvidence` | true |
| predicted status | `silent_rewrite`; all lawful outcomes false |

### `claim_provenance_defect`

| field | predicted value |
| --- | --- |
| claim key | `(m_episode, family_provenance, t_provenance_focus, c_provenance_focus, claim_episode)` |
| trigger/conflict | `trigger_provenance` / `conflict_provenance` |
| changed record | carried `m_laundered`, same record id and claim, changed value |
| mutation/provenance/audit records | carried and linked to the selected retrieval |
| purported provenance | names `mutation_laundered` but root/lineage `999` |
| `ctx_recon.provenanceMatchesMutation` | false |
| predicted status | `provenance_defect` (highest priority) |

### `claim_ordinary_read`

| field | predicted value |
| --- | --- |
| claim key | `(m_episode, family_ordinary, t_ordinary_focus, c_ordinary_focus, claim_episode)` |
| inventory | complete `inventory_ordinary` over two distinct contexts |
| transport maps | pointwise equal in both contexts |
| `RetrievalWithoutTransportEvidence` | true |
| reconsolidation trigger | false because context dependence is absent |
| predicted status | `ordinary_read`; all lawful outcomes false |

### `claim_unstatused_conflict`

| field | predicted value |
| --- | --- |
| claim key | `(m_episode, family_unstatused, t_unstatused_focus, c_unstatused_focus, claim_episode)` |
| trigger/conflict | `trigger_unstatused` / `conflict_unstatused` |
| complete F9 disposition inventory | `[]` |
| `NoF9DispositionFor` | true (`E14Reconsolidation.lean:467-476`) |
| higher-priority cases | all false |
| predicted status | `unstatused_conflict` |

## 4. Registered Controls and Case-Enumeration Coverage

### `ctrl_transport_single_valued_same_context`

`inventory_bad_same_context` is scoped to the otherwise-unused
`family_bad_same_context` and contains three
carried, declared records:

```text
inventory_bad_same_context.declaredTransports
  = [t_bad_focus, t_bad_focus_disagree, t_bad_peer]

t_bad_focus.transportId = 224
t_bad_focus.contextRecord = c_bad_focus
t_bad_focus.transportedRecord = T_home
t_bad_focus_disagree.transportId = 225
t_bad_focus_disagree.contextRecord = c_bad_focus
t_bad_focus_disagree.transportedRecord(a) = contradictory_a
t_bad_focus_disagree.transportedRecord(x) = T_home(x) for x in {b,c,d}
t_bad_peer.transportId = 226
t_bad_peer.contextRecord = c_bad_peer
t_bad_peer.transportedRecord = T_shift
```

All three transports name `m_episode`, use `q_current`, are carried, and have
unique registry IDs.
`t_bad_focus` covers `c_bad_focus`, and `t_bad_peer` covers `c_bad_peer`, so
`everyContextCovered = true`. All records pass the sound
declared-transport checks, and the fixture-wide registry contains no other
transport for `family_bad_same_context`, so `completeForClaim = true`.
Registered prediction:
`transportSingleValuedPerContext = false` is the sole failed inventory field,
so
`CompleteRetrievalTransportInventory` is not constructible and no E14 status
may be classified from this malformed inventory.

### `ctrl_coarsening_audited_pair_mismatch`

The proposed quotient transition merges `(a,b)`, but
`audit_merge_cd.mergedLeft = c`, `mergedRight = d`, and its unsupported-pair
registry does not contain `(c,d)`. Registered prediction:
`RecordCoarseningEvidence = false`, `RecordCoarsenedCase = false`; with the
carried F9 coarsening disposition unsupported by a sound outcome inventory,
the claim key
`(m_episode, family_pair_mismatch, t_pair_focus, c_pair_focus,
claim_episode)` has status `unrealized_disposition`.

### `ctrl_unresolved_provenance_root_mismatch`

`m_root_drift` differs from `m_episode` only in `provenanceRootId`. Registered
prediction: `provenanceRootPreserved = false`,
`StatusedUnresolvedEvidence = false`, and `StatusedUnresolvedCase = false`.
`residual_root_drift` is carried and linked to `conflict_root_drift`;
`led_residual_root_drift` is carried, present, and accepted for the exact
amount. Thus provenance-root preservation is the only failed
`StatusedUnresolvedEvidence` field.
Because both provenance branches require a `recordValue` change, the
distinct claim key
`(m_episode, family_root_drift, t_root_focus, c_root_focus, claim_episode)`
has Lean-consistent status `unrealized_disposition`, not `silent_rewrite` or
`provenance_defect`.

### `ctrl_no_conflict_after_transport`

The queried key is `(m_episode, family_clear, t_clear_focus, c_clear_focus,
claim_episode)`. `T_clear_home != T_clear_shift` at `c`, but exhaustive pair
evaluation gives `DeltaSet = {}`. Registered prediction:
`ContextDependentRetrieval = true`,
`RetrievalConflictEvidence = false`, `ReconsolidationTrigger = false`, and no
reconsolidation-outcome status is registered for this episode. This covers Case
Enumeration item 10.

### `ctrl_conflict_for_other_claim`

The queried key is `(m_other, family_other, t_other_focus, c_other_focus,
claim_other)`, and both `t_other_focus` and `t_other_peer` name `m_other`.
The raw `(a,b)` discrepancy exists under `claim_episode`, while the queried
source owns `claim_other`. Registered prediction: `conflictLinked = false` for
the borrowed conflict record and direct `DeltaSet(..., claim_other) = {}`;
there is no trigger or lawful E14 outcome. This covers item 11.

### `ctrl_non_strict_coarsening`

`q_after_same = q_before`, so `Refines = true` but no pair is distinct before
and merged after. Registered prediction: `strictMerge = false`,
`RecordCoarseningEvidence = false`, and a carried unsupported F9 coarsening tag
classifies the distinct key `(m_episode, family_non_strict,
t_non_strict_focus, c_non_strict_focus, claim_episode)` as
`unrealized_disposition`, never `record_coarsened`. This covers item 12.

### `ctrl_wrong_direction_refinement`

`q_before_wrong` merges `a,b`, while `q_after_wrong` separates them. Under D1's
actual direction, `Refines(q_before_wrong,q_after_wrong) = false`. Registered
prediction: no coarsening evidence; the unsupported carried coarsening
disposition classifies `(m_episode, family_wrong_direction, t_wrong_focus,
c_wrong_focus, claim_episode)` as `unrealized_disposition`. This covers item
13.

### `ctrl_uncarried_post_retrieval_record`

The raw successor values match `m_repaired`, but its F20 formation occurrence
uses `generatedByS = false`. Registered prediction:
`F20CarriedMemoryRecord = false`, `RecordRepairEvidence = false`, and the
unsupported direct repair disposition classifies `(m_episode,
family_uncarried, t_uncarried_focus, c_uncarried_focus, claim_episode)` as
`unrealized_disposition`. This covers item 14.

### `ctrl_ledger_charge_label_only`

The residual has a positive exact amount, but `led_missing_label` is absent
from `S.Lambda_S` and the exact amount comparator is false. Registered
prediction: `StatusedUnresolvedEvidence = false`; the F9 unresolved disposition
is unrealized, so `(m_episode, family_ledger_label, t_ledger_focus,
c_ledger_focus, claim_episode)` has status `unrealized_disposition`, never
`statused_unresolved`. This covers item 15.

### `ctrl_per_retrieval_claim_scoping`

The same `m_episode` is classified under two distinct full keys:

```text
(m_episode, family_scope, t_scope_home, c_scope_home, claim_episode)
  -> record_repaired
(m_episode, family_scope, t_scope_shift, c_scope_shift, claim_episode)
  -> statused_unresolved
```

These statuses use dedicated evidence rather than borrowing the primary
repair or unresolved records:

```text
repair_scope_home:
  repairId = 304
  contextRecord = c_scope_home
  repairValue(a,b,c,d) = ({scope_left}, {scope_right}, {}, {})

mutation_scope_home:
  mutationId = 420
  beforeRecord = m_episode
  afterRecord = m_scope_repaired
  retrievalTransportId = 218
  contextRecord = c_scope_home
  mutationKind = repair

m_scope_repaired:
  recordId = 100
  version = 5
  claimRecord = claim_episode
  provenanceRootId = 700
  recordValue(x) = m_episode.recordValue(x) union repair_scope_home.repairValue(x)

disp_scope_home:
  conflictRecord = conflict_scope_home
  disposition = record_repair
  supportingMutation = some mutation_scope_home
  supportingResidual = none

residual_scope_shift:
  residualId = 610
  conflictRecord = conflict_scope_shift
  residualAmount = Fraction(1,3)

led_residual_scope_shift:
  residualId = 610
  amount = Fraction(1,3)
  carried member of S.Lambda_S

disp_scope_shift:
  conflictRecord = conflict_scope_shift
  disposition = statused_unresolved
  supportingMutation = none
  supportingResidual = some residual_scope_shift
```

`mutation_scope_home` has its own carried honest provenance, D4 step, join
install, and sound repair inventory. `residual_scope_shift` has its own sound
residual inventory and exact ledger comparator result. Both therefore realize
their own dispositions under `trigger_scope_home` and `trigger_scope_shift`.

Registered prediction: both claims are independently complete and retain their
different statuses. `CompleteReconsolidationStatus.statusUnique`
(`E14Reconsolidation.lean:1483-1513`) must not be applied source-record-wide.
Both keys are otherwise unused in this document. This covers item 16.

### `ctrl_unrelated_mutation_evidence`

`mutation_other` is a lawful carried repair for another source, transport, and
context. Registered prediction: it cannot enter the current sound outcome
inventory; `record.mutationRecord` and direct disposition support do not match
the current claim `(m_episode, family_unrelated, t_unrelated_focus,
c_unrelated_focus, claim_episode)`. The current carried repair tag remains
`unrealized_disposition`, not `record_repaired`. This covers item 17.

### `strata_budget_memory_fate_direction`

This is one aggregate registered comparison over the 16 deterministic claims
declared in the configuration. It is not a per-fixture status assertion and is
not a theorem consequence.

| measured count | loose stratum | tight stratum | registered direction |
| --- | ---: | ---: | --- |
| `record_repaired` | `6` | `1` | loose `>` tight |
| `record_coarsened` | `1` | `6` | tight `>` loose |
| `statused_unresolved` | `1` | `1` | equal control |

This jointly covers Case Enumeration items 18 and 19. Round B must classify
all 16 claims from concrete E14 evidence before grouping by the exact rational
budget metadata.

## 5. Case Enumeration Coverage Audit

| E14 case item | registered comparison |
| ---: | --- |
| 1 | `claim_record_repaired` |
| 2 | `claim_record_coarsened` |
| 3 | `claim_statused_unresolved` |
| 4 | `claim_outcome_collision` |
| 5 | `claim_unrealized_direct_reference` |
| 6 | `claim_silent_rewrite` |
| 7 | `claim_provenance_defect` |
| 8 | `claim_ordinary_read` |
| 9 | `claim_unstatused_conflict` |
| 10 | `ctrl_no_conflict_after_transport` |
| 11 | `ctrl_conflict_for_other_claim` |
| 12 | `ctrl_non_strict_coarsening` |
| 13 | `ctrl_wrong_direction_refinement` |
| 14 | `ctrl_uncarried_post_retrieval_record` |
| 15 | `ctrl_ledger_charge_label_only` |
| 16 | `ctrl_per_retrieval_claim_scoping` |
| 17 | `ctrl_unrelated_mutation_evidence` |
| 18-19 | `strata_budget_memory_fate_direction` |

The same-context single-valuedness, audited-pair mismatch, and root-preservation
controls are additional review-fix regressions beyond the numbered case table.

## 6. Registered Comparison List

Round B must emit one `PASS`/`FAIL` row for each of these 21 comparisons, in
this order:

| # | registered comparison | expected value | Lean grounding |
| ---: | --- | --- | --- |
| 1 | `claim_record_repaired.status` | `record_repaired` | `RecordRepairedCase` (`E14Reconsolidation.lean:1173-1211`) consumes the linked D4/F20 repair and direct F9 mutation reference. |
| 2 | `claim_record_coarsened.status` | `record_coarsened` | `RecordCoarsenedCase` (`:1213-1252`) consumes strict `RecordCoarseningEvidence` over audit-owned pair `(a,b)`. |
| 3 | `claim_statused_unresolved.status` | `statused_unresolved` | `StatusedUnresolvedCase` (`:1254-1294`) consumes the unchanged record, direct residual reference, and exact `Lambda_S` charge. |
| 4 | `claim_outcome_collision.status` | `outcome_collision` | `OutcomeCollisionCase` (`:1112-1135`) credits two concrete outcomes before all lawful branches. |
| 5 | `claim_unrealized_direct_reference.status` | `unrealized_disposition`; direct full record absent despite ID coincidence | `DispositionRealizedByInventory` (`:730-760`) compares the directly referenced full record against the sound list. |
| 6 | `claim_silent_rewrite.status` | `silent_rewrite`; three lawful holds predicates false | `SilentRewriteCase` (`:1057-1086`) consumes changed value plus complete empty outcome/F9/provenance inventories. |
| 7 | `claim_provenance_defect.status` | `provenance_defect` | `ProvenanceDefectCase` (`:1034-1055`) consumes carried `LaunderedProvenanceDefect` and outranks every other case. |
| 8 | `claim_ordinary_read.status` | `ordinary_read`; three lawful holds predicates false | `OrdinaryReadCase` (`:1088-1110`) consumes pointwise `RetrievalWithoutTransportEvidence`. |
| 9 | `claim_unstatused_conflict.status` | `unstatused_conflict` | `UnstatusedConflictCase` (`:1296-1328`) consumes a genuine trigger and complete empty F9 inventory. |
| 10 | `ctrl_transport_single_valued_same_context` | `transportSingleValuedPerContext = false`; complete inventory rejected | `CompleteRetrievalTransportInventory` (`:301-337`) requires pointwise agreement for two records sharing one context. |
| 11 | `ctrl_coarsening_audited_pair_mismatch.status` | `unrealized_disposition`; `RecordCoarseningEvidence = false` | `strictMerge` and `distinctionUnsupported` (`:588-601`) both consume the pair stored by the same audit record. |
| 12 | `ctrl_unresolved_provenance_root_mismatch.status` | `unrealized_disposition`; `StatusedUnresolvedEvidence = false` | `provenanceRootPreserved` is mandatory at `:643-644`; failed evidence leaves the direct F9 residual unrealized. |
| 13 | `ctrl_no_conflict_after_transport` | context dependence true; `DeltaSet = {}`; no trigger/outcome status | `RetrievalConflictEvidence.deltaConflict` (`:397-402`) requires a concrete pair, so `ReconsolidationTrigger` cannot form. |
| 14 | `ctrl_conflict_for_other_claim` | borrowed conflict link false; own `DeltaSet = {}`; no trigger/outcome status | `conflictLinked` (`:387-390`) fixes the conflict to `sourceRecord.claimRecord`. |
| 15 | `ctrl_non_strict_coarsening.status` | `unrealized_disposition`; strict merge false | `RecordCoarseningEvidence.strictMerge` (`:595-599`) rejects quotient equality without a newly merged pair. |
| 16 | `ctrl_wrong_direction_refinement.status` | `unrealized_disposition`; `Refines before after = false` | `RecordCoarseningEvidence.coarsens` uses D1's literal direction at `:594`. |
| 17 | `ctrl_uncarried_post_retrieval_record.status` | `unrealized_disposition`; F20 carriedness false | `afterRecordCarried` (`:500` or `:555`) requires full `F20CarriedMemoryRecord`, not raw value shape. |
| 18 | `ctrl_ledger_charge_label_only.status` | `unrealized_disposition`; ledger membership and amount comparator false | `StatusedUnresolvedEvidence` requires real ledger membership and comparator truth at `:657-666`. |
| 19 | `ctrl_per_retrieval_claim_scoping` | same source: home claim `record_repaired`, shift claim `statused_unresolved` | Full claim matching (`:1005-1017`) and scoped uniqueness (`:1483-1513`) keep the retrievals independent. |
| 20 | `ctrl_unrelated_mutation_evidence.status` | `unrealized_disposition`; unrelated evidence not in sound scoped inventory | `CompleteReconsolidationOutcomeInventory.soundRepairs` (`:695-700`) requires current-trigger repair evidence for each listed mutation. |
| 21 | `strata_budget_memory_fate_direction` | repair counts loose/tight `6/1`; coarsening counts loose/tight `1/6`; unresolved `1/1` | Each indexed episode first runs the same three lawful cases; only then are statuses grouped by exact budget metadata. |

All nine `ReconsolidationStatus` constructors occur at least once in rows 1-9.

## 7. Falsification Conditions

1. `claim_record_repaired` is falsified if the D4 step, F20 successor
   formation, record-join install, direct F9 mutation reference, mutation
   linkage, or honest provenance is skipped, or if status is not exactly
   `record_repaired`.
2. `claim_record_coarsened` is falsified if D1 `Refines` is reversed, the
   merge is non-strict, the support audit does not own `(a,b)`, the shared
   comparator audits another pair, or status is not `record_coarsened`.
3. `claim_statused_unresolved` is falsified if identity, claim, version,
   value, or provenance root changes; if the exact residual is nonpositive;
   or if the linked carried ledger entry is absent or mismatched.
4. `claim_outcome_collision` is falsified if Round B priority-selects one
   lawful outcome without first detecting two concrete witnesses for the same
   trigger.
5. `claim_unrealized_direct_reference` is falsified if numeric ID coincidence
   is treated as full record equality or if the disposition's own direct
   support reference is ignored.
6. `claim_silent_rewrite` is falsified if a value mutation with complete empty
   outcome, F9, and provenance inventories is accepted as lawful, or if the
   same-claim lawful outcomes are not excluded.
7. `claim_provenance_defect` is falsified if a laundered carried provenance
   record is accepted from its label instead of the shared full-lineage
   comparator, or if the highest-priority status is not `provenance_defect`.
8. `claim_ordinary_read` is falsified if pointwise context-invariant retrieval
   is treated as reconsolidation, or if one of the three lawful outcomes remains
   true under the same complete status.
9. `claim_unstatused_conflict` is falsified if a genuine conflict with a
   complete empty F9 inventory silently receives no status.
10. `ctrl_transport_single_valued_same_context` is falsified if two disagreeing
    transports for one context can construct a complete inventory or if the
    classifier existentially picks the convenient transport.
11. `ctrl_coarsening_audited_pair_mismatch` is falsified if a quotient merge
    on `(a,b)` can borrow a support audit for `(c,d)` or reach
    `record_coarsened`.
12. `ctrl_unresolved_provenance_root_mismatch` is falsified if root preservation
    is omitted, if `statused_unresolved` fires, or if Round B invents a value
    change absent from the registered record to force a provenance branch.
13. `ctrl_no_conflict_after_transport` is falsified if context dependence alone
    is treated as `Delta` conflict or as a reconsolidation outcome.
14. `ctrl_conflict_for_other_claim` is falsified if a conflict under
    `claim_episode` can be credited to a source owning `claim_other`.
15. `ctrl_non_strict_coarsening` is falsified if quotient equality satisfies
    `strictMerge` or reaches `record_coarsened`.
16. `ctrl_wrong_direction_refinement` is falsified if Round B reverses D1
    `Refines` or accepts a finer after quotient as coarsening.
17. `ctrl_uncarried_post_retrieval_record` is falsified if raw value shape can
    bypass the next record's F20/D3 evidence.
18. `ctrl_ledger_charge_label_only` is falsified if a stored label or boolean
    substitutes for real `S.Lambda_S` membership and exact amount linkage.
19. `ctrl_per_retrieval_claim_scoping` is falsified if uniqueness is applied to
    the source record alone or if two transports in one context are permitted.
20. `ctrl_unrelated_mutation_evidence` is falsified if evidence for another
    source, transport, context, or claim can enter the current sound inventory.
21. `strata_budget_memory_fate_direction` is falsified if the classified counts
    are not exactly repair `6/1`, coarsening `1/6`, unresolved `1/1`, or if
    status is selected from budget labels rather than concrete E14 evidence.
22. The future sweep is falsified if any expected status is read from a lookup
    table instead of evaluating carried evidence, literal `Delta`, direct
    disposition references, D1 refinement, exact ledger charge, claim matching,
    and the nine-case priority chain.

## 8. Round B Implementation Guard

Round B must compute every certified boolean or Prop-mirroring fact from the
registered data:

```text
F20CarriedMemoryRecord
DeclaredRetrievalTransport
CompleteRetrievalTransportInventory
ContextDependentRetrieval
RetrievalWithoutTransportEvidence
RetrievalConflictEvidence / Delta
ReconsolidationTrigger
CompleteReconsolidationDispositionInventory
F9ReconsolidationCoverageCertified / NoF9DispositionFor
RecordRepairEvidence
RecordCoarseningEvidence / Refines / strictMerge
StatusedUnresolvedEvidence
CompleteReconsolidationOutcomeInventory
DispositionRealizedByInventory
ReconsolidationOutcomeCollision
CompleteMutationProvenanceInventory
SilentRewriteEvidence
LaunderedProvenanceDefect
ReconsolidationStatusRecordMatchesClaim
ReconsolidationStatusOccurrenceFor
CompleteReconsolidationStatus
```

The classifier must be an explicit priority chain in the committed order:

```text
provenance_defect > silent_rewrite > ordinary_read > outcome_collision >
unrealized_disposition > record_repaired > record_coarsened >
statused_unresolved > unstatused_conflict
```

No comparator may ignore an argument, no record may carry a disconnected
truth flag in place of computation, and no status may be hardcoded from the
registered expected-value table.

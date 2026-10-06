# E16 Adaptability Law - Toy-Lab Predictions (Round A, pre-registration)

This document pre-registers E16 before any sweep implementation. It is grounded
in `formalization/notes/examples/E16.md`, the committed
`lean/SixBirdsFoundationsV/Laws/E16Adaptability.lean`, and `THEOREMS.md`.
Round B must mirror the Lean predicates, not benchmark labels. Expected
statuses may not be stored in fixtures or selected from a lookup table.

All arithmetic uses `fractions.Fraction`; all other data are finite maps,
sets, lists, or records. No float, randomness, or nondeterministic iteration is
permitted in the E16 calculation path.

Round B must report exactly **69 registered comparisons**.

## 1. Toy-Lab Configuration

### Repair-World carrier and deterministic IDs

The sweep specializes one `repair_world.py` `ESystem`, its D4 checker, and its
one carried `Lambda_S`. There is no second carrier. Every positive record has
real `CarriedRecordAt` evidence and a `CarriedSource` with an accepted source
tag, `generatedByS = true`, and `inScope = true`, matching `E16Carried`
(`E16Adaptability.lean:37-43`). A stored `carried` Boolean is forbidden.

Every fixture receives `fixtureIndex = i`:

```text
status fixtures: i = 1..10
theorem/census fixtures: i = 20..23
control for registered row r: i = 1000 + r

idBase(i) = 16000000 + 100000*i
comparisonBaseId = idBase(i)+1
packageId = idBase(i)+2
routePairId = idBase(i)+3
candidateId = idBase(i)+4
familyId = idBase(i)+10
protocolId = idBase(i)+11
bridgeId = idBase(i)+12
residueId = idBase(i)+13
statusRecordId = idBase(i)+14
budgetEntryId = idBase(i)+20
spendEntryId = idBase(i)+21
leftDistributionId = idBase(i)+30
rightDistributionId = idBase(i)+31
probabilityRecordId(side,class) = idBase(i)+100+10*side+class
trialId(side,class,k) = idBase(i)+1000+100*side+10*class+k
trialLedgerEntryId(side,class,k) = idBase(i)+2000+100*side+10*class+k
protocolCounterpartId(k) = idBase(i)+3000+k
completionCounterpartId(k) = idBase(i)+4000+k
refinementCounterpartId(k) = idBase(i)+5000+k
continuationControlId(k) = idBase(i)+6000+k
perturbationBoundId = idBase(i)+7000
perturbationTrialId(k) = idBase(i)+7100+k
```

The v44 regression controls use these previously unused deterministic bands:

```text
row 67 ctrl_flat_unrelated_pair_rejected:
  fixtureIndex=1067; idBase=122700000; allocated band=[122700000,122799999]
  unrelatedFamilyId=idBase+15
  unrelatedProtocolId=idBase+16
  unrelatedLeftDistributionId=idBase+32
  unrelatedRightDistributionId=idBase+33
  unrelatedProbabilityRecordId(side,class)=idBase+100+10*side+class,
    with side=2/3
  unrelatedTrialId(side,class,k)=idBase+1000+100*side+10*class+k,
    with side=2/3
  unrelatedTrialLedgerEntryId(side,class,k)=
    idBase+2000+100*side+10*class+k, with side=2/3
row 68 ctrl_perturbation_off_universe_rejected:
  fixtureIndex=1068; idBase=122800000; allocated band=[122800000,122899999]
  offUniversePerturbationTrialId=idBase+7190
row 69 ctrl_swapped_trial_populations_rejected:
  fixtureIndex=1069; idBase=122900000; allocated band=[122900000,122999999]
  uses the canonical left/right distribution, probability, trial, and ledger
    formulas above; only the two complete trial populations are exchanged
```

`side=0` is gamma/loop, `side=1` is eta/identity, classes `0/1` are
`C_repair/C_shift`, and `k=0..3`. Bands are disjoint. Full records establish
semantic linkage; IDs only key inventories. The canonical full claim is
`(candidateId, package, routePair, protocol, economy, move, binding budget,
C_repair, observedAt=Fraction(10))`.

### Native finite `RouteTransportCore`

Round B constructs this core natively, using `HolonomyMemory.Wheel` only as an
independent cross-check:

```text
Interface = {i0}
History(i0) = {FF,FT,TF,TT} = Bool x Bool
Event(i0) = {present}; Observation = Bool
Continuation(i0,i0) = all total four-entry WheelMaps (exactly 4^4=256)
push(h,f)=f(h); observe((visible,latent),present)=visible
id = [FF->FF, FT->FT, TF->TF, TT->TT]
compose(f,g)(h)=g(f(h))
ell0 = [FF->FT, FT->FF, TF->TT, TT->TF]
reveal = [FF->FF, FT->TT, TF->FF, TT->TT]
erase_latent = [FF->FF, FT->FF, TF->TF, TT->TF]
```

Identity/composition laws are exhaustively checked. The flagship route pair
starts at `FF`, with gamma=`ell0` and eta=`id`, so endpoints are `FT` and `FF`.
They are current equivalent, but `reveal` yields `TT` versus `FF`; hence they
occupy one current class and two endpoint predictive classes.
`CurrentLoopTrivial(ell0)` holds representative-by-representative for all four
histories, while `PredictiveLoopNontrivial(ell0)` is witnessed by `[FF]`.

A separate `flat_native` core has histories `{F,T}`, one event, Boolean
observation, and only identity continuation. Its current and predictive
relations coincide and `FlatAt=true`. The all-future flat fixture uses
identity versus identity from `F`. The second flat fixture uses the wheel pair
but equal held-out repair distributions.

The reveal-removal mutation constructs a separate lawful `no_reveal_core` whose
continuation carrier is exactly `{id,ell0}`. This two-map carrier is closed
under composition, and both maps preserve the visible bit. `FT` and `FF` are
therefore future equivalent in that core and no `PredictiveWitness` can be
constructed. Merely deleting `reveal` from an E16 admissibility registry would
not affect vendored `FuturePredictiveEquiv`, which quantifies over the core's
actual continuation type, and is explicitly forbidden as an invalid control.

### Exact repair distributions and binding budget

The carried held-out family is `[C_repair,C_shift]`, `Nodup`, declared at
`Fraction(0)`. Its shared protocol is measured at `Fraction(10)`. The exact
budget has `spend=budget=Fraction(6)`, distinct carried budget/spend entries,
`BudgetFeasible=true`, `BindingExposureBudget=true`, and
`protocolUsesBindingBudget=true`.

Each route/class has exactly four eligible, carried, D4-lawful trials. Success
is derived only from the concrete repair and ledger effect: the discharge entry
is absent before, present after, and accepted by
`trialLedgerEffectRecordsDischarge`.

| side | `C_repair` successes/probability | `C_shift` successes/probability |
| --- | --- | --- |
| gamma | `{0,1,2}` / `Fraction(3,4)` | `{0,1}` / `Fraction(1,2)` |
| eta | `{0}` / `Fraction(1,4)` | `{0,1}` / `Fraction(1,2)` |

Probability support lists contain exactly successful trials' physical ledger
entries. Every distribution, probability, trial, and support entry is carried;
support entries are in `Lambda_S` and relevant. Ratios are recomputed from the
complete eligible denominator (`E16Adaptability.lean:163-205,257-455`). Thus
the canonical declared difference on `C_repair` is exactly `3/4` versus `1/4`.

### Actual E15 bridge

Fixture `i` uses the actual E15 record:

```text
RouteResidueDebtRecord(
 residueId=idBase(i)+13,
 routeResidue=(package,routePair,C_repair,3/4,1/4),
 reconciliationClaimId=candidateId,
 recordedAt=Fraction(4), residualAmount=Fraction(1,2))
```

The carried bridge names that full record and the exact package, pair, and
capacity difference; `reconciledAt=9`, `observedAt=10`, bridge acceptance is
true, and E15's literal `f3RouteResidueAwaitingReconciliation(record,10)` is
false (`E16Adaptability.lean:990-1024`). The disconnected control preserves the
numeric residue ID but changes the payload to an eta-only trace and amount to
`1/4`; full-record equality must fail.

### Complete control inventories

The context declares finite eligible universes before classification:

```text
one same-base honest protocol counterpart
one same-base completion
one same-base refinement
continuations reveal and, only where declared, erase_latent
carried perturbation bound Fraction(1,2), declaredAt Fraction(5)
trials at magnitudes [0,1/4,1/2]
```

Every inventory checks coverage, soundness, record and ID `Nodup`, carriedness,
and single-valuedness (`E16Adaptability.lean:786-943`). In the coherent base:
the honest protocol retains the split; completion has witness/discrepancy
`(1,1/2)`; refinement has `(1,1/2,2)`; reveal retains a complete `3/4` versus
`1/4` endpoint difference; and all in-bound perturbations preserve.

Dissipation uses the genuine inventory-member `erase_latent`, mapping both
endpoints to `FF` with no later difference. Perturbation brittleness instead
has no dissipating continuation and changes only preservation at magnitude
`1/4` to false.

### Status fixture families

| fixture (`i`) | positive raw evidence | expected status |
| --- | --- | --- |
| `claim_coherent_wheel` (1) | candidate plus all four freedoms | `coherent_adaptability` |
| `claim_support_confound` (2) | carried eligible changed-base counterpart | `support_confound` |
| `claim_artifact_trap` (3) | same-base honest protocol clears | `artifact` |
| `claim_flat_future` (4) | gated `flat_native` future equivalence | `flat` |
| `claim_flat_equal_capacity` (5) | gated wheel pair, all declared probabilities equal | `flat` |
| `claim_flattenable` (6) | same-base completion clears to zero | `flattenable` |
| `claim_currentizable` (7) | same-base refinement gives `(0,0,1)` | `currentizable_slack` |
| `claim_dissipative` (8) | inventory-member continuation clears | `dissipative` |
| `claim_rejected_perturbation` (9) | in-bound failure, no dissipating continuation | `adaptability_rejected` |
| `claim_rejected_unbound_flat` (10) | verified unbound-budget administrative arm | `adaptability_rejected` |

The exact priority is `support_confound > artifact > flat > flattenable >
currentizable_slack > dissipative > coherent_adaptability >
adaptability_rejected`, using record-independent evidence predicates
(`E16Adaptability.lean:1590-1872`).

## 2. Registered Theorem-Facing Predictions

1. The fixtures reach all eight statuses and both positive rejection arms.
2. The wheel fixture exercises current-audit blindness: `FT` and `FF` remain in
   one current class while `reveal` separates their predictive classes.
3. Route manufacture returns carried records with exact probabilities `3/4`
   and `1/4` on the same `C_repair`.
4. The loop anchor has moved predictive action and fixed current image.
5. Artifact, flat, flattenable, currentizable, and dissipative evidence each
   exclude coherent Holds; currentizable positively remains legible slack.
6. Raw support-confound evidence excludes all seven lower Holds predicates.

## 3. Registered Eight-Status Scenarios

Rows 1-10 classify the status fixtures independently. The paper's six regimes
map to `claim_flat_future`, `claim_artifact_trap`, `claim_flattenable`,
`claim_currentizable`, `claim_dissipative`, and `claim_coherent_wheel`.
`support_confound` is an E16 guard, not a seventh paper regime;
`adaptability_rejected` is E16 administrative evidence, not a paper regime.
The wheel is an operational coherent-candidate instance, not an ontological or
universal existence claim.

## 4. Registered Controls and Mutation Fixtures

### Independent controls and robustness

- `ctrl_support_only`: every other check passes; only an eligible
  counterpart's declared base differs.
- `ctrl_flattening_only`: support is fixed and only a `(0,0)` completion clears.
- `ctrl_currentization_only`: completion does not clear; only a same-base
  `(witnesses,discrepancy,maxFiber)=(0,0,1)` refinement currentizes.
- `ctrl_dissipation_only`: only inventory-member `erase_latent` clears; all
  perturbations preserve.
- `ctrl_perturbation_only`: all continuations preserve, but one in-bound
  perturbation fails. It is rejected, never dissipative.

### Bridge, scope, and inventory controls

`ctrl_e15_still_outstanding` changes only E15's literal outstanding result at
time 10. `ctrl_e15_reconciled` is the positive bridge.
`ctrl_e15_disconnected_same_id` uses the changed full residue with the same
ID. `ctrl_undeclared_proxy` keeps declared support equal but adds an
analyst-only hidden variable that appears in no registered record and no
mechanical computation path. The declared-data classifier therefore does not
diagnose a support confound and returns `coherent_adaptability`. Withholding
positive certification is a documented governance limitation/nonclaim from
E16.md item 4 and Section 6, not a scored Round B output.

Wrong route, class, protocol, and time evidence remain valid for another full
claim but cannot outrank this claim. Missing eligible records fail coverage;
included ineligible records fail soundness; duplicates fail `Nodup` or
single-valuedness. An off-inventory continuation cannot dissipate, a nonzero
completion cannot flatten, and an out-of-bound perturbation is ineligible.

### Comparator mutation battery

Rows 26, 28, 36-38, and 57-64 independently mutate the route-admissibility,
ledger-computation, ledger-relevance, budget-linkage, counterpart-
admissibility, honest-protocol clearing, completion clearing, refinement
currentization, continuation dissipation, perturbation survival, E15 bridge
acceptance, and E15 outstanding-status comparators. One shared context computes
them from registries, route maps, trial/ledger data, or full bridge records. It
contains no status selector.

Row 57 contains four deterministic subvariants, in this order: protocol,
completion, refinement, continuation. Each starts from its own valid complete
inventory, changes only that counterpart's admissibility result to false, and
must flip that inventory's `everyRecordEligible` result from true to false.
Row 65 similarly checks package, base, pair, challenge family, protocol,
distribution, probability, trial, each counterpart kind, bridge, and status
records; for each family it mutates source tag, `generatedByS`, and `inScope`
independently in that order.

### v44 full-record and claim-pair regressions

- `ctrl_flat_unrelated_pair_rejected` uses the native wheel claim with its
  claim-linked `C_repair` probabilities fixed at `Fraction(3,4)` and
  `Fraction(1,4)`, so the future-equivalence flat arm is false and the linked
  pair is unequal. A second, fully complete distribution pair over the same
  typed route pair uses the row-67 auxiliary protocol and has equal
  probabilities on both declared classes, so it independently inhabits
  `NoDeclaredRepairCapacityDifference`. Its protocol differs from the claim's
  protocol, however, so it does not satisfy `DistributionsMatchClaim`; the
  claim-matched pair satisfies that linkage but is unequal and therefore does
  not inhabit `NoDeclaredRepairCapacityDifference`. No one pair satisfies both
  flat-arm conjuncts, so `FlatEvidenceFor` is false
  (`E16Adaptability.lean:538-560,1370-1425,1609-1612`).
- `ctrl_perturbation_off_universe_rejected` creates the carried row-68 trial
  at time `Fraction(10)` with the canonical candidate/package/base and
  magnitude `Fraction(1,4) <= Fraction(1,2)`, but excludes that full record
  from the shared `perturbationTrialEligible` universe. The canonical universe
  remains completely covered. If the off-universe record is added to
  `records`, `everyRecordEligible` fails solely at the shared comparator
  (`E16Adaptability.lean:771-776,912-958`).
- `ctrl_swapped_trial_populations_rejected` exchanges the complete left and
  right trial lists while leaving route endpoints and probability records
  unchanged. Every record remains carried and all IDs remain deterministic,
  but the shared `trialEligibleForRouteEndpoint` predicate specialized at each
  distribution rejects the opposite endpoint's trials; hence
  `everyTrialEligible=false` and the distribution is incomplete
  (`E16Adaptability.lean:163-205,369-470`).

## 5. Case Enumeration Coverage Audit

| E16 item | coverage |
| ---: | --- |
| 1 | rows 1, 15-19 |
| 2 | rows 1, 11-13 and native-wheel disclaimer |
| 3 | rows 2, 15 |
| 4 | row 23, demonstrated limitation plus documented nonclaim |
| 5 | rows 3, 58 |
| 6 | row 4 |
| 7 | rows 5, 67 |
| 8 | rows 6, 16 |
| 9 | row 47 |
| 10 | rows 7, 17 |
| 11 | row 48 |
| 12 | rows 6, 7, 14 |
| 13 | rows 8, 18, 61 |
| 14 | row 46 |
| 15 | rows 9, 19, 62 |
| 16 | rows 49, 68 |
| 17 | row 29 |
| 18 | row 30 |
| 19 | rows 31-33 |
| 20 | rows 34, 65 |
| 21 | rows 24, 69 |
| 22 | row 25 |
| 23 | rows 10, 26-28 |
| 24 | rows 20, 64 |
| 25 | rows 21, 63 |
| 26 | row 22 |
| 27 | row 40 |
| 28 | rows 41-44 |
| 29 | row 45 |
| 30 | row 11 |
| 31 | row 12 |
| 32 | rows 50-53 |
| 33 | rows 54-55 |
| 34 | row 56 |
| 35 | rows 26, 28, 36-38, 57-64 |
| 36 | row 14 and rows 1, 3, 4, 6-8 |

All 36 items are covered. Item 4 remains the accepted governance limitation,
not an invented mechanical status.

## 6. Registered Comparison List

| # | comparison | exact expected value |
| ---: | --- | --- |
| 1 | `claim_coherent_wheel.status` | `coherent_adaptability` |
| 2 | `claim_support_confound.status` | `support_confound` |
| 3 | `claim_artifact_trap.status` | `artifact` |
| 4 | `claim_flat_future.status` | `flat` |
| 5 | `claim_flat_equal_capacity.status` | `flat` |
| 6 | `claim_flattenable.status` | `flattenable` |
| 7 | `claim_currentizable.status` | `currentizable_slack` |
| 8 | `claim_dissipative.status` | `dissipative` |
| 9 | `claim_rejected_perturbation.status` | `adaptability_rejected` |
| 10 | `claim_rejected_unbound_flat.status` | `adaptability_rejected` |
| 11 | `claim_coherent_wheel.current_audit` | `CurrentEventEquiv=true; current_class(FT)=current_class(FF)` |
| 12 | `claim_coherent_wheel.route_capacity` | `C_repair: gamma=3/4; eta=1/4; unequal=true` |
| 13 | `claim_coherent_wheel.loop_anchor` | `CurrentLoopTrivial=true; PredictiveLoopNontrivial=true; current_image_fixed=true` |
| 14 | `six_regime_census` | `flat=1; artifact=1; flattenable=1; explicit_latent=1; dissipative=1; coherent_candidate=1` |
| 15 | `ctrl_support_only` | `supportFreedom=false; other_freedoms=true; support_confound` |
| 16 | `ctrl_flattening_only` | `flatteningFreedom=false; other_freedoms=true; flattenable` |
| 17 | `ctrl_currentization_only` | `currentizationFreedom=false; completionClears=false; currentizable_slack` |
| 18 | `ctrl_dissipation_only` | `dissipationFreedom=false; perturbations_preserve=true; dissipative` |
| 19 | `ctrl_perturbation_only` | `bounded_failure=true; continuation_dissipation=false; adaptability_rejected` |
| 20 | `ctrl_e15_still_outstanding` | `residue_eligible=false; candidate=false` |
| 21 | `ctrl_e15_reconciled` | `residue_eligible=true; proceeds_to_controls=true` |
| 22 | `ctrl_e15_disconnected_same_id` | `numeric_id_equal=true; full_record_equal=false; bridge_eligible=false` |
| 23 | `ctrl_undeclared_proxy` | `declared_base_equal=true; SupportConfoundEvidenceFor=false; mechanical_status=coherent_adaptability` |
| 24 | `ctrl_wrong_route_endpoint` | `endpoint_linkage=false; capacity_difference=false` |
| 25 | `ctrl_different_protocols` | `sameProtocol=false; distribution_pair=false` |
| 26 | `ctrl_route_inadmissible` | `routePairAdmissible=false; candidate=false; administrative_rejection=true` |
| 27 | `ctrl_package_undeclared` | `routePackageDeclared=false; candidate=false; administrative_rejection=true` |
| 28 | `ctrl_budget_linkage` | `binding=true; protocolUsesBindingBudget=false; flat=false; rejected=true` |
| 29 | `ctrl_undeclared_challenge_difference` | `C_hidden_not_declared=true; capacity_difference=false` |
| 30 | `ctrl_missing_declared_class` | `everyClassCovered=false; complete_distribution=false` |
| 31 | `ctrl_duplicate_probability_record` | `recordsNodup=false; complete_distribution=false` |
| 32 | `ctrl_duplicate_probability_id` | `recordIdsNodup=false; complete_distribution=false` |
| 33 | `ctrl_contradictory_same_class` | `singleValuedPerClass=false; complete_distribution=false` |
| 34 | `ctrl_uncarried_ledger_support` | `everyLedgerEntryCarried=false; capacity_difference=false` |
| 35 | `ctrl_uncarried_distribution` | `distributionCarried=false; complete_distribution=false` |
| 36 | `ctrl_probability_ledger_computation` | `stored=3/4; computed=1/2; everyProbabilityComputed=false` |
| 37 | `ctrl_ledger_relevance` | `supportingLedgerEntryRelevant=false; capacity_difference=false` |
| 38 | `ctrl_exact_denominator` | `successful=3; eligible=4; stored=2/3; everyProbabilityComputed=false; exact_ratio=false` |
| 39 | `ctrl_trial_inventory_omission` | `eligible_trial_missing=true; everyEligibleTrialCovered=false` |
| 40 | `ctrl_protocol_inventory_omission` | `eligible_counterpart_missing=true; supportFreedom=false` |
| 41 | `ctrl_completion_inventory_omission` | `eligible_completion_missing=true; flatteningFreedom=false` |
| 42 | `ctrl_refinement_inventory_omission` | `eligible_refinement_missing=true; currentizationFreedom=false` |
| 43 | `ctrl_continuation_inventory_omission` | `eligible_continuation_missing=true; dissipationFreedom=false` |
| 44 | `ctrl_perturbation_inventory_omission` | `eligible_trial_missing=true; dissipationFreedom=false` |
| 45 | `ctrl_duplicate_counterpart_key` | `recordIdsNodup=false; singleValuedPerDeclaredKey=false` |
| 46 | `ctrl_unregistered_dissipating_continuation` | `off_inventory=true; DissipativeEvidenceFor=false` |
| 47 | `ctrl_completion_label_without_collapse` | `witnessCount=1; discrepancy=1/2; clears=false` |
| 48 | `ctrl_changed_support_refinement` | `refinement_base_equal=false; changed_base_refinement_cannot_currentize=true; CurrentizableEvidenceFor=false; SupportConfoundEvidenceFor=false` |
| 49 | `ctrl_out_of_bound_perturbation` | `magnitude=3/4; bound=1/2; eligible=false; coherence_unchanged=true` |
| 50 | `ctrl_wrong_claim_route` | `valid_other_claim=true; evidence_for_current=false` |
| 51 | `ctrl_wrong_claim_challenge` | `valid_other_claim=true; evidence_for_current=false` |
| 52 | `ctrl_wrong_claim_protocol` | `valid_other_claim=true; evidence_for_current=false` |
| 53 | `ctrl_wrong_claim_time` | `other_time=11; current_time=10; evidence_for_current=false` |
| 54 | `ctrl_priority_artifact_flattening_collision` | `artifactEvidence=true; flattenableEvidence=true; status=artifact` |
| 55 | `ctrl_lower_tag_with_raw_artifact` | `record_tag=flattenable; ArtifactEvidenceFor=true; FlattenableCase=false` |
| 56 | `ctrl_status_uniqueness` | `same_claim=true; tags=(artifact,flattenable); complete_status=false` |
| 57 | `mut_counterpart_admissibility` | `protocol/completion/refinement/continuation: each admissible true->false and inventory_sound true->false` |
| 58 | `mut_honest_protocol_clears` | `false->true; ArtifactEvidenceFor=false->true` |
| 59 | `mut_completion_clears` | `false->true; FlattenableEvidenceFor=false->true` |
| 60 | `mut_refinement_currentizes` | `false->true; CurrentizableEvidenceFor=false->true` |
| 61 | `mut_continuation_dissipates` | `false->true; DissipativeEvidenceFor=false->true` |
| 62 | `mut_perturbation_survival` | `true->false at 1/4; coherent=false; rejected=true` |
| 63 | `mut_e15_bridge_acceptance` | `true->false; residue_eligible=true->false` |
| 64 | `mut_e15_outstanding_status` | `false->true at time 10; residue_eligible=true->false` |
| 65 | `mut_carriedness_fields` | `sourceTag/generatedByS/inScope flips each make E16Carried=false` |
| 66 | `mut_predictive_reveal` | `no_reveal_core Continuation={id,ell0}; FuturePredictiveEquiv=true; witness=false; candidate=false` |
| 67 | `ctrl_flat_unrelated_pair_rejected` | `claim_pair_unequal=true; claim_pair_no_difference=false; unrelated_pair_complete=true; unrelated_pair_equal=true; unrelated_pair_matches_claim=false; FlatEvidenceFor=false` |
| 68 | `ctrl_perturbation_off_universe_rejected` | `old_conditions_met=true; perturbationTrialEligible=false; coverage_unaffected=true; record_inclusion_fails_soundness=true` |
| 69 | `ctrl_swapped_trial_populations_rejected` | `everyTrialEligible=false; complete_distribution=false` |

Round B emits one `PASS`/`FAIL` row for every comparison in exactly this order.

## 7. Falsification Conditions

The pre-registration is falsified if any expected value differs; the output
count/order is not exactly 69; any expected status is unreachable; current or
future equivalence is inferred from labels rather than finite observation
tables; the wheel lacks a revealing continuation or representative-level loop
asymmetry; a probability bypasses exact complete-trial counting; an inventory
defect is ignored; an ID-only E15 bridge is accepted; a substantive or flat
branch bypasses the admissibility/budget gate; perturbation failure is called
dissipation without a continuation; the flat arm combines
`DistributionsMatchClaim` from the claim pair with
`NoDeclaredRepairCapacityDifference` from a different equal pair rather than
requiring both conjuncts of one existential witness; perturbation completeness
ranges
over all well-typed records instead of the declared eligible universe; trial
eligibility is stored per distribution or keyed only by ID rather than fixed by
the shared route-endpoint comparator; priority uses status-tag mismatch; or any
fixture/classifier contains expected status data, floats, randomness, or an
oracle call to `HolonomyMemory.Wheel` or `_holonomy_support`.

The positive wheel result remains one operational coherent-candidate fixture,
not a universal existence claim.

## 8. Round B Implementation Guard

Round B follows the E14/E15 architecture: deterministic `Fixture`,
`build_fixture()`, per-claim raw-evidence computation and priority dispatch,
`SweepResults`, markdown formatting, and discipline checks.

It must compute, never store:

- push/composition laws, current/future equivalence tables, current/predictive
  quotient classes, `FlatAt`, predictive loop action, and representative-level
  `CurrentLoopTrivial`;
- D4 trial success, exact eligible/successful counts and rational ratios,
  carried/relevant ledger support, and complete distributions;
- package/route admissibility and the binding budget;
- complete/sound/Nodup/single-valued control inventories, including the
  classifier-declared full-record perturbation universe and the shared
  route-endpoint-conditioned trial universe;
- every clearing/currentization/dissipation/perturbation comparator;
- the actual E15 full-record bridge and literal outstanding predicate;
- all eight record-independent evidence truths and the exact priority chain.

Every classified row must satisfy `AdaptabilityStatusOccurrenceFor`, have one
complete same-claim status, and have exactly one true Holds result. A control
that fails before classification reports its evidence predicate false; it may
not fabricate rejection unless a positive administrative or bounded-
perturbation rejection arm exists. Expected values belong only in tests and
this Round A document.

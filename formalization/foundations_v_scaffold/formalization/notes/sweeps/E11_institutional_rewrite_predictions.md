# E11 Institutional Rewrite Predictions

This is the pre-registered prediction artifact for the E11 toy-laboratory
probe. It is intentionally written before any E11 sweep implementation exists.
Round B should implement the sweep against this document, not redesign the
configuration after seeing results.

No experiment has been run for this artifact. All quantities below are exact
and should be represented with `fractions.Fraction` where arithmetic is
needed. This E11 Round A instance is fully deterministic: no random seed,
stochastic simulation, or hash-audited float branch is required.

## 1. Toy-Lab Configuration

### Repeated-Game Carrier

The sweep specializes the Repair-World carrier shape in
`lab/sixbirds_foundations_v/worlds/repair_world.py`, but uses a repeated-game
interpretation of the same four-state fixture family:

```text
X = {a,b,c,d}.
```

The states are:

| state | repeated-game reading |
| --- | --- |
| `a` | idle / entry |
| `b` | mutual cooperation |
| `c` | unilateral defection |
| `d` | sanction / exit |

The base support relation is:

```text
S_base =
  {(a,a), (a,b),
   (b,b), (b,c),
   (c,c), (c,d),
   (d,d)}.
```

The live institutional-license intervention rewrites support:

```text
S_license =
  {(a,a), (a,b),
   (b,b), (b,d),
   (c,c), (c,d),
   (d,d)}.
```

Thus:

```text
supportUnder(theta_open,b,d) = False
supportUnder(theta_license,b,d) = True
supportUnder(theta_open,b,c) = True
supportUnder(theta_license,b,c) = False
```

The conditioning-only support is unchanged:

```text
S_low_fee = S_high_fee = S_base.
```

The washout/static-label support is unchanged:

```text
S_static_blue = S_static_red = S_base.
```

The macro-inert and near-zero transition controls also keep the support
signature unchanged:

```text
S_macro_label_left = S_macro_label_right = S_base
S_near_low = S_near_high = S_base.
```

The constitutive support is:

```text
S_constitution_old = S_base
S_constitution_new =
  S_base union {(a,d)}
```

The closure-only stack-active control leaves support unchanged but changes the
closure signature:

```text
S_closure_old = S_closure_new = S_base.
```

Closure signatures are declared as exact labels:

| intervention | closure signature |
| --- | --- |
| `theta_open` | `closure_base` |
| `theta_license` | `closure_license` |
| `theta_low_fee` | `closure_base` |
| `theta_high_fee` | `closure_base` |
| `theta_static_blue` | `closure_base` |
| `theta_static_red` | `closure_base` |
| `theta_macro_left` | `closure_base` |
| `theta_macro_right` | `closure_base` |
| `theta_near_low` | `closure_base` |
| `theta_near_high` | `closure_base` |
| `theta_constitution_old` | `closure_base` |
| `theta_constitution_new` | `closure_constitution` |
| `theta_closure_old` | `closure_base` |
| `theta_closure_new` | `closure_cycle_rank_2` |

The support comparator uses exact set membership. The closure comparator uses
the closure-signature table above. The parameter comparator uses exact
registered parameter values:

| comparison | parameter value under left intervention | parameter value under right intervention | `parametersDiffer` |
| --- | ---: | ---: | --- |
| `comp_conditioning_fee` | `Fraction(1,3)` | `Fraction(2,3)` | `True` |
| `comp_washout_static` | `Fraction(1,2)` | `Fraction(1,2)` | `False` |
| `comp_stack_license` | `Fraction(1,2)` | `Fraction(1,2)` | `False` |
| `comp_constitutive_rule` | `Fraction(1,2)` | `Fraction(1,2)` | `False` |
| `comp_stack_closure` | `Fraction(1,2)` | `Fraction(1,2)` | `False` |
| `comp_macro_label` | `Fraction(1,2)` | `Fraction(1,2)` | `False` |
| `comp_near_zero` | `Fraction(0,1)` | `Fraction(1,1000)` | `True` |

### Institutional Interventions

The carried intervention records are:

| intervention | label | intervention record | support | closure | source tag | generatedByS | inScope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `theta_open` | `open_market` | `irec_open` | `S_base` | `closure_base` | `committed_state` | `true` | `true` |
| `theta_license` | `license_regime` | `irec_license` | `S_license` | `closure_license` | `committed_state` | `true` | `true` |
| `theta_low_fee` | `fee_low` | `irec_low_fee` | `S_base` | `closure_base` | `committed_state` | `true` | `true` |
| `theta_high_fee` | `fee_high` | `irec_high_fee` | `S_base` | `closure_base` | `committed_state` | `true` | `true` |
| `theta_static_blue` | `static_blue` | `irec_static_blue` | `S_base` | `closure_base` | `committed_state` | `true` | `true` |
| `theta_static_red` | `static_red` | `irec_static_red` | `S_base` | `closure_base` | `committed_state` | `true` | `true` |
| `theta_macro_left` | `macro_left` | `irec_macro_left` | `S_base` | `closure_base` | `committed_state` | `true` | `true` |
| `theta_macro_right` | `macro_right` | `irec_macro_right` | `S_base` | `closure_base` | `committed_state` | `true` | `true` |
| `theta_near_low` | `near_low` | `irec_near_low` | `S_base` | `closure_base` | `committed_state` | `true` | `true` |
| `theta_near_high` | `near_high` | `irec_near_high` | `S_base` | `closure_base` | `committed_state` | `true` | `true` |
| `theta_constitution_old` | `charter_old` | `irec_charter_old` | `S_base` | `closure_base` | `committed_state` | `true` | `true` |
| `theta_constitution_new` | `charter_new` | `irec_charter_new` | `S_constitution_new` | `closure_constitution` | `committed_state` | `true` | `true` |
| `theta_closure_old` | `closure_old` | `irec_closure_old` | `S_base` | `closure_base` | `committed_state` | `true` | `true` |
| `theta_closure_new` | `closure_new` | `irec_closure_new` | `S_base` | `closure_cycle_rank_2` | `committed_state` | `true` | `true` |

All listed intervention and label records are carried under `labelPolicy` and
`interventionPolicy` with the listed source triples. All listed ledger entries
are in `S.Lambda_S.ledgerEntries`. All listed audit records have
`HasCarriedRecordEvidence(S.auditRecordPolicy, auditRecord)`.

### Matched Comparisons And Channel Records

The main comparisons are:

| comparison | theta_i | theta_j | channel record | uncontrolled difference | purpose |
| --- | --- | --- | --- | --- | --- |
| `comp_stack_license` | `theta_open` | `theta_license` | `td_accepted_stack` | `none` | support rewrite / stack-active |
| `comp_conditioning_fee` | `theta_low_fee` | `theta_high_fee` | `td_accepted_conditioning` | `none` | parameter-only conditioning |
| `comp_washout_static` | `theta_static_blue` | `theta_static_red` | `td_accepted_washout` | `none` | static-label washout |
| `comp_constitutive_rule` | `theta_constitution_old` | `theta_constitution_new` | `td_accepted_constitutive` | `none` | E4-certified constitutive |
| `comp_stack_closure` | `theta_closure_old` | `theta_closure_new` | `td_accepted_closure` | `none` | closure-only stack-active |
| `comp_macro_label` | `theta_macro_left` | `theta_macro_right` | `td_structural_only` | `none` | inert macro-label control |
| `comp_near_zero` | `theta_near_low` | `theta_near_high` | `td_accepted_conditioning` | `none` | near-zero parameter control |
| `comp_stack_blocked_channel` | `theta_open` | `theta_license` | `td_structural_only` | `none` | genuine support difference with blocked channel |
| `comp_delta_claimed` | `theta_open` | `theta_license` | `td_accepted_delta_claimed` | `none` | claimed structural rewrite with placebo reproduction |
| `comp_delta_placebo` | `theta_low_fee` | `theta_high_fee` | `td_accepted_delta_placebo` | `none` | independent parameter-only placebo |
| `comp_unmatched` | `theta_open` | `theta_license` | `td_accepted_stack` | `some uncontrolled_context_shift` | matched-controls failure |
| `comp_unlinked_other` | `theta_static_blue` | `theta_static_red` | `td_accepted_washout` | `none` | unlinked-evidence control target |

Every `td_accepted_*` record below reuses FIII's `acceptedTopDownRecord`
field values:

| field | value |
| --- | --- |
| `host` | `Host.fin` |
| `profile` | `baseProfile` |
| `macroRecordPresent` | `true` |
| `substrateRecordPresent` | `true` |
| `structuralPathPresent` | `true` |
| `interventionGate` | `true` |
| `matchedControlsGate` | `true` |
| `feasibilityGate` | `true` |
| `sourceGate` | `true` |
| `visibilityGate` | `true` |
| `auditGate` | `true` |
| `noSmugglingGate` | `true` |
| `effectGate` | `true` |
| `comparatorFinite` | `true` |
| `thresholdFinite` | `true` |
| `nonclaimRecorded` | `true` |

The NC-TD control reuses FIII's `structuralOnlyTopDownRecord` field values:

```text
structuralPathPresent = true
interventionGate = false
effectGate = false
all other fields equal acceptedTopDownRecord.
```

Registered FIII outcomes:

| record | `StructDown` | `TopDownChannelAcceptedBool` | `TopDownChannelClaimStatus` |
| --- | --- | --- | --- |
| `td_accepted_stack` | `True` | `True` | `accepted` |
| `td_accepted_constitutive` | `True` | `True` | `accepted` |
| `td_accepted_closure` | `True` | `True` | `accepted` |
| `td_accepted_conditioning` | `True` | `True` | `accepted` |
| `td_accepted_washout` | `True` | `True` | `accepted` |
| `td_accepted_delta_claimed` | `True` | `True` | `accepted` |
| `td_accepted_delta_placebo` | `True` | `True` | `accepted` |
| `td_structural_only` | `True` | `False` | `blocked` |

### Structural And Parameter Effects

The main structural effects are:

| effect | comparison record | channel record | support witness | closure witness | observed outcome |
| --- | --- | --- | --- | --- | --- |
| `effect_stack_exit` | `mcr_stack_license` | `td_accepted_stack` | `some(b,d)` | `none` | `out_direct_exit_available` |
| `effect_constitutive_charter` | `mcr_constitutive_rule` | `td_accepted_constitutive` | `some(a,d)` | `some closure_diff_constitution` | `out_constitutional_exit_available` |
| `effect_stack_closure` | `mcr_stack_closure` | `td_accepted_closure` | `none` | `some closure_diff_cycle_rank` | `out_cycle_rank_changed` |
| `effect_blocked_channel` | `mcr_stack_blocked_channel` | `td_structural_only` | `some(b,d)` | `none` | `out_blocked_channel_support_difference` |
| `effect_delta_claimed` | `mcr_delta_claimed` | `td_accepted_delta_claimed` | `some(b,d)` | `none` | `out_defection_pressure_shift` |
| `effect_unlinked` | `mcr_unlinked_other` | `td_accepted_stack` | `some(b,d)` | `none` | `out_direct_exit_available` |

The parameter effects are:

| parameter effect | comparison record | parameter record | observed outcome |
| --- | --- | --- | --- |
| `param_effect_fee` | `mcr_conditioning_fee` | `prec_fee` | `out_fee_shift_only` |
| `param_effect_delta_placebo` | `mcr_delta_placebo` | `prec_delta_placebo` | `out_defection_pressure_shift` |
| `param_effect_near_zero` | `mcr_near_zero` | `prec_near_zero` | `out_tiny_weight_shift` |

For `effect_stack_exit`:

```text
supportUnder(theta_open,b,d) = False
supportUnder(theta_license,b,d) = True
StructuralEffectFor(comp_stack_license,td_accepted_stack,effect_stack_exit) = True
```

For `effect_constitutive_charter`:

```text
supportUnder(theta_constitution_old,a,d) = False
supportUnder(theta_constitution_new,a,d) = True
ClosureDiffers(theta_constitution_old,theta_constitution_new) = True
StructuralEffectFor(comp_constitutive_rule,td_accepted_constitutive,
  effect_constitutive_charter) = True
```

For `effect_stack_closure`:

```text
S_closure_old = S_closure_new = S_base
ClosureDiffers(theta_closure_old,theta_closure_new) = True
KernelSupportDiffers(theta_closure_old,theta_closure_new) = False
StructuralEffectFor(comp_stack_closure,td_accepted_closure,
  effect_stack_closure) = True
```

For `effect_blocked_channel`:

```text
supportUnder(theta_open,b,d) = False
supportUnder(theta_license,b,d) = True
KernelSupportDiffers(theta_open,theta_license) = True
TopDownChannelAcceptedBool(td_structural_only) = False
StructuralEffectFor(comp_stack_blocked_channel,td_structural_only,
  effect_blocked_channel) = False
```

The failure is specifically due to the blocked FIII channel record, not due
to a fake support difference.

For `param_effect_fee`:

```text
ParameterConditioningOnly(comp_conditioning_fee) = True
StructuralEffectFor(comp_conditioning_fee,_,_) = False
```

For `effect_unlinked`:

```text
effect_unlinked.comparisonRecord = mcr_unlinked_other
comp_stack_license.comparisonRecord = mcr_stack_license
effect_unlinked.channelRecord = td_accepted_stack
StructuralEffectFor(comp_stack_license,td_accepted_stack,effect_unlinked) = False
```

The rejection is by the anti-unlinked-evidence equality
`effect.comparisonRecord = comparison.comparisonRecord`.

### Delta Stack Placebo

The genuine stack-active comparison has no parameter-only placebo reproducing
its observed outcome:

```text
DeltaStackEmptyFor(comp_stack_license,effect_stack_exit) = True.
```

The falsifier control has one:

```text
ParameterConditioningOnly(comp_delta_placebo) = True.
ReproducesClaimedEffect(param_effect_delta_placebo,effect_delta_claimed) = True,
because both observedOutcome fields are out_defection_pressure_shift.
Delta_stack(comp_delta_claimed,effect_delta_claimed,
  comp_delta_placebo,param_effect_delta_placebo) = True.
DeltaStackEmptyFor(comp_delta_claimed,effect_delta_claimed) = False.
```

This is the counterfactual/placebo version of `Delta_stack`, not the earlier
vacuous same-comparison version.

### Carried Status Records

The carried status records are:

| status record | comparison | status | channelRecord | effectRecord | parameterRecord | compiledRecord |
| --- | --- | --- | --- | --- | --- | --- |
| `isr_stack` | `mcr_stack_license` | `stack_active` | `some td_accepted_stack` | `some ierc_stack_exit` | `none` | `none` |
| `isr_constitutive` | `mcr_constitutive_rule` | `constitutive` | `some td_accepted_constitutive` | `some ierc_constitutive_charter` | `none` | `some comp_rec_constitutive` |
| `isr_stack_closure` | `mcr_stack_closure` | `stack_active` | `some td_accepted_closure` | `some ierc_stack_closure` | `none` | `none` |
| `isr_conditioning` | `mcr_conditioning_fee` | `conditioning` | `none` | `none` | `some prec_fee` | `none` |
| `isr_inert` | `mcr_washout_static` | `inert` | `none` | `none` | `none` | `none` |
| `isr_macro_inert` | `mcr_macro_label` | `inert` | `none` | `none` | `none` | `none` |
| `isr_near_zero` | `mcr_near_zero` | `conditioning` | `none` | `none` | `some prec_near_zero` | `none` |
| `isr_blocked_channel` | `mcr_stack_blocked_channel` | `inert` | `none` | `none` | `none` | `none` |

All status records are carried under `statusPolicy` with:

```text
sourceTag = committed_state
generatedByS = true
inScope = true
```

All status-record ledger entries are in `S.Lambda_S.ledgerEntries`, and all
status-record audit entries have `HasCarriedRecordEvidence`.

### E4 Compilation Certified Input

E4 has not landed. E11 therefore treats compilation as certified input.
Round B should implement this as a deterministic table:

```text
e4Compiled.holds(comp_constitutive_rule,
  td_accepted_constitutive,effect_constitutive_charter) = True

e4Compiled.compiledRecordFor(comp_constitutive_rule,
  td_accepted_constitutive,effect_constitutive_charter)
  = comp_rec_constitutive
```

All other `e4Compiled.holds` values in this fixture are `False`.

Therefore:

```text
ConstitutiveEvidenceExistsFor(comp_stack_license) = False.
ConstitutiveEvidenceExistsFor(comp_stack_closure) = False.
ConstitutiveEvidenceExistsFor(comp_constitutive_rule) = True.
```

## 2. Registered Theorem-Facing Predictions

### `E11_StackActivity`

The theorem-facing stack-active row is:

```text
comparison = comp_stack_license
channelRecord = td_accepted_stack
effect = effect_stack_exit
statusRecord = isr_stack
```

Registered facts:

| predicate or value | registered value |
| --- | --- |
| `MatchedControlsComparison(comp_stack_license)` | `True` |
| `StructuralEffectFor(comp_stack_license,td_accepted_stack,effect_stack_exit)` | `True` |
| `DeltaStackEmptyFor(comp_stack_license,effect_stack_exit)` | `True` |
| `ConstitutiveEvidenceExistsFor(comp_stack_license)` | `False` |
| `InstitutionalRewriteStatusOccurrenceFor(comp_stack_license,isr_stack)` | `True` |
| `isr_stack.status` | `stack_active` |
| `isr_stack.channelRecord` | `some td_accepted_stack` |
| `isr_stack.effectRecord` | `some ierc_stack_exit` |
| `isr_stack.parameterRecord` | `none` |
| `isr_stack.compiledRecord` | `none` |
| `StackActiveHolds(comp_stack_license)` | `True` |

### `E11_Constitutive`

This Round A fixture exercises the constitutive branch using E4 certified
input rather than deferring the branch:

```text
comparison = comp_constitutive_rule
channelRecord = td_accepted_constitutive
effect = effect_constitutive_charter
compiledRecord = comp_rec_constitutive
statusRecord = isr_constitutive
```

Registered facts:

| predicate or value | registered value |
| --- | --- |
| `MatchedControlsComparison(comp_constitutive_rule)` | `True` |
| `StructuralEffectFor(comp_constitutive_rule,td_accepted_constitutive,effect_constitutive_charter)` | `True` |
| `DeltaStackEmptyFor(comp_constitutive_rule,effect_constitutive_charter)` | `True` |
| `e4Compiled.holds(comp_constitutive_rule,td_accepted_constitutive,effect_constitutive_charter)` | `True` |
| `CarriedRecordAt(compiledPolicy,comp_rec_constitutive,n_compiled,committed_state,true,true)` | `True` |
| `compiledRecordFor(...) = comp_rec_constitutive` | `True` |
| `InstitutionalRewriteStatusOccurrenceFor(comp_constitutive_rule,isr_constitutive)` | `True` |
| `isr_constitutive.status` | `constitutive` |
| `isr_constitutive.compiledRecord` | `some comp_rec_constitutive` |
| `ConstitutiveHolds(comp_constitutive_rule)` | `True` |

### `E11_ConditioningOnly`

The theorem-facing conditioning row is:

```text
comparison = comp_conditioning_fee
parameterEffect = param_effect_fee
statusRecord = isr_conditioning
```

Registered facts:

| predicate or value | registered value |
| --- | --- |
| `MatchedControlsComparison(comp_conditioning_fee)` | `True` |
| `ParameterConditioningOnly(comp_conditioning_fee)` | `True` |
| `StructuralEffectFor(comp_conditioning_fee,_,_)` | `False` for every channel/effect pair in the fixture |
| `param_effect_fee.comparisonRecord = mcr_conditioning_fee` | `True` |
| `CarriedRecordAt(parameterPolicy,prec_fee,n_parameter,committed_state,true,true)` | `True` |
| `InstitutionalRewriteStatusOccurrenceFor(comp_conditioning_fee,isr_conditioning)` | `True` |
| `isr_conditioning.status` | `conditioning` |
| `isr_conditioning.parameterRecord` | `some prec_fee` |
| `ConditioningHolds(comp_conditioning_fee)` | `True` |

### `E11_WashoutInert`

The theorem-facing washout row is:

```text
comparison = comp_washout_static
statusRecord = isr_inert
```

Registered facts:

| predicate or value | registered value |
| --- | --- |
| `StaticInstitutionalLabels(comp_washout_static)` | `True` |
| `BaseIndependentBehavior(comp_washout_static)` | `True` |
| `StrictInstitutionalRefinement(comp_washout_static)` | `False` |
| `ParameterConditioningOnly(comp_washout_static)` | `False` |
| `StructuralEffectFor(comp_washout_static,_,_)` | `False` for every channel/effect pair in the fixture |
| `WashoutNull(comp_washout_static)` | `True` |
| `InstitutionalRewriteStatusOccurrenceFor(comp_washout_static,isr_inert)` | `True` |
| `isr_inert.status` | `inert` |
| `isr_inert.channelRecord/effectRecord/parameterRecord/compiledRecord` | all `none` |
| `InertHolds(comp_washout_static)` | `True` |

### `E11_NCTDObstruction`

The NC-TD row uses FIII's own fixture:

```text
channelRecord = structuralOnlyTopDownRecord
```

Registered facts:

| predicate or value | registered value |
| --- | --- |
| `StructDown(structuralOnlyTopDownRecord)` | `True` |
| `TopDownChannelAcceptedBool(structuralOnlyTopDownRecord)` | `False` |
| `TopDownChannelClaimStatus(structuralOnlyTopDownRecord)` | `blocked` |
| `E11_NCTDObstruction` | `True`, by direct reuse of FIII's theorem |

### `E11_StatusPartition`

The status table is over actual carried status records, not labels or feasible
comparisons.

| row | comparison | carried status record | inert | conditioning | stack_active | constitutive |
| --- | --- | --- | --- | --- | --- | --- |
| `stack_support_rewrite` | `comp_stack_license` | `isr_stack` | `False` | `False` | `True` | `False` |
| `stack_closure_rewrite` | `comp_stack_closure` | `isr_stack_closure` | `False` | `False` | `True` | `False` |
| `constitutive_compiled` | `comp_constitutive_rule` | `isr_constitutive` | `False` | `False` | `False` | `True` |
| `conditioning_fee` | `comp_conditioning_fee` | `isr_conditioning` | `False` | `True` | `False` | `False` |
| `washout_static` | `comp_washout_static` | `isr_inert` | `True` | `False` | `False` | `False` |

The `stack_support_rewrite` row is not blocked by
`ConstitutiveEvidenceExistsFor`, because the only E4-compiled effect in this
fixture is tied to `comp_constitutive_rule`, not to `comp_stack_license`.

## 3. Lucas-Style Descent Failure Demonstration

The registered macro law is:

```text
L0: direct one-step sanction/exit from cooperation is unavailable.
L0_readout = support(b,d) = 0.
```

This law descends under washout/static labels:

| regime | comparison | predicted `support(b,d)` | actual `support(b,d)` | descent residual |
| --- | --- | ---: | ---: | ---: |
| washout/static | `comp_washout_static` | `0` | `0` | `0` |
| conditioning-only | `comp_conditioning_fee` | `0` | `0` | `0` |
| stack-active license | `comp_stack_license` | `0` | `1` | `1` |

The residual is exact:

```text
residual = abs(actual_support_indicator - predicted_support_indicator).
```

The Lucas-style failure is switched on by stack-activity:

```text
descent_failure(comp_washout_static) = False
descent_failure(comp_conditioning_fee) = False
descent_failure(comp_stack_license) = True
```

The parameter-only row may change transition weights from `Fraction(1,3)` to
`Fraction(2,3)`, but it does not change the support readout used by `L0`.

## 4. Null And Control Predictions

### NC-TD Control

Using `td_structural_only = structuralOnlyTopDownRecord`:

| quantity | registered value |
| --- | --- |
| `structuralPathPresent` | `true` |
| `interventionGate` | `false` |
| `effectGate` | `false` |
| `TopDownChannelAcceptedBool` | `False` |
| `TopDownChannelClaimStatus` | `blocked` |
| accepted channel evidence? | `False` |

### Blocked Channel With Genuine Structural Difference Control

Post-review addition: methodology review found that the original NC-TD-style
controls used a blocked channel only on rows with no support or closure
difference. This control tests the sharper E11 discipline: even a genuine
lower-layer support change must not be credited as `stack_active` unless the
same channel record is an accepted FIII top-down channel. This is not a
post-hoc fit to observed sweep output; it is forced by Lean's
`StructuralEffectFor` conjunct
`TopDownChannelAcceptedBool(channelRecord) = true`.

```text
comparison = comp_stack_blocked_channel
theta_i = theta_open
theta_j = theta_license
channelRecord = td_structural_only
effect = effect_blocked_channel
statusRecord = isr_blocked_channel
```

Registered predictions:

| quantity | registered value |
| --- | --- |
| `KernelSupportDiffers(theta_open,theta_license)` | `True` |
| support witness `(b,d)` is genuine | `True` |
| `TopDownChannelAcceptedBool(td_structural_only)` | `False` |
| `TopDownChannelClaimStatus(td_structural_only)` | `blocked` |
| `StructuralEffectFor(comp_stack_blocked_channel,td_structural_only,effect_blocked_channel)` | `False` |
| rejection reason | blocked channel, not fake support difference |
| `StackActiveHolds(comp_stack_blocked_channel)` | `False` |
| predicted status | `inert` via the non-washout inert branch |

The inert classification is not washout: `ParameterConditioningOnly` is false
and no `StructuralEffectFor` witness exists because the only supplied channel
is blocked. This keeps genuine structural difference separate from accepted
top-down channel evidence.

### `Delta_stack` Nonempty Control

| quantity | registered value |
| --- | --- |
| claimed comparison | `comp_delta_claimed` |
| claimed effect | `effect_delta_claimed` |
| placebo comparison | `comp_delta_placebo` |
| placebo parameter effect | `param_effect_delta_placebo` |
| `ParameterConditioningOnly(comp_delta_placebo)` | `True` |
| `ReproducesClaimedEffect(param_effect_delta_placebo,effect_delta_claimed)` | `True` |
| `Delta_stack(...)` | `True` |
| `DeltaStackEmptyFor(comp_delta_claimed,effect_delta_claimed)` | `False` |
| status credited as `stack_active`? | `False` |

### Matched-Controls Failure Control

```text
comp_unmatched.uncontrolledDifferenceWitness = some uncontrolled_context_shift.
```

Registered predictions:

| quantity | registered value |
| --- | --- |
| `MatchedControlsComparison(comp_unmatched)` | `False` |
| `StructuralEffectFor(comp_unmatched,_,_)` | `False` |
| status theorem applies? | `False` |

### Inert/Conditioning Boundary Control

The boundary is the `ParameterConditioningOnly` guard:

| comparison | `StaticInstitutionalLabels` | `BaseIndependentBehavior` | `parametersDiffer` | `ParameterConditioningOnly` | predicted status |
| --- | --- | --- | --- | --- | --- |
| `comp_washout_static` | `True` | `True` | `False` | `False` | `inert` |
| `comp_conditioning_fee` | `False` | `False` | `True` | `True` | `conditioning` |

The same labels being carried is not enough to make the washout row
conditioning. Conversely, a parameter-only comparison is not washout because
`ParameterConditioningOnly` is true.

### Unlinked Evidence Control

The control pairs an accepted channel for `comp_stack_license` with an effect
record whose `comparisonRecord` is `mcr_unlinked_other`.

Registered predictions:

| quantity | registered value |
| --- | --- |
| `TopDownChannelAcceptedBool(td_accepted_stack)` | `True` |
| support inequality `supportUnder(theta_open,b,d) != supportUnder(theta_license,b,d)` | `True` |
| `effect_unlinked.comparisonRecord = comp_stack_license.comparisonRecord` | `False` |
| `StructuralEffectFor(comp_stack_license,td_accepted_stack,effect_unlinked)` | `False` |
| `StackActiveHolds` from this unlinked evidence | `False` |

### Closure-Only Stack-Active Control

This control covers the case where lower support is identical but lower
closure changes.

Registered predictions:

| quantity | registered value |
| --- | --- |
| comparison | `comp_stack_closure` |
| `KernelSupportDiffers(theta_closure_old,theta_closure_new)` | `False` |
| `ClosureDiffers(theta_closure_old,theta_closure_new)` | `True` |
| `StructuralEffectFor(comp_stack_closure,td_accepted_closure,effect_stack_closure)` | `True` |
| `DeltaStackEmptyFor(comp_stack_closure,effect_stack_closure)` | `True` |
| `ConstitutiveEvidenceExistsFor(comp_stack_closure)` | `False` |
| predicted status | `stack_active` |

This is not a support-rewrite duplicate. The only structural witness is
`closure_diff_cycle_rank`.

### Macro-Inert Control

This control covers an inert row with no accepted channel and no
parameter-only shift.

```text
comparison = comp_macro_label
theta_i = theta_macro_left
theta_j = theta_macro_right
channelRecord = td_structural_only
statusRecord = isr_macro_inert
```

Registered predictions:

| quantity | registered value |
| --- | --- |
| `TopDownChannelAcceptedBool(td_structural_only)` | `False` |
| `supportUnder(theta_macro_left,_,_) = supportUnder(theta_macro_right,_,_)` | `True` |
| `ClosureDiffers(theta_macro_left,theta_macro_right)` | `False` |
| parameter values | `Fraction(1,2)` and `Fraction(1,2)` |
| `ParameterConditioningOnly(comp_macro_label)` | `False` |
| `StructuralEffectFor(comp_macro_label,_,_)` | `False` |
| predicted status | `inert` |

### Near-Zero Transition-Tolerance Control

This control prevents transition-probability drift from being silently
promoted to a support rewrite.

```text
epsilon_support = Fraction(1,100)
transitionWeight(theta_near_low,b,d) = Fraction(0,1)
transitionWeight(theta_near_high,b,d) = Fraction(1,1000)
```

Because both weights are below `epsilon_support`, the support readout remains
false on both sides:

| quantity | registered value |
| --- | --- |
| `supportUnder(theta_near_low,b,d)` | `False` |
| `supportUnder(theta_near_high,b,d)` | `False` |
| `KernelSupportDiffers(theta_near_low,theta_near_high)` | `False` |
| `ClosureDiffers(theta_near_low,theta_near_high)` | `False` |
| `ParameterConditioningOnly(comp_near_zero)` | `True` |
| predicted status | `conditioning`, not `stack_active` |

### Constitutive Overclaim Before E4 Control

This control checks that an ordinary stack-active rewrite is not promoted to
`constitutive` merely because it has an accepted top-down channel.

Registered predictions:

| quantity | registered value |
| --- | --- |
| comparison | `comp_stack_license` |
| `StructuralEffectFor(comp_stack_license,td_accepted_stack,effect_stack_exit)` | `True` |
| `e4Compiled.holds(comp_stack_license,td_accepted_stack,effect_stack_exit)` | `False` |
| `ConstitutiveEvidenceExistsFor(comp_stack_license)` | `False` |
| `ConstitutiveHolds(comp_stack_license)` | `False` |
| `StackActiveHolds(comp_stack_license)` | `True` |

## 5. Scope Note: Actual Carried Comparison vs Feasible Intervention

The registered predictions are about the actual carried interventions,
matched comparisons, FIII channel records, effect records, parameter-effect
records, compiled records, ledger entries, audit records, and status records
exposed by the toy-lab state.

They are not about an existential claim that some intervention pair could be
made stack-active. Round B may compute feasibility sanity checks, but it must
not use an existential feasible intervention as the status classifier.

The status rows above must be derived from:

```text
ActualCarriedInstitutionalComparison:
  InstitutionalInterventionOccurrenceFor
  MatchedControlsComparison
  StructuralEffectFor / ParameterConditioningOnly / WashoutNull
  Delta_stack / DeltaStackEmptyFor
  InstitutionalRewriteStatusOccurrenceFor
  carried status records
```

not from:

```text
ExistentialFeasibleInstitution:
  some label-shaped object
  some top-down-looking path
  some support difference measured under a different comparison
  some status tag copied from a registered table
```

This is E11's analogue of E1's generator-reachability guard, E2's
actual-carried-tower versus feasible-tower guard, and E3's actual carried
apparatus versus existential maintenance guard.

## 6. Falsification Conditions

The following outcomes falsify the corresponding registered predictions.

1. The fixture is falsified if the future sweep does not build the actual
   carried institutional interventions, matched comparisons, FIII channel
   records, structural effects, parameter effects, compiled records, and
   status records listed above, or if it uses a different carrier than
   `X = {a,b,c,d}` without an explicit correction to this pre-registration.

2. The FIII fixture is falsified if `td_accepted_stack` does not use
   `acceptedTopDownRecord` field values, or if `td_structural_only` does not
   use `structuralOnlyTopDownRecord` field values.

3. `E11_StackActivity` is falsified if
   `StructuralEffectFor(comp_stack_license,td_accepted_stack,effect_stack_exit)`
   is not computed from the actual support witness `(b,d)`, if
   `DeltaStackEmptyFor(comp_stack_license,effect_stack_exit)` is false, if
   `ConstitutiveEvidenceExistsFor(comp_stack_license)` is true, or if
   `StackActiveHolds(comp_stack_license)` is reported without the carried
   `isr_stack` status record.

4. `E11_Constitutive` is falsified if the constitutive row is reported
   without the certified E4 table value, without the carried
   `comp_rec_constitutive` record, or without
   `compiledRecordFor(...) = comp_rec_constitutive`.

5. `E11_ConditioningOnly` is falsified if the fee comparison changes support
   or closure, if `ParameterConditioningOnly(comp_conditioning_fee)` is false,
   or if `ConditioningHolds(comp_conditioning_fee)` is reported without
   `isr_conditioning`.

6. `E11_WashoutInert` is falsified if
   `ParameterConditioningOnly(comp_washout_static)` is true, if any
   structural effect is found for `comp_washout_static`, or if the row is not
   classified as exactly `inert`.

7. `E11_NCTDObstruction` is falsified if `structuralOnlyTopDownRecord` is
   accepted, or if its claim status is anything other than `blocked`.

8. `E11_StatusPartition` is falsified if any exercised row in the status
   table has zero statuses or more than one status, or if any row's computed
   status differs from the registered table.

9. The closure-only stack-active control is falsified if
   `KernelSupportDiffers(theta_closure_old,theta_closure_new)` is true, if
   `ClosureDiffers(theta_closure_old,theta_closure_new)` is false, or if
   `comp_stack_closure` is not classified as `stack_active`.

10. The macro-inert control is falsified if `td_structural_only` is accepted,
    if any parameter-only or structural effect is found for `comp_macro_label`,
    or if `comp_macro_label` is not classified as `inert`.

11. The near-zero tolerance control is falsified if the
    `Fraction(1,1000)` transition-weight shift is promoted to a support
    difference under `epsilon_support = Fraction(1,100)`, or if the row is
    classified as `stack_active`.

12. The constitutive-overclaim control is falsified if
    `ConstitutiveHolds(comp_stack_license)` is true without the certified E4
    compiled evidence and carried compiled record for that same comparison.

13. The Lucas-style descent prediction is falsified if the washout or
   conditioning row has descent residual other than `0`, or if the
   stack-active license row has residual other than `1`.

14. The `Delta_stack` control is falsified if
    `DeltaStackEmptyFor(comp_delta_claimed,effect_delta_claimed)` is true even
    though the independent parameter-only placebo reproduces
    `out_defection_pressure_shift`, or if that row is credited as
    `stack_active`.

15. The matched-controls control is falsified if
    `comp_unmatched.uncontrolledDifferenceWitness = some ...` is accepted as a
    valid matched-controls comparison.

16. The inert/conditioning boundary control is falsified if
    `comp_washout_static` and `comp_conditioning_fee` produce the same status
    despite opposite `ParameterConditioningOnly` values.

17. The unlinked-evidence control is falsified if
    `StructuralEffectFor(comp_stack_license,td_accepted_stack,effect_unlinked)`
    is true despite `effect_unlinked.comparisonRecord !=
    comp_stack_license.comparisonRecord`.

18. The actual-vs-existential scope guard is falsified if a row is classified
    using a support difference, channel record, parameter effect, or status
    record not carried by the actual comparison being classified.

19. The blocked-channel control fixture is falsified if
    `comp_stack_blocked_channel` is not built from
    `theta_open`/`theta_license` with `td_structural_only` and
    `effect_blocked_channel`.

20. The blocked-channel structural-difference control is falsified if
    `StackActiveHolds(comp_stack_blocked_channel)` is true, or if
    `StructuralEffectFor(comp_stack_blocked_channel,td_structural_only,
    effect_blocked_channel)` is true despite
    `TopDownChannelAcceptedBool(td_structural_only) = false`.

21. The future sweep guard is falsified if Round B hardcodes any status,
    support/closure difference, gate outcome, `Delta_stack` outcome, or
    Lucas residual from this document instead of computing it from the
    concrete carried records, support/closure comparators, parameter
    comparator, and FIII gate functions.

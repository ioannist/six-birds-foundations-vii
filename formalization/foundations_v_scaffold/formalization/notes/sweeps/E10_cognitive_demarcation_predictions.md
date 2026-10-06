# E10 Cognitive Demarcation Law - Toy-Lab Predictions (Round A, pre-registration)

This document pre-registers the toy-lab probe for E10 before any E10 sweep
implementation exists. It is grounded in the accepted six-field normal form
`formalization/notes/examples/E10.md` and the mechanized Lean module
`lean/SixBirdsFoundationsV/Laws/E10CognitiveDemarcation.lean`.

The probe mirrors the Lean predicates, not a looser prose reading. In
particular, E10 is scoped by concrete claim references
`CognitiveClaimRef`, `IntentionClaimRef`, and `GoalClaimRef`; package repair
credit must pass through the target package's own `PackageRepairDescent`;
top-down gating must use the shared `CognitiveDemarcationClassifierContext`
comparators; support records must be linked to their own intervention records;
and goal persistence must quantify over real `RouteSubstitutionEvaluation`
witnesses for every declared route.

All quantities below are exact rationals or finite sets. Round B must use
`fractions.Fraction` for rational data and no floating-point arithmetic or
randomness.

Round B must report exactly 26 registered comparisons.

## 1. Toy-Lab Configuration

### Single carrier and carried-source convention

The fixture contains one deterministic finite E-system carrier:

```text
S.Z = {z0, z1, ..., z9}
S.T.suppK(zi, zj) := j = (i + 1) mod 10
```

Every positive carried record uses source tag `committed_state` or
`audited_cell_records`, `generatedByS = true`, and `inScope = true`.
Scaffolding and uncarried controls intentionally omit at least one of these
D3 occurrence facts.

The challenge and target classes are:

| record | class id | role |
| --- | ---: | --- |
| `C_nav` | `1` | access/action navigation class |
| `C_memory` | `2` | passive decodable memory class |
| `C_planning` | `3` | intention/goal target class |
| `C_other` | `4` | wrong-claim scoping control |

Target-class records:

```text
T_nav = TargetClassRecord(recordId = 101, challengeClass = C_nav)
T_plan = TargetClassRecord(recordId = 102, challengeClass = C_planning)
T_other = TargetClassRecord(recordId = 103, challengeClass = C_other)
```

### Shared classifier context

The shared context is `ctx_cog`. Round B must instantiate it once and pass the
same object to every predicate.

```text
ctx_cog.packageInstallsQuotient(package, qBefore, qAfter)
  := install_map[(package.recordId, qBefore.recordId)] = qAfter.recordId

ctx_cog.deltaNonempty(q, C)
  := Delta(q, C) is a nonempty split set

ctx_cog.deltaStrictlyReducedBy(qBefore, qAfter, C)
  := Delta(qAfter, C) proper-subset Delta(qBefore, C)

ctx_cog.kernelSupportDiffers(support1, support2)
  := support1.packageRecord = support2.packageRecord
     and support1.challengeClass = support2.challengeClass
     and support1.supportId != support2.supportId

ctx_cog.supportForIntervention(support, intervention)
  := support.packageRecord = intervention.packageRecord
     and support_link[(intervention.recordId)] = support.recordId

ctx_cog.channelCertifiesKernelComparison(channel, matched, support1, support2)
  := channel = tdc_accept_*
     and matched.interventionA and matched.interventionB are the two interventions
     and supportForIntervention(support1, matched.interventionA)
     and supportForIntervention(support2, matched.interventionB)
     and kernelSupportDiffers(support1, support2)

ctx_cog.decodesPackage(readout, package, C)
  := readout.packageRecord = package and readout.decodedClass = C

ctx_cog.scheduleExplainsKernelChange(schedule, supportBefore, supportAfter)
  := schedule.scheduleId = schedule_support_change[(supportBefore, supportAfter)]

ctx_cog.supportStrictSubset(restricted, unrestricted)
  := support_set[restricted] proper-subset support_set[unrestricted]

ctx_cog.targetCoherentUnderProbe(target, probe, restriction)
  := target_probe_coherence[(target, probe, restriction)] = true

ctx_cog.approximateSupportRestriction(restriction)
  := restriction.recordId in approximate_restriction_ids

ctx_cog.routeEvaluationTargets(eval, route, target)
  := eval.route = route and eval.targetQuotient = target

ctx_cog.routeSelectionPersists(target, evaluations)
  := every eval in evaluations targets target and persistence_flag[target] = true

ctx_cog.rewardProxyExplainsSelection(proxy, target)
  := proxy.theta = target.theta and proxy.proxyValue > 0
```

The `supportForIntervention` and `channelCertifiesKernelComparison`
comparators are deliberately shared. Round B must not install per-row
trivially true functions.

### FIII top-down channel records

The fixture uses the real vendored FIII shape from
`SixBirdsIII.TopDownChannel`:

```text
tdc_accept_nav:
  TopDownChannelRecord with all WF and gate booleans true
  TopDownChannelAcceptedBool = true
  TopDownChannelClaimStatus = ClaimStatus.accepted

tdc_accept_intention:
  same accepted shape, used for support restriction

tdc_accept_goal:
  same accepted shape, used for goal orientation

tdc_structural_only:
  structuralPathPresent = true
  interventionGate = false
  effectGate = false
  TopDownChannelAcceptedBool = false
  TopDownChannelClaimStatus = ClaimStatus.blocked
```

### Package, provenance, and Delta data

The main package records are:

| package | value id | declared class | formation/invocation carried? |
| --- | ---: | --- | --- |
| `pkg_nav_cognitive` | `10` | `C_nav` | true |
| `pkg_passive_memory` | `11` | `C_memory` | true |
| `pkg_schedule_trap` | `12` | `C_nav` | true |
| `pkg_external_scaffold` | `13` | `C_nav` | false |
| `pkg_structural_path` | `14` | `C_nav` | true |
| `pkg_decodable` | `15` | `C_memory` | true |
| `pkg_repair_no_gate` | `16` | `C_nav` | true |
| `pkg_gate_no_repair` | `17` | `C_nav` | true |
| `pkg_priority_decodable` | `18` | `C_memory` | true |
| `pkg_priority_schedule` | `19` | `C_nav` | true |
| `pkg_other_repair` | `20` | `C_other` | true |

Delta readouts are represented as exact split sets:

```text
PackageRepairDescent =
  witnessRecord.beforeQuotient = qBefore
  and witnessRecord.afterQuotient = qAfter
  and witnessRecord.challengeClass = C
  and package.declaredClass = C
  and Delta(qBefore, C) nonempty
  and packageInstallsQuotient(package, qBefore, qAfter)
  and Delta(qAfter, C) proper-subset Delta(qBefore, C)
```

| descent | package | class | before splits | after splits | install link | strict reduction |
| --- | --- | --- | --- | --- | --- | --- |
| `desc_nav_cognitive` | `pkg_nav_cognitive` | `C_nav` | `{a,b,c}` | `{a}` | true | true |
| `desc_repair_no_gate` | `pkg_repair_no_gate` | `C_nav` | `{d,e}` | `{d}` | true | true |
| `desc_priority_decodable` | `pkg_priority_decodable` | `C_memory` | `{m1,m2}` | `{m1}` | true | true |
| `desc_priority_schedule` | `pkg_priority_schedule` | `C_nav` | `{s1,s2}` | `{s1}` | true | true |
| `desc_other_real` | `pkg_other_repair` | `C_other` | `{x,y}` | `{x}` | true | true for the package's declared `C_other` class |

### Interventions, supports, matched controls, and inventories

For each accepted top-down gate, two distinct interventions are carried and
the support records are linked to their own intervention by the shared
`supportForIntervention` map.

| gate | package | class | intervention 1 `(idx,value)` | support 1 | intervention 2 `(idx,value)` | support 2 | channel |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `gate_nav_cognitive` | `pkg_nav_cognitive` | `C_nav` | `(0,0)` | `supp_nav_val0` | `(1,1)` | `supp_nav_val1` | `tdc_accept_nav` |
| `gate_gate_no_repair` | `pkg_gate_no_repair` | `C_nav` | `(0,0)` | `supp_gate_val0` | `(1,1)` | `supp_gate_val1` | `tdc_accept_nav` |
| `gate_intention` | `theta_intention` | `C_planning` | `(0,0)` | `supp_action_unrestricted` | `(1,1)` | `supp_action_restricted` | `tdc_accept_intention` |
| `gate_goal` | `theta_goal` | `C_planning` | `(0,0)` | `supp_goal_route0` | `(1,1)` | `supp_goal_route1` | `tdc_accept_goal` |

The support sets are:

| support | kind | support set |
| --- | --- | --- |
| `supp_nav_val0` | access | `{n0,n1,n2}` |
| `supp_nav_val1` | access | `{n0,n2}` |
| `supp_gate_val0` | access | `{g0,g1}` |
| `supp_gate_val1` | access | `{g0}` |
| `supp_action_unrestricted` | action | `{act0,act1,act2}` |
| `supp_action_restricted` | action | `{act1}` |
| `supp_action_approx` | action | `{act0,act1,act2}` |
| `supp_action_posthoc` | action | `{act1}` |
| `supp_goal_route0` | action | `{route0,route1}` |
| `supp_goal_route1` | action | `{route1}` |
| `supp_wrong_for_intervention` | access | `{n0,n1}` |

The load-bearing support-linkage control uses:

```text
supportForIntervention(supp_nav_val0, int_nav_value0) = true
supportForIntervention(supp_wrong_for_intervention, int_nav_value0) = false
channelCertifiesKernelComparison(tdc_accept_nav, match_nav,
  supp_wrong_for_intervention, supp_nav_val1) = false
```

Complete inventories are always scoped to the queried package/class. For
positive gates, `declaredAcceptedChannels = [the accepted channel]`. For
gate-ablated rows, `declaredAcceptedChannels = []`. For repair-absent rows,
`declaredDescentRecords = []`.

### Schedule trap, decodability, and structural controls

```text
schedule_nav_exogenous:
  challengeClass = C_nav
  scheduleId = 700
  scheduleExplainsKernelChange(schedule_nav_exogenous,
    supp_sched_before, supp_sched_after) = true
```

The decodability readouts are:

| readout | package | decoded class | `ctx.decodesPackage` |
| --- | --- | --- | --- |
| `readout_decodable` | `pkg_decodable` | `C_memory` | true |
| `readout_priority_decodable` | `pkg_priority_decodable` | `C_memory` | true |

Structural path:

```text
path_structural_only:
  package = pkg_structural_path
  challengeClass = C_nav
  channelRecord = tdc_structural_only
  StructDown(tdc_structural_only) = true
  TopDownChannelClaimStatus(tdc_structural_only) = ClaimStatus.blocked
```

### E10.1 intention records

The intention packages are:

| theta | declared class | provenance carried? |
| --- | --- | --- |
| `theta_intention` | `C_planning` | true |
| `theta_neutral` | `C_planning` | true |
| `theta_posthoc` | `C_planning` | true |
| `theta_approx` | `C_planning` | true |
| `theta_incoherent` | `C_planning` | true |
| `theta_priority_posthoc` | `C_planning` | true |
| `theta_uncarried_intention` | `C_planning` | false |

Support-restriction records:

| restriction | theta | target | unrestricted | restricted | time | outcome | strict subset | approximate | coherent probes |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| `restrict_intention` | `theta_intention` | `T_plan` | `supp_action_unrestricted` | `supp_action_restricted` | `2` | `5` | true | false | true |
| `restrict_posthoc` | `theta_posthoc` | `T_plan` | `supp_action_unrestricted` | `supp_action_restricted` | `8` | `5` | true | false | true |
| `restrict_approx` | `theta_approx` | `T_plan` | `supp_action_unrestricted` | `supp_action_approx` | `2` | `5` | false | true | true |
| `restrict_incoherent` | `theta_incoherent` | `T_plan` | `supp_action_unrestricted` | `supp_action_restricted` | `2` | `5` | true | false | false for `probe_plan_bad` |
| `restrict_priority_posthoc` | `theta_priority_posthoc` | `T_plan` | `supp_action_unrestricted` | `supp_action_restricted` | `9` | `5` | true | false | true |
| `restrict_uncarried_intention` | `theta_uncarried_intention` | `T_plan` | `supp_action_unrestricted` | `supp_action_restricted` | `2` | `5` | true | false | true |

For `restrict_intention`, `certifiedRestrictionLinked` is genuine:

```text
gate_intention.support1 = restrict_intention.unrestrictedSupport
gate_intention.support2 = restrict_intention.restrictedSupport
```

Future probes:

```text
probe_plan_ok_1, probe_plan_ok_2:
  targetClass = T_plan
  targetCoherentUnderProbe = true for restrict_intention

probe_plan_bad:
  targetClass = T_plan
  targetCoherentUnderProbe = false for restrict_incoherent
```

### E10.2 goal records

Goal packages:

| theta | declared class | provenance carried? |
| --- | --- | --- |
| `theta_goal` | `C_planning` | true |
| `theta_not_goal` | `C_planning` | true |
| `theta_reward_proxy` | `C_planning` | true |
| `theta_route_unstable` | `C_planning` | true |
| `theta_missing_eval` | `C_planning` | true |
| `theta_priority_reward` | `C_planning` | true |
| `theta_uncarried_goal` | `C_planning` | false |

Target quotients:

| target quotient | theta | target class | quotient id | carried |
| --- | --- | --- | ---: | --- |
| `target_goal_plan` | `theta_goal` | `T_plan` | `900` | true |
| `target_neutral_plan` | `theta_not_goal` | `T_plan` | `901` | true |
| `target_reward_plan` | `theta_reward_proxy` | `T_plan` | `902` | true |
| `target_unstable_plan` | `theta_route_unstable` | `T_plan` | `903` | true |
| `target_missing_eval_plan` | `theta_missing_eval` | `T_plan` | `904` | true |
| `target_priority_reward_plan` | `theta_priority_reward` | `T_plan` | `905` | true |
| `target_uncarried_goal_plan` | `theta_uncarried_goal` | `T_plan` | `906` | true |

Route substitutions and evaluations:

| route | target class | evaluation | target quotient | before splits | after splits | delta evaluated | carried |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `route_goal_a` | `T_plan` | `eval_goal_a` | `target_goal_plan` | `{r1,r2}` | `{r1}` | true | true |
| `route_goal_b` | `T_plan` | `eval_goal_b` | `target_goal_plan` | `{r3,r4}` | `{r3}` | true | true |
| `route_unstable_a` | `T_plan` | `eval_unstable_a` | `target_unstable_plan` | `{u1,u2}` | `{u1}` | true | true |
| `route_unstable_b` | `T_plan` | `eval_unstable_b` | `target_unstable_plan` | `{u3,u4}` | `{u3}` | true | true |
| `route_missing_a` | `T_plan` | `eval_missing_a` | `target_missing_eval_plan` | `{m1,m2}` | `{m1}` | true | true |
| `route_missing_b` | `T_plan` | absent | `target_missing_eval_plan` | `{m3,m4}` | absent | false | true |
| `route_uncarried_goal_a` | `T_plan` | `eval_uncarried_goal_a` | `target_uncarried_goal_plan` | `{cg1,cg2}` | `{cg1}` | true | true |
| `route_uncarried_goal_b` | `T_plan` | `eval_uncarried_goal_b` | `target_uncarried_goal_plan` | `{cg3,cg4}` | `{cg3}` | true | true |

Route-persistence facts:

```text
routeSelectionPersists(target_goal_plan, [eval_goal_a, eval_goal_b]) = true
routeSelectionPersists(target_unstable_plan, [eval_unstable_a, eval_unstable_b]) = false
everyRouteEvaluated([route_missing_a, route_missing_b], [eval_missing_a]) = false
routeSelectionPersists(target_uncarried_goal_plan,
  [eval_uncarried_goal_a, eval_uncarried_goal_b]) = true
```

Reward proxies:

| reward proxy | theta | proxy value | explains selection |
| --- | --- | ---: | --- |
| `reward_proxy_only_plan` | `theta_reward_proxy` | `7/10` | true |
| `reward_priority_plan` | `theta_priority_reward` | `9/10` | true |

## 2. Registered Theorem-Facing Predictions

Round B must report exactly 26 registered comparisons.

| theorem / apparatus | concrete instantiation | registered prediction |
| --- | --- | --- |
| `E10_CognitiveDemarcation` | every registered `CognitiveClaimRef` below | exactly one of the eight main status predicates holds for that claim |
| `E10_DecodableCorrelate` | `claim_pkg_decodable`, with scoped complete status | `DecodableCorrelateHolds = true`; `CognitiveHolds = false` |
| `E10_ScheduleTrapNull` | `claim_pkg_schedule_trap`, with scoped complete status | `ScheduleTrapHolds = true`; `CognitiveHolds = false` |
| `E10_1_Intention` | every registered `IntentionClaimRef` below | exactly one of the five intention status predicates holds for that claim |
| `E10_1_PostHocIntentionFalsifier` | `claim_intention_posthoc`, with scoped complete status | `PostHocIntentionHolds = true`; `IntentionHolds = false` |
| `E10_2_Goal` | every registered `GoalClaimRef` below | exactly one of the four goal status predicates holds for that claim |
| `E10_2_RewardProxyNotGoal` | `claim_goal_reward_proxy_only`, with scoped complete status | `RewardProxyOnlyHolds = true`; `GoalHolds = false` |

The current Lean falsifier corollaries use the scoped `Complete...Status`
hypothesis to access `statusUnique`; Round B must include the complete
claim-scoped record set in each falsifier comparison, not treat a bare status
label as globally exclusive.

## 3. Registered Main Status Scenarios

### `claim_pkg_nav_cognitive`

| field | predicted value |
| --- | --- |
| claim ref | `CognitiveClaimRef.package(pkg_nav_cognitive, C_nav)` |
| carried status record | `status_pkg_nav_cognitive`, status `cognitive` |
| provenance | true: package, formation, invocation carried |
| `PackageRepairDescent` | true via `desc_nav_cognitive` (`{a} proper-subset {a,b,c}` and install link true) |
| `TopDownKernelGateCertified` | true via `gate_nav_cognitive` |
| support/intervention links | true for both intervention-support pairs |
| higher-priority obstruction cases | all false |
| predicted status | `cognitive` |

### `claim_pkg_passive_non_cognitive`

| field | predicted value |
| --- | --- |
| claim ref | `CognitiveClaimRef.package(pkg_passive_memory, C_memory)` |
| carried status record | `status_pkg_passive_non_cognitive`, status `non_cognitive` |
| schedule trap | false |
| scaffolding | false (provenance carried) |
| structural path only | false |
| decodable correlate | false |
| repair without gate | false |
| gate without repair | false |
| cognitive | false |
| predicted status | `non_cognitive` |

### `claim_pkg_schedule_trap`

| field | predicted value |
| --- | --- |
| claim ref | `CognitiveClaimRef.package(pkg_schedule_trap, C_nav)` |
| carried status record | `status_pkg_schedule_trap`, status `schedule_trap` |
| schedule record | `schedule_nav_exogenous` |
| schedule explains support change | true |
| accepted top-down gate inventory | empty (`NoAcceptedTopDownGateFor = true`) |
| `ScheduleTrapHolds` | true |
| `CognitiveHolds` under same complete status | false |
| predicted status | `schedule_trap` |

### `claim_pkg_external_scaffold`

| field | predicted value |
| --- | --- |
| claim ref | `CognitiveClaimRef.package(pkg_external_scaffold, C_nav)` |
| carried status record | `status_pkg_external_scaffold`, status `scaffolding` |
| package class linked | true |
| complete provenance inventory | empty (`NoCarriedPackageProvenanceFor = true`) |
| schedule trap | false |
| predicted status | `scaffolding` |

### `claim_pkg_structural_path`

| field | predicted value |
| --- | --- |
| claim ref | `CognitiveClaimRef.package(pkg_structural_path, C_nav)` |
| carried status record | `status_pkg_structural_path`, status `structural_path_only` |
| structural channel | `tdc_structural_only` |
| `StructDown` | true |
| `TopDownChannelClaimStatus` | `ClaimStatus.blocked` |
| support difference | true |
| schedule/scaffolding higher priorities | false |
| predicted status | `structural_path_only` |

### `claim_pkg_decodable`

| field | predicted value |
| --- | --- |
| claim ref | `CognitiveClaimRef.package(pkg_decodable, C_memory)` |
| carried status record | `status_pkg_decodable`, status `decodable_correlate` |
| readout | `readout_decodable` |
| `ctx.decodesPackage` | true |
| accepted top-down gate inventory | empty (`gatingAblated = true`) |
| higher-priority schedule/scaffolding/structural cases | false |
| `CognitiveHolds` under same complete status | false |
| predicted status | `decodable_correlate` |

### `claim_pkg_repair_no_gate`

| field | predicted value |
| --- | --- |
| claim ref | `CognitiveClaimRef.package(pkg_repair_no_gate, C_nav)` |
| carried status record | `status_pkg_repair_no_gate`, status `repair_without_gate` |
| repair descent | true via `desc_repair_no_gate` |
| accepted top-down gate inventory | empty |
| decodable correlate | false |
| predicted status | `repair_without_gate` |

### `claim_pkg_gate_no_repair`

| field | predicted value |
| --- | --- |
| claim ref | `CognitiveClaimRef.package(pkg_gate_no_repair, C_nav)` |
| carried status record | `status_pkg_gate_no_repair`, status `gate_without_repair` |
| top-down gate | true via `gate_gate_no_repair` |
| complete repair inventory | empty (`NoPackageRepairDescentFor = true`) |
| repair without gate | false |
| predicted status | `gate_without_repair` |

## 4. Registered E10.1 Intention Scenarios

### `claim_intention_clean`

| field | predicted value |
| --- | --- |
| claim ref | `IntentionClaimRef.theta(theta_intention, T_plan)` |
| carried status record | `status_intention_clean`, status `intention` |
| restriction | `restrict_intention` |
| in advance | true (`2 < 5`) |
| strict support restriction | true (`{act1} proper-subset {act0,act1,act2}`) |
| `certifiedRestrictionLinked` | true (`gate_intention.support1/2` are the restriction's unrestricted/restricted supports) |
| future probes coherent | true for `probe_plan_ok_1`, `probe_plan_ok_2` |
| predicted status | `intention` |

### `claim_intention_neutral`

| field | predicted value |
| --- | --- |
| claim ref | `IntentionClaimRef.theta(theta_neutral, T_plan)` |
| carried status record | `status_intention_neutral`, status `not_intention` |
| post-hoc witness | false |
| approximate support defect | false |
| target-incoherent defect | false |
| positive intention evidence | false |
| predicted status | `not_intention` |

### `claim_intention_posthoc`

| field | predicted value |
| --- | --- |
| claim ref | `IntentionClaimRef.theta(theta_posthoc, T_plan)` |
| carried status record | `status_intention_posthoc`, status `post_hoc_intention` |
| restriction | `restrict_posthoc` |
| in advance | false (`8 < 5` is false) |
| `PostHocIntentionHolds` | true |
| `IntentionHolds` under same complete status | false |
| predicted status | `post_hoc_intention` |

### `claim_intention_approximate`

| field | predicted value |
| --- | --- |
| claim ref | `IntentionClaimRef.theta(theta_approx, T_plan)` |
| carried status record | `status_intention_approximate`, status `approximate_support_defect` |
| restriction | `restrict_approx` |
| approximate support restriction | true |
| exact strict subset | false |
| post-hoc higher priority | false |
| predicted status | `approximate_support_defect` |

### `claim_intention_target_incoherent`

| field | predicted value |
| --- | --- |
| claim ref | `IntentionClaimRef.theta(theta_incoherent, T_plan)` |
| carried status record | `status_intention_target_incoherent`, status `target_incoherent_restriction` |
| restriction | `restrict_incoherent` |
| failed probe | `probe_plan_bad` |
| target coherent under failed probe | false |
| post-hoc / approximate higher priorities | false |
| predicted status | `target_incoherent_restriction` |

## 5. Registered E10.2 Goal Scenarios

### `claim_goal_clean`

| field | predicted value |
| --- | --- |
| claim ref | `GoalClaimRef.theta(theta_goal, T_plan)` |
| carried status record | `status_goal_clean`, status `goal` |
| target quotient | `target_goal_plan` |
| at least two distinct routes | true (`route_goal_a != route_goal_b`) |
| every route evaluated | true (`eval_goal_a`, `eval_goal_b`) |
| every evaluation targets selected quotient | true |
| route selection persists | true |
| reward proxy higher priority | false |
| route unstable higher priority | false |
| predicted status | `goal` |

### `claim_goal_neutral`

| field | predicted value |
| --- | --- |
| claim ref | `GoalClaimRef.theta(theta_not_goal, T_plan)` |
| carried status record | `status_goal_neutral`, status `not_goal` |
| reward proxy only | false |
| route unstable | false |
| positive goal evidence | false |
| predicted status | `not_goal` |

### `claim_goal_reward_proxy_only`

| field | predicted value |
| --- | --- |
| claim ref | `GoalClaimRef.theta(theta_reward_proxy, T_plan)` |
| carried status record | `status_goal_reward_proxy_only`, status `reward_proxy_only` |
| reward proxy | `reward_proxy_only_plan`, proxy value `7/10` |
| proxy explains selection | true |
| route persistence inventory | empty (`NoRoutePersistenceFor = true`) |
| `RewardProxyOnlyHolds` | true |
| `GoalHolds` under same complete status | false |
| predicted status | `reward_proxy_only` |

### `claim_goal_route_unstable`

| field | predicted value |
| --- | --- |
| claim ref | `GoalClaimRef.theta(theta_route_unstable, T_plan)` |
| carried status record | `status_goal_route_unstable`, status `route_unstable` |
| target quotient | `target_unstable_plan` |
| at least two distinct routes | true |
| every route evaluated | true |
| route selection persists | false |
| reward proxy higher priority | false |
| predicted status | `route_unstable` |

## 6. Null and Control Predictions

### `ctrl_support_for_intervention_linkage`

| field | predicted value |
| --- | --- |
| shared context | `ctx_cog` |
| good link | `supportForIntervention(supp_nav_val0, int_nav_value0) = true` |
| bad link | `supportForIntervention(supp_wrong_for_intervention, int_nav_value0) = false` |
| bad gate | `channelCertifiesKernelComparison(tdc_accept_nav, match_nav, supp_wrong_for_intervention, supp_nav_val1) = false` |
| registered prediction | the support/intervention comparator is load-bearing and data-linked |

### `ctrl_main_claim_scoping`

| field | predicted value |
| --- | --- |
| status record | `status_pkg_nav_cognitive` |
| matches `CognitiveClaimRef.package(pkg_nav_cognitive, C_nav)` | true |
| matches `CognitiveClaimRef.package(pkg_nav_cognitive, C_other)` | false |
| wrong-class claim | `CognitiveClaimRef.package(pkg_other_repair, C_nav)` |
| wrong-class carried status record | `status_wrong_class_non_cognitive`, status `non_cognitive` |
| real repair available for package's declared class | `desc_other_real` is valid for `C_other` |
| valid `PackageRepairDescent` for wrong `C_nav` claim | false, because Lean requires `package.declaredClass = challengeClass` |
| higher-priority cases for wrong-class claim | all false |
| predicted status for wrong-class claim | `non_cognitive` |
| registered prediction | `CognitiveStatusRecordMatchesClaim` and repair descent are per package/class, not global |

### `ctrl_decodable_priority_blocks_cognitive`

| field | predicted value |
| --- | --- |
| claim ref | `CognitiveClaimRef.package(pkg_priority_decodable, C_memory)` |
| carried decodability readout | `readout_priority_decodable`, true |
| repair descent | true via `desc_priority_decodable` |
| accepted top-down gate | false (`declaredAcceptedChannels = []`) |
| predicted status | `decodable_correlate` |
| theorem-facing negation | `E10_DecodableCorrelate` gives `¬ CognitiveHolds` under scoped completeness |

### `ctrl_schedule_priority_blocks_cognitive`

| field | predicted value |
| --- | --- |
| claim ref | `CognitiveClaimRef.package(pkg_priority_schedule, C_nav)` |
| schedule trap evidence | true via `schedule_nav_exogenous` |
| raw repair descent | true via `desc_priority_schedule` |
| accepted top-down gate | false |
| predicted status | `schedule_trap` |
| theorem-facing negation | `E10_ScheduleTrapNull` gives `¬ CognitiveHolds` under scoped completeness |

### `ctrl_post_hoc_priority_blocks_intention`

| field | predicted value |
| --- | --- |
| claim ref | `IntentionClaimRef.theta(theta_priority_posthoc, T_plan)` |
| carried restriction | `restrict_priority_posthoc` |
| strict support subset | true |
| timing | post-hoc (`9 < 5` is false) |
| predicted status | `post_hoc_intention` |
| theorem-facing negation | `E10_1_PostHocIntentionFalsifier` gives `¬ IntentionHolds` under scoped completeness |

### `ctrl_reward_proxy_priority_blocks_goal`

| field | predicted value |
| --- | --- |
| claim ref | `GoalClaimRef.theta(theta_priority_reward, T_plan)` |
| target quotient | `target_priority_reward_plan` |
| reward proxy | `reward_priority_plan`, proxy value `9/10` |
| route persistence inventory | empty |
| predicted status | `reward_proxy_only` |
| theorem-facing negation | `E10_2_RewardProxyNotGoal` gives `¬ GoalHolds` under scoped completeness |

### `ctrl_every_route_evaluated_universal`

| field | predicted value |
| --- | --- |
| claim ref | `GoalClaimRef.theta(theta_missing_eval, T_plan)` |
| target quotient | `target_missing_eval_plan` |
| declared routes | `[route_missing_a, route_missing_b]` |
| carried evaluations | `[eval_missing_a]` |
| at least two distinct routes | true |
| `everyRouteEvaluated` | false because `route_missing_b` has no `RouteSubstitutionEvaluation` witness |
| route unstable witness | false (also requires every route evaluated) |
| goal evidence | false |
| predicted status | `not_goal` |

### `ctrl_uncarried_intention_rejected`

| field | predicted value |
| --- | --- |
| claim ref | `IntentionClaimRef.theta(theta_uncarried_intention, T_plan)` |
| otherwise-clean restriction | `restrict_uncarried_intention`, strict subset true and in advance |
| future probes coherent | true |
| top-down restriction-looking data | supports match `supp_action_unrestricted` / `supp_action_restricted` |
| theta provenance carried | false |
| post-hoc / approximate / target-incoherent higher priorities | false |
| positive `IntentionCase` | false because `IntentionEvidence.provenance` is unconstructible |
| predicted status | `not_intention` |

### `ctrl_uncarried_goal_rejected`

| field | predicted value |
| --- | --- |
| claim ref | `GoalClaimRef.theta(theta_uncarried_goal, T_plan)` |
| otherwise-clean target quotient | `target_uncarried_goal_plan`, carried |
| otherwise-clean routes | `[route_uncarried_goal_a, route_uncarried_goal_b]` |
| every route evaluated | true |
| route selection persists | true |
| theta provenance carried | false |
| reward proxy / route-unstable higher priorities | false |
| positive `GoalCase` | false because `GoalEvidence.provenance` is unconstructible |
| predicted status | `not_goal` |

### Case Enumeration item 18 note

Case Enumeration item 18 is intentionally not a separate Round B registered
comparison. It is an interaction-status/E11-forward-obligation note:
E10.1 classifies intention through the direct FIII support-restriction
apparatus, while the bridge to E11's planning/execution vocabulary remains
open for the later interaction-matrix check. This matches the six-field
document's treatment of item 18 as a design-level compatibility note, not as
a separate Lean status branch.

## 7. Registered Comparison List

Round B must emit one `PASS`/`FAIL` row for each of these 26 comparisons:

| # | registered comparison | expected value |
| ---: | --- | --- |
| 1 | `claim_pkg_nav_cognitive.status` | `cognitive` |
| 2 | `claim_pkg_passive_non_cognitive.status` | `non_cognitive` |
| 3 | `claim_pkg_schedule_trap.status` | `schedule_trap`; `CognitiveHolds = false` under scoped completeness |
| 4 | `claim_pkg_external_scaffold.status` | `scaffolding` |
| 5 | `claim_pkg_structural_path.status` | `structural_path_only` |
| 6 | `claim_pkg_decodable.status` | `decodable_correlate`; `CognitiveHolds = false` under scoped completeness |
| 7 | `claim_pkg_repair_no_gate.status` | `repair_without_gate` |
| 8 | `claim_pkg_gate_no_repair.status` | `gate_without_repair` |
| 9 | `claim_intention_clean.status` | `intention` |
| 10 | `claim_intention_neutral.status` | `not_intention` |
| 11 | `claim_intention_posthoc.status` | `post_hoc_intention`; `IntentionHolds = false` under scoped completeness |
| 12 | `claim_intention_approximate.status` | `approximate_support_defect` |
| 13 | `claim_intention_target_incoherent.status` | `target_incoherent_restriction` |
| 14 | `claim_goal_clean.status` | `goal` |
| 15 | `claim_goal_neutral.status` | `not_goal` |
| 16 | `claim_goal_reward_proxy_only.status` | `reward_proxy_only`; `GoalHolds = false` under scoped completeness |
| 17 | `claim_goal_route_unstable.status` | `route_unstable` |
| 18 | `ctrl_support_for_intervention_linkage` | good support link true; wrong support link false; bad gate false |
| 19 | `ctrl_main_claim_scoping` | exact package/class scoping holds; wrong-class real `C_other` repair queried under `C_nav` yields `non_cognitive` |
| 20 | `ctrl_decodable_priority_blocks_cognitive.status` | `decodable_correlate` |
| 21 | `ctrl_schedule_priority_blocks_cognitive.status` | `schedule_trap` |
| 22 | `ctrl_post_hoc_priority_blocks_intention.status` | `post_hoc_intention` |
| 23 | `ctrl_reward_proxy_priority_blocks_goal.status` | `reward_proxy_only` |
| 24 | `ctrl_every_route_evaluated_universal.status` | `not_goal`; universal route evaluation check false |
| 25 | `ctrl_uncarried_intention_rejected.status` | `not_intention`; otherwise-clean restriction cannot bypass missing theta provenance |
| 26 | `ctrl_uncarried_goal_rejected.status` | `not_goal`; otherwise-clean route persistence cannot bypass missing theta provenance |

## 8. Falsification Conditions

1. `claim_pkg_nav_cognitive` is falsified if package provenance,
   target-owned Delta reduction, accepted FIII top-down channel, carried
   interventions/supports/channel, or support-to-intervention linkage is
   skipped; it is also falsified if the status is not exactly `cognitive`.
2. `claim_pkg_passive_non_cognitive` is falsified if passive carried data is
   upgraded to cognition without repair descent and top-down gate evidence, or
   if status uniqueness is applied globally instead of per claim.
3. `claim_pkg_schedule_trap` is falsified if exogenous schedule evidence is
   accepted from a bare flag, if `NoAcceptedTopDownGateFor` is ignored, or if
   the mandatory schedule-trap obstruction does not block cognition under the
   scoped complete status.
4. `claim_pkg_external_scaffold` is falsified if missing D3 provenance can
   enter the positive cognitive branch.
5. `claim_pkg_structural_path` is falsified if `StructDown` plus support
   difference is treated as an accepted top-down channel despite
   `TopDownChannelClaimStatus = ClaimStatus.blocked`.
6. `claim_pkg_decodable` is falsified if theorist decodability with ablated
   top-down gating is classified cognitive, or if the decodable readout is not
   linked to the queried package/class.
7. `claim_pkg_repair_no_gate` is falsified if repair descent alone is enough
   for cognition without two carried interventions, matched controls, linked
   supports, and an accepted channel.
8. `claim_pkg_gate_no_repair` is falsified if top-down gating alone is enough
   for cognition without a package-owned Delta reduction.
9. `claim_intention_clean` is falsified if `certifiedRestrictionLinked` is not
   checked, if the restriction is not before outcome, if support strictness is
   not computed from support sets, or if future probes are not carried and
   target-coherent.
10. `claim_intention_neutral` is falsified if the catch-all status is computed
    without negating the four higher-priority intention cases for the same
    `IntentionClaimRef`.
11. `claim_intention_posthoc` is falsified if post-hoc timing is ignored or
    if strict support restriction after the outcome is accepted as intention.
12. `claim_intention_approximate` is falsified if approximate/stochastic
    restriction is accepted as exact strict support inclusion.
13. `claim_intention_target_incoherent` is falsified if a failed carried
    future probe does not produce the target-incoherent defect status.
14. `claim_goal_clean` is falsified if fewer than two distinct routes are
    accepted, if route evaluations are not linked to the selected target
    quotient, if `deltaEvaluatedAgainstTarget` is ignored, or if persistence is
    not computed from the route-evaluation list.
15. `claim_goal_neutral` is falsified if goal status is assigned without
    target quotient selection plus route-substitution persistence.
16. `claim_goal_reward_proxy_only` is falsified if a reward scalar proxy is
    treated as a goal without route persistence, or if the mandatory
    reward-proxy obstruction does not block `GoalHolds`.
17. `claim_goal_route_unstable` is falsified if two evaluated routes with
    failed persistence are accepted as a goal.
18. `ctrl_support_for_intervention_linkage` is falsified if
    `supportForIntervention` or `channelCertifiesKernelComparison` is a
    per-instance trivially true predicate rather than the shared
    `ctx_cog` computation over real support/intervention records.
19. `ctrl_main_claim_scoping` is falsified if
    `CognitiveStatusRecordMatchesClaim` ignores package identity or challenge
    class, if a valid `C_other` descent for `pkg_other_repair` can be credited
    to the wrong `C_nav` claim, or if `CompleteCognitiveStatus.statusUnique`
    is global.
20. `ctrl_decodable_priority_blocks_cognitive` is falsified if decodability
    plus raw repair-looking data can bypass the ablated-gate obstruction.
21. `ctrl_schedule_priority_blocks_cognitive` is falsified if schedule-trap
    evidence is lower priority than repair-looking evidence.
22. `ctrl_post_hoc_priority_blocks_intention` is falsified if post-hoc support
    restriction can classify as intention because strict support inclusion is
    present.
23. `ctrl_reward_proxy_priority_blocks_goal` is falsified if reward-proxy
    evidence can classify as goal without route persistence.
24. `ctrl_every_route_evaluated_universal` is falsified if Round B implements
    route coverage existentially; `route_missing_b` must force
    `everyRouteEvaluated = false`.
25. `ctrl_uncarried_intention_rejected` is falsified if otherwise-clean
    support restriction, future probes, and top-down-looking data can enter
    `IntentionCase` without carried theta provenance.
26. `ctrl_uncarried_goal_rejected` is falsified if otherwise-clean target
    quotient selection and route persistence can enter `GoalCase` without
    carried theta provenance.
27. The future sweep is falsified if any registered row is produced by a
    lookup table instead of evaluating carried-source records, Delta split
    sets, FIII channel records, shared context comparators, claim-scoped
    occurrence predicates, and priority-normalized case predicates.

## 9. Round B Implementation Guard

Round B must compute all certified boolean/Prop-mirroring facts from fixture
data:

```text
PackageCarriedProvenance
PackageRepairDescent
TopDownKernelGateCertified
CompleteKernelGateInventory / NoAcceptedTopDownGateFor
CompletePackageRepairInventory / NoPackageRepairDescentFor
CognitiveStatusRecordMatchesClaim
CognitiveStatusOccurrenceFor
SupportRestrictionInAdvance
TargetCoherenceUnderFutureProbes
IntentionStatusRecordMatchesClaim
GoalTargetSelection
RouteSubstitutionEvaluation
RouteSubstitutionPersistenceCertified
CompleteRoutePersistenceInventory / NoRoutePersistenceFor
GoalStatusRecordMatchesClaim
```

No predicate may be implemented as an ignored-argument lambda or stored status
flag. The Round B classifier must be an explicit priority chain matching the
Lean case order:

```text
schedule_trap > scaffolding > structural_path_only >
decodable_correlate > repair_without_gate > gate_without_repair >
cognitive > non_cognitive

post_hoc_intention > approximate_support_defect >
target_incoherent_restriction > intention > not_intention

reward_proxy_only > route_unstable > goal > not_goal
```

The registered comparison count is 26.

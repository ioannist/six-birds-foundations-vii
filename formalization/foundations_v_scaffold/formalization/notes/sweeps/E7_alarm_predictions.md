# E7 Alarm Predictions

This is the pre-registered prediction artifact for the E7 toy-laboratory
probe. It is intentionally written before any E7 sweep implementation exists.
Round B should implement the sweep against this document, not redesign the
configuration after seeing results.

No experiment has been run for this artifact. All exact quantities below are
specified over `fractions.Fraction`. This E7 Round A instance is fully
deterministic: no random seed, stochastic simulation, or hash-audited float
branch is required.

## 1. Toy-Lab Configuration

### Repair-World Hazard Carrier

The E7 sweep specializes Repair-World to a one-hidden-factor hazard process.
The carrier uses `RepairWorldState` and `repair_world_viability_kernel` /
`repair_world_viability_kernel_history` from
`lab/sixbirds_foundations_v/worlds/repair_world.py`. The state id used by the
sweep may be a host registry key, but the external coordinate `state.y` is the
following finite code:

| state id | meaning | safe? |
| --- | --- | --- |
| `0` | quiescent/pre-hazard state `S0` | yes |
| `1` | hazard age 1, residual level `H=1` | yes |
| `2` | hazard age 2, residual level `H=2` | yes |
| `3` | hazard age 3, residual level `H=3` | yes |
| `4` | currentized/recovered state `C` | yes |
| `5` | unsafe absorbing state `D` | no |

Without currentization, the deterministic external progression is:

```text
0 -> 1 -> 2 -> 3 -> 5 -> 5
```

Currentization from any hazard state `{1,2,3}` goes to `4`; `4` stays at `4`.
The safe predicate for the viability kernel is `state.y != 5`.

### Xi Blind-Spot Fixture

The hazard factor uses a one-dimensional Xi fixture:

```python
F = Fraction

C_h = ((F(1),),)
L_blind = ((F(0),),)
KLLdagger_blind = ((F(0),),)
Omega = ((F(0),),)
z_h = (F(1),)
```

At time `t` after hazard onset, the declared target/readout row is:

```python
D_t = ((H_t,),)
```

where `H_t in {0,1,2,3}` is the residual level in the table above. With this
fixture,

```text
ResidualMatrix(t) = adequacyResidual(C_h, L_blind, D_t, KLLdagger_blind)
                  = ((H_t^2),)
Delta_Xi(t)       = ResidualMatrix(t) - Omega
BlindSpotWitness  = quad(Delta_Xi(t), z_h) > 0
                  = H_t^2 > 0.
```

Thus the first genuine blind-spot crossing occurs at hazard age 1, state `1`,
with exact excess `1`.

### Viability Coupling

The declared horizon is:

```text
horizon = 3 steps after first positive witness.
```

For the canonical hazard path, the first positive witness is at state `1`.
If no currentization occurs before the transition from state `3`, the next
state is unsafe absorbing state `5`. Therefore:

```text
ViabilityCoupled(state 1, z_h, horizon=3) = True
ViabilityProbeDescends without currentization = False
```

This is the concrete Python-side F19 instantiation: the viability kernel is
computed by `repair_world_viability_kernel`, not by a parallel viability
definition.

### Standing Access Policy and Preemption

The standing E6/E9 policy has one ordinary monitoring/attention move `O` and
one hazard-currentization move `A`.

```text
O: discharge = 1,   cost = 1, AccessMoveRatio = 1
A: discharge = 1/2, cost = 1, AccessMoveRatio = 1/2
```

Under the **in-policy-only ablation**, `A` must compete inside the standing
policy, so `O` is selected over `A` whenever both are available. Therefore the
hazard is not currentized by ordinary access competition.

Under the **preemption-enabled policy**, a genuine
`BlindSpotWitness + ViabilityCoupled` event produces an
`AlarmConstraintRewrite`:

```text
preConstraintSet.preemptedWitness  = None
postConstraintSet.preemptedWitness = z_h
postConstraintSet.witnessExposureAdmissible(z_h) = True
postConstraintSet != preConstraintSet
```

The rewritten constraint set forces `A` before ordinary in-policy comparison.
This is the registered E7 difference: alarm changes the constraint set rather
than winning by `AccessMoveRatio`.

### Monitoring Budget Schedule

The monitoring budget `B_mon` controls the earliest scheduled Xi residual
check. It does not change the hazard statistics.

| `B_mon` | check times | first positive witness time | currentization time | latency |
| ---: | --- | ---: | ---: | ---: |
| `0` | none | `1` | none | none |
| `1` | `{3}` | `1` | `3` | `2` |
| `2` | `{2}` | `1` | `2` | `1` |
| `3` | `{1}` | `1` | `1` | `0` |

For `B_mon=0`, no alarm is currentized and the trajectory reaches unsafe state
`5`. For `B_mon in {1,2,3}`, currentization occurs before the unsafe transition,
so the trajectory reaches recovered state `4`.

## 2. Registered Predictions

### Detection Latency vs Monitoring Budget

For the canonical hazard path `0 -> 1 -> 2 -> 3 -> 5`, the predicted
currentization/latency table is exactly:

| `B_mon` | currentization? | currentization state/time | latency from first witness | final state by time 5 |
| ---: | --- | ---: | ---: | ---: |
| `0` | no | none | none | `5` |
| `1` | yes | `3` | `2` | `4` |
| `2` | yes | `2` | `1` | `4` |
| `3` | yes | `1` | `0` | `4` |

Registered prediction: latency is strictly decreasing over the monitored
budgets `1,2,3`:

```text
2 > 1 > 0.
```

### Policy-Relative Trajectory Outcomes Under Preemption vs In-Policy Competition

The standard `repair_world_viability_kernel` / `viability_kernel` is not the
registered comparator for this policy contrast. It is an existential greatest
fixed point: a safe state remains in the kernel when some feasible action keeps
it safe. The in-policy-only ablation keeps hazard-currentization move `A`
feasible; it merely loses to ordinary move `O` under the standing
`AccessMoveRatio`. Therefore, with `A` feasible in both variants, the standard
existential kernel sanity check is:

```text
K_existential_preempt   = {0,1,2,3,4}
K_existential_in_policy = {0,1,2,3,4}
```

This equality is expected and is not the E7 preemption claim. The E7 claim is a
policy-realized trajectory claim: which action the policy actually selects when
the hazard event occurs.

The finite matched hazard sweep has four configurations:

| config | onset state/time | severity path | first witness | deadline unsafe transition |
| --- | ---: | --- | ---: | ---: |
| `N0` | none | no hazard | none | none |
| `H1` | `1` | `1,2,3` | `1` | after `3` |
| `H2` | `2` | `1,2,3` | `2` | after `4` |
| `H3` | `3` | `1,2,3` | `3` | after `5` |

The sweep uses identical hazard configurations for both policies and records
actual forward trajectories under each policy's action-selection rule.
Predicted policy-realized survival/death counts:

| policy | survived configs | died configs |
| --- | ---: | ---: |
| preemption-enabled | `4` | `0` |
| in-policy-only | `1` | `3` |

The sole in-policy survival is `N0`, where there is no hazard. In `H1/H2/H3`,
the in-policy-only system never rewrites the constraint set, keeps choosing
ordinary move `O`, and reaches unsafe state `5`.

### Preemption vs In-Policy Matched Outcomes

For the three genuine hazard configurations:

```text
preemption-enabled survival count = 3/3
in-policy-only survival count     = 0/3
strict advantage                  = 3 configs
```

This is the registered version of THEOREMS.md's claim: matched systems with
in-policy-only alarm die more often under identical hazard statistics.

### False-Alarm / Missed-Alarm Threshold Census

The threshold sweep uses three genuine viability-coupled hazard events and two
non-coupled protocol-artifact events:

```text
genuine coupled residuals:      {1, 2, 3}
non-coupled artifact residuals: {1, 2}
```

For threshold `theta`, the sweep treats a residual as a detected positive
witness iff `residual > theta`. The lawful E7 policy currentizes only detected
genuine coupled events. Detected non-coupled artifacts are statused as
`lawful_discount(protocol_artifact)`, not currentized.

Registered lawful-policy census:

| `theta` | true currentizations | lawful artifact discounts | false alarms | missed genuine alarms |
| ---: | ---: | ---: | ---: | ---: |
| `0` | `3` | `2` | `0` | `0` |
| `1` | `2` | `1` | `0` | `1` |
| `2` | `1` | `0` | `0` | `2` |
| `3` | `0` | `0` | `0` | `3` |

For comparison, the no-audit control currentizes every detected positive
witness, coupled or not:

| `theta` | no-audit false alarms | no-audit missed genuine alarms |
| ---: | ---: | ---: |
| `0` | `2` | `0` |
| `1` | `1` | `1` |
| `2` | `0` | `2` |
| `3` | `0` | `3` |

### Protocol-Artifact Control

The protocol-artifact control is the non-coupled residual event:

```text
residual = 2
BlindSpotWitness = True when theta < 2
ViabilityCoupled = False
```

Registered prediction:

```text
theta = 0 or 1:
  Lawful E7 disposition = lawful_discount(protocol_artifact)
  CurrentizationHolds   = False
  FalseAlarm count      = 0

theta = 2 or 3:
  no disposition required because residual > theta is false.
```

This directly exercises E7.md's Nonclaim: a positive Xi residual alone is not an
alarm without viability coupling.

## 3. Falsification Conditions

The following outcomes falsify the corresponding registered predictions.

1. Detection latency is falsified if, under the specified check schedules,
   `B_mon=1,2,3` do not currentize at states/times `3,2,1` respectively, or if
   the latencies are not exactly `2,1,0`.

2. The no-monitoring case is falsified if `B_mon=0` currentizes, or if it does
   not reach unsafe absorbing state `5` by time `5`.

3. The standard existential-kernel sanity check is falsified if, with
   hazard-currentization action `A` feasible in both variants,
   `repair_world_viability_kernel` does not return exactly `{0,1,2,3,4}` for
   both variants. This equality does not falsify E7's preemption claim; it is
   expected because the kernel is existential over feasible actions.

4. The matched-policy survival prediction is falsified if the
   preemption-enabled policy survives fewer than `4/4` configurations, if the
   in-policy-only policy survives more than `1/4`, or if the strict advantage
   over genuine hazard configurations is not exactly `3`.

5. The preemption-vs-competition claim is falsified if the in-policy-only
   variant survives at least as often as the preemption-enabled variant over the
   four matched configurations, or if it survives any of `H1/H2/H3` without a
   constraint-set rewrite.

6. The lawful false-alarm/missed-alarm census is falsified if the lawful policy
   has any false alarms at any `theta in {0,1,2,3}`, if its missed-genuine
   counts are not exactly `0,1,2,3`, or if its artifact-discount counts are not
   exactly `2,1,0,0`.

7. The no-audit control is falsified if its false-alarm counts are not exactly
   `2,1,0,0` at `theta = 0,1,2,3`, respectively.

8. The protocol-artifact control is falsified if a non-coupled residual
   `2 > theta` for `theta in {0,1}` is currentized as a genuine alarm rather
   than statused as `lawful_discount(protocol_artifact)`, or if it contributes
   to `CurrentizationHolds`.

9. The Xi witness fixture is falsified if Round B's direct xi computation does
   not report `ResidualMatrix(t) = ((H_t^2),)` and
   `quad(Delta_Xi(t), z_h) = H_t^2` for `H_t in {0,1,2,3}`.

10. The E7 preemption signature is falsified if any counted currentization in
    the preemption-enabled policy leaves `preConstraintSet = postConstraintSet`,
    fails to set `postConstraintSet.preemptedWitness = z_h`, or succeeds only
    by winning the standing `AccessMoveRatio` comparison inside the old
    constraint set.

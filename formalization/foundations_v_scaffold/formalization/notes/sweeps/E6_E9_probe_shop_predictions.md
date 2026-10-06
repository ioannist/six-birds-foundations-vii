# E6+E9 Probe-Shop Predictions

This is the pre-registered prediction artifact for the E6+E9 toy-laboratory
probe. It is intentionally written before any sweep implementation exists.
Round B should implement the sweep against this document, not redesign the
configuration after seeing results.

No experiment has been run for this artifact. All exact quantities below are
specified over `fractions.Fraction` unless explicitly marked as the
hash-audited numerical salience branch.

## 1. Toy-Lab Configuration

### Base Sanity Fixture

The sweep keeps the already-verified two-factor fixture as a saturation-null
sanity check:

```python
F = Fraction

C_base = ((F(1), F(0)), (F(0), F(2)))
L_base = ((F(1), F(1)),)
D_base_1d = ((F(1), F(0)),)
KLLdagger_base = ((F(2, 3),),)
```

Registered baseline facts to preserve:

- `adequacyResidual(C_base, L_base, D_base_1d, KLLdagger_base) == ((F(1, 3),),)`.
- Repackaged probes `M=((F(2),F(2)),)` with `B=((F(2),),)` and
  `M=((F(1),F(1)),)` with `B=((F(1),),)` are same-family saturated:
  `conditionalCurrencyDM_L == zeroMat` and `is_same_family_saturated == True`.
- Strict one-row candidates `((F(0),F(1)),)`, `((F(1),F(0)),)`, and
  `((F(1),F(-1)),)` are not saturated and each discharges `F(1,3)` in this
  one-target fixture.

This fixture is a clean null check, but it is deliberately not the E6 allocation
sweep because the strict candidates have uniform discharge.

### Extended Probe-Shop Instance

The actual E6+E9 sweep uses three hidden factors and a two-owned-probe active
family. Hidden factor 3 is initially unowned, so it is available only through
acquisition candidates.

```python
C = (
    (F(1), F(0), F(0)),
    (F(0), F(1), F(0)),
    (F(0), F(0), F(1)),
)

L_owned = (
    (F(1), F(0), F(0)),  # owned probe A
    (F(0), F(1), F(0)),  # owned probe B
)

D = (
    (F(3), F(0), F(0)),
    (F(0), F(2), F(0)),
    (F(0), F(0), F(1, 2)),
)
```

The target energies are therefore `A: 9`, `B: 4`, and `C: 1/4`. The active
family for allocation has support `{A, B}`. The catalog also contains strict
acquisition candidates with a factor-3 component and repackaged candidates in
the span of `{A, B}`.

For allocation weights `w = (w_A, w_B)`, Round B should use the exact host
response

```python
rho(t) = t / (1 + t)
KLLdagger_alloc(w) = (
    (rho(w_A), F(0)),
    (F(0), rho(w_B)),
)
Residual(w) = adequacyResidual(C, L_owned, D, KLLdagger_alloc(w))
```

This is a declared finite host surface using the xi module's explicit
`KLLdagger` parameter. It is not a claim that the toy lab has implemented a
general Moore-Penrose solver.

For this instance:

```text
trace(Residual(w)) = 9 * (1 - rho(w_A)) + 4 * (1 - rho(w_B)) + 1/4.
Discharge(w) = 9 * rho(w_A) + 4 * rho(w_B).
```

Allocation costs are `c_A = 1`, `c_B = 1`. Lawful allocation is capped at
`0 <= w_A <= 2`, `0 <= w_B <= 1`, so the maximum useful owned-exposure spend is
`3`.

For exact finite search, Round B should enumerate rational weights on the grid

```text
w_A in {0, 1/5, 2/5, ..., 2}
w_B in {0, 1/5, 2/5, ..., 1}
```

subject to `w_A + w_B <= B_alloc`. The registered KKT optima at the main binding
budgets are:

| `B_alloc` | predicted `w_A` | predicted `w_B` | exact marginal ratio `lambda_exp` |
| --- | ---: | ---: | ---: |
| `1` | `4/5` | `1/5` | `25/9` |
| `2` | `7/5` | `3/5` | `25/16` |
| `3` | `2` | `1` | `1` |

The exact marginal ratios above use
`MarginalDischarge_A(w) = 9 / (1 + w_A)^2` and
`MarginalDischarge_B(w) = 4 / (1 + w_B)^2`. Round B should also report finite
difference ratios using

```text
MD_delta_A(w) = 9 / ((1 + w_A) * (1 + w_A + delta))
MD_delta_B(w) = 4 / ((1 + w_B) * (1 + w_B + delta))
```

for feasible forward increments, and the analogous left finite difference at
the cap point `B_alloc = 3`. At `delta = 1/20`, the predicted finite-difference
ratios are:

| `B_alloc` | A ratio | B ratio | spread |
| --- | ---: | ---: | ---: |
| `1` | `100/37` | `8/3` | `4/111` |
| `2` | `75/49` | `50/33` | `25/1617` |
| `3` left-difference | `60/59` | `40/39` | `20/2301` |

The spread should shrink as `delta` is refined.

### Acquisition Catalog

E9 acquisition strictness is evaluated against the actual span of the owned
family. For that strictness check, Round B should use

```python
KLLdagger_span = (
    (F(1), F(0)),
    (F(0), F(1)),
)
```

not the damped allocation response `KLLdagger_alloc(w)`.

Repackaged, same-family-saturated candidates:

| candidate | matrix `M` | factor witness `B` | cost |
| --- | --- | --- | ---: |
| `A2` | `((F(2),F(0),F(0)),)` | `((F(2),F(0)),)` | `1/10` |
| `AB` | `((F(1),F(1),F(0)),)` | `((F(1),F(1)),)` | `1/10` |
| `B2` | `((F(0),F(2),F(0)),)` | `((F(0),F(2)),)` | `1/10` |

Strict candidates:

| candidate | matrix `M` | cost | predicted discharge | discharge per cost |
| --- | --- | ---: | ---: | ---: |
| `C` | `((F(0),F(0),F(1)),)` | `1` | `1/4` | `1/4` |
| `AC` | `((F(1),F(0),F(1)),)` | `2` | `1/4` | `1/8` |
| `BC` | `((F(0),F(1),F(1)),)` | `4` | `1/4` | `1/16` |

For the strict candidates, Round B should compute discharge with the xi
chain-rule contraction:

```text
traceMat(
  matMul(
    matMul(conditionalCurrencyDM_L(C, L_owned, D, M, KLLdagger_span),
           KMMLdagger),
    conditionalCurrencyMD_L(C, L_owned, D, M, KLLdagger_span)))
```

where `KMMLdagger = ((F(1),),)` for these one-row candidates. The prediction is
that each strict candidate discharges exactly the remaining factor-3 residual,
`1/4`, while the same-family candidates discharge `0` and are rejected by
`is_same_family_saturated`.

### Budget Sweep

The shared budget sweep is:

```text
B_total in {0, 1, 2, 3, 4}
```

Allocation and acquisition compete through the same access ratio geometry:

- owned allocation spends against `w_A + w_B`;
- acquisition spends its listed candidate cost;
- allocation is considered degraded when the owned allocation cannot reach
  `(w_A,w_B) = (2,1)`;
- acquisition activity means at least one strict acquisition is selected.

## 2. E6 Registered Predictions

### KKT-Ratio Convergence

At binding owned-allocation budgets `1`, `2`, and `3`, the exact finite search
should select the weight pairs registered above. For the selected probes A and
B, exact marginal discharge per cost should equal the listed `lambda_exp`:

```text
B_alloc = 1:  25/9
B_alloc = 2:  25/16
B_alloc = 3:  1
```

Finite-difference estimates at `delta in {1/5, 1/10, 1/20}` should converge
toward those exact ratios, with the A/B spread decreasing as `delta` decreases.
At `delta = 1/20`, the spreads should be the exact values in the configuration
table above.

Unselected lawful allocation alternatives on the finite grid should not have a
higher discharge-per-cost ratio than the selected frontier at the same budget.

### Slack Collapse

The owned allocation surface has no useful lawful exposure beyond
`w_A = 2`, `w_B = 1`, so the registered slack threshold is:

```text
B_alloc > 3.
```

For `B_alloc = 4`, predicted owned-allocation spend is still `3`, the exposure
budget is slack, and the reported multiplier or marginal-ratio floor for
additional owned allocation should collapse to `0`.

### Salience Tracking

The salience check uses

```text
Delta_Xi = Xi_C(D | L_w) - Omega
```

with `Omega = zeroMat(3,3)` for the first sweep. At the full owned allocation
`w_A = 2`, `w_B = 1`, the base target residual has diagonal magnitudes:

```text
A residual: 3
B residual: 2
C residual: 1/4
```

So the top direction should align with factor A.

The named perturbation is:

```python
D_shift_B = (
    (F(3), F(0), F(0)),
    (F(0), F(4), F(0)),
    (F(0), F(0), F(1, 2)),
)
```

Under the same allocation, the B residual becomes `8`, exceeding A's `3`.
The prediction is that the top salience direction shifts from factor A to
factor B, and the top magnitude shifts from `3` to `8`.

This branch should use the project's hash-audited numerical-run discipline
because eigenvectors/eigenvalues of rational matrices are generally not
rational. Round B should freeze the configuration, seed, and output hash for
this branch.

### Proxy-Attention Control

The negative-control policy is the fixed proxy allocation:

```text
w_proxy = (0, 1)
```

under `B_alloc = 3`. It allocates only to B and leaves the high-discharge A
direction unfunded, so it is deliberately uncorrelated with true
discharge-per-cost.

Held-out discharge prediction is registered with exact values at `B_alloc = 3`:

```text
KKT allocation (2,1): discharge = 8
proxy allocation (0,1): discharge = 2
```

The KKT allocation therefore has exactly `4x` the proxy discharge at this
budget.

Residual trace at `B_alloc = 3` is also registered exactly:

```text
KKT allocation (2,1): residual_trace = 21/4
proxy allocation (0,1): residual_trace = 45/4
```

The proxy residual is more than double the KKT residual.

The budget-perturbation check uses the already-registered allocation budgets
`B_alloc in {1,2,3,4}`. KKT realized discharge is predicted to strictly
increase as budget rises from `1` to `3`, then plateau at the lawful cap:

```text
B_alloc = 1: KKT discharge = 14/3
B_alloc = 2: KKT discharge = 27/4
B_alloc = 3: KKT discharge = 8
B_alloc = 4: KKT discharge = 8
```

The proxy realized discharge is predicted to remain exactly `2` at every
budget in `{1,2,3,4}`, because `w_proxy = (0,1)` never spends more than one
unit of budget. This budget-invariant response is the registered proxy failure:
it does not track the scarcity/opportunity signal that the KKT allocation
tracks.

## 3. E9 Registered Predictions

### Saturation-Null Census

Across the full shared budget sweep, `100%` of same-family-saturated candidates
`A2`, `AB`, and `B2` should be excluded from acquisition selection, regardless
of their low cost `1/10`.

The reason is structural, not numerical: they factor through `L_owned`, have
zero conditional currency, have zero xi contraction discharge, and therefore
fail `AcquisitionStrict`.

### Discharge-Per-Cost Frontier

For the strict candidates, the registered acquisition frontier is:

```text
C   : 1/4
AC  : 1/8
BC  : 1/16
```

Therefore the strict-candidate ranking must be:

```text
C > AC > BC.
```

No same-family candidate is allowed onto the frontier.

### Attention/Curiosity Arbitration Under Budget Tightening

The shared access policy compares allocation and acquisition moves by
discharge per cost over the same budget geometry.

Prediction over `B_total in {0,1,2,3,4}`:

- At `B_total = 4`, owned allocation reaches `(2,1)` with spend `3`, leaving one
  budget unit. The strict acquisition `C` is selected because its ratio is
  `1/4` and its cost is `1`.
- At `B_total = 3`, owned allocation still reaches `(2,1)`, but no budget
  remains for strict acquisition. Acquisition activity stops.
- At `B_total < 3`, owned allocation degrades below `(2,1)`.

Thus the falsifiable ordering is:

```text
acquisition halts at B_total = 3,
allocation degradation begins only for B_total < 3.
```

Purchases are therefore the first margin to close under budget tightening in
this registered instance.

## 4. Falsification Conditions

The following outcomes falsify the corresponding registered predictions.

1. KKT-ratio convergence is falsified if the exact finite search at
   `B_alloc in {1,2,3}` selects a different weight pair than registered, if the
   exact selected-probe ratios do not equal the listed `lambda_exp`, if
   finite-difference A/B spreads do not shrink as `delta` is refined, or if an
   unselected lawful allocation alternative has a higher ratio than the
   selected frontier at the same budget.

2. Slack collapse is falsified if `B_alloc > 3` produces positive additional
   owned-allocation spend, a positive marginal-ratio floor for further owned
   allocation, or a nonzero reported slack multiplier.

3. Salience tracking is falsified if the base configuration's top salience
   direction is not factor A, if `D_shift_B` does not move the top direction to
   factor B, if the reported top magnitudes do not match the registered `3` and
   `8` diagonal case, or if the numerical branch cannot reproduce its frozen
   configuration/hash.

4. Proxy-attention control is falsified if the proxy discharge is not exactly
   `2` at every `B_alloc in {1,2,3,4}`, if KKT discharge does not strictly
   increase from `14/3` at `B_alloc = 1` to `27/4` at `B_alloc = 2` to `8` at
   `B_alloc = 3`, if KKT discharge at `B_alloc = 4` is not the capped value
   `8`, if the `B_alloc = 3` discharges are not exactly `8` for KKT and `2` for
   the proxy, or if the `B_alloc = 3` residual traces are not exactly `21/4`
   for KKT and `45/4` for the proxy.

5. Saturation-null census is falsified if any same-family-saturated candidate
   is selected at any budget, if any such candidate has nonzero xi contraction
   discharge, or if `is_same_family_saturated` fails to classify the registered
   repackaged candidates as saturated with their listed `B` witnesses.

6. The acquisition frontier is falsified if the strict-candidate discharge
   values are not all `1/4`, if the cost-normalized ranking is not
   `C > AC > BC`, or if a lower-ranked candidate is selected while a
   higher-ranked feasible strict candidate is available at the same budget.

7. The attention/curiosity arbitration ordering is falsified if acquisition
   remains active at `B_total = 3` or lower, if allocation degrades at
   `B_total = 3` while acquisition is still possible, or if acquisition does
   not halt before allocation degradation begins as the budget is tightened.

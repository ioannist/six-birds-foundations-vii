# Active Foundations VII Lean project through FVII-SCI-04

This cumulative Lean project reuses the exact prior libraries under `../foundations_v_scaffold/lean/` and `../foundations_vi_scaffold/lean/` through Lake `srcDir` entries. Those imported trees are immutable.

The active VII-owned source now includes:

- `Core/` — typed kernel, identifiers, grades, ledgers, and protocol records;
- `Prior/` — narrow adapters and exact inherited declaration anchors;
- `Access/` — domain normal forms, admission/replay, provenance, reachability, and occupancy;
- `Contact/`, `Join/`, and `Residuals/` — contact, strict join, obstruction, certified non-interaction, and residuals;
- `Enablement/` — attribution, endogeny, birth, separation, and composition;
- `Dynamics/` — transmission/descent, confluence, holonomy/arrow, cross-time contact, residual flow, and primitive-algebra readiness;
- `NoGo/` — admission, join, and dynamics no-go fronts;
- `Models/Finite/` plus `Phase2` through `Phase4` — executable finite controls;
- `Trust/PrintAxioms*.lean` — theorem-level trust replay surfaces.

The Phase-4 source surface contributes 268 public declarations, including 135 theorems, lemmas, and corollaries. Static auditing finds no VII-owned `sorry`, proof-tactic `admit`, new axiom, opaque declaration, or unsafe declaration. This is not a substitute for kernel elaboration.

The current toolchain pin is:

```text
leanprover/lean4:v4.28.0
```

A compatible Lean 4 version may be selected by editing `lean-toolchain` and recording the change in Git. The cumulative external replay is:

```sh
bash scripts/run_fvii_sci04_external_lean.sh
```

It runs `lake clean`, `lake build`, all four finite executables, all theorem-level axiom queries, and the Phase-4 Lean/Python differential gate. Until that script succeeds, the truthful kernel status is external replay pending.

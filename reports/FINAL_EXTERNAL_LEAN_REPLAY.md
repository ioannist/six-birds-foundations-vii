# FVII-SCI-05 external Lean replay

**Kernel status:** `PASS`

The replay was executed locally in this repository: the public kernel build, all five finite
differentials, and the `#print axioms` capture for every public theorem have run and passed.
Kernel verification does not upgrade a scientific disposition -- a formalSchema is still a schema.

The cumulative replay contract is:

```sh
bash scripts/run_fvii_sci05_external_lean.sh
```

The script rebuilds all five finite layers, performs `lake clean` and `lake build`, runs every Lean finite executable, compares Lean and Python results, captures one `#print axioms` request per public theorem, records the actual toolchain, and reruns the strict final validator.

A compatible Lean 4 version may be selected by editing and committing `formalization/lean/lean-toolchain`. Until the replay succeeds, source-level proof grades, static trust reachability, and finite Python evidence remain distinct from kernel verification.

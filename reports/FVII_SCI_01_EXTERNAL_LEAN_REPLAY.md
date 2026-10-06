# External Lean replay directions for FVII-SCI-01

The delivered source targets `leanprover/lean4:v4.28.0`. The owner authorized changing `formalization/lean/lean-toolchain` to an available Lean 4 version when that is the least-resistance route, provided the version change is recorded and the full replay succeeds.

From the repository root run:

```bash
bash scripts/run_fvii_sci01_external_lean.sh
```

The script performs `lake clean`, `lake build`, executes all 51 Lean fixtures, compares Lean and Python outputs, captures every `#print axioms` result, records the toolchain/build status, removes transient `.lake` products, and runs the strict validator with `--require-lean-results`.

A successful replay must establish 51 shared fixture IDs, no missing IDs, no status/pass mismatches, successful kernel checking of the full public root, and a captured axiom report. Until then, the repository intentionally retains `NOT_RUN_LOCAL_ENVIRONMENT` rather than claiming compilation.

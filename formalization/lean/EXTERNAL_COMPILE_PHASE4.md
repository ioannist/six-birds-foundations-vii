# External Lean replay — FVII-SCI-04

The cumulative source is currently pinned to `leanprover/lean4:v4.28.0`. A different compatible Lean 4 release may be selected by editing `lean-toolchain` and committing the change before replay.

From the repository root, run:

```sh
bash scripts/run_fvii_sci04_external_lean.sh
```

The script requires `lean`, `lake`, and `python3` on `PATH`. It performs:

1. deterministic regeneration of the Phase-1 through Phase-4 Python baselines;
2. `lake clean` followed by the cumulative `lake build`;
3. execution of the Phase-1 reference world;
4. execution of the Phase-2, Phase-3, and Phase-4 finite-envelope runners;
5. replay of the assigned Phase-4 scenarios and countermodels;
6. `#print axioms` capture for every cumulative theorem surface;
7. exact Lean/Python differential checks for Phase 4;
8. the strict FVII-SCI-04 validator with `--require-lean-results`.

A successful replay updates only execution-status and generated validation/report surfaces. It does not change theorem statements or finite-family definitions. Commit the replay receipts and any toolchain-pin change.

## Expected Phase-4 outputs

- `formalization/foundations_vii_lab/phase4/results/lean_results.jsonl`
- `formalization/foundations_vii_lab/phase4/results/cross_implementation_status.json`
- `formalization/foundations_vii_lab/phase4/results/lean_axioms.txt`
- `formalization/lean/BUILD_STATUS_PHASE4.json`

Until those receipts exist and pass the strict validator, the truthful grade is source-complete with external kernel replay pending.
